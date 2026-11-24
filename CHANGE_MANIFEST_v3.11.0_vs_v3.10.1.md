# OPERA-X v3.11.0 vs v3.10.1 change manifest

Baseline: `OPERA-X_Streamlit_Deployment_v3.10.1_Final.zip`  
Target: OPERA-X v3.11.0

## Changed files (12)

- `app.py` — approved flat header/navigation, native page controls, notifications/avatar popovers, responsive menu, breadcrumb, and dead authenticated-header code removal.
- `VERSION` — `3.10.1` → `3.11.0`.
- `requirements.txt` — exact `streamlit==1.66.1` pin for tested header CSS compatibility.
- `README.md` — current header, dependency, deployment, restart, and live-data guidance.
- `BUILD_NOTES.md` — promoted current v3.11.0 notes.
- `TEST_RESULTS.md` — 68-test and four-width browser verification results.
- `tests/test_v3101_mapping_regressions.py` — current single-source version expectation while retaining the v3.10.1 mapping regression scenario.
- `tests/test_v310_features.py` — user-menu action expectations replace the obsolete stacked-action layout.
- `tests/test_v350_features.py` — authenticated page smoke test now drives native navigation state; flat-header assertion updated.
- `tests/test_v380_features.py` — current version and user-menu Sign Out expectations.
- `tests/test_v390_features.py` — current version and brand-bar Vision 2030 wrapper expectations.
- `tests/test_version_consistency.py` — current version and complete version-helper import expectation.

## Added files (12)

- `CHANGE_MANIFEST_v3.11.0_vs_v3.10.1.md`
- `BUILD_NOTES_v3.10.1.md` — preserved copy of the prior generic build notes.
- `BUILD_NOTES_v3.11.0.md`
- `LIVE_DATA_UPDATE_v3.11.0.md`
- `VISUAL_VERIFICATION_v3.11.0.md`
- `tests/test_v3110_header.py`
- `verification/v3.11.0/header_1920px.png`
- `verification/v3.11.0/header_1560px.png`
- `verification/v3.11.0/header_1366px.png`
- `verification/v3.11.0/header_1280px.png`
- `verification/v3.11.0/header_1279px.png` — breakpoint evidence.
- `verification/v3.11.0/header_measurements.json`

## Deleted files (0)

None. Dead radio-navigation, stacked-action, and unused header CSS were removed from `app.py`; no standalone file needed deletion.

## `~/opera_data`

**No update is required.** The bundled `data/` tree is byte-for-byte restored from the verified v3.10.1 baseline after testing, and the code-only package excludes `data/`, `registers/`, and `reference_sources/`. Keep `OPERA_DATA_DIR=~/opera_data` (or `OPERAX_DATA_DIR`) and fully restart with `~/OPERA/start_opera.sh` after `git pull`.
