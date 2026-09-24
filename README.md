# TABERBNACLEFX- + Composio GitHub

This repo contains a small Python client for connecting Composio to GitHub. It can start the GitHub OAuth flow, list the tools exposed to the connected account, read repository metadata, and create an issue.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Set `COMPOSIO_API_KEY` in `.env`. Keep `.env` local; it is ignored by Git. `COMPOSIO_USER_ID` identifies the Composio user whose GitHub connection will be used.

## Connect GitHub

Run:

```bash
python app.py connect
```

Open the printed URL, authorize GitHub, and return to the terminal. To print the URL without waiting:

```bash
python app.py connect --no-wait
```

## First real tool call

After authorization, discover the GitHub tools available to your account:

```bash
python app.py tools
```

Then make a real read call against this repository through Composio:

```bash
python app.py repo
```

The command tries the compatible repository-read slug returned by the installed SDK (`GITHUB_GET_REPOSITORY`, `GITHUB_GET_REPO`, or `GITHUB_GET_REPOS`).

## Optional write call

After verifying the read call, create an issue only when you intend to perform a real write:

```bash
python app.py issue \
  --title "Composio integration test" \
  --body "Created by the TABERBNACLEFX- Composio GitHub demo."
```

## Troubleshooting

- If `connect` is unavailable, upgrade the SDK: `pip install --upgrade composio`.
- If authentication fails, reconnect GitHub and verify `COMPOSIO_USER_ID`.
- If a tool name is not found, run `python app.py tools` and use the exact slug shown by your SDK version.
- Never commit `COMPOSIO_API_KEY` or `.env`.
