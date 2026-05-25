import logging
import time

from langchain_core.runnables import RunnableLambda

from app.agents import query_understanding, search_agent, answer_generator, source_linker
from app.models.schemas import QueryResponse, SourceLink

logger = logging.getLogger(__name__)

pipeline = (
    RunnableLambda(query_understanding.run)
    | RunnableLambda(search_agent.run)
    | RunnableLambda(answer_generator.run)
    | RunnableLambda(source_linker.run)
)


def run_pipeline(question: str, top_k: int | None = None) -> QueryResponse:
    start = time.monotonic()

    result = pipeline.invoke({"raw_query": question, "top_k": top_k})

    elapsed_ms = int((time.monotonic() - start) * 1000)
    logger.info("Pipeline completed in %dms", elapsed_ms)

    return QueryResponse(
        question=question,
        answer=result["answer_text"],
        intent=result["intent"],
        has_answer=result["has_answer"],
        sources=result["sources"],
        processing_time_ms=elapsed_ms,
    )
