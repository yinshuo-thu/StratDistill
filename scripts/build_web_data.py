#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, Any, List

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
PROCESSED = DATA / "processed"
RAW = DATA / "raw"
WEB = ROOT / "web"
WEB_DATA = WEB / "data"


def _read_latest_leader_fills() -> Dict[str, Any]:
    d = RAW / "leader_fills"
    files = sorted(d.glob("leader_fills_top*_*.json"))
    if not files:
        return {}
    return json.loads(files[-1].read_text(encoding="utf-8"))


def _read_latest_vault_details() -> Dict[str, Any]:
    d = RAW / "vault_details"
    files = sorted(d.glob("details_top*_*.json"))
    if not files:
        return {}
    return json.loads(files[-1].read_text(encoding="utf-8"))


def _safe_float(x: Any, default: float | None = None) -> float | None:
    try:
        return float(x)
    except Exception:
        return default


def _extract_series_from_details(detail: Dict[str, Any]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    portfolio = detail.get("portfolio", [])
    if not isinstance(portfolio, list):
        return out

    for item in portfolio:
        if not isinstance(item, list) or len(item) != 2:
            continue
        label, payload = item
        if not isinstance(payload, dict):
            continue
        hist = payload.get("accountValueHistory", [])
        if not isinstance(hist, list):
            continue
        for idx, point in enumerate(hist):
            if not isinstance(point, list) or len(point) < 2:
                continue
            out.append(
                {
                    "series": str(label),
                    "idx": idx,
                    "time": int(point[0]) if point[0] is not None else None,
                    "value": _safe_float(point[1], 0.0),
                    "source": "accountValueHistory",
                }
            )
    return out


def _read_series(vault_addr: str, details_map: Dict[str, Any]) -> List[Dict[str, Any]]:
    detail = details_map.get(vault_addr)
    if isinstance(detail, dict):
        rows = _extract_series_from_details(detail)
        if rows:
            return rows

    p = PROCESSED / "timeseries" / f"{vault_addr}.csv"
    if not p.exists():
        return []
    df = pd.read_csv(p)
    out = []
    for _, r in df.iterrows():
        out.append(
            {
                "series": str(r.get("series")),
                "idx": int(r.get("idx", 0)),
                "time": None,
                "value": float(r.get("value", 0.0)),
                "source": "pnlSeries",
            }
        )
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Build static web data for strategy performance + action proxies")
    parser.add_argument("--top-n", type=int, default=50)
    parser.add_argument("--max-fills-per-strategy", type=int, default=1500)
    args = parser.parse_args()

    WEB_DATA.mkdir(parents=True, exist_ok=True)

    rank = pd.read_csv(PROCESSED / "strategy_ranked_extended.csv")
    top = rank.sort_values("extended_rank").head(args.top_n).copy()

    leader_fills = _read_latest_leader_fills()
    details_map = _read_latest_vault_details()

    items = []
    for _, r in top.iterrows():
        vault = str(r.get("vault_address"))
        leader = str(r.get("leader_detail")) if pd.notna(r.get("leader_detail")) else ""
        fills = leader_fills.get(leader, []) if isinstance(leader_fills, dict) else []
        if isinstance(fills, list):
            fills = sorted(fills, key=lambda x: x.get("time", 0))[-args.max_fills_per_strategy :]
        else:
            fills = []

        fill_rows = []
        for f in fills:
            fill_rows.append(
                {
                    "time": int(f.get("time", 0)),
                    "coin": str(f.get("coin", "")),
                    "dir": str(f.get("dir", "")),
                    "side": str(f.get("side", "")),
                    "px": float(f.get("px", 0.0) or 0.0),
                    "sz": float(f.get("sz", 0.0) or 0.0),
                    "closedPnl": float(f.get("closedPnl", 0.0) or 0.0),
                }
            )

        items.append(
            {
                "name": str(r.get("name", vault)),
                "vault_address": vault,
                "leader": leader,
                "extended_rank": int(r.get("extended_rank", 0)),
                "extended_score": float(r.get("extended_score", 0.0)),
                "composite_score": float(r.get("composite_score", 0.0)),
                "apr": float(r.get("apr", 0.0)) if pd.notna(r.get("apr")) else None,
                "tvl": float(r.get("tvl", 0.0)) if pd.notna(r.get("tvl")) else None,
                "pnl_all_time_last": float(r.get("pnl_all_time_last", 0.0)) if pd.notna(r.get("pnl_all_time_last")) else None,
                "pnl_all_time_max_dd": float(r.get("pnl_all_time_max_dd", 0.0)) if pd.notna(r.get("pnl_all_time_max_dd")) else None,
                "pnl_all_time_stability": float(r.get("pnl_all_time_stability", 0.0)) if pd.notna(r.get("pnl_all_time_stability")) else None,
                "series": _read_series(vault, details_map),
                "fills": fill_rows,
            }
        )

    payload = {
        "meta": {
            "top_n": args.top_n,
            "max_fills_per_strategy": args.max_fills_per_strategy,
            "note": "fills are leader-level public fills used as action/position proxy; may cover multiple vaults managed by same leader",
            "series_note": "prefer accountValueHistory from latest vaultDetails raw snapshot; fallback to processed pnl series when timestamped detail history is unavailable",
        },
        "strategies": items,
    }
    out_path = WEB_DATA / "top_strategies.json"
    out_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"out": str(out_path), "strategies": len(items)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
