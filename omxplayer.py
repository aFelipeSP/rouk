import os
import socket
import time
import traceback
from pathlib import Path
from queue import Queue
from subprocess import PIPE, Popen
from threading import Thread
from tinytag import TinyTag

import instance.config as config
from neo4j import GraphDatabase

codes = {
    't': ['Playlist', 'INCLUDED_IN'],
    'm': ['Album', 'INCLUDED_IN'],
    'a': ['Artist', 'BY']
}

def add_song(tx, song, root, a):
    query = (
        'MERGE (al:Album {name: $album})'
        'MERGE (ar:Artist {name: $artist})'
        'MERGE (f:Folder {path: $path})'
        'CREATE (al)<-[:INCLUDED_IN {track: $track}]-'
        '(s:Song {title: $title, year: $year, duration: $duration})-[:BY]->(ar)'
        'CREATE (ar)<-[:BY]-(al) CREATE (f)-[:CONTAINS {name: $song}]->(s)'
    )
    tx.run(query, album=a.album, artist=a.artist, path=root, track=a.track,
        title=a.title, year=a.year, duration=a.duration, song=song)

def delete_songs(tx, songs, path):
    query = (
        'WITH $songs as song'
        'MATCH (s:Song)<-[:CONTAINS {name: $song}]-(f:Folder {path: $path})'
        'DETACH DELETE s'
    )
    tx.run(query, songs=songs, path=path)

def songs_in_folder(tx, path):
    query = 'MATCH (:Song)<-[c:CONTAINS]-(:Folder {path: $p}) RETURN c.name as s'
    return [song.data()['s'] for song in tx.run(query, p=path)]

def create_subfolders(tx, subfolders, path):
    query = (
        'WITH $subfolders as subfolders'
        'UNWIND subfolders as subfolder'
        'MERGE (r:Folder {path: $path})'
        'MERGE (f:Folder {path: subfolder})'
        'MERGE (f)-[:IS_SUBFOLDER]->(r)'
    )
    tx.run(query, subfolders=subfolders, path=path)

def delete_subfolders(tx, subfolders, path):
    query = (
        'MATCH (r:Folder {path: $path})<-[:IS_SUBFOLDER]-'
        '(f:Folder)-[:CONTAINS]->(s:Song)'
        'WHERE NOT f.path IN $subfolders DETACH DELETE f, s'
    )
    tx.run(query, subfolders=subfolders, path=path)

def search_new_songs(queue, neo4j, music_root):
    formats = ['m4a', 'mp3', 'wma', 'ogg', 'flac']
    for root, dirs, files in os.walk(Path(music_root)):
        try:
            x = queue.get(False)
            if x == 'q': return False
        except:
            pass

        with neo4j.session() as session:
            session.write_transaction(create_subfolders, dirs, root)
            session.write_transaction(delete_subfolders, dirs, root)

        music_files = [ff for ff in files if Path(ff).suffix in formats]

        with neo4j.session() as session:
            songs = session.read_transaction(songs_in_folder, root)
        songs_set = set(songs)
        files_set = set(music_files)
        new_songs = files_set - songs_set
        del_songs = songs_set - files_set
        len_new_songs, len_del_songs = [len(new_songs) > 0, len(del_songs) > 0]

        if len_new_songs:
            for song in new_songs:
                attrs = TinyTag.get(song)
                with neo4j.session() as session:
                    songs = session.write_transaction(add_song, song, root, attrs)

        if len_del_songs:
            with neo4j.session() as session:
                songs = session.write_transaction(delete_songs, del_songs, root)

    return True

def end_song(process):
    if process is None: return
    process.stdin.write(b'q')
    process.kill()
    process.wait()

def get_playlist(tx, data, id_):
    query = (
        'MATCH (f:Folder)-[C:CONTAINS]->(:Song)-[i:$type]->(p:$label {id: $id})'
        'RETURN (f.path + c.name) as s, i.track as track ORDER BY track'
    )

    query2 = 'MATCH (p:$label {id: $id}) RETURN p.current'

    result = tx.run(query, type=data[1], label=data[0], id=playlist_id)
    cur = tx.run(query2, label=data[0], id=playlist_id)

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

def next_song(current, song, neo4j, size, playlist_id):
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

if __name__ == "__main__":
    neo4j_user, neo4j_passwrod = [config.NEO4J_USER, config.NEO4J_PASSWORD]

    uri = "neo4j://localhost:7687"
    neo4j = GraphDatabase.driver(uri, auth=(neo4j_user, neo4j_passwrod))

    queue = Queue()
    new_songs_monitor = Thread(
        search_new_songs, daemon=True, args=[queue, neo4j, config.MUSIC_ROOT])
    new_songs_monitor.start()

    host, port = "localhost", 9999
    server = create_server(host, port)

    process = current = song = playlist_id = size = None

    playlist = []

    try:
        while True:
            time.sleep(0.1)

            if not process is None and not process.poll() is None:
                current, song, process = next_song(
                    current, song, neo4j, size, playlist_id)
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
                    current, song, process = next_song(current, song, neo4j, size, playlist_id)
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
    except Exception as error:
        traceback.print_exc()
    finally:
        queue.put('q')
        end_song(process)
        server.close()
        new_songs_monitor.join()
