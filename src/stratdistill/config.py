from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA_RAW = ROOT / "data" / "raw"
DATA_PROCESSED = ROOT / "data" / "processed"
REPORTS = ROOT / "reports"
LOGS = ROOT / "logs"

STATS_VAULTS_URL = "https://stats-data.hyperliquid.xyz/Mainnet/vaults"
INFO_URL = "https://api.hyperliquid.xyz/info"

MAX_VAULTS = 300
TOP_N = 50
