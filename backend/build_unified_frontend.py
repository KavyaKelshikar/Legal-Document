import os
import re

EXTRACT_DIR = os.path.join(os.path.dirname(__file__), "stitch_extracted")
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")

def read_screen(name):
    path = os.path.join(EXTRACT_DIR, name, "code.html")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def extract_main_content(html):
    m = re.search(r'<main[^>]*>([\s\S]*?)</main>', html)
    if m:
        return m.group(1).strip()
    return ""

def enhance_screen0(html):
    # Dashboard metrics
    html = re.sub(
        r'<span class="font-metric-display text-metric-display text-on-surface tracking-tight">\d+</span>',
        r'<span id="dash-avg-risk" class="font-metric-display text-metric-display text-on-surface tracking-tight">0</span>',
        html, count=1
    )
    html = re.sub(
        r'<span class="font-metric-display-sm text-metric-display-sm text-on-surface tracking-tight">7</span>',
        r'<span id="dash-total-docs" class="font-metric-display-sm text-metric-display-sm text-on-surface tracking-tight">0</span>',
        html, count=1
    )
    html = re.sub(
        r'<span class="font-metric-display-sm text-metric-display-sm text-error tracking-tight">4</span>',
        r'<span id="dash-high-risk-count" class="font-metric-display-sm text-metric-display-sm text-error tracking-tight">0</span>',
        html, count=1
    )
    html = re.sub(
        r'<span class="font-metric-display-sm text-metric-display-sm text-tertiary tracking-tight">3</span>',
        r'<span id="dash-low-risk-count" class="font-metric-display-sm text-metric-display-sm text-tertiary tracking-tight">0</span>',
        html, count=1
    )
    html = re.sub(
        r'(<tbody class="divide-y divide-surface-container-high/40 text-on-surface font-body-sm text-body-sm">)',
        r'<tbody id="dash-recent-docs-tbody" class="divide-y divide-surface-container-high/40 text-on-surface font-body-sm text-body-sm">',
        html, count=1
    )
    return html

def enhance_screen1(html):
    # Analysis
    html = re.sub(
        r'Document Analysis — High_Risk_Vendor_Contract\.pdf',
        r'Document Analysis — <span id="analysis-doc-title">Select or Upload a Document</span>',
        html
    )
    html = re.sub(
        r'<button class="flex items-center gap-space-xs px-space-md py-space-xs bg-primary[^>]*>[\s\S]*?Export PDF Report[\s\S]*?</button>',
        r'<button id="analysis-export-report-btn" class="flex items-center gap-space-xs px-space-md py-space-xs bg-primary text-on-primary font-title-sm text-title-sm rounded-lg hover:bg-primary-container transition-colors shadow-sm cursor-pointer" type="button"><span class="material-symbols-outlined text-[18px]">picture_as_pdf</span><span>Export PDF Report</span></button>',
        html
    )
    html = re.sub(
        r'<span class="font-metric-display-sm text-metric-display-sm text-on-surface tracking-tight">\d+</span>',
        r'<span id="analysis-risk-score" class="font-metric-display-sm text-metric-display-sm text-on-surface tracking-tight">0</span>',
        html, count=1
    )
    html = re.sub(
        r'Risk: CRITICAL \(\d+/100\)',
        r'<span id="analysis-risk-badge">Risk: PENDING</span>',
        html
    )
    html = re.sub(
        r'(stroke-dasharray="301\.6"\s+stroke-dashoffset="[\d\.]+")',
        r'id="analysis-risk-gauge-circle" stroke-dasharray="301.6" stroke-dashoffset="301.6"',
        html
    )
    # Add category filter bar above Clauses table
    filter_bar_html = """
    <div class="px-space-md py-space-xs bg-surface-container-low flex flex-wrap items-center justify-between gap-space-xs border-b border-surface-container-high/60">
      <div class="flex items-center gap-1.5 flex-wrap text-xs font-mono" id="clause-filter-pills">
        <button type="button" onclick="filterClauses('ALL')" class="clause-filter-btn px-2.5 py-1 rounded-md bg-surface-container-high text-primary font-semibold">All</button>
        <button type="button" onclick="filterClauses('Liability')" class="clause-filter-btn px-2.5 py-1 rounded-md bg-surface-container text-on-surface-variant hover:text-on-surface">Liability</button>
        <button type="button" onclick="filterClauses('Payment')" class="clause-filter-btn px-2.5 py-1 rounded-md bg-surface-container text-on-surface-variant hover:text-on-surface">Payment</button>
        <button type="button" onclick="filterClauses('Termination')" class="clause-filter-btn px-2.5 py-1 rounded-md bg-surface-container text-on-surface-variant hover:text-on-surface">Termination</button>
        <button type="button" onclick="filterClauses('Confidentiality')" class="clause-filter-btn px-2.5 py-1 rounded-md bg-surface-container text-on-surface-variant hover:text-on-surface">Confidentiality</button>
        <button type="button" onclick="filterClauses('HIGH_RISK')" class="clause-filter-btn px-2.5 py-1 rounded-md bg-error-container/20 text-error hover:bg-error-container/40">High Risk Only</button>
      </div>
      <div class="relative">
        <span class="material-symbols-outlined absolute left-2 top-1.5 text-[14px] text-outline">search</span>
        <input type="text" id="clause-search-box" oninput="searchClausesLocal(this.value)" placeholder="Filter clauses..." class="pl-6 pr-2 py-1 bg-surface-container text-xs text-on-surface rounded border border-surface-container-high focus:outline-none focus:border-primary w-36"/>
      </div>
    </div>
    """
    html = re.sub(
        r'(<div class="p-space-md flex items-center justify-between bg-surface-container-low">[\s\S]*?</div>)',
        r'\1' + filter_bar_html,
        html, count=1
    )

    html = re.sub(
        r'(<tbody class="divide-y divide-surface-container-high/40 font-body-sm text-body-sm">)',
        r'<tbody id="analysis-clauses-tbody" class="divide-y divide-surface-container-high/40 font-body-sm text-body-sm">',
        html, count=1
    )
    html = re.sub(
        r'(<div class="lg:col-span-5 bg-surface-container rounded-xl p-space-lg shadow-md flex flex-col gap-space-md">)',
        r'<div id="analysis-clause-detail-container" class="lg:col-span-5 bg-surface-container rounded-xl p-space-lg shadow-md flex flex-col gap-space-md">',
        html, count=1
    )
    html = re.sub(
        r'(<div class="space-y-space-sm">\s*<div class="p-space-sm bg-surface-container-low rounded-lg text-body-sm font-body-sm text-on-surface">\s*<strong class="text-primary font-semibold block mb-space-2xs">1\. Scope)',
        r'<div id="analysis-summary-container" class="space-y-space-sm">\n<div class="p-space-sm bg-surface-container-low rounded-lg text-body-sm font-body-sm text-on-surface">\n<strong class="text-primary font-semibold block mb-space-2xs">1. Scope',
        html, count=1
    )
    html = re.sub(
        r'(<div class="space-y-space-md">\s*<!-- Missing Item 1 -->)',
        r'<div id="analysis-missing-clauses-container" class="space-y-space-md">\n<!-- Missing Item 1 -->',
        html, count=1
    )
    return html

def enhance_screen2(html):
    # Documents
    # Add Quick Sample Contracts Banner
    samples_banner_html = """
    <div class="bg-surface-container-low p-space-md rounded-xl border border-surface-container-high flex flex-col sm:flex-row sm:items-center justify-between gap-space-sm shadow-sm">
      <div class="flex items-center gap-space-sm">
        <div class="w-10 h-10 rounded-lg bg-primary-container/20 text-primary flex items-center justify-center shrink-0">
          <span class="material-symbols-outlined text-[22px]">quickreference</span>
        </div>
        <div>
          <span class="font-title-sm text-title-sm text-on-surface font-semibold block">Quick Demo Contracts</span>
          <span class="font-body-sm text-body-sm text-on-surface-variant">Click to load and analyze a realistic legal contract instantly:</span>
        </div>
      </div>
      <div class="flex items-center gap-space-xs flex-wrap">
        <button type="button" onclick="loadSampleContract('High_Risk_Vendor_Contract.pdf')" class="px-3 py-1.5 rounded-lg bg-surface-container hover:bg-surface-bright text-xs font-semibold text-error border border-error/30 transition-all flex items-center gap-1 shadow-sm">
          <span class="material-symbols-outlined text-[14px]">gavel</span> High Risk Vendor
        </button>
        <button type="button" onclick="loadSampleContract('Standard_Consulting_Agreement.pdf')" class="px-3 py-1.5 rounded-lg bg-surface-container hover:bg-surface-bright text-xs font-semibold text-primary border border-primary/30 transition-all flex items-center gap-1 shadow-sm">
          <span class="material-symbols-outlined text-[14px]">description</span> Consulting Agmt
        </button>
        <button type="button" onclick="loadSampleContract('Simple_NDA.pdf')" class="px-3 py-1.5 rounded-lg bg-surface-container hover:bg-surface-bright text-xs font-semibold text-tertiary border border-tertiary/30 transition-all flex items-center gap-1 shadow-sm">
          <span class="material-symbols-outlined text-[14px]">lock</span> Simple NDA
        </button>
      </div>
    </div>
    """
    html = re.sub(
        r'(<div class="grid grid-cols-1 md:grid-cols-4 gap-space-md">)',
        samples_banner_html + r'\n\1',
        html, count=1
    )

    html = re.sub(
        r'(<tbody class="divide-y-0 text-on-surface font-body-md text-body-md">)',
        r'<tbody id="docs-vault-tbody" class="divide-y-0 text-on-surface font-body-md text-body-md">',
        html, count=1
    )
    html = re.sub(
        r'<span class="font-metric-display-sm text-metric-display-sm text-on-surface tracking-tight">14</span>',
        r'<span id="docs-total-count" class="font-metric-display-sm text-metric-display-sm text-on-surface tracking-tight">0</span>',
        html, count=1
    )
    # Make top "Upload PDF" button trigger upload
    html = re.sub(
        r'<button class="flex items-center gap-space-xs px-space-md py-space-xs bg-primary[^>]*>',
        r'<button onclick="triggerUpload()" class="flex items-center gap-space-xs px-space-md py-space-xs bg-primary text-on-primary font-title-sm text-title-sm rounded-lg hover:bg-primary-container hover:text-on-primary transition-all shadow-md cursor-pointer" type="button">',
        html
    )
    # Make dropzone clickable
    html = re.sub(
        r'id="dropzone"',
        r'id="dropzone" onclick="triggerUpload()"',
        html
    )
    # Make "Browse Files" an explicit button
    html = re.sub(
        r'<span class="text-primary underline decoration-primary/40 underline-offset-4">Browse Files</span>',
        r'<span class="text-primary underline decoration-primary/40 underline-offset-4 font-bold hover:text-white cursor-pointer" onclick="event.stopPropagation(); triggerUpload();">Browse Files</span>',
        html
    )
    # Make bottom button clickable
    html = re.sub(
        r'<button class="flex items-center gap-space-xs px-space-lg py-space-xs bg-primary[^>]*>',
        r'<button onclick="triggerUpload()" class="flex items-center gap-space-xs px-space-lg py-space-xs bg-primary text-on-primary font-title-sm text-title-sm rounded-lg hover:bg-primary-container transition-colors shadow-md cursor-pointer" type="button">',
        html
    )
    return html

def enhance_screen3(html):
    # Search
    html = re.sub(
        r'<span class="font-code-sm text-code-sm text-on-surface font-semibold truncate max-w-\[240px\]">High_Risk_Vendor_Contract\.pdf</span>',
        r'<span id="search-doc-target" class="font-code-sm text-code-sm text-on-surface font-semibold truncate max-w-[240px]">Select a Document</span>',
        html
    )
    html = re.sub(
        r'(<button class="[^"]*absolute right-2 top-2[^"]*"[^>]*>)',
        r'<button id="search-submit-btn" class="absolute right-2 top-2 h-10 px-space-md bg-primary text-on-primary font-title-sm text-title-sm rounded hover:bg-primary-container transition-colors flex items-center gap-space-xs shadow cursor-pointer" type="button">',
        html
    )
    html = re.sub(
        r'(<!-- RANK #1: HIGHEST COSINE SIMILARITY \(MASTER CARD\) -->\s*<article[\s\S]*?</article>(\s*<article[\s\S]*?</article>)+)',
        r'<div id="search-results-container" class="flex flex-col gap-space-md">\1</div>',
        html
    )
    return html

def enhance_screen4(html):
    # AI Assistant
    html = re.sub(
        r'<span class="font-code-sm text-code-sm text-on-surface font-semibold truncate max-w-\[220px\]">High_Risk_Vendor_Contract\.pdf</span>',
        r'<span id="assistant-doc-target" class="font-code-sm text-code-sm text-on-surface font-semibold truncate max-w-[220px]">Select a Document</span>',
        html
    )
    html = re.sub(
        r'(<button class="[^"]*bg-primary text-on-primary[^"]*"[^>]*onclick="simulateSubmit\(\)"[^>]*>)',
        r'<button id="assistant-send-btn" class="w-10 h-10 rounded-lg bg-primary text-on-primary flex items-center justify-center shrink-0 hover:bg-primary-container transition-colors shadow-md cursor-pointer" type="button">',
        html
    )
    return html

def main():
    s0 = read_screen("screen0_dashboard")
    s1 = read_screen("screen1_analysis")
    s2 = read_screen("screen2_documents")
    s3 = read_screen("screen3_search")
    s4 = read_screen("screen4_assistant")

    head_match = re.search(r'<head>([\s\S]*?)</head>', s0)
    head_content = head_match.group(1) if head_match else ""

    aside_match = re.search(r'(<aside[\s\S]*?</aside>)', s0)
    aside_html = aside_match.group(1) if aside_match else ""

    # Enhance aside with user profile and quick logout
    aside_html = re.sub(
        r'<span class="font-title-sm text-title-sm text-on-surface truncate">Marcus Vance</span>',
        r'<span id="user-display-name" class="font-title-sm text-title-sm text-on-surface truncate">Marcus Vance</span>',
        aside_html
    )
    aside_html = re.sub(
        r'<span class="font-label-sm text-label-sm text-on-surface-variant truncate">Legal Counsel / Lead</span>',
        r'<div class="flex items-center justify-between"><span id="user-display-role" class="font-label-sm text-label-sm text-on-surface-variant truncate">Legal Counsel</span><button type="button" onclick="logoutUser()" title="Sign Out" class="text-outline hover:text-error transition-colors ml-2"><span class="material-symbols-outlined text-[16px]">logout</span></button></div>',
        aside_html
    )

    header_match = re.search(r'(<header[\s\S]*?</header>)', s0)
    header_html = header_match.group(1) if header_match else ""

    # Enhance top header with document selector, guide button, and upload button
    header_html = re.sub(
        r'<span class="font-title-sm text-title-sm truncate">High_Risk_Vendor_Contract\.pdf</span>',
        r'<span id="top-doc-title" class="font-title-sm text-title-sm truncate">No Document Selected</span>',
        header_html
    )
    header_html = re.sub(
        r'<span class="px-space-xs py-space-2xs rounded bg-error-container text-error font-label-sm text-label-sm font-semibold">Analyzed</span>',
        r'<span id="top-doc-risk" class="px-space-xs py-space-2xs rounded bg-surface-container-high text-on-surface-variant font-label-sm text-label-sm font-semibold">Ready</span>',
        header_html
    )
    # Search button in top bar
    header_html = re.sub(
        r'<button class="flex items-center gap-space-sm[^>]*>',
        r'<button id="top-search-btn" onclick="switchTab(\'search\')" class="flex items-center gap-space-sm px-space-sm py-space-2xs bg-surface-container-low hover:bg-surface-container-high text-on-surface-variant hover:text-on-surface rounded-lg transition-colors cursor-pointer" type="button">',
        header_html
    )
    # Upload button in top bar + Guide button + Doc selector dropdown
    top_extra_controls = """
    <select id="top-doc-selector" onchange="if(this.value) selectDocument(this.value)" class="bg-surface-container-high border border-surface-highest text-on-surface text-xs rounded-lg px-2.5 py-1.5 focus:outline-none focus:border-primary cursor-pointer max-w-[210px] truncate" title="Switch active contract">
      <option value="">Switch Contract...</option>
    </select>
    <button type="button" onclick="openHelpModal()" class="flex items-center gap-1 px-2.5 py-1.5 rounded-lg bg-surface-container-low hover:bg-surface-container-high text-on-surface-variant hover:text-primary text-xs font-semibold transition-colors cursor-pointer border border-surface-container-high" title="Architecture Guide & Viva Walkthrough">
      <span class="material-symbols-outlined text-[16px] text-primary">help</span>
      <span>Guide</span>
    </button>
    """
    header_html = re.sub(
        r'(<div class="flex items-center gap-space-sm">\s*)',
        r'\1' + top_extra_controls,
        header_html, count=1
    )
    header_html = re.sub(
        r'<button class="flex items-center gap-space-2xs[^>]*>',
        r'<button id="top-upload-btn" onclick="triggerUpload()" class="flex items-center gap-space-2xs px-space-md py-space-xs bg-primary text-on-primary font-title-sm text-title-sm rounded-lg hover:bg-primary-container hover:text-on-primary transition-colors cursor-pointer shadow-md" type="button">',
        header_html
    )

    main0 = extract_main_content(enhance_screen0(s0))
    main1 = extract_main_content(enhance_screen1(s1))
    main2 = extract_main_content(enhance_screen2(s2))
    main3 = extract_main_content(enhance_screen3(s3))
    main4 = extract_main_content(enhance_screen4(s4))

    view0 = f'<div id="view-dashboard" class="tab-view">{main0}</div>'
    view1 = f'<div id="view-analysis" class="tab-view hidden">{main1}</div>'
    view2 = f'<div id="view-documents" class="tab-view hidden">{main2}</div>'
    view3 = f'<div id="view-search" class="tab-view hidden">{main3}</div>'
    view4 = f'<div id="view-ai-assistant" class="tab-view hidden">{main4}</div>'

    unified_html = f"""<!DOCTYPE html>
<html lang="en" class="dark">
<head>
{head_content}
<title>LexiCore - Deterministic Legal NLP Suite</title>
<style>
  .tab-view {{
    animation: fadeIn 0.2s cubic-bezier(0.16, 1, 0.3, 1);
  }}
  @keyframes fadeIn {{
    from {{ opacity: 0; transform: translateY(6px); }}
    to {{ opacity: 1; transform: translateY(0); }}
  }}
  .nav-active {{
    background-color: #122131 !important;
    color: #adc6ff !important;
    font-weight: 600 !important;
  }}
  .cursor-pointer {{
    cursor: pointer;
  }}
  #chatStream::-webkit-scrollbar, .overflow-x-auto::-webkit-scrollbar {{
    width: 6px;
    height: 6px;
    display: block;
  }}
  #chatStream::-webkit-scrollbar-thumb, .overflow-x-auto::-webkit-scrollbar-thumb {{
    background: #1c2b3c;
    border-radius: 4px;
  }}
  #chatStream::-webkit-scrollbar-thumb:hover, .overflow-x-auto::-webkit-scrollbar-thumb:hover {{
    background: #273647;
  }}
</style>
</head>
<body class="bg-surface text-on-surface min-h-screen selection:bg-primary/20 selection:text-primary">
{aside_html}
<div class="pl-64">
{header_html}
<main class="w-full pt-16 bg-surface min-h-screen">
{view0}
{view1}
{view2}
{view3}
{view4}
</main>
</div>

<!-- Global file input for PDF uploads -->
<input type="file" id="global-pdf-input" accept=".pdf" class="hidden" onchange="handleFileSelect(this)" />

<!-- Processing / Upload Modal with Pipeline Telemetry -->
<div id="upload-modal" class="fixed inset-0 z-50 bg-black/75 backdrop-blur-sm flex items-center justify-center p-4 hidden">
  <div class="bg-surface-container border border-surface-high rounded-2xl p-6 max-w-lg w-full shadow-2xl space-y-4">
    <div class="flex items-center justify-between pb-3 border-b border-surface-high">
      <div class="flex items-center gap-2.5">
        <div class="w-8 h-8 rounded-lg bg-primary-container text-on-primary-container flex items-center justify-center">
          <span class="material-symbols-outlined text-[20px] animate-spin">sync</span>
        </div>
        <div>
          <h3 class="font-title-sm text-on-surface font-semibold truncate max-w-[280px]" id="upload-filename">Ingesting Document.pdf</h3>
          <span class="text-xs text-primary font-mono">Deterministic Legal NLP Pipeline Active</span>
        </div>
      </div>
      <span id="upload-progress-percent" class="text-xs font-mono font-bold text-tertiary">20%</span>
    </div>

    <!-- Progress Bar -->
    <div class="w-full bg-surface-low rounded-full h-2 overflow-hidden">
      <div id="upload-progress-bar" class="bg-primary h-full transition-all duration-300" style="width: 20%;"></div>
    </div>

    <!-- Pipeline Steps Checklist -->
    <div class="space-y-2 text-xs font-mono py-1">
      <div id="step-ingress" class="flex items-center gap-2 text-primary font-semibold">
        <span class="material-symbols-outlined text-[16px] animate-pulse">hourglass_top</span>
        <span>1. Text Ingress & OCR Validation (PyMuPDF)</span>
      </div>
      <div id="step-segment" class="flex items-center gap-2 text-outline">
        <span class="material-symbols-outlined text-[16px]">radio_button_unchecked</span>
        <span>2. Deterministic Clause Segmentation (spaCy v3.7)</span>
      </div>
      <div id="step-classify" class="flex items-center gap-2 text-outline">
        <span class="material-symbols-outlined text-[16px]">radio_button_unchecked</span>
        <span>3. Clause Classification (Multinomial Naive Bayes)</span>
      </div>
      <div id="step-fuzzy" class="flex items-center gap-2 text-outline">
        <span class="material-symbols-outlined text-[16px]">radio_button_unchecked</span>
        <span>4. Risk Inference & Defuzzification (Mamdani Engine)</span>
      </div>
      <div id="step-summary" class="flex items-center gap-2 text-outline">
        <span class="material-symbols-outlined text-[16px]">radio_button_unchecked</span>
        <span>5. Extractive Summary & Missing Clause Audit</span>
      </div>
    </div>

    <p class="text-xs text-on-surface-variant font-mono text-center pt-2 border-t border-surface-high/60">
      Zero LLM interpolation &bull; 100% deterministic reproducibility
    </p>
  </div>
</div>

<!-- Architecture & Help Guide Modal -->
<div id="help-modal" class="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 hidden">
  <div class="bg-surface-container border border-surface-high rounded-2xl max-w-2xl w-full max-h-[85vh] flex flex-col shadow-2xl overflow-hidden">
    <div class="p- space-md p-5 flex items-center justify-between border-b border-surface-high bg-surface-low">
      <div class="flex items-center gap-2">
        <span class="material-symbols-outlined text-primary text-[22px]">menu_book</span>
        <h3 class="font-title-md text-on-surface font-semibold">LexiCore System Guide & Viva Walkthrough</h3>
      </div>
      <button type="button" onclick="closeHelpModal()" class="text-on-surface-variant hover:text-on-surface">
        <span class="material-symbols-outlined text-[20px]">close</span>
      </button>
    </div>
    <div class="p-6 overflow-y-auto space-y-5 text-sm font-body-md text-on-surface-variant leading-relaxed">
      <div>
        <h4 class="text-primary font-semibold text-base mb-1.5 flex items-center gap-1.5">
          <span class="material-symbols-outlined text-[18px]">verified</span> 1. What is LexiCore?
        </h4>
        <p>LexiCore is an <strong>AI Legal Document Assistant</strong> designed to analyze, classify, evaluate risk, and answer questions from legal contracts using <strong>deterministic algorithms</strong> without relying on expensive, hallucinatory Large Language Models (LLMs).</p>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 font-mono text-xs">
        <div class="p-3 rounded-xl bg-surface-low border border-surface-high/60">
          <strong class="text-primary block mb-1">Text Ingress & Segmentation:</strong>
          PyMuPDF parses PDF byte streams, spaCy v3.7 splits raw text into distinct contractual clauses using sentence boundaries and numbered headings.
        </div>
        <div class="p-3 rounded-xl bg-surface-low border border-surface-high/60">
          <strong class="text-primary block mb-1">Naive Bayes Classification:</strong>
          Multinomial Naive Bayes classifier predicts clause types: <em>Payment, Confidentiality, Termination, Liability, General</em> with ~75% test accuracy.
        </div>
        <div class="p-3 rounded-xl bg-surface-low border border-surface-high/60">
          <strong class="text-tertiary block mb-1">Mamdani Fuzzy Logic Risk:</strong>
          Computes Importance, Ambiguity, and Risk Indicators into triangular/trapezoidal membership functions to defuzzify into exact 0-100 risk scores.
        </div>
        <div class="p-3 rounded-xl bg-surface-low border border-surface-high/60">
          <strong class="text-tertiary block mb-1">TF-IDF Retrieval & Dialogflow:</strong>
          Transforms user questions into TF-IDF vector space, computes Cosine Similarity against clauses, and extracts the exact answer sentence.
        </div>
      </div>

      <div>
        <h4 class="text-primary font-semibold text-base mb-1.5 flex items-center gap-1.5">
          <span class="material-symbols-outlined text-[18px]">rule</span> 2. Risk Level Interpretation
        </h4>
        <ul class="space-y-1 list-disc pl-5">
          <li><strong class="text-tertiary">LOW RISK (0 &ndash; 34)</strong>: Standard balanced commercial provisions with clear obligations and mutual remedies.</li>
          <li><strong class="text-amber-300">MEDIUM RISK (35 &ndash; 64)</strong>: Ambiguous terms, vague notice periods, or mild unilateral obligations requiring clarification.</li>
          <li><strong class="text-error">HIGH RISK (65 &ndash; 100)</strong>: Asymmetric indemnity, uncapped consequential liability, or harsh unilateral termination covenants.</li>
        </ul>
      </div>

      <div>
        <h4 class="text-primary font-semibold text-base mb-1.5 flex items-center gap-1.5">
          <span class="material-symbols-outlined text-[18px]">smart_toy</span> 3. How to Demo to Your Professor
        </h4>
        <ol class="space-y-1.5 list-decimal pl-5">
          <li>Open <strong>Documents</strong> tab &rarr; click <strong>"High Risk Vendor"</strong> sample contract.</li>
          <li>Show <strong>Analysis</strong> tab: explain the circular Mamdani Risk Gauge (score: 78, High) and the 5 extractive summary categories.</li>
          <li>Point out the <strong>Missing Clause Audit</strong>: shows which mandatory protections were omitted.</li>
          <li>Switch to <strong>Search</strong> tab: type <em>"When does this contract expire?"</em> to show TF-IDF cosine ranking.</li>
          <li>Switch to <strong>AI Assistant</strong>: say <em>"Hi"</em>, ask <em>"What are the payment terms?"</em> or click prompt suggestions to show interactive conversational retrieval!</li>
        </ol>
      </div>
    </div>
    <div class="p-4 border-t border-surface-high bg-surface-low flex justify-end">
      <button type="button" onclick="closeHelpModal()" class="px-4 py-2 bg-primary text-on-primary font-semibold rounded-lg hover:bg-primary-container transition-colors text-xs">
        Got it, let's explore!
      </button>
    </div>
  </div>
</div>

<script src="/static/app.js"></script>
</body>
</html>
"""

    out_path = os.path.join(STATIC_DIR, "index.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(unified_html)

    print(f"Generated user-friendly index.html with Help Guide & Sample Switcher: {len(unified_html)} bytes at {out_path}")

if __name__ == "__main__":
    main()
