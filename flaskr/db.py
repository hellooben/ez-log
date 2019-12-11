# import sqlite3
# import psycopg2
import os

import click
from flask import current_app, g, Flask
import mysql.connector
from flask.cli import with_appcontext


def get_db():
    if 'db' not in g:
        db = mysql.connector.connect(
            host="localhost", user="root", passwd="genericpassword", database="ez-log-db")
        g.db = db
    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_db():
    db = get_db()

    cursor = db.cursor()

    with current_app.open_resource('schema.sql') as f:
        cursor.execute(f.read())
    db.commit()


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)


@click.command('init-db')
@with_appcontext
def init_db_command():
    init_db()
    click.echo('Initialized the database.')
