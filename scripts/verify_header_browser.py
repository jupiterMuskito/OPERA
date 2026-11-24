#!/usr/bin/env python3
"""Render and validate the real OPERA-X Streamlit header at release breakpoints.

Run from the repository root after installing Playwright:
    OPERAX_RUN_BROWSER_TESTS=1 python scripts/verify_header_browser.py

The script starts the actual app twice: once at / and once with Streamlit's
/operationaldashboard/ baseUrlPath. A non-zero exit means the release contract
failed. It writes screenshots and machine-readable measurements under
verification/v3.11.1/.
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

from playwright.sync_api import Page, sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "verification" / "v3.11.1"
WIDTHS = (1920, 1560, 1536, 1366, 1280, 1279)
DESKTOP_LABELS = (
    "Home", "Plant", "Equipment", "Dashboards", "Parameters", "Data Pipeline",
    "Optimization", "Event Log", "Lessons", "Risk Assessment", "Admin",
)
PAGES = (
    ("home", "Home", "OPERA-X Home", "OPERA-X Home"),
    ("equipment", "Equipment", "Equipment Overview", "Equipment Overview"),
    ("admin", "Admin", "Admin / Super Admin", "Admin / Super Admin"),
)


def _browser_executable() -> str | None:
    configured = os.getenv("PLAYWRIGHT_CHROMIUM_EXECUTABLE")
    if configured and Path(configured).is_file():
        return configured
    bundled = sorted(Path("/opt/pw-browsers").glob("chromium-*/chrome-linux*/chrome"), reverse=True)
    return str(bundled[0]) if bundled else None


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
    page.wait_for_timeout(900)


def _box(page: Page, selector: str) -> dict[str, float]:
    box = page.locator(f"{selector}:visible").first.bounding_box()
    if not box:
        raise AssertionError(f"Missing visible element: {selector}")
    return {key: round(float(value), 2) for key, value in box.items()}


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _measure(page: Page, path_name: str, page_slug: str, width: int) -> dict[str, object]:
    nav = _box(page, ".st-key-primary_navigation")
    crumb = _box(page, ".st-key-breadcrumb_strip")
    crumb_inner = _box(page, ".opera-breadcrumb")
    heading_locator = page.locator(":is(h1,h2,h3,h4,h5,h6):visible").first
    heading_locator.wait_for(state="visible", timeout=90_000)
    heading = heading_locator.bounding_box()
    if heading is None:  # A Streamlit rerun can replace the node during a viewport change.
        page.wait_for_timeout(500)
        heading = page.locator(":is(h1,h2,h3,h4,h5,h6):visible").first.bounding_box()
    _assert(heading is not None, f"{path_name}/{page_slug}/{width}: first page heading missing")

    desktop = page.locator(".st-key-desktop_navigation:visible").first
    mobile = page.locator(".st-key-mobile_navigation:visible").first
    desktop_visible = page.locator(".st-key-desktop_navigation:visible").count() > 0
    mobile_visible = page.locator(".st-key-mobile_navigation:visible").count() > 0
    expected_desktop = width >= 1280
    _assert(desktop_visible == expected_desktop, f"{path_name}/{page_slug}/{width}: wrong desktop visibility")
    _assert(mobile_visible != expected_desktop, f"{path_name}/{page_slug}/{width}: wrong compact-menu visibility")
    _assert(abs(nav["height"] - 52) <= 1, f"{path_name}/{page_slug}/{width}: nav is {nav['height']}px, expected 52px")
    _assert(39 <= crumb["height"] <= 42, f"{path_name}/{page_slug}/{width}: breadcrumb height is {crumb['height']}px")
    _assert(crumb_inner["y"] >= crumb["y"] - .5, f"{path_name}/{page_slug}/{width}: breadcrumb starts above its strip")
    _assert(crumb_inner["y"] + crumb_inner["height"] <= crumb["y"] + crumb["height"] + .5,
            f"{path_name}/{page_slug}/{width}: breadcrumb is clipped")
    _assert(float(heading["y"]) >= crumb["y"] + crumb["height"] - .5,
            f"{path_name}/{page_slug}/{width}: first heading overlaps breadcrumb")

    carets = page.locator(
        ".st-key-notifications_menu [data-testid='stIconMaterial']:visible, "
        ".st-key-user_menu [data-testid='stIconMaterial']:visible"
    ).filter(has_text="expand_more")
    visible_carets = carets.count()
    _assert(visible_carets == 0, f"{path_name}/{page_slug}/{width}: visible popover caret remains")

    body_size = page.evaluate("({scroll:document.documentElement.scrollWidth, client:document.documentElement.clientWidth})")
    _assert(body_size["scroll"] <= body_size["client"] + 1, f"{path_name}/{page_slug}/{width}: horizontal overflow")
    visible_exceptions = page.locator("[data-testid='stException']:visible").count()
    _assert(visible_exceptions == 0, f"{path_name}/{page_slug}/{width}: Streamlit exception is visible")

    rows: list[float] = []
    packed_width = None
    empty_before_bell = None
    if expected_desktop:
        buttons = desktop.get_by_role("button")
        _assert(buttons.count() == len(DESKTOP_LABELS), f"{path_name}/{page_slug}/{width}: desktop labels missing")
        labels = [text.strip() for text in buttons.all_inner_texts()]
        _assert(labels == list(DESKTOP_LABELS), f"{path_name}/{page_slug}/{width}: wrong labels/order: {labels}")
        boxes = [buttons.nth(index).bounding_box() for index in range(buttons.count())]
        _assert(all(boxes), f"{path_name}/{page_slug}/{width}: hidden flat-menu item")
        rows = sorted({round(float(box["y"]), 1) for box in boxes if box})
        _assert(len(rows) == 1, f"{path_name}/{page_slug}/{width}: menu wrapped to {len(rows)} rows")
        packed_width = round(float(boxes[-1]["x"] + boxes[-1]["width"] - boxes[0]["x"]), 2)
        _assert(packed_width <= 1040, f"{path_name}/{page_slug}/{width}: menu is not packed ({packed_width}px)")
        bell = _box(page, ".st-key-notifications_menu button")
        empty_before_bell = round(bell["x"] - (boxes[-1]["x"] + boxes[-1]["width"]), 2)
        _assert(empty_before_bell >= 8, f"{path_name}/{page_slug}/{width}: no flexible space before bell")
    else:
        compact = _box(page, ".st-key-mobile_navigation [data-testid='stPopoverButton']")
        _assert(compact["width"] <= 42, f"{path_name}/{page_slug}/{width}: compact menu is too wide")
        _assert(compact["x"] <= nav["x"] + 62, f"{path_name}/{page_slug}/{width}: compact menu is not left aligned")

    return {
        "path": path_name, "page": page_slug, "width": width,
        "devicePixelRatio": page.evaluate("devicePixelRatio"),
        "desktopVisible": desktop_visible, "mobileVisible": mobile_visible,
        "nav": nav, "breadcrumb": crumb, "breadcrumbContent": crumb_inner,
        "heading": {key: round(float(value), 2) for key, value in heading.items()},
        "buttonRows": rows, "packedMenuWidth": packed_width,
        "emptyBeforeBell": empty_before_bell, "horizontalOverflow": body_size,
        "visibleExceptions": visible_exceptions,
    }


def _run_path(browser, base_path: str, capture: bool) -> list[dict[str, object]]:
    path_name = base_path or "root"
    port = _free_port()
    temp_root = Path(tempfile.mkdtemp(prefix=f"operax-{path_name}-"))
    data_root = temp_root / "data"
    shutil.copytree(ROOT / "data", data_root)
    command = [
        sys.executable, "-m", "streamlit", "run", str(ROOT / "app.py"),
        "--server.headless=true", f"--server.port={port}", "--server.address=127.0.0.1",
    ]
    if base_path:
        command.append(f"--server.baseUrlPath={base_path}")
    env = os.environ.copy()
    env["OPERA_DATA_DIR"] = str(data_root)
    process = subprocess.Popen(command, cwd=ROOT, env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    prefix = f"/{base_path}" if base_path else ""
    health = f"http://127.0.0.1:{port}{prefix}/_stcore/health"
    url = f"http://127.0.0.1:{port}{prefix}/"
    results: list[dict[str, object]] = []
    try:
        _wait_for_health(health, process)
        page = browser.new_page(viewport={"width": 1280, "height": 700}, device_scale_factor=1)
        _login(page, url)
        page_dir = OUT / path_name
        page_dir.mkdir(parents=True, exist_ok=True)
        for page_slug, button_name, breadcrumb_name, heading_name in PAGES:
            page.set_viewport_size({"width": 1280, "height": 700})
            if page_slug != "home":
                page.locator(".st-key-desktop_navigation:visible").get_by_role("button", name=button_name, exact=True).click()
                page.locator(".opera-breadcrumb .page", has_text=breadcrumb_name).wait_for(timeout=90_000)
            page.get_by_role("heading", name=heading_name, exact=True).wait_for(timeout=120_000)
            page.wait_for_timeout(900)
            for width in WIDTHS:
                page.set_viewport_size({"width": width, "height": 700})
                page.wait_for_timeout(350)
                result = _measure(page, path_name, page_slug, width)
                results.append(result)
                if capture:
                    page.screenshot(path=str(page_dir / f"{page_slug}_{width}px.png"), full_page=False)
            if page_slug != "home":
                page.set_viewport_size({"width": 1280, "height": 700})
                page.locator(".st-key-desktop_navigation:visible").get_by_role("button", name="Home", exact=True).click()
                page.locator(".opera-breadcrumb .page", has_text="OPERA-X Home").wait_for(timeout=90_000)
                page.wait_for_timeout(700)
        page.close()
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
    executable = _browser_executable()
    if not executable:
        raise RuntimeError("Chromium not found; set PLAYWRIGHT_CHROMIUM_EXECUTABLE")
    OUT.mkdir(parents=True, exist_ok=True)
    all_results: list[dict[str, object]] = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True, executable_path=executable, args=["--no-sandbox"])
        try:
            for base_path in ("", "operationaldashboard"):
                all_results.extend(_run_path(browser, base_path, capture=not args.check_only))
        finally:
            browser.close()
    (OUT / "header_measurements.json").write_text(json.dumps(all_results, indent=2), encoding="utf-8")
    print(f"PASS: {len(all_results)} real-app header checks across root and /operationaldashboard/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
