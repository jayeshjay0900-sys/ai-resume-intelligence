from pathlib import Path

from fastapi import (
    FastAPI,
    File,
    Form,
    UploadFile,
    HTTPException
)

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse


from app.services.pdf_service import (
    extract_text_from_pdf
)

from app.services.resume_service import (
    parse_resume,
    extract_job_skills,
    compare_skills
)

from app.services.embedding_service import (
    calculate_similarity
)

from app.rag.retriever import (
    search_knowledge_base
)

from app.services.llm_service import (
    generate_analysis
)


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="ResumeIQ",
    description="AI Resume Intelligence & Job Matching Platform",
    version="1.1.0"
)


# ============================================================
# DIRECTORIES
# ============================================================

UPLOAD_DIR = Path("uploads")

UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# LIMITS
# ============================================================

MAX_RESUME_SIZE = 10 * 1024 * 1024

MAX_JOB_DESCRIPTION_LENGTH = 20_000

ALLOWED_EXTENSION = ".pdf"


# ============================================================
# FRONTEND
# ============================================================

app.mount(
    "/static",
    StaticFiles(directory="frontend"),
    name="static"
)


# ============================================================
# ALIGNMENT SCORE
# ============================================================

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
        (
            skill_match_score * 0.5
        )
        +
        (
            semantic_score * 0.5
        )
    )

    return {

        "alignment_score":
            alignment_score,

        "skill_match_score":
            skill_match_score,

        "semantic_similarity":
            semantic_score
    }


# ============================================================
# HOME PAGE
# ============================================================

@app.get("/")
def home():

    return FileResponse(
        "frontend/index.html"
    )


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health():

    return {

        "status": "healthy",

        "service": "ResumeIQ",

        "version": "1.1.0"
    }


# ============================================================
# MODEL INFORMATION
# ============================================================

@app.get("/model")
def model():

    return {

        "provider": "Ollama",

        "model": "llama3.2:3b",

        "embedding_model":
            "sentence-transformers/all-MiniLM-L6-v2"
    }
    


# ============================================================
# KNOWLEDGE BASE SEARCH
# ============================================================

@app.get("/search")
def search_knowledge(
    query: str,
    top_k: int = 3
):

    if not query.strip():

        raise HTTPException(
            status_code=400,
            detail="Search query cannot be empty."
        )


    if len(query) > 5000:

        raise HTTPException(
            status_code=400,
            detail="Search query is too long."
        )


    if top_k < 1 or top_k > 20:

        raise HTTPException(
            status_code=400,
            detail="top_k must be between 1 and 20."
        )


    try:

        results = search_knowledge_base(
            query,
            top_k
        )

        return {

            "query": query,

            "results": results
        }


    except FileNotFoundError:

        raise HTTPException(
            status_code=503,
            detail="Knowledge base is not available."
        )


    except Exception as error:

        print(
            f"KNOWLEDGE BASE SEARCH ERROR: {error}",
            flush=True
        )

        raise HTTPException(
            status_code=500,
            detail="Knowledge base search failed."
        )


# ============================================================
# RESUME ANALYSIS
# ============================================================

@app.post("/analyze")
async def analyze_resume(
    resume: UploadFile = File(...),
    job_description: str = Form(...)
):

    # --------------------------------------------------------
    # VALIDATE FILE NAME
    # --------------------------------------------------------

    if not resume.filename:

        raise HTTPException(
            status_code=400,
            detail="Please upload a resume."
        )


    original_filename = Path(
        resume.filename
    ).name


    # --------------------------------------------------------
    # VALIDATE PDF
    # --------------------------------------------------------

    if not original_filename.lower().endswith(
        ALLOWED_EXTENSION
    ):

        raise HTTPException(
            status_code=400,
            detail="Only PDF resumes are supported."
        )


    # --------------------------------------------------------
    # VALIDATE JOB DESCRIPTION
    # --------------------------------------------------------

    job_description = (
        job_description.strip()
    )


    if not job_description:

        raise HTTPException(
            status_code=400,
            detail="Job description cannot be empty."
        )


    if len(job_description) > MAX_JOB_DESCRIPTION_LENGTH:

        raise HTTPException(
            status_code=400,
            detail=(
                "Job description is too long. "
                "Maximum allowed length is "
                "20,000 characters."
            )
        )


    # --------------------------------------------------------
    # READ RESUME
    # --------------------------------------------------------

    content = await resume.read()


    if not content:

        raise HTTPException(
            status_code=400,
            detail="Uploaded PDF is empty."
        )


    # --------------------------------------------------------
    # CHECK FILE SIZE
    # --------------------------------------------------------

    if len(content) > MAX_RESUME_SIZE:

        raise HTTPException(
            status_code=413,
            detail=(
                "Resume file is too large. "
                "Maximum allowed size is 10 MB."
            )
        )


    # --------------------------------------------------------
    # SAVE FILE
    # --------------------------------------------------------

    safe_filename = original_filename

    file_path = (
        UPLOAD_DIR /
        safe_filename
    )


    try:

        with open(
            file_path,
            "wb"
        ) as file:

            file.write(content)


        # ----------------------------------------------------
        # EXTRACT PDF TEXT
        # ----------------------------------------------------

        extracted_text = (
            extract_text_from_pdf(
                str(file_path)
            )
        )


    except Exception as error:

        print(
            f"PDF PROCESSING ERROR: {error}",
            flush=True
        )


        if file_path.exists():

            try:
                file_path.unlink()
            except Exception:
                pass


        raise HTTPException(
            status_code=400,
            detail=(
                "The uploaded file could not "
                "be processed as a valid PDF."
            )
        )


    # --------------------------------------------------------
    # CHECK EXTRACTED TEXT
    # --------------------------------------------------------

    if not extracted_text:

        if file_path.exists():

            try:
                file_path.unlink()
            except Exception:
                pass


        raise HTTPException(
            status_code=400,
            detail=(
                "Could not extract readable text "
                "from this PDF."
            )
        )


    # --------------------------------------------------------
    # PARSE RESUME
    # --------------------------------------------------------

    try:

        resume_data = parse_resume(
            extracted_text
        )


    except Exception as error:

        print(
            f"RESUME PARSING ERROR: {error}",
            flush=True
        )


        raise HTTPException(
            status_code=500,
            detail="Resume parsing failed."
        )


    # --------------------------------------------------------
    # EXTRACT JOB SKILLS
    # --------------------------------------------------------

    try:

        job_skills = extract_job_skills(
            job_description
        )


    except Exception as error:

        print(
            f"JOB SKILL EXTRACTION ERROR: {error}",
            flush=True
        )


        raise HTTPException(
            status_code=500,
            detail="Job description analysis failed."
        )


    # --------------------------------------------------------
    # COMPARE SKILLS
    # --------------------------------------------------------

    try:

        skill_comparison = compare_skills(
            resume_data["skills"],
            job_skills
        )


    except Exception as error:

        print(
            f"SKILL MATCHING ERROR: {error}",
            flush=True
        )


        raise HTTPException(
            status_code=500,
            detail="Skill matching failed."
        )


    # --------------------------------------------------------
    # SEMANTIC MATCHING
    # --------------------------------------------------------

    try:

        alignment = calculate_alignment_score(
            extracted_text,
            job_description,
            skill_comparison[
                "skill_match_score"
            ]
        )


    except Exception as error:

        print(
            f"SEMANTIC MATCHING ERROR: {error}",
            flush=True
        )


        raise HTTPException(
            status_code=500,
            detail="Semantic matching failed."
        )


    # --------------------------------------------------------
    # COMBINED MATCHING DATA
    # --------------------------------------------------------

    matching_data = {

        **skill_comparison,

        **alignment
    }


    # --------------------------------------------------------
    # RAG KNOWLEDGE BASE
    # --------------------------------------------------------

    try:

        rag_results = search_knowledge_base(
            job_description,
            top_k=3
        )

        rag_available = True


    except FileNotFoundError:

        print(
            "RAG ERROR: Knowledge base files not found.",
            flush=True
        )

        rag_results = []

        rag_available = False


    except Exception as error:

        print(
            f"RAG SEARCH ERROR: {error}",
            flush=True
        )

        rag_results = []

        rag_available = False


    # --------------------------------------------------------
    # AI ANALYSIS
    # --------------------------------------------------------

    try:

        print(
            "AI ANALYSIS: Starting Ollama request...",
            flush=True
        )


        ai_analysis = generate_analysis(
            resume_data,
            job_description,
            matching_data,
            rag_results
        )


        print(
            "AI ANALYSIS: Ollama request completed.",
            flush=True
        )


        ai_available = True


    except Exception as error:

        # IMPORTANT:
        # Do not hide the real Ollama error.
        # This will appear in Docker logs.

        print(
            "=" * 70,
            flush=True
        )

        print(
            "AI ANALYSIS ERROR:",
            flush=True
        )

        print(
            str(error),
            flush=True
        )

        print(
            "=" * 70,
            flush=True
        )


        ai_analysis = {

            "summary":
                f"AI analysis failed: {str(error)}",

            "strengths": [],

            "missing_or_not_detected": [],

            "resume_improvements": [],

            "learning_recommendations": [],

            "project_recommendations": []
        }


        ai_available = False


    # --------------------------------------------------------
    # FINAL RESPONSE
    # --------------------------------------------------------

    return {

        "filename":
            safe_filename,


        "resume_text_length":
            len(extracted_text),


        "resume":
            resume_data,


        "job": {

            "required_skills":
                job_skills
        },


        "matching":
            matching_data,


        "rag": {

            "available":
                rag_available,

            "results":
                rag_results
        },


        "ai_analysis":
            ai_analysis,


        "ai_available":
            ai_available,


        "resume_text":
            extracted_text
    }