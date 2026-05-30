# GLOSSARY.md — 用語集

用語のゆれを防ぎ、AI と人間が同じ意味で話すための辞書。

## Terms

| 用語（日本語） | Term (English) | 定義 | コード上の名前 | 備考 |
|------|------|------|------|------|
| プロジェクタ | projector | 画像や映像を投影する出力機器 | `projector` | ハードウェア制御は当面スコープ外 |
| 投影ウィンドウ | projection window | プロジェクタに表示するための専用ウィンドウ | `projection_window` | 操作 UI とは分ける |
| 操作 UI | operator UI | 投影を開始・停止・設定するための操作画面 | `operator_ui` | 将来追加候補 |
| ディスプレイ | display | OS が認識する画面出力先 | `display` | projector が display として見える想定 |
| モニター | monitor | display とほぼ同義。コード上は `display` に統一 | `display` | 呼称は `display` 優先 |
| ウィンドウ位置 | window position | OS デスクトップ座標上の左上位置 | `window_position` | 通常は `(x, y)` |
| ウィンドウ geometry | window geometry | 左上座標、幅、高さをまとめたもの | `window_geometry` | `x`, `y`, `width`, `height` |
| フルスクリーン | fullscreen | 指定ディスプレイ全体を覆う表示モード | `fullscreen` | 枠なし表示を含むかは設計時に確認 |
| ボーダーレス | borderless | タイトルバーや枠のないウィンドウ | `borderless` | フルスクリーンの実装手段候補 |
| 表示素材 | media | 投影する画像、動画、生成フレーム | `media` | ファイルとは限らない |
| 静止画 | image | 1 枚の画像素材 | `image` | PNG / JPEG など |
| 動画 | video | 時間方向を持つ映像素材 | `video` | 音声扱いは未決 |
| フレーム | frame | 動画や生成映像の 1 時点の画像 | `frame` | 配列や画像オブジェクトを想定 |
| 表示倍率 | scale | 投影ウィンドウ内で素材を拡大縮小する倍率 | `scale` | fit mode と併用する可能性あり |
| フィットモード | fit mode | 素材を投影ウィンドウへ収める方法 | `fit_mode` | `contain`, `cover`, `stretch`, `native` |
| テストパターン | test pattern | 位置・解像度・色確認用の画像 | `test_pattern` | 初期実装で有用 |
| 投影テスト | projection test | 実機や外部ディスプレイで表示結果を確認する作業 | `projection_test` | `docs/EXPERIMENTS.md` に記録 |

## Abbreviations

| 略語 | 正式名 | 意味 |
|------|------|------|
| API | Application Programming Interface | Python から呼び出す公開インターフェース |
| GUI | Graphical User Interface | 画面を持つ操作インターフェース |
| FPS | Frames Per Second | 1 秒あたりのフレーム数 |
| OS | Operating System | Windows などの基本ソフトウェア |

## Naming Conventions

- コードでは「モニター」より `display` を優先する。
- 投影用の表示面は `projection_window`、操作画面は `operator_ui` と呼び分ける。
- 位置は `x`, `y`、サイズは `width`, `height` を基本名にする。
- フルスクリーン指定は `fullscreen` に統一する。
