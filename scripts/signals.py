"""总览上的信号和数据健康。同一份数据每次得到同一组结果。

信号是规则算出来的提示，不是结论。阈值写在下面的常数里。
变动用 scripts/common.py，不用笔记里的涨跌列。
"""

from __future__ import annotations

import csv
import json
from datetime import date, timedelta
from pathlib import Path

from common import (
    day_move,
    fnum,
    format_change,
    fresh_pair,
    kind_change,
    lookback,
    parse_day,
    pct_change,
    price_carried,
    series_points,
)

RESERVE_RISK = 10
RESERVE_WATCH = 25
SOFR_WATCH_LOW = -3
NET_4W = 150
HY_WIDEN_BP = 50
HY_LEVEL = 5
HY_PERCENTILE = 10
VIX_HIGH = 25
VIX_LOW = 13
HIKE_RISK = 1
BREADTH_HIGH = 80
BREADTH_LOW = 20
PREMIUM_HIGH = 5
PREMIUM_LOW = 0
PRICE_WEEK = 5
ROUTER_WEEK = 10
SILICON_30 = -20
SILICON_90 = -30
KOREA_HIGH = 30
REVISION_EXTREME = 50
FRED_GAP = 0.02
DAILY_STALE = 4
WEEKLY_STALE = 10
# 笔记把这两只美元 ADR 的财报单位写成 CNY。已核对 EPS 就是美元，数字不再换汇。
USD_EPS_ADR = {"PDD", "TME"}
FILING_RISK = ("辞职", "诉讼", "调查", "减值", "违约", "下调")
FILING_WATCH = ("收购", "协议")
FRED_CHECK = {
    "DGS10": "us_10y",
    "DGS2": "us_2y",
    "DFII10": "tips_10y",
    "T10YIE": "t10yie",
    "T10Y2Y": "t10y2y",
    "BAMLH0A0HYM2": "hy_oas",
}
FRED_WINDOW = 10
RATIO_TOLERANCE = 1
RATIO_DAYS = 10
HEALTH_ORDER = {"错误": 0, "警告": 1, "提示": 2}
CALENDAR_HINTS = ("初请失业金", "加密", "韩国出口与 TSMC")
RATE_RISK_IDS = ("us_10y", "tips_10y", "us_2y", "t10yie", "hy_oas")


def load_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def grouped(rows: list[dict[str, str]], key: str) -> dict[str, list[dict[str, str]]]:
    out: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        out.setdefault(row.get(key, ""), []).append(row)
    for values in out.values():
        values.sort(key=lambda item: item.get("date") or item.get("period") or "")
    return out


def signal(bucket: str, title: str, evidence: str, threshold: str, page: str) -> dict[str, str]:
    return {"bucket": bucket, "title": title, "evidence": evidence, "threshold": threshold, "page": page}


def health(level: str, text: str) -> dict[str, str]:
    return {"level": level, "text": text}


def age_days(today: date, text: str) -> int | None:
    day = parse_day(text)
    if day is None:
        return None
    return (today - day).days


def latest_spread(rows: list[dict[str, str]]) -> dict[str, str] | None:
    for row in reversed(rows):
        if row.get("sofr_iorb_bp"):
            return row
    return None


def percentile(values: list[float], current: float) -> float:
    if not values:
        return 0
    return sum(1 for value in values if value <= current) / len(values) * 100


def level_shift(points: list[tuple[date, float]], days: int) -> float | None:
    """回看窗口两端的水平差。净流动性用十亿美元，不用百分比。"""
    found = lookback(points, days)
    if not found:
        return None
    return found[3] - found[1]


def filing_hits(rows: list[dict[str, str]], today: date, words: tuple[str, ...]) -> list[dict[str, str]]:
    start = (today - timedelta(days=3)).isoformat()
    end = today.isoformat()
    found = []
    for row in rows:
        when = row.get("date") or ""
        if not (start <= when <= end):
            continue
        blob = (row.get("title") or "") + (row.get("summary") or "")
        if any(word in blob for word in words):
            found.append(row)
    return found


def rate_level_signals(latest: dict[str, dict[str, str]]) -> list[dict[str, str]]:
    named = []
    for series_id in RATE_RISK_IDS:
        row = latest.get(series_id)
        if row and row.get("label") == "风险":
            named.append(f"{row.get('name') or series_id} {row.get('value')}（{row.get('obs_date') or row.get('date')}）")
    if not named:
        return []
    return [signal("风险", "利率笔记标了风险", "；".join(named), "笔记情绪列写「风险」就合成一条", "sentiment.html")]


def mood_signal(latest: dict[str, dict[str, str]]) -> list[dict[str, str]]:
    fear = []
    greed = []
    for series_id, label in (("cnn_fg", "CNN"), ("aaii", "AAII")):
        row = latest.get(series_id)
        if not row:
            continue
        if row.get("label") == "恐慌":
            fear.append(f"{label} {row.get('value')}（{row.get('obs_date') or row.get('date')}）")
        elif row.get("label") == "贪婪":
            greed.append(f"{label} {row.get('value')}（{row.get('obs_date') or row.get('date')}）")
    out = []
    if fear:
        out.append(signal("机会", "情绪偏恐慌，逆向偏机会", "；".join(fear), "CNN 或 AAII 标恐慌", "sentiment.html"))
    if greed:
        out.append(signal("风险", "情绪偏贪婪，逆向偏风险", "；".join(greed), "CNN 或 AAII 标贪婪", "sentiment.html"))
    return out


def breadth_signals(latest: dict[str, dict[str, str]]) -> list[dict[str, str]]:
    high = []
    low = []
    for series_id, row in latest.items():
        if "breadth" not in series_id:
            continue
        value = fnum(row.get("value"))
        if value is None:
            continue
        bit = f"{row.get('name') or series_id} {value:g}%"
        if value > BREADTH_HIGH:
            high.append(bit)
        elif value < BREADTH_LOW:
            low.append(bit)
    out = []
    if high:
        out.append(signal("风险", "参与度过高", "；".join(high), f"高于 {BREADTH_HIGH}%", "sentiment.html"))
    if low:
        out.append(signal("机会", "参与度过低", "；".join(low), f"低于 {BREADTH_LOW}%", "sentiment.html"))
    return out


def premium_signals(latest: dict[str, dict[str, str]]) -> list[dict[str, str]]:
    high = []
    low = []
    for series_id in ("etf_spx", "etf_ndx"):
        row = latest.get(series_id)
        if not row:
            continue
        value = fnum(row.get("value"))
        if value is None:
            continue
        bit = f"{row.get('name') or series_id} {value:g}%（{row.get('obs_date') or row.get('date')}）"
        if value > PREMIUM_HIGH:
            high.append(bit)
        elif value < PREMIUM_LOW:
            low.append(bit)
    out = []
    if high:
        out.append(signal("风险", "QDII ETF 溢价偏高", "；".join(high), f"高于 {PREMIUM_HIGH}%", "sentiment.html"))
    if low:
        out.append(signal("机会", "QDII ETF 折价", "；".join(low), f"低于 {PREMIUM_LOW}%", "sentiment.html"))
    return out


def earnings_signals(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    if not rows:
        return []
    latest = max(row.get("date") or "" for row in rows)
    day = [row for row in rows if row.get("date") == latest]
    out = []
    up = []
    down = []
    rsi = []
    triggers = []
    for row in day:
        rev = fnum(row.get("revision_30d"))
        if rev is not None and abs(rev) >= REVISION_EXTREME:
            continue
        signal_name = row.get("revision_signal") or ""
        counts = f"上调 {row.get('up30') or '—'} / 下调 {row.get('down30') or '—'}"
        if signal_name == "强上修":
            up.append(f"{row.get('ticker')}（{counts}）")
        elif signal_name == "强下修":
            down.append(f"{row.get('ticker')}（{counts}）")
        value = fnum(row.get("rsi"))
        if value is not None and (value > 70 or value < 30):
            rsi.append(f"{row.get('ticker')} {value:.1f}")
        if row.get("triggered") == "1":
            triggers.append(f"{row.get('ticker')} Forward PE {row.get('forward_pe') or '—'}，目标 {row.get('target_pe') or '—'}")
    if down:
        out.append(signal("风险", "盈利强下修", "、".join(down) + f"。笔记日期 {latest}", "强下修，且 30 日修正绝对值小于 50%。按家数，不按幅度", "earnings.html"))
    if up:
        out.append(signal("机会", "盈利强上修", "、".join(up) + f"。笔记日期 {latest}", "强上修，且 30 日修正绝对值小于 50%。按家数，不按幅度", "earnings.html"))
    if triggers:
        out.append(signal("机会", "估值触发", "、".join(triggers), "笔记把 Forward PE 标成触发", "earnings.html"))
    if rsi:
        out.append(signal("关注", "个股 RSI 在 30 以外", "、".join(rsi), "RSI 高于 70 或低于 30", "earnings.html"))
    return out


def price_week_signals(memory: list[dict[str, str]], gpu: list[dict[str, str]]) -> list[dict[str, str]]:
    down = []
    up = []
    for name_key, rows, label in (("product", memory, "存储"), ("gpu", gpu, "GPU")):
        for name, items in grouped(rows, name_key).items():
            found = lookback(series_points(items, value_key="value" if name_key == "product" else "price"), 7)
            if not found:
                continue
            _prev_day, _prev, last_day, _last, change = found
            bit = f"{label} {name} 7 日 {change:+.1f}%（截至 {last_day.isoformat()}）"
            if change <= -PRICE_WEEK:
                down.append(bit)
            elif change >= PRICE_WEEK:
                up.append(bit)
    out = []
    if down:
        out.append(signal("风险", "存储或 GPU 租金一周走弱", "；".join(down), f"自算 7 日变动 ≤ −{PRICE_WEEK}%", "semis.html"))
    if up:
        out.append(signal("机会", "存储或 GPU 租金一周走强", "；".join(up), f"自算 7 日变动 ≥ +{PRICE_WEEK}%", "semis.html"))
    return out


def usage_signals(router: list[dict[str, str]], silicon: list[dict[str, str]], korea: list[dict[str, str]]) -> list[dict[str, str]]:
    out = []
    week = [row for row in router if row.get("window") == "7日"]
    if week:
        change = fnum(week[-1].get("change_pct"))
        if change is not None and change >= ROUTER_WEEK:
            out.append(signal("机会", "OpenRouter 用量上升", f"7 日环比 {change:+.1f}%，截至 {week[-1].get('date')}", f"7 日环比 ≥ +{ROUTER_WEEK}%", "semis.html"))
        elif change is not None and change <= -ROUTER_WEEK:
            out.append(signal("风险", "OpenRouter 用量下降", f"7 日环比 {change:+.1f}%，截至 {week[-1].get('date')}", f"7 日环比 ≤ −{ROUTER_WEEK}%", "semis.html"))
    if silicon:
        row = silicon[-1]
        bits = []
        month = fnum(row.get("chg_30d_pct"))
        quarter = fnum(row.get("chg_90d_pct"))
        if month is not None and month <= SILICON_30:
            bits.append(f"30 日 {month:+.1f}%")
        if quarter is not None and quarter <= SILICON_90:
            bits.append(f"90 日 {quarter:+.1f}%")
        if bits:
            out.append(signal("关注", "SiliconData token 价格下行", "，".join(bits) + f"，截至 {row.get('date')}", f"30 日 ≤ {SILICON_30}% 或 90 日 ≤ {SILICON_90}%", "semis.html"))
    if korea:
        row = sorted(korea, key=lambda item: item.get("period") or "")[-1]
        value = fnum(row.get("month_yoy"))
        label = "全月同比"
        if value is None:
            value = fnum(row.get("d20_yoy"))
            label = "1–20 日同比"
        if value is None:
            value = fnum(row.get("d10_yoy"))
            label = "1–10 日同比"
        if value is not None and value >= KOREA_HIGH:
            out.append(signal("机会", "韩国芯片出口同比偏高", f"{row.get('period')} {label} {value:+.1f}%", f"同比 ≥ {KOREA_HIGH}%", "semis.html"))
        elif value is not None and value < 0:
            out.append(signal("风险", "韩国芯片出口同比为负", f"{row.get('period')} {label} {value:+.1f}%", "同比 < 0", "semis.html"))
    return out


def liquidity_signals(weekly: list[dict[str, str]], spreads: list[dict[str, str]], hy: list[dict[str, str]], vix: list[dict[str, str]], nfci: list[dict[str, str]], sentiment: dict[str, dict[str, str]]) -> list[dict[str, str]]:
    out = []
    if weekly:
        last = weekly[-1]
        pct = fnum(last.get("reserves_percentile"))
        if pct is not None and pct < RESERVE_RISK:
            out.append(signal("风险", "准备金分位很低", f"{last.get('date')} 约 {pct:.1f}%", f"低于 {RESERVE_RISK}%", "liquidity.html"))
        elif pct is not None and pct < RESERVE_WATCH:
            out.append(signal("关注", "准备金分位偏低", f"{last.get('date')} 约 {pct:.1f}%", f"低于 {RESERVE_WATCH}%，但不低于 {RESERVE_RISK}%", "liquidity.html"))
        points = series_points(weekly, value_key="net_liq_bn")
        change = level_shift(points, 28)
        if change is not None and change <= -NET_4W:
            out.append(signal("风险", "净流动性 4 周收缩", f"4 周 {change:+.0f} 十亿美元，截至 {last.get('date')}", f"4 周变动 ≤ −{NET_4W}", "liquidity.html"))
        elif change is not None and change >= NET_4W:
            out.append(signal("机会", "净流动性 4 周放松", f"4 周 {change:+.0f} 十亿美元，截至 {last.get('date')}", f"4 周变动 ≥ +{NET_4W}", "liquidity.html"))
    spread = latest_spread(spreads)
    if spread:
        gap = fnum(spread.get("sofr_iorb_bp"))
        if gap is not None and gap > 0:
            out.append(signal("风险", "SOFR 高于 IORB", f"{spread.get('date')} SOFR−IORB {gap:+.0f}bp", "大于 0bp", "liquidity.html"))
        elif gap is not None and SOFR_WATCH_LOW <= gap <= 0:
            out.append(signal("关注", "SOFR 接近 IORB", f"{spread.get('date')} SOFR−IORB {gap:+.0f}bp", f"{SOFR_WATCH_LOW}bp 到 0bp", "liquidity.html"))
    if nfci:
        value = fnum(nfci[-1].get("value"))
        if value is not None and value > 0:
            out.append(signal("风险", "NFCI 偏紧", f"{nfci[-1].get('date')} {value:.3f}", "大于 0", "liquidity.html"))
    if hy:
        points = [(parse_day(row.get("date", "")), fnum(row.get("value"))) for row in hy]
        points = [(day, value) for day, value in points if day and value is not None and day >= date(2022, 1, 1)]
        if points:
            last_day, last_val = points[-1]
            found = lookback(points, 28)
            widen = None
            if found:
                widen = (last_val - found[1]) * 100
            rank = percentile([value for _day, value in points], last_val)
            if (widen is not None and widen >= HY_WIDEN_BP) or last_val >= HY_LEVEL:
                reason = []
                if widen is not None and widen >= HY_WIDEN_BP:
                    reason.append(f"4 周走阔 {widen:+.0f}bp")
                if last_val >= HY_LEVEL:
                    reason.append(f"水平 {last_val:.2f}%")
                out.append(signal("风险", "高收益利差走阔", f"{last_day.isoformat()} " + "，".join(reason), f"4 周走阔 ≥ {HY_WIDEN_BP}bp，或水平 ≥ {HY_LEVEL}%", "liquidity.html"))
            elif rank <= HY_PERCENTILE:
                out.append(signal("关注", "高收益利差处于低位", f"{last_day.isoformat()} {last_val:.2f}%，2022 年以来约第 {rank:.0f} 分位", f"分位 ≤ {HY_PERCENTILE}%", "liquidity.html"))
    if vix:
        value = fnum(vix[-1].get("value"))
        if value is not None and value >= VIX_HIGH:
            out.append(signal("风险", "VIX 偏高", f"{vix[-1].get('date')} {value:.2f}", f"≥ {VIX_HIGH}", "liquidity.html"))
        elif value is not None and value <= VIX_LOW:
            out.append(signal("关注", "VIX 很低", f"{vix[-1].get('date')} {value:.2f}", f"≤ {VIX_LOW}", "liquidity.html"))
    year = sentiment.get("effr_year")
    if year:
        hikes = fnum(year.get("hike_count"))
        if hikes is not None and hikes >= HIKE_RISK:
            out.append(signal("风险", "年底隐含加息不少于 1 次", f"年底 EFFR {year.get('value')}，隐含加息 {hikes:g} 次（{year.get('obs_date') or year.get('date')}）", f"隐含加息 ≥ {HIKE_RISK} 次", "sentiment.html"))
    return out


def filing_signals(rows: list[dict[str, str]], today: date) -> list[dict[str, str]]:
    out = []
    risk = filing_hits(rows, today, FILING_RISK)
    watch = filing_hits(rows, today, FILING_WATCH)
    risk_ids = {(row.get("date"), row.get("ticker"), row.get("title")) for row in risk}
    watch = [row for row in watch if (row.get("date"), row.get("ticker"), row.get("title")) not in risk_ids]
    if risk:
        bits = [f"{row.get('date')} {row.get('ticker')} {row.get('title')}" for row in risk[:4]]
        out.append(signal("风险", "近 3 天公告里有敏感字样", "；".join(bits), "标题含辞职、诉讼、调查、减值、违约、下调", "earnings.html"))
    if watch:
        bits = [f"{row.get('date')} {row.get('ticker')} {row.get('title')}" for row in watch[:4]]
        out.append(signal("关注", "近 3 天公告里有交易字样", "；".join(bits), "标题含收购、协议", "earnings.html"))
    return out


def agenda(events: list[dict], today: date) -> list[dict]:
    end = (today + timedelta(days=7)).isoformat()
    start = today.isoformat()
    rows = [row for row in events if row.get("priority") == "高" and start <= row.get("date", "") <= end]
    return sorted(rows, key=lambda row: (row.get("date", ""), row.get("time_bj", ""), row.get("title", "")))


def freshness_table(today: date, items: list[tuple[str, str, str]]) -> list[dict]:
    """每块数据一行。过期与否写在表里，不再另写一条过期警告。"""
    out = []
    for name, when, kind in items:
        days = age_days(today, when[:10] if when else "")
        limit = WEEKLY_STALE if kind == "week" else DAILY_STALE
        if days is None:
            out.append({"name": name, "obs_date": "", "age_days": None, "status": "过期"})
            continue
        out.append({
            "name": name,
            "obs_date": when[:10],
            "age_days": days,
            "status": "过期" if days > limit else "正常",
        })
    return out


def latest_row(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    """每个序列取 obs_date 最大的一条；同一天再取笔记日期较新的那条。"""
    latest: dict[str, dict[str, str]] = {}
    for row in rows:
        series_id = row.get("series_id") or ""
        prev = latest.get(series_id)
        key = ((row.get("obs_date") or "")[:10], row.get("date") or "")
        if prev is None or key >= ((prev.get("obs_date") or "")[:10], prev.get("date") or ""):
            latest[series_id] = row
    return latest


def fred_tables(data_dir: Path) -> dict[str, dict[str, float]]:
    """series_id → {观测日: FRED 值}。文件不存在的序列不出现。"""
    out = {}
    for fred_id, series_id in FRED_CHECK.items():
        path = data_dir / "series" / f"{fred_id}.csv"
        if not path.exists():
            continue
        values = {}
        for item in load_csv(path):
            day = (item.get("date") or "")[:10]
            value = fnum(item.get("value"))
            if day and value is not None:
                values[day] = value
        out[series_id] = values
    return out


def with_fred_values(rows: list[dict[str, str]], tables: dict[str, dict[str, float]]) -> list[dict[str, str]]:
    """FRED 有当天值时换成收盘价。FRED 还没有的日期保留笔记原值。"""
    if not tables:
        return rows
    out = []
    for row in rows:
        values = tables.get(row.get("series_id") or "")
        obs = (row.get("obs_date") or "")[:10]
        if not values or obs not in values:
            out.append(row)
            continue
        copied = dict(row)
        copied["value"] = f"{values[obs]:g}"
        out.append(copied)
    return out


def mismatch_health(sentiment_rows: list[dict[str, str]], gpu: list[dict[str, str]], memory: list[dict[str, str]]) -> list[dict[str, str]]:
    out = []
    by_id = grouped(sentiment_rows, "series_id")
    for series_id in ("wti", "gold", "copper", "btc"):
        rows = by_id.get(series_id) or []
        prev, curr = fresh_pair(rows)
        if not prev or not curr:
            continue
        reported = (curr.get("change_text") or "").replace("%", "").replace("+", "")
        reported_value = fnum(reported)
        computed = pct_change(fnum(prev.get("value")), fnum(curr.get("value")))
        if reported_value is None or computed is None:
            continue
        if abs(reported_value - computed) >= 1:
            out.append(health(
                "警告",
                f"{curr.get('name') or series_id} 笔记涨跌写 {curr.get('change_text')}，按价格从 {prev.get('value')} 到 {curr.get('value')} 是 {computed:+.2f}%。页面用自算的数。",
            ))
    gpu_bits = []
    for name, rows in grouped(gpu, "gpu").items():
        points = series_points(rows, value_key="price")
        move = day_move(points)
        if not move or not rows:
            continue
        reported = fnum(rows[-1].get("chg_1d_pct"))
        _a, _b, _c, _d, computed = move
        if reported is not None and abs(reported - computed) >= 1:
            gpu_bits.append(f"{name} 笔记写 {reported:+.1f}%，按价格是 {computed:+.1f}%")
    if gpu_bits:
        out.append(health("警告", "GPU 租金的一日涨跌和价格对不上：" + "；".join(gpu_bits) + "。今日小结和信号用价格自算。"))
    return out


def carry_health(gpu: list[dict[str, str]], memory: list[dict[str, str]]) -> list[dict[str, str]]:
    bits = []
    for name_key, rows, value_key in (("gpu", gpu, "price"), ("product", memory, "value")):
        for name, items in grouped(rows, name_key).items():
            ordered = sorted(items, key=lambda row: row.get("date") or "")
            for prev, curr in zip(ordered, ordered[1:]):
                when = curr.get("date") or ""
                if when < "2026-09-01" or not price_carried(prev, curr, value_key):
                    continue
                bits.append(f"{name} {when}")
    if not bits:
        return []
    shown = "；".join(bits[:8]) + ("。" if len(bits) <= 8 else " 等。")
    return [health("提示", "这些日期按沿用处理，不计入新观测。价格和涨跌列都与前一天相同，或周末且价格没变：" + shown)]


def ratio_series(series_id: str) -> bool:
    """参与度和 ETF 溢价是比例，小修订不值得单独警告。"""
    return "breadth" in series_id or series_id in {"etf_spx", "etf_ndx"}


def conflict_health(sentiment_rows: list[dict[str, str]], tables: dict[str, dict[str, float]], today: date | None = None) -> list[dict[str, str]]:
    by_id = grouped(sentiment_rows, "series_id")
    settled = []
    open_conflicts = []
    cutoff = (today - timedelta(days=RATIO_DAYS)).isoformat() if today else ""
    for series_id, rows in by_id.items():
        seen: dict[str, set[str]] = {}
        for row in rows:
            obs = (row.get("obs_date") or "")[:10]
            value = row.get("value") or ""
            if obs and value:
                seen.setdefault(obs, set()).add(value)
        name = rows[-1].get("name") or series_id
        fred = tables.get(series_id) or {}
        for obs, values in seen.items():
            if len(values) < 2:
                continue
            if ratio_series(series_id):
                if cutoff and obs < cutoff:
                    continue
                numbers = [fnum(value) for value in values]
                if all(number is not None for number in numbers) and max(numbers) - min(numbers) <= RATIO_TOLERANCE:
                    continue
            shown = " 和 ".join(sorted(values, key=lambda item: (len(item), item)))
            if obs in fred:
                settled.append(f"{name} 观测日 {obs} 有 {shown}，FRED 为 {fred[obs]:g}，以 {fred[obs]:g} 为准")
            else:
                open_conflicts.append(f"{name} 观测日 {obs} 有 {shown}")
    out = []
    if settled:
        out.append(health("警告", "同一观测日出现了不同数字：" + "；".join(settled) + "。"))
    if open_conflicts:
        out.append(health("警告", "同一观测日出现了不同数字，页面用较新的那份笔记：" + "；".join(open_conflicts) + "。"))
    return out


def fred_health(data_dir: Path, sentiment_rows: list[dict[str, str]], tables: dict[str, dict[str, float]] | None = None) -> list[dict[str, str]]:
    """最近 10 个 FRED 交易日里，每个重叠观测日都比。同一天有多条笔记时，用笔记日期较新的那条。"""
    if tables is None:
        tables = fred_tables(data_dir)
    missing = [fred_id for fred_id, series_id in FRED_CHECK.items() if series_id not in tables]
    out = []
    if missing:
        out.append(health("警告", "还没有这些 FRED 利率序列，没法和笔记交叉核对：" + "、".join(missing) + "。"))
    gaps = []
    for fred_id, series_id in FRED_CHECK.items():
        fred = tables.get(series_id) or {}
        if not fred:
            continue
        window = set(sorted(fred)[-FRED_WINDOW:])
        chosen: dict[str, dict[str, str]] = {}
        for row in sentiment_rows:
            if row.get("series_id") != series_id:
                continue
            obs = (row.get("obs_date") or "")[:10]
            if obs not in window:
                continue
            prev = chosen.get(obs)
            if prev is None or (row.get("date") or "") >= (prev.get("date") or ""):
                chosen[obs] = row
        for obs, row in sorted(chosen.items()):
            note_value = fnum(row.get("value"))
            fred_value = fred.get(obs)
            if note_value is None or fred_value is None:
                continue
            if abs(round(note_value - fred_value, 4)) > FRED_GAP:
                gaps.append(f"{row.get('name') or series_id} 笔记 {note_value:g}，FRED {fred_id} {fred_value:g}（{obs}）")
    if gaps:
        out.append(health("警告", "笔记和 FRED 同一天相差超过 0.02 个百分点：" + "；".join(gaps) + "。"))
    return out


def currency_health(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    if not rows:
        return []
    latest = max(row.get("date") or "" for row in rows)
    names = []
    for row in rows:
        if row.get("date") != latest:
            continue
        ticker = row.get("ticker") or ""
        if ticker in USD_EPS_ADR:
            continue
        if (row.get("eps_unit") or "").upper() == "CNY" and (row.get("market") or "").upper() in {"", "US"}:
            names.append(ticker)
    if not names:
        return []
    return [health(
        "错误",
        "、".join(name for name in names if name) + " 的 EPS 单位是人民币，股价是美元 ADR。笔记没有写明 Forward PE 是否已按汇率换算。未核对之前，估值触发只当笔记原文，不当成已经确认的便宜。",
    )]


def extreme_health(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    if not rows:
        return []
    latest = max(row.get("date") or "" for row in rows)
    bits = []
    for row in rows:
        if row.get("date") != latest:
            continue
        value = fnum(row.get("revision_30d"))
        if value is not None and abs(value) >= REVISION_EXTREME:
            bits.append(f"{row.get('ticker')} {value:+.2f}%")
    if not bits:
        return []
    return [health("警告", "30 日修正绝对值达到 50%，标成异常，不参与总览信号：" + "、".join(bits) + "。")]


def source_health(meta: dict, events_payload: dict) -> list[dict[str, str]]:
    out = []
    failed = []
    for item in meta.get("series") or []:
        if item.get("last_fetch_ok") is False:
            failed.append(item.get("id") or item.get("name") or "")
    if failed:
        out.append(health("警告", "这些 FRED 序列上次没有抓到：" + "、".join(failed) + "。"))
    for source in events_payload.get("sources") or []:
        status = source.get("status") or ""
        if status in {"failed", "skipped"}:
            name = source.get("name") or ""
            level = "提示" if any(hint in name for hint in CALENDAR_HINTS) else "警告"
            out.append(health(level, f"日历来源 {name}：{source.get('detail') or status}。"))
    return out


def build_signals(data_dir: Path, today: date | None = None) -> dict:
    today = today or date.today()
    sentiment_rows = load_csv(data_dir / "sentiment" / "series.csv")
    latest = latest_row(sentiment_rows)
    fred = fred_tables(data_dir)
    weekly = load_csv(data_dir / "derived" / "weekly.csv")
    spreads = load_csv(data_dir / "derived" / "spreads.csv")
    earnings = load_csv(data_dir / "earnings" / "daily.csv")
    filings = load_csv(data_dir / "filings" / "announcements.csv")
    memory = load_csv(data_dir / "semis" / "memory.csv")
    gpu = load_csv(data_dir / "semis" / "gpu.csv")
    router = load_csv(data_dir / "semis" / "openrouter.csv")
    silicon = load_csv(data_dir / "semis" / "silicon.csv")
    korea = load_csv(data_dir / "semis" / "korea.csv")
    meta_path = data_dir / "meta.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}
    calendar_path = data_dir / "calendar" / "events.json"
    events_payload = json.loads(calendar_path.read_text(encoding="utf-8")) if calendar_path.exists() else {}
    rows = []
    rows.extend(liquidity_signals(
        weekly,
        spreads,
        load_csv(data_dir / "series" / "BAMLH0A0HYM2.csv"),
        load_csv(data_dir / "series" / "VIXCLS.csv"),
        load_csv(data_dir / "series" / "NFCI.csv"),
        latest,
    ))
    rows.extend(rate_level_signals(latest))
    rows.extend(mood_signal(latest))
    rows.extend(breadth_signals(latest))
    rows.extend(premium_signals(latest))
    rows.extend(earnings_signals(earnings))
    rows.extend(price_week_signals(memory, gpu))
    rows.extend(usage_signals(router, silicon, korea))
    rows.extend(filing_signals(filings, today))
    buckets = {"风险": [], "机会": [], "关注": []}
    for row in rows:
        buckets[row["bucket"]].append({key: value for key, value in row.items() if key != "bucket"})
    sentiment_obs = [
        (row.get("obs_date") or "")[:10]
        for row in sentiment_rows
        if row.get("series_id") != "btc" and row.get("obs_date")
    ]
    issues = []
    issues.extend(mismatch_health(sentiment_rows, gpu, memory))
    issues.extend(conflict_health(sentiment_rows, fred, today))
    issues.extend(extreme_health(earnings))
    issues.extend(currency_health(earnings))
    issues.extend(fred_health(data_dir, sentiment_rows, fred))
    issues.extend(source_health(meta, events_payload))
    issues.extend(carry_health(gpu, memory))
    issues.sort(key=lambda item: HEALTH_ORDER.get(item["level"], 9))
    spread = latest_spread(spreads)
    return {
        "asof": today.isoformat(),
        "signals": buckets,
        "agenda": agenda(events_payload.get("events") or [], today),
        "health": issues,
        "freshness": freshness_table(today, [
            ("流动性周三", weekly[-1]["date"] if weekly else "", "week"),
            ("SOFR/EFFR 利差", spread.get("date", "") if spread else "", "day"),
            ("情绪笔记", max(sentiment_obs) if sentiment_obs else "", "day"),
            ("盈利", max((row.get("date") or "" for row in earnings), default=""), "day"),
            ("公告", max((row.get("date") or "" for row in filings), default=""), "day"),
            ("存储", max((row.get("date") or "" for row in memory), default=""), "day"),
            ("GPU", max((row.get("date") or "" for row in gpu), default=""), "day"),
            ("OpenRouter", max((row.get("date") or "" for row in router), default=""), "day"),
            ("SiliconData", max((row.get("date") or "" for row in silicon), default=""), "day"),
            ("日历", (events_payload.get("today_bj") or (events_payload.get("generated_at") or "")[:10]), "day"),
        ]),
    }
