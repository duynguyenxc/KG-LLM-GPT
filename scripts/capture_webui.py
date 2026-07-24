"""Capture web-UI pages to PNG for embedding in the report.

Uses Selenium with a headless Chromium/Edge driver (Selenium Manager resolves the
driver automatically). The knowledge-graph page runs a physics layout, so we wait for
it to settle before the shot. Output: outputs/screenshots/webui_*.png
"""
from __future__ import annotations

import time
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By

ROOT = Path(__file__).resolve().parents[1]
SHOT = ROOT / "outputs" / "screenshots"
SHOT.mkdir(parents=True, exist_ok=True)
BASE = "http://127.0.0.1:8000"


def _driver():
    for factory, opts_cls in (
        (webdriver.Chrome, webdriver.ChromeOptions),
        (webdriver.Edge, webdriver.EdgeOptions),
    ):
        try:
            o = opts_cls()
            o.add_argument("--headless=new")
            o.add_argument("--window-size=1500,1250")
            o.add_argument("--hide-scrollbars")
            o.add_argument("--force-device-scale-factor=1")
            return factory(options=o)
        except Exception as e:  # noqa: BLE001
            print(f"  {factory.__name__} unavailable: {str(e)[:80]}")
    raise SystemExit("No Chromium/Edge webdriver available.")


def shot(driver, path: str, out: str, wait: float, settle_selector: str | None = None):
    driver.get(BASE + path)
    time.sleep(wait)
    if settle_selector:
        try:
            driver.find_element(By.CSS_SELECTOR, settle_selector)
        except Exception:  # noqa: BLE001
            pass
    dest = SHOT / out
    driver.save_screenshot(str(dest))
    print(f"  saved {dest.name} ({dest.stat().st_size} bytes)")


def main():
    d = _driver()
    try:
        # Graph: let the vis-network physics settle before the shot.
        shot(d, "/graph", "webui_graph.png", wait=8.0, settle_selector="canvas")
        shot(d, "/workflow", "webui_workflow.png", wait=2.5)
        shot(d, "/", "webui_control_room.png", wait=2.0)
    finally:
        d.quit()


if __name__ == "__main__":
    main()
    print("done")
