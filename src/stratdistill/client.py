import time
import requests
from typing import Any, Dict, List

class HyperliquidClient:
    def __init__(self, timeout: int = 30, retries: int = 3, backoff: float = 1.5):
        self.timeout = timeout
        self.retries = retries
        self.backoff = backoff

    def _request(self, method: str, url: str, **kwargs) -> requests.Response:
        last_err = None
        for i in range(self.retries):
            try:
                r = requests.request(method, url, timeout=self.timeout, **kwargs)
                r.raise_for_status()
                return r
            except Exception as e:
                last_err = e
                time.sleep(self.backoff * (i + 1))
        raise RuntimeError(f"request failed after retries: {url}; err={last_err}")

    def fetch_vaults_stats(self, url: str) -> List[Dict[str, Any]]:
        return self._request("GET", url).json()

    def fetch_vault_details(self, info_url: str, vault_address: str) -> Dict[str, Any]:
        payload = {"type": "vaultDetails", "vaultAddress": vault_address}
        return self._request("POST", info_url, json=payload).json()

    def fetch_user_fills(self, info_url: str, user: str) -> List[Dict[str, Any]]:
        payload = {"type": "userFills", "user": user}
        out = self._request("POST", info_url, json=payload).json()
        return out if isinstance(out, list) else []
