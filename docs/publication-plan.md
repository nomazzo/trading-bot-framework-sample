# 公開方針

このリポジトリは、実売買Botを公開するためのものではなく、取引Botフレームワークの設計サンプルとして構成しています。

公開上の焦点は、broker抽象化、mock execution、注文ライフサイクル、risk guard、event loop構成、paper fill、テストしやすい状態遷移です。実口座や実注文に接続するのではなく、取引Botをどのように責務分離して作るかを示します。

## 参考にした元コード

以下のファイルは実装の参考としてのみ扱います。直接コピーせず、broker依存や実売買処理を外した公開用サンプルとして再構成します。

| 元ファイル | 公開版での扱い |
| --- | --- |
| `trading_codes/GridTrading/saxo_grid/safety.py` | `SpreadGuard`、`TradingWindow`、`Watchdog`、`AuditLogger`、preflight checkなどの参考。公開版ではgenericな名前にし、broker依存をなくします。 |
| `trading_codes/GridTrading/saxo_grid/orders.py` | order payload作成、retry / backoff、cancel fallback、working order一覧、idempotent close処理の参考。公開版では `BrokerClient` interface と `MockBrokerClient` を使い、Saxo endpointやaccount fieldは残しません。 |
| `trading_codes/GridTrading/saxo_grid/main.py` | bootstrap、quote polling、guard check、bar loop、order reconciliation、fills sync、health output、graceful shutdownなど全体構成の参考。real auth、account resolution、live trading、strategy parameterが混在するため直接コピーしません。 |
| `trading_codes/salamander/mm_bot_v3/mm_skew/state.py` | market state、inventory state、live orders、order state、token bucket、event bus、symbol別contextなど、state container設計の参考。domain固有項目を簡略化して使います。 |
| `trading_codes/salamander/mm_bot_v3/mm_skew/quote_engine.py` | quote calculationとexecutionを分離する設計の参考。公開版ではprivate alpha logicではなく、moving-averageやstatic spread quoteのtoy strategyを使います。 |
| `trading_codes/salamander/mm_bot_v3/mm_skew/order_manager.py` | place / modify / cancel、post-only guard、stale-data cancel、inventory guard、action budget、graceful stopなど注文ライフサイクルの参考。live Hyperliquid executionやcredential wiringはコピーしません。 |
| `trading_codes/salamander/mm_bot_v3/mm_skew/metrics.py` | action / fill / inventory の構造化ログの参考。公開版ではsample値だけを使い、synthetic paper-trading outputに限定します。 |

## 公開用の構成

```text
trading-bot-framework-sample/
  README.md
  pyproject.toml
  .env.example
  src/trading_bot_framework/
    __init__.py
    cli.py
    config.py
    models.py
    event_bus.py
    broker/
      __init__.py
      base.py
      mock.py
    strategy/
      __init__.py
      moving_average.py
    risk/
      __init__.py
      guards.py
    execution/
      __init__.py
      order_manager.py
      paper_fill.py
  examples/
    bot.example.yaml
  docs/
    publication-plan.md
    architecture.md
    sample-output.md
    release-checklist.md
  tests/
```

## 残すもの

- 実broker implementationではなく、broker abstraction
- deterministicなorder IDとsynthetic fillを持つmock broker
- side、type、quantity、price、status、timestamp、client order IDなどのorder model
- submit、cancel、replace、fill、reject、expireなどの注文ライフサイクル
- paper execution と synthetic market data fixture
- risk guard
  - max position
  - max notional
  - max spread
  - stale quote / stale market data
  - trading window
  - reject後のcooldown
  - kill switch / graceful stop
- retry / backoff pattern。ただしmockまたは公開して安全なinterfaceの範囲に限定する
- sample値だけを使ったaction / fill / inventoryの構造化ログ
- state transition と risk decision の単体テスト

## 公開前に再構成すること

- Saxo / OANDA / Hyperliquid のAPI clientを `BrokerClient` protocolへ置き換える
- 実order endpointを `MockBrokerClient` へ置き換える
- strategy thresholdをtoy example parameterへ置き換える
- runtime settingを `examples/bot.example.yaml` へ移す
- symbolは `EURUSD` や `BTCUSD` などgenericなものにし、価格はsyntheticにする
- paper executionをこのリポジトリのデフォルトかつ唯一の実行モードにする
- live trading supportはscope外にする
- 以下のテストを追加する
  - order submit / fill / cancel
  - risk guardによるblock
  - stale data cancellation
  - fill後のposition update
  - graceful shutdown

## 削除・除外するもの

以下は公開リポジトリへコピーしません。

- `.env`、`.cfg`、token file、private key、refresh token、OAuth token、API key、account key、account address、broker credential
- 実broker client
  - `token_manager.py`
  - `auth_bootstrap.py`
  - `auth.py`
  - real `saxo_client.py`
  - OANDA / Hyperliquid execution client
- 実売買のscriptやVPS entrypoint
  - `trading_codes/GridTrading/saxo_grid/main.py`
  - `trading_codes/Paradise/SAXO/main.py`
  - `trading_codes/salamander/*/run_mm.py`
  - `trading_codes/salamander/*/trade_*.py`
- production strategy logic、threshold、symbol list、private parameter sweep
- account balance fetching、account-key resolution、token refresh、browser auth、live broker position endpoint
- generated data / logs
  - `data/`
  - `logs/`
  - `out/`
  - `output/`
  - `reports/`
  - `*.csv`
  - `*.csv.gz`
  - `*.parquet`
  - `*.jsonl`
  - `*.log`
- model artifact
  - `models/`
  - `*.pkl`
  - `*.pickle`
  - `*.joblib`
  - `*.pb`
- credentialやprivate research outputを含む可能性のあるnotebookや古いexperiment folder

## 公開実装の境界

公開版で示すもの:

- `MockBrokerClient`
- `PaperFillEngine`
- synthetic market data
- toy strategy example
- risk と lifecycle のtest
- framework-style interface

公開版で扱わないもの:

- live order placement
- real broker authentication
- account balance query
- production trading parameter
- private strategy alpha
- private historical dataset

公開版の目的は、実口座でどう取引するかではなく、Botをどのように設計・分離・テストするかを示すことです。

## セキュリティメモ

過去の棚卸しで、`2ndStage_BTCBot` と `Binary_bot` 配下の古いnotebookに Bybit 形式の `api_key` / `secret_key` がハードコードされているものを確認しています。これらのnotebookは、このリポジトリへコピーしません。

該当credentialは、すでに無効化していない場合は漏洩済みとして扱い、削除・ローテーションする前提です。

このリポジトリの安全なデフォルトは、network order endpointなし、broker credentialなし、real account stateなしです。すべてのexampleはofflineで動作する前提にします。
