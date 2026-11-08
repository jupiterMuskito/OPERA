"""Register loader and deterministic hazard engine (multi-business-unit).

Every hazard returned is copied verbatim from the selected business unit's register - nothing is generated, and nothing
is shared between business units. Categories, motion/status options and synonyms are all read from the register.
"""
from __future__ import annotations

import hashlib
import io
import json
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from openpyxl import Workbook, load_workbook

ENGINE_VERSION = "5.2"
LEVEL_ORDER = {"E": 0, "H": 1, "M": 2, "L": 3, "N": 4}
LEVEL_NAME = {"E": "EXTREME", "H": "HIGH", "M": "MODERATE", "L": "LOW", "N": "NEGLIGIBLE"}
# Fallback order only, used when a register's Lists sheet has no HazardCategory column.
DEFAULT_CAT_ORDER = ["Job Related Hazard", "Job Location Related Hazard", "Equipment and Material Related Hazard"]
OTHER_LOC_NAME = "Other Area (User should Specify)"
REQUIRED_SHEETS = ["JobTags", "EquipmentTypes", "Equipment", "ActivityHazards", "EquipmentHazards"]


# ----------------------------------------------------------------------------- loading
def _s(v) -> str:
    if v is None:
        return ""
    if isinstance(v, float) and v.is_integer():
        v = int(v)
    return str(v).strip()


def _sheet_rows(ws, key_header: str) -> list[dict]:
    rows = list(ws.iter_rows(values_only=True))
    hdr_idx = next((i for i, r in enumerate(rows[:6]) if any(_s(c) == key_header for c in r)), None)
    if hdr_idx is None:
        return []
    headers = [_s(c) for c in rows[hdr_idx]]
    out = []
    for r in rows[hdr_idx + 1:]:
        if r is None or all(_s(c) == "" for c in r):
            continue
        out.append({h: _s(r[j]) if j < len(r) else "" for j, h in enumerate(headers) if h})
    return out


def _list_columns(ws) -> dict[str, list[str]]:
    rows = list(ws.iter_rows(values_only=True))
    for i, r in enumerate(rows[:6]):
        hdr = [_s(c) for c in r]
        if "HazardCategory" in hdr or "Category" in hdr or "MotionOption" in hdr:
            return {h: [_s(x[j]) for x in rows[i + 1:] if j < len(x) and _s(x[j])] for j, h in enumerate(hdr) if h}
    return {}


def _multi(row: dict, prefix: str, n: int) -> list[str]:
    return [row.get(f"{prefix}{i}", "") for i in range(1, n + 1) if row.get(f"{prefix}{i}", "")]


@dataclass
class Register:
    path: str
    locations: list[dict] = field(default_factory=list)
    job_tags: list[dict] = field(default_factory=list)
    equipment_types: list[str] = field(default_factory=list)
    equipment: list[dict] = field(default_factory=list)
    activity_hazards: list[dict] = field(default_factory=list)
    equipment_hazards: list[dict] = field(default_factory=list)
    presets: list[dict] = field(default_factory=list)
    tools: list[dict] = field(default_factory=list)
    rules: list[dict] = field(default_factory=list)
    synonyms: list[dict] = field(default_factory=list)
    settings: dict = field(default_factory=dict)
    categories: list[str] = field(default_factory=list)
    motions: list[str] = field(default_factory=lambda: ["Running", "Static"])
    statuses: list[str] = field(default_factory=lambda: ["Operational", "Shutdown/Isolated"])
    fingerprint: str = ""
    warnings: list[str] = field(default_factory=list)

    @property
    def tag_names(self) -> list[str]:
        return [t["t"] for t in self.job_tags]

    @property
    def hazard_count(self) -> int:
        return len(self.activity_hazards) + len(self.equipment_hazards)

    def loc_type(self, name: str) -> str:
        return next((l["type"] for l in self.locations if l["n"] == name), "")

    def equip(self, name: str) -> dict | None:
        return next((e for e in self.equipment if e["n"] == name), None)

    def available(self, e: dict, loc: str) -> bool:
        if not loc or loc == OTHER_LOC_NAME or loc not in {l["n"] for l in self.locations}:
            return True
        scope = e.get("scope") or "All areas"
        if scope == "All areas":
            return True
        if scope == "All process areas":
            return self.loc_type(loc) == "Process"
        return loc in e.get("locs", [])


class RegisterError(Exception):
    pass


def load_register(path: str | Path) -> Register:
    p = Path(path)
    if not p.exists():
        raise RegisterError(f"Register file not found: {p.name}")
    try:
        wb = load_workbook(p, read_only=True, data_only=True)
    except Exception as exc:
        raise RegisterError(f"The file could not be opened as an Excel workbook ({exc.__class__.__name__}).") from exc
    missing = [s for s in REQUIRED_SHEETS if s not in wb.sheetnames]
    if missing:
        wb.close()
        raise RegisterError("Missing required sheet(s): " + ", ".join(missing))

    R = Register(path=str(p))
    if "Locations" in wb.sheetnames:
        R.locations = [{"id": r.get("LocationID", ""), "n": r["LocationArea"], "type": r.get("AreaType") or "Other"}
                       for r in _sheet_rows(wb["Locations"], "LocationArea") if r.get("LocationArea")]
    R.job_tags = [{"id": r.get("JobTagID", ""), "t": r["JobTag"], "c": r.get("Category") or "Other"}
                  for r in _sheet_rows(wb["JobTags"], "JobTag") if r.get("JobTag")]
    R.equipment_types = [r["EquipmentType"] for r in _sheet_rows(wb["EquipmentTypes"], "EquipmentType") if r.get("EquipmentType")]
    R.equipment = [{"id": r.get("EquipmentID", ""), "n": r["EquipmentName"], "t": r.get("EquipmentType", ""),
                    "scope": r.get("LocationScope") or "All areas", "locs": _multi(r, "LocationArea", 20)}
                   for r in _sheet_rows(wb["Equipment"], "EquipmentName") if r.get("EquipmentName")]

    def hz(rows, idcol, keycol):
        out = []
        for r in rows:
            if not (r.get(keycol) and r.get("Hazard")):
                continue
            ppe = _multi(r, "PPE", 12) or [x.strip() for x in r.get("RequiredPPE", "").split(",") if x.strip()]
            out.append({"id": r.get(idcol, ""), "key": r[keycol], "cat": r.get("HazardCategory", ""), "hz": r["Hazard"],
                        "lv": r.get("LevelOfRisk", ""), "ct": r.get("ControlMeasures", ""), "rd": r.get("ReducedLevelOfRisk", ""),
                        "rp": r.get("ResponsiblePerson", ""), "ppe": [x for x in ppe if x and x != "N/A"],
                        "mo": r.get("AppliesWhenMotion") or "Any", "st": r.get("AppliesWhenStatus") or "Any"})
        return out

    R.activity_hazards = hz(_sheet_rows(wb["ActivityHazards"], "Hazard"), "ActivityHazardID", "JobTag")
    R.equipment_hazards = hz(_sheet_rows(wb["EquipmentHazards"], "Hazard"), "EquipmentHazardID", "EquipmentType")
    if "TaskPresets" in wb.sheetnames:
        R.presets = [{"id": r.get("PresetID", ""), "n": r["PresetName"], "cat": r.get("PresetCategory") or "Other",
                      "d": r.get("Description", ""), "tags": _multi(r, "JobTag", 20), "et": r.get("EquipmentType", ""),
                      "mo": r.get("EquipmentMotion") or "", "st": r.get("EquipmentStatus") or "",
                      "ref": r.get("EquipmentRef", ""), "loc": r.get("LocationArea", "")}
                     for r in _sheet_rows(wb["TaskPresets"], "PresetName") if r.get("PresetName")]
    if "ToolRecognition" in wb.sheetnames:
        R.tools = [{"p": r["ToolPhrase"].lower(), "c": r.get("ToolCategory", ""), "tags": _multi(r, "JobTag", 8)}
                   for r in _sheet_rows(wb["ToolRecognition"], "ToolPhrase") if r.get("ToolPhrase")]
    if "InferenceRules" in wb.sheetnames:
        for r in _sheet_rows(wb["InferenceRules"], "TriggerRegex"):
            if not r.get("TriggerRegex"):
                continue
            try:
                trig, also = re.compile(r["TriggerRegex"], re.I), re.compile(r.get("AlsoRequiresRegex") or ".", re.I)
            except re.error:
                R.warnings.append(f"InferenceRules {r.get('RuleID', '?')}: invalid pattern ignored")
                continue
            R.rules.append({"id": r.get("RuleID", ""), "trig": trig, "also": also, "label": r.get("Label", ""), "tags": _multi(r, "JobTag", 6)})
    if "Synonyms" in wb.sheetnames:
        R.synonyms = [{"p": r["Phrase"].lower(), "t": r.get("JobTag", "")}
                      for r in _sheet_rows(wb["Synonyms"], "Phrase") if r.get("Phrase") and r.get("JobTag")]
    lists = _list_columns(wb["Lists"]) if "Lists" in wb.sheetnames else {}
    R.motions = [x for x in lists.get("MotionOption", []) if x != "Any"] or R.motions
    R.statuses = [x for x in lists.get("StatusOption", []) if x != "Any"] or R.statuses
    cats = list(dict.fromkeys(lists.get("HazardCategory", [])))
    used = list(dict.fromkeys(h["cat"] for h in R.activity_hazards + R.equipment_hazards if h["cat"]))
    if not cats:
        cats = [c for c in DEFAULT_CAT_ORDER if c in used]
    R.categories = cats + [c for c in used if c not in cats]      # never drop a hazard whose category is missing from Lists
    if "Settings" in wb.sheetnames:
        R.settings = {r["Key"]: r.get("Value", "") for r in _sheet_rows(wb["Settings"], "Key") if r.get("Key")}
    wb.close()

    if not R.activity_hazards and not R.equipment_hazards:
        raise RegisterError("The register contains no hazard rows.")
    if not R.job_tags:
        raise RegisterError("The JobTags sheet has no activities.")
    R.fingerprint = fingerprint(R)
    R.warnings += check_register(R)
    return R


def load_register_bytes(data: bytes, tmp_dir: Path, name: str = "upload.xlsx") -> Register:
    tmp_dir.mkdir(parents=True, exist_ok=True)
    p = tmp_dir / name
    p.write_bytes(data)
    return load_register(p)


def fingerprint(R: Register) -> str:
    row = lambda h: [h["id"], h["key"], h["cat"], h["hz"], h["lv"], h["ct"], h["rd"], h["rp"], h["ppe"], h["mo"], h["st"]]
    payload = {"ah": [row(h) for h in R.activity_hazards], "eh": [row(h) for h in R.equipment_hazards],
               "tags": [t["t"] for t in R.job_tags], "rules": [[r["id"], r["trig"].pattern, r["also"].pattern, r["tags"]] for r in R.rules],
               "tools": [[t["p"], t["tags"]] for t in R.tools], "syn": [[x["p"], x["t"]] for x in R.synonyms], "cats": R.categories}
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()[:8].upper()


def check_register(R: Register) -> list[str]:
    w = []
    tags, types, locs = set(R.tag_names), set(R.equipment_types), {l["n"] for l in R.locations}
    w += [f"{h['id'] or '?'}: activity '{h['key']}' is not on the JobTags sheet" for h in R.activity_hazards if h["key"] not in tags]
    w += [f"{h['id'] or '?'}: equipment type '{h['key']}' is not on the EquipmentTypes sheet" for h in R.equipment_hazards if h["key"] not in types]
    w += [f"{h['id'] or '?'}: risk level '{h['lv']}' / '{h['rd']}' not in E/H/M/L/N" for h in R.activity_hazards + R.equipment_hazards
          if h["lv"] not in LEVEL_ORDER or (h["rd"] and h["rd"] not in LEVEL_ORDER)]
    w += [f"{h['id'] or '?'}: no hazard category" for h in R.activity_hazards + R.equipment_hazards if not h["cat"]]
    ids = [h["id"] for h in R.activity_hazards + R.equipment_hazards if h["id"]]
    w += [f"Hazard ID '{i}' is used more than once" for i in sorted({i for i in ids if ids.count(i) > 1})]
    for e in R.equipment:
        if e["t"] not in types:
            w.append(f"{e['id'] or e['n']}: equipment type '{e['t']}' is not on the EquipmentTypes sheet")
        w += [f"{e['id'] or e['n']}: location '{a}' is not on the Locations sheet" for a in e["locs"] if locs and a not in locs]
    for p in R.presets:
        w += [f"Preset '{p['n']}': activity '{t}' not found" for t in p["tags"] if t not in tags]
    for r in R.rules:
        w += [f"Rule {r['id']}: activity '{t}' not found" for t in r["tags"] if t not in tags]
    w += [f"Synonym '{x['p']}': activity '{x['t']}' not found" for x in R.synonyms if x["t"] not in tags]
    return w


def compare_registers(old: Register | None, new: Register) -> dict:
    """What changes if `new` replaces `old` - compared on hazard row ID (falls back to hazard text when IDs are blank)."""
    key = lambda h: h["id"] or ("TXT:" + h["key"] + "|" + h["hz"])
    def idx(R):
        return {key(h): h for h in (R.activity_hazards + R.equipment_hazards)} if R else {}
    o, n = idx(old), idx(new)
    fields = [("hz", "Hazard"), ("lv", "Level"), ("ct", "Controls"), ("rd", "Residual"), ("rp", "Responsible"), ("ppe", "PPE"), ("key", "Linked to")]
    changed = []
    for k in sorted(set(o) & set(n)):
        diffs = [lbl for f, lbl in fields if o[k][f] != n[k][f]]
        if diffs:
            changed.append({"ID": k, "Hazard": n[k]["hz"], "Changed": ", ".join(diffs)})
    return {"added": [{"ID": k, "Linked to": n[k]["key"], "Hazard": n[k]["hz"], "Level": n[k]["lv"]} for k in sorted(set(n) - set(o))],
            "removed": [{"ID": k, "Linked to": o[k]["key"], "Hazard": o[k]["hz"], "Level": o[k]["lv"]} for k in sorted(set(o) - set(n))],
            "changed": changed,
            "counts": {"activities": (len(old.job_tags) if old else 0, len(new.job_tags)),
                       "hazards": (old.hazard_count if old else 0, new.hazard_count),
                       "equipment": (len(old.equipment) if old else 0, len(new.equipment)),
                       "locations": (len(old.locations) if old else 0, len(new.locations)),
                       "presets": (len(old.presets) if old else 0, len(new.presets))}}


# ----------------------------------------------------------------------------- hazard engine
def collect_hazards(R: Register, tags: list[str], equip_type: str | None, motion: str, status: str) -> list[dict]:
    sel = set(tags)
    ok_m = lambda v: v in ("Any", "") or v == motion
    ok_s = lambda v: v in ("Any", "") or v == status
    out = [{**h, "src": "Activity: " + h["key"]} for h in R.activity_hazards if h["key"] in sel and ok_m(h["mo"]) and ok_s(h["st"])]
    if equip_type and equip_type in R.equipment_types:
        out += [{**h, "src": "Equipment: " + h["key"]} for h in R.equipment_hazards if h["key"] == equip_type and ok_m(h["mo"]) and ok_s(h["st"])]
    seen: dict[str, dict] = {}
    for h in out:
        k = h["hz"].lower().strip()
        if k not in seen or LEVEL_ORDER.get(h["lv"], 9) < LEVEL_ORDER.get(seen[k]["lv"], 9):
            seen[k] = h
    res = sorted(seen.values(), key=lambda h: LEVEL_ORDER.get(h["lv"], 9))
    for i, h in enumerate(res):
        h["uid"] = h["id"] or f"X{i:03d}"
    return res


def compile_ppe(hazards: list[dict]) -> list[str]:
    return list(dict.fromkeys(p for h in hazards for p in h["ppe"]))


def counts(hazards: list[dict]) -> dict:
    c = {k: 0 for k in LEVEL_ORDER}
    for h in hazards:
        if h["lv"] in c:
            c[h["lv"]] += 1
    return c


# ----------------------------------------------------------------------------- description helper
GENERIC = set("work working worker the and for with during equipment operation operations use using handling material materials general site "
              "activity activities related area task tasks from into onto near over under while this that will need needs some other person "
              "personnel someone team job around we our are going have has been their they".split())


def _stem(w: str) -> str:
    if len(w) > 6 and w.endswith("ing"):
        return w[:-3]
    if len(w) > 6 and w.endswith("tion"):
        return w[:-4]
    if len(w) > 5 and w.endswith("ed"):
        return w[:-2]
    if len(w) > 4 and w.endswith("s") and not w.endswith("ss"):
        return w[:-1]
    return w


def suggest_from_text(R: Register, text: str) -> dict:
    """Selects activities from THIS register only (names, Synonyms, ToolRecognition, InferenceRules). Never invents hazards."""
    low = (text or "").lower()
    valid = set(R.tag_names)
    reasons: dict[str, str] = {}
    toks = {_stem(t) for t in re.split(r"[^a-z0-9]+", low) if t}
    scored = []
    for t in R.tag_names:
        s = 0
        tl = re.sub(r"\s*\([^)]*\)", "", t.lower()).strip()
        if tl and tl in low:
            s += 10
        for w in re.split(r"[^a-z0-9]+", re.sub(r"\([^)]*\)", "", t.lower())):
            sw = _stem(w)
            if len(w) >= 3 and w not in GENERIC and len(sw) >= 3 and sw not in GENERIC and sw in toks:
                s += 3
        if any(x["t"] == t and x["p"] in low for x in R.synonyms):
            s += 8
        if s >= 6:
            scored.append((s, t))
    for _, t in sorted(scored, reverse=True)[:12]:
        reasons.setdefault(t, "named in the description")
    tools_found = []
    for tool in R.tools:
        if re.search(r"(^|[^a-z])" + re.escape(tool["p"]) + r"($|[^a-z])", low):
            tools_found.append(tool["p"])
            for t in tool["tags"]:
                if t in valid:
                    reasons.setdefault(t, f"tool: {tool['p']}")
    for r in R.rules:
        if r["trig"].search(text or "") and r["also"].search(text or ""):
            for t in r["tags"]:
                if t in valid:
                    reasons.setdefault(t, f"rule {r['id']}: {r['label']}")
    ref, best = None, 0
    for e in R.equipment:
        n = e["n"].lower()
        if n in low:
            ref = e
            break
        ws = [w for w in re.split(r"[^a-z0-9]+", n) if len(w) >= 4 and w not in GENERIC]
        sc = sum(1 for w in ws if w in low)
        if (sc >= 2 or (sc == 1 and len(ws) == 1)) and sc > best:
            ref, best = e, sc
    mo = st = None
    if re.search(r"\b(running|operating|in operation|online|on-?stream)\b", low):
        mo, st = "Running", "Operational"
    if re.search(r"shut\s*down|isolat|stopped|locked\s*out|de-?energi[sz]ed|outage|turnaround", low):
        mo, st = "Static", "Shutdown/Isolated"
    if mo not in R.motions or st not in R.statuses:
        mo = st = None
    return {"tags": list(reasons), "reasons": reasons, "tools": tools_found, "equipment": ref["n"] if ref else None,
            "equipment_type": ref["t"] if ref else None, "motion": mo, "status": st}


# ----------------------------------------------------------------------------- serial number
def area_code(txt: str) -> str:
    stop = {"the", "and", "for", "of", "a", "an", "with", "on", "in", "to"}
    words = [w for w in re.sub(r"[^A-Z0-9 ]", " ", (txt or "").upper()).split() if w.lower() not in stop]
    if not words:
        return "GEN"
    if len(words) >= 3:
        code = words[0][0] + words[1][0] + words[2][0]
    elif len(words) == 2:
        code = words[0][0] + words[1][0] + (words[1][1:2] or words[0][1:2] or "X")
    else:
        cons = re.sub(r"[AEIOU]", "", words[0])
        code = cons[:3] if len(cons) >= 3 else (words[0] + "XXX")[:3]
    return (code + "XXX")[:3].upper()


def make_serial(now: datetime, equip_ref: str, equip_type: str) -> str:
    serial_day = (now.date() - datetime(1899, 12, 30).date()).days
    return f"{serial_day}{now:%H%M%S}{now.microsecond // 10000:02d}{area_code(equip_ref or equip_type)}"


# ----------------------------------------------------------------------------- blank template
def blank_template_bytes(bu_name: str = "") -> bytes:
    wb = Workbook()
    sheets = {
        "ReadMe": ["This workbook will be the only source of hazards for your business unit. Fill in every sheet, keep sheet and column "
                   "names unchanged, then upload it on the app's Register admin tab (or send it to the app administrator)."],
        "Settings": ["Key", "Value"],
        "Lists": ["Category", "HazardCategory", "RiskLevel", "ResponsiblePerson", "PPEItem", "MotionOption", "StatusOption"],
        "Locations": ["LocationID", "LocationCode", "LocationArea", "AreaType", "AddedByReview"],
        "JobTags": ["JobTagID", "JobTag", "Category"],
        "EquipmentTypes": ["EquipmentTypeID", "EquipmentType"],
        "Equipment": ["EquipmentID", "EquipmentName", "EquipmentType", "LocationScope"] + [f"LocationArea{i}" for i in range(1, 11)],
        "ActivityHazards": ["ActivityHazardID", "JobTag", "HazardCategory", "Hazard", "LevelOfRisk", "ControlMeasures", "ReducedLevelOfRisk",
                            "ResponsiblePerson"] + [f"PPE{i}" for i in range(1, 8)] + ["AppliesWhenMotion", "AppliesWhenStatus"],
        "EquipmentHazards": ["EquipmentHazardID", "EquipmentType", "HazardCategory", "Hazard", "LevelOfRisk", "ControlMeasures",
                             "ReducedLevelOfRisk", "ResponsiblePerson"] + [f"PPE{i}" for i in range(1, 8)] + ["AppliesWhenMotion", "AppliesWhenStatus"],
        "TaskPresets": ["PresetID", "PresetName", "PresetCategory", "Description"] + [f"JobTag{i}" for i in range(1, 11)] +
                       ["EquipmentType", "EquipmentMotion", "EquipmentStatus", "EquipmentRef", "LocationArea"],
        "ToolRecognition": ["ToolID", "ToolPhrase", "ToolCategory"] + [f"JobTag{i}" for i in range(1, 6)],
        "InferenceRules": ["RuleID", "TriggerRegex", "AlsoRequiresRegex", "Label", "JobTag1", "JobTag2", "JobTag3"],
        "Synonyms": ["SynonymID", "Phrase", "JobTag"],
    }
    for i, (name, hdr) in enumerate(sheets.items()):
        ws = wb.active if i == 0 else wb.create_sheet(name)
        ws.title = name
        ws.append(hdr)
        for c in ws[1]:
            c.font = c.font.copy(bold=True)
    for k, v in (("BusinessUnit", bu_name), ("CompanyName", ""), ("FormTitle", "RISK ASSESSMENT FORM"), ("RegisterStatus", "DRAFT"),
                 ("ERP1", ""), ("ERP2", ""), ("ERP3", "")):
        wb["Settings"].append([k, v])
    lists = wb["Lists"]
    for row in [["", "Job Related Hazard", "E", "", "", "Any", "Any"], ["", "Job Location Related Hazard", "H", "", "", "Running", "Operational"],
                ["", "Equipment and Material Related Hazard", "M", "", "", "Static", "Shutdown/Isolated"], ["", "", "L"], ["", "", "N"]]:
        lists.append(row)
    bio = io.BytesIO()
    wb.save(bio)
    return bio.getvalue()
