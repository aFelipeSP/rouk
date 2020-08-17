from flask import Blueprint, current_app, Response, jsonify, request, stream_with_context
from rouk.db import get_db
import socket
import time

bp = Blueprint("api", __name__, url_prefix='/api')


def get_song_tx(tx, id_):
    query = ('MATCH (s:Album)<-[:INCLUDED_IN]-(s:Song)-[:BY]->(a:Artist)'
        ' WHERE ID(s)=$id RETURN s.name as name, s.duration as duration,'
        's.year as year, a.name as artist, al.name as album')
    return tx.run(query).single().data()

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

@bp.route('/song')
def search_songs_():
    neo4j = get_db()
    query = request.args.get('q', '')
    with neo4j.session() as session:
        if query == '': data = session.read_transaction(get_all_songs)
        else: data = session.read_transaction(search_songs, query)
    return jsonify(data)

@bp.route('/song/<string:id_>')
def get_song(id_):
    neo4j = get_db()
    with neo4j.session() as session:
        data = session.read_transaction(get_song_tx, id_)
    return jsonify(data)