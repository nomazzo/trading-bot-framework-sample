# Trading Bot Framework Sample

## 概要

このリポジトリは、Python で作成した取引Botフレームワークの公開用サンプルです。

実APIに接続するBotではなく、`MockBrokerClient` と paper execution を使って、注文抽象化、RiskGuard、注文ライフサイクル、ポジション更新、toy strategy の流れを確認できるようにしています。

実運用で使っていたSAXO / Hyperliquid系のBotコードをそのまま公開するのではなく、設計パターンだけを抽出し、秘密情報・実売買・本番戦略を含まない形に再構成しています。

実際のコードでは、Broker API への接続、注文発行、約定反映、ポジション同期、risk limit、Depth / 板情報を使った短い時間軸の売買判断などを扱っていました。この公開版では安全性を優先し、外部APIや実注文には接続せず、同じ責務分離の考え方を小さな offline framework として確認できるようにしています。

## 主な内容

- Broker interface による実装境界の分離
- Mock broker による安全な offline 実行
- Market / limit order model
- Synthetic fill による paper execution
- OrderManager による発注、約定、ポジション更新
- RiskGuard による spread / stale data / position / quantity check
- Moving average toy strategy
- Offline CLI demo
- Unit tests

## 技術スタック

- Python
- dataclasses
- enum
- argparse
- unittest
- mock execution
- paper trading style flow

## Skills

- 取引Botの責務分離
- broker / exchange API の抽象化
- mock broker による安全なテスト
- 注文状態のライフサイクル管理
- fill によるポジション更新
- stale data / spread / position limit の risk guard
- 板情報、約定、ポジションを分けて扱う execution architecture
- Depth データを使った market making / HFT 寄りの設計経験
- 実売買コードを公開せずに設計意図を見せる構成
- 本番戦略やprivate parameterを含めない公開リポジトリ設計

## 実運用版で扱っていた領域

公開版では toy strategy と mock broker に絞っていますが、実際の運用コードではより実戦的な売買執行ロジックを扱っていました。

- SAXO / Hyperliquid など、複数の取引APIを前提にした broker adapter
- 発注、キャンセル、再発注、約定確認、ポジション同期を分離した order lifecycle 管理
- 価格、spread、position、未約定注文、更新遅延を見た risk control
- 板情報や top-of-book を使った短い時間軸の market making / execution logic
- Depth データをもとにした liquidity、imbalance、quote skew の判断
- HFT に近い短時間判断を前提にした order placement / cancellation の設計
- 約定後の inventory 調整、position limit、異常時の取引停止
- Botの状態を再起動後に復元するための state management
- ログ、metrics、dry-run、paper mode を使った検証しやすい運用構成

このリポジトリには上記の本番ロジックそのものは含めていません。代わりに、`BrokerClient`、`OrderManager`、`RiskGuard`、`PaperFillEngine` という形で、実運用コードでも重要になる境界と責務を読み取れるようにしています。

## Architecture

```text
trading-bot-framework-sample/
├── pyproject.toml
├── README.md
├── src/
│   └── trading_bot_framework/
│       ├── cli.py
│       ├── config.py
│       ├── event_bus.py
│       ├── models.py
│       ├── broker/
│       │   ├── base.py
│       │   └── mock.py
│       ├── execution/
│       │   ├── order_manager.py
│       │   └── paper_fill.py
│       ├── risk/
│       │   └── guards.py
│       └── strategy/
│           └── moving_average.py
├── examples/
│   └── bot.example.yaml
├── docs/
│   ├── publication-plan.md
│   ├── architecture.md
│   ├── sample-output.md
│   └── release-checklist.md
└── tests/
```

責務の分け方:

- `models.py`: tick、order、fill、position などの共通モデル
- `broker/base.py`: broker client の境界
- `broker/mock.py`: offline demo / test 用の mock broker
- `execution/order_manager.py`: 発注前risk check、broker呼び出し、fill反映
- `execution/paper_fill.py`: limit order の synthetic fill
- `risk/guards.py`: spread、stale data、position、quantity の制限
- `strategy/moving_average.py`: framework確認用のtoy strategy
- `cli.py`: offline demo のエントリポイント

設計の詳細は [docs/architecture.md](docs/architecture.md) にまとめています。

## Setup

```bash
git clone <repository-url>
cd trading-bot-framework-sample
python -m pip install -e .
```

offline demo:

```bash
trading-bot-sample --symbol BTCUSD --ticks 8
```

出力例は [docs/sample-output.md](docs/sample-output.md) にまとめています。

モジュールとして実行する場合:

```bash
python -m trading_bot_framework.cli --symbol BTCUSD --ticks 8
```

## Test

```bash
python -m unittest discover -s tests
```

公開前の確認項目は [docs/release-checklist.md](docs/release-checklist.md) にまとめています。

## 公開用サンプルとして除外しているもの

このリポジトリには、以下を含めていません。

- broker / exchange のAPIキー
- broker authentication files
- 秘密鍵
- 口座ID / account key
- `.env` の実値
- 実売買の注文処理
- 本番の取引戦略
- private な閾値やパラメータ
- 非公開の市場データ
- 生成済みCSV / Parquet / gzipデータ
- 学習済みモデル
- 実運用ログ
- 収益情報
- 取引履歴

## 関連リポジトリ

- [mobile-app-portfolio](https://github.com/nomazzo/mobile-app-portfolio): 全体のアプリポートフォリオ説明
- [market-data-recorder-aws](https://github.com/nomazzo/market-data-recorder-aws): public WebSocket 市場データレコーダー
- [lightgbm-market-ml-pipeline](https://github.com/nomazzo/lightgbm-market-ml-pipeline): 市場データを対象にした LightGBM パイプライン
- [hyperliquid-mm-simulator](https://github.com/nomazzo/hyperliquid-mm-simulator): Hyperliquid を題材にしたマーケットメイクシミュレーター
- [defi-lp-bot-simulator](https://github.com/nomazzo/defi-lp-bot-simulator): DeFi LP ポジション管理のシミュレーター

## Public Demo Notes

このプロジェクトは公開用ポートフォリオです。取引Botの責務分離、注文管理、risk check、paper execution の流れを確認しやすい形にしています。

本番のbroker接続、実口座、実注文、Depthデータを使った本番戦略、private parameterには接続していません。より実運用に近い市場データ収集のサンプルは [market-data-recorder-aws](https://github.com/nomazzo/market-data-recorder-aws) に分けています。

公開前の切り出し方針は [docs/publication-plan.md](docs/publication-plan.md) にまとめています。
