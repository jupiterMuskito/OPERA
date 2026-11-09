from __future__ import annotations

import sys
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
from openpyxl import load_workbook

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from opera.auth import hash_password
from opera.storage import BASE_COLUMNS, SOURCES, atomic_write_csv
from opera.dashboard import default_templates

DATA = ROOT / "data"
RNG = np.random.default_rng(20261108)

BUS = [
    {"id": "cement", "name": "Cement", "active": "true", "placeholder": "false", "register_file": "registers/OKPELLA_Master_Workbook_v8.xlsx", "notes": "Okpella hierarchy cloned to Obajana and Ibese"},
    {"id": "refinery", "name": "Refinery", "active": "true", "placeholder": "false", "register_file": "registers/DANGOTE_REFINERY_Master_Workbook_v1.xlsx", "notes": "Includes Butamer"},
    {"id": "fertilizer", "name": "Fertilizer", "active": "true", "placeholder": "false", "register_file": "registers/DANGOTE_FERTILISER_Master_Workbook_v1.xlsx", "notes": ""},
    {"id": "nascon", "name": "NASCON", "active": "true", "placeholder": "false", "register_file": "", "notes": "Salt and Sugar sections"},
] + [{"id": f"bu{i}", "name": f"BU{i}", "active": "false", "placeholder": "true", "register_file": "", "notes": "Inactive placeholder"} for i in range(5, 10)]

EQUIPMENT = {
    "refinery": [("REF-CRUDE-PUMP-01", "Main Crude Charge Pump", "Refinery Complex", "CDU", "Pump"),
                 ("REF-CDU-HEATER-01", "Crude Charge Heater", "Refinery Complex", "CDU", "Heater"),
                 ("REF-BUT-RX-01", "Butamer Reactor 1", "Refinery Complex", "Butamer Unit", "Reactor"),
                 ("REF-BUT-RX-02", "Butamer Reactor 2", "Refinery Complex", "Butamer Unit", "Reactor"),
                 ("REF-BUT-DRY-01", "Butamer Feed Dryer", "Refinery Complex", "Butamer Unit", "Dryer"),
                 ("REF-BUT-STAB-01", "Butamer Stabiliser", "Refinery Complex", "Butamer Unit", "Column"),
                 ("REF-BUT-HTR-01", "Butamer Charge Heater", "Refinery Complex", "Butamer Unit", "Heater"),
                 ("REF-CCR-COMP-01", "Recycle Gas Compressor", "Refinery Complex", "CCR", "Compressor")],
    "fertilizer": [("FER-REF-01", "Primary Reformer", "Fertilizer Plant", "Ammonia Unit", "Furnace"),
                   ("FER-COMP-01", "Synthesis Gas Compressor", "Fertilizer Plant", "Ammonia Unit", "Compressor"),
                   ("FER-UREA-RX-01", "Urea Reactor", "Fertilizer Plant", "Urea Unit", "Reactor"),
                   ("FER-STRIP-01", "Urea Stripper", "Fertilizer Plant", "Urea Unit", "Stripper"),
                   ("FER-GRAN-01", "Urea Granulator", "Fertilizer Plant", "Granulation", "Granulator"),
                   ("FER-BAG-01", "Bagging Line 1", "Fertilizer Plant", "Bagging", "Bagging Machine")],
    "nascon": [("NAS-SALT-EVAP-01", "Salt Evaporator 1", "NASCON Plant", "Salt", "Evaporator"),
              ("NAS-SALT-DRY-01", "Salt Dryer 1", "NASCON Plant", "Salt", "Dryer"),
              ("NAS-SALT-PACK-01", "Salt Packing Line 1", "NASCON Plant", "Salt", "Packing Line"),
              ("NAS-SUGAR-MILL-01", "Sugar Mill 1", "NASCON Plant", "Sugar", "Mill"),
              ("NAS-SUGAR-EVAP-01", "Sugar Evaporator 1", "NASCON Plant", "Sugar", "Evaporator"),
              ("NAS-SUGAR-CENT-01", "Sugar Centrifuge 1", "NASCON Plant", "Sugar", "Centrifuge"),
              ("NAS-SUGAR-PACK-01", "Sugar Packing Line 1", "NASCON Plant", "Sugar", "Packing Line")],
}

FIELD_NAMES = {
"cement": {
"DCS": [("Kiln Feed Rate","t/h",180,520,420),("Kiln Speed","rpm",2.0,4.5,3.6),("Kiln Inlet Oxygen","%",0.5,5.0,2.5),("Preheater Outlet Temperature","°C",280,420,350),("Calciner Temperature","°C",780,930,870),("Kiln Torque","%",30,95,65),("Cooler Grate Speed","spm",2,12,7),("Clinker Cooler Outlet Temperature","°C",70,180,110),("Raw Mill Differential Pressure","mbar",20,95,55),("Raw Mill Outlet Temperature","°C",70,115,90),("Coal Mill Outlet Temperature","°C",55,85,72),("Cement Mill Main Drive Power","kW",2500,7500,5600),("Separator Speed","rpm",700,1500,1100),("Kiln Bag Filter Differential Pressure","mbar",5,35,18),("Primary Crusher Motor Current","A",80,420,260),("Cooler Fan Pressure","mbar",25,95,60),("Kiln Main Drive Current","A",120,460,320),("Kiln ID Fan Speed","rpm",450,1100,820),("Clinker Silo Level","%",10,95,70),("Packing Rate","t/h",40,180,130)],
"Lab": [("Raw Meal LSF","ratio",88,105,96),("Raw Meal Silica Modulus","ratio",2.0,3.2,2.5),("Raw Meal Alumina Modulus","ratio",1.0,2.2,1.6),("Raw Meal Residue 90 µm","%",8,22,14),("Raw Meal Moisture","%",0.1,2.5,0.8),("Clinker Free Lime","%",0.4,3.0,1.4),("Clinker C3S","%",45,70,58),("Clinker C2S","%",8,28,17),("Clinker C3A","%",4,14,8),("Clinker MgO","%",0.5,5.0,2.5),("Clinker SO3","%",0.1,2.0,0.9),("Cement Blaine","cm²/g",2800,4500,3600),("Cement Residue 45 µm","%",2,16,8),("Initial Setting Time","min",90,220,150),("Final Setting Time","min",150,360,240),("2-Day Compressive Strength","MPa",15,38,26),("28-Day Compressive Strength","MPa",38,68,52),("Loss on Ignition","%",0.5,5.0,2.5),("Chloride","%",0.01,0.10,0.05),("Insoluble Residue","%",0.1,2.5,1.0)],
"Field": [("Kiln Inlet Shell Temperature","°C",180,420,300),("Kiln Outlet Shell Temperature","°C",180,420,310),("Kiln Girth Gear Vibration","mm/s",0.2,7.0,3.0),("Kiln Main Drive Bearing Temperature","°C",35,85,60),("ID Fan Bearing Temperature","°C",35,90,62),("Cooler Drive Bearing Temperature","°C",30,85,58),("Raw Mill Gearbox Vibration","mm/s",0.2,7.0,2.8),("Raw Mill Bearing Temperature","°C",35,90,60),("Coal Mill CO","ppm",0,180,45),("Coal Mill Bearing Temperature","°C",35,90,58),("Cement Mill Inlet Temperature","°C",60,125,90),("Cement Mill Outlet Temperature","°C",75,125,105),("Separator Bearing Temperature","°C",35,90,58),("Crusher Bearing Vibration","mm/s",0.2,8.0,3.0),("Crusher Bearing Temperature","°C",35,90,60),("Clinker Conveyor Belt Drift","mm",0,35,8),("Bucket Elevator Boot Temperature","°C",30,90,55),("Packing Machine Air Pressure","bar",4.5,8.0,6.2),("Dust Collector Hopper Temperature","°C",25,95,55),("Silo Roof Dust Level","mg/m³",0,10,3)]},
"refinery": {
"DCS": [("Butamer Feed Flow","m³/h",120,520,350),("Butamer Reactor Inlet Temperature","°C",120,210,170),("Butamer Reactor Outlet Temperature","°C",130,230,185),("Butamer Reactor Pressure","bar",15,35,25),("Hydrogen to Hydrocarbon Ratio","mol/mol",0.5,3.5,1.8),("Stabiliser Top Temperature","°C",40,95,65),("Stabiliser Bottom Temperature","°C",120,210,165),("Stabiliser Pressure","bar",5,18,11),("Recycle Gas Flow","Nm³/h",2000,12000,7000),("Charge Heater Outlet Temperature","°C",130,220,180),("Feed Dryer Differential Pressure","bar",0.0,1.8,0.6),("Product iC4 Ratio","%",45,95,78),("Feed iC4 Ratio","%",10,55,30),("Reactor Differential Temperature","°C",0,35,15),("Reactor Level","%",20,85,55),("Compressor Discharge Pressure","bar",20,45,32),("Compressor Vibration","mm/s",0.2,7.0,2.5),("Fuel Gas Flow","Nm³/h",200,1800,950),("Flare Header Pressure","bar",0.01,1.5,0.4),("Butamer Product Flow","m³/h",100,500,330)],
"Lab": [("Feed iC4","%",10,55,30),("Product iC4","%",45,95,78),("Feed nC4","%",30,85,62),("Product nC4","%",2,45,18),("Feed C3","%",0,8,2),("Product C3","%",0,8,2),("Feed C5+","%",0,5,1),("Product C5+","%",0,5,1),("Feed Sulfur","mg/kg",0,10,2),("Product Sulfur","mg/kg",0,10,2),("Feed Water","mg/kg",0,80,25),("Product Water","mg/kg",0,80,20),("Chloride","mg/kg",0,5,1),("Caustic Strength","wt%",5,25,15),("Hydrogen Purity","%",85,100,96),("Octane Number","RON",80,96,90),("Vapour Pressure","kPa",25,90,55),("Density at 15°C","kg/m³",540,650,590),("Copper Strip Corrosion","rating",0,2,1),("Product Yield","%",85,100,96)],
"Field": [("Reactor Skin Temperature","°C",100,250,180),("Charge Heater Tube Skin Temperature","°C",300,680,500),("Reactor Inlet Local Pressure","bar",15,35,25),("Reactor Outlet Local Pressure","bar",15,35,24),("Compressor DE Bearing Temperature","°C",35,90,62),("Compressor NDE Bearing Temperature","°C",35,90,60),("Compressor Axial Vibration","mm/s",0.2,7,2.5),("Feed Dryer Bed Temperature","°C",20,90,55),("Stabiliser Reboiler Outlet Temperature","°C",120,220,175),("Stabiliser Reflux Drum Level","%",20,85,55),("Pump Seal Temperature","°C",30,95,60),("Pump Vibration","mm/s",0.2,8,3),("Control Valve Position Check","%",0,100,50),("Drier Moisture Indicator","ppm",0,100,20),("Hydrogen Detector Reading","%LEL",0,20,2),("Area H2S Reading","ppm",0,10,1),("Local Flow Indicator","m³/h",100,520,350),("Local Temperature Indicator","°C",120,230,180),("Local Pressure Indicator","bar",15,35,25),("Dräger Hydrochloric Acid","ppm",0,5,0.5)]},
"fertilizer": {
"DCS": [("Natural Gas Feed Flow","Nm³/h",50000,140000,100000),("Primary Reformer Outlet Temperature","°C",700,900,820),("Secondary Reformer Outlet Temperature","°C",850,1100,980),("Synthesis Gas Compressor Discharge Pressure","bar",120,180,155),("Ammonia Converter Inlet Temperature","°C",300,450,380),("Ammonia Converter Outlet Temperature","°C",430,560,500),("Ammonia Production Rate","t/d",1200,3300,2500),("CO2 Compressor Discharge Pressure","bar",120,180,155),("Urea Reactor Pressure","bar",130,175,155),("Urea Reactor Temperature","°C",165,205,185),("Stripper Top Temperature","°C",150,205,180),("Carbamate Condenser Temperature","°C",140,195,170),("Granulator Bed Temperature","°C",90,120,105),("Granulator Feed Rate","t/h",40,180,130),("Fluid Bed Cooler Outlet Temperature","°C",35,65,48),("Ammonia Storage Level","%",15,90,60),("Cooling Water Supply Temperature","°C",25,38,31),("Steam Header Pressure","bar",35,125,80),("Plant Power Demand","MW",20,85,55),("Bagging Rate","t/h",30,180,120)],
"Lab": [("Ammonia Product Purity","%",99.0,100,99.8),("Ammonia Water Content","%",0,0.5,0.2),("Urea Nitrogen Content","%",45.5,46.8,46.3),("Urea Moisture","%",0.1,0.8,0.4),("Urea Biuret","%",0.3,1.5,0.9),("Urea Formaldehyde","%",0.1,0.8,0.4),("Granule Size 2–4 mm","%",85,100,95),("Crushing Strength","kg/granule",1.5,4.5,3),("Bulk Density","kg/m³",700,820,760),("Cooling Water pH","pH",6.5,9.0,7.8),("Boiler Water Conductivity","µS/cm",0,50,15),("Boiler Water Silica","mg/L",0,0.5,0.1),("Condensate Iron","mg/L",0,0.2,0.05),("Natural Gas Methane","%",80,100,92),("Natural Gas Sulfur","mg/Nm³",0,15,3),("Process Condensate Ammonia","mg/L",0,100,20),("Prill Temperature","°C",35,65,48),("Product Dust","%",0,1.0,0.3),("Oil in Ammonia","mg/kg",0,10,2),("CO2 Purity","%",95,100,99)],
"Field": [("Primary Reformer Tube Skin Temperature","°C",650,980,850),("Reformer Burner Flame Quality","index",0,10,8),("Syngas Compressor Bearing Temperature","°C",35,90,62),("Syngas Compressor Vibration","mm/s",0.2,7,2.5),("Ammonia Pump Seal Temperature","°C",30,90,58),("Ammonia Area Detector","ppm",0,25,2),("Urea Reactor Local Pressure","bar",130,175,155),("Stripper Vibration","mm/s",0.2,7,2.5),("Granulator Vibration","mm/s",0.2,8,3),("Granulator Bed Visual Level","%",20,85,55),("Fluid Bed Fan Bearing Temperature","°C",35,90,60),("Conveyor Belt Drift","mm",0,35,8),("Bucket Elevator Bearing Temperature","°C",35,90,58),("Bagging Air Pressure","bar",4.5,8,6.2),("Dust Collector Differential Pressure","mbar",5,35,18),("Cooling Tower Fan Vibration","mm/s",0.2,8,3),("Steam Trap Temperature","°C",80,190,130),("Valve Packing Leak Index","index",0,10,1),("Housekeeping Dust Level","mg/m³",0,10,3),("Product Storage Temperature","°C",25,55,38)]},
"nascon": {
"DCS": [("Salt Brine Feed Flow","m³/h",20,180,100),("Salt Evaporator Temperature","°C",70,125,105),("Salt Evaporator Vacuum","kPa abs",10,65,30),("Salt Dryer Inlet Temperature","°C",100,220,160),("Salt Dryer Outlet Temperature","°C",45,95,70),("Salt Packing Rate","t/h",5,45,28),("Sugar Cane Feed Rate","t/h",80,420,280),("Mill Extraction","%",85,99,95),("Mixed Juice Flow","m³/h",50,350,220),("Clarifier Temperature","°C",85,110,98),("Sugar Evaporator Brix","°Bx",45,72,62),("Vacuum Pan Pressure","kPa abs",8,35,18),("Massecuite Temperature","°C",55,85,70),("Centrifuge Speed","rpm",700,1500,1100),("Sugar Dryer Outlet Temperature","°C",35,65,48),("Sugar Packing Rate","t/h",10,90,60),("Boiler Steam Pressure","bar",15,55,35),("Boiler Steam Temperature","°C",250,460,380),("Power Demand","MW",2,35,18),("Warehouse Silo Level","%",10,95,65)],
"Lab": [("Salt NaCl Purity","%",97,100,99.2),("Salt Moisture","%",0.0,1.0,0.3),("Salt Insoluble Matter","%",0,0.5,0.1),("Salt Iodine","mg/kg",30,70,50),("Salt Particle Size Pass","%",85,100,95),("Brine Density","kg/m³",1100,1250,1180),("Brine Calcium","mg/L",0,100,30),("Brine Magnesium","mg/L",0,80,20),("Sugar Polarisation","°Z",98,100,99.5),("Sugar Moisture","%",0,0.15,0.05),("Sugar Colour","IU",20,300,120),("Sugar Ash","%",0,0.15,0.05),("Reducing Sugars","%",0,0.1,0.03),("Cane Brix","°Bx",12,24,18),("Cane Pol","%",10,22,16),("Bagasse Moisture","%",42,55,48),("Mixed Juice Purity","%",75,92,85),("Final Molasses Brix","°Bx",75,90,83),("Final Molasses Purity","%",25,45,35),("Process Water pH","pH",6.5,9,7.5)],
"Field": [("Salt Evaporator Body Temperature","°C",70,130,105),("Salt Dryer Bearing Temperature","°C",35,90,60),("Salt Dryer Vibration","mm/s",0.2,8,3),("Salt Conveyor Belt Drift","mm",0,35,8),("Salt Packing Air Pressure","bar",4.5,8,6.2),("Mill Roller Bearing Temperature","°C",35,95,65),("Mill Gearbox Vibration","mm/s",0.2,8,3),("Juice Pump Vibration","mm/s",0.2,8,3),("Clarifier Mud Level","%",10,85,45),("Evaporator Tube Condition Index","index",0,10,8),("Vacuum Pan Local Pressure","kPa abs",8,35,18),("Centrifuge Bearing Temperature","°C",35,90,60),("Centrifuge Vibration","mm/s",0.2,8,3),("Sugar Dryer Bearing Temperature","°C",35,90,58),("Sugar Conveyor Belt Drift","mm",0,35,8),("Sugar Packing Air Pressure","bar",4.5,8,6.2),("Boiler Feed Pump Vibration","mm/s",0.2,8,3),("Boiler Drum Local Level","%",20,80,50),("Bagasse Conveyor Condition","index",0,10,8),("Warehouse Dust Level","mg/m³",0,10,3)]}
}

CALC_NAMES = {
    "cement": ["Average Kiln Feed Rate","Peak Kiln Feed Rate","Minimum Kiln Speed","Clinker Quality Index","Kiln Field-DCS Deviation","Thermal Stability Index","Cement Strength Index","Packing Performance"],
    "refinery": ["Average Butamer Feed","Peak Reactor Temperature","Minimum Reactor Pressure","iC4 Improvement","Field-DCS Feed Deviation","Reactor Temperature Rise","Product Quality Index","Butamer Throughput Performance"],
    "fertilizer": ["Average Gas Feed","Peak Reformer Temperature","Minimum Urea Pressure","Product Quality Index","Field-DCS Pressure Deviation","Converter Temperature Rise","Granulation Quality Index","Bagging Performance"],
    "nascon": ["Average Salt Brine Feed","Peak Dryer Temperature","Minimum Evaporator Vacuum","Sugar Quality Index","Field-DCS Evaporator Deviation","Mill Extraction Index","Salt Quality Index","Packing Performance"],
}


def cement_equipment(register: Path) -> list[tuple[str, str, str, str, str]]:
    wb = load_workbook(register, read_only=True, data_only=True)
    ws = wb["Equipment"]
    rows = list(ws.iter_rows(values_only=True))
    headers = [str(x or "").strip() for x in rows[0]]
    out = []
    for row in rows[1:]:
        rec = {h: str(row[i] or "").strip() for i, h in enumerate(headers) if h}
        if not rec.get("EquipmentID") or not rec.get("EquipmentName"):
            continue
        section = rec.get("LocationArea1") or ("All process areas" if rec.get("LocationScope") == "All process areas" else "Plant-wide")
        out.append((rec["EquipmentID"], rec["EquipmentName"], "Okpella Cement Plant", section, rec.get("EquipmentType") or "Equipment"))
    wb.close()
    clones = []
    for prefix, plant in [("OBJ", "Obajana Cement Plant"), ("IBE", "Ibese Cement Plant")]:
        clones.extend([(f"{prefix}-{equipment_id}", name, plant, section, equipment_type) for equipment_id, name, _, section, equipment_type in out])
    return out + clones


def seed() -> None:
    (DATA / "shared").mkdir(parents=True, exist_ok=True)
    atomic_write_csv(DATA / "shared" / "business_units.csv", pd.DataFrame(BUS))
    pwd = "ChangeMe!2026"
    users = [
        {"username":"superadmin","display_name":"OPERA Super Admin","password_hash":hash_password(pwd, "00112233445566778899aabbccddeeff"),"role":"Super Admin","business_units":"*","active":"true","must_change_password":"true","failed_attempts":"0","lock_until":""},
        {"username":"buadmin","display_name":"BU Administrator","password_hash":hash_password(pwd, "11112222333344445555666677778888"),"role":"BU Admin","business_units":"cement;refinery;fertilizer;nascon","active":"true","must_change_password":"false","failed_attempts":"0","lock_until":""},
        {"username":"operator","display_name":"Shift Operator","password_hash":hash_password(pwd, "abcdefabcdefabcdefabcdefabcdefab"),"role":"Operator","business_units":"cement;refinery;fertilizer;nascon","active":"true","must_change_password":"false","failed_attempts":"0","lock_until":""},
        {"username":"viewer","display_name":"Read Only Viewer","password_hash":hash_password(pwd, "fedcbafedcbafedcbafedcbafedcbafe"),"role":"Viewer","business_units":"cement;refinery;fertilizer;nascon","active":"true","must_change_password":"false","failed_attempts":"0","lock_until":""},
    ]
    atomic_write_csv(DATA / "shared" / "users.csv", pd.DataFrame(users))
    cement_reg = ROOT / "registers" / "OKPELLA_Master_Workbook_v8.xlsx"
    EQUIPMENT["cement"] = cement_equipment(cement_reg)
    for bu in [x["id"] for x in BUS]:
        folder = DATA / "business_units" / bu
        (folder / "inputs").mkdir(parents=True, exist_ok=True)
        if bu in EQUIPMENT:
            named = EQUIPMENT[bu]
        else:
            named = [(f"{bu.upper()}-CONFIG-001", "Configure equipment", f"{bu.upper()} Plant", "Configure unit/section", "Equipment")]
        rows = [{"equipment_id":i,"equipment_name":n,"plant":p,"unit_section":u,"equipment_type":t,"section_tag":u if bu=="nascon" else "","active":"true","placeholder":"false"} for i,n,p,u,t in named]
        prefix = {"cement":"CEM","refinery":"REF","fertilizer":"FER","nascon":"NAS"}.get(bu, bu.upper())
        rows += [{"equipment_id":f"{prefix}-SPARE-{i:03d}","equipment_name":f"Spare equipment {i:03d}","plant":named[0][2],"unit_section":"Unassigned","equipment_type":"Placeholder","section_tag":"","active":"false","placeholder":"true"} for i in range(1,501)]
        atomic_write_csv(folder / "equipment.csv", pd.DataFrame(rows))
        reg_rows=[]
        for source,pfx in SOURCES.items():
            definitions = FIELD_NAMES.get(bu, {}).get(source, [])
            for i in range(1,1001):
                field_id=f"{pfx}{i}"
                if i <= len(definitions):
                    name,uom,low,high,target=definitions[i-1]
                    active="true"
                else:
                    name,uom,low,high,target=f"{source} placeholder field {i}","UOM?","","",""
                    active="false"
                reg_rows.append({"field_id":field_id,"source":source,"field_name":name,"uom":uom,"min_value":low,"max_value":high,
                                 "data_format":"0.00","target":target,"target_direction":"High","jump_limit":((float(high)-float(low))*0.4 if low!="" else ""),"active":active})
        atomic_write_csv(folder / "fields.csv", pd.DataFrame(reg_rows))
        first = rows[0]
        for source,pfx in SOURCES.items():
            cols=BASE_COLUMNS+[f"{pfx}{i}" for i in range(1,1001)]
            samples=[]
            if bu in FIELD_NAMES and source in FIELD_NAMES[bu]:
                defs=FIELD_NAMES[bu][source]
                periods=30 if source=="Lab" else 120
                for j in range(periods):
                    day=date(2026,10,10)+timedelta(days=(j if source=="Lab" else j//4))
                    hour=6 if source=="Lab" else [0,6,12,18][j%4]
                    rec={"Date":day.isoformat(),"Time":f"{hour:02d}:00","Business unit":bu,"Plant":first["plant"],"Unit/Section":first["unit_section"],
                         "Equipment":first["equipment_id"],"Recorded by":"sample-generator","Recorded at":"2026-11-08T12:00:00+00:00"}
                    for i,(_,_,low,high,target) in enumerate(defs,1):
                        sigma=(high-low)/18
                        value=float(np.clip(RNG.normal(target,sigma),low,high))
                        if j==5 and i in (1,7): value=high+(high-low)*0.15
                        rec[f"{pfx}{i}"]=round(value,3)
                    samples.append(rec)
            atomic_write_csv(folder / "inputs" / f"{source.lower()}.csv", pd.DataFrame(samples,columns=cols))
        calc=[]
        if bu in CALC_NAMES:
            formulas=["[DP1]","[DP2]","[DP3]","([L1]+[L2])/2","ABS([F1]-[DP1])","ABS([DP3]-[DP2])","([L6]+[L7])/2","[DP20]"]
            for i,(name,formula) in enumerate(zip(CALC_NAMES[bu],formulas),1):
                calc.append({"field_id":f"CF{i}","field_name":name,"formula":formula,"uom":"Derived","aggregation":["Average","Maximum","Minimum"][i%3],
                             "daily_target":FIELD_NAMES[bu]["DCS"][min(i-1,19)][4],"period_target":FIELD_NAMES[bu]["DCS"][min(i-1,19)][4],
                             "target_direction":"High","status":"active","evaluation_order":i,"mtd_aggregation":["Average","Maximum","Minimum"][i%3],
                             "ytd_aggregation":["Average","Maximum","Minimum"][i%3],"dashboard":"true","dashboard_group":"Operations","chart":"line"})
        atomic_write_csv(folder / "calculated_fields.csv", pd.DataFrame(calc,columns=["field_id","field_name","formula","uom","aggregation","daily_target","period_target","target_direction","status","evaluation_order","mtd_aggregation","ytd_aggregation","dashboard","dashboard_group","chart"]))
        for name,columns in {
            "events.csv":["event_id","timestamp","event_date","event_time","event_types","format","plant","unit_section","equipment","title","details","picture_path","reported_by","notification_sent","field_update_sent","field_update_ids"],
            "flags.csv":["timestamp","date","time","field_id","value","flag_type","message","status"],
            "lessons.csv":["lesson_id","timestamp","event_id","unit_section","lesson","entered_by"],
            "notifications.csv":["id","timestamp","recipient","level","message","created_by","read_by"],
            "audit_log.csv":["timestamp","business_unit","user","action","details"],
            "risk_assessments.csv":["serial","timestamp","preset","job_type","location","equipment","hazard_count","assessed_by"],
        }.items():
            atomic_write_csv(folder/name,pd.DataFrame(columns=columns))
        if bu in FIELD_NAMES:
            sample_flags = [
                {"timestamp":"2026-10-11T12:00:00+00:00","date":"2026-10-11","time":"06:00","field_id":"DP1","value":FIELD_NAMES[bu]["DCS"][0][3] * 1.15,"flag_type":"Out of range","message":"Deliberate sample value above configured maximum","status":"Open"},
                {"timestamp":"2026-10-11T12:00:00+00:00","date":"2026-10-11","time":"06:00","field_id":"L7","value":FIELD_NAMES[bu]["Lab"][6][3] * 1.15,"flag_type":"Out of range","message":"Deliberate sample value above configured maximum","status":"Open"},
                {"timestamp":"2026-10-11T12:00:00+00:00","date":"2026-10-11","time":"06:00","field_id":"F1","value":FIELD_NAMES[bu]["Field"][0][3] * 1.15,"flag_type":"Out of range","message":"Deliberate sample value above configured maximum","status":"Open"},
            ]
            atomic_write_csv(folder/"flags.csv",pd.DataFrame(sample_flags))
        (folder/"presets.json").write_text("{}",encoding="utf-8")
        (folder/"pipeline.json").write_text('{"url":"","token_secret_name":""}',encoding="utf-8")
        (folder/"dashboard_templates.json").write_text(__import__("json").dumps(default_templates(), indent=2), encoding="utf-8")
        hierarchy = {
            "plants": sorted({row["plant"] for row in rows if row["plant"]}),
            "units": sorted({row["unit_section"] for row in rows if row["unit_section"] and row["unit_section"] != "Unassigned"}),
            "equipment_types": sorted({row["equipment_type"] for row in rows if row["equipment_type"] and row["equipment_type"] != "Placeholder"}),
        }
        (folder/"equipment_validation.json").write_text(__import__("json").dumps(hierarchy, indent=2), encoding="utf-8")

if __name__ == "__main__":
    seed()
    print("OPERA seed data created")
