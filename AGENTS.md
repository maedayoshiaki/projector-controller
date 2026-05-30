# AGENTS.md — Contributor Guide for AI Agents

AI コーディングエージェント（Claude Code / Codex 等）向けの運用規約。人間向けの概要は `README.md`。
Claude Code は `CLAUDE.md` 経由でこのファイルを取り込む。AGENTS.md はルート直下に置くと各種ツールが自動で読み込む共通フォーマット。

**Location:** `AGENTS.md`（リポジトリのルート）

## Table of Contents
1. [How To Use This File](#how-to-use-this-file)
2. [Policies & Mandatory Rules](#policies--mandatory-rules)
3. [Project Structure Guide](#project-structure-guide)
4. [Operation Guide](#operation-guide)
5. [Agent Cheatsheet](#agent-cheatsheet)

## How To Use This File

着手前に次の順で文脈を取得する：

1. この `AGENTS.md`（守るべき規約）
2. `STATUS.md`（今の状態）
3. 該当する `PLANS.md` のプラン（これからやること）
4. 必要なときだけ開く（全部は読まない）: 設計 → `docs/ARCHITECTURE.md` / 数式 → `docs/THEORY.md` / 用語 → `docs/GLOSSARY.md` / 実験 → `docs/EXPERIMENTS.md` / UI → `DESIGN.md`

## Policies & Mandatory Rules

本プロジェクトの「憲法」。例外なく守る。

### 1. Human-in-the-Loop（人間が最終決定する）

AI は実装・検証・別解提示の伴走者であり、次は独断で確定しない。着手前に必ず人間へ確認する：

- 数式・理論・前提の確定（→ §3）
- アーキテクチャ / 公開 API / 永続フォーマット（DB スキーマ・ファイル形式・設定）の変更
- 新規依存ライブラリの追加
- 破壊的変更（既存の挙動・インターフェースを壊す）
- プランのスコープ変更

確認は「これで進めてよいか？」の 1 行で十分。沈黙で進めない。

### 2. Propose Multiple Options（複数案を出す）

非自明な設計・実装は、いきなり実装せず 2〜3 案を提示する。各案に「概要・長所/短所・推奨と理由」を添え、人間が選んだ案を実装する。自明な選択（型注釈、軽微なリファクタ）まで毎回案出しはしない。
例: 設定からモデルを生成する箇所 → ①直書き分岐 ②Factory ③Registry を比較して提示。

### 3. Mathematical & Theoretical Work（研究の数式は人間が所有）

| 工程 | 担当 |
|------|------|
| 定式化（式・記号定義・前提を立てる） | 人間 |
| 整合性レビュー（次元/記号衝突/境界条件）・別解/文献の提示 | AI（提案のみ） |
| 式の正しさの最終判断 | 人間 |
| コードへの実装（式↔関数の対応づけ） | AI（人間確認後） |
| 検証（解析解・極限・保存量による単体テスト） | AI+人間 |

- AI が生成・変形した式は `（未確認）` を付け、人間レビュー前に実装しない。
- 実装する式は `docs/THEORY.md` に記載し、式番号とコード関数を対応づける（例: 式(1) ↔ `loss.py: compute_loss()`）。
- 「とりあえず動く実装」で妥当性を誤魔化さない。検証（sanity check）を必ず添える。

### 4. Be Educational（なぜそうするかを説明する）

実装・リファクタの際は選択理由を 1〜3 文で添える（例: 「分岐が散るので Factory に集約」）。ブラックボックス化しない。長文の講義は不要。

### 5. Planning（複数ステップは計画してから）

複数ファイル / 新機能 / リファクタ / 1 時間超の作業は、着手前に `PLANS.md` にプランを作る。living sections（`Progress`, `Surprises & Discoveries`, `Decision Log`, `Outcomes & Retrospective`）を作業中に更新する。スコープが変わったら書き直す。意図的に省く場合は理由を一言述べる。

### 6. State & Memory（状態と記憶を残す）

- 作業の最初に `STATUS.md` を読み、最後に更新する。
- 確定した決定・再発防止したい落とし穴は `MEMORY.md` に追記する（上書きしない）。

### 7. Verification Before "Done"（完了の前に検証する）

「完了」と報告する前に通す（コマンドは Operation Guide）：

- 整形 `{{make format}}` → 静的解析 `{{make lint}}` → 型 `{{make typecheck}}` → テスト `{{make test}}`
- （研究）seed 固定で数値が再現するか

ドキュメント / メタ情報のみの変更では検証スタックを省略してよい。

### 8. Safety & Secrets

- API キー・認証情報・個人情報・未公開データを Markdown やコードに書かない / 外部に送らない。
- `.env*`・認証ファイルはコミットしない。
- 大きなデータセットはリポジトリに入れず、取得方法を文書化する。

## Project Structure Guide

<!-- TODO: 自分の構成に書き換える。下は研究用 Python の例 -->

### Overview

{{1〜2 文。例: 「時系列データから状態を推定する研究用ライブラリと実験スクリプト群」}}
Python は一貫性のため `{{uv run python ...}}` 経由で実行する。

### Repo Structure

```
.
├── AGENTS.md            # このファイル（AI 向け規約）
├── CLAUDE.md            # AGENTS.md を参照（Claude Code 用）
├── README.md            # 人間向け入口
├── PLANS.md             # 進行中タスクの計画
├── STATUS.md            # 今の状態
├── MEMORY.md            # 確定した決定・落とし穴
├── DESIGN.md            # UI 設計（UI がある場合のみ）
├── docs/
│   ├── ARCHITECTURE.md  # 設計思想・依存・パターン
│   ├── THEORY.md        # 数式・理論（人間所有）
│   ├── GLOSSARY.md      # 用語集
│   ├── EXPERIMENTS.md   # 実験ログ
│   └── adr/             # 重い意思決定の正式記録
├── src/{{package}}/     # ライブラリ本体
├── experiments/         # 実験スクリプト・設定
└── tests/               # テスト
```

### Module Boundaries

モジュールの責務と依存の向きは `docs/ARCHITECTURE.md` に集約。新モジュールを足すときはまずそこを確認・更新する。

## Operation Guide

### Prerequisites

<!-- TODO -->
- {{Python 3.10+}} / 依存管理 {{uv}} / タスクランナー {{make}}

### Setup

```bash
{{uv sync}}
```

### Development Workflow

1. `main` を取り込み作業ブランチを作る: `git checkout -b feature/<short-description>`（命名は Git Workflow 参照）
2. 複数ステップなら `PLANS.md` に計画する（§5）
3. 実装し、コードと一緒にテストを追加・更新する
4. 破壊的変更・API 変更・数式変更は着手前に人間へ確認（§1）
5. 検証スタックを通す（§7）
6. `STATUS.md` を更新し、確定事項を `MEMORY.md` へ
7. 小さく焦点を絞ったコミットを命令形で。PR を開く

### Frequently Used Commands

```bash
{{make format}}     # 整形
{{make lint}}       # 静的解析
{{make typecheck}}  # 型チェック
{{make test}}       # テスト（単体: uv run pytest -k <pattern>）
```

### Coding Conventions

<!-- TODO: 言語に合わせて -->
- スタイル: {{ruff / black 等}}。インポート順はツールに従う。
- 命名: 関数 `snake_case` / クラス `PascalCase`。略語を避ける（`lr` でなく `learning_rate`）。
- コメント: 完結した文。「なぜ」を書く（「何を」はコードで分かる）。
- 公開 API・ユーザー向け挙動を変えたらドキュメントを更新する。

### Git Workflow（ブランチ・コミット・PR）

- **ブランチ名:** `feature/xxx`（機能）/ `fix/xxx`（修正）。例: `feature/add-sampler`, `fix/seed-nondeterminism`
- **コミットメッセージ:** Conventional Commits 準拠 `<type>: <要約>`（命令形・簡潔）
  - `feat:` 機能追加 / `fix:` バグ修正 / `docs:` ドキュメント / `refactor:` 挙動を変えない整理 / `test:` テスト / `chore:` 雑務（依存更新・設定）
  - 例: `feat: add cosine LR scheduler`
- **PR:** 必ず検証スタック（`format` → `lint` → `typecheck` → `test`）を**通してから**作成する
  - テンプレート（`.github/PULL_REQUEST_TEMPLATE.md`）に沿い、概要・テスト計画・関連 issue を記載
  - 新挙動にはテストを追加。数式を変えたら `docs/THEORY.md` の更新有無を明記
- コミットは小さく焦点を絞る

### Review Checklist

- ✅ 検証スタック（format / lint / typecheck / test）が通る
- ✅ テストが新挙動とエッジケースを網羅
- ✅ 設計判断は複数案から選ばれ、理由が残っている
- ✅ 数式は人間確認済みで、式↔コードの対応が明記
- ✅ `STATUS.md` / `MEMORY.md` / 必要なら `docs/*` が更新済み
- ✅ コミット/ブランチが規約準拠（Conventional Commits / `feature|fix/xxx`）

## Agent Cheatsheet

**やる**
- 着手前に STATUS と該当 PLAN を読む
- 設計は 2〜3 案を出して人間に選ばせる
- 「なぜ」を 1〜3 文添える
- 数式は人間確認後に実装し、式↔コードを対応づける
- 完了前に検証スタックを通す
- 終わりに STATUS を更新、確定事項を MEMORY へ

**やらない**
- 数式・破壊的変更・新規依存・スコープ変更を独断で確定する
- 検証なしで「完了」と言う
- MEMORY を上書きする（追記のみ）
- 秘密情報・未公開データを書く / 送る
- 過剰設計（必要になる前の抽象化）
