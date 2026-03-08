from __future__ import annotations

import json
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

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


@dataclass
class ProxyArtifacts:
    fills_summary_csv: Path
    strategy_proxy_csv: Path
    report_md: Path
    figures: List[Path]


def run_action_position_proxy(leader_top_k: int = 200) -> ProxyArtifacts:
    rank_path = DATA_PROCESSED / "strategy_ranked_extended.csv"
    if not rank_path.exists():
        raise FileNotFoundError(f"missing file: {rank_path}")

    df = pd.read_csv(rank_path)
    pick = (
        df.dropna(subset=["leader_detail"])
        .sort_values("extended_score", ascending=False)
        .drop_duplicates(subset=["leader_detail"])
        .head(leader_top_k)
        .copy()
    )

    client = HyperliquidClient(timeout=35, retries=3, backoff=1.2)
    leader_rows: List[Dict[str, Any]] = []
    symbol_counter: Dict[str, int] = {}
    raw_fills: Dict[str, Any] = {}

    for _, r in pick.iterrows():
        leader = r["leader_detail"]
        if not isinstance(leader, str) or not leader:
            continue
        try:
            fills = client.fetch_user_fills("https://api.hyperliquid.xyz/info", leader)
        except Exception as e:
            leader_rows.append({"leader_detail": leader, "fill_count": 0, "fetch_error": str(e)})
            time.sleep(0.8)
            continue

        raw_fills[leader] = fills

        if not fills:
            leader_rows.append({"leader_detail": leader, "fill_count": 0})
            time.sleep(0.2)
            continue

        times = np.array([int(x.get("time", 0)) for x in fills if x.get("time") is not None], dtype=np.int64)
        days = np.unique((times // 1000) // 86400) if len(times) else np.array([])
        coins = [str(x.get("coin")) for x in fills if x.get("coin") is not None]
        dirs = [str(x.get("dir", "")) for x in fills]
        sides = [str(x.get("side", "")) for x in fills]
        closed_pnls = np.array([_safe_float(x.get("closedPnl"), 0.0) for x in fills], dtype=float)
        sz = np.array([abs(_safe_float(x.get("sz"), 0.0)) for x in fills], dtype=float)

        for c in coins:
            symbol_counter[c] = symbol_counter.get(c, 0) + 1

        buy_cnt = sum(1 for d in dirs if "Buy" in d or "Long" in d)
        sell_cnt = sum(1 for d in dirs if "Sell" in d or "Short" in d)
        close_cnt = sum(1 for d in dirs if "Close" in d)

        leader_rows.append(
            {
                "leader_detail": leader,
                "fill_count": int(len(fills)),
                "active_day_count": int(len(days)),
                "active_span_days": float((days.max() - days.min() + 1) if len(days) else 0),
                "symbol_count": int(len(set(coins))),
                "buy_like_count": int(buy_cnt),
                "sell_like_count": int(sell_cnt),
                "close_count": int(close_cnt),
                "buy_sell_ratio": float((buy_cnt + 1) / (sell_cnt + 1)),
                "avg_abs_fill_size": float(np.mean(sz)) if len(sz) else np.nan,
                "sum_closed_pnl": float(np.sum(closed_pnls)) if len(closed_pnls) else np.nan,
                "positive_close_ratio": float(np.mean(closed_pnls > 0)) if len(closed_pnls) else np.nan,
                "first_fill_ts": datetime.fromtimestamp(times.min() / 1000, tz=timezone.utc).isoformat() if len(times) else None,
                "last_fill_ts": datetime.fromtimestamp(times.max() / 1000, tz=timezone.utc).isoformat() if len(times) else None,
            }
        )
        time.sleep(0.2)

    # raw dump
    DATA_RAW.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    raw_dir = DATA_RAW / "leader_fills"
    raw_dir.mkdir(parents=True, exist_ok=True)
    raw_json = raw_dir / f"leader_fills_top{leader_top_k}_{stamp}.json"
    raw_json.write_text(json.dumps(raw_fills, ensure_ascii=False), encoding="utf-8")

    fills_summary = pd.DataFrame(leader_rows)
    fills_summary_csv = DATA_PROCESSED / "leader_fills_summary.csv"
    fills_summary.to_csv(fills_summary_csv, index=False)

    # merge to strategy-level proxy table
    merged = df.merge(fills_summary, on="leader_detail", how="left")
    merged["action_intensity"] = np.log1p(merged["fill_count"].fillna(0)) * np.log1p(merged["symbol_count"].fillna(0))
    merged["position_turnover_proxy"] = np.log1p(merged["avg_abs_fill_size"].fillna(0)) * np.log1p(merged["fill_count"].fillna(0))
    merged["execution_consistency_proxy"] = merged["active_day_count"].fillna(0) / merged["active_span_days"].replace(0, np.nan)

    strategy_proxy_csv = DATA_PROCESSED / "strategy_action_position_proxy.csv"
    merged.to_csv(strategy_proxy_csv, index=False)

    # figures
    fig_dir = REPORTS / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)
    figures: List[Path] = []

    # fill count distribution
    plt.figure(figsize=(10, 5))
    vals = fills_summary["fill_count"].fillna(0)
    plt.hist(np.log1p(vals), bins=35, color="#4e79a7", alpha=0.85)
    plt.title("Leader Fill Count Distribution (log1p)")
    plt.xlabel("log1p(fill_count)")
    plt.ylabel("Count")
    plt.tight_layout()
    f1 = fig_dir / "proxy_fill_count_distribution.png"
    plt.savefig(f1, dpi=180)
    plt.close()
    figures.append(f1)

    # action intensity vs score
    p = merged.dropna(subset=["action_intensity", "extended_score"]).copy()
    plt.figure(figsize=(9, 6))
    plt.scatter(p["action_intensity"], p["extended_score"], alpha=0.55)
    plt.title("Action Intensity Proxy vs Extended Score")
    plt.xlabel("Action Intensity Proxy")
    plt.ylabel("Extended Score")
    plt.tight_layout()
    f2 = fig_dir / "proxy_action_intensity_vs_score.png"
    plt.savefig(f2, dpi=180)
    plt.close()
    figures.append(f2)

    # top symbols
    sym = sorted(symbol_counter.items(), key=lambda x: x[1], reverse=True)[:20]
    if sym:
        plt.figure(figsize=(11, 6))
        x = [k for k, _ in sym]
        y = [v for _, v in sym]
        plt.bar(x, y, color="#59a14f")
        plt.title("Top Symbols by Public Fill Frequency (sampled leaders)")
        plt.ylabel("Fill Count")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        f3 = fig_dir / "proxy_top_symbols_fill_frequency.png"
        plt.savefig(f3, dpi=180)
        plt.close()
        figures.append(f3)

    report_md = REPORTS / "proxy_report.md"
    lines = [
        "# Action / Position Proxy Report",
        "",
        f"- sampled leaders: {len(fills_summary)}",
        f"- leader_top_k param: {leader_top_k}",
        "",
        "## Proxy Definitions",
        "- action_intensity = log1p(fill_count) * log1p(symbol_count)",
        "- position_turnover_proxy = log1p(avg_abs_fill_size) * log1p(fill_count)",
        "- execution_consistency_proxy = active_day_count / active_span_days",
        "",
        "## Coverage",
        f"- leaders with non-empty fills: {int((fills_summary['fill_count']>0).sum()) if len(fills_summary) else 0}",
        f"- total sampled fills: {int(fills_summary['fill_count'].fillna(0).sum()) if len(fills_summary) else 0}",
        "",
        "## Notes",
        "- This is proxy-level analysis from public fills, not full private position ledger.",
        "- API-side pagination/retention limits may cap historical depth for some leaders.",
    ]
    report_md.write_text("\n".join(lines), encoding="utf-8")

    return ProxyArtifacts(
        fills_summary_csv=fills_summary_csv,
        strategy_proxy_csv=strategy_proxy_csv,
        report_md=report_md,
        figures=figures,
    )
