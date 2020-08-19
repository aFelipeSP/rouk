import json
import socket
import time
import traceback
from pathlib import Path
from subprocess import PIPE, Popen
from threading import Thread

import click
from flask import current_app
from flask.cli import with_appcontext

from rouk.db import get_db
from rouk.player.update_library import update_library

def init_app(app):
    app.cli.add_command(start_omxplayer)

def get_playlist(tx, relationship, playlist_type, playlist_id):
    query = (
        'MATCH (al:Album)<-[:INCLUDED_IN]-(s:Song)-[:BY]->(a:Artist)'
        'MATCH (f:Folder)-[c:CONTAINS]->(s)-[i:{}]->(p:{}) WHERE id(p)=$id '
        'WITH s, i, al, a, f, p, c ORDER BY i.track RETURN collect(id(s) as id,'
        's.name as name, s.year as year, s.duration as duration,{id: id(a), '
        'name: a.name} as artist, {id: id(al), name: al.name} as album, '
        'f.path as root, c.name as filename, i.track as track) as songs, '
        'p.current_track as track'
    ).format(relationship, playlist_type)

    result = tx.run(query, id=playlist_id).single().data()
    current_track = result['current_track'] - 1
    return current_track, result['songs']

def get_song(tx, id_):
    query = (
        'MATCH (al:Album)<-[:INCLUDED_IN]-(s:Song)-[:BY]->(a:Artist) '
        'WHERE id(s)=$id MATCH (f:Folder)-[c:CONTAINS]->(s) RETURN id(s) as id,'
        's.name as name, s.duration as duration, s.year as year, {id: id(a),'
        'name: a.name} as artist, {id: id(al), name: al.name} as album,'
        'f.path as root, c.name as filename, i.track as track'
    )

    return tx.run(query, id=id_).single().data()

def set_current(tx, playlist_type, playlist_id, current_track):
    query = 'MATCH (p:{}) WHERE id(p)=$id SET p.current_track=$current_track'.format(playlist_type)
    tx.run(query, id=playlist_id, current_track=current_track)

class Player:

    LABEL_CODES = {
        't': ['playlist', 'INCLUDED_IN'],
        'm': ['album', 'INCLUDED_IN'],
        'a': ['artist', 'BY']
    }

    def __init__(self, *args, **kwargs):
        self.neo4j = get_db()

        self.player_process = self.current_track = self.song = None
        self.playlist_type = self.playlist_id = self.playlist_size = None
        self.new_songs_monitor = self.time = self.start_time = None
        self.playing = False
        self.playlist = []
        self.subscribers = []

    def create_server(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((
            current_app.config.get('PLAYER_HOST', 'localhost'), 
            current_app.config.get('PLAYER_PORT', 9999)
        ))
        self.server.listen()
        self.server.settimeout(0)

    def emit_state(self):
        msg = json.dumps(dict(
            playlistType = self.playlist_type,
            playlistId = self.playlist_id,
            song = self.song,
            track = self.current_track,
            time = None if self.start_time is None else time.time() - self.start_time,
            playing = self.playing
        ))
        for subscriber in self.subscribers:
            try: subscriber.sendall(msg.encode('utf8'))
            except BrokenPipeError: self.subscribers.remove(subscriber)

    def set_playlist(self, code, id_):
        info = self.LABEL_CODES[code]
        self.playlist_id = info[0]
        with self.neo4j.session() as session:
            self.current_track, self.playlist = session.read_transaction(
                get_playlist, info[1], info[0], id_)
        self.song = self.playlist[self.current_track]
        self.playlist_size = len(self.playlist)
        self.playing = True

    def play_song(self):
        file_ = Path(self.song['root']) / self.song['filename']
        command = ['omxplayer', '-o', 'alsa', str(file_)]
        self.player_process = Popen(command, stdin=PIPE, stdout=PIPE, bufsize=0)
        self.start_time = time.time()

    def next_song(self):
        if self.playlist is None: return

        self.end_song()
        if self.playlist_size == self.current_track + 1:
            self.playing = False
            self.song
            self.current_track = 0
        else:
            self.current_track += 1
            self.play_song()
        
        self.song = self.playlist[self.current_track]
        self.update_current()

    def end_song(self):
        if self.player_process is None: return
        self.player_process.stdin.write(b'q')
        self.player_process.kill()
        self.player_process.wait()
        self.player_process = None

    def update_current(self):
        with self.neo4j.session() as session:
            session.write_transaction(set_current, self.playlist_type,
                self.playlist_id, self.current_track)

    def process(self):
        if (not self.player_process is None and 
            not self.player_process.poll() is None
        ):
            self.next_song()

        try: conn, _ = self.server.accept()
        except: return

        conn.settimeout(0)
        data = ''
        while True:
            try: data += conn.recv(1024).decode('utf8')
            except: break

        close_conn = emit = playing = True
        code, content = [data[0], data[2:]] 

        if code in self.LABEL_CODES:
            self.set_playlist(code, content)
            self.play_song()
        elif data[0] == 's':
            self.playlist_id = None
            self.playlist = None
            with self.neo4j.session() as session:
                self.song = session.read_transaction(get_song, content)
            self.play_song()
        elif data == 'q':
            return 'q'
        elif data == 'p':
            if not self.player_process is None and self.player_process.poll() is None:
                self.player_process.stdin.write(b'p')
                playing = not self.playing
        elif data == 'n':
            if self.playlist_id is None: return
            self.next_song()
            emit = False
        elif data == 'l':
            if self.playlist_id is None: return
            self.end_song()
            self.current_track = max(0, self.current_track - 1)
            self.update_current()
            self.song = self.playlist[self.current_track]
            self.play_song()
        elif data == 'r':
            self.end_song()
            self.play_song()
        elif data == 'i':
            self.subscribers.append(conn)
            close_conn = False
            emit = False

        self.playing = playing

        if close_conn:
            conn.sendall(b'ok')
            conn.close()
        
        if emit:
            self.emit_state()

    def run(self):
        try:
            while True:
                time.sleep(0.1)
                res = self.process()
                self.emit_state()
                if res == 'q': break
        except KeyboardInterrupt:
            print("caught keyboard interrupt, exiting")
        except Exception:
            traceback.print_exc()
        finally:
            self.end_song()
            self.server.close()
            
            for subscriber in self.subscribers:
                try: subscriber.close()
                except: pass


@click.command("player")
@with_appcontext
def start_omxplayer():
    player = Player()
    player.run()