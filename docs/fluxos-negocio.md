---
title: Product flows — MCP Google
kind: guide
area: product
project: mcp-google
collection: mcp-google
owner: maintainers
status: current
canonical: docs/fluxos-negocio.md
globalRef: qmd://mcp-google/docs/fluxos-negocio.md
reviewCadenceDays: 90
lastReviewedAt: 2026-09-28
sourceRefs:
  - README.md
  - src/mcp_google/tools/gmail.py
  - src/mcp_google/tools/calendar.py
related:
  - docs/arquitetura.md
  - docs/operacao.md
  - docs/index.md
supersedes: []
supersededBy: []
sensitivity: public
---
# Product flows

MCP Google exposes a small Gmail and Google Calendar surface to an MCP client.
The operator supplies OAuth configuration for one or more accounts and the
client invokes a registered tool through the MCP server.

## Account selection

`GOOGLE_ACCOUNTS_JSON` defines the available accounts. When a tool receives an
`account`, the server resolves that exact email. When it is omitted, the current
implementation selects the first configured account. Requiring an explicit
account for mutating tools is tracked in
[Issue #7](https://github.com/antonio-mello-ai/mcp-google/issues/7).

## Gmail read flow

1. `gmail_list_unread` lists up to 100 unread message references.
2. The server loads metadata for each reference and returns ID, subject, sender,
   date and snippet.
3. `gmail_get_message` retrieves one message and returns headers, labels and the
   extracted plain-text body.

Arbitrary search, pagination and richer MIME handling are tracked in Issues
[#1](https://github.com/antonio-mello-ai/mcp-google/issues/1),
[#12](https://github.com/antonio-mello-ai/mcp-google/issues/12) and
[#10](https://github.com/antonio-mello-ai/mcp-google/issues/10).

## Gmail send flow

`gmail_send` constructs a plain-text MIME message, sends it through the Gmail
API and returns the new message and thread identifiers. This is an external side
effect. The caller remains responsible for confirming recipient, subject, body
and account before invoking it.

## Calendar read flow

- `calendar_today` lists events between the current UTC day boundaries.
- `calendar_week` lists events between Monday and Sunday using UTC boundaries.
- Both return at most 50 events ordered by start time.

Account-local time-zone handling is tracked in
[Issue #8](https://github.com/antonio-mello-ai/mcp-google/issues/8).

## Calendar write flow

`calendar_create_event` inserts an event in the primary calendar from a title
and explicit ISO 8601 start/end values. This is an external side effect. Updating
and deleting events remain planned under
[Issue #2](https://github.com/antonio-mello-ai/mcp-google/issues/2).

## Current boundaries

- The server uses stdio transport.
- Gmail messages are sent as plain text.
- Calendar operations target the primary calendar.
- Credentials are cached only in process memory.
- The repository does not host, proxy or persist mailbox or calendar content.
