import io
from dataclasses import dataclass

from pypdf import PdfReader
from pypdf.errors import PyPdfError


class UnsupportedDocumentError(ValueError):
    pass


@dataclass(frozen=True)
class Page:
    number: int  # 1-based, used for citations
    text: str


def parse_document(filename: str, data: bytes) -> list[Page]:
    """Turn an uploaded file into pages of text. Plain text files count as a single page."""
    name = filename.lower()
    if name.endswith(".pdf"):
        return _parse_pdf(data)
    if name.endswith((".txt", ".md")):
        try:
            return [Page(number=1, text=data.decode("utf-8"))]
        except UnicodeDecodeError as exc:
            raise UnsupportedDocumentError("Text files must be UTF-8 encoded") from exc
    raise UnsupportedDocumentError("Only .pdf, .txt and .md files are supported")


def _parse_pdf(data: bytes) -> list[Page]:
    try:
        reader = PdfReader(io.BytesIO(data))
        return [Page(number=i, text=p.extract_text() or "") for i, p in enumerate(reader.pages, 1)]
    except PyPdfError as exc:
        raise UnsupportedDocumentError("Could not read PDF") from exc
