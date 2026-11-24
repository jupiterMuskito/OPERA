import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "verify_header_browser.py"


def test_browser_verifier_covers_release_breakpoints_paths_and_breadcrumb_contract():
    source = SCRIPT.read_text(encoding="utf-8")
    assert "WIDTHS = (1920, 1560, 1536, 1366, 1280, 1279)" in source
    assert 'for base_path in ("", "operationaldashboard")' in source
    assert 'expected_desktop = width >= 1280' in source
    assert "menu wrapped" in source
    assert "breadcrumb is clipped" in source
    assert "first heading overlaps breadcrumb" in source
    assert 'PAGES = (' in source and '("admin", "Admin", "Admin / Super Admin", "Admin / Super Admin")' in source


@pytest.mark.browser
def test_real_streamlit_header_in_chromium():
    if os.getenv("OPERAX_RUN_BROWSER_TESTS") != "1":
        pytest.skip("Set OPERAX_RUN_BROWSER_TESTS=1 to run the real Chromium/Streamlit suite")
    subprocess.run([sys.executable, str(SCRIPT), "--check-only"], cwd=ROOT, check=True, timeout=900)
