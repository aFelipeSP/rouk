from flask import Blueprint, Response, jsonify, request
from rouk.db import get_db

bp = Blueprint("playlist", __name__, url_prefix='/api')

def get_playlist_tx(tx, id_):
    query = ('MATCH (s:Song)-[i:INCLUDED_IN]->(al:Playlist)'
        'WHERE id(al)=$id WITH s, i, al ORDER BY i.track '
        'RETURN collect({id: id(s), track:i.track, name: s.name,'
        'duration: s.duration, year: s.year}) as songs, al.name as name'
    )
    return tx.run(query, id=id_).single().data()

def get_all_playlists(tx):
    query = ('MATCH (al:Playlist) RETURN id(al) as id, al.name as name')
    return [item.data() for item in tx.run(query)]

def search_playlists(tx, text):
    query = (
        'CALL db.index.fulltext.queryNodes("searchPlaylist", $text) '
        'YIELD node,score MATCH (node)-[:BY]->(a:Artist) '
        'RETURN id(node) as id, node.name as name, a.name as artist'
    )

    result = tx.run(query, index_name='searchPlaylist', text=text)
    return [song.data() for song in result]

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

@bp.route('/playlist')
def search_playlists_():
    neo4j = get_db()
    query = request.args.get('q', '')
    with neo4j.session() as session:
        if query == '': data = session.read_transaction(get_all_playlists)
        else: data = session.read_transaction(search_playlists, query)
    return jsonify(data)

@bp.route('/playlist/<string:id_>')
def get_playlist(id_):
    with get_db().session() as session:
        result = session.read_transaction(get_playlist_tx, id_)
    return jsonify(result)

@bp.route('/playlist', methods=['POST'])
def create_playlist_():
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