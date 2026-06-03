from __future__ import annotations

from trading_bot_framework.broker.base import BrokerClient
from trading_bot_framework.models import Fill, MarketTick, Order, OrderStatus, Position
from trading_bot_framework.risk.guards import RiskGuard


class OrderManager:
    def __init__(self, broker: BrokerClient, risk_guard: RiskGuard) -> None:
        # brokerとriskを注入し、実装差し替えをテストしやすくする。
        self.broker = broker
        self.risk_guard = risk_guard
        self.position_by_symbol: dict[str, Position] = {}
        self.orders: dict[str, Order] = {}

    def submit(self, order: Order, tick: MarketTick) -> Order:
        # 発注前に必ずRiskGuardを通し、戦略側から直接brokerへ触らせない。
        position = self.position_by_symbol.setdefault(order.symbol, Position(order.symbol))
        decision = self.risk_guard.check_order(order, position, tick)
        if not decision.allowed:
            order.status = OrderStatus.REJECTED
            order.reason = decision.reason
            return order

        accepted = self.broker.submit_order(order, tick)
        if accepted.order_id:
            # 後からcancelやfill反映を追えるよう、accepted orderをローカルにも保持する。
            self.orders[accepted.order_id] = accepted
        self.reconcile_fills()
        return accepted

    def cancel(self, order_id: str) -> Order:
        # cancel結果もローカル状態に戻し、broker側だけに状態を閉じ込めない。
        canceled = self.broker.cancel_order(order_id)
        self.orders[order_id] = canceled
        return canceled

    def reconcile_fills(self) -> list[Fill]:
        # brokerからfillイベントを回収し、position更新をOrderManagerに集約する。
        fills = self.broker.pop_fills()
        for fill in fills:
            pos = self.position_by_symbol.setdefault(fill.symbol, Position(fill.symbol))
            pos.apply_fill(fill)
            if fill.order_id in self.orders:
                self.orders[fill.order_id].status = OrderStatus.FILLED
        return fills
