from __future__ import annotations

import argparse

from trading_bot_framework.broker.mock import MockBrokerClient
from trading_bot_framework.config import BotConfig
from trading_bot_framework.execution.order_manager import OrderManager
from trading_bot_framework.models import MarketTick
from trading_bot_framework.risk.guards import RiskGuard, RiskLimits
from trading_bot_framework.strategy.moving_average import MovingAverageStrategy


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    # 公開デモではsymbolとtick数だけを受け取り、実broker設定は持たせない。
    parser = argparse.ArgumentParser(description="Run the offline trading bot framework sample.")
    parser.add_argument("--symbol", default="BTCUSD")
    parser.add_argument("--ticks", type=int, default=6)
    return parser.parse_args(argv)


def run_demo(config: BotConfig, ticks: int) -> dict[str, object]:
    # CLIデモは必ずMockBrokerで動かし、誤って実口座へ接続する経路を作らない。
    broker = MockBrokerClient()
    risk = RiskGuard(
        RiskLimits(
            max_abs_position=config.max_abs_position,
            max_order_quantity=config.max_order_quantity,
            max_spread_bps=config.max_spread_bps,
        )
    )
    manager = OrderManager(broker, risk)
    strategy = MovingAverageStrategy(config.symbol, window=3, quantity=1.0)

    base = 100.0
    for i in range(max(1, int(ticks))):
        # synthetic tickを使い、ネットワークなしでstrategyからposition更新まで確認する。
        mid = base + (i % 4) - 1
        tick = MarketTick(symbol=config.symbol, bid=mid - 0.01, ask=mid + 0.01)
        order = strategy.on_tick(tick)
        if order is not None:
            accepted = manager.submit(order, tick)
            print(f"{accepted.status.value:8s} {accepted.side.value:4s} qty={accepted.quantity} reason={accepted.reason}")

    pos = manager.position_by_symbol.get(config.symbol)
    return {"position": pos, "orders": manager.orders}


def main(argv: list[str] | None = None) -> None:
    # 最終ポジションを表示し、paper executionの状態変化をREADMEと照合しやすくする。
    args = parse_args(argv)
    result = run_demo(BotConfig(symbol=args.symbol), ticks=args.ticks)
    print(f"Final position: {result['position']}")


if __name__ == "__main__":
    main()
