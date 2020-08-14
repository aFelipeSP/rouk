from rouk.db import get_db
from rouk.player.update_library import update_library
from queue import Queue

def test_update_library(app):
    with app.app_context():
        neo4j = get_db()
    q = Queue()
    update_library(q, neo4j, app.config['MUSIC_ROOT'])

