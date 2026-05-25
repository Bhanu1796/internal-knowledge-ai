import json
import logging

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from app.core.config import get_settings
from app.models.schemas import QueryContext

logger = logging.getLogger(__name__)
settings = get_settings()

SYSTEM_PROMPT = """You are an internal knowledge base assistant that helps employees find company information.

Your task is to analyse the employee's question and return a structured JSON response with the following fields:

- "intent": Classify the question into exactly one of these categories:
    - "PROCESS_INQUIRY"   — How to complete a task or follow a process
    - "POLICY_LOOKUP"     — What the rules, policies, or guidelines say
    - "CONTACT_LOOKUP"    — Who to contact or who is responsible for something
    - "GENERAL_INFO"      — General factual questions about the company
    - "UNKNOWN"           — Cannot be determined

- "reformulated_query": Rewrite the question as a clear, keyword-rich sentence optimised
  for semantic search. Remove filler words, expand acronyms, and make implicit context
  explicit. Do NOT answer the question — only reformulate it.

- "key_entities": A list of the most important nouns and topics in the question (maximum 5 items).

Return ONLY valid JSON. No explanation, no markdown, no code fences."""

RETRY_PROMPT = """You previously returned an invalid response. Please try again.

Employee question: {raw_query}

You MUST return valid JSON only, with exactly these fields:
- "intent" (string)
- "reformulated_query" (string)
- "key_entities" (array of strings)

No explanation. No markdown. No code fences. JSON only."""

PROMPT = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", "Employee question: {raw_query}"),
])

RETRY_PROMPT_TEMPLATE = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", RETRY_PROMPT),
])


def _get_llm() -> ChatOpenAI:
    return ChatOpenAI(
        model=settings.llm_model,
        openai_api_key=settings.litellm_api_key,
        openai_api_base=settings.litellm_proxy_url,
        temperature=0,
    )


def _parse_response(raw_query: str, content: str) -> QueryContext:
    cleaned = content.strip().strip("```json").strip("```").strip()
    data = json.loads(cleaned)
    return QueryContext(
        raw_query=raw_query,
        intent=data.get("intent", "UNKNOWN"),
        reformulated_query=data.get("reformulated_query", raw_query),
        key_entities=data.get("key_entities", []),
    )


def run(input_data: dict) -> dict:
    raw_query: str = input_data["raw_query"]
    llm = _get_llm()
    chain = PROMPT | llm

    for attempt in range(2):
        try:
            if attempt == 0:
                response = chain.invoke({"raw_query": raw_query})
            else:
                logger.warning("Retrying query understanding (attempt 2)...")
                retry_chain = RETRY_PROMPT_TEMPLATE | llm
                response = retry_chain.invoke({"raw_query": raw_query})

            query_context = _parse_response(raw_query, response.content)
            logger.info(
                "Intent: %s | Reformulated: %s",
                query_context.intent,
                query_context.reformulated_query,
            )
            return {"query_context": query_context}

        except (json.JSONDecodeError, KeyError) as e:
            logger.warning("Query understanding parse error (attempt %d): %s", attempt + 1, e)

    logger.error("Query understanding failed after 2 attempts. Using fallback.")
    return {
        "query_context": QueryContext(
            raw_query=raw_query,
            intent="UNKNOWN",
            reformulated_query=raw_query,
            key_entities=[],
        )
    }
