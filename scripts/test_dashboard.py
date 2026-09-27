#!/usr/bin/env python3
"""笔记解析、今日小结和日历解析。夹具只放临时目录。"""

from __future__ import annotations

import sys
import tempfile
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "ingest"))

from briefing import build_briefing, calendar_lines, earnings_summary_lines, semis_lines
from build_site import build_site
from fetch_calendar import annotate, dedupe, event, h41_events, load_manual, parse_bea, parse_census
from parse_notes import parse_earnings, parse_filings, parse_press, parse_sentiment, to_beijing


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
        (data / "summary.csv").write_text(
            "date,text,source\n"
            "2026-09-26,情绪指标：CNN仍处恐慌区间。 利率指标：10年美债收益率偏高。,\n",
            encoding="utf-8",
        )
        (root / "index.html").write_text("<head></head><p>流动性</p>", encoding="utf-8")
        (root / "assets").mkdir()
        (root / "assets" / "site.css").write_text("body{}", encoding="utf-8")
        briefing = build_briefing(root / "data", today=date(2026, 9, 27), calendar_events=[])
        assert briefing["pages"]["sentiment"] == [
            "情绪指标：CNN仍处恐慌区间。",
            "利率指标：10年美债收益率偏高。",
        ]
        assert not any("变为" in line for line in briefing["pages"]["sentiment"])
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
    manual = load_manual(Path("/workspace/calendar/manual.yaml"))
    assert len(manual) == 41
    by_title = {row["title"]: row for row in manual}
    for title in (
        "ASML 2026年第三季度业绩",
        "台积电 3Q26 业绩会",
        "联电 3Q26 业绩与法说会",
        "应用材料 FY26 Q4 业绩（官方标注预计）",
    ):
        assert by_title[title]["category"] == "财报"
        assert by_title[title]["tags"] == ["半导体"]
        assert by_title[title]["note"]
    assert by_title["台积电9月营收"]["category"] == "半导体"
    assert by_title["台积电9月营收"]["tags"] == []
    assert by_title["韩国9月进出口（产业通商部，全月初值）"]["category"] == "半导体"
    gtc = next(row for row in manual if "GTC" in row["title"])
    assert gtc["title"].startswith("英伟达 GTC")
    assert "NVIDIA GTC" in gtc["note"]
    assert gtc["priority"] == "低"
    assert by_title["台积电9月营收"]["priority"] == "高"
    assert by_title["联电9月营收"]["priority"] == "中"
    nasdaq = event(
        "2026-09-30", "", "财报", "Micron Technology, Inc.（MU）财报",
        "https://www.nasdaq.com/market-activity/earnings", "Nasdaq earnings calendar",
        "美东盘后", previous="2.86", consensus="31.24", tags=["半导体"],
    )
    note = event(
        "2026-10-01", "", "财报", "MICRON TECHNOLOGY INC（MU）财报",
        "", "盈利跟踪笔记", "笔记里的未来 7 天财报", tags=["半导体"],
    )
    nike = event("2026-10-02", "", "财报", "NIKE, Inc.（NKE）财报", "", "盈利跟踪笔记", "")
    merged = dedupe([note, nasdaq, nike])
    assert len(merged) == 2
    mu = next(row for row in merged if "MU" in row["title"])
    assert mu["date"] == "2026-09-30"
    assert "2026-09-30" in mu["note"] and "2026-10-01" in mu["note"]
    assert mu["consensus"] == "31.24"
    assert {link["source"] for link in mu["links"]} == {"Nasdaq earnings calendar", "盈利跟踪笔记"}
    tsm_manual = event(
        "2026-10-15", "14:00", "财报", "台积电 3Q26 业绩会",
        "https://investor.tsmc.com/english/financial-calendar", "calendar/manual.yaml",
        "TSMC IR 财务日历", tags=["半导体"],
    )
    tsm_auto = event(
        "2026-10-15", "", "财报", "Taiwan Semiconductor Manufacturing（TSM）财报",
        "https://www.nasdaq.com/market-activity/earnings", "Nasdaq earnings calendar",
        "美东盘前", consensus="1.00", tags=["半导体"],
    )
    one = dedupe([tsm_auto, tsm_manual])
    assert len(one) == 1
    assert one[0]["title"] == "台积电 3Q26 业绩会"
    assert one[0]["note"] == "TSMC IR 财务日历"
    assert one[0]["consensus"] == "1.00"
    assert len(one[0]["links"]) == 2
    minutes_auto = event("2026-10-08", "", "大事", "September 会议纪要", "https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm", "Federal Reserve FOMC calendars", "页面写的是发布日")
    minutes_manual = event("2026-10-08", "02:00", "大事", "FOMC 9月会议纪要", "https://www.federalreserve.gov/newsevents/2026-october.htm", "calendar/manual.yaml", "美联储10月日历")
    minutes = dedupe([minutes_auto, minutes_manual])
    assert len(minutes) == 1
    assert minutes[0]["title"] == "FOMC 9月会议纪要"
    assert minutes[0]["note"] == "美联储10月日历"
    gdp = annotate(event(
        "2026-09-30", "20:30", "宏观",
        "GDP：GDP (Third Estimate), 2nd Quarter 2026",
        "https://www.bea.gov/news/schedule", "BEA Release Schedule", "美东 8:30 AM",
    ))
    assert gdp["title"] == "2026年二季度 GDP 第三次估计"
    assert gdp["priority"] == "高"
    assert gdp["note"].count("原名：") == 1
    assert "Third Estimate" in gdp["note"]
    again = annotate(dict(gdp))
    assert again["title"] == gdp["title"]
    assert again["note"].count("原名：") == 1
    speech = event(
        "2026-09-28", "20:15", "大事",
        "美联储：Recent Developments in Bank Supervision and Regulation",
        "https://www.federalreserve.gov/newsevents/2026-september.htm",
        "Federal Reserve calendar", "美东 8:15 a.m.",
    )
    assert speech["title"] == "美联储讲话：银行监管近况"
    assert speech["priority"] == "低"
    assert "Recent Developments in Bank Supervision" in speech["note"]
    retail = parse_census(
        "<tr><td>Advance Monthly Sales for Retail and Food Services</td><td>October 15, 2026</td><td>8:30 AM</td><td>September 2026</td></tr>",
        date(2026, 9, 27), date(2026, 10, 20),
    )
    assert retail[0]["title"] == "2026年9月零售和餐饮销售"
    assert "Retail" not in retail[0]["title"]
    income = parse_bea(
        """<th>Year 2026</th><tr><td><div class="release-date">September 30</div><small>8:30 AM</small></td>
        <td class="release-title">Personal Income and Outlays, August 2026</td></tr>""",
        date(2026, 9, 27), date(2026, 10, 11),
    )
    assert income[0]["title"] == "2026年8月个人收入与支出"
    preview = event(
        "2026-09-30", "20:30", "宏观",
        "经济指标预览：Advance Economic Indicators Report (International Trade, Retail, & Wholesale)",
        "https://www.census.gov/economic-indicators/calendar-listview.html",
        "Census economic indicators calendar",
        "美东 8:30 AM August 2026",
    )
    assert preview["title"] == "2026年8月经济指标预览"
    assert preview["priority"] == "中"
    assert "International Trade" not in preview["title"]
    lines = calendar_lines([
        {"date": "2026-09-27", "priority": "低", "title": "美联储讲话：银行监管近况", "time_bj": "20:15"},
        {"date": "2026-09-28", "priority": "高", "title": "2026年8月个人收入与支出", "time_bj": "20:30"},
        {"date": "2026-09-30", "priority": "高", "title": "2026年二季度 GDP 第三次估计", "time_bj": "20:30"},
    ], date(2026, 9, 27))
    assert lines == ["明天 20:30 2026年8月个人收入与支出"]


def test_earnings_and_semis_lines() -> None:
    text = """一、EPS：
1、修正信号：强上修：NVDA, HOOD, TSM, GOOGL, MSFT；强下修：MCD, AAPL, META, QCOM, TME。
2、EPS变化：下财年EPS均无变化。
二、RSI信号：低于30 MCD；高于70 META。
三、估值触发：PDD（6.69<7）, MCD（18.16<20）。
四、未来7天财报：MICRON TECHNOLOGY INC(MU) 2026-10-01；NIKE, Inc.(NKE) 2026-10-02。
⚠️不适用：MARA Holdings, Inc. / MARA：EPS 合计 ≤ 0，所以不计算 Forward PE；IREN Ltd / IREN：EPS 合计 ≤ 0，所以不计算 Forward PE。"""
    lines = earnings_summary_lines(text)
    assert lines[0].startswith("修正：强上修 NVDA、HOOD、TSM、GOOGL、MSFT")
    assert "强下修 MCD、AAPL、META、QCOM、TME" in lines[0]
    assert lines[0].endswith("下财年 EPS 没有变化")
    assert lines[1] == "RSI：低于 30 的是 MCD，高于 70 的是 META"
    assert lines[2] == "估值触发：PDD、MCD"
    assert "美光（MU）2026-10-01" in lines[3] and "耐克（NKE）2026-10-02" in lines[3]
    assert lines[4].startswith("不适用：MARA、IREN")
    assert "Forward PE" in lines[4]
    semis = semis_lines(
        [
            {"date": "2026-09-26", "product": "DDR4", "chg_1d_pct": "-0.70"},
            {"date": "2026-09-26", "product": "DDR5", "chg_1d_pct": "0.29"},
        ],
        [
            {"date": "2026-09-26", "gpu": "B200", "chg_1d_pct": "0.0", "chg_7d_pct": "15.4"},
            {"date": "2026-09-26", "gpu": "H100 SXM", "chg_1d_pct": "6.7", "chg_7d_pct": "8.7"},
            {"date": "2026-09-26", "gpu": "H200", "chg_1d_pct": "-4.1", "chg_7d_pct": "-2.8"},
        ],
        [{"date": "2026-09-26", "window": "7日", "change_pct": "11.2"}],
        [{"date": "2026-09-25", "chg_7d_pct": "-3.58"}],
        [
            {"period": "2026-08", "asof": "2026-09-26"},
            {"period": "2026-09", "asof": "2026-09-26"},
        ],
    )
    assert semis[0] == "存储：今天没有明显波动"
    assert "H100 SXM 一日 +6.7%" in semis[1]
    assert "B200 一日没动，一周 +15.4%" in semis[1]
    assert "H200" not in semis[1]
    assert semis[2] == "用量：OpenRouter 7 日环比 +11.2%"
    assert semis[3] == "韩国出口今日无新数"
    brief = parse_earnings(Path("盈利跟踪_2026-09-26.md"), {"data_date": "2026-09-26"}, "## 简要总结\n" + text + "\n", [])
    assert brief[2]["text"].startswith("一、EPS")
    assert brief[2]["date"] == "2026-09-26"


if __name__ == "__main__":
    test_beijing()
    test_sentiment_schema()
    test_filings_and_press()
    test_briefing_and_build()
    test_calendar_parsers()
    test_earnings_and_semis_lines()
    print("OK")
