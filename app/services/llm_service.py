import json
import os

import requests


OLLAMA_URL = os.getenv(
    "OLLAMA_URL",
    "http://127.0.0.1:11434/api/generate"
)

OLLAMA_MODEL = os.getenv(
    "OLLAMA_MODEL",
    "llama3.2:3b"
)


def build_prompt(
    resume_data,
    job_description,
    matching_data,
    rag_results
):

    context_parts = []

    for result in rag_results[:2]:

        context_parts.append(
            f"Source: {result.get('source', 'Unknown')}\n"
            f"{result.get('text', '')}"
        )

    knowledge_context = "\n\n".join(
        context_parts
    )

    resume_context = {
        "name": resume_data.get("name"),
        "skills": resume_data.get("skills", []),
        "summary": resume_data.get("summary", []),
        "education": resume_data.get("education", []),
        "experience": resume_data.get("experience", []),
        "projects": resume_data.get("projects", []),
        "certifications": resume_data.get("certifications", [])
    }

    prompt = f"""
You are ResumeIQ.

Analyze the resume against the job description.

RULES:
- Be factual.
- Do not predict hiring outcomes.
- Do not invent information.
- "Not detected" means not found in the uploaded resume.
- Use knowledge only for learning/project recommendations.
- Return JSON only.
- Keep answers short.
- No markdown.

RESUME:
{json.dumps(resume_context, ensure_ascii=False)}

JOB:
{job_description}

MATCHING:
{json.dumps(matching_data, ensure_ascii=False)}

KNOWLEDGE:
{knowledge_context}

Return exactly:

{{
  "summary": "2 short sentences",
  "strengths": [
    "strength",
    "strength",
    "strength"
  ],
  "missing_or_not_detected": [
    "requirement"
  ],
  "resume_improvements": [
    "improvement",
    "improvement"
  ],
  "learning_recommendations": [
    "recommendation",
    "recommendation"
  ],
  "project_recommendations": [
    "project",
    "project"
  ]
}}
"""

    return prompt


def generate_analysis(
    resume_data,
    job_description,
    matching_data,
    rag_results
):

    prompt = build_prompt(
        resume_data,
        job_description,
        matching_data,
        rag_results
    )

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "format": "json",

        "options": {
            "temperature": 0.1,
            "num_predict": 180,
            "num_ctx": 1536
        }
    }

    try:

        response = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=120
        )

        response.raise_for_status()

    except requests.exceptions.ConnectionError as error:

        raise RuntimeError(
            "Could not connect to Ollama. "
            "Make sure Ollama is running."
        ) from error

    except requests.exceptions.Timeout as error:

        raise RuntimeError(
            "Ollama analysis timed out after 120 seconds."
        ) from error

    except requests.exceptions.HTTPError as error:

        raise RuntimeError(
            f"Ollama returned HTTP error "
            f"{response.status_code}: "
            f"{response.text[:500]}"
        ) from error

    except requests.exceptions.RequestException as error:

        raise RuntimeError(
            f"Ollama request failed: {error}"
        ) from error

    try:

        data = response.json()

    except ValueError as error:

        raise RuntimeError(
            "Ollama returned an invalid response."
        ) from error

    raw_response = data.get(
        "response",
        ""
    ).strip()

    if not raw_response:

        raise RuntimeError(
            "Ollama returned an empty response."
        )

    try:

        result = json.loads(
            raw_response
        )

    except json.JSONDecodeError as error:

        raise RuntimeError(
            "Ollama returned invalid JSON."
        ) from error

    required_fields = [
        "summary",
        "strengths",
        "missing_or_not_detected",
        "resume_improvements",
        "learning_recommendations",
        "project_recommendations"
    ]

    for field in required_fields:

        if field not in result:

            if field == "summary":

                result[field] = (
                    "AI analysis was generated."
                )

            else:

                result[field] = []

    return result