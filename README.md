# TABERBNACLEFX- + Composio GitHub + MT5 + social architecture

This repo now includes a layered architecture for a disciplined trading-and-publishing workflow:

- `mt5_service.py` reads market/account information, with a read-only demo fallback when MT5 is not installed or connected.
- `claude_service.py` produces a structured recommendation from the market and account context.
- `risk_policy.py` gate-keeps the recommendation with a conservative safety model.
- `workflow.py` orchestrates the end-to-end decision path and blocks unsafe actions.
- `social_workflow.py` handles the Composio social-tool OAuth and publish flow.

## Safe control flow

1. Read market + account state from MT5 or demo data.
2. Ask Claude for a structured recommendation.
3. Validate the recommendation against the risk gate.
4. Require explicit approval before any external action.
5. Publish to Instagram/TikTok/YouTube only via a verified Composio slug.

## Configuration

```bash
cp .env.example .env
```

Add your credentials and allowlists in `.env`:

```env
COMPOSIO_API_KEY=...
COMPOSIO_USER_ID=...
GITHUB_OWNER=innocentaluma11-rgb
GITHUB_REPO=TABERBNACLEFX-
ALLOWED_SYMBOLS=EURUSD,GBPUSD,USDJPY,XAUUSD
MAX_DAILY_LOSS=250.0
MAX_POSITION_SIZE=0.10
MIN_CONFIDENCE=0.6
DEFAULT_SOCIAL_PLATFORM=instagram
COMPOSIO_INSTAGRAM_TOOLKIT=instagram
COMPOSIO_TIKTOK_TOOLKIT=tiktok
COMPOSIO_YOUTUBE_TOOLKIT=youtube
```

Then discover the exact publish slugs for each platform:

```bash
python social_workflow.py discover --platform instagram
python social_workflow.py discover --platform tiktok
python social_workflow.py discover --platform youtube
```

After verifying the slugs, set them in `.env`, for example:

```env
COMPOSIO_INSTAGRAM_PUBLISH_TOOL=paste_exact_slug_here
```

## Run the workflow

Preview the recommendation without publishing:

```bash
python workflow.py --symbol EURUSD --platform instagram
```

Execute the approved action with an explicit and intentional confirmation:

```bash
python workflow.py --symbol EURUSD --platform instagram --confirm
```

## Social OAuth and publishing

Connect each platform to Composio:

```bash
python social_workflow.py connect --platform instagram
python social_workflow.py connect --platform tiktok
python social_workflow.py connect --platform youtube
```

Publish a post only after the exact tool slug is known and `--confirm` is supplied:

```bash
python social_workflow.py publish --platform instagram --text "Market structure update: EURUSD is cleaning up after a shallow retracement." --confirm
```

## Safety rules

- MT5 access is read-only unless you add a separate, explicit execution path.
- The model is not allowed to decide credentials, broker settings, or publish permissions.
- Social posts require `--confirm`.
- The risk gate blocks low-confidence or disallowed symbols.
- Keep all credentials and secrets out of Git.
