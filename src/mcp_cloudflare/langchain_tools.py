"""LangChain @tool wrappers for Cloudflare operations.

Usage:
    from mcp_cloudflare.langchain_tools import TOOLS

    # Or import individual tools:
    from mcp_cloudflare.langchain_tools import cf_dns_list, cf_zone_list
"""

from __future__ import annotations

import json
from functools import lru_cache
from typing import Optional

from langchain_core.tools import tool
from pydantic import BaseModel, Field

from .client import CloudflareClient
from .operations import accounts, cache, dns, tunnels, zones


@lru_cache
def _get_client() -> CloudflareClient:
    """Singleton CloudflareClient configured from environment."""
    return CloudflareClient()


# =============================================================================
# Status
# =============================================================================


@tool
def cf_status() -> str:
    """Check Cloudflare API connection status and token validity."""
    try:
        result = accounts.verify_token(_get_client())
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)}, indent=2)


# =============================================================================
# Zones
# =============================================================================


class ZoneListInput(BaseModel):
    name: Optional[str] = Field(default=None, description="Filter by zone name (domain)")
    status: Optional[str] = Field(
        default=None,
        description="Filter by status (active, pending, initializing, moved, deleted)",
    )
    per_page: int = Field(default=50, description="Results per page (max 50)")


@tool(args_schema=ZoneListInput)
def cf_zone_list(
    name: Optional[str] = None,
    status: Optional[str] = None,
    per_page: int = 50,
) -> str:
    """List all zones (domains) in the Cloudflare account."""
    return json.dumps(
        zones.list_zones(_get_client(), name=name, status=status, per_page=per_page),
        indent=2,
    )


class ZoneGetInput(BaseModel):
    zone_id: str = Field(description="The zone ID")


@tool(args_schema=ZoneGetInput)
def cf_zone_get(zone_id: str) -> str:
    """Get detailed information about a specific zone."""
    return json.dumps(zones.get_zone(_get_client(), zone_id), indent=2)


class ZoneSettingsInput(BaseModel):
    zone_id: str = Field(description="The zone ID")


@tool(args_schema=ZoneSettingsInput)
def cf_zone_settings(zone_id: str) -> str:
    """Get all settings for a zone (SSL, security level, cache, etc.)."""
    return json.dumps(zones.get_zone_settings(_get_client(), zone_id), indent=2)


# =============================================================================
# DNS
# =============================================================================


class DNSListInput(BaseModel):
    zone_id: str = Field(description="The zone ID")
    record_type: Optional[str] = Field(
        default=None, description="Filter by type (A, AAAA, CNAME, TXT, MX)"
    )
    name: Optional[str] = Field(default=None, description="Filter by record name")
    per_page: int = Field(default=100, description="Results per page (max 100)")


@tool(args_schema=DNSListInput)
def cf_dns_list(
    zone_id: str,
    record_type: Optional[str] = None,
    name: Optional[str] = None,
    per_page: int = 100,
) -> str:
    """List DNS records for a zone."""
    return json.dumps(
        dns.list_records(
            _get_client(), zone_id, record_type=record_type, name=name, per_page=per_page
        ),
        indent=2,
    )


class DNSCreateInput(BaseModel):
    zone_id: str = Field(description="The zone ID")
    record_type: str = Field(description="Record type (A, AAAA, CNAME, TXT, MX)")
    name: str = Field(description="Record name (e.g., 'www' or 'subdomain.example.com')")
    content: str = Field(description="Record content (IP address, hostname, or text)")
    ttl: int = Field(default=1, description="Time to live (1 = automatic)")
    proxied: bool = Field(default=False, description="Proxy through Cloudflare")
    priority: Optional[int] = Field(default=None, description="Priority for MX records")


@tool(args_schema=DNSCreateInput)
def cf_dns_create(
    zone_id: str,
    record_type: str,
    name: str,
    content: str,
    ttl: int = 1,
    proxied: bool = False,
    priority: Optional[int] = None,
) -> str:
    """Create a new DNS record."""
    return json.dumps(
        dns.create_record(
            _get_client(),
            zone_id,
            record_type,
            name,
            content,
            ttl=ttl,
            proxied=proxied,
            priority=priority,
        ),
        indent=2,
    )


class DNSUpdateInput(BaseModel):
    zone_id: str = Field(description="The zone ID")
    record_id: str = Field(description="The DNS record ID")
    record_type: str = Field(description="Record type (A, AAAA, CNAME, TXT, MX)")
    name: str = Field(description="Record name")
    content: str = Field(description="Record content")
    ttl: int = Field(default=1, description="Time to live (1 = automatic)")
    proxied: bool = Field(default=False, description="Proxy through Cloudflare")
    priority: Optional[int] = Field(default=None, description="Priority for MX records")


@tool(args_schema=DNSUpdateInput)
def cf_dns_update(
    zone_id: str,
    record_id: str,
    record_type: str,
    name: str,
    content: str,
    ttl: int = 1,
    proxied: bool = False,
    priority: Optional[int] = None,
) -> str:
    """Update an existing DNS record."""
    return json.dumps(
        dns.update_record(
            _get_client(),
            zone_id,
            record_id,
            record_type,
            name,
            content,
            ttl=ttl,
            proxied=proxied,
            priority=priority,
        ),
        indent=2,
    )


class DNSDeleteInput(BaseModel):
    zone_id: str = Field(description="The zone ID")
    record_id: str = Field(description="The DNS record ID to delete")


@tool(args_schema=DNSDeleteInput)
def cf_dns_delete(zone_id: str, record_id: str) -> str:
    """Delete a DNS record."""
    return json.dumps(dns.delete_record(_get_client(), zone_id, record_id), indent=2)


# =============================================================================
# Tunnels
# =============================================================================


class TunnelListInput(BaseModel):
    account_id: str = Field(description="Cloudflare account ID")
    name: Optional[str] = Field(default=None, description="Filter by tunnel name")
    is_deleted: bool = Field(default=False, description="Include deleted tunnels")


@tool(args_schema=TunnelListInput)
def cf_tunnel_list(
    account_id: str,
    name: Optional[str] = None,
    is_deleted: bool = False,
) -> str:
    """List Cloudflare Tunnels for an account."""
    return json.dumps(
        tunnels.list_tunnels(
            _get_client(), account_id, name=name, is_deleted=is_deleted
        ),
        indent=2,
    )


class TunnelGetInput(BaseModel):
    account_id: str = Field(description="Cloudflare account ID")
    tunnel_id: str = Field(description="The tunnel ID")


@tool(args_schema=TunnelGetInput)
def cf_tunnel_get(account_id: str, tunnel_id: str) -> str:
    """Get details of a specific tunnel."""
    return json.dumps(
        tunnels.get_tunnel(_get_client(), account_id, tunnel_id), indent=2
    )


class TunnelCreateInput(BaseModel):
    account_id: str = Field(description="Cloudflare account ID")
    name: str = Field(description="Name for the new tunnel")
    config_src: str = Field(default="cloudflare", description="Config source (cloudflare or local)")


@tool(args_schema=TunnelCreateInput)
def cf_tunnel_create(
    account_id: str,
    name: str,
    config_src: str = "cloudflare",
) -> str:
    """Create a new Cloudflare Tunnel."""
    return json.dumps(
        tunnels.create_tunnel(_get_client(), account_id, name, config_src=config_src),
        indent=2,
    )


class TunnelDeleteInput(BaseModel):
    account_id: str = Field(description="Cloudflare account ID")
    tunnel_id: str = Field(description="The tunnel ID to delete")


@tool(args_schema=TunnelDeleteInput)
def cf_tunnel_delete(account_id: str, tunnel_id: str) -> str:
    """Delete a Cloudflare Tunnel."""
    return json.dumps(
        tunnels.delete_tunnel(_get_client(), account_id, tunnel_id), indent=2
    )


class TunnelConfigInput(BaseModel):
    account_id: str = Field(description="Cloudflare account ID")
    tunnel_id: str = Field(description="The tunnel ID")


@tool(args_schema=TunnelConfigInput)
def cf_tunnel_configurations(account_id: str, tunnel_id: str) -> str:
    """Get the configuration for a tunnel (ingress rules, etc.)."""
    return json.dumps(
        tunnels.get_configurations(_get_client(), account_id, tunnel_id), indent=2
    )


class TunnelUpdateConfigInput(BaseModel):
    account_id: str = Field(description="Cloudflare account ID")
    tunnel_id: str = Field(description="The tunnel ID")
    config: dict = Field(description="Tunnel configuration with ingress rules")


@tool(args_schema=TunnelUpdateConfigInput)
def cf_tunnel_update_config(account_id: str, tunnel_id: str, config: dict) -> str:
    """Update the configuration for a tunnel."""
    return json.dumps(
        tunnels.update_configuration(_get_client(), account_id, tunnel_id, config),
        indent=2,
    )


# =============================================================================
# Cache
# =============================================================================


class CachePurgeAllInput(BaseModel):
    zone_id: str = Field(description="The zone ID")


@tool(args_schema=CachePurgeAllInput)
def cf_cache_purge_all(zone_id: str) -> str:
    """Purge all cached content for a zone."""
    return json.dumps(cache.purge_all(_get_client(), zone_id), indent=2)


class CachePurgeUrlsInput(BaseModel):
    zone_id: str = Field(description="The zone ID")
    urls: list[str] = Field(description="List of URLs to purge (max 30)")


@tool(args_schema=CachePurgeUrlsInput)
def cf_cache_purge_urls(zone_id: str, urls: list[str]) -> str:
    """Purge specific URLs from cache."""
    return json.dumps(cache.purge_urls(_get_client(), zone_id, urls), indent=2)


class CachePurgeTagsInput(BaseModel):
    zone_id: str = Field(description="The zone ID")
    tags: list[str] = Field(description="List of cache tags to purge")


@tool(args_schema=CachePurgeTagsInput)
def cf_cache_purge_tags(zone_id: str, tags: list[str]) -> str:
    """Purge cached content by Cache-Tag (Enterprise only)."""
    return json.dumps(cache.purge_tags(_get_client(), zone_id, tags), indent=2)


class CachePurgePrefixesInput(BaseModel):
    zone_id: str = Field(description="The zone ID")
    prefixes: list[str] = Field(description="List of URL prefixes to purge")


@tool(args_schema=CachePurgePrefixesInput)
def cf_cache_purge_prefixes(zone_id: str, prefixes: list[str]) -> str:
    """Purge cached content by URL prefix (Enterprise only)."""
    return json.dumps(cache.purge_prefixes(_get_client(), zone_id, prefixes), indent=2)


# =============================================================================
# Accounts
# =============================================================================


@tool
def cf_account_list() -> str:
    """List all accounts the API token has access to."""
    return json.dumps(accounts.list_accounts(_get_client()), indent=2)


# =============================================================================
# Tool exports
# =============================================================================

TOOLS = [
    # Status
    cf_status,
    # Zones
    cf_zone_list,
    cf_zone_get,
    cf_zone_settings,
    # DNS
    cf_dns_list,
    cf_dns_create,
    cf_dns_update,
    cf_dns_delete,
    # Tunnels
    cf_tunnel_list,
    cf_tunnel_get,
    cf_tunnel_create,
    cf_tunnel_delete,
    cf_tunnel_configurations,
    cf_tunnel_update_config,
    # Cache
    cf_cache_purge_all,
    cf_cache_purge_urls,
    cf_cache_purge_tags,
    cf_cache_purge_prefixes,
    # Accounts
    cf_account_list,
]
