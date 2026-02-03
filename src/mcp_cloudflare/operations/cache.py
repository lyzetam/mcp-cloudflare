"""Cache purge operations."""

from __future__ import annotations

from ..client import CloudflareClient


def purge_all(client: CloudflareClient, zone_id: str) -> dict:
    """Purge all cached content for a zone."""
    result = client.request(
        "POST", f"/zones/{zone_id}/purge_cache", {"purge_everything": True}
    )
    return {
        "status": "purged",
        "message": "All cached content has been purged",
        "id": result.get("result", {}).get("id"),
    }


def purge_urls(client: CloudflareClient, zone_id: str, urls: list[str]) -> dict:
    """Purge specific URLs from cache (max 30 per request)."""
    if len(urls) > 30:
        raise ValueError("Maximum 30 URLs per request")
    result = client.request("POST", f"/zones/{zone_id}/purge_cache", {"files": urls})
    return {
        "status": "purged",
        "urls_purged": len(urls),
        "id": result.get("result", {}).get("id"),
    }


def purge_tags(client: CloudflareClient, zone_id: str, tags: list[str]) -> dict:
    """Purge cached content by Cache-Tag (Enterprise only)."""
    result = client.request("POST", f"/zones/{zone_id}/purge_cache", {"tags": tags})
    return {
        "status": "purged",
        "tags_purged": tags,
        "id": result.get("result", {}).get("id"),
    }


def purge_prefixes(client: CloudflareClient, zone_id: str, prefixes: list[str]) -> dict:
    """Purge cached content by URL prefix (Enterprise only)."""
    result = client.request(
        "POST", f"/zones/{zone_id}/purge_cache", {"prefixes": prefixes}
    )
    return {
        "status": "purged",
        "prefixes_purged": prefixes,
        "id": result.get("result", {}).get("id"),
    }
