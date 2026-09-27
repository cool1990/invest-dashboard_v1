#!/usr/bin/env python3
"""抓公开日历，和 calendar/manual.yaml、盈利笔记里的下次财报合并。

同一件事只留一条。财报按公司代码合并，日期不同就在备注里写明两个日期，卡片放在较早的那天；有手工条目时，备注和标题用手工的，来源链接都保留。同一天、同一分类、标题指同一件事（会议纪要、褐皮书，或标题互相包含）也合并，备注用手工的。

不编造日期。某个来源失败就记在 sources 里，页面上不出现它的条目。
发布时刻页面按北京时间显示。美东时刻用 America/New_York 换算，含夏令时。

来源：
- BEA Release Schedule：https://www.bea.gov/news/schedule
- Census 经济指标日历：https://www.census.gov/economic-indicators/calendar-listview.html
- FOMC：https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm
- 美联储讲话：https://www.federalreserve.gov/newsevents/YYYY-month.htm
- H.4.1：页面写明每周四、通常美东 16:30。https://www.federalreserve.gov/releases/h41/
- 财报：Nasdaq 公开日历，另加盈利笔记最新一天的「未来 7 天财报」
- CPI / PPI / 非农 / JOLTS：只有设置了 FRED_API_KEY 才向 FRED 要发布日
- 初请失业金、韩国出口档期、TSMC 月营收、代币解锁：这次没有稳定的公开接口，不生成日期
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import urllib.request
from datetime import date, datetime, timedelta
from html import unescape
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
ET = ZoneInfo("America/New_York")
BJ = ZoneInfo("Asia/Shanghai")
UA = "Mozilla/5.0 (compatible; macro-dashboard/1.0; +https://github.com/cool1990/macro-dashboard)"
BROWSER_UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
HORIZON_DAYS = 45
MEGA_CAP = 100_000_000_000
SEMI_AI = {"NVDA", "MU", "INTC", "TSM", "QCOM", "SNDK", "AVGO", "ASML", "AMD", "AMAT", "LRCX", "KLAC", "ARM", "SMCI"}
FRED_RELEASES = (
    (10, "CPI"),
    (46, "PPI"),
    (50, "Employment Situation"),
    (192, "JOLTS"),
)
MONTHS = {
    "january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6,
    "july": 7, "august": 8, "september": 9, "october": 10, "november": 11, "december": 12,
}
ZH = (
    ("Personal Income and Outlays", "个人收入与支出"),
    ("Gross Domestic Product", "GDP"),
    ("GDP", "GDP"),
    ("International Trade in Goods and Services", "国际贸易（商品和服务）"),
    ("Advance Monthly Sales for Retail and Food Services", "零售和餐饮销售"),
    ("Construction Spending", "建筑支出"),
    ("Monthly Wholesale Trade", "批发贸易"),
    ("Business Formation Statistics", "新企业统计"),
    ("Advance Report on Durable Goods", "耐用品订单"),
    ("New Residential Sales", "新屋销售"),
    ("New Residential Construction", "新屋开工"),
    ("Manufacturers' Shipments", "制造业出货、库存和订单"),
    ("Advance Economic Indicators", "经济指标预览"),
)


def log(msg: str) -> None:
    print(msg, flush=True)


def beijing_today() -> date:
    return datetime.now(BJ).date()


def fetch(url: str, timeout: int = 30, user_agent: str | None = None) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": user_agent or UA, "Accept": "text/html,application/json,*/*"})
    with urllib.request.urlopen(req, timeout=timeout) as res:
        return res.read()


def strip_tags(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", unescape(text)).strip()


def zh_title(title: str) -> str:
    for needle, label in ZH:
        if needle.lower() in title.lower():
            return label
    return title.strip()


def clock_to_bj(year: int, month: int, day: int, hour: int, minute: int) -> tuple[str, str]:
    moment = datetime(year, month, day, hour, minute, tzinfo=ET).astimezone(BJ)
    return moment.date().isoformat(), moment.strftime("%H:%M")


def parse_ampm(text: str) -> tuple[int, int] | None:
    match = re.search(r"(\d{1,2}):(\d{2})\s*(a\.?m\.?|p\.?m\.?)?", text, re.I)
    if not match:
        return None
    hour, minute = int(match.group(1)), int(match.group(2))
    mark = (match.group(3) or "").lower().replace(".", "")
    if mark == "pm" and hour < 12:
        hour += 12
    if mark == "am" and hour == 12:
        hour = 0
    return hour, minute


SPEECH_MAP = (
    ("Recent Developments in Bank Supervision", "银行监管近况"),
    ("AI and Emerging Tech", "人工智能与新兴技术"),
    ("Opening Remarks", "开幕致辞"),
    ("Federal Reserve Economic Data", "FRED 数据"),
    ("U.S. Economy and Monetary Policy", "美国经济与货币政策"),
    ("Modernizing Financial Regulation", "金融监管现代化"),
    ("Global Central Banking", "全球央行"),
    ("Economic Outlook", "经济展望"),
    ("Rural Economy", "农村经济"),
    ("Payments", "支付"),
)
EARNINGS_ZH = {
    "MU": "美光", "NKE": "耐克", "ACN": "埃森哲", "PEP": "百事",
    "NVDA": "英伟达", "TSM": "台积电", "AMD": "超威", "INTC": "英特尔",
    "QCOM": "高通", "AMAT": "应用材料", "AVGO": "博通", "ARM": "Arm",
    "LRCX": "拉姆研究", "KLAC": "科磊", "SMCI": "超微电脑", "SNDK": "闪迪",
    "ASML": "ASML",
}
QUARTER_ZH = {"1st": "一", "2nd": "二", "3rd": "三", "4th": "四"}
MONTH_LABELS = (
    "个人收入与支出", "国际贸易（商品和服务）", "零售和餐饮销售", "建筑支出",
    "耐用品订单", "新屋销售", "新屋开工", "制造业出货、库存和订单", "批发贸易",
    "经济指标预览",
)


def event(day: str, time_bj: str, category: str, title: str, url: str, source: str, note: str = "", previous: str = "", consensus: str = "", tags: list[str] | None = None) -> dict:
    return annotate({
        "date": day,
        "time_bj": time_bj,
        "category": category,
        "title": title,
        "url": url,
        "source": source,
        "note": note,
        "previous": previous,
        "consensus": consensus,
        "tags": tags or [],
    })


def append_original(note: str, original: str) -> str:
    original = re.sub(r"\s+", " ", original or "").strip(" 。")
    if not original or not re.search(r"[A-Za-z]{3,}", original):
        return note or ""
    marker = "原名：" + original
    note = (note or "").strip()
    if marker in note:
        return note
    return f"{note}。{marker}" if note else marker


def month_phrase(text: str) -> str:
    match = re.search(
        r"(January|February|March|April|May|June|July|August|September|October|November|December)\s+(20\d{2})",
        text or "",
        re.I,
    )
    if not match:
        return ""
    month = MONTHS.get(match.group(1).lower())
    return f"{match.group(2)}年{month}月" if month else ""


def macro_title(label: str, english: str) -> str:
    low = f"{label} {english}".lower()
    if "gdp" in low or "gross domestic product" in low:
        quarter = re.search(r"(1st|2nd|3rd|4th)\s+Quarter\s+(20\d{2})", english or "", re.I)
        estimate = ""
        if re.search(r"Third Estimate", english or "", re.I):
            estimate = "第三次估计"
        elif re.search(r"Second Estimate", english or "", re.I):
            estimate = "第二次估计"
        elif re.search(r"Advance Estimate", english or "", re.I):
            estimate = "首次估计"
        head = f"{quarter.group(2)}年{QUARTER_ZH[quarter.group(1).lower()]}季度" if quarter else ""
        return " ".join(part for part in (head, "GDP", estimate) if part) or "GDP"
    named = (
        ("advance economic indicators", "经济指标预览"),
        ("personal income", "个人收入与支出"),
        ("international trade", "国际贸易（商品和服务）"),
        ("retail and food", "零售和餐饮销售"),
        ("construction spending", "建筑支出"),
        ("construction put in place", "建筑支出"),
        ("wholesale trade", "批发贸易"),
        ("business formation", "新企业统计"),
        ("durable goods", "耐用品订单"),
        ("new residential sales", "新屋销售"),
        ("new residential construction", "新屋开工"),
        ("manufacturers' shipments", "制造业出货、库存和订单"),
        ("manufacturers’ shipments", "制造业出货、库存和订单"),
        ("services supplied through affiliates", "附属机构服务供应"),
        ("manufacturing and trade", "制造业与贸易库存和销售"),
        ("steel products", "钢材进口初值"),
        ("housing vacancies", "住房空置与自有住房率"),
    )
    chosen = next((text for needle, text in named if needle in low), "")
    if not chosen:
        chosen = label
    if chosen == "附属机构服务供应":
        year = re.search(r"(20\d{2})", english or "")
        if year:
            return f"{year.group(1)}年{chosen}"
    month = month_phrase(english)
    if month and chosen in MONTH_LABELS:
        return month + chosen
    return chosen


def priority_for(item: dict) -> str:
    title = item.get("title") or ""
    category = item.get("category") or ""
    tags = item.get("tags") or []
    note = item.get("note") or ""
    source = item.get("source") or ""
    if category == "财报":
        if "半导体" in tags or "盈利" in source:
            return "高"
        return "中"
    if any(key in title for key in ("H.4.1", "个人收入与支出", "CPI", "PPI", "非农", "JOLTS")) or "GDP" in title or "FOMC" in title:
        return "高"
    if "个税" in title or "再融资" in title:
        return "高"
    if "韩国" in title and "出口" in title:
        return "高"
    if "台积电" in title and "营收" in title:
        return "高"
    if title.startswith("美联储讲话") or title.startswith("美联储："):
        return "低"
    if any(key in title for key in ("西部半导体展", "欧洲半导体展", "SEMICON", "英伟达 GTC")):
        return "低"
    if any(key in title for key in ("批发贸易", "住房空置", "新企业统计", "钢材进口", "附属机构", "制造业与贸易库存")):
        return "低"
    if category == "加密" or "代币解锁" in title:
        if any(key in title for key in ("SEC", "ETF", "Deribit", "期权")):
            return "中"
        share = re.search(r"约占已释放供应\s*([0-9]+(?:\.[0-9]+)?)\s*%", note)
        if share and float(share.group(1)) >= 2:
            return "中"
        return "低"
    return "中"


def annotate(item: dict) -> dict:
    title = item.get("title") or ""
    note = item.get("note") or ""
    if title.startswith("美联储讲话"):
        pass
    elif title.startswith("美联储：") or title.startswith("美联储:"):
        english = re.split(r"[：:]", title, maxsplit=1)[1].strip()
        label = next((text for needle, text in SPEECH_MAP if needle.lower() in english.lower()), "")
        title = f"美联储讲话：{label}" if label else "美联储讲话"
        note = append_original(note, english)
    elif title.startswith("NVIDIA GTC"):
        paren = re.search(r"（[^）]+）", title)
        title = "英伟达 GTC 华盛顿" + (paren.group(0) if paren else "")
        note = append_original(note, "NVIDIA GTC Washington, D.C.")
    elif "SEMICON West" in title:
        paren = re.search(r"（[^）]+）", title)
        title = "西部半导体展" + (paren.group(0) if paren else "")
        note = append_original(note, "SEMICON West 2026")
    elif "SEMICON Europa" in title:
        paren = re.search(r"（[^）]+）", title)
        title = "欧洲半导体展" + (paren.group(0) if paren else "")
        note = append_original(note, "SEMICON Europa 2026")
    elif "Regulation Crypto Assets" in title:
        title = title.replace("《Regulation Crypto Assets》", "《加密资产规则》")
        note = append_original(note, "Regulation Crypto Assets")
    else:
        month_name = re.match(r"^([A-Za-z]+)\s+会议纪要$", title)
        if month_name and month_name.group(1).lower() in MONTHS:
            title = f"FOMC {MONTHS[month_name.group(1).lower()]}月会议纪要"
        elif item.get("category") == "财报":
            found = re.search(r"[（(]([A-Za-z][A-Za-z0-9.]*)[）)]\s*财报\s*$", title)
            if found:
                ticker = found.group(1).upper()
                label = EARNINGS_ZH.get(ticker, "")
                desired = f"{label}（{ticker}）财报" if label else ""
                if desired and title != desired:
                    prefix = re.split(r"[（(]", title, maxsplit=1)[0].strip()
                    title = desired
                    if prefix and prefix != label and re.search(r"[A-Za-z]", prefix):
                        note = append_original(note, prefix)
        elif "：" in title:
            left, right = title.split("：", 1)
            if re.search(r"[A-Za-z]{3,}", right):
                chosen = macro_title(left.strip(), right.strip())
                if not re.match(r"20\d{2}年", chosen):
                    month = month_phrase(note)
                    if month and chosen in MONTH_LABELS:
                        chosen = month + chosen
                title = chosen
                note = append_original(note, right.strip())
    item["title"] = title
    item["note"] = note
    item["priority"] = priority_for(item)
    return item


def in_window(day: str, start: date, end: date) -> bool:
    try:
        found = date.fromisoformat(day)
    except ValueError:
        return False
    return start <= found <= end


def parse_bea(html: str, start: date, end: date) -> list[dict]:
    year_match = re.search(r"Year\s+(20\d{2})", html)
    year = int(year_match.group(1)) if year_match else start.year
    rows = []
    for chunk in re.findall(r"<tr[\s\S]*?</tr>", html, flags=re.I):
        if "release-date" not in chunk or "release-title" not in chunk:
            continue
        date_text = strip_tags(re.search(r'class="release-date">(.*?)</div>', chunk, re.S).group(1) if re.search(r'class="release-date">', chunk) else "")
        time_text = strip_tags(re.search(r"<small[^>]*>(.*?)</small>", chunk, re.S).group(1) if re.search(r"<small", chunk) else "")
        title = strip_tags(re.search(r'class="release-title[^"]*"[^>]*>(.*?)</td>', chunk, re.S).group(1) if "release-title" in chunk else "")
        month_day = re.match(r"([A-Za-z]+)\s+(\d{1,2})", date_text)
        clock = parse_ampm(time_text)
        if not month_day or not clock or not title:
            continue
        month = MONTHS.get(month_day.group(1).lower())
        if not month:
            continue
        day_bj, time_bj = clock_to_bj(year, month, int(month_day.group(2)), clock[0], clock[1])
        if not in_window(day_bj, start, end):
            continue
        rows.append(event(
            day_bj, time_bj, "宏观", f"{zh_title(title)}：{title}",
            "https://www.bea.gov/news/schedule", "BEA Release Schedule",
            f"美东 {time_text}",
        ))
    return rows


def parse_census(html: str, start: date, end: date) -> list[dict]:
    rows = []
    for chunk in re.findall(r"<tr[\s\S]*?</tr>", html, flags=re.I):
        cells = re.findall(r"<td[^>]*>([\s\S]*?)</td>", chunk, flags=re.I)
        if len(cells) < 3:
            continue
        title = strip_tags(cells[0])
        date_text = strip_tags(cells[1])
        time_text = strip_tags(cells[2])
        found = re.match(r"([A-Za-z]+)\s+(\d{1,2}),\s*(20\d{2})", date_text)
        clock = parse_ampm(time_text)
        if not found or not clock or not title or title.lower() == "title":
            continue
        month = MONTHS.get(found.group(1).lower())
        if not month:
            continue
        day_bj, time_bj = clock_to_bj(int(found.group(3)), month, int(found.group(2)), clock[0], clock[1])
        if not in_window(day_bj, start, end):
            continue
        href = re.search(r'href="([^"]+)"', cells[0])
        url = "https://www.census.gov" + href.group(1) if href and href.group(1).startswith("/") else "https://www.census.gov/economic-indicators/calendar-listview.html"
        period = strip_tags(cells[3]) if len(cells) > 3 else ""
        rows.append(event(
            day_bj, time_bj, "宏观", f"{zh_title(title)}：{title}",
            url, "Census economic indicators calendar",
            " ".join(part for part in (f"美东 {time_text}", period) if part),
        ))
    return rows


def parse_fomc(html: str, start: date, end: date) -> list[dict]:
    rows = []
    for year_match in re.finditer(r'id="\d+">(20\d{2}) FOMC Meetings', html):
        year = int(year_match.group(1))
        rest = html[year_match.end():]
        nxt = re.search(r'id="\d+">20\d{2} FOMC Meetings', rest)
        section = rest[: nxt.start()] if nxt else rest
        parts = re.split(r'fomc-meeting__month', section)
        for part in parts[1:]:
            month_name = re.search(r"<strong>([A-Za-z]+)</strong>", part)
            days = re.search(r'fomc-meeting__date[^>]*>([^<]+)', part)
            if not month_name or not days:
                continue
            month = MONTHS.get(month_name.group(1).lower())
            if not month:
                continue
            sep = "*" in days.group(1)
            numbers = [int(item) for item in re.findall(r"\d+", days.group(1))]
            if not numbers:
                continue
            last = numbers[-1]
            try:
                meeting = date(year, month, last)
            except ValueError:
                continue
            if start <= meeting <= end:
                title = "FOMC 会议"
                if sep:
                    title += "（含经济预测摘要）"
                rows.append(event(
                    meeting.isoformat(), "", "大事", title,
                    "https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm",
                    "Federal Reserve FOMC calendars",
                    "会议日落在北京时间同一天；声明通常在美东下午，具体钟点以当天新闻稿为准",
                ))
            released = re.search(r"Released\s+([A-Za-z]+)\s+(\d{1,2}),\s*(20\d{2})", part)
            if released:
                rel_month = MONTHS.get(released.group(1).lower())
                if rel_month:
                    try:
                        rel = date(int(released.group(3)), rel_month, int(released.group(2)))
                    except ValueError:
                        rel = None
                    if rel and start <= rel <= end:
                        rows.append(event(
                            rel.isoformat(), "", "大事", f"{month_name.group(1)} 会议纪要",
                            "https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm",
                            "Federal Reserve FOMC calendars",
                            "页面写的是发布日，没有写钟点",
                        ))
    return rows


def parse_fed_speeches(html: str, year: int, month: int, page_url: str, start: date, end: date) -> list[dict]:
    rows = []
    blocks = re.findall(r'<div class="panel-body">([\s\S]*?)</div>\s*</div>\s*</div>', html)
    for block in blocks:
        clock_text = ""
        title = ""
        place = ""
        day_text = ""
        link = ""
        time_match = re.search(r"<p>(\d{1,2}:\d{2}\s*[ap]\.m\.)</p>", block, re.I)
        if time_match:
            clock_text = time_match.group(1)
        title_match = re.search(r"calendar__title[\s\S]*?<em>(.*?)</em>", block)
        if title_match:
            title = strip_tags(title_match.group(1))
        who = re.search(r"<p>((?:Speech|Discussion|Remarks)[^<]*)</p>", block)
        place_match = re.search(r"<p>(At [^<]+)</p>", block)
        if place_match:
            place = strip_tags(place_match.group(1))
        day_match = re.search(r'<div class="col-xs-3">\s*<p>(\d{1,2})</p>', block)
        if day_match:
            day_text = day_match.group(1)
        href = re.search(r'href="(https?://[^"]+)"', block)
        if href:
            link = href.group(1)
        if not (clock_text and title and day_text):
            continue
        clock = parse_ampm(clock_text)
        if not clock:
            continue
        try:
            day_bj, time_bj = clock_to_bj(year, month, int(day_text), clock[0], clock[1])
        except ValueError:
            continue
        if not in_window(day_bj, start, end):
            continue
        speaker = strip_tags(who.group(1)) if who else ""
        rows.append(event(
            day_bj, time_bj, "大事", f"美联储：{title}",
            link or page_url, "Federal Reserve calendar",
            " ".join(part for part in (speaker, place, f"美东 {clock_text}") if part),
        ))
    return rows


def h41_events(page_text: str, start: date, end: date) -> list[dict]:
    if not re.search(r"released each Thursday,\s*generally at 4:30 p\.m\.", page_text, re.I):
        return []
    rows = []
    day = start
    while day <= end:
        if day.weekday() == 3:
            day_bj, time_bj = clock_to_bj(day.year, day.month, day.day, 16, 30)
            if in_window(day_bj, start, end):
                rows.append(event(
                    day_bj, time_bj, "宏观", "美联储 H.4.1（资产负债表）",
                    "https://www.federalreserve.gov/releases/h41/",
                    "Federal Reserve H.4.1",
                    "页面写明每周四、通常美东 16:30；遇联邦假日顺延。这一条按周四生成，没有另核假日表",
                ))
        day += timedelta(days=1)
    return rows


def parse_nasdaq_rows(payload: dict, day: str) -> list[dict]:
    rows = []
    for item in (payload.get("data") or {}).get("rows") or []:
        symbol = (item.get("symbol") or "").upper()
        cap_text = item.get("marketCap") or ""
        digits = re.sub(r"[^0-9]", "", cap_text)
        cap = int(digits) if digits else 0
        if cap < MEGA_CAP and symbol not in SEMI_AI:
            continue
        when = item.get("time") or ""
        session = {"time-pre-market": "美东盘前", "time-after-hours": "美东盘后", "time-not-supplied": ""}.get(when, when)
        tags = ["半导体"] if symbol in SEMI_AI else []
        name = item.get("name") or symbol
        rows.append(event(
            day, "", "财报", f"{name}（{symbol}）财报",
            "https://www.nasdaq.com/market-activity/earnings",
            "Nasdaq earnings calendar",
            session,
            previous=item.get("lastYearEPS") or "",
            consensus=item.get("epsForecast") or "",
            tags=tags,
        ))
    return rows


def watchlist_events(events_csv: Path, start: date, end: date) -> list[dict]:
    if not events_csv.exists():
        return []
    with events_csv.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        return []
    latest = max(row.get("note_date", "") for row in rows)
    out = []
    for row in rows:
        if row.get("note_date") != latest:
            continue
        when = row.get("earnings_date", "")
        if not in_window(when, start, end):
            continue
        ticker = (row.get("ticker") or "").upper()
        tags = ["半导体"] if ticker in SEMI_AI else []
        out.append(event(
            when, "", "财报", f"{row.get('company') or ticker}（{ticker}）财报",
            "", "盈利跟踪笔记",
            f"笔记 {row.get('source', '')} 的未来 7 天财报",
            tags=tags,
        ))
    return out


def load_manual(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows = []
    current: dict[str, str] | None = None
    for raw in path.read_text(encoding="utf-8").splitlines():
        if not raw.strip() or raw.strip().startswith("#"):
            continue
        if raw.strip() == "[]":
            return []
        if raw.startswith("- "):
            if current:
                rows.append(current)
            current = {}
            body = raw[2:]
            if ":" in body:
                key, value = body.split(":", 1)
                current[key.strip()] = value.strip().strip('"').strip("'")
            continue
        if current is not None and ":" in raw:
            key, value = raw.strip().split(":", 1)
            current[key.strip()] = value.strip().strip('"').strip("'")
    if current:
        rows.append(current)
    out = []
    for item in rows:
        if not item.get("date") or not item.get("title") or not item.get("category"):
            continue
        tags = [part.strip() for part in item.get("tags", "").replace("，", ",").split(",") if part.strip()]
        out.append(event(
            item["date"], item.get("time_bj", ""), item["category"], item["title"],
            item.get("url", ""), "calendar/manual.yaml", item.get("note", ""),
            previous=item.get("previous", ""), consensus=item.get("consensus", ""),
            tags=tags,
        ))
    return out


COMPANY_TICKERS = (
    ("台积电", "TSM"),
    ("TSMC", "TSM"),
    ("ASML", "ASML"),
    ("联电", "UMC"),
    ("应用材料", "AMAT"),
    ("APPLIED MATERIALS", "AMAT"),
    ("美光", "MU"),
    ("MICRON", "MU"),
    ("英伟达", "NVDA"),
    ("NVIDIA", "NVDA"),
)
PHRASE_GROUPS = (
    ("会议纪要", "fomcminutes"),
    ("褐皮书", "beigebook"),
)


def ticker_of(title: str) -> str:
    match = re.search(r"[（(]([A-Za-z][A-Za-z0-9.]*)[）)]", title or "")
    if match:
        return match.group(1).upper()
    upper = (title or "").upper()
    for needle, ticker in COMPANY_TICKERS:
        if needle in title or needle in upper:
            return ticker
    return ""


def normalize_title(title: str) -> str:
    return re.sub(r"[\s\-—_:：,，.。'’\"“”()（）]+", "", title or "").lower()


def same_event(left: dict, right: dict) -> bool:
    if left["category"] == "财报" and right["category"] == "财报":
        ticker = ticker_of(left["title"])
        if ticker and ticker == ticker_of(right["title"]):
            return True
    if left["date"] != right["date"] or left["category"] != right["category"]:
        return False
    a = normalize_title(left["title"])
    b = normalize_title(right["title"])
    if a == b:
        return True
    if len(a) >= 8 and len(b) >= 8 and (a in b or b in a):
        return True
    for group in PHRASE_GROUPS:
        keys = [normalize_title(key) for key in group]
        if any(key in a for key in keys) and any(key in b for key in keys):
            return True
    return False


def _filled(primary: dict, rows: list[dict], key: str) -> str:
    if primary.get(key):
        return primary[key]
    for row in rows:
        if row.get(key):
            return row[key]
    return ""


def merge_events(group: list[dict]) -> dict:
    manuals = [row for row in group if row.get("source") == "calendar/manual.yaml"]
    ordered = manuals + [row for row in sorted(group, key=lambda item: item["date"]) if row not in manuals]
    primary = ordered[0]
    day = primary["date"] if manuals else min(row["date"] for row in group)
    time_bj = primary.get("time_bj") or ""
    if not time_bj:
        for row in ordered:
            if row["date"] == day and row.get("time_bj"):
                time_bj = row["time_bj"]
                break
    note = (primary.get("note") or "").strip()
    dates = {row["date"] for row in group}
    if len(dates) > 1:
        parts = [f"{row['source']}写的是 {row['date']}" for row in sorted(group, key=lambda item: (item["date"], item["source"]))]
        sentence = "日期不一样：" + "，".join(parts)
        note = f"{note}。{sentence}" if note else sentence
    links = []
    seen = set()
    for row in ordered:
        link = {"source": row.get("source") or "", "url": row.get("url") or ""}
        key = (link["source"], link["url"])
        if key in seen or key == ("", ""):
            continue
        seen.add(key)
        links.append(link)
    tags = []
    for row in ordered:
        for tag in row.get("tags") or []:
            if tag not in tags:
                tags.append(tag)
    merged = event(
        day, time_bj, primary["category"], primary["title"],
        _filled(primary, ordered, "url"),
        "；".join(link["source"] for link in links),
        note,
        previous=_filled(primary, ordered, "previous"),
        consensus=_filled(primary, ordered, "consensus"),
        tags=tags,
    )
    merged["links"] = links
    return merged


def dedupe(rows: list[dict]) -> list[dict]:
    groups: list[list[dict]] = []
    for row in rows:
        placed = False
        for group in groups:
            if any(same_event(row, other) for other in group):
                group.append(row)
                placed = True
                break
        if not placed:
            groups.append([row])
    merged = [merge_events(group) for group in groups]
    return sorted(merged, key=lambda item: (item["date"], item["time_bj"], item["category"], item["title"]))


def fred_events(start: date, end: date, key: str) -> tuple[list[dict], str]:
    if not key:
        return [], "未设置 FRED_API_KEY，CPI、PPI、非农、JOLTS 的发布日没有抓"
    rows = []
    notes = []
    for release_id, fallback in FRED_RELEASES:
        url = (
            "https://api.stlouisfed.org/fred/release/dates"
            f"?release_id={release_id}&api_key={key}&file_type=json"
            f"&realtime_start={start.isoformat()}&realtime_end={end.isoformat()}&include_release_dates_with_no_data=true"
        )
        try:
            payload = json.loads(fetch(url).decode("utf-8"))
        except Exception as exc:
            notes.append(f"{fallback} 失败：{exc}")
            continue
        name = ((payload.get("release") or {}) or {}).get("name") if isinstance(payload.get("release"), dict) else ""
        # dates endpoint nests release_dates
        dates = payload.get("release_dates") or []
        label = zh_title(name or fallback)
        for item in dates:
            day = item.get("date") if isinstance(item, dict) else ""
            if day and in_window(day, start, end):
                rows.append(event(
                    day, "", "宏观", f"{label} 发布",
                    f"https://fred.stlouisfed.org/release?rid={release_id}",
                    "FRED release dates",
                    name or fallback,
                ))
        notes.append(f"{name or fallback} {len(dates)} 天")
    return rows, "；".join(notes)


def collect(root: Path, today: date | None = None) -> dict:
    today = today or beijing_today()
    end = today + timedelta(days=HORIZON_DAYS)
    sources = []
    rows: list[dict] = []

    def take(name: str, url: str, parser):
        try:
            html = fetch(url).decode("utf-8", "replace")
            found = parser(html)
            rows.extend(found)
            sources.append({"name": name, "url": url, "status": "ok", "detail": f"{len(found)} 条"})
            return html
        except Exception as exc:
            sources.append({"name": name, "url": url, "status": "failed", "detail": str(exc)})
            return ""

    take("BEA", "https://www.bea.gov/news/schedule", lambda html: parse_bea(html, today, end))
    take("Census", "https://www.census.gov/economic-indicators/calendar-listview.html", lambda html: parse_census(html, today, end))
    take("FOMC", "https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm", lambda html: parse_fomc(html, today, end))
    h41 = take("H.4.1", "https://www.federalreserve.gov/releases/h41/", lambda html: h41_events(html, today, end))
    if not h41:
        pass
    speech_count = 0
    speech_errors = []
    cursor = today.replace(day=1)
    for _ in range(3):
        slug = cursor.strftime("%Y-%B").lower()
        url = f"https://www.federalreserve.gov/newsevents/{slug}.htm"
        try:
            html = fetch(url).decode("utf-8", "replace")
            found = parse_fed_speeches(html, cursor.year, cursor.month, url, today, end)
            rows.extend(found)
            speech_count += len(found)
        except Exception as exc:
            speech_errors.append(f"{slug}: {exc}")
        if cursor.month == 12:
            cursor = date(cursor.year + 1, 1, 1)
        else:
            cursor = date(cursor.year, cursor.month + 1, 1)
    sources.append({
        "name": "美联储讲话",
        "url": "https://www.federalreserve.gov/newsevents/calendar.htm",
        "status": "ok" if not speech_errors else "partial",
        "detail": f"{speech_count} 条" + ("" if not speech_errors else "；" + "；".join(speech_errors)),
    })

    nasdaq_count = 0
    nasdaq_errors = []
    for offset in range(0, 16):
        day = today + timedelta(days=offset)
        url = f"https://api.nasdaq.com/api/calendar/earnings?date={day.isoformat()}"
        payload = None
        last_error = ""
        log(f"NASDAQ {day.isoformat()}")
        try:
            payload = json.loads(fetch(url, timeout=20, user_agent=BROWSER_UA).decode("utf-8"))
        except Exception as exc:
            last_error = str(exc)
        if payload is None:
            nasdaq_errors.append(f"{day.isoformat()} {last_error}")
            continue
        found = parse_nasdaq_rows(payload, day.isoformat())
        rows.extend(found)
        nasdaq_count += len(found)
    sources.append({
        "name": "Nasdaq 财报",
        "url": "https://api.nasdaq.com/api/calendar/earnings",
        "status": "failed" if nasdaq_errors and nasdaq_count == 0 else ("partial" if nasdaq_errors else "ok"),
        "detail": f"{nasdaq_count} 条" + (("；未抓到 " + "；".join(nasdaq_errors)) if nasdaq_errors else "。接口每次大约返回 20 家，保留市值不低于 1000 亿美元的，以及半导体/AI 代码"),
    })

    notes = watchlist_events(root / "data" / "earnings" / "events.csv", today, end)
    rows.extend(notes)
    sources.append({"name": "盈利笔记财报日", "url": "", "status": "ok", "detail": f"{len(notes)} 条"})

    manual = load_manual(root / "calendar" / "manual.yaml")
    rows.extend(manual)
    sources.append({"name": "手工日历", "url": "calendar/manual.yaml", "status": "ok", "detail": f"{len(manual)} 条"})

    fred_rows, fred_detail = fred_events(today, end, os.environ.get("FRED_API_KEY", ""))
    rows.extend(fred_rows)
    sources.append({
        "name": "FRED 发布日",
        "url": "https://fred.stlouisfed.org/docs/api/fred/",
        "status": "skipped" if "未设置" in fred_detail else "ok",
        "detail": fred_detail,
    })
    sources.append({
        "name": "初请失业金",
        "url": "https://oui.doleta.gov/unemploy/claims.asp",
        "status": "failed",
        "detail": "页面没有写每周几、几点发布，所以没有按周四生成",
    })
    has_crypto = any(item["category"] == "加密" for item in manual)
    has_semi_manual = any(item["category"] == "半导体" and ("韩国" in item["title"] or "营收" in item["title"]) for item in manual)
    sources.append({
        "name": "加密",
        "url": "https://api.llama.fi/emissions",
        "status": "failed",
        "detail": "DefiLlama emissions 返回 402。核对过的解锁和期限在手工日历" if has_crypto else "DefiLlama emissions 返回 402，没有改用别的未核对清单",
    })
    sources.append({
        "name": "韩国出口与 TSMC 月营收",
        "url": "",
        "status": "failed",
        "detail": "自动页面没有解析出发布日。核对过的日期在手工日历" if has_semi_manual else "这次没有抓到写明发布日的官方页面，manual.yaml 里也没有补",
    })
    return {
        "generated_at": datetime.now(BJ).isoformat(timespec="seconds"),
        "today_bj": today.isoformat(),
        "horizon_end": end.isoformat(),
        "events": dedupe(rows),
        "sources": sources,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="抓公开日历")
    parser.add_argument("--root", default=str(ROOT))
    parser.add_argument("--annotate", action="store_true", help="只给现有 events.json 补中文标题和优先级，不重新抓取")
    args = parser.parse_args()
    root = Path(args.root)
    if args.annotate:
        path = root / "data" / "calendar" / "events.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["events"] = [annotate(item) for item in payload.get("events", [])]
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        log(f"ANNOTATED data/calendar/events.json events={len(payload['events'])}")
        return 0
    payload = collect(root)
    dest = root / "data" / "calendar"
    dest.mkdir(parents=True, exist_ok=True)
    (dest / "events.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    log(f"WROTE data/calendar/events.json events={len(payload['events'])}")
    for source in payload["sources"]:
        log(f"SOURCE {source['status']} {source['name']} {source['detail']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
