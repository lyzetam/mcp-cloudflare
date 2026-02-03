"""Cloudflare MCP Server — backward-compatible @mcp.tool wrappers.

Tool names match the original server.py for drop-in replacement.
"""

from __future__ import annotations

import json
from typing import Optional

from fastmcp import FastMCP

from .client import CloudflareClient
from .operations import accounts, cache, dns, tunnels, zones

mcp = FastMCP("cloudflare-mcp")

_client: CloudflareClient | None = None


def _get_client() -> CloudflareClient:
    global _client
    if _client is None:
        _client = CloudflareClient()
    return _client


# --- Status ---

@mcp.tool
def cloudflare_status() -> str:
    """Check Cloudflare API connection status and token validity."""
    try:
        return json.dumps(accounts.verify_token(_get_client()), indent=2)
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)}, indent=2)


# --- Zones ---

@mcp.tool
def zone_list(name: Optional[str] = None, status: Optional[str] = None, per_page: int = 50) -> str:
    """List all zones (domains) in the Cloudflare account."""
    return json.dumps(zones.list_zones(_get_client(), name=name, status=status, per_page=per_page), indent=2)


@mcp.tool
def zone_get(zone_id: str) -> str:
    """Get detailed information about a specific zone."""
    return json.dumps(zones.get_zone(_get_client(), zone_id), indent=2)


@mcp.tool
def zone_settings(zone_id: str) -> str:
    """Get all settings for a zone."""
    return json.dumps(zones.get_zone_settings(_get_client(), zone_id), indent=2)


# --- DNS ---

@mcp.tool
def dns_list(zone_id: str, record_type: Optional[str] = None, name: Optional[str] = None, per_page: int = 100) -> str:
    """List DNS records for a zone."""
    return json.dumps(dns.list_records(_get_client(), zone_id, record_type=record_type, name=name, per_page=per_page), indent=2)


@mcp.tool
def dns_create(zone_id: str, record_type: str, name: str, content: str, ttl: int = 1, proxied: bool = False, priority: Optional[int] = None) -> str:
    """Create a new DNS record."""
    return json.dumps(dns.create_record(_get_client(), zone_id, record_type, name, content, ttl=ttl, proxied=proxied, priority=priority), indent=2)


@mcp.tool
def dns_update(zone_id: str, record_id: str, record_type: str, name: str, content: str, ttl: int = 1, proxied: bool = False, priority: Optional[int] = None) -> str:
    """Update an existing DNS record."""
    return json.dumps(dns.update_record(_get_client(), zone_id, record_id, record_type, name, content, ttl=ttl, proxied=proxied, priority=priority), indent=2)


@mcp.tool
def dns_delete(zone_id: str, record_id: str) -> str:
    """Delete a DNS record."""
    return json.dumps(dns.delete_record(_get_client(), zone_id, record_id), indent=2)


# --- Tunnels ---

@mcp.tool
def tunnel_list(account_id: str, name: Optional[str] = None, is_deleted: bool = False) -> str:
    """List Cloudflare Tunnels for an account."""
    return json.dumps(tunnels.list_tunnels(_get_client(), account_id, name=name, is_deleted=is_deleted), indent=2)


@mcp.tool
def tunnel_get(account_id: str, tunnel_id: str) -> str:
    """Get details of a specific tunnel."""
    return json.dumps(tunnels.get_tunnel(_get_client(), account_id, tunnel_id), indent=2)


@mcp.tool
def tunnel_create(account_id: str, name: str, config_src: str = "cloudflare") -> str:
    """Create a new Cloudflare Tunnel."""
    return json.dumps(tunnels.create_tunnel(_get_client(), account_id, name, config_src=config_src), indent=2)


@mcp.tool
def tunnel_delete(account_id: str, tunnel_id: str) -> str:
    """Delete a Cloudflare Tunnel."""
    return json.dumps(tunnels.delete_tunnel(_get_client(), account_id, tunnel_id), indent=2)


@mcp.tool
def tunnel_configurations(account_id: str, tunnel_id: str) -> str:
    """Get the configuration for a tunnel."""
    return json.dumps(tunnels.get_configurations(_get_client(), account_id, tunnel_id), indent=2)


@mcp.tool
def tunnel_update_config(account_id: str, tunnel_id: str, config: dict) -> str:
    """Update the configuration for a tunnel."""
    return json.dumps(tunnels.update_configuration(_get_client(), account_id, tunnel_id, config), indent=2)


# --- Cache ---

@mcp.tool
def cache_purge_all(zone_id: str) -> str:
    """Purge all cached content for a zone."""
    return json.dumps(cache.purge_all(_get_client(), zone_id), indent=2)


@mcp.tool
def cache_purge_urls(zone_id: str, urls: list) -> str:
    """Purge specific URLs from cache (max 30 per request)."""
    return json.dumps(cache.purge_urls(_get_client(), zone_id, urls), indent=2)


@mcp.tool
def cache_purge_tags(zone_id: str, tags: list) -> str:
    """Purge cached content by Cache-Tag (Enterprise only)."""
    return json.dumps(cache.purge_tags(_get_client(), zone_id, tags), indent=2)


@mcp.tool
def cache_purge_prefixes(zone_id: str, prefixes: list) -> str:
    """Purge cached content by URL prefix (Enterprise only)."""
    return json.dumps(cache.purge_prefixes(_get_client(), zone_id, prefixes), indent=2)


# --- Accounts ---

@mcp.tool
def account_list() -> str:
    """List all accounts the API token has access to."""
    return json.dumps(accounts.list_accounts(_get_client()), indent=2)


def main():
    mcp.run()


if __name__ == "__main__":
    main()
