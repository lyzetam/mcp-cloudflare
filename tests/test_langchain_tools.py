"""Tests for LangChain tool interfaces."""

from langchain_core.tools import BaseTool

from mcp_cloudflare.langchain_tools import TOOLS


def test_tools_count():
    assert len(TOOLS) == 19


def test_all_tools_are_base_tool():
    for t in TOOLS:
        assert isinstance(t, BaseTool), f"{t} is not a BaseTool"


def test_tool_names_follow_convention():
    for t in TOOLS:
        assert t.name.startswith("cf_"), f"Tool {t.name} does not follow cf_ naming convention"


def test_tool_names_are_unique():
    names = [t.name for t in TOOLS]
    assert len(names) == len(set(names)), f"Duplicate tool names: {names}"


def test_expected_tools_present():
    names = {t.name for t in TOOLS}
    expected = {
        "cf_status",
        "cf_zone_list",
        "cf_zone_get",
        "cf_zone_settings",
        "cf_dns_list",
        "cf_dns_create",
        "cf_dns_update",
        "cf_dns_delete",
        "cf_tunnel_list",
        "cf_tunnel_get",
        "cf_tunnel_create",
        "cf_tunnel_delete",
        "cf_tunnel_configurations",
        "cf_tunnel_update_config",
        "cf_cache_purge_all",
        "cf_cache_purge_urls",
        "cf_cache_purge_tags",
        "cf_cache_purge_prefixes",
        "cf_account_list",
    }
    assert expected == names


def test_all_tools_have_descriptions():
    for t in TOOLS:
        assert t.description, f"Tool {t.name} has no description"
