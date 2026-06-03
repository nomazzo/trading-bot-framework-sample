from __future__ import annotations

from dataclasses import dataclass

from trading_bot_framework.models import MarketTick, Order, Position, Side, now_ms


@dataclass(frozen=True)
class RiskDecision:
    allowed: bool
    reason: str = ""


@dataclass
class RiskLimits:
    max_abs_position: float = 3.0
    max_order_quantity: float = 1.0
    max_spread_bps: float = 25.0
    stale_after_ms: int = 5_000


class RiskGuard:
    def __init__(self, limits: RiskLimits | None = None) -> None:
        # 制限値を1か所に集約し、strategy側にrisk判定を散らさない。
        self.limits = limits or RiskLimits()

    def check_order(self, order: Order, position: Position, tick: MarketTick) -> RiskDecision:
        # まず市場データの品質を確認し、古い気配で発注判断しないようにする。
        age_ms = now_ms() - tick.ts_ms
        if age_ms > self.limits.stale_after_ms:
            return RiskDecision(False, "stale_market_data")

        if tick.spread_bps > self.limits.max_spread_bps:
            return RiskDecision(False, "spread_too_wide")

        # 明らかにおかしい数量は、brokerへ渡す前に止める。
        if order.quantity <= 0 or order.quantity > self.limits.max_order_quantity:
            return RiskDecision(False, "invalid_order_quantity")

        # 約定後の想定ポジションで判定し、片方向への積み上がりを抑える。
        signed_qty = order.quantity if order.side == Side.BUY else -order.quantity
        next_qty = position.quantity + signed_qty
        if abs(next_qty) > self.limits.max_abs_position:
            return RiskDecision(False, "position_limit")

        return RiskDecision(True, "ok")
