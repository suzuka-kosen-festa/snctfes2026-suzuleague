# snctfes2026-suzuleague

鈴鹿高専 高専祭2026 ステージイベント「スズリーグ」の進行システム（バックエンド）。

テレビ番組「ネプリーグ」の「パーセントバルーン」をベースにしたクイズイベントで、
Scratch（ステージ表示・回答UI）とPython（進行管理・採点）が
TurboWarpのクラウド変数を介して連携する。

```
Scratch(TurboWarp) <-> TurboWarp cloud <-> Python(scratchattach) [<-> Firestore(将来)]
```

- イベント内容: [docs/イベント責任者作成の企画書.md](docs/イベント責任者作成の企画書.md)
- Scratch担当向け通信仕様: [docs/protocol.md](docs/protocol.md)

## セットアップ

[uv](https://docs.astral.sh/uv/) を使用。

```
uv sync
```

## 使い方

```
# 司会進行ダッシュボード（TurboWarp cloudに接続）
uv run suzuleague

# cloud接続なしでロジックだけ確認
uv run suzuleague --offline

# Scratch側シミュレータ（別ターミナルで。Scratch実装なしのE2E確認用）
uv run python -m suzuleague.sim_scratch          # 手動回答
uv run python -m suzuleague.sim_scratch --auto   # 自動回答

# cloud疎通スモークテスト
uv run python -m suzuleague.cloud

# Scratch貼り付け用の問題文リストを生成
uv run python -m suzuleague.questions > questions.txt
```

接続先ルームは `--project-id` または環境変数 `SUZULEAGUE_PROJECT_ID` で指定
（デフォルトは開発用ルーム `suzuleague-dev`）。

## テスト

```
uv run pytest
```

## 構成

| ファイル | 役割 |
|---|---|
| `src/suzuleague/models.py` | ドメインモデル (Question/Team/RoundResult) |
| `src/suzuleague/questions.py` | 問題セット管理（コード内管理） |
| `src/suzuleague/engine.py` | ゲーム進行ステートマシン・採点（通信非依存） |
| `src/suzuleague/protocol.py` | cloud変数プロトコルのエンコード/デコード |
| `src/suzuleague/cloud.py` | TurboWarp cloud接続ブリッジ |
| `src/suzuleague/dashboard.py` | 司会進行用CLIダッシュボード |
| `src/suzuleague/sim_scratch.py` | Scratch側シミュレータ（開発用） |
