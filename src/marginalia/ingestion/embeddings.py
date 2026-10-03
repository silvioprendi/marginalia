from functools import lru_cache

from sentence_transformers import SentenceTransformer

from marginalia.config import settings


@lru_cache
def _model() -> SentenceTransformer:
    # Loaded once per process: it is ~90MB and takes seconds to initialise.
    return SentenceTransformer(settings.embedding_model)


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed texts as unit-length vectors, so cosine distance behaves well."""
    if not texts:
        return []
    vectors = _model().encode(texts, normalize_embeddings=True, batch_size=32)
    return vectors.tolist()
