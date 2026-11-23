# OPERA-X v3.7.0 — Performance Report

## Test method

Measurements use Streamlit `AppTest` against the packaged Cement BU on the same container and Python environment. Each value is elapsed server-side application-test time for one navigation/rerun; browser/network/nginx latency is not included. v3.6.0 and v3.7.0 were measured from their own extracted packages. Small sub-second differences on simple pages are test-run noise; the material dashboard reductions are the focus.

## End-to-end page times

| Page | v3.6.0 (s) | v3.7.0 (s) | Change |
|---|---:|---:|---:|
| OPERA-X Home | 15.363 | 0.820 | 94.7% faster |
| Plant Overview | 49.088 | 3.848 | 92.2% faster |
| Equipment Overview | 8.879 | 1.642 | 81.5% faster |
| Operations Dashboard | 4.448 | 1.531 | 65.6% faster |
| Operational Data | 14.425 | 1.290 | 91.1% faster |
| Operating Parameters | 5.941 | 1.806 | 69.6% faster |

Additional v3.7.0 measurements:

| Page | v3.7.0 (s) |
|---|---:|
| Event Log | 1.523 |
| Job Risk Assessment | 1.042 |
| Lesson Bank | 0.403 |
| Admin / Super Admin default area | 0.402 |
| Admin / Field Mappings (10,012 fields) | 5.063 |

## Data-path profile

| Operation | v3.6.0 | v3.7.0 |
|---|---:|---:|
| Full Cement long-data preparation | 12.8–14.0 s | 0.69–0.72 s |
| Calculated-data preparation | 7.2–7.7 s | 0.15–0.17 s |
| Mapping table, cold | 30.33 s | 1.75 s data preparation; about 5.1 s end-to-end Admin page including controls/tables |
| Mapping table, warm | 2.05–5.11 s | 0.002–0.007 s |
| Home reading count | full 197,100-row long-frame build | 0.38 s cold; 0.05–0.06 s warm |
| Populated Obajana equipment data preparation | whole-BU load | 0.50 s cold; 0.13–0.15 s warm |

## Changes responsible

- Read only active source columns instead of all 1,008 columns in every source CSV.
- Filter plant/equipment rows before converting wide input to long form.
- Cache CSV/JSON snapshots by modification signature; atomic writes invalidate immediately.
- Keep Excel authoritative while using a signature-checked compressed runtime mapping cache.
- Replace eagerly executed Operational Data and Admin tabs with lazy-loaded section ribbons.
- Default period views to the latest 30 days while retaining user access to the full range.
- Downsample chart traces to at most 300 points per field.
- Keep 12 template fields but render four CPP-style panels at a time.
- Count Home readings directly from active wide columns instead of building a 197,100-row long frame.

## Interpretation

The test host shows substantial reductions on all previously heavy pages. Production time will also include disk, CPU, reverse-proxy and browser conditions on `172.20.130.228`; use the same benchmark after deployment if infrastructure-level timings are required.
