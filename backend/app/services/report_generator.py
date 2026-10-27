import io
import csv
from datetime import datetime, timezone
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
    KeepTogether,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from app.database.models import ComparisonRecord, PolicyChangeRecord


class ReportGenerator:
    @staticmethod
    def generate_csv(comparison: ComparisonRecord, changes: list[PolicyChangeRecord]) -> str:
        """Generates a structured, properly escaped CSV document string."""
        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_ALL)

        # Header row
        writer.writerow([
            "Change ID",
            "Change Type",
            "Category",
            "Priority",
            "Similarity Score",
            "Confidence",
            "Plain-English Explanation",
            "Priority Rationale",
            "Old Text",
            "New Text",
            "Old Section",
            "New Section",
            "Old Page",
            "New Page",
            "Reviewed Status",
        ])

        for c in changes:
            writer.writerow([
                c.id,
                c.change_type,
                c.category,
                c.priority,
                f"{c.similarity_score:.3f}",
                f"{c.alignment_confidence:.3f}",
                c.explanation or "",
                c.priority_rationale or "",
                c.old_text or "",
                c.new_text or "",
                c.old_section or "",
                c.new_section or "",
                c.old_page or "",
                c.new_page or "",
                "Reviewed" if c.is_reviewed else "Pending Review",
            ])

        return output.getvalue()

    @staticmethod
    def generate_pdf(comparison: ComparisonRecord, changes: list[PolicyChangeRecord]) -> bytes:
        """Generates an executive-grade PDF comparison report using ReportLab."""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=40,
            leftMargin=40,
            topMargin=40,
            bottomMargin=40,
        )

        styles = getSampleStyleSheet()

        # Custom paragraph styles
        title_style = ParagraphStyle(
            "DocTitle",
            parent=styles["Heading1"],
            fontSize=22,
            leading=26,
            textColor=colors.HexColor("#0f172a"),
            spaceAfter=4,
        )
        subtitle_style = ParagraphStyle(
            "DocSubtitle",
            parent=styles["Normal"],
            fontSize=11,
            leading=15,
            textColor=colors.HexColor("#475569"),
            spaceAfter=12,
        )
        section_heading = ParagraphStyle(
            "SectionHeading",
            parent=styles["Heading2"],
            fontSize=14,
            leading=18,
            textColor=colors.HexColor("#1e293b"),
            spaceBefore=14,
            spaceAfter=6,
        )
        body_style = ParagraphStyle(
            "Body",
            parent=styles["Normal"],
            fontSize=9,
            leading=13,
            textColor=colors.HexColor("#334155"),
        )
        bold_label = ParagraphStyle(
            "BoldLabel",
            parent=styles["Normal"],
            fontSize=9,
            leading=13,
            fontName="Helvetica-Bold",
            textColor=colors.HexColor("#0f172a"),
        )
        explanation_style = ParagraphStyle(
            "Expl",
            parent=styles["Normal"],
            fontSize=9,
            leading=13,
            textColor=colors.HexColor("#0369a1"),
            fontName="Helvetica-Oblique",
        )

        story = []

        # 1. Header & Title
        story.append(Paragraph("PolicyDiff — Semantic Change Analysis Report", title_style))
        inst_text = f" | Institution: {comparison.institution}" if comparison.institution else ""
        story.append(
            Paragraph(
                f"Generated on {datetime.now(timezone.utc).strftime('%B %d, %Y at %H:%M UTC')}{inst_text}",
                subtitle_style,
            )
        )
        story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#2563eb"), spaceAfter=14))

        # 2. Comparison Metadata Table
        meta_data = [
            [
                Paragraph("<b>Comparison Title:</b>", body_style),
                Paragraph(comparison.title, body_style),
                Paragraph("<b>NLP Engine:</b>", body_style),
                Paragraph(comparison.nlp_engine, body_style),
            ],
            [
                Paragraph("<b>Old Document:</b>", body_style),
                Paragraph(f"{comparison.old_filename} ({comparison.old_version})", body_style),
                Paragraph("<b>New Document:</b>", body_style),
                Paragraph(f"{comparison.new_filename} ({comparison.new_version})", body_style),
            ],
        ]
        meta_table = Table(meta_data, colWidths=[110, 160, 90, 170])
        meta_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ])
        )
        story.append(meta_table)
        story.append(Spacer(1, 14))

        # 3. Executive Metrics Table
        story.append(Paragraph("Executive Summary Statistics", section_heading))
        stats_data = [
            ["Total Detected Changes", "Added Rules", "Removed Rules", "Modified Rules", "High/Critical Priority"],
            [
                str(comparison.total_changes),
                str(comparison.added_count),
                str(comparison.removed_count),
                str(comparison.modified_count),
                str(comparison.high_priority_count),
            ],
        ]
        stats_table = Table(stats_data, colWidths=[106, 106, 106, 106, 106])
        stats_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e293b")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 9),
                ("FONTNAME", (0, 1), (-1, 1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 1), (-1, 1), 12),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BACKGROUND", (0, 1), (-1, 1), colors.HexColor("#f1f5f9")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ])
        )
        story.append(stats_table)
        story.append(Spacer(1, 14))

        # 4. Detailed Changes Breakdown
        story.append(Paragraph("Detected Policy Changes & Explanations", section_heading))

        active_changes = [c for c in changes if c.change_type != "UNCHANGED"]
        if not active_changes:
            story.append(Paragraph("No material policy differences were detected between the versions.", body_style))
        else:
            for idx, c in enumerate(active_changes, start=1):
                # Badge color
                type_color = "#16a34a" if c.change_type == "ADDED" else ("#dc2626" if c.change_type == "REMOVED" else "#d97706")
                priority_color = "#b91c1c" if c.priority == "Critical" else ("#c2410c" if c.priority == "High" else "#475569")

                item_elements = []
                item_elements.append(
                    Paragraph(
                        f"<b>#{idx}. [{c.change_type}]</b> &nbsp; <font color='{type_color}'><b>{c.category}</b></font> &nbsp; | &nbsp; "
                        f"Priority: <font color='{priority_color}'><b>{c.priority}</b></font> &nbsp; | &nbsp; "
                        f"Similarity: <b>{c.similarity_score:.0%}</b>",
                        bold_label,
                    )
                )

                if c.explanation:
                    item_elements.append(Spacer(1, 3))
                    item_elements.append(Paragraph(f"<b>Explanation:</b> {c.explanation}", explanation_style))

                if c.priority_rationale:
                    item_elements.append(Spacer(1, 2))
                    item_elements.append(Paragraph(f"<b>Priority Rationale:</b> {c.priority_rationale}", body_style))

                # Excerpt comparison table
                excerpts = []
                if c.old_text:
                    excerpts.append([
                        Paragraph(f"<b>Old Policy ({comparison.old_version}):</b>", bold_label),
                        Paragraph(c.old_text, body_style),
                    ])
                if c.new_text:
                    excerpts.append([
                        Paragraph(f"<b>New Policy ({comparison.new_version}):</b>", bold_label),
                        Paragraph(c.new_text, body_style),
                    ])

                if excerpts:
                    ex_table = Table(excerpts, colWidths=[130, 400])
                    ex_table.setStyle(
                        TableStyle([
                            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
                            ("TOPPADDING", (0, 0), (-1, -1), 3),
                            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                            ("LEFTPADDING", (0, 0), (-1, -1), 4),
                            ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                            ("VALIGN", (0, 0), (-1, -1), "TOP"),
                            ("LINEBELOW", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                        ])
                    )
                    item_elements.append(Spacer(1, 4))
                    item_elements.append(ex_table)

                item_elements.append(Spacer(1, 8))
                item_elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#e2e8f0"), spaceAfter=8))

                story.append(KeepTogether(item_elements))

        # 5. Methodology & Disclaimer
        story.append(Spacer(1, 10))
        story.append(Paragraph("Methodology & Institutional Disclaimer", section_heading))
        disclaimer_text = (
            "<b>Methodology:</b> PolicyDiff extracts document structure, segments rules, computes dual-mode "
            "semantic and lexical similarity matrices (sentence vectors, TF-IDF n-grams, and token alignment), "
            "and performs deterministic entity difference detection for dates, numeric thresholds, and modality.<br/>"
            "<b>Disclaimer:</b> PolicyDiff is an automated decision-support system designed to assist academic review. "
            "It does not constitute official legal or administrative counsel. Always consult authorized institutional officers."
        )
        story.append(Paragraph(disclaimer_text, body_style))

        doc.build(story)
        return buffer.getvalue()
