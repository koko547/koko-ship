"""Generate a koko-ship card PNG from a JSON payload.

Usage:
    python3 generate_image.py --slug <slug> --json '<payload>'
    python3 generate_image.py --slug <slug> --json-file <path>
    python3 generate_image.py --slug <slug>            # uses bundled day1 demo

Output: <cwd>/.bip-images/<slug>.png

Payload schema:
{
  "label": "DAY 1 OF KOKO-SHIP",     # small caps header
  "title": "voice profile, built from data",
  "subtitle": "fed viral patterns + my own writing into one ruleset",
  "stats": [                          # 1-4 items
    {"num": "79", "label": "viral BIP posts", "detail": "filter: 500+ likes"}
  ],
  "code_lines": [                     # right-panel code (optional)
    "{",
    "  \"language\": \"en\",",
    "  ...",
    "}"
  ],
  "footer_left": "build-in-public, day 1",
  "hashtag": "#koko-ship"
}

Requirements: playwright (chromium). Install once with:
    pip install playwright && playwright install chromium
"""
import argparse
import json
import re
import sys
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sys.exit("playwright not installed. run: pip install playwright && playwright install chromium")

DEFAULT_PAYLOAD = {
    "label": "DAY 1",
    "title": "voice profile, built from data",
    "subtitle": "fed writing samples into a voice engine",
    "stats": [
        {"num": "50", "label": "writing samples", "detail": "analyzed for voice patterns"},
        {"num": "5", "label": "signature patterns", "detail": "extracted from your writing"},
        {"num": "1", "label": "voice profile", "detail": "ready to generate posts"},
    ],
    "code_lines": [
        "{",
        '  "language": "en",',
        '  "tone": "direct, lowercase, no hype",',
        '  "length": "180-260 chars",',
        '  "format": "single tweet",',
        '  "hashtags": "branded only",',
        '  "emoji": "learn from data",',
        '  "banned": "excited / thrilled / gamechanger"',
        "}",
    ],
    "footer_left": "build-in-public, day 1",
    "hashtag": "#your-project",
}


HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&family=Inter:wght@400;500;600;800&display=swap');
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: 'Inter', -apple-system, sans-serif;
    background: #0a0a0a;
    color: #e5e5e5;
    width: 1600px;
    padding: 60px;
  }
  .card {
    background: #111;
    border: 1px solid #222;
    border-radius: 24px;
    padding: 60px;
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 50px;
  }
  .header {
    grid-column: 1 / -1;
    border-bottom: 1px solid #222;
    padding-bottom: 30px;
  }
  .label {
    font-size: 14px;
    color: #666;
    text-transform: uppercase;
    letter-spacing: 2px;
    font-weight: 500;
  }
  .title {
    font-size: 56px;
    font-weight: 800;
    margin-top: 10px;
    color: #fff;
    letter-spacing: -1.5px;
    line-height: 1.1;
  }
  .subtitle {
    font-size: 22px;
    color: #888;
    margin-top: 14px;
  }
  .stats {
    display: flex;
    flex-direction: column;
    gap: 32px;
  }
  .stat-num {
    font-family: 'JetBrains Mono', ui-monospace, monospace;
    font-size: 88px;
    font-weight: 700;
    line-height: 1;
    color: #fff;
    letter-spacing: -3px;
  }
  .stat-label {
    font-size: 16px;
    color: #888;
    margin-top: 8px;
  }
  .stat-detail {
    font-size: 13px;
    color: #555;
    font-family: 'JetBrains Mono', ui-monospace, monospace;
    margin-top: 4px;
  }
  .code {
    background: #0d0d0d;
    border: 1px solid #1a1a1a;
    border-radius: 16px;
    padding: 28px 32px;
    font-family: 'JetBrains Mono', ui-monospace, Menlo, monospace;
    font-size: 15px;
    line-height: 1.85;
    color: #c8c8c8;
    white-space: pre;
  }
  .code-title {
    font-size: 12px;
    color: #555;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin-bottom: 18px;
  }
  .code .line { display: block; }
  .key { color: #7dd3fc; }
  .str { color: #a7f3d0; }
  .punct { color: #555; }
  .footer {
    grid-column: 1 / -1;
    margin-top: 30px;
    padding-top: 24px;
    border-top: 1px solid #222;
    display: flex;
    justify-content: space-between;
    align-items: center;
    color: #555;
    font-size: 14px;
    font-family: 'JetBrains Mono', ui-monospace, monospace;
  }
  .tag { color: #7dd3fc; }
</style>
</head>
<body>
  <div class="card">
    <div class="header">
      <div class="label">__LABEL__</div>
      <div class="title">__TITLE__</div>
      __SUBTITLE_HTML__
    </div>
    <div class="stats">__STATS_HTML__</div>
    <div class="code">
      <div class="code-title">.bip-voice.json</div>
__CODE_HTML__
    </div>
    <div class="footer">
      <span>__FOOTER_LEFT__</span>
      <span class="tag">__HASHTAG__</span>
    </div>
  </div>
</body>
</html>"""


def _highlight_json_line(line: str) -> str:
    """Naive JSON syntax highlight for the right-panel code."""
    # Order matters: keys first, then strings, then punctuation
    # Match "key": pattern
    line = re.sub(r'"([^"]+)"(\s*:)', r'<span class="key">"\1"</span>\2', line)
    # Match string values (after colon)
    line = re.sub(r'(:\s*)"([^"]+)"', r'\1<span class="str">"\2"</span>', line)
    # Match braces and commas (faded)
    line = re.sub(r"([\{\}\[\],])", r'<span class="punct">\1</span>', line)
    return line


def _stat_html(stat: dict) -> str:
    detail = (
        f'<div class="stat-detail">{stat["detail"]}</div>'
        if stat.get("detail")
        else ""
    )
    return (
        '<div class="stat">'
        f'<div class="stat-num">{stat["num"]}</div>'
        f'<div class="stat-label">{stat["label"]}</div>'
        f"{detail}</div>"
    )


def render(payload: dict, slug: str, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{slug}.png"
    html_path = out_dir / f"{slug}.html"

    stats_html = "\n".join(_stat_html(s) for s in payload.get("stats", []))
    code_lines = payload.get("code_lines") or []
    code_html = "\n".join(
        f'<span class="line">{_highlight_json_line(l)}</span>' for l in code_lines
    )
    subtitle_html = (
        f'<div class="subtitle">{payload["subtitle"]}</div>'
        if payload.get("subtitle")
        else ""
    )

    html = (
        HTML_TEMPLATE
        .replace("__LABEL__", payload.get("label", ""))
        .replace("__TITLE__", payload.get("title", ""))
        .replace("__SUBTITLE_HTML__", subtitle_html)
        .replace("__STATS_HTML__", stats_html)
        .replace("__CODE_HTML__", code_html)
        .replace("__FOOTER_LEFT__", payload.get("footer_left", ""))
        .replace("__HASHTAG__", payload.get("hashtag", ""))
    )
    html_path.write_text(html)

    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page(
            viewport={"width": 1600, "height": 1200},
            device_scale_factor=2,
        )
        page.goto(f"file://{html_path}")
        page.wait_for_load_state("networkidle")
        page.evaluate("document.fonts.ready")
        page.wait_for_timeout(1500)
        height = page.evaluate("document.body.scrollHeight")
        page.set_viewport_size({"width": 1600, "height": height})
        page.screenshot(path=str(out_path), full_page=True)
        browser.close()

    return out_path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slug", required=True, help="output filename slug (no extension)")
    ap.add_argument("--json", help="JSON payload as a string")
    ap.add_argument("--json-file", help="path to a JSON payload file")
    ap.add_argument(
        "--out-dir",
        default=str(Path.cwd() / ".bip-images"),
        help="output directory (default: <cwd>/.bip-images)",
    )
    args = ap.parse_args()

    if args.json:
        payload = json.loads(args.json)
    elif args.json_file:
        payload = json.loads(Path(args.json_file).read_text())
    else:
        payload = DEFAULT_PAYLOAD

    out_path = render(payload, args.slug, Path(args.out_dir))
    print(f"saved → {out_path}")


if __name__ == "__main__":
    main()
