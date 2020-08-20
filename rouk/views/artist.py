from flask import Blueprint, jsonify, request, Response
from rouk.db import get_db
import socket
import time

bp = Blueprint("artist", __name__, url_prefix='/api')

def get_artist_tx(tx, id_):
    query = (
        'MATCH (al:Album)-[:BY]->(a:Artist) WHERE id(a)=$id WITH al, a ORDER BY'
        ' al.year RETURN id(a) as id, a.name as name collect({id: id(al),'
        'name: al.name, year: al.year}) as albums'
    )
    return tx.run(query, id=id_).single().data()

def get_all_artists(tx):
    query = 'MATCH (a:Artist) RETURN id(a) as id, a.name as name'
    return [item.data() for item in tx.run(query)]

def search_artists(tx, text):
    query = (
        'CALL db.index.fulltext.queryNodes("searchArtist", $text) '
        'YIELD node,score RETURN id(node) as id, node.name as name'
    )

    result = tx.run(query, index_name='searchAlbum', text=text)
    return [artist.data() for artist in result]

@bp.route('/artist')
def search():
    neo4j = get_db()
    query = request.args.get('q', '')
    with neo4j.session() as session:
        if query == '': data = session.read_transaction(get_all_artists)
        else: data = session.read_transaction(search_artists, query)
    return jsonify(data)

@bp.route('/artist/<int:id_>')
def get_album(id_):
    with get_db().session() as session:
        result = session.read_transaction(get_artist_tx, id_)
    return jsonify(result)