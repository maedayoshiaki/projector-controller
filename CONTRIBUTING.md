# CONTRIBUTING — 開発参加の手引き

人間の開発者向けの手順です。AI エージェントと併用する場合の本体ルールは `AGENTS.md` にあります。

## Setup

```powershell
uv sync --dev
```

## Branch & Commit

- ブランチ: `feature/<short-description>` または `fix/<short-description>`
- コミット: Conventional Commits 準拠。例: `docs: initialize projector controller docs`
- コミットは小さく焦点を絞る。

## Before You Open a PR

コード変更がある場合は、整形、静的解析、型チェック、テストを通してください。

```powershell
uv run ruff format .
uv run ruff check .
uv run mypy src tests
uv run pytest
```

ドキュメントのみの変更では、検索ツールで未置換プレースホルダや未処理マーカーが残っていないことを確認してください。

## Working With AI Agents

本プロジェクトは AI に丸投げせず、開発者が主導します。

- 数式、アーキテクチャ、公開 API、破壊的変更、新規依存は人間が最終決定する。
- 非自明な設計では AI に 2〜3 案を出させてから選ぶ。
- なぜその実装やパターンにしたかを短く残す。
- 作業後に `STATUS.md` を更新し、確定事項は `MEMORY.md` へ追記する。

## Review Checklist

- 検証またはドキュメント確認が通っている。
- 新挙動にはテストがある。
- 投影ウィンドウ、ディスプレイ、フルスクリーンなどの仕様変更がドキュメントに反映されている。
- 設計判断の理由が残っている。
- 秘密情報や大容量素材が混入していない。
