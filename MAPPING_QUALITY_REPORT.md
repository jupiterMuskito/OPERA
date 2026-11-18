# OPERA-X v3.7.0 — Engineering Mapping Quality Report

## Scope and method

The default mapping was rebuilt from field names, units, formulas, physical process context and the registered equipment inventory. Named DP, F and L fields use curated field-by-field engineering rules. Calculated fields inherit the union of equipment mapped to their formula inputs. Placeholder fields use a source-aware SPARE assignment and are explicitly marked for review when named. No named field uses round-robin, index-based or random assignment.

- Named/calculated fields reviewed: **288**
- Placeholder fields retained: **89,760**
- Named fields marked **Review**: **65**
- Placeholder fields marked **Review**: **89,760** (grouped below because listing all IDs would add 89,760 low-value rows)

## Mapping counts by BU and dashboard template

Counts are field-to-template relationships; a field is counted in each template where it genuinely serves more than one use.

### Named and calculated fields

| Business unit | Condition Monitoring | Plant Performance | Process Performance | Quality and Compliance | Reliability |
|---|---|---|---|---|---|
| bu5 | 0 | 0 | 0 | 0 | 0 |
| bu6 | 0 | 0 | 0 | 0 | 0 |
| bu7 | 0 | 0 | 0 | 0 | 0 |
| bu8 | 0 | 0 | 0 | 0 | 0 |
| bu9 | 0 | 0 | 0 | 0 | 0 |
| cement | 30 | 6 | 43 | 29 | 14 |
| fertilizer | 22 | 11 | 42 | 28 | 17 |
| nascon | 23 | 17 | 41 | 28 | 15 |
| refinery | 16 | 11 | 42 | 29 | 11 |

### Complete database, including placeholders

| Business unit | Condition Monitoring | Plant Performance | Process Performance | Quality and Compliance | Reliability |
|---|---|---|---|---|---|
| bu5 | 1000 | 0 | 9000 | 1000 | 0 |
| bu6 | 1000 | 0 | 9000 | 1000 | 0 |
| bu7 | 1000 | 0 | 9000 | 1000 | 0 |
| bu8 | 1000 | 0 | 9000 | 1000 | 0 |
| bu9 | 1000 | 0 | 9000 | 1000 | 0 |
| cement | 1010 | 6 | 9003 | 1009 | 14 |
| fertilizer | 1002 | 11 | 9002 | 1008 | 17 |
| nascon | 1003 | 17 | 9001 | 1008 | 15 |
| refinery | 996 | 11 | 9002 | 1009 | 11 |

## Named mappings marked Review

These are not silent guesses. Most indicate that the physically correct equipment or sample point is absent from the current register and the field has been assigned to a clearly identified SPARE record or a documented shared process scope.

| Business unit | Field ID | Data field | Equipment IDs | Mapping basis |
|---|---|---|---|---|
| refinery | DP19 | Flare Header Pressure | REF-BUT-RX-01; REF-BUT-RX-02; REF-BUT-STAB-01; REF-BUT-HTR-01; REF-CCR-COMP-01 | Flare-header pressure is shared by connected Butamer relief sources; dedicated flare equipment is not in the register. |
| refinery | L13 | Chloride | REF-BUT-DRY-01 | Chloride is treated as a feed/contaminant QAQC result; sample point should be confirmed. |
| refinery | L14 | Caustic Strength | REF-BUT-STAB-01 | Caustic strength supports treating around the product/stabilisation section; exact vessel is not registered. |
| refinery | F11 | Pump Seal Temperature | REF-SPARE-001 | A Butamer pump is not separately registered; mapped to a spare pending equipment identification. |
| refinery | F12 | Pump Vibration | REF-SPARE-001 | A Butamer pump is not separately registered; mapped to a spare pending equipment identification. |
| refinery | F13 | Control Valve Position Check | REF-SPARE-002 | The control valve service is unspecified; mapped to a spare pending tag/equipment identification. |
| refinery | F15 | Hydrogen Detector Reading | REF-SPARE-003 | Hydrogen area detector is not separately registered; spare mapping requires detector-location confirmation. |
| refinery | F16 | Area H2S Reading | REF-SPARE-004 | Area H2S detector is not separately registered; spare mapping requires detector-location confirmation. |
| refinery | F20 | Dräger Hydrochloric Acid | REF-SPARE-005 | The HCl Draeger sample location is not identified in the equipment register. |
| fertilizer | DP3 | Secondary Reformer Outlet Temperature | FER-SPARE-001 | Secondary reformer is not in the equipment register; spare mapping requires registration. |
| fertilizer | DP5 | Ammonia Converter Inlet Temperature | FER-SPARE-002 | Ammonia converter is not in the equipment register; spare mapping requires registration. |
| fertilizer | DP6 | Ammonia Converter Outlet Temperature | FER-SPARE-002 | Ammonia converter is not in the equipment register; spare mapping requires registration. |
| fertilizer | DP7 | Ammonia Production Rate | FER-SPARE-002 | Ammonia production is produced by the converter loop; converter is not yet registered. |
| fertilizer | DP8 | CO2 Compressor Discharge Pressure | FER-SPARE-003 | CO2 compressor is not in the equipment register; spare mapping requires registration. |
| fertilizer | DP12 | Carbamate Condenser Temperature | FER-SPARE-004 | Carbamate condenser is not in the equipment register; spare mapping requires registration. |
| fertilizer | DP15 | Fluid Bed Cooler Outlet Temperature | FER-SPARE-005 | Fluid-bed cooler is not in the equipment register; spare mapping requires registration. |
| fertilizer | DP16 | Ammonia Storage Level | FER-SPARE-006 | Ammonia storage is not in the equipment register; spare mapping requires registration. |
| fertilizer | DP17 | Cooling Water Supply Temperature | FER-SPARE-007 | Cooling-water system is not in the equipment register; spare mapping requires registration. |
| fertilizer | DP18 | Steam Header Pressure | FER-SPARE-008 | Steam header is a shared utility not represented in the equipment register. |
| fertilizer | DP19 | Plant Power Demand | FER-SPARE-009 | Plant electrical demand is plant-wide; electrical system is not registered as equipment. |
| fertilizer | L1 | Ammonia Product Purity | FER-SPARE-002 | Ammonia purity is a product QAQC result; converter/product lab point is not registered. |
| fertilizer | L2 | Ammonia Water Content | FER-SPARE-002 | Ammonia water content is a product specification; lab/product point is not registered. |
| fertilizer | L10 | Cooling Water pH | FER-SPARE-007 | Cooling-water chemistry point is not represented in the equipment register. |
| fertilizer | L11 | Boiler Water Conductivity | FER-SPARE-010 | Boiler-water system is not represented in the equipment register. |
| fertilizer | L12 | Boiler Water Silica | FER-SPARE-010 | Boiler-water system is not represented in the equipment register. |
| fertilizer | L13 | Condensate Iron | FER-SPARE-011 | Condensate system is not represented in the equipment register. |
| fertilizer | L16 | Process Condensate Ammonia | FER-SPARE-011 | Process-condensate system is not represented in the equipment register. |
| fertilizer | L19 | Oil in Ammonia | FER-SPARE-006 | Oil in ammonia is a product/storage quality result; storage equipment is not registered. |
| fertilizer | L20 | CO2 Purity | FER-SPARE-003 | CO2 purity characterises urea-feed gas; CO2 compressor/header is not registered. |
| fertilizer | F5 | Ammonia Pump Seal Temperature | FER-SPARE-012 | Ammonia pump is not separately registered; spare mapping requires identification. |
| fertilizer | F6 | Ammonia Area Detector | FER-SPARE-013 | Ammonia area detector is not separately registered; location requires confirmation. |
| fertilizer | F11 | Fluid Bed Fan Bearing Temperature | FER-SPARE-005 | Fluid-bed fan/cooler is not registered; spare mapping requires registration. |
| fertilizer | F12 | Conveyor Belt Drift | FER-SPARE-014 | Product conveyor is not registered; spare mapping requires registration. |
| fertilizer | F13 | Bucket Elevator Bearing Temperature | FER-SPARE-015 | Bucket elevator is not registered; spare mapping requires registration. |
| fertilizer | F15 | Dust Collector Differential Pressure | FER-SPARE-016 | Dust collector is not registered; spare mapping requires registration. |
| fertilizer | F16 | Cooling Tower Fan Vibration | FER-SPARE-017 | Cooling-tower fan is not registered; spare mapping requires registration. |
| fertilizer | F17 | Steam Trap Temperature | FER-SPARE-008 | Steam-trap/header equipment is not represented in the register. |
| fertilizer | F18 | Valve Packing Leak Index | FER-SPARE-018 | Valve service is unspecified; spare mapping requires identification. |
| fertilizer | F20 | Product Storage Temperature | FER-SPARE-019 | Product storage is not registered; spare mapping requires registration. |
| fertilizer | CF6 | Converter Temperature Rise | FER-SPARE-002 | Calculated field inherits equipment from formula input(s): DP6, DP5. Formula: ABS([DP6]-[DP5]). |
| fertilizer | CF9 | Ammonia Capacity Utilisation | FER-SPARE-002 | Calculated field inherits equipment from formula input(s): DP7. Formula: ([DP7]/3300)*100. |
| fertilizer | CF11 | Granulation Health Index | FER-GRAN-01; FER-SPARE-005 | Calculated field inherits equipment from formula input(s): DP13, F9, F11. Formula: ([DP13]+[F9]+[F11])/3. |
| fertilizer | CF12 | Energy Demand Index | FER-SPARE-009 | Calculated field inherits equipment from formula input(s): DP19. Formula: [DP19]. |
| nascon | DP10 | Clarifier Temperature | NAS-SPARE-001 | Clarifier is not in the equipment register; spare mapping requires registration. |
| nascon | DP12 | Vacuum Pan Pressure | NAS-SPARE-002 | Vacuum pan is not in the equipment register; spare mapping requires registration. |
| nascon | DP13 | Massecuite Temperature | NAS-SPARE-002 | Massecuite is produced in the vacuum-pan crystallisation section, not separately registered. |
| nascon | DP15 | Sugar Dryer Outlet Temperature | NAS-SPARE-003 | Sugar dryer is not in the equipment register; spare mapping requires registration. |
| nascon | DP17 | Boiler Steam Pressure | NAS-SPARE-004 | Boiler/steam system is not in the equipment register; spare mapping requires registration. |
| nascon | DP18 | Boiler Steam Temperature | NAS-SPARE-004 | Boiler/steam system is not in the equipment register; spare mapping requires registration. |
| nascon | DP19 | Power Demand | NAS-SPARE-005 | Plant electrical demand is plant-wide; electrical system is not registered. |
| nascon | DP20 | Warehouse Silo Level | NAS-SPARE-006 | Warehouse silo is not in the equipment register; spare mapping requires registration. |
| nascon | L18 | Final Molasses Brix | NAS-SPARE-007 | Final-molasses point is not separately registered; spare mapping requires registration. |
| nascon | L19 | Final Molasses Purity | NAS-SPARE-007 | Final-molasses point is not separately registered; spare mapping requires registration. |
| nascon | L20 | Process Water pH | NAS-SPARE-008 | Process-water system is not represented in the equipment register. |
| nascon | F4 | Salt Conveyor Belt Drift | NAS-SPARE-009 | Salt conveyor is not registered; spare mapping requires registration. |
| nascon | F8 | Juice Pump Vibration | NAS-SPARE-010 | Juice pump is not registered; spare mapping requires identification. |
| nascon | F9 | Clarifier Mud Level | NAS-SPARE-001 | Clarifier is not registered; spare mapping requires registration. |
| nascon | F11 | Vacuum Pan Local Pressure | NAS-SPARE-002 | Local vacuum-pan pressure checks the DCS pan pressure; pan is not registered. |
| nascon | F14 | Sugar Dryer Bearing Temperature | NAS-SPARE-003 | Sugar dryer is not registered; spare mapping requires registration. |
| nascon | F15 | Sugar Conveyor Belt Drift | NAS-SPARE-011 | Sugar conveyor is not registered; spare mapping requires registration. |
| nascon | F17 | Boiler Feed Pump Vibration | NAS-SPARE-004 | Boiler feed pump is not registered; spare mapping requires identification. |
| nascon | F18 | Boiler Drum Local Level | NAS-SPARE-004 | Boiler drum is not registered; spare mapping requires registration. |
| nascon | F19 | Bagasse Conveyor Condition | NAS-SPARE-012 | Bagasse conveyor is not registered; spare mapping requires registration. |
| nascon | F20 | Warehouse Dust Level | NAS-SPARE-006 | Warehouse dust is an environmental/housekeeping measurement; warehouse is not registered. |
| nascon | CF12 | Utility Load Index | NAS-SPARE-004; NAS-SPARE-005 | Calculated field inherits equipment from formula input(s): DP17, DP19. Formula: ([DP17]+[DP19])/2. |

## Placeholder Review summary

| Business unit | Source group | Review placeholders | Basis |
|---|---|---|---|
| cement | DCS | 980 | Default placeholder mapping – review when field is named. |
| cement | QAQC | 980 | Default placeholder mapping – review when field is named. |
| cement | Field | 980 | Default placeholder mapping – review when field is named. |
| cement | Others | 7000 | Default placeholder mapping – review when field is named. |
| refinery | DCS | 980 | Default placeholder mapping – review when field is named. |
| refinery | QAQC | 980 | Default placeholder mapping – review when field is named. |
| refinery | Field | 980 | Default placeholder mapping – review when field is named. |
| refinery | Others | 7000 | Default placeholder mapping – review when field is named. |
| fertilizer | DCS | 980 | Default placeholder mapping – review when field is named. |
| fertilizer | QAQC | 980 | Default placeholder mapping – review when field is named. |
| fertilizer | Field | 980 | Default placeholder mapping – review when field is named. |
| fertilizer | Others | 7000 | Default placeholder mapping – review when field is named. |
| nascon | DCS | 980 | Default placeholder mapping – review when field is named. |
| nascon | QAQC | 980 | Default placeholder mapping – review when field is named. |
| nascon | Field | 980 | Default placeholder mapping – review when field is named. |
| nascon | Others | 7000 | Default placeholder mapping – review when field is named. |
| bu5 | DCS | 1000 | Default placeholder mapping – review when field is named. |
| bu5 | QAQC | 1000 | Default placeholder mapping – review when field is named. |
| bu5 | Field | 1000 | Default placeholder mapping – review when field is named. |
| bu5 | Others | 7000 | Default placeholder mapping – review when field is named. |
| bu6 | DCS | 1000 | Default placeholder mapping – review when field is named. |
| bu6 | QAQC | 1000 | Default placeholder mapping – review when field is named. |
| bu6 | Field | 1000 | Default placeholder mapping – review when field is named. |
| bu6 | Others | 7000 | Default placeholder mapping – review when field is named. |
| bu7 | DCS | 1000 | Default placeholder mapping – review when field is named. |
| bu7 | QAQC | 1000 | Default placeholder mapping – review when field is named. |
| bu7 | Field | 1000 | Default placeholder mapping – review when field is named. |
| bu7 | Others | 7000 | Default placeholder mapping – review when field is named. |
| bu8 | DCS | 1000 | Default placeholder mapping – review when field is named. |
| bu8 | QAQC | 1000 | Default placeholder mapping – review when field is named. |
| bu8 | Field | 1000 | Default placeholder mapping – review when field is named. |
| bu8 | Others | 7000 | Default placeholder mapping – review when field is named. |
| bu9 | DCS | 1000 | Default placeholder mapping – review when field is named. |
| bu9 | QAQC | 1000 | Default placeholder mapping – review when field is named. |
| bu9 | Field | 1000 | Default placeholder mapping – review when field is named. |
| bu9 | Others | 7000 | Default placeholder mapping – review when field is named. |

## Twenty named mappings for spot-checking

| BU | Field | Equipment | Templates | Reason | Confidence |
|---|---|---|---|---|---|
| cement | DP1 — Kiln Feed Rate | Rotary Kiln; Rotary Kiln; Rotary Kiln | Plant Performance; Process Performance | Kiln feed is the solids throughput entering each rotary kiln. | High |
| cement | DP8 — Clinker Cooler Outlet Temperature | Clinker Cooler; Clinker Cooler; Clinker Cooler | Process Performance; Quality and Compliance | Clinker outlet temperature is produced at the clinker cooler discharge. | High |
| cement | L6 — Clinker Free Lime | Quality Control Laboratory; Quality Control Laboratory; Quality Control Laboratory | Quality and Compliance; Process Performance | Clinker free lime is a kiln-burning and clinker-quality laboratory result. | High |
| cement | F3 — Kiln Girth Gear Vibration | Rotary Kiln; Rotary Kiln; Rotary Kiln | Condition Monitoring; Reliability | Girth-gear vibration is a kiln drive-train condition measurement. | High |
| cement | CF6 — Calciner-Preheater Temperature Difference | Calciner; Calciner; Calciner; Preheater Tower / Cyclones; Preheater Tower / Cyclones; Preheater Tower / Cyclones | Process Performance | Calculated field inherits equipment from formula input(s): DP5, DP4. Formula: ABS([DP5]-[DP4]). | High |
| refinery | DP2 — Butamer Reactor Inlet Temperature | Butamer Reactor 1; Butamer Reactor 2 | Process Performance | Reactor inlet temperature applies to the two-reactor Butamer train. | High |
| refinery | DP11 — Feed Dryer Differential Pressure | Butamer Feed Dryer | Process Performance; Condition Monitoring | Differential pressure measures restriction across the Butamer feed dryer bed. | High |
| refinery | L20 — Product Yield | Butamer Reactor 1; Butamer Reactor 2; Butamer Stabiliser | Plant Performance; Quality and Compliance | Product yield covers conversion through the reactor train and product recovery at the stabiliser. | High |
| refinery | F17 — Local Flow Indicator | Butamer Feed Dryer; Butamer Charge Heater | Plant Performance; Process Performance | Local feed-flow indication checks the DCS Butamer feed flow through the front end. | High |
| refinery | CF6 — Reactor Temperature Rise | Butamer Reactor 1; Butamer Reactor 2 | Process Performance | Calculated field inherits equipment from formula input(s): DP3, DP2. Formula: ABS([DP3]-[DP2]). | High |
| fertilizer | DP9 — Urea Reactor Pressure | Urea Reactor | Process Performance | Urea synthesis pressure is measured on the urea reactor. | High |
| fertilizer | DP14 — Granulator Feed Rate | Urea Granulator | Plant Performance; Process Performance | Granulator feed rate is the throughput entering the urea granulator. | High |
| fertilizer | L7 — Granule Size 2–4 mm | Urea Granulator | Quality and Compliance; Process Performance | Two-to-four-millimetre granule fraction is a granulator product-size result. | High |
| fertilizer | F7 — Urea Reactor Local Pressure | Urea Reactor | Process Performance | Local reactor pressure checks the DCS urea-reactor pressure. | High |
| fertilizer | CF5 — Field-DCS Urea Pressure Deviation | Urea Reactor | Process Performance | Calculated field inherits equipment from formula input(s): F7, DP9. Formula: ABS([F7]-[DP9]). | High |
| nascon | DP8 — Mill Extraction | Sugar Mill 1 | Plant Performance; Process Performance | Mill extraction is a sugar-mill performance KPI. | High |
| nascon | DP14 — Centrifuge Speed | Sugar Centrifuge 1 | Process Performance; Condition Monitoring | Centrifuge speed is measured on the sugar centrifuge. | High |
| nascon | L4 — Salt Iodine | Salt Packing Line 1 | Quality and Compliance | Iodine content is a finished iodised-salt compliance result. | High |
| nascon | F1 — Salt Evaporator Body Temperature | Salt Evaporator 1 | Process Performance; Condition Monitoring | Local evaporator-body temperature checks the DCS salt-evaporator temperature. | High |
| nascon | CF8 — Average Packing Rate | Salt Packing Line 1; Sugar Packing Line 1 | Plant Performance | Calculated field inherits equipment from formula input(s): DP6, DP16. Formula: ([DP6]+[DP16])/2. | High |

## Calculated-field check

The 32 packaged calculated fields were checked against their formulas. Misnamed or dimensionally inconsistent v3.5.0 defaults were corrected in the four configured BUs. Each calculated mapping now inherits equipment from its actual formula inputs, and its database basis records those input IDs and formula.

## Instrument Check pairs recorded

The Excel databases record the physically comparable local/DCS pairs for Refinery (Butamer feed flow, reactor temperatures and pressures), Fertilizer (urea-reactor pressure) and NASCON (salt-evaporator temperature and vacuum-pan pressure). Cement has no defensible same-point F/DP pair in the current 60-field sample, so none was fabricated.
