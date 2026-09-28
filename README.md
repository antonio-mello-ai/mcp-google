# mcp-google

MCP server for Google APIs — Gmail and Calendar tools for LLM agents.

## Install

```bash
# Run directly with uvx (no install needed)
uvx mcp-google

# Or install with pip
pip install mcp-google
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `GOOGLE_CLIENT_ID` | OAuth2 client ID from Google Cloud Console |
| `GOOGLE_CLIENT_SECRET` | OAuth2 client secret |
| `GOOGLE_ACCOUNTS_JSON` | JSON array of account configs (see below) |

### GOOGLE_ACCOUNTS_JSON format

```json
[
  {"email": "personal@gmail.com", "refresh_token": "1//..."},
  {"email": "work@company.com", "refresh_token": "1//..."}
]
```

The first account in the array is used as default when no `account` parameter is specified.

## Tools

### Phase 1 — Read-only

| Tool | Parameters | Description |
|------|-----------|-------------|
| `gmail_list_unread` | `account?`, `max_results?` | List unread emails (subject, sender, date, snippet) |
| `gmail_get_message` | `message_id`, `account?` | Get full email content by ID |
| `calendar_today` | `account?` | Today's events |
| `calendar_week` | `account?` | This week's agenda |

### Phase 2 — Write

| Tool | Parameters | Description |
|------|-----------|-------------|
| `gmail_send` | `to`, `subject`, `body`, `account?` | Send an email |
| `calendar_create_event` | `title`, `start`, `end`, `account?` | Create a calendar event |

## OAuth Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project (or select existing)
3. Enable **Gmail API** and **Google Calendar API**
4. Go to **Credentials** > **Create Credentials** > **OAuth 2.0 Client ID**
   - Application type: **Desktop app**
   - Note the Client ID and Client Secret
5. Configure OAuth consent screen with required scopes:
   - `https://www.googleapis.com/auth/gmail.readonly`
   - `https://www.googleapis.com/auth/gmail.send`
   - `https://www.googleapis.com/auth/calendar.readonly`
   - `https://www.googleapis.com/auth/calendar.events`
6. Obtain refresh tokens for each account using the OAuth2 flow
7. Set environment variables (copy `.env.example` to `.env` and fill in values)

### Obtaining Refresh Tokens

Use the [Google OAuth Playground](https://developers.google.com/oauthplayground/)
or a local OAuth flow created for a **Desktop app** client. Refresh tokens are
credentials: keep them out of repository files, issues, terminal transcripts,
shell history and shared logs. Store the resulting configuration in a local
secret source and inject it through the environment at runtime.

A first-class setup helper that avoids unsafe output by default is tracked in
[Issue #5](https://github.com/antonio-mello-ai/mcp-google/issues/5).

## Running

```bash
# As MCP server (stdio transport)
mcp-google

# Or directly
python -m mcp_google.server
```

### Claude Desktop config

```json
{
  "mcpServers": {
    "google": {
      "command": "mcp-google",
      "env": {
        "GOOGLE_CLIENT_ID": "...",
        "GOOGLE_CLIENT_SECRET": "...",
        "GOOGLE_ACCOUNTS_JSON": "[{\"email\": \"me@gmail.com\", \"refresh_token\": \"...\"}]"
      }
    }
  }
}
```

## License

MIT

## Documentation and roadmap

- [Current product flows](docs/fluxos-negocio.md)
- [Architecture](docs/arquitetura.md)
- [Operations](docs/operacao.md)
- [Documentation index](docs/index.md)
- [Open roadmap items](https://github.com/antonio-mello-ai/mcp-google/issues)

Priorities live in GitHub Issues and Projects. Delivery history lives in closed
Issues, pull requests and GitHub Releases.
