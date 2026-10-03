from pathlib import Path
import json

import faiss
import numpy as np

from app.services.embedding_service import create_embedding


VECTORSTORE_DIR = Path("data/vectorstore")

INDEX_PATH = VECTORSTORE_DIR / "index.faiss"
CHUNKS_PATH = VECTORSTORE_DIR / "chunks.json"


def load_vectorstore():

    if not INDEX_PATH.exists():
        raise FileNotFoundError(
            "FAISS index not found. Run: python -m app.rag.ingest"
        )

    if not CHUNKS_PATH.exists():
        raise FileNotFoundError(
            "chunks.json not found. Run: python -m app.rag.ingest"
        )

    index = faiss.read_index(
        str(INDEX_PATH)
    )

    with open(
        CHUNKS_PATH,
        "r",
        encoding="utf-8"
    ) as file:

        chunks = json.load(file)

    return index, chunks


def search_knowledge_base(
    query: str,
    top_k: int = 5
):

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