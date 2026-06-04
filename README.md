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

Use the [Google OAuth Playground](https://developers.google.com/oauthplayground/) or run a local OAuth flow:

```bash
# Quick method via oauth2l
pip install google-auth-oauthlib
python -c "
from google_auth_oauthlib.flow import InstalledAppFlow
flow = InstalledAppFlow.from_client_config(
    {'installed': {'client_id': 'YOUR_CLIENT_ID', 'client_secret': 'YOUR_SECRET', 'auth_uri': 'https://accounts.google.com/o/oauth2/auth', 'token_uri': 'https://oauth2.googleapis.com/token'}},
    scopes=['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.send', 'https://www.googleapis.com/auth/calendar.readonly', 'https://www.googleapis.com/auth/calendar.events']
)
creds = flow.run_local_server(port=0)
print(f'Refresh token: {creds.refresh_token}')
"
```

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
