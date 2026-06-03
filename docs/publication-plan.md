# Publication Plan

This repository should be published as a trading bot framework sample, not as a
live trading bot. Keep the public surface focused on architecture: broker
abstraction, mock execution, order lifecycle, risk guards, event loop structure,
paper fills, and testable state transitions.

## Source Files To Cut Out

Use these files as implementation references, but do not copy them directly.

| Source file | How to use it |
| --- | --- |
| `trading_codes/GridTrading/saxo_grid/safety.py` | Strong reference for public-safe components: `SpreadGuard`, `TradingWindow`, `Watchdog`, `AuditLogger`, and preflight checks. Rebuild with generic names and no broker dependency. |
| `trading_codes/GridTrading/saxo_grid/orders.py` | Reference for order payload construction, retry/backoff, cancel fallback, working-order listing, and idempotent close handling. Public version should expose a `BrokerClient` interface and `MockBrokerClient`; do not keep Saxo endpoints or account fields. |
| `trading_codes/GridTrading/saxo_grid/main.py` | Reference for overall orchestration: bootstrap, quote polling, guard checks, bar loop, order reconciliation, fills sync, health output, and graceful shutdown. Do not copy directly because it mixes real auth, account resolution, live trading, and strategy parameters. |
| `trading_codes/salamander/mm_bot_v3/mm_skew/state.py` | Reference for clean state containers: market state, inventory state, live orders, order state, token buckets, event bus, and per-symbol context. This is useful for framework design after simplifying domain-specific fields. |
| `trading_codes/salamander/mm_bot_v3/mm_skew/quote_engine.py` | Reference for separating quote calculation from execution. Public version should use a toy strategy such as moving-average or static spread quotes, not private alpha logic. |
| `trading_codes/salamander/mm_bot_v3/mm_skew/order_manager.py` | Reference for order lifecycle ideas: place/modify/cancel, post-only guard, stale-data cancel, inventory guard, action budgets, and graceful stop. Do not copy live Hyperliquid execution or credential wiring. |
| `trading_codes/salamander/mm_bot_v3/mm_skew/metrics.py` | Reference for structured logs and CSV-style action/fill/inventory records. Public version should keep logs small and write only synthetic paper-trading output. |

## Suggested Public Structure

```text
trading-bot-framework-sample/
  README.md
  pyproject.toml
  .env.example
  src/trading_bot_framework/
    __init__.py
    cli.py
    config.py
    models.py
    event_bus.py
    broker/
      __init__.py
      base.py
      mock.py
    strategy/
      __init__.py
      moving_average.py
      grid_example.py
    risk/
      __init__.py
      guards.py
      limits.py
    execution/
      __init__.py
      order_manager.py
      paper_fill.py
    logging/
      __init__.py
      metrics.py
  examples/
    bot.example.yaml
  docs/
    publication-plan.md
    architecture.md
    release-checklist.md
  tests/
```

## Keep

- Broker abstraction instead of real broker implementation.
- Mock broker with deterministic order IDs and synthetic fills.
- Order models: side, type, quantity, price, status, timestamps, client order id.
- Order lifecycle: submit, cancel, replace, fill, reject, expire.
- Paper execution and synthetic market data fixtures.
- Risk guards:
  - max position
  - max notional
  - max spread
  - stale quote / stale market data
  - trading window
  - cooldown after rejects
  - kill switch / graceful stop
- Retry/backoff patterns, but only around mock or public-safe interfaces.
- Structured action/fill/inventory logs with sample values only.
- Unit tests for state transitions and risk decisions.

## Refactor Before Publishing

- Replace Saxo / OANDA / Hyperliquid API clients with `BrokerClient` protocols.
- Replace real order endpoints with `MockBrokerClient`.
- Replace strategy thresholds with toy example parameters.
- Move all runtime settings into `examples/bot.example.yaml`.
- Keep symbols generic, such as `EURUSD` or `BTCUSD`, with synthetic prices.
- Make paper execution the default and only execution mode in this repository.
- Keep live trading support out of scope.
- Add tests around:
  - order submit / fill / cancel
  - risk guard blocks
  - stale data cancellation
  - position update after fill
  - graceful shutdown

## Exclude

Do not copy these into the public repository.

- Any `.env`, `.cfg`, token file, private key, refresh token, OAuth token, API key,
  account key, account address, or broker credential.
- Real broker clients:
  - `token_manager.py`
  - `auth_bootstrap.py`
  - `auth.py`
  - real `saxo_client.py` / OANDA / Hyperliquid execution clients
- Real live-order scripts and VPS entrypoints:
  - `trading_codes/GridTrading/saxo_grid/main.py`
  - `trading_codes/Paradise/SAXO/main.py`
  - `trading_codes/salamander/*/run_mm.py`
  - `trading_codes/salamander/*/trade_*.py`
- Production strategy logic, thresholds, symbol lists, and private parameter sweeps.
- Account balance fetching, account-key resolution, token refresh, browser auth,
  or live broker position endpoints.
- Generated data and logs: `data/`, `logs/`, `out/`, `output/`, `reports/`,
  `*.csv`, `*.csv.gz`, `*.parquet`, `*.jsonl`, `*.log`.
- Model artifacts: `models/`, `*.pkl`, `*.pickle`, `*.joblib`, `*.pb`.
- Notebooks or old experiment folders with credentials or private research outputs.

## Public Implementation Boundary

The public sample should demonstrate how a bot is structured, not how to trade a
real account.

Allowed:

- `MockBrokerClient`
- `PaperFillEngine`
- synthetic market data
- toy strategy examples
- risk and lifecycle tests
- framework-style interfaces

Not allowed:

- live order placement
- real broker authentication
- account balance queries
- production trading parameters
- private strategy alpha
- private historical datasets

## Security Notes

Earlier inventory found hardcoded Bybit-style `api_key` and `secret_key` values
in old notebooks under `2ndStage_BTCBot` and `Binary_bot`. Do not copy notebooks
from those folders into this repository. Treat those credentials as compromised
unless they have already been revoked.

For this repository, the safest default is: no network order endpoint, no broker
credential, and no real account state. All examples should run offline.
