from flask import Blueprint, jsonify, request
from rouk.db import get_db

bp = Blueprint("album", __name__, url_prefix='/api')

def get_album_tx(tx, id_):
    query = (
        'MATCH (s:Song)-[i:INCLUDED_IN]->(al:Album)-[:BY]->(a:Artist)'
        'WHERE id(al)=$id WITH s, i, al, a order by i.track '
        'RETURN id(al) as id, al.name as name, collect({id: id(s),'
        'track:i.track, name: s.name, duration: s.duration, year: s.year}) '
        'as songs, {name: a.name, id:id(a)} as artist'
    )
    return tx.run(query, id=id_).single().data()

def get_all_albums(tx):
    query = ('MATCH (al:Album)-[:BY]->(a:Artist)'
        'RETURN id(al) as id, al.name as name, a.name as artist')
    return [item.data() for item in tx.run(query)]

def search_albums(tx, text):
    query = (
        'CALL db.index.fulltext.queryNodes("searchAlbum", $text) '
        'YIELD node,score MATCH (node)-[:BY]->(a:Artist) '
        'RETURN id(node) as id, node.name as name, a.name as artist'
    )

    result = tx.run(query, index_name='searchAlbum', text=text)
    return [song.data() for song in result]

@bp.route('/album')
def search_albums_():
    neo4j = get_db()
    query = request.args.get('q', '')
    with neo4j.session() as session:
        if query == '': data = session.read_transaction(get_all_albums)
        else: data = session.read_transaction(search_albums, query)
    return jsonify(data)

@bp.route('/album/<int:id_>')
def get_album(id_):
    with get_db().session() as session:
        result = session.read_transaction(get_album_tx, id_)
    return jsonify(result)