import pytest
from sqlalchemy import select

from marginalia.config import settings
from marginalia.db import SessionLocal
from marginalia.models import Chunk, Document

pytestmark = pytest.mark.db


def vec(i: int) -> list[float]:
    v = [0.0] * settings.embedding_dim
    v[i] = 1.0
    return v


def test_chunk_roundtrip_and_nearest_neighbour():
    with SessionLocal() as session, session.begin():
        doc = Document(filename="report.pdf", page_count=2)
        doc.chunks = [
            Chunk(page_number=1, chunk_index=0, content="alpha", embedding=vec(0)),
            Chunk(page_number=2, chunk_index=1, content="beta", embedding=vec(1)),
        ]
        session.add(doc)
        session.flush()

        nearest = session.scalars(
            select(Chunk)
            .where(Chunk.document_id == doc.id)
            .order_by(Chunk.embedding.cosine_distance(vec(1)))
            .limit(1)
        ).one()
        assert (nearest.content, nearest.page_number) == ("beta", 2)

        session.rollback()  # leave the dev database clean
