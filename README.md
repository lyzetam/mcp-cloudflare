# mcp-cloudflare

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Cloudflare operations as a Python library, LangChain tools, and MCP server.

## Features

- **19 LangChain tools** for use with LangChain/LangGraph agents
- **19 MCP tools** for use with Claude Code and other MCP clients
- **Modular operations layer** usable as a standalone Python library
- Covers **Zones**, **DNS**, **Tunnels**, **Cache**, and **Accounts**

### MCP Tools

| Category | Tools |
|----------|-------|
| Status | `cloudflare_status` |
| Zones | `zone_list`, `zone_get`, `zone_settings` |
| DNS | `dns_list`, `dns_create`, `dns_update`, `dns_delete` |
| Tunnels | `tunnel_list`, `tunnel_get`, `tunnel_create`, `tunnel_delete`, `tunnel_configurations`, `tunnel_update_config` |
| Cache | `cache_purge_all`, `cache_purge_urls`, `cache_purge_tags`, `cache_purge_prefixes` |
| Accounts | `account_list` |

### LangChain Tools

| Category | Tools |
|----------|-------|
| Status | `cf_status` |
| Zones | `cf_zone_list`, `cf_zone_get`, `cf_zone_settings` |
| DNS | `cf_dns_list`, `cf_dns_create`, `cf_dns_update`, `cf_dns_delete` |
| Tunnels | `cf_tunnel_list`, `cf_tunnel_get`, `cf_tunnel_create`, `cf_tunnel_delete`, `cf_tunnel_configurations`, `cf_tunnel_update_config` |
| Cache | `cf_cache_purge_all`, `cf_cache_purge_urls`, `cf_cache_purge_tags`, `cf_cache_purge_prefixes` |
| Accounts | `cf_account_list` |

## Installation

```bash
# Core library only (httpx)
pip install .

# With MCP server support
pip install ".[mcp]"

# With LangChain tools
pip install ".[langchain]"

# Everything
pip install ".[all]"
```

## Configuration

All settings are read from environment variables with the `CLOUDFLARE_` prefix, or from a `.env` file.

| Variable | Description | Default |
|----------|-------------|---------|
| `CLOUDFLARE_API_TOKEN` | Cloudflare API token | `""` |
| `CLOUDFLARE_ACCOUNT_ID` | Cloudflare account ID | `""` |

## Quick Start

### As a Python library

```python
from mcp_cloudflare.client import CloudflareClient
from mcp_cloudflare.operations import dns, zones

client = CloudflareClient()
zone_list = zones.list_zones(client)
records = dns.list_records(client, zone_id="...")
```

### As LangChain tools

```python
from mcp_cloudflare.langchain_tools import TOOLS

# Use with a LangChain agent
agent = create_react_agent(llm, TOOLS)
```

### As an MCP server

```bash
mcp-cloudflare
```

### `.env` example

```env
CLOUDFLARE_API_TOKEN=your-api-token
CLOUDFLARE_ACCOUNT_ID=your-account-id
```

## License

MIT
