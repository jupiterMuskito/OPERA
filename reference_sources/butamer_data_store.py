from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]

# ----------------------------------
# FILES
# ----------------------------------

KPI_FILE = ROOT / "data/processed/analysis/butamer_kpi_dataset.csv"
KPI_UNIT = "Butamer"
DCS_FILE = ROOT / "data/processed/dcs/butamer_master_dataset.csv"

PARAMETER_MAPPING_FILE = ROOT / "config/parameter_mapping.csv"
OPERATING_MODES_FILE = ROOT / "config/operating_modes.csv"
OPERATING_LIMITS_FILE = ROOT / "config/operating_limits.csv"
VERIFICATION_LIMITS_FILE = ROOT / "config/verification_limits.csv"

SAMPLE_DIR = ROOT / "data/sample"

HIERARCHY_FILE = SAMPLE_DIR / "master_hierarchy.csv"
ROUNDS_FILE = SAMPLE_DIR / "operator_rounds.csv"
SCHEDULE_FILE = SAMPLE_DIR / "measurement_schedule.csv"
CHECKLIST_FILE = SAMPLE_DIR / "equipment_checklists.csv"
CHECKLIST_RECORDS_FILE = SAMPLE_DIR / "checklist_records.csv"
TAG_REFERENCE_FILE = SAMPLE_DIR / "tag_reference.csv"
LAB_FILE = SAMPLE_DIR / "laboratory_results.csv"
DRAGER_FILE = SAMPLE_DIR / "drager_tests.csv"
SIMULATED_DCS_FILE = SAMPLE_DIR / "dcs_simulated_values.csv"
INVESTIGATION_FILE = SAMPLE_DIR / "investigation_history.csv"
EQUIPMENT_FILE = SAMPLE_DIR / "equipment_reference.csv"
SOP_FILE = SAMPLE_DIR / "sop_library.csv"
GUIDE_FILE = SAMPLE_DIR / "troubleshooting_guide.csv"
LESSONS_FILE = SAMPLE_DIR / "lessons_learned.csv"

NORMAL_MODE = "Normal Operation"

# ----------------------------------
# LOADING
# ----------------------------------

def load_csv(path, dates=False):

    if not path.exists():
        return pd.DataFrame()

    df = pd.read_csv(path)

    if dates and not df.empty and "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"])

    return df


def load_kpis():

    df = load_csv(KPI_FILE, dates=True)

    if not df.empty:
        df["operating_mode"] = df["date"].apply(operating_mode)

    return df


def append_rows(path, rows):

    new_rows = pd.DataFrame(rows)

    if path.exists():
        new_rows = pd.concat(
            [pd.read_csv(path), new_rows],
            ignore_index=True
        )

    new_rows.to_csv(path, index=False)

# ----------------------------------
# OPERATING MODE
# ----------------------------------

def operating_mode(date):

    modes = load_csv(OPERATING_MODES_FILE)
    day = pd.Timestamp(date)

    for _, row in modes.iterrows():

        if pd.Timestamp(row["start_date"]) <= day <= pd.Timestamp(row["end_date"]):
            return row["mode"]

    return NORMAL_MODE


def mode_note(date):

    modes = load_csv(OPERATING_MODES_FILE)
    day = pd.Timestamp(date)

    for _, row in modes.iterrows():

        if pd.Timestamp(row["start_date"]) <= day <= pd.Timestamp(row["end_date"]):
            return f"{row['mode']}: {row['notes']} ({row['source']})."

    return ""

# ----------------------------------
# TAGS AND DCS VALUES
# ----------------------------------

def tag_for(display_name):

    mapping = load_csv(PARAMETER_MAPPING_FILE)

    matches = mapping.loc[
        mapping["display_name"] == display_name.removesuffix("_feed"),
        "tag"
    ]

    return matches.iloc[0] if not matches.empty else ""


def dcs_value(tag, date):

    dcs = load_csv(DCS_FILE)

    if dcs.empty or not tag:
        return None

    day = pd.to_datetime(dcs["timestamp"]).dt.date == pd.Timestamp(date).date()
    values = dcs.loc[day & (dcs["instrument_tag"] == tag), "value"]

    return values.mean() if not values.empty else None

# ----------------------------------
# STATUS RULES
# ----------------------------------

def limit_status(value, limit):

    if pd.isna(value):
        return "No Data"

    if value < limit.get("low_action", float("-inf")) or value > limit.get("high_action", float("inf")):
        return "Action Required"

    if value < limit.get("low_monitor", float("-inf")) or value > limit.get("high_monitor", float("inf")):
        return "Monitor"

    return "Normal"


REACTOR_TAGS = {
    "A": {"reactor_inlet_temp": "TI2504", "reactor_outlet_temp": "TI2509"},
    "B": {"reactor_inlet_temp": "TI2510", "reactor_outlet_temp": "TI2515"},
}


def operating_limits():

    limits = load_csv(OPERATING_LIMITS_FILE)

    return [
        row.dropna().to_dict()
        for _, row in limits.iterrows()
    ]


def caustic_strength(date):

    lab = load_csv(LAB_FILE, dates=True)

    if lab.empty:
        return None

    rows = lab[
        (lab["date"].dt.date == pd.Timestamp(date).date())
        & (lab["parameter"] == "Caustic Strength")
    ]

    return rows.iloc[0]["value"] if not rows.empty else None


def health_summary(selected):

    rows = []

    for limit in operating_limits():

        if limit["data_source"] == "kpi":
            value = selected[limit["key"]]
            tag = (
                REACTOR_TAGS.get(selected["online_reactor"], {}).get(limit["key"])
                or tag_for(limit["key"])
            )
            source = "DCS"

        elif limit["data_source"] == "dcs":
            value = dcs_value(limit["key"], selected["date"])
            tag = limit["key"]
            source = "DCS"

        else:
            value = caustic_strength(selected["date"])
            tag = ""
            source = "Simulated"

        if value is None:
            value = float("nan")

        rows.append(
            {
                "Section": limit["section"],
                "Parameter": limit["label"],
                "Tag": tag,
                "Value": round(value, 3),
                "Unit": limit.get("unit", ""),
                "Status": limit_status(value, limit),
                "Source": source,
            }
        )

    return pd.DataFrame(rows)

# ----------------------------------
# FIELD VS DCS VERIFICATION
# ----------------------------------

def dcs_reference(equipment, parameter, date):

    tags = load_csv(TAG_REFERENCE_FILE)

    row = tags[
        (tags["equipment"] == equipment)
        & (tags["parameter"] == parameter)
    ]

    if not row.empty and pd.notna(row.iloc[0]["dcs_tag"]):

        tag = row.iloc[0]["dcs_tag"]
        value = dcs_value(tag, date)

        if value is not None:
            return value, f"DCS {tag} (daily average)"

    simulated = load_csv(SIMULATED_DCS_FILE, dates=True)

    if not simulated.empty:

        match = simulated[
            (simulated["date"].dt.date == pd.Timestamp(date).date())
            & (simulated["equipment"] == equipment)
            & (simulated["parameter"] == parameter)
        ]

        if not match.empty:
            return match.iloc[0]["dcs_value"], "Simulated"

    return None, "No DCS reference"


def verify_reading(equipment, parameter, date, field_value):

    dcs, source = dcs_reference(equipment, parameter, date)

    result = {
        "dcs_value": dcs,
        "difference": None,
        "status": "Not Verified",
        "source": source,
    }

    if dcs is None:
        return result

    difference = abs(field_value - dcs)
    result["difference"] = difference

    limits = load_csv(VERIFICATION_LIMITS_FILE)

    limit = limits[
        (limits["equipment"] == equipment)
        & (limits["parameter"] == parameter)
    ]

    if limit.empty:
        result["status"] = "No Limit Set"

    elif difference >= limit.iloc[0]["critical_difference"]:
        result["status"] = "Critical"

    elif difference >= limit.iloc[0]["monitor_difference"]:
        result["status"] = "Monitor"

    else:
        result["status"] = "Normal"

    return result


def verification_table(round_records):

    rows = []

    for _, record in round_records.iterrows():

        check = verify_reading(
            record["equipment"],
            record["parameter"],
            record["date"],
            record["field_value"]
        )

        if check["dcs_value"] is None:
            continue

        rows.append(
            {
                "Equipment": record["equipment"],
                "Parameter": record["parameter"],
                "Field": record["field_value"],
                "DCS": round(check["dcs_value"], 2),
                "Difference": round(check["difference"], 2),
                "Status": check["status"],
                "DCS Source": check["source"],
            }
        )

    return pd.DataFrame(rows)

# ----------------------------------
# ANALYTICS
# ----------------------------------

def relationship_summary(df, columns, target="product_ic4_ratio"):

    rows = []

    for label, column in columns.items():

        pair = df[[column, target]].dropna()

        if len(pair) < 3 or pair[column].nunique() < 2:
            continue

        r = pair[column].corr(pair[target])

        if abs(r) < 0.4:
            strength = "Weak"
        elif abs(r) < 0.7:
            strength = "Moderate"
        else:
            strength = "Strong"

        at_ceiling = (pair[column] >= pair[column].max() * 0.99).mean()

        rows.append(
            {
                "Condition": label,
                "Days": len(pair),
                "Correlation (r)": round(r, 2),
                "Strength": strength,
                "Note": (
                    f"At its maximum reading on {at_ceiling:.0%} of days. Check the instrument range."
                    if at_ceiling > 0.5
                    else ""
                ),
            }
        )

    summary = pd.DataFrame(rows)

    if summary.empty:
        return summary

    return summary.sort_values(
        "Correlation (r)",
        key=abs,
        ascending=False
    )
