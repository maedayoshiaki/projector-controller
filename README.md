# projector-controller

Python から画像や映像をプロジェクタへ投影するための制御ライブラリを育てるリポジトリです。投影時のウィンドウ位置、対象ディスプレイ、フルスクリーン表示を扱える設計を目標にします。

> このファイルは人間向けの入口です。AI コーディングエージェント向けの運用規約は `AGENTS.md`、現在の作業状態は `STATUS.md` を参照してください。

## Current Status

- 現時点ではドキュメント整理段階です。
- Python パッケージ、実行コマンド、依存ライブラリはまだ未作成・未確定です。
- 公開 API、GUI / 動画再生バックエンド、設定ファイル形式は人間確認後に決めます。

## Goals

- Python から呼び出せる投影制御 API を提供する。
- 静止画と映像の投影を扱う。
- 投影ウィンドウの位置、サイズ、対象ディスプレイ、フルスクリーン表示を指定できるようにする。
- 将来的な投影テストや現場ごとの設定を記録し、再現しやすくする。

## Non-Goals for the Initial Setup

- プロジェクションマッピング、台形補正、色補正などの数式を今すぐ実装しない。
- GUI / メディア再生ライブラリをこの段階で固定しない。
- ハードウェア固有の制御プロトコルを先に作り込まない。

## Planned Usage Sketch

以下は API の形を考えるためのスケッチであり、確定した公開 API ではありません。

```python
from projector_controller import ProjectionWindow

with ProjectionWindow(display=1, fullscreen=True, background="black") as window:
    window.show_image("media/test-pattern.png")
```

この形にするか、関数ベースにするか、設定ファイルを中心にするかは `docs/ARCHITECTURE.md` の候補を見て決めます。

## Requirements

- Python: バージョン未確定。最初の実装前に決める。
- 依存管理: 未確定。
- GUI / メディア再生バックエンド: 未確定。

## Quickstart

まだ実行可能な Python パッケージはありません。実装環境を作る段階で、セットアップ手順と実行コマンドをここに追記します。

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

- 画像・映像表示のバックエンドに何を使うか。
- 最初の公開 API は、関数ベース、ウィンドウオブジェクトベース、設定ファイルベースのどれにするか。
- ディスプレイ番号、座標、フルスクリーン指定をどう表現するか。
- 実行環境を `uv` / `pip` / その他のどれで管理するか。

## License

[MIT](./LICENSE)
