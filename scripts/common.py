"""变动都用序列自己算。

收益率、利差、EFFR 路径用基点（差值乘 100）。
参与度、ETF 溢价、AAII 用百分点（直接相减）。
CNN、RSI、VIX 用点。价格用百分比。
观测日没变，或笔记标明沿用，就不算新的变动。
"""

from __future__ import annotations

from datetime import date, timedelta


SENTIMENT_KIND = {
    "us_10y": "bp",
    "us_2y": "bp",
    "tips_10y": "bp",
    "t10yie": "bp",
    "t10y2y": "bp",
    "hy_oas": "bp",
    "effr_next": "bp",
    "effr_year": "bp",
    "effr_ny": "bp",
    "etf_spx": "pp",
    "etf_ndx": "pp",
    "aaii": "pp",
    "spx_breadth_20": "pp",
    "spx_breadth_50": "pp",
    "spx_breadth_200": "pp",
    "ndx_breadth_20": "pp",
    "ndx_breadth_50": "pp",
    "ndx_breadth_200": "pp",
    "cnn_fg": "pt",
    "spx_rsi": "pt",
    "nasdaq_rsi": "pt",
    "vix": "pt",
    "wti": "pct",
    "gold": "pct",
    "copper": "pct",
    "usdcny": "pct",
    "btc": "pct",
}


def fnum(text) -> float | None:
    if text is None or text == "":
        return None
    try:
        return float(text)
    except (TypeError, ValueError):
        return None


def parse_day(text: str) -> date | None:
    if not text:
        return None
    try:
        return date.fromisoformat(str(text)[:10])
    except ValueError:
        return None


def diff(prev: float | None, curr: float | None) -> float | None:
    if prev is None or curr is None:
        return None
    return curr - prev


def pct_change(prev: float | None, curr: float | None) -> float | None:
    if prev is None or curr is None or prev == 0:
        return None
    return (curr - prev) / abs(prev) * 100


def bp_change(prev: float | None, curr: float | None) -> float | None:
    change = diff(prev, curr)
    # 百分点相减再乘 100，四舍五入到 0.01bp，避免 0.05 变成 4.999999。
    return None if change is None else round(change * 100, 2)


def kind_change(kind: str, prev: float | None, curr: float | None) -> float | None:
    if kind == "bp":
        return bp_change(prev, curr)
    if kind == "pct":
        return pct_change(prev, curr)
    return diff(prev, curr)


def format_change(kind: str, value: float | None) -> str:
    if value is None:
        return ""
    if kind == "bp":
        number = f"{value:+.0f}" if abs(value - round(value)) < 0.05 else f"{value:+.1f}"
        return number + "bp"
    if kind == "pp":
        return f"{value:+.2f} 个百分点"
    if kind == "pt":
        return f"{value:+.1f} 点"
    return f"{value:+.1f}%"


def notable(kind: str, series_id: str, value: float) -> bool:
    if kind == "bp":
        return abs(value) >= 5
    if kind == "pp":
        if "breadth" in series_id or series_id == "aaii":
            return abs(value) >= 3
        return abs(value) >= 0.5
    if kind == "pt":
        return abs(value) >= 1 if series_id == "vix" else abs(value) >= 3
    return abs(value) >= 1.5


def observation_of(row: dict, obs_key: str = "obs_date", date_key: str = "date") -> str:
    return (row.get(obs_key) or row.get(date_key) or "")[:10]


def fresh_pair(rows: list[dict], obs_key: str = "obs_date", date_key: str = "date") -> tuple[dict | None, dict | None]:
    """最新一条如果标明沿用，就没有新变动。否则和上一条不同观测日比较。"""
    if not rows:
        return None, None
    curr = rows[-1]
    if str(curr.get("carried") or "") == "1":
        return None, curr
    curr_obs = observation_of(curr, obs_key, date_key)
    prev = None
    for row in reversed(rows[:-1]):
        obs = observation_of(row, obs_key, date_key)
        if obs and obs != curr_obs:
            prev = row
            break
    return prev, curr


def series_points(rows: list[dict], date_key: str = "date", value_key: str = "value") -> list[tuple[date, float]]:
    found: dict[date, float] = {}
    for row in rows:
        day = parse_day(row.get(date_key, ""))
        value = fnum(row.get(value_key, ""))
        if day is not None and value is not None:
            found[day] = value
    return sorted(found.items())


def day_move(points: list[tuple[date, float]]) -> tuple[date, float, date, float, float] | None:
    if len(points) < 2:
        return None
    prev_day, prev_val = points[-2]
    last_day, last_val = points[-1]
    change = pct_change(prev_val, last_val)
    if change is None:
        return None
    return prev_day, prev_val, last_day, last_val, change


def lookback(points: list[tuple[date, float]], days: int) -> tuple[date, float, date, float, float] | None:
    if len(points) < 2:
        return None
    last_day, last_val = points[-1]
    target = last_day - timedelta(days=days)
    prev = None
    for day, value in points:
        if day <= target:
            prev = (day, value)
        else:
            break
    if prev is None or prev[0] == last_day:
        return None
    change = pct_change(prev[1], last_val)
    if change is None:
        return None
    return prev[0], prev[1], last_day, last_val, change


def price_carried(prev: dict, curr: dict, value_key: str = "price") -> bool:
    """沿用：涨跌列和价格都与前一天逐字相同，或周末且价格没变。

    只有价格相同、涨跌列不同的工作日，仍是新观测，一日变动记 0。
    周末价格变了，仍算新观测。
    """
    price_same = str(prev.get(value_key, "")) == str(curr.get(value_key, ""))
    keys = sorted(key for key in set(prev) | set(curr) if key.startswith("chg_"))
    change_same = bool(keys) and all(str(prev.get(key, "")) == str(curr.get(key, "")) for key in keys)
    if price_same and change_same:
        return True
    day = parse_day(curr.get("date") or "")
    return bool(price_same and day is not None and day.weekday() >= 5)


def repeated_runs(points: list[tuple[date, float]]) -> list[tuple[date, date, float]]:
    """相邻日期数值完全一样。价格相同本身不是沿用，沿用看 price_carried。"""
    runs = []
    index = 1
    while index < len(points):
        if points[index][1] == points[index - 1][1] and (points[index][0] - points[index - 1][0]).days == 1:
            start = index - 1
            value = points[index][1]
            while index < len(points) and points[index][1] == value and (points[index][0] - points[index - 1][0]).days == 1:
                index += 1
            runs.append((points[start][0], points[index - 1][0], value))
        else:
            index += 1
    return runs
