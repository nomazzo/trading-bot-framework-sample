# Sample Output

このドキュメントは、`trading-bot-framework-sample` の offline demo 出力イメージを示すためのものです。

ここに掲載している値は説明用のサンプルです。実取引ログ、実口座情報、実運用の損益は含めていません。

## CLI Demo

```bash
trading-bot-sample --symbol BTCUSD --ticks 6
```

出力例:

```text
FILLED   BUY  qty=1.0 reason=
FILLED   BUY  qty=1.0 reason=
FILLED   SELL qty=1.0 reason=
FILLED   SELL qty=1.0 reason=
Final position: Position(symbol='BTCUSD', quantity=0.0, avg_price=0.0, realized_pnl=-4.04)
```

## 出力の読み方

- `FILLED`: mock broker 上で約定した注文
- `BUY` / `SELL`: 注文方向
- `qty`: 注文数量
- `reason`: RiskGuardでrejectされた場合の理由。約定時は空
- `Final position`: demo終了時点のpaper position

## Risk Rejection Example

RiskGuard が注文を止めた場合、`OrderStatus.REJECTED` と reason が残ります。

例:

```text
REJECTED BUY qty=2.0 reason=position_limit
```

主な reason:

- `stale_market_data`
- `spread_too_wide`
- `invalid_order_quantity`
- `position_limit`

## Paper Fill Example

limit order は、価格が到達するまで live order として保持されます。

```text
submit BUY limit 100.00
tick ask=99.50
fill BUY 1.0 @ 99.50
```

この処理は `MockBrokerClient` と `PaperFillEngine` による synthetic fill です。実取引所の約定ではありません。
