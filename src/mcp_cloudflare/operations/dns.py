"""DNS record management operations."""

from __future__ import annotations

from ..client import CloudflareClient


def list_records(
    client: CloudflareClient,
    zone_id: str,
    record_type: str | None = None,
    name: str | None = None,
    per_page: int = 100,
) -> list[dict]:
    """List DNS records for a zone."""
    params = f"?per_page={per_page}"
    if record_type:
        params += f"&type={record_type}"
    if name:
        params += f"&name={name}"

    result = client.request("GET", f"/zones/{zone_id}/dns_records{params}")
    return [
        {
            "id": r["id"],
            "type": r["type"],
            "name": r["name"],
            "content": r["content"],
            "ttl": r["ttl"],
            "proxied": r.get("proxied", False),
            "priority": r.get("priority"),
        }
        for r in result.get("result", [])
    ]


def create_record(
    client: CloudflareClient,
    zone_id: str,
    record_type: str,
    name: str,
    content: str,
    ttl: int = 1,
    proxied: bool = False,
    priority: int | None = None,
) -> dict:
    """Create a new DNS record."""
    data: dict = {
        "type": record_type.upper(),
        "name": name,
        "content": content,
        "ttl": ttl,
        "proxied": proxied,
    }
    if priority is not None:
        data["priority"] = priority

    result = client.request("POST", f"/zones/{zone_id}/dns_records", data)
    record = result.get("result", {})
    return {
        "status": "created",
        "id": record.get("id"),
        "type": record.get("type"),
        "name": record.get("name"),
        "content": record.get("content"),
    }


def update_record(
    client: CloudflareClient,
    zone_id: str,
    record_id: str,
    record_type: str,
    name: str,
    content: str,
    ttl: int = 1,
    proxied: bool = False,
    priority: int | None = None,
) -> dict:
    """Update an existing DNS record."""
    data: dict = {
        "type": record_type.upper(),
        "name": name,
        "content": content,
        "ttl": ttl,
        "proxied": proxied,
    }
    if priority is not None:
        data["priority"] = priority

    result = client.request("PUT", f"/zones/{zone_id}/dns_records/{record_id}", data)
    record = result.get("result", {})
    return {
        "status": "updated",
        "id": record.get("id"),
        "type": record.get("type"),
        "name": record.get("name"),
        "content": record.get("content"),
    }


def delete_record(
    client: CloudflareClient,
    zone_id: str,
    record_id: str,
) -> dict:
    """Delete a DNS record."""
    result = client.request("DELETE", f"/zones/{zone_id}/dns_records/{record_id}")
    return {"status": "deleted", "id": result.get("result", {}).get("id")}
