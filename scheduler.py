from __future__ import annotations

import argparse
import os
import secrets
import uuid
from typing import Any

from apscheduler.schedulers.blocking import BlockingScheduler

from audit_log import AuditLog
from claude_service import ClaudeAdvisor
from config import get_settings
from mt5_execution import MT5PaperExecutor, PaperOrder
from mt5_service import build_market_report
from risk_policy import RiskGate


def check_market(symbol: str, log: AuditLog, execute: bool, approval_token: str | None) -> dict[str, Any]:
    settings = get_settings()
    correlation_id = str(uuid.uuid4())
    report = build_market_report(symbol, settings.mt5_terminal_path)
    log.record("market_snapshot", correlation_id, report)

    recommendation = ClaudeAdvisor(settings.anthropic_api_key).analyze(
        report, report["account"], symbol
    )
    recommendation["symbol"] = symbol.upper()
    log.record("recommendation", correlation_id, recommendation)

    decision = RiskGate(
        settings.allowed_symbols,
        settings.max_daily_loss,
        settings.max_position_size,
        settings.min_confidence,
    ).evaluate(recommendation, report["account"])
    log.record("risk_decision", correlation_id, decision.to_dict())

    result: dict[str, Any] = {"correlation_id": correlation_id, "risk": decision.to_dict()}
    if not execute or not decision.allowed:
        result["status"] = "pending_approval" if decision.allowed else "denied"
        return result

    side = str(recommendation.get("signal", "hold")).lower()
    order = PaperOrder(symbol=symbol, side=side, volume=decision.max_position)
    try:
        execution = MT5PaperExecutor(settings.mt5_terminal_path).execute(
            order,
            risk_approved=decision.allowed,
            approval_token=approval_token,
            expected_token=os.getenv("PAPER_EXECUTION_APPROVAL_TOKEN"),
            demo_account=os.getenv("APP_ENV", "development").lower() == "paper"
            and os.getenv("MT5_DEMO_ONLY", "true").lower() == "true",
        )
    except Exception as exc:
        execution = {"status": "blocked", "error": str(exc)}
    log.record("paper_execution", correlation_id, execution)
    result.update({"status": execution.get("status", "unknown"), "execution": execution})
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Paper-trading scheduler with audit logging")
    parser.add_argument("--symbol", default="EURUSD")
    parser.add_argument("--interval", type=int, default=5, help="Minutes between market checks")
    parser.add_argument("--audit-db", default="data/audit.sqlite3")
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--execute-approved", action="store_true", help="Enable the second approval path")
    parser.add_argument("--approval-token", help="Must match PAPER_EXECUTION_APPROVAL_TOKEN")
    args = parser.parse_args()

    log = AuditLog(args.audit_db)
    job = lambda: print(check_market(args.symbol, log, args.execute_approved, args.approval_token))
    if args.once:
        job()
        return

    scheduler = BlockingScheduler(timezone="UTC")
    scheduler.add_job(job, "interval", minutes=args.interval, id="market-check", max_instances=1, coalesce=True)
    print(f"Paper scheduler running every {args.interval} minute(s). Audit DB: {args.audit_db}")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown(wait=False)


if __name__ == "__main__":
    main()
