import re


COMMON_SKILLS = [
    "Python",
    "Java",
    "C++",
    "JavaScript",
    "TypeScript",
    "SQL",
    "HTML",
    "CSS",
    "React",
    "Node.js",
    "FastAPI",
    "Flask",
    "Django",
    "Pandas",
    "NumPy",
    "Scikit-learn",
    "TensorFlow",
    "PyTorch",
    "Keras",
    "Machine Learning",
    "Deep Learning",
    "Artificial Intelligence",
    "NLP",
    "Natural Language Processing",
    "LLM",
    "RAG",
    "LangChain",
    "FAISS",
    "Transformers",
    "Hugging Face",
    "Git",
    "GitHub",
    "Docker",
    "AWS",
    "Azure",
    "GCP",
    "Power BI",
    "Tableau",
    "Excel",
    "Matplotlib",
    "Seaborn",
    "Plotly",
    "Streamlit",
    "MongoDB",
    "MySQL",
    "PostgreSQL",
    "SQLite",
    "REST API",
]


SKILL_ALIASES = {
    "ml": "Machine Learning",
    "machine learning": "Machine Learning",
    "ai": "Artificial Intelligence",
    "artificial intelligence": "Artificial Intelligence",
    "nlp": "NLP",
    "natural language processing": "NLP",
    "deep learning": "Deep Learning",
    "llms": "LLM",
    "large language models": "LLM",
    "scikit learn": "Scikit-learn",
    "scikit-learn": "Scikit-learn",
    "huggingface": "Hugging Face",
    "postgres": "PostgreSQL",
    "rest apis": "REST API",
    "rest api": "REST API",
}


SECTION_ALIASES = {
    "summary": [
        "professional summary",
        "summary",
        "profile",
        "objective",
    ],

    "skills": [
        "skills",
        "technical skills",
        "technical skill",
    ],

    "experience": [
        "professional experience",
        "work experience",
        "experience",
    ],

    "projects": [
        "projects",
        "personal projects",
        "academic projects",
    ],

    "education": [
        "education",
        "academic background",
    ],

    "certifications": [
        "certifications",
        "certificates",
    ],

    "achievements": [
        "achievements",
        "accomplishments",
    ],
}


def extract_email(text: str):

    match = re.search(
        r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
        text
    )

    return match.group(0) if match else None


def extract_phone(text: str):

    patterns = [
        r"\+91[\s-]?[6-9]\d{9}",
        r"\b[6-9]\d{9}\b",
        r"\+\d{1,3}[\s-]?\d{7,12}",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text
        )

        if match:
            return match.group(0)

    return None


def extract_name(text: str):

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    for line in lines[:10]:

        if (
            "@" in line
            or re.search(r"\d", line)
            or len(line) > 50
        ):
            continue

        words = line.split()

        if 2 <= len(words) <= 4:

            if all(
                re.match(
                    r"^[A-Za-z.\-]+$",
                    word
                )
                for word in words
            ):
                return line

    return None


def normalize_skill(skill: str):

    key = skill.lower().strip()

    return SKILL_ALIASES.get(
        key,
        skill
    )


def extract_skills(text: str):

    text_lower = text.lower()

    found = []

    for skill in COMMON_SKILLS:

        if skill.lower() in text_lower:

            normalized = normalize_skill(
                skill
            )

            if normalized not in found:
                found.append(normalized)

    return found


def is_section_header(line: str):

    cleaned = line.strip().lower()

    if not cleaned:
        return None

    for section, aliases in SECTION_ALIASES.items():

        for alias in aliases:

            if cleaned == alias:
                return section

    return None


def extract_section(
    text: str,
    section_names
):

    lines = text.splitlines()

    requested_sections = [
        name.lower().strip()
        for name in section_names
    ]

    start = None

    for index, line in enumerate(lines):

        cleaned = line.strip().lower()

        if cleaned in requested_sections:

            start = index + 1
            break

    if start is None:
        return []

    result = []

    for line in lines[start:]:

        cleaned = line.strip()

        if not cleaned:
            continue

        next_section = is_section_header(
            cleaned
        )

        if next_section:
            break

        result.append(cleaned)

    return result


def extract_job_skills(job_description: str):

    text_lower = job_description.lower()

    found = []

    for skill in COMMON_SKILLS:

        if skill.lower() in text_lower:

            normalized = normalize_skill(
                skill
            )

            if normalized not in found:

                found.append(
                    normalized
                )

    return found


def compare_skills(
    resume_skills,
    job_skills
):

    resume_set = {
        normalize_skill(skill)
        for skill in resume_skills
    }

    job_set = {
        normalize_skill(skill)
        for skill in job_skills
    }

    matched = sorted(
        resume_set.intersection(
            job_set
        )
    )

    missing = sorted(
        job_set - resume_set
    )

    if job_set:

        score = round(
            (
                len(matched)
                / len(job_set)
            ) * 100
        )

    else:

        score = 0

    return {
        "matched_skills": matched,
        "missing_skills": missing,
        "skill_match_score": score,
    }


def parse_resume(text: str):

    education = extract_section(
        text,
        SECTION_ALIASES["education"]
    )

    experience = extract_section(
        text,
        SECTION_ALIASES["experience"]
    )

    projects = extract_section(
        text,
        SECTION_ALIASES["projects"]
    )

    summary = extract_section(
        text,
        SECTION_ALIASES["summary"]
    )

    certifications = extract_section(
        text,
        SECTION_ALIASES["certifications"]
    )

    return {

        "name": extract_name(text),

        "email": extract_email(text),

        "phone": extract_phone(text),

        "skills": extract_skills(text),

        "summary": summary,

        "education": education,

        "experience": experience,

        "projects": projects,

        "certifications": certifications,
    }