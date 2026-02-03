"""Account and status operations."""

from __future__ import annotations

from ..client import CloudflareClient


def verify_token(client: CloudflareClient) -> dict:
    """Check Cloudflare API connection status and token validity."""
    if not client.api_token:
        return {"status": "error", "message": "No API token configured"}
    result = client.request("GET", "/user/tokens/verify")
    return {
        "status": "connected",
        "token_status": result.get("result", {}).get("status", "unknown"),
        "message": "Cloudflare API token is valid",
    }


def list_accounts(client: CloudflareClient) -> list[dict]:
    """List all accounts the API token has access to."""
    result = client.request("GET", "/accounts")
    return [
        {
            "id": a["id"],
            "name": a["name"],
            "type": a.get("type", "standard"),
        }
        for a in result.get("result", [])
    ]
