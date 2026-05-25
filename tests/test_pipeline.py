from unittest.mock import MagicMock, patch

from app.models.schemas import DocumentChunk, QueryContext, SearchResult, GeneratedAnswer


# ─── Fixtures ─────────────────────────────────────────────────────────────────

def make_query_context(**kwargs) -> QueryContext:
    defaults = dict(
        raw_query="What is the annual leave policy?",
        intent="POLICY_LOOKUP",
        reformulated_query="annual leave policy entitlement days",
        key_entities=["annual leave", "policy"],
    )
    return QueryContext(**{**defaults, **kwargs})


def make_chunk(**kwargs) -> DocumentChunk:
    defaults = dict(
        chunk_id="annual-leave-policy_0_0",
        content="Employees are entitled to 20 days of annual leave per year.",
        source="annual-leave-policy.md",
        doc_url="https://confluence.internal/pages/annual-leave-policy",
        page=0,
        score=0.88,
    )
    return DocumentChunk(**{**defaults, **kwargs})


# ─── Stage 1: Query Understanding ─────────────────────────────────────────────
# The run() function does: llm = _get_llm(); chain = PROMPT | llm; chain.invoke(...)
# LangChain RunnableSequence calls llm.invoke(...) internally, so we mock that.

# LangChain RunnableSequence calls the LLM as a callable: llm(messages).
# Set mock_llm.return_value (not .invoke.return_value) to control the response.

@patch("app.agents.query_understanding._get_llm")
def test_query_understanding_returns_query_context(mock_get_llm):
    mock_response = MagicMock()
    mock_response.content = '{"intent": "POLICY_LOOKUP", "reformulated_query": "annual leave policy days", "key_entities": ["annual leave"]}'
    mock_llm = MagicMock()
    mock_llm.return_value = mock_response  # llm(messages) in RunnableSequence
    mock_get_llm.return_value = mock_llm

    from app.agents.query_understanding import run

    result = run({"raw_query": "How many leave days do I get?"})

    assert "query_context" in result
    ctx = result["query_context"]
    assert ctx.intent == "POLICY_LOOKUP"
    assert ctx.reformulated_query == "annual leave policy days"
    assert "annual leave" in ctx.key_entities


@patch("app.agents.query_understanding._get_llm")
def test_query_understanding_fallback_on_bad_json(mock_get_llm):
    mock_response = MagicMock()
    mock_response.content = "this is not valid json"  # causes JSONDecodeError → fallback
    mock_llm = MagicMock()
    mock_llm.return_value = mock_response
    mock_get_llm.return_value = mock_llm

    from app.agents.query_understanding import run

    result = run({"raw_query": "some question"})
    ctx = result["query_context"]

    assert ctx.intent == "UNKNOWN"
    assert ctx.raw_query == "some question"


# ─── Stage 2: Search Agent ────────────────────────────────────────────────────

@patch("app.agents.search_agent.get_store")
def test_search_agent_returns_chunks(mock_get_store):
    mock_doc = MagicMock()
    mock_doc.page_content = "Employees get 20 days leave."
    mock_doc.metadata = {
        "chunk_id": "annual-leave-policy_0_0",
        "source": "annual-leave-policy.md",
        "doc_url": "https://confluence.internal/pages/annual-leave-policy",
        "page": 0,
    }

    mock_store = MagicMock()
    mock_store.similarity_search_with_relevance_scores.return_value = [(mock_doc, 0.91)]
    mock_get_store.return_value = mock_store

    from app.agents.search_agent import run

    query_context = make_query_context()
    result = run({"query_context": query_context, "top_k": 5})

    assert "search_result" in result
    sr = result["search_result"]
    assert len(sr.chunks) == 1
    assert sr.chunks[0].score == 0.91
    assert sr.chunks[0].source == "annual-leave-policy.md"


@patch("app.agents.search_agent.get_store")
def test_search_agent_filters_low_score(mock_get_store):
    mock_doc = MagicMock()
    mock_doc.page_content = "Some irrelevant content."
    mock_doc.metadata = {
        "chunk_id": "other_0_0",
        "source": "other.md",
        "doc_url": "https://confluence.internal/pages/other",
        "page": 0,
    }

    mock_store = MagicMock()
    mock_store.similarity_search_with_relevance_scores.return_value = [(mock_doc, 0.10)]
    mock_get_store.return_value = mock_store

    from app.agents.search_agent import run

    result = run({"query_context": make_query_context(), "top_k": 5})
    assert result["search_result"].chunks == []


# ─── Stage 3: Answer Generator ────────────────────────────────────────────────

@patch("app.agents.answer_generator._get_llm")
def test_answer_generator_with_chunks(mock_get_llm):
    mock_response = MagicMock()
    mock_response.content = "Employees are entitled to 20 days of annual leave per year."
    mock_llm = MagicMock()
    mock_llm.return_value = mock_response  # llm(messages) in RunnableSequence
    mock_get_llm.return_value = mock_llm

    from app.agents.answer_generator import run

    search_result = SearchResult(
        query_context=make_query_context(),
        chunks=[make_chunk()],
    )
    result = run({"search_result": search_result})

    assert "generated_answer" in result
    ga = result["generated_answer"]
    assert ga.has_answer is True
    assert "20 days" in ga.answer_text


def test_answer_generator_no_chunks_returns_fallback():
    from app.agents.answer_generator import run, FALLBACK_MESSAGE

    search_result = SearchResult(
        query_context=make_query_context(),
        chunks=[],
    )
    result = run({"search_result": search_result})

    ga = result["generated_answer"]
    assert ga.has_answer is False
    assert ga.answer_text == FALLBACK_MESSAGE


# ─── Stage 4: Source Linker ───────────────────────────────────────────────────

def test_source_linker_deduplicates_by_source():
    from app.agents.source_linker import run

    chunk1 = make_chunk(score=0.88)
    chunk2 = make_chunk(score=0.75)  # same source, lower score
    chunk3 = make_chunk(
        chunk_id="it-software-request_0_0",
        source="it-software-request.md",
        doc_url="https://confluence.internal/pages/it-software-request",
        score=0.70,
    )

    generated_answer = GeneratedAnswer(
        search_result=SearchResult(
            query_context=make_query_context(),
            chunks=[chunk1, chunk2, chunk3],
        ),
        answer_text="Some answer.",
        has_answer=True,
    )

    result = run({"generated_answer": generated_answer})

    assert len(result["sources"]) == 2
    assert result["sources"][0].score == 0.88  # highest score first


def test_source_linker_empty_chunks():
    from app.agents.source_linker import run

    generated_answer = GeneratedAnswer(
        search_result=SearchResult(
            query_context=make_query_context(),
            chunks=[],
        ),
        answer_text="No info found.",
        has_answer=False,
    )

    result = run({"generated_answer": generated_answer})
    assert result["sources"] == []
    assert result["has_answer"] is False
