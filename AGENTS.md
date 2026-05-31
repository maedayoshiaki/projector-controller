# AGENTS.md — Contributor Guide for AI Agents

AI コーディングエージェント向けの運用規約です。人間向けの概要は `README.md`、現在の状態は `STATUS.md` にあります。

**Location:** `AGENTS.md`（リポジトリのルート）

## How To Use This File

着手前に次の順で文脈を取得する。

1. `AGENTS.md`（守るべき規約）
2. `STATUS.md`（今の状態）
3. 該当する `PLANS.md` のプラン（これからやること）
4. 必要なときだけ開く: 設計は `docs/ARCHITECTURE.md`、数式は `docs/THEORY.md`、用語は `docs/GLOSSARY.md`、投影テストは `docs/EXPERIMENTS.md`、表示設計は `DESIGN.md`

## Policies & Mandatory Rules

本プロジェクトの「憲法」。例外なく守る。

### 1. Human-in-the-Loop（人間が最終決定する）

AI は実装・検証・別解提示の伴走者であり、次は独断で確定しない。着手前に必ず人間へ確認する。

- 数式・理論・前提の確定
- アーキテクチャ、公開 API、設定ファイルなどの永続フォーマットの変更
- 新規依存ライブラリの追加
- 破壊的変更（既存の挙動・インターフェースを壊す）
- プランのスコープ変更

確認は「これで進めてよいか？」の 1 行でよい。沈黙で進めない。

### 2. Propose Multiple Options（複数案を出す）

非自明な設計・実装は、いきなり実装せず 2〜3 案を提示する。各案に「概要・長所/短所・推奨と理由」を添え、人間が選んだ案を実装する。自明な選択まで毎回案出しはしない。

例: 投影バックエンド選定、公開 API の形、設定ファイル形式、ディスプレイ指定方法。

### 3. Mathematical & Theoretical Work（数式は人間が所有）

投影幾何、台形補正、座標変換、色補正などの数式は人間が所有する。

| 工程 | 担当 |
|------|------|
| 定式化（式・記号定義・前提を立てる） | 人間 |
| 整合性レビュー（次元/記号衝突/境界条件）・別解/文献の提示 | AI（提案のみ） |
| 式の正しさの最終判断 | 人間 |
| コードへの実装（式↔関数の対応づけ） | AI（人間確認後） |
| 検証（解析解・極限・保存量による単体テスト） | AI+人間 |

- AI が生成・変形した式は `（未確認）` を付け、人間レビュー前に実装しない。
- 実装する式は `docs/THEORY.md` に記載し、式番号とコード関数を対応づける。
- 「とりあえず動く実装」で妥当性を誤魔化さず、sanity check を添える。

### 4. Be Educational（なぜそうするかを説明する）

実装・リファクタの際は選択理由を 1〜3 文で添える。ブラックボックス化しない。長文の講義は不要。

### 5. Planning（複数ステップは計画してから）

複数ファイル / 新機能 / リファクタ / 1 時間超の作業は、着手前に `PLANS.md` にプランを作る。`Progress`, `Surprises & Discoveries`, `Decision Log`, `Outcomes & Retrospective` を作業中に更新する。スコープが変わったら書き直す。

### 6. State & Memory（状態と記憶を残す）

- 作業の最初に `STATUS.md` を読み、最後に更新する。
- 確定した決定・再発防止したい落とし穴は `MEMORY.md` に追記する。
- `MEMORY.md` の実データを削除・上書きしない。テンプレート由来の空欄整理は例外として、事実を消さない。

### 7. Verification Before "Done"（完了の前に検証する）

コード変更では、完了報告前に整形、静的解析、型チェック、テストを通す。現時点では Python 環境とタスクランナーが未整備なので、実装環境を作るまでは実行できない検証コマンドと理由を報告する。

ドキュメント / メタ情報のみの変更では検証スタックを省略してよい。その場合も Markdown 内の未置換プレースホルダやリンク切れを確認する。

### 8. Safety & Secrets

- API キー、認証情報、個人情報、未公開データを Markdown やコードに書かない。
- `.env*`、認証ファイル、現場固有の秘密情報はコミットしない。
- 大きな動画素材や現場データはリポジトリに入れず、取得方法や置き場所を文書化する。

## Project Structure Guide

### Overview

このリポジトリは、Python からプロジェクタ投影用の画像・映像表示を制御するためのライブラリを作る場所。最初は小さく始め、ウィンドウ位置、対象ディスプレイ、フルスクリーン表示を安定して扱うことを優先する。

### Repo Structure

現時点の構成と、実装開始時に追加する想定の構成。

```text
.
├── AGENTS.md
├── CLAUDE.md
├── README.md
├── PLANS.md
├── STATUS.md
├── MEMORY.md
├── DESIGN.md
├── CONTRIBUTING.md
├── docs/
│   ├── ARCHITECTURE.md
│   ├── THEORY.md
│   ├── GLOSSARY.md
│   ├── EXPERIMENTS.md
│   └── adr/
├── pyproject.toml
├── uv.lock
├── src/projector_controller/      # ライブラリ本体（pure-Python。pygame 経路＋realtime クライアント）
├── packages/renderer/             # Rust/wgpu renderer。別 PyPI パッケージ（maturin bin）
├── examples/                      # 使用例
├── tests/                         # 自動テスト
└── media/                         # （未作成・予定）小さなサンプルのみ。大容量素材は置かない
```

### Module Boundaries

モジュール責務と依存方向は `docs/ARCHITECTURE.md` に集約する。新モジュールを足すときは先にそこを確認・更新する。

## Operation Guide

### Prerequisites

- Python 3.12
- uv
- pygame / SDL backend

### Setup

```powershell
uv sync --dev
```

### Development Workflow

1. 作業前に `STATUS.md` と該当する `PLANS.md` を読む。
2. 複数ステップなら `PLANS.md` に計画する。
3. 設計、公開 API、依存追加、数式、破壊的変更は着手前に人間へ確認する。
4. 実装する場合はコードと一緒にテストを追加・更新する。
5. 検証スタックを通す。未整備で実行できない場合は理由を報告する。
6. `STATUS.md` を更新し、確定事項を `MEMORY.md` へ追記する。

### Frequently Used Commands

```powershell
uv run ruff format .
uv run ruff check .
uv run mypy src tests
uv run pytest
uv run projector-controller --list-displays
uv run projector-controller --display 0 --width 1280 --height 720 --duration 5
```

### Coding Conventions

- 言語: Python を想定する。
- 命名: 関数・変数は `snake_case`、クラスは `PascalCase`。
- 公開 API は `ProjectionWindow` を入口に小さく始める。
- GUI / 動画再生など外部ライブラリ固有の処理は adapter 層に閉じ込める。
- コメントは「なぜ」を短く書く。「何を」はコードで読めるようにする。
- ユーザー向け挙動を変えたら README、ARCHITECTURE、必要なら DESIGN を更新する。

### Git Workflow

- **ブランチ名:** `feature/<short-description>` または `fix/<short-description>`
- **コミットメッセージ:** Conventional Commits 準拠。例: `docs: initialize projector controller docs`
- **PR:** コード変更がある場合は検証スタックを通してから作成する。

## Review Checklist

- 検証スタック、またはドキュメント変更時の軽量確認が通っている。
- テストが新挙動とエッジケースを網羅している。
- 設計判断は複数案から選ばれ、理由が残っている。
- 数式は人間確認済みで、式↔コードの対応がある。
- `STATUS.md` / `MEMORY.md` / 必要な `docs/*` が更新済み。
- 秘密情報や大容量素材が混入していない。

## Agent Cheatsheet

**やる**
- 着手前に `AGENTS.md`、`STATUS.md`、該当 `PLANS.md` を読む。
- 設計、API、依存、数式は複数案を出して人間に確認する。
- 投影表示の座標・ディスプレイ・フルスクリーン仕様はドキュメントに残す。
- 完了前に検証し、終わりに `STATUS.md` と必要なら `MEMORY.md` を更新する。

**やらない**
- 数式、破壊的変更、新規依存、公開 API を独断で確定する。
- 検証なしで「完了」と言う。
- `MEMORY.md` の実データを削除する。
- 秘密情報、未公開データ、大容量動画素材をコミットする。
- 将来使うかもしれないだけの抽象化を先に作る。
