from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

try:
    import MetaTrader5 as mt5  # type: ignore
except Exception:  # pragma: no cover
    mt5 = None


@dataclass(frozen=True)
class PaperOrder:
    symbol: str
    side: str
    volume: float
    stop_loss: float | None = None
    take_profit: float | None = None
    comment: str = "TABERBNACLEFX-paper"


class MT5PaperExecutor:
    """Demo-account-only order executor with a separate execution approval gate."""

    def __init__(self, terminal_path: str | None = None) -> None:
        self.terminal_path = terminal_path

    def validate_second_approval(self, approval_token: str | None, expected_token: str | None) -> None:
        if not approval_token or not expected_token or approval_token != expected_token:
            raise PermissionError("A valid second execution approval token is required.")

    def execute(
        self,
        order: PaperOrder,
        *,
        risk_approved: bool,
        approval_token: str | None,
        expected_token: str | None,
        demo_account: bool,
    ) -> dict[str, Any]:
        if not risk_approved:
            raise PermissionError("Risk approval is required before execution.")
        self.validate_second_approval(approval_token, expected_token)
        if not demo_account:
            raise PermissionError("Paper executor refuses to run unless demo_account=True.")
        if order.side not in {"buy", "sell"}:
            raise ValueError("Order side must be buy or sell.")
        if order.volume <= 0:
            raise ValueError("Order volume must be positive.")

        base = {
            "mode": "paper",
            "symbol": order.symbol.upper(),
            "side": order.side,
            "volume": order.volume,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        if mt5 is None:
            return {**base, "status": "simulated", "reason": "MetaTrader5 package unavailable"}

        if not mt5.initialize(path=self.terminal_path or ""):
            return {**base, "status": "simulated", "reason": "MT5 initialize failed"}

        try:
            symbol = order.symbol.upper()
            tick = mt5.symbol_info_tick(symbol)
            if tick is None:
                return {**base, "status": "rejected", "reason": f"No tick data for {symbol}"}
            order_type = mt5.ORDER_TYPE_BUY if order.side == "buy" else mt5.ORDER_TYPE_SELL
            price = float(tick.ask if order.side == "buy" else tick.bid)
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": order.volume,
                "type": order_type,
                "price": price,
                "sl": order.stop_loss or 0.0,
                "tp": order.take_profit or 0.0,
                "deviation": 20,
                "magic": 260924,
                "comment": order.comment,
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            result = mt5.order_send(request)
            if result is None:
                return {**base, "status": "rejected", "reason": str(mt5.last_error())}
            return {
                **base,
                "status": "submitted",
                "retcode": int(result.retcode),
                "order": int(getattr(result, "order", 0)),
                "deal": int(getattr(result, "deal", 0)),
                "comment": str(getattr(result, "comment", "")),
            }
        finally:
            mt5.shutdown()
