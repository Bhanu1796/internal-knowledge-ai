import logging
from typing import List

from langchain_chroma import Chroma

from app.core.config import get_settings
from app.ingestion.embedder import get_vector_store
from app.models.schemas import DocumentChunk, QueryContext, SearchResult

logger = logging.getLogger(__name__)
settings = get_settings()

_vector_store: Chroma | None = None


def get_store() -> Chroma:
    global _vector_store
    if _vector_store is None:
        _vector_store = get_vector_store()
    return _vector_store


def run(input_data: dict) -> dict:
    query_context: QueryContext = input_data["query_context"]
    top_k: int = input_data.get("top_k") or settings.search_top_k

    store = get_store()

    results = store.similarity_search_with_relevance_scores(
        query=query_context.reformulated_query,
        k=top_k,
    )

    chunks: List[DocumentChunk] = []
    for doc, score in results:
        if score < settings.search_min_score:
            continue
        meta = doc.metadata
        chunks.append(
            DocumentChunk(
                chunk_id=meta.get("chunk_id", ""),
                content=doc.page_content,
                source=meta.get("source", ""),
                doc_url=meta.get("doc_url", ""),
                page=int(meta.get("page", 0)),
                score=round(score, 4),
            )
        )

    chunks.sort(key=lambda c: c.score, reverse=True)
    logger.info("Search returned %d chunks above threshold %.2f", len(chunks), settings.search_min_score)

    return {
        "search_result": SearchResult(
            query_context=query_context,
            chunks=chunks,
        )
    }
