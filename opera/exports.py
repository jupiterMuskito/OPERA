from __future__ import annotations

import io
from html import escape
from typing import Any

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from . import operational, storage


def csv_bytes(frame: pd.DataFrame) -> bytes:
    return frame.to_csv(index=False, encoding="utf-8", lineterminator="\n").encode("utf-8")


def excel_bytes(sheets: dict[str, pd.DataFrame] | pd.DataFrame, masks: dict[str, pd.DataFrame] | None = None) -> bytes:
    frames = {"Data": sheets} if isinstance(sheets, pd.DataFrame) else sheets
    out = io.BytesIO()
    with pd.ExcelWriter(out, engine="openpyxl") as writer:
        writer.book.properties.creator = "OPERA-X"
        writer.book.properties.lastModifiedBy = "OPERA-X"
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
            mask = (masks or {}).get(name)
            if mask is not None:
                for row_number, (_, flags) in enumerate(mask.reindex(columns=frame.columns).iterrows(), start=2):
                    for column_number, flagged in enumerate(flags, start=1):
                        if bool(flagged):
                            cell = ws.cell(row=row_number, column=column_number)
                            cell.fill = cell.fill.copy(fill_type="solid", fgColor="FBE5E5")
                            cell.font = cell.font.copy(color="9F1F2A", bold=True)
    return out.getvalue()


def pdf_bytes(title: str, frame: pd.DataFrame, subtitle: str = "", target_mask: pd.DataFrame | None = None) -> bytes:
    out = io.BytesIO()
    page = landscape(A4) if len(frame.columns) > 4 else A4
    doc = SimpleDocTemplate(out, pagesize=page, leftMargin=10 * mm, rightMargin=10 * mm, topMargin=10 * mm, bottomMargin=12 * mm,
                            title=title, author="OPERA-X")
    styles = getSampleStyleSheet()
    story: list[Any] = [Paragraph(title, styles["Title"])]
    if subtitle:
        story += [Paragraph(subtitle, styles["BodyText"]), Spacer(1, 5)]
    view = frame.head(250).fillna("").astype(str)
    # Split very wide frames into readable column groups. Paragraph cells wrap
    # long content instead of allowing text to overlap adjacent columns.
    max_columns = 7 if page == landscape(A4) else 4
    columns = list(view.columns)
    groups = [columns[index:index + max_columns] for index in range(0, len(columns), max_columns)] or [[]]
    body_style = styles["BodyText"].clone("TableBody")
    body_style.fontName = "Helvetica"
    body_style.fontSize = 6.2
    body_style.leading = 7.4
    header_style = styles["BodyText"].clone("TableHeader")
    header_style.fontName = "Helvetica-Bold"
    header_style.textColor = colors.white
    header_style.fontSize = 6.4
    header_style.leading = 7.4
    width = page[0] - 20 * mm
    for number, group in enumerate(groups, start=1):
        if number > 1:
            story += [PageBreak(), Paragraph(f"{title} — Columns {number}", styles["Heading2"]), Spacer(1, 4)]
        segment = view[group]
        data = [[Paragraph(escape(str(column)), header_style) for column in group]]
        data += [[Paragraph(escape(str(value)).replace("\n", "<br/>"), body_style) for value in row] for row in segment.values.tolist()]
        table = Table(data, colWidths=[width / max(1, len(group))] * max(1, len(group)), repeatRows=1, hAlign="LEFT")
        commands = [("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#123A73")), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                                   ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                                   ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#D7E3EE")), ("VALIGN", (0, 0), (-1, -1), "TOP"),
                                   ("LEFTPADDING", (0, 0), (-1, -1), 3), ("RIGHTPADDING", (0, 0), (-1, -1), 3),
                                   ("TOPPADDING", (0, 0), (-1, -1), 2.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
                                   ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F2F6FC")])]
        if target_mask is not None:
            for row_number, row_index in enumerate(segment.index, start=1):
                for column_number, column in enumerate(group):
                    if column in target_mask.columns and bool(target_mask.at[row_index, column]):
                        commands += [("BACKGROUND", (column_number, row_number), (column_number, row_number), colors.HexColor("#FBE5E5")),
                                     ("TEXTCOLOR", (column_number, row_number), (column_number, row_number), colors.HexColor("#9F1F2A")),
                                     ("FONTNAME", (column_number, row_number), (column_number, row_number), "Helvetica-Bold")]
        table.setStyle(TableStyle(commands))
        story.append(table)
    if len(frame) > 250:
        story += [Spacer(1, 5), Paragraph(f"PDF preview limited to 250 of {len(frame)} rows; use Excel or CSV for the complete export.", styles["Italic"])]
    doc.build(story)
    return out.getvalue()


def lesson_pdf_bytes(title: str, metadata: dict[str, Any], lesson: str) -> bytes:
    """Create a readable single-lesson PDF with wrapped text."""
    out = io.BytesIO()
    doc = SimpleDocTemplate(out, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm, topMargin=16 * mm, bottomMargin=16 * mm,
                            title=title, author="OPERA-X")
    styles = getSampleStyleSheet()
    story: list[Any] = [Paragraph(escape(title), styles["Title"]), Spacer(1, 8)]
    for label, value in metadata.items():
        if str(value).strip():
            story.append(Paragraph(f"<b>{escape(str(label))}:</b> {escape(str(value))}", styles["BodyText"]))
            story.append(Spacer(1, 3))
    story += [Spacer(1, 8), Paragraph("Lesson", styles["Heading2"])]
    for paragraph in str(lesson).splitlines() or [""]:
        story += [Paragraph(escape(paragraph) or "&nbsp;", styles["BodyText"]), Spacer(1, 5)]
    doc.build(story)
    return out.getvalue()


def build_export(fmt: str, title: str, frame: pd.DataFrame, bu: str, user: str, details: dict[str, Any] | None = None) -> tuple[bytes, str, str]:
    fmt = fmt.lower()
    input_registry = storage.registry(bu)
    calculated_registry = storage.read_csv(storage.bu_dir(bu) / "calculated_fields.csv")
    mask = operational.out_of_target_mask(frame, input_registry, calculated_registry)
    if fmt == "excel":
        data, ext, mime = excel_bytes(frame, {"Data": mask}), "xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    elif fmt == "pdf":
        data, ext, mime = pdf_bytes(title, frame, target_mask=mask), "pdf", "application/pdf"
    else:
        data, ext, mime = csv_bytes(frame), "csv", "text/csv"
    storage.audit(bu, user, "export_prepared", {"title": title, "format": fmt, "rows": len(frame), **(details or {})})
    return data, ext, mime
