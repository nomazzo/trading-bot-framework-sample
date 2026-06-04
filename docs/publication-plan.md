# 公開方針

このリポジトリは、実売買Botを公開するためのものではなく、取引Botフレームワークの設計サンプルとして構成している。

GitHub公開上の焦点は、broker抽象化、mock execution、注文ライフサイクル、risk guard、event loop構成、paper fill、テストしやすい状態遷移。実口座や実注文に接続するのではなく、取引Botをどのように責務分離して作るかを示す。

## GitHub公開用の構成

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
  tests/
```

## GitHub公開版に残すもの

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

## 再構成すること

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