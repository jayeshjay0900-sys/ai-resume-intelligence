import os
from functools import lru_cache

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

LLM_PROVIDER = os.getenv(
    "LLM_PROVIDER",
    "ollama"
).lower()


# ---------------------------------------------------------
# Lightweight cloud mode
# ---------------------------------------------------------

@lru_cache(maxsize=1)
def get_tfidf_vectorizer():
    """
    Create a lightweight TF-IDF vectorizer for cloud deployment.

    This avoids loading PyTorch/Sentence Transformers on
    low-memory cloud instances.
    """
    return TfidfVectorizer(
        lowercase=True,
        stop_words="english",
        ngram_range=(1, 2),
        max_features=5000
    )


def calculate_tfidf_similarity(
    text1: str,
    text2: str
):
    """
    Calculate text similarity using TF-IDF.

    This is intentionally lightweight and suitable for
    Render's 512 MB memory limit.
    """

    vectorizer = get_tfidf_vectorizer()

    vectors = vectorizer.fit_transform(
        [text1, text2]
    )

    similarity = cosine_similarity(
        vectors[0:1],
        vectors[1:2]
    )[0][0]

    return round(
        float(similarity) * 100,
        2
    )


# ---------------------------------------------------------
# Local Sentence Transformer mode
# ---------------------------------------------------------

@lru_cache(maxsize=1)
def get_model():
    """
    Load the Sentence Transformer only for local use.

    Cloud/Groq deployments do not call this function.
    """

    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(
        MODEL_NAME,
        device="cpu"
    )


@lru_cache(maxsize=32)
def create_embedding(text: str):
    """
    Create an embedding using Sentence Transformers.

    This function is used by the local RAG/vector-search
    workflow. Cloud similarity uses TF-IDF instead.
    """

    model = get_model()

    embedding = model.encode(
        text,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=False
    )

    return embedding


def calculate_similarity(
    text1: str,
    text2: str
):
    """
    Calculate semantic similarity.

    Local/Ollama:
        Sentence Transformers

    Cloud/Groq:
        Lightweight TF-IDF similarity
    """

    if LLM_PROVIDER == "groq":
        return calculate_tfidf_similarity(
            text1,
            text2
        )

    embedding1 = create_embedding(text1)
    embedding2 = create_embedding(text2)

    similarity = cosine_similarity(
        [embedding1],
        [embedding2]
    )[0][0]

    return round(
        float(similarity) * 100,
        2
    )

