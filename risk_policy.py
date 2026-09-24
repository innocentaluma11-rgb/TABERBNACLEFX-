from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class RiskDecision:
    allowed: bool
    reasons: list[str]
    max_position: float
    confidence: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "allowed": self.allowed,
            "reasons": self.reasons,
            "max_position": self.max_position,
            "confidence": self.confidence,
        }


class RiskGate:
    """Prevents unsafe or unauthorized actions from reaching the tools layer."""

    def __init__(
        self,
        allowed_symbols: tuple[str, ...],
        max_daily_loss: float,
        max_position_size: float,
        min_confidence: float,
    ) -> None:
        self.allowed_symbols = tuple(s.upper() for s in allowed_symbols)
        self.max_daily_loss = max_daily_loss
        self.max_position_size = max_position_size
        self.min_confidence = min_confidence

    def evaluate(self, recommendation: dict[str, Any], account: dict[str, Any]) -> RiskDecision:
        reasons: list[str] = []
        signal = str(recommendation.get("signal", "hold")).lower()
        confidence = float(recommendation.get("confidence", 0.0))
        symbol = str(recommendation.get("symbol", "UNKNOWN")).upper()

        if symbol not in self.allowed_symbols:
            reasons.append(f"Symbol {symbol} is not allowed")
        if signal == "hold":
            reasons.append("Signal is not actionable")
        if confidence < self.min_confidence:
            reasons.append(f"Confidence {confidence} is below minimum {self.min_confidence}")
        if float(account.get("equity", 0.0)) <= 0:
            reasons.append("Account equity is non-positive")
        if self.max_daily_loss <= 0:
            reasons.append("Daily loss limit is invalid")

        max_position = min(self.max_position_size, self.max_daily_loss / max(float(account.get("equity", 1.0)) or 1.0, 1.0))
        allowed = len(reasons) == 0 and signal in {"buy", "sell"}
        return RiskDecision(allowed=allowed, reasons=reasons, max_position=max_position, confidence=confidence)
