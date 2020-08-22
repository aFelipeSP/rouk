import json
import random
import socket
import time
import traceback
from pathlib import Path
from subprocess import PIPE, Popen, run as sp_run

import click
from flask import current_app
from flask.cli import with_appcontext

from rouk.db import get_db

def init_app(app):
    app.cli.add_command(start_omxplayer)

def get_playlist(tx, relationship, playlist_type, playlist_id):
    query = (
        'MATCH (al:Album)<-[:INCLUDED_IN]-(s:Song)-[:BY]->(a:Artist)'
        'MATCH (f:Folder)-[c:CONTAINS]->(s)-[i:{}]->(p:{}) WHERE id(p)=$id '
        'WITH s, i, al, a, f, p, c ORDER BY i.track RETURN collect({{id: id(s),'
        'name: s.name, year: s.year, duration: s.duration, artist: {{id: id(a), '
        'name: a.name}}, album: {{id: id(al), name: al.name}}, root: f.path, '
        'filename: c.name, track: i.track}}) as songs, p.current_track as track'
    ).format(relationship, playlist_type.capitalize())

    result = tx.run(query, id=playlist_id).single().data()
    current_track = result.get('current_track', 1) - 1
    return current_track, result['songs']

def get_song(tx, id_):
    query = (
        'MATCH (al:Album)<-[i:INCLUDED_IN]-(s:Song)-[:BY]->(a:Artist) '
        'WHERE id(s)=$id MATCH (f:Folder)-[c:CONTAINS]->(s) RETURN id(s) as id,'
        's.name as name, s.duration as duration, s.year as year, {id: id(a),'
        'name: a.name} as artist, {id: id(al), name: al.name} as album,'
        'f.path as root, c.name as filename, i.track as track'
    )

    return tx.run(query, id=id_).single().data()

def set_current(tx, playlist_type, playlist_id, current_track):
    query = 'MATCH (p:{}) WHERE id(p)=$id SET p.current_track=$current_track'.format(playlist_type)
    tx.run(query, id=playlist_id, current_track=current_track)

def secs_to_song_format(t):
    secs = int(t % 60)
    mins_ = t / 60
    mins = int(mins_ % 60)
    hours = int(mins_/60)
    return '{:0<2}:{:0<2}:{:0<2}'.format(hours, mins, secs)

class Player:

    LABEL_CODES = {
        't': ['playlist', 'INCLUDED_IN'],
        'm': ['album', 'INCLUDED_IN'],
        'a': ['artist', 'BY']
    }

    def __init__(self, *args, **kwargs):
        self.stop = False

        self.player_process = self.current_track = self.song = None
        self.playlist_type = self.playlist_id = self.playlist_size = None
        self.new_songs_monitor = self.start_time = None
        self.time = 0
        self.playing = self.random = False
        self.already_played = set()
        self.playlist = []
        self.subscribers = []

    def create_server(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((
            current_app.config.get('PLAYER_HOST', 'localhost'),
            current_app.config.get('PLAYER_PORT', 9999)
        ))
        self.server.listen()
        self.server.settimeout(0)

    @property
    def state(self):
        time_ = self.time
        if self.playing:
            time_ += time.time() - self.start_time

        return json.dumps(dict(
            playlistType = self.playlist_type,
            playlistId = self.playlist_id,
            song = self.song,
            track = self.current_track,
            time = time_,
            playing = self.playing,
            random = self.random
        )).encode('utf8')

    def emit_state(self):
        for subscriber in self.subscribers:
            try:
                subscriber.sendall(self.state)
            except:
                try:
                    subscriber.shutdown(socket.SHUT_RDWR)
                    subscriber.close()
                except:
                    pass

    def set_playlist(self, code, id_):
        self.already_played = set()
        info = self.LABEL_CODES[code]
        self.playlist_type = info[0]
        self.playlist_id = id_
        with get_db().session() as session:
            self.current_track, self.playlist = session.read_transaction(
                get_playlist, info[1], info[0], id_)

        self.playlist_size = len(self.playlist)
        if self.random:
            self.current_track = random.randrange(self.playlist_size)

        self.song = self.playlist[self.current_track]
        self.playing = True

    def play_song(self, position=None):
        file_ = Path(self.song['root']) / self.song['filename']

        command = ['omxplayer', '-o', 'alsa']
        if position:
            self.time = position
            command += ['-l', secs_to_song_format(position)]
        else:
            self.time = 0
        command += [str(file_)]

        self.player_process = Popen(command, stdin=PIPE, stdout=PIPE, bufsize=0)
        self.playing = True
        self.start_time = time.time()

    def set_volume(self, volume):
        sp_run(['amixer', '-q', 'set', 'Master', str(volume)+'%'])

    def next_song(self):

        if self.random:
            if self.playlist_size == len(self.already_played) + 1:
                self.current_track = random.randrange(self.playlist_size)
                self.song = self.playlist[self.current_track]
            else:
                self.current_track = random.choice([
                    i for i in range(0,self.playlist_size)
                    if i not in self.already_played
                ])
                self.already_played.add(self.current_track)
                self.song = self.playlist[self.current_track]
                self.play_song()
        else:
            if self.playlist_size == self.current_track + 1:
                self.current_track = 0
                self.song = self.playlist[self.current_track]
            else:
                self.current_track += 1
                self.song = self.playlist[self.current_track]
                self.play_song()

            if self.playlist_id: self.update_current()

    def end_song(self):
        if self.player_process is None: return
        try:
            self.player_process.stdin.write(b'q')
            self.player_process.wait()
        except:
            pass
        self.player_process = None
        self.playing = False
        self.time = 0

    def update_current(self):
        with get_db().session() as session:
            session.write_transaction(set_current, self.playlist_type,
                self.playlist_id, self.current_track)

    def process(self):
        if (not self.player_process is None and
            not self.player_process.poll() is None
        ):
            self.end_song()
            self.next_song()
            self.emit_state()

        try:
            conn, _ = self.server.accept()
        except:
            return

        conn.settimeout(0)
        data = ''
        while True:
            try:
                data += conn.recv(1024).decode('utf8')
            except:
                break

        code, content = [data[0], data[2:]]

        if code == 'i':
            self.subscribers.append(conn)
            self.emit_state()
            return

        msg = b'ok'

        if code == 'p':
            if not self.player_process is None and self.player_process.poll() is None:
                self.player_process.stdin.write(b'p')
                self.playing = not self.playing
                current_time = time.time()
                if self.playing:
                    self.start_time = current_time
                else:
                    self.time += current_time - self.start_time
            elif self.song:
                self.play_song()
        elif code == 'd':
            self.random = not self.random
        elif code in self.LABEL_CODES:
            self.end_song()
            self.set_playlist(code, int(content))
            self.play_song()
        elif code == 's':
            self.playlist_type = 'song'
            self.end_song()
            self.playlist_id = int(content)
            with get_db().session() as session:
                self.song = session.read_transaction(get_song, int(content))
            self.current_track = 0
            self.playlist = [self.song]
            self.playlist_size = 1
            self.play_song()
        elif code == 'n':
            if not self.playlist_type in ['playlist', 'album', 'artist']: return
            self.end_song()
            self.next_song()
        elif code == 'l':
            if not self.playlist_type in ['playlist', 'album', 'artist']: return
            self.end_song()
            if self.random:
                choices = [
                    i for i in range(0,self.playlist_size)
                    if i not in self.already_played
                ]
                if len(choices) > 0:
                    self.current_track = random.choice([
                        i for i in range(0,self.playlist_size)
                        if i not in self.already_played
                    ])
                    self.already_played.add(self.current_track)
                    self.song = self.playlist[self.current_track]
                    self.play_song()
            else:
                self.current_track = max(0, self.current_track - 1)
                self.update_current()
                self.song = self.playlist[self.current_track]
                self.play_song()
        elif code == 'r':
            self.end_song()
            self.play_song()
        elif code == 'k':
            self.end_song()
            self.play_song(int(content))
        elif code == 'v':
            self.set_volume(int(content))
        elif code == 'f':
            msg = self.state

        conn.sendall(msg)
        conn.shutdown(socket.SHUT_RDWR)
        conn.close()

        self.emit_state()

    def teardown (self):
        self.end_song()
        self.server.shutdown(socket.SHUT_RDWR)
        self.server.close()

        for subscriber in self.subscribers:
            try:
                subscriber.sendall(b'end')
                subscriber.shutdown(socket.SHUT_RDWR)
                subscriber.close()
            except:
                pass
        print('player closed')

    def run(self):
        self.create_server()
        try:
            while True:
                if self.stop: break
                time.sleep(0.1)
                self.process()
        except KeyboardInterrupt:
            print("caught keyboard interrupt, exiting")
        except Exception:
            traceback.print_exc()
        finally:
            self.teardown()


@click.command("player")
@with_appcontext
def start_omxplayer():
    player = Player()
    player.run()