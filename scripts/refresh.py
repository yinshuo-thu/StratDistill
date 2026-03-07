#!/usr/bin/env python3
import argparse
import json
from stratdistill.pipeline import run_refresh


def main() -> None:
    parser = argparse.ArgumentParser(description="Refresh Hyperliquid public vault data and ranking outputs.")
    parser.add_argument("--max-vaults", type=int, default=300, help="Maximum candidate vaults to keep in master table")
    parser.add_argument("--top-n", type=int, default=50, help="Top N rows to export in top performers table")
    args = parser.parse_args()

    artifacts = run_refresh(max_vaults=args.max_vaults, top_n=args.top_n)
    print(
        json.dumps(
            {
                "raw_vaults_json": str(artifacts.raw_vaults_json),
                "master_csv": str(artifacts.master_csv),
                "master_parquet": str(artifacts.master_parquet),
                "top_csv": str(artifacts.top_csv),
                "report_md": str(artifacts.report_md),
                "max_vaults": args.max_vaults,
                "top_n": args.top_n,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
