"""Tests for Cloudflare operations using respx mocks."""

import httpx
import pytest
import respx

from mcp_cloudflare.client import CloudflareClient
from mcp_cloudflare.operations import accounts, cache, dns, tunnels, zones

BASE = "https://api.cloudflare.com/client/v4"


@pytest.fixture
def client():
    return CloudflareClient(api_token="test-token", account_id="test-account")


@respx.mock
def test_verify_token(client):
    respx.get(f"{BASE}/user/tokens/verify").mock(
        return_value=httpx.Response(200, json={"success": True, "result": {"status": "active"}})
    )
    result = accounts.verify_token(client)
    assert result["status"] == "connected"
    assert result["token_status"] == "active"


@respx.mock
def test_verify_token_no_token():
    c = CloudflareClient(api_token="")
    result = accounts.verify_token(c)
    assert result["status"] == "error"


@respx.mock
def test_list_accounts(client):
    respx.get(f"{BASE}/accounts").mock(
        return_value=httpx.Response(200, json={
            "success": True,
            "result": [{"id": "acc1", "name": "My Account", "type": "standard"}],
        })
    )
    result = accounts.list_accounts(client)
    assert len(result) == 1
    assert result[0]["id"] == "acc1"


@respx.mock
def test_list_zones(client):
    respx.get(f"{BASE}/zones").mock(
        return_value=httpx.Response(200, json={
            "success": True,
            "result": [{
                "id": "z1", "name": "example.com", "status": "active",
                "plan": {"name": "Free"}, "name_servers": ["ns1.example.com"],
            }],
        })
    )
    result = zones.list_zones(client)
    assert len(result) == 1
    assert result[0]["name"] == "example.com"


@respx.mock
def test_get_zone(client):
    respx.get(f"{BASE}/zones/z1").mock(
        return_value=httpx.Response(200, json={
            "success": True,
            "result": {
                "id": "z1", "name": "example.com", "status": "active",
                "paused": False, "type": "full",
                "plan": {"name": "Free"}, "name_servers": [],
                "original_name_servers": [],
                "created_on": "2024-01-01", "modified_on": "2024-01-02",
            },
        })
    )
    result = zones.get_zone(client, "z1")
    assert result["id"] == "z1"
    assert result["status"] == "active"


@respx.mock
def test_get_zone_settings(client):
    respx.get(f"{BASE}/zones/z1/settings").mock(
        return_value=httpx.Response(200, json={
            "success": True,
            "result": [
                {"id": "ssl", "value": "full"},
                {"id": "min_tls_version", "value": "1.2"},
            ],
        })
    )
    result = zones.get_zone_settings(client, "z1")
    assert result["ssl"] == "full"
    assert result["min_tls_version"] == "1.2"


@respx.mock
def test_list_dns_records(client):
    respx.get(f"{BASE}/zones/z1/dns_records").mock(
        return_value=httpx.Response(200, json={
            "success": True,
            "result": [{
                "id": "r1", "type": "A", "name": "example.com",
                "content": "1.2.3.4", "ttl": 1, "proxied": True,
            }],
        })
    )
    result = dns.list_records(client, "z1")
    assert len(result) == 1
    assert result[0]["type"] == "A"


@respx.mock
def test_create_dns_record(client):
    respx.post(f"{BASE}/zones/z1/dns_records").mock(
        return_value=httpx.Response(200, json={
            "success": True,
            "result": {"id": "r2", "type": "A", "name": "test.example.com", "content": "5.6.7.8"},
        })
    )
    result = dns.create_record(client, "z1", "A", "test.example.com", "5.6.7.8")
    assert result["status"] == "created"
    assert result["id"] == "r2"


@respx.mock
def test_update_dns_record(client):
    respx.put(f"{BASE}/zones/z1/dns_records/r1").mock(
        return_value=httpx.Response(200, json={
            "success": True,
            "result": {"id": "r1", "type": "A", "name": "example.com", "content": "9.8.7.6"},
        })
    )
    result = dns.update_record(client, "z1", "r1", "A", "example.com", "9.8.7.6")
    assert result["status"] == "updated"


@respx.mock
def test_delete_dns_record(client):
    respx.delete(f"{BASE}/zones/z1/dns_records/r1").mock(
        return_value=httpx.Response(200, json={"success": True, "result": {"id": "r1"}})
    )
    result = dns.delete_record(client, "z1", "r1")
    assert result["status"] == "deleted"


@respx.mock
def test_list_tunnels(client):
    respx.get(f"{BASE}/accounts/acc1/cfd_tunnel").mock(
        return_value=httpx.Response(200, json={
            "success": True,
            "result": [{"id": "t1", "name": "my-tunnel", "status": "healthy", "created_at": "2024-01-01", "connections": []}],
        })
    )
    result = tunnels.list_tunnels(client, "acc1")
    assert len(result) == 1
    assert result[0]["name"] == "my-tunnel"


@respx.mock
def test_get_tunnel(client):
    respx.get(f"{BASE}/accounts/acc1/cfd_tunnel/t1").mock(
        return_value=httpx.Response(200, json={
            "success": True,
            "result": {"id": "t1", "name": "my-tunnel", "status": "healthy", "created_at": "2024-01-01", "connections": []},
        })
    )
    result = tunnels.get_tunnel(client, "acc1", "t1")
    assert result["id"] == "t1"


@respx.mock
def test_create_tunnel(client):
    respx.post(f"{BASE}/accounts/acc1/cfd_tunnel").mock(
        return_value=httpx.Response(200, json={
            "success": True,
            "result": {"id": "t2", "name": "new-tunnel", "token": "abc123"},
        })
    )
    result = tunnels.create_tunnel(client, "acc1", "new-tunnel")
    assert result["status"] == "created"
    assert result["id"] == "t2"


@respx.mock
def test_delete_tunnel(client):
    respx.delete(f"{BASE}/accounts/acc1/cfd_tunnel/t1").mock(
        return_value=httpx.Response(200, json={"success": True})
    )
    result = tunnels.delete_tunnel(client, "acc1", "t1")
    assert result["status"] == "deleted"


@respx.mock
def test_cache_purge_all(client):
    respx.post(f"{BASE}/zones/z1/purge_cache").mock(
        return_value=httpx.Response(200, json={"success": True, "result": {"id": "purge1"}})
    )
    result = cache.purge_all(client, "z1")
    assert result["status"] == "purged"


@respx.mock
def test_cache_purge_urls(client):
    respx.post(f"{BASE}/zones/z1/purge_cache").mock(
        return_value=httpx.Response(200, json={"success": True, "result": {"id": "purge2"}})
    )
    result = cache.purge_urls(client, "z1", ["https://example.com/page1"])
    assert result["urls_purged"] == 1


@respx.mock
def test_cache_purge_urls_too_many(client):
    with pytest.raises(ValueError, match="Maximum 30"):
        cache.purge_urls(client, "z1", [f"https://example.com/{i}" for i in range(31)])
