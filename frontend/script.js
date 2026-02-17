// Navigation
function navigate(sectionId) {
    document.querySelectorAll('.app-section').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));

    document.getElementById(`section-${sectionId}`).classList.add('active');

    // Find nav item by text match or icon (simple heuristic)
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => {
        if (item.getAttribute('onclick') && item.getAttribute('onclick').includes(sectionId)) {
            item.classList.add('active');
        }
    });

    const titles = {
        'search': 'Legal Research Dashboard',
        'drafting': 'Automated Document Drafting',
        'help': 'Emergency Legal Aid'
    };
    document.getElementById('main-title').innerText = titles[sectionId] || 'Defend U';
}

// Voice Search
let recognition;
if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;

    recognition.onstart = () => {
        document.getElementById('voice-btn').classList.add('listening');
    };

    recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        document.getElementById('query').value = transcript;
        searchLegal();
    };

    recognition.onend = () => {
        document.getElementById('voice-btn').classList.remove('listening');
    };

    recognition.onerror = () => {
        document.getElementById('voice-btn').classList.remove('listening');
    };
}

function startVoiceSearch() {
    if (!recognition) {
        alert("Speech Recognition not supported in this browser.");
        return;
    }
    recognition.start();
}

async function searchLegal() {
    const query = document.getElementById("query").value;
    const resultsDiv = document.getElementById("results");

    if (!query) return;

    resultsDiv.innerHTML = '<div class="loading-spinner">Searching Legal Database...</div>';

    try {
        const lang = currentLanguage;
        const response = await fetch("http://127.0.0.1:8000/ask", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ query: query, lang: lang })
        });

        const data = await response.json();
        renderResults(data, resultsDiv);

    } catch (err) {
        resultsDiv.innerHTML = "❌ Backend not running or CORS blocked";
        console.error(err);
    }
}

// Retro Typewriter Effect
function typeWriter(element, text, speed = 10) {
    element.innerHTML = "";
    let i = 0;
    function type() {
        if (i < text.length) {
            element.innerHTML += text.charAt(i);
            i++;
            setTimeout(type, speed);
        }
    }
    type();
}

function renderResults(data, container) {
    container.innerHTML = ""; // Clear existing

    // 0. Rights & Roadmap (Primary for Help)
    if (data.rights && data.rights.length > 0) {
        const rightsCard = document.createElement("div");
        rightsCard.className = "card";
        rightsCard.style.gridColumn = "1 / -1";
        rightsCard.style.borderColor = "var(--accent)";
        rightsCard.innerHTML = `
            <h2 style="color: var(--accent); margin-bottom: 1.5rem;">🚨 Know Your Rights</h2>
            <ul class="rights-list">
                ${data.rights.map(r => `<li>${r}</li>`).join("")}
            </ul>
        `;
        container.appendChild(rightsCard);
    }

    if (data.roadmap && data.roadmap.length > 0) {
        const roadmapCard = document.createElement("div");
        roadmapCard.className = "card";
        roadmapCard.style.gridColumn = "1 / -1";
        roadmapCard.innerHTML = `
            <h2 style="color: var(--accent-gold); margin-bottom: 1.5rem;">🗺️ Legal Roadmap</h2>
            <div class="roadmap-container">
                ${data.roadmap.map((step, idx) => `
                    <div class="roadmap-step">
                        <div class="step-num">${idx + 1}</div>
                        <div>${step}</div>
                    </div>
                `).join("")}
            </div>
        `;
        container.appendChild(roadmapCard);
    }

    // 1. Topic Overview (Typed)
    if (data.summary) {
        const summaryCard = document.createElement("div");
        summaryCard.className = "card topic-overview";
        summaryCard.style.borderLeft = "4px solid var(--accent)";
        summaryCard.style.background = "linear-gradient(90deg, rgba(100, 255, 218, 0.05), transparent)";
        summaryCard.style.gridColumn = "1 / -1";
        summaryCard.innerHTML = `
            <h3 style="color: var(--accent); margin-bottom: 0.5rem;">> TOPIC_OVERVIEW</h3>
            <p id="summary-text" style="font-size: 1.1rem; line-height: 1.6; font-family: 'Courier New', monospace;"></p>
        `;
        container.appendChild(summaryCard);
        typeWriter(summaryCard.querySelector("#summary-text"), data.summary, 10);
    }

    // 2. Local Results
    if (data.local_results && data.local_results.length > 0) {
        const localHeader = document.createElement("div");
        localHeader.className = "section-header";
        localHeader.innerText = "> INTERNAL_DATABASE_MATCHES";
        container.appendChild(localHeader);

        data.local_results.forEach(res => {
            const card = document.createElement("div");
            card.className = "card";
            card.innerHTML = `
                <span class="card-tag tag-local">LOCAL_PRECEDENT</span>
                <p class="card-snippet">${res}</p>
            `;
            container.appendChild(card);
        });
    }

    // 3. Kanoon Results
    if (data.kanoon_results && data.kanoon_results.length > 0) {
        const kanoonHeader = document.createElement("div");
        kanoonHeader.className = "section-header";
        kanoonHeader.innerText = "> EXTERNAL_PRECEDENTS (INDIAN KANOON)";
        container.appendChild(kanoonHeader);

        data.kanoon_results.forEach(doc => {
            const card = document.createElement("div");
            card.className = "card";
            card.innerHTML = `
                <span class="card-tag tag-kanoon">CASE_FILE</span>
                <h3 class="card-title"><a href="https://indiankanoon.org/doc/${doc.tid}/" target="_blank">${doc.title}</a></h3>
                <p class="card-snippet">${doc.headline || "No excerpt available."}</p>
            `;
            container.appendChild(card);
        });
    }

    // 4. Action Toolkit (NEW: Prescription)
    if (data.priority_actions && data.priority_actions.length > 0) {
        const toolkit = document.createElement("div");
        toolkit.className = "action-toolkit";
        toolkit.style.gridColumn = "1 / -1";

        // Priority Actions Widget
        let actionsHtml = `
            <div class="action-widget">
                <div class="widget-title">🚩 NEXT STEPS: PRIORITY ACTIONS</div>
                <div class="action-list">
        `;
        data.priority_actions.forEach(act => {
            const pClass = `p-${act.priority.toLowerCase()}`;
            actionsHtml += `
                <div class="priority-item ${pClass}">
                    <span class="priority-badge">${act.priority}</span>
                    <span>${act.text}</span>
                </div>
            `;
        });
        actionsHtml += `</div></div>`;

        // Evidence Checklist Widget
        let checklistHtml = `
            <div class="action-widget">
                <div class="widget-title">📂 EVIDENCE CHECKLIST</div>
                <div class="action-list">
        `;
        if (data.evidence_checklist) {
            data.evidence_checklist.forEach(item => {
                checklistHtml += `
                    <div class="checklist-item">
                        <span class="checkbox-custom"></span>
                        <span>${item}</span>
                    </div>
                `;
            });
        }
        checklistHtml += `</div></div>`;

        // Drafting Shortcut
        let shortcutHtml = "";
        if (data.recommended_template) {
            shortcutHtml = `
                <div class="shortcut-card">
                    <div class="shortcut-text">
                        <h3>Prepare your documents</h3>
                        <p>Based on your case, we recommend drafting a <b>${data.recommended_template.replace('_', ' ')}</b> immediately.</p>
                    </div>
                    <button class="btn-white" onclick="goToDraft('${data.recommended_template}')">START DRAFTING</button>
                </div>
            `;
        }

        toolkit.innerHTML = actionsHtml + checklistHtml + shortcutHtml;
        container.appendChild(toolkit);
    }

    // 5. Helplines
    if (data.helplines && data.helplines.length > 0) {
        const hHeader = document.createElement("div");
        hHeader.className = "section-header";
        hHeader.innerText = "> RELEVANT_HELPLINES";
        container.appendChild(hHeader);

        data.helplines.forEach(h => {
            const card = document.createElement("div");
            card.className = "card";
            card.innerHTML = `<h3>${h.name}</h3><p class="phone">${h.number}</p>`;
            container.appendChild(card);
        });
    }

    if (!data.summary && (!data.local_results || data.local_results.length === 0) && (!data.kanoon_results || data.kanoon_results.length === 0)) {
        container.innerHTML = `<div class="empty-state"><p>> NO_RESULTS_FOUND</p></div>`;
    } else {
        // 6. Enrichment: Empowerment Toolkit
        renderEmpowermentToolkit(data, container);
    }
}

function goToDraft(templateId) {
    navigate('drafting');
    document.getElementById('templateSelect').value = templateId;
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Document Drafting
async function generateDraft() {
    const templateId = document.getElementById('templateSelect').value;
    const name = document.getElementById('userName').value || "NAME";
    const details = document.getElementById('caseDetails').value || "DETAILS";

    const draftOutput = document.getElementById('draft-output-container');
    const draftText = document.getElementById('draft-text');

    draftOutput.style.display = 'block';
    draftText.innerText = "Generating draft...";

    try {
        const response = await fetch(`http://127.0.0.1:8000/draft/${templateId}?name=${encodeURIComponent(name)}&details=${encodeURIComponent(details)}`);
        const data = await response.json();

        // Show with typing effect or just set
        draftText.innerText = data.content;
        draftOutput.scrollIntoView({ behavior: 'smooth' });

    } catch (err) {
        draftText.innerText = "❌ Error generating draft.";
        console.error(err);
    }
}

function copyDraft() {
    const text = document.getElementById('draft-text').innerText;
    navigator.clipboard.writeText(text).then(() => {
        alert("Draft copied to clipboard!");
    });
}

// Tab Switching Logic
function showTab(tabName) {
    document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));

    document.getElementById(`tab-${tabName}`).classList.add('active');
    event.target.classList.add('active');
}

// Helper to send analysis request
async function sendAnalysisRequest(formData) {
    const resultsDiv = document.getElementById("results");
    const loadingDiv = document.getElementById("loading");

    // Add Language
    const lang = currentLanguage;
    formData.append("lang", lang);

    resultsDiv.innerHTML = "";
    loadingDiv.style.display = "block";

    try {
        const response = await fetch("http://127.0.0.1:8000/analyze", {
            method: "POST",
            body: formData
        });

        const data = await response.json();
        loadingDiv.style.display = "none";

        if (data.error) {
            resultsDiv.innerHTML = `<p style="color: red;">Error: ${data.error}</p>`;
            return;
        }

        renderAnalysis(data, resultsDiv);

    } catch (err) {
        loadingDiv.style.display = "none";
        resultsDiv.innerHTML = "❌ Error analyzing input.";
        console.error(err);
    }
}

async function uploadCaseFile() {
    const fileInput = document.getElementById("fileInput");
    const file = fileInput.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);
    await sendAnalysisRequest(formData);
}

async function analyzeUrl() {
    const url = document.getElementById("urlInput").value;
    if (!url) return;

    const formData = new FormData();
    formData.append("url", url);
    await sendAnalysisRequest(formData);
}

async function analyzeText() {
    const text = document.getElementById("textInput").value;
    if (!text) return;

    const formData = new FormData();
    formData.append("text_input", text);
    await sendAnalysisRequest(formData);
}

function renderAnalysis(data, container) {
    let html = `
        <div class="card" style="grid-column: 1 / -1; border-color: var(--accent);">
            <h2 style="color: var(--primary); margin-bottom: 1rem;">⚖️ Case Analysis Report</h2>
            
            <h3 style="margin-top: 1rem;">📌 Immediate Advice</h3>
            <ul style="margin-left: 1.5rem; margin-bottom: 1rem;">
                ${data.analysis.advice_steps.map(step => `<li>${step}</li>`).join("")}
            </ul>

            ${data.analysis.rights && data.analysis.rights.length > 0 ? `
                <h3 style="color: var(--accent);">🚨 Your Rights</h3>
                <ul class="rights-list" style="margin-bottom: 1rem;">
                    ${data.analysis.rights.map(r => `<li>${r}</li>`).join("")}
                </ul>
            ` : ""}

            ${data.analysis.roadmap && data.analysis.roadmap.length > 0 ? `
                <h3 style="color: var(--accent);">🗺️ Suggested Roadmap</h3>
                <div class="roadmap-container" style="margin-bottom: 1.5rem;">
                    ${data.analysis.roadmap.map((step, idx) => `
                        <div class="roadmap-step">
                            <div class="step-num">${idx + 1}</div>
                            <div>${step}</div>
                        </div>
                    `).join("")}
                </div>
            ` : ""}

            <h3>📂 Documents to Arrange</h3>
            <ul style="margin-left: 1.5rem; margin-bottom: 2rem;">
                ${data.analysis.documents_to_arrange.map(doc => `<li>${doc}</li>`).join("")}
            </ul>

            <div class="shortcut-card" style="margin-bottom: 2rem;">
                 <div class="shortcut-text">
                    <h3>Technical Action</h3>
                    <p>Proceed with the suggested legal strategy or draft your document base.</p>
                </div>
                <button class="btn-white" onclick="goToDraft('${data.analysis.recommended_template || 'police_complaint'}')">START DRAFTING</button>
            </div>

            <h3>🆔 Key Entities Detected</h3>
            <p>
                ${Object.entries(data.analysis.entities).map(([label, names]) =>
        `<b>${label}:</b> ${names.join(", ")}`
    ).join(" | ")}
            </p>
        </div>
    `;

    container.innerHTML = html;

    // Enrich with Empowerment Suite
    renderEmpowermentToolkit(data.analysis, container);

    // Add Precedents Header
    const precHeader = document.createElement("div");
    precHeader.className = "section-header";
    precHeader.innerText = "Similar Legal Precedents";
    container.appendChild(precHeader);

    // Add Local Precedents
    if (data.similar_precedents) {
        data.similar_precedents.forEach(p => {
            const card = document.createElement("div");
            card.className = "card";
            card.innerHTML = `<span class="card-tag tag-local">Reference</span><p>${p}</p>`;
            container.appendChild(card);
        });
    }

    // Add Kanoon Precedents
    if (data.kanoon_precedents) {
        data.kanoon_precedents.forEach(doc => {
            const card = document.createElement("div");
            card.className = "card";
            card.innerHTML = `
                <span class="card-tag tag-kanoon">Case Law</span>
                <h3 class="card-title"><a href="https://indiankanoon.org/doc/${doc.tid}/" target="_blank">${doc.title}</a></h3>
                <p class="card-snippet">${doc.headline || "No excerpt."}</p>
            `;
            container.appendChild(card);
        });
    }
}
function startGuidedInterview() {
    const modal = document.createElement("div");
    modal.className = "modal-overlay";
    modal.id = "guided-modal";

    const content = document.createElement("div");
    content.className = "modal-content";

    modal.appendChild(content);
    document.body.appendChild(modal);

    showInterviewStep(1);
}

const interviewData = {
    1: {
        question: "What area of law does your issue relate to?",
        choices: [
            { text: "Police / Crime / FIR", next: 2, query: "criminal FIR police" },
            { text: "Shopping / Services / Fraud", next: 2, query: "consumer fraud refund" },
            { text: "RTI / Government Info", next: 2, query: "RTI official information" },
            { text: "Marriage / Divorce / Family", next: 2, query: "divorce marriage custody" }
        ]
    },
    2: {
        question: "Is this an urgent situation?",
        choices: [
            { text: "Yes, immediate action needed", next: 'finish', query_plus: "urgent immediate action" },
            { text: "No, seeking information", next: 'finish', query_plus: "information guidance" }
        ]
    }
};

let currentSelection = "";

function showInterviewStep(stepId) {
    const container = document.querySelector("#guided-modal .modal-content");
    const step = interviewData[stepId];

    if (stepId === 'finish') {
        document.getElementById('query').value = currentSelection;
        closeInterview();
        searchLegal();
        return;
    }

    container.innerHTML = `
    < h2 style = "color: var(--primary); margin-bottom: 1rem;" > Defend U Guide</h2 >
        <p style="color: var(--text-secondary);">${step.question}</p>
        <div class="choice-grid">
            ${step.choices.map((c, i) => `
                <button class="choice-btn" onclick="handleInterviewChoice(${stepId}, ${i})">${c.text}</button>
            `).join("")}
        </div>
        <button onclick="closeInterview()" style="margin-top: 2rem; background: none; border: none; color: var(--text-secondary); cursor: pointer; text-decoration: underline;">Cancel</button>
`;
}

function handleInterviewChoice(stepId, choiceIdx) {
    const choice = interviewData[stepId].choices[choiceIdx];
    if (stepId === 1) {
        currentSelection = choice.query;
    } else {
        currentSelection += " " + (choice.query_plus || "");
    }

    showInterviewStep(choice.next);
}

function closeInterview() {
    const modal = document.getElementById("guided-modal");
    if (modal) modal.remove();
}

function toggleEmergencyMode() {
    const existing = document.getElementById('emergency-overlay');
    if (existing) {
        existing.remove();
        return;
    }

    const overlay = document.createElement('div');
    overlay.id = 'emergency-overlay';
    overlay.className = 'modal-overlay';
    overlay.style.zIndex = "2000";

    overlay.innerHTML = `
    < div class="modal-content" style = "border: 4px solid #e74c3c;" >
            <h1 style="color: #e74c3c; margin-bottom: 1rem;">🆘 EMERGENCY LEGAL PROTECTION</h1>
            <p style="font-weight: 700; margin-bottom: 2rem;">Stay calm. Here are your immediate Constitutional Protections:</p>
            
            <div class="emergency-tips" style="text-align: left; margin-bottom: 2rem;">
                <div class="card" style="margin-bottom: 10px; border-left: 5px solid #e74c3c;">
                    <b>Right to Silence:</b> You do not have to answer any questions without a lawyer.
                </div>
                <div class="card" style="margin-bottom: 10px; border-left: 5px solid #e74c3c;">
                    <b>Grounds of Arrest:</b> You must be informed WHY you are being held immediately.
                </div>
                <div class="card" style="margin-bottom: 10px; border-left: 5px solid #e74c3c;">
                    <b>Informing Kin:</b> You have a right to inform one friend or relative of your arrest.
                </div>
            </div>

            <button onclick="this.closest('#emergency-overlay').remove()" class="action-btn" style="background: #e74c3c;">I UNDERSTAND</button>
        </div >
    `;
    document.body.appendChild(overlay);
}

function renderEmpowermentToolkit(data, container) {
    if (!data.evidence_checklist && !data.roadmap && !data.emergency_tips) return;

    const toolkit = document.createElement("div");
    toolkit.className = "empowerment-container";

    // 1. Emergency Panel (If urgent)
    if (data.emergency_tips && data.emergency_tips.length > 0) {
        const emergency = document.createElement("div");
        emergency.className = "emergency-panel";
        emergency.innerHTML = `
    < div class="emergency-icon" >📢</div >
        <div class="emergency-content">
            <h3>FIRST RESPONSE: DO'S & DON'TS</h3>
            <div class="emergency-tips">
                ${data.emergency_tips.map(tip => `<span class="tip-tag">${tip}</span>`).join("")}
            </div>
        </div>
`;
        container.insertBefore(emergency, container.firstChild);
    }

    // 2. Legal Action Checklist
    if (data.priority_actions && data.priority_actions.length > 0) {
        const checklist = document.createElement("div");
        checklist.className = "action-checklist";
        checklist.innerHTML = `
            <h3>Legal Action Checklist</h3>
            <p style="font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 1rem;">Actionable steps for your situation:</p>
            <div class="action-list">
                ${data.priority_actions.map((action, idx) => `
                    <div class="checklist-item">
                        <input type="checkbox" id="action-${idx}" class="action-check">
                        <label for="action-${idx}" class="action-label">
                            <span class="priority-badge ${action.priority.toLowerCase()}">${action.priority}</span>
                            ${action.text}
                        </label>
                    </div>
                `).join("")}
            </div>
        `;
        toolkit.appendChild(checklist);
    }

    // 3. Readiness Widget
    if (data.evidence_checklist && data.evidence_checklist.length > 0) {
        const readiness = document.createElement("div");
        readiness.className = "readiness-widget";
        readiness.innerHTML = `
    < div class="score-header" >
                <h3>Evidence Readiness</h3>
                <div class="score-meter" id="meter-container">
                    <div class="score-circle" id="score-circle" data-score="0" style="--p: 0"></div>
                </div>
            </div >
            <p style="font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 1rem;">Check the evidence you have to see your case strength:</p>
            <div class="action-list">
                ${data.evidence_checklist.map((item, idx) => `
                    <div class="checklist-item">
                        <input type="checkbox" class="readiness-check" onchange="updateReadinessScore()">
                        <span>${item}</span>
                    </div>
                `).join("")}
            </div>
`;
        toolkit.appendChild(readiness);
    }

    // 3. Legal Compass (Timeline)
    if (data.roadmap && data.roadmap.length > 0) {
        const compass = document.createElement("div");
        compass.className = "compass-widget";
        compass.innerHTML = `
            <h3>Legal Compass</h3>
            <p style="font-size: 0.85rem; color: var(--text-secondary);">Your journey from incident to justice:</p>
            <div class="timeline-visual">
                ${data.roadmap.map((step, idx) => `
                    <div class="timeline-dot ${idx === 0 ? 'active' : ''}" title="${step}">
                        <div class="dot-label">${step.split(' ')[0]}</div>
                    </div>
                `).join("")}
            </div>
        `;
        toolkit.appendChild(compass);
    }

    container.appendChild(toolkit);

    // 4. Legal Aid Finder
    if (data.legal_aid_url) {
        const aid = document.createElement("div");
        aid.className = "aid-finder";
        aid.innerHTML = `
            <div class="aid-text">
                <h3>Eligible for Free Legal Aid?</h3>
                <p>Under Article 39A, you may be entitled to a free government lawyer.</p>
            </div>
            <a href="${data.legal_aid_url}" target="_blank" class="aid-link">FIND LEGAL AID</a>
        `;
        container.appendChild(aid);
    }
}

function updateReadinessScore() {
    const checks = document.querySelectorAll('.readiness-check');
    const checked = Array.from(checks).filter(c => c.checked).length;
    const score = checks.length > 0 ? Math.round((checked / checks.length) * 100) : 0;

    const circle = document.getElementById('score-circle');
    if (circle) {
        circle.style.setProperty('--p', score);
        circle.setAttribute('data-score', score);

        // Color feedback
        if (score < 40) circle.style.background = `conic - gradient(#e74c3c calc(${score} * 1 %), #eee 0)`;
        else if (score < 80) circle.style.background = `conic - gradient(#f1c40f calc(${score} * 1 %), #eee 0)`;
        else circle.style.background = `conic - gradient(#2ecc71 calc(${score} * 1 %), #eee 0)`;
    }
}

let currentLanguage = 'en';

function toggleDropdown() {
    const options = document.getElementById('dropdownOptions');
    options.classList.toggle('show');
}

function selectLanguage(code, icon, name) {
    currentLanguage = code;
    document.getElementById('currentLangIcon').innerText = icon;
    document.getElementById('currentLangName').innerText = name;
    document.getElementById('dropdownOptions').classList.remove('show');

    const query = document.getElementById('searchInput').value;
    if (query) {
        searchLegal();
    }
}

// Close dropdown when clicking outside
window.addEventListener('click', function (e) {
    const selector = document.getElementById('languageSelector');
    const options = document.getElementById('dropdownOptions');
    if (selector && !selector.contains(e.target)) {
        options.classList.remove('show');
    }
});
