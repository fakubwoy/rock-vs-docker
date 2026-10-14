import os
import sqlite3
from flask import Flask, jsonify, request, g

app = Flask(__name__)
DB = os.environ.get("NOTES_DB", "/tmp/notes.db")


def db():
    if "db" not in g:
        g.db = sqlite3.connect(DB)
        g.db.execute("CREATE TABLE IF NOT EXISTS notes (id INTEGER PRIMARY KEY, text TEXT NOT NULL)")
    return g.db


@app.teardown_appcontext
def close_db(_):
    conn = g.pop("db", None)
    if conn:
        conn.close()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/notes")
def list_notes():
    rows = db().execute("SELECT id, text FROM notes ORDER BY id").fetchall()
    return jsonify([{"id": i, "text": t} for i, t in rows])


@app.post("/notes")
def add_note():
    text = (request.get_json(silent=True) or {}).get("text", "").strip()
    if not text:
        return {"error": "text is required"}, 400
    cur = db().execute("INSERT INTO notes (text) VALUES (?)", (text,))
    db().commit()
    return {"id": cur.lastrowid, "text": text}, 201
