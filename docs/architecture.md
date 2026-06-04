# Architecture

このリポジトリは、実口座へ発注するBotではなく、実運用で使っていたBot構成から、公開しても安全な設計要素だけを取り出し、`MockBrokerClient` と paper execution で確認できる形にしている。

## 全体構成

```text
strategy
  -> order intent
OrderManager
  -> RiskGuard
  -> BrokerClient
MockBrokerClient
  -> accepted order / synthetic fill
OrderManager
  -> Position update
```

## Modules

```text
src/trading_bot_framework/
├── cli.py
├── config.py
├── event_bus.py
├── models.py
├── broker/
│   ├── base.py
│   └── mock.py
├── execution/
│   ├── order_manager.py
│   └── paper_fill.py
├── risk/
│   └── guards.py
└── strategy/
    └── moving_average.py
```

## 責務

### `models.py`

Bot全体で共有する値を定義。

- `MarketTick`
- `Order`
- `Fill`
- `Position`
- `Side`
- `OrderType`
- `OrderStatus`

`Position.apply_fill()` は、fill によるポジション数量、平均価格、実現損益の更新を担当する。

### `broker/base.py`

Brokerとの境界を `BrokerClient` protocol として定義。

GitHub公開版では、この境界の先に実API clientを置かない。実API接続はこのリポジトリの範囲外。

### `broker/mock.py`

offline demo / unit test 用の broker。

- market order は現在tickの反対気配で即時約定
- limit order は一度 live order として保持
- `PaperFillEngine` が価格到達を検知したら synthetic fill を作成

### `risk/guards.py`

発注前の制限をまとめている。

- stale market data
- spread too wide
- invalid order quantity
- position limit

戦略から直接 broker に触らせず、必ず `OrderManager` 経由で `RiskGuard` を通す。

### `execution/order_manager.py`

注文ライフサイクルの中心。

- strategy が作った `Order` を受け取る
- `RiskGuard` で発注可否を判定
- `BrokerClient` へ注文を渡す
- fill を回収して position に反映
- rejected order に reason を残す

### `execution/paper_fill.py`

limit order の synthetic fill を担当する。

実取引所の約定ではなく、テスト用の簡易的な paper fill。

### `strategy/moving_average.py`

framework の流れを見るための toy strategy。

※このstrategyは収益性を目的にしていない。注文生成、risk check、fill、position update の一連の流れを確認するためだけのもの。

## GitHub公開版と実運用版の差

GitHub公開版に含めるもの:

- broker abstraction
- mock broker
- paper fill
- toy strategy
- risk guard
- order lifecycle
- position update
- unit tests

GitHub公開版に含めないもの:

- 実APIの発注処理
- broker認証
- 口座情報取得
- 本番戦略
- privateな閾値
- 実取引履歴
- 非公開データ

## 実運用コードとの関係

実運用版では、SAXO / Hyperliquid などのAPIを使った注文管理、ポジション管理、risk制御、ログ設計を行っている。

GitHub公開版では、そのままのコードを出すのではなく、以下だけを抽出している。

- 発注処理を抽象化する考え方
- strategy と execution を分ける構成
- 発注前にrisk guardを通す流れ
- fillをpositionへ反映する状態管理
- offlineでテストできるmock実行環境
