# Paper deployment: MT5 execution, audit log, and scheduler

The deployment pieces are now included:

- `mt5_execution.py`: demo-only MT5 order path with a separate execution approval token.
- `audit_log.py`: append-only SQLite audit log at `data/audit.sqlite3`.
- `scheduler.py`: recurring market checks with `--once` support for testing.
- `run_paper_trading.bat`: Windows startup command for the scheduler.

## Install on the Windows MT5 host

1. Install MetaTrader 5 and log into a broker **demo** account.
2. Clone this repository to the Windows host.
3. Create and activate a virtual environment:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install MetaTrader5 anthropic
copy .env.example .env
```

4. Set `APP_ENV=paper`, `MT5_DEMO_ONLY=true`, the demo terminal path, and a strong `PAPER_EXECUTION_APPROVAL_TOKEN` in `.env`.
5. Test one cycle without placing an order:

```powershell
.venv\Scripts\python.exe scheduler.py --once --symbol EURUSD
```

This records the market snapshot, Claude/fallback recommendation, and risk decision in `data/audit.sqlite3`. It does not execute an order.

## Second approval gate

The scheduler never executes by default. To enable the paper order path for one intentional run, supply both flags and the exact token stored in `.env`:

```powershell
.venv\Scripts\python.exe scheduler.py --once --symbol EURUSD --execute-approved --approval-token "YOUR_TOKEN"
```

The executor still refuses the request unless:

- `APP_ENV=paper`
- `MT5_DEMO_ONLY=true`
- risk approval passed
- the token matches
- the order signal is `buy` or `sell`

The default background command remains analysis-only:

```powershell
run_paper_trading.bat
```

## Audit log

Inspect recent events with Python:

```powershell
.venv\Scripts\python.exe -c "from audit_log import AuditLog; import json; print(json.dumps(AuditLog().recent(), indent=2))"
```

Keep `data/audit.sqlite3` backed up securely. Do not commit `.env` or credentials.

## Important limitation

The `mt5_execution.py` guard is demo-only, but `mt5.order_send` still submits an order to the connected broker demo account. Start with `--once` without `--execute-approved`, verify the audit record, and use a minimal demo volume before testing the second gate.
