#!/usr/bin/env python3
"""从 FRED 公开 CSV 拉取美国流动性序列，并写入 data/。

只用 Python 标准库。任一序列刷新失败就退出，并且不改写 data/，
避免静默留下过期数据。

不要给请求加自定义 User-Agent。2026-09-27 实测：自定义 UA 在
HTTP/2 上会立刻 INTERNAL_ERROR，在 HTTP/1.1 上会挂起直到超时；
curl / Python 的默认请求头可以正常下载。
"""

from __future__ import annotations

import csv
import io
import json
import shutil
import sys
import tempfile
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
START = date(2022, 1, 1)
TIMEOUT_SEC = 30
RETRIES = 3
Q_BN = Decimal("0.001")
Q_PCT = Decimal("0.01")
Q_BP = Decimal("0.1")

SERIES: list[dict] = [
    {
        "id": "WALCL",
        "name": "美联储总资产",
        "unit": "百万美元",
        "display_unit": "十亿美元",
        "to_bn": Decimal("0.001"),
        "frequency": "每周三",
    },
    {
        "id": "WDTGAL",
        "name": "财政部在美联储账户（TGA，周三水平）",
        "unit": "百万美元",
        "display_unit": "十亿美元",
        "to_bn": Decimal("0.001"),
        "frequency": "每周三",
    },
    {
        "id": "RRPONTSYD",
        "name": "隔夜逆回购（ON RRP）",
        "unit": "十亿美元",
        "display_unit": "十亿美元",
        "to_bn": Decimal("1"),
        "frequency": "每个交易日",
    },
    {
        "id": "WRBWFRBL",
        "name": "准备金余额（周三）",
        "unit": "百万美元",
        "display_unit": "十亿美元",
        "to_bn": Decimal("0.001"),
        "frequency": "每周三",
    },
    {
        "id": "SOFR",
        "name": "担保隔夜融资利率（SOFR）",
        "unit": "百分比",
        "display_unit": "百分比",
        "to_bn": None,
        "frequency": "每个交易日",
    },
    {
        "id": "IORB",
        "name": "准备金余额利率（IORB）",
        "unit": "百分比",
        "display_unit": "百分比",
        "to_bn": None,
        "frequency": "每个交易日",
    },
    {
        "id": "EFFR",
        "name": "有效联邦基金利率（EFFR）",
        "unit": "百分比",
        "display_unit": "百分比",
        "to_bn": None,
        "frequency": "每个交易日",
    },
    {
        "id": "NFCI",
        "name": "芝加哥联储全国金融状况指数（NFCI）",
        "unit": "指数",
        "display_unit": "指数",
        "to_bn": None,
        "frequency": "每周",
    },
    {
        "id": "BAMLH0A0HYM2",
        "name": "美国高收益债期权调整利差（HY OAS）",
        "unit": "百分比",
        "display_unit": "百分比",
        "to_bn": None,
        "frequency": "每个交易日",
    },
    {
        "id": "VIXCLS",
        "name": "标普 500 波动率指数（VIX）",
        "unit": "指数",
        "display_unit": "指数",
        "to_bn": None,
        "frequency": "每个交易日",
    },
]


def _log(msg: str) -> None:
    print(msg, flush=True)


def fetch_csv(series_id: str) -> str:
    """下载单个序列。失败时抛出异常，由调用方决定整次运行失败。"""
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"
    last_err: Exception | None = None
    for attempt in range(1, RETRIES + 1):
        try:
            # 不设置 User-Agent，沿用 urllib 默认头。
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=TIMEOUT_SEC) as resp:
                raw = resp.read()
            text = raw.decode("utf-8-sig", errors="replace")
            head = text[:400].lower()
            if "observation_date" not in head or "<html" in head or "<!doctype" in head:
                raise RuntimeError(f"返回的不是 FRED CSV：{text[:160]!r}")
            if text.count("\n") < 2:
                raise RuntimeError("CSV 行数过少")
            return text
        except (urllib.error.URLError, TimeoutError, RuntimeError, OSError) as exc:
            last_err = exc
            _log(f"RETRY {series_id} {attempt}/{RETRIES} {exc}")
            if attempt < RETRIES:
                time.sleep(2 ** attempt)
    raise RuntimeError(f"{series_id} 刷新失败：{last_err}")


def parse_series(text: str) -> list[tuple[date, Decimal]]:
    rows: list[tuple[date, Decimal]] = []
    reader = csv.reader(io.StringIO(text))
    next(reader, None)
    for row in reader:
        if len(row) < 2:
            continue
        raw_v = row[1].strip()
        if raw_v in {"", ".", "NA", "ND"}:
            continue
        try:
            d = datetime.strptime(row[0].strip(), "%Y-%m-%d").date()
            value = Decimal(raw_v)
        except Exception:
            continue
        if d < START:
            continue
        rows.append((d, value))
    rows.sort(key=lambda item: item[0])
    return rows


def asof(series: list[tuple[date, Decimal]], day: date) -> tuple[date, Decimal] | None:
    lo, hi = 0, len(series) - 1
    best: tuple[date, Decimal] | None = None
    while lo <= hi:
        mid = (lo + hi) // 2
        if series[mid][0] <= day:
            best = series[mid]
            lo = mid + 1
        else:
            hi = mid - 1
    return best


def bn(value: Decimal, scale: Decimal) -> Decimal:
    return (value * scale).quantize(Q_BN, rounding=ROUND_HALF_UP)


def dec_str(value: Decimal) -> str:
    return format(value, "f")


def bp(rate: Decimal, iorb: Decimal) -> Decimal:
    return ((rate - iorb) * Decimal(100)).quantize(Q_BP, rounding=ROUND_HALF_UP)


def write_csv(path: Path, header: list[str], rows: list[list[str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(header)
        writer.writerows(rows)


def build_weekly(
    levels: dict[str, list[tuple[date, Decimal]]],
    specs: dict[str, dict],
) -> list[dict]:
    walcl = levels["WALCL"]
    wednesdays = [d for d, _ in walcl if d.weekday() == 2 and d >= START]
    if not wednesdays:
        raise RuntimeError("WALCL 在 2022-01-01 之后没有周三观测")

    reserves_all = [(d, v) for d, v in levels["WRBWFRBL"] if d >= START and d.weekday() == 2]
    if not reserves_all:
        raise RuntimeError("WRBWFRBL 在 2022-01-01 之后没有周三观测")

    out: list[dict] = []
    for day in wednesdays:
        wal = asof(levels["WALCL"], day)
        tga = asof(levels["WDTGAL"], day)
        rrp = asof(levels["RRPONTSYD"], day)
        res = asof(levels["WRBWFRBL"], day)
        if not (wal and tga and rrp and res):
            continue
        if (day - tga[0]).days > 6 or (day - res[0]).days > 6 or (day - rrp[0]).days > 6:
            continue
        if wal[0] != day:
            continue
        wal_bn = bn(wal[1], specs["WALCL"]["to_bn"])
        tga_bn = bn(tga[1], specs["WDTGAL"]["to_bn"])
        rrp_bn = bn(rrp[1], specs["RRPONTSYD"]["to_bn"])
        res_bn = bn(res[1], specs["WRBWFRBL"]["to_bn"])
        hist = [bn(v, specs["WRBWFRBL"]["to_bn"]) for d, v in reserves_all if d <= day]
        if not hist:
            continue
        pct = (Decimal(sum(1 for x in hist if x <= res_bn)) / Decimal(len(hist)) * Decimal(100)).quantize(
            Q_PCT, rounding=ROUND_HALF_UP
        )
        sofr = asof(levels["SOFR"], day)
        effr = asof(levels["EFFR"], day)
        iorb = asof(levels["IORB"], day)
        sofr_bp = ""
        effr_bp = ""
        rates_asof = ""
        if iorb and (day - iorb[0]).days <= 6:
            candidates = []
            if sofr and (day - sofr[0]).days <= 4:
                sofr_bp = dec_str(bp(sofr[1], iorb[1]))
                candidates.append(sofr[0])
            if effr and (day - effr[0]).days <= 4:
                effr_bp = dec_str(bp(effr[1], iorb[1]))
                candidates.append(effr[0])
            if candidates:
                rates_asof = max(candidates).isoformat()
        out.append(
            {
                "date": day,
                "walcl_bn": wal_bn,
                "tga_bn": tga_bn,
                "tga_asof": tga[0],
                "on_rrp_bn": rrp_bn,
                "on_rrp_asof": rrp[0],
                "reserves_bn": res_bn,
                "reserves_asof": res[0],
                "net_liq_bn": (wal_bn - tga_bn - rrp_bn).quantize(Q_BN, rounding=ROUND_HALF_UP),
                "reserves_percentile": pct,
                "sofr_iorb_bp": sofr_bp,
                "effr_iorb_bp": effr_bp,
                "rates_asof": rates_asof,
            }
        )
    if len(out) < 10:
        raise RuntimeError(f"对齐后的周三观测只有 {len(out)} 条，拒绝写入")
    for i, row in enumerate(out):
        if i == 0:
            row["walcl_wow_bn"] = ""
            row["tga_wow_bn"] = ""
            row["on_rrp_wow_bn"] = ""
            row["reserves_wow_bn"] = ""
            row["net_liq_wow_bn"] = ""
            continue
        prev = out[i - 1]
        row["walcl_wow_bn"] = dec_str(row["walcl_bn"] - prev["walcl_bn"])
        row["tga_wow_bn"] = dec_str(row["tga_bn"] - prev["tga_bn"])
        row["on_rrp_wow_bn"] = dec_str(row["on_rrp_bn"] - prev["on_rrp_bn"])
        row["reserves_wow_bn"] = dec_str(row["reserves_bn"] - prev["reserves_bn"])
        row["net_liq_wow_bn"] = dec_str(row["net_liq_bn"] - prev["net_liq_bn"])
    return out


def build_spreads(levels: dict[str, list[tuple[date, Decimal]]]) -> list[dict]:
    dates = sorted({d for key in ("SOFR", "EFFR") for d, _ in levels[key]})
    rows: list[dict] = []
    for day in dates:
        iorb = asof(levels["IORB"], day)
        if not iorb or (day - iorb[0]).days > 6:
            continue
        sofr = asof(levels["SOFR"], day)
        effr = asof(levels["EFFR"], day)
        sofr_v = sofr[1] if sofr and sofr[0] == day else None
        effr_v = effr[1] if effr and effr[0] == day else None
        if sofr_v is None and effr_v is None:
            continue
        rows.append(
            {
                "date": day.isoformat(),
                "sofr": dec_str(sofr_v) if sofr_v is not None else "",
                "iorb": dec_str(iorb[1]),
                "effr": dec_str(effr_v) if effr_v is not None else "",
                "sofr_iorb_bp": dec_str(bp(sofr_v, iorb[1])) if sofr_v is not None else "",
                "effr_iorb_bp": dec_str(bp(effr_v, iorb[1])) if effr_v is not None else "",
            }
        )
    if len(rows) < 10:
        raise RuntimeError("利差序列过短，拒绝写入")
    return rows


def series_meta(spec: dict, rows: list[tuple[date, Decimal]]) -> dict:
    last_d, last_v = rows[-1]
    scale = spec["to_bn"]
    return {
        "id": spec["id"],
        "name": spec["name"],
        "unit": spec["unit"],
        "display_unit": spec["display_unit"],
        "scale_to_billions": float(scale) if scale is not None else None,
        "frequency": spec["frequency"],
        "source": "FRED",
        "source_url": f"https://fred.stlouisfed.org/series/{spec['id']}",
        "file": f"series/{spec['id']}.csv",
        "last_date": last_d.isoformat(),
        "last_value": dec_str(last_v),
        "observations": len(rows),
    }


def publish(staging: Path) -> None:
    data_dir = ROOT / "data"
    backup = ROOT / "data.prev"
    if backup.exists():
        shutil.rmtree(backup)
    if data_dir.exists():
        data_dir.rename(backup)
    staging.rename(data_dir)
    if backup.exists():
        shutil.rmtree(backup)


def main() -> int:
    specs = {item["id"]: item for item in SERIES}
    fetched: dict[str, list[tuple[date, Decimal]]] = {}
    errors: list[str] = []

    def _one(spec: dict) -> tuple[str, list[tuple[date, Decimal]]]:
        text = fetch_csv(spec["id"])
        rows = parse_series(text)
        if not rows:
            raise RuntimeError(f"{spec['id']} 在 {START.isoformat()} 之后没有有效观测")
        return spec["id"], rows

    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = {pool.submit(_one, spec): spec["id"] for spec in SERIES}
        for fut in as_completed(futures):
            sid = futures[fut]
            try:
                key, rows = fut.result()
                fetched[key] = rows
                _log(f"FETCH_OK {key} n={len(rows)} last={rows[-1][0].isoformat()}")
            except Exception as exc:  # noqa: BLE001
                errors.append(f"{sid}: {exc}")
                _log(f"FETCH_FAIL {sid} {exc}")

    if errors or len(fetched) != len(SERIES):
        print("刷新失败，未改写 data/。", file=sys.stderr)
        for err in errors:
            print(err, file=sys.stderr)
        return 1

    weekly = build_weekly(fetched, specs)
    spreads = build_spreads(fetched)
    updated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    staging = Path(tempfile.mkdtemp(prefix="macro-data-", dir=str(ROOT)))
    try:
        for spec in SERIES:
            rows = fetched[spec["id"]]
            write_csv(
                staging / "series" / f"{spec['id']}.csv",
                ["date", "value"],
                [[d.isoformat(), dec_str(v)] for d, v in rows],
            )

        weekly_header = [
            "date",
            "walcl_bn",
            "tga_bn",
            "tga_asof",
            "on_rrp_bn",
            "on_rrp_asof",
            "reserves_bn",
            "reserves_asof",
            "net_liq_bn",
            "walcl_wow_bn",
            "tga_wow_bn",
            "on_rrp_wow_bn",
            "reserves_wow_bn",
            "net_liq_wow_bn",
            "reserves_percentile",
            "sofr_iorb_bp",
            "effr_iorb_bp",
            "rates_asof",
        ]
        weekly_rows = []
        for row in weekly:
            weekly_rows.append(
                [
                    row["date"].isoformat(),
                    dec_str(row["walcl_bn"]),
                    dec_str(row["tga_bn"]),
                    row["tga_asof"].isoformat(),
                    dec_str(row["on_rrp_bn"]),
                    row["on_rrp_asof"].isoformat(),
                    dec_str(row["reserves_bn"]),
                    row["reserves_asof"].isoformat(),
                    dec_str(row["net_liq_bn"]),
                    row["walcl_wow_bn"],
                    row["tga_wow_bn"],
                    row["on_rrp_wow_bn"],
                    row["reserves_wow_bn"],
                    row["net_liq_wow_bn"],
                    dec_str(row["reserves_percentile"]),
                    row["sofr_iorb_bp"],
                    row["effr_iorb_bp"],
                    row["rates_asof"],
                ]
            )
        write_csv(staging / "derived" / "weekly.csv", weekly_header, weekly_rows)
        write_csv(
            staging / "derived" / "spreads.csv",
            ["date", "sofr", "iorb", "effr", "sofr_iorb_bp", "effr_iorb_bp"],
            [[r["date"], r["sofr"], r["iorb"], r["effr"], r["sofr_iorb_bp"], r["effr_iorb_bp"]] for r in spreads],
        )

        latest = weekly[-1]
        latest_spread = next((r for r in reversed(spreads) if r["sofr_iorb_bp"]), None)
        meta = {
            "updated_at": updated_at,
            "history_start": START.isoformat(),
            "display_unit": "十亿美元",
            "spread_unit": "基点",
            "net_liquidity": {
                "name": "市场常用净流动性代理（非官方）",
                "formula": "WALCL − WDTGAL − RRPONTSYD，三条都换算成十亿美元后再相减",
                "note": "这是市场上常用的代理算法，不是美联储发布的官方指标。",
                "file": "derived/weekly.csv",
                "column": "net_liq_bn",
            },
            "weekly_change": {
                "name": "周变动",
                "note": "与上一条周三观测相比的差额，单位是十亿美元。",
            },
            "spreads": {
                "name": "SOFR−IORB 与 EFFR−IORB",
                "formula": "(利率 − IORB) × 100，单位是基点",
                "file": "derived/spreads.csv",
            },
            "reserves_percentile": {
                "name": "准备金分位（2022年以来）",
                "definition": "2022-01-01 起至该周三（含）的周三观测中，准备金余额小于或等于当前值的占比。",
                "note": "这不是准备金短缺的度量，只说明当前水平在这段历史里的位置。",
                "file": "derived/weekly.csv",
                "column": "reserves_percentile",
            },
            "files": {
                "weekly": "derived/weekly.csv",
                "spreads": "derived/spreads.csv",
            },
            "series": [series_meta(spec, fetched[spec["id"]]) for spec in SERIES],
            "latest_wednesday": latest["date"].isoformat(),
        }
        (staging / "meta.json").write_text(
            json.dumps(meta, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        publish(staging)
        staging = None
    finally:
        if staging is not None and staging.exists():
            shutil.rmtree(staging, ignore_errors=True)

    latest = weekly[-1]
    latest_spread = next((r for r in reversed(spreads) if r["sofr_iorb_bp"]), None)
    _log(f"UPDATED {updated_at}")
    _log(f"WED {latest['date'].isoformat()}")
    _log(f"NET_LIQ_BN={dec_str(latest['net_liq_bn'])}")
    _log(f"NET_LIQ_WOW={latest['net_liq_wow_bn']}")
    _log(f"TGA_BN={dec_str(latest['tga_bn'])}")
    _log(f"RESERVES_BN={dec_str(latest['reserves_bn'])}")
    _log(f"RESERVES_PCTL={dec_str(latest['reserves_percentile'])}")
    _log(f"ON_RRP_BN={dec_str(latest['on_rrp_bn'])}")
    _log(f"WALCL_BN={dec_str(latest['walcl_bn'])}")
    if latest_spread:
        _log(f"SOFR_IORB_BP={latest_spread['sofr_iorb_bp']} asof={latest_spread['date']}")
        _log(f"EFFR_IORB_BP={latest_spread['effr_iorb_bp']}")
    _log("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
