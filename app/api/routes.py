import logging
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse

from app.core.config import get_settings
from app.core.pipeline import run_pipeline
from app.ingestion.embedder import get_collection_count, get_vector_store
from app.models.schemas import (
    DocumentInfo,
    DocumentListResponse,
    HealthResponse,
    QueryRequest,
    QueryResponse,
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    count = get_collection_count()
    return HealthResponse(status="ok", vector_store_docs=count)


@router.post("/query", response_model=QueryResponse)
def query(request: QueryRequest) -> QueryResponse:
    try:
        return run_pipeline(question=request.question, top_k=request.top_k)
    except Exception as e:
        logger.exception("Pipeline error: %s", e)
        raise HTTPException(status_code=500, detail=f"Pipeline error: {str(e)}")


@router.get("/documents", response_model=DocumentListResponse)
def documents() -> DocumentListResponse:
    try:
        store = get_vector_store()
        collection = store._collection
        total_chunks = collection.count()

        results = collection.get(include=["metadatas"])
        metadatas = results.get("metadatas") or []

        doc_map: dict[str, dict] = {}
        for meta in metadatas:
            src = meta.get("source", "unknown")
            if src not in doc_map:
                doc_map[src] = {
                    "title": meta.get("title", src),
                    "source_file": src,
                    "url": meta.get("doc_url", ""),
                    "chunk_count": 0,
                }
            doc_map[src]["chunk_count"] += 1

        doc_list = [DocumentInfo(**v) for v in doc_map.values()]
        doc_list.sort(key=lambda d: d.title)

        return DocumentListResponse(
            total_chunks=total_chunks,
            total_documents=len(doc_list),
            documents=doc_list,
        )
    except Exception as e:
        logger.exception("Error fetching documents: %s", e)
        raise HTTPException(status_code=500, detail=f"Error fetching documents: {str(e)}")


@router.get("/documents/view/{filename}", response_class=HTMLResponse)
def view_document(filename: str) -> HTMLResponse:
    """Serve a raw document file as an HTML page for in-browser reading."""
    settings = get_settings()
    docs_dir = Path(settings.docs_path).resolve()
    # Prevent path traversal: resolve and confirm it stays inside docs_path
    target = (docs_dir / filename).resolve()
    if not str(target).startswith(str(docs_dir)):
        raise HTTPException(status_code=400, detail="Invalid filename.")
    if not target.exists() or not target.is_file():
        raise HTTPException(status_code=404, detail=f"Document '{filename}' not found.")

    content = target.read_text(encoding="utf-8")
    # Wrap in a minimal HTML page with readable styling
    title = filename.replace("-", " ").replace("_", " ").rsplit(".", 1)[0].title()
    escaped = content.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{title}</title>
  <style>
    body {{ font-family: system-ui, sans-serif; max-width: 860px; margin: 40px auto;
            padding: 0 24px; line-height: 1.7; color: #1e293b; }}
    pre  {{ white-space: pre-wrap; word-break: break-word; font-family: inherit;
            background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px;
            padding: 24px; font-size: 0.95rem; }}
    h1   {{ border-bottom: 2px solid #e2e8f0; padding-bottom: 12px; }}
  </style>
</head>
<body>
  <h1>{title}</h1>
  <pre>{escaped}</pre>
</body>
</html>"""
    return HTMLResponse(content=html)
