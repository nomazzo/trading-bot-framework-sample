from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from trading_bot_framework.broker.mock import MockBrokerClient
from trading_bot_framework.execution.paper_fill import PaperFillEngine
from trading_bot_framework.models import MarketTick, Order, OrderStatus, OrderType, Side


class PaperFillTests(unittest.TestCase):
    def test_limit_order_fills_when_price_crosses(self):
        broker = MockBrokerClient()
        engine = PaperFillEngine(broker)
        tick = MarketTick("BTCUSD", bid=99.0, ask=101.0)
        order = Order("BTCUSD", side=Side.BUY, order_type=OrderType.LIMIT, quantity=1.0, price=100.0)

        accepted = broker.submit_order(order, tick)
        self.assertEqual(accepted.status, OrderStatus.LIVE)

        engine.on_tick(MarketTick("BTCUSD", bid=98.0, ask=99.5))
        fills = broker.pop_fills()

        self.assertEqual(len(fills), 1)
        self.assertEqual(fills[0].price, 99.5)


if __name__ == "__main__":
    unittest.main()
