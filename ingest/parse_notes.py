#!/usr/bin/env python3
"""把 Hermes 早晨笔记（Markdown + YAML 头）整理进 data/。

只使用 Python 标准库。重复运行同一批笔记不会制造重复行：按主键覆盖，
空值和「未更新 / 抓取失败」不会把已有数字抹掉。

日期优先用文首 data_date，没有则从文件名里的 YYYY-MM-DD 取。
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from decimal import Decimal, InvalidOperation
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

MISSING_TOKENS = {
    "",
    "—",
    "-",
    "–",
    "无",
    "n/a",
    "na",
    "null",
    "none",
    "low_sample",
    "low_base",
}
FAIL_MARKERS = ("未更新", "抓取失败")

SERIES_RULES: list[tuple[str, str, str, str]] = [
    ("CNN 恐贪", "cnn_fg", "CNN 恐贪指数", "点"),
    ("AAII", "aaii", "AAII 牛熊差", "百分点"),
    ("标普500 RSI", "spx_rsi", "标普500 RSI(14)", "点"),
    ("纳斯达克 RSI", "nasdaq_rsi", "纳斯达克 RSI(14)", "点"),
    ("10Y-2Y", "t10y2y", "10年减2年美债利差", "百分点"),
    ("高收益债", "hy_oas", "高收益债信用利差", "百分点"),
    ("10年期实际利率", "tips_10y", "10年期实际利率", "百分比"),
    ("US_10y", "us_10y", "美国10年期国债收益率", "百分比"),
    ("US_2y", "us_2y", "美国2年期国债收益率", "百分比"),
    ("VIX", "vix", "VIX", "点"),
    ("博时标普500", "etf_spx", "博时标普500ETF溢价率", "百分比"),
    ("广发纳指", "etf_ndx", "广发纳指ETF溢价率", "百分比"),
    ("标普参与度>20", "spx_breadth_20", "标普成分高于20日均线的比例", "百分比"),
    ("标普参与度>50", "spx_breadth_50", "标普成分高于50日均线的比例", "百分比"),
    ("标普参与度>200", "spx_breadth_200", "标普成分高于200日均线的比例", "百分比"),
    ("纳指100参与度>20", "ndx_breadth_20", "纳指100高于20日均线的比例", "百分比"),
    ("纳指100参与度>50", "ndx_breadth_50", "纳指100高于50日均线的比例", "百分比"),
    ("纳指100参与度>200", "ndx_breadth_200", "纳指100高于200日均线的比例", "百分比"),
    ("WTI", "wti", "WTI 原油期货", "美元"),
    ("COMEX黄金", "gold", "COMEX 黄金", "美元"),
    ("黄金", "gold", "COMEX 黄金", "美元"),
    ("COMEX铜", "copper", "COMEX 铜", "美元"),
    ("铜", "copper", "COMEX 铜", "美元"),
    ("美元兑人民币", "usdcny", "美元兑人民币", "人民币"),
    ("btc", "btc", "比特币", "美元"),
]


def log(msg: str) -> None:
    print(msg, flush=True)


def strip_html(text: str) -> str:
    text = re.sub(r"<[^>]+>", "", text)
    return text.replace("&nbsp;", " ").replace("&amp;", "&").strip()


def clean_cell(text: str) -> str:
    return re.sub(r"\s+", " ", strip_html(text)).strip()


def is_fail_text(text: str) -> bool:
    compact = clean_cell(text).replace(" ", "")
    return any(mark in compact for mark in FAIL_MARKERS) and not re.search(r"\d", compact)


def parse_decimal(text: str) -> str | None:
    raw = clean_cell(text)
    if not raw:
        return None
    lowered = raw.lower().replace(" ", "")
    if lowered in MISSING_TOKENS or is_fail_text(raw):
        return None
    match = re.search(r"[-+]?\d+(?:\.\d+)?", raw.replace(",", ""))
    if not match:
        return None
    try:
        return format(Decimal(match.group(0)), "f")
    except InvalidOperation:
        return None


def parse_percent(text: str) -> str | None:
    raw = clean_cell(text)
    if not raw or is_fail_text(raw):
        return None
    match = re.search(r"([-+]?\d+(?:\.\d+)?)\s*%", raw.replace(",", ""))
    if not match:
        return None
    try:
        return format(Decimal(match.group(1)), "f")
    except InvalidOperation:
        return None


def split_frontmatter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    meta: dict[str, str] = {}
    for line in parts[1].splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        meta[key.strip()] = value.strip().strip('"').strip("'")
    return meta, parts[2]


def filename_date(path: Path) -> str:
    match = re.search(r"(20\d{2}-\d{2}-\d{2})", path.name)
    return match.group(1) if match else ""


def note_date(meta: dict[str, str], path: Path) -> str:
    for key in ("data_date", "date_date"):
        value = meta.get(key, "")
        value = value.replace("/", "-")
        if re.fullmatch(r"20\d{2}-\d{2}-\d{2}", value):
            return value
    return filename_date(path)


def parse_tables(body: str) -> list[list[dict[str, str]]]:
    tables: list[list[dict[str, str]]] = []
    lines = body.splitlines()
    i = 0
    while i < len(lines):
        if not lines[i].strip().startswith("|"):
            i += 1
            continue
        block: list[str] = []
        while i < len(lines) and lines[i].strip().startswith("|"):
            block.append(lines[i].strip())
            i += 1
        if len(block) < 2:
            continue
        header = split_row(block[0])
        start = 1
        if start < len(block) and is_separator(block[start]):
            start += 1
        rows: list[dict[str, str]] = []
        for line in block[start:]:
            if is_separator(line):
                continue
            cells = split_row(line)
            if not any(cells):
                continue
            row = {}
            for idx, key in enumerate(header):
                if not key:
                    continue
                row[key] = cells[idx] if idx < len(cells) else ""
            if row:
                rows.append(row)
        if rows:
            tables.append(rows)
    return tables


def split_row(line: str) -> list[str]:
    text = line.strip()
    if text.startswith("|"):
        text = text[1:]
    if text.endswith("|"):
        text = text[:-1]
    return [clean_cell(cell) for cell in text.split("|")]


def is_separator(line: str) -> bool:
    return bool(re.fullmatch(r"[\s|:\-]+", line.strip()))


def header_key(name: str) -> str:
    return re.sub(r"\s+", "", name).lower()


def classify(path: Path) -> str:
    name = path.name
    if "宏观指标" in name:
        return "sentiment"
    if "盈利跟踪" in name:
        return "earnings"
    if "存储价格" in name:
        return "memory"
    if "GPU" in name:
        return "gpu"
    if "OpenRouter" in name:
        return "openrouter"
    if "SiliconData" in name:
        return "silicon"
    if "韩国出口" in name:
        return "korea"
    return ""


def series_info(raw_name: str) -> tuple[str, str, str]:
    compact = raw_name.replace(" ", "")
    rules = sorted(SERIES_RULES, key=lambda item: len(item[0].replace(" ", "")), reverse=True)
    for needle, series_id, name, unit in rules:
        if needle.replace(" ", "") in compact or needle.lower() in raw_name.lower():
            return series_id, name, unit
    slug = re.sub(r"\s+", "", raw_name)[:40] or "unknown"
    return slug, raw_name, ""


def sentiment_label(raw: str) -> str:
    text = clean_cell(raw)
    if text in {"恐慌", "中性", "贪婪", "机会", "风险"}:
        return text
    lowered = text.lower()
    if lowered == "fear":
        return "恐慌"
    if lowered == "greed":
        return "贪婪"
    if lowered in {"neutral", "中性"}:
        return "中性"
    return ""


def carried_flag(remark: str) -> str:
    text = remark or ""
    if any(word in text for word in ("未更新", "沿用", "使用最近", "休市")):
        return "1"
    return ""


def load_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def upsert(existing: list[dict[str, str]], incoming: list[dict[str, str]], keys: list[str]) -> list[dict[str, str]]:
    merged: dict[tuple[str, ...], dict[str, str]] = {}
    for row in existing:
        merged[tuple(row.get(key, "") for key in keys)] = dict(row)
    for row in incoming:
        if any(not row.get(key) for key in keys):
            continue
        key = tuple(row.get(field, "") for field in keys)
        current = dict(merged.get(key, {}))
        for field, value in row.items():
            if value not in ("", None):
                current[field] = value
        for field in keys:
            current.setdefault(field, row.get(field, ""))
        merged[key] = current
    return sorted(merged.values(), key=lambda row: tuple(row.get(key, "") for key in keys))


def write_csv(path: Path, rows: list[dict[str, str]], columns: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, lineterminator="\n", extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({col: row.get(col, "") for col in columns})
    tmp.replace(path)


def parse_sentiment(path: Path, meta: dict[str, str], body: str, skipped: list[dict[str, str]]) -> tuple[list[dict[str, str]], dict[str, str] | None]:
    day = note_date(meta, path)
    rows: list[dict[str, str]] = []
    if not day:
        skipped.append({"area": "sentiment", "date": "", "key": path.name, "field": "date", "raw": "", "reason": "没有 data_date，文件名里也没有日期"})
        return rows, None
    for table in parse_tables(body):
        if "指标" not in table[0] or "数值" not in table[0]:
            continue
        for item in table:
            name = item.get("指标", "")
            raw_value = item.get("数值", "")
            if is_fail_text(raw_value):
                skipped.append({"area": "sentiment", "date": day, "key": name, "field": "数值", "raw": raw_value, "reason": "单元格标明未更新或抓取失败"})
                continue
            value = parse_decimal(raw_value)
            if value is None:
                if raw_value:
                    skipped.append({"area": "sentiment", "date": day, "key": name, "field": "数值", "raw": raw_value, "reason": "没有可解析的数字"})
                continue
            series_id, series_name, unit = series_info(name)
            label_raw = item.get("情绪") or item.get("机会or风险or中性") or ""
            obs = item.get("日期", "")
            if not re.fullmatch(r"20\d{2}-\d{2}-\d{2}", obs):
                obs = ""
            rows.append({
                "date": day,
                "series_id": series_id,
                "name": series_name,
                "value": value,
                "unit": unit,
                "change_text": item.get("涨跌幅", ""),
                "label": sentiment_label(label_raw),
                "obs_date": obs,
                "carried": carried_flag(item.get("备注", "")),
                "source": path.name,
            })
    composite = None
    for line in body.splitlines():
        if "综合：" not in line and "综合:" not in line:
            continue
        text = clean_cell(line.lstrip("-").strip())
        label_match = re.search(r"综合[:：]\s*([^（(]+)", text)
        score_match = re.search(r"加权分\s*([+-]?\d+(?:\.\d+)?)", text)
        cnn_match = re.search(r"CNN官方\s*=\s*([^\s；;）)]+)", text)
        composite = {
            "date": day,
            "label": label_match.group(1).strip() if label_match else "",
            "score": score_match.group(1) if score_match else "",
            "cnn_official": cnn_match.group(1) if cnn_match else "",
            "text": text,
            "source": path.name,
        }
        break
    return rows, composite


EARNINGS_ALIASES = {
    "ticker": "ticker",
    "公司名": "company",
    "market": "market",
    "收盘价": "close",
    "当日涨跌幅": "day_pct",
    "涨跌幅": "day_pct",
    "rsi(14)": "rsi",
    "rsi": "rsi",
    "eps合计": "eps_sum",
    "forwardpe": "forward_pe",
    "目标pe": "target_pe",
    "触发": "triggered",
    "下财年eps": "next_fy_eps",
    "30日修正%": "revision_30d",
    "up30": "up30",
    "down30": "down30",
    "修正信号": "revision_signal",
    "状态": "status",
    "flags": "flags",
    "is_trading_day": "is_trading_day",
    "财报单位": "eps_unit",
}
NUMERIC_EARNINGS = {"close", "day_pct", "rsi", "eps_sum", "forward_pe", "target_pe", "next_fy_eps", "revision_30d", "up30", "down30"}


def parse_earnings(path: Path, meta: dict[str, str], body: str, skipped: list[dict[str, str]]) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    day = note_date(meta, path)
    quotes: list[dict[str, str]] = []
    events: list[dict[str, str]] = []
    if not day:
        skipped.append({"area": "earnings", "date": "", "key": path.name, "field": "date", "raw": "", "reason": "没有日期"})
        return quotes, events
    for table in parse_tables(body):
        headers = {header_key(key): key for key in table[0]}
        if "ticker" not in headers:
            continue
        for item in table:
            ticker = clean_cell(item.get(headers["ticker"], "")).upper()
            if not ticker or ticker in {"TICKER", "—"}:
                continue
            row = {"date": day, "ticker": ticker, "source": path.name}
            for alias, field in EARNINGS_ALIASES.items():
                original = headers.get(alias)
                if not original or field in {"ticker"}:
                    continue
                raw = item.get(original, "")
                if field in NUMERIC_EARNINGS:
                    if is_fail_text(raw):
                        skipped.append({"area": "earnings", "date": day, "key": ticker, "field": field, "raw": raw, "reason": "单元格标明未更新或抓取失败"})
                        continue
                    if field == "day_pct" or field == "revision_30d":
                        number = parse_percent(raw) or parse_decimal(raw)
                    else:
                        number = parse_decimal(raw)
                    if number is not None:
                        row[field] = number
                elif field == "triggered":
                    row[field] = "1" if any(mark in raw for mark in ("✔️", "✓", "✔")) else "0"
                elif raw and not is_fail_text(raw):
                    row[field] = raw
            quotes.append(row)
    for line in body.splitlines():
        if "财报" not in line:
            continue
        if re.search(r"财报[*]*[:：]\s*无", line):
            continue
        for company, ticker, when in re.findall(r"([^；;。\n]{0,80}?)\(([A-Za-z0-9.]+)\)\s*(20\d{2}-\d{2}-\d{2})", line):
            company_name = clean_cell(company)
            company_name = re.split(r"[:：]", company_name)[-1].strip(" ：:")
            events.append({
                "note_date": day,
                "ticker": ticker.upper(),
                "company": company_name,
                "earnings_date": when,
                "source": path.name,
            })
    return quotes, events


def parse_memory(path: Path, meta: dict[str, str], body: str, skipped: list[dict[str, str]]) -> list[dict[str, str]]:
    day = note_date(meta, path)
    rows: list[dict[str, str]] = []
    for table in parse_tables(body):
        if "指标" not in table[0]:
            continue
        if not any("统一口径" in key or "原始报价" in key for key in table[0]):
            continue
        for item in table:
            product = item.get("指标", "")
            raw = item.get("统一口径") or item.get("原始报价") or ""
            if is_fail_text(raw):
                skipped.append({"area": "memory", "date": day, "key": product, "field": "统一口径", "raw": raw, "reason": "单元格标明未更新或抓取失败"})
                continue
            value = parse_decimal(raw)
            if value is None:
                continue
            unit_match = re.search(r"(USD/[A-Za-z]+|USD)", clean_cell(raw))
            rows.append({
                "date": day,
                "product": product,
                "value": value,
                "unit": unit_match.group(1) if unit_match else "",
                "chg_1d_pct": parse_percent(item.get("相比1D", "")) or "",
                "chg_7d_pct": parse_percent(item.get("相比7D", "")) or "",
                "chg_30d_pct": parse_percent(item.get("相比30D", "")) or "",
                "source": path.name,
            })
    return rows


def parse_gpu(path: Path, meta: dict[str, str], body: str, skipped: list[dict[str, str]]) -> list[dict[str, str]]:
    day = note_date(meta, path)
    rows: list[dict[str, str]] = []
    for table in parse_tables(body):
        if "昨日价格" not in table[0] or "指标" not in table[0]:
            continue
        for item in table:
            name = item.get("指标", "")
            raw = item.get("昨日价格", "")
            if is_fail_text(raw):
                skipped.append({"area": "gpu", "date": day, "key": name, "field": "昨日价格", "raw": raw, "reason": "单元格标明未更新或抓取失败"})
                continue
            price = parse_decimal(raw)
            if price is None:
                continue
            rows.append({
                "date": day,
                "gpu": name.replace(" median", "").replace(" Median", ""),
                "price": price,
                "unit": meta.get("price_unit") or "USD/GPU-hour",
                "chg_1d_pct": parse_percent(item.get("相比昨天", "")) or "",
                "chg_7d_pct": parse_percent(item.get("相比上周", "")) or "",
                "chg_30d_pct": parse_percent(item.get("相比上月", "")) or "",
                "chg_90d_pct": parse_percent(item.get("相比上季", "")) or "",
                "source": path.name,
            })
    return rows


def parse_openrouter(path: Path, meta: dict[str, str], body: str, skipped: list[dict[str, str]]) -> list[dict[str, str]]:
    day = note_date(meta, path)
    rows: list[dict[str, str]] = []
    for table in parse_tables(body):
        if "当前值" not in table[0] or "指标" not in table[0]:
            continue
        for item in table:
            window = item.get("指标", "")
            if window not in {"1日", "7日", "30日"}:
                continue
            raw = item.get("当前值", "")
            if is_fail_text(raw):
                skipped.append({"area": "openrouter", "date": day, "key": window, "field": "当前值", "raw": raw, "reason": "单元格标明未更新或抓取失败"})
                continue
            value = parse_decimal(raw)
            if value is None:
                continue
            unit = "T" if "T" in raw else ""
            rows.append({
                "date": day,
                "window": window,
                "tokens": value,
                "unit": unit,
                "change_pct": parse_percent(item.get("环比", "")) or "",
                "note": item.get("历史提示", ""),
                "source": path.name,
            })
        if rows:
            break
    return rows


def parse_silicon(path: Path, meta: dict[str, str], body: str, skipped: list[dict[str, str]]) -> list[dict[str, str]]:
    note_day = note_date(meta, path)
    kv: dict[str, str] = {}
    for table in parse_tables(body):
        if "指标" in table[0] and ("值" in table[0] or "数值" in table[0]):
            value_key = "值" if "值" in table[0] else "数值"
            for item in table:
                kv[item.get("指标", "")] = item.get(value_key, "")
    raw_value = ""
    for key, value in kv.items():
        if "最新" in key and "日期" not in key:
            raw_value = value
            break
    if is_fail_text(raw_value):
        skipped.append({"area": "silicon", "date": note_day, "key": "index", "field": "最新", "raw": raw_value, "reason": "单元格标明未更新或抓取失败"})
        return []
    value = parse_decimal(raw_value)
    if value is None:
        return []
    obs = kv.get("最新日期", "")
    if not re.fullmatch(r"20\d{2}-\d{2}-\d{2}", obs):
        obs = note_day
    return [{
        "date": obs,
        "value": value,
        "unit": "USD/M tokens",
        "chg_7d_pct": parse_percent(kv.get("环比7D", "")) or "",
        "chg_30d_pct": parse_percent(kv.get("环比30D", "")) or "",
        "chg_90d_pct": parse_percent(kv.get("环比90天", "")) or "",
        "note_date": note_day,
        "source": path.name,
    }]


KOREA_FIELDS = {
    "前10日芯片(百万USD)": "d10_usd_mn",
    "前10日YoY%": "d10_yoy",
    "前10日占比%": "d10_share",
    "前20日芯片(百万USD)": "d20_usd_mn",
    "前20日YoY%": "d20_yoy",
    "前20日占比%": "d20_share",
    "全月芯片(百万USD)": "month_usd_mn",
    "全月YoY%": "month_yoy",
    "全月占比%": "month_share",
}


def parse_korea(path: Path, meta: dict[str, str], body: str, skipped: list[dict[str, str]]) -> list[dict[str, str]]:
    asof = note_date(meta, path)
    rows: list[dict[str, str]] = []
    for table in parse_tables(body):
        if "期间" not in table[0]:
            continue
        for item in table:
            period = item.get("期间", "")
            if not re.fullmatch(r"20\d{2}-\d{2}", period):
                continue
            row = {"period": period, "asof": asof, "source": path.name}
            for original, field in KOREA_FIELDS.items():
                raw = item.get(original, "")
                if is_fail_text(raw):
                    skipped.append({"area": "korea", "date": asof, "key": period, "field": field, "raw": raw, "reason": "单元格标明未更新或抓取失败"})
                    continue
                number = parse_decimal(raw)
                if number is not None:
                    row[field] = number
            if any(row.get(field) for field in KOREA_FIELDS.values()):
                rows.append(row)
    return rows


def latest_date(rows: list[dict[str, str]], field: str) -> str:
    dates = [row.get(field, "") for row in rows if row.get(field)]
    return max(dates) if dates else ""


def earliest_date(rows: list[dict[str, str]], field: str) -> str:
    dates = [row.get(field, "") for row in rows if row.get(field)]
    return min(dates) if dates else ""


# 这些键属于流动性抓取。整理笔记时先抄下来，写完再放回去。
LIQUIDITY_META_KEYS = (
    "updated_at",
    "history_start",
    "display_unit",
    "spread_unit",
    "net_liquidity",
    "weekly_change",
    "spreads",
    "reserves_percentile",
    "files",
    "series",
    "latest_wednesday",
    "derived_refresh",
)


def build_meta(existing: dict, bundles: dict) -> dict:
    preserved = {key: existing[key] for key in LIQUIDITY_META_KEYS if key in existing}
    sentiment = bundles["sentiment"]
    composite = bundles["composite"]
    earnings = bundles["earnings"]
    events = bundles["events"]
    existing["sentiment"] = {
        "name": "市场情绪",
        "source": "Hermes 早晨笔记 inbox/notes/每日/宏观指标_YYYY-MM-DD.md",
        "history_start": earliest_date(sentiment, "date"),
        "history_end": latest_date(sentiment, "date"),
        "observations": len(sentiment),
        "composite_end": latest_date(composite, "date"),
        "files": {
            "series": "sentiment/series.csv",
            "composite": "sentiment/composite.csv",
        },
        "note": "日期是笔记的 data_date。obs_date 是该指标自己的观测日，可能更早。carried=1 表示笔记写明这是沿用的最近可得值。",
    }
    existing["earnings"] = {
        "name": "盈利跟踪",
        "source": "Hermes 早晨笔记 inbox/notes/每日/盈利跟踪_YYYY-MM-DD.md 或 美港股盈利跟踪_YYYY-MM-DD.md",
        "history_start": earliest_date(earnings, "date"),
        "history_end": latest_date(earnings, "date"),
        "rows": len(earnings),
        "events": len(events),
        "files": {
            "daily": "earnings/daily.csv",
            "events": "earnings/events.csv",
        },
        "note": "涨跌幅和 30 日修正都是百分数，不带百分号。triggered=1 表示笔记里的估值触发。",
    }
    existing["semis"] = {
        "name": "半导体景气",
        "source": "Hermes 早晨笔记 inbox/notes/半导体/YYYY-MM-DD_半导体-*.md",
        "files": {
            "memory": "semis/memory.csv",
            "gpu": "semis/gpu.csv",
            "openrouter": "semis/openrouter.csv",
            "silicon": "semis/silicon.csv",
            "korea": "semis/korea.csv",
        },
        "memory": {"start": earliest_date(bundles["memory"], "date"), "end": latest_date(bundles["memory"], "date")},
        "gpu": {"start": earliest_date(bundles["gpu"], "date"), "end": latest_date(bundles["gpu"], "date"), "unit": "USD/GPU-hour"},
        "openrouter": {"start": earliest_date(bundles["openrouter"], "date"), "end": latest_date(bundles["openrouter"], "date"), "unit": "万亿 token"},
        "silicon": {"start": earliest_date(bundles["silicon"], "date"), "end": latest_date(bundles["silicon"], "date"), "unit": "USD/M tokens"},
        "korea": {"start": earliest_date(bundles["korea"], "period"), "end": latest_date(bundles["korea"], "period"), "unit": "百万美元", "note": "月度数据，按期间覆盖；空的全月数字不会抹掉已有值。"},
    }
    ends = [
        existing["sentiment"]["history_end"],
        existing["earnings"]["history_end"],
        existing["semis"]["memory"]["end"],
        existing["semis"]["gpu"]["end"],
        existing["semis"]["openrouter"]["end"],
        existing["semis"]["silicon"]["end"],
        existing["semis"]["korea"]["end"],
    ]
    existing["notes_asof"] = max((item for item in ends if item), default="")
    existing.update(preserved)
    return existing


def main() -> int:
    parser = argparse.ArgumentParser(description="把 Hermes 笔记整理进 data/")
    parser.add_argument("--notes", action="append", default=[], help="笔记根目录，可重复。默认 inbox/notes")
    args = parser.parse_args()
    roots = [Path(item) for item in args.notes] or [ROOT / "inbox" / "notes"]

    files: list[Path] = []
    for root in roots:
        if not root.exists():
            log(f"SKIP 目录不存在 {root}")
            continue
        for path in root.rglob("*.md"):
            if path.name.startswith("._") or "/._" in str(path):
                continue
            if classify(path):
                files.append(path)
    files.sort(key=lambda path: (filename_date(path), str(path)))

    incoming = {
        "sentiment": [],
        "composite": [],
        "earnings": [],
        "events": [],
        "memory": [],
        "gpu": [],
        "openrouter": [],
        "silicon": [],
        "korea": [],
    }
    skipped: list[dict[str, str]] = []
    used = 0
    for path in files:
        text = path.read_text(encoding="utf-8", errors="replace")
        meta, body = split_frontmatter(text)
        kind = classify(path)
        if kind == "sentiment":
            rows, composite = parse_sentiment(path, meta, body, skipped)
            incoming["sentiment"].extend(rows)
            if composite:
                incoming["composite"].append(composite)
        elif kind == "earnings":
            quotes, events = parse_earnings(path, meta, body, skipped)
            incoming["earnings"].extend(quotes)
            incoming["events"].extend(events)
        elif kind == "memory":
            incoming["memory"].extend(parse_memory(path, meta, body, skipped))
        elif kind == "gpu":
            incoming["gpu"].extend(parse_gpu(path, meta, body, skipped))
        elif kind == "openrouter":
            incoming["openrouter"].extend(parse_openrouter(path, meta, body, skipped))
        elif kind == "silicon":
            incoming["silicon"].extend(parse_silicon(path, meta, body, skipped))
        elif kind == "korea":
            incoming["korea"].extend(parse_korea(path, meta, body, skipped))
        used += 1
        log(f"PARSED {kind} {path.name}")

    specs = {
        "sentiment": ("sentiment/series.csv", ["date", "series_id"], ["date", "series_id", "name", "value", "unit", "change_text", "label", "obs_date", "carried", "source"]),
        "composite": ("sentiment/composite.csv", ["date"], ["date", "label", "score", "cnn_official", "text", "source"]),
        "earnings": ("earnings/daily.csv", ["date", "ticker"], ["date", "ticker", "company", "market", "close", "day_pct", "rsi", "eps_sum", "forward_pe", "target_pe", "triggered", "next_fy_eps", "revision_30d", "up30", "down30", "revision_signal", "status", "flags", "is_trading_day", "eps_unit", "source"]),
        "events": ("earnings/events.csv", ["note_date", "ticker", "earnings_date"], ["note_date", "ticker", "company", "earnings_date", "source"]),
        "memory": ("semis/memory.csv", ["date", "product"], ["date", "product", "value", "unit", "chg_1d_pct", "chg_7d_pct", "chg_30d_pct", "source"]),
        "gpu": ("semis/gpu.csv", ["date", "gpu"], ["date", "gpu", "price", "unit", "chg_1d_pct", "chg_7d_pct", "chg_30d_pct", "chg_90d_pct", "source"]),
        "openrouter": ("semis/openrouter.csv", ["date", "window"], ["date", "window", "tokens", "unit", "change_pct", "note", "source"]),
        "silicon": ("semis/silicon.csv", ["date"], ["date", "value", "unit", "chg_7d_pct", "chg_30d_pct", "chg_90d_pct", "note_date", "source"]),
        "korea": ("semis/korea.csv", ["period"], ["period", "d10_usd_mn", "d10_yoy", "d10_share", "d20_usd_mn", "d20_yoy", "d20_share", "month_usd_mn", "month_yoy", "month_share", "asof", "source"]),
    }
    stored: dict[str, list[dict[str, str]]] = {}
    for key, (rel, keys, columns) in specs.items():
        path = DATA / rel
        merged = upsert(load_csv(path), incoming[key], keys)
        write_csv(path, merged, columns)
        stored[key] = merged
        log(f"WROTE {rel} rows={len(merged)} incoming={len(incoming[key])}")

    skipped_path = DATA / "notes_skipped.csv"
    skipped_merged = upsert(load_csv(skipped_path), skipped, ["area", "date", "key", "field", "raw"])
    write_csv(skipped_path, skipped_merged, ["area", "date", "key", "field", "raw", "reason"])

    meta_path = DATA / "meta.json"
    existing = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}
    meta = build_meta(existing, stored)
    tmp = meta_path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(meta_path)
    log(f"NOTES {used} SKIPPED_ROWS {len(skipped)}")
    log("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
