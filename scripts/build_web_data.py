#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
PROCESSED = DATA / "processed"
RAW = DATA / "raw"
WEB = ROOT / "web"
WEB_DATA = WEB / "data"


def _read_latest_leader_fills() -> Tuple[Path | None, Dict[str, Any]]:
    d = RAW / "leader_fills"
    files = sorted(d.glob("leader_fills_top*_*.json"))
    if not files:
        return None, {}
    path = files[-1]
    return path, json.loads(path.read_text(encoding="utf-8"))


def _read_latest_vault_details() -> Tuple[Path | None, Dict[str, Any]]:
    d = RAW / "vault_details"
    files = sorted(d.glob("details_top*_*.json"))
    if not files:
        return None, {}
    path = files[-1]
    return path, json.loads(path.read_text(encoding="utf-8"))


def _portfolio_map(portfolio: Any) -> Dict[str, Dict[str, Any]]:
    out: Dict[str, Dict[str, Any]] = {}
    if not isinstance(portfolio, list):
        return out
    for item in portfolio:
        if isinstance(item, list) and len(item) == 2 and isinstance(item[1], dict):
            out[str(item[0])] = item[1]
    return out


def _series_with_ts(pm: Dict[str, Dict[str, Any]], label: str, key: str) -> List[Dict[str, Any]]:
    p = pm.get(label, {})
    arr = p.get(key, []) if isinstance(p, dict) else []
    out: List[Dict[str, Any]] = []
    if not isinstance(arr, list):
        return out
    for i, x in enumerate(arr):
        if isinstance(x, list) and len(x) >= 2:
            try:
                out.append({"i": i, "ts": int(float(x[0])), "v": float(x[1])})
            except Exception:
                pass
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Build static web data for strategy performance + action proxies")
    parser.add_argument("--top-n", type=int, default=50)
    parser.add_argument("--max-fills-per-strategy", type=int, default=1500)
    args = parser.parse_args()

    WEB_DATA.mkdir(parents=True, exist_ok=True)

    rank = pd.read_csv(PROCESSED / "strategy_ranked_extended.csv")
    top = rank.sort_values("extended_rank").head(args.top_n).copy()

    leader_fills_path, leader_fills = _read_latest_leader_fills()
    vault_details_path, vault_details = _read_latest_vault_details()

    items = []
    for _, r in top.iterrows():
        vault = str(r.get("vault_address"))
        leader = str(r.get("leader_detail")) if pd.notna(r.get("leader_detail")) else ""

        # actions
        fills = leader_fills.get(leader, []) if isinstance(leader_fills, dict) else []
        if isinstance(fills, list):
            fills = sorted(fills, key=lambda x: x.get("time", 0))[-args.max_fills_per_strategy :]
        else:
            fills = []

        fill_rows = []
        for f in fills:
            try:
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
            except Exception:
                pass

        # return/account series with real timestamps from vaultDetails
        detail = vault_details.get(vault, {}) if isinstance(vault_details, dict) else {}
        pm = _portfolio_map(detail.get("portfolio"))
        series = {
            "allTime": {
                "pnl": _series_with_ts(pm, "allTime", "pnlHistory"),
                "account": _series_with_ts(pm, "allTime", "accountValueHistory"),
            },
            "month": {
                "pnl": _series_with_ts(pm, "month", "pnlHistory"),
                "account": _series_with_ts(pm, "month", "accountValueHistory"),
            },
            "week": {
                "pnl": _series_with_ts(pm, "week", "pnlHistory"),
                "account": _series_with_ts(pm, "week", "accountValueHistory"),
            },
            "day": {
                "pnl": _series_with_ts(pm, "day", "pnlHistory"),
                "account": _series_with_ts(pm, "day", "accountValueHistory"),
            },
        }

        items.append(
            {
                "name": str(r.get("name", vault)),
                "vault_address": vault,
                "leader": leader,
                "extended_rank": int(r.get("extended_rank", 0)),
                "extended_score": float(r.get("extended_score", 0.0)),
                "composite_score": float(r.get("composite_score", 0.0)) if pd.notna(r.get("composite_score")) else None,
                "apr": float(r.get("apr", 0.0)) if pd.notna(r.get("apr")) else None,
                "tvl": float(r.get("tvl", 0.0)) if pd.notna(r.get("tvl")) else None,
                "pnl_all_time_last": float(r.get("pnl_all_time_last", 0.0)) if pd.notna(r.get("pnl_all_time_last")) else None,
                "pnl_all_time_max_dd": float(r.get("pnl_all_time_max_dd", 0.0)) if pd.notna(r.get("pnl_all_time_max_dd")) else None,
                "pnl_all_time_stability": float(r.get("pnl_all_time_stability", 0.0)) if pd.notna(r.get("pnl_all_time_stability")) else None,
                "av_cagr": float(r.get("av_cagr", 0.0)) if pd.notna(r.get("av_cagr")) else None,
                "av_sharpe": float(r.get("av_sharpe", 0.0)) if pd.notna(r.get("av_sharpe")) else None,
                "series": series,
                "fills": fill_rows,
            }
        )

    payload = {
        "meta": {
            "top_n": args.top_n,
            "max_fills_per_strategy": args.max_fills_per_strategy,
            "schema_version": 2,
            "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "leader_fills_file": leader_fills_path.name if leader_fills_path else None,
            "vault_details_file": vault_details_path.name if vault_details_path else None,
            "note": "fills are leader-level public fills used as action/position proxy; may cover multiple vaults managed by same leader",
        },
        "strategies": items,
    }
    (WEB_DATA / "top_strategies.json").write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"out": str(WEB_DATA / 'top_strategies.json'), "strategies": len(items)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
