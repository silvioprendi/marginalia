from collections.abc import Iterator
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy.orm import Session

from marginalia.config import settings
from marginalia.db import SessionLocal
from marginalia.ingestion.parsing import UnsupportedDocumentError
from marginalia.ingestion.service import ingest_document

router = APIRouter(prefix="/documents", tags=["documents"])


def get_session() -> Iterator[Session]:
    with SessionLocal() as session:
        yield session


class DocumentOut(BaseModel):
    id: int
    filename: str
    page_count: int
    chunk_count: int


@router.post("", status_code=201)
def upload_document(
    file: UploadFile, session: Annotated[Session, Depends(get_session)]
) -> DocumentOut:
    if file.size is not None and file.size > settings.max_upload_bytes:
        raise HTTPException(413, "File too large")
    try:
        doc = ingest_document(session, file.filename or "unnamed", file.file.read())
    except UnsupportedDocumentError as exc:
        raise HTTPException(422, str(exc)) from exc
    return DocumentOut(
        id=doc.id, filename=doc.filename, page_count=doc.page_count, chunk_count=len(doc.chunks)
    )
