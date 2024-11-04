import sqlite3
from flask import g

def get_connection():
    db = sqlite3.connect("database.db")
    db.execute("PRAGMA foreign_keys = ON")
    db.row_factory = sqlite3.Row
    return db

def execute(sql, params=[]):
    db = get_connection()
    result = db.execute(sql, params)
    db.commit()
    g.last_insert_id = result.lastrowid
    db.close()

def query(sql, params=[]):
    db = get_connection()
    result = db.execute(sql, params).fetchall()
    db.close()
    return result

def last_insert_id():
    return g.last_insert_id
