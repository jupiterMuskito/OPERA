#!/usr/bin/env python3
"""Cross-browser release verification for the OPERA-X authenticated UI.

Runs the real Streamlit app at / and /operationaldashboard/ in Chromium and
Microsoft Edge.  It verifies the 1100 CSS-pixel breakpoint, the primary
1272px/scrollbar target, a 1.5 device scale factor, one-row navigation, control
borders and all application routes. Screenshots and measurements are written to
verification/v3.12.0/.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

from playwright.sync_api import Browser, Page, sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "verification" / "v3.12.0"
WIDTHS = (1920, 1536, 1366, 1280, 1272, 1099)
DESKTOP_LABELS = (
    "Home", "Plant", "Equipment", "KPI's", "Parameters", "Data Pipeline",
    "Optimization", "Event Log", "Lessons", "Risk Assessment", "Admin",
)
PAGES = (
    ("home", "Home", "OPERA-X Home"),
    ("plant", "Plant", "Plant Overview"),
    ("equipment", "Equipment", "Equipment Overview"),
    ("kpis", "KPI's", "Operations Dashboard"),
    ("parameters", "Parameters", "Operating Parameters"),
    ("pipeline", "Data Pipeline", "Operational Data Pipeline"),
    ("optimization", "Optimization", "Process Optimization"),
    ("events", "Event Log", "Event Log"),
    ("lessons", "Lessons", "Lesson Bank"),
    ("risk", "Risk Assessment", "Job Risk Assessment"),
    ("admin", "Admin", "Admin / Super Admin"),
)


def _executables() -> dict[str, str]:
    configured = os.getenv("PLAYWRIGHT_CHROMIUM_EXECUTABLE")
    bundled = sorted(Path("/opt/pw-browsers").glob("chromium-*/chrome-linux*/chrome"), reverse=True)
    chrome = configured if configured and Path(configured).is_file() else str(bundled[0]) if bundled else ""
    edge = shutil.which("microsoft-edge") or shutil.which("microsoft-edge-stable") or ""
    missing = [name for name, value in {"chrome": chrome, "edge": edge}.items() if not value]
    if missing:
        raise RuntimeError("Missing browser executable(s): " + ", ".join(missing))
    return {"chrome": chrome, "edge": edge}


def _free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _wait_for_health(url: str, process: subprocess.Popen[str], timeout: float = 90) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        if process.poll() is not None:
            raise RuntimeError(f"Streamlit exited early with code {process.returncode}")
        try:
            with urllib.request.urlopen(url, timeout=2) as response:
                if response.read().decode().strip() == "ok":
                    return
        except Exception:
            time.sleep(.4)
    raise RuntimeError(f"Streamlit health check timed out: {url}")


def _login(page: Page, url: str) -> None:
    page.goto(url, wait_until="domcontentloaded", timeout=90_000)
    page.get_by_label("Username").fill("buadmin")
    page.get_by_role("textbox", name="Password").fill("ChangeMe!2026")
    page.get_by_role("button", name="Sign In", exact=True).click()
    page.get_by_text("Select Business Unit", exact=True).wait_for(timeout=60_000)
    page.get_by_role("button", name="Open OPERA-X", exact=True).click()
    page.locator(".st-key-brand_ribbon").wait_for(timeout=90_000)
    page.locator(".opera-breadcrumb .page").wait_for(timeout=60_000)
    # Reproduce the user's real page: a persistent vertical scrollbar removes
    # roughly 15-17 CSS pixels from the usable 1272px Edge viewport.
    page.add_style_tag(content="html{overflow-y:scroll!important}.stApp{width:calc(100% - 17px)!important}")
    page.wait_for_timeout(700)


def _box(page: Page, selector: str) -> dict[str, float]:
    box = page.locator(f"{selector}:visible").first.bounding_box()
    if not box:
        raise AssertionError(f"Missing visible element: {selector}")
    return {key: round(float(value), 2) for key, value in box.items()}


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _measure(page: Page, browser_name: str, path_name: str, width: int, dsf: float) -> dict[str, object]:
    nav = _box(page, ".st-key-primary_navigation")
    desktop = page.locator(".st-key-desktop_navigation:visible").first
    desktop_visible = page.locator(".st-key-desktop_navigation:visible").count() > 0
    mobile_visible = page.locator(".st-key-mobile_navigation:visible").count() > 0
    expected_desktop = width >= 1100
    _assert(desktop_visible == expected_desktop, f"{browser_name}/{path_name}/{width}: wrong desktop visibility")
    _assert(mobile_visible != expected_desktop, f"{browser_name}/{path_name}/{width}: wrong compact-menu visibility")
    _assert(abs(nav["height"] - 52) <= 1, f"{browser_name}/{path_name}/{width}: nav is {nav['height']}px")

    viewport = page.evaluate("""() => ({
      innerWidth: window.innerWidth,
      outerWidth: window.outerWidth,
      clientWidth: document.documentElement.clientWidth,
      scrollWidth: document.documentElement.scrollWidth,
      clientHeight: document.documentElement.clientHeight,
      scrollHeight: document.documentElement.scrollHeight,
      appUsableWidth: document.querySelector('.stApp')?.getBoundingClientRect().width,
      dpr: window.devicePixelRatio,
      mediaCompact: matchMedia('(max-width:1099px)').matches
    })""")
    _assert(viewport["scrollWidth"] <= viewport["clientWidth"] + 1, f"{browser_name}/{path_name}/{width}: horizontal overflow")
    if width == 1272:
        _assert(viewport["appUsableWidth"] <= viewport["innerWidth"] - 16,
                f"{browser_name}/{path_name}/1272: scrollbar gutter was not emulated")

    packed_width = None
    rows: list[float] = []
    if expected_desktop:
        options = desktop.get_by_test_id("stRadioOption")
        labels = [text.strip() for text in options.all_inner_texts()]
        _assert(labels == list(DESKTOP_LABELS), f"{browser_name}/{path_name}/{width}: labels/order {labels}")
        boxes = [options.nth(index).bounding_box() for index in range(options.count())]
        _assert(all(boxes), f"{browser_name}/{path_name}/{width}: hidden flat-menu item")
        rows = sorted({round(float(box["y"]), 1) for box in boxes if box})
        _assert(len(rows) == 1, f"{browser_name}/{path_name}/{width}: menu wrapped")
        packed_width = round(float(boxes[-1]["x"] + boxes[-1]["width"] - boxes[0]["x"]), 2)
        menu_box = desktop.bounding_box()
        _assert(menu_box is not None and packed_width <= menu_box["width"] + 1,
                f"{browser_name}/{path_name}/{width}: menu {packed_width}px exceeds slot")
        font_sizes = {page.evaluate("el => getComputedStyle(el).fontSize", options.nth(i).element_handle()) for i in range(options.count())}
        _assert(all(float(value.removesuffix("px")) >= 14 for value in font_sizes),
                f"{browser_name}/{path_name}/{width}: nav font below 14px: {font_sizes}")
    else:
        compact = _box(page, ".st-key-mobile_navigation button")
        _assert(compact["width"] <= 42, f"{browser_name}/{path_name}/{width}: compact menu too wide")

    _assert(page.locator("[data-testid='stException']:visible").count() == 0,
            f"{browser_name}/{path_name}/{width}: visible Streamlit exception")
    return {
        "browser": browser_name, "path": path_name, "width": width,
        "requestedDeviceScaleFactor": dsf, "viewport": viewport,
        "desktopVisible": desktop_visible, "mobileVisible": mobile_visible,
        "buttonRows": rows, "packedMenuWidth": packed_width,
    }


def _assert_content_borders(page: Page, label: str) -> dict[str, int]:
    selectors = {
        "select": "[data-testid='stMainBlockContainer'] [data-testid='stSelectbox']:visible [data-rac][role='group']:visible",
        "multiselect": "[data-testid='stMainBlockContainer'] [data-testid='stMultiSelect']:visible [data-rac][role='group']:visible",
        "input": "[data-testid='stMainBlockContainer'] :is([data-testid='stDateInputField'],[data-testid='stTimeInputField'],[data-testid='stTextInputRootElement'],[data-testid='stNumberInputContainer']):visible",
        "uploader": "[data-testid='stMainBlockContainer'] [data-testid='stFileUploaderDropzone']:visible",
        "expander": "[data-testid='stMainBlockContainer'] [data-testid='stExpander']:visible details",
    }
    counts: dict[str, int] = {}
    for name, selector in selectors.items():
        locator = page.locator(selector)
        counts[name] = locator.count()
        for index in range(locator.count()):
            border = page.evaluate("el => getComputedStyle(el).borderTopWidth", locator.nth(index).element_handle())
            _assert(float(border.removesuffix("px")) >= 1, f"{label}: border missing for {name} #{index + 1}")
    return counts


def _wait_page_content(page: Page, slug: str) -> None:
    markers = {
        "home": ("text", "Modules"),
        "plant": ("text", "Dashboard Template"),
        "equipment": ("text", "Dashboard Template"),
        "kpis": ("text", "Key Performance Indicators"),
        "parameters": ("text", "Quality / QAQC"),
        "pipeline": ("radio", "Manual Entry"),
        "optimization": ("text", "Bounded Response Optimization"),
        "events": ("text", "View Event Log"),
        "lessons": ("text", "Review Lessons"),
        "risk": ("text", "Job Risk Assessment"),
        "admin": ("radio", "Business Units"),
    }
    kind, name = markers[slug]
    locator = page.get_by_role("radio", name=name, exact=True) if kind == "radio" else page.get_by_text(name, exact=True).first
    locator.wait_for(timeout=180_000)
    page.locator("[data-testid='stStatusWidget']:visible").wait_for(state="hidden", timeout=180_000)
    page.evaluate("""() => new Promise((resolve) => {
      let timer;
      const done = () => { observer.disconnect(); resolve(true); };
      const observer = new MutationObserver(() => { clearTimeout(timer); timer = setTimeout(done, 600); });
      observer.observe(document.querySelector('[data-testid="stMainBlockContainer"]'), {subtree:true, childList:true, attributes:true, characterData:true});
      timer = setTimeout(done, 600);
    })""")


def _audit_pages(page: Page, browser_name: str, output_dir: Path, capture: bool) -> list[dict[str, object]]:
    page.set_viewport_size({"width": 1366, "height": 720})
    results: list[dict[str, object]] = []
    for slug, button_name, breadcrumb_name in PAGES:
        current = page.locator(".opera-breadcrumb .page").inner_text().strip()
        if current != breadcrumb_name:
            page.locator(".st-key-desktop_navigation:visible").get_by_test_id("stRadioOption").filter(has_text=button_name).click(force=True)
            page.locator(".opera-breadcrumb .page", has_text=breadcrumb_name).wait_for(timeout=120_000)
        _wait_page_content(page, slug)
        _assert(page.locator("[data-testid='stException']:visible").count() == 0,
                f"{browser_name}/{slug}: visible Streamlit exception")
        borders = _assert_content_borders(page, f"{browser_name}/{slug}")
        title_count = page.locator("[data-testid='stMainBlockContainer'] h1:visible").count()
        _assert(title_count == 0, f"{browser_name}/{slug}: leftover page-title element is visible")
        if capture:
            page.screenshot(path=str(output_dir / f"page_{slug}_1366px.png"), full_page=False)
        results.append({"browser": browser_name, "page": slug, "contentBorders": borders, "visibleH1": title_count})
    return results


def _audit_header_actions(page: Page, browser_name: str) -> dict[str, object]:
    page.set_viewport_size({"width": 1366, "height": 720})
    page.locator(".st-key-user_menu button:visible").click()
    page.locator(".st-key-header_user_panel:visible").wait_for(timeout=60_000)
    for name in ("Change Business Unit", "Help", "Sign Out"):
        page.locator(".st-key-header_user_panel").get_by_role("button", name=name, exact=True).wait_for()
    page.locator(".st-key-user_menu button:visible").click()
    page.locator(".st-key-header_user_panel").wait_for(state="hidden", timeout=60_000)

    page.locator(".st-key-notifications_menu button:visible").click()
    page.locator(".st-key-header_notice_panel:visible").wait_for(timeout=60_000)
    page.locator(".st-key-notifications_menu button:visible").click()
    page.locator(".st-key-header_notice_panel").wait_for(state="hidden", timeout=60_000)

    page.set_viewport_size({"width": 1099, "height": 720})
    page.locator(".st-key-mobile_navigation button:visible").click()
    page.locator(".st-key-header_mobile_panel:visible").get_by_label("Page").wait_for(timeout=60_000)
    page.locator(".st-key-mobile_navigation button:visible").click()
    page.locator(".st-key-header_mobile_panel").wait_for(state="hidden", timeout=60_000)
    return {"browser": browser_name, "headerActions": "pass"}


def _run_path(browser: Browser, browser_name: str, base_path: str, capture: bool) -> list[dict[str, object]]:
    path_name = base_path or "root"
    port = _free_port()
    temp_root = Path(tempfile.mkdtemp(prefix=f"operax-{browser_name}-{path_name}-"))
    data_root = temp_root / "data"
    shutil.copytree(ROOT / "data", data_root)
    command = [sys.executable, "-m", "streamlit", "run", str(ROOT / "app.py"),
               "--server.headless=true", f"--server.port={port}", "--server.address=127.0.0.1"]
    if base_path:
        command.append(f"--server.baseUrlPath={base_path}")
    env = os.environ.copy()
    env["OPERA_DATA_DIR"] = str(data_root)
    process = subprocess.Popen(command, cwd=ROOT, env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    prefix = f"/{base_path}" if base_path else ""
    health = f"http://127.0.0.1:{port}{prefix}/_stcore/health"
    url = f"http://127.0.0.1:{port}{prefix}/"
    output_dir = OUT / browser_name / path_name
    output_dir.mkdir(parents=True, exist_ok=True)
    results: list[dict[str, object]] = []
    try:
        _wait_for_health(health, process)
        page = browser.new_page(viewport={"width": 1280, "height": 700}, device_scale_factor=1)
        _login(page, url)
        for width in WIDTHS:
            page.set_viewport_size({"width": width, "height": 700})
            page.wait_for_timeout(400)
            results.append(_measure(page, browser_name, path_name, width, 1.0))
            if capture:
                page.screenshot(path=str(output_dir / f"home_{width}px.png"), full_page=False)
        if path_name == "root":
            results.extend(_audit_pages(page, browser_name, output_dir, capture))
            results.append(_audit_header_actions(page, browser_name))
        page.close()

        scaled = browser.new_page(viewport={"width": 1280, "height": 700}, device_scale_factor=1.5)
        _login(scaled, url)
        results.append(_measure(scaled, browser_name, path_name, 1280, 1.5))
        if capture:
            scaled.screenshot(path=str(output_dir / "home_1280px_dsf1.5.png"), full_page=False)
        scaled.close()
    finally:
        process.terminate()
        try:
            process.wait(timeout=15)
        except subprocess.TimeoutExpired:
            process.kill()
        shutil.rmtree(temp_root, ignore_errors=True)
    return results


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check-only", action="store_true", help="Run assertions without writing screenshots")
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    all_results: list[dict[str, object]] = []
    with sync_playwright() as playwright:
        for browser_name, executable in _executables().items():
            browser = playwright.chromium.launch(headless=True, executable_path=executable, args=["--no-sandbox"])
            try:
                for base_path in ("", "operationaldashboard"):
                    all_results.extend(_run_path(browser, browser_name, base_path, capture=not args.check_only))
            finally:
                browser.close()
    (OUT / "browser_measurements.json").write_text(json.dumps(all_results, indent=2), encoding="utf-8")
    print(f"PASS: {len(all_results)} Chrome/Edge checks across root and /operationaldashboard/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
