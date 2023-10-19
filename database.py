# from flask import g
# import sqlite3

# def connect_db():
#     sql = sqlite3.connect('D:\flask udemy\section 5/questions.db')
#     sql.row_factory = sqlite3.Row
#     return sql

# def get_db():
#     if not hasattr(g, 'sqlite_db'):
#         g.sqlite_db = connect_db()
#     return g.sqlite_db

from flask import g
import sqlite3
import os

def connect_db():
    db_path = os.path.join(os.path.dirname(__file__), 'questions.db')
    sql = sqlite3.connect(db_path)
    sql.row_factory = sqlite3.Row
    return sql

def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

# @app.teardown_appcontext
# def close_db(error):
#     if hasattr(g, 'sqlite_db'):
#         g.sqlite_db.close()