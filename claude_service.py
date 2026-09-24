from __future__ import annotations

import json
from typing import Any

try:
    import anthropic  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    anthropic = None


class ClaudeAdvisor:
    """Builds a structured recommendation for market conditions."""

    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key
        self.client = anthropic.Anthropic(api_key=api_key) if api_key and anthropic is not None else None

    def analyze(self, market: dict[str, Any], account: dict[str, Any], symbol: str) -> dict[str, Any]:
        if self.client is not None:
            try:
                return self._ask_claude(market, account, symbol)
            except Exception:
                pass
        return self._fallback_analysis(market, account, symbol)

    def _ask_claude(self, market: dict[str, Any], account: dict[str, Any], symbol: str) -> dict[str, Any]:
        prompt = f"""You are a disciplined market analyst for {symbol}. Only return JSON with keys: analysis, signal, confidence, rationale, social_caption, risk_level.

Market: {json.dumps(market, sort_keys=True)}
Account: {json.dumps(account, sort_keys=True)}

Rules:
- Be risk-aware and conservative.
- If signal is not clear, choose 'hold'.
- Keep content safe for social channels.
"""
        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=512,
            messages=[{"role": "user", "content": prompt}],
        )
        text = response.content[0].text  # type: ignore[index]
        return json.loads(text)

    def _fallback_analysis(self, market: dict[str, Any], account: dict[str, Any], symbol: str) -> dict[str, Any]:
        snapshot = market.get("market", {})
        trend = snapshot.get("trend", "neutral")
        spread = float(snapshot.get("spread_points", 0.0))
        confidence = 0.72 if trend != "neutral" and spread < 0.02 else 0.5
        action = "buy" if trend == "bullish" else "sell" if trend == "bearish" else "hold"
        return {
            "analysis": f"{symbol} is showing a {trend} bias with modest spread risk.",
            "signal": action,
            "confidence": confidence,
            "rationale": "Structured fallback model: trend direction and spread risk determine the action.",
            "social_caption": f"Market review for {symbol}: trend is {trend}. Use disciplined risk management before entering.",
            "risk_level": "medium" if confidence >= 0.6 else "low",
        }
