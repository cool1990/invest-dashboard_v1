#!/usr/bin/env python3
"""从已经整理好的 data/ 生成各页「今日小结」。

规则都写在这个文件里，同一份数据每次得到同一段话。
比较的是每个序列最近一条和它上一条，不猜笔记没写过的数字。

市场情绪
- 情绪标签变了：写成「名称由甲变为乙」。
- 数值变动超过下面的阈值才写一句。收益率、利差、实际利率、盈亏平衡通胀用百分点；
  RSI、CNN、AAII、参与度用点数或百分点；价格类用笔记里的涨跌幅百分数，没有则用数值变化百分比。
  cnn_fg 5，aaii 5，spx_rsi / nasdaq_rsi 5，参与度 5，
  us_10y / us_2y / tips_10y / t10yie 0.10，t10y2y / hy_oas 0.10，
  vix 10%，etf 溢价 5%，wti / gold / copper / btc 3%，usdcny 0.3%，
  EFFR 路径 0.10 个百分点，或隐含加息次数变化达到 0.3。
- 跨过笔记里写明的线也写一句：10 年期 4.5%，实际利率 2.5%，参与度 20% 和 80%，
  RSI 30 和 70，QDII 溢价 0。

盈利跟踪
- 估值触发达成、RSI 跨过 30 或 70、修正信号新变成强上修或强下修。
- 最新一天有公告或新闻稿。

半导体
- 存储或 GPU 的 1 日变动达到 5%，OpenRouter 7 日环比达到 10%，SiliconData 7 日达到 5%。
- 韩国出口：只有最新一期的 asof 比上一期更晚时，才写成新期间。笔记把各期 asof 覆盖成同一天时不报。

流动性
- 出现新的周三。
- 净流动性、TGA、准备金的周变动绝对值达到 50（十亿美元）。
- SOFR−IORB 变号，或变动达到 5 个基点。
- 准备金分位跨过 10% 或 25%。

日历
- 只列北京时间的今天和明天。没有就写「今日无变动」。

每页最多 8 句。没有任何一句时写「今日无变动」。
"""

from __future__ import annotations

import csv
import json
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

BJ = timezone(timedelta(hours=8))
PCT_IDS = {"vix", "etf_spx", "etf_ndx", "wti", "gold", "copper", "btc", "usdcny"}
LEVEL_ABS = {
    "cnn_fg": 5,
    "aaii": 5,
    "spx_rsi": 5,
    "nasdaq_rsi": 5,
    "spx_breadth_20": 5,
    "spx_breadth_50": 5,
    "spx_breadth_200": 5,
    "ndx_breadth_20": 5,
    "ndx_breadth_50": 5,
    "ndx_breadth_200": 5,
    "us_10y": 0.10,
    "us_2y": 0.10,
    "tips_10y": 0.10,
    "t10yie": 0.10,
    "t10y2y": 0.10,
    "hy_oas": 0.10,
    "effr_next": 0.10,
    "effr_year": 0.10,
    "effr_ny": 0.10,
}
PCT_ABS = {"vix": 10, "etf_spx": 5, "etf_ndx": 5, "wti": 3, "gold": 3, "copper": 3, "btc": 3, "usdcny": 0.3}
LINES = {
    "us_10y": (4.5, "4.5%"),
    "tips_10y": (2.5, "2.5%"),
    "spx_rsi": None,
    "nasdaq_rsi": None,
    "etf_spx": (0, "0"),
    "etf_ndx": (0, "0"),
}
BREADTH = {"spx_breadth_20", "spx_breadth_50", "spx_breadth_200", "ndx_breadth_20", "ndx_breadth_50", "ndx_breadth_200"}
SEMI_NAMES = {"NVDA", "MU", "INTC", "TSM", "QCOM", "SNDK", "AVGO", "ASML", "AMD", "AMAT", "LRCX", "KLAC", "ARM", "SMCI"}


def beijing_today() -> date:
    return datetime.now(BJ).date()


def load_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def fnum(text: str) -> float | None:
    if text is None or text == "":
        return None
    try:
        return float(text)
    except ValueError:
        return None


def pct_of(text: str) -> float | None:
    if not text or "%" not in text:
        return None
    return fnum(text.replace("%", "").replace("pp", "").replace("+", ""))


def grouped(rows: list[dict[str, str]], key: str) -> dict[str, list[dict[str, str]]]:
    out: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        out.setdefault(row.get(key, ""), []).append(row)
    for values in out.values():
        values.sort(key=lambda item: item.get("date") or item.get("period") or "")
    return out


def cap(lines: list[str]) -> list[str]:
    clean = []
    seen = set()
    for line in lines:
        text = line.strip()
        if not text or text in seen:
            continue
        seen.add(text)
        clean.append(text if text.endswith("。") else text + "。")
    if not clean:
        return ["今日无变动"]
    if len(clean) > 8:
        extra = len(clean) - 7
        clean = clean[:7] + [f"另外还有 {extra} 项变动。"]
    return clean


def cross(prev: float, curr: float, level: float) -> bool:
    return (prev - level) * (curr - level) < 0 or (prev < level <= curr) or (prev > level >= curr)


def sentiment_lines(rows: list[dict[str, str]]) -> list[str]:
    lines: list[str] = []
    for series_id, points in grouped(rows, "series_id").items():
        if len(points) < 2:
            continue
        prev, curr = points[-2], points[-1]
        name = curr.get("name") or series_id
        old_label, new_label = prev.get("label", ""), curr.get("label", "")
        if old_label and new_label and old_label != new_label:
            lines.append(f"{name}由{old_label}变为{new_label}")
        old, new = fnum(prev.get("value", "")), fnum(curr.get("value", ""))
        if old is None or new is None:
            continue
        if series_id in PCT_IDS:
            change = pct_of(curr.get("change_text", ""))
            if change is None and old:
                change = (new - old) / abs(old) * 100
            limit = PCT_ABS.get(series_id, 5)
            if change is not None and abs(change) >= limit:
                lines.append(f"{name}变动 {curr.get('change_text') or f'{change:+.1f}%'}")
        else:
            limit = LEVEL_ABS.get(series_id)
            if limit is not None and abs(new - old) >= limit:
                lines.append(f"{name}从 {old:g} 到 {new:g}")
        old_hike, new_hike = fnum(prev.get("hike_count", "")), fnum(curr.get("hike_count", ""))
        if old_hike is not None and new_hike is not None and abs(new_hike - old_hike) >= 0.3:
            lines.append(f"{name}隐含加息由 {old_hike:g} 次到 {new_hike:g} 次")
        if series_id in {"spx_rsi", "nasdaq_rsi"}:
            for level in (30, 70):
                if cross(old, new, level):
                    lines.append(f"{name}跨过 {level}")
        if series_id in BREADTH:
            for level in (20, 80):
                if cross(old, new, level):
                    lines.append(f"{name}跨过 {level}%")
        spec = LINES.get(series_id)
        if spec and cross(old, new, spec[0]):
            lines.append(f"{name}跨过 {spec[1]}")
    return lines


def earnings_lines(daily: list[dict[str, str]], filings: list[dict[str, str]], press: list[dict[str, str]], days: list[dict[str, str]]) -> list[str]:
    lines: list[str] = []
    by_ticker = grouped(daily, "ticker")
    for ticker, points in by_ticker.items():
        if len(points) < 2:
            continue
        prev, curr = points[-2], points[-1]
        if prev.get("triggered") != "1" and curr.get("triggered") == "1":
            lines.append(f"{ticker} 估值触发")
        old, new = fnum(prev.get("rsi", "")), fnum(curr.get("rsi", ""))
        if old is not None and new is not None:
            for level in (30, 70):
                if cross(old, new, level):
                    lines.append(f"{ticker} RSI 跨过 {level}")
        old_sig, new_sig = prev.get("revision_signal", ""), curr.get("revision_signal", "")
        if new_sig in {"强上修", "强下修"} and new_sig != old_sig:
            lines.append(f"{ticker} 修正信号变为{new_sig}")
    latest_days = [row.get("date", "") for row in days if row.get("date")]
    latest = max(latest_days) if latest_days else ""
    if latest:
        ann = [row for row in filings if row.get("date") == latest]
        news = [row for row in press if row.get("date") == latest]
        if ann:
            names = "、".join(sorted({row.get("ticker") or row.get("company", "") for row in ann}))
            lines.append(f"{latest} 有 {len(ann)} 条公告（{names}）")
        if news:
            names = "、".join(sorted({row.get("ticker") or row.get("company", "") for row in news}))
            lines.append(f"{latest} 有 {len(news)} 条公司新闻（{names}）")
    return lines


def semis_lines(memory: list[dict[str, str]], gpu: list[dict[str, str]], router: list[dict[str, str]], silicon: list[dict[str, str]], korea: list[dict[str, str]]) -> list[str]:
    lines: list[str] = []
    for row in memory:
        change = fnum(row.get("chg_1d_pct", ""))
        if change is not None and abs(change) >= 5 and row.get("date") == max(item.get("date", "") for item in memory):
            lines.append(f"{row.get('product')} 一日变动 {change:+.1f}%")
    if gpu:
        latest = max(row.get("date", "") for row in gpu)
        for row in gpu:
            if row.get("date") != latest:
                continue
            change = fnum(row.get("chg_1d_pct", ""))
            if change is not None and abs(change) >= 5:
                lines.append(f"{row.get('gpu')} 租金一日变动 {change:+.1f}%")
    week = [row for row in router if row.get("window") == "7日"]
    if len(week) >= 1:
        change = fnum(week[-1].get("change_pct", ""))
        if change is not None and abs(change) >= 10:
            lines.append(f"OpenRouter 7 日用量环比 {change:+.1f}%")
    if silicon:
        change = fnum(silicon[-1].get("chg_7d_pct", ""))
        if change is not None and abs(change) >= 5:
            lines.append(f"SiliconData 7 日变动 {change:+.1f}%")
    korea_sorted = sorted(korea, key=lambda row: row.get("period", ""))
    if len(korea_sorted) >= 2:
        prev, curr = korea_sorted[-2], korea_sorted[-1]
        # 各期的 asof 会被最新笔记覆盖成同一天，所以只有最新一期的 asof 更晚时才算新发布。
        if curr.get("asof", "") > prev.get("asof", "") and curr.get("period"):
            lines.append(f"韩国出口新期间 {curr.get('period')}")
    return lines


def liquidity_lines(weekly: list[dict[str, str]], spreads: list[dict[str, str]]) -> list[str]:
    lines: list[str] = []
    if len(weekly) >= 2:
        prev, curr = weekly[-2], weekly[-1]
        if curr.get("date") != prev.get("date"):
            lines.append(f"流动性更新到周三 {curr.get('date')}")
        for field, label, limit in (
            ("net_liq_wow_bn", "净流动性周变动", 50),
            ("tga_wow_bn", "TGA 周变动", 50),
            ("reserves_wow_bn", "准备金周变动", 50),
        ):
            value = fnum(curr.get(field, ""))
            if value is not None and abs(value) >= limit:
                lines.append(f"{label} {value:+.1f}（十亿美元）")
        old_p, new_p = fnum(prev.get("reserves_percentile", "")), fnum(curr.get("reserves_percentile", ""))
        if old_p is not None and new_p is not None:
            for level in (10, 25):
                if cross(old_p, new_p, level):
                    lines.append(f"准备金分位跨过 {level}%")
    usable = [row for row in spreads if row.get("sofr_iorb_bp") not in ("", None)]
    if len(usable) >= 2:
        old, new = fnum(usable[-2].get("sofr_iorb_bp", "")), fnum(usable[-1].get("sofr_iorb_bp", ""))
        if old is not None and new is not None:
            if old * new < 0:
                lines.append(f"SOFR−IORB 由 {old:g} bp 变为 {new:g} bp")
            elif abs(new - old) >= 5:
                lines.append(f"SOFR−IORB 由 {old:g} bp 到 {new:g} bp")
    return lines


def calendar_lines(events: list[dict], today: date) -> list[str]:
    tomorrow = (today + timedelta(days=1)).isoformat()
    today_s = today.isoformat()
    lines = []
    for event in events:
        when = event.get("date", "")
        if when not in {today_s, tomorrow}:
            continue
        clock = event.get("time_bj") or ""
        prefix = "今天" if when == today_s else "明天"
        title = event.get("title") or ""
        lines.append(f"{prefix} {clock} {title}".strip())
    return lines


def build_briefing(data_dir: Path, today: date | None = None, calendar_events: list[dict] | None = None) -> dict:
    today = today or beijing_today()
    sentiment = load_csv(data_dir / "sentiment" / "series.csv")
    earnings = load_csv(data_dir / "earnings" / "daily.csv")
    filings = load_csv(data_dir / "filings" / "announcements.csv")
    press = load_csv(data_dir / "filings" / "press.csv")
    days = load_csv(data_dir / "filings" / "days.csv")
    weekly = load_csv(data_dir / "derived" / "weekly.csv")
    spreads = load_csv(data_dir / "derived" / "spreads.csv")
    if calendar_events is None:
        path = data_dir / "calendar" / "events.json"
        if path.exists():
            calendar_events = json.loads(path.read_text(encoding="utf-8")).get("events", [])
        else:
            calendar_events = []
    pages = {
        "liquidity": cap(liquidity_lines(weekly, spreads)),
        "sentiment": cap(sentiment_lines(sentiment)),
        "semis": cap(semis_lines(
            load_csv(data_dir / "semis" / "memory.csv"),
            load_csv(data_dir / "semis" / "gpu.csv"),
            load_csv(data_dir / "semis" / "openrouter.csv"),
            load_csv(data_dir / "semis" / "silicon.csv"),
            load_csv(data_dir / "semis" / "korea.csv"),
        )),
        "earnings": cap(earnings_lines(earnings, filings, press, days)),
        "calendar": cap(calendar_lines(calendar_events, today)),
    }
    return {"asof": today.isoformat(), "pages": pages, "semi_ai": sorted(SEMI_NAMES)}
