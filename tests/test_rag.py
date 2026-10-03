from app.rag.retriever import (
    search_knowledge_base
)


def test_rag_search():

    results = search_knowledge_base(
        "machine learning",
        top_k=3
    )

    assert isinstance(
        results,
        list
    )

    assert len(results) <= 3

    if results:

        assert "text" in results[0]

        assert "source" in results[0]

        assert "distance" in results[0]