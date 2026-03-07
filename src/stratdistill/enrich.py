from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from .client import HyperliquidClient
from .config import DATA_RAW, DATA_PROCESSED, REPORTS


def _safe_float(x, default=np.nan):
    try:
        return float(x)
    except Exception:
        return default


def _portfolio_to_map(portfolio: Any) -> Dict[str, Dict[str, Any]]:
    out: Dict[str, Dict[str, Any]] = {}
    if not isinstance(portfolio, list):
        return out
    for item in portfolio:
        if not isinstance(item, list) or len(item) != 2:
            continue
        label, payload = item
        if isinstance(payload, dict):
            out[str(label)] = payload
    return out


def _extract_portfolio_stats(pm: Dict[str, Dict[str, Any]], label: str) -> Tuple[float, int]:
    p = pm.get(label, {})
    hist = p.get("accountValueHistory", [])
    if not isinstance(hist, list) or len(hist) == 0:
        return (np.nan, 0)
    last = hist[-1]
    if isinstance(last, list) and len(last) >= 2:
        return (_safe_float(last[1]), len(hist))
    return (np.nan, len(hist))


@dataclass
class EnrichArtifacts:
    details_csv: Path
    ranking_csv: Path
    fig_dir: Path
    figures: List[Path]


def run_enrichment(top_k: int = 200) -> EnrichArtifacts:
    DATA_RAW.mkdir(parents=True, exist_ok=True)
    DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
    (REPORTS / "figures").mkdir(parents=True, exist_ok=True)

    master_path = DATA_PROCESSED / "vault_master.csv"
    if not master_path.exists():
        raise FileNotFoundError(f"missing master table: {master_path}")
    master = pd.read_csv(master_path)
    pick = master.sort_values("composite_score", ascending=False).head(top_k).copy()

    client = HyperliquidClient(timeout=30, retries=4, backoff=1.0)
    details_rows: List[Dict[str, Any]] = []
    raw_details: Dict[str, Any] = {}

    for _, r in pick.iterrows():
        addr = r["vault_address"]
        if not isinstance(addr, str) or not addr:
            continue
        try:
            d = client.fetch_vault_details("https://api.hyperliquid.xyz/info", addr)
        except Exception as e:
            details_rows.append({"vault_address": addr, "details_fetch_error": str(e)})
            continue

        raw_details[addr] = d
        pm = _portfolio_to_map(d.get("portfolio"))
        day_v, day_n = _extract_portfolio_stats(pm, "day")
        week_v, week_n = _extract_portfolio_stats(pm, "week")
        month_v, month_n = _extract_portfolio_stats(pm, "month")
        all_v, all_n = _extract_portfolio_stats(pm, "allTime")

        details_rows.append(
            {
                "vault_address": d.get("vaultAddress", addr),
                "name_detail": d.get("name"),
                "leader_detail": d.get("leader"),
                "apr_detail": _safe_float(d.get("apr")),
                "followers_detail": _safe_float(d.get("followers")),
                "leader_fraction": _safe_float(d.get("leaderFraction")),
                "leader_commission": _safe_float(d.get("leaderCommission")),
                "max_distributable": _safe_float(d.get("maxDistributable")),
                "max_withdrawable": _safe_float(d.get("maxWithdrawable")),
                "allow_deposits": bool(d.get("allowDeposits", False)),
                "always_close_on_withdraw": bool(d.get("alwaysCloseOnWithdraw", False)),
                "is_closed_detail": bool(d.get("isClosed", False)),
                "description_len": len((d.get("description") or "").strip()),
                "av_day_last": day_v,
                "av_day_obs": day_n,
                "av_week_last": week_v,
                "av_week_obs": week_n,
                "av_month_last": month_v,
                "av_month_obs": month_n,
                "av_all_time_last": all_v,
                "av_all_time_obs": all_n,
            }
        )

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    raw_dir = DATA_RAW / "vault_details"
    raw_dir.mkdir(parents=True, exist_ok=True)
    raw_json = raw_dir / f"details_top{top_k}_{stamp}.json"
    raw_json.write_text(json.dumps(raw_details, ensure_ascii=False, indent=2), encoding="utf-8")

    details = pd.DataFrame(details_rows)
    details_csv = DATA_PROCESSED / "strategy_registry.csv"
    details.to_csv(details_csv, index=False)

    merged = master.merge(details, on="vault_address", how="left")
    merged["withdrawable_ratio"] = merged["max_withdrawable"] / merged["max_distributable"]

    # extended ranking adds details quality terms
    def nrm(s, asc=False):
        return s.rank(method="average", ascending=asc, pct=True).fillna(0.0)

    merged["score_commission"] = nrm(merged["leader_commission"], asc=True)
    merged["score_withdrawable"] = nrm(merged["withdrawable_ratio"], asc=False)
    merged["score_av_depth"] = nrm(merged["av_all_time_obs"], asc=False)

    merged["extended_score"] = (
        0.75 * merged["composite_score"].fillna(0.0)
        + 0.08 * merged["score_commission"]
        + 0.07 * merged["score_withdrawable"]
        + 0.10 * merged["score_av_depth"]
    )
    merged["extended_rank"] = merged["extended_score"].rank(ascending=False, method="first").astype(int)
    merged = merged.sort_values("extended_rank")

    ranking_csv = DATA_PROCESSED / "strategy_ranked_extended.csv"
    merged.to_csv(ranking_csv, index=False)

    fig_dir = REPORTS / "figures"
    figures: List[Path] = []

    top20 = merged.head(20).copy()
    plt.figure(figsize=(12, 7))
    plt.barh(top20["name"].fillna(top20["vault_address"]), top20["extended_score"], color="#4e79a7")
    plt.gca().invert_yaxis()
    plt.title("Top 20 Strategies by Extended Score")
    plt.xlabel("Extended Score")
    plt.tight_layout()
    f1 = fig_dir / "top20_extended_score.png"
    plt.savefig(f1, dpi=180)
    plt.close()
    figures.append(f1)

    plot_df = merged.dropna(subset=["apr", "pnl_all_time_max_dd", "tvl"]).head(300)
    plt.figure(figsize=(10, 7))
    sc = plt.scatter(plot_df["apr"], plot_df["pnl_all_time_max_dd"], c=np.log1p(plot_df["tvl"].clip(lower=0.0)), cmap="viridis", alpha=0.7)
    plt.colorbar(sc, label="log(1+TVL)")
    plt.title("APR vs Max Drawdown (colored by TVL)")
    plt.xlabel("APR")
    plt.ylabel("Max Drawdown")
    plt.tight_layout()
    f2 = fig_dir / "apr_vs_drawdown_tvl.png"
    plt.savefig(f2, dpi=180)
    plt.close()
    figures.append(f2)

    plt.figure(figsize=(10, 6))
    vals = merged["tvl"].dropna()
    vals = vals[vals > 0]
    plt.hist(np.log10(vals), bins=40, color="#f28e2b", alpha=0.85)
    plt.title("TVL Distribution (log10 scale)")
    plt.xlabel("log10(TVL)")
    plt.ylabel("Count")
    plt.tight_layout()
    f3 = fig_dir / "tvl_distribution_log10.png"
    plt.savefig(f3, dpi=180)
    plt.close()
    figures.append(f3)

    miss_cols = [
        "apr",
        "tvl",
        "pnl_all_time_last",
        "pnl_all_time_max_dd",
        "followers_detail",
        "leader_commission",
        "av_all_time_obs",
    ]
    miss = merged[miss_cols].isna().mean().sort_values(ascending=False)
    plt.figure(figsize=(10, 5))
    plt.bar(miss.index, miss.values, color="#e15759")
    plt.title("Missingness Ratio by Key Feature")
    plt.ylabel("Missing Ratio")
    plt.xticks(rotation=25, ha="right")
    plt.tight_layout()
    f4 = fig_dir / "feature_missingness_ratio.png"
    plt.savefig(f4, dpi=180)
    plt.close()
    figures.append(f4)

    return EnrichArtifacts(details_csv=details_csv, ranking_csv=ranking_csv, fig_dir=fig_dir, figures=figures)
