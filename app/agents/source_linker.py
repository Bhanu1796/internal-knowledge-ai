import logging
from typing import List

from app.models.schemas import GeneratedAnswer, SourceLink

logger = logging.getLogger(__name__)


def _filename_to_title(source: str) -> str:
    import re
    stem = source.rsplit(".", 1)[0]
    return stem.replace("-", " ").replace("_", " ").title()


def run(input_data: dict) -> dict:
    generated_answer: GeneratedAnswer = input_data["generated_answer"]
    chunks = generated_answer.search_result.chunks

    seen: dict[str, SourceLink] = {}
    for chunk in chunks:
        src = chunk.source
        if src not in seen or chunk.score > seen[src].score:
            seen[src] = SourceLink(
                title=_filename_to_title(src),
                url=chunk.doc_url,
                source_file=src,
                page=chunk.page,
                score=chunk.score,
            )

    sources: List[SourceLink] = sorted(
        seen.values(), key=lambda s: s.score, reverse=True
    )

    logger.info("Source linker produced %d unique sources.", len(sources))

    ctx = generated_answer.search_result.query_context
    return {
        "answer_text": generated_answer.answer_text,
        "has_answer": generated_answer.has_answer,
        "intent": ctx.intent,
        "sources": sources,
        "reformulated_query": ctx.reformulated_query,
        "key_entities": ctx.key_entities,
        "chunks_retrieved": len(chunks),
    }
