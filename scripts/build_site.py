#!/usr/bin/env python3
"""把整个站点构建到 dist/。相对路径，不写死 GitHub Pages 的项目前缀。"""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from briefing import build_briefing

ROOT = Path(__file__).resolve().parent.parent
STATIC_HTML = ("index.html", "sentiment.html", "semis.html", "earnings.html", "calendar.html")
ROBOTS = "User-agent: *\nDisallow: /\n"


def ensure_robots(text: str) -> str:
    if 'name="robots"' in text or "name='robots'" in text:
        return text
    return text.replace("<head>", '<head>\n  <meta name="robots" content="noindex">', 1)


def build_site(root: Path | None = None, dist: Path | None = None) -> Path:
    root = root or ROOT
    dist = dist or (root / "dist")
    if dist.exists():
        shutil.rmtree(dist)
    dist.mkdir(parents=True)
    for name in STATIC_HTML:
        source = root / name
        if not source.exists():
            continue
        text = ensure_robots(source.read_text(encoding="utf-8"))
        (dist / name).write_text(text, encoding="utf-8")
    nojekyll = root / ".nojekyll"
    if nojekyll.exists():
        shutil.copyfile(nojekyll, dist / ".nojekyll")
    else:
        (dist / ".nojekyll").write_text("", encoding="utf-8")
    if (root / "assets").exists():
        shutil.copytree(root / "assets", dist / "assets")
    if (root / "data").exists():
        shutil.copytree(root / "data", dist / "data")
    else:
        (dist / "data").mkdir()
    briefing = build_briefing(dist / "data")
    (dist / "data" / "briefing.json").write_text(
        json.dumps(briefing, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (dist / "robots.txt").write_text(ROBOTS, encoding="utf-8")
    return dist


def main() -> int:
    dist = build_site()
    print(f"WROTE {dist}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
