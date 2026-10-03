import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from marginalia.db import SessionLocal
from marginalia.main import app
from marginalia.models import Chunk, Document

pytestmark = pytest.mark.db

client = TestClient(app)


def test_upload_text_stores_document_and_embedded_chunks():
    text = "Penetration test findings. " * 100
    response = client.post("/documents", files={"file": ("report.txt", text.encode())})
    assert response.status_code == 201
    body = response.json()
    assert body["page_count"] == 1 and body["chunk_count"] > 1

    with SessionLocal() as session:
        try:
            chunks = session.scalars(select(Chunk).where(Chunk.document_id == body["id"])).all()
            assert len(chunks) == body["chunk_count"]
            assert all(len(c.embedding) == 384 and c.page_number == 1 for c in chunks)
        finally:  # leave the dev database clean
            session.delete(session.get(Document, body["id"]))
            session.commit()


def test_unsupported_file_type_is_rejected():
    response = client.post("/documents", files={"file": ("image.png", b"\x89PNG")})
    assert response.status_code == 422
