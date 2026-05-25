import logging
from typing import List

import chromadb
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


def _get_embeddings() -> OpenAIEmbeddings:
    return OpenAIEmbeddings(
        model=settings.litellm_embedding_model,
        openai_api_key=settings.litellm_api_key,
        openai_api_base=settings.litellm_proxy_url,
    )


def get_vector_store() -> Chroma:
    return Chroma(
        collection_name=settings.chroma_collection_name,
        embedding_function=_get_embeddings(),
        persist_directory=settings.chroma_persist_dir,
    )


def embed_and_store(chunks: List[Document], reset: bool = True) -> Chroma:
    if reset:
        logger.info("Resetting ChromaDB collection '%s' ...", settings.chroma_collection_name)
        client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
        try:
            client.delete_collection(settings.chroma_collection_name)
            logger.info("Collection deleted.")
        except Exception:
            logger.info("Collection did not exist, creating fresh.")

    logger.info("Embedding %d chunks (model: %s) ...", len(chunks), settings.litellm_embedding_model)

    batch_size = 100
    texts = [c.page_content for c in chunks]
    metadatas = [c.metadata for c in chunks]
    ids = [c.metadata["chunk_id"] for c in chunks]

    vector_store = Chroma(
        collection_name=settings.chroma_collection_name,
        embedding_function=_get_embeddings(),
        persist_directory=settings.chroma_persist_dir,
    )

    for i in range(0, len(chunks), batch_size):
        batch_texts = texts[i : i + batch_size]
        batch_meta = metadatas[i : i + batch_size]
        batch_ids = ids[i : i + batch_size]
        vector_store.add_texts(texts=batch_texts, metadatas=batch_meta, ids=batch_ids)
        logger.info("  Batch %d/%d stored.", i // batch_size + 1, -(-len(chunks) // batch_size))

    count = vector_store._collection.count()
    logger.info("ChromaDB collection '%s' now contains %d documents.", settings.chroma_collection_name, count)
    return vector_store


def get_collection_count() -> int:
    try:
        client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
        collection = client.get_collection(settings.chroma_collection_name)
        return collection.count()
    except Exception:
        return 0
