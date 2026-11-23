from __future__ import annotations

import re
from typing import Any

import pandas as pd


PLANT = "plant-performance"
PROCESS = "process-performance"
CONDITION = "condition-monitoring"
QUALITY = "quality-compliance"
RELIABILITY = "reliability"

PLACEHOLDER_TEMPLATES = {
    "DCS": [PROCESS],
    "Field": [PROCESS, CONDITION],
    "Lab": [QUALITY],
    "TA": [PROCESS],
    "TB": [PROCESS],
    "TC": [PROCESS],
    "TD": [PROCESS],
    "TE": [PROCESS],
    "TF": [PROCESS],
    "TG": [PROCESS],
}


# Each named input field is deliberately assigned to the process equipment that
# measures or produces it. Terms are matched against the equipment register; a
# SPARE:n term is used only when the required item is absent from that register.
# The runtime source remains field_mappings.xlsx; these rules are one-time seed
# knowledge for a fresh deployment or migration from pre-v3.6.
ENGINEERING_RULES: dict[str, dict[str, dict[str, Any]]] = {
    "cement": {
        "DP1": {"equipment": ["Rotary Kiln"], "templates": [PLANT, PROCESS], "basis": "Kiln feed is the solids throughput entering each rotary kiln.", "confidence": "High"},
        "DP2": {"equipment": ["Rotary Kiln"], "templates": [PROCESS, CONDITION], "basis": "Kiln speed is a rotary-kiln process and drive-loading variable.", "confidence": "High"},
        "DP3": {"equipment": ["Rotary Kiln"], "templates": [PROCESS, QUALITY], "basis": "Kiln inlet oxygen is measured at the kiln inlet and supports combustion and emissions control.", "confidence": "High"},
        "DP4": {"equipment": ["Preheater Tower / Cyclones"], "templates": [PROCESS], "basis": "Preheater outlet temperature is produced and measured in the preheater tower gas/meal circuit.", "confidence": "High"},
        "DP5": {"equipment": ["Calciner"], "templates": [PROCESS], "basis": "Calciner temperature is the principal calciner combustion/process temperature.", "confidence": "High"},
        "DP6": {"equipment": ["Rotary Kiln"], "templates": [PROCESS, CONDITION], "basis": "Kiln torque is a rotary-kiln loading and drive-condition indicator.", "confidence": "High"},
        "DP7": {"equipment": ["Clinker Cooler"], "templates": [PROCESS, CONDITION], "basis": "Grate speed is the clinker-cooler solids transport control variable.", "confidence": "High"},
        "DP8": {"equipment": ["Clinker Cooler"], "templates": [PROCESS, QUALITY], "basis": "Clinker outlet temperature is produced at the clinker cooler discharge.", "confidence": "High"},
        "DP9": {"equipment": ["Raw Mill"], "templates": [PROCESS, CONDITION], "basis": "Differential pressure across the raw mill indicates grinding-circuit loading and restriction.", "confidence": "High"},
        "DP10": {"equipment": ["Raw Mill"], "templates": [PROCESS], "basis": "Raw-mill outlet temperature is measured at the raw grinding circuit discharge.", "confidence": "High"},
        "DP11": {"equipment": ["Coal Mill"], "templates": [PROCESS, CONDITION], "basis": "Coal-mill outlet temperature belongs to the coal grinding and drying circuit.", "confidence": "High"},
        "DP12": {"equipment": ["Cement Mill"], "templates": [PLANT, PROCESS, CONDITION], "basis": "Main-drive power is consumed by the cement mill and indicates throughput and equipment loading.", "confidence": "High"},
        "DP13": {"equipment": ["Cement Mill Separator"], "templates": [PROCESS, CONDITION], "basis": "Separator speed controls cement fineness in the cement grinding circuit.", "confidence": "High"},
        "DP14": {"equipment": ["Bag Filter / Dust Collector"], "templates": [CONDITION, QUALITY], "basis": "Bag-filter differential pressure measures filter restriction and dust-control performance.", "confidence": "High"},
        "DP15": {"equipment": ["Primary Crusher"], "templates": [PROCESS, CONDITION], "basis": "Motor current is drawn by the primary crusher drive and indicates crusher load.", "confidence": "High"},
        "DP16": {"equipment": ["Clinker Cooler"], "templates": [PROCESS, CONDITION], "basis": "Cooler-fan pressure supplies the clinker cooler aeration zones.", "confidence": "High"},
        "DP17": {"equipment": ["Rotary Kiln"], "templates": [PROCESS, CONDITION], "basis": "Main-drive current is a direct rotary-kiln drive load/condition measurement.", "confidence": "High"},
        "DP18": {"equipment": ["Process Fan (ID/Booster)"], "templates": [PROCESS, CONDITION], "basis": "Kiln ID-fan speed is measured on the kiln induced-draft process fan.", "confidence": "High"},
        "DP19": {"equipment": ["Clinker Storage Dome"], "templates": [PLANT, PROCESS], "basis": "Clinker inventory level is measured in clinker storage.", "confidence": "High"},
        "DP20": {"equipment": ["Packing Plant / Bagging Machine"], "templates": [PLANT, PROCESS], "basis": "Packing rate is the finished-cement throughput of each packing plant.", "confidence": "High"},
        "L1": {"equipment": ["Quality Control Laboratory"], "templates": [QUALITY, PROCESS], "basis": "Raw-meal LSF is a QAQC result used to control raw mix and kiln chemistry.", "confidence": "High"},
        "L2": {"equipment": ["Quality Control Laboratory"], "templates": [QUALITY, PROCESS], "basis": "Raw-meal silica modulus is determined at the cement QAQC laboratory.", "confidence": "High"},
        "L3": {"equipment": ["Quality Control Laboratory"], "templates": [QUALITY, PROCESS], "basis": "Raw-meal alumina modulus is determined at the cement QAQC laboratory.", "confidence": "High"},
        "L4": {"equipment": ["Quality Control Laboratory"], "templates": [QUALITY, PROCESS], "basis": "Raw-meal residue is a laboratory grinding/fineness control result.", "confidence": "High"},
        "L5": {"equipment": ["Quality Control Laboratory"], "templates": [QUALITY, PROCESS], "basis": "Raw-meal moisture is measured by QAQC for raw-mill and kiln feed control.", "confidence": "High"},
        "L6": {"equipment": ["Quality Control Laboratory"], "templates": [QUALITY, PROCESS], "basis": "Clinker free lime is a kiln-burning and clinker-quality laboratory result.", "confidence": "High"},
        "L7": {"equipment": ["Quality Control Laboratory"], "templates": [QUALITY], "basis": "Clinker C3S is a clinker mineralogy QAQC result.", "confidence": "High"},
        "L8": {"equipment": ["Quality Control Laboratory"], "templates": [QUALITY], "basis": "Clinker C2S is a clinker mineralogy QAQC result.", "confidence": "High"},
        "L9": {"equipment": ["Quality Control Laboratory"], "templates": [QUALITY], "basis": "Clinker C3A is a clinker mineralogy QAQC result.", "confidence": "High"},
        "L10": {"equipment": ["Quality Control Laboratory"], "templates": [QUALITY], "basis": "Clinker MgO is a regulated clinker/cement chemistry result.", "confidence": "High"},
        "L11": {"equipment": ["Quality Control Laboratory"], "templates": [QUALITY], "basis": "Clinker SO3 is determined by QAQC for product chemistry control.", "confidence": "High"},
        "L12": {"equipment": ["Quality Control Laboratory"], "templates": [QUALITY, PROCESS], "basis": "Cement Blaine is the laboratory fineness result used to control cement grinding.", "confidence": "High"},
        "L13": {"equipment": ["Quality Control Laboratory"], "templates": [QUALITY, PROCESS], "basis": "Cement 45 µm residue is a laboratory fineness result.", "confidence": "High"},
        "L14": {"equipment": ["Quality Control Laboratory"], "templates": [QUALITY], "basis": "Initial setting time is a finished-cement specification test.", "confidence": "High"},
        "L15": {"equipment": ["Quality Control Laboratory"], "templates": [QUALITY], "basis": "Final setting time is a finished-cement specification test.", "confidence": "High"},
        "L16": {"equipment": ["Quality Control Laboratory"], "templates": [QUALITY], "basis": "Two-day compressive strength is a finished-cement quality result.", "confidence": "High"},
        "L17": {"equipment": ["Quality Control Laboratory"], "templates": [QUALITY], "basis": "Twenty-eight-day compressive strength is a finished-cement quality result.", "confidence": "High"},
        "L18": {"equipment": ["Quality Control Laboratory"], "templates": [QUALITY], "basis": "Loss on ignition is a finished-cement compliance and quality result.", "confidence": "High"},
        "L19": {"equipment": ["Quality Control Laboratory"], "templates": [QUALITY], "basis": "Chloride is a finished-cement regulatory/specification result.", "confidence": "High"},
        "L20": {"equipment": ["Quality Control Laboratory"], "templates": [QUALITY], "basis": "Insoluble residue is a finished-cement specification result.", "confidence": "High"},
        "F1": {"equipment": ["Rotary Kiln"], "templates": [PROCESS, CONDITION], "basis": "Local shell-temperature reading is taken at the kiln inlet shell.", "confidence": "High"},
        "F2": {"equipment": ["Rotary Kiln"], "templates": [PROCESS, CONDITION], "basis": "Local shell-temperature reading is taken at the kiln outlet shell.", "confidence": "High"},
        "F3": {"equipment": ["Rotary Kiln"], "templates": [CONDITION, RELIABILITY], "basis": "Girth-gear vibration is a kiln drive-train condition measurement.", "confidence": "High"},
        "F4": {"equipment": ["Rotary Kiln"], "templates": [CONDITION, RELIABILITY], "basis": "Main-drive bearing temperature is a kiln drive condition indicator.", "confidence": "High"},
        "F5": {"equipment": ["Process Fan (ID/Booster)"], "templates": [CONDITION, RELIABILITY], "basis": "Bearing temperature is measured on the kiln ID/process fan.", "confidence": "High"},
        "F6": {"equipment": ["Clinker Cooler"], "templates": [CONDITION, RELIABILITY], "basis": "Drive-bearing temperature is measured on the clinker cooler drive.", "confidence": "High"},
        "F7": {"equipment": ["Raw Mill"], "templates": [CONDITION, RELIABILITY], "basis": "Gearbox vibration is a raw-mill drive-train condition measurement.", "confidence": "High"},
        "F8": {"equipment": ["Raw Mill"], "templates": [CONDITION, RELIABILITY], "basis": "Bearing temperature is measured on the raw mill.", "confidence": "High"},
        "F9": {"equipment": ["Coal Mill"], "templates": [PROCESS, QUALITY, RELIABILITY], "basis": "Coal-mill CO is a fire/explosion safety and process-condition measurement.", "confidence": "High"},
        "F10": {"equipment": ["Coal Mill"], "templates": [CONDITION, RELIABILITY], "basis": "Bearing temperature is measured on the coal mill.", "confidence": "High"},
        "F11": {"equipment": ["Cement Mill"], "templates": [PROCESS], "basis": "Local inlet temperature is taken at the cement mill inlet.", "confidence": "High"},
        "F12": {"equipment": ["Cement Mill"], "templates": [PROCESS], "basis": "Local outlet temperature is taken at the cement mill outlet.", "confidence": "High"},
        "F13": {"equipment": ["Cement Mill Separator"], "templates": [CONDITION, RELIABILITY], "basis": "Bearing temperature is measured on the cement-mill separator.", "confidence": "High"},
        "F14": {"equipment": ["Primary Crusher"], "templates": [CONDITION, RELIABILITY], "basis": "Crusher-bearing vibration is a primary-crusher condition measurement.", "confidence": "High"},
        "F15": {"equipment": ["Primary Crusher"], "templates": [CONDITION, RELIABILITY], "basis": "Crusher-bearing temperature is a primary-crusher condition measurement.", "confidence": "High"},
        "F16": {"equipment": ["Belt Conveyor"], "templates": [CONDITION, RELIABILITY], "basis": "Belt drift is measured on clinker belt conveying equipment.", "confidence": "High"},
        "F17": {"equipment": ["Bucket Elevator"], "templates": [CONDITION, RELIABILITY], "basis": "Boot temperature is measured at the bucket elevator boot.", "confidence": "High"},
        "F18": {"equipment": ["Packing Plant / Bagging Machine"], "templates": [PROCESS, CONDITION], "basis": "Air pressure supplies the packing-machine pneumatic system.", "confidence": "High"},
        "F19": {"equipment": ["Bag Filter / Dust Collector"], "templates": [CONDITION, QUALITY], "basis": "Hopper temperature is measured on the dust collector/bag filter.", "confidence": "High"},
        "F20": {"equipment": ["Cement Silo"], "templates": [QUALITY, RELIABILITY], "basis": "Silo-roof dust is an environmental/housekeeping measurement at cement silos.", "confidence": "High"},
    },
    "refinery": {
        "DP1": {"equipment": ["Butamer Feed Dryer", "Butamer Charge Heater"], "templates": [PLANT, PROCESS], "basis": "Butamer feed flows through the feed-drying and charge-heating train.", "confidence": "High", "pairs": ["F17"]},
        "DP2": {"equipment": ["Butamer Reactor 1", "Butamer Reactor 2"], "templates": [PROCESS], "basis": "Reactor inlet temperature applies to the two-reactor Butamer train.", "confidence": "High", "pairs": ["F18"]},
        "DP3": {"equipment": ["Butamer Reactor 1", "Butamer Reactor 2"], "templates": [PROCESS], "basis": "Reactor outlet temperature is produced by the Butamer reactor train.", "confidence": "High"},
        "DP4": {"equipment": ["Butamer Reactor 1", "Butamer Reactor 2"], "templates": [PROCESS], "basis": "Butamer reactor pressure applies to the common two-reactor train.", "confidence": "High", "pairs": ["F3", "F4", "F19"]},
        "DP5": {"equipment": ["Butamer Reactor 1", "Butamer Reactor 2"], "templates": [PROCESS], "basis": "Hydrogen-to-hydrocarbon ratio controls the Butamer reactor feed mixture.", "confidence": "High"},
        "DP6": {"equipment": ["Butamer Stabiliser"], "templates": [PROCESS], "basis": "Top temperature is measured on the Butamer stabiliser column.", "confidence": "High"},
        "DP7": {"equipment": ["Butamer Stabiliser"], "templates": [PROCESS], "basis": "Bottom temperature is measured on the Butamer stabiliser column.", "confidence": "High"},
        "DP8": {"equipment": ["Butamer Stabiliser"], "templates": [PROCESS], "basis": "Column pressure is measured on the Butamer stabiliser.", "confidence": "High"},
        "DP9": {"equipment": ["Recycle Gas Compressor", "Butamer Reactor 1", "Butamer Reactor 2"], "templates": [PROCESS, CONDITION], "basis": "Recycle gas is circulated by the compressor through both Butamer reactors.", "confidence": "High"},
        "DP10": {"equipment": ["Butamer Charge Heater"], "templates": [PROCESS, CONDITION], "basis": "Outlet temperature is produced by the Butamer charge heater.", "confidence": "High"},
        "DP11": {"equipment": ["Butamer Feed Dryer"], "templates": [PROCESS, CONDITION], "basis": "Differential pressure measures restriction across the Butamer feed dryer bed.", "confidence": "High"},
        "DP12": {"equipment": ["Butamer Stabiliser"], "templates": [PLANT, QUALITY], "basis": "Product iC4 ratio is a Butamer product-composition KPI downstream of stabilisation.", "confidence": "High"},
        "DP13": {"equipment": ["Butamer Feed Dryer"], "templates": [PROCESS, QUALITY], "basis": "Feed iC4 ratio characterises the feed entering the Butamer train.", "confidence": "High"},
        "DP14": {"equipment": ["Butamer Reactor 1", "Butamer Reactor 2"], "templates": [PROCESS], "basis": "Differential temperature is developed across the Butamer reactor train.", "confidence": "High"},
        "DP15": {"equipment": ["Butamer Reactor 1", "Butamer Reactor 2"], "templates": [PROCESS], "basis": "The configured reactor level belongs to the Butamer reactor train.", "confidence": "Medium"},
        "DP16": {"equipment": ["Recycle Gas Compressor"], "templates": [PROCESS, CONDITION], "basis": "Discharge pressure is measured at the recycle-gas compressor outlet.", "confidence": "High"},
        "DP17": {"equipment": ["Recycle Gas Compressor"], "templates": [CONDITION, RELIABILITY], "basis": "Vibration is a direct recycle-gas compressor health measurement.", "confidence": "High"},
        "DP18": {"equipment": ["Butamer Charge Heater"], "templates": [PLANT, PROCESS], "basis": "Fuel-gas flow is consumed by the Butamer charge heater.", "confidence": "High"},
        "DP19": {"equipment": ["Butamer Reactor 1", "Butamer Reactor 2", "Butamer Stabiliser", "Butamer Charge Heater", "Recycle Gas Compressor"], "templates": [PROCESS, QUALITY, RELIABILITY], "basis": "Flare-header pressure is shared by connected Butamer relief sources; dedicated flare equipment is not in the register.", "confidence": "Review"},
        "DP20": {"equipment": ["Butamer Stabiliser"], "templates": [PLANT, PROCESS], "basis": "Butamer product flow leaves the product stabilisation section.", "confidence": "High"},
        "L1": {"equipment": ["Butamer Feed Dryer"], "templates": [QUALITY, PROCESS], "basis": "Feed iC4 is a feed laboratory result for the Butamer train.", "confidence": "Medium"},
        "L2": {"equipment": ["Butamer Stabiliser"], "templates": [QUALITY, PLANT], "basis": "Product iC4 is a product QAQC result downstream of stabilisation.", "confidence": "Medium"},
        "L3": {"equipment": ["Butamer Feed Dryer"], "templates": [QUALITY, PROCESS], "basis": "Feed nC4 is a feed-composition laboratory result.", "confidence": "Medium"},
        "L4": {"equipment": ["Butamer Stabiliser"], "templates": [QUALITY], "basis": "Product nC4 is a Butamer product-composition result.", "confidence": "Medium"},
        "L5": {"equipment": ["Butamer Feed Dryer"], "templates": [QUALITY], "basis": "Feed C3 is a feed-composition laboratory result.", "confidence": "Medium"},
        "L6": {"equipment": ["Butamer Stabiliser"], "templates": [QUALITY], "basis": "Product C3 is a Butamer product-composition result.", "confidence": "Medium"},
        "L7": {"equipment": ["Butamer Feed Dryer"], "templates": [QUALITY], "basis": "Feed C5+ is a feed-composition laboratory result.", "confidence": "Medium"},
        "L8": {"equipment": ["Butamer Stabiliser"], "templates": [QUALITY], "basis": "Product C5+ is a Butamer product-composition result.", "confidence": "Medium"},
        "L9": {"equipment": ["Butamer Feed Dryer"], "templates": [QUALITY], "basis": "Feed sulfur is a feed quality/compliance result before the Butamer train.", "confidence": "Medium"},
        "L10": {"equipment": ["Butamer Stabiliser"], "templates": [QUALITY], "basis": "Product sulfur is a finished-product compliance result.", "confidence": "Medium"},
        "L11": {"equipment": ["Butamer Feed Dryer"], "templates": [QUALITY, CONDITION], "basis": "Feed water measures dryer inlet loading and feed quality.", "confidence": "High"},
        "L12": {"equipment": ["Butamer Stabiliser"], "templates": [QUALITY], "basis": "Product water is a finished-product specification result.", "confidence": "Medium"},
        "L13": {"equipment": ["Butamer Feed Dryer"], "templates": [QUALITY], "basis": "Chloride is treated as a feed/contaminant QAQC result; sample point should be confirmed.", "confidence": "Review"},
        "L14": {"equipment": ["Butamer Stabiliser"], "templates": [QUALITY, PROCESS], "basis": "Caustic strength supports treating around the product/stabilisation section; exact vessel is not registered.", "confidence": "Review"},
        "L15": {"equipment": ["Recycle Gas Compressor"], "templates": [QUALITY, PROCESS], "basis": "Hydrogen purity characterises recycle/make-up gas serving the reactor loop.", "confidence": "Medium"},
        "L16": {"equipment": ["Butamer Stabiliser"], "templates": [QUALITY, PLANT], "basis": "Octane number is a final Butamer product-quality result.", "confidence": "Medium"},
        "L17": {"equipment": ["Butamer Stabiliser"], "templates": [QUALITY], "basis": "Vapour pressure is a final Butamer product specification.", "confidence": "Medium"},
        "L18": {"equipment": ["Butamer Stabiliser"], "templates": [QUALITY], "basis": "Density at 15°C is a final Butamer product property.", "confidence": "Medium"},
        "L19": {"equipment": ["Butamer Stabiliser"], "templates": [QUALITY], "basis": "Copper strip corrosion is a final product compliance test.", "confidence": "Medium"},
        "L20": {"equipment": ["Butamer Reactor 1", "Butamer Reactor 2", "Butamer Stabiliser"], "templates": [PLANT, QUALITY], "basis": "Product yield covers conversion through the reactor train and product recovery at the stabiliser.", "confidence": "High"},
        "F1": {"equipment": ["Butamer Reactor 1", "Butamer Reactor 2"], "templates": [PROCESS, CONDITION], "basis": "Skin temperature is measured locally on the Butamer reactors.", "confidence": "High"},
        "F2": {"equipment": ["Butamer Charge Heater"], "templates": [PROCESS, CONDITION, RELIABILITY], "basis": "Tube-skin temperature is a charge-heater thermal and integrity indicator.", "confidence": "High"},
        "F3": {"equipment": ["Butamer Reactor 1", "Butamer Reactor 2"], "templates": [PROCESS], "basis": "Local inlet pressure checks the reactor-train inlet Digital Data pressure.", "confidence": "High", "pairs": ["DP4"]},
        "F4": {"equipment": ["Butamer Reactor 1", "Butamer Reactor 2"], "templates": [PROCESS], "basis": "Local outlet pressure checks the reactor-train pressure profile.", "confidence": "High", "pairs": ["DP4"]},
        "F5": {"equipment": ["Recycle Gas Compressor"], "templates": [CONDITION, RELIABILITY], "basis": "Drive-end bearing temperature is measured on the recycle-gas compressor.", "confidence": "High"},
        "F6": {"equipment": ["Recycle Gas Compressor"], "templates": [CONDITION, RELIABILITY], "basis": "Non-drive-end bearing temperature is measured on the recycle-gas compressor.", "confidence": "High"},
        "F7": {"equipment": ["Recycle Gas Compressor"], "templates": [CONDITION, RELIABILITY], "basis": "Axial vibration is a direct compressor health measurement.", "confidence": "High"},
        "F8": {"equipment": ["Butamer Feed Dryer"], "templates": [PROCESS, CONDITION], "basis": "Bed temperature is measured locally in the Butamer feed dryer.", "confidence": "High"},
        "F9": {"equipment": ["Butamer Stabiliser"], "templates": [PROCESS, CONDITION], "basis": "Reboiler outlet temperature belongs to the stabiliser heat-input circuit.", "confidence": "High"},
        "F10": {"equipment": ["Butamer Stabiliser"], "templates": [PROCESS], "basis": "Reflux-drum level supports stabiliser overhead control; drum is not separately registered.", "confidence": "Medium"},
        "F11": {"equipment": ["SPARE:001"], "templates": [CONDITION, RELIABILITY], "basis": "A Butamer pump is not separately registered; mapped to a spare pending equipment identification.", "confidence": "Review"},
        "F12": {"equipment": ["SPARE:001"], "templates": [CONDITION, RELIABILITY], "basis": "A Butamer pump is not separately registered; mapped to a spare pending equipment identification.", "confidence": "Review"},
        "F13": {"equipment": ["SPARE:002"], "templates": [PROCESS], "basis": "The control valve service is unspecified; mapped to a spare pending tag/equipment identification.", "confidence": "Review"},
        "F14": {"equipment": ["Butamer Feed Dryer"], "templates": [PROCESS, QUALITY], "basis": "Drier moisture indication checks feed-dryer outlet performance.", "confidence": "High"},
        "F15": {"equipment": ["SPARE:003"], "templates": [QUALITY, RELIABILITY], "basis": "Hydrogen area detector is not separately registered; spare mapping requires detector-location confirmation.", "confidence": "Review"},
        "F16": {"equipment": ["SPARE:004"], "templates": [QUALITY, RELIABILITY], "basis": "Area H2S detector is not separately registered; spare mapping requires detector-location confirmation.", "confidence": "Review"},
        "F17": {"equipment": ["Butamer Feed Dryer", "Butamer Charge Heater"], "templates": [PLANT, PROCESS], "basis": "Local feed-flow indication checks the Digital Data Butamer feed flow through the front end.", "confidence": "High", "pairs": ["DP1"]},
        "F18": {"equipment": ["Butamer Reactor 1", "Butamer Reactor 2"], "templates": [PROCESS], "basis": "Local reactor temperature indication checks the reactor inlet Digital Data measurement.", "confidence": "Medium", "pairs": ["DP2"]},
        "F19": {"equipment": ["Butamer Reactor 1", "Butamer Reactor 2"], "templates": [PROCESS], "basis": "Local pressure indication checks the reactor Digital Data pressure.", "confidence": "Medium", "pairs": ["DP4"]},
        "F20": {"equipment": ["SPARE:005"], "templates": [QUALITY, RELIABILITY], "basis": "The HCl Draeger sample location is not identified in the equipment register.", "confidence": "Review"},
    },
    "fertilizer": {
        "DP1": {"equipment": ["Primary Reformer"], "templates": [PLANT, PROCESS], "basis": "Natural gas feed enters the ammonia reforming train at the primary reformer.", "confidence": "High"},
        "DP2": {"equipment": ["Primary Reformer"], "templates": [PROCESS, CONDITION], "basis": "Primary-reformer outlet temperature is produced by the reformer.", "confidence": "High"},
        "DP3": {"equipment": ["SPARE:001"], "templates": [PROCESS], "basis": "Secondary reformer is not in the equipment register; spare mapping requires registration.", "confidence": "Review"},
        "DP4": {"equipment": ["Synthesis Gas Compressor"], "templates": [PROCESS, CONDITION], "basis": "Discharge pressure is measured at the synthesis-gas compressor outlet.", "confidence": "High"},
        "DP5": {"equipment": ["SPARE:002"], "templates": [PROCESS], "basis": "Ammonia converter is not in the equipment register; spare mapping requires registration.", "confidence": "Review"},
        "DP6": {"equipment": ["SPARE:002"], "templates": [PROCESS], "basis": "Ammonia converter is not in the equipment register; spare mapping requires registration.", "confidence": "Review"},
        "DP7": {"equipment": ["SPARE:002"], "templates": [PLANT], "basis": "Ammonia production is produced by the converter loop; converter is not yet registered.", "confidence": "Review"},
        "DP8": {"equipment": ["SPARE:003"], "templates": [PROCESS, CONDITION], "basis": "CO2 compressor is not in the equipment register; spare mapping requires registration.", "confidence": "Review"},
        "DP9": {"equipment": ["Urea Reactor"], "templates": [PROCESS], "basis": "Urea synthesis pressure is measured on the urea reactor.", "confidence": "High", "pairs": ["F7"]},
        "DP10": {"equipment": ["Urea Reactor"], "templates": [PROCESS], "basis": "Urea synthesis temperature is measured on the urea reactor.", "confidence": "High"},
        "DP11": {"equipment": ["Urea Stripper"], "templates": [PROCESS], "basis": "Stripper top temperature is measured on the urea stripper.", "confidence": "High"},
        "DP12": {"equipment": ["SPARE:004"], "templates": [PROCESS, CONDITION], "basis": "Carbamate condenser is not in the equipment register; spare mapping requires registration.", "confidence": "Review"},
        "DP13": {"equipment": ["Urea Granulator"], "templates": [PROCESS, QUALITY], "basis": "Granulator bed temperature controls urea granule formation.", "confidence": "High"},
        "DP14": {"equipment": ["Urea Granulator"], "templates": [PLANT, PROCESS], "basis": "Granulator feed rate is the throughput entering the urea granulator.", "confidence": "High"},
        "DP15": {"equipment": ["SPARE:005"], "templates": [PROCESS, CONDITION], "basis": "Fluid-bed cooler is not in the equipment register; spare mapping requires registration.", "confidence": "Review"},
        "DP16": {"equipment": ["SPARE:006"], "templates": [PLANT, PROCESS], "basis": "Ammonia storage is not in the equipment register; spare mapping requires registration.", "confidence": "Review"},
        "DP17": {"equipment": ["SPARE:007"], "templates": [PROCESS, QUALITY], "basis": "Cooling-water system is not in the equipment register; spare mapping requires registration.", "confidence": "Review"},
        "DP18": {"equipment": ["SPARE:008"], "templates": [PLANT, PROCESS], "basis": "Steam header is a shared utility not represented in the equipment register.", "confidence": "Review"},
        "DP19": {"equipment": ["SPARE:009"], "templates": [PLANT, CONDITION], "basis": "Plant electrical demand is plant-wide; electrical system is not registered as equipment.", "confidence": "Review"},
        "DP20": {"equipment": ["Bagging Line 1"], "templates": [PLANT, PROCESS], "basis": "Bagging rate is the finished-product throughput of the bagging line.", "confidence": "High"},
        "L1": {"equipment": ["SPARE:002"], "templates": [QUALITY, PLANT], "basis": "Ammonia purity is a product QAQC result; converter/product lab point is not registered.", "confidence": "Review"},
        "L2": {"equipment": ["SPARE:002"], "templates": [QUALITY], "basis": "Ammonia water content is a product specification; lab/product point is not registered.", "confidence": "Review"},
        "L3": {"equipment": ["Urea Granulator"], "templates": [QUALITY, PLANT], "basis": "Urea nitrogen is a finished-product QAQC result associated with granulated product.", "confidence": "Medium"},
        "L4": {"equipment": ["Urea Granulator"], "templates": [QUALITY], "basis": "Urea moisture is a finished granule quality result.", "confidence": "Medium"},
        "L5": {"equipment": ["Urea Reactor", "Urea Granulator"], "templates": [QUALITY, PROCESS], "basis": "Biuret forms in urea synthesis/finishing and is controlled as a product-quality parameter.", "confidence": "High"},
        "L6": {"equipment": ["Urea Granulator"], "templates": [QUALITY, PROCESS], "basis": "Formaldehyde additive is measured on finished granulation quality.", "confidence": "Medium"},
        "L7": {"equipment": ["Urea Granulator"], "templates": [QUALITY, PROCESS], "basis": "Two-to-four-millimetre granule fraction is a granulator product-size result.", "confidence": "High"},
        "L8": {"equipment": ["Urea Granulator"], "templates": [QUALITY], "basis": "Crushing strength is a finished urea granule quality result.", "confidence": "High"},
        "L9": {"equipment": ["Urea Granulator"], "templates": [QUALITY], "basis": "Bulk density is a finished granular-urea quality result.", "confidence": "Medium"},
        "L10": {"equipment": ["SPARE:007"], "templates": [QUALITY, PROCESS], "basis": "Cooling-water chemistry point is not represented in the equipment register.", "confidence": "Review"},
        "L11": {"equipment": ["SPARE:010"], "templates": [QUALITY, RELIABILITY], "basis": "Boiler-water system is not represented in the equipment register.", "confidence": "Review"},
        "L12": {"equipment": ["SPARE:010"], "templates": [QUALITY, RELIABILITY], "basis": "Boiler-water system is not represented in the equipment register.", "confidence": "Review"},
        "L13": {"equipment": ["SPARE:011"], "templates": [QUALITY, RELIABILITY], "basis": "Condensate system is not represented in the equipment register.", "confidence": "Review"},
        "L14": {"equipment": ["Primary Reformer"], "templates": [QUALITY, PROCESS], "basis": "Natural-gas methane content characterises reformer feed quality.", "confidence": "High"},
        "L15": {"equipment": ["Primary Reformer"], "templates": [QUALITY, PROCESS], "basis": "Natural-gas sulfur is a reformer feed-contaminant result.", "confidence": "High"},
        "L16": {"equipment": ["SPARE:011"], "templates": [QUALITY, PROCESS], "basis": "Process-condensate system is not represented in the equipment register.", "confidence": "Review"},
        "L17": {"equipment": ["Urea Granulator"], "templates": [QUALITY, PROCESS], "basis": "Prill/product temperature is associated with finished urea cooling/handling.", "confidence": "Medium"},
        "L18": {"equipment": ["Bagging Line 1"], "templates": [QUALITY, RELIABILITY], "basis": "Product dust is a finished-product handling and environmental result.", "confidence": "Medium"},
        "L19": {"equipment": ["SPARE:006"], "templates": [QUALITY], "basis": "Oil in ammonia is a product/storage quality result; storage equipment is not registered.", "confidence": "Review"},
        "L20": {"equipment": ["SPARE:003"], "templates": [QUALITY, PROCESS], "basis": "CO2 purity characterises urea-feed gas; CO2 compressor/header is not registered.", "confidence": "Review"},
        "F1": {"equipment": ["Primary Reformer"], "templates": [PROCESS, CONDITION, RELIABILITY], "basis": "Tube-skin temperature is a primary-reformer thermal and integrity measurement.", "confidence": "High"},
        "F2": {"equipment": ["Primary Reformer"], "templates": [PROCESS, CONDITION], "basis": "Burner flame quality is observed on the primary reformer burners.", "confidence": "High"},
        "F3": {"equipment": ["Synthesis Gas Compressor"], "templates": [CONDITION, RELIABILITY], "basis": "Bearing temperature is measured on the synthesis-gas compressor.", "confidence": "High"},
        "F4": {"equipment": ["Synthesis Gas Compressor"], "templates": [CONDITION, RELIABILITY], "basis": "Vibration is measured on the synthesis-gas compressor.", "confidence": "High"},
        "F5": {"equipment": ["SPARE:012"], "templates": [CONDITION, RELIABILITY], "basis": "Ammonia pump is not separately registered; spare mapping requires identification.", "confidence": "Review"},
        "F6": {"equipment": ["SPARE:013"], "templates": [QUALITY, RELIABILITY], "basis": "Ammonia area detector is not separately registered; location requires confirmation.", "confidence": "Review"},
        "F7": {"equipment": ["Urea Reactor"], "templates": [PROCESS], "basis": "Local reactor pressure checks the Digital Data urea-reactor pressure.", "confidence": "High", "pairs": ["DP9"]},
        "F8": {"equipment": ["Urea Stripper"], "templates": [CONDITION, RELIABILITY], "basis": "Vibration is measured on the urea stripper assembly.", "confidence": "High"},
        "F9": {"equipment": ["Urea Granulator"], "templates": [CONDITION, RELIABILITY], "basis": "Vibration is measured on the urea granulator.", "confidence": "High"},
        "F10": {"equipment": ["Urea Granulator"], "templates": [PROCESS], "basis": "Visual bed level is observed in the urea granulator.", "confidence": "High"},
        "F11": {"equipment": ["SPARE:005"], "templates": [CONDITION, RELIABILITY], "basis": "Fluid-bed fan/cooler is not registered; spare mapping requires registration.", "confidence": "Review"},
        "F12": {"equipment": ["SPARE:014"], "templates": [CONDITION, RELIABILITY], "basis": "Product conveyor is not registered; spare mapping requires registration.", "confidence": "Review"},
        "F13": {"equipment": ["SPARE:015"], "templates": [CONDITION, RELIABILITY], "basis": "Bucket elevator is not registered; spare mapping requires registration.", "confidence": "Review"},
        "F14": {"equipment": ["Bagging Line 1"], "templates": [PROCESS, CONDITION], "basis": "Pneumatic pressure supplies the urea bagging line.", "confidence": "High"},
        "F15": {"equipment": ["SPARE:016"], "templates": [CONDITION, QUALITY], "basis": "Dust collector is not registered; spare mapping requires registration.", "confidence": "Review"},
        "F16": {"equipment": ["SPARE:017"], "templates": [CONDITION, RELIABILITY], "basis": "Cooling-tower fan is not registered; spare mapping requires registration.", "confidence": "Review"},
        "F17": {"equipment": ["SPARE:008"], "templates": [PROCESS, CONDITION], "basis": "Steam-trap/header equipment is not represented in the register.", "confidence": "Review"},
        "F18": {"equipment": ["SPARE:018"], "templates": [CONDITION, RELIABILITY], "basis": "Valve service is unspecified; spare mapping requires identification.", "confidence": "Review"},
        "F19": {"equipment": ["Bagging Line 1"], "templates": [QUALITY, RELIABILITY], "basis": "Housekeeping dust is monitored around product handling/bagging.", "confidence": "Medium"},
        "F20": {"equipment": ["SPARE:019"], "templates": [QUALITY, PROCESS], "basis": "Product storage is not registered; spare mapping requires registration.", "confidence": "Review"},
    },
    "nascon": {
        "DP1": {"equipment": ["Salt Evaporator 1"], "templates": [PLANT, PROCESS], "basis": "Brine feed enters the salt evaporation circuit.", "confidence": "High"},
        "DP2": {"equipment": ["Salt Evaporator 1"], "templates": [PROCESS], "basis": "Salt evaporator temperature is measured on the evaporator body.", "confidence": "High", "pairs": ["F1"]},
        "DP3": {"equipment": ["Salt Evaporator 1"], "templates": [PROCESS, CONDITION], "basis": "Evaporator vacuum is a primary salt-evaporation process variable.", "confidence": "High"},
        "DP4": {"equipment": ["Salt Dryer 1"], "templates": [PROCESS], "basis": "Dryer inlet temperature is measured at the salt dryer inlet.", "confidence": "High"},
        "DP5": {"equipment": ["Salt Dryer 1"], "templates": [PROCESS, QUALITY], "basis": "Dryer outlet temperature controls finished-salt moisture/temperature.", "confidence": "High"},
        "DP6": {"equipment": ["Salt Packing Line 1"], "templates": [PLANT, PROCESS], "basis": "Salt packing rate is the throughput of the salt packing line.", "confidence": "High"},
        "DP7": {"equipment": ["Sugar Mill 1"], "templates": [PLANT, PROCESS], "basis": "Cane feed rate is the throughput entering the sugar mill.", "confidence": "High"},
        "DP8": {"equipment": ["Sugar Mill 1"], "templates": [PLANT, PROCESS], "basis": "Mill extraction is a sugar-mill performance KPI.", "confidence": "High"},
        "DP9": {"equipment": ["Sugar Mill 1", "Sugar Evaporator 1"], "templates": [PLANT, PROCESS], "basis": "Mixed juice is produced by milling and feeds the evaporation train.", "confidence": "High"},
        "DP10": {"equipment": ["SPARE:001"], "templates": [PROCESS, QUALITY], "basis": "Clarifier is not in the equipment register; spare mapping requires registration.", "confidence": "Review"},
        "DP11": {"equipment": ["Sugar Evaporator 1"], "templates": [PROCESS, QUALITY], "basis": "Evaporator Brix measures concentration produced by the sugar evaporator.", "confidence": "High"},
        "DP12": {"equipment": ["SPARE:002"], "templates": [PROCESS, CONDITION], "basis": "Vacuum pan is not in the equipment register; spare mapping requires registration.", "confidence": "Review", "pairs": ["F11"]},
        "DP13": {"equipment": ["SPARE:002"], "templates": [PROCESS, QUALITY], "basis": "Massecuite is produced in the vacuum-pan crystallisation section, not separately registered.", "confidence": "Review"},
        "DP14": {"equipment": ["Sugar Centrifuge 1"], "templates": [PROCESS, CONDITION], "basis": "Centrifuge speed is measured on the sugar centrifuge.", "confidence": "High"},
        "DP15": {"equipment": ["SPARE:003"], "templates": [PROCESS, QUALITY], "basis": "Sugar dryer is not in the equipment register; spare mapping requires registration.", "confidence": "Review"},
        "DP16": {"equipment": ["Sugar Packing Line 1"], "templates": [PLANT, PROCESS], "basis": "Sugar packing rate is the throughput of the sugar packing line.", "confidence": "High"},
        "DP17": {"equipment": ["SPARE:004"], "templates": [PLANT, PROCESS], "basis": "Boiler/steam system is not in the equipment register; spare mapping requires registration.", "confidence": "Review"},
        "DP18": {"equipment": ["SPARE:004"], "templates": [PLANT, PROCESS, CONDITION], "basis": "Boiler/steam system is not in the equipment register; spare mapping requires registration.", "confidence": "Review"},
        "DP19": {"equipment": ["SPARE:005"], "templates": [PLANT, CONDITION], "basis": "Plant electrical demand is plant-wide; electrical system is not registered.", "confidence": "Review"},
        "DP20": {"equipment": ["SPARE:006"], "templates": [PLANT, PROCESS], "basis": "Warehouse silo is not in the equipment register; spare mapping requires registration.", "confidence": "Review"},
        "L1": {"equipment": ["Salt Packing Line 1"], "templates": [QUALITY, PLANT], "basis": "NaCl purity is a finished-salt product specification.", "confidence": "Medium"},
        "L2": {"equipment": ["Salt Dryer 1", "Salt Packing Line 1"], "templates": [QUALITY, PROCESS], "basis": "Salt moisture is controlled by drying and confirmed on finished packed salt.", "confidence": "High"},
        "L3": {"equipment": ["Salt Packing Line 1"], "templates": [QUALITY], "basis": "Insoluble matter is a finished-salt specification result.", "confidence": "Medium"},
        "L4": {"equipment": ["Salt Packing Line 1"], "templates": [QUALITY], "basis": "Iodine content is a finished iodised-salt compliance result.", "confidence": "High"},
        "L5": {"equipment": ["Salt Packing Line 1"], "templates": [QUALITY], "basis": "Salt particle-size pass is a finished-product grading result.", "confidence": "Medium"},
        "L6": {"equipment": ["Salt Evaporator 1"], "templates": [QUALITY, PROCESS], "basis": "Brine density characterises feed to the salt evaporator.", "confidence": "High"},
        "L7": {"equipment": ["Salt Evaporator 1"], "templates": [QUALITY, PROCESS], "basis": "Brine calcium is an evaporator-feed impurity result.", "confidence": "High"},
        "L8": {"equipment": ["Salt Evaporator 1"], "templates": [QUALITY, PROCESS], "basis": "Brine magnesium is an evaporator-feed impurity result.", "confidence": "High"},
        "L9": {"equipment": ["Sugar Packing Line 1"], "templates": [QUALITY, PLANT], "basis": "Polarisation is a finished-sugar specification result.", "confidence": "Medium"},
        "L10": {"equipment": ["Sugar Packing Line 1"], "templates": [QUALITY], "basis": "Moisture is a finished-sugar specification result.", "confidence": "Medium"},
        "L11": {"equipment": ["Sugar Packing Line 1"], "templates": [QUALITY], "basis": "Colour is a finished-sugar product specification.", "confidence": "Medium"},
        "L12": {"equipment": ["Sugar Packing Line 1"], "templates": [QUALITY], "basis": "Ash is a finished-sugar product specification.", "confidence": "Medium"},
        "L13": {"equipment": ["Sugar Packing Line 1"], "templates": [QUALITY], "basis": "Reducing sugars are a finished-sugar quality result.", "confidence": "Medium"},
        "L14": {"equipment": ["Sugar Mill 1"], "templates": [QUALITY, PROCESS], "basis": "Cane Brix characterises raw cane feed to the sugar mill.", "confidence": "High"},
        "L15": {"equipment": ["Sugar Mill 1"], "templates": [QUALITY, PROCESS], "basis": "Cane pol characterises raw cane feed to the sugar mill.", "confidence": "High"},
        "L16": {"equipment": ["Sugar Mill 1"], "templates": [QUALITY, PLANT], "basis": "Bagasse moisture is a milling-extraction and boiler-fuel quality KPI.", "confidence": "High"},
        "L17": {"equipment": ["Sugar Mill 1", "Sugar Evaporator 1"], "templates": [QUALITY, PROCESS], "basis": "Mixed-juice purity is measured after milling and before evaporation.", "confidence": "High"},
        "L18": {"equipment": ["SPARE:007"], "templates": [QUALITY, PROCESS], "basis": "Final-molasses point is not separately registered; spare mapping requires registration.", "confidence": "Review"},
        "L19": {"equipment": ["SPARE:007"], "templates": [QUALITY, PLANT], "basis": "Final-molasses point is not separately registered; spare mapping requires registration.", "confidence": "Review"},
        "L20": {"equipment": ["SPARE:008"], "templates": [QUALITY, PROCESS], "basis": "Process-water system is not represented in the equipment register.", "confidence": "Review"},
        "F1": {"equipment": ["Salt Evaporator 1"], "templates": [PROCESS, CONDITION], "basis": "Local evaporator-body temperature checks the Digital Data salt-evaporator temperature.", "confidence": "High", "pairs": ["DP2"]},
        "F2": {"equipment": ["Salt Dryer 1"], "templates": [CONDITION, RELIABILITY], "basis": "Bearing temperature is measured on the salt dryer.", "confidence": "High"},
        "F3": {"equipment": ["Salt Dryer 1"], "templates": [CONDITION, RELIABILITY], "basis": "Vibration is measured on the salt dryer.", "confidence": "High"},
        "F4": {"equipment": ["SPARE:009"], "templates": [CONDITION, RELIABILITY], "basis": "Salt conveyor is not registered; spare mapping requires registration.", "confidence": "Review"},
        "F5": {"equipment": ["Salt Packing Line 1"], "templates": [PROCESS, CONDITION], "basis": "Pneumatic pressure supplies the salt packing line.", "confidence": "High"},
        "F6": {"equipment": ["Sugar Mill 1"], "templates": [CONDITION, RELIABILITY], "basis": "Roller-bearing temperature is measured on the sugar mill.", "confidence": "High"},
        "F7": {"equipment": ["Sugar Mill 1"], "templates": [CONDITION, RELIABILITY], "basis": "Gearbox vibration is measured on the sugar mill drive.", "confidence": "High"},
        "F8": {"equipment": ["SPARE:010"], "templates": [CONDITION, RELIABILITY], "basis": "Juice pump is not registered; spare mapping requires identification.", "confidence": "Review"},
        "F9": {"equipment": ["SPARE:001"], "templates": [PROCESS], "basis": "Clarifier is not registered; spare mapping requires registration.", "confidence": "Review"},
        "F10": {"equipment": ["Sugar Evaporator 1"], "templates": [CONDITION, RELIABILITY], "basis": "Tube condition is an evaporator heat-transfer/cleanliness indicator.", "confidence": "High"},
        "F11": {"equipment": ["SPARE:002"], "templates": [PROCESS], "basis": "Local vacuum-pan pressure checks the Digital Data pan pressure; pan is not registered.", "confidence": "Review", "pairs": ["DP12"]},
        "F12": {"equipment": ["Sugar Centrifuge 1"], "templates": [CONDITION, RELIABILITY], "basis": "Bearing temperature is measured on the sugar centrifuge.", "confidence": "High"},
        "F13": {"equipment": ["Sugar Centrifuge 1"], "templates": [CONDITION, RELIABILITY], "basis": "Vibration is measured on the sugar centrifuge.", "confidence": "High"},
        "F14": {"equipment": ["SPARE:003"], "templates": [CONDITION, RELIABILITY], "basis": "Sugar dryer is not registered; spare mapping requires registration.", "confidence": "Review"},
        "F15": {"equipment": ["SPARE:011"], "templates": [CONDITION, RELIABILITY], "basis": "Sugar conveyor is not registered; spare mapping requires registration.", "confidence": "Review"},
        "F16": {"equipment": ["Sugar Packing Line 1"], "templates": [PROCESS, CONDITION], "basis": "Pneumatic pressure supplies the sugar packing line.", "confidence": "High"},
        "F17": {"equipment": ["SPARE:004"], "templates": [CONDITION, RELIABILITY], "basis": "Boiler feed pump is not registered; spare mapping requires identification.", "confidence": "Review"},
        "F18": {"equipment": ["SPARE:004"], "templates": [PROCESS, RELIABILITY], "basis": "Boiler drum is not registered; spare mapping requires registration.", "confidence": "Review"},
        "F19": {"equipment": ["SPARE:012"], "templates": [CONDITION, RELIABILITY], "basis": "Bagasse conveyor is not registered; spare mapping requires registration.", "confidence": "Review"},
        "F20": {"equipment": ["SPARE:006"], "templates": [QUALITY, RELIABILITY], "basis": "Warehouse dust is an environmental/housekeeping measurement; warehouse is not registered.", "confidence": "Review"},
    },
}


CALCULATED_TEMPLATE_RULES = {
    "cement": {"CF1": [PLANT], "CF2": [PROCESS, CONDITION], "CF3": [PROCESS, QUALITY], "CF4": [QUALITY, PROCESS], "CF5": [PROCESS, CONDITION], "CF6": [PROCESS], "CF7": [QUALITY], "CF8": [PLANT, PROCESS]},
    "refinery": {"CF1": [PLANT], "CF2": [PROCESS], "CF3": [PROCESS], "CF4": [QUALITY, PLANT], "CF5": [CONDITION, PROCESS], "CF6": [PROCESS], "CF7": [QUALITY], "CF8": [PLANT]},
    "fertilizer": {"CF1": [PLANT], "CF2": [PROCESS, CONDITION], "CF3": [PROCESS], "CF4": [QUALITY], "CF5": [PROCESS], "CF6": [PROCESS], "CF7": [QUALITY], "CF8": [PLANT]},
    "nascon": {"CF1": [PLANT], "CF2": [PROCESS], "CF3": [PROCESS, CONDITION], "CF4": [QUALITY], "CF5": [PROCESS, CONDITION], "CF6": [PLANT], "CF7": [QUALITY], "CF8": [PLANT]},
}


def _spare_id(equipment: pd.DataFrame, number: int) -> str:
    spare = equipment[equipment.get("placeholder", pd.Series(dtype=str)).astype(str).str.lower() == "true"]
    ids = spare.get("equipment_id", pd.Series(dtype=str)).astype(str).tolist()
    if not ids:
        ids = equipment.get("equipment_id", pd.Series(dtype=str)).astype(str).tolist()
    if not ids:
        return ""
    suffix = f"{max(1, number):03d}"
    exact = next((item for item in ids if item.endswith(suffix)), None)
    return exact or ids[(max(1, number) - 1) % len(ids)]


def _equipment_ids(equipment: pd.DataFrame, terms: list[str]) -> list[str]:
    results: list[str] = []
    for term in terms:
        if term.startswith("SPARE:"):
            item = _spare_id(equipment, int(term.split(":", 1)[1]))
            if item:
                results.append(item)
            continue
        names = equipment.get("equipment_name", pd.Series(index=equipment.index, dtype=str)).astype(str)
        active = equipment.get("active", pd.Series(index=equipment.index, dtype=str)).astype(str).str.lower() == "true"
        named = equipment.get("placeholder", pd.Series(index=equipment.index, dtype=str)).astype(str).str.lower() != "true"
        exact = names.str.lower() == term.lower()
        name_match = exact if exact.any() else names.str.contains(term, case=False, regex=False)
        matches = equipment[name_match & active & named]
        results.extend(matches.get("equipment_id", pd.Series(dtype=str)).astype(str).tolist())
    return list(dict.fromkeys(results))


def _placeholder_spare_number(field_id: str, source: str) -> int:
    number = int("".join(character for character in field_id if character.isdigit()) or "1")
    source_offsets = {"DCS": 0, "Lab": 100, "Field": 200, "TA": 300, "TB": 325, "TC": 350, "TD": 375, "TE": 400, "TF": 425, "TG": 450}
    return ((source_offsets.get(source, 475) + number - 1) % 500) + 1


def build_engineering_defaults(
    bu: str,
    catalog: pd.DataFrame,
    equipment: pd.DataFrame,
    calculated_fields: pd.DataFrame,
) -> dict[str, dict[str, Any]]:
    records: dict[str, dict[str, Any]] = {}
    rules = ENGINEERING_RULES.get(bu, {})
    spare_mask = equipment.get("placeholder", pd.Series(index=equipment.index, dtype=str)).astype(str).str.lower() == "true"
    spare_ids = equipment.loc[spare_mask, "equipment_id"].astype(str).tolist() if "equipment_id" in equipment else []
    all_equipment_ids = equipment.get("equipment_id", pd.Series(dtype=str)).astype(str).tolist()

    def spare_for(number: int) -> str:
        ids = spare_ids or all_equipment_ids
        if not ids:
            return ""
        suffix = f"{max(1, number):03d}"
        exact = next((item for item in ids if item.endswith(suffix)), None)
        return exact or ids[(max(1, number) - 1) % len(ids)]

    input_catalog = catalog[catalog["field_type"].astype(str) != "Calculated"]
    for field in input_catalog.itertuples(index=False):
        field_id = str(field.field_id)
        source = str(field.source_key)
        if str(field.field_type) == "Placeholder":
            spare_id = spare_for(_placeholder_spare_number(field_id, source))
            records[field_id] = {
                "equipment_ids": [spare_id] if spare_id else [],
                "template_ids": PLACEHOLDER_TEMPLATES.get(source, [PROCESS]),
                "mapping_type": "Computed Default",
                "mapping_basis": "Default placeholder mapping – review when field is named.",
                "confidence": "Review",
                "instrument_check_pairs": [],
            }
            continue
        rule = rules.get(field_id)
        if not rule:
            spare_id = spare_for(_placeholder_spare_number(field_id, source))
            records[field_id] = {
                "equipment_ids": [spare_id] if spare_id else [],
                "template_ids": PLACEHOLDER_TEMPLATES.get(source, [PROCESS]),
                "mapping_type": "Computed Default",
                "mapping_basis": f"Named field '{field.field_name}' has no approved engineering rule; review equipment and template assignment.",
                "confidence": "Review",
                "instrument_check_pairs": [],
            }
            continue
        equipment_ids = _equipment_ids(equipment, list(rule["equipment"]))
        if not equipment_ids:
            equipment_ids = [spare_for(_placeholder_spare_number(field_id, source))]
            confidence = "Review"
            basis = str(rule["basis"]) + " No matching registered equipment was found."
        else:
            confidence = str(rule.get("confidence", "High"))
            basis = str(rule["basis"])
        records[field_id] = {
            "equipment_ids": [item for item in equipment_ids if item],
            "template_ids": list(rule["templates"]),
            "mapping_type": "Computed Default",
            "mapping_basis": basis,
            "confidence": confidence,
            "instrument_check_pairs": list(rule.get("pairs", [])),
        }

    formula_lookup = calculated_fields.set_index("field_id") if not calculated_fields.empty and "field_id" in calculated_fields else pd.DataFrame()
    for field in catalog[catalog["field_type"].astype(str) == "Calculated"].itertuples(index=False):
        field_id = str(field.field_id)
        formula = str(formula_lookup.loc[field_id].get("formula", "")) if not formula_lookup.empty and field_id in formula_lookup.index else ""
        inputs = list(dict.fromkeys(re.findall(r"\[([^\]]+)\]", formula)))
        equipment_ids: list[str] = []
        input_confidence: list[str] = []
        for input_id in inputs:
            input_record = records.get(input_id, {})
            equipment_ids.extend(input_record.get("equipment_ids", []))
            input_confidence.append(str(input_record.get("confidence", "Review")))
        equipment_ids = list(dict.fromkeys(equipment_ids))
        confidence = "Review" if "Review" in input_confidence or not equipment_ids else ("Medium" if "Medium" in input_confidence else "High")
        records[field_id] = {
            "equipment_ids": equipment_ids or [spare_for(_placeholder_spare_number(field_id, "Calculated"))],
            "template_ids": CALCULATED_TEMPLATE_RULES.get(bu, {}).get(field_id, [PROCESS]),
            "mapping_type": "Computed Default",
            "mapping_basis": f"Calculated field inherits equipment from formula input(s): {', '.join(inputs) or 'none found'}. Formula: {formula or 'not configured'}.",
            "confidence": confidence,
            "instrument_check_pairs": [],
        }
    return records
