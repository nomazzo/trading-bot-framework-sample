from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from trading_bot_framework.broker.mock import MockBrokerClient
from trading_bot_framework.execution.order_manager import OrderManager
from trading_bot_framework.models import MarketTick, Order, OrderStatus, OrderType, Side
from trading_bot_framework.risk.guards import RiskGuard, RiskLimits


class OrderManagerTests(unittest.TestCase):
    def test_market_order_updates_position(self):
        broker = MockBrokerClient()
        manager = OrderManager(broker, RiskGuard())
        tick = MarketTick("BTCUSD", bid=100.0, ask=100.02)

        order = Order("BTCUSD", side=Side.BUY, order_type=OrderType.MARKET, quantity=1.0)
        accepted = manager.submit(order, tick)

        self.assertEqual(accepted.status, OrderStatus.FILLED)
        self.assertEqual(manager.position_by_symbol["BTCUSD"].quantity, 1.0)
        self.assertEqual(manager.position_by_symbol["BTCUSD"].avg_price, 100.02)

    def test_risk_guard_rejects_position_limit(self):
        broker = MockBrokerClient()
        risk = RiskGuard(RiskLimits(max_abs_position=1.0, max_order_quantity=2.0))
        manager = OrderManager(broker, risk)
        tick = MarketTick("BTCUSD", bid=100.0, ask=100.02)

        order = Order("BTCUSD", side=Side.BUY, order_type=OrderType.MARKET, quantity=2.0)
        rejected = manager.submit(order, tick)

        self.assertEqual(rejected.status, OrderStatus.REJECTED)
        self.assertEqual(rejected.reason, "position_limit")


if __name__ == "__main__":
    unittest.main()
