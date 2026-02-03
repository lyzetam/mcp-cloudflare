#!/usr/bin/env python3
"""
Cloudflare MCP Server - Provides Cloudflare API interactions via MCP protocol.
Supports DNS management, Tunnel management, Zone management, and Cache purging.
"""
import os
import json
from typing import Optional

from fastmcp import FastMCP
import httpx

# Configuration from environment (strip to handle trailing newlines from Docker secrets)
CLOUDFLARE_API_TOKEN = os.environ.get("CLOUDFLARE_API_TOKEN", "").strip()
CLOUDFLARE_API_URL = "https://api.cloudflare.com/client/v4"

mcp = FastMCP("cloudflare-mcp")


def get_headers() -> dict:
    """Get headers for Cloudflare API requests."""
    return {
        "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
        "Content-Type": "application/json"
    }


def make_request(method: str, endpoint: str, data: Optional[dict] = None) -> dict:
    """Make a synchronous request to the Cloudflare API."""
    url = f"{CLOUDFLARE_API_URL}{endpoint}"
    with httpx.Client(timeout=30.0) as client:
        if method == "GET":
            response = client.get(url, headers=get_headers())
        elif method == "POST":
            response = client.post(url, headers=get_headers(), json=data)
        elif method == "PUT":
            response = client.put(url, headers=get_headers(), json=data)
        elif method == "PATCH":
            response = client.patch(url, headers=get_headers(), json=data)
        elif method == "DELETE":
            response = client.delete(url, headers=get_headers())
        else:
            return {"success": False, "errors": [{"message": f"Unknown method: {method}"}]}

        return response.json()


# =============================================================================
# Status Tool
# =============================================================================

@mcp.tool
def cloudflare_status() -> str:
    """Check Cloudflare API connection status and token validity.

    Returns:
        JSON with connection status and user/token information
    """
    if not CLOUDFLARE_API_TOKEN:
        return json.dumps({"status": "error", "message": "No API token configured"}, indent=2)

    try:
        result = make_request("GET", "/user/tokens/verify")
        if result.get("success"):
            return json.dumps({
                "status": "connected",
                "token_status": result.get("result", {}).get("status", "unknown"),
                "message": "Cloudflare API token is valid"
            }, indent=2)
        else:
            errors = result.get("errors", [{"message": "Unknown error"}])
            return json.dumps({
                "status": "error",
                "message": errors[0].get("message", "Unknown error")
            }, indent=2)
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)}, indent=2)


# =============================================================================
# Zone Management Tools
# =============================================================================

@mcp.tool
def zone_list(name: Optional[str] = None, status: Optional[str] = None, per_page: int = 50) -> str:
    """List all zones (domains) in the Cloudflare account.

    Args:
        name: Filter by zone name (domain)
        status: Filter by status (active, pending, initializing, moved, deleted)
        per_page: Number of results per page (max 50)

    Returns:
        JSON list of zones with id, name, status, and plan
    """
    try:
        params = f"?per_page={per_page}"
        if name:
            params += f"&name={name}"
        if status:
            params += f"&status={status}"

        result = make_request("GET", f"/zones{params}")

        if result.get("success"):
            zones = [{
                "id": z["id"],
                "name": z["name"],
                "status": z["status"],
                "plan": z.get("plan", {}).get("name", "N/A"),
                "name_servers": z.get("name_servers", [])
            } for z in result.get("result", [])]
            return json.dumps(zones, indent=2)
        else:
            return json.dumps({"error": result.get("errors", [])}, indent=2)
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool
def zone_get(zone_id: str) -> str:
    """Get detailed information about a specific zone.

    Args:
        zone_id: The zone ID (can be obtained from zone_list)

    Returns:
        JSON with full zone details
    """
    try:
        result = make_request("GET", f"/zones/{zone_id}")

        if result.get("success"):
            zone = result.get("result", {})
            return json.dumps({
                "id": zone.get("id"),
                "name": zone.get("name"),
                "status": zone.get("status"),
                "paused": zone.get("paused"),
                "type": zone.get("type"),
                "plan": zone.get("plan", {}).get("name"),
                "name_servers": zone.get("name_servers", []),
                "original_name_servers": zone.get("original_name_servers", []),
                "created_on": zone.get("created_on"),
                "modified_on": zone.get("modified_on")
            }, indent=2)
        else:
            return json.dumps({"error": result.get("errors", [])}, indent=2)
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool
def zone_settings(zone_id: str) -> str:
    """Get all settings for a zone.

    Args:
        zone_id: The zone ID

    Returns:
        JSON with zone settings (SSL, security level, cache, etc.)
    """
    try:
        result = make_request("GET", f"/zones/{zone_id}/settings")

        if result.get("success"):
            settings = {s["id"]: s.get("value") for s in result.get("result", [])}
            return json.dumps(settings, indent=2)
        else:
            return json.dumps({"error": result.get("errors", [])}, indent=2)
    except Exception as e:
        return f"Error: {str(e)}"


# =============================================================================
# DNS Management Tools
# =============================================================================

@mcp.tool
def dns_list(zone_id: str, record_type: Optional[str] = None, name: Optional[str] = None, per_page: int = 100) -> str:
    """List DNS records for a zone.

    Args:
        zone_id: The zone ID
        record_type: Filter by record type (A, AAAA, CNAME, TXT, MX, etc.)
        name: Filter by record name
        per_page: Number of results per page (max 100)

    Returns:
        JSON list of DNS records
    """
    try:
        params = f"?per_page={per_page}"
        if record_type:
            params += f"&type={record_type}"
        if name:
            params += f"&name={name}"

        result = make_request("GET", f"/zones/{zone_id}/dns_records{params}")

        if result.get("success"):
            records = [{
                "id": r["id"],
                "type": r["type"],
                "name": r["name"],
                "content": r["content"],
                "ttl": r["ttl"],
                "proxied": r.get("proxied", False),
                "priority": r.get("priority")
            } for r in result.get("result", [])]
            return json.dumps(records, indent=2)
        else:
            return json.dumps({"error": result.get("errors", [])}, indent=2)
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool
def dns_create(zone_id: str, record_type: str, name: str, content: str,
               ttl: int = 1, proxied: bool = False, priority: Optional[int] = None) -> str:
    """Create a new DNS record.

    Args:
        zone_id: The zone ID
        record_type: Record type (A, AAAA, CNAME, TXT, MX, etc.)
        name: Record name (e.g., 'www' or 'subdomain.example.com')
        content: Record content (IP address, hostname, or text)
        ttl: Time to live (1 = automatic, otherwise seconds)
        proxied: Whether to proxy through Cloudflare (only for A, AAAA, CNAME)
        priority: Priority for MX records

    Returns:
        JSON with created record details
    """
    try:
        data = {
            "type": record_type.upper(),
            "name": name,
            "content": content,
            "ttl": ttl,
            "proxied": proxied
        }
        if priority is not None:
            data["priority"] = priority

        result = make_request("POST", f"/zones/{zone_id}/dns_records", data)

        if result.get("success"):
            record = result.get("result", {})
            return json.dumps({
                "status": "created",
                "id": record.get("id"),
                "type": record.get("type"),
                "name": record.get("name"),
                "content": record.get("content")
            }, indent=2)
        else:
            return json.dumps({"error": result.get("errors", [])}, indent=2)
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool
def dns_update(zone_id: str, record_id: str, record_type: str, name: str, content: str,
               ttl: int = 1, proxied: bool = False, priority: Optional[int] = None) -> str:
    """Update an existing DNS record.

    Args:
        zone_id: The zone ID
        record_id: The DNS record ID
        record_type: Record type (A, AAAA, CNAME, TXT, MX, etc.)
        name: Record name
        content: Record content
        ttl: Time to live (1 = automatic)
        proxied: Whether to proxy through Cloudflare
        priority: Priority for MX records

    Returns:
        JSON with updated record details
    """
    try:
        data = {
            "type": record_type.upper(),
            "name": name,
            "content": content,
            "ttl": ttl,
            "proxied": proxied
        }
        if priority is not None:
            data["priority"] = priority

        result = make_request("PUT", f"/zones/{zone_id}/dns_records/{record_id}", data)

        if result.get("success"):
            record = result.get("result", {})
            return json.dumps({
                "status": "updated",
                "id": record.get("id"),
                "type": record.get("type"),
                "name": record.get("name"),
                "content": record.get("content")
            }, indent=2)
        else:
            return json.dumps({"error": result.get("errors", [])}, indent=2)
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool
def dns_delete(zone_id: str, record_id: str) -> str:
    """Delete a DNS record.

    Args:
        zone_id: The zone ID
        record_id: The DNS record ID to delete

    Returns:
        JSON with deletion status
    """
    try:
        result = make_request("DELETE", f"/zones/{zone_id}/dns_records/{record_id}")

        if result.get("success"):
            return json.dumps({
                "status": "deleted",
                "id": result.get("result", {}).get("id")
            }, indent=2)
        else:
            return json.dumps({"error": result.get("errors", [])}, indent=2)
    except Exception as e:
        return f"Error: {str(e)}"


# =============================================================================
# Tunnel Management Tools
# =============================================================================

@mcp.tool
def tunnel_list(account_id: str, name: Optional[str] = None, is_deleted: bool = False) -> str:
    """List Cloudflare Tunnels for an account.

    Args:
        account_id: The Cloudflare account ID
        name: Filter by tunnel name
        is_deleted: Include deleted tunnels

    Returns:
        JSON list of tunnels
    """
    try:
        params = f"?is_deleted={str(is_deleted).lower()}"
        if name:
            params += f"&name={name}"

        result = make_request("GET", f"/accounts/{account_id}/cfd_tunnel{params}")

        if result.get("success"):
            tunnels = [{
                "id": t["id"],
                "name": t["name"],
                "status": t.get("status", "unknown"),
                "created_at": t.get("created_at"),
                "connections": len(t.get("connections", []))
            } for t in result.get("result", [])]
            return json.dumps(tunnels, indent=2)
        else:
            return json.dumps({"error": result.get("errors", [])}, indent=2)
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool
def tunnel_get(account_id: str, tunnel_id: str) -> str:
    """Get details of a specific tunnel.

    Args:
        account_id: The Cloudflare account ID
        tunnel_id: The tunnel ID

    Returns:
        JSON with tunnel details and connections
    """
    try:
        result = make_request("GET", f"/accounts/{account_id}/cfd_tunnel/{tunnel_id}")

        if result.get("success"):
            tunnel = result.get("result", {})
            return json.dumps({
                "id": tunnel.get("id"),
                "name": tunnel.get("name"),
                "status": tunnel.get("status"),
                "created_at": tunnel.get("created_at"),
                "connections": tunnel.get("connections", []),
                "conns_active_at": tunnel.get("conns_active_at")
            }, indent=2)
        else:
            return json.dumps({"error": result.get("errors", [])}, indent=2)
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool
def tunnel_create(account_id: str, name: str, config_src: str = "cloudflare") -> str:
    """Create a new Cloudflare Tunnel.

    Args:
        account_id: The Cloudflare account ID
        name: Name for the new tunnel
        config_src: Configuration source ('cloudflare' or 'local')

    Returns:
        JSON with created tunnel details including credentials
    """
    try:
        data = {
            "name": name,
            "config_src": config_src
        }

        result = make_request("POST", f"/accounts/{account_id}/cfd_tunnel", data)

        if result.get("success"):
            tunnel = result.get("result", {})
            return json.dumps({
                "status": "created",
                "id": tunnel.get("id"),
                "name": tunnel.get("name"),
                "credentials_file": tunnel.get("credentials_file", {}),
                "token": tunnel.get("token")
            }, indent=2)
        else:
            return json.dumps({"error": result.get("errors", [])}, indent=2)
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool
def tunnel_delete(account_id: str, tunnel_id: str) -> str:
    """Delete a Cloudflare Tunnel.

    Args:
        account_id: The Cloudflare account ID
        tunnel_id: The tunnel ID to delete

    Returns:
        JSON with deletion status
    """
    try:
        result = make_request("DELETE", f"/accounts/{account_id}/cfd_tunnel/{tunnel_id}")

        if result.get("success"):
            return json.dumps({
                "status": "deleted",
                "id": tunnel_id
            }, indent=2)
        else:
            return json.dumps({"error": result.get("errors", [])}, indent=2)
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool
def tunnel_configurations(account_id: str, tunnel_id: str) -> str:
    """Get the configuration for a tunnel.

    Args:
        account_id: The Cloudflare account ID
        tunnel_id: The tunnel ID

    Returns:
        JSON with tunnel configuration (ingress rules, etc.)
    """
    try:
        result = make_request("GET", f"/accounts/{account_id}/cfd_tunnel/{tunnel_id}/configurations")

        if result.get("success"):
            return json.dumps(result.get("result", {}), indent=2)
        else:
            return json.dumps({"error": result.get("errors", [])}, indent=2)
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool
def tunnel_update_config(account_id: str, tunnel_id: str, config: dict) -> str:
    """Update the configuration for a tunnel.

    Args:
        account_id: The Cloudflare account ID
        tunnel_id: The tunnel ID
        config: Tunnel configuration with ingress rules

    Returns:
        JSON with updated configuration
    """
    try:
        result = make_request("PUT", f"/accounts/{account_id}/cfd_tunnel/{tunnel_id}/configurations",
                             {"config": config})

        if result.get("success"):
            return json.dumps({
                "status": "updated",
                "config": result.get("result", {})
            }, indent=2)
        else:
            return json.dumps({"error": result.get("errors", [])}, indent=2)
    except Exception as e:
        return f"Error: {str(e)}"


# =============================================================================
# Cache/Purge Tools
# =============================================================================

@mcp.tool
def cache_purge_all(zone_id: str) -> str:
    """Purge all cached content for a zone.

    Args:
        zone_id: The zone ID

    Returns:
        JSON with purge status
    """
    try:
        result = make_request("POST", f"/zones/{zone_id}/purge_cache", {"purge_everything": True})

        if result.get("success"):
            return json.dumps({
                "status": "purged",
                "message": "All cached content has been purged",
                "id": result.get("result", {}).get("id")
            }, indent=2)
        else:
            return json.dumps({"error": result.get("errors", [])}, indent=2)
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool
def cache_purge_urls(zone_id: str, urls: list) -> str:
    """Purge specific URLs from cache.

    Args:
        zone_id: The zone ID
        urls: List of URLs to purge (max 30 per request)

    Returns:
        JSON with purge status
    """
    try:
        if len(urls) > 30:
            return json.dumps({"error": "Maximum 30 URLs per request"}, indent=2)

        result = make_request("POST", f"/zones/{zone_id}/purge_cache", {"files": urls})

        if result.get("success"):
            return json.dumps({
                "status": "purged",
                "urls_purged": len(urls),
                "id": result.get("result", {}).get("id")
            }, indent=2)
        else:
            return json.dumps({"error": result.get("errors", [])}, indent=2)
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool
def cache_purge_tags(zone_id: str, tags: list) -> str:
    """Purge cached content by Cache-Tag (Enterprise only).

    Args:
        zone_id: The zone ID
        tags: List of cache tags to purge

    Returns:
        JSON with purge status
    """
    try:
        result = make_request("POST", f"/zones/{zone_id}/purge_cache", {"tags": tags})

        if result.get("success"):
            return json.dumps({
                "status": "purged",
                "tags_purged": tags,
                "id": result.get("result", {}).get("id")
            }, indent=2)
        else:
            return json.dumps({"error": result.get("errors", [])}, indent=2)
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool
def cache_purge_prefixes(zone_id: str, prefixes: list) -> str:
    """Purge cached content by URL prefix (Enterprise only).

    Args:
        zone_id: The zone ID
        prefixes: List of URL prefixes to purge (e.g., ['example.com/images/'])

    Returns:
        JSON with purge status
    """
    try:
        result = make_request("POST", f"/zones/{zone_id}/purge_cache", {"prefixes": prefixes})

        if result.get("success"):
            return json.dumps({
                "status": "purged",
                "prefixes_purged": prefixes,
                "id": result.get("result", {}).get("id")
            }, indent=2)
        else:
            return json.dumps({"error": result.get("errors", [])}, indent=2)
    except Exception as e:
        return f"Error: {str(e)}"


# =============================================================================
# Account Tools
# =============================================================================

@mcp.tool
def account_list() -> str:
    """List all accounts the API token has access to.

    Returns:
        JSON list of accounts with id and name
    """
    try:
        result = make_request("GET", "/accounts")

        if result.get("success"):
            accounts = [{
                "id": a["id"],
                "name": a["name"],
                "type": a.get("type", "standard")
            } for a in result.get("result", [])]
            return json.dumps(accounts, indent=2)
        else:
            return json.dumps({"error": result.get("errors", [])}, indent=2)
    except Exception as e:
        return f"Error: {str(e)}"


if __name__ == "__main__":
    mcp.run()
