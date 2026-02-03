"""Zone management operations."""

from __future__ import annotations

from ..client import CloudflareClient


def list_zones(
    client: CloudflareClient,
    name: str | None = None,
    status: str | None = None,
    per_page: int = 50,
) -> list[dict]:
    """List all zones in the account."""
    params = f"?per_page={per_page}"
    if name:
        params += f"&name={name}"
    if status:
        params += f"&status={status}"

    result = client.request("GET", f"/zones{params}")
    return [
        {
            "id": z["id"],
            "name": z["name"],
            "status": z["status"],
            "plan": z.get("plan", {}).get("name", "N/A"),
            "name_servers": z.get("name_servers", []),
        }
        for z in result.get("result", [])
    ]


def get_zone(client: CloudflareClient, zone_id: str) -> dict:
    """Get detailed information about a specific zone."""
    result = client.request("GET", f"/zones/{zone_id}")
    zone = result.get("result", {})
    return {
        "id": zone.get("id"),
        "name": zone.get("name"),
        "status": zone.get("status"),
        "paused": zone.get("paused"),
        "type": zone.get("type"),
        "plan": zone.get("plan", {}).get("name"),
        "name_servers": zone.get("name_servers", []),
        "original_name_servers": zone.get("original_name_servers", []),
        "created_on": zone.get("created_on"),
        "modified_on": zone.get("modified_on"),
    }


def get_zone_settings(client: CloudflareClient, zone_id: str) -> dict:
    """Get all settings for a zone."""
    result = client.request("GET", f"/zones/{zone_id}/settings")
    return {s["id"]: s.get("value") for s in result.get("result", [])}
