from __future__ import annotations

from collections import deque

from trading_bot_framework.models import MarketTick, Order, OrderType, Side


class MovingAverageStrategy:
    """Tiny toy strategy for framework demonstration.

    This is intentionally not a profitable trading strategy. It only produces
    deterministic sample orders so the framework lifecycle can be tested.
    """

    def __init__(self, symbol: str, window: int = 3, quantity: float = 1.0) -> None:
        # デモ用なので、外部データや学習済みモデルには依存させない。
        self.symbol = symbol
        self.window = max(2, int(window))
        self.quantity = float(quantity)
        self._mids: deque[float] = deque(maxlen=self.window)

    def on_tick(self, tick: MarketTick) -> Order | None:
        # 初期windowが埋まるまでは注文を出さず、状態遷移を安定させる。
        self._mids.append(tick.mid)
        if len(self._mids) < self.window:
            return None

        avg = sum(self._mids) / len(self._mids)
        if tick.mid > avg:
            # 上向きならBUY、下向きならSELLという単純なtoy signalだけを返す。
            return Order(symbol=self.symbol, side=Side.BUY, order_type=OrderType.MARKET, quantity=self.quantity)
        if tick.mid < avg:
            return Order(symbol=self.symbol, side=Side.SELL, order_type=OrderType.MARKET, quantity=self.quantity)
        return None
