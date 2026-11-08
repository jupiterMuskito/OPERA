from __future__ import annotations

import io
from typing import Any

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from . import storage


def csv_bytes(frame: pd.DataFrame) -> bytes:
    return frame.to_csv(index=False, encoding="utf-8", lineterminator="\n").encode("utf-8")


def excel_bytes(sheets: dict[str, pd.DataFrame] | pd.DataFrame) -> bytes:
    frames = {"Data": sheets} if isinstance(sheets, pd.DataFrame) else sheets
    out = io.BytesIO()
    with pd.ExcelWriter(out, engine="openpyxl") as writer:
        for name, frame in frames.items():
            frame.to_excel(writer, sheet_name=str(name)[:31], index=False)
            ws = writer.book[str(name)[:31]]
            ws.freeze_panes = "A2"
            ws.auto_filter.ref = ws.dimensions
            for cell in ws[1]:
                cell.font = cell.font.copy(bold=True, name="Arial")
                cell.fill = cell.fill.copy(fill_type="solid", fgColor="D9E8FB")
            for column in ws.columns:
                letter = column[0].column_letter
                ws.column_dimensions[letter].width = min(28, max(11, max(len(str(c.value or "")) for c in column[:100]) + 2))
    return out.getvalue()


def pdf_bytes(title: str, frame: pd.DataFrame, subtitle: str = "") -> bytes:
    out = io.BytesIO()
    page = landscape(A4) if len(frame.columns) > 5 else A4
    doc = SimpleDocTemplate(out, pagesize=page, leftMargin=10 * mm, rightMargin=10 * mm, topMargin=10 * mm, bottomMargin=12 * mm,
                            title=title, author="OPERA")
    styles = getSampleStyleSheet()
    story: list[Any] = [Paragraph(title, styles["Title"])]
    if subtitle:
        story += [Paragraph(subtitle, styles["BodyText"]), Spacer(1, 5)]
    view = frame.head(250).fillna("").astype(str)
    data = [list(view.columns)] + view.values.tolist()
    width = page[0] - 20 * mm
    cols = max(1, len(view.columns))
    table = Table(data, colWidths=[width / cols] * cols, repeatRows=1)
    table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#123A73")), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                               ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"), ("FONTSIZE", (0, 0), (-1, -1), 6.5),
                               ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#D7E3EE")), ("VALIGN", (0, 0), (-1, -1), "TOP"),
                               ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F2F6FC")])]))
    story.append(table)
    if len(frame) > 250:
        story += [Spacer(1, 5), Paragraph(f"PDF preview limited to 250 of {len(frame)} rows; use Excel or CSV for the complete export.", styles["Italic"])]
    doc.build(story)
    return out.getvalue()


def build_export(fmt: str, title: str, frame: pd.DataFrame, bu: str, user: str, details: dict[str, Any] | None = None) -> tuple[bytes, str, str]:
    fmt = fmt.lower()
    if fmt == "excel":
        data, ext, mime = excel_bytes(frame), "xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    elif fmt == "pdf":
        data, ext, mime = pdf_bytes(title, frame), "pdf", "application/pdf"
    else:
        data, ext, mime = csv_bytes(frame), "csv", "text/csv"
    storage.audit(bu, user, "export_prepared", {"title": title, "format": fmt, "rows": len(frame), **(details or {})})
    return data, ext, mime
