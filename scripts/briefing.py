#!/usr/bin/env python3
"""从已经整理好的 data/ 生成各页「今日小结」。

规则都写在这个文件里，同一份数据每次得到同一段话。
比较的是每个序列最近一条和它上一条，不猜笔记没写过的数字。

市场情绪
- 直接用最新一篇宏观指标笔记的「小结」，不另写。小结按句拆开。没有小结就写「今日无变动」。

盈利跟踪
- 估值触发达成、RSI 跨过 30 或 70、修正信号新变成强上修或强下修。
- 最新一天有公告或新闻稿。

半导体
- 存储或 GPU 的 1 日变动达到 5%，OpenRouter 7 日环比达到 10%，SiliconData 7 日达到 5%。
- 韩国出口：只有最新一期的 asof 比上一期更晚时，才写成新期间。笔记把各期 asof 覆盖成同一天时不报。

流动性（四段，数字都从 data/ 现算）
- 数量层：净流动性周变动达到 20（十亿美元）写边际放松或收紧，否则写变化不大。准备金分位不高于 25 写缓冲仍薄，不低于 50 写缓冲还厚。净流动性写本周和上周的周变动，准备金写本周周变动。净流动性公式里，WALCL、TGA、隔夜逆回购三项里贡献最大的那一项写主因。联储资产周变动绝对值小于 10 写基本横盘。准备金分位照 weekly.csv。隔夜逆回购低于 10 写缓冲基本用完。
- 价格层：用利差表最后一天，和至少早 7 天的那一天比。SOFR、EFFR 都低于 IORB 时写融资市场还没有确认稀缺。NFCI 为负写金融条件仍宽松，为正写偏紧。
- 信贷：银行总信贷 TOTBKCR、工商业贷款 TOTCI、存款 DPSACBW027SBOG，用最新值和大约一年前（不晚于 365 天前）的值算同比。两者都为正写信贷没有熄火。存款同比比上一周低 0.3 个百分点以上才写放缓。
- TGA 前景：读 data/liquidity/tga_outlook.json。峰值来自 2026-08-05 财政部季度再融资声明（https://home.treasury.gov/news/press-releases/sb0590）：10 月下旬约 1.05 万亿，上下 500 亿美元。高出本周 TGA 的差额按本周三的数来算。没有这个文件就不写这一段。

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


def signed_bn(value: float) -> str:
    text = f"{value:+.1f}"
    return text[:-2] if text.endswith(".0") else text


def plain_bn(value: float) -> str:
    text = f"{abs(value):.1f}"
    return text[:-2] if text.endswith(".0") else text


def pct_text(value: float) -> str:
    return f"{value:+.2f}%"


def bp_text(value: float) -> str:
    gap = abs(value)
    number = f"{gap:.0f}" if abs(gap - round(gap)) < 0.05 else f"{gap:.1f}"
    if value < -0.05:
        return f"低 {number}bp"
    if value > 0.05:
        return f"高 {number}bp"
    return "持平"


def yoy_pair(rows: list[dict[str, str]]) -> tuple[float, float] | None:
    points = [(row["date"], fnum(row.get("value", ""))) for row in rows if fnum(row.get("value", "")) is not None]
    if len(points) < 2:
        return None

    def ratio(index: int) -> float | None:
        if index < 0:
            index += len(points)
        day = date.fromisoformat(points[index][0])
        target = day - timedelta(days=365)
        base = None
        for obs, value in points[: index + 1]:
            if date.fromisoformat(obs) <= target:
                base = value
        if base in (None, 0):
            return None
        return (points[index][1] - base) / abs(base) * 100

    latest, previous = ratio(-1), ratio(-2)
    if latest is None or previous is None:
        return None
    return previous, latest


def liquidity_lines(weekly: list[dict[str, str]], spreads: list[dict[str, str]], nfci: list[dict[str, str]], credit: list[dict[str, str]], loans: list[dict[str, str]], deposits: list[dict[str, str]], outlook: dict | None) -> list[str]:
    lines: list[str] = []
    if len(weekly) >= 2:
        prev, curr = weekly[-2], weekly[-1]
        net = fnum(curr.get("net_liq_wow_bn", ""))
        prev_net = fnum(prev.get("net_liq_wow_bn", ""))
        reserves = fnum(curr.get("reserves_wow_bn", ""))
        tga = fnum(curr.get("tga_wow_bn", ""))
        walcl = fnum(curr.get("walcl_wow_bn", ""))
        rrp_wow = fnum(curr.get("on_rrp_wow_bn", ""))
        rrp = fnum(curr.get("on_rrp_bn", ""))
        percentile = fnum(curr.get("reserves_percentile", ""))
        if net is not None and net >= 20:
            tone = "本周边际放松"
        elif net is not None and net <= -20:
            tone = "本周边际收紧"
        else:
            tone = "本周变化不大"
        if percentile is not None and percentile <= 25:
            tone += "，但缓冲仍薄"
        elif percentile is not None and percentile >= 50:
            tone += "，缓冲还厚"
        bits = []
        if net is not None:
            prior = f"（上周 {signed_bn(prev_net)}）" if prev_net is not None else ""
            bits.append(f"净流动性代理 {signed_bn(net)}{prior}")
        if reserves is not None:
            bits.append(f"准备金 {signed_bn(reserves)}")
        drivers = []
        if tga is not None:
            drivers.append((abs(tga), f"TGA {'回落' if tga < 0 else '上升'} {plain_bn(tga)}"))
        if walcl is not None:
            drivers.append((abs(walcl), f"联储资产{'增加' if walcl > 0 else '减少'} {plain_bn(walcl)}"))
        if rrp_wow is not None:
            drivers.append((abs(rrp_wow), f"隔夜逆回购{'下降' if rrp_wow < 0 else '上升'} {plain_bn(rrp_wow)}"))
        if drivers:
            bits.append("主因是 " + max(drivers)[1])
        body = "，".join(bits)
        if walcl is not None:
            sheet = "联储资产负债表基本横盘" if abs(walcl) < 10 else f"联储资产负债表变动 {signed_bn(walcl)}"
            body = f"{body}；{sheet}" if body else sheet
        sentence = f"数量层：{tone}。" + (body + "。" if body else "")
        tail = []
        if percentile is not None:
            tail.append(f"准备金仍在 2022 年以来约第 {percentile:.1f} 分位")
        if rrp is not None:
            tail.append(f"隔夜逆回购{'只剩' if rrp < 10 else '还有'} {plain_bn(rrp)}")
        if tail:
            sentence += "，".join(tail) + "。"
        if rrp is not None and rrp < 10:
            sentence += "这层缓冲基本用完。"
        lines.append(sentence)

    usable = [row for row in spreads if fnum(row.get("sofr_iorb_bp", "")) is not None and fnum(row.get("effr_iorb_bp", "")) is not None]
    if usable:
        latest = usable[-1]
        latest_day = date.fromisoformat(latest["date"])
        earlier = [row for row in usable if date.fromisoformat(row["date"]) <= latest_day - timedelta(days=7)]
        prior = earlier[-1] if earlier else None
        sofr, effr = fnum(latest["sofr_iorb_bp"]), fnum(latest["effr_iorb_bp"])
        price = []
        if sofr is not None and effr is not None and sofr < 0 and effr < 0:
            price.append("融资市场还没有确认稀缺")
        elif sofr is not None and effr is not None and (sofr > 0 or effr > 0):
            price.append("融资利率已经到了 IORB 上方")
        sofr_bit = f"SOFR 比 IORB {bp_text(sofr)}"
        effr_bit = f"EFFR {bp_text(effr)}"
        old_sofr = old_effr = None
        if prior is not None:
            old_sofr, old_effr = fnum(prior["sofr_iorb_bp"]), fnum(prior["effr_iorb_bp"])
            if old_sofr is not None and abs(old_sofr - sofr) >= 0.05:
                sofr_bit += f"（一周前{bp_text(old_sofr)}）"
            if old_effr is not None and abs(old_effr - effr) >= 0.05:
                effr_bit += f"（一周前{bp_text(old_effr)}）"
        price.append(sofr_bit)
        price.append(effr_bit)
        if sofr is not None and effr is not None and sofr < 0 and effr < 0:
            closer = []
            if old_sofr is not None and sofr > old_sofr:
                closer.append("SOFR")
            if old_effr is not None and effr > old_effr:
                closer.append("EFFR")
            stay = "两者还在 IORB 下方"
            if closer:
                stay += "，" + "、".join(closer) + " 比一周前更接近转正"
            price.append(stay)
        nfci_points = [fnum(row.get("value", "")) for row in nfci if fnum(row.get("value", "")) is not None]
        if nfci_points:
            latest_nfci = nfci_points[-1]
            condition = "金融条件仍宽松" if latest_nfci < 0 else "金融条件偏紧" if latest_nfci > 0 else "金融条件接近中性"
            price.append(f"NFCI {latest_nfci:.3f}，{condition}")
        lines.append("价格层：" + "。".join(price) + "。")

    credit_yoy, loan_yoy, deposit_yoy = yoy_pair(credit), yoy_pair(loans), yoy_pair(deposits)
    if credit_yoy and loan_yoy and deposit_yoy:
        credit_now, loan_now, deposit_prev, deposit_now = credit_yoy[1], loan_yoy[1], deposit_yoy[0], deposit_yoy[1]
        head = "信贷没有熄火" if credit_now > 0 and loan_now > 0 else "信贷同比转弱"
        deposit_bit = f"存款同比 {pct_text(deposit_now)}"
        if deposit_prev - deposit_now >= 0.3:
            deposit_bit = f"存款同比从 {deposit_prev:.2f}% 放缓到 {deposit_now:.2f}%"
        elif deposit_now - deposit_prev >= 0.3:
            deposit_bit = f"存款同比从 {deposit_prev:.2f}% 加快到 {deposit_now:.2f}%"
        lines.append(f"{head}。银行总信贷同比 {pct_text(credit_now)}，工商业贷款 {pct_text(loan_now)}；{deposit_bit}。")

    if outlook and len(weekly) >= 1:
        peak = fnum(str(outlook.get("peak_bn", "")))
        band = fnum(str(outlook.get("band_bn", "")))
        current = fnum(weekly[-1].get("tga_bn", ""))
        when = outlook.get("when") or ""
        if peak is not None and current is not None and peak > current:
            peak_text = f"{peak / 1000:.2f}".rstrip("0").rstrip(".")
            gap = peak - current
            band_text = f"（上下 {round(band * 10):,} 亿）" if band is not None else ""
            lines.append(
                f"下一段压力来自 TGA。财政部 {outlook.get('stated_on', '')} 的季度再融资声明估计，"
                f"TGA 在 {when}升到约 {peak_text} 万亿{band_text}，比本周高约 {round(gap * 10):,} 亿。"
                "TGA 上去，净流动性会被压低。"
            )
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


def sentiment_note(rows: list[dict[str, str]]) -> list[str]:
    if not rows:
        return []
    text = (rows[-1].get("text") or "").strip()
    if not text:
        return []
    parts = [part.strip() for part in text.split("。") if part.strip()]
    return [part if part.endswith("。") else part + "。" for part in parts]


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
    outlook_path = data_dir / "liquidity" / "tga_outlook.json"
    outlook = json.loads(outlook_path.read_text(encoding="utf-8")) if outlook_path.exists() else None
    pages = {
        "liquidity": cap(liquidity_lines(
            weekly,
            spreads,
            load_csv(data_dir / "series" / "NFCI.csv"),
            load_csv(data_dir / "series" / "TOTBKCR.csv"),
            load_csv(data_dir / "series" / "TOTCI.csv"),
            load_csv(data_dir / "series" / "DPSACBW027SBOG.csv"),
            outlook,
        )),
        "sentiment": cap(sentiment_note(load_csv(data_dir / "sentiment" / "summary.csv"))),
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
