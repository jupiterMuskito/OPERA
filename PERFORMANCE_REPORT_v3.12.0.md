# OPERA-X v3.12.0 performance report

See `BUILD_NOTES_v3.12.0.md` for the full root-cause analysis.

## Method

Median of three warm authenticated click-to-settled-page transitions after one warm-up cycle, on the same container host using the same bundled Chromium executable. A DOM-quiet interval is included so early page markers do not under-report a still-rendering Streamlit page.

| Page | v3.10.1 reference | v3.11.1 before | v3.12.0 after | v3.11.1 → v3.12.0 |
|---|---:|---:|---:|---:|
| Home | 1.623 s | 5.946 s | 1.532 s | -74.2% |
| Plant Overview | 1.086 s | 2.372 s | 1.066 s | -55.1% |
| Equipment Overview | 4.606 s | 2.284 s | 1.495 s | -34.5% |
| Operations Dashboard | 5.315 s | 18.901 s | 7.718 s | -59.2% |
| Admin | 1.512 s | 4.560 s | 1.359 s | -70.2% |

## Fixes measured

- one desktop navigation widget instead of eleven buttons;
- hidden mobile controls are not built until the compact menu is opened;
- notification and account panel bodies are not built while closed;
- repeated compact Vision 2030 payload reduced from 520,934-byte PNG to 24,770-byte WebP;
- asset encoding cached;
- Operations Dashboard aligned data cached against source-file signatures.

Raw results:

- `verification/v3.12.0/performance_v3.10.1_vs_v3.12.0.json`
- `verification/v3.12.0/performance_v3.11.1_vs_v3.12.0.json`
- `verification/v3.12.0/performance_comparison_v3.10.1_v3.11.1_v3.12.0.json`
