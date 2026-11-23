from pathlib import Path

import opera
from opera.version import get_version, version_badge_html


ROOT = Path(__file__).resolve().parents[1]


def test_banner_version_file_and_package_version_agree():
    """Guard the full path from VERSION to package metadata and the live banner."""
    expected = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    app_source = (ROOT / "app.py").read_text(encoding="utf-8")

    assert expected == "3.10.1"
    assert opera.__version__ == expected
    assert get_version() == expected
    assert version_badge_html() == f'<div class="version">v{expected}</div>'
    assert "from opera.version import version_badge_html" in app_source
    assert "version_badge_html()" in app_source
    assert "APP_VERSION" not in app_source


def test_version_badge_reads_the_version_file_instead_of_a_cached_literal(monkeypatch, tmp_path):
    version_file = tmp_path / "VERSION"
    version_file.write_text("9.8.7\n", encoding="utf-8")
    monkeypatch.setattr("opera.version.VERSION_FILE", version_file)

    assert get_version() == "9.8.7"
    assert version_badge_html() == '<div class="version">v9.8.7</div>'

    version_file.write_text("9.8.8\n", encoding="utf-8")
    assert version_badge_html() == '<div class="version">v9.8.8</div>'