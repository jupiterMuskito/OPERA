from pathlib import Path

from app import NAV_LABELS, PAGES, _page_category, _user_initials
from opera import __version__


ROOT = Path(__file__).resolve().parents[1]


def test_flat_menu_order_labels_and_full_page_routes_are_stable():
    assert PAGES == [
        "OPERA-X Home",
        "Plant Overview",
        "Equipment Overview",
        "Operations Dashboard",
        "Operating Parameters",
        "Operational Data Pipeline",
        "Process Optimization",
        "Event Log",
        "Lesson Bank",
        "Job Risk Assessment",
        "Admin / Super Admin",
    ]
    assert [NAV_LABELS[page] for page in PAGES] == [
        "Home", "Plant", "Equipment", "KPI's", "Parameters", "Data Pipeline",
        "Optimization", "Event Log", "Lessons", "Risk Assessment", "Admin",
    ]


def test_header_uses_one_native_radio_group_without_anchor_navigation_or_eleven_buttons():
    source = (ROOT / "app.py").read_text(encoding="utf-8")
    navigation = source[source.index("def top_navigation"):source.index("def source_frame")]
    assert "st.radio(" in navigation
    assert "<a href" not in navigation
    assert 'desktop_key = "desktop_navigation_page"' in navigation
    assert "on_change=_select_mobile_page" in navigation
    assert "def _render_nav_buttons" not in source
    assert 'horizontal=True, label_visibility="collapsed"' in navigation
    assert "st.columns([ratios[page]" not in navigation
    assert 'key="mobile_menu"' in navigation
    assert 'key="notifications_menu"' in navigation
    assert 'key="user_menu"' in navigation
    assert 'page != "Admin / Super Admin" or auth.allowed(user, "configure")' in navigation


def test_brand_version_breadcrumb_and_responsive_css_match_approved_design():
    source = (ROOT / "app.py").read_text(encoding="utf-8")
    requirements = (ROOT / "requirements.txt").read_text(encoding="utf-8").splitlines()
    assert __version__ == "3.13.0"
    assert "streamlit==1.66.1" in requirements
    assert "One Platform for All Plant Operational Data" in source
    assert "opera-vision-block" in source and "version_badge_html()" in source
    assert "opera-breadcrumb" in source and "opera-bu-badge" in source
    assert "@media(max-width:1099px)" in source
    assert "@media(min-width:1100px) and (max-width:1365px)" in source
    assert ".st-key-mobile_navigation{display:none}" in source
    assert "border-bottom:4px solid #D7262F" in source
    assert "white-space:nowrap" in source
    assert ".st-key-primary_navigation{position:sticky;top:68px" in source
    assert "height:52px;min-height:52px" in source
    assert "margin-top:-16px" in source
    assert "padding:0 13px" in source
    assert "padding-left:8px;padding-right:8px;font-size:14px" in source
    assert "operax-app-styles" in source
    assert "overflow:visible!important;gap:0!important" in source


def test_lazy_header_panels_badge_and_compact_mobile_menu_are_styled_cleanly():
    source = (ROOT / "app.py").read_text(encoding="utf-8")
    assert "top:-2px;right:-1px" in source
    assert 'st.button("☰", key="mobile_menu"' in source
    assert 'key="header_mobile_panel"' in source
    assert 'key="header_notice_panel"' in source
    assert 'key="header_user_panel"' in source
    assert "st.popover(" not in source[source.index("def top_navigation"):source.index("def source_frame")]
    assert "justify-content:flex-start!important" in source


def test_breadcrumb_categories_and_initials():
    assert _page_category("Equipment Overview") == "Operational Data"
    assert _page_category("Lesson Bank") == "Operational Knowledge"
    assert _page_category("Admin / Super Admin") == "Administration"
    assert _page_category("OPERA-X Home") == "Home"
    assert _user_initials("John Akukuata") == "JA"
    assert _user_initials("OPERA-X Super Admin") == "OX"
    assert _user_initials("") == "OX"
