from flask import Blueprint, current_app, Response, jsonify, request, stream_with_context
from rouk.db import get_db
import socket
import time

bp = Blueprint("api", __name__, url_prefix='/api')


@bp.route('/stream')
def stream():
    def fn ():
        try:
            conf = current_app.config
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((conf['PLAYER_HOST'], conf['PLAYER_PORT']))
            client.sendall(b'i')
            while True:
                data = ''
                while True:
                    data_ = client.recv(1024)
                    if not data_: break
                    data += data_.decode('utf8')
                yield 'event:' + data[0] + '\ndata:' + data[2:] + '\n\n'
        finally:
            client.close()

    resp = Response(stream_with_context(fn()))
    resp.headers['Content-Type'] = 'text/event-stream'
    resp.headers['Cache-Control'] = 'no-cache'
    resp.headers['Connection'] = 'keep-alive'
    return resp

def send_request(msg):
    conf = current_app.config
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        client.connect((conf['PLAYER_HOST'], conf['PLAYER_PORT']))
        client.sendall(msg.encode('utf8'))
        return client.recv(1024)

def set_current(tx, label, playlist_id, current):
    query = 'MATCH (p:{} {{id: $id}}) SET p.current=$current'.format(label)
    tx.run(query, id=playlist_id, current=current)

def create_playlist(tx, name):
    query = 'CREATE (p:Playlist {name: $name}) RETURN ID(p) as id'
    return tx.run(query, name=name).single().data()['id']

def add_songs(tx, playlist_id, songs):
    query = (
        'MATCH (p:Playlist) WHERE id(p)=$id WITH p '
        'MATCH q =(:Song)-[:INCLUDED_IN]->(p) '
        'WITH p, length(q) as len, $songs as songs '
        'FOREACH (i IN range(0, $size) | '
        'MATCH (s:Song) WHERE id(s)=songs[i] '
        'CREATE (s)-[:INCLUDED_IN {track: len+i}]->(p))'
    )
    tx.run(query, id=playlist_id, songs=songs, size=len(songs))

def delete_playlist(tx, id_):
    query = 'MATCH (p:Playlist) WHERE id(p)=$id DETACH DELETE p'
    tx.run(query, id=id_)

def get(tx, label, id_):
    query = 'MATCH (p:{}) WHERE id(p)=$id RETURN p'.format(label)
    return tx.run(query, id=id_).single().data()['p']

@bp.route('/update', methods=['POST'])
def update():
    send_request('u')
    return Response('OK', 200)

@bp.route('/random', methods=['POST'])
def random():
    send_request('d')
    return Response('OK', 200)

@bp.route('/last', methods=['POST'])
def last():
    send_request('l')
    return Response('OK', 200)

@bp.route('/toggle-play', methods=['POST'])
def toggle_play():
    send_request('p')
    return Response('OK', 200)

@bp.route('/next', methods=['POST'])
def next():
    send_request('n')
    return Response('OK', 200)

@bp.route('/repeat', methods=['POST'])
def repeat():
    send_request('r')
    return Response('OK', 200)

def get_all_songs(tx):
    query = ('MATCH (al:Album)<-[:INCLUDED_IN]-(s:Song)-[:BY]->(a:Artist)'
        ' RETURN s.name as name, s.duration as duration, s.year as year,'
        'a.name as artist, al.name as album')
    return [item.data() for item in tx.run(query)]

def search_songs(tx, text):
    query = (
        'CALL db.index.fulltext.queryNodes("searchSong", $text) '
        'YIELD node, score MATCH (al:Album)<-[:INCLUDED_IN]'
        '-(node)-[:BY]->(a:Artist) RETURN node.name as name, node.duration '
        'as duration, node.year as year, a.name as artist, al.name as album'
    )

    result = tx.run(query, text=text)
    return [song.data() for song in result]

@bp.route('/search/song')
def search_songs_():
    neo4j = get_db()
    query = request.args.get('q', '')
    with neo4j.session() as session:
        if query == '': data = session.read_transaction(get_all_songs)
        else: data = session.read_transaction(search_songs, query)
    return jsonify(data)


def get_all_albums(tx):
    query = ('MATCH (al:Album)-[:BY]->(a:Artist)'
        'RETURN al.name as name, a.name as artist')
    return [item.data() for item in tx.run(query)]

def search_albums(tx, text):
    query = (
        'CALL db.index.fulltext.queryNodes("searchAlbum", $text) '
        'YIELD node,score MATCH (node)-[:BY]->(a:Artist) '
        'RETURN node.name as name, a.name as artist'
    )

    result = tx.run(query, index_name='searchAlbum', text=text)
    return [song.data() for song in result]

@bp.route('/search/album')
def search_albums_():
    neo4j = get_db()
    query = request.args.get('q', '')
    with neo4j.session() as session:
        if query == '': data = session.read_transaction(get_all_albums)
        else: data = session.read_transaction(search_albums, query)
    return jsonify(data)

def get_all(tx, label):
    query = 'MATCH (p:{}) RETURN p'.format(label)
    return [item.data()['p'] for item in tx.run(query)]

def search_tx(tx, label, text):
    query = (
        'CALL db.index.fulltext.queryNodes($index_name, $text) '
        'YIELD node, score RETURN node'
    )

    result = tx.run(query, index_name='search'+label, text=text)
    return [song.data()['node'] for song in result]

@bp.route('/search/<string:label>')
def search(label):
    if not label in ['playlist', 'artist']:
        return Response('Page Not Found', 404)

    neo4j = get_db()
    label = label.capitalize()
    query = request.args.get('q', '')
    with neo4j.session() as session:
        if query == '': data = session.read_transaction(get_all, label)
        else: data = session.read_transaction(search_tx, label, query)
    return jsonify(data)

@bp.route('/play/song/<int:id_>', methods=['POST'])
def play_song(id_):
    send_request('s:'+id_)
    return Response('OK', 200)

@bp.route('/play/<string:label>/<string:id>', methods=['POST'])
def play(label, id_):
    codes = {
        'playlist': 't',
        'album': 'm',
        'artist': 'a'
    }
    if not label in codes: return Response('Page not found', 404)
    data = request.json
    if isinstance(data, dict) and data.get('current', False):
        neo4j = get_db()
        with neo4j.session() as session:
            session.write_transaction(
                set_current, label.capitalize(), id_, data['current'])
    send_request('{}:{}'.format(codes[label], id_))
    return Response('OK', 200)

@bp.route('/playlist', methods=['POST'])
def create_playlist_():
    data = request.json
    name = data.get('name', None)
    if name is None: return Response('"name" is required', 400)
    neo4j = get_db()
    with neo4j.session() as session:
        playlist_id = session.write_transaction(create_playlist, name)

    return jsonify(playlist_id=playlist_id)

@bp.route('/playlist/<int:id_>', methods=['PUT'])
def playlist_songs(id_):
    data = request.json
    songs = data.get('songs', None)
    if songs is None: return Response('"songs" array is required', 400)
    neo4j = get_db()
    with neo4j.session() as session:
        session.write_transaction(add_songs, id_, songs)

    return Response('OK', 200)

@bp.route('/playlist/<int:id_>', methods=['DELETE'])
def delete_playlist_(id_):
    neo4j = get_db()
    with neo4j.session() as session:
        session.write_transaction(delete_playlist, id_)
    return Response('OK', 200)

@bp.route('/<string:label>/<int:id_>')
def get_playlist(label, id_):
    if not label in ['playlist', 'album', 'artist', 'song']:
        return Response('Page not found', 404)
    with get_db().session() as session:
        result = session.read_transaction(get, 'Playlist', id_)
    return jsonify(result)
