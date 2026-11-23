# OPERA-X v3.10.0 vs v3.9.0 change manifest

## Summary

| Result | Count |
|---|---:|
| Modified | 13 |
| Added | 10 |
| Deleted | 2 |
| Unchanged | 285 |
| v3.9.0 files | 300 |
| v3.10.0 files | 308 |

Counts use SHA-256 file comparison, exclude directories/caches, and include `SHA256SUMS.txt` as modified plus this manifest as added.

## Modified files

```text
BUILD_NOTES.md
DATA_OVERWRITE_WARNING.md
MAPPING_QUALITY_REPORT.md
README.md
SHA256SUMS.txt
TEST_RESULTS.md
VERSION
app.py
opera/__init__.py
scripts/build_mapping_quality_report.py
tests/test_v350_features.py
tests/test_v380_features.py
tests/test_v390_features.py
```

## Added files

```text
CHANGE_MANIFEST_v3.10.0_vs_v3.9.0.md
CODE_ONLY_DELETE_INSTRUCTIONS_v3.10.0.txt
LIVE_DATA_UPDATE_v3.10.0.md
VISUAL_VERIFICATION_v3.10.0.md
assets/dangote_vision_2030.png
assets/dangote_vision_2030_compact.png
tests/test_v310_features.py
verification/home_and_header_v3.10.0.png
verification/operational_data_pipeline_v3.10.0.png
verification/sign_in_v3.10.0.png
```

## Deleted files

```text
assets/dangote_vision_2030.jpg
assets/dangote_vision_2030_compact.jpg
```

The removed JPEG files are replaced by transparent PNG assets. A ZIP overlay cannot delete repository files, so follow `CODE_ONLY_DELETE_INSTRUCTIONS_v3.10.0.txt` after applying the code-only package.

## User-facing behavior

- The Home category/group remains **Operational Data**.
- The module formerly shown as Operational Data is now **Operational Data Pipeline** in Home, navigation, the page heading, export names and displayed audit labels.
- Process Optimization is grouped under Operational Data.
- Job Risk Assessment is grouped under Operational Knowledge.
- Admin / Super Admin is removed from the Home cards and remains available in top navigation for authorized users.
- Top navigation uses plain v3.8-style labels with no category prefixes, legend, icons or category colour formatting.
- Change BU is stacked above Sign Out, with the transparent Vision 2030 mark beside the stack.

## Runtime-data and overwrite impact

Every file under `data/`, `registers/` and `reference_sources/` is byte-for-byte unchanged from v3.9.0.

**No file in live `~/opera_data` must be added, replaced, renamed or edited.** Internal route, storage, source, CSV, Excel and historical audit identifiers remain compatible. Stored `data_input_saved` and `bulk_upload` values are translated only in the Admin audit display.

## Recommended GitHub/DDF deployment

Use `OPERA-X_Code_Only_Update_v3.10.0_vs_v3.9.0.zip`. It contains every modified or added file above except `SHA256SUMS.txt` and excludes `data/`, `registers/` and `reference_sources/`.

1. Overlay the code-only ZIP at the repository root.
2. Delete the two obsolete JPEG assets listed in the delete instructions.
3. Commit and test on Streamlit Community Cloud.
4. On the DDF server, run `git pull` in the existing checkout.
5. Keep `OPERA_DATA_DIR=~/opera_data` (or `OPERAX_DATA_DIR`) in the startup environment.
6. Restart Streamlit on port 8089/address 172.20.130.228.
7. Do not copy the full ZIP's `data/` folder into `~/opera_data`.

## Verification

- 59 automated tests passed.
- Python compilation passed for `app.py`, `opera/*.py` and `scripts/*.py`.
- Sign-in, Home/header and Operational Data Pipeline were rendered at 1600×1000 with no visible Streamlit exception panel.
- Visual captures are included under `verification/`.
