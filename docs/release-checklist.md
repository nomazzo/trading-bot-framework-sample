# Release Checklist

このチェックリストは、`trading-bot-framework-sample` を GitHub に公開する前の確認用です。

## 1. 追跡対象の確認

```bash
git status --short
```

確認すること:

- `.env` が表示されていない
- `*.cfg` が表示されていない
- token / key / credential 系ファイルが表示されていない
- `data/`、`logs/`、`out/`、`output/` が表示されていない
- `*.csv`、`*.csv.gz`、`*.parquet` が表示されていない
- model artifact が表示されていない

## 2. テスト

```bash
python -m unittest discover -s tests
```

期待結果:

```text
OK
```

## 3. Pythonコンパイル確認

```bash
python -m compileall -q src tests
```

エラーが出ないことを確認します。

## 4. Offline demo

```bash
trading-bot-sample --symbol BTCUSD --ticks 6
```

または:

```bash
python -m trading_bot_framework.cli --symbol BTCUSD --ticks 6
```

確認すること:

- 実APIに接続しない
- mock brokerだけで実行できる
- `FILLED` または `REJECTED` の注文状態が表示される
- final position が表示される

## 5. 秘密情報チェック

```bash
rg -n "api[_-]?key|secret|private[_-]?key|password|token|account[_-]?key|account_address|refresh|oauth" .
```

確認すること:

- 実値が含まれていない
- `.env.example` やドキュメントの説明文だけである
- 誤検知がある場合も、値や認証情報ではないことを確認する

必要に応じて、`.git`、`docs/publication-plan.md`、`docs/release-checklist.md`、`.env.example` は除外して確認します。

## 6. 除外対象の確認

公開前に、以下が含まれていないことを確認します。

- broker / exchange のAPIキー
- OAuth / refresh token
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

## 7. README確認

確認すること:

- 実APIに接続しない公開用サンプルであることが明記されている
- `MockBrokerClient` / paper execution が説明されている
- Setup / Test / docs への導線がある
- 関連リポジトリのリンクが正しい

## 8. 最終確認

```bash
git status --short
```

意図したソースコード、README、docs、examples、tests だけが表示されていることを確認してから commit します。
