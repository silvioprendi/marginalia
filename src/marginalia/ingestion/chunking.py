from dataclasses import dataclass

from marginalia.ingestion.parsing import Page


@dataclass(frozen=True)
class TextChunk:
    page_number: int
    text: str


def chunk_pages(pages: list[Page], chunk_size: int, overlap: int) -> list[TextChunk]:
    """Split each page into overlapping chunks.

    Chunks never span pages, so every chunk maps to exactly one page number for citations.
    Splits happen on word boundaries; `overlap` characters are repeated at the start of the next
    chunk so a sentence cut at a boundary still appears whole in one of the two chunks.
    """
    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    return [
        TextChunk(page_number=page.number, text=text)
        for page in pages
        for text in _split_words(page.text.split(), chunk_size, overlap)
    ]


def _split_words(words: list[str], chunk_size: int, overlap: int) -> list[str]:
    texts: list[str] = []
    start = 0
    while start < len(words):
        end = _chunk_end(words, start, chunk_size)
        texts.append(" ".join(words[start:end]))
        if end == len(words):
            break
        start = _next_start(words, start, end, overlap)
    return texts


def _chunk_end(words: list[str], start: int, chunk_size: int) -> int:
    """Index just past the last word that fits in `chunk_size`; always takes at least one word."""
    end, length = start + 1, len(words[start]) + 1
    while end < len(words) and length + len(words[end]) + 1 <= chunk_size:
        length += len(words[end]) + 1
        end += 1
    return end


def _next_start(words: list[str], start: int, end: int, overlap: int) -> int:
    """Step back from `end` to repeat roughly `overlap` characters, but always advance."""
    back, carried = end, 0
    while back > start + 1 and carried + len(words[back - 1]) + 1 <= overlap:
        back -= 1
        carried += len(words[back]) + 1
    return back
