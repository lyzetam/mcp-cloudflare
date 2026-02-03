"""Cloudflare Tunnel management operations."""

from __future__ import annotations

from ..client import CloudflareClient


def list_tunnels(
    client: CloudflareClient,
    account_id: str,
    name: str | None = None,
    is_deleted: bool = False,
) -> list[dict]:
    """List Cloudflare Tunnels for an account."""
    params = f"?is_deleted={str(is_deleted).lower()}"
    if name:
        params += f"&name={name}"

    result = client.request("GET", f"/accounts/{account_id}/cfd_tunnel{params}")
    return [
        {
            "id": t["id"],
            "name": t["name"],
            "status": t.get("status", "unknown"),
            "created_at": t.get("created_at"),
            "connections": len(t.get("connections", [])),
        }
        for t in result.get("result", [])
    ]


def get_tunnel(client: CloudflareClient, account_id: str, tunnel_id: str) -> dict:
    """Get details of a specific tunnel."""
    result = client.request("GET", f"/accounts/{account_id}/cfd_tunnel/{tunnel_id}")
    tunnel = result.get("result", {})
    return {
        "id": tunnel.get("id"),
        "name": tunnel.get("name"),
        "status": tunnel.get("status"),
        "created_at": tunnel.get("created_at"),
        "connections": tunnel.get("connections", []),
        "conns_active_at": tunnel.get("conns_active_at"),
    }


def create_tunnel(
    client: CloudflareClient,
    account_id: str,
    name: str,
    config_src: str = "cloudflare",
) -> dict:
    """Create a new Cloudflare Tunnel."""
    data = {"name": name, "config_src": config_src}
    result = client.request("POST", f"/accounts/{account_id}/cfd_tunnel", data)
    tunnel = result.get("result", {})
    return {
        "status": "created",
        "id": tunnel.get("id"),
        "name": tunnel.get("name"),
        "credentials_file": tunnel.get("credentials_file", {}),
        "token": tunnel.get("token"),
    }


def delete_tunnel(client: CloudflareClient, account_id: str, tunnel_id: str) -> dict:
    """Delete a Cloudflare Tunnel."""
    client.request("DELETE", f"/accounts/{account_id}/cfd_tunnel/{tunnel_id}")
    return {"status": "deleted", "id": tunnel_id}


def get_configurations(
    client: CloudflareClient,
    account_id: str,
    tunnel_id: str,
) -> dict:
    """Get the configuration for a tunnel."""
    result = client.request(
        "GET", f"/accounts/{account_id}/cfd_tunnel/{tunnel_id}/configurations"
    )
    return result.get("result", {})


def update_configuration(
    client: CloudflareClient,
    account_id: str,
    tunnel_id: str,
    config: dict,
) -> dict:
    """Update the configuration for a tunnel."""
    result = client.request(
        "PUT",
        f"/accounts/{account_id}/cfd_tunnel/{tunnel_id}/configurations",
        {"config": config},
    )
    return {"status": "updated", "config": result.get("result", {})}
