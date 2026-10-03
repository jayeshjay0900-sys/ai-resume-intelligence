from app.services.embedding_service import calculate_similarity


def calculate_alignment_score(
    resume_text: str,
    job_description: str,
    skill_match_score: int
):

    semantic_score = calculate_similarity(
        resume_text,
        job_description
    )

    alignment_score = round(
        (skill_match_score * 0.5)
        + (semantic_score * 0.5)
    )

    return {
        "alignment_score": alignment_score,
        "skill_match_score": skill_match_score,
        "semantic_similarity": semantic_score
    }