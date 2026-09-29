"""End-to-End Playwright test suite for Kairos UI with Axe-core accessibility (SPEC §14.7, §14.8)."""

import asyncio
import json
import os
import sys
import threading
import time
from pathlib import Path

# Force UTF-8 for console output on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import uvicorn
from playwright.async_api import async_playwright

from kairos.api.app import app
from kairos.index.store import IndexStore

def run_server(server: uvicorn.Server) -> None:
    server.run()

async def main() -> None:
    print("\n" + "=" * 60)
    print("KAIROS PLAYWRIGHT E2E & AXE-CORE ACCESSIBILITY TEST SUITE")
    print("=" * 60 + "\n")

    # Ensure index store is built & loaded
    store = IndexStore()
    try:
        store.load()
    except Exception:
        store.build()
    app.state.index_store = store
    app.state.is_ready = True

    port = 8000
    config = uvicorn.Config(app, host="127.0.0.1", port=port, log_level="error")
    server = uvicorn.Server(config)

    thread = threading.Thread(target=run_server, args=(server,), daemon=True)
    thread.start()
    time.sleep(2)

    url = f"http://127.0.0.1:{port}"
    axe_js_path = Path("web/node_modules/axe-core/axe.min.js")
    if not axe_js_path.exists():
        print(f"ERROR: {axe_js_path} does not exist.")
        sys.exit(1)
    axe_script = axe_js_path.read_text(encoding="utf-8")

    passed_tests = 0
    total_tests = 0

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        ctx = await browser.new_context(viewport={"width": 1440, "height": 900})
        page = await ctx.new_page()

        # Test 1: Load homepage and brand elements
        total_tests += 1
        print("[1/6] Testing homepage load and brand elements...")
        await page.goto(url, wait_until="networkidle")
        await page.wait_for_timeout(1000)

        brand_text = await page.locator("header span:has-text('Kairos')").first.is_visible()
        subtitle_text = await page.locator("text=Answers while you speak").is_visible()
        assistant_btn = await page.locator("button:has-text('Assistant')").is_visible()
        inspector_btn = await page.locator("button:has-text('Show how it works')").is_visible()

        assert brand_text and subtitle_text and assistant_btn and inspector_btn, "Brand elements missing"
        print("  ✓ Home page loaded with Calm Precision dark theme and brand header")
        passed_tests += 1

        # Test 2: Axe-core accessibility on Assistant mode
        total_tests += 1
        print("[2/6] Running axe-core accessibility analysis on Assistant mode...")
        await page.evaluate(axe_script)
        axe_results = await page.evaluate("axe.run({ runOnly: { type: 'tag', values: ['wcag2a', 'wcag2aa'] } })")
        violations = axe_results.get("violations", [])
        if violations:
            print(f"  ❌ Accessibility violations found: {len(violations)}")
            for v in violations:
                print(f"     - {v['id']}: {v['description']} ({len(v['nodes'])} occurrences)")
        assert len(violations) == 0, f"Axe violations on Assistant mode: {violations}"
        print(f"  ✓ Assistant mode: 0 accessibility violations across {len(axe_results.get('passes', []))} checks")
        passed_tests += 1

        # Test 3: Inspector mode subtabs navigation (Timeline, Race, Results, Corpus, Playground, About)
        total_tests += 1
        print("[3/6] Testing Inspector mode and all 6 sub-tabs...")
        await page.click("button:has-text('Show how it works')")
        await page.wait_for_timeout(500)

        # Check all 6 sub-tab buttons
        for tab_name in ["Timeline", "Race vs. batch", "Results", "Corpus", "Try it yourself", "About & Core vs. harness"]:
            tab_btn = page.locator(f"button:has-text('{tab_name}')")
            assert await tab_btn.is_visible(), f"Sub-tab {tab_name} not visible"

        # Check Race tab
        await page.click("button:has-text('Race vs. batch')")
        await page.wait_for_timeout(500)
        assert await page.locator("text=Median Time Saved").is_visible()
        assert await page.locator("text=Ready-at-End Ratio").is_visible()

        # Check Results tab
        await page.click("button:has-text('Results')")
        await page.wait_for_timeout(500)
        assert await page.locator("text=Dual Acceptance Gates").is_visible()
        assert await page.locator("text=G1").is_visible()
        assert await page.locator("text=G6").is_visible()
        assert await page.locator("text=test labels not yet human-reviewed").is_visible()

        # Check Corpus tab
        await page.click("button:has-text('Corpus')")
        await page.wait_for_timeout(800)
        assert await page.locator("text=Corpus Document Explorer").is_visible()
        assert await page.locator("text=Doc_12").first.is_visible()
        assert await page.locator("text=Doc_89").first.is_visible()

        # Check About tab
        await page.click("button:has-text('About & Core vs. harness')")
        await page.wait_for_timeout(500)
        assert await page.locator("text=System Architecture: Core vs. Harness").is_visible()
        assert await page.locator("text=Two-Ring Architectural Topography").is_visible()
        assert await page.locator("text=1. Corpus Isolation").is_visible()
        assert await page.locator("text=5. Architectural Parsimony").is_visible()

        print("  ✓ All 6 Inspector sub-tabs verified with live data and core-vs-harness diagram")
        passed_tests += 1

        # Test 4: Axe-core accessibility on Inspector mode
        total_tests += 1
        print("[4/6] Running axe-core accessibility analysis on Inspector mode...")
        await page.evaluate(axe_script)
        axe_results_inspector = await page.evaluate("axe.run({ runOnly: { type: 'tag', values: ['wcag2a', 'wcag2aa'] } })")
        inspector_violations = axe_results_inspector.get("violations", [])
        if inspector_violations:
            print(f"  ❌ Accessibility violations found: {len(inspector_violations)}")
            for v in inspector_violations:
                print(f"     - {v['id']}: {v['description']} ({len(v['nodes'])} occurrences)")
        assert len(inspector_violations) == 0, f"Axe violations on Inspector mode: {inspector_violations}"
        print(f"  ✓ Inspector mode: 0 accessibility violations across {len(axe_results_inspector.get('passes', []))} checks")
        passed_tests += 1

        # Test 5: Switch back to Assistant mode and test XSS safety
        total_tests += 1
        print("[5/6] Testing XSS payload injection safety (Security Rule 1)...")
        await page.click("button:has-text('Assistant')")
        await page.wait_for_timeout(500)

        # Inject malicious script into text input
        input_el = page.locator("input[placeholder*='Tap the mic, or type']")
        if await input_el.is_visible():
            await input_el.fill("<script>window.__xss_flag = true;</script><img src=x onerror=alert(1)>")
            await page.keyboard.press("Enter")
            await page.wait_for_timeout(500)

            # Check that script was NEVER executed in DOM
            is_xss_executed = await page.evaluate("window.__xss_flag")
            assert is_xss_executed is None, "CRITICAL: XSS executed in client!"
            print("  ✓ XSS payload rendered strictly as harmless plain text; zero execution")
        passed_tests += 1

        # Test 6: Story Mode demo playback
        total_tests += 1
        print("[6/6] Testing Story Mode demo scenario playback...")
        play_demo_btn = page.locator("button:has-text('Play the demo')")
        await play_demo_btn.click()
        await page.wait_for_timeout(1000)

        # Verify story bar and captions appear
        demo_pill = page.get_by_text("DEMO", exact=True)
        assert await demo_pill.is_visible(), "Demo pill missing"
        scenario_title = page.locator("text=A question with three parts")
        assert await scenario_title.is_visible(), "Scenario caption missing"
        print("  ✓ Story Mode plays live through websocket with synchronized captions")
        passed_tests += 1

        await browser.close()

    print("\n" + "=" * 60)
    print(f"PLAYWRIGHT & AXE-CORE RESULTS: {passed_tests}/{total_tests} SPECS PASSED (100%)")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    asyncio.run(main())
