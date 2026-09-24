# TABERBNACLEFX- + Composio GitHub

This repo contains a small Python client for connecting Composio to GitHub. It can list the available GitHub tools, read repository metadata, and create an issue after you authorize GitHub in Composio.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

In `.env`, set your Composio API key and connected-user ID:

```env
COMPOSIO_API_KEY=your_api_key_here
COMPOSIO_USER_ID=user-123
GITHUB_OWNER=innocentaluma11-rgb
GITHUB_REPO=TABERBNACLEFX-
```

In the Composio dashboard, connect the **GitHub** toolkit and authorize the GitHub account that should be used. Keep `.env` local; it is ignored by Git.

## First real GitHub tool call

List the GitHub tools exposed to your connected account:

```bash
python app.py tools
```

Then read this repository through Composio:

```bash
python app.py repo
```

The command uses the first compatible repository-read slug returned by the installed SDK (`GITHUB_GET_REPOSITORY`, `GITHUB_GET_REPO`, or `GITHUB_GET_REPOS`).

## Optional write call: create an issue

After verifying the read call, create an issue:

```bash
python app.py issue \
  --title "Composio integration test" \
  --body "Created by the TABERBNACLEFX- Composio GitHub demo."
```

This performs a real write against `GITHUB_OWNER/GITHUB_REPO`, so only run it when you intend to create the issue.

## Troubleshooting

- If authentication fails, reconnect GitHub in Composio and verify `COMPOSIO_USER_ID`.
- If a tool name is not found, run `python app.py tools` and use the exact slug shown by your SDK version.
- Never commit `COMPOSIO_API_KEY` or `.env`.
