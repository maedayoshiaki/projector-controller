# MEMORY.md — 確定した知識

**過去（確定）**を扱うファイル。もう動かない事実・決定・落とし穴の蓄積。
新しい確定事項は追記し、既存の実データを削除しない。

## Decisions

| 日付 | 決定 | 理由 | 影響範囲 |
|------|------|------|------|
| 2026-05-30 | このリポジトリは Python から画像・映像をプロジェクタへ投影するためのプログラムを扱う | ユーザーがプロジェクト目的として明示 | README、設計文書、今後の実装 |
| 2026-05-30 | 初期整理では公開 API、依存ライブラリ、バックエンドを確定しない | AGENTS.md の Human-in-the-Loop に従い、人間確認前に設計を固定しないため | docs/ARCHITECTURE.md、README |
| 2026-05-30 | 投影ウィンドウ、操作 UI、display という用語を分けて使う | 投影面と操作画面、OS 上の表示先を混同しないため | docs/GLOSSARY.md、DESIGN.md |
| 2026-05-30 | 初期実装は Python 3.12 + uv、pygame / SDL backend、`ProjectionWindow` API で進める | display 指定、fullscreen、ウィンドウ位置を先に検証するため | pyproject.toml、src/projector_controller、README、ARCHITECTURE |
| 2026-05-30 | MVP は静止画と生成テストパターンに絞り、動画・音声・操作 UI は後回しにする | 投影面の基本制御を先に安定させるため | src/projector_controller、examples、docs/EXPERIMENTS.md |

## Conventions

- **文書:** 人間向け入口は `README.md`、AI 向け規約は `AGENTS.md`、現在地は `STATUS.md`、確定事項は `MEMORY.md` に分ける。
- **用語:** コード上は「モニター」より `display` を優先する。
- **投影表示:** 投影ウィンドウの既定背景は黒を基本候補にする。
- **設計:** GUI / メディア再生バックエンド固有処理は adapter に隔離する。

## Gotchas & Pitfalls

- Python 実装環境は `uv sync --dev` で作成する。
- フルスクリーン、ウィンドウ座標、ディスプレイ選択は OS と接続環境の影響を受けるため、実機テストログを残す必要がある。

## Domain Facts

- 投影対象は静止画と映像を想定する。
- 投影時にウィンドウ位置指定とフルスクリーン表示へ対応したい。
- 現時点ではプロジェクションマッピング、台形補正、色補正などの数式は未定義。

## Glossary Pointer

用語の定義・和英対応は `docs/GLOSSARY.md` に集約する。
