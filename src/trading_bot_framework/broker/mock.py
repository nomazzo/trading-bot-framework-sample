from __future__ import annotations

from dataclasses import replace
from itertools import count

from trading_bot_framework.models import Fill, MarketTick, Order, OrderStatus, OrderType, Side, now_ms


class MockBrokerClient:
    """Offline broker used for demos and tests.

    Market orders fill immediately at the opposite side of the current tick.
    Limit orders rest until the paper fill engine sees a crossing price.
    """

    def __init__(self) -> None:
        # order_idを決定的に発行し、テスト結果が毎回同じになるようにする。
        self._ids = count(1)
        self._open_orders: dict[str, Order] = {}
        self._fills: list[Fill] = []

    def submit_order(self, order: Order, tick: MarketTick) -> Order:
        order_id = order.order_id or f"MOCK-{next(self._ids):06d}"
        accepted = replace(order, order_id=order_id, status=OrderStatus.LIVE, updated_ts_ms=now_ms())

        if accepted.order_type == OrderType.MARKET:
            # market orderは現在の反対気配で即時約定させ、実APIなしで流れを確認する。
            fill_price = tick.ask if accepted.side == Side.BUY else tick.bid
            filled = self._fill_order(accepted, fill_price)
            return filled

        # limit orderはpaper fill engineが価格到達を検知するまで保持する。
        self._open_orders[order_id] = accepted
        return accepted

    def cancel_order(self, order_id: str) -> Order:
        order = self._open_orders.pop(order_id)
        order.status = OrderStatus.CANCELED
        order.updated_ts_ms = now_ms()
        return order

    def list_open_orders(self) -> list[Order]:
        return list(self._open_orders.values())

    def pop_fills(self) -> list[Fill]:
        # fillは一度だけ消費されるイベントとして扱い、position更新の二重反映を避ける。
        fills = list(self._fills)
        self._fills.clear()
        return fills

    def fill_crossed_limits(self, tick: MarketTick) -> list[Order]:
        # paper実行では、現在気配がlimit priceに届いた注文だけを約定扱いにする。
        filled: list[Order] = []
        for order_id, order in list(self._open_orders.items()):
            if order.side == Side.BUY and order.price is not None and tick.ask <= order.price:
                self._open_orders.pop(order_id)
                filled.append(self._fill_order(order, tick.ask))
            elif order.side == Side.SELL and order.price is not None and tick.bid >= order.price:
                self._open_orders.pop(order_id)
                filled.append(self._fill_order(order, tick.bid))
        return filled

    def _fill_order(self, order: Order, price: float) -> Order:
        # broker内でOrder状態とFillイベントを同時に作り、後段のreconcileで拾えるようにする。
        order.status = OrderStatus.FILLED
        order.filled_quantity = order.quantity
        order.avg_fill_price = price
        order.updated_ts_ms = now_ms()
        assert order.order_id is not None
        self._fills.append(
            Fill(
                order_id=order.order_id,
                symbol=order.symbol,
                side=order.side,
                quantity=order.quantity,
                price=price,
            )
        )
        return order
