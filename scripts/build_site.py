#!/usr/bin/env python3
"""把整个站点构建到 dist/。相对路径，不写死 GitHub Pages 的项目前缀。"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from report_pages import load_allowlist, load_reports, write_report_site

ROOT = Path(__file__).resolve().parent.parent
STATIC_HTML = ("index.html", "sentiment.html", "semis.html", "earnings.html")
ROBOTS = "User-agent: *\nDisallow: /\n"


def ensure_robots(text: str) -> str:
    if 'name="robots"' in text or "name='robots'" in text:
        return text
    return text.replace("<head>", '<head>\n  <meta name="robots" content="noindex">', 1)


def build_site(
    root: Path | None = None,
    dist: Path | None = None,
    reports_dir: Path | None = None,
    allow: set[str] | None = None,
    allowlist: Path | None = None,
) -> Path:
    root = root or ROOT
    dist = dist or (root / "dist")
    reports_dir = reports_dir if reports_dir is not None else root / "inbox" / "reports"
    if allow is None:
        allow = load_allowlist(allowlist or (root / "reports" / "publish.json"))
    if dist.exists():
        shutil.rmtree(dist)
    dist.mkdir(parents=True)
    for name in STATIC_HTML:
        source = root / name
        text = ensure_robots(source.read_text(encoding="utf-8"))
        (dist / name).write_text(text, encoding="utf-8")
    nojekyll = root / ".nojekyll"
    if nojekyll.exists():
        shutil.copyfile(nojekyll, dist / ".nojekyll")
    else:
        (dist / ".nojekyll").write_text("", encoding="utf-8")
    shutil.copytree(root / "assets", dist / "assets")
    if (root / "data").exists():
        shutil.copytree(root / "data", dist / "data")
    (dist / "robots.txt").write_text(ROBOTS, encoding="utf-8")
    write_report_site(load_reports(reports_dir, allow), dist / "reports")
    return dist


def main() -> int:
    dist = build_site()
    print(f"WROTE {dist}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
