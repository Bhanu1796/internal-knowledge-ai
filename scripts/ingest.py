import argparse
import logging
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.ingestion.document_loader import load_and_chunk
from app.ingestion.embedder import embed_and_store

logging.basicConfig(
    level=logging.INFO,
    format="[Ingest] %(message)s",
)
logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ingest documents into ChromaDB.")
    parser.add_argument(
        "--docs-path",
        type=str,
        default=None,
        help="Path to the docs directory (defaults to DOCS_PATH in .env)",
    )
    parser.add_argument(
        "--no-reset",
        action="store_true",
        help="Append to existing collection instead of wiping and rebuilding",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    reset = not args.no_reset
    start = time.time()

    logger.info("Loading documents from %s ...", args.docs_path or "default DOCS_PATH")
    chunks = load_and_chunk(docs_path=args.docs_path)

    if not chunks:
        logger.error("No chunks produced. Check that DOCS_PATH contains supported files.")
        sys.exit(1)

    logger.info("Loaded %d chunks total.", len(chunks))
    embed_and_store(chunks, reset=reset)

    elapsed = time.time() - start
    logger.info("Done. Time elapsed: %.1fs", elapsed)


if __name__ == "__main__":
    main()
