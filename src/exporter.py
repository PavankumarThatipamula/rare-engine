from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from src.config import REBUTTALS_DIR
from src.document_agent import DisputePackage


class DefensePacketExporter:
    """Compiles extracted telemetry, network rules, and rebuttal text into a formal PDF submission packet."""

    @staticmethod
    def export_pdf(package: DisputePackage, rebuttal_data: dict) -> Path:
        evidence = package.extracted_data
        output_path = REBUTTALS_DIR / f"defense_packet_{evidence.dispute_id}.pdf"

        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=letter,
            rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40
        )
        
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "DocTitle", parent=styles["Heading1"], fontSize=18, leading=22, textColor=colors.HexColor("#0C2340")
        )
        heading_style = ParagraphStyle(
            "DocSubTitle", parent=styles["Heading2"], fontSize=12, leading=16, textColor=colors.HexColor("#1D4ED8")
        )
        body_style = ParagraphStyle(
            "DocBody", parent=styles["Normal"], fontSize=9, leading=13
        )

        elements = []

        # Header Section
        elements.append(Paragraph("<b>RPAY AUTO-REPRESENTMENT DEFENSE PACKET</b>", title_style))
        elements.append(Paragraph(f"Dispute ID: {evidence.dispute_id} | Transaction ID: {evidence.transaction_id}", heading_style))
        elements.append(Spacer(1, 10))

        # Metadata Summary Table
        table_data = [
            ["Dispute Amount", f"{evidence.currency} {evidence.amount:,.2f}", "Network / Reason Code", f"{evidence.network} ({evidence.reason_code})"],
            ["Customer Name", evidence.customer.name, "Customer IP Address", evidence.customer.ip_address],
            ["3DS Version", evidence.telemetry.three_ds_version, "3DS Status (Liability Shift)", "PASS" if evidence.is_3ds_authenticated else "FAIL"],
            ["AVS Match Code", evidence.telemetry.avs_match, "Evidence Score", f"{evidence.compelling_evidence_score * 100:.0f}%"]
        ]

        t = Table(table_data, colWidths=[120, 150, 130, 130])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor("#1E293B")),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(t)
        elements.append(Spacer(1, 15))

        # Network Governing Standard Section
        elements.append(Paragraph("<b>Card Network Compliance Standard</b>", heading_style))
        elements.append(Paragraph(f"Governing Clause: {rebuttal_data['governing_clause']}", body_style))
        elements.append(Spacer(1, 10))

        # Legal Rebuttal Body
        elements.append(Paragraph("<b>Automated Rebuttal Defense Statement</b>", heading_style))
        formatted_rebuttal = rebuttal_data["rebuttal_text"].replace("\n", "<br/>")
        elements.append(Paragraph(formatted_rebuttal, body_style))

        doc.build(elements)
        return output_path