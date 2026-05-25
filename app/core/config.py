from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # LiteLLM Proxy
    litellm_proxy_url: str = "http://litellm.amzur.com:4000"
    litellm_api_key: str = ""
    llm_model: str = "gemini/gemini-2.5-flash"
    litellm_embedding_model: str = "text-embedding-3-large"

    # ChromaDB
    chroma_persist_dir: str = "./chroma_db"
    chroma_collection_name: str = "knowledge_base"

    # Document ingestion
    docs_path: str = "./data/sample_docs"
    doc_base_url: str = "https://confluence.internal/pages"
    chunk_size: int = 800
    chunk_overlap: int = 100

    # Search
    search_top_k: int = 5
    search_min_score: float = 0.30

    # FastAPI
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    log_level: str = "INFO"

    # Streamlit
    api_base_url: str = "http://localhost:8000"


@lru_cache
def get_settings() -> Settings:
    return Settings()
