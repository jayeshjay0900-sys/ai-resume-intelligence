from app.services.resume_service import (
    extract_email,
    extract_phone,
    extract_skills,
    compare_skills
)


def test_extract_email():

    text = """
    John Doe
    john@example.com
    """

    assert (
        extract_email(text)
        == "john@example.com"
    )


def test_extract_phone():

    text = """
    John Doe
    +91 9876543210
    """

    assert (
        extract_phone(text)
        == "+91 9876543210"
    )


def test_extract_skills():

    text = """
    Python
    SQL
    Machine Learning
    FastAPI
    """

    skills = extract_skills(
        text
    )

    assert "Python" in skills

    assert "SQL" in skills

    assert "Machine Learning" in skills

    assert "FastAPI" in skills


def test_compare_skills():

    resume_skills = [
        "Python",
        "SQL",
        "Machine Learning"
    ]

    job_skills = [
        "Python",
        "SQL",
        "Machine Learning",
        "Docker"
    ]

    result = compare_skills(
        resume_skills,
        job_skills
    )

    assert (
        result["skill_match_score"]
        == 75
    )