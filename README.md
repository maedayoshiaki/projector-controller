# projector-controller

Python から画像や映像をプロジェクタへ投影するための制御ライブラリを育てるリポジトリです。投影時のウィンドウ位置、対象ディスプレイ、フルスクリーン表示を扱える設計を目標にします。

> このファイルは人間向けの入口です。AI コーディングエージェント向けの運用規約は `AGENTS.md`、現在の作業状態は `STATUS.md` を参照してください。

## Current Status

- Python 3.12 + uv のパッケージ環境を作成済みです。
- `ProjectionWindow` API と pygame / SDL backend の MVP を追加済みです。
- 静止画、生成テストパターン、ウィンドウ位置、サイズ、対象 display、fullscreen 指定に対応しています。
- Rust / wgpu renderer と `RealtimeProjection` API を追加し、Python からリアルタイム RGBA/BGRA フレームを GPU 投影できます。
- 動画ファイルデコード、音声、設定ファイル形式、操作 UI は未実装です。

## Goals

- Python から呼び出せる投影制御 API を提供する。
- 静止画と映像の投影を扱う。
- 投影ウィンドウの位置、サイズ、対象ディスプレイ、フルスクリーン表示を指定できるようにする。
- 将来的な投影テストや現場ごとの設定を記録し、再現しやすくする。

## Non-Goals for the Initial Setup

- プロジェクションマッピング、台形補正、色補正などの数式を今すぐ実装しない。
- GUI 操作画面や動画再生をこの段階で作り込まない。
- ハードウェア固有の制御プロトコルを先に作り込まない。

## Usage

```python
from projector_controller import ProjectionWindow

with ProjectionWindow(display=1, fullscreen=True, background="black") as window:
    window.show_image("media/test-pattern.png")
    window.wait()
```

テストパターンを表示する場合:

```python
from projector_controller import ProjectionWindow

# position 省略 -> display 0 の中央。position=(x, y) でデスクトップ絶対座標。
with ProjectionWindow(display=0, fullscreen=False, size=(1280, 720)) as window:
    window.show_test_pattern()
    window.wait()
```

リアルタイムフレームを Rust GPU renderer へ送る場合:

```python
from projector_controller import RealtimeProjection

width = 640
height = 360
frame = bytes([0, 0, 0, 255]) * (width * height)  # RGBA8

with RealtimeProjection(display=0, fullscreen=False, size=(1280, 720)) as projection:
    projection.submit_frame(frame, width=width, height=height)
```

## Requirements

- Python 3.12（`.python-version` で指定）
- uv
- pygame 2.6+
- Rust toolchain（Rust renderer を使う場合）

## Quickstart

```powershell
uv sync --dev
uv run projector-controller --list-displays
uv run projector-controller --display 0 --width 1280 --height 720 --duration 5
```

Rust GPU renderer を使う場合:

```powershell
cargo build -p projector-controller-renderer
# realtime 経路の display 番号は Rust renderer(winit) 列挙が権威。これで番号を確認する。
uv run projector-controller --list-monitors
uv run python examples\realtime_frames.py
```

> `--list-displays` は pygame 経路（`ProjectionWindow`）用、`--list-monitors` は realtime 経路
> （`RealtimeProjection`）用です。realtime の `--display` には `--list-monitors` の番号を使ってください。

フルスクリーンでテストパターンを表示する場合:

```powershell
uv run projector-controller --display 1 --fullscreen
```

ウィンドウ位置を指定する場合（`--x/--y` はデスクトップ絶対座標。省略すると `--display` の中央）:

```powershell
# display 1 の中央にウィンドウ表示
uv run projector-controller --display 1 --width 1280 --height 720
# デスクトップ絶対座標 (1500, 100) に表示
uv run projector-controller --x 1500 --y 100 --width 800 --height 600
```

画像ファイルを表示する場合:

```powershell
uv run projector-controller --image path\to\image.png --display 0 --fit-mode contain
```

Esc キーまたはウィンドウの閉じる操作で終了します。`--duration` を指定すると秒数で自動終了します。

## Development Commands

```powershell
uv run ruff format .
uv run ruff check .
uv run mypy src tests
uv run pytest
cargo fmt --check
cargo clippy -p projector-controller-renderer --all-targets -- -D warnings
cargo test -p projector-controller-renderer
```

## Documentation Map

| ファイル | 内容 |
|------|------|
| `AGENTS.md` | AI エージェント向けの運用規約 |
| `STATUS.md` | 今の作業状態、次の作業、未決事項 |
| `PLANS.md` | 複数ステップ作業の計画 |
| `MEMORY.md` | 確定した決定、規約、落とし穴 |
| `docs/ARCHITECTURE.md` | 設計方針、候補案、モジュール境界 |
| `docs/GLOSSARY.md` | 用語集 |
| `docs/THEORY.md` | 投影幾何や補正など、数式を扱う場合の記録 |
| `docs/EXPERIMENTS.md` | 投影テスト、現場検証、再現条件のログ |
| `DESIGN.md` | 投影ウィンドウと将来の操作 UI の表示設計 |
| `CONTRIBUTING.md` | 人間の開発者向けの参加手順 |

## Open Questions

- Rust renderer のフレーム転送を copy ベースから shared memory / ring buffer に進めるか。
- 動画デコードと音声をどのレイヤで扱うか。
- TOML などの設定ファイルをいつ導入するか。
- Rust renderer で display 番号、fullscreen、座標指定が期待通り動くか。
- プロジェクションマッピング、台形補正、色補正をいつ扱うか。

## License

[MIT](./LICENSE)
