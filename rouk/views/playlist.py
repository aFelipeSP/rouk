from flask import Blueprint, Response, jsonify, request
from rouk.db import get_db

bp = Blueprint("playlist", __name__, url_prefix='/api')

def get_playlist_tx(tx, id_):
    query = ('MATCH (s:Song)-[i:INCLUDED_IN]->(al:Playlist) WHERE id(al)=$id '
        'WITH s, i, al ORDER BY i.track RETURN id(al) as id, al.name as name, '
        'collect({id: id(s), track: i.track, name: s.name, duration:s.duration,'
        'year: s.year}) as songs'
    )
    return tx.run(query, id=id_).single().data()

def get_all_playlists(tx):
    query = ('MATCH (al:Playlist) RETURN id(al) as id, al.name as name')
    return [item.data() for item in tx.run(query)]

def search_playlists(tx, text):
    query = (
        'CALL db.index.fulltext.queryNodes("searchPlaylist", $text) '
        'YIELD node,score MATCH (node) RETURN id(node) as id, node.name as name'
    )

    result = tx.run(query, index_name='searchPlaylist', text=text)
    return [song.data() for song in result]

def create_playlist(tx, name, songs):
    songs = [{'track': i+1, 'id': song} for i, song in enumerate(songs) if not song is None]
    query = 'CREATE (p:Playlist {name: $name})'
    if len(songs) > 0:
        query += (
            'WITH p UNWIND $songs as song MATCH (s:Song) WHERE id(s)=song.id '
            'CREATE (s)-[:INCLUDED_IN {track: song.track}]->(p) RETURN p.id as id'
        )
    return tx.run(query, name=name, songs=songs, size=len(songs)).single().data()['id']

def add_songs(tx, playlist_id, songs):
    songs = [{'track': i+1, 'id': song} for i, song in enumerate(songs) if not song is None]
    if len(songs) == 0: return
    query = (
        'MATCH (p:Playlist) WHERE id(p)=$id WITH p '
        'MATCH q =(:Song)-[:INCLUDED_IN]->(p) '
        'WITH p, length(q) as len UNWIND $songs as song '
        'MATCH (s:Song) WHERE id(s)=song.id '
        'MERGE (s)-[:INCLUDED_IN {track: len + song.track}]->(p)'
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

@bp.route('/playlist/<int:id_>')
def get_playlist(id_):
    with get_db().session() as session:
        result = session.read_transaction(get_playlist_tx, id_)
    return jsonify(result)

@bp.route('/playlist', methods=['POST'])
def create_playlist_():
    data = request.json
    name = data.get('name', None)
    songs = data.get('songs', [])
    if name is None: return Response('"name" is required', 400)
    neo4j = get_db()
    with neo4j.session() as session:
        playlist_id = session.write_transaction(create_playlist, name, songs)

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