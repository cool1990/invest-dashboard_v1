#!/usr/bin/env python3
"""确认流动性发布和笔记整理都不会清掉对方的数据。"""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
from pathlib import Path


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


ROOT = Path(__file__).resolve().parent.parent
fetch = load("fetch_liquidity", ROOT / "scripts" / "fetch_liquidity.py")
notes = load("parse_notes", ROOT / "ingest" / "parse_notes.py")


def test_publish_keeps_notes() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        data = Path(tmp) / "data"
        (data / "sentiment").mkdir(parents=True)
        (data / "sentiment" / "series.csv").write_text("keep-sentiment\n", encoding="utf-8")
        (data / "earnings").mkdir()
        (data / "earnings" / "daily.csv").write_text("keep-earnings\n", encoding="utf-8")
        (data / "semis").mkdir()
        (data / "semis" / "gpu.csv").write_text("keep-gpu\n", encoding="utf-8")
        (data / "notes_skipped.csv").write_text("keep-skipped\n", encoding="utf-8")
        (data / "series").mkdir()
        (data / "series" / "WALCL.csv").write_text("old\n", encoding="utf-8")
        (data / "series" / "KEPT.csv").write_text("kept\n", encoding="utf-8")
        (data / "derived").mkdir()
        (data / "derived" / "weekly.csv").write_text("old-week\n", encoding="utf-8")
        (data / "meta.json").write_text(
            json.dumps(
                {
                    "series": [{"id": "WALCL"}],
                    "latest_wednesday": "2026-09-23",
                    "sentiment": {"observations": 220},
                    "earnings": {"rows": 466},
                    "semis": {"memory": {"start": "2026-09-16"}},
                    "notes_asof": "2026-09-26",
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        staging = Path(tmp) / "staging"
        (staging / "series").mkdir(parents=True)
        (staging / "series" / "WALCL.csv").write_text("new\n", encoding="utf-8")
        (staging / "series" / "KEPT.csv").write_text("kept\n", encoding="utf-8")
        (staging / "sentiment").mkdir()
        (staging / "sentiment" / "evil.csv").write_text("nope\n", encoding="utf-8")
        (staging / "meta.json").write_text(
            json.dumps(
                {
                    "updated_at": "NEW",
                    "series": [{"id": "WALCL", "last_fetch_ok": True}],
                    "sentiment": {"observations": 0},
                    "notes_asof": "",
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        fetch.publish(staging, data)

        assert (data / "sentiment" / "series.csv").read_text(encoding="utf-8") == "keep-sentiment\n"
        assert not (data / "sentiment" / "evil.csv").exists()
        assert (data / "earnings" / "daily.csv").read_text(encoding="utf-8") == "keep-earnings\n"
        assert (data / "semis" / "gpu.csv").read_text(encoding="utf-8") == "keep-gpu\n"
        assert (data / "notes_skipped.csv").read_text(encoding="utf-8") == "keep-skipped\n"
        assert (data / "series" / "WALCL.csv").read_text(encoding="utf-8") == "new\n"
        assert (data / "series" / "KEPT.csv").read_text(encoding="utf-8") == "kept\n"
        assert (data / "derived" / "weekly.csv").read_text(encoding="utf-8") == "old-week\n"
        meta = json.loads((data / "meta.json").read_text(encoding="utf-8"))
        assert meta["updated_at"] == "NEW"
        assert meta["series"][0]["last_fetch_ok"] is True
        assert meta["sentiment"]["observations"] == 220
        assert meta["earnings"]["rows"] == 466
        assert meta["semis"]["memory"]["start"] == "2026-09-16"
        assert meta["notes_asof"] == "2026-09-26"
        assert meta["latest_wednesday"] == "2026-09-23"

        derived = Path(tmp) / "derived-only"
        (derived / "derived").mkdir(parents=True)
        (derived / "derived" / "weekly.csv").write_text("new-week\n", encoding="utf-8")
        fetch.publish(derived, data)
        assert (data / "derived" / "weekly.csv").read_text(encoding="utf-8") == "new-week\n"
        assert (data / "sentiment" / "series.csv").read_text(encoding="utf-8") == "keep-sentiment\n"
        assert (data / "series" / "WALCL.csv").read_text(encoding="utf-8") == "new\n"


def test_ingest_keeps_liquidity() -> None:
    existing = {
        "updated_at": "2026-09-27T10:04:02Z",
        "history_start": "2022-01-01",
        "series": [{"id": "WALCL", "last_fetch_ok": True, "last_obs_date": "2026-09-23"}],
        "latest_wednesday": "2026-09-23",
        "derived_refresh": {"ok": True},
        "sentiment": {"observations": 1},
        "notes_asof": "old",
    }
    empty = {
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
    out = notes.build_meta(existing, empty)
    assert out["series"][0]["id"] == "WALCL"
    assert out["series"][0]["last_fetch_ok"] is True
    assert out["latest_wednesday"] == "2026-09-23"
    assert out["derived_refresh"]["ok"] is True
    assert out["updated_at"] == "2026-09-27T10:04:02Z"
    assert out["history_start"] == "2022-01-01"
    assert "sentiment" in out
    assert "earnings" in out
    assert "semis" in out


if __name__ == "__main__":
    test_publish_keeps_notes()
    test_ingest_keeps_liquidity()
    print("OK")
    sys.exit(0)
