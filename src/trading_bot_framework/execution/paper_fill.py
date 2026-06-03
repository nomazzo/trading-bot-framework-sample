from __future__ import annotations

from trading_bot_framework.broker.mock import MockBrokerClient
from trading_bot_framework.models import MarketTick


class PaperFillEngine:
    def __init__(self, broker: MockBrokerClient) -> None:
        # paper fillはMockBroker専用にし、実brokerの約定処理とは明確に分ける。
        self.broker = broker

    def on_tick(self, tick: MarketTick) -> None:
        # paper実行では、気配がlimit priceに届いた注文だけを約定扱いにする。
        self.broker.fill_crossed_limits(tick)
