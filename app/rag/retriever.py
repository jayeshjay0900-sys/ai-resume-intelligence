from pathlib import Path
import json
import os
import re

import faiss
import numpy as np

from app.services.embedding_service import create_embedding


VECTORSTORE_DIR = Path("data/vectorstore")

INDEX_PATH = VECTORSTORE_DIR / "index.faiss"
CHUNKS_PATH = VECTORSTORE_DIR / "chunks.json"

LLM_PROVIDER = os.getenv(
    "LLM_PROVIDER",
    "ollama"
).lower()


def load_chunks():
    """
    Load knowledge-base chunks from chunks.json.
    """

    if not CHUNKS_PATH.exists():
        raise FileNotFoundError(
            "chunks.json not found. Run: python -m app.rag.ingest"
        )

    with open(
        CHUNKS_PATH,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def load_vectorstore():

    if not INDEX_PATH.exists():
        raise FileNotFoundError(
            "FAISS index not found. Run: python -m app.rag.ingest"
        )

    chunks = load_chunks()

    index = faiss.read_index(
        str(INDEX_PATH)
    )

    return index, chunks


def keyword_search(
    query: str,
    chunks: list,
    top_k: int = 5
):
    """
    Lightweight keyword-based retrieval.

    Used for cloud/Groq deployment so that the
    Sentence Transformer model does not need to load.
    """

    query_words = set(
        re.findall(
            r"\b[a-zA-Z0-9+#.-]+\b",
            query.lower()
        )
    )

    scored_chunks = []

    for chunk in chunks:

        text = chunk.get(
            "text",
            ""
        )

        text_words = set(
            re.findall(
                r"\b[a-zA-Z0-9+#.-]+\b",
                text.lower()
            )
        )

        overlap = query_words.intersection(
            text_words
        )

        score = len(overlap)

        if score > 0:

            scored_chunks.append(
                (
                    score,
                    chunk
                )
            )

    scored_chunks.sort(
        key=lambda item: item[0],
        reverse=True
    )

    results = []

    for score, chunk in scored_chunks[:top_k]:

        results.append({
            "text": chunk["text"],
            "source": chunk["source"],
            "distance": float(
                1.0 / (1.0 + score)
            )
        })

    return results


def search_knowledge_base(
    query: str,
    top_k: int = 5
):
    """
    Search the ResumeIQ knowledge base.

    Local/Ollama:
        FAISS + Sentence Transformer

    Cloud/Groq:
        Lightweight keyword retrieval
    """

    if LLM_PROVIDER == "groq":

        chunks = load_chunks()

        return keyword_search(
            query,
            chunks,
            top_k
        )

    # -----------------------------------------------------
    # Local FAISS retrieval
    # -----------------------------------------------------

    index, chunks = load_vectorstore()

    query_embedding = create_embedding(
        query
    )

    query_embedding = np.array(
        [query_embedding],
        dtype="float32"
    )

    distances, indices = index.search(
        query_embedding,
        top_k
    )

    results = []

    for distance, index_id in zip(
        distances[0],
        indices[0]
    ):

        if index_id == -1:
            continue

        chunk = chunks[index_id]

        results.append({
            "text": chunk["text"],
            "source": chunk["source"],
            "distance": float(distance)
        })

    return results


if __name__ == "__main__":

    query = input(
        "Enter your search query: "
    )

    results = search_knowledge_base(
        query,
        top_k=5
    )

    print("\nTop results:\n")

    for number, result in enumerate(
        results,
        start=1
    ):

        print(
            f"Result {number}"
        )

        print(
            f"Source: {result['source']}"
        )

        print(
            f"Distance: {result['distance']:.4f}"
        )

        print(
            f"Text: {result['text']}"
        )

        print("-" * 60)

