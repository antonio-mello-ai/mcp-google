---
title: Operations — MCP Google
kind: runbook
area: operations
project: mcp-google
collection: mcp-google
owner: maintainers
status: current
canonical: docs/operacao.md
globalRef: qmd://mcp-google/docs/operacao.md
reviewCadenceDays: 90
lastReviewedAt: 2026-09-28
sourceRefs:
  - README.md
  - .env.example
  - .github/workflows/ci.yml
  - .github/workflows/publish.yml
related:
  - docs/fluxos-negocio.md
  - docs/arquitetura.md
  - docs/index.md
supersedes: []
supersededBy: []
sensitivity: public
---
# Operations

## Local installation

```bash
git config core.hooksPath .githooks
uv sync --all-extras --all-groups
```

Configure `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET` and
`GOOGLE_ACCOUNTS_JSON` outside the repository. `.env.example` contains only
placeholders and may be copied locally to a gitignored file.

## Credential handling

- Treat client secrets and refresh tokens as credentials.
- Do not pass secret values in command-line arguments that will be retained in
  shell history or process listings.
- Do not print complete credentials into terminal transcripts or shared logs.
- Do not place real account inventories in documentation, issues or tests.
- Rotate or revoke a token if it is exposed.

The setup-helper improvement and safe-output requirements are tracked in
[Issue #5](https://github.com/antonio-mello-ai/mcp-google/issues/5).

## Run

```bash
uv run mcp-google
```

The process communicates over stdio. Keep stdout reserved for the MCP protocol;
operational diagnostics should not include credentials or message content.

## Validation

```bash
uv run --all-extras --all-groups pytest -q
uvx ruff check src/ tests/
uvx ruff format --check src/ tests/
gitleaks git --redact --no-banner --log-opts='--all' .
```

CI runs lint, formatting and tests on Python 3.12 and 3.13 for pushes and pull
requests targeting `main`.

## Release

Publishing a GitHub Release triggers the PyPI workflow with trusted publishing.
Before publishing, verify that the tag and package/runtime versions agree. The
version-source correction is tracked in
[Issue #9](https://github.com/antonio-mello-ai/mcp-google/issues/9).

## Failure modes

| Symptom | Check |
| --- | --- |
| Configuration rejected at startup | Confirm all three required environment variables and valid account JSON. |
| Account not found | Pass an account exactly present in the configured account list. |
| OAuth refresh failure | Re-authorize the account; improved classification/retry is tracked in Issue #3. |
| Empty body for a valid message | Check whether it is HTML-only or nested MIME; see Issue #10. |
| Calendar result crosses a local day boundary | Current calculations use UTC; see Issue #8. |

Roadmap and operational follow-ups belong in GitHub Issues, not in this runbook.
