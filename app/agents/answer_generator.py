import logging

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from app.core.config import get_settings
from app.models.schemas import GeneratedAnswer, SearchResult

logger = logging.getLogger(__name__)
settings = get_settings()

FALLBACK_MESSAGE = (
    "I could not find relevant information in the knowledge base for your query. "
    "Please contact your HR or IT helpdesk directly."
)

SYSTEM_PROMPT = """You are a helpful internal knowledge base assistant for a company.

Your job is to answer employee questions using ONLY the information provided in the context below. The context comes from official company documents.

Rules you must follow:
1. Answer directly and concisely. Avoid unnecessary preamble.
2. Use ONLY the information in the provided context. Do not use any outside knowledge.
3. If the context does not contain enough information to answer the question, respond with exactly: "I could not find relevant information in the knowledge base for your query. Please contact your HR or IT helpdesk directly."
4. If the answer spans multiple documents, synthesise the information coherently.
5. Do not mention the document filenames or chunk IDs in your answer.
6. Use plain, professional language suitable for an employee-facing assistant.
7. If the answer involves a process or steps, use a numbered list."""

PROMPT = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", "Context:\n{context}\n\n---\n\nEmployee question: {question}\n\nAnswer:"),
])


def _build_context(search_result: SearchResult) -> str:
    parts = []
    for chunk in search_result.chunks:
        parts.append(
            f"[Source: {chunk.source} | Page {chunk.page}]\n{chunk.content}"
        )
    return "\n\n".join(parts)


def _get_llm() -> ChatOpenAI:
    return ChatOpenAI(
        model=settings.llm_model,
        openai_api_key=settings.litellm_api_key,
        openai_api_base=settings.litellm_proxy_url,
        temperature=0,
    )


def run(input_data: dict) -> dict:
    search_result: SearchResult = input_data["search_result"]

    if not search_result.chunks:
        logger.info("No chunks found — returning fallback answer.")
        return {
            "generated_answer": GeneratedAnswer(
                search_result=search_result,
                answer_text=FALLBACK_MESSAGE,
                has_answer=False,
            )
        }

    context = _build_context(search_result)
    raw_query = search_result.query_context.raw_query

    llm = _get_llm()
    chain = PROMPT | llm
    response = chain.invoke({"context": context, "question": raw_query})
    answer_text = response.content.strip()

    has_answer = FALLBACK_MESSAGE.lower() not in answer_text.lower()
    logger.info("Answer generated. has_answer=%s", has_answer)

    return {
        "generated_answer": GeneratedAnswer(
            search_result=search_result,
            answer_text=answer_text,
            has_answer=has_answer,
        )
    }
