# ARCHITECTURE.md — 設計方針

プロジェクタ投影用 Python ライブラリの設計メモ。初期実装では Python 3.12 + uv、`ProjectionWindow` API、pygame / SDL backend を採用する。

## Design Goals

- Python から画像・映像の投影を呼び出せる。
- 投影ウィンドウの位置、サイズ、対象ディスプレイ、フルスクリーン表示を明示できる。
- GUI / 動画再生バックエンドを後から差し替えられる。
- 現場ごとの投影条件を記録し、再現しやすくする。
- 最初は小さく実装し、プロジェクションマッピングや補正は必要になってから拡張する。

## Constraints

- 公開 API は `ProjectionWindow` を入口に小さく始める。
- 初期 backend は pygame / SDL。将来差し替えられるよう adapter に隔離する。
- Windows 環境での利用を当面の主対象にするが、OS 固有処理は可能な範囲で adapter に隔離する。
- 大容量の画像・動画素材はリポジトリに含めない。

## Architectural Style

初期方針は「小さなレイヤード構成 + adapter 境界」。プロジェクタ制御では GUI / 動画再生ライブラリの差し替え可能性が重要なので、核となる設定・状態・API と、バックエンド固有処理を分ける。

```text
user code / examples
        |
public API facade
        |
projection window facade
        |
config / fit calculation
        |
backend adapters
        |
OS / window system / media library
```

## Public API Decision

| 案 | 概要 | 長所 | 短所 |
|----|------|------|------|
| A | 関数ベース: `show_image(path, fullscreen=True)` | 最初に使いやすい | 状態管理や連続再生が複雑になる |
| B | ウィンドウオブジェクト: `ProjectionWindow(...).show_image(...)` | ウィンドウ位置、フルスクリーン、再利用を表現しやすい | 初期 API が少し重くなる |
| C | 設定ファイル中心: `run_projection(config)` | 現場設定の再現性が高い | 小さなスクリプトからは回りくどい |

採用案は B。理由は、ユーザー要件の「ウィンドウの場所」「フルスクリーン」を状態として自然に持てるため。設定ファイル中心の入口は、現場設定を共有したくなった段階で追加する。

## Backend Decision

| 案 | 概要 | 向いていること | 注意点 |
|----|------|------|------|
| A | OpenCV 系 | 静止画表示や簡単な動画処理 | マルチディスプレイや UI 制御は検証が必要 |
| B | SDL / pygame 系 | フルスクリーン、ディスプレイ選択、イベント処理 | 高度な動画再生は別途検討が必要 |
| C | Qt / PySide 系 | ウィンドウ制御、UI、動画表示をまとめやすい | 依存が重くなりやすい |
| D | Web / browser 系 | HTML / CSS / video を使える | Python だけで完結しにくい |

採用案は B。投影ウィンドウ、display 指定、fullscreen の検証を先に固めるため。バックエンドは adapter に閉じ込め、公開 API から直接依存させない。

## Planned Module Map

現在の実装構成。

| モジュール | 責務 | 依存してよい先 |
|------|------|------|
| `projector_controller.window` | `ProjectionWindow` 公開 API | `config`, backend adapter |
| `projector_controller.config` | 表示設定、ウィンドウ設定、値オブジェクト | なし |
| `projector_controller.fit` | `contain` / `cover` / `stretch` / `native` の配置計算 | `config` |
| `projector_controller.display` | ディスプレイ一覧の取得 | `config`, backend adapter |
| `projector_controller.adapters` | GUI / 動画再生バックエンド固有処理 | 外部ライブラリ |
| `projector_controller.cli` | 手動検証用 CLI | `window`, `display`, `config` |

```mermaid
graph TD
  cli --> window
  cli --> display
  window --> adapters
  display --> adapters
  fit --> config
  window --> config
```

## Dependency Rules

- `config` と `fit` は外部 GUI ライブラリに依存しない。
- バックエンド固有処理は `adapters` に閉じ込める。
- 公開 API は adapter の具体クラスを直接露出しない。
- OS ごとの分岐は小さくまとめ、テスト可能な純粋ロジックと分離する。
- 大きな抽象は、同じ分岐や重複が実際に 3 回程度出てから導入する。

## Key Data Concepts

- `DisplaySpec`: ディスプレイ番号、名前、原点座標、解像度、スケールなど。
- `WindowGeometry`: ウィンドウ左上座標、幅、高さ。
- `ProjectionConfig`: フルスクリーン、対象ディスプレイ、背景色、表示倍率など。
- `FitMode`: `contain`, `cover`, `stretch`, `native` などの表示方法。
- `MediaSource`: 静止画、動画、生成フレームなどの入力。

## Configuration Options（未確定）

| 案 | 概要 | 長所 | 短所 |
|----|------|------|------|
| A | Python の dataclass / dict だけ | すぐ使える | 現場設定をファイルで共有しにくい |
| B | TOML / YAML などの設定ファイル | 再現性が高い | パーサ依存とスキーマ管理が必要 |
| C | Python API + 任意で設定ファイル | 小さく始めて拡張しやすい | 2 系統の整合性管理が必要 |

初期実装では Python API と dataclass を採用する。設定ファイルは、現場設定を共有する必要が出た段階で TOML などを比較して導入する。

## Testing Strategy

- 設定や座標計算は純粋関数として単体テストする。
- GUI バックエンドは adapter 単位で薄くし、可能ならモックでテストする。
- 実機プロジェクタやマルチディスプレイでしか検証できない内容は `docs/EXPERIMENTS.md` に記録する。
- フルスクリーン、ウィンドウ位置、ディスプレイ選択は OS / 環境差が大きいため、手動検証ログを残す。

## Open Decisions

- 設定ファイル形式を導入するか、導入するならどの形式にするか。
- 動画再生と音声を pygame で拡張するか、Qt などへ広げるか。
- プロジェクションマッピングや台形補正をいつ扱うか。
