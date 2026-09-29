"""Capture UX screenshots at 1440px desktop and 390px mobile viewports (SPEC §14, Item 14)."""

import asyncio
import os
import sys
import threading
import time
from pathlib import Path
import uvicorn
from playwright.async_api import async_playwright

from kairos.api.app import app
from kairos.index.store import IndexStore

def run_server(server: uvicorn.Server) -> None:
    server.run()

async def main() -> None:
    # Ensure index store is built & loaded
    store = IndexStore()
    try:
        store.load()
    except Exception:
        store.build()
    app.state.index_store = store
    app.state.is_ready = True

    port = 8765
    config = uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning")
    server = uvicorn.Server(config)

    thread = threading.Thread(target=run_server, args=(server,), daemon=True)
    thread.start()
    time.sleep(2)

    output_dir = Path("docs/img/ux")
    output_dir.mkdir(parents=True, exist_ok=True)

    url = f"http://127.0.0.1:{port}"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        # 1. Desktop 1440px Assistant Mode
        print("Capturing Desktop 1440px Assistant Mode...")
        ctx_desktop = await browser.new_context(viewport={"width": 1440, "height": 900})
        page = await ctx_desktop.new_page()
        await page.goto(url, wait_until="networkidle")
        await page.wait_for_timeout(1000)
        await page.screenshot(path=str(output_dir / "assistant_desktop_1440px.png"), full_page=True)

        # 2. Desktop 1440px Inspector Mode
        print("Capturing Desktop 1440px Inspector Mode...")
        inspector_btn = page.locator("button:has-text('Show how it works')")
        if await inspector_btn.count() > 0:
            await inspector_btn.click()
            await page.wait_for_timeout(1000)
            await page.screenshot(path=str(output_dir / "inspector_desktop_1440px.png"), full_page=True)

        # 3. Mobile 390px Assistant Mode
        print("Capturing Mobile 390px Assistant Mode...")
        ctx_mobile = await browser.new_context(
            viewport={"width": 390, "height": 844},
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15"
        )
        page_m = await ctx_mobile.new_page()
        await page_m.goto(url, wait_until="networkidle")
        await page_m.wait_for_timeout(1000)
        await page_m.screenshot(path=str(output_dir / "assistant_mobile_390px.png"), full_page=True)

        await browser.close()

    print("Screenshots captured successfully in docs/img/ux/")

if __name__ == "__main__":
    asyncio.run(main())
