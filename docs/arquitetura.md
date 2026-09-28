---
title: Architecture — MCP Google
kind: architecture
area: engineering
project: mcp-google
collection: mcp-google
owner: maintainers
status: current
canonical: docs/arquitetura.md
globalRef: qmd://mcp-google/docs/arquitetura.md
reviewCadenceDays: 90
lastReviewedAt: 2026-09-28
sourceRefs:
  - pyproject.toml
  - src/mcp_google
related:
  - docs/fluxos-negocio.md
  - docs/operacao.md
  - docs/index.md
supersedes: []
supersededBy: []
sensitivity: public
---
# Architecture

## Components

| Component | Responsibility |
| --- | --- |
| `server.py` | Creates the FastMCP server, registers tool modules and starts stdio transport. |
| `config.py` | Parses OAuth client configuration and the account list from environment variables. |
| `auth.py` | Resolves an account, builds Google credentials, refreshes tokens and maintains the in-memory cache. |
| `tools/gmail.py` | Implements Gmail list, read and send operations. |
| `tools/calendar.py` | Implements Calendar day/week listing and event creation. |

## Request path

```text
MCP client
  -> FastMCP tool registration
  -> environment-backed GoogleConfig
  -> account resolution and credential refresh/cache
  -> Google API client
  -> normalized dictionary/list response
```

The server has no application database. Google remains the system of record;
only OAuth credentials are cached in memory for the process lifetime.

## Authentication boundary

OAuth client ID, client secret and refresh tokens enter through environment
variables. They must be injected by the operator from a local secret source and
must never be committed or copied into public issues and logs.

The current credentials request the combined Gmail read/send and Calendar
read/write scopes. Least-privilege scope profiles are tracked in
[Issue #11](https://github.com/antonio-mello-ai/mcp-google/issues/11), while
refresh failure handling is tracked in
[Issue #3](https://github.com/antonio-mello-ai/mcp-google/issues/3).

## Safety boundaries

- Unit tests mock the Google API and do not use live accounts.
- Tool risk annotations are planned in
  [Issue #13](https://github.com/antonio-mello-ai/mcp-google/issues/13).
- Explicit account selection for external mutations is tracked in Issue #7.
- Public examples use placeholders rather than real accounts or credentials.

## Known structural gaps

- Package and runtime version sources are inconsistent; see
  [Issue #9](https://github.com/antonio-mello-ai/mcp-google/issues/9).
- List operations do not expose continuation state; see Issue #12.
- Calendar day/week boundaries currently use UTC; see Issue #8.
- MIME extraction is deliberately narrow; see Issue #10.
