import click
from neo4j import GraphDatabase
from flask import current_app, g
from flask.cli import with_appcontext


def init_app(app):
    app.config.setdefault('NEO4J_URI', 'neo4j://localhost:7687')
    app.teardown_appcontext(teardown)
    app.cli.add_command(init_db_command)

def teardown(exception):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def create_indexes(tx, label):
    query = (
        'CALL db.index.fulltext.createNodeIndex("search{0}",["{0}"],["name"])'
    ).format(label)
    tx.run(query)

def init_db():
    """Clear existing data and create new tables."""
    neo4j = get_db()
    with neo4j.session() as session:
        for label in ['Song', 'Playlist', 'Album', 'Artist']:
            session.write_transaction(create_indexes, label)

@click.command("init-db")
@with_appcontext
def init_db_command():
    """Clear existing data and create new tables."""
    init_db()
    click.echo("Initialized the database.")


def get_db():
    if 'db' not in g:
        c = current_app.config
        g.db = GraphDatabase.driver(
            c['NEO4J_URI'], auth=(c['NEO4J_USER'], c["NEO4J_PASSWORD"])
        )
    return g.db