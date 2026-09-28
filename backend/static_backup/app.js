// ── DOM Elements ──
const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');
const browseBtn = document.getElementById('browse-btn');
const fileInfo = document.getElementById('file-info');
const fileName = document.getElementById('file-name');
const clearBtn = document.getElementById('clear-btn');
const analyzeBtn = document.getElementById('analyze-btn');
const errorBanner = document.getElementById('error-banner');
const resultsSection = document.getElementById('results-section');

let selectedFile = null;

// ── File Selection ──
browseBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    fileInput.click();
});

dropZone.addEventListener('click', () => fileInput.click());

fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        selectFile(e.target.files[0]);
    }
});

clearBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    clearFile();
});

// ── Drag & Drop ──
dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('dragover');
});

dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('dragover');
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('dragover');
    if (e.dataTransfer.files.length > 0) {
        selectFile(e.dataTransfer.files[0]);
    }
});

function selectFile(file) {
    if (!file.name.toLowerCase().endsWith('.pdf')) {
        showError('Please select a PDF file.');
        return;
    }
    selectedFile = file;
    fileName.textContent = file.name;
    fileInfo.hidden = false;
    document.querySelector('.drop-zone-content').style.display = 'none';
    analyzeBtn.disabled = false;
    hideError();
}

function clearFile() {
    selectedFile = null;
    fileInput.value = '';
    fileInfo.hidden = true;
    document.querySelector('.drop-zone-content').style.display = '';
    analyzeBtn.disabled = true;
}

// ── Analysis ──
analyzeBtn.addEventListener('click', async () => {
    if (!selectedFile) return;

    const btnText = analyzeBtn.querySelector('.btn-text');
    const btnLoader = analyzeBtn.querySelector('.btn-loader');
    btnText.hidden = true;
    btnLoader.hidden = false;
    analyzeBtn.disabled = true;
    hideError();
    resultsSection.hidden = true;

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
        const response = await fetch('/api/v1/analyze', {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || `Server error: ${response.status}`);
        }

        const data = await response.json();
        renderResults(data);
    } catch (err) {
        showError(err.message);
    } finally {
        btnText.hidden = false;
        btnLoader.hidden = true;
        analyzeBtn.disabled = false;
    }
});

// ── Render Results ──
function renderResults(data) {
    // Summary stats
    document.getElementById('stat-filename').textContent = data.filename;
    document.getElementById('stat-pages').textContent = data.metadata?.page_count ?? '—';
    document.getElementById('stat-clauses').textContent = data.total_clauses;

    // Risk gauge
    const risk = data.document_risk;
    const gaugeCircle = document.getElementById('gauge-circle');
    const gaugeScore = document.getElementById('gauge-score');
    const riskBadge = document.getElementById('risk-badge');

    gaugeScore.textContent = risk.overall_score;
    const level = risk.overall_level.toLowerCase();
    gaugeCircle.className = 'gauge-circle ' + level;
    riskBadge.textContent = risk.overall_level;
    riskBadge.className = 'risk-badge ' + level;

    // Category breakdown
    const catContainer = document.getElementById('category-breakdown');
    catContainer.innerHTML = '';
    const catColors = {
        Payment: 'var(--cat-payment)',
        Confidentiality: 'var(--cat-confidentiality)',
        Termination: 'var(--cat-termination)',
        Liability: 'var(--cat-liability)',
        General: 'var(--cat-general)',
    };
    const maxCount = Math.max(...Object.values(risk.category_breakdown), 1);

    for (const [cat, count] of Object.entries(risk.category_breakdown)) {
        const pct = (count / maxCount) * 100;
        const color = catColors[cat] || 'var(--accent)';
        catContainer.innerHTML += `
            <div class="cat-row">
                <span class="cat-label">${cat}</span>
                <div class="cat-bar-bg">
                    <div class="cat-bar-fill" style="width: ${pct}%; background: ${color};"></div>
                </div>
                <span class="cat-count">${count}</span>
            </div>
        `;
    }

    // Clause list
    const clausesList = document.getElementById('clauses-list');
    clausesList.innerHTML = '';

    for (const c of data.clauses) {
        const riskLvl = c.risk_level.toLowerCase();
        const fi = c.fuzzy_inputs;

        const item = document.createElement('div');
        item.className = 'clause-item';
        item.innerHTML = `
            <div class="clause-header">
                <span class="clause-id">Clause ${c.clause_id}</span>
                <div class="clause-badges">
                    <span class="badge badge-category ${c.predicted_category}">${c.predicted_category} (${(c.classification_confidence * 100).toFixed(1)}%)</span>
                    <span class="badge badge-risk ${riskLvl}">Risk: ${c.risk_score} — ${c.risk_level}</span>
                </div>
            </div>
            <div class="clause-text">${escapeHtml(c.original_text)}</div>
            <div class="expand-hint">Click to ${'{'}expand fuzzy details{'}'}</div>
            <div class="fuzzy-details">
                <div class="fuzzy-grid">
                    <div class="fuzzy-metric">
                        <div class="fuzzy-metric-label">Importance</div>
                        <div class="fuzzy-metric-value">${fi.importance} / 10</div>
                    </div>
                    <div class="fuzzy-metric">
                        <div class="fuzzy-metric-label">Ambiguity</div>
                        <div class="fuzzy-metric-value">${fi.ambiguity} / 10</div>
                    </div>
                    <div class="fuzzy-metric">
                        <div class="fuzzy-metric-label">Risk Indicators</div>
                        <div class="fuzzy-metric-value">${fi.risk_indicators} / 10</div>
                    </div>
                    <div class="fuzzy-metric">
                        <div class="fuzzy-metric-label">Fuzzy Risk Score</div>
                        <div class="fuzzy-metric-value" style="color: var(--risk-${riskLvl})">${c.risk_score}</div>
                    </div>
                </div>
            </div>
        `;

        item.addEventListener('click', () => {
            item.classList.toggle('expanded');
            const hint = item.querySelector('.expand-hint');
            hint.textContent = item.classList.contains('expanded')
                ? 'Click to collapse'
                : 'Click to expand fuzzy details';
        });

        clausesList.appendChild(item);
    }

    resultsSection.hidden = false;
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// ── Helpers ──
function showError(msg) {
    errorBanner.textContent = msg;
    errorBanner.hidden = false;
}

function hideError() {
    errorBanner.hidden = true;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
