import logging
import re
from pathlib import Path
from typing import List

from langchain_core.documents import Document
from langchain_community.document_loaders import (
    TextLoader,
    PyPDFLoader,
    Docx2txtLoader,
)
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

SUPPORTED_EXTENSIONS = {".md", ".pdf", ".docx", ".txt"}


def _filename_to_title(filename: str) -> str:
    stem = Path(filename).stem
    return stem.replace("-", " ").replace("_", " ").title()


def _filename_to_url(filename: str) -> str:
    stem = Path(filename).stem
    return f"{settings.doc_base_url}/{stem}"


def _load_file(file_path: Path) -> List[Document]:
    ext = file_path.suffix.lower()
    try:
        if ext == ".md":
            loader = TextLoader(str(file_path), encoding="utf-8")
        elif ext == ".pdf":
            loader = PyPDFLoader(str(file_path))
        elif ext == ".docx":
            loader = Docx2txtLoader(str(file_path))
        elif ext == ".txt":
            loader = TextLoader(str(file_path), encoding="utf-8")
        else:
            logger.warning("Skipping unsupported file type: %s", file_path.name)
            return []
        return loader.load()
    except Exception as e:
        logger.error("Failed to load %s: %s", file_path.name, e)
        return []


def load_and_chunk(docs_path: str | None = None) -> List[Document]:
    path = Path(docs_path or settings.docs_path)
    if not path.exists():
        raise FileNotFoundError(f"Docs directory not found: {path}")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    all_chunks: List[Document] = []
    files = [f for f in sorted(path.iterdir()) if f.suffix.lower() in SUPPORTED_EXTENSIONS]

    logger.info("Found %d supported files in %s", len(files), path)

    for file_path in files:
        raw_docs = _load_file(file_path)
        if not raw_docs:
            continue

        chunks = splitter.split_documents(raw_docs)

        title = _filename_to_title(file_path.name)
        doc_url = _filename_to_url(file_path.name)

        for i, chunk in enumerate(chunks):
            page = chunk.metadata.get("page", 0)
            chunk.metadata.update(
                {
                    "source": file_path.name,
                    "title": title,
                    "doc_url": doc_url,
                    "page": int(page),
                    "chunk_id": f"{file_path.stem}_{page}_{i}",
                }
            )

        all_chunks.extend(chunks)
        logger.info("  %s → %d chunks", file_path.name, len(chunks))

    logger.info("Total chunks created: %d", len(all_chunks))
    return all_chunks
