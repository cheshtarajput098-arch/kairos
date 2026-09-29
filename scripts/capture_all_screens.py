"""Launch Chrome in headless debugging mode and capture all 4 screen screenshots + mid-answer + axe-core."""

import json
import os
import subprocess
import sys
import time
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

def main() -> None:
    # Locate Chrome binary
    chrome_path = Path(
        r"C:\Users\Chiranjeevi U Jadhav\AppData\Local\ms-playwright\chromium-1243\chrome-win64\chrome.exe"
    )
    if not chrome_path.exists():
        chrome_path = Path(
            r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        )
    if not chrome_path.exists():
        print(f"Error: Chrome binary not found")
        sys.exit(1)

    print(f"Launching headless Chrome from: {chrome_path}")
    temp_dir = Path(os.environ.get("TEMP", "C:/Temp")) / "kairos_chrome_debug"
    temp_dir.mkdir(parents=True, exist_ok=True)

    chrome_proc = subprocess.Popen([
        str(chrome_path),
        "--headless=new",
        "--remote-debugging-address=0.0.0.0",
        "--remote-debugging-port=9222",
        "--remote-allow-origins=*",
        f"--user-data-dir={temp_dir}",
        "--disable-gpu",
        "--no-sandbox",
        "--disable-dev-shm-usage",
    ])
    time.sleep(3)

    try:
        cmd = [
            "docker", "run", "--rm",
            "--add-host=host.docker.internal:host-gateway",
            "-v", f"{Path.cwd().resolve()}:/app",
            "-w", "/app/web",
            "node:20-slim",
            "node", "/app/web/capture_screenshots.mjs",
            "http://127.0.0.1:8765",
        ]
        print("Running capture_screenshots.mjs in node:20-slim container...")
        res = subprocess.run(cmd, capture_output=True, text=True)
        print(f"Runner exited with code {res.returncode}")
        if res.stdout:
            print(res.stdout)
        if res.stderr:
            print("Stderr:", res.stderr[:500])
        if res.returncode != 0:
            sys.exit(res.returncode)
    finally:
        chrome_proc.terminate()

    print("\nDone capturing screenshots and axe checks.")

if __name__ == "__main__":
    main()
