const API_BASE_URL = window.REVEXA_API_BASE_URL || "http://127.0.0.1:8000";

// =========================================
// AI PROVIDERS
// =========================================
// API keys stay in the backend .env file.
// Frontend sends only the selected provider.
//
// GEMINI_API_KEY
// GROQ_API_KEY
// =========================================

const AI_PROVIDERS = {
    gemini: {
        label: "Gemini"
    },
    groq: {
        label: "Groq"
    }
};

function getSelectedProvider() {

    const value =
        String(aiModel?.value || "gemini")
            .trim()
            .toLowerCase();

    return AI_PROVIDERS[value]
        ? value
        : "gemini";
}

function ensureProviderOptions() {

    if (!aiModel) {
        return;
    }

    Object.entries(AI_PROVIDERS)
        .forEach(([value, provider]) => {

            const exists =
                Array.from(aiModel.options)
                    .some(
                        option =>
                            option.value === value
                    );

            if (!exists) {

                const option =
                    document.createElement("option");

                option.value = value;
                option.textContent =
                    provider.label;

                aiModel.appendChild(option);
            }
        });
}





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

            getSelectedProvider();





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

            `${repository} • ${AI_PROVIDERS[model].label}`;





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

                    data.error ||

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

            \<div class="answer-empty">

                \<p>

                    No answer was returned

                    by the AI provider.

                \</p>

            \</div>

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
    const cleanAnswer = cleanAIResponse(answer || "").trim();
    const genericSuccess = /^(analysis completed successfully\.?|repository insights\.?|the repository investigation could not be completed\.?)$/i;

    if (!cleanAnswer || genericSuccess.test(cleanAnswer)) {
        return `
            <section class="friendly-report-state is-incomplete" role="status">
                <div class="friendly-report-icon" aria-hidden="true">!</div>
                <div><span class="friendly-report-kicker">REPORT NOT READY</span>
                    <h2>We couldn't finish checking this repository.</h2>
                    <p>No useful results came back, so this is <strong>not</strong> a clean bill of health. Try again or check the AI provider connection.</p>
                </div>
            </section>`;
    }

    const sections = parseAnswerSections(cleanAnswer);
    if (!sections.length) {
        return `
            <section class="friendly-report-hero">
                <div class="friendly-report-kicker">YOUR REPOSITORY ANSWER</div>
                <h2>Here's what Revexa found</h2>
                <p class="friendly-report-lead">${formatPlainText(cleanAnswer)}</p>
            </section>
            <details class="friendly-report-details"><summary>Read the full AI response</summary><div class="revexa-report-body">${formatPlainText(cleanAnswer)}</div></details>`;
    }

    const summary = getSection(sections, "SUMMARY");
    const findings = getSection(sections, "WHAT I FOUND");
    const evidence = getSection(sections, "EVIDENCE");
    const missing = getSection(sections, "WHAT IS MISSING");
    const risks = getSection(sections, "RISKS OR CONCERNS");
    const improvements = getSection(sections, "HOW TO ADD OR IMPROVE IT");
    const recommendation = getSection(sections, "FINAL RECOMMENDATION");
    const simpleSummary = summary?.content || findings?.content || "Revexa checked the repository and returned the details below.";
    const cards = [
        { key: "findings", icon: "◈", title: "Things found", plain: "What Revexa noticed", content: findings?.content },
        { key: "risks", icon: "△", title: "Things to watch", plain: "Possible problems", content: risks?.content },
        { key: "missing", icon: "○", title: "Things not found", plain: "What may be missing", content: missing?.content },
        { key: "improvements", icon: "✦", title: "Ways to improve", plain: "What you can do next", content: improvements?.content }
    ].filter(card => card.content && card.content.trim());
    const countFor = content => extractList(content).length;
    const totalItems = cards.reduce((sum, card) => sum + countFor(card.content), 0);
    const summaryText = cleanAIResponse(simpleSummary).replace(/^[-•*\s]+/, '').trim();
    const firstSentence = summaryText.split(/(?<=[.!?])\s+/)[0] || summaryText;

    const cardMarkup = cards.map(card => `
        <details class="friendly-report-card ${card.key}" open>
            <summary>
                <span class="friendly-card-icon" aria-hidden="true">${card.icon}</span>
                <span class="friendly-card-title"><strong>${card.title}</strong><small>${card.plain}</small></span>
                <span class="friendly-card-count">${countFor(card.content) || "•"}</span>
                <span class="friendly-card-toggle" aria-hidden="true">⌄</span>
            </summary>
            <div class="friendly-card-content revexa-report-body">${formatPlainText(card.content)}</div>
        </details>`).join("");

    return `
        <section class="friendly-report-hero">
            <div class="friendly-report-topline"><span class="friendly-report-kicker">YOUR REPOSITORY REPORT</span><span class="friendly-report-pill">AI checked</span></div>
            <h2>Here's what Revexa found</h2>
            <p class="friendly-report-lead">${formatPlainText(firstSentence)}</p>
            <div class="friendly-report-translation"><span class="translation-icon" aria-hidden="true">💡</span><div><strong>In simple words</strong><p>${formatPlainText(summaryText)}</p></div></div>
        </section>
        <section class="friendly-report-overview" aria-label="Report overview">
            <div><strong>${cards.length}</strong><span>Topics explained</span></div>
            <div><strong>${totalItems || "—"}</strong><span>Listed points</span></div>
            <div><strong>${evidence ? "Yes" : "—"}</strong><span>Code evidence</span></div>
        </section>
        ${cards.length ? `<div class="friendly-report-section-title"><div><span class="friendly-report-kicker">THE IMPORTANT PARTS</span><h3>What does this mean?</h3></div><p>Open a card to see the details.</p></div><div class="friendly-report-cards">${cardMarkup}</div>` : ""}
        ${evidence ? `<details class="friendly-report-details"><summary><span>⌕</span><span><strong>Show proof</strong><small>Files and code references used for this answer</small></span></summary><div class="revexa-report-body">${formatPlainText(evidence.content)}</div></details>` : ""}
        ${recommendation ? `<section class="friendly-report-next"><span class="friendly-report-kicker">WHAT TO DO NEXT</span><h3>Your next step</h3><div class="revexa-report-body">${formatPlainText(recommendation.content)}</div></section>` : ""}
        <details class="friendly-report-details technical-details"><summary><span>⚙</span><span><strong>Technical details</strong><small>Read the full engineering explanation</small></span></summary>
            ${sections.map(section => `<div class="technical-report-block"><h4>${escapeHTML(section.title.replace(/_/g, " "))}</h4><div class="revexa-report-body">${formatPlainText(section.content)}</div></div>`).join("")}
        </details>
        <p class="revexa-report-footnote">AI can make mistakes. Check important points in the actual code and run tests before changing or merging anything.</p>`;
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
    `^\\s*(${pattern})\\s*$`,
    "gim"
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

        \<div class="ci-stat-card">



            \<div class="ci-stat-icon">

                ${icon}

            \</div>



            \<div class="ci-stat-value">

                ${value}

            \</div>



            \<div class="ci-stat-label">

                ${label}

            \</div>



        \</div>

    `;

}





function sectionHeading(

    title,

    description

) {



    return `

        \<div class="ci-section-heading">



            \<div>

                \<span>

                    CODE INTELLIGENCE

                \</span>



                \<h3>

                    ${title}

                \</h3>



                \<p>

                    ${description}

                \</p>

            \</div>



        \</div>

    `;

}





function renderFindingCards(content) {
    const items = extractList(content);
    if (!items.length) {
        return `<div class="ci-text-card">${formatPlainText(content)}</div>`;
    }

    return items.map((item, index) => {
        const clean = item.replace(/^[-•*]\s+/, "").trim();
        const findingId = `revexa-finding-${index + 1}-${simpleHash(clean)}`;
        const reviewed = localStorage.getItem(`revexa.reviewed.${findingId}`) === "true";
        return `
            <article class="ci-finding-card ${reviewed ? "is-reviewed" : ""}"
                     data-finding-id="${findingId}" data-finding-text="${escapeHTML(clean)}"
                     style="--item-delay:${index * 70}ms">
                <div class="ci-finding-number">${String(index + 1).padStart(2, "0")}</div>
                <div class="ci-finding-content">
                    <div class="ci-finding-title">${formatInlineText(clean)}</div>
                    <div class="ci-finding-line">${reviewed ? "Reviewed" : "Repository finding"}</div>
                    <div class="ci-finding-detail" id="${findingId}-detail" aria-hidden="true">
                        <strong>Finding details</strong>
                        <p>${formatInlineText(clean)}</p>
                        <p class="ci-detail-note">This is the finding text returned by the analysis agent. Check the referenced code before treating it as a confirmed defect.</p>
                    </div>
                    <div class="ci-finding-actions">
                        <button type="button" class="ci-expand-action" aria-expanded="false" aria-controls="${findingId}-detail" data-finding-action="expand">View details</button>
                        <button type="button" data-finding-action="copy">Copy finding</button>
                        <button type="button" data-finding-action="review">${reviewed ? "Mark unreviewed" : "Mark reviewed"}</button>
                    </div>
                </div>
                <div class="ci-finding-arrow" aria-hidden="true">→</div>
            </article>
        `;
    }).join("");
}

function simpleHash(value) {
    let hash = 0;
    for (let i = 0; i < value.length; i++) hash = ((hash << 5) - hash + value.charCodeAt(i)) | 0;
    return Math.abs(hash).toString(36);
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

                        \<div class="ci-evidence-card">

                            ${formatInlineText(

                                line

                            )}

                        \</div>

                    `;

                }



                return `

                    \<details

                        class="ci-evidence-card"

                        style="--item-delay:${index * 70}ms"

                    >



                        \<summary>



                            \<div class="ci-file-icon">

                                JS

                            \</div>



                            \<div class="ci-file-info">



                                \<strong>

                                    ${escapeHTML(

                                        match[1]

                                    )}

                                \</strong>



                                \<span>

                                    Repository evidence

                                \</span>



                            \</div>



                            \<div class="ci-chevron">

                                +

                            \</div>



                        \</summary>



                        \<div class="ci-evidence-detail">



                            ${formatInlineText(

                                match[2]

                            )}



                        \</div>



                    \</details>

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

            \<div class="ci-text-card">

                ${formatPlainText(content)}

            \</div>

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

                    \<div

                        class="ci-check-item ${type}"

                        style="--item-delay:${index * 80}ms"

                    >



                        \<div class="ci-check-icon">

                            ${

                                type === "risk"

                                    ? "!"

                                    : "×"

                            }

                        \</div>



                        \<span>

                            ${formatInlineText(

                                clean

                            )}

                        \</span>



                    \</div>

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

            \<div class="ci-text-card">

                ${formatPlainText(content)}

            \</div>

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

                    \<div

                        class="ci-step"

                        style="--item-delay:${index * 100}ms"

                    >



                        \<div class="ci-step-number">

                            ${String(

                                index + 1

                            ).padStart(2, "0")}

                        \</div>



                        \<div class="ci-step-line">\</div>



                        \<div class="ci-step-content">



                            \<strong>

                                ${formatInlineText(

                                    clean

                                )}

                            \</strong>



                            \<span>

                                Implementation step

                            \</span>



                        \</div>



                    \</div>

                `;

            }

        )

        .join("");

}





// =========================================

// =========================================
// PLAIN TEXT
// =========================================

function formatPlainText(text) {

    return cleanAIResponse(text)
        .split(/\n+/)
        .map(
            line =>
                line.trim()
        )
        .filter(Boolean)
        .map(
            line =>
                `<p>${formatInlineText(line)}</p>`
        )
        .join("");
}


// =========================================
// INLINE MARKDOWN
// =========================================

function formatInlineText(text) {

    let value =
        escapeHTML(text);

    value =
        value.replace(
            /\*\*(.*?)\*\*/g,
            "<strong>$1</strong>"
        );

    value =
        value.replace(
            /`([^`]+)`/g,
            "<code>$1</code>"
        );

    return value;
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

            /\</g,

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

        "\\\\$&"

    );



}





// =========================================

// INITIAL PAGE

// =========================================



ensureProviderOptions();

showPage(

    "dashboard"

);


// =========================================
// GITHUB OAUTH SESSION + REPOSITORY PICKER
// =========================================
const githubConnectButton = document.getElementById("githubConnectButton");
const githubConnectLabel = document.getElementById("githubConnectLabel");
const profileMenu = document.getElementById("profileMenu");
const profileAvatar = document.getElementById("profileAvatar");
const profileLogin = document.getElementById("profileLogin");
const githubLogoutButton = document.getElementById("githubLogoutButton");
const loadGithubReposButton = document.getElementById("loadGithubReposButton");
const githubRepositoriesHint = document.getElementById("githubRepositoriesHint");
const githubRepositorySelect = document.getElementById("githubRepositorySelect");

async function refreshGitHubSession() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/auth/me`, { credentials: "include" });
        if (!response.ok) throw new Error(`Session check failed (${response.status})`);
        const data = await response.json();
        const user = data.user;
        if (data.authenticated && user) {
            const hasGitHub = Boolean(user.connected);
            if (githubConnectLabel) githubConnectLabel.textContent = hasGitHub ? "GitHub connected" : "Connect GitHub";
            githubConnectButton?.classList.toggle("connected", hasGitHub);
            if (profileMenu) profileMenu.hidden = false;
            if (profileLogin) profileLogin.textContent = user.login || user.name || user.email || "Signed-in user";
            if (profileAvatar) {
                profileAvatar.onerror = () => {
                    // If the stored avatar URL is stale, retry GitHub's public avatar
                    // endpoint once before hiding the image to avoid a broken-image icon.
                    const fallback = user.login
                        ? `https://github.com/${encodeURIComponent(user.login)}.png?size=64`
                        : "";
                    if (fallback && profileAvatar.dataset.fallbackTried !== "true" && profileAvatar.src !== fallback) {
                        profileAvatar.dataset.fallbackTried = "true";
                        profileAvatar.src = fallback;
                    } else {
                        profileAvatar.hidden = true;
                        const fallbackBadge = document.getElementById("profileAvatarFallback");
                        if (fallbackBadge) {
                            fallbackBadge.hidden = false;
                            fallbackBadge.textContent = (user.login || user.name || user.email || "R").trim().slice(0, 1).toUpperCase();
                        }
                    }
                };
                const fallbackBadge = document.getElementById("profileAvatarFallback");
                if (fallbackBadge) fallbackBadge.hidden = true;
                profileAvatar.dataset.fallbackTried = "false";
                if (user.avatar_url) {
                    profileAvatar.hidden = false;
                    profileAvatar.src = user.avatar_url;
                } else if (user.login && user.connected) {
                    profileAvatar.hidden = false;
                    profileAvatar.src = `https://github.com/${encodeURIComponent(user.login)}.png?size=64`;
                } else {
                    profileAvatar.removeAttribute("src");
                    profileAvatar.hidden = true;
                    const fallbackBadge = document.getElementById("profileAvatarFallback");
                    if (fallbackBadge) { fallbackBadge.hidden = false; fallbackBadge.textContent = (user.login || user.name || user.email || "R").trim().slice(0, 1).toUpperCase(); }
                }
            }
            githubRepositoriesHint.textContent = hasGitHub
                ? `Connected as @${user.login}. Load repositories to get started.`
                : `Signed in with ${user.provider || "email"}${hasGitHub ? "" : ". Connect GitHub to browse repositories."}`;
            const settingsStatus = document.getElementById("settingsGithubStatus");
            const settingsButton = document.getElementById("settingsGithubButton");
            if (settingsStatus) settingsStatus.textContent = hasGitHub ? `Connected as @${user.login}.` : "No GitHub account connected to this session.";
            if (settingsButton) settingsButton.textContent = hasGitHub ? "Reconnect GitHub" : "Connect GitHub";
        } else {
            githubConnectLabel.textContent = "Connect GitHub";
            githubConnectButton?.classList.remove("connected");
            profileMenu.hidden = true;
            githubRepositoriesHint.textContent = "Connect GitHub to browse your authorized repositories here.";
            const settingsStatus = document.getElementById("settingsGithubStatus");
            const settingsButton = document.getElementById("settingsGithubButton");
            if (settingsStatus) settingsStatus.textContent = "Not connected.";
            if (settingsButton) settingsButton.textContent = "Connect GitHub";
        }
    } catch (error) {
        githubRepositoriesHint.textContent = "Backend unavailable. Start FastAPI and refresh this page.";
    }
}

if (githubConnectButton) {
    githubConnectButton.addEventListener("click", () => {
        window.location.href = `${API_BASE_URL}/api/auth/github/login`;
    });
}

if (githubLogoutButton) {
    githubLogoutButton.addEventListener("click", async () => {
        githubLogoutButton.disabled = true;
        try {
            await fetch(`${API_BASE_URL}/api/auth/logout`, {
                method: "POST", credentials: "include"
            });
        } catch (error) {
            console.warn("Logout request could not reach the backend:", error);
        } finally {
            // Always return to the public page; it will show the signed-out state.
            window.location.replace("index.html?logged_out=1");
        }
    });
}

if (loadGithubReposButton) {
    loadGithubReposButton.addEventListener("click", async () => {
        loadGithubReposButton.disabled = true;
        loadGithubReposButton.textContent = "Loading…";
        try {
            const response = await fetch(`${API_BASE_URL}/api/auth/github/repos`, { credentials: "include" });
            const data = await response.json();
            if (!response.ok) throw new Error(data.detail || "Could not load repositories");
            githubRepositorySelect.innerHTML = '<option value="">Choose a repository</option>';
            data.repositories.forEach((repo) => {
                const option = document.createElement("option");
                option.value = repo.url;
                option.textContent = `${repo.name}${repo.private ? " · private" : ""}`;
                githubRepositorySelect.appendChild(option);
            });
            githubRepositorySelect.hidden = false;
            githubRepositoriesHint.textContent = `${data.repositories.length} repositories available.`;
        } catch (error) {
            githubRepositoriesHint.textContent = error.message;
        } finally {
            loadGithubReposButton.disabled = false;
            loadGithubReposButton.textContent = "Load repositories";
        }
    });
}

if (githubRepositorySelect) {
    githubRepositorySelect.addEventListener("change", () => {
        if (githubRepositorySelect.value && repoUrl) repoUrl.value = githubRepositorySelect.value;
    });
}

const authQuery = new URLSearchParams(window.location.search);
if (authQuery.get("auth") === "connected") {
    history.replaceState({}, document.title, window.location.pathname);
}
if (authQuery.get("auth_error")) {
    const githubAuthMessages = {
        github_denied: "GitHub sign-in was cancelled. You can try connecting again.",
        github_not_configured: "GitHub OAuth is not configured. Check the backend OAuth settings.",
        github_state_invalid: "The GitHub sign-in session expired or could not be verified. Start the connection again.",
        github_code_expired: "This GitHub sign-in link has already been used or expired. Start a fresh connection; do not refresh the callback page.",
        github_token_exchange_failed: "GitHub could not complete the token exchange. Check the OAuth client ID, secret and callback URL.",
        github_profile_failed: "GitHub authorized the app, but Revexa could not load your GitHub profile. Try again.",
        github_account_conflict: "This GitHub account is already connected to a different Revexa account. Sign out, then sign in using the Revexa account that already owns this GitHub identity. Accounts are not merged automatically for security.",
    };
    const errorCode = authQuery.get("auth_error");
    if (githubRepositoriesHint) {
        githubRepositoriesHint.textContent = githubAuthMessages[errorCode] || "GitHub connection could not be completed. Please start a new connection.";
        githubRepositoriesHint.classList.add("is-error");
        githubRepositoriesHint.setAttribute("role", "alert");
    }
    history.replaceState({}, document.title, window.location.pathname);
}

// =========================================
// PR REVIEW + LOCAL WORKSPACE HISTORY
// =========================================
const PR_HISTORY_KEY = "mergemind.workspace.history.v1";
const prUrlInput = document.getElementById("prUrlInput");
const runPrReviewButton = document.getElementById("runPrReviewButton");
const prReviewButtonText = document.getElementById("prReviewButtonText");
const prReviewLoader = document.getElementById("prReviewLoader");
const prReviewResult = document.getElementById("prReviewResult");
const prReviewModel = document.getElementById("prReviewModel");

function readWorkspaceHistory() {
    try {
        const value = JSON.parse(localStorage.getItem(PR_HISTORY_KEY) || "[]");
        return Array.isArray(value) ? value : [];
    } catch (_) { return []; }
}

function recordWorkspaceSession(entry) {
    const history = readWorkspaceHistory();
    history.unshift({
        id: `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
        type: entry.type || "Workspace activity",
        title: entry.title || "Completed task",
        repository: entry.repository || "",
        detail: entry.detail || "",
        findings: Number(entry.findings || 0),
        at: new Date().toISOString()
    });
    try { localStorage.setItem(PR_HISTORY_KEY, JSON.stringify(history.slice(0, 100))); }
    catch (error) { console.warn("Could not save local history", error); }
    renderWorkspaceHistory();
}

function safeText(value) {
    return String(value ?? "").replace(/[&<>"']/g, char => ({
        "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
    })[char]);
}

function renderWorkspaceHistory() {
    const history = readWorkspaceHistory();
    const sessions = document.getElementById("sessionsList");
    const activity = document.getElementById("activityList");
    const sessionEmpty = '<div class="empty-state"><span>◷</span><h3>No sessions yet</h3><p>Run a repository analysis or PR review and it will appear here.</p><button class="secondary-action" data-go-page="repository" type="button">Start an analysis</button></div>';
    const activityEmpty = '<div class="empty-state"><span>⌁</span><h3>Nothing to show yet</h3><p>Your completed analyses will be listed here.</p></div>';
    const cards = history.map(item => {
        const date = new Date(item.at);
        const dateText = Number.isNaN(date.getTime()) ? "Saved locally" : date.toLocaleString();
        return `<article class="history-item"><div class="history-icon">${item.type === "PR review" ? "⌘" : "◈"}</div><div class="history-main"><h3>${safeText(item.title)}</h3><p>${safeText(item.type)}${item.repository ? ` · ${safeText(item.repository)}` : ""}${item.detail ? ` · ${safeText(item.detail)}` : ""}</p></div><span class="history-time">${safeText(dateText)}</span></article>`;
    }).join("");
    if (sessions) sessions.innerHTML = cards || sessionEmpty;
    if (activity) activity.innerHTML = cards || activityEmpty;
    const uniqueRepos = new Set(history.map(item => item.repository).filter(Boolean));
    const metric = (id, value) => { const node = document.getElementById(id); if (node) node.textContent = String(value); };
    metric("metricSessions", history.length);
    metric("metricRepos", uniqueRepos.size);
    metric("metricPrReviews", history.filter(item => item.type === "PR review").length);
    const findingsTotal = history.reduce((sum, item) => sum + Number(item.findings || 0), 0);
    metric("metricFindings", findingsTotal);
    metric("dashboardMetricRepos", uniqueRepos.size);
    metric("dashboardMetricReviews", history.filter(item => item.type === "PR review").length);
    metric("dashboardMetricFindings", findingsTotal);
    metric("dashboardMetricSessions", history.length);
    const dashboardRecent = document.getElementById("dashboardRecentSessions");
    if (dashboardRecent) {
        dashboardRecent.innerHTML = history.slice(0, 3).map(item => {
            const when = new Date(item.at);
            const relative = Number.isNaN(when.getTime()) ? "Saved locally" : when.toLocaleDateString();
            return `<div class="session"><div class="session-icon">${item.type === "PR review" ? "⌘" : "◈"}</div><div class="session-info"><strong>${safeText(item.title)}</strong><span>${safeText(item.type)}${item.repository ? ` · ${safeText(item.repository)}` : ""}</span></div><span class="status completed">Completed</span><small>${safeText(relative)}</small></div>`;
        }).join("") || '<div class="empty-state compact-empty"><h3>No recent activity</h3><p>Your completed repository analyses and PR reviews will show here.</p></div>';
    }
}

function renderPrReview(data, prUrl) {
    const pr = data.pr || {};
    const reviewPayload = data.review || {};
    if (reviewPayload.provider === "comparison") {
        const review = reviewPayload;
        const cards = Object.entries(review.results || {}).map(([provider, result]) => {
            const findings = Array.isArray(result.issues) ? result.issues : [];
            return `<section class="review-provider-column"><h3>${safeText(provider === "gemini" ? "Gemini review" : "Groq review")}</h3><p>${safeText(result.summary || "")}</p><p>${safeText(result.overall_assessment || "")}</p><h4>${findings.length} findings</h4>${findings.map(item => `<article class="review-issue"><strong>${safeText(item.severity || "Finding")} · ${safeText(item.category || "Code quality")}</strong><p>${safeText(item.message || "")}</p><small>${safeText(item.file || "File unavailable")}${item.line ? ` · line ${safeText(item.line)}` : ""}</small><p>${safeText(item.suggestion || "")}</p></article>`).join("") || "<p>No actionable findings returned.</p>"}</section>`;
        }).join("");
        const errors = Object.entries(review.errors || {}).map(([name, message]) => `<p class="field-help">${safeText(name)} unavailable: ${safeText(message)}</p>`).join("");
        prReviewResult.innerHTML = `<section class="review-report-head"><span class="eyebrow">AI MODEL COMPARISON</span><h3>${safeText(pr.title || "Pull request review")}</h3><p>Each provider reviewed the same pull-request diff independently.</p></section><div class="review-provider-comparison">${cards}</div>${errors}`;
        return;
    }
    const review = reviewPayload.review || reviewPayload;
    const issues = Array.isArray(review.issues) ? review.issues : [];
    const recommendations = Array.isArray(review.recommendations) ? review.recommendations : [];
    const severityClass = value => {
        const normalized = String(value || "low").toLowerCase();
        if (normalized.includes("critical")) return "critical";
        if (normalized.includes("high")) return "high";
        if (normalized.includes("medium") || normalized.includes("moderate")) return "medium";
        return "low";
    };
    const issueMarkup = issues.length ? issues.map((issue, index) => `
        <article class="review-issue">
            <div class="review-report-meta"><span class="issue-severity ${severityClass(issue.severity)}">${safeText(issue.severity || "Finding")}</span><span>${safeText(issue.category || "Code quality")}</span></div>
            <h4>${safeText(issue.message || `Finding ${index + 1}`)}</h4>
            <div class="issue-location">${safeText(issue.file || "File not specified")}${issue.line ? ` · line ${safeText(issue.line)}` : ""}</div>
            ${issue.suggestion ? `<p><strong>Suggested fix:</strong> ${safeText(issue.suggestion)}</p>` : ""}
        </article>`).join("") : '<article class="review-issue"><h4>No specific issues returned</h4><p>The review did not identify actionable findings in the supplied diff. Still inspect and test the changes before merging.</p></article>';
    const recommendationsMarkup = recommendations.length ? `<section class="review-recommendations"><h4>Recommended next steps</h4><ul>${recommendations.map(item => `<li>${safeText(item)}</li>`).join("")}</ul></section>` : "";
    prReviewResult.innerHTML = `
        <section class="review-report-head">
            <span class="eyebrow">REVIEW COMPLETE</span><h3>${safeText(pr.title || "Pull request review")}</h3>
            <p>${safeText(pr.description || "No pull request description provided.")}</p>
            <div class="review-report-meta"><span>${safeText(pr.author ? `@${pr.author}` : "GitHub pull request")}</span><span>${safeText(pr.state || "state unavailable")}</span><span>${safeText(pr.changed_files ?? issues.length)} changed files</span><span>${issues.length} findings</span></div>
            <p><strong>Overall assessment:</strong> ${safeText(review.overall_assessment || "Review completed; verify findings before merging.")}</p>
            <p>${safeText(review.summary || "The AI review has completed.")}</p>
            <p><a class="review-source-link" href="${safeText(prUrl)}" target="_blank" rel="noopener noreferrer">Open pull request ↗</a></p>
        </section>
        <div class="review-issues">${issueMarkup}</div>${recommendationsMarkup}`;
}

if (runPrReviewButton) {
    runPrReviewButton.addEventListener("click", async () => {
        const prUrl = (prUrlInput?.value || "").trim();
        if (!/^https?:\/\/github\.com\/[^/]+\/[^/]+\/pull\/\d+\/?(?:\?.*)?$/i.test(prUrl)) {
            prReviewResult.innerHTML = '<div class="empty-state"><h3>Enter a valid GitHub pull request URL</h3><p>Expected format: https://github.com/owner/repository/pull/123</p></div>';
            prUrlInput?.focus();
            return;
        }
        runPrReviewButton.disabled = true;
        if (prReviewButtonText) prReviewButtonText.textContent = "Reviewing pull request…";
        prReviewLoader?.classList.remove("hidden");
        prReviewResult.innerHTML = '<div class="empty-state"><span>✦</span><h3>Review in progress</h3><p>Fetching changed files and asking the review agent to inspect the diff.</p></div>';
        try {
            const response = await fetch(`${API_BASE_URL}/api/review`, {
                method: "POST", credentials: "include", headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ pr_url: prUrl, model: prReviewModel?.value || "gemini" })
            });
            const data = await response.json();
            if (!response.ok) throw new Error(data.detail || "PR review failed. Check backend logs and credentials.");
            renderPrReview(data, prUrl);
            const parsed = data.review || {};
            recordWorkspaceSession({ type: "PR review", title: data.pr?.title || prUrl, repository: prUrl.split("/pull/")[0], detail: `${data.risk?.level || "Risk assessed"}`, findings: Array.isArray(parsed.issues) ? parsed.issues.length : 0 });
        } catch (error) {
            prReviewResult.innerHTML = `<div class="empty-state"><span>!</span><h3>Review could not be completed</h3><p>${safeText(error.message || "Unexpected error")}</p><p>Confirm the backend is running and backend/.env contains valid GitHub and selected AI provider credentials.</p></div>`;
        } finally {
            runPrReviewButton.disabled = false;
            if (prReviewButtonText) prReviewButtonText.textContent = "Run PR review";
            prReviewLoader?.classList.add("hidden");
        }
    });
}

function clearWorkspaceHistory() {
    if (!window.confirm("Clear the session history saved in this browser?")) return;
    localStorage.removeItem(PR_HISTORY_KEY);
    renderWorkspaceHistory();
}
document.getElementById("clearHistoryButton")?.addEventListener("click", clearWorkspaceHistory);
document.getElementById("settingsClearHistoryButton")?.addEventListener("click", clearWorkspaceHistory);
document.querySelectorAll("[data-go-page]").forEach(button => button.addEventListener("click", () => showPage(button.dataset.goPage)));

const defaultProviderSetting = document.getElementById("defaultProviderSetting");
if (defaultProviderSetting && aiModel) {
    const savedProvider = localStorage.getItem("mergemind.defaultProvider");
    if (savedProvider && ["gemini", "groq"].includes(savedProvider)) aiModel.value = savedProvider;
    defaultProviderSetting.value = aiModel.value === "groq" ? "groq" : "gemini";
    defaultProviderSetting.addEventListener("change", () => {
        aiModel.value = defaultProviderSetting.value;
        localStorage.setItem("mergemind.defaultProvider", defaultProviderSetting.value);
    });
}
document.getElementById("settingsGithubButton")?.addEventListener("click", () => {
    window.location.href = `${API_BASE_URL}/api/auth/github/login`;
});


// Accessible finding-card interactions: expand, copy, and local reviewed state.
document.addEventListener("click", async (event) => {
    const button = event.target.closest("[data-finding-action]");
    if (!button) return;
    const card = button.closest(".ci-finding-card");
    if (!card) return;

    const action = button.dataset.findingAction;
    const findingId = card.dataset.findingId;
    const findingText = card.dataset.findingText || "";

    if (action === "expand") {
        const expanded = card.classList.toggle("is-expanded");
        button.setAttribute("aria-expanded", String(expanded));
        button.textContent = expanded ? "Hide details" : "View details";
        card.querySelector(".ci-finding-detail")?.setAttribute("aria-hidden", String(!expanded));
        return;
    }

    if (action === "copy") {
        try {
            await navigator.clipboard.writeText(findingText);
            const original = button.textContent;
            button.textContent = "Copied";
            window.setTimeout(() => { button.textContent = original; }, 1400);
        } catch {
            const area = document.createElement("textarea");
            area.value = findingText;
            area.setAttribute("readonly", "");
            area.style.position = "fixed";
            area.style.opacity = "0";
            document.body.appendChild(area);
            area.select();
            const copied = document.execCommand("copy");
            area.remove();
            button.textContent = copied ? "Copied" : "Copy unavailable";
            window.setTimeout(() => { button.textContent = "Copy finding"; }, 1400);
        }
        return;
    }

    if (action === "review") {
        const reviewed = !card.classList.contains("is-reviewed");
        card.classList.toggle("is-reviewed", reviewed);
        localStorage.setItem(`revexa.reviewed.${findingId}`, String(reviewed));
        const status = card.querySelector(".ci-finding-line");
        if (status) status.textContent = reviewed ? "Reviewed" : "Repository finding";
        button.textContent = reviewed ? "Mark unreviewed" : "Mark reviewed";
    }
});

renderWorkspaceHistory();

refreshGitHubSession();
