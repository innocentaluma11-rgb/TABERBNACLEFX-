from __future__ import annotations

import argparse
import json
import os
from typing import Any

from claude_service import ClaudeAdvisor
from composio import Composio
from config import get_settings
from mt5_service import build_market_report
from risk_policy import RiskGate


def publish_to_social(platform: str, text: str, media_url: str | None = None, confirm: bool = False) -> dict[str, Any]:
    if not confirm:
        raise RuntimeError("Social publishing requires --confirm to prevent accidental posts.")

    settings = get_settings()
    api_key = settings.composio_api_key
    if not api_key:
        raise RuntimeError("Set COMPOSIO_API_KEY in your environment before publishing.")

    client = Composio(api_key=api_key)
    slug = settings.publish_tool_slug(platform)
    if not slug:
        raise RuntimeError(
            f"Set COMPOSIO_{platform.upper()}_PUBLISH_TOOL in .env after running `python social_workflow.py discover --platform {platform}`."
        )

    arguments: dict[str, Any] = {"text": text, "caption": text}
    if media_url:
        arguments.update({"media_url": media_url, "video_url": media_url})
    return client.tools.execute(slug, arguments=arguments, user_id=settings.composio_user_id)


def run_workflow(symbol: str, platform: str, confirm: bool = False) -> dict[str, Any]:
    settings = get_settings()
    errors = settings.validate()
    if errors:
        return {"status": "configuration_error", "errors": errors}

    report = build_market_report(symbol, settings.mt5_terminal_path)
    advisor = ClaudeAdvisor(api_key=settings.anthropic_api_key)
    recommendation = advisor.analyze(report, report["account"], symbol)
    recommendation["symbol"] = symbol.upper()
    recommendation["platform"] = platform

    gate = RiskGate(
        allowed_symbols=settings.allowed_symbols,
        max_daily_loss=settings.max_daily_loss,
        max_position_size=settings.max_position_size,
        min_confidence=settings.min_confidence,
    )
    decision = gate.evaluate(recommendation, report["account"])

    if not decision.allowed:
        return {
            "status": "denied",
            "recommendation": recommendation,
            "risk": decision.to_dict(),
            "market": report,
        }

    if not confirm:
        return {
            "status": "pending_approval",
            "recommendation": recommendation,
            "risk": decision.to_dict(),
            "market": report,
        }

    if platform not in settings.social_platforms:
        return {
            "status": "platform_not_allowed",
            "platform": platform,
            "allowed_platforms": settings.social_platforms,
        }

    publish = publish_to_social(
        platform,
        recommendation.get("social_caption", "Market check"),
        media_url=None,
        confirm=confirm,
    )
    return {
        "status": "approved_and_published",
        "recommendation": recommendation,
        "risk": decision.to_dict(),
        "market": report,
        "publish": publish,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Approve-or-deny structured MT5 + Claude + social workflow")
    parser.add_argument("--symbol", default="EURUSD")
    parser.add_argument("--platform", default="instagram")
    parser.add_argument("--confirm", action="store_true")
    args = parser.parse_args()
    print(json.dumps(run_workflow(args.symbol, args.platform, confirm=args.confirm), indent=2, default=str))


if __name__ == "__main__":
    main()
