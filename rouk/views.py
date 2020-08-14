from flask import Blueprint, current_app, Response, jsonify, request
from rouk.db import get_db
import socket
from uuid import uuid4

bp = Blueprint("api", __name__)

codes = {
    'playlist': 't',
    'album': 'm',
    'artist': 'a',
    'song': 's'
}

def send_request(msg):
    conf = current_app.config
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        client.connect((conf['PLAYER_HOST'], conf['PLAYER_PORT']))
        client.sendall(msg.encode('utf8'))
        return client.recv(1024)

def search_tx(tx, label, text):
    query = (
        'CALL db.index.fulltext.queryNodes($index_name, $text) '
        'YIELD node, score RETURN node, score'
    )

    result = tx.run(query, index_name='search'+label, text=text)
    return [song.data() for song in result]

def set_current(tx, label, playlist_id, current):
    query = 'MATCH (p:{} {{id: $id}}) SET p.current=$current'.format(label)
    tx.run(query, id=playlist_id, current=current)

def create_playlist(tx, name):
    playlist_id = str(uuid4())
    query = 'CREATE (p:Playlist {id: $id, name: $name})'
    tx.run(query, id=playlist_id, name=name)
    return playlist_id

def add_songs(tx, playlist_id, songs):
    query = (
        'MATCH (p:Playlist {id: $id}) WITH p '
        'MATCH q =(:Song)-[INCLUDED_IN]->(p) '
        'WITH p, length(q) as size, $songs as songs '
        'FOREACH (i IN range(0, $size) | '
        'MATCH (s:Song {id: songs[size + i]}) '
        'CREATE (s)-[INCLUDED_IN]->(p)) '
    )
    tx.run(query, id=playlist_id, songs=songs, size=len(songs))

def delete_playlist(tx, playlist_id):
    query = 'MATCH (p:Playlist {id: $id}) DETACH DELETE p'
    tx.run(query, id=playlist_id)

def get(tx, label, id_):
    query = 'MATCH (p:{} {{id: $id}}) RETURN p'.format(label)
    return tx.run(query, id=id_).single().data()['p']

def get_all(tx, label):
    query = 'MATCH (p:{}) RETURN p'.format(label)
    return [item.data()['p'] for item in tx.run(query)]

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

@bp.route('/search/<string:label>')
def search(label):
    neo4j = get_db()
    if not label in ['song', 'playlist', 'artist', 'album']:
        return Response('wrong "label" value', 400)

    label = label.capitalize()
    query = request.args.get('q', '')
    with neo4j.session() as session:
        if query == '':
            data = session.read_transaction(get_all, label)
        else:
            data = session.read_transaction(search_tx, label, query)
    return jsonify(data)

@bp.route('/play/song/<string:path>', methods=['POST'])
def play_song(path):
    send_request('s:{}'.format(path))
    return Response('OK', 200)

@bp.route('/play/<string:label>/<string:id>', methods=['POST'])
def play(label, id_):
    data = request.json
    if isinstance(data, dict) and data.get('current', False):
        current = data['current']
        neo4j = get_db()
        with neo4j.session() as session:
            session.write_transaction(set_current, label.capitalize(), id_, current)
    send_request('{}:{}'.format(codes[label], id_))
    return Response('OK', 200)

@bp.route('/playlist', methods=['POST'])
def playlist():
    data = request.json
    name = data.get('name', None)
    if name is None: return Response('"name" is required', 400)
    neo4j = get_db()
    with neo4j.session() as session:
        playlist_id = session.write_transaction(create_playlist, name)

    return jsonify(playlist_id=playlist_id)

@bp.route('/playlist/<string:id_>', methods=['PUT'])
def playlist_songs(id_):
    data = request.json
    songs = data.get('songs', None)
    if songs is None: return Response('"songs" array is required', 400)
    neo4j = get_db()
    with neo4j.session() as session:
        session.write_transaction(add_songs, id_, songs)

    return Response('OK', 200)

@bp.route('/playlist/<string:id_>', methods=['DELETE'])
def delete_playlist_(id_):
    neo4j = get_db()
    with neo4j.session() as session:
        session.write_transaction(delete_playlist, id_)
    return Response('OK', 200)

@bp.route('/playlist')
def playlist_get_all():
    with get_db().session() as session:
        result = session.read_transaction(get_all, 'Playlist')
    return jsonify(result)

@bp.route('/song')
def song_get_all():
    with get_db().session() as session:
        result = session.read_transaction(get_all, 'Song')
    return jsonify(result)

@bp.route('/artist')
def artist_get_all():
    with get_db().session() as session:
        result = session.read_transaction(get_all, 'Artist')
    return jsonify(result)

@bp.route('/playlist/<string:id_>')
def get_playlist(id_):
    with get_db().session() as session:
        result = session.read_transaction(get, 'Playlist', id_)
    return jsonify(result)

@bp.route('/album/<string:id_>')
def get_album(id_):
    with get_db().session() as session:
        result = session.read_transaction(get, 'Album', id_)
    return jsonify(result)

@bp.route('/artist/<string:id_>')
def get_artist(id_):
    with get_db().session() as session:
        result = session.read_transaction(get, 'Artist', id_)
    return jsonify(result)

@bp.route('/song/<string:id_>')
def get_song(id_):
    with get_db().session() as session:
        result = session.read_transaction(get, 'Song', id_)
    return jsonify(result)