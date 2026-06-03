from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import time


def now_ms() -> int:
    return int(time.time() * 1000)


class Side(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class OrderType(str, Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"


class OrderStatus(str, Enum):
    NEW = "NEW"
    LIVE = "LIVE"
    FILLED = "FILLED"
    CANCELED = "CANCELED"
    REJECTED = "REJECTED"


@dataclass(frozen=True)
class MarketTick:
    # StrategyとRiskGuardが同じ気配を見るよう、bid/askを1つの値型にまとめる。
    symbol: str
    bid: float
    ask: float
    ts_ms: int = field(default_factory=now_ms)

    @property
    def mid(self) -> float:
        return (self.bid + self.ask) / 2.0

    @property
    def spread(self) -> float:
        return max(0.0, self.ask - self.bid)

    @property
    def spread_bps(self) -> float:
        # 取引対象が変わっても比較しやすいよう、spreadはbpsでも持つ。
        if self.mid <= 0:
            return 0.0
        return self.spread / self.mid * 10000.0


@dataclass
class Order:
    # 実broker固有のpayloadではなく、framework内の共通注文モデルとして扱う。
    symbol: str
    side: Side
    order_type: OrderType
    quantity: float
    price: float | None = None
    client_order_id: str | None = None
    order_id: str | None = None
    status: OrderStatus = OrderStatus.NEW
    filled_quantity: float = 0.0
    avg_fill_price: float = 0.0
    reason: str = ""
    created_ts_ms: int = field(default_factory=now_ms)
    updated_ts_ms: int = field(default_factory=now_ms)


@dataclass(frozen=True)
class Fill:
    # 約定はOrderとは分け、position更新に必要な最小情報だけを残す。
    order_id: str
    symbol: str
    side: Side
    quantity: float
    price: float
    ts_ms: int = field(default_factory=now_ms)


@dataclass
class Position:
    symbol: str
    quantity: float = 0.0
    avg_price: float = 0.0
    realized_pnl: float = 0.0

    def apply_fill(self, fill: Fill) -> None:
        # BUYを正、SELLを負として扱い、long/shortを同じ経路で更新する。
        signed_qty = fill.quantity if fill.side == Side.BUY else -fill.quantity
        prev_qty = self.quantity
        new_qty = prev_qty + signed_qty

        if prev_qty == 0 or (prev_qty > 0 and signed_qty > 0) or (prev_qty < 0 and signed_qty < 0):
            # 同じ方向に積み増す場合は、数量加重で平均価格を更新する。
            total_cost = abs(prev_qty) * self.avg_price + abs(signed_qty) * fill.price
            total_qty = abs(prev_qty) + abs(signed_qty)
            self.avg_price = total_cost / total_qty if total_qty else 0.0
        else:
            # 反対売買は既存ポジションのクローズとして実現損益を計算する。
            closed_qty = min(abs(prev_qty), abs(signed_qty))
            if prev_qty > 0:
                self.realized_pnl += closed_qty * (fill.price - self.avg_price)
            else:
                self.realized_pnl += closed_qty * (self.avg_price - fill.price)
            if abs(signed_qty) > abs(prev_qty):
                self.avg_price = fill.price
            elif new_qty == 0:
                self.avg_price = 0.0

        self.quantity = new_qty
