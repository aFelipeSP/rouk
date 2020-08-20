import os
from pathlib import Path

import click
from flask import current_app
from flask.cli import with_appcontext
from tinytag import TinyTag

from rouk.db import get_db

def init_app(app):
    app.cli.add_command(update_library_)

def add_song(tx, song, root, a):
    query = (
        'MERGE (ar:Artist {name: $artist})<-[by:BY]-(al:Album {name: $album, year: $year})'
        'MERGE (f:Folder {path: $path}) '
        'CREATE (al)<-[:INCLUDED_IN {track: $track}]-'
        '(s:Song {name: $title, year: $year, duration: $duration})-[:BY]->(ar) '
        'CREATE (f)-[:CONTAINS {name: $song}]->(s)'
    )
    tx.run(query, album=a.album, artist=a.artist, path=root, track=a.track,
        title=a.title, year=a.year, duration=a.duration, song=song)

def delete_songs(tx, songs, path):
    query = (
        'UNWIND $songs as song '
        'MATCH (s:Song)<-[:CONTAINS {name: song}]-(f:Folder {path: $path}) '
        'DETACH DELETE s'
    )
    tx.run(query, songs=songs, path=path)

def songs_in_folder(tx, path):
    query = 'MATCH (:Song)<-[c:CONTAINS]-(:Folder {path: $p}) RETURN c.name as s'
    return [song.data()['s'] for song in tx.run(query, p=path)]

def create_subfolders(tx, subfolders, path):
    query = (
        'UNWIND $subfolders as subfolder '
        'MERGE (r:Folder {path: $path}) '
        "MERGE (f:Folder {path: subfolder}) "
        'MERGE (f)-[:IS_SUBFOLDER]->(r)'
    )
    tx.run(query, subfolders=subfolders, path=path)

def delete_subfolders(tx, subfolders, path):
    query = (
        'MATCH (r:Folder {path: $path})<-[:IS_SUBFOLDER]-'
        '(f:Folder)-[:CONTAINS]->(s:Song) '
        'WHERE NOT f.path IN $subfolders DETACH DELETE f, s'
    )
    tx.run(query, subfolders=subfolders, path=path)

def update_library(neo4j, music_root):
    formats = ['m4a', 'mp3', 'wma', 'ogg', 'flac']
    for root, dirs, files in os.walk(Path(music_root)):
        dirs = [str(Path(root) / dr) for dr in dirs]

        with neo4j.session() as session:
            session.write_transaction(create_subfolders, dirs, root)
            session.write_transaction(delete_subfolders, dirs, root)

        music_files = [ff for ff in files if Path(ff).suffix[1:] in formats]

        with neo4j.session() as session:
            songs = session.read_transaction(songs_in_folder, root)
        songs_set = set(songs)
        files_set = set(music_files)
        new_songs = files_set - songs_set
        del_songs = songs_set - files_set
        len_new_songs, len_del_songs = [len(new_songs) > 0, len(del_songs) > 0]

        if len_new_songs:
            for song in new_songs:
                attrs = TinyTag.get(str(Path(root)/song))
                with neo4j.session() as session:
                    songs = session.write_transaction(add_song, song, root, attrs)

        if len_del_songs:
            with neo4j.session() as session:
                songs = session.write_transaction(delete_songs, list(del_songs), root)

    return True

@click.command("update-library")
@with_appcontext
def update_library_():
    music_root = current_app.config.get('MUSIC_ROOT')
    if music_root:
        neo4j = get_db()
        update_library(neo4j, music_root)