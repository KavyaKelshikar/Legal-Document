"""
Deterministic PDF Report Generation Service for AI Legal Document Assistant.
Generates an academic analysis report using PyMuPDF (fitz) without any LLM.
"""

import io
import logging
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
import pymupdf as fitz
from src.storage.document_store import get_document_store
from src.services.analytics_service import get_analytics_service
from src.services.missing_clause_service import get_missing_clause_service
from src.services.summary_service import get_summary_service

logger = logging.getLogger(__name__)

# Color constants (RGB 0.0 - 1.0)
COLOR_PRIMARY = (0.1, 0.18, 0.35)      # Deep Navy
COLOR_SECONDARY = (0.25, 0.35, 0.5)    # Slate Blue
COLOR_TEXT = (0.15, 0.15, 0.15)         # Charcoal Dark
COLOR_MUTED = (0.45, 0.45, 0.45)        # Muted Gray
COLOR_LINE = (0.85, 0.85, 0.88)         # Light Gray Divider
COLOR_BG_LIGHT = (0.96, 0.97, 0.98)     # Soft Background Box

COLOR_RISK_HIGH = (0.82, 0.15, 0.15)    # Red
COLOR_RISK_MED = (0.85, 0.55, 0.1)     # Amber/Orange
COLOR_RISK_LOW = (0.15, 0.6, 0.28)     # Green


class PDFReportBuilder:
    """Helper class to layout multi-page PDF document cleanly using PyMuPDF."""

    def __init__(self, page_width: float = 595.0, page_height: float = 842.0):
        self.doc = fitz.open()
        self.width = page_width
        self.height = page_height
        self.margin_left = 50.0
        self.margin_right = page_width - 50.0
        self.margin_top = 50.0
        self.margin_bottom = page_height - 50.0
        self.usable_width = self.margin_right - self.margin_left
        self.current_page: Optional[fitz.Page] = None
        self.y = self.margin_top
        self.page_number = 0
        self._new_page()

    def _new_page(self) -> None:
        """Starts a new page and resets cursor."""
        self.current_page = self.doc.new_page(width=self.width, height=self.height)
        self.page_number += 1
        self.y = self.margin_top
        # Top banner line on subsequent pages
        if self.page_number > 1:
            self.current_page.draw_line(
                (self.margin_left, 35),
                (self.margin_right, 35),
                color=COLOR_LINE,
                width=0.5,
            )
            self.current_page.insert_text(
                (self.margin_left, 30),
                "AI Legal Document Analysis Report (Academic Demo)",
                fontsize=8,
                fontname="helv",
                color=COLOR_MUTED,
            )

    def ensure_space(self, needed_height: float) -> None:
        """Ensures that needed_height is available on the current page or adds a new page."""
        if self.y + needed_height > self.margin_bottom:
            self._new_page()

    def add_header(self, title: str, subtitle: str) -> None:
        """Draws top report title and subtitle with accent bar."""
        self.ensure_space(70)
        # Accent decorative bar
        rect = fitz.Rect(self.margin_left, self.y, self.margin_left + 4, self.y + 42)
        self.current_page.draw_rect(rect, color=COLOR_PRIMARY, fill=COLOR_PRIMARY)

        # Title
        self.current_page.insert_text(
            (self.margin_left + 12, self.y + 18),
            title,
            fontsize=18,
            fontname="hebo",
            color=COLOR_PRIMARY,
        )
        # Subtitle
        self.current_page.insert_text(
            (self.margin_left + 12, self.y + 34),
            subtitle,
            fontsize=9.5,
            fontname="helv",
            color=COLOR_MUTED,
        )
        self.y += 54
        # Divider line
        self.current_page.draw_line(
            (self.margin_left, self.y),
            (self.margin_right, self.y),
            color=COLOR_LINE,
            width=1.0,
        )
        self.y += 15

    def add_section_title(self, title: str) -> None:
        """Adds a prominent section heading with an underline."""
        self.ensure_space(35)
        self.current_page.insert_text(
            (self.margin_left, self.y + 12),
            title,
            fontsize=12,
            fontname="hebo",
            color=COLOR_PRIMARY,
        )
        self.current_page.draw_line(
            (self.margin_left, self.y + 17),
            (self.margin_left + 220, self.y + 17),
            color=COLOR_SECONDARY,
            width=1.0,
        )
        self.y += 26

    def add_text_line(self, label: str, value: str, indent: float = 0.0) -> None:
        """Adds a single key-value row."""
        self.ensure_space(16)
        x = self.margin_left + indent
        self.current_page.insert_text(
            (x, self.y + 10),
            f"{label}:",
            fontsize=9.5,
            fontname="hebo",
            color=COLOR_TEXT,
        )
        self.current_page.insert_text(
            (x + 130, self.y + 10),
            str(value),
            fontsize=9.5,
            fontname="helv",
            color=COLOR_TEXT,
        )
        self.y += 15

    def add_risk_badge(self, level: str, score: float) -> None:
        """Draws a highlighted risk banner with score and classification."""
        self.ensure_space(42)
        lvl_upper = level.upper()
        if lvl_upper == "HIGH":
            badge_color = COLOR_RISK_HIGH
        elif lvl_upper == "MEDIUM":
            badge_color = COLOR_RISK_MED
        else:
            badge_color = COLOR_RISK_LOW

        box_rect = fitz.Rect(self.margin_left, self.y, self.margin_right, self.y + 36)
        self.current_page.draw_rect(box_rect, color=COLOR_LINE, fill=COLOR_BG_LIGHT)

        # Risk indicator box
        badge_rect = fitz.Rect(self.margin_left + 10, self.y + 6, self.margin_left + 110, self.y + 30)
        self.current_page.draw_rect(badge_rect, color=badge_color, fill=badge_color)
        self.current_page.insert_text(
            (self.margin_left + 22, self.y + 22),
            f"RISK: {lvl_upper}",
            fontsize=10.5,
            fontname="hebo",
            color=(1.0, 1.0, 1.0),
        )

        score_text = f"Fuzzy Risk Score: {score:.1f} / 100" if score is not None else "Fuzzy Risk Score: N/A"
        self.current_page.insert_text(
            (self.margin_left + 125, self.y + 22),
            score_text,
            fontsize=10,
            fontname="hebo",
            color=COLOR_TEXT,
        )
        self.y += 46

    def add_wrapped_paragraph(
        self,
        text: str,
        fontsize: float = 9.0,
        fontname: str = "helv",
        color: tuple = COLOR_TEXT,
        indent: float = 0.0,
        bg: bool = False,
    ) -> None:
        """Inserts text wrapped inside usable bounding box."""
        if not text:
            return

        box_width = self.usable_width - indent
        # Approximate line count: ~105 characters per line at font 9
        chars_per_line = max(1, int(box_width / (fontsize * 0.52)))
        lines = [text[i:i + chars_per_line] for i in range(0, len(text), chars_per_line)]
        approx_height = max(18.0, len(lines) * (fontsize + 3.5) + 6.0)

        self.ensure_space(approx_height)

        rect = fitz.Rect(
            self.margin_left + indent,
            self.y,
            self.margin_right,
            self.y + approx_height,
        )

        if bg:
            self.current_page.draw_rect(rect, color=COLOR_LINE, fill=COLOR_BG_LIGHT)

        # Insert textbox wraps words naturally
        self.current_page.insert_textbox(
            rect,
            text,
            fontsize=fontsize,
            fontname=fontname,
            color=color,
        )
        self.y += approx_height + 4.0

    def add_table_header(self, columns: List[Tuple[str, float]]) -> None:
        """Draws table header row with column widths."""
        self.ensure_space(22)
        rect = fitz.Rect(self.margin_left, self.y, self.margin_right, self.y + 18)
        self.current_page.draw_rect(rect, color=COLOR_PRIMARY, fill=COLOR_PRIMARY)

        curr_x = self.margin_left + 6
        for title, width in columns:
            self.current_page.insert_text(
                (curr_x, self.y + 13),
                title,
                fontsize=8.5,
                fontname="hebo",
                color=(1.0, 1.0, 1.0),
            )
            curr_x += width
        self.y += 20

    def add_table_row(self, columns: List[Tuple[str, float]], is_even: bool = False) -> None:
        """Draws a table row with subtle zebra striping."""
        self.ensure_space(18)
        rect = fitz.Rect(self.margin_left, self.y, self.margin_right, self.y + 16)
        if is_even:
            self.current_page.draw_rect(rect, color=(0.95, 0.95, 0.96), fill=(0.95, 0.95, 0.96))

        curr_x = self.margin_left + 6
        for val, width in columns:
            self.current_page.insert_text(
                (curr_x, self.y + 11),
                str(val),
                fontsize=8.5,
                fontname="helv",
                color=COLOR_TEXT,
            )
            curr_x += width
        self.y += 17

    def finalize(self) -> bytes:
        """Adds page numbers to all pages and returns PDF bytes."""
        total_pages = self.doc.page_count
        for i in range(total_pages):
            page = self.doc.load_page(i)
            # Footer text
            footer_text = f"Page {i + 1} of {total_pages} — AI Legal Document Assistant"
            page.draw_line(
                (self.margin_left, self.height - 35),
                (self.margin_right, self.height - 35),
                color=COLOR_LINE,
                width=0.5,
            )
            page.insert_text(
                (self.margin_left, self.height - 24),
                footer_text,
                fontsize=8,
                fontname="helv",
                color=COLOR_MUTED,
            )
            page.insert_text(
                (self.margin_right - 140, self.height - 24),
                "Academic Demonstration Only",
                fontsize=8,
                fontname="helv",
                color=COLOR_MUTED,
            )

        pdf_bytes = self.doc.tobytes()
        self.doc.close()
        return pdf_bytes


class ReportService:
    """Service to create comprehensive, deterministic PDF analysis reports."""

    def generate_report_bytes(self, document_id: str) -> Optional[Tuple[bytes, str]]:
        """
        Retrieves document by ID and compiles PDF report.

        Returns:
            Optional[Tuple[bytes, str]]: (pdf_bytes, suggested_filename) or None if not found.
        """
        store = get_document_store()
        doc = store.get_document(document_id)
        if doc is None:
            return None

        pdf_bytes = self.build_pdf(doc)
        raw_name = doc.get("filename", "contract.pdf")
        clean_name = re.sub(r"[^\w\.\-]", "_", raw_name)
        if clean_name.lower().endswith(".pdf"):
            clean_name = clean_name[:-4]
        filename = f"legal_analysis_{clean_name}.pdf"

        return pdf_bytes, filename

    def build_pdf(self, doc: Dict[str, Any]) -> bytes:
        """Builds the complete multi-page PDF document from stored analysis."""
        builder = PDFReportBuilder()

        # ── Title & Subtitle ──
        builder.add_header(
            "AI Legal Document Analysis Report",
            "Deterministic Pipeline Analysis (PyMuPDF / spaCy / Naive Bayes / Fuzzy Logic)",
        )

        # ── 1. Document Information ──
        builder.add_section_title("1. Document Information")
        builder.add_text_line("Document Filename", doc.get("filename", "N/A"))
        builder.add_text_line("Document ID", doc.get("document_id", "N/A"))

        timestamp = doc.get("upload_timestamp", "")
        if timestamp:
            try:
                # Format friendly date
                dt = datetime.fromisoformat(timestamp)
                timestamp_str = dt.strftime("%B %d, %Y - %H:%M:%S UTC")
            except Exception:
                timestamp_str = str(timestamp)
        else:
            timestamp_str = "N/A"
        builder.add_text_line("Analysis Date", timestamp_str)

        pages_count = doc.get("metadata", {}).get("page_count", "N/A")
        builder.add_text_line("Total Pages", str(pages_count))
        builder.add_text_line("Total Clauses", str(doc.get("total_clauses", len(doc.get("clauses", [])))))
        builder.y += 8

        # ── 2. Overall Risk Assessment ──
        builder.add_section_title("2. Overall Risk Assessment")
        doc_risk = doc.get("document_risk", {})
        overall_level = str(doc_risk.get("overall_level", "LOW")).upper()
        overall_score = doc_risk.get("overall_score")
        score_float = float(overall_score) if isinstance(overall_score, (int, float)) else 0.0
        builder.add_risk_badge(overall_level, score_float)

        # ── 3. Extractive Contract Summary ──
        builder.add_section_title("3. Extractive Contract Summary")
        summary_info = doc.get("summary")
        if not summary_info:
            summary_service = get_summary_service()
            summary_info = summary_service.extract_summary(doc.get("clauses", []))

        category_labels = [
            ("duration", "Contract Duration / Term"),
            ("payment_terms", "Payment Terms & Invoicing"),
            ("termination", "Termination & Notice Period"),
            ("confidentiality", "Confidentiality Obligations"),
            ("liability", "Limitation of Liability"),
        ]

        for key, label in category_labels:
            cat_data = summary_info.get(key, {})
            status = cat_data.get("status", "not_detected")
            builder.ensure_space(20)
            builder.current_page.insert_text(
                (builder.margin_left, builder.y + 10),
                f"- {label}:",
                fontsize=9.5,
                fontname="hebo",
                color=COLOR_TEXT,
            )
            builder.y += 14

            if status == "detected" and cat_data.get("text"):
                builder.add_wrapped_paragraph(cat_data["text"], fontsize=8.5, indent=14, bg=True)
            else:
                builder.current_page.insert_text(
                    (builder.margin_left + 14, builder.y + 8),
                    "Not detected",
                    fontsize=8.5,
                    fontname="helv",
                    color=COLOR_MUTED,
                )
                builder.y += 14

        builder.y += 8

        # ── 4. Clause Classification Breakdown ──
        builder.add_section_title("4. Clause Classification Breakdown")
        analytics_service = get_analytics_service()
        doc_analytics = analytics_service.calculate_document_analytics(doc)
        cat_dist = doc_analytics.get("category_distribution", {})

        builder.add_table_header([("Clause Category", 240.0), ("Clause Count", 120.0), ("Percentage", 135.0)])
        total_c = max(1, doc.get("total_clauses", 1))
        is_even = False
        for cat_name, count in sorted(cat_dist.items(), key=lambda x: x[1], reverse=True):
            pct = (count / total_c) * 100
            builder.add_table_row(
                [(cat_name, 240.0), (str(count), 120.0), (f"{pct:.1f}%", 135.0)],
                is_even=is_even,
            )
            is_even = not is_even

        builder.y += 10

        # ── 5. Clause-Level Risk Analysis Table ──
        builder.add_section_title("5. Clause-Level Risk Analysis")
        clauses = doc.get("clauses", [])
        builder.add_table_header([
            ("ID", 30.0),
            ("Category", 105.0),
            ("Risk Score", 75.0),
            ("Risk Level", 75.0),
            ("Clause Excerpt", 210.0),
        ])

        is_even = False
        for c in clauses:
            cid = f"#{c.get('clause_id', '-')}"
            ccat = str(c.get("predicted_category", "General"))
            r_score = c.get("risk_score")
            score_str = f"{r_score:.1f}" if isinstance(r_score, (int, float)) else "N/A"
            lvl = str(c.get("risk_level", "LOW")).upper()

            # Shorten excerpt to fit single line
            text = c.get("original_text", "").replace("\n", " ").strip()
            excerpt = (text[:48] + "...") if len(text) > 48 else text

            builder.add_table_row([
                (cid, 30.0),
                (ccat, 105.0),
                (score_str, 75.0),
                (lvl, 75.0),
                (excerpt, 210.0),
            ], is_even=is_even)
            is_even = not is_even

        builder.y += 10

        # ── 6. Potentially Missing Clause Categories ──
        builder.add_section_title("6. Potentially Missing Clause Categories")
        missing_data = doc.get("missing_clauses")
        if not missing_data:
            missing_service = get_missing_clause_service()
            missing_data = missing_service.detect_missing_clauses(clauses)

        missing_items = missing_data.get("missing_clauses", [])
        if not missing_items:
            builder.current_page.insert_text(
                (builder.margin_left, builder.y + 10),
                "No potentially missing clause categories were detected.",
                fontsize=9.0,
                fontname="helv",
                color=COLOR_TEXT,
            )
            builder.y += 18
        else:
            for item in missing_items:
                cat = item.get("category", "")
                rationale = item.get("rationale", "")
                risk_impact = item.get("risk_impact", "")

                builder.ensure_space(34)
                builder.current_page.insert_text(
                    (builder.margin_left, builder.y + 10),
                    f"- {cat} : Potentially missing clause category",
                    fontsize=9.0,
                    fontname="hebo",
                    color=COLOR_RISK_HIGH,
                )
                builder.y += 13
                full_desc = f"{rationale} {risk_impact}"
                builder.add_wrapped_paragraph(full_desc, fontsize=8.0, indent=14, color=COLOR_MUTED)

        builder.y += 8

        # ── 7. Important Findings ──
        builder.add_section_title("7. Important Findings & Analytical Summary")
        high_risk_list = doc_analytics.get("high_risk_clauses", [])
        highest_score = doc_analytics.get("highest_clause_risk_score", 0.0)

        findings = [
            f"Overall Document Risk is categorized as {overall_level} with a weighted score of {score_float:.1f}.",
            f"Highest individual clause risk score observed is {highest_score:.1f}.",
            f"Detected {len(high_risk_list)} high-risk clause(s) requiring careful review.",
            f"Detected {len(missing_items)} potentially missing standard legal category/categories.",
        ]
        for f in findings:
            builder.ensure_space(14)
            builder.current_page.insert_text(
                (builder.margin_left, builder.y + 10),
                f"- {f}",
                fontsize=8.5,
                fontname="helv",
                color=COLOR_TEXT,
            )
            builder.y += 14

        builder.y += 8

        # ── 8. Academic Analysis Disclaimer ──
        builder.add_section_title("8. Academic Analysis Disclaimer")
        disclaimer = (
            "This report is generated using deterministic document-analysis techniques including "
            "rule-based processing, Naive Bayes classification, TF-IDF/Cosine Similarity, and "
            "fuzzy logic risk assessment. It is intended for academic and informational purposes "
            "and does not constitute legal advice."
        )
        builder.add_wrapped_paragraph(
            disclaimer,
            fontsize=8.0,
            fontname="helv",
            color=COLOR_MUTED,
            bg=True,
        )

        return builder.finalize()


# Global singleton instance
_report_instance: Optional[ReportService] = None


def get_report_service() -> ReportService:
    """Provides a singleton instance of ReportService."""
    global _report_instance
    if _report_instance is None:
        _report_instance = ReportService()
    return _report_instance
