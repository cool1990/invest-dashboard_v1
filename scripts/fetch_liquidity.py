#!/usr/bin/env python3
"""从 FRED 公开 CSV 拉取美国流动性序列，并写入 data/series/。

只用 Python 标准库。每条序列单独处理：下载成功就覆盖它的 CSV；
失败就留下原来的文件，并在 data/meta.json 记下 last_fetch_ok、
last_obs_date、fetched_at。publish() 只替换 data/series 和 data/derived，
再合并 meta.json 里的流动性字段，不动情绪、盈利、半导体和 notes_skipped.csv。

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
    {
        "id": "ANFCI",
        "name": "芝加哥联储调整后全国金融状况指数（ANFCI）",
        "unit": "指数",
        "display_unit": "指数",
        "to_bn": None,
        "frequency": "每周",
    },
    {
        "id": "STLFSI4",
        "name": "圣路易斯联储金融压力指数（STLFSI4）",
        "unit": "指数",
        "display_unit": "指数",
        "to_bn": None,
        "frequency": "每周",
    },
    {
        "id": "STLFSI",
        "name": "圣路易斯联储金融压力指数（旧版，已停更）",
        "unit": "指数",
        "display_unit": "指数",
        "to_bn": None,
        "frequency": "每周",
        "skip_if_ended": True,
    },
    {
        "id": "WRESBAL",
        "name": "准备金余额（周平均）",
        "unit": "百万美元",
        "display_unit": "十亿美元",
        "to_bn": Decimal("0.001"),
        "frequency": "每周",
    },
    {
        "id": "WTREGEN",
        "name": "财政部一般账户（TGA，周平均）",
        "unit": "百万美元",
        "display_unit": "十亿美元",
        "to_bn": Decimal("0.001"),
        "frequency": "每周",
    },
    {
        "id": "WLRRAOL",
        "name": "逆回购：其他（周三水平）",
        "unit": "百万美元",
        "display_unit": "十亿美元",
        "to_bn": Decimal("0.001"),
        "frequency": "每周三",
    },
    {
        "id": "WCURCIR",
        "name": "流通中货币（周平均）",
        "unit": "百万美元",
        "display_unit": "十亿美元",
        "to_bn": Decimal("0.001"),
        "frequency": "每周",
    },
    {
        "id": "SOFR1",
        "name": "SOFR 第 1 百分位",
        "unit": "百分比",
        "display_unit": "百分比",
        "to_bn": None,
        "frequency": "每个交易日",
    },
    {
        "id": "SOFR25",
        "name": "SOFR 第 25 百分位",
        "unit": "百分比",
        "display_unit": "百分比",
        "to_bn": None,
        "frequency": "每个交易日",
    },
    {
        "id": "SOFR75",
        "name": "SOFR 第 75 百分位",
        "unit": "百分比",
        "display_unit": "百分比",
        "to_bn": None,
        "frequency": "每个交易日",
    },
    {
        "id": "SOFR99",
        "name": "SOFR 第 99 百分位",
        "unit": "百分比",
        "display_unit": "百分比",
        "to_bn": None,
        "frequency": "每个交易日",
    },
    {
        "id": "SOFRVOL",
        "name": "SOFR 成交量",
        "unit": "十亿美元",
        "display_unit": "十亿美元",
        "to_bn": Decimal("1"),
        "frequency": "每个交易日",
    },
    {
        "id": "TOTBKCR",
        "name": "全部商业银行信贷",
        "unit": "十亿美元",
        "display_unit": "十亿美元",
        "to_bn": Decimal("1"),
        "frequency": "每周",
    },
    {
        "id": "TOTCI",
        "name": "全部商业银行工商业贷款",
        "unit": "十亿美元",
        "display_unit": "十亿美元",
        "to_bn": Decimal("1"),
        "frequency": "每周",
    },
    {
        "id": "TLAACBW027SBOG",
        "name": "全部商业银行总资产",
        "unit": "十亿美元",
        "display_unit": "十亿美元",
        "to_bn": Decimal("1"),
        "frequency": "每周",
    },
    {
        "id": "CCLACBW027SBOG",
        "name": "全部商业银行消费贷款（信用卡及其他循环额度）",
        "unit": "十亿美元",
        "display_unit": "十亿美元",
        "to_bn": Decimal("1"),
        "frequency": "每周",
    },
    {
        "id": "CREACBW027SBOG",
        "name": "全部商业银行商业房地产贷款",
        "unit": "十亿美元",
        "display_unit": "十亿美元",
        "to_bn": Decimal("1"),
        "frequency": "每周",
    },
    {
        "id": "DPSACBW027SBOG",
        "name": "全部商业银行存款",
        "unit": "十亿美元",
        "display_unit": "十亿美元",
        "to_bn": Decimal("1"),
        "frequency": "每周",
    },
    {
        "id": "DPSLCBW027SBOG",
        "name": "大型国内商业银行存款",
        "unit": "十亿美元",
        "display_unit": "十亿美元",
        "to_bn": Decimal("1"),
        "frequency": "每周",
    },
]

# 周三派生表用到的序列。其中任何一条这次没刷新，就不重写 derived/。
DERIVED_IDS = ("WALCL", "WDTGAL", "RRPONTSYD", "WRBWFRBL", "SOFR", "IORB", "EFFR")

# 这些键属于早晨笔记。publish() 合并 meta 时一律保留磁盘上的原值。
NOTES_META_KEYS = ("sentiment", "earnings", "semis", "notes_asof")


def _log(msg: str) -> None:
    print(msg, flush=True)


class FetchProblem(Exception):
    def __init__(self, message: str, *, missing: bool = False):
        super().__init__(message)
        self.missing = missing


def fetch_csv(series_id: str) -> str:
    """下载单个序列。失败时抛出 FetchProblem，不改动已有文件。"""
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
                missing = "does not exist" in head or "wasn't recognized" in head or "not found" in head
                raise FetchProblem(f"返回的不是 FRED CSV：{text[:160]!r}", missing=missing)
            if text.count("\n") < 2:
                raise FetchProblem("CSV 行数过少")
            return text
        except urllib.error.HTTPError as exc:
            missing = exc.code == 404
            last_err = FetchProblem(f"HTTP {exc.code}", missing=missing)
            _log(f"RETRY {series_id} {attempt}/{RETRIES} {last_err}")
            if missing:
                break
            if attempt < RETRIES:
                time.sleep(2 ** attempt)
        except (urllib.error.URLError, TimeoutError, FetchProblem, OSError) as exc:
            last_err = exc if isinstance(exc, FetchProblem) else FetchProblem(str(exc))
            _log(f"RETRY {series_id} {attempt}/{RETRIES} {last_err}")
            if attempt < RETRIES:
                time.sleep(2 ** attempt)
    raise FetchProblem(f"{series_id} 刷新失败：{last_err}", missing=bool(getattr(last_err, "missing", False)))


def parse_observations(text: str) -> list[tuple[date, Decimal]]:
    """解析全部有效观测，不过滤起始日。缺失值（. / 空）跳过。"""
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
        rows.append((d, value))
    rows.sort(key=lambda item: item[0])
    return rows


def parse_series(text: str) -> list[tuple[date, Decimal]]:
    return [item for item in parse_observations(text) if item[0] >= START]


def judge(
    spec: dict,
    rows_all: list[tuple[date, Decimal]] | None,
    error: str | None,
    missing: bool,
    existing_n: int,
) -> dict:
    """决定写入、保留旧文件，还是把已停更的序列标出来。不产生数字。"""
    if error:
        if missing and spec.get("skip_if_ended"):
            return {
                "action": "discontinued",
                "last_fetch_ok": False,
                "rows": None,
                "last_raw": None,
                "error": error,
            }
        return {
            "action": "keep",
            "last_fetch_ok": False,
            "rows": None,
            "last_raw": None,
            "error": error,
        }
    window = [item for item in (rows_all or []) if item[0] >= START]
    last_raw = rows_all[-1] if rows_all else None
    if not window:
        if spec.get("skip_if_ended"):
            return {
                "action": "discontinued",
                "last_fetch_ok": True,
                "rows": [],
                "last_raw": last_raw,
                "error": None,
            }
        return {
            "action": "keep",
            "last_fetch_ok": False,
            "rows": None,
            "last_raw": last_raw,
            "error": f"{spec['id']} 在 {START.isoformat()} 之后没有有效观测",
        }
    if existing_n >= 20 and len(window) * 2 < existing_n:
        return {
            "action": "keep",
            "last_fetch_ok": False,
            "rows": None,
            "last_raw": window[-1],
            "error": f"新数据只有 {len(window)} 行，旧文件有 {existing_n} 行，拒绝覆盖",
        }
    return {
        "action": "write",
        "last_fetch_ok": True,
        "rows": window,
        "last_raw": window[-1],
        "error": None,
    }


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
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(header)
        writer.writerows(rows)
    tmp.replace(path)


def read_series_file(path: Path) -> list[tuple[date, Decimal]]:
    if not path.exists():
        return []
    return parse_series(path.read_text(encoding="utf-8"))


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


def now_stamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def series_entry(
    spec: dict,
    rows: list[tuple[date, Decimal]] | None,
    *,
    last_fetch_ok: bool,
    fetched_at: str,
    status: str,
    last_raw: tuple[date, Decimal] | None = None,
    error: str | None = None,
) -> dict:
    scale = spec["to_bn"]
    entry = {
        "id": spec["id"],
        "name": spec["name"],
        "unit": spec["unit"],
        "display_unit": spec["display_unit"],
        "scale_to_billions": float(scale) if scale is not None else None,
        "frequency": spec["frequency"],
        "source": "FRED",
        "source_url": f"https://fred.stlouisfed.org/series/{spec['id']}",
        "status": status,
        "last_fetch_ok": last_fetch_ok,
        "fetched_at": fetched_at,
    }
    if status == "discontinued":
        entry["file"] = None
        entry["last_obs_date"] = last_raw[0].isoformat() if last_raw else None
        entry["last_date"] = entry["last_obs_date"] or ""
        entry["last_value"] = dec_str(last_raw[1]) if last_raw else None
        entry["observations"] = 0
        if last_raw:
            entry["note"] = (
                f"FRED 仍能下载，但最后观测是 {last_raw[0].isoformat()}，早于 {START.isoformat()}，没有写入 CSV。"
            )
        else:
            entry["note"] = error or "FRED 没有发布这条序列，没有写入 CSV。"
        return entry
    if rows:
        last_d, last_v = rows[-1]
        entry["file"] = f"series/{spec['id']}.csv"
        entry["last_obs_date"] = last_d.isoformat()
        entry["last_date"] = last_d.isoformat()
        entry["last_value"] = dec_str(last_v)
        entry["observations"] = len(rows)
    else:
        entry["file"] = f"series/{spec['id']}.csv" if (ROOT / "data" / "series" / f"{spec['id']}.csv").exists() else None
        entry["last_obs_date"] = None
        entry["last_date"] = ""
        entry["last_value"] = None
        entry["observations"] = 0
    if error:
        entry["fetch_error"] = error
    return entry


def merge_meta(existing: dict, incoming: dict) -> dict:
    """用 incoming 更新流动性字段，笔记字段始终留 existing 里的那一份。"""
    merged = dict(existing)
    for key, value in incoming.items():
        if key in NOTES_META_KEYS:
            continue
        merged[key] = value
    for key in NOTES_META_KEYS:
        if key in existing:
            merged[key] = existing[key]
    return merged


def replace_subdir(src: Path, dest: Path) -> None:
    """用 src 换掉 dest 这一个子目录，不动它旁边的其他目录。"""
    if not src.is_dir():
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    incoming = dest.parent / f".{dest.name}.incoming"
    backup = dest.parent / f".{dest.name}.backup"
    if incoming.exists():
        shutil.rmtree(incoming)
    shutil.copytree(src, incoming)
    if backup.exists():
        shutil.rmtree(backup)
    if dest.exists():
        dest.rename(backup)
    try:
        incoming.rename(dest)
    except Exception:
        if backup.exists() and not dest.exists():
            backup.rename(dest)
        raise
    if backup.exists():
        shutil.rmtree(backup)


def publish(staging: Path, data_dir: Path | None = None) -> None:
    """只替换 data/series 和 data/derived，并合并 meta.json。

    staging 里就算带了 sentiment/ 或一份残缺的 meta，也不会覆盖笔记数据。
    某个子目录不在 staging 里时，磁盘上的那个目录保持原样。
    """
    data = data_dir if data_dir is not None else ROOT / "data"
    data.mkdir(parents=True, exist_ok=True)
    for name in ("series", "derived"):
        src = staging / name
        if src.is_dir():
            replace_subdir(src, data / name)
    meta_src = staging / "meta.json"
    if not meta_src.exists():
        return
    incoming = json.loads(meta_src.read_text(encoding="utf-8"))
    meta_path = data / "meta.json"
    existing = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}
    merged = merge_meta(existing, incoming)
    tmp = meta_path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(merged, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(meta_path)


def write_derived(weekly: list[dict], spreads: list[dict], dest: Path) -> None:
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
    write_csv(dest / "weekly.csv", weekly_header, weekly_rows)
    write_csv(
        dest / "spreads.csv",
        ["date", "sofr", "iorb", "effr", "sofr_iorb_bp", "effr_iorb_bp"],
        [[r["date"], r["sofr"], r["iorb"], r["effr"], r["sofr_iorb_bp"], r["effr_iorb_bp"]] for r in spreads],
    )


def main() -> int:
    data_series = ROOT / "data" / "series"
    data_series.mkdir(parents=True, exist_ok=True)
    existing_counts = {
        spec["id"]: len(read_series_file(data_series / f"{spec['id']}.csv")) for spec in SERIES
    }
    outcomes: dict[str, dict] = {}

    def _one(spec: dict) -> tuple[str, dict]:
        fetched_at = now_stamp()
        try:
            text = fetch_csv(spec["id"])
            rows_all = parse_observations(text)
            decision = judge(spec, rows_all, None, False, existing_counts[spec["id"]])
        except FetchProblem as exc:
            decision = judge(spec, None, str(exc), exc.missing, existing_counts[spec["id"]])
        decision["fetched_at"] = fetched_at
        return spec["id"], decision

    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = {pool.submit(_one, spec): spec["id"] for spec in SERIES}
        for fut in as_completed(futures):
            sid = futures[fut]
            try:
                key, decision = fut.result()
            except Exception as exc:  # noqa: BLE001
                key = sid
                decision = {
                    "action": "keep",
                    "last_fetch_ok": False,
                    "rows": None,
                    "last_raw": None,
                    "error": str(exc),
                    "fetched_at": now_stamp(),
                }
            outcomes[key] = decision
            if decision["action"] == "write":
                last = decision["rows"][-1][0].isoformat()
                _log(f"FETCH_OK {key} n={len(decision['rows'])} last={last}")
            elif decision["action"] == "discontinued":
                raw = decision["last_raw"][0].isoformat() if decision["last_raw"] else "none"
                _log(f"DISCONTINUED {key} last_published={raw}")
            else:
                _log(f"FETCH_FAIL {key} {decision['error']}")

    staging = Path(tempfile.mkdtemp(prefix="liq-stage-", dir=str(ROOT)))
    levels: dict[str, list[tuple[date, Decimal]]] = {}
    try:
        for spec in SERIES:
            decision = outcomes[spec["id"]]
            path = data_series / f"{spec['id']}.csv"
            if decision["action"] == "write":
                rows = decision["rows"]
                write_csv(
                    staging / "series" / f"{spec['id']}.csv",
                    ["date", "value"],
                    [[d.isoformat(), dec_str(v)] for d, v in rows],
                )
                levels[spec["id"]] = rows
            elif decision["action"] == "keep" and path.exists():
                dest = staging / "series" / path.name
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(path, dest)
                kept = read_series_file(path)
                if kept:
                    levels[spec["id"]] = kept
                    _log(f"KEPT {spec['id']} n={len(kept)} last={kept[-1][0].isoformat()}")
            elif decision["action"] == "keep":
                _log(f"KEPT {spec['id']} 没有旧文件")

        updated_at = now_stamp()
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
            "files": {"weekly": "derived/weekly.csv", "spreads": "derived/spreads.csv"},
        }

        entries = []
        for spec in SERIES:
            decision = outcomes[spec["id"]]
            if decision["action"] == "discontinued":
                entries.append(
                    series_entry(
                        spec,
                        None,
                        last_fetch_ok=decision["last_fetch_ok"],
                        fetched_at=decision["fetched_at"],
                        status="discontinued",
                        last_raw=decision["last_raw"],
                        error=decision["error"],
                    )
                )
                continue
            rows = levels.get(spec["id"])
            status = "ok" if decision["last_fetch_ok"] else "fetch_failed"
            entries.append(
                series_entry(
                    spec,
                    rows,
                    last_fetch_ok=decision["last_fetch_ok"],
                    fetched_at=decision["fetched_at"],
                    status=status,
                    error=decision["error"],
                )
            )
        meta["series"] = entries

        failed_core = [sid for sid in DERIVED_IDS if not outcomes[sid]["last_fetch_ok"]]
        weekly = None
        spreads = None
        if failed_core:
            meta["derived_refresh"] = {
                "ok": False,
                "fetched_at": updated_at,
                "failed": failed_core,
                "note": "这些序列本次没有刷新，周三表和利差表保持原文件：" + "、".join(failed_core),
            }
            _log("DERIVED_SKIP " + ",".join(failed_core))
        else:
            specs = {item["id"]: item for item in SERIES}
            try:
                weekly = build_weekly(levels, specs)
                spreads = build_spreads(levels)
                write_derived(weekly, spreads, staging / "derived")
                meta["latest_wednesday"] = weekly[-1]["date"].isoformat()
                meta["derived_refresh"] = {"ok": True, "fetched_at": updated_at}
                _log(f"DERIVED_OK wed={weekly[-1]['date'].isoformat()}")
            except Exception as exc:  # noqa: BLE001
                meta["derived_refresh"] = {
                    "ok": False,
                    "fetched_at": updated_at,
                    "note": f"周三表没有重算，原文件保留：{exc}",
                }
                _log(f"DERIVED_FAIL {exc}")
                weekly = None

        (staging / "meta.json").write_text(
            json.dumps(meta, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        publish(staging)
    finally:
        shutil.rmtree(staging, ignore_errors=True)

    failed = [spec["id"] for spec in SERIES if outcomes[spec["id"]]["action"] == "keep"]
    discontinued = [spec["id"] for spec in SERIES if outcomes[spec["id"]]["action"] == "discontinued"]
    _log(f"UPDATED {updated_at}")
    if weekly:
        latest = weekly[-1]
        latest_spread = next((r for r in reversed(spreads or []) if r["sofr_iorb_bp"]), None)
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
    if discontinued:
        _log("DISCONTINUED_IDS " + ",".join(discontinued))
    if failed:
        print("有序列本次没有刷新，旧文件保留，详见 meta.json 的 last_fetch_ok。", file=sys.stderr)
        for sid in failed:
            print(f"{sid}: {outcomes[sid]['error']}", file=sys.stderr)
    _log("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
