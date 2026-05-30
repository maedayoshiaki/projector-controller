# CONTRIBUTING — 開発参加の手引き

人間の開発者向け。AI と併用する際のルールも含む（規約の本体は `AGENTS.md`）。

## Setup

```bash
{{uv sync}}
```

## Branch & Commit
- ブランチ: `{{feat/<short-description>}}` / `{{fix/...}}`
- コミット: 命令形・簡潔・小さく焦点を絞る（例: `add cosine LR scheduler`）。

## Before You Open a PR

検証スタックを通す：

```bash
{{make format}}
{{make lint}}
{{make typecheck}}
{{make test}}
```

PR は `.github/PULL_REQUEST_TEMPLATE.md` に沿って記述。

## Working With AI Agents（AI 併用のルール）

本プロジェクトは AI に丸投げせず、開発者が主導する（`AGENTS.md` §1〜4）。

- **人間が必ず関与する:** 数式・理論（`docs/THEORY.md`）、アーキテクチャ・API・破壊的変更、新規依存。
- **AI には複数案を出させる:** 非自明な設計は 2〜3 案を比較してから選ぶ。
- **理由を残す:** なぜその実装・パターンにしたかをコミットや該当 doc に短く記す。
- **記録を更新する:** 作業後に `STATUS.md`、確定事項は `MEMORY.md` を更新。

## Review Checklist
- ✅ 検証スタックが通る
- ✅ テストが新挙動とエッジケースを網羅
- ✅ 設計判断の理由が残っている
- ✅ 数式は人間確認済み・式↔コード対応あり
- ✅ ドキュメント（STATUS / MEMORY / docs）が更新済み
