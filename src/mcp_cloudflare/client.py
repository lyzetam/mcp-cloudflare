"""Cloudflare API client with httpx."""

from __future__ import annotations

import httpx

from mcp_cloudflare.config import get_settings


class CloudflareClient:
    """Manages httpx client for Cloudflare API v4.

    Reads credentials from environment variables or .env file via Pydantic Settings:
    - CLOUDFLARE_API_TOKEN
    - CLOUDFLARE_ACCOUNT_ID (optional, for tunnel operations)
    """

    BASE_URL = "https://api.cloudflare.com/client/v4"

    def __init__(
        self,
        api_token: str | None = None,
        account_id: str | None = None,
    ) -> None:
        settings = get_settings()
        self.api_token = (api_token or settings.api_token).strip()
        self.account_id = (account_id or settings.account_id).strip()

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
        }

    def request(
        self,
        method: str,
        endpoint: str,
        data: dict | None = None,
    ) -> dict:
        """Make a synchronous request to the Cloudflare API."""
        url = f"{self.BASE_URL}{endpoint}"
        with httpx.Client(timeout=30.0) as http:
            response = http.request(method, url, headers=self._headers(), json=data)
            response.raise_for_status()
            return response.json()
