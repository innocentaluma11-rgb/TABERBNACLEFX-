# TABERBNACLEFX- + Composio GitHub, MT5, and social workflow

This Python repo provides a safe starting point for connecting Composio to GitHub and to social toolkits for Instagram, TikTok, and YouTube. It does **not** place trades or publish content automatically: every external write requires an explicit command and confirmation.

## Install and configure

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Set `COMPOSIO_API_KEY` and `COMPOSIO_USER_ID` in `.env`. Never commit `.env`, API keys, broker credentials, or refresh tokens.

## Social connection workflow

Connect each account in the browser:

```bash
python social_workflow.py connect --platform instagram
python social_workflow.py connect --platform tiktok
python social_workflow.py connect --platform youtube
```

Discover the actions actually available in your Composio workspace. Tool names can vary by SDK/catalog version, so do not hard-code an unverified slug:

```bash
python social_workflow.py discover --platform instagram
python social_workflow.py discover --platform tiktok
python social_workflow.py discover --platform youtube
```

Copy the exact publish action into the corresponding `COMPOSIO_*_PUBLISH_TOOL` variable in `.env`. Then make an explicit, real call:

```bash
python social_workflow.py publish \
  --platform instagram \
  --text "Market structure update: BTC is respecting the weekly range." \
  --media-url "https://example.com/public-image.jpg" \
  --confirm
```

The `--confirm` flag is mandatory. Start with a private/test account and verify each platform's media requirements before publishing.

## MT5 + Claude operating model

Use Claude to produce a proposed market-analysis or social-content object, then require a human/risk gate before any side effect:

1. MT5 read-only market data and account state.
2. Claude analyzes the data and returns structured JSON: `analysis`, `signal`, `risk`, and optional `content`.
3. Validate position size, stop loss, daily loss, and allowed symbols locally.
4. Review/approve the trade or content.
5. Execute one narrowly scoped Composio/MT5/social action.
6. Log the request, response, approval, and external result without storing secrets.

This repository currently contains the Composio client and social workflow scaffold; it does not yet contain an MT5 execution engine or Claude API client. Add those behind the approval gate rather than allowing an LLM to call a broker or publish directly.

## Existing GitHub flow

```bash
python app.py connect
python app.py tools
python app.py repo
```

To create a GitHub issue, use the explicit write command documented in `app.py`/the prior README version.

## Safety notes

- Keep trading in paper/demo mode until the full path is tested.
- Do not let Claude decide credentials, account IDs, leverage, or publish permissions.
- Do not auto-publish trade calls or performance claims without review.
- Use allowlists for symbols, platforms, and Composio action slugs.
