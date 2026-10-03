from functools import lru_cache

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


# Load the embedding model once.
model = SentenceTransformer(MODEL_NAME)


@lru_cache(maxsize=256)
def create_embedding(text: str):

    embedding = model.encode(
        text,
        convert_to_numpy=True
    )

    return embedding


def calculate_similarity(
    text1: str,
    text2: str
):

    embedding1 = create_embedding(
        text1
    )

    embedding2 = create_embedding(
        text2
    )

    similarity = cosine_similarity(
        [embedding1],
        [embedding2]
    )[0][0]

    return round(
        float(similarity) * 100,
        2
    )