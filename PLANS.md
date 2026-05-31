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

| 案  | 概要                                                                        | 長所                                           | 短所                                     |
| --- | --------------------------------------------------------------------------- | ---------------------------------------------- | ---------------------------------------- |
| A   | テンプレート文言を最小限だけ置換する                                        | 速い                                           | このプロジェクト固有の判断材料が残らない |
| B   | README / AGENTS / docs を初期プロジェクト向けに具体化し、未決事項を明記する | すぐ作業を始めやすい。確定と未確定を分けられる | 初回の編集量はやや多い                   |
| C   | 実装予定の API や依存まで仮決めして文書化する                               | 具体的                                         | 人間確認前に設計を確定しすぎる           |

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

---

## Plan: pygame MVP 実装

- **Status:** `Done`
- **Owner:** AI
- **Created / Updated:** 2026-05-30 / 2026-05-30
- **Related:** README.md, docs/ARCHITECTURE.md, DESIGN.md

### Goal & Non-Goals
- **Goal:** Python 3.12 + uv の実装環境を作り、`ProjectionWindow` オブジェクト型 API で静止画・テストパターンを pygame backend から投影できる MVP を追加する。ウィンドウ位置、サイズ、対象 display、fullscreen 指定を扱う。
- **Non-Goals:** 動画再生、音声、プロジェクションマッピング、台形補正、色補正、GUI 操作画面は今回扱わない。

### Context & Constraints
ユーザー確認により、最初の方針は「Python 3.12 + uv」「pygame / SDL backend」「`ProjectionWindow` 型 API」「まず静止画とテストパターン」とする。pygame 固有処理は adapter 層に閉じ込める。

### Approach（検討した案）

| 案 | 概要 | 長所 | 短所 |
|----|------|------|------|
| A | OpenCV HighGUI で最小表示 | 画像表示が簡単 | display 指定や fullscreen の投影アプリ基盤として弱い |
| B | pygame / SDL で投影ウィンドウを作る | display 指定、fullscreen、イベント処理を扱いやすい | 動画再生は別途検討が必要 |
| C | PySide6 / Qt で最初から作る | 操作 UI や動画再生まで広げやすい | 初期依存が重くなる |

- **採用案:** B
- **理由:** 最初の関心が投影ウィンドウの位置・display・fullscreen の検証なので、SDL 系の pygame が小さく始めやすい。将来差し替えられるよう backend adapter に隔離する。

### Milestones / Steps
- [x] `pyproject.toml` と `src/` / `tests/` 構成を追加する
- [x] `ProjectionWindow`、設定型、fit mode、テストパターン生成を実装する
- [x] pygame adapter を追加する
- [x] examples と README / ARCHITECTURE / AGENTS / CONTRIBUTING を更新する
- [x] format / lint / typecheck / test を通す
- [x] STATUS / MEMORY を更新する

### Risks & Compatibility
- 新規依存として `pygame` を追加する。ユーザー確認済み。
- 実機プロジェクタやマルチディスプレイの挙動は環境差が大きいため、自動テストでは純粋ロジック中心に検証し、実機検証は `docs/EXPERIMENTS.md` に残す。
- 公開 API は MVP として小さく始める。破壊的変更が必要になった場合は事前確認する。

---

### Living Sections

#### Progress
- 2026-05-30: 方針相談で Python 3.12 + uv、pygame / SDL、`ProjectionWindow` 型 API を採用することを確認。
- 2026-05-30: `pyproject.toml`、`.python-version`、`src/projector_controller/`、`tests/`、`examples/` を追加。
- 2026-05-30: `ProjectionWindow`、`ProjectionConfig`、fit mode 計算、pygame adapter、CLI を実装。
- 2026-05-30: README / AGENTS / ARCHITECTURE / CONTRIBUTING / MEMORY を実装内容に合わせて更新。
- 2026-05-30: `uv sync --dev`、format、lint、typecheck、test、CLI の display 列挙を実行。

#### Surprises & Discoveries
- 2026-05-30: uv 環境には Python 3.12.12 が導入済みで、`.python-version` に従って利用できた。
- 2026-05-30: この環境で pygame から display 0 `1440x900`、display 1 `1280x800` を取得できた。

#### Decision Log
- 2026-05-30: 最初の MVP は静止画・テストパターン・display 指定・ウィンドウ位置・fullscreen に絞る。動画や操作 UI より先に投影面の基本制御を固めるため。

#### Outcomes & Retrospective
- 2026-05-30: pygame backend の MVP を追加し、静止画・生成テストパターン・display 指定・ウィンドウ位置・fullscreen を扱う入口を作った。実機投影での fullscreen / 座標挙動は次の手動検証で確認する。
