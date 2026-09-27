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
from datetime import datetime, timedelta, timezone
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
    ("10年期通胀预期", "t10yie", "10年期通胀预期", "百分比"),
    ("10Y-2Y", "t10y2y", "10年减2年美债利差", "百分点"),
    ("10年期实际利率", "tips_10y", "10年期实际利率", "百分比"),
    ("10年期美债", "us_10y", "10年期美债", "百分比"),
    ("高收益率利差", "hy_oas", "高收益率利差", "百分点"),
    ("高收益债", "hy_oas", "高收益债信用利差", "百分点"),
    ("明年底EFFR", "effr_ny", "明年底 EFFR", "百分比"),
    ("下月EFFR", "effr_next", "下月 EFFR", "百分比"),
    ("年底EFFR", "effr_year", "年底 EFFR", "百分比"),
    ("2年期美债", "us_2y", "2年期美债", "百分比"),
    ("US_10y", "us_10y", "美国10年期国债收益率", "百分比"),
    ("US_2y", "us_2y", "美国2年期国债收益率", "百分比"),
    ("VIX", "vix", "VIX", "点"),
    ("博时标普500", "etf_spx", "博时标普500ETF溢价率", "百分比"),
    ("广发纳指", "etf_ndx", "广发纳指ETF溢价率", "百分比"),
    ("标普500参与度>200", "spx_breadth_200", "标普500参与度>200日", "百分比"),
    ("标普500参与度>50", "spx_breadth_50", "标普500参与度>50日", "百分比"),
    ("标普500参与度>20", "spx_breadth_20", "标普500参与度>20日", "百分比"),
    ("标普参与度>200", "spx_breadth_200", "标普成分高于200日均线的比例", "百分比"),
    ("标普参与度>50", "spx_breadth_50", "标普成分高于50日均线的比例", "百分比"),
    ("标普参与度>20", "spx_breadth_20", "标普成分高于20日均线的比例", "百分比"),
    ("纳斯达克100参与度>200", "ndx_breadth_200", "纳斯达克100参与度>200日", "百分比"),
    ("纳斯达克100参与度>50", "ndx_breadth_50", "纳斯达克100参与度>50日", "百分比"),
    ("纳斯达克100参与度>20", "ndx_breadth_20", "纳斯达克100参与度>20日", "百分比"),
    ("纳指100参与度>200", "ndx_breadth_200", "纳指100高于200日均线的比例", "百分比"),
    ("纳指100参与度>50", "ndx_breadth_50", "纳指100高于50日均线的比例", "百分比"),
    ("纳指100参与度>20", "ndx_breadth_20", "纳指100高于20日均线的比例", "百分比"),
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
    if "美港股公告" in name:
        return "filings"
    if "美港股新闻稿" in name:
        return "press"
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


def split_sections(body: str) -> list[tuple[str, str]]:
    sections: list[tuple[str, str]] = []
    heading = ""
    buf: list[str] = []
    for line in body.splitlines():
        if line.startswith("## "):
            sections.append((heading, "\n".join(buf)))
            heading = line[3:].strip()
            buf = []
        else:
            buf.append(line)
    sections.append((heading, "\n".join(buf)))
    return sections


def section_bucket(heading: str) -> str:
    if "情绪" in heading and "综合" not in heading and "小结" not in heading:
        return "情绪"
    if "利率" in heading:
        return "利率"
    if "其他" in heading or "价格" in heading:
        return "其他"
    return ""


def hike_count(remark: str) -> str:
    match = re.search(r"隐含加息\s*([0-9]+(?:\.[0-9]+)?)\s*次", remark or "")
    return match.group(1) if match else ""


def summary_text(body: str) -> str:
    for heading, chunk in split_sections(body):
        if heading == "小结":
            lines = [clean_cell(line.lstrip("-").strip()) for line in chunk.splitlines()]
            lines = [line for line in lines if line]
            return " ".join(lines)
    return ""


def earnings_brief(body: str) -> str:
    for heading, chunk in split_sections(body):
        if heading != "简要总结":
            continue
        lines = []
        for line in chunk.splitlines():
            text = clean_cell(line.strip())
            if not text or text.startswith("|"):
                continue
            lines.append(text)
        return "\n".join(lines)
    return ""


def parse_sentiment(path: Path, meta: dict[str, str], body: str, skipped: list[dict[str, str]]) -> tuple[list[dict[str, str]], dict[str, str] | None, dict[str, str] | None]:
    day = note_date(meta, path)
    rows: list[dict[str, str]] = []
    if not day:
        skipped.append({"area": "sentiment", "date": "", "key": path.name, "field": "date", "raw": "", "reason": "没有 data_date，文件名里也没有日期"})
        return rows, None, None
    for heading, chunk in split_sections(body):
        bucket = section_bucket(heading)
        for table in parse_tables(chunk):
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
                series_id, _series_name, unit = series_info(name)
                label_raw = item.get("情绪") or item.get("机会or风险or中性") or ""
                obs = item.get("日期", "")
                if not re.fullmatch(r"20\d{2}-\d{2}-\d{2}", obs):
                    obs = ""
                remark = item.get("备注", "")
                rows.append({
                    "date": day,
                    "series_id": series_id,
                    "name": name or series_id,
                    "value": value,
                    "unit": unit,
                    "change_text": item.get("涨跌幅", ""),
                    "label": sentiment_label(label_raw),
                    "obs_date": obs,
                    "carried": carried_flag(remark),
                    "section": bucket,
                    "remark": remark,
                    "hike_count": hike_count(remark),
                    "source": path.name,
                })
    summary = None
    text = summary_text(body)
    if text:
        summary = {"date": day, "text": text, "source": path.name}
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
    return rows, composite, summary


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


def parse_earnings(path: Path, meta: dict[str, str], body: str, skipped: list[dict[str, str]]) -> tuple[list[dict[str, str]], list[dict[str, str]], dict[str, str] | None]:
    day = note_date(meta, path)
    quotes: list[dict[str, str]] = []
    events: list[dict[str, str]] = []
    if not day:
        skipped.append({"area": "earnings", "date": "", "key": path.name, "field": "date", "raw": "", "reason": "没有日期"})
        return quotes, events, None
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
            if ticker in {"PDD", "TME"} and (row.get("market") or "US").upper() in {"", "US"}:
                row["eps_unit"] = "USD"
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
    brief = earnings_brief(body)
    summary = {"date": day, "text": brief, "source": path.name} if brief else None
    return quotes, events, summary


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


BJ = timezone(timedelta(hours=8))
COMPANY_RE = re.compile(r"^##\s+(.+?)\s*[（(]\s*([^）)]+?)\s*[）)]\s*$")
FIELD_RE = re.compile(r"^(公司|标题|核心内容|链接|时间|摘要)\s*[:：]\s*(.*)$")


def to_beijing(raw: str) -> str:
    text = (raw or "").strip()
    if not text:
        return ""
    if re.match(r"\d{4}-\d{2}-\d{2}T", text):
        stamp = text.replace("Z", "+00:00")
        try:
            moment = datetime.fromisoformat(stamp)
        except ValueError:
            return text
        if moment.tzinfo is None:
            moment = moment.replace(tzinfo=timezone.utc)
        return moment.astimezone(BJ).strftime("%Y-%m-%d %H:%M")
    match = re.match(r"(\d{2})/(\d{2})/(\d{4})\s+(\d{2}:\d{2})", text)
    if match:
        day, month, year, clock = match.groups()
        return f"{year}-{month}-{day} {clock}"
    return text


def extract_url(text: str) -> str:
    match = re.search(r"\((https?://[^)\s]+)\)", text or "")
    if match:
        return match.group(1)
    match = re.search(r"https?://\S+", text or "")
    if not match:
        return ""
    return match.group(0).rstrip(").,，。")


def _consume_fields(lines: list[str]) -> dict[str, str]:
    fields: dict[str, str] = {}
    current = ""
    buf: list[str] = []

    def flush() -> None:
        if current:
            fields[current] = clean_cell(" ".join(part.strip() for part in buf if part.strip()))

    for line in lines:
        match = FIELD_RE.match(line.strip())
        if match:
            flush()
            current = match.group(1)
            buf = [match.group(2)]
            continue
        if current and line.strip():
            buf.append(line.strip().lstrip("-").strip())
    flush()
    return fields


def parse_filings(path: Path, meta: dict[str, str], body: str) -> tuple[list[dict[str, str]], list[dict[str, str]], dict[str, str]]:
    day = note_date(meta, path)
    items: list[dict[str, str]] = []
    insiders: list[dict[str, str]] = []
    company = ""
    ticker = ""
    block: list[str] = []
    insider_buf: list[str] = []
    in_insider = False

    def flush_block() -> None:
        if not block or not company:
            return
        heading = block[0]
        match = re.match(r"^###\s+(.+?)\s+[—–-]\s+(.+)$", heading.strip())
        filed_raw = match.group(1).strip() if match else ""
        accession = match.group(2).strip() if match else ""
        fields = _consume_fields(block[1:])
        title = fields.get("标题", "")
        summary = fields.get("核心内容", "")
        if not title and not summary:
            return
        items.append({
            "date": day,
            "company": fields.get("公司", "") or company,
            "ticker": ticker,
            "filed_raw": filed_raw,
            "filed_bj": to_beijing(filed_raw),
            "accession": accession,
            "title": title,
            "summary": summary,
            "url": extract_url(fields.get("链接", "")),
            "source": path.name,
        })

    for line in body.splitlines():
        if line.startswith("## "):
            if in_insider:
                insider_buf.append(line)
                continue
            flush_block()
            block = []
            heading = line[3:].strip()
            if "内部人" in heading:
                in_insider = True
                insider_buf = []
                company = ""
                ticker = ""
                continue
            found = COMPANY_RE.match(line)
            if found:
                company = found.group(1).strip()
                ticker = found.group(2).strip().upper()
            else:
                company = ""
                ticker = ""
            continue
        if in_insider:
            insider_buf.append(line)
            continue
        if line.startswith("### "):
            flush_block()
            block = [line]
            continue
        if block and line.strip() != "---":
            block.append(line)
    flush_block()
    insider_text = clean_cell(" ".join(insider_buf))
    if insider_text and "今日无" not in insider_text:
        insiders.append({"date": day, "text": insider_text, "source": path.name})
    day_row = {
        "date": day,
        "kind": "announcement",
        "item_count": str(len(items)),
        "status": meta.get("fetch_status", ""),
        "insider_count": meta.get("insider_count", "0"),
        "source": path.name,
    }
    return items, insiders, day_row


def parse_press(path: Path, meta: dict[str, str], body: str) -> tuple[list[dict[str, str]], dict[str, str]]:
    day = note_date(meta, path)
    items: list[dict[str, str]] = []
    company = ""
    ticker = ""
    current: dict[str, str] | None = None

    def flush() -> None:
        nonlocal current
        if current and (current.get("title") or current.get("summary")):
            items.append(current)
        current = None

    for line in body.splitlines():
        if line.startswith("## "):
            flush()
            found = COMPANY_RE.match(line)
            if found:
                company = found.group(1).strip()
                ticker = found.group(2).strip().upper()
            else:
                company = ""
                ticker = ""
            continue
        bullet = re.match(r"^-\s+\[(.+?)[（(]([^）)]+)[）)]\]\s*(.+)$", line.strip())
        if bullet and not line.startswith("  "):
            flush()
            current = {
                "date": day,
                "company": company or bullet.group(1).strip(),
                "ticker": (ticker or bullet.group(2)).strip().upper(),
                "title": bullet.group(3).strip(),
                "time_bj": "",
                "url": "",
                "summary": "",
                "source": path.name,
            }
            continue
        if current is None:
            continue
        stripped = line.strip().lstrip("-").strip()
        match = FIELD_RE.match(stripped)
        if not match:
            continue
        key, value = match.group(1), match.group(2).strip()
        if key == "时间":
            current["time_bj"] = value
        elif key == "链接":
            current["url"] = extract_url(value) or value
        elif key == "摘要":
            current["summary"] = value
    flush()
    day_row = {
        "date": day,
        "kind": "press",
        "item_count": str(len(items) if items else (0 if "今日无" in body else len(items))),
        "status": meta.get("fetch_status", ""),
        "insider_count": "",
        "source": path.name,
    }
    if "今日无" in body and not items:
        day_row["item_count"] = "0"
    return items, day_row


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
            "summary": "sentiment/summary.csv",
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
            "summary": "earnings/summary.csv",
        },
        "note": "涨跌幅和 30 日修正都是百分数，不带百分号。triggered=1 表示笔记里的估值触发。",
    }
    filings = bundles.get("filings", [])
    press = bundles.get("press", [])
    filing_days = bundles.get("filing_days", [])
    existing["filings"] = {
        "name": "公告和新闻稿",
        "source": "inbox/notes/每日/美港股公告 与 美港股新闻稿",
        "history_end": latest_date(filing_days, "date"),
        "announcements": len(filings),
        "press": len(press),
        "files": {
            "announcements": "filings/announcements.csv",
            "press": "filings/press.csv",
            "insiders": "filings/insiders.csv",
            "days": "filings/days.csv",
        },
        "note": "日期用笔记 data_date 或文件名，不用正文标题。SEC 的 UTC 时间已换成北京时间，港交所 HKT 与北京时间相同。",
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
        "summary": [],
        "filings": [],
        "insiders": [],
        "press": [],
        "filing_days": [],
        "earnings": [],
        "events": [],
        "earnings_summary": [],
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
            rows, composite, summary = parse_sentiment(path, meta, body, skipped)
            incoming["sentiment"].extend(rows)
            if composite:
                incoming["composite"].append(composite)
            if summary:
                incoming["summary"].append(summary)
        elif kind == "filings":
            rows, insiders, day_row = parse_filings(path, meta, body)
            incoming["filings"].extend(rows)
            incoming["insiders"].extend(insiders)
            if day_row.get("date"):
                incoming["filing_days"].append(day_row)
        elif kind == "press":
            rows, day_row = parse_press(path, meta, body)
            incoming["press"].extend(rows)
            if day_row.get("date"):
                incoming["filing_days"].append(day_row)
        elif kind == "earnings":
            quotes, events, earnings_summary = parse_earnings(path, meta, body, skipped)
            incoming["earnings"].extend(quotes)
            incoming["events"].extend(events)
            if earnings_summary:
                incoming["earnings_summary"].append(earnings_summary)
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
        "sentiment": ("sentiment/series.csv", ["date", "series_id"], ["date", "series_id", "name", "value", "unit", "change_text", "label", "obs_date", "carried", "section", "remark", "hike_count", "source"]),
        "composite": ("sentiment/composite.csv", ["date"], ["date", "label", "score", "cnn_official", "text", "source"]),
        "summary": ("sentiment/summary.csv", ["date"], ["date", "text", "source"]),
        "filings": ("filings/announcements.csv", ["date", "ticker", "accession", "title"], ["date", "company", "ticker", "filed_raw", "filed_bj", "accession", "title", "summary", "url", "source"]),
        "insiders": ("filings/insiders.csv", ["date", "text"], ["date", "text", "source"]),
        "press": ("filings/press.csv", ["date", "ticker", "title"], ["date", "company", "ticker", "title", "time_bj", "url", "summary", "source"]),
        "filing_days": ("filings/days.csv", ["date", "kind"], ["date", "kind", "item_count", "status", "insider_count", "source"]),
        "earnings": ("earnings/daily.csv", ["date", "ticker"], ["date", "ticker", "company", "market", "close", "day_pct", "rsi", "eps_sum", "forward_pe", "target_pe", "triggered", "next_fy_eps", "revision_30d", "up30", "down30", "revision_signal", "status", "flags", "is_trading_day", "eps_unit", "source"]),
        "events": ("earnings/events.csv", ["note_date", "ticker", "earnings_date"], ["note_date", "ticker", "company", "earnings_date", "source"]),
        "earnings_summary": ("earnings/summary.csv", ["date"], ["date", "text", "source"]),
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
