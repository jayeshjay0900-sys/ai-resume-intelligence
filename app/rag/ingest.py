from pathlib import Path
import json

import faiss
import numpy as np

from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.services.pdf_service import extract_text_from_pdf
from app.services.embedding_service import create_embedding


KNOWLEDGE_BASE_DIR = Path("knowledge_base")
VECTORSTORE_DIR = Path("data/vectorstore")

VECTORSTORE_DIR.mkdir(
    parents=True,
    exist_ok=True
)


def load_documents():

    documents = []

    for pdf_file in KNOWLEDGE_BASE_DIR.glob("*.pdf"):

        text = extract_text_from_pdf(
            str(pdf_file)
        )

        if text.strip():

            documents.append({
                "source": pdf_file.name,
                "text": text
            })

    return documents


def create_chunks(documents):

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=80
    )

    chunks = []

    for document in documents:

        split_texts = splitter.split_text(
            document["text"]
        )

        for text in split_texts:

            chunks.append({
                "text": text,
                "source": document["source"]
            })

    return chunks


def build_vectorstore():

    documents = load_documents()

    if not documents:

        raise ValueError(
            "No PDF documents found in knowledge_base."
        )

    chunks = create_chunks(
        documents
    )

    embeddings = [
        create_embedding(chunk["text"])
        for chunk in chunks
    ]

    embeddings = np.array(
        embeddings,
        dtype="float32"
    )

    dimension = embeddings.shape[1]

    index = faiss.IndexFlatL2(
        dimension
    )

    index.add(embeddings)

    faiss.write_index(
        index,
        str(
            VECTORSTORE_DIR /
            "index.faiss"
        )
    )

    with open(
        VECTORSTORE_DIR / "chunks.json",
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            chunks,
            file,
            indent=2,
            ensure_ascii=False
        )

    return {
        "documents": len(documents),
        "chunks": len(chunks),
        "vector_dimension": dimension
    }


if __name__ == "__main__":

    result = build_vectorstore()

    print(
        "RAG vector store created successfully."
    )

    print(
        f"Documents: {result['documents']}"
    )

    print(
        f"Chunks: {result['chunks']}"
    )

    print(
        f"Vector dimension: {result['vector_dimension']}"
    )