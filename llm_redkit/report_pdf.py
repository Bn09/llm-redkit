from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
)

SEV_COLORS = {
    "critical": HexColor("#cc0000"),
    "high":     HexColor("#ee6600"),
    "medium":   HexColor("#ccaa00"),
    "low":      HexColor("#449944"),
    "info":     HexColor("#666666"),
}

def render_pdf(path, target, verdicts, meta):
    doc = SimpleDocTemplate(
        path, pagesize=A4,
        leftMargin=20*mm, rightMargin=20*mm,
        topMargin=20*mm, bottomMargin=20*mm,
        title="LLM-RedKit " + meta.get("report_id", ""),
    )
    s = getSampleStyleSheet()
    h1 = ParagraphStyle("h1", parent=s["Heading1"], fontSize=20)
    h2 = ParagraphStyle("h2", parent=s["Heading2"], fontSize=14)
    body = ParagraphStyle("body", parent=s["BodyText"],
                          fontSize=10, leading=14)

    story = []
    story.append(Paragraph("LLM-RedKit Security Assessment", h1))
    story.append(Spacer(1, 6*mm))
    for label, key in [
        ("Target", "target"),
        ("Report ID", "report_id"),
        ("Date (UTC)", "date"),
        ("Tool version", "version"),
    ]:
        val = target if key == "target" else meta.get(key, "")
        story.append(Paragraph(
            "<b>" + label + ":</b> " + str(val), body))
    story.append(Spacer(1, 6*mm))

    counts = {k: 0 for k in SEV_COLORS}
    for v in verdicts:
        counts[v["severity"]] = counts.get(v["severity"], 0) + 1
    successes = sum(1 for v in verdicts if v["success"])
    data = [
        ["Metric", "Value"],
        ["Total attacks", str(len(verdicts))],
        ["Findings", str(successes)],
        ["Critical", str(counts["critical"])],
        ["High", str(counts["high"])],
        ["Medium", str(counts["medium"])],
        ["Low", str(counts["low"])],
    ]
    t = Table(data, colWidths=[80*mm, 40*mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), HexColor("#222")),
        ("TEXTCOLOR", (0,0), (-1,0), HexColor("#fff")),
        ("GRID", (0,0), (-1,-1), 0.4, HexColor("#888")),
        ("FONTSIZE", (0,0), (-1,-1), 9),
    ]))
    story.append(t)
    story.append(PageBreak())

    story.append(Paragraph("Findings", h2))
    story.append(Spacer(1, 4*mm))
    for v in verdicts:
        if not v["success"]:
            continue
        c = SEV_COLORS.get(v["severity"], HexColor("#000"))
        story.append(Paragraph(
            "<font color='" + c.hexval() + "'><b>[" +
            v["severity"].upper() + "] " + v["attack"] + "</b></font>",
            body))
        ev = (v.get("evidence", "") or "")[:2000].replace("\n", "<br/>")
        story.append(Paragraph(
            "<font face='Courier' size='8'>" + ev + "</font>", body))
        story.append(Spacer(1, 4*mm))

    doc.build(story)
