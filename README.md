# ResumeIQ — AI Resume Intelligence & Job Matching Platform

<p align="center">
  <strong>AI-powered resume analysis, job matching, and recommendation generation for modern hiring workflows.</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white" alt="Python 3">
  <img src="https://img.shields.io/badge/FastAPI-API-009688?logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/Ollama-Local%20LLM-black" alt="Ollama">
  <img src="https://img.shields.io/badge/FAISS-Vector%20Search-0467DF" alt="FAISS">
  <img src="https://img.shields.io/badge/Docker-Containerized-2496ED?logo=docker&logoColor=white" alt="Docker">
  <img src="https://img.shields.io/badge/Pytest-Testing-0A9ED0?logo=pytest&logoColor=white" alt="Pytest">
</p>

---

## Overview

ResumeIQ is an AI-driven system that evaluates how well a candidate's resume aligns with a target job description. It combines PDF parsing, skill extraction, semantic similarity analysis, vector search, and LLM-powered recommendations to provide actionable hiring insights.

The platform is designed to help candidates, recruiters, and career coaches understand:

- the skills present in a resume,
- the requirements missing from the profile,
- the resume-to-job similarity score,
- opportunities for upskilling or resume improvements.

---

## Key Features

- PDF resume upload and parsing
- Structured extraction of candidate information and skills
- Job requirement analysis
- Skill matching between resume and target role
- Semantic similarity scoring using sentence-transformer embeddings
- Vector-based knowledge retrieval with FAISS
- Retrieval-augmented generation (RAG) for contextual recommendations
- Local LLM analysis using Ollama
- JSON API access and a lightweight frontend interface
- Docker support for local deployment

---

## How It Works

1. Upload a PDF resume and provide a job description.
2. Extract readable text from the uploaded document.
3. Parse the resume into structured sections such as skills, experience, and profile data.
4. Identify required skills from the job description.
5. Compare resume skills against required skills.
6. Compute semantic similarity between the full resume and the job description.
7. Retrieve supporting context from the local knowledge base using FAISS + RAG.
8. Generate summary, strengths, missing skills, and improvement suggestions using Ollama.
9. Return a structured API response and display the results in the frontend.

---

## Architecture

```text
┌──────────────────────────────┐
│          User               │
│ Resume PDF + Job Description │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│        Frontend UI           │
│  HTML / CSS / JavaScript    │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│         FastAPI API          │
│  /health /model /search /analyze │
└───────┬──────────────┬───────┘
        │              │
        ▼              ▼
┌──────────────┐  ┌──────────────────────┐
│ PDF Parser   │  │ Skill & Resume       │
│ PyMuPDF      │  │ Extraction Logic     │
└──────┬───────┘  └─────────┬────────────┘
       │                    │
       ▼                    ▼
┌─────────────────────┐  ┌──────────────────────┐
│ Sentence Embeddings │  │ Skill Matching       │
│ all-MiniLM-L6-v2    │  │ + Similarity Scoring │
└──────────┬──────────┘  └──────────┬───────────┘
           │                       │
           └──────────────┬────────┘
                          ▼
              ┌──────────────────────┐
              │ Resume–Job Alignment │
              │  Score (50% Skills + │
              │   50% Semantic)     │
              └──────────┬───────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │  RAG + FAISS         │
              │ knowledge retrieval  │
              └──────────┬───────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │ Ollama Local LLM     │
              │ llama3.2:3b          │
              └──────────┬───────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │ Structured Analysis  │
              │ and Recommendations  │
              └──────────────────────┘
```

---

## Resume–Job Alignment Score

The alignment score combines:

- 50% skill match score
- 50% semantic similarity score

This provides a balanced view of how closely a resume matches a role based on both explicit competency overlap and contextual similarity.

> Note: this score is intended as an analytical signal, not a hiring prediction or employment guarantee.

---

## Technology Stack

| Category | Technologies |
| --- | --- |
| Backend | Python, FastAPI, Uvicorn, Pydantic |
| PDF Processing | PyMuPDF |
| NLP / ML | Sentence Transformers, Scikit-learn |
| Embeddings | sentence-transformers/all-MiniLM-L6-v2 |
| Vector Search | FAISS |
| RAG | LangChain Text Splitters, local knowledge base |
| LLM | Ollama |
| Frontend | HTML, CSS, JavaScript |
| Testing | Pytest |
| Deployment | Docker |

---

## Project Structure

```text
ai-resume-intelligence/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── matching_service.py
│   ├── rag/
│   └── services/
├── frontend/
├── knowledge_base/
├── tests/
├── uploads/
├── .env.example
├── .gitignore
├── Dockerfile
├── README.md
├── requirements.txt
└── .dockerignore
```

---

## Prerequisites

Before running the project, ensure you have:

- Python 3.10+ recommended
- Ollama installed and running locally
- Git
- Docker (optional, for containerized deployment)

---

## Quick Start

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd ai-resume-intelligence
```

### 2. Create and activate a virtual environment

On macOS/Linux:

```bash
python -m venv .venv
source .venv/bin/activate
```

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Copy the example environment file:

```bash
cp .env.example .env
```

Or on Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

The project uses local Ollama settings by default, as shown in `.env.example`.

### 5. Start Ollama

```bash
ollama run llama3.2:3b
```

If you prefer another model, update the value in `.env` and the app configuration accordingly.

### 6. Run the API server

```bash
uvicorn app.main:app --reload
```

The app will be available at:

```text
http://localhost:8000
```

---

## Docker Deployment

Build the image:

```bash
docker build -t resumeiq .
```

Run the container:

```bash
docker run --name resumeiq -p 8000:8000 \
  -e OLLAMA_URL=http://host.docker.internal:11434/api/generate \
  -e OLLAMA_MODEL=llama3.2:3b \
  resumeiq
```

This setup is useful for running ResumeIQ in an isolated environment while keeping Ollama on the host machine.

---

## API Endpoints

### Health check

```http
GET /health
```

Returns service status and version details.

### Model information

```http
GET /model
```

Returns the connected Ollama provider and embedding model metadata.

### Knowledge base search

```http
GET /search?query=python%20fastapi&top_k=3
```

Searches the local knowledge base for relevant context.

### Resume analysis

```http
POST /analyze
```

Request form-data:

- `resume`: uploaded PDF file
- `job_description`: string containing the job requirement text

The response includes:

- extracted resume details,
- required skills,
- matched and missing skills,
- alignment score,
- semantic similarity,
- RAG results,
- AI-generated recommendations.

Example request:

```bash
curl -X POST "http://localhost:8000/analyze" \
  -F "resume=@sample_resume.pdf" \
  -F "job_description=We are looking for a Python engineer with FastAPI, SQL, Docker, and cloud deployment experience."
```

---

## Output Example

ResumeIQ returns a structured result similar to:

```json
{
  "filename": "resume.pdf",
  "resume_text_length": 4200,
  "resume": {
    "name": "Jane Doe",
    "skills": ["Python", "FastAPI", "Docker"]
  },
  "job": {
    "required_skills": ["Python", "FastAPI", "SQL", "Docker"]
  },
  "matching": {
    "alignment_score": 87,
    "skill_match_score": 75,
    "semantic_similarity": 0.91
  },
  "ai_analysis": {
    "summary": "Strong technical profile aligned with the role.",
    "strengths": ["Python backend development", "API experience"],
    "missing_or_not_detected": ["SQL"],
    "resume_improvements": ["Add deployment experience"],
    "learning_recommendations": ["Improve SQL and cloud knowledge"],
    "project_recommendations": ["Build a portfolio backend project"]
  }
}
```

---

## Testing

Run the automated API tests:

```bash
pytest -q
```

The main tests are located under:

```text
tests/test_api.py
```

---

## Limitations

This project is a portfolio-grade proof of concept and has a few practical limitations:

- Resume parsing accuracy depends on the PDF structure and quality.
- Skill extraction depends on the supported vocabulary and heuristics.
- Image-based or scanned PDFs may require OCR for best results.
- LLM responses may vary between runs.
- RAG quality depends on the knowledge base content.
- The alignment score is an analytical signal, not a hiring prediction.

---

## Disclaimer

ResumeIQ provides analytical and AI-generated insights based on uploaded resumes, job descriptions, knowledge-base retrieval, and model output. It does not guarantee interviews, job offers, or hiring outcomes.

---

## Author

Jayesh S

This project was built as an AI and ML portfolio application to demonstrate:

- NLP and text processing
- Embeddings and semantic matching
- Vector search and retrieval
- RAG workflows
- Local LLM integration
- FastAPI backend services
- Dockerized deployment
