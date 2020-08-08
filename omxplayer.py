
import time
from subprocess import PIPE, Popen
import socket
from neo4j import GraphDatabase
import traceback
from pathlib import Path

def end_song(process):
    if process is None: return
    process.stdin.write(b'q')
    process.kill()
    process.wait()

def get_playlist(tx, playlist_id):
    query = (
        'MATCH (s:Song)-[i:INCLUDED_IN]->(p:Playlist {id: $id})'
        'RETURN s, i.track as track ORDER BY track'
    )

    query2 = 'MATCH (p:Playlist {id: $id}) RETURN p.current'

    result = tx.run(query, id=playlist_id)
    cur = tx.run(query2, id=playlist_id)

    current = cur.single().value() - 1

    return current, [song.data()['s'] for song in result]

def create_server(host, port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen()
    server.settimeout(0)
    return server

def play_song(data):
    song = data['path']
    return Popen(['omxplayer', '-o', 'alsa', song], stdin=PIPE, stdout=PIPE, bufsize=0)

if __name__ == "__main__":

    with Path('instance/config') as f:
        neo4j_user, neo4j_passwrod = f.read().split('\n')

    uri = "neo4j://localhost:7687"
    neo4j = GraphDatabase.driver(uri, auth=(neo4j_user, neo4j_passwrod))

    host, port = "localhost", 9999
    server = create_server(host, port)

    process = current = song = playlist = size = None

    try:
        while True:
            time.sleep(0.1)

            if not process is None and not process.poll() is None:
                current += 1
                if size == current:
                    process = None
                else:
                    song = playlist[current]
                    process = play_song(song)

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

                if data.startswith('t'):
                    playlist_id = data[2:]
                    with neo4j.session() as session:
                        current, playlist = session.read_transaction(
                            get_playlist, playlist_id)
                    
                    song = playlist[current]
                    size = len(playlist)
                    process = play_song(song)
                elif data == 'q':
                    break
                elif data == 'p':
                    if not process is None and process.poll() is None:
                        process.stdin.write(b'p')
                elif data == 'n':
                    end_song(process)
                    current += 1
                    if size == current:
                        process = None
                    else:
                        song = playlist[current]
                        process = play_song(song)
                elif data == 'l':
                    end_song(process)
                    current = max(0, current - 1)
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
        end_song(process)
        server.close()
