"""PDF risk assessment form and register-request notice - colour scheme of the original OKPELLA HTML app."""
from __future__ import annotations

import io
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.platypus import KeepTogether, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

try:
    from .risk_engine import ENGINE_VERSION, LEVEL_NAME, LEVEL_ORDER
except ImportError:
    from engine import ENGINE_VERSION, LEVEL_NAME, LEVEL_ORDER

PAPER_DIM = colors.HexColor("#f2f6fc")
INK = colors.HexColor("#14202e")
INK_DIM = colors.HexColor("#5c7086")
LINE = colors.HexColor("#d7e3ee")
BLUE_DEEP = colors.HexColor("#123a73")
BLUE_LIGHT = colors.HexColor("#e4eefb")
SUB = colors.HexColor("#bcd2ee")
RED = colors.HexColor("#c6303e")
RED_DARK = colors.HexColor("#a2242f")
LV = {"E": colors.HexColor("#c6303e"), "H": colors.HexColor("#e0793a"), "M": colors.HexColor("#d9b23a"),
      "L": colors.HexColor("#4f9d63"), "N": colors.HexColor("#4a7fc9")}
EXCL_BG = colors.HexColor("#eef0f3")
EXCL_INK = colors.HexColor("#7d8996")

S = {
    "company": ParagraphStyle("company", fontName="Helvetica-Bold", fontSize=15, leading=18, textColor=colors.white, alignment=TA_CENTER),
    "form": ParagraphStyle("form", fontName="Helvetica", fontSize=10, leading=12, textColor=SUB, alignment=TA_CENTER),
    "k": ParagraphStyle("k", fontName="Helvetica-Bold", fontSize=8.5, leading=11, textColor=INK_DIM),
    "v": ParagraphStyle("v", fontName="Helvetica", fontSize=9, leading=11.5, textColor=INK),
    "h3": ParagraphStyle("h3", fontName="Helvetica-Bold", fontSize=9.5, leading=12, textColor=colors.white),
    "hz": ParagraphStyle("hz", fontName="Helvetica-Bold", fontSize=9.5, leading=12, textColor=INK),
    "hzx": ParagraphStyle("hzx", fontName="Helvetica-Bold", fontSize=9.5, leading=12, textColor=EXCL_INK),
    "ct": ParagraphStyle("ct", fontName="Helvetica", fontSize=8.5, leading=11, textColor=INK_DIM),
    "ctx": ParagraphStyle("ctx", fontName="Helvetica", fontSize=8.5, leading=11, textColor=EXCL_INK),
    "src": ParagraphStyle("src", fontName="Courier", fontSize=7, leading=9, textColor=colors.HexColor("#8b99a8")),
    "tag": ParagraphStyle("tag", fontName="Courier-Bold", fontSize=7, leading=9, textColor=colors.HexColor("#5f6b77")),
    "badge": ParagraphStyle("badge", fontName="Helvetica-Bold", fontSize=8.5, leading=10, textColor=colors.white, alignment=TA_CENTER),
    "chip": ParagraphStyle("chip", fontName="Helvetica-Bold", fontSize=7.5, leading=9, textColor=colors.white, alignment=TA_CENTER),
    "body": ParagraphStyle("body", fontName="Helvetica", fontSize=8.5, leading=11.5, textColor=INK),
    "erp_h": ParagraphStyle("erp_h", fontName="Helvetica-Bold", fontSize=9, leading=12, textColor=RED_DARK),
    "empty": ParagraphStyle("empty", fontName="Helvetica-Oblique", fontSize=8.5, leading=11, textColor=INK_DIM, alignment=TA_CENTER),
    "sig": ParagraphStyle("sig", fontName="Helvetica", fontSize=7.5, leading=9, textColor=INK_DIM),
}


def P(text, style):
    return Paragraph(escape(str(text or "")).replace("\n", "<br/>"), S[style])


def _badge(lv, faded=False):
    col = colors.HexColor("#b8c0c8") if faded else LV.get(lv, colors.HexColor("#c7ccd1"))
    t = Table([[P(lv or "-", "badge")]], colWidths=[9 * mm], rowHeights=[5.2 * mm])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), col), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                           ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                           ("TOPPADDING", (0, 0), (-1, -1), 1), ("BOTTOMPADDING", (0, 0), (-1, -1), 1)]))
    return t


def _bar(text, width):
    t = Table([[P(text.upper(), "h3")]], colWidths=[width])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), BLUE_DEEP), ("LEFTPADDING", (0, 0), (-1, -1), 7),
                           ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4)]))
    return t


def _card(h, excluded, width):
    title = f"<strike>{escape(h['hz'])}</strike>" if excluded else escape(h["hz"])
    resid = Table([[P("Residual risk after controls", "ct"), _badge(h["rd"], excluded)]], colWidths=[46 * mm, 10 * mm], hAlign="LEFT")
    resid.setStyle(TableStyle([("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0), ("TOPPADDING", (0, 0), (-1, -1), 0),
                               ("BOTTOMPADDING", (0, 0), (-1, -1), 0), ("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
    left = [Paragraph(title, S["hzx" if excluded else "hz"]), Spacer(1, 2), P(h["ct"], "ctx" if excluded else "ct"), Spacer(1, 2), resid, Spacer(1, 2),
            P(f"{h['id']} · {h['src']} · Responsible: {h['rp'] or '-'}", "src")]
    if h["ppe"]:
        left.append(P("PPE: " + "; ".join(h["ppe"]), "src"))
    if excluded:
        left += [Spacer(1, 2), P("REVIEWED AND EXCLUDED BY ASSESSOR AS NOT APPLICABLE", "tag")]
    t = Table([[left, _badge(h["lv"], excluded)]], colWidths=[width - 14 * mm, 14 * mm])
    t.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#aab5c0") if excluded else LINE),
                           ("BACKGROUND", (0, 0), (-1, -1), EXCL_BG if excluded else colors.white), ("VALIGN", (0, 0), (-1, -1), "TOP"),
                           ("LEFTPADDING", (0, 0), (-1, -1), 7), ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                           ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5)]))
    return t


def _chips(hazards, excluded_ids):
    inc = [h for h in hazards if h["uid"] not in excluded_ids]
    c = {k: sum(h["lv"] == k for h in inc) for k in LEVEL_ORDER}
    cells, cols, styles = [P(f"{len(inc)} HAZARDS", "chip")], [26 * mm], [("BACKGROUND", (0, 0), (0, 0), BLUE_DEEP)]
    for k in "EHMLN":
        if c[k]:
            cells.append(P(f"{c[k]} {LEVEL_NAME[k]}", "chip"))
            cols.append(28 * mm)
            styles.append(("BACKGROUND", (len(cells) - 1, 0), (len(cells) - 1, 0), LV[k]))
    if len(hazards) - len(inc):
        cells.append(P(f"{len(hazards) - len(inc)} EXCLUDED", "chip"))
        cols.append(26 * mm)
        styles.append(("BACKGROUND", (len(cells) - 1, 0), (len(cells) - 1, 0), colors.HexColor("#8c98a4")))
    t = Table([cells], colWidths=cols, hAlign="LEFT")
    t.setStyle(TableStyle(styles + [("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                                    ("LINEAFTER", (0, 0), (-2, -1), 3, colors.white)]))
    return t


class _NumberedCanvas(rl_canvas.Canvas):
    def __init__(self, *a, footer="", **kw):
        super().__init__(*a, **kw)
        self._saved, self._footer = [], footer

    def showPage(self):
        self._saved.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        n = len(self._saved)
        for st in self._saved:
            self.__dict__.update(st)
            w, _ = A4
            self.setStrokeColor(RED)
            self.setLineWidth(1.2)
            self.line(14 * mm, 12 * mm, w - 14 * mm, 12 * mm)
            self.setFont("Helvetica", 7)
            self.setFillColor(INK_DIM)
            self.drawString(14 * mm, 8 * mm, self._footer)
            self.drawRightString(w - 14 * mm, 8 * mm, f"Page {self._pageNumber} of {n}")
            super().showPage()
        super().save()


def _banner(top, sub, W):
    b = Table([[P(top, "company")], [P(sub, "form")]], colWidths=[W])
    b.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), BLUE_DEEP), ("TOPPADDING", (0, 0), (-1, 0), 9),
                           ("BOTTOMPADDING", (0, -1), (-1, -1), 9), ("LINEBELOW", (0, -1), (-1, -1), 2.5, RED)]))
    return b


def _kv(rows, W, kw=42):
    t = Table([[P(k, "k"), P(v, "v")] for k, v in rows], colWidths=[kw * mm, W - kw * mm])
    t.setStyle(TableStyle([("LINEBELOW", (0, 0), (-1, -1), 0.4, LINE), ("VALIGN", (0, 0), (-1, -1), "TOP"),
                           ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3), ("LEFTPADDING", (0, 0), (-1, -1), 2)]))
    return t


def build_pdf(a: dict) -> bytes:
    buf = io.BytesIO()
    W = A4[0] - 28 * mm
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=14 * mm, rightMargin=14 * mm, topMargin=12 * mm, bottomMargin=18 * mm,
                            title=f"Risk Assessment {a['serial']}", author=a.get("assessed_by", ""), subject=a["bu"])
    story = [_banner(a["company"], a.get("form_title") or "RISK ASSESSMENT FORM", W), Spacer(1, 6)]
    if "draft" in (a.get("register_status") or "").lower():
        warn = Table([[P(f"Register status: {a['register_status']}. Hazards must be validated by the business unit HSE lead.", "body")]], colWidths=[W])
        warn.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#fff8e6")), ("LINEBEFORE", (0, 0), (0, -1), 3, colors.HexColor("#d9a441")),
                                  ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4)]))
        story += [warn, Spacer(1, 5)]
    story += [_kv(a["header"], W), Spacer(1, 7), _chips(a["hazards"], a["excluded"]), Spacer(1, 6)]
    for n, cat in enumerate(a["categories"], 1):
        rows = [h for h in a["hazards"] if h["cat"] == cat]
        bar = _bar(f"{n}. {cat}", W)
        if not rows:
            e = Table([[P("No hazards in this category for the current selection.", "empty")]], colWidths=[W])
            e.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), PAPER_DIM)]))
            story += [KeepTogether([bar, Spacer(1, 3), e]), Spacer(1, 6)]
            continue
        cards = [_card(h, h["uid"] in a["excluded"], W) for h in rows]
        story.append(KeepTogether([bar, Spacer(1, 3), cards[0]]))
        for c in cards[1:]:
            story += [Spacer(1, 3), c]
        story.append(Spacer(1, 7))
    inc = [h for h in a["hazards"] if h["uid"] not in a["excluded"]]
    ppe = list(dict.fromkeys(p for h in inc for p in h["ppe"]))
    pbox = Table([[P("; ".join(ppe) if ppe else "No PPE listed for the included hazards.", "body")]], colWidths=[W])
    pbox.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), PAPER_DIM), ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5)]))
    story += [KeepTogether([_bar("PPE Required (compiled from included hazards)", W), Spacer(1, 3), pbox]), Spacer(1, 7)]
    erp = Table([[[P("Emergency Response Plan", "erp_h")] + [P(x, "body") for x in a["erp"]]]], colWidths=[W])
    erp.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), BLUE_LIGHT), ("LINEBEFORE", (0, 0), (0, -1), 3.5, RED),
                             ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6), ("LEFTPADDING", (0, 0), (-1, -1), 8)]))
    story += [erp, Spacer(1, 8)]
    half = W / 2 - 3 * mm
    sig = lambda k, v: [Table([[P(k, "k"), P(v or "-", "v")]], colWidths=[36 * mm, half - 36 * mm]), Spacer(1, 16),
                        Table([[P("Signature / Date", "sig")]], colWidths=[half], style=[("LINEABOVE", (0, 0), (-1, 0), 0.6, INK_DIM)])]
    auth = Table([[sig("Assessed By", a["assessed_by"]), sig("Reviewed / Approved By", a["reviewed_by"])]], colWidths=[W / 2, W / 2])
    auth.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0)]))
    story += [KeepTogether([_bar("Authorization", W), Spacer(1, 4), auth]), Spacer(1, 8),
              P(f"Generated {a['generated']} · Engine v{ENGINE_VERSION} · Register {a.get('register_source', '')} · fingerprint {a['fingerprint']} · "
                f"Every hazard is quoted verbatim from the {a['bu']} register (row ID shown).", "src")]
    footer = f"Assessment No. {a['serial']} · {a['bu']} · Register {a['fingerprint']}"
    doc.build(story, canvasmaker=lambda *x, **k: _NumberedCanvas(*x, footer=footer, **k))
    return buf.getvalue()


def build_register_request_pdf(r: dict) -> bytes:
    buf = io.BytesIO()
    W = A4[0] - 28 * mm
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=14 * mm, rightMargin=14 * mm, topMargin=12 * mm, bottomMargin=18 * mm,
                            title="Risk Register Update Request", subject=r["bu"])
    alert = Table([[[P("Risk assessments cannot be generated for this business unit", "erp_h"),
                     P("The Risk Assessment Generator takes every hazard, control measure and PPE item from the business unit's own approved "
                       "risk register. No usable register is available for this business unit, so no assessment can be produced until the "
                       "register owner uploads or updates it.", "body")]]], colWidths=[W])
    alert.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#fbe9e7")), ("LINEBEFORE", (0, 0), (0, -1), 3.5, RED),
                               ("TOPPADDING", (0, 0), (-1, -1), 7), ("BOTTOMPADDING", (0, 0), (-1, -1), 7), ("LEFTPADDING", (0, 0), (-1, -1), 8)]))
    steps = ["1. Download the blank register template from the app (same structure as the Okpella cement register).",
             "2. Populate Locations, JobTags, EquipmentTypes, Equipment, ActivityHazards and EquipmentHazards. Settings, Lists, TaskPresets, "
             "ToolRecognition, InferenceRules and Synonyms are recommended.",
             "3. Have the register reviewed and approved by the business unit HSE lead.",
             "4. Upload the approved workbook on the app's Register admin tab (app administrator access required)."]
    story = [_banner(r["bu"].upper(), "RISK REGISTER UPDATE REQUIRED", W), Spacer(1, 8), alert, Spacer(1, 8), _kv(r["rows"], W, 48), Spacer(1, 8),
             _bar("Action required by the register owner", W), Spacer(1, 4)] + [P(s, "body") for s in steps]
    doc.build(story, canvasmaker=lambda *x, **k: _NumberedCanvas(*x, footer=f"Register update request · {r['bu']} · {r['when']}", **k))
    return buf.getvalue()
