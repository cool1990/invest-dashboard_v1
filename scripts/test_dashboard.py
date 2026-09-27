#!/usr/bin/env python3
"""笔记解析、今日小结和日历解析。夹具只放临时目录。"""

from __future__ import annotations

import sys
import tempfile
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "ingest"))

from briefing import build_briefing
from build_site import build_site
from fetch_calendar import h41_events, load_manual, parse_bea, parse_census
from parse_notes import parse_filings, parse_press, parse_sentiment, to_beijing


def test_beijing() -> None:
    assert to_beijing("2026-09-25T16:05:16.000Z") == "2026-09-26 00:05"
    assert to_beijing("25/09/2026 17:22") == "2026-09-25 17:22"


def test_sentiment_schema() -> None:
    body = """
# 宏观指标 2026-09-25
## 小结
- 情绪指标：CNN仍处恐慌区间。
## 情绪指标
|指标|数值|涨跌幅|日期|情绪|备注|
|---|---:|---:|---|---|---|
|标普500参与度>20日|30.2|+3.4pp|2026-09-25|中性|<20机会/>80风险|
## 利率指标
|指标|数值|涨跌幅|日期|情绪|备注|
|---|---:|---:|---|---|---|
|下月EFFR|4.046||2026-09-25|中性|**隐含加息0.7次**|
"""
    path = Path("宏观指标_2026-09-25.md")
    rows, _composite, summary = parse_sentiment(path, {"data_date": "2026-09-26"}, body, [])
    by_id = {row["series_id"]: row for row in rows}
    assert by_id["spx_breadth_20"]["date"] == "2026-09-26"
    assert by_id["spx_breadth_20"]["section"] == "情绪"
    assert by_id["effr_next"]["hike_count"] == "0.7"
    assert by_id["effr_next"]["section"] == "利率"
    assert "恐慌" in summary["text"]


def test_filings_and_press() -> None:
    filing = """
## Circle Internet Group, Inc. (CRCL)
### 2026-09-25T16:05:16.000Z — 0001876042-26-000279
公司：Circle Internet Group, Inc.
标题：董事会成员辞职
核心内容：第一句。
- 还有一句
链接：[SEC Filing](https://www.sec.gov/example)
## 内部人买入（Form 4，P 类）
今日无 P 类交易触发
"""
    items, insiders, day = parse_filings(Path("美港股公告 2026-09-26.md"), {"data_date": "2026-09-25", "fetch_status": "OK"}, filing)
    assert day["date"] == "2026-09-25"
    assert items[0]["ticker"] == "CRCL"
    assert items[0]["filed_bj"] == "2026-09-26 00:05"
    assert items[0]["url"].startswith("https://www.sec.gov/")
    assert "还有一句" in items[0]["summary"]
    assert insiders == []
    empty, _ins, empty_day = parse_filings(Path("美港股公告 2026-09-26.md"), {"data_date": "2026-09-26", "fetch_status": "NO_TRIGGER"}, "今日无公告。\n")
    assert empty == []
    assert empty_day["item_count"] == "0"
    press_body = """
## Strategy（MSTR）
- [Strategy（MSTR）] Strategy 8-K
  - 时间：2026-09-25 16:03（北京时间）
  - 链接：https://www.sec.gov/Archives/example
  - 摘要：一句话摘要
今日无新增新闻稿
"""
    # 有条目时不以“今日无”把条数清零；空文件才是 0
    rows, day_row = parse_press(Path("美港股新闻稿 2026-09-26.md"), {"data_date": "2026-09-25"}, press_body)
    assert rows[0]["ticker"] == "MSTR"
    assert rows[0]["summary"] == "一句话摘要"
    assert day_row["item_count"] == "1"
    none_rows, none_day = parse_press(Path("美港股新闻稿 2026-09-26.md"), {"data_date": "2026-09-26"}, "今日无新增新闻稿\n")
    assert none_rows == []
    assert none_day["item_count"] == "0"


def test_briefing_and_build() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        data = root / "data" / "sentiment"
        data.mkdir(parents=True)
        (data / "series.csv").write_text(
            "date,series_id,name,value,unit,change_text,label,obs_date,carried,section,remark,hike_count,source\n"
            "2026-09-25,cnn_fg,CNN,40,点,,中性,,,,,,\n"
            "2026-09-26,cnn_fg,CNN,30,点,,恐慌,,,,,,\n",
            encoding="utf-8",
        )
        (root / "index.html").write_text("<head></head><p>流动性</p>", encoding="utf-8")
        (root / "assets").mkdir()
        (root / "assets" / "site.css").write_text("body{}", encoding="utf-8")
        briefing = build_briefing(root / "data", today=date(2026, 9, 27), calendar_events=[])
        assert any("恐慌" in line for line in briefing["pages"]["sentiment"])
        dist = build_site(root, root / "dist")
        text = (dist / "index.html").read_text(encoding="utf-8")
        assert 'name="robots"' in text
        assert "Disallow: /" in (dist / "robots.txt").read_text(encoding="utf-8")
        assert (dist / "data" / "briefing.json").exists()
        assert not (dist / "reports").exists()


def test_calendar_parsers() -> None:
    bea = """
    <th>Year 2026</th>
    <tr class="scheduled-releases-type-press">
      <td><div class="release-date">September 30</div><small>8:30 AM</small></td>
      <td class="release-title">Personal Income and Outlays, August 2026</td>
    </tr>
    """
    rows = parse_bea(bea, date(2026, 9, 27), date(2026, 10, 11))
    assert rows and rows[0]["date"] == "2026-09-30" and rows[0]["time_bj"] == "20:30"
    census = """
    <tr><td><a href="/retail/x">Advance Monthly Sales for Retail and Food Services</a></td>
    <td>October 15, 2026</td><td>8:30 AM</td><td>September 2026</td></tr>
    """
    retail = parse_census(census, date(2026, 9, 27), date(2026, 10, 20))
    assert retail and retail[0]["date"] == "2026-10-15"
    assert "零售" in retail[0]["title"]
    h41 = h41_events("These data are released each Thursday, generally at 4:30 p.m.", date(2026, 9, 27), date(2026, 10, 8))
    assert any(row["title"].startswith("美联储 H.4.1") for row in h41)
    assert load_manual(Path("/workspace/calendar/manual.yaml")) == []


if __name__ == "__main__":
    test_beijing()
    test_sentiment_schema()
    test_filings_and_press()
    test_briefing_and_build()
    test_calendar_parsers()
    print("OK")
