"""Capture a screenshot or short video from a URL or local HTML file.

Usage:
    # Screenshot from localhost
    python3 capture_screenshot.py --url http://localhost:3000 --out screenshot.png

    # Screenshot from HTML file
    python3 capture_screenshot.py --file ./dashboard/index.html --out screenshot.png

    # Screenshot of specific viewport size (mobile)
    python3 capture_screenshot.py --url http://localhost:3000 --width 390 --height 844 --out mobile.png

    # Short video (scrolls the page, 3-5 seconds)
    python3 capture_screenshot.py --url http://localhost:3000 --video --out demo.webm

    # Auto-detect: find dev server or HTML files in a project
    python3 capture_screenshot.py --detect --cwd /path/to/project

Requirements: playwright (chromium). Already installed if using koko-ship.
"""
import argparse
import json
import re
import subprocess
import sys
import time
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sys.exit("playwright not installed. run: pip install playwright && playwright install chromium")


def detect_sources(cwd: str) -> dict:
    """Auto-detect capturable sources in a project directory."""
    cwd = Path(cwd)
    sources = {"urls": [], "html_files": [], "dev_command": None}

    # Check package.json for dev server
    pkg = cwd / "package.json"
    if pkg.exists():
        try:
            d = json.loads(pkg.read_text())
            scripts = d.get("scripts", {})
            for key in ["dev", "start", "serve"]:
                if key in scripts:
                    cmd = scripts[key]
                    # Guess port
                    port_match = re.search(r"(?:port|PORT|p)\s*[=:]\s*(\d+)", cmd)
                    port = port_match.group(1) if port_match else "3000"
                    sources["urls"].append(f"http://localhost:{port}")
                    sources["dev_command"] = f"npm run {key}"
                    break
        except Exception:
            pass

    # Check for HTML files
    for pattern in ["index.html", "*.html", "**/*.html"]:
        for f in sorted(cwd.glob(pattern)):
            # Skip node_modules, .next, dist build artifacts
            parts = f.relative_to(cwd).parts
            if any(p in parts for p in ["node_modules", ".next", "dist", "build", ".git", ".venv", "venv", "__pycache__", ".bip-images"]):
                continue
            sources["html_files"].append(str(f))
            if len(sources["html_files"]) >= 10:
                break
        if sources["html_files"]:
            break

    # Check if localhost is already running — these go FIRST (real rendered UI)
    import urllib.request
    live_urls = []
    for port in [3000, 3001, 3456, 5173, 5174, 8080, 8000, 4200, 4321, 8888]:
        try:
            urllib.request.urlopen(f"http://localhost:{port}", timeout=1)
            live_urls.append(f"http://localhost:{port}")
        except Exception:
            pass

    # Live servers always take priority over static HTML files
    if live_urls:
        sources["urls"] = live_urls + [u for u in sources["urls"] if u not in live_urls]

    return sources


def capture_screenshot(
    url: str = None,
    file_path: str = None,
    out_path: str = "screenshot.png",
    width: int = 1280,
    height: int = 800,
    full_page: bool = True,
    wait_ms: int = 2000,
    device_scale: int = 2,
) -> str:
    """Capture a screenshot and return the output path."""
    if not url and not file_path:
        raise ValueError("provide --url or --file")

    target = url if url else f"file://{Path(file_path).resolve()}"
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page(
            viewport={"width": width, "height": height},
            device_scale_factor=device_scale,
        )
        page.goto(target, wait_until="networkidle", timeout=15000)
        page.wait_for_timeout(wait_ms)

        # Try waiting for fonts
        try:
            page.evaluate("document.fonts.ready")
        except Exception:
            pass

        if full_page:
            actual_height = page.evaluate("document.body.scrollHeight")
            page.set_viewport_size({"width": width, "height": min(actual_height, 4000)})
            page.wait_for_timeout(500)

        page.screenshot(path=str(out), full_page=full_page)
        browser.close()

    return str(out)


def capture_video(
    url: str = None,
    file_path: str = None,
    out_path: str = "demo.webm",
    width: int = 1280,
    height: int = 800,
    duration_sec: float = 4.0,
    scroll: bool = True,
) -> str:
    """Capture a short video (page load + optional scroll)."""
    if not url and not file_path:
        raise ValueError("provide --url or --file")

    target = url if url else f"file://{Path(file_path).resolve()}"
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    video_dir = out.parent / ".video-tmp"
    video_dir.mkdir(exist_ok=True)

    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        context = browser.new_context(
            viewport={"width": width, "height": height},
            record_video_dir=str(video_dir),
            record_video_size={"width": width, "height": height},
        )
        page = context.new_page()
        page.goto(target, wait_until="networkidle", timeout=15000)
        page.wait_for_timeout(1500)

        if scroll:
            total_height = page.evaluate("document.body.scrollHeight")
            viewport_height = height
            scroll_distance = total_height - viewport_height

            if scroll_distance > 0:
                steps = max(8, int(duration_sec * 4))
                step_size = scroll_distance / steps
                step_delay = (duration_sec * 1000) / steps

                for i in range(steps):
                    page.evaluate(f"window.scrollBy(0, {step_size})")
                    page.wait_for_timeout(int(step_delay))
            else:
                page.wait_for_timeout(int(duration_sec * 1000))
        else:
            page.wait_for_timeout(int(duration_sec * 1000))

        # Close to finalize video
        video_path = page.video.path()
        context.close()
        browser.close()

        # Move video to output path
        if video_path and Path(video_path).exists():
            Path(video_path).rename(out)

    # Cleanup temp dir
    try:
        import shutil
        shutil.rmtree(video_dir, ignore_errors=True)
    except Exception:
        pass

    return str(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", help="URL to capture (e.g. http://localhost:3000)")
    ap.add_argument("--file", help="local HTML file path")
    ap.add_argument("--out", default=None, help="output file path")
    ap.add_argument("--width", type=int, default=1280, help="viewport width (default 1280)")
    ap.add_argument("--height", type=int, default=800, help="viewport height (default 800)")
    ap.add_argument("--video", action="store_true", help="capture video instead of screenshot")
    ap.add_argument("--duration", type=float, default=4.0, help="video duration in seconds (default 4)")
    ap.add_argument("--no-scroll", action="store_true", help="don't scroll during video")
    ap.add_argument("--detect", action="store_true", help="auto-detect sources in project")
    ap.add_argument("--cwd", default=".", help="project directory for --detect")
    ap.add_argument("--full-page", action="store_true", default=True, help="capture full page (default true)")
    args = ap.parse_args()

    if args.detect:
        sources = detect_sources(args.cwd)
        print(json.dumps(sources, indent=2))
        return

    if not args.url and not args.file:
        print("error: provide --url or --file (or --detect to find sources)", file=sys.stderr)
        sys.exit(1)

    # Default output path
    if not args.out:
        if args.video:
            args.out = str(Path.cwd() / ".bip-images" / "capture.webm")
        else:
            args.out = str(Path.cwd() / ".bip-images" / "capture.png")

    if args.video:
        result = capture_video(
            url=args.url,
            file_path=args.file,
            out_path=args.out,
            width=args.width,
            height=args.height,
            duration_sec=args.duration,
            scroll=not args.no_scroll,
        )
    else:
        result = capture_screenshot(
            url=args.url,
            file_path=args.file,
            out_path=args.out,
            width=args.width,
            height=args.height,
        )

    print(f"saved → {result}")


if __name__ == "__main__":
    main()
