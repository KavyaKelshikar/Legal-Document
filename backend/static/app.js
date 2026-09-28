/**
 * LexiCore - Deterministic Legal NLP Suite
 * Unified Frontend Application Controller
 */

// Application State
const state = {
  currentTab: 'dashboard',
  activeDocumentId: null,
  activeDocument: null,
  documents: [],
  selectedClauseIndex: 0
};

// ==========================================
// Authentication & User Session Helpers
// ==========================================
function getCurrentUser() {
  try {
    const raw = localStorage.getItem('lexicore_current_user');
    if (raw) return JSON.parse(raw);
  } catch (e) {
    console.error('Error parsing user session:', e);
  }
  return null;
}

function getCurrentUserEmail() {
  const user = getCurrentUser();
  return user && user.email ? user.email.trim().toLowerCase() : null;
}

function initUserProfile() {
  const user = getCurrentUser();
  if (user) {
    const nameEl = document.getElementById('user-display-name');
    const roleEl = document.getElementById('user-display-role');
    if (nameEl) nameEl.textContent = user.name || 'Legal Counsel';
    if (roleEl) roleEl.textContent = user.email || 'Enterprise User';
  } else {
    // If running in development without auth session, set demo session
    const demoUser = { name: 'Marcus Vance', email: 'admin@lexicore.ai' };
    localStorage.setItem('lexicore_current_user', JSON.stringify(demoUser));
    const nameEl = document.getElementById('user-display-name');
    const roleEl = document.getElementById('user-display-role');
    if (nameEl) nameEl.textContent = demoUser.name;
    if (roleEl) roleEl.textContent = demoUser.email;
  }
}

function logoutUser() {
  localStorage.removeItem('lexicore_current_user');
  window.location.href = '/';
}

// ==========================================
// Initialization
// ==========================================
document.addEventListener('DOMContentLoaded', () => {
  initUserProfile();
  initNavigation();
  initUploadHandlers();
  initSearchHandlers();
  initAssistantHandlers();
  initPillsAndShortcuts();

  // Load existing documents vault and dashboard
  loadDocumentsVault().then(() => {
    loadDashboardData();
  });
});

// ==========================================
// Navigation & Tab Switching
// ==========================================
function initNavigation() {
  const navLinks = document.querySelectorAll('aside nav a[data-path]');
  navLinks.forEach(link => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      const path = link.getAttribute('data-path');
      if (path === 'reports') {
        exportCurrentReport();
      } else if (path === 'settings') {
        showToast('LexiCore Legal Intelligence Suite: Enterprise NLP & Risk Engine', 'info');
      } else {
        switchTab(path);
      }
    });
  });

  // Top bar search button
  const topSearchBtn = document.getElementById('top-search-btn');
  if (topSearchBtn) {
    topSearchBtn.addEventListener('click', () => switchTab('search'));
  }

  // Top bar upload button
  const topUploadBtn = document.getElementById('top-upload-btn');
  const globalInput = document.getElementById('global-pdf-input');
  if (topUploadBtn && globalInput) {
    topUploadBtn.addEventListener('click', () => globalInput.click());
  }

  // Full Analysis link in header of search/assistant
  document.querySelectorAll('a[data-path="analysis"]').forEach(el => {
    el.addEventListener('click', (e) => {
      e.preventDefault();
      switchTab('analysis');
    });
  });
}

function switchTab(tabName) {
  state.currentTab = tabName;

  // Hide all tab views
  const views = document.querySelectorAll('.tab-view');
  views.forEach(view => view.classList.add('hidden'));

  // Show active tab view
  const targetView = document.getElementById(`view-${tabName}`);
  if (targetView) {
    targetView.classList.remove('hidden');
  }

  // Update sidebar active classes
  const navLinks = document.querySelectorAll('aside nav a[data-path]');
  navLinks.forEach(link => {
    const path = link.getAttribute('data-path');
    if (path === tabName) {
      link.classList.remove('text-on-surface-variant', 'hover:bg-surface-container-high', 'hover:text-on-surface');
      link.classList.add('bg-surface-container', 'text-primary', 'font-title-sm');
    } else {
      link.classList.remove('bg-surface-container', 'text-primary');
      link.classList.add('text-on-surface-variant', 'hover:bg-surface-container-high', 'hover:text-on-surface');
    }
  });

  // Contextual refreshes
  if (tabName === 'dashboard') {
    loadDashboardData();
  } else if (tabName === 'documents') {
    loadDocumentsVault();
  } else if (tabName === 'analysis') {
    if (state.activeDocumentId) {
      refreshAnalysisView(state.activeDocumentId);
    }
  } else if (tabName === 'search' || tabName === 'ai-assistant') {
    updateActiveDocumentLabels();
  }
}

// ==========================================
// Document Management & Uploads
// ==========================================
function triggerUpload() {
  const input = document.getElementById('global-pdf-input');
  if (input) {
    input.value = '';
    input.click();
  } else {
    showToast('File selector not found in document.', 'error');
  }
}

function handleFileSelect(input) {
  if (input && input.files && input.files[0]) {
    uploadPdfFile(input.files[0]);
  }
}

function initUploadHandlers() {
  // Global file input
  const globalInput = document.getElementById('global-pdf-input');
  if (globalInput) {
    globalInput.addEventListener('change', (e) => {
      if (e.target.files && e.target.files[0]) {
        uploadPdfFile(e.target.files[0]);
      }
    });
  }

  // Top upload button
  const topUploadBtn = document.getElementById('top-upload-btn');
  if (topUploadBtn) {
    topUploadBtn.addEventListener('click', (e) => {
      e.preventDefault();
      triggerUpload();
    });
  }

  // Dropzone in Documents view
  const dropzone = document.getElementById('dropzone');
  if (dropzone) {
    ['dragenter', 'dragover'].forEach(name => {
      dropzone.addEventListener(name, (e) => {
        e.preventDefault();
        dropzone.classList.add('bg-surface-container-high', 'border-primary');
      });
    });

    ['dragleave', 'drop'].forEach(name => {
      dropzone.addEventListener(name, (e) => {
        e.preventDefault();
        dropzone.classList.remove('bg-surface-container-high', 'border-primary');
      });
    });

    dropzone.addEventListener('drop', (e) => {
      e.preventDefault();
      if (e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files[0]) {
        uploadPdfFile(e.dataTransfer.files[0]);
      }
    });

    dropzone.addEventListener('click', (e) => {
      triggerUpload();
    });
  }

  // Catch all upload buttons
  document.querySelectorAll('button').forEach(btn => {
    const text = btn.textContent.trim();
    if (text.includes('Upload your first legal document') || text.includes('Upload PDF') || text === 'Upload') {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        triggerUpload();
      });
    }
  });

  // Global window drag and drop support
  window.addEventListener('dragover', (e) => e.preventDefault());
  window.addEventListener('drop', (e) => {
    e.preventDefault();
    if (e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files[0] && e.dataTransfer.files[0].name.toLowerCase().endsWith('.pdf')) {
      uploadPdfFile(e.dataTransfer.files[0]);
    }
  });
}

async function uploadPdfFile(file) {
  if (!file.name.toLowerCase().endsWith('.pdf')) {
    showToast('Only PDF documents are supported for deterministic analysis.', 'error');
    return;
  }

  const modal = document.getElementById('upload-modal');
  const filenameEl = document.getElementById('upload-filename');
  const percentEl = document.getElementById('upload-progress-percent');
  const progressBar = document.getElementById('upload-progress-bar');

  if (filenameEl) filenameEl.textContent = file.name;
  if (modal) modal.classList.remove('hidden');

  const setProgress = (pct, activeStepId) => {
    if (percentEl) percentEl.textContent = `${pct}%`;
    if (progressBar) progressBar.style.width = `${pct}%`;
    const stepIds = ['step-ingress', 'step-segment', 'step-classify', 'step-fuzzy', 'step-summary'];
    stepIds.forEach(id => {
      const el = document.getElementById(id);
      if (!el) return;
      const icon = el.querySelector('.material-symbols-outlined');
      if (id === activeStepId) {
        el.className = 'flex items-center gap-2 text-primary font-semibold';
        if (icon) {
          icon.textContent = 'hourglass_top';
          icon.className = 'material-symbols-outlined text-[16px] text-primary animate-pulse';
        }
      } else if (stepIds.indexOf(id) < stepIds.indexOf(activeStepId)) {
        el.className = 'flex items-center gap-2 text-tertiary';
        if (icon) {
          icon.textContent = 'check_circle';
          icon.className = 'material-symbols-outlined text-[16px] text-tertiary';
        }
      } else {
        el.className = 'flex items-center gap-2 text-outline/60';
        if (icon) {
          icon.textContent = 'radio_button_unchecked';
          icon.className = 'material-symbols-outlined text-[16px] text-outline/40';
        }
      }
    });
  };

  // Start visual step progression
  setProgress(20, 'step-ingress');
  const timer1 = setTimeout(() => setProgress(40, 'step-segment'), 300);
  const timer2 = setTimeout(() => setProgress(65, 'step-classify'), 700);
  const timer3 = setTimeout(() => setProgress(85, 'step-fuzzy'), 1100);

  const userEmail = getCurrentUserEmail();
  const formData = new FormData();
  formData.append('file', file);
  if (userEmail) {
    formData.append('user_email', userEmail);
  }

  const reqHeaders = {};
  if (userEmail) {
    reqHeaders['X-User-Email'] = userEmail;
  }

  try {
    const response = await fetch('/api/v1/analyze', {
      method: 'POST',
      headers: reqHeaders,
      body: formData
    });

    clearTimeout(timer1);
    clearTimeout(timer2);
    clearTimeout(timer3);

    if (!response.ok) {
      const err = await response.json();
      throw new Error(err.detail || 'Analysis pipeline failed');
    }

    const data = await response.json();
    setProgress(100, 'step-summary');

    state.activeDocumentId = data.document_id;
    state.activeDocument = data;

    const riskLevel = data.document_risk ? data.document_risk.overall_level : 'ANALYZED';

    // Delay 400ms so user sees the 100% completion checkmark
    setTimeout(async () => {
      if (modal) modal.classList.add('hidden');
      showToast(`Analysis completed for ${data.filename}! Risk: ${riskLevel}`, 'success');

      updateActiveDocumentLabels();
      await loadDocumentsVault();
      await refreshAnalysisView(data.document_id, data);
      switchTab('analysis');
    }, 450);

  } catch (err) {
    clearTimeout(timer1);
    clearTimeout(timer2);
    clearTimeout(timer3);
    if (modal) modal.classList.add('hidden');
    console.error('Upload error:', err);
    showToast(`Upload failed: ${err.message}`, 'error');
  }
}

async function loadDocumentsVault() {
  try {
    const userEmail = getCurrentUserEmail();
    const url = userEmail ? `/api/v1/documents?user_email=${encodeURIComponent(userEmail)}` : '/api/v1/documents';
    const res = await fetch(url);
    if (!res.ok) return;
    const docs = await res.json();
    state.documents = docs;

    // Update counter
    const countEl = document.getElementById('docs-total-count');
    if (countEl) countEl.textContent = docs.length;

    // If no active document, set the first one, or reset if no docs
    if (docs.length > 0) {
      if (!state.activeDocumentId || !docs.some(d => d.document_id === state.activeDocumentId)) {
        selectDocument(docs[0].document_id);
      }
    } else {
      state.activeDocumentId = null;
      state.activeDocument = null;
      updateActiveDocumentLabels();
    }

    renderDocumentsTable(docs);
    updateTopDocSelector(docs);
    loadDashboardData();
  } catch (err) {
    console.error('Failed to load documents vault:', err);
  }
}

function renderDocumentsTable(docs) {
  const tbody = document.getElementById('docs-vault-tbody');
  if (!tbody) return;

  if (docs.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="6" class="py-space-xl text-center text-on-surface-variant font-body-md">
          No documents uploaded yet. Use the upload area above to analyze your first PDF.
        </td>
      </tr>
    `;
    return;
  }

  tbody.innerHTML = docs.map(doc => {
    const isSelected = doc.document_id === state.activeDocumentId;
    const risk = (doc.overall_level || 'MODERATE').toUpperCase();
    let riskBadgeColor = 'bg-surface-container-high text-on-surface-variant';
    let riskIcon = 'check_circle';
    let scoreColor = 'text-primary';

    if (risk.includes('HIGH') || risk.includes('CRITICAL')) {
      riskBadgeColor = 'bg-error-container/30 text-error';
      riskIcon = 'gavel';
      scoreColor = 'text-error';
    } else if (risk.includes('MEDIUM') || risk.includes('MODERATE')) {
      riskBadgeColor = 'bg-amber-500/20 text-amber-300';
      riskIcon = 'warning';
      scoreColor = 'text-amber-300';
    } else {
      riskBadgeColor = 'bg-tertiary-container/30 text-tertiary';
      riskIcon = 'verified';
      scoreColor = 'text-tertiary';
    }

    const dateStr = doc.upload_timestamp ? new Date(doc.upload_timestamp).toLocaleDateString() : 'Today';

    return `
      <tr class="${isSelected ? 'bg-surface-container-high border-l-4 border-primary' : 'bg-surface-container'} hover:bg-surface-container-high transition-colors group cursor-pointer" onclick="selectDocument('${doc.document_id}')">
        <td class="py-space-md px-space-md">
          <div class="flex items-center gap-space-sm min-w-0">
            <div class="w-10 h-10 rounded-lg ${riskBadgeColor} flex items-center justify-center shrink-0">
              <span class="material-symbols-outlined text-[20px]">${riskIcon}</span>
            </div>
            <div class="flex flex-col min-w-0">
              <span class="font-title-sm text-title-sm text-on-surface font-semibold truncate group-hover:text-primary transition-colors">${escapeHtml(doc.filename)}</span>
              <span class="font-code-sm text-code-sm text-outline truncate">${doc.document_id.substring(0, 16)}...</span>
            </div>
          </div>
        </td>
        <td class="py-space-md px-space-md font-code-sm text-code-sm text-on-surface-variant">${dateStr}</td>
        <td class="py-space-md px-space-md">
          <span class="px-space-xs py-space-2xs bg-surface-container-lowest rounded text-on-surface-variant font-code-sm text-code-sm">${doc.total_clauses || 0} Clauses</span>
        </td>
        <td class="py-space-md px-space-md">
          <div class="flex items-center gap-space-xs">
            <span class="font-code-sm text-code-sm ${scoreColor} font-bold">${Math.round(doc.overall_score || 0)}/100</span>
            <span class="px-space-xs py-space-2xs rounded ${riskBadgeColor} font-label-sm text-label-sm uppercase font-semibold">${risk}</span>
          </div>
        </td>
        <td class="py-space-md px-space-md">
          <span class="inline-flex items-center gap-1.5 px-space-xs py-space-2xs rounded bg-surface-container-lowest font-code-sm text-code-sm text-tertiary">
            <span class="w-1.5 h-1.5 rounded-full bg-tertiary"></span> Indexed
          </span>
        </td>
        <td class="py-space-md px-space-md text-right" onclick="event.stopPropagation()">
          <div class="flex items-center justify-end gap-space-xs">
            <button class="px-3 py-1.5 rounded bg-surface-container-high hover:bg-primary hover:text-on-primary text-on-surface font-title-sm text-title-sm transition-all" onclick="selectDocument('${doc.document_id}'); switchTab('analysis');">
              Analyze
            </button>
            <button class="p-1.5 rounded hover:bg-surface-container-highest text-on-surface-variant hover:text-primary transition-colors" title="Search Clauses" onclick="selectDocument('${doc.document_id}'); switchTab('search');">
              <span class="material-symbols-outlined text-[18px]">manage_search</span>
            </button>
            <button class="p-1.5 rounded hover:bg-surface-container-highest text-on-surface-variant hover:text-primary transition-colors" title="Export PDF Report" onclick="window.open('/api/v1/documents/${doc.document_id}/report', '_blank')">
              <span class="material-symbols-outlined text-[18px]">picture_as_pdf</span>
            </button>
          </div>
        </td>
      </tr>
    `;
  }).join('');
}

async function selectDocument(docId) {
  state.activeDocumentId = docId;
  try {
    const res = await fetch(`/api/v1/documents/${docId}`);
    if (res.ok) {
      state.activeDocument = await res.json();
    }
  } catch (err) {
    console.error('Error fetching document details:', err);
  }

  updateActiveDocumentLabels();
  if (state.activeDocument) {
    renderAnalysisData(state.activeDocument);
  }
}

function updateActiveDocumentLabels() {
  const filename = state.activeDocument ? state.activeDocument.filename : 'No Document Selected';
  let risk = 'Ready';
  if (state.activeDocument && state.activeDocument.document_risk) {
    risk = state.activeDocument.document_risk.overall_level || 'ANALYZED';
  }

  // Top bar
  const topTitle = document.getElementById('top-doc-title');
  if (topTitle) topTitle.textContent = filename;

  const topRisk = document.getElementById('top-doc-risk');
  if (topRisk) {
    topRisk.textContent = risk;
    if (risk.toUpperCase().includes('HIGH') || risk.toUpperCase().includes('CRITICAL')) {
      topRisk.className = 'px-space-xs py-space-2xs rounded bg-error-container text-error font-label-sm text-label-sm font-semibold';
    } else if (risk.toUpperCase().includes('MEDIUM') || risk.toUpperCase().includes('MODERATE')) {
      topRisk.className = 'px-space-xs py-space-2xs rounded bg-amber-500/20 text-amber-300 font-label-sm text-label-sm font-semibold';
    } else {
      topRisk.className = 'px-space-xs py-space-2xs rounded bg-tertiary-container/30 text-tertiary font-label-sm text-label-sm font-semibold';
    }
  }

  // Analysis view title
  const analysisTitle = document.getElementById('analysis-doc-title');
  if (analysisTitle) analysisTitle.textContent = filename;

  // Search target
  const searchTarget = document.getElementById('search-doc-target');
  if (searchTarget) searchTarget.textContent = filename;

  // Assistant target
  const assistantTarget = document.getElementById('assistant-doc-target');
  if (assistantTarget) assistantTarget.textContent = filename;
}

// ==========================================
// Dashboard Population & Real Metrics
// ==========================================
async function loadDashboardData() {
  const userEmail = getCurrentUserEmail();
  const docs = state.documents || [];

  // Fetch system-wide analytics for this user
  let analyticsData = null;
  try {
    const url = userEmail ? `/api/v1/analytics?user_email=${encodeURIComponent(userEmail)}` : '/api/v1/analytics';
    const res = await fetch(url);
    if (res.ok) {
      analyticsData = await res.json();
    }
  } catch (e) {
    console.warn('Analytics fetch error:', e);
  }

  const totalDocs = docs.length;
  const totalClauses = docs.reduce((acc, d) => acc + (d.total_clauses || 0), 0);
  const highRiskDocs = docs.filter(d => (d.overall_level || '').toUpperCase() === 'HIGH').length;
  const medRiskDocs = docs.filter(d => (d.overall_level || '').toUpperCase() === 'MEDIUM' || (d.overall_level || '').toUpperCase() === 'MODERATE').length;
  const lowRiskDocs = docs.filter(d => (d.overall_level || '').toUpperCase() === 'LOW').length;

  const avgRiskScore = totalDocs > 0
    ? Math.round(docs.reduce((acc, d) => acc + (d.overall_score || 0), 0) / totalDocs)
    : 0;

  // 1. KPI Cards
  const totalDocsEl = document.getElementById('dash-total-docs');
  if (totalDocsEl) totalDocsEl.textContent = totalDocs;

  const docsSubtext = document.getElementById('dash-docs-subtext');
  if (docsSubtext) {
    docsSubtext.textContent = totalDocs === 0 ? 'No documents in repository' : `${totalDocs} active in repository`;
  }

  const totalClausesEl = document.getElementById('dash-total-clauses');
  if (totalClausesEl) totalClausesEl.textContent = totalClauses;

  const highRiskEl = document.getElementById('dash-high-risk-docs');
  if (highRiskEl) highRiskEl.textContent = highRiskDocs;

  const riskTagEl = document.getElementById('dash-risk-tag');
  if (riskTagEl) {
    if (highRiskDocs > 0) {
      riskTagEl.textContent = 'Action Req.';
      riskTagEl.className = 'px-space-xs py-space-2xs rounded bg-error-container text-error font-label-sm text-label-sm uppercase font-semibold tracking-wide';
    } else {
      riskTagEl.textContent = 'Optimal';
      riskTagEl.className = 'px-space-xs py-space-2xs rounded bg-surface-container text-tertiary font-label-sm text-label-sm uppercase font-semibold tracking-wide';
    }
  }

  const avgRiskEl = document.getElementById('dash-avg-risk');
  if (avgRiskEl) avgRiskEl.textContent = avgRiskScore;

  // 2. Donut & Risk Distribution
  const donutCount = document.getElementById('dash-donut-count');
  if (donutCount) donutCount.textContent = totalDocs;

  const lowPct = totalDocs > 0 ? (lowRiskDocs / totalDocs) * 100 : 0;
  const medPct = totalDocs > 0 ? (medRiskDocs / totalDocs) * 100 : 0;
  const highPct = totalDocs > 0 ? (highRiskDocs / totalDocs) * 100 : 0;

  const barLow = document.getElementById('dash-bar-low');
  if (barLow) barLow.style.width = `${lowPct}%`;
  const barMed = document.getElementById('dash-bar-med');
  if (barMed) barMed.style.width = `${medPct}%`;
  const barHigh = document.getElementById('dash-bar-high');
  if (barHigh) barHigh.style.width = `${highPct}%`;

  const countLow = document.getElementById('dash-count-low');
  if (countLow) countLow.textContent = lowRiskDocs;
  const shareLow = document.getElementById('dash-share-low');
  if (shareLow) shareLow.textContent = `${lowPct.toFixed(1)}% share`;

  const countMed = document.getElementById('dash-count-med');
  if (countMed) countMed.textContent = medRiskDocs;
  const shareMed = document.getElementById('dash-share-med');
  if (shareMed) shareMed.textContent = `${medPct.toFixed(1)}% share`;

  const countHigh = document.getElementById('dash-count-high');
  if (countHigh) countHigh.textContent = highRiskDocs;
  const shareHigh = document.getElementById('dash-share-high');
  if (shareHigh) shareHigh.textContent = `${highPct.toFixed(1)}% share`;

  // SVG Circles
  const circ = 301.59;
  const circleLow = document.getElementById('dash-circle-low');
  const circleMed = document.getElementById('dash-circle-med');
  const circleHigh = document.getElementById('dash-circle-high');

  if (circleLow && circleMed && circleHigh) {
    if (totalDocs === 0) {
      circleLow.style.strokeDashoffset = circ;
      circleMed.style.strokeDashoffset = circ;
      circleHigh.style.strokeDashoffset = circ;
    } else {
      const lowLen = circ * (lowPct / 100);
      const medLen = circ * (medPct / 100);
      const highLen = circ * (highPct / 100);

      circleLow.style.strokeDashoffset = circ - lowLen;
      circleMed.style.transform = `rotate(${((lowPct) / 100) * 360}deg)`;
      circleMed.style.transformOrigin = 'center';
      circleMed.style.strokeDashoffset = circ - medLen;

      circleHigh.style.transform = `rotate(${((lowPct + medPct) / 100) * 360}deg)`;
      circleHigh.style.transformOrigin = 'center';
      circleHigh.style.strokeDashoffset = circ - highLen;
    }
  }

  // 3. Recent Documents Table in Dashboard
  const dashTbody = document.getElementById('dash-recent-docs-tbody');
  if (dashTbody) {
    if (docs.length === 0) {
      dashTbody.innerHTML = `
        <tr>
          <td colspan="5" class="py-space-xl text-center text-on-surface-variant font-body-md">
            <div class="flex flex-col items-center justify-center gap-2 py-8">
              <div class="w-12 h-12 rounded-xl bg-surface-container flex items-center justify-center text-outline">
                <span class="material-symbols-outlined text-[28px]">folder_open</span>
              </div>
              <span class="text-on-surface font-title-sm">No contracts uploaded in your workspace yet</span>
              <span class="text-xs text-on-surface-variant max-w-sm">Upload a legal contract (PDF) to begin AI clause segmentation, risk evaluation, and search.</span>
              <button type="button" onclick="triggerUpload()" class="mt-3 px-4 py-2 bg-primary text-on-primary text-xs font-semibold rounded-lg hover:bg-primary-container transition-colors shadow flex items-center gap-1.5 cursor-pointer">
                <span class="material-symbols-outlined text-[16px]">upload_file</span>
                <span>Upload Your First Contract</span>
              </button>
            </div>
          </td>
        </tr>
      `;
    } else {
      dashTbody.innerHTML = docs.slice(0, 5).map(doc => {
        const risk = (doc.overall_level || 'MODERATE').toUpperCase();
        let riskBadgeColor = 'bg-surface-container text-on-surface-variant';
        let iconBg = 'bg-surface-container text-secondary';

        if (risk.includes('HIGH') || risk.includes('CRITICAL')) {
          riskBadgeColor = 'bg-error-container text-error font-semibold';
          iconBg = 'bg-error-container text-error';
        } else if (risk.includes('MEDIUM') || risk.includes('MODERATE')) {
          riskBadgeColor = 'bg-surface-container text-secondary font-semibold';
          iconBg = 'bg-surface-container text-secondary';
        } else {
          riskBadgeColor = 'bg-surface-container text-tertiary font-semibold';
          iconBg = 'bg-surface-container text-tertiary';
        }

        const dateStr = doc.upload_timestamp ? new Date(doc.upload_timestamp).toLocaleDateString() : 'Today';

        return `
          <tr class="hover:bg-surface-container/60 transition-colors group cursor-pointer" onclick="selectDocument('${doc.document_id}'); switchTab('analysis');">
            <td class="py-space-md px-space-lg">
              <div class="flex items-center gap-space-sm min-w-0">
                <div class="p-space-xs rounded ${iconBg} shrink-0">
                  <span class="material-symbols-outlined text-[18px]">description</span>
                </div>
                <div class="flex flex-col min-w-0">
                  <span class="font-title-sm text-title-sm text-on-surface truncate group-hover:text-primary transition-colors">${escapeHtml(doc.filename)}</span>
                  <span class="font-code-sm text-code-sm text-on-surface-variant truncate">ID: ${doc.document_id.substring(0, 14)}...</span>
                </div>
              </div>
            </td>
            <td class="py-space-md px-space-md text-on-surface-variant font-code-sm text-code-sm whitespace-nowrap">
              ${dateStr}
            </td>
            <td class="py-space-md px-space-md text-on-surface font-code-sm text-code-sm whitespace-nowrap">
              <div class="flex items-center gap-space-xs">
                <span>${doc.total_clauses || 0} Clauses</span>
                <span class="w-1.5 h-1.5 rounded-full bg-primary"></span>
              </div>
            </td>
            <td class="py-space-md px-space-md whitespace-nowrap">
              <div class="inline-flex items-center gap-space-xs px-space-sm py-space-2xs rounded ${riskBadgeColor} font-code-sm text-code-sm">
                <span>${risk} (${Math.round(doc.overall_score || 0)}/100)</span>
              </div>
            </td>
            <td class="py-space-md px-space-lg text-right whitespace-nowrap" onclick="event.stopPropagation()">
              <button onclick="selectDocument('${doc.document_id}'); switchTab('analysis');" class="inline-flex items-center gap-space-xs px-space-sm py-space-xs bg-surface-container hover:bg-surface-container-high text-primary hover:text-on-surface rounded-lg transition-colors font-title-sm text-title-sm cursor-pointer" type="button">
                <span>View Analysis</span>
                <span class="material-symbols-outlined text-[16px]">arrow_forward</span>
              </button>
            </td>
          </tr>
        `;
      }).join('');
    }
  }

  // 4. Clause Categories on Dashboard
  const catList = document.getElementById('dash-clause-categories-list');
  if (catList) {
    let catCounts = {};
    if (analyticsData && analyticsData.category_distribution && Object.keys(analyticsData.category_distribution).length > 0) {
      catCounts = analyticsData.category_distribution;
    }

    const entries = Object.entries(catCounts);
    if (entries.length === 0) {
      catList.innerHTML = `
        <div class="text-on-surface-variant text-body-sm font-body-sm py-6 text-center">
          No clauses analyzed yet. Upload a PDF contract to view AI taxonomy classification.
        </div>
      `;
    } else {
      const totalCatClauses = entries.reduce((acc, [, val]) => acc + val, 0) || 1;
      const sorted = entries.sort((a, b) => b[1] - a[1]);
      const palette = ['bg-primary-container', 'bg-primary', 'bg-secondary', 'bg-tertiary-container', 'bg-error', 'bg-outline'];

      catList.innerHTML = sorted.slice(0, 5).map(([cat, count], idx) => {
        const pct = ((count / totalCatClauses) * 100).toFixed(1);
        const color = palette[idx % palette.length];
        return `
          <div class="flex flex-col space-y-space-xs">
            <div class="flex justify-between items-center text-body-sm font-body-sm">
              <span class="text-on-surface font-title-sm text-title-sm">${escapeHtml(cat)}</span>
              <span class="font-code-sm text-code-sm text-on-surface-variant">${count} clauses (${pct}%)</span>
            </div>
            <div class="w-full h-2 rounded bg-surface-container overflow-hidden">
              <div class="${color} h-full rounded transition-all duration-300" style="width: ${pct}%"></div>
            </div>
          </div>
        `;
      }).join('');
    }
  }
}

// ==========================================
// Analysis Tab Population
// ==========================================
async function refreshAnalysisView(docId, preloadedData = null) {
  if (!docId) return;

  let docData = preloadedData;
  if (!docData) {
    try {
      const res = await fetch(`/api/v1/documents/${docId}`);
      if (res.ok) {
        docData = await res.json();
        state.activeDocument = docData;
      }
    } catch (e) {
      console.warn('Could not fetch single doc', e);
    }
  }

  if (docData) {
    renderAnalysisData(docData);
  }
}

function renderAnalysisData(docData) {
  const docRisk = docData.document_risk || {};
  const score = Math.round(docRisk.overall_score || 0);
  const risk = (docRisk.overall_level || 'LOW').toUpperCase();

  const scoreEl = document.getElementById('analysis-risk-score');
  if (scoreEl) scoreEl.textContent = score;

  const badgeEl = document.getElementById('analysis-risk-badge');
  if (badgeEl) badgeEl.textContent = `Risk: ${risk} (${score}/100)`;

  // Radial SVG progress circle
  const circle = document.getElementById('analysis-risk-gauge-circle');
  if (circle) {
    const circ = 301.6;
    const offset = circ - (circ * score / 100);
    circle.style.strokeDashoffset = offset;
    if (risk.includes('HIGH') || risk.includes('CRITICAL')) {
      circle.style.stroke = '#ffb4ab';
    } else if (risk.includes('MEDIUM') || risk.includes('MODERATE')) {
      circle.style.stroke = '#fcd34d';
    } else {
      circle.style.stroke = '#4edea3';
    }
  }

  // Render clauses preview
  const clauses = docData.clauses || [];
  if (clauses.length > 0) {
    renderClausesPreview(clauses);
    inspectClause(clauses[0], 0);
  }

  // Extractive Summary
  if (docData.summary) {
    renderExtractiveSummary(docData.summary);
  } else {
    fetch(`/api/v1/documents/${docData.document_id}/summary`)
      .then(r => r.json())
      .then(s => renderExtractiveSummary(s))
      .catch(e => console.error(e));
  }

  // Missing Clauses
  if (docData.missing_clauses) {
    renderMissingClauses(docData.missing_clauses);
  } else {
    fetch(`/api/v1/documents/${docData.document_id}/missing-clauses`)
      .then(r => r.json())
      .then(m => renderMissingClauses(m))
      .catch(e => console.error(e));
  }

  // PDF report export button
  const exportBtn = document.getElementById('analysis-export-report-btn');
  if (exportBtn) {
    exportBtn.onclick = () => {
      window.open(`/api/v1/documents/${docData.document_id}/report`, '_blank');
    };
  }
}

function renderClausesPreview(clauses) {
  const tbody = document.getElementById('analysis-clauses-tbody');
  if (!tbody) return;

  tbody.innerHTML = clauses.map((clause, idx) => {
    const risk = (clause.risk_level || 'LOW').toUpperCase();
    let badgeColor = 'bg-surface-container text-on-surface-variant';
    let riskTextColor = 'text-tertiary';

    if (risk === 'HIGH') {
      badgeColor = 'bg-error-container text-error';
      riskTextColor = 'text-error';
    } else if (risk === 'MEDIUM') {
      badgeColor = 'bg-amber-500/20 text-amber-300';
      riskTextColor = 'text-amber-300';
    } else {
      badgeColor = 'bg-tertiary-container/30 text-tertiary';
    }

    const rawText = clause.original_text || clause.text || '';
    const snippet = rawText.replace(/\s+/g, ' ').substring(0, 75) + '...';
    const category = clause.predicted_category || clause.category || 'General';
    const clauseIdText = `Clause ${(idx + 1).toString().padStart(2, '0')}`;

    return `
      <tr class="hover:bg-surface-bright transition-colors cursor-pointer" onclick="inspectClauseIndex(${idx})">
        <td class="py-space-sm px-space-md">
          <div class="flex items-center gap-space-xs">
            <span class="material-symbols-outlined text-[16px] ${riskTextColor}">gavel</span>
            <div>
              <span class="font-title-sm text-title-sm text-on-surface block">${clauseIdText}</span>
              <span class="text-on-surface-variant font-body-sm text-body-sm truncate block max-w-[210px]">${escapeHtml(snippet)}</span>
            </div>
          </div>
        </td>
        <td class="py-space-sm px-space-sm">
          <span class="px-space-xs py-space-2xs bg-surface-container rounded text-primary font-code-sm text-code-sm">
            ${escapeHtml(category)}
          </span>
        </td>
        <td class="py-space-sm px-space-sm text-right">
          <span class="font-code-sm text-code-sm ${riskTextColor} font-bold">${Math.round(clause.risk_score || 0)} / 100</span>
        </td>
        <td class="py-space-sm px-space-sm">
          <span class="px-space-xs py-space-2xs rounded ${badgeColor} font-label-sm text-label-sm font-semibold">
            ${risk}
          </span>
        </td>
        <td class="py-space-sm px-space-md text-right">
          <button class="px-space-xs py-space-2xs rounded hover:bg-surface-container-highest text-primary font-label-sm text-label-sm">
            Inspect
          </button>
        </td>
      </tr>
    `;
  }).join('');
}

window.inspectClauseIndex = function(idx) {
  if (state.activeDocument && state.activeDocument.clauses && state.activeDocument.clauses[idx]) {
    inspectClause(state.activeDocument.clauses[idx], idx);
  }
};

function inspectClause(clause, idx) {
  const container = document.getElementById('analysis-clause-detail-container');
  if (!container) return;

  const risk = (clause.risk_level || 'LOW').toUpperCase();
  const riskColor = risk === 'HIGH' ? 'text-error' : (risk === 'MEDIUM' ? 'text-amber-300' : 'text-tertiary');
  const badgeBg = risk === 'HIGH' ? 'bg-error-container text-error' : (risk === 'MEDIUM' ? 'bg-amber-500/20 text-amber-300' : 'bg-tertiary-container/30 text-tertiary');
  const conf = Math.round((clause.classification_confidence || clause.confidence || 0.85) * 100);
  const category = clause.predicted_category || clause.category || 'General';
  const text = clause.original_text || clause.text || '';

  container.innerHTML = `
    <div class="flex items-center justify-between pb-space-xs border-b border-surface-container-high">
      <div class="flex items-center gap-space-xs">
        <span class="px-space-xs py-space-2xs rounded ${badgeBg} font-code-sm text-code-sm font-bold">${risk} DETAIL</span>
        <span class="font-title-sm text-title-sm text-on-surface">Clause ${(idx + 1).toString().padStart(2, '0')} Inspection</span>
      </div>
      <span class="font-code-sm text-code-sm text-on-surface-variant">Page ${clause.page_number || 1}</span>
    </div>
    
    <div class="grid grid-cols-2 gap-space-xs p-space-xs bg-surface-container-low rounded-lg font-code-sm text-code-sm">
      <div class="p-space-xs bg-surface-container rounded">
        <span class="text-on-surface-variant block text-[10px] uppercase">AI Clause Classification</span>
        <span class="text-primary font-semibold">${escapeHtml(category)} (${conf}% conf)</span>
      </div>
      <div class="p-space-xs bg-surface-container rounded">
        <span class="text-on-surface-variant block text-[10px] uppercase">Fuzzy Risk Score</span>
        <span class="${riskColor} font-bold">${Math.round(clause.risk_score || 0)} / 100 [${risk}]</span>
      </div>
    </div>

    <div class="flex flex-col gap-space-2xs">
      <span class="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider">Extracted Clause Text</span>
      <div class="p-space-md bg-surface-container-low rounded-lg font-body-sm text-body-sm text-on-surface leading-relaxed max-h-60 overflow-y-auto border border-surface-container-high/40">
        ${escapeHtml(text || 'No text extracted for this clause.')}
      </div>
    </div>

    <div class="pt-space-xs flex items-center justify-between">
      <button class="px-space-md py-space-xs rounded bg-surface-container-high hover:bg-surface-bright text-on-surface font-title-sm text-title-sm transition-colors" onclick="copyClauseText('${escapeHtml(text)}')">
        Copy Clause
      </button>
      <button class="px-space-md py-space-xs rounded bg-primary text-on-primary font-title-sm text-title-sm hover:bg-primary-container transition-colors" onclick="queryThisClauseInSearch('${escapeHtml(category)}')">
        Search Similar
      </button>
    </div>
  `;
}

function renderExtractiveSummary(summary) {
  const container = document.getElementById('analysis-summary-container');
  if (!container) return;

  const cats = [
    { keys: ['duration'], label: '1. Duration & Term', icon: 'schedule' },
    { keys: ['payment_terms', 'payment'], label: '2. Payment Terms', icon: 'payments' },
    { keys: ['termination'], label: '3. Termination Protocol', icon: 'cancel' },
    { keys: ['confidentiality'], label: '4. Confidentiality & Non-Disclosure', icon: 'lock' },
    { keys: ['liability'], label: '5. Limitation of Liability & Indemnity', icon: 'gavel' }
  ];

  container.innerHTML = cats.map(c => {
    let content = null;
    for (const k of c.keys) {
      if (summary[k]) {
        content = summary[k];
        break;
      }
    }
    const textContent = content || 'No explicit provisions detected in this category.';
    return `
      <div class="p-space-sm bg-surface-container-low rounded-lg text-body-sm font-body-sm text-on-surface">
        <div class="flex items-center gap-space-2xs mb-space-2xs">
          <span class="material-symbols-outlined text-primary text-[16px]">${c.icon}</span>
          <strong class="text-primary font-semibold">${c.label}:</strong>
        </div>
        <p class="text-on-surface-variant pl-5 text-sm">${escapeHtml(textContent)}</p>
      </div>
    `;
  }).join('');
}

function renderMissingClauses(missingData) {
  const container = document.getElementById('analysis-missing-clauses-container');
  if (!container) return;

  const missingList = missingData.missing_clauses || [];
  if (missingList.length === 0) {
    container.innerHTML = `
      <div class="p-space-md bg-tertiary-container/10 border border-tertiary/20 rounded-lg flex items-center gap-space-sm">
        <span class="material-symbols-outlined text-tertiary text-[24px]">verified</span>
        <div>
          <span class="font-title-sm text-title-sm text-tertiary font-semibold block">All Essential Clauses Present</span>
          <p class="font-body-sm text-body-sm text-on-surface-variant">The analyzed document includes Payment, Confidentiality, Termination, and Liability provisions.</p>
        </div>
      </div>
    `;
    return;
  }

  container.innerHTML = missingList.map(item => {
    const sev = (item.severity || 'HIGH').toUpperCase();
    const sevColor = sev === 'HIGH' ? 'text-error' : 'text-amber-300';
    return `
      <div class="p-space-md bg-surface-container-low rounded-lg border border-surface-container-high/40">
        <div class="flex items-center justify-between mb-space-xs">
          <span class="font-title-sm text-title-sm ${sevColor} flex items-center gap-space-2xs">
            <span class="material-symbols-outlined text-[16px]">warning</span>
            Missing: ${escapeHtml(item.category)}
          </span>
          <span class="px-space-xs py-space-2xs bg-surface-container rounded text-on-surface-variant font-code-sm text-code-sm">${sev} SEVERITY</span>
        </div>
        <p class="font-body-sm text-body-sm text-on-surface-variant">${escapeHtml(item.recommendation || 'Standard commercial safeguards recommend including this clause.')}</p>
      </div>
    `;
  }).join('');
}

// ==========================================
// Dashboard Tab Population
// ==========================================
async function loadDashboardData() {
  try {
    const res = await fetch('/api/v1/analytics');
    if (!res.ok) return;
    const analytics = await res.json();

    const totalDocsEl = document.getElementById('dash-total-docs');
    if (totalDocsEl) totalDocsEl.textContent = analytics.total_documents || 0;

    const avgRiskEl = document.getElementById('dash-avg-risk');
    if (avgRiskEl) avgRiskEl.textContent = Math.round(analytics.average_risk_score || 0);

    const highRiskEl = document.getElementById('dash-high-risk-count');
    if (highRiskEl) highRiskEl.textContent = (analytics.risk_distribution && analytics.risk_distribution.HIGH) || 0;

    const lowRiskEl = document.getElementById('dash-low-risk-count');
    if (lowRiskEl) lowRiskEl.textContent = (analytics.risk_distribution && analytics.risk_distribution.LOW) || 0;

    // Recent documents table in dashboard
    const tbody = document.getElementById('dash-recent-docs-tbody');
    if (tbody && state.documents && state.documents.length > 0) {
      tbody.innerHTML = state.documents.slice(0, 5).map(doc => {
        const risk = (doc.overall_level || 'MODERATE').toUpperCase();
        const riskColor = risk === 'HIGH' ? 'text-error' : (risk === 'MEDIUM' ? 'text-amber-300' : 'text-tertiary');
        const badgeBg = risk === 'HIGH' ? 'bg-error-container text-error' : (risk === 'MEDIUM' ? 'bg-amber-500/20 text-amber-300' : 'bg-tertiary-container/30 text-tertiary');

        return `
          <tr class="hover:bg-surface-bright transition-colors cursor-pointer" onclick="selectDocument('${doc.document_id}'); switchTab('analysis');">
            <td class="py-space-sm px-space-md">
              <span class="font-title-sm text-title-sm text-on-surface block truncate max-w-[240px]">${escapeHtml(doc.filename)}</span>
            </td>
            <td class="py-space-sm px-space-md font-code-sm text-code-sm text-on-surface-variant">${doc.total_clauses || 0}</td>
            <td class="py-space-sm px-space-md font-code-sm text-code-sm ${riskColor} font-bold">${Math.round(doc.overall_score || 0)}/100</td>
            <td class="py-space-sm px-space-md">
              <span class="px-space-xs py-space-2xs rounded ${badgeBg} font-label-sm text-label-sm uppercase font-semibold">${risk}</span>
            </td>
            <td class="py-space-sm px-space-md text-right">
              <span class="material-symbols-outlined text-[18px] text-primary">arrow_forward</span>
            </td>
          </tr>
        `;
      }).join('');
    }
  } catch (err) {
    console.error('Failed to load dashboard analytics:', err);
  }
}

// ==========================================
// Semantic Search Tab Logic
// ==========================================
function initSearchHandlers() {
  const queryInput = document.getElementById('query-input');
  const searchBtn = document.getElementById('search-submit-btn');

  if (queryInput) {
    queryInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        executeSearch(queryInput.value);
      }
    });
  }

  if (searchBtn && queryInput) {
    searchBtn.addEventListener('click', () => {
      executeSearch(queryInput.value);
    });
  }
}

async function executeSearch(query) {
  if (!query || !query.trim()) return;
  if (!state.activeDocumentId) {
    showToast('Please upload or select a document in the Documents vault first.', 'error');
    switchTab('documents');
    return;
  }

  const resultsContainer = document.getElementById('search-results-container');
  if (resultsContainer) {
    resultsContainer.innerHTML = `
      <div class="py-space-xl text-center flex flex-col items-center justify-center gap-space-sm">
        <span class="w-6 h-6 rounded-full border-2 border-primary border-t-transparent animate-spin"></span>
        <span class="font-code-sm text-code-sm text-on-surface-variant">Searching semantic clause vector space...</span>
      </div>
    `;
  }

  try {
    const res = await fetch(`/api/v1/documents/${state.activeDocumentId}/search?question=${encodeURIComponent(query)}`);
    if (!res.ok) {
      throw new Error('Search failed');
    }
    const data = await res.json();
    renderSearchResults(data, query);
  } catch (err) {
    console.error('Search error:', err);
    if (resultsContainer) {
      resultsContainer.innerHTML = `
        <div class="p-space-lg bg-surface-container rounded-xl text-center text-error font-body-md">
          Search request failed: ${escapeHtml(err.message)}
        </div>
      `;
    }
  }
}

function renderSearchResults(data, query) {
  const container = document.getElementById('search-results-container');
  if (!container) return;

  if (!data.found) {
    container.innerHTML = `
      <div class="p-space-xl bg-surface-container rounded-xl text-center flex flex-col items-center gap-space-sm">
        <span class="material-symbols-outlined text-outline text-[36px]">search_off</span>
        <h4 class="font-title-md text-title-md text-on-surface">No Semantic Matches Found</h4>
        <p class="font-body-sm text-body-sm text-on-surface-variant max-w-md">No clauses in this document met the cosine similarity threshold (0.15) for &ldquo;${escapeHtml(query)}&rdquo;.</p>
      </div>
    `;
    return;
  }

  const simPct = Math.round((data.similarity_score || 0) * 100);
  const category = data.clause_category || 'General';

  container.innerHTML = `
    <article class="bg-surface-container-low rounded-xl p-space-md lg:p-space-lg flex flex-col gap-space-md shadow-md relative overflow-hidden">
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-space-sm">
        <div class="flex items-center gap-space-sm">
          <span class="px-space-xs py-space-2xs rounded bg-surface-container-high font-code-sm text-code-sm text-primary font-semibold">BEST MATCH</span>
          <span class="font-title-md text-title-md text-on-surface font-semibold">${escapeHtml(category)} Provision</span>
        </div>
        <div class="flex items-center gap-space-xs self-start sm:self-auto bg-surface-container px-space-sm py-space-xs rounded-full">
          <span class="w-2.5 h-2.5 rounded-full bg-tertiary"></span>
          <span class="font-code-sm text-code-sm font-semibold text-tertiary">Cosine Similarity: ${simPct}%</span>
        </div>
      </div>
      <div class="p-space-md bg-surface-container rounded-lg border-l-4 border-primary">
        <span class="font-label-sm text-label-sm text-primary uppercase block mb-1">Deterministic Extracted Answer:</span>
        <p class="font-title-sm text-title-sm text-on-surface font-semibold">${escapeHtml(data.answer)}</p>
      </div>
      <div class="flex flex-col gap-1">
        <span class="font-label-sm text-label-sm text-on-surface-variant uppercase">Full Source Clause:</span>
        <p class="font-body-sm text-body-sm text-on-surface-variant leading-relaxed">
          ${escapeHtml(data.source_clause || '')}
        </p>
      </div>
      <div class="flex items-center justify-between pt-space-xs border-t border-surface-container-high/40">
        <span class="font-code-sm text-code-sm text-outline">Category: ${escapeHtml(category)}</span>
        <button class="px-space-sm py-space-xs rounded bg-surface-container hover:bg-surface-container-high text-primary font-code-sm text-code-sm transition-colors cursor-pointer" onclick="copyClauseText('${escapeHtml(data.source_clause || '')}')">
          Copy Text
        </button>
      </div>
    </article>
  `;
}

// ==========================================
// AI Assistant Tab Logic
// ==========================================
function initAssistantHandlers() {
  const promptInput = document.getElementById('userPromptInput');
  const sendBtn = document.getElementById('assistant-send-btn');

  if (promptInput) {
    promptInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        submitAssistantMessage();
      }
    });
  }

  if (sendBtn) {
    sendBtn.addEventListener('click', () => submitAssistantMessage());
  }

  // Pre-seed chatStream with a friendly welcome message if empty
  const stream = document.getElementById('chatStream');
  if (stream && stream.children.length === 0) {
    appendBotBubble(
      "Hello! 👋 I am your **LexiCore AI Legal Assistant**.\n\n" +
      "I analyze legal contracts deterministically without using an LLM. You can say **\"Hi\"**, ask **\"What can you do?\"**, or ask questions about your active contract like:\n" +
      "• *\"What are the payment terms?\"*\n" +
      "• *\"When does this contract expire?\"*\n" +
      "• *\"What happens if I terminate early?\"*\n" +
      "• *\"Are there any missing clauses?\"*\n\n" +
      "Click any prompt pill or type below to begin!",
      null
    );
  }
}

async function submitAssistantMessage(presetQuery = null) {
  const input = document.getElementById('userPromptInput');
  const question = (presetQuery || (input ? input.value : '')).trim();
  if (!question) return;

  if (input) input.value = '';

  const stream = document.getElementById('chatStream');
  if (!stream) return;

  // Append user bubble
  const userBubble = document.createElement('div');
  userBubble.className = 'flex items-start justify-end gap-space-md';
  userBubble.innerHTML = `
    <div class="flex flex-col items-end gap-1.5 max-w-2xl">
      <div class="flex items-center gap-space-xs">
        <span class="font-label-sm text-label-sm text-outline">Just now</span>
        <span class="font-title-sm text-title-sm text-on-surface font-semibold">User</span>
      </div>
      <div class="bg-primary text-on-primary p-space-md rounded-xl font-body-md text-body-md shadow-md">
        <p class="font-medium">${escapeHtml(question)}</p>
      </div>
    </div>
    <div class="w-9 h-9 rounded-lg bg-surface-container-highest text-primary flex items-center justify-center flex-shrink-0 shadow-sm">
      <span class="material-symbols-outlined text-[20px]">person</span>
    </div>
  `;
  stream.appendChild(userBubble);
  userBubble.scrollIntoView({ behavior: 'smooth', block: 'end' });

  // Bot loading indicator
  const loadingBubble = document.createElement('div');
  loadingBubble.className = 'flex items-start gap-space-md';
  loadingBubble.innerHTML = `
    <div class="w-9 h-9 rounded-lg bg-primary-container text-on-primary-container flex items-center justify-center flex-shrink-0 shadow-md">
      <span class="material-symbols-outlined text-[20px]">smart_toy</span>
    </div>
    <div class="flex flex-col gap-space-sm max-w-3xl w-full">
      <div class="bg-surface-container p-space-md rounded-xl text-on-surface font-body-md text-body-md flex items-center gap-2">
        <span class="w-4 h-4 rounded-full border-2 border-primary border-t-transparent animate-spin"></span>
        <span class="font-code-sm text-code-sm text-on-surface-variant">Thinking & querying LexiCore Dialogflow Webhook...</span>
      </div>
    </div>
  `;
  stream.appendChild(loadingBubble);
  loadingBubble.scrollIntoView({ behavior: 'smooth', block: 'end' });

  try {
    const res = await fetch('/api/v1/dialogflow/webhook', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        question: question,
        document_id: state.activeDocumentId || undefined
      })
    });

    loadingBubble.remove();

    if (!res.ok) throw new Error('Webhook processing failed');
    const data = await res.json();
    const fulfillmentText = data.fulfillmentText || 'I processed your request.';
    const payload = data.payload || {};
    const retResult = payload.retrieval_result;

    let citation = null;
    if (retResult && retResult.found) {
      citation = {
        category: retResult.clause_category || 'General',
        page: 1,
        similarity: Math.round((retResult.similarity_score || 0) * 100),
        clause_id: retResult.clause_id
      };
    }

    appendBotBubble(fulfillmentText, citation);

  } catch (err) {
    loadingBubble.remove();
    console.error('Assistant error:', err);
    // Friendly fallback
    appendBotBubble(`Hello! I'm here to assist. For specific contract queries, please ensure a document is selected in the Documents Vault!`, null);
  }
}

function formatAssistantResponse(rawText) {
  let html = escapeHtml(rawText);
  // Bold **text**
  html = html.replace(/\*\*([^*]+)\*\*/g, '<strong class="text-primary font-semibold">$1</strong>');
  // Italic *text*
  html = html.replace(/\*([^*]+)\*/g, '<em class="text-on-surface">$1</em>');
  // Bullet points
  html = html.replace(/^• (.*)$/gm, '<li class="ml-4 list-disc text-on-surface-variant">$1</li>');
  html = html.replace(/^- (.*)$/gm, '<li class="ml-4 list-disc text-on-surface-variant">$1</li>');
  // Line breaks
  html = html.replace(/\n\n/g, '<div class="my-2"></div>');
  html = html.replace(/\n/g, '<br/>');
  return html;
}

function appendBotBubble(text, citation) {
  const stream = document.getElementById('chatStream');
  if (!stream) return;

  const botBubble = document.createElement('div');
  botBubble.className = 'flex items-start gap-space-md';

  let citationHtml = '';
  if (citation) {
    citationHtml = `
      <div class="p-space-sm bg-surface-container-lowest rounded-lg font-code-sm text-code-sm text-on-surface-variant flex items-center justify-between mt-2 border border-surface-container-high/40">
        <span class="flex items-center gap-1.5 text-primary">
          <span class="material-symbols-outlined text-[16px]">verified</span>
          ${escapeHtml(citation.category || 'General')} Provision (Clause #${citation.clause_id || 1})
        </span>
        <span class="text-tertiary font-semibold">Cosine ${citation.similarity}%</span>
      </div>
    `;
  }

  botBubble.innerHTML = `
    <div class="w-9 h-9 rounded-lg bg-primary-container text-on-primary-container flex items-center justify-center flex-shrink-0 shadow-md">
      <span class="material-symbols-outlined text-[20px]">smart_toy</span>
    </div>
    <div class="flex flex-col gap-space-sm max-w-3xl w-full">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-space-xs">
          <span class="font-title-sm text-title-sm text-on-surface font-semibold">LexiCore Dialogflow Engine</span>
          <span class="px-1.5 py-0.5 rounded bg-tertiary-container/30 text-tertiary font-code-sm text-code-sm">AI Assistant</span>
        </div>
        <span class="font-label-sm text-label-sm text-outline">Just now</span>
      </div>
      <div class="bg-surface-container p-space-md rounded-xl text-on-surface font-body-md text-body-md flex flex-col gap-space-sm shadow-sm">
        <div class="leading-relaxed">${formatAssistantResponse(text)}</div>
        ${citationHtml}
      </div>
    </div>
  `;

  stream.appendChild(botBubble);
  botBubble.scrollIntoView({ behavior: 'smooth', block: 'end' });
}

// ==========================================
// Helpers, Pills & Toast
// ==========================================
function initPillsAndShortcuts() {
  // Query pills in Search
  document.querySelectorAll('.query-pill').forEach(pill => {
    pill.addEventListener('click', () => {
      const input = document.getElementById('query-input');
      const text = pill.querySelector('span:last-child') ? pill.querySelector('span:last-child').textContent.trim() : pill.textContent.trim();
      if (input) {
        input.value = text;
        executeSearch(text);
      }
    });
  });

  // Prompt pills in Assistant
  document.querySelectorAll('button').forEach(btn => {
    const text = btn.textContent.trim();
    if (text.startsWith('When does this contract') || 
        text.startsWith('What happens if I terminate') || 
        text.startsWith('What is my notice period') || 
        text.startsWith('When do I need to make the payment') || 
        text.startsWith('What are my obligations') || 
        text.startsWith('Is there an uncapped liability')) {
      btn.addEventListener('click', () => {
        const input = document.getElementById('userPromptInput');
        if (input) {
          input.value = text;
          submitAssistantMessage();
        }
      });
    }
  });
}

function exportCurrentReport() {
  if (state.activeDocumentId) {
    window.open(`/api/v1/documents/${state.activeDocumentId}/report`, '_blank');
  } else {
    showToast('Please select or upload a document to generate its PDF report.', 'info');
    switchTab('documents');
  }
}

function copyClauseText(text) {
  navigator.clipboard.writeText(text).then(() => {
    showToast('Clause text copied to clipboard!', 'success');
  });
}

function queryThisClauseInSearch(category) {
  switchTab('search');
  const input = document.getElementById('query-input');
  if (input) {
    input.value = `What are the ${category} requirements and terms?`;
    executeSearch(input.value);
  }
}

function showToast(msg, type = 'info') {
  let toast = document.getElementById('lexi-toast');
  if (!toast) {
    toast = document.createElement('div');
    toast.id = 'lexi-toast';
    toast.className = 'fixed bottom-6 right-6 z-50 px-space-md py-space-sm rounded-xl font-body-sm text-body-sm shadow-2xl flex items-center gap-space-xs transition-all transform translate-y-12 opacity-0 pointer-events-none';
    document.body.appendChild(toast);
  }

  let bg = 'bg-surface-container-highest text-on-surface border border-surface-bright';
  let icon = 'info';

  if (type === 'success') {
    bg = 'bg-tertiary-container text-on-tertiary-container shadow-tertiary/20';
    icon = 'check_circle';
  } else if (type === 'error') {
    bg = 'bg-error-container text-on-error-container shadow-error/20';
    icon = 'error';
  }

  toast.className = `fixed bottom-6 right-6 z-50 px-space-md py-space-sm rounded-xl font-body-sm text-body-sm shadow-2xl flex items-center gap-space-xs transition-all transform translate-y-0 opacity-100 pointer-events-auto ${bg}`;
  toast.innerHTML = `<span class="material-symbols-outlined text-[18px]">${icon}</span><span>${escapeHtml(msg)}</span>`;

  clearTimeout(toast.timeout);
  toast.timeout = setTimeout(() => {
    toast.classList.add('translate-y-12', 'opacity-0', 'pointer-events-none');
    toast.classList.remove('translate-y-0', 'opacity-100', 'pointer-events-auto');
  }, 3500);
}

function escapeHtml(string) {
  const entityMap = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#39;',
    '/': '&#x2F;'
  };
  return String(string).replace(/[&<>"'\/]/g, s => entityMap[s]);
}

function initUserProfile() {
  try {
    const raw = localStorage.getItem('lexicore_current_user');
    if (raw) {
      const user = JSON.parse(raw);
      const nameEl = document.getElementById('user-display-name');
      const roleEl = document.getElementById('user-display-role');
      if (nameEl && user.name) nameEl.textContent = user.name;
      if (roleEl && user.email) roleEl.textContent = user.email;
    }
  } catch (e) {
    console.warn('Could not read user session:', e);
  }
}

function logoutUser() {
  localStorage.removeItem('lexicore_current_user');
  showToast('Signing out of LexiCore Workspace...', 'info');
  setTimeout(() => {
    window.location.href = '/';
  }, 350);
}

// ==========================================
// Top Document Selector Dropdown
// ==========================================
function updateTopDocSelector(docs) {
  const selector = document.getElementById('top-doc-selector');
  if (!selector) return;

  selector.innerHTML = '<option value="">Switch Contract...</option>';
  (docs || state.documents).forEach(doc => {
    const opt = document.createElement('option');
    opt.value = doc.document_id;
    opt.textContent = doc.filename;
    if (doc.document_id === state.activeDocumentId) opt.selected = true;
    selector.appendChild(opt);
  });
}

// ==========================================
// Sample Contract Quick Loader
// ==========================================
async function loadSampleContract(filename) {
  // Check if already loaded
  const existingDoc = state.documents.find(d => d.filename === filename);
  if (existingDoc) {
    await selectDocument(existingDoc.document_id);
    switchTab('analysis');
    showToast(`Switched to ${filename}`, 'success');
    return;
  }
  showToast(`Loading sample: ${filename}...`, 'info');
  try {
    const res = await fetch(`/sample_pdfs/${filename}`);
    if (!res.ok) throw new Error('Sample not found');
    const blob = await res.blob();
    const file = new File([blob], filename, { type: 'application/pdf' });
    await uploadPdfFile(file);
  } catch (err) {
    console.error('Failed to load sample:', err);
    showToast(`Could not load sample: ${err.message}`, 'error');
  }
}

// ==========================================
// Help / Guide Modal
// ==========================================
function openHelpModal() {
  const modal = document.getElementById('help-modal');
  if (modal) {
    modal.classList.remove('hidden');
    modal.style.opacity = '0';
    requestAnimationFrame(() => { modal.style.opacity = '1'; });
  }
}

function closeHelpModal() {
  const modal = document.getElementById('help-modal');
  if (modal) {
    modal.style.opacity = '0';
    setTimeout(() => modal.classList.add('hidden'), 150);
  }
}

// ==========================================
// Clause Filter Pills & Search (Analysis Tab)
// ==========================================
let allClausesCache = [];

function cacheAllClauses() {
  if (state.activeDocument && state.activeDocument.clauses) {
    allClausesCache = [...state.activeDocument.clauses];
  }
}

function filterClauses(category) {
  cacheAllClauses();
  if (!allClausesCache.length) return;

  // Highlight the active pill
  document.querySelectorAll('.clause-filter-pill').forEach(pill => {
    if (pill.getAttribute('data-category') === category) {
      pill.classList.add('bg-primary', 'text-on-primary');
      pill.classList.remove('bg-surface-container', 'text-on-surface-variant');
    } else {
      pill.classList.remove('bg-primary', 'text-on-primary');
      pill.classList.add('bg-surface-container', 'text-on-surface-variant');
    }
  });

  let filtered;
  if (category === 'All') {
    filtered = allClausesCache;
  } else if (category === 'High Risk Only') {
    filtered = allClausesCache.filter(c => (c.risk_level || '').toUpperCase() === 'HIGH');
  } else {
    filtered = allClausesCache.filter(c => {
      const cat = (c.predicted_category || c.category || '').toLowerCase();
      return cat.includes(category.toLowerCase());
    });
  }

  renderClausesPreview(filtered);
  if (filtered.length > 0) {
    inspectClause(filtered[0], 0);
  }
}

function searchClausesLocal(keyword) {
  cacheAllClauses();
  if (!keyword || !keyword.trim()) {
    renderClausesPreview(allClausesCache);
    return;
  }

  const kw = keyword.toLowerCase();
  const filtered = allClausesCache.filter(c => {
    const text = (c.original_text || c.text || '').toLowerCase();
    const cat = (c.predicted_category || c.category || '').toLowerCase();
    return text.includes(kw) || cat.includes(kw);
  });

  renderClausesPreview(filtered);
  if (filtered.length > 0) {
    inspectClause(filtered[0], 0);
  } else {
    showToast(`No clauses matching "${keyword}"`, 'info');
  }
}

// ==========================================
// Prompt pill quick submit (AI Assistant)
// ==========================================
function sendPromptPill(text) {
  const input = document.getElementById('userPromptInput');
  if (input) {
    input.value = text;
  }
  submitAssistantMessage(text);
}

// Global exposure for inline HTML event handlers
window.triggerUpload = triggerUpload;
window.handleFileSelect = handleFileSelect;
window.logoutUser = logoutUser;
window.openHelpModal = openHelpModal;
window.closeHelpModal = closeHelpModal;
window.loadSampleContract = loadSampleContract;
window.filterClauses = filterClauses;
window.searchClausesLocal = searchClausesLocal;
window.sendPromptPill = sendPromptPill;
window.updateTopDocSelector = updateTopDocSelector;
window.insertPrompt = function(text) {
  const input = document.getElementById('userPromptInput');
  if (input) {
    input.value = text;
    input.focus();
  }
};
window.simulateSubmit = submitAssistantMessage;
window.selectDocument = selectDocument;
window.switchTab = switchTab;
window.copyClauseText = copyClauseText;
window.queryThisClauseInSearch = queryThisClauseInSearch;
