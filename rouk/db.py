import click
from neo4j import GraphDatabase
from flask import current_app, g
from flask.cli import with_appcontext


def init_app(app):
    app.config.setdefault('NEO4J_URI', 'neo4j://localhost:7687')
    app.teardown_appcontext(teardown)
    app.cli.add_command(init_db_command)
    app.cli.add_command(db_console_command)

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
    neo4j = get_db()
    with neo4j.session() as session:
        for label in ['Song', 'Playlist', 'Album', 'Artist']:
            session.write_transaction(create_indexes, label)

@click.command("init-db")
@with_appcontext
def init_db_command():
    init_db()
    click.echo("Initialized the database.")


def run_query(tx, query):
    print(query)
    return tx.run(query)

@click.command("db-console")
@with_appcontext
def db_console_command():
    fn = lambda tx, query: tx.run(query)
    neo4j = get_db()
    session = neo4j.session()
    try:
        while True:
            x = input('-> ')
            if x == 'q':
                break
            if x[0] == 'w': res = session.write_transaction(run_query, x[2:])
            elif x[0] == 'r': res = session.read_transaction(run_query, x[2:])
            import pdb; pdb.set_trace()
    finally:
        session.close()
            
def get_db():
    if 'db' not in g:
        c = current_app.config
        g.db = GraphDatabase.driver(
            c['NEO4J_URI'], auth=(c['NEO4J_USER'], c["NEO4J_PASSWORD"])
        )
    return g.db