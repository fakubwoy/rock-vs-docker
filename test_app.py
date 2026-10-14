import os, tempfile
os.environ["NOTES_DB"] = os.path.join(tempfile.mkdtemp(), "t.db")
from app import app


def test_notes_roundtrip():
    c = app.test_client()
    assert c.get("/health").json == {"status": "ok"}
    assert c.post("/notes", json={"text": ""}).status_code == 400
    assert c.post("/notes", json={"text": "hi"}).status_code == 201
    assert c.get("/notes").json == [{"id": 1, "text": "hi"}]
