"""Run Lighthouse audit on Kairos web app for Desktop and Mobile (SPEC §14.7)."""

import json
import os
import subprocess
import sys
import threading
import time
from pathlib import Path
import uvicorn

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from kairos.api.app import app
from kairos.index.store import IndexStore

def run_server(server: uvicorn.Server) -> None:
    server.run()

def main() -> None:
    print("\n" + "=" * 60)
    print("KAIROS LIGHTHOUSE PERFORMANCE & ACCESSIBILITY AUDIT")
    print("=" * 60 + "\n")

    # 1. Start Kairos app server
    store = IndexStore()
    try:
        store.load()
    except Exception:
        store.build()
    app.state.index_store = store
    app.state.is_ready = True

    port = 8765
    from kairos.config import load_config
    settings = load_config()
    settings.security.allowed_origins.extend([f"http://127.0.0.1:{port}", f"http://localhost:{port}", f"http://host.docker.internal:{port}"])

    config = uvicorn.Config(app, host="0.0.0.0", port=port, log_level="error")
    server = uvicorn.Server(config)

    thread = threading.Thread(target=run_server, args=(server,), daemon=True)
    thread.start()
    time.sleep(2)

    # 2. Locate Chrome binary
    chrome_path = Path(
        r"C:\Users\Chiranjeevi U Jadhav\AppData\Local\ms-playwright\chromium-1243\chrome-win64\chrome.exe"
    )
    if not chrome_path.exists():
        chrome_path = Path(
            r"C:\Users\Chiranjeevi U Jadhav\AppData\Local\ms-playwright\chromium-1228\chrome-win64\chrome.exe"
        )
    if not chrome_path.exists():
        print(f"Error: Chrome binary not found at {chrome_path}")
        sys.exit(1)

    print(f"Launching headless Chrome from: {chrome_path}")
    chrome_proc = subprocess.Popen([
        str(chrome_path),
        "--headless=new",
        "--remote-debugging-address=0.0.0.0",
        "--remote-debugging-port=9222",
        "--remote-allow-origins=*",
        "--disable-gpu",
        "--no-sandbox",
        "--disable-dev-shm-usage",
    ])
    time.sleep(2)

    docs_lh_dir = Path("docs/lighthouse")
    docs_lh_dir.mkdir(parents=True, exist_ok=True)

    try:
        # 3. Run Desktop Lighthouse audit
        print("\n[1/2] Running Desktop Lighthouse audit...")
        desktop_cmd = [
            "docker", "run", "--rm",
            "--add-host=host.docker.internal:host-gateway",
            "-v", f"{Path.cwd().resolve()}:/app",
            "-w", "/app/web",
            "node:20-slim",
            "node", "/app/web/lighthouse_runner.mjs",
            f"http://127.0.0.1:{port}",
            "desktop",
            "/app/docs/lighthouse/desktop",
        ]
        res_d = subprocess.run(desktop_cmd, capture_output=True, text=True)
        print(f"Desktop audit finished (code {res_d.returncode})")
        if res_d.stdout:
            print(res_d.stdout)
        if res_d.returncode != 0 and res_d.stderr:
            print("Desktop stderr:", res_d.stderr[:500])

        # 4. Run Mobile Lighthouse audit
        print("\n[2/2] Running Mobile Lighthouse audit...")
        mobile_cmd = [
            "docker", "run", "--rm",
            "--add-host=host.docker.internal:host-gateway",
            "-v", f"{Path.cwd().resolve()}:/app",
            "-w", "/app/web",
            "node:20-slim",
            "node", "/app/web/lighthouse_runner.mjs",
            f"http://127.0.0.1:{port}",
            "mobile",
            "/app/docs/lighthouse/mobile",
        ]
        res_m = subprocess.run(mobile_cmd, capture_output=True, text=True)
        print(f"Mobile audit finished (code {res_m.returncode})")
        if res_m.stdout:
            print(res_m.stdout)
        if res_m.returncode != 0 and res_m.stderr:
            print("Mobile stderr:", res_m.stderr[:500])

    finally:
        chrome_proc.terminate()

    # 5. Read and report scores
    desktop_json = docs_lh_dir / "desktop.report.json"
    mobile_json = docs_lh_dir / "mobile.report.json"

    print("\n" + "=" * 60)
    print("LIGHTHOUSE AUDIT RESULTS SUMMARY (TARGET: >= 90)")
    print("=" * 60)

    if desktop_json.exists():
        d_data = json.loads(desktop_json.read_text(encoding="utf-8"))
        d_cats = d_data.get("categories", {})
        d_perf = int((d_cats.get("performance", {}).get("score") or 0) * 100)
        d_a11y = int((d_cats.get("accessibility", {}).get("score") or 0) * 100)
        d_best = int((d_cats.get("best-practices", {}).get("score") or 0) * 100)
        print(f"\nDesktop Scores:")
        print(f"  - Performance:    {d_perf}/100 {'✓' if d_perf >= 90 else '⚠'}")
        print(f"  - Accessibility:  {d_a11y}/100 {'✓' if d_a11y >= 90 else '⚠'}")
        print(f"  - Best Practices: {d_best}/100 {'✓' if d_best >= 90 else '⚠'}")
        print(f"  Report: docs/lighthouse/desktop.report.html")

    if mobile_json.exists():
        m_data = json.loads(mobile_json.read_text(encoding="utf-8"))
        m_cats = m_data.get("categories", {})
        m_perf = int((m_cats.get("performance", {}).get("score") or 0) * 100)
        m_a11y = int((m_cats.get("accessibility", {}).get("score") or 0) * 100)
        m_best = int((m_cats.get("best-practices", {}).get("score") or 0) * 100)
        print(f"\nMobile Scores:")
        print(f"  - Performance:    {m_perf}/100 {'✓' if m_perf >= 90 else '⚠'}")
        print(f"  - Accessibility:  {m_a11y}/100 {'✓' if m_a11y >= 90 else '⚠'}")
        print(f"  - Best Practices: {m_best}/100 {'✓' if m_best >= 90 else '⚠'}")
        print(f"  Report: docs/lighthouse/mobile.report.html")

    print("\n" + "=" * 60 + "\n")

if __name__ == "__main__":
    main()
