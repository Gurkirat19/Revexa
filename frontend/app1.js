const API_BASE_URL = "http://127.0.0.1:8000";

function cleanAIResponse(text) {
    if (!text) {
        return "";
    }

    return text
        .replace(/\\n/g, "\n")
        .replace(/\\t/g, "\t")
        .replace(/\\"/g, '"');
}


// =========================================
// ELEMENTS
// =========================================

const navItems =
    document.querySelectorAll(".nav-item");

const pageTitle =
    document.getElementById("pageTitle");

const repoUrl =
    document.getElementById("repoUrl");

const aiModel =
    document.getElementById("aiModel");

const repositoryQuestion =
    document.getElementById(
        "repositoryQuestion"
    );

const analyzeRepositoryButton =
    document.getElementById(
        "analyzeRepositoryButton"
    );

const analyzeText =
    document.getElementById(
        "analyzeText"
    );

const analyzeLoader =
    document.getElementById(
        "analyzeLoader"
    );

const analysisQuestion =
    document.getElementById(
        "analysisQuestion"
    );

const analysisRepo =
    document.getElementById(
        "analysisRepo"
    );

const analysisStatus =
    document.getElementById(
        "analysisStatus"
    );

const progressBar =
    document.getElementById(
        "progressBar"
    );

const progressFile =
    document.getElementById(
        "progressFile"
    );

const progressPercent =
    document.getElementById(
        "progressPercent"
    );

const analysisSteps =
    document.querySelectorAll(
        ".analysis-step"
    );

const resultQuestion =
    document.getElementById(
        "resultQuestion"
    );

const repositoryAnswer =
    document.getElementById(
        "repositoryAnswer"
    );

const startAnalysisButton =
    document.getElementById(
        "startAnalysisButton"
    );

const newAnalysisButton =
    document.getElementById(
        "newAnalysisButton"
    );

const refreshButton =
    document.getElementById(
        "refreshButton"
    );


// =========================================
// STATE
// =========================================

let animationTimers = [];


// =========================================
// NAVIGATION
// =========================================

navItems.forEach((item) => {

    item.addEventListener(
        "click",
        () => {

            const page =
                item.dataset.page;

            showPage(page);

        }
    );

});


function showPage(page) {

    document
        .querySelectorAll(".page-section")
        .forEach((section) => {

            section.classList.remove(
                "active-page"
            );

        });


    const target =
        document.getElementById(
            `${page}Page`
        );


    if (target) {

        target.classList.add(
            "active-page"
        );

    }


    navItems.forEach((item) => {

        item.classList.toggle(
            "active",
            item.dataset.page === page
        );

    });


    const titles = {

        dashboard:
            "Dashboard",

        reviews:
            "PR Reviews",

        repository:
            "Repository Assistant",

        sessions:
            "Sessions",

        activity:
            "Activity",

        analytics:
            "Analytics",

        settings:
            "Settings",

        analysis:
            "Live Analysis",

        result:
            "Analysis Result"

    };


    pageTitle.textContent =
        titles[page] ||
        "Dashboard";

}


// =========================================
// DASHBOARD CTA
// =========================================

startAnalysisButton.addEventListener(
    "click",
    () => {

        showPage(
            "repository"
        );

        repoUrl.focus();

    }
);


// =========================================
// NEW ANALYSIS
// =========================================

newAnalysisButton.addEventListener(
    "click",
    () => {

        showPage(
            "repository"
        );

        repositoryAnswer.innerHTML =
            "";

    }
);


// =========================================
// REFRESH
// =========================================

refreshButton.addEventListener(
    "click",
    () => {

        refreshButton.style.transform =
            "rotate(360deg)";


        setTimeout(
            () => {

                refreshButton.style.transform =
                    "rotate(0deg)";

            },
            400
        );

    }
);


// =========================================
// REPOSITORY ANALYSIS
// =========================================

analyzeRepositoryButton.addEventListener(
    "click",
    async () => {

        const repository =
            repoUrl.value.trim();


        const question =
            repositoryQuestion.value.trim();


        const model =
            aiModel.value;


        // -----------------------------
        // VALIDATION
        // -----------------------------

        if (!repository) {

            alert(
                "Please enter a GitHub repository URL."
            );

            return;

        }


        if (!question) {

            alert(
                "Please enter a question about the repository."
            );

            return;

        }


        // -----------------------------
        // START UI
        // -----------------------------

        startButtonLoading();


        showPage(
            "analysis"
        );


        analysisQuestion.textContent =
            question;


        analysisRepo.textContent =
            repository;


        resetAnalysisAnimation();


        startAnalysisAnimation();


        try {

            // -----------------------------
            // BACKEND REQUEST
            // -----------------------------

            const response =
                await fetch(
                    `${API_BASE_URL}/api/repository/chat`,
                    {
                        method: "POST",
                        credentials: "include",

                        headers: {
                            "Content-Type":
                                "application/json"
                        },

                        body: JSON.stringify({

                            repo_url:
                                repository,

                            question:
                                question,

                            model:
                                model

                        })

                    }
                );


           const data =
    await response.json();

console.log(
    "Backend response:",
    data
);

data.answer =
    cleanAIResponse(
        data.answer
    );


            // -----------------------------
            // HTTP ERROR
            // -----------------------------

            if (!response.ok) {

                throw new Error(
                    data.detail ||
                    "Repository analysis failed."
                );

            }


            // -----------------------------
            // BACKEND ERROR
            // -----------------------------

            if (data.error) {

                throw new Error(
                    data.answer ||
                    "Repository analysis failed."
                );

            }


            // -----------------------------
            // ANALYSIS COMPLETE
            // -----------------------------

          finishAnalysisAnimation();

console.log(
    "Rendering result..."
);

renderResult(
    data
);

        }
        catch (error) {

            failAnalysisAnimation(
                error.message
            );


            setTimeout(
                () => {

                    alert(
                        error.message
                    );


                    showPage(
                        "repository"
                    );

                },
                900
            );

        }
        finally {

            stopButtonLoading();

        }

    }
);


// =========================================
// BUTTON LOADING
// =========================================

function startButtonLoading() {

    analyzeRepositoryButton.disabled =
        true;


    analyzeText.textContent =
        "Analyzing";


    analyzeLoader.classList.remove(
        "hidden"
    );

}


function stopButtonLoading() {

    analyzeRepositoryButton.disabled =
        false;


    analyzeText.textContent =
        "Start Analysis";


    analyzeLoader.classList.add(
        "hidden"
    );

}


// =========================================
// ANALYSIS ANIMATION
// =========================================

function resetAnalysisAnimation() {

    // Clear previous timers
    animationTimers.forEach(
        clearTimeout
    );


    animationTimers = [];


    // Reset progress
    progressBar.style.width =
        "0%";


    progressPercent.textContent =
        "0%";


    progressFile.textContent =
        "Discovering repository";


    // Reset status
    analysisStatus.textContent =
        "RUNNING";


    // Reset all steps
    analysisSteps.forEach(
        (step) => {

            step.classList.remove(
                "active",
                "done"
            );

        }
    );

}


// =========================================
// START ANALYSIS ANIMATION
// =========================================

function startAnalysisAnimation() {

    const stages = [

        {
            step: 0,
            progress: 12,
            text:
                "Discovering repository",
            delay: 300
        },

        {
            step: 1,
            progress: 30,
            text:
                "Searching relevant code",
            delay: 1400
        },

        {
            step: 2,
            progress: 48,
            text:
                "Reading repository files",
            delay: 2800
        },

        {
            step: 3,
            progress: 66,
            text:
                "Analyzing implementation",
            delay: 4300
        },

        {
            step: 4,
            progress: 82,
            text:
                "Reviewing security risks",
            delay: 5900
        },

        {
            step: 5,
            progress: 94,
            text:
                "Generating engineering answer",
            delay: 7500
        }

    ];


    stages.forEach(
        (stage) => {

            const timer =
                setTimeout(
                    () => {

                        activateStage(
                            stage.step,
                            stage.progress,
                            stage.text
                        );

                    },
                    stage.delay
                );


            animationTimers.push(
                timer
            );

        }
    );

}


// =========================================
// ACTIVATE ANALYSIS STAGE
// =========================================

function activateStage(
    index,
    progress,
    text
) {

    analysisSteps.forEach(
        (step, stepIndex) => {

            if (
                stepIndex <
                index
            ) {

                step.classList.remove(
                    "active"
                );

                step.classList.add(
                    "done"
                );

            }

            else if (
                stepIndex ===
                index
            ) {

                step.classList.add(
                    "active"
                );

                step.classList.remove(
                    "done"
                );

            }

            else {

                step.classList.remove(
                    "active",
                    "done"
                );

            }

        }
    );


    progressBar.style.width =
        `${progress}%`;


    progressPercent.textContent =
        `${progress}%`;


    progressFile.textContent =
        text;

}


// =========================================
// FINISH ANALYSIS
// =========================================

function finishAnalysisAnimation() {

    // Stop scheduled animation
    animationTimers.forEach(
        clearTimeout
    );


    animationTimers = [];


    // Mark every stage complete
    analysisSteps.forEach(
        (step) => {

            step.classList.remove(
                "active"
            );

            step.classList.add(
                "done"
            );

        }
    );


    // Complete progress
    progressBar.style.width =
        "100%";


    progressPercent.textContent =
        "100%";


    progressFile.textContent =
        "Analysis complete";


    analysisStatus.textContent =
        "COMPLETED";

}


// =========================================
// ANALYSIS ERROR
// =========================================

function failAnalysisAnimation(
    message
) {

    animationTimers.forEach(
        clearTimeout
    );


    animationTimers = [];


    analysisStatus.textContent =
        "ERROR";


    progressFile.textContent =
        message ||
        "Analysis failed.";

}


// =========================================
// RENDER RESULT
// =========================================

function renderResult(
    data
) {

    console.log(
        "renderResult called:",
        data
    );


    resultQuestion.textContent =
        data.question ||
        "—";


    const answer =
        cleanAIResponse(
            data.answer
        );


    console.log(
        "Final answer:",
        answer
    );


    if (!answer) {

        repositoryAnswer.innerHTML = `
            <div class="answer-empty">
                <p>
                    No answer was returned
                    by the AI provider.
                </p>
            </div>
        `;

    }

    else {

        repositoryAnswer.innerHTML =
            formatAnswer(
                answer
            );

    }


    showPage(
        "result"
    );

}

// =========================================
// FORMAT AI ANSWER
// =========================================

function formatAnswer(answer) {

    if (!answer) {
        return `
            <div class="ci-empty">
                <div class="ci-empty-icon">✦</div>
                <h3>No analysis returned</h3>
                <p>The repository agent did not return an answer.</p>
            </div>
        `;
    }

    answer = cleanAIResponse(answer).trim();

    const sections = parseAnswerSections(answer);

    const summary =
        getSection(sections, "SUMMARY");

    const findings =
        getSection(sections, "WHAT I FOUND");

    const evidence =
        getSection(sections, "EVIDENCE");

    const missing =
        getSection(sections, "WHAT IS MISSING");

    const risks =
        getSection(sections, "RISKS OR CONCERNS");

    const solution =
        getSection(
            sections,
            "HOW TO ADD OR IMPROVE IT"
        );

    const recommendation =
        getSection(
            sections,
            "FINAL RECOMMENDATION"
        );

    const fileCount =
        extractFiles(evidence).length;

    const missingItems =
        extractList(missing).length;

    const riskItems =
        extractList(risks).length;

    const findingItems =
        extractList(findings).length;

    return `

        <!-- SUMMARY HERO -->

        <section class="ci-result-hero">

            <div class="ci-result-status">
                <span class="ci-status-dot"></span>
                ANALYSIS COMPLETE
            </div>

            <h2>
                Repository
                <span>insights.</span>
            </h2>

            <p class="ci-summary">
                ${formatPlainText(
                    summary?.content ||
                    "Analysis completed successfully."
                )}
            </p>

        </section>


        <!-- STATISTICS -->

        <section class="ci-stat-grid">

            ${statCard(
                "◈",
                findingItems,
                "Findings"
            )}

            ${statCard(
                "⌁",
                missingItems,
                "Missing"
            )}

            ${statCard(
                "⚠",
                riskItems,
                "Concerns"
            )}

            ${statCard(
                "▣",
                fileCount,
                "Files"
            )}

        </section>


        <!-- FINDINGS -->

        ${
            findings
                ? `
                    <section
                        class="ci-report-section"
                        style="--delay: 120ms"
                    >

                        ${sectionHeading(
                            "WHAT I FOUND",
                            "Repository evidence discovered by the agent."
                        )}

                        <div class="ci-finding-list">

                            ${renderFindingCards(
                                findings.content
                            )}

                        </div>

                    </section>
                `
                : ""
        }


        <!-- EVIDENCE -->

        ${
            evidence
                ? `
                    <section
                        class="ci-report-section"
                        style="--delay: 220ms"
                    >

                        ${sectionHeading(
                            "EVIDENCE",
                            "Files and code locations used by the agent."
                        )}

                        <div class="ci-evidence-list">

                            ${renderEvidence(
                                evidence.content
                            )}

                        </div>

                    </section>
                `
                : ""
        }


        <!-- MISSING -->

        ${
            missing
                ? `
                    <section
                        class="ci-report-section"
                        style="--delay: 320ms"
                    >

                        ${sectionHeading(
                            "WHAT IS MISSING",
                            "Capabilities that were not found in the repository."
                        )}

                        <div class="ci-checklist">

                            ${renderChecklist(
                                missing.content,
                                "missing"
                            )}

                        </div>

                    </section>
                `
                : ""
        }


        <!-- RISKS -->

        ${
            risks
                ? `
                    <section
                        class="ci-report-section"
                        style="--delay: 420ms"
                    >

                        ${sectionHeading(
                            "RISKS & CONCERNS",
                            "Potential issues identified during analysis."
                        )}

                        <div class="ci-risk-list">

                            ${renderChecklist(
                                risks.content,
                                "risk"
                            )}

                        </div>

                    </section>
                `
                : ""
        }


        <!-- SOLUTION -->

        ${
            solution
                ? `
                    <section
                        class="ci-report-section"
                        style="--delay: 520ms"
                    >

                        ${sectionHeading(
                            "HOW TO ADD OR IMPROVE IT",
                            "A practical implementation path."
                        )}

                        <div class="ci-solution">

                            ${renderSteps(
                                solution.content
                            )}

                        </div>

                    </section>
                `
                : ""
        }


        <!-- RECOMMENDATION -->

        ${
            recommendation
                ? `
                    <section
                        class="ci-recommendation"
                        style="--delay: 620ms"
                    >

                        <div class="ci-rec-icon">
                            ✦
                        </div>

                        <div class="ci-rec-content">

                            <span>
                                RECOMMENDED NEXT STEP
                            </span>

                            ${formatPlainText(
                                recommendation.content
                            )}

                        </div>

                    </section>
                `
                : ""
        }

    `;
}


function parseAnswerSections(answer) {

    const headings = [
        "SUMMARY",
        "WHAT I FOUND",
        "EVIDENCE",
        "WHAT IS MISSING",
        "RISKS OR CONCERNS",
        "HOW TO ADD OR IMPROVE IT",
        "FINAL RECOMMENDATION"
    ];

    const pattern =
        headings
            .map(escapeRegex)
            .join("|");

    const regex = new RegExp(
        `(?:^|\\n)\\s*(${pattern})\\s*(?=\\n|$)`,
        "gi"
    );

    const matches = [
        ...answer.matchAll(regex)
    ];

    return matches.map(
        (match, index) => {

            const title =
                match[1]
                    .trim()
                    .toUpperCase();

            const start =
                match.index +
                match[0].length;

            const end =
                index + 1 <
                matches.length
                    ? matches[index + 1].index
                    : answer.length;

            return {
                title,
                content:
                    answer
                        .slice(start, end)
                        .trim()
            };
        }
    );
}


function getSection(
    sections,
    title
) {

    return sections.find(
        section =>
            section.title === title
    );
}


function extractList(content) {

    if (!content) {
        return [];
    }

    return cleanAIResponse(content)
        .split("\n")
        .map(line => line.trim())
        .filter(line =>
            /^[-•*]\s+/.test(line) ||
            /^\d+\.\s+/.test(line)
        );
}


function extractFiles(content) {

    if (!content) {
        return [];
    }

    const files = [];

    const regex =
        /`([^`]+\.(?:js|jsx|ts|tsx|py|java|cpp|c|json|css|html|md|yml|yaml|sql))`/gi;

    let match;

    while (
        (match = regex.exec(content))
        !== null
    ) {

        if (!files.includes(match[1])) {
            files.push(match[1]);
        }
    }

    return files;
}


function statCard(
    icon,
    value,
    label
) {

    return `
        <div class="ci-stat-card">

            <div class="ci-stat-icon">
                ${icon}
            </div>

            <div class="ci-stat-value">
                ${value}
            </div>

            <div class="ci-stat-label">
                ${label}
            </div>

        </div>
    `;
}


function sectionHeading(
    title,
    description
) {

    return `
        <div class="ci-section-heading">

            <div>
                <span>
                    CODE INTELLIGENCE
                </span>

                <h3>
                    ${title}
                </h3>

                <p>
                    ${description}
                </p>
            </div>

        </div>
    `;
}


function renderFindingCards(
    content
) {

    const items =
        extractList(content);

    if (!items.length) {

        return `
            <div class="ci-text-card">
                ${formatPlainText(content)}
            </div>
        `;
    }

    return items
        .map(
            (item, index) => {

                const clean =
                    item.replace(
                        /^[-•*]\s+/,
                        ""
                    );

                return `
                    <div
                        class="ci-finding-card"
                        style="--item-delay:${index * 80}ms"
                    >

                        <div class="ci-finding-number">
                            ${String(
                                index + 1
                            ).padStart(2, "0")}
                        </div>

                        <div class="ci-finding-content">

                            <div class="ci-finding-title">
                                ${formatInlineText(
                                    clean
                                )}
                            </div>

                            <div class="ci-finding-line">
                                Repository finding
                            </div>

                        </div>

                        <div class="ci-finding-arrow">
                            →
                        </div>

                    </div>
                `;
            }
        )
        .join("");
}


function renderEvidence(
    content
) {

    const lines =
        cleanAIResponse(content)
            .split("\n")
            .map(line => line.trim())
            .filter(Boolean);

    return lines
        .map(
            (line, index) => {

                const match =
                    line.match(
                        /^`([^`]+)`\s*[—:-]\s*(.*)$/
                    );

                if (!match) {

                    return `
                        <div class="ci-evidence-card">
                            ${formatInlineText(
                                line
                            )}
                        </div>
                    `;
                }

                return `
                    <details
                        class="ci-evidence-card"
                        style="--item-delay:${index * 70}ms"
                    >

                        <summary>

                            <div class="ci-file-icon">
                                JS
                            </div>

                            <div class="ci-file-info">

                                <strong>
                                    ${escapeHTML(
                                        match[1]
                                    )}
                                </strong>

                                <span>
                                    Repository evidence
                                </span>

                            </div>

                            <div class="ci-chevron">
                                +
                            </div>

                        </summary>

                        <div class="ci-evidence-detail">

                            ${formatInlineText(
                                match[2]
                            )}

                        </div>

                    </details>
                `;
            }
        )
        .join("");
}


function renderChecklist(
    content,
    type
) {

    const items =
        extractList(content);

    if (!items.length) {

        return `
            <div class="ci-text-card">
                ${formatPlainText(content)}
            </div>
        `;
    }

    return items
        .map(
            (item, index) => {

                const clean =
                    item
                        .replace(
                            /^[-•*]\s+/,
                            ""
                        )
                        .replace(
                            /^\d+\.\s+/,
                            ""
                        );

                return `
                    <div
                        class="ci-check-item ${type}"
                        style="--item-delay:${index * 80}ms"
                    >

                        <div class="ci-check-icon">
                            ${
                                type === "risk"
                                    ? "!"
                                    : "×"
                            }
                        </div>

                        <span>
                            ${formatInlineText(
                                clean
                            )}
                        </span>

                    </div>
                `;
            }
        )
        .join("");
}


function renderSteps(
    content
) {

    const items =
        cleanAIResponse(content)
            .split("\n")
            .map(line => line.trim())
            .filter(line =>
                /^\d+\.\s+/.test(line)
            );

    if (!items.length) {

        return `
            <div class="ci-text-card">
                ${formatPlainText(content)}
            </div>
        `;
    }

    return items
        .map(
            (item, index) => {

                const clean =
                    item.replace(
                        /^\d+\.\s+/,
                        ""
                    );

                return `
                    <div
                        class="ci-step"
                        style="--item-delay:${index * 100}ms"
                    >

                        <div class="ci-step-number">
                            ${String(
                                index + 1
                            ).padStart(2, "0")}
                        </div>

                        <div class="ci-step-line"></div>

                        <div class="ci-step-content">

                            <strong>
                                ${formatInlineText(
                                    clean
                                )}
                            </strong>

                            <span>
                                Implementation step
                            </span>

                        </div>

                    </div>
                `;
            }
        )
        .join("");
}


// =========================================
// HTML SECURITY
// =========================================

function escapeHTML(
    value
) {

    return String(value)

        .replace(
            /&/g,
            "&amp;"
        )

        .replace(
            /</g,
            "&lt;"
        )

        .replace(
            />/g,
            "&gt;"
        )

        .replace(
            /"/g,
            "&quot;"
        )

        .replace(
            /'/g,
            "&#039;"
        );

}


// =========================================
// REGEX ESCAPE
// =========================================

function escapeRegex(value) {

    return value.replace(
        /[.*+?^${}()|[\]\\]/g,
        "\\$&"
    );

}


// =========================================
// INITIAL PAGE
// =========================================

showPage(
    "dashboard"
);