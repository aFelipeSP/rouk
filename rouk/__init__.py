import os
from flask import Flask, send_file
from pathlib import Path
from flask_cors import CORS
    

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    CORS(app)

    app.config.from_mapping(
        SECRET_KEY="dev"
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        app.config.update(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from rouk import db
    db.init_app(app)

    from rouk import player
    player.init_app(app)

    from rouk.views import (
        album, artist, commands, play, playlist, song, stream
    )
    for view in (album, artist, commands, play, playlist, song, stream):
        app.register_blueprint(view.bp)

    # def index(path): return send_file(str(Path('static/index.html')))
    # app.add_url_rule('/', 'index', index, defaults={'path': ''})
    # app.add_url_rule('/<path:path>', 'index', index)

    return app