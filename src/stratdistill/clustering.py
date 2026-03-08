from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from .config import DATA_PROCESSED, REPORTS


@dataclass
class ClusterArtifacts:
    cluster_csv: Path
    summary_csv: Path
    report_md: Path
    figures: List[Path]


def _zscore(df: pd.DataFrame) -> pd.DataFrame:
    std = df.std(ddof=0).replace(0, 1.0)
    return (df - df.mean()) / std


def _kmeans_np(x: np.ndarray, k: int = 4, n_iter: int = 80, seed: int = 42):
    rng = np.random.default_rng(seed)
    idx = rng.choice(len(x), size=k, replace=False)
    centers = x[idx].copy()

    for _ in range(n_iter):
        d2 = ((x[:, None, :] - centers[None, :, :]) ** 2).sum(axis=2)
        labels = d2.argmin(axis=1)
        new_centers = []
        for j in range(k):
            pts = x[labels == j]
            if len(pts) == 0:
                new_centers.append(centers[j])
            else:
                new_centers.append(pts.mean(axis=0))
        new_centers = np.vstack(new_centers)
        if np.allclose(new_centers, centers):
            break
        centers = new_centers

    d2 = ((x[:, None, :] - centers[None, :, :]) ** 2).sum(axis=2)
    labels = d2.argmin(axis=1)
    inertia = float(np.sum((x - centers[labels]) ** 2))
    return labels, centers, inertia


def _cluster_name(row: pd.Series) -> str:
    # rule-based semantic label from centroid-like stats
    high_tvl = row["tvl_median"] > 5e4
    high_dd = abs(row["pnl_all_time_max_dd_median"]) > 5e4
    stable = row["pnl_all_time_stability_median"] < 2e4
    high_score = row["extended_score_median"] > 0.48

    if high_tvl and high_score and stable:
        return "Core Bluechip"
    if high_dd and not stable:
        return "Aggressive Swing"
    if stable and not high_dd:
        return "Steady Grinder"
    if not high_tvl and high_score:
        return "Niche Alpha"
    return "Mixed Profile"


def run_clustering(k: int = 5) -> ClusterArtifacts:
    df_path = DATA_PROCESSED / "strategy_ranked_extended.csv"
    if not df_path.exists():
        raise FileNotFoundError(f"missing file: {df_path}")

    df = pd.read_csv(df_path)
    base_cols = [
        "apr",
        "tvl",
        "pnl_all_time_last",
        "pnl_all_time_max_dd",
        "pnl_all_time_stability",
        "extended_score",
        "av_all_time_obs",
        "leader_commission",
    ]
    xdf = df[base_cols].copy()
    xdf = xdf.replace([np.inf, -np.inf], np.nan)
    xdf["tvl"] = np.log1p(xdf["tvl"].clip(lower=0))
    xdf["pnl_all_time_last"] = np.log1p(xdf["pnl_all_time_last"].clip(lower=0))
    xdf["pnl_all_time_max_dd"] = np.log1p(xdf["pnl_all_time_max_dd"].abs())
    xdf = xdf.fillna(xdf.median(numeric_only=True))
    zx = _zscore(xdf)

    labels, centers, inertia = _kmeans_np(zx.to_numpy(dtype=float), k=k)
    df["cluster_id"] = labels

    cluster = (
        df.groupby("cluster_id", dropna=False)
        .agg(
            n=("vault_address", "count"),
            extended_score_median=("extended_score", "median"),
            apr_median=("apr", "median"),
            tvl_median=("tvl", "median"),
            pnl_all_time_last_median=("pnl_all_time_last", "median"),
            pnl_all_time_max_dd_median=("pnl_all_time_max_dd", "median"),
            pnl_all_time_stability_median=("pnl_all_time_stability", "median"),
            av_all_time_obs_median=("av_all_time_obs", "median"),
            leader_commission_median=("leader_commission", "median"),
        )
        .reset_index()
        .sort_values("extended_score_median", ascending=False)
    )
    cluster["cluster_theme"] = cluster.apply(_cluster_name, axis=1)
    cluster["cluster_name"] = cluster.apply(lambda r: f"{r['cluster_theme']} C{int(r['cluster_id'])}", axis=1)

    name_map: Dict[int, str] = dict(zip(cluster["cluster_id"], cluster["cluster_name"]))
    df["cluster_name"] = df["cluster_id"].map(name_map)

    cluster_csv = DATA_PROCESSED / "strategy_cluster_assignments.csv"
    summary_csv = DATA_PROCESSED / "strategy_cluster_summary.csv"
    df.to_csv(cluster_csv, index=False)
    cluster.to_csv(summary_csv, index=False)

    fig_dir = REPORTS / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)
    figs: List[Path] = []

    # scatter 1: APR vs Drawdown by cluster
    plt.figure(figsize=(10, 7))
    for cid, g in df.groupby("cluster_id"):
        plt.scatter(g["apr"], g["pnl_all_time_max_dd"], alpha=0.6, label=f"C{int(cid)}")
    plt.axhline(0, color="gray", lw=1)
    plt.title("Cluster Map: APR vs Max Drawdown")
    plt.xlabel("APR")
    plt.ylabel("Max Drawdown")
    plt.legend()
    plt.tight_layout()
    f1 = fig_dir / "cluster_apr_drawdown.png"
    plt.savefig(f1, dpi=180)
    plt.close()
    figs.append(f1)

    # bar: cluster size
    plt.figure(figsize=(9, 5))
    c = cluster.sort_values("n", ascending=False)
    plt.bar(c["cluster_name"], c["n"], color="#59a14f")
    plt.title("Cluster Size Distribution")
    plt.ylabel("Strategy Count")
    plt.xticks(rotation=20, ha="right")
    plt.tight_layout()
    f2 = fig_dir / "cluster_size_distribution.png"
    plt.savefig(f2, dpi=180)
    plt.close()
    figs.append(f2)

    # bar: median extended score by cluster
    plt.figure(figsize=(9, 5))
    c2 = cluster.sort_values("extended_score_median", ascending=False)
    plt.bar(c2["cluster_name"], c2["extended_score_median"], color="#edc948")
    plt.title("Median Extended Score by Cluster")
    plt.ylabel("Median Extended Score")
    plt.xticks(rotation=20, ha="right")
    plt.tight_layout()
    f3 = fig_dir / "cluster_median_score.png"
    plt.savefig(f3, dpi=180)
    plt.close()
    figs.append(f3)

    report_md = REPORTS / "cluster_report.md"
    lines = [
        "# Strategy Clustering Report",
        "",
        f"- KMeans (numpy) with k={k}",
        f"- Inertia: {inertia:.4f}",
        "",
        "## Cluster Summary",
        "",
        "| Cluster | Name | Count | Median Score | Median APR | Median TVL | Median Drawdown |",
        "|---:|---|---:|---:|---:|---:|---:|",
    ]
    for _, r in cluster.iterrows():
        lines.append(
            f"| {int(r['cluster_id'])} | {r['cluster_name']} | {int(r['n'])} | {r['extended_score_median']:.4f} | {r['apr_median']:.6f} | {r['tvl_median']:.2f} | {r['pnl_all_time_max_dd_median']:.2f} |"
        )

    lines.extend([
        "",
        "## Notes",
        "- Cluster names are semantic labels derived from centroid-like median traits.",
        "- Use this as cohort analysis (not deterministic strategy taxonomy).",
    ])
    report_md.write_text("\n".join(lines), encoding="utf-8")

    return ClusterArtifacts(cluster_csv=cluster_csv, summary_csv=summary_csv, report_md=report_md, figures=figs)
