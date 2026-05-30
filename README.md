# Research & Dev Repo Template

> **English (summary):** A Markdown scaffold for running research & development repositories with AI coding agents (Claude Code / Codex) and humans working together. **`AGENTS.md` is the core** (the operating manual for AI agents); every other file supports it. Click **"Use this template"**, then fill the `{{...}}` placeholders and `<!-- TODO -->` markers — start with `AGENTS.md`. Full documentation is in Japanese below; see `TEMPLATE_GUIDE.md` for the whole system.
> <!-- この英語サマリーは配布用の任意項目です。不要なら削除して構いません。 -->

AI コーディングエージェント（Claude Code / Codex 等）と人間が**協働**で研究開発リポジトリをきれいに運用するための雛形。
**中心は `AGENTS.md`**（AI への運用規約）。他のファイルはそれを支える。

> このリポジトリは GitHub の **テンプレートリポジトリ**として配布される想定です。
> 配布する側は Settings → General → **Template repository** を ON にすると「Use this template」ボタンが出ます。

<!-- ▼▼ セットアップが終わったら、ここから区切り線（---）までを削除し、下を自分のプロジェクト README にしてください ▼▼ -->

## How To Use This Template

1. 上部の **「Use this template」→ Create a new repository** で自分のリポを作る。
2. 下記の **プレースホルダ／TODO を埋める**（最重要は `AGENTS.md`）。
3. 仕組みの全体像は [`TEMPLATE_GUIDE.md`](./TEMPLATE_GUIDE.md) を参照（把握後は削除可）。

## Filling In TODOs（プレースホルダの埋め方）

プレースホルダは 2 種類：

- **`{{...}}`** … 自分の値に置き換える。例: `{{package}}` → `mylib`
- **`<!-- TODO: ... -->`** … 対応が必要な箇所の目印。HTML コメントなので表示はされない。埋めたら削除する。

置き換えの例（before → after）：

```
Project Overview: {{時系列データから状態を推定する…}}  →  本プロジェクトは … を推定する。
- セットアップ: {{uv sync}}                              →  - セットアップ: uv sync
| src/{{package}}/ | 本体 |                              →  | src/mylib/ | 本体 |
LICENSE: Copyright (c) 2026 {{YOUR NAME / ORG}}          →  Copyright (c) 2026 Taro Yamada
```

**まずここから（`AGENTS.md` が主体）：**

- `Project Overview` — プロジェクトの 1〜2 文
- `Directory Structure` — 実際の構成に合わせる
- `Commands` / `Operation Guide`（Prerequisites・Setup・Coding Conventions）— 実コマンド・実スタックに

**次に（必要なものだけ）：**

- `LICENSE` — `{{YOUR NAME / ORG}}` を自分／組織名に
- `CLAUDE.md` — 基本そのまま（`@AGENTS.md` を参照する）。固有メモがあれば追記
- `docs/ARCHITECTURE.md` — 採用するアーキ様式・Module Map を確定
- `docs/THEORY.md` — 数式を扱うなら記号表・式から
- この README 下部の本体（`{{プロジェクト名}}` 等）
- 使わない doc は削除してよい（規模別の取捨は [`TEMPLATE_GUIDE.md`](./TEMPLATE_GUIDE.md)）

> ヒント：全部を一度に埋めない。**`AGENTS.md` だけ埋めて走り出す**のが最小構成。
> 普遍ルールを全リポで効かせたいなら、`AGENTS.md` の Policies を `~/.claude/CLAUDE.md` にも置くとよい。

<!-- ▲▲ ここまで削除 ▲▲ -->

---

# {{プロジェクト名}}

{{1〜2 文の説明。何をするプロジェクトか。}}

> このファイルは**人間向け**の入口。AI コーディングエージェント向けの運用規約は `AGENTS.md`（Claude Code は `CLAUDE.md` 経由で参照）。

## Quickstart

```bash
{{uv sync}}    # セットアップ
{{make run}}   # 実行
{{make test}}  # テスト
```

## Requirements

- {{Python 3.10+ など}}
- {{依存管理ツール}}

## Documentation Map

| ファイル | 内容 |
|------|------|
| `AGENTS.md` | AI への運用規約（**中心**） |
| `PLANS.md` | 進行中タスクの計画 |
| `STATUS.md` | 今の状態 |
| `MEMORY.md` | 確定した決定・落とし穴 |
| `docs/ARCHITECTURE.md` | 設計思想・依存ルール・パターン集 |
| `docs/THEORY.md` | 数式・理論 |
| `docs/GLOSSARY.md` | 用語集 |
| `docs/EXPERIMENTS.md` | 実験ログ |
| `CONTRIBUTING.md` | 開発参加の手引き |

## License

[MIT](./LICENSE)
