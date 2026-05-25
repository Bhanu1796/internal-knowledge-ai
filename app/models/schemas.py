from pydantic import BaseModel, Field
from typing import List, Optional


# ─── Pipeline Internal Models ─────────────────────────────────────────────────

class QueryContext(BaseModel):
    raw_query: str
    intent: str = "UNKNOWN"
    reformulated_query: str
    key_entities: List[str] = Field(default_factory=list)


class DocumentChunk(BaseModel):
    chunk_id: str
    content: str
    source: str
    doc_url: str
    page: int = 0
    score: float = 0.0


class SearchResult(BaseModel):
    query_context: QueryContext
    chunks: List[DocumentChunk] = Field(default_factory=list)


class GeneratedAnswer(BaseModel):
    search_result: SearchResult
    answer_text: str
    has_answer: bool = True


# ─── API Request / Response Models ────────────────────────────────────────────

class QueryRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)
    top_k: Optional[int] = Field(default=None, ge=1, le=20)


class SourceLink(BaseModel):
    title: str
    url: str
    source_file: str
    page: int
    score: float


class QueryResponse(BaseModel):
    question: str
    answer: str
    intent: str
    has_answer: bool
    sources: List[SourceLink]
    processing_time_ms: int


class DocumentInfo(BaseModel):
    title: str
    source_file: str
    url: str
    chunk_count: int


class DocumentListResponse(BaseModel):
    total_chunks: int
    total_documents: int
    documents: List[DocumentInfo]


class HealthResponse(BaseModel):
    status: str
    vector_store_docs: int
