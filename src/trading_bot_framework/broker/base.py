from __future__ import annotations

from typing import Protocol

from trading_bot_framework.models import Fill, MarketTick, Order


class BrokerClient(Protocol):
    """Broker boundary used by the framework.

    Public samples implement this with a mock broker only. Real broker clients
    should live outside this repository.
    """

    def submit_order(self, order: Order, tick: MarketTick) -> Order:
        # StrategyやOrderManagerは、実brokerかmockかを意識しない。
        ...

    def cancel_order(self, order_id: str) -> Order:
        ...

    def list_open_orders(self) -> list[Order]:
        ...

    def pop_fills(self) -> list[Fill]:
        ...
