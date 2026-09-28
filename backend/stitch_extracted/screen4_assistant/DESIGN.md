---
name: LexiCore Systems
colors:
  surface: '#051424'
  surface-dim: '#051424'
  surface-bright: '#2c3a4c'
  surface-container-lowest: '#010f1f'
  surface-container-low: '#0d1c2d'
  surface-container: '#122131'
  surface-container-high: '#1c2b3c'
  surface-container-highest: '#273647'
  on-surface: '#d4e4fa'
  on-surface-variant: '#c2c6d6'
  inverse-surface: '#d4e4fa'
  inverse-on-surface: '#233143'
  outline: '#8c909f'
  outline-variant: '#424754'
  surface-tint: '#adc6ff'
  primary: '#adc6ff'
  on-primary: '#002e6a'
  primary-container: '#4d8eff'
  on-primary-container: '#00285d'
  inverse-primary: '#005ac2'
  secondary: '#c0c1ff'
  on-secondary: '#1000a9'
  secondary-container: '#3131c0'
  on-secondary-container: '#b0b2ff'
  tertiary: '#4edea3'
  on-tertiary: '#003824'
  tertiary-container: '#00a572'
  on-tertiary-container: '#00311f'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#d8e2ff'
  primary-fixed-dim: '#adc6ff'
  on-primary-fixed: '#001a42'
  on-primary-fixed-variant: '#004395'
  secondary-fixed: '#e1e0ff'
  secondary-fixed-dim: '#c0c1ff'
  on-secondary-fixed: '#07006c'
  on-secondary-fixed-variant: '#2f2ebe'
  tertiary-fixed: '#6ffbbe'
  tertiary-fixed-dim: '#4edea3'
  on-tertiary-fixed: '#002113'
  on-tertiary-fixed-variant: '#005236'
  background: '#051424'
  on-background: '#d4e4fa'
  surface-variant: '#273647'
typography:
  headline-xl:
    fontFamily: Geist
    fontSize: 40px
    fontWeight: '700'
    lineHeight: 48px
  headline-xl-mobile:
    fontFamily: Geist
    fontSize: 30px
    fontWeight: '700'
    lineHeight: 38px
  headline-lg:
    fontFamily: Geist
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
  headline-lg-mobile:
    fontFamily: Geist
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  headline-md:
    fontFamily: Geist
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  headline-sm:
    fontFamily: Geist
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
  metric-display:
    fontFamily: Geist
    fontSize: 48px
    fontWeight: '700'
    lineHeight: 52px
  metric-display-sm:
    fontFamily: Geist
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 36px
  title-md:
    fontFamily: Geist
    fontSize: 16px
    fontWeight: '600'
    lineHeight: 24px
  title-sm:
    fontFamily: Geist
    fontSize: 14px
    fontWeight: '600'
    lineHeight: 20px
  body-lg:
    fontFamily: Geist
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 26px
  body-md:
    fontFamily: Geist
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 22px
  body-sm:
    fontFamily: Geist
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 18px
  label-md:
    fontFamily: Geist
    fontSize: 13px
    fontWeight: '500'
    lineHeight: 16px
  label-sm:
    fontFamily: Geist
    fontSize: 11px
    fontWeight: '600'
    lineHeight: 14px
  code-sm:
    fontFamily: JetBrains Mono
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  gutter: 1rem
  gutter-lg: 1.5rem
  margin: 1.5rem
  margin-mobile: 1rem
  space-2xs: 0.125rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 1rem
  space-lg: 1.5rem
  space-xl: 2rem
  space-2xl: 3rem
---

## Brand & Style

This design system defines an analytical, deterministic, and mission-critical workspace for legal professionals, corporate counsel, and compliance officers. The platform does not rely on generative hallucinations; its intelligence stems from rule-based NLP, deterministic classification models, named entity recognition (spaCy), vector space similarity (TF-IDF), and rule-governed conversational flows (Dialogflow). 

The visual style is **Corporate / Modern High-Utility Dark Mode**. It avoids neon glowing halos, whimsical floating gradients, and conversational AI tropes in favor of structural density, crisp telemetry, razor-sharp information hierarchies, and surgical precision. 

The emotional response evoked must be:
- **Absolute Authority & Rigor:** Interfaces reflect institutional trust, legal auditability, and mathematical reproducibility.
- **Cognitive Clarity:** High-density data layouts, clause-level diffing, and risk distributions are consumed without fatigue through controlled contrast ratios and strict vertical rhythm.
- **Engineered Restraint:** Aesthetic flourishes are subordinated to data integrity, scan speed, and compliance clarity.

## Colors

The system uses a dark mode palette calibrated for prolonged focus, zero eye fatigue, and rapid visual triage of legal liabilities.

### Canvas & Surface Architecture
- **Canvas Base (`#0B0F17`):** The foundational viewport background for persistent shells, application gutters, and modal backdrops.
- **Surface Layer 1 (`#0F172A`):** Deep slate-navy used for primary structural containers, left navigation sidebars, and sticky table header planes.
- **Surface Layer 2 (`#131C2E`):** Resting state for interactive cards, data panels, document viewports, and audit modules.
- **Surface Layer 3 (`#182238`):** Elevated state for floating dialogs, flyout drawers, hovering states, and contextual action toolbars.
- **Structural Border (`#24324D`):** Architectural boundary line applied across cards, splitters, and grid lines with a 1px solid stroke. Subdued borders use `#1E293B`.

### Interactive & Brand Accents
- **Primary Electric Blue (`#3B82F6`):** Primary action buttons, active tab indicators, selected clause highlights, and deterministic match indicators.
- **Secondary Indigo (`#6366F1`):** Statistical analysis accents, categorical vector tags, entity categorization, and system states.

### Status & Legal Risk Tiers
Risk visualization relies on a triple-tier semantically anchored token system (Foreground / Soft Container / Border):
- **Low Risk / Safe Term:**
  - Ink: `#10B981` (Emerald)
  - Badge Container: `#064E3B` at 65% opacity
  - Stroke: `#059669`
- **Medium Risk / Ambiguous Term:**
  - Ink: `#F59E0B` (Amber)
  - Badge Container: `#78350F` at 65% opacity
  - Stroke: `#D97706`
- **High Risk / Non-Standard or Breach:**
  - Ink: `#EF4444` (Coral Red)
  - Badge Container: `#7F1D1D` at 65% opacity
  - Stroke: `#DC2626`

### Typography & Content Inks
- **Primary Text (`#F8FAFC`):** Maximum contrast for legal clause content, active numerals, headers, and imperative actions.
- **Secondary / Supporting Text (`#94A3B8`):** Neutral slate for metadata, entity labels, column descriptors, and breadcrumb trails.
- **Tertiary / Disabled Text (`#64748B`):** Timestamps, deactivated states, clause subsection numbers, and table footer statistics.

## Typography

Typography is calibrated using **Geist** for corporate precision, neutral geometry, and high-density legibility across tabular datasets and legal contracts. Numerical telemetry leverages tabular figures (`font-variant-numeric: tabular-nums`) to align risk scores, confidence values, and page indices without layout shifts.

- **Metric Numerals:** Standalone scores (e.g., `"84 / 100"`, `"99.2% Similarity"`) use `metric-display` with tight tracking (`-0.03em`) and tabular numerals, pairing the active score in `#F8FAFC` and the scale denominator in `#64748B`.
- **Legal Document Body (`body-md` / `body-lg`):** Calibrated for long-form legal agreements with increased line height (`1.6x`) to facilitate in-line entity highlighting, clause segmenting, and fuzzy-match underlines without row collision.
- **Code & Token Telemetry (`code-sm`):** Fallback font **JetBrains Mono** is specified for TF-IDF weight parameters, spaCy POS tags (`ORG`, `GPE`, `DATE`, `LAW`), and regex pattern indicators.

## Layout & Spacing

The layout is built on a 4px/8px deterministic spacing grid structured around a persistent productivity shell.

### Grid & Viewport Architecture
- **Desktop (>= 1280px):** 
  - Persistent left-rail navigation bar: 240px fixed width (`#0F172A`), collapsible to an icon-only 64px state.
  - Primary application viewport: Fluid grid spanning 12 columns with `1.5rem` (`gutter-lg`) spacing and `1.5rem` (`margin`) boundary insets.
  - Multi-pane workflow: For document analysis, the layout adopts a split-screen master-detail pane (40% clause directory / 60% legal document canvas, or 50/50 dual-document diff viewer).
- **Tablet (768px - 1279px):**
  - Left navigation collapses to 64px compact icon rail automatically.
  - Fluid 8-column layout with `1rem` gutters. Analysis split-panes switch to stacked tab views.
- **Mobile (< 768px):**
  - Navigation converts into a bottom-anchored bar or a slide-out drawer triggered from a compact 48px top-app bar.
  - 4-column layout with `1rem` margins. Dense data tables enable horizontal touch-scrolling with pinned identifier columns.

### Component Spacing Discipline
- Compact forms and entity lists use `space-xs` (4px) and `space-sm` (8px).
- Card interiors, form groupings, and analytic stat blocks enforce uniform `space-md` (16px) or `space-lg` (24px) internal paddings.
- Viewport sections maintain `space-xl` (32px) margins to preserve hierarchical separation between document review bars and aggregated telemetry panels.

## Elevation & Depth

This design system rejects deep drop shadows and skeuomorphic blur stacks, employing **Tonal Layering combined with Low-Contrast Precision Outlines**. Depth is established through stepped luminance levels of slate-navy and razor-sharp borders.

- **Base Layer (Elevation 0 - Background):** `#0B0F17`. Deepest canvas plane. Zero shadows, zero outlines.
- **Structural Layer (Elevation 1 - Sidebars, Navbars):** `#0F172A` with a right or bottom 1px stroke of `#24324D`. No drop shadow.
- **Card & Workspace Layer (Elevation 2 - Panels, Data Grids):** `#131C2E` resting on `#0B0F17`. Enclosed in a crisp 1px solid `#24324D` border. Hovering on interactive cards elevates the background to `#182238` and shifts border color to `#3B82F6` at 50% opacity.
- **Floating Overlays (Elevation 3 - Popovers, Dropdowns, Clause Hovercards):** `#182238` surface, 1px solid border of `#3B82F6` (30% opacity), paired with a focused, directional ambient shadow: `0 8px 24px -4px rgba(0, 0, 0, 0.45), 0 2px 6px -1px rgba(0, 0, 0, 0.30)`.
- **Dialogflow Chatbot Drawer & Modals (Elevation 4):** Anchored drawer and central modal dialogs use `#131C2E` surface, a 1px border of `#384B70`, and a wide ambient shadow: `0 20px 40px -8px rgba(0, 0, 0, 0.65)`. Background underlay uses `#0B0F17` at 70% opacity with a subtle `backdrop-filter: blur(4px)`.

## Shapes

The design system uses a **Soft (Level 1)** shape language. The interface favors disciplined, micro-radii to reinforce an architectural, legal-grade tool aesthetic rather than a consumer app.

- **Micro Radii (`0.25rem` / 4px):** Applied to badges, table tags, clause highlight blocks, checkboxes, metric pills, and tab indicators.
- **Standard Radii (`rounded-lg` / `0.5rem` / 8px):** Applied to inputs, buttons, card enclosures, floating popovers, and analysis widgets.
- **Panel Radii (`rounded-xl` / `0.75rem` / 12px):** Applied to top-level modal dialogs and the floating Dialogflow assistant drawer container.
- **Circular (`9999px`):** Reserved exclusively for status indicator pips, circular risk gauges, user avatars, and step-progress indicators.

## Components

### 1. Buttons
- **Primary:** Background `#3B82F6`, text `#F8FAFC`, font weight 500, radius 8px, height 36px (compact) or 40px (default). Hover: `#2563EB`. Active: `#1D4ED8`. Focus: 2px outline `#60A5FA` with 2px offset.
- **Secondary / Outline:** Background `transparent`, border 1px solid `#24324D`, text `#F8FAFC`. Hover: `#182238` background, border `#3B82F6`.
- **Ghost / Utility:** Transparent fill, no border, text `#94A3B8`. Hover: text `#F8FAFC`, background `#182238`. Used for table actions, copy buttons, and document pagination controls.
- **Destructive:** Background `#7F1D1D` at 30% fill, border 1px solid `#EF4444`, text `#EF4444`. Hover: background `#EF4444`, text `#FFFFFF`.

### 2. Form Inputs & Search Fields
- **Text & Numeric Inputs:** Height 40px, background `#0F172A`, border 1px solid `#24324D`, text `#F8FAFC`, radius 8px, padding 0 12px. Placeholder text `#64748B`. Focused state: border `#3B82F6`, box-shadow `0 0 0 1px #3B82F6`.
- **Global / Clause Regex Search:** Includes prepended search icon (`#64748B`), clear shortcut badge (`Ctrl + K` in `code-sm`, background `#182238`, border `#24324D`).

### 3. Checkboxes & Radio Controls
- Base: 16x16px, background `#0F172A`, border 1px solid `#24324D`, radius 4px (checkbox) or 9999px (radio).
- Checked: Background `#3B82F6`, border `#3B82F6`, checkmark/inner-dot `#F8FAFC`. Focus ring: 2px `#6366F1` offset by 2px `#0B0F17`.

### 4. Cards & Extractive Summary Panels
- Background `#131C2E`, border 1px solid `#24324D`, padding 20px, radius 8px. Header features clause title in `title-sm`, accompanied by model confidence percentage in `code-sm`.
- Card footers feature metadata tags (e.g., `"Extracted via spaCy [ORG]"`, `"Naive Bayes: 94.2% Conf"`) in `#94A3B8` over `#0F172A` chip containers.

### 5. Risk Scoring Badges & Clause Chips
- Composed of 4px rounded chips, height 22px, padding 0 8px, `label-sm` font.
- **Low Risk:** Text `#10B981`, background `rgba(6, 78, 59, 0.5)`, border 1px solid `rgba(16, 185, 129, 0.3)`.
- **Medium Risk:** Text `#F59E0B`, background `rgba(120, 53, 15, 0.5)`, border 1px solid `rgba(245, 158, 11, 0.3)`.
- **High Risk:** Text `#EF4444`, background `rgba(127, 29, 29, 0.5)`, border 1px solid `rgba(239, 68, 68, 0.3)`.

### 6. Circular Risk Gauges & Telemetry Meters
- Built as SVG concentric stroke rings or radial meters.
- Background meter track: `#182238` with 6px stroke width.
- Metric indicator stroke: Dynamically colored `#10B981` (0-35), `#F59E0B` (36-70), or `#EF4444` (71-100).
- Center text: Score displayed in `metric-display-sm` (`#F8FAFC`) with risk severity descriptor below in `label-sm` (`#94A3B8`).

### 7. Legal Data Tables
- Header: `#0F172A`, text `label-sm` in `#64748B`, uppercase, tracking `0.05em`, bottom border 1px solid `#24324D`.
- Rows: Alternating or uniform `#131C2E`, border-bottom 1px solid `#1E293B`, height 48px, text `body-md` (`#F8FAFC`). Hover state `#182238`.
- Cell Alignment: Numerical similarity scores and dates right-aligned with tabular figures. Clause names and status badges left-aligned.

### 8. TF-IDF Similarity & Fuzzy Match Indicators
- Horizontal inline micro-bars (width 64px, height 6px, radius 2px, background `#1E293B`).
- Fill percentage bar: Electric blue (`#3B82F6`) transitioning to indigo (`#6366F1`) based on standard score. Paired with numeric indicator `code-sm` (`0.87`).
- Fuzzy string matches highlight differing tokens in the text viewport using soft red strikethroughs (`rgba(239, 68, 68, 0.2)`) and green inserts (`rgba(16, 185, 129, 0.2)`).

### 9. Persistent Sidebar Navigation
- Width 240px, background `#0F172A`, border-right 1px solid `#24324D`.
- Navigation Items: Height 40px, margin `0 8px 4px 8px`, padding `0 12px`, radius 6px, text `title-sm` in `#94A3B8`.
- Active Item: Background `#131C2E`, text `#F8FAFC`, left border-accent 3px solid `#3B82F6`.
- Item categories: Dashboard, Upload, Documents, Analysis, Search, Dialogflow Assistant, Analytics, Reports, Settings.

### 10. Dialogflow Chatbot Floating Drawer
- Docked at bottom-right viewport (`bottom: 24px`, `right: 24px`), width 400px, height 580px, elevation 4, radius 12px.
- Surface: `#131C2E`, header `#0F172A` with Dialogflow intent confidence indicator (`Intent: query_clause_liability [0.96]`).
- Message bubbles:
  - User: Background `#3B82F6`, text `#F8FAFC`, radius 8px 8px 2px 8px.
  - Assistant: Background `#182238`, border 1px solid `#24324D`, text `#F8FAFC`, radius 8px 8px 8px 2px. Includes actionable intent buttons (e.g., `"Jump to Section 14.2"`, `"Export Redline"`).