
from functools import lru_cache

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


@lru_cache(maxsize=1)
def get_model():
    """
    Load the embedding model only when it is actually needed.

    This prevents the model from consuming memory during application
    startup, which is important for low-memory cloud deployments.
    """
    return SentenceTransformer(
        MODEL_NAME,
        device="cpu"
    )


@lru_cache(maxsize=64)
def create_embedding(text: str):
    """
    Create an embedding for the supplied text.

    A smaller cache keeps memory usage lower on cloud deployments.
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
    Calculate semantic similarity between two texts.
    """

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
