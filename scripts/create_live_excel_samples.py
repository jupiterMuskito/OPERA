#!/usr/bin/env python3
"""Build the three standalone OPERA-X Live Excel sample workbooks."""

from __future__ import annotations

from datetime import date, time
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.worksheet.table import Table, TableStyleInfo

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "reference_sources"
BLUE = "1857C9"
LIGHT_BLUE = "EAF1FC"
WHITE = "FFFFFF"
BORDER = Side(style="thin", color="C9D8EC")

SAMPLES = [
    {
        "number": 1,
        "bu": "refinery",
        "plant": "Refinery Complex",
        "unit": "Butamer Unit",
        "equipment": "REF-BUT-RX-01",
        "equipment_name": "Butamer Reactor 1",
        "fields": [("DP1", "Butamer Feed Flow", "m³/h"), ("DP2", "Butamer Reactor Inlet Temperature", "°C"), ("DP3", "Butamer Reactor Outlet Temperature", "°C"), ("DP4", "Butamer Reactor Pressure", "bar"), ("DP5", "Hydrogen to Hydrocarbon Ratio", "mol/mol")],
        "values": [[360, 176, 188, 26.2, 1.8], [372, 178, 190, 26.5, 1.9], [368, 177, 189, 26.4, 1.85]],
        "filename": "OPERA-X_Live_Excel_1_Refinery_Sample.xlsx",
    },
    {
        "number": 2,
        "bu": "cement",
        "plant": "Okpella Cement Plant",
        "unit": "56 Rotary Kiln and Tertiary Air Duct",
        "equipment": "EQ04",
        "equipment_name": "Rotary Kiln",
        "fields": [("DP1", "Kiln Feed Rate", "t/h"), ("DP2", "Kiln Speed", "rpm"), ("DP3", "Kiln Inlet Oxygen", "%"), ("DP4", "Preheater Outlet Temperature", "°C"), ("DP5", "Calciner Temperature", "°C")],
        "values": [[410, 3.2, 2.1, 354, 872], [418, 3.25, 2.0, 356, 875], [415, 3.22, 2.2, 355, 873]],
        "filename": "OPERA-X_Live_Excel_2_Cement_Sample.xlsx",
    },
    {
        "number": 3,
        "bu": "fertilizer",
        "plant": "Fertilizer Plant",
        "unit": "Urea Unit",
        "equipment": "FER-UREA-RX-01",
        "equipment_name": "Urea Reactor",
        "fields": [("DP7", "Ammonia Production Rate", "t/d"), ("DP8", "CO2 Compressor Discharge Pressure", "bar"), ("DP9", "Urea Reactor Pressure", "bar"), ("DP10", "Urea Reactor Temperature", "°C")],
        "values": [[2750, 151, 158, 184], [2780, 152, 159, 185], [2765, 151.5, 158.5, 184.5]],
        "filename": "OPERA-X_Live_Excel_3_Fertilizer_Sample.xlsx",
    },
]


def apply_font(ws) -> None:
    for row in ws.iter_rows():
        for cell in row:
            cell.font = cell.font.copy(name="Arial")
            cell.alignment = Alignment(vertical="center", wrap_text=cell.alignment.wrap_text)


def build(sample: dict) -> Path:
    wb = Workbook()
    live = wb.active
    live.title = "Live Data"
    headers = ["Date", "Time", "Business unit", "Plant", "Unit/Section", "Equipment"] + [field[0] for field in sample["fields"]]
    live.append(headers)
    for offset, values in enumerate(sample["values"]):
        live.append([date(2026, 11, 25), time(6 + offset, 0), sample["bu"], sample["plant"], sample["unit"], sample["equipment"], *values])
    for cell in live[1]:
        cell.fill = PatternFill("solid", fgColor=BLUE)
        cell.font = Font(name="Arial", bold=True, color=WHITE)
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = Border(bottom=BORDER)
    for row in live.iter_rows(min_row=2):
        row[0].number_format = "yyyy-mm-dd"
        row[1].number_format = "hh:mm"
        for cell in row:
            cell.border = Border(bottom=Border(bottom=BORDER).bottom)
    live.freeze_panes = "A2"
    live.auto_filter.ref = live.dimensions
    live.sheet_view.showGridLines = False
    widths = {"A": 14, "B": 11, "C": 16, "D": 24, "E": 40, "F": 22}
    for column, width in widths.items():
        live.column_dimensions[column].width = width
    for index in range(7, len(headers) + 1):
        live.column_dimensions[live.cell(1, index).column_letter].width = 14
    table = Table(displayName=f"LiveExcel{sample['number']}Data", ref=live.dimensions)
    table.tableStyleInfo = TableStyleInfo(name="TableStyleMedium2", showRowStripes=True, showColumnStripes=False)
    live.add_table(table)

    guide = wb.create_sheet("How to use")
    guide.sheet_view.showGridLines = False
    guide.merge_cells("A1:D1")
    guide["A1"] = f"OPERA-X Live Excel files {sample['number']} — How to use"
    guide["A1"].fill = PatternFill("solid", fgColor=BLUE)
    guide["A1"].font = Font(name="Arial", size=16, bold=True, color=WHITE)
    guide["A1"].alignment = Alignment(vertical="center")
    guide.row_dimensions[1].height = 30
    instructions = [
        ("Purpose", f"Sample server-folder input for BU '{sample['bu']}', {sample['equipment']} — {sample['equipment_name']}."),
        ("Server filename", f"Rename this workbook to live_excel_{sample['number']}.xlsx before uploading to ~/opera_inbox/live_excel/."),
        ("Edit here", "Add new rows only on the 'Live Data' sheet. Keep the column names exactly as supplied."),
        ("Date format", "YYYY-MM-DD (example: 2026-11-25)."),
        ("Time format", "24-hour HH:MM (example: 06:00)."),
        ("New rows", "Use a new Date + Time + Business unit + Plant + Unit/Section + Equipment combination. If that key already exists, changed DP values update the existing Digital Data row."),
        ("Duplicates", "Unchanged rows already imported are skipped automatically."),
        ("Sample data", "The supplied readings are realistic demonstration values, not production measurements."),
    ]
    row = 3
    for label, text in instructions:
        guide.cell(row, 1, label).font = Font(name="Arial", bold=True, color=BLUE)
        guide.cell(row, 2, text).alignment = Alignment(wrap_text=True, vertical="top")
        guide.merge_cells(start_row=row, start_column=2, end_row=row, end_column=4)
        row += 1
    row += 1
    guide.cell(row, 1, "Excel column").value = "Excel column"
    guide.cell(row, 2, "Digital Data field").value = "Digital Data field"
    guide.cell(row, 3, "Unit").value = "Unit"
    guide.cell(row, 4, "Mapping scope").value = "Mapping scope"
    for cell in guide[row]:
        cell.fill = PatternFill("solid", fgColor=BLUE)
        cell.font = Font(name="Arial", bold=True, color=WHITE)
    for field_id, name, uom in sample["fields"]:
        row += 1
        guide.append([]) if guide.max_row < row else None
        guide.cell(row, 1, field_id)
        guide.cell(row, 2, name)
        guide.cell(row, 3, uom)
        guide.cell(row, 4, f"{sample['bu']} / {sample['equipment']}")
        for cell in guide[row]:
            cell.fill = PatternFill("solid", fgColor=LIGHT_BLUE if row % 2 == 0 else WHITE)
    guide.column_dimensions["A"].width = 20
    guide.column_dimensions["B"].width = 44
    guide.column_dimensions["C"].width = 16
    guide.column_dimensions["D"].width = 34
    for r in range(3, guide.max_row + 1):
        guide.row_dimensions[r].height = 30
    guide.freeze_panes = "A3"
    apply_font(live)
    apply_font(guide)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    path = OUTPUT / sample["filename"]
    wb.save(path)
    return path


if __name__ == "__main__":
    for item in SAMPLES:
        print(build(item))
