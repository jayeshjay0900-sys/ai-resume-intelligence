const resumeInput = document.getElementById("resume");
const resumeDropzone = document.getElementById("resume-dropzone");
const resumeEmpty = document.getElementById("resume-empty");
const resumeSelected = document.getElementById("resume-selected");
const resumeFilename = document.getElementById("resume-filename");
const chooseResumeButton = document.getElementById("choose-resume");
const clearResumeButton = document.getElementById("clear-resume");
const jobDescription = document.getElementById("job-description");
const characterCount = document.getElementById("character-count");
const analyzeForm = document.getElementById("analyze-form");
const analyzeButton = document.getElementById("analyze-button");
const result = document.getElementById("result");

const MAX_FILE_SIZE = 10 * 1024 * 1024;


function escapeHtml(value) {

    if (
        value === null ||
        value === undefined
    ) {
        return "";
    }

    return String(value)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}


function validateResume(file) {

    if (!file) {
        return false;
    }

    const isPdf =
        file.type === "application/pdf" ||
        file.name.toLowerCase().endsWith(".pdf");

    if (!isPdf) {

        alert(
            "Please select a PDF resume."
        );

        return false;
    }

    if (file.size > MAX_FILE_SIZE) {

        alert(
            "Resume must be smaller than 10 MB."
        );

        return false;
    }

    return true;
}


function updateResumeUI() {

    const file =
        resumeInput.files[0];

    if (!file) {

        resumeEmpty.classList.remove(
            "hidden"
        );

        resumeSelected.classList.add(
            "hidden"
        );

        clearResumeButton.disabled = true;

        resumeDropzone.classList.remove(
            "has-file"
        );

        return;
    }

    resumeEmpty.classList.add(
        "hidden"
    );

    resumeSelected.classList.remove(
        "hidden"
    );

    resumeFilename.textContent =
        file.name;

    clearResumeButton.disabled = false;

    resumeDropzone.classList.add(
        "has-file"
    );
}


resumeInput.addEventListener(
    "change",
    () => {

        const file =
            resumeInput.files[0];

        if (
            file &&
            !validateResume(file)
        ) {

            resumeInput.value = "";
        }

        updateResumeUI();
    }
);


chooseResumeButton.addEventListener(
    "click",
    () => {

        resumeInput.click();
    }
);


clearResumeButton.addEventListener(
    "click",
    () => {

        resumeInput.value = "";

        result.innerHTML = "";

        updateResumeUI();
    }
);


resumeDropzone.addEventListener(
    "dragover",
    (event) => {

        event.preventDefault();

        resumeDropzone.classList.add(
            "dragging"
        );
    }
);


resumeDropzone.addEventListener(
    "dragleave",
    () => {

        resumeDropzone.classList.remove(
            "dragging"
        );
    }
);


resumeDropzone.addEventListener(
    "drop",
    (event) => {

        event.preventDefault();

        resumeDropzone.classList.remove(
            "dragging"
        );

        const file =
            event.dataTransfer.files[0];

        if (
            !file ||
            !validateResume(file)
        ) {

            return;
        }

        const dataTransfer =
            new DataTransfer();

        dataTransfer.items.add(file);

        resumeInput.files =
            dataTransfer.files;

        updateResumeUI();
    }
);


jobDescription.addEventListener(
    "input",
    () => {

        characterCount.textContent =
            `${jobDescription.value.length.toLocaleString()} / 20,000`;
    }
);


analyzeForm.addEventListener(
    "submit",
    async (event) => {

        event.preventDefault();

        await analyzeResume();
    }
);


async function analyzeResume() {

    const file =
        resumeInput.files[0];

    const jobText =
        jobDescription.value.trim();

    if (!file) {

        alert(
            "Please choose a PDF resume."
        );

        return;
    }

    if (!validateResume(file)) {
        return;
    }

    if (!jobText) {

        alert(
            "Please enter a job description."
        );

        return;
    }

    if (jobText.length > 20000) {

        alert(
            "Job description cannot exceed 20,000 characters."
        );

        return;
    }

    const formData =
        new FormData();

    formData.append(
        "resume",
        file
    );

    formData.append(
        "job_description",
        jobText
    );

    analyzeButton.disabled = true;

    analyzeButton.innerHTML = `
        <span>Analyzing...</span>
        <span class="button-spinner"></span>
    `;

    result.innerHTML = `
        <div class="loading-card">

            <div class="loading-spinner"></div>

            <h3>
                Analyzing your resume
            </h3>

            <p>
                ResumeIQ is extracting your resume,
                matching skills, searching the knowledge
                base, and generating recommendations.
            </p>

        </div>
    `;

    const startTime =
        performance.now();

    try {

        const response =
            await fetch(
                "/analyze",
                {
                    method: "POST",
                    body: formData
                }
            );

        const data =
            await response.json();

        if (!response.ok) {

            throw new Error(
                data.detail ||
                "Analysis failed."
            );
        }

        const elapsed =
            (
                performance.now() -
                startTime
            ) / 1000;

        displayResults(
            data,
            elapsed
        );

    } catch (error) {

        result.innerHTML = `
            <div class="error-card">

                <h3>
                    Analysis failed
                </h3>

                <p>
                    ${escapeHtml(
                        error.message
                    )}
                </p>

            </div>
        `;

    } finally {

        analyzeButton.disabled = false;

        analyzeButton.innerHTML = `
            <span>
                Analyze Resume
            </span>

            <span class="button-arrow">
                →
            </span>
        `;
    }
}


function createList(
    items,
    emptyText = "None detected"
) {

    if (
        !Array.isArray(items) ||
        items.length === 0
    ) {

        return `
            <p class="muted">
                ${escapeHtml(emptyText)}
            </p>
        `;
    }

    return `
        <ul class="result-list">

            ${items.map(
                item => `
                    <li>
                        ${escapeHtml(item)}
                    </li>
                `
            ).join("")}

        </ul>
    `;
}


function createSkillTags(skills) {

    if (
        !Array.isArray(skills) ||
        skills.length === 0
    ) {

        return `
            <p class="muted">
                No skills detected.
            </p>
        `;
    }

    return `
        <div class="skill-tags">

            ${skills.map(
                skill => `
                    <span class="skill-tag">
                        ${escapeHtml(skill)}
                    </span>
                `
            ).join("")}

        </div>
    `;
}


function displayResults(
    data,
    elapsed
) {

    const resume =
        data.resume || {};

    const matching =
        data.matching || {};

    const ai =
        data.ai_analysis || {};

    const matchedSkills =
        matching.matched_skills || [];

    const missingSkills =
        matching.missing_skills || [];


    result.innerHTML = `

        <div class="results-container">

            <div class="result-header">

                <div>

                    <span class="result-label">
                        ANALYSIS COMPLETE
                    </span>

                    <h2>
                        Resume Analysis
                    </h2>

                    <p>
                        ${escapeHtml(
                            data.filename ||
                            "Resume"
                        )}
                    </p>

                </div>

                <div class="analysis-time">
                    ${elapsed.toFixed(1)}s
                </div>

            </div>


            <div class="score-grid">

                <div class="score-card">

                    <span>
                        Resume–Job Alignment
                    </span>

                    <strong>
                        ${matching.alignment_score ?? 0}%
                    </strong>

                    <small>
                        Overall alignment
                    </small>

                </div>


                <div class="score-card">

                    <span>
                        Skill Match
                    </span>

                    <strong>
                        ${matching.skill_match_score ?? 0}%
                    </strong>

                    <small>
                        Required skills detected
                    </small>

                </div>


                <div class="score-card">

                    <span>
                        Semantic Similarity
                    </span>

                    <strong>
                        ${matching.semantic_similarity ?? 0}%
                    </strong>

                    <small>
                        Resume and job text
                    </small>

                </div>

            </div>


            <div class="result-grid">

                <section class="result-section">

                    <div class="section-heading">

                        <span class="section-number">
                            01
                        </span>

                        <div>

                            <h3>
                                Candidate Information
                            </h3>

                            <p>
                                Details extracted from the resume.
                            </p>

                        </div>

                    </div>


                    <div class="info-grid">

                        <div class="info-item">

                            <span>
                                Name
                            </span>

                            <strong>
                                ${escapeHtml(
                                    resume.name ||
                                    "Not detected"
                                )}
                            </strong>

                        </div>


                        <div class="info-item">

                            <span>
                                Email
                            </span>

                            <strong>
                                ${escapeHtml(
                                    resume.email ||
                                    "Not detected"
                                )}
                            </strong>

                        </div>


                        <div class="info-item">

                            <span>
                                Phone
                            </span>

                            <strong>
                                ${escapeHtml(
                                    resume.phone ||
                                    "Not detected"
                                )}
                            </strong>

                        </div>

                    </div>

                </section>


                <section class="result-section">

                    <div class="section-heading">

                        <span class="section-number">
                            02
                        </span>

                        <div>

                            <h3>
                                Skills Detected
                            </h3>

                            <p>
                                Skills found in the uploaded resume.
                            </p>

                        </div>

                    </div>


                    ${createSkillTags(
                        resume.skills
                    )}

                </section>

            </div>


            <div class="result-grid">

                <section class="result-section">

                    <div class="section-heading">

                        <span class="section-number">
                            03
                        </span>

                        <div>

                            <h3>
                                Matched Skills
                            </h3>

                            <p>
                                Skills appearing in both the
                                resume and job description.
                            </p>

                        </div>

                    </div>


                    ${createSkillTags(
                        matchedSkills
                    )}

                </section>


                <section class="result-section">

                    <div class="section-heading">

                        <span class="section-number">
                            04
                        </span>

                        <div>

                            <h3>
                                Not Detected
                            </h3>

                            <p>
                                Requirements not found in
                                the uploaded resume.
                            </p>

                        </div>

                    </div>


                    ${createSkillTags(
                        missingSkills
                    )}


                    <div class="notice">

                        <strong>
                            Note:
                        </strong>

                        Not detected means the skill was
                        not found in the uploaded resume.
                        It does not mean the candidate
                        does not possess the skill.

                    </div>

                </section>

            </div>


            <section class="result-section ai-section">

                <div class="section-heading">

                    <span class="section-number">
                        05
                    </span>

                    <div>

                        <h3>
                            AI Analysis
                        </h3>

                        <p>
                            Structured recommendations generated
                            from the resume, job description,
                            and knowledge base.
                        </p>

                    </div>

                </div>


                <div class="summary-box">

                    <span>
                        SUMMARY
                    </span>

                    <p>
                        ${escapeHtml(
                            ai.summary ||
                            "AI analysis unavailable."
                        )}
                    </p>

                </div>


                <div class="recommendation-grid">

                    <div class="recommendation-card">

                        <h4>
                            Strengths
                        </h4>

                        ${createList(
                            ai.strengths,
                            "No strengths generated."
                        )}

                    </div>


                    <div class="recommendation-card">

                        <h4>
                            Resume Improvements
                        </h4>

                        ${createList(
                            ai.resume_improvements,
                            "No improvements generated."
                        )}

                    </div>


                    <div class="recommendation-card">

                        <h4>
                            Learning Recommendations
                        </h4>

                        ${createList(
                            ai.learning_recommendations,
                            "No recommendations generated."
                        )}

                    </div>


                    <div class="recommendation-card">

                        <h4>
                            Project Recommendations
                        </h4>

                        ${createList(
                            ai.project_recommendations,
                            "No project recommendations generated."
                        )}

                    </div>

                </div>

            </section>


            <div class="result-grid">

                <section class="result-section">

                    <div class="section-heading">

                        <span class="section-number">
                            06
                        </span>

                        <div>

                            <h3>
                                Education
                            </h3>

                        </div>

                    </div>


                    ${createList(
                        resume.education,
                        "Education not detected."
                    )}

                </section>


                <section class="result-section">

                    <div class="section-heading">

                        <span class="section-number">
                            07
                        </span>

                        <div>

                            <h3>
                                Experience
                            </h3>

                        </div>

                    </div>


                    ${createList(
                        resume.experience,
                        "Experience not detected."
                    )}

                </section>

            </div>


            <div class="result-grid">

                <section class="result-section">

                    <div class="section-heading">

                        <span class="section-number">
                            08
                        </span>

                        <div>

                            <h3>
                                Projects
                            </h3>

                        </div>

                    </div>


                    ${createList(
                        resume.projects,
                        "Projects not detected."
                    )}

                </section>


                <section class="result-section">

                    <div class="section-heading">

                        <span class="section-number">
                            09
                        </span>

                        <div>

                            <h3>
                                Certifications
                            </h3>

                        </div>

                    </div>


                    ${createList(
                        resume.certifications,
                        "Certifications not detected."
                    )}

                </section>

            </div>

        </div>
    `;


    result.scrollIntoView({
        behavior: "smooth",
        block: "start"
    });
}


updateResumeUI();