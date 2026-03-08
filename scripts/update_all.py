#!/usr/bin/env python3
import argparse
import json

from stratdistill.pipeline import run_refresh
from stratdistill.enrich import run_enrichment
from stratdistill.clustering import run_clustering
from stratdistill.proxy import run_action_position_proxy


def main() -> None:
    parser = argparse.ArgumentParser(description="Run full StratDistill pipeline: refresh + enrichment + visualization")
    parser.add_argument("--max-vaults", type=int, default=300)
    parser.add_argument("--top-n", type=int, default=50)
    parser.add_argument("--details-top-k", type=int, default=200)
    parser.add_argument("--cluster-k", type=int, default=5)
    parser.add_argument("--leader-top-k", type=int, default=200)
    args = parser.parse_args()

    a = run_refresh(max_vaults=args.max_vaults, top_n=args.top_n)
    b = run_enrichment(top_k=args.details_top_k)
    c = run_clustering(k=args.cluster_k)
    d = run_action_position_proxy(leader_top_k=args.leader_top_k)

    print(
        json.dumps(
            {
                "refresh": {
                    "raw_vaults_json": str(a.raw_vaults_json),
                    "master_csv": str(a.master_csv),
                    "top_csv": str(a.top_csv),
                    "report_md": str(a.report_md),
                },
                "enrich": {
                    "details_csv": str(b.details_csv),
                    "ranking_csv": str(b.ranking_csv),
                    "fig_dir": str(b.fig_dir),
                    "figures": [str(x) for x in b.figures],
                },
                "cluster": {
                    "cluster_csv": str(c.cluster_csv),
                    "summary_csv": str(c.summary_csv),
                    "report_md": str(c.report_md),
                    "figures": [str(x) for x in c.figures],
                },
                "proxy": {
                    "fills_summary_csv": str(d.fills_summary_csv),
                    "strategy_proxy_csv": str(d.strategy_proxy_csv),
                    "report_md": str(d.report_md),
                    "figures": [str(x) for x in d.figures],
                },
                "params": vars(args),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
