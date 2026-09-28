---
title: AGENTS.md — MCP Google
kind: policy
area: engineering
project: mcp-google
collection: mcp-google
owner: maintainers
status: current
canonical: AGENTS.md
globalRef: qmd://mcp-google/AGENTS.md
reviewCadenceDays: 90
lastReviewedAt: 2026-09-28
sourceRefs:
  - github:antonio-mello-ai/mcp-google
related:
  - README.md
  - docs/fluxos-negocio.md
  - docs/arquitetura.md
  - docs/operacao.md
  - docs/index.md
supersedes:
  - CLAUDE.md
  - GEMINI.md
supersededBy: []
sensitivity: public
---
# AGENTS.md — MCP Google

## Purpose

This repository provides a public, self-hostable MCP server for Gmail and
Google Calendar. Keep code, examples, issues and documentation generic and safe
for public collaboration.

## Public repository boundary

- Never commit OAuth client secrets, refresh tokens, access tokens, real account
  inventories, private hostnames, local user paths or internal topology.
- Use placeholders and reserved examples in documentation and tests.
- Do not copy operational context from private deployments into this repository.
- Treat Gmail sending and Calendar writes as external side effects. Tests must
  mock Google APIs and must not depend on live accounts.

## Stack

- Python 3.12+
- FastMCP
- Google Gmail and Calendar APIs
- `uv`, Ruff and pytest

## Local setup and validation

```bash
git config core.hooksPath .githooks
uv sync --all-extras --all-groups
uv run --all-extras --all-groups pytest -q
uvx ruff check src/ tests/
uvx ruff format --check src/ tests/
```

The current versioning inconsistency is tracked in GitHub Issue #9. Do not add
another version source while resolving it.

## Documentation sources of truth

- `README.md`: public installation and usage entry point
- `docs/fluxos-negocio.md`: behavior exposed to MCP clients
- `docs/arquitetura.md`: implementation model and boundaries
- `docs/operacao.md`: self-hosting, credentials, validation and release operation
- `docs/index.md`: navigable documentation index

Roadmap, backlog and priority live in GitHub Issues and the Felhen GitHub
Project. Delivery history lives in closed Issues, pull requests and GitHub
Releases. Do not add `roadmap.md`, `docs/backlog.md` or `CHANGELOG.md`.
