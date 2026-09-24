from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from typing import Any

try:
    import MetaTrader5 as mt5  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    mt5 = None


@dataclass
class MarketSnapshot:
    symbol: str
    bid: float
    ask: float
    spread_points: float
    trend: str
    volatility: float
    timestamp: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class MT5MarketService:
    """Read-only market access for MT5. Falls back to demo data when MT5 is unavailable."""

    def __init__(self, terminal_path: str | None = None) -> None:
        self.terminal_path = terminal_path

    def get_market_snapshot(self, symbol: str) -> MarketSnapshot:
        if mt5 is not None:
            return self._from_mt5(symbol)
        return self._demo_snapshot(symbol)

    def _from_mt5(self, symbol: str) -> MarketSnapshot:
        if not mt5.initialize(path=self.terminal_path or "", login=0, password="", server=""):
            return self._demo_snapshot(symbol)

        try:
            ticks = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M1, 0, 50)
            if ticks is None or len(ticks) == 0:
                return self._demo_snapshot(symbol)

            last = ticks[-1]
            close = float(last[4])
            open_ = float(last[1])
            bid = float(last[2])
            ask = float(last[3])
            diff = close - open_
            trend = "bullish" if diff >= 0 else "bearish"
            volatility = abs(float(last[7]) - float(last[8])) / max(close, 1e-6)
            return MarketSnapshot(
                symbol=symbol.upper(),
                bid=bid,
                ask=ask,
                spread_points=max(ask - bid, 0.0),
                trend=trend,
                volatility=volatility,
                timestamp=str(last[0]),
            )
        finally:
            mt5.shutdown()

    def _demo_snapshot(self, symbol: str) -> MarketSnapshot:
        base = 1.0
        symbol_upper = symbol.upper()
        if "JPY" in symbol_upper:
            base = 150.0
        elif "XAU" in symbol_upper:
            base = 2300.0
        elif "BTC" in symbol_upper:
            base = 62000.0

        bid = base * 0.9992
        ask = base * 1.0008
        trend = "bullish" if symbol_upper.endswith("USD") or "XAU" in symbol_upper else "neutral"
        return MarketSnapshot(
            symbol=symbol_upper,
            bid=bid,
            ask=ask,
            spread_points=ask - bid,
            trend=trend,
            volatility=0.003,
            timestamp="demo",
        )

    def account_summary(self) -> dict[str, Any]:
        if mt5 is not None:
            try:
                account = mt5.account_info()
                if account is not None:
                    return {
                        "balance": float(account.balance),
                        "equity": float(account.equity),
                        "margin_free": float(account.margin_free),
                        "currency": str(account.currency),
                    }
            except Exception:
                pass
        return {"balance": 10000.0, "equity": 9900.0, "margin_free": 3000.0, "currency": "USD"}


def build_market_report(symbol: str, terminal_path: str | None = None) -> dict[str, Any]:
    service = MT5MarketService(terminal_path=terminal_path)
    snapshot = service.get_market_snapshot(symbol)
    account = service.account_summary()
    return {
        "market": snapshot.to_dict(),
        "account": account,
    }
