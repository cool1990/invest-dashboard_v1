#!/usr/bin/env python3
"""研报渲染只用临时夹具，不往站点里写假报告。"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from build_site import build_site
from report_pages import load_reports, reading_order, render_bodies


def write_fixture(root: Path) -> None:
    daily = root / "日报"
    macro = root / "宏观周报"
    industry = root / "产业周报"
    for folder in (daily, macro, industry):
        folder.mkdir(parents=True)
    (daily / "2026-09-27_市场观点汇总.md").write_text(
        """---
title: 市场观点汇总
date: 2026-09-27
---
# 市场观点汇总

今天先看流动性。见 [[2026-W39 宏观周报|本周宏观]]，也见 [[不存在的笔记]]。

> [!note] 备忘
> 颜色 <span style="color:red">只要文字</span>
> <span style="color:red"><b>不要执行</b></span>

| 指标 | 读数 |
| --- | --- |
| 净流动性 | 100 |

`[[不要变成链接]]`

```
![[图表.png]]
```

![[附件.pdf|附件]]
""",
        encoding="utf-8",
    )
    (daily / "2026-09-27_主题跟踪.md").write_text(
        """---
date: 2026-09-27
---
## 半导体

- 存储
- GPU

### 租金
""",
        encoding="utf-8",
    )
    (daily / "2026-09-26_市场观点汇总.md").write_text(
        "---\ntitle: 市场观点汇总\ndate: 2026-09-26\n---\n\n昨天。\n",
        encoding="utf-8",
    )
    (macro / "2026-W39 宏观周报.md").write_text(
        """---
title: 宏观周报
---
## 这一周

> [!warning]
> 表格紧挨着文字
| 项目 | 变化 |
| --- | --- |
| TGA | 下降 |

见 [[2026-09-27_市场观点汇总]]。
""",
        encoding="utf-8",
    )
    (industry / "2026-W39 产业周报.md").write_text(
        "---\ntitle: 产业周报\n---\n\n产业这一周。\n",
        encoding="utf-8",
    )


def test_render() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        write_fixture(root)
        reports = load_reports(root)
        assert {item.stem for item in reports} == {
            "2026-09-26_市场观点汇总",
            "2026-09-27_市场观点汇总",
            "2026-09-27_主题跟踪",
            "2026-W39 宏观周报",
            "2026-W39 产业周报",
        }
        ordered = reading_order(reports)
        assert [item.stem for item in ordered] == [
            "2026-09-27_市场观点汇总",
            "2026-09-27_主题跟踪",
            "2026-09-26_市场观点汇总",
            "2026-W39 宏观周报",
            "2026-W39 产业周报",
        ]
        assert ordered[0].title == "市场观点汇总"
        assert ordered[3].date_label == "2026-W39"
        render_bodies(reports)
        by_stem = {item.stem: item for item in reports}
        daily = by_stem["2026-09-27_市场观点汇总"]
        assert "只要文字" in daily.body_html
        assert "<span" not in daily.body_html
        assert "<b>" not in daily.body_html
        assert "&lt;b&gt;" in daily.body_html
        assert 'href="2026-W39-宏观周报.html"' in daily.body_html
        assert "本周宏观" in daily.body_html
        assert "不存在的笔记" in daily.body_html
        assert "不存在的笔记</a>" not in daily.body_html
        assert "[[不要变成链接]]" in daily.body_html
        assert "图表.png" in daily.body_html
        assert "附件" in daily.body_html
        assert "附件.pdf" not in daily.body_html or "附件</a>" not in daily.body_html
        assert 'class="callout callout-note"' in daily.body_html
        assert 'class="report-table"' in daily.body_html
        assert 'class="table-scroll"' in daily.body_html
        assert "<h1>" not in daily.body_html
        weekly = by_stem["2026-W39 宏观周报"]
        assert 'class="callout callout-warning"' in weekly.body_html
        assert 'class="report-table"' in weekly.body_html
        assert 'href="2026-09-27_市场观点汇总.html"' in weekly.body_html
        assert weekly.outline[0][2] == "这一周"
        theme = by_stem["2026-09-27_主题跟踪"]
        assert [level for level, _id, _text in theme.outline] == [2, 3]


def test_build_outputs() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        reports = tmp_path / "reports-src"
        write_fixture(reports)
        root = Path(__file__).resolve().parent.parent
        dist = tmp_path / "dist"
        build_site(root, dist, reports)
        index = (dist / "reports" / "index.html").read_text(encoding="utf-8")
        weekly = (dist / "reports" / "2026-W39-宏观周报.html").read_text(encoding="utf-8")
        robots = (dist / "robots.txt").read_text(encoding="utf-8")
        home = (dist / "index.html").read_text(encoding="utf-8")
        assert "Disallow: /" in robots
        assert 'name="robots" content="noindex"' in index
        assert 'name="robots" content="noindex"' in home
        assert "市场观点汇总" in index
        assert "2026-09-27" in index
        assert 'aria-current="page"' in index
        assert "主题跟踪" in index
        assert "宏观周报" in weekly
        assert 'href="../assets/site.css"' in weekly
        assert "/macro-dashboard/" not in weekly
        assert "/macro-dashboard/" not in index
        assert (dist / "assets" / "site.css").exists()
        assert (dist / "data" / "meta.json").exists()
        assert not (dist / "inbox").exists()
        mobile_bits = ("toc-drawer", "summary>目录</summary>", "toc-side")
        for bit in mobile_bits:
            assert bit in index


if __name__ == "__main__":
    test_render()
    test_build_outputs()
    print("OK")
