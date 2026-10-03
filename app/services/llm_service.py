import json
import os
import re

import requests


# ============================================================
# LLM CONFIGURATION
# ============================================================

LLM_PROVIDER = os.getenv(
    "LLM_PROVIDER",
    "ollama"
).lower()

# ----------------------------
# Ollama configuration
# ----------------------------

OLLAMA_URL = os.getenv(
    "OLLAMA_URL",
    "http://127.0.0.1:11434/api/generate"
)

OLLAMA_MODEL = os.getenv(
    "OLLAMA_MODEL",
    "llama3.2:3b"
)

# ----------------------------
# Groq configuration
# ----------------------------

GROQ_API_KEY = os.getenv(
    "GROQ_API_KEY",
    ""
)

GROQ_URL = os.getenv(
    "GROQ_URL",
    "https://api.groq.com/openai/v1/chat/completions"
)

GROQ_MODEL = os.getenv(
    "GROQ_MODEL",
    "openai/gpt-oss-20b"
)


# ============================================================
# PROMPT
# ============================================================

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

IMPORTANT RULES:
- Return ONLY one valid JSON object.
- Do not use markdown.
- Do not use ```json.
- Do not write anything before or after the JSON.
- Be factual.
- Do not predict hiring outcomes.
- Do not invent information.
- "Not detected" means not found in the uploaded resume.
- Use knowledge only for learning and project recommendations.
- Keep answers short.
- Make sure all JSON strings use double quotes.
- Make sure the JSON is complete and properly closed.

RESUME:
{json.dumps(resume_context, ensure_ascii=False)}

JOB:
{job_description}

MATCHING:
{json.dumps(matching_data, ensure_ascii=False)}

KNOWLEDGE:
{knowledge_context}

Return exactly this JSON structure:

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


# ============================================================
# JSON PARSER
# ============================================================

def extract_json(raw_response: str):
    """
    Safely extract a JSON object from an LLM response.

    Handles:
    - Normal JSON
    - JSON surrounded by whitespace
    - ```json ... ```
    - Extra text before/after JSON
    """

    if not raw_response:
        raise RuntimeError(
            "LLM returned an empty response."
        )

    text = raw_response.strip()

    # --------------------------------------------------------
    # First attempt: direct JSON parsing
    # --------------------------------------------------------

    try:
        return json.loads(text)

    except json.JSONDecodeError:
        pass

    # --------------------------------------------------------
    # Remove markdown code fences
    # --------------------------------------------------------

    text = re.sub(
        r"```json\s*",
        "",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"```\s*$",
        "",
        text
    )

    text = text.strip()

    # --------------------------------------------------------
    # Second attempt after removing code fences
    # --------------------------------------------------------

    try:
        return json.loads(text)

    except json.JSONDecodeError:
        pass

    # --------------------------------------------------------
    # Find the JSON object inside extra text
    # --------------------------------------------------------

    start = text.find("{")
    end = text.rfind("}")

    if start != -1 and end != -1 and end > start:

        json_text = text[
            start:end + 1
        ]

        try:
            return json.loads(
                json_text
            )

        except json.JSONDecodeError:
            pass

    # --------------------------------------------------------
    # Give a useful error
    # --------------------------------------------------------

    preview = raw_response[:500].replace(
        "\n",
        " "
    )

    raise RuntimeError(
        "LLM returned invalid JSON. "
        f"Response preview: {preview}"
    )


# ============================================================
# OLLAMA
# ============================================================

def generate_with_ollama(prompt):

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "format": "json",

        "options": {
            "temperature": 0.1,
            "num_predict": 300,
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

    return raw_response


# ============================================================
# GROQ
# ============================================================

def generate_with_groq(prompt):

    if not GROQ_API_KEY:

        raise RuntimeError(
            "GROQ_API_KEY is not configured."
        )

    payload = {
        "model": GROQ_MODEL,

        "messages": [
            {
                "role": "system",
                "content": (
                    "You are ResumeIQ. "
                    "Return only one valid JSON object. "
                    "Do not use markdown."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],

        "temperature": 0.1,

        "max_tokens": 300,

        "response_format": {
            "type": "json_object"
        }
    }

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    try:

        response = requests.post(
            GROQ_URL,
            headers=headers,
            json=payload,
            timeout=120
        )

        response.raise_for_status()

    except requests.exceptions.ConnectionError as error:

        raise RuntimeError(
            "Could not connect to Groq."
        ) from error

    except requests.exceptions.Timeout as error:

        raise RuntimeError(
            "Groq analysis timed out after 120 seconds."
        ) from error

    except requests.exceptions.HTTPError as error:

        raise RuntimeError(
            f"Groq returned HTTP error "
            f"{response.status_code}: "
            f"{response.text[:500]}"
        ) from error

    except requests.exceptions.RequestException as error:

        raise RuntimeError(
            f"Groq request failed: {error}"
        ) from error

    try:

        data = response.json()

    except ValueError as error:

        raise RuntimeError(
            "Groq returned an invalid response."
        ) from error

    try:

        raw_response = (
            data["choices"][0]["message"]["content"]
            .strip()
        )

    except (
        KeyError,
        IndexError,
        TypeError
    ) as error:

        raise RuntimeError(
            "Groq returned an unexpected response."
        ) from error

    if not raw_response:

        raise RuntimeError(
            "Groq returned an empty response."
        )

    return raw_response


# ============================================================
# MAIN ANALYSIS FUNCTION
# ============================================================

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

    # --------------------------------------------------------
    # Select LLM provider
    # --------------------------------------------------------

    if LLM_PROVIDER == "groq":

        raw_response = generate_with_groq(
            prompt
        )

    elif LLM_PROVIDER == "ollama":

        raw_response = generate_with_ollama(
            prompt
        )

    else:

        raise RuntimeError(
            f"Unsupported LLM_PROVIDER: "
            f"{LLM_PROVIDER}"
        )

    # --------------------------------------------------------
    # Parse JSON safely
    # --------------------------------------------------------

    result = extract_json(
        raw_response
    )

    if not isinstance(result, dict):

        raise RuntimeError(
            "LLM returned valid JSON, "
            "but it was not a JSON object."
        )

    # --------------------------------------------------------
    # Guarantee required fields
    # --------------------------------------------------------

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