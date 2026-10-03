from itertools import pairwise

import pytest

from marginalia.ingestion.chunking import chunk_pages
from marginalia.ingestion.parsing import Page


def test_short_page_is_one_chunk():
    chunks = chunk_pages([Page(1, "hello   world\nagain")], chunk_size=100, overlap=10)
    assert [(c.page_number, c.text) for c in chunks] == [(1, "hello world again")]


def test_chunks_never_span_pages_and_keep_page_numbers():
    pages = [Page(1, "a " * 100), Page(2, "b " * 100)]
    chunks = chunk_pages(pages, chunk_size=50, overlap=10)
    assert {c.page_number for c in chunks} == {1, 2}
    for c in chunks:
        assert set(c.text.split()) == ({"a"} if c.page_number == 1 else {"b"})


def test_chunks_respect_size_and_overlap_and_lose_no_words():
    words = [f"w{i}" for i in range(200)]
    chunks = chunk_pages([Page(1, " ".join(words))], chunk_size=60, overlap=15)
    assert len(chunks) > 1
    assert all(len(c.text) <= 60 for c in chunks)
    # consecutive chunks share words (overlap), and together cover every word in order
    for prev, nxt in pairwise(chunks):
        assert prev.text.split()[-1] in nxt.text.split()
    covered = dict.fromkeys(w for c in chunks for w in c.text.split())
    assert list(covered) == words


def test_empty_page_produces_no_chunks():
    assert chunk_pages([Page(1, "  \n ")], chunk_size=100, overlap=10) == []


def test_word_longer_than_chunk_size_still_terminates():
    chunks = chunk_pages([Page(1, "x" * 300 + " tail")], chunk_size=50, overlap=10)
    assert chunks[0].text == "x" * 300
    assert chunks[-1].text.endswith("tail")


def test_overlap_must_be_smaller_than_chunk_size():
    with pytest.raises(ValueError):
        chunk_pages([Page(1, "x")], chunk_size=10, overlap=10)
