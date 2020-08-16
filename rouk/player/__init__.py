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

LABEL_CODES = {
    't': ['Playlist', 'INCLUDED_IN'],
    'm': ['Album', 'INCLUDED_IN'],
    'a': ['Artist', 'BY']
}

def init_app(app):
    app.cli.add_command(start_omxplayer)

def end_song(process):
    if process is None: return
    process.stdin.write(b'q')
    process.kill()
    process.wait()

def get_playlist(tx, code, label_id):
    label = LABEL_CODES[code][0]
    type_ = LABEL_CODES[code][1]
    query = (
        'MATCH (f:Folder)-[c:CONTAINS]->(s:Song)-[i:{}]->(p:{}) WHERE id(p)=$id'
        ' RETURN s.name as name, s.year as year, s.duration as duration,'
        'f.path as root, c.name as filename, i.track as track ORDER BY track'
    ).format(type_, label)

    query2 = 'MATCH (p:{}) WHERE id(p)=$id RETURN p.current'.format(label)

    result = tx.run(query, id=label_id)
    cur = tx.run(query2, id=label_id)

    current = cur.single().value() - 1

    return current, [song.data() for song in result]

def set_current(tx, label, label_id, current):
    query = 'MATCH (p:{}) WHERE id(p)=$id SET p.current=$current'.format(label)
    tx.run(query, id=label_id, current=current)

def create_server(host, port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen()
    server.settimeout(0)
    return server

def play_song(song):
    return Popen(['omxplayer', '-o', 'alsa', song], stdin=PIPE, stdout=PIPE, bufsize=0)

def emit_event(subscribers, msg):
    for subscriber in subscribers:
        subscriber.sendall(msg)

def next_song(current, label, song, neo4j, size, playlist, label_id):
    current += 1
    process = None
    if size == current:
        with neo4j.session() as session:
            session.write_transaction(set_current, label, label_id, 0)
    else:
        with neo4j.session() as session:
            session.write_transaction(set_current, label, label_id, current)
        song = playlist[current]
        process = play_song(song)
    return current, song, process

@click.command("omxplayer")
@with_appcontext
def start_omxplayer():
    neo4j = get_db()

    queue = Queue()

    host, port = "localhost", 9999
    server = create_server(host, port)

    process = current = song = label = label_id = size = new_songs_monitor = None

    playlist = []

    subscribers = []

    try:
        while True:
            time.sleep(0.1)

            if not process is None and not process.poll() is None:
                emit_event(subscribers, 'e')
                current, song, process = next_song(
                    current, label, song, neo4j, size, playlist, label_id)
            try:
                conn, _ = server.accept()
            except:
                conn = None

            if not conn is None:
                data = ''
                while True:
                    data_ = conn.recv(1024).decode('utf8')
                    if not data_: break
                    data += data_

                close_conn = True
                emit = True

                if data[0] in LABEL_CODES:
                    label = data[0]
                    label_id = data[2:]
                    with neo4j.session() as session:
                        current, playlist = session.read_transaction(
                            get_playlist, label, label_id)
                    
                    song = playlist[current]
                    size = len(playlist)
                    process = play_song(song)
                elif data == 'u':
                    new_songs_monitor = Thread(target=update_library, daemon=True,
                        args=[queue, neo4j, current_app.config['MUSIC_ROOT']])
                    new_songs_monitor.start()
                    emit = False
                elif data[0] == 's':
                    label_id = None
                    song = {'path': data[2:]}
                    process = play_song(data[2:])
                elif data == 'q':
                    break
                elif data == 'p':
                    if not process is None and process.poll() is None:
                        process.stdin.write(b'p')
                elif data == 'n':
                    if label_id is None: continue
                    end_song(process)
                    current, song, process = next_song(current, label, song, neo4j, size, playlist, label_id)
                elif data == 'l':
                    if label_id is None: continue
                    end_song(process)
                    current = max(0, current - 1)
                    with neo4j.session() as session:
                        session.write_transaction(set_current, label, label_id, current)
                    song = playlist[current]
                    process = play_song(song)
                elif data == 'r':
                    end_song(process)
                    process = play_song(song)
                elif data == 'i':
                    subscribers.append(conn)
                    close_conn = False
                    emit = False
                
                if close_conn:
                    conn.sendall(b'ok')
                    conn.close()
                
                if emit:
                    emit_event(subscribers, data)


    except KeyboardInterrupt:
        print("caught keyboard interrupt, exiting")
    except Exception:
        traceback.print_exc()
    finally:
        queue.put('q')
        end_song(process)
        server.close()
        if not new_songs_monitor is None: new_songs_monitor.join()
