from flask import Blueprint, current_app, Response, jsonify, request, stream_with_context
from rouk.db import get_db
from rouk.utils import send_request
import socket
import time

bp = Blueprint("play", __name__, url_prefix='/api')


def set_current(tx, label, playlist_id, current):
    query = 'MATCH (p:{} {{id: $id}}) SET p.current=$current'.format(label)
    tx.run(query, id=playlist_id, current=current)


@bp.route('/play/song/<string:id_>', methods=['POST'])
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