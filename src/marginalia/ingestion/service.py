from sqlalchemy.orm import Session

from marginalia.config import settings
from marginalia.ingestion.chunking import chunk_pages
from marginalia.ingestion.embeddings import embed_texts
from marginalia.ingestion.parsing import UnsupportedDocumentError, parse_document
from marginalia.models import Chunk, Document


def ingest_document(session: Session, filename: str, data: bytes) -> Document:
    pages = parse_document(filename, data)
    chunks = chunk_pages(pages, settings.chunk_size, settings.chunk_overlap)
    if not chunks:
        raise UnsupportedDocumentError("No extractable text (scanned PDFs need OCR)")

    vectors = embed_texts([c.text for c in chunks])
    document = Document(
        filename=filename,
        page_count=len(pages),
        chunks=[
            Chunk(page_number=c.page_number, chunk_index=i, content=c.text, embedding=v)
            for i, (c, v) in enumerate(zip(chunks, vectors, strict=True))
        ],
    )
    session.add(document)
    session.commit()
    return document
