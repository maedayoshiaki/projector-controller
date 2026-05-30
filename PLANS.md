# PLANS.md — タスクの計画

**未来**を扱うファイル。「これから何をするか」の設計図。
複数ファイルにまたがる作業、新機能、大きなリファクタ、数式・アルゴリズム実装では着手前にプランを書く。

---

## Plan: Projector Controller 文書初期整理

- **Status:** `Done`
- **Owner:** AI
- **Created / Updated:** 2026-05-30 / 2026-05-30
- **Related:** README.md, AGENTS.md, docs/ARCHITECTURE.md, DESIGN.md

### Goal & Non-Goals
- **Goal:** テンプレート由来のプレースホルダを、プロジェクタ投影用 Python ライブラリの初期方針に合わせて整理する。人間向け README、AI 向け AGENTS、設計メモ、UI/投影表示メモ、状態管理ファイルを実用できる状態にする。
- **Non-Goals:** Python 実装、依存ライブラリ追加、公開 API の確定、ウィンドウ制御バックエンドの確定は今回行わない。

### Context & Constraints
このリポジトリは、今後プロジェクタで画像や映像を投影するためのプログラムを書く場所。Python から呼び出せる形式を想定し、投影時のウィンドウ位置指定、対象ディスプレイ選択、フルスクリーン表示を扱える設計にしたい。

AGENTS.md の Human-in-the-Loop に従い、アーキテクチャ、公開 API、新規依存は人間確認前に確定しない。今回の文書では「初期候補」「未決事項」として記録する。

### Approach（検討した案）

| 案 | 概要 | 長所 | 短所 |
|----|------|------|------|
| A | テンプレート文言を最小限だけ置換する | 速い | このプロジェクト固有の判断材料が残らない |
| B | README / AGENTS / docs を初期プロジェクト向けに具体化し、未決事項を明記する | すぐ作業を始めやすい。確定と未確定を分けられる | 初回の編集量はやや多い |
| C | 実装予定の API や依存まで仮決めして文書化する | 具体的 | 人間確認前に設計を確定しすぎる |

- **採用案:** B
- **理由:** ユーザーの意図に沿って文書を実用化しつつ、AGENTS.md の確認ルールを守るため。API や依存は候補として残す。

### Milestones / Steps
- [x] 現状のテンプレート文書とリポジトリ構成を確認する
- [x] README / AGENTS / CONTRIBUTING を projector-controller 用に整理する
- [x] docs/ARCHITECTURE.md / docs/GLOSSARY.md / DESIGN.md を初期方針に合わせる
- [x] STATUS.md / MEMORY.md を更新する
- [x] Markdown 内にテンプレート由来の未置換プレースホルダが残っていないか確認する

### Risks & Compatibility
- ドキュメントのみの変更なので、既存コードの挙動変更はない。
- 公開 API、永続フォーマット、新規依存は確定しない。必要な選択肢は Open Questions に残す。
- ドキュメント / メタ情報のみの変更のため、検証スタックは省略できる。

---

### Living Sections

#### Progress
- 2026-05-30: AGENTS.md / STATUS.md / PLANS.md と現状ファイル構成を確認。
- 2026-05-30: README.md / AGENTS.md / docs/ARCHITECTURE.md / DESIGN.md / docs/GLOSSARY.md を projector-controller 向けに更新。
- 2026-05-30: docs/THEORY.md / docs/EXPERIMENTS.md / CONTRIBUTING.md / CLAUDE.md / MEMORY.md / STATUS.md を更新。
- 2026-05-30: 未置換プレースホルダ検索と `git diff --check` を実行。

#### Surprises & Discoveries
- 2026-05-30: README.md など多くの文書がテンプレートのプレースホルダを含む状態だった。

#### Decision Log
- 2026-05-30: 実装や依存追加は今回の対象外にした。AGENTS.md の確認ルールに従い、設計・API は候補として書き、人間確認後に確定する。
- 2026-05-30: テンプレート専用の TEMPLATE_GUIDE.md は、プロジェクト固有文書としては紛らわしいため削除した。

#### Outcomes & Retrospective
- 2026-05-30: テンプレート由来の Markdown を projector-controller 用に整理した。実装、依存追加、公開 API 確定は行わず、次に人間が判断する Open Questions として残した。
