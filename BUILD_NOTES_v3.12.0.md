# OPERA-X v3.12.0 build notes

## Scope

v3.12.0 starts from the complete v3.11.1 package and preserves the v3.9–v3.11.1 mapping, version, header, nginx base-path and Community Cloud fixes. It addresses the Edge breakpoint, content-control borders, navigation wording, duplicate page headings, page-opening performance and Lesson Bank categories.

## 1. Edge menu collapse — root cause and fix

### Root cause

The user measured the primary Dangote laptop in Microsoft Edge with DevTools undocked and the Edge sidebar closed:

- physical display: 1920 px;
- Windows scaling: 150%;
- `screen.width`: 1280 CSS px;
- `window.outerWidth`: 1280 CSS px;
- `window.innerWidth`: 1272 CSS px;
- `devicePixelRatio`: 1.5;
- usable page width with the vertical scrollbar: approximately 1255 CSS px.

v3.11.1 collapsed the desktop menu at 1279 px and below. Edge therefore followed the compact branch even though the physical screen was 1920 px. This was a breakpoint problem, not a different Edge rendering engine: Edge and Chrome are both Chromium, but their effective CSS viewport can differ by window chrome, scaling and scrollbar allocation.

### Fix

- The flat menu remains visible from 1100 CSS px upward and collapses only at 1099 px and below.
- A compact desktop range from 1100–1365 px uses 8 px horizontal item padding, 14 px text and 1 px group dividers.
- Normal 13 px item padding remains at 1366 px and above; nav text is never below 14 px.
- The responsive decision is a CSS viewport media query, not a Streamlit column/container measurement.
- All eleven items, the bell and avatar stay on one row. At the 1272 px test viewport with a 17 px scrollbar gutter, the measured menu row is 829.52 px inside 1255 px of usable application width.
- “Dashboards” is now `KPI's`; it still routes to Operations Dashboard.

## 2. Missing field and button borders — root cause and fix

v3.11.1 gave the header explicit border resets but left content fields dependent on Streamlit theme defaults. Streamlit 1.66.1 renders select/date controls with React Aria (`data-rac`, `stDateInputField`) rather than only the older BaseWeb nodes. Against the light-blue secondary background, those default control backgrounds and edges had insufficient contrast and looked like floating text.

The header rules now remain header-key scoped, and content controls have separate selectors under `stMainBlockContainer`. Visible 1 px borders, white field backgrounds and blue focus rings are applied to:

- buttons and download buttons;
- selectboxes and multiselects;
- date, time, text and number inputs;
- file-upload drop zones; and
- expanders.

Both old BaseWeb and current React-Aria structures are covered so the login, Select Business Unit page and every authenticated page retain accessible focus styling.

## 3. Navigation label and page heading

- The flat label `Dashboards` is now `KPI's`.
- The internal route remains `Operations Dashboard`.
- The breadcrumb continues to show `Operations Dashboard`.
- The explicit v3.11.1 H1 elements added directly below the breadcrumb on Home, Equipment Overview and Admin were removed. The breadcrumb and each page’s own section titles remain, with no duplicate/leftover page heading.

## 4. Performance — root causes and fixes

### Root causes found

1. v3.11.1 rendered eleven desktop navigation buttons and another eleven hidden mobile buttons on every rerun.
2. Closed mobile, notification and account popovers still executed their body widgets on every rerun.
3. The 1823 px Vision 2030 compact PNG was 520,934 bytes and became an approximately 694 KB base64 string injected on every page rerun.
4. Brand assets were read and base64-encoded repeatedly.
5. Operations Dashboard rebuilt the same aligned input/calculated snapshot whenever the page reopened, even when no source file had changed.

### Fixes

- Replaced eleven desktop buttons with one Streamlit-native radio-group widget styled as the approved flat menu.
- The compact menu, notification panel and account panel now render their inner widgets only while open.
- Added right-sized transparent WebP assets: the repeated compact asset is 24,770 bytes instead of 520,934 bytes.
- Cached asset data URIs per process.
- Added a file-signature cache for Operations Dashboard data. Any change to source CSVs, fields, calculated-field definitions or constants changes the key automatically; no stale manual invalidation is required.

### Measured result

Method: median of three warm authenticated click-to-settled-page transitions after one warm-up cycle, same container host and bundled Chromium. Times include Streamlit rerun, backend work and settled page rendering.

| Page | v3.10.1 reference | v3.11.1 before | v3.12.0 after | Change vs v3.11.1 |
|---|---:|---:|---:|---:|
| Home | 1.623 s | 5.946 s | 1.532 s | -74.2% |
| Plant Overview | 1.086 s | 2.372 s | 1.066 s | -55.1% |
| Equipment Overview | 4.606 s | 2.284 s | 1.495 s | -34.5% |
| Operations Dashboard | 5.315 s | 18.901 s | 7.718 s | -59.2% |
| Admin | 1.512 s | 4.560 s | 1.359 s | -70.2% |

Four target pages are at or faster than the v3.10.1 reference within these paired runs. Operations Dashboard is 2.402 s above the v3.10.1 reference but 11.184 s faster than v3.11.1; it remains the heaviest page because it renders the aligned KPI card and chart workspace.

Machine-readable results are in `verification/v3.12.0/performance_comparison_v3.10.1_v3.11.1_v3.12.0.json`.

## 5. Lesson Bank categories

- Controlled defaults: Equipment, Safety, General and Plant Operations.
- Admin can maintain the controlled list under **Admin / Super Admin → Equipment → Validation Lists → Lesson Categories**. Equipment and General are retained for compatibility.
- Input Lesson stores `category`.
- Equipment is required only for the Equipment category; it is optional for every other category.
- Event-linked non-equipment lessons can optionally retain the event’s equipment.
- Review Lessons includes a Category filter and category column.
- The selected lesson PDF metadata and filtered Lesson Bank Excel export include Category.
- Home’s Super Admin Lessons Excel export also uses the migrated category-aware frame.

### Existing lesson migration

On first category-aware lesson load for each business unit, OPERA-X atomically adds the `category` column if needed:

- an existing row with equipment becomes `Equipment`;
- an existing row without equipment becomes `General`.

No manual CSV edit is required.

## Compatibility and deployment

- `streamlit==1.66.1` remains pinned.
- Both `OPERA_DATA_DIR` and `OPERAX_DATA_DIR` remain supported.
- Root-path Community Cloud and nginx `/operationaldashboard/` were tested.
- The code-only ZIP excludes `data/`, `registers/` and `reference_sources/`.

Deploy the complete code-only update, then fully restart and hard-refresh:

```bash
cd ~/OPERA
git pull
source .venv/bin/activate
python -m pip install -r requirements.txt
~/OPERA/start_opera.sh
```

Use **Ctrl+F5** in both Chrome and Edge. A Streamlit hot reload is not sufficient for the header/CSS and asset changes.
