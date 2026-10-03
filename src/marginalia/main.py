from fastapi import FastAPI

from marginalia import __version__
from marginalia.api_documents import router as documents_router

app = FastAPI(title="Marginalia", version=__version__)
app.include_router(documents_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "version": __version__}
