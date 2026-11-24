#!/usr/bin/env python3
"""Measure warm authenticated page-navigation time for v3.10.1 and a target build."""
from __future__ import annotations

import argparse
import json
import os
import shutil
import socket
import statistics
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

from playwright.sync_api import Page, sync_playwright

PAGES = (
    ("Plant Overview", "Plant", "plant"),
    ("Equipment Overview", "Equipment", "equipment"),
    ("Operations Dashboard", "KPI's", "operations"),
    ("Admin / Super Admin", "Admin", "admin"),
    ("OPERA-X Home", "Home", "home"),
)


def _free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _wait(url: str, process: subprocess.Popen[str]) -> None:
    deadline = time.time() + 90
    while time.time() < deadline:
        if process.poll() is not None:
            raise RuntimeError(f"Streamlit exited with {process.returncode}")
        try:
            with urllib.request.urlopen(url, timeout=2) as response:
                if response.read().decode().strip() == "ok":
                    return
        except Exception:
            time.sleep(.3)
    raise TimeoutError(url)


def _login(page: Page, url: str) -> None:
    page.goto(url, wait_until="domcontentloaded", timeout=90_000)
    page.get_by_label("Username").fill("buadmin")
    page.get_by_role("textbox", name="Password").fill("ChangeMe!2026")
    page.get_by_role("button", name="Sign In", exact=True).click()
    page.get_by_text("Select Business Unit", exact=True).wait_for(timeout=60_000)
    page.get_by_role("button", name="Open OPERA-X", exact=True).click()
    page.get_by_text("Modules", exact=True).wait_for(timeout=120_000)


def _click_route(page: Page, full_name: str, short_name: str) -> None:
    if page.locator(".st-key-desktop_navigation:visible").count():
        desktop = page.locator(".st-key-desktop_navigation:visible")
        if desktop.get_by_test_id("stRadioOption").count():
            # v3.12 single-widget flat menu
            desktop.get_by_test_id("stRadioOption").filter(has_text=short_name).click(force=True)
        else:
            # v3.11.1 rendered eleven individual buttons
            desktop.get_by_role("button", name=("Dashboards" if short_name == "KPI's" else short_name), exact=True).click()
    else:
        # v3.10.1 baseline
        page.get_by_test_id("stRadioOption").filter(has_text=full_name).click(force=True)


def _wait_page(page: Page, key: str) -> None:
    if key == "home":
        page.get_by_text("Modules", exact=True).wait_for(timeout=180_000)
    elif key == "plant":
        page.get_by_text("Dashboard Template", exact=True).first.wait_for(timeout=180_000)
    elif key == "equipment":
        page.get_by_text("Unit / Section", exact=True).first.wait_for(timeout=180_000)
    elif key == "operations":
        page.get_by_text("Key Performance Indicators", exact=True).wait_for(timeout=180_000)
    elif key == "admin":
        page.get_by_role("radio", name="Business Units", exact=True).wait_for(timeout=180_000)
    page.locator("[data-testid='stStatusWidget']:visible").wait_for(state="hidden", timeout=180_000)
    page.evaluate("""() => new Promise((resolve) => {
      let timer;
      const done = () => { observer.disconnect(); resolve(true); };
      const observer = new MutationObserver(() => { clearTimeout(timer); timer = setTimeout(done, 600); });
      observer.observe(document.querySelector('[data-testid="stMainBlockContainer"]'), {subtree:true, childList:true, attributes:true, characterData:true});
      timer = setTimeout(done, 600);
    })""")


def _run_build(browser, root: Path, cycles: int) -> dict[str, object]:
    port = _free_port()
    temp = Path(tempfile.mkdtemp(prefix=f"operax-benchmark-{root.name}-"))
    data_root = temp / "data"
    shutil.copytree(root / "data", data_root)
    env = os.environ.copy()
    env["OPERA_DATA_DIR"] = str(data_root)
    command = [sys.executable, "-m", "streamlit", "run", str(root / "app.py"),
               "--server.headless=true", f"--server.port={port}", "--server.address=127.0.0.1"]
    process = subprocess.Popen(command, cwd=root, env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    samples = {key: [] for _, _, key in PAGES}
    try:
        _wait(f"http://127.0.0.1:{port}/_stcore/health", process)
        page = browser.new_page(viewport={"width": 1366, "height": 720})
        _login(page, f"http://127.0.0.1:{port}/")
        # First cycle warms Python, Streamlit, pandas and browser caches.
        for cycle in range(cycles + 1):
            for full_name, short_name, key in PAGES:
                start = time.perf_counter()
                _click_route(page, full_name, short_name)
                _wait_page(page, key)
                elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
                if cycle:
                    samples[key].append(elapsed_ms)
        page.close()
    finally:
        process.terminate()
        try:
            process.wait(timeout=15)
        except subprocess.TimeoutExpired:
            process.kill()
        shutil.rmtree(temp, ignore_errors=True)
    return {
        "samplesMs": samples,
        "medianMs": {key: round(statistics.median(values), 2) for key, values in samples.items()},
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--target", type=Path, required=True)
    parser.add_argument("--baseline-label", default="v3.10.1")
    parser.add_argument("--target-label", default="target")
    parser.add_argument("--cycles", type=int, default=3)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    executable = os.getenv("PLAYWRIGHT_CHROMIUM_EXECUTABLE")
    if not executable:
        matches = sorted(Path("/opt/pw-browsers").glob("chromium-*/chrome-linux*/chrome"), reverse=True)
        executable = str(matches[0]) if matches else ""
    if not executable:
        raise RuntimeError("Chromium executable not found")
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True, executable_path=executable, args=["--no-sandbox"])
        try:
            baseline = _run_build(browser, args.baseline.resolve(), args.cycles)
            target = _run_build(browser, args.target.resolve(), args.cycles)
        finally:
            browser.close()
    comparison = {}
    for key in baseline["medianMs"]:
        before, after = baseline["medianMs"][key], target["medianMs"][key]
        comparison[key] = {
            f"{args.baseline_label}Ms": before,
            f"{args.target_label}Ms": after,
            "changeMs": round(after - before, 2),
            "changePercent": round((after - before) / before * 100, 1) if before else None,
        }
    result = {"method": "Median of warm authenticated click-to-settled-page transitions", "cycles": args.cycles,
              "baselineLabel": args.baseline_label, "targetLabel": args.target_label,
              "baseline": baseline, "target": target, "comparison": comparison}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(comparison, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
