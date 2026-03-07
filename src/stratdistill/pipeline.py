from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any

import numpy as np
import pandas as pd

from .client import HyperliquidClient
from .config import DATA_RAW, DATA_PROCESSED, REPORTS, STATS_VAULTS_URL, MAX_VAULTS, TOP_N


@dataclass
class RunArtifacts:
    raw_vaults_json: Path
    master_csv: Path
    master_parquet: Path
    top_csv: Path
    report_md: Path


def ensure_dirs() -> None:
    for p in [DATA_RAW, DATA_PROCESSED, REPORTS]:
        p.mkdir(parents=True, exist_ok=True)


def _safe_float(x, default=np.nan):
    try:
        return float(x)
    except Exception:
        return default


def _to_iso_utc(ms: Any) -> str | None:
    try:
        msf = float(ms)
        return datetime.fromtimestamp(msf / 1000.0, tz=timezone.utc).isoformat()
    except Exception:
        return None


def _extract_pnl_features(pnls: List[Any]) -> Dict[str, float]:
    # pnls format typically: [["day", [...]], ["week", [...]], ["month", [...]], ["allTime", [...]]]
    label_map = {"day": "day", "week": "week", "month": "month", "allTime": "all_time"}
    out = {
        "pnl_day_last": np.nan,
        "pnl_week_last": np.nan,
        "pnl_month_last": np.nan,
        "pnl_all_time_last": np.nan,
        "pnl_all_time_max_dd": np.nan,
        "pnl_all_time_stability": np.nan,
        "pnl_obs_count": 0,
    }
    for item in pnls or []:
        if not isinstance(item, list) or len(item) != 2:
            continue
        k, arr = item
        key = label_map.get(k, str(k))
        if not isinstance(arr, list) or len(arr) == 0:
            continue
        vals = np.array([_safe_float(v, 0.0) for v in arr], dtype=float)
        out["pnl_obs_count"] += len(vals)
        out[f"pnl_{key}_last"] = float(vals[-1])
        if key == "all_time":
            running_max = np.maximum.accumulate(vals)
            dd = vals - running_max
            out["pnl_all_time_max_dd"] = float(dd.min())
            diffs = np.diff(vals)
            if len(diffs) > 1:
                out["pnl_all_time_stability"] = float(np.std(diffs))
    return out


def _normalize_rank(s: pd.Series, asc: bool) -> pd.Series:
    return s.rank(method="average", ascending=asc, pct=True).fillna(0.0)


def build_master(vaults: List[Dict[str, Any]]) -> pd.DataFrame:
    rows = []
    for v in vaults:
        summary = v.get("summary", {})
        row = {
            "name": summary.get("name"),
            "vault_address": summary.get("vaultAddress"),
            "leader": summary.get("leader"),
            "tvl": _safe_float(summary.get("tvl")),
            "apr": _safe_float(v.get("apr")),
            "followers": _safe_float(summary.get("followers")),
            "created_at": _to_iso_utc(summary.get("createTimeMillis")) or summary.get("createdAt"),
            "is_closed": bool(summary.get("isClosed", False)),
            "raw_has_description": bool(summary.get("description")),
        }
        row.update(_extract_pnl_features(v.get("pnls", [])))
        rows.append(row)

    df = pd.DataFrame(rows)

    # Base factors (public-data-first): if a factor is mostly missing, dynamic weighting handles it.
    factor_scores = {
        "apr": _normalize_rank(df["apr"], asc=False),
        "tvl": _normalize_rank(df["tvl"], asc=False),
        "followers": _normalize_rank(df["followers"], asc=False),
        "pnl_all": _normalize_rank(df["pnl_all_time_last"], asc=False),
        "drawdown": _normalize_rank(df["pnl_all_time_max_dd"].abs(), asc=True),
        "stability": _normalize_rank(df["pnl_all_time_stability"], asc=True),
        "data_quality": _normalize_rank(df["pnl_obs_count"], asc=False),
    }
    for k, v in factor_scores.items():
        df[f"score_{k}"] = v

    weights = {
        "apr": 0.20,
        "tvl": 0.18,
        "followers": 0.12,
        "pnl_all": 0.20,
        "drawdown": 0.12,
        "stability": 0.08,
        "data_quality": 0.10,
    }

    # Dynamic renormalization: if column effectively missing, skip and redistribute.
    valid_weight = 0.0
    for k, w in weights.items():
        col = df[f"score_{k}"]
        if float(col.sum()) > 0:
            valid_weight += w
    if valid_weight <= 0:
        valid_weight = 1.0

    composite = np.zeros(len(df), dtype=float)
    for k, w in weights.items():
        col = df[f"score_{k}"]
        if float(col.sum()) <= 0:
            continue
        composite += (w / valid_weight) * col.to_numpy(dtype=float)

    df["closed_penalty"] = np.where(df["is_closed"], 0.10, 0.0)
    df["composite_score"] = composite - df["closed_penalty"].to_numpy(dtype=float)
    df["rank"] = df["composite_score"].rank(ascending=False, method="first").astype(int)
    return df.sort_values("rank")


def write_report(df: pd.DataFrame, report_path: Path, assumptions: List[str], source_meta: Dict[str, Any]) -> None:
    ts = datetime.now(timezone.utc).isoformat()
    top = df.head(20)
    lines = [
        "# Hyperliquid Strategy Distillation Report",
        "",
        f"Generated at (UTC): {ts}",
        "",
        "## Data Sources",
        "- Official Info API: `POST https://api.hyperliquid.xyz/info`",
        "- Public stats dataset used for discovery: `GET https://stats-data.hyperliquid.xyz/Mainnet/vaults`",
        "",
        "## Source Validation",
        f"- info type=vaultSummaries response size: {source_meta.get('vault_summaries_size')}",
        f"- stats vault records fetched: {source_meta.get('stats_records')}",
        "",
        "## Known Limits",
        "- `vaultSummaries` currently returned empty array in test; discovery currently relies on public stats endpoint.",
        "- Public dataset does not consistently expose all follower/flow dimensions for each vault.",
        "- PnL/account value granularity depends on available `pnls` arrays; no private trade-level fields are assumed.",
        "",
        "## Scoring Assumptions",
    ]
    lines.extend([f"- {a}" for a in assumptions])
    lines.extend([
        "",
        "## Top 20 by Composite Score",
        "",
        "| Rank | Name | Vault | APR | TVL | PnL(all time) | Max Drawdown | Stability(std ΔPnL) | Score |",
        "|---:|---|---|---:|---:|---:|---:|---:|---:|",
    ])
    for _, r in top.iterrows():
        lines.append(
            f"| {int(r['rank'])} | {r['name']} | `{r['vault_address']}` | {r['apr']:.6f} | {r['tvl']:.2f} | {r['pnl_all_time_last']:.2f} | {r['pnl_all_time_max_dd']:.2f} | {r['pnl_all_time_stability']:.4f} | {r['composite_score']:.4f} |"
        )
    report_path.write_text("\n".join(lines), encoding="utf-8")


def run_refresh(max_vaults: int = MAX_VAULTS, top_n: int = TOP_N) -> RunArtifacts:
    ensure_dirs()
    client = HyperliquidClient()
    now = datetime.now(timezone.utc)
    stamp = now.strftime("%Y%m%dT%H%M%SZ")

    # Validate official endpoint behavior
    try:
        import requests
        info_resp = requests.post("https://api.hyperliquid.xyz/info", json={"type": "vaultSummaries"}, timeout=20)
        info_resp.raise_for_status()
        info_json = info_resp.json()
        vault_summaries_size = len(info_json) if isinstance(info_json, list) else -1
    except Exception:
        vault_summaries_size = -1

    vaults = client.fetch_vaults_stats(STATS_VAULTS_URL)
    raw_path = DATA_RAW / f"vaults_stats_{stamp}.json"
    raw_path.write_text(json.dumps(vaults, ensure_ascii=False, indent=2), encoding="utf-8")

    df_full = build_master(vaults)

    # Candidate filtering (public-signal first)
    candidate = df_full[(~df_full["is_closed"]) & (df_full["pnl_obs_count"] >= 20)].copy()
    candidate = candidate[candidate["tvl"].fillna(0) > 1000].copy()
    candidate = candidate[candidate["pnl_all_time_last"].fillna(0) > 0].copy()
    candidate = candidate.sort_values(["composite_score", "tvl"], ascending=False)

    df = candidate.head(max_vaults).copy()
    df["rank"] = df["composite_score"].rank(ascending=False, method="first").astype(int)
    df = df.sort_values("rank")
    df["snapshot_ts_utc"] = now.isoformat()

    master_csv = DATA_PROCESSED / "vault_master.csv"
    master_parquet = DATA_PROCESSED / "vault_master.parquet"
    top_csv = DATA_PROCESSED / "vault_top_performers.csv"
    report_md = REPORTS / "latest_report.md"

    df.to_csv(master_csv, index=False)
    try:
        df.to_parquet(master_parquet, index=False)
    except Exception:
        pass
    df.head(top_n).to_csv(top_csv, index=False)

    assumptions = [
        "Composite score uses multi-factor ranking (apr/tvl/followers/pnl/drawdown/stability/data quality).",
        "If some factors are mostly missing, weights are dynamically renormalized over available factors.",
        "Closed vaults receive a fixed score penalty of 0.10.",
        "Discovery uses public stats endpoint while official vaultSummaries remains empty in observed tests.",
    ]
    write_report(
        df,
        report_md,
        assumptions,
        source_meta={"vault_summaries_size": vault_summaries_size, "stats_records": len(vaults)},
    )

    # Per-vault series extraction from available pnls arrays
    ts_dir = DATA_PROCESSED / "timeseries"
    ts_dir.mkdir(parents=True, exist_ok=True)
    raw_map = {x.get("summary", {}).get("vaultAddress"): x for x in vaults}
    for addr in df["vault_address"].dropna().head(top_n):
        obj = raw_map.get(addr, {})
        pnls = obj.get("pnls", [])
        rows = []
        for item in pnls:
            if not isinstance(item, list) or len(item) != 2:
                continue
            label, arr = item
            for idx, val in enumerate(arr or []):
                rows.append({"series": label, "idx": idx, "value": _safe_float(val)})
        if rows:
            pd.DataFrame(rows).to_csv(ts_dir / f"{addr}.csv", index=False)

    return RunArtifacts(raw_path, master_csv, master_parquet, top_csv, report_md)
