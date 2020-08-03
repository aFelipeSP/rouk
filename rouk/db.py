from neo4j import GraphDatabase
from flask import current_app, g


def init_app(app):
    app.config.setdefault('NEO4J_URI', 'neo4j://localhost:7687')
    app.teardown_appcontext(self.teardown)

def teardown(exception):
    db = g.pop("db", None)
    if db is not None:
        db.close()

def get_db():
    if 'db' not in g:
        c = current_app.config
        g.db = GraphDatabase.driver(
            c['NEO4J_URI'], auth=(c['NEO4J_USER'], c["NEO4J_PASSWORD"])
        )
    return g.db