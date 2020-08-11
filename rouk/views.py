from flask import Blueprint, current_app, Response, jsonify, request
from rouk.db import get_db
import socket

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
        client.connect((conf.PLAYER_HOST, conf.PLAYER_PORT))
        client.sendall(msg)
        return client.recv(1024)


def search_tx(tx, label, text):
    query = (
        'CALL db.index.fulltext.queryNodes($index_name, $text) YIELD node, score'
        'RETURN node, score'
    )

    result = tx.run(query, index_name='search'+label, text=text)
    return [song.data() for song in result]


def set_current(tx, label, playlist_id, current):
    query = 'MATCH (p:$label {id: $id}) SET p.current=$current'
    tx.run(query, label=label, id=playlist_id, current=current)

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

@bp.route('/search/<string:label>/<string:text>')
def search(label, text):
    neo4j = get_db()
    with neo4j.session() as session:
        data = session.read_transaction(
            search_tx, label, text)
    return jsonify(data)

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
