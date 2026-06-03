from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BotConfig:
    symbol: str = "BTCUSD"
    initial_cash: float = 100_000.0
    max_abs_position: float = 3.0
    max_order_quantity: float = 1.0
    max_spread_bps: float = 25.0
