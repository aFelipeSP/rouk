import socket
import time
import traceback
from queue import Queue
from subprocess import PIPE, Popen
from threading import Thread

import click
from flask import current_app
from flask.cli import with_appcontext

from rouk.db import get_db
from rouk.player.update_library import update_library

def init_app(app):
    app.cli.add_command(start_omxplayer)

def end_song(process):
    if process is None: return
    process.stdin.write(b'q')
    process.kill()
    process.wait()

def get_playlist(tx, data, id_):
    query = (
        'MATCH (f:Folder)-[C:CONTAINS]->(:Song)-[i:{}]->(p:{} {{id: $id}}) '
        'RETURN (f.path + c.name) as s, i.track as track ORDER BY track'
    ).format(data[1], data[0])

    query2 = 'MATCH (p:{} {{id: $id}}) RETURN p.current'.format(data[0])

    result = tx.run(query, id=id_)
    cur = tx.run(query2, id=id_)

    current = cur.single().value() - 1

    return current, [song.data()['s'] for song in result]

def set_current(tx, playlist_id, current):
    current += 1
    query = 'MATCH (p:Playlist {id: $id}) SET p.current=$current'
    tx.run(query, id=playlist_id, current=current)

def create_server(host, port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen()
    server.settimeout(0)
    return server

def play_song(song):
    return Popen(['omxplayer', '-o', 'alsa', song], stdin=PIPE, stdout=PIPE, bufsize=0)

def next_song(current, song, neo4j, size, playlist, playlist_id):
    current += 1
    process = None
    if size == current:
        with neo4j.session() as session:
            session.write_transaction(set_current, playlist_id, 0)
    else:
        with neo4j.session() as session:
            session.write_transaction(set_current, playlist_id, current)
        song = playlist[current]
        process = play_song(song)
    return current, song, process

@click.command("omxplayer")
@with_appcontext
def start_omxplayer():
    codes = {
        't': ['Playlist', 'INCLUDED_IN'],
        'm': ['Album', 'INCLUDED_IN'],
        'a': ['Artist', 'BY']
    }

    neo4j = get_db()

    queue = Queue()

    host, port = "localhost", 9999
    server = create_server(host, port)

    process = current = song = playlist_id = size = new_songs_monitor = None

    playlist = []

    try:
        while True:
            time.sleep(0.1)

            if not process is None and not process.poll() is None:
                current, song, process = next_song(
                    current, song, neo4j, size, playlist, playlist_id)
            try:
                conn, _ = server.accept()
            except:
                conn = None

            if not conn is None:
                data = ''
                with conn:
                    while True:
                        data_ = conn.recv(1024).decode('utf8')
                        if not data_: break
                        data += data_
                        conn.sendall(b'ok')

                if data[0] in codes:
                    playlist_id = data[2:]
                    with neo4j.session() as session:
                        current, playlist = session.read_transaction(
                            get_playlist, codes[data[0]], playlist_id)
                    
                    song = playlist[current]
                    size = len(playlist)
                    process = play_song(song)
                elif data == 'u':
                    new_songs_monitor = Thread(target=update_library, daemon=True,
                        args=[queue, neo4j, current_app.config['MUSIC_ROOT']])
                    new_songs_monitor.start()
                elif data == 's':
                    playlist_id = None
                    song = {'path': data[2:]}
                    process = play_song(data[2:])
                elif data == 'q':
                    break
                elif data == 'p':
                    if not process is None and process.poll() is None:
                        process.stdin.write(b'p')
                elif data == 'n':
                    if playlist_id is None: continue
                    end_song(process)
                    current, song, process = next_song(current, song, neo4j, size, playlist, playlist_id)
                elif data == 'l':
                    if playlist_id is None: continue
                    end_song(process)
                    current = max(0, current - 1)
                    with neo4j.session() as session:
                        session.write_transaction(set_current, playlist_id, current)
                    song = playlist[current]
                    process = play_song(song)
                elif data == 'r':
                    end_song(process)
                    process = play_song(song)

    except KeyboardInterrupt:
        print("caught keyboard interrupt, exiting")
    except Exception:
        traceback.print_exc()
    finally:
        queue.put('q')
        end_song(process)
        server.close()
        if not new_songs_monitor is None: new_songs_monitor.join()
