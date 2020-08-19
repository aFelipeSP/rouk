import json
import socket
import time
import traceback
from pathlib import Path
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
        'MATCH (al:Album)<-[:INCLUDED_IN]-(s:Song)-[:BY]->(a:Artist)'
        'MATCH (f:Folder)-[c:CONTAINS]->(s)-[i:{}]->(p:{}) WHERE id(p)=$id '
        'WITH s, i, al, a, f, p, c ORDER BY i.track RETURN collect(id(s) as id,'
        's.name as name, s.year as year, s.duration as duration,{id: id(a), '
        'name: a.name} as artist, {id: id(al), name: al.name} as album, '
        'f.path as root, c.name as filename, i.track as track) as songs, '
        'p.current as track'
    ).format(type_, label)

    result = tx.run(query, id=label_id).single().data()
    current = result['current'] - 1
    return current, result['songs']

def get_song(tx, id_):
    query = (
        'MATCH (al:Album)<-[:INCLUDED_IN]-(s:Song)-[:BY]->(a:Artist) '
        'WHERE id(s)=$id MATCH (f:Folder)-[c:CONTAINS]->(s) RETURN id(s) as id,'
        's.name as name, s.duration as duration, s.year as year, {id: id(a),'
        'name: a.name} as artist, {id: id(al), name: al.name} as album,'
        'f.path as root, c.name as filename, i.track as track'
    )

    return tx.run(query, id=id_).single().data()

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
    file_ = Path(song['root']) / song['filename']
    return Popen(['omxplayer', '-o', 'alsa', str(file_)], stdin=PIPE, stdout=PIPE, bufsize=0)

def emit_event(subscribers, msg):
    for subscriber in subscribers:
        try:
            subscriber.sendall(msg.encode('utf8'))
        except BrokenPipeError:
            subscribers.remove(subscriber)

def next_song(current, label, song, neo4j, size, playlist, label_id, subscribers):
    current += 1
    process = None
    if size == current:
        emit_event(subscribers, 'e')
        playing = False
        with neo4j.session() as session:
            session.write_transaction(set_current, label, label_id, 0)
    else:
        with neo4j.session() as session:
            session.write_transaction(set_current, label, label_id, current)
        song = playlist[current]

        emit_event(subscribers, 'n:' + json.dumps({
            'id': label_id,
            'song': song
        }))
        playing = True

        process = play_song(song)
    return current, song, process, playing

@click.command("omxplayer")
@with_appcontext
def start_omxplayer():
    neo4j = get_db()

    queue = Queue()

    host, port = "localhost", 9999
    server = create_server(host, port)

    process = current = song = label = label_id = size = new_songs_monitor = None
    playing = False
    playlist = []

    subscribers = []

    try:
        while True:
            time.sleep(0.1)

            if not process is None and not process.poll() is None:
                current, song, process, playing = next_song( current, label,
                    song, neo4j, size, playlist, label_id, subscribers)
            try:
                conn, _ = server.accept()
            except:
                conn = None

            if not conn is None:
                conn.settimeout(0)
                data = ''
                while True:
                    try:
                        data_ = conn.recv(1024)
                    except:
                        data_ = None
                    if not data_: break
                    data += data_.decode('utf8')

                close_conn = True
                emit = True

                if data[0] in LABEL_CODES:
                    label = LABEL_CODES[data[0]][0]
                    _id = data[2:]
                    with neo4j.session() as session:
                        current, playlist = session.read_transaction(
                            get_playlist, data[0], _id)
                    
                    song = playlist[current]
                    data = data[0] + ':' + json.dumps({
                        'id': data[2:],
                        'song': song
                    })
                    playing = True
                    size = len(playlist)
                    process = play_song(song)
                elif data == 'u':
                    new_songs_monitor = Thread(target=update_library, daemon=True,
                        args=[queue, neo4j, current_app.config['MUSIC_ROOT']])
                    new_songs_monitor.start()
                    emit = False
                elif data[0] == 's':
                    label_id = None
                    with neo4j.session() as session:
                        song = session.read_transaction(get_song, data[2:])
                    playlist = [song]
                    data = 's:' + json.dumps({
                        'song': song
                    })
                    playing = True
                    process = play_song(song)
                elif data == 'q':
                    break
                elif data == 'p':
                    if not process is None and process.poll() is None:
                        process.stdin.write(b'p')
                    playing = not playing
                    data = 'p:' + ('1' if playing else '0')
                elif data == 'n':
                    if label_id is None: continue
                    end_song(process)
                    current, song, process, playing = next_song(current, label,
                        song, neo4j, size, playlist, label_id, subscribers)
                    emit = False
                    playing = True
                elif data == 'l':
                    if label_id is None: continue
                    end_song(process)
                    current = max(0, current - 1)
                    with neo4j.session() as session:
                        session.write_transaction(
                            set_current, label, label_id, current)
                    song = playlist[current]
                    data = 'l:'+ json.dumps({
                        'id': label_id,
                        'song': song
                    })
                    process = play_song(song)
                    playing = True
                elif data == 'r':
                    end_song(process)
                    process = play_song(song)
                    playing = True
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
        
        for subscriber in subscribers:
            try:
                subscriber.close()
            except:
                pass
        if not new_songs_monitor is None: new_songs_monitor.join()
