# PLANS.md — タスクの計画

**未来**を扱うファイル。「これから何をするか」の設計図。
複数ファイルにまたがる作業、新機能、大きなリファクタ、数式・アルゴリズム実装では着手前にプランを書く。

---

## Plan: pygame `show_frame`（生ピクセル byte 列表示）

- **Status:** `Done`
- **Owner:** AI
- **Created / Updated:** 2026-06-09 / 2026-06-09
- **Related:** src/projector_controller/{config,window,adapters/base,adapters/pygame_backend}.py, tests/test_show_frame.py, examples/show_frame.py, README.md, docs/ARCHITECTURE.md

### Goal & Non-Goals
- **Goal:** pygame backend に「生ピクセル byte 列を渡して画面を更新する」公開 API を追加する。`ProjectionWindow.show_frame(data, size, *, pixel_format, fit_mode)` を入口にする。
- **Non-Goals:** CLI 対応（生バイトファイルの入力仕様は別途）、realtime(Rust) 経路の変更、行間パディング（stride）対応、動画/連番ループの抽象化。

### Approach（人間が選んだ案）
- **API の形:** `ProjectionWindow` にメソッド追加（base protocol + pygame backend に実装）。既存 `show_image`/`show_test_pattern` と一貫した入口にするため。
- **ピクセルフォーマット:** RGB と RGBA 両対応・既定 RGB。realtime 経路（RGBA）との整合を取りつつ、最小の RGB を既定に。
- **スコープ:** 今回はライブラリ API のみ（CLI は見送り）。
- いずれも 2026-06-09 に人間承認済み（AskUserQuestion）。

### Milestones / Steps
- [x] `config` に `PixelFormat` / `PIXEL_FORMAT_BYTES` / `normalize_pixel_format` を追加
- [x] `adapters/base` protocol に `show_frame` を追加
- [x] pygame backend に `show_frame` を実装（`image.frombuffer` → 既存 `_draw_surface` 再利用、byte 長検証は open 前）
- [x] `ProjectionWindow` facade に `show_frame` を追加
- [x] テスト（byte 長不一致 / 不明フォーマット / 検証ヘルパ。GUI 不要）と `examples/show_frame.py`
- [x] README / ARCHITECTURE / STATUS / MEMORY を更新
- [x] format / lint / typecheck / test と RGB/RGBA の windowed smoke を通す

### Decision Log
- 2026-06-09: byte 長検証（`width*height*bpp`）を window を開く前に行い、不一致は `got/expected` 付き `ValueError`。pygame の不透明な `frombuffer` 失敗より明確で、GUI なしで単体テストできる。
- 2026-06-09: `frombuffer` は buffer を非コピーで包むが、`_draw_surface` が同期的に blit/scale して display surface に取り込むため、buffer は呼び出し中だけ生きていればよい（dangling 参照なし）。
- 2026-06-09: `normalize_pixel_format` は `dict[PixelFormat, int]` への `in` で mypy が str→PixelFormat を絞れるため、`normalize_fit_mode`（frozenset[str]）と違い `type: ignore` 不要。

### Outcomes & Retrospective
- 2026-06-09: 完了。生ピクセル byte 列（RGB/RGBA, tightly-packed）を pygame backend で投影できるようになった。検証スタック全緑（50 passed）＋ RGB/RGBA の windowed smoke 成功。realtime 経路は無改修。

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

---

## Plan: ウィンドウ位置(x,y)の仕様確定と実装

- **Status:** `Done`
- **Owner:** AI
- **Created / Updated:** 2026-05-31 / 2026-05-31
- **Related:** src/projector_controller/{config,window,cli,adapters/pygame_backend}.py, docs/ARCHITECTURE.md

### Goal & Non-Goals
- **Goal:** `--x/--y`（ウィンドウ位置）の座標原点を確定し、`ProjectionWindow`・CLI・backend で一貫して扱えるようにする。
- **Non-Goals:** ディスプレイ相対座標、複数ウィンドウ、動画再生は扱わない。

### Context & Constraints
旧実装は windowed 時に常に `SDL_VIDEO_WINDOW_POS=geometry.x,y`（既定 0,0）と `set_mode(display=N)` を両方渡しており、(1) 位置未指定でも (0,0) に固定される、(2) 絶対座標と display 指定が競合し得る、という問題があった。座標原点の定義は公開 API 仕様なので人間確認が必要（AGENTS.md ルール1）。

### Approach（検討した案）

| 案 | 概要 | 長所 | 短所 |
|----|------|------|------|
| A | 絶対座標＋画面ターゲット（位置省略時は display 中央） | 追加依存なし・堅牢。既存バグも解消 | ディスプレイ相対指定はできない |
| B | 絶対座標のみ | 最小 | 「画面 N に出す」が利用者計算頼み |
| C | ディスプレイ相対座標（ctypes で原点取得） | 直感的 | pygame 公開 API 外。脆い実装が増え「小さく始める」に反する |

- **採用案:** A（2026-05-31 人間承認）
- **理由:** pygame 2.6.1 にディスプレイ原点取得 API が無いことを probe で確認。追加依存なしで堅牢、かつ既存の (0,0) 固定バグを同時に解消できる。

### Milestones / Steps
- [x] probe で pygame の display 原点 API の有無を確認
- [x] `ProjectionConfig` を `geometry` から `position(None=中央)`/`size` へ
- [x] `ProjectionWindow` の placement 解決（`geometry=` 後方互換維持）
- [x] pygame backend を「position 指定時のみ絶対配置」に修正
- [x] CLI `--x/--y` を default=None にし、省略時は中央
- [x] tests（config/cli の中央デフォルト・絶対座標）を追加
- [x] README / ARCHITECTURE / STATUS / MEMORY を更新
- [x] format / lint / typecheck / test を通す

### Living Sections

#### Decision Log
- 2026-05-31: 案 A 採用。座標原点はデスクトップ絶対、位置省略時は対象 display 中央。

#### Outcomes & Retrospective
- 2026-05-31: 位置指定を実装し、windowed の (0,0) 固定バグを解消。実機での座標挙動は次の手動検証（projtest）で確認する。

---

## Plan: pygame 動画再生

- **Status:** `Superseded`
- **Owner:** AI
- **Created / Updated:** 2026-05-31 / 2026-05-31
- **Related:** src/projector_controller/{window,cli,adapters/pygame_backend}.py, README.md, docs/ARCHITECTURE.md

### Goal & Non-Goals
- **Goal:** pygame の投影ウィンドウへ動画フレームを描画し、CLI から動画ファイルを再生できる最小機能を追加する。
- **Non-Goals:** 音声再生、シーク UI、プレイリスト、動画編集、色補正、台形補正は初期実装では扱わない。

### Context & Constraints
pygame 2.6.1 (classic) には `pygame.movie` が無いため、mp4 などの一般的な動画ファイルを読むには別のデコーダが必要。投影ウィンドウ、display、fullscreen、fit mode は既存 pygame backend を再利用し、動画デコードだけを小さく追加する。

AGENTS.md に従い、新規依存ライブラリ追加と公開 API 追加は人間確認後に進める。

### Approach（検討中の案）

| 案 | 概要 | 長所 | 短所 |
|----|------|------|------|
| A | 依存追加なし。連番画像を pygame で一定 FPS 表示 | 最小・安定・追加依存なし | mp4 などの動画ファイルを直接再生できない |
| B | `opencv-python-headless` で動画をデコードし、pygame Surface に描画 | 実装が単純。Windows wheel で導入しやすい。mp4 検証を始めやすい | 新規依存が大きい。音声なし。codec は OpenCV wheel に依存 |
| C | `av` (PyAV) で動画をデコードし、pygame Surface に描画 | 動画デコード用途に素直。タイムスタンプ制御を拡張しやすい | 新規依存。API は OpenCV より少し複雑。音声同期は別実装 |

- **推奨案:** B
- **理由:** 最初の狙いは「プロジェクタに動画を出す」ことなので、実装量と検証速度を優先する。pygame は window/display/fullscreen を担当し、OpenCV は無音のフレームデコードに限定すれば adapter 境界に閉じ込められる。

### Milestones / Steps
- [ ] 人間がデコーダ方式、初期の音声有無、公開 API 名を確認する
- [ ] 必要な依存を `pyproject.toml` / `uv.lock` に追加する
- [ ] 動画再生ループを pygame backend に追加する
- [ ] `ProjectionWindow.show_video(...)` と CLI `--video` を追加する
- [ ] README / ARCHITECTURE / STATUS / MEMORY を更新する
- [ ] format / lint / typecheck / test を通す
- [ ] 可能なら短いサンプル動画で手動再生確認する

### Risks & Compatibility
- 新規依存追加が必要になる場合がある。
- 初期実装は無音。音声が必要なら別途 pygame mixer か外部音声再生との同期を検討する。
- 動画 FPS / タイムスタンプ / コーデック差は実機検証が必要。

---

### Living Sections

#### Progress
- 2026-05-31: pygame 2.6.1 で `pygame.movie` が無いことを確認。
- 2026-05-31: 方式案を整理。新規依存と公開 API 追加は人間確認待ち。

#### Surprises & Discoveries
- 2026-05-31: pygame だけでは mp4 などの一般的な動画ファイル再生を完結しにくい。

#### Decision Log
- 2026-05-31: ユーザー判断により、pygame + 動画デコーダ方式ではなく Rust renderer でリアルタイムフレーム投影に耐える設計へ切り替える。

#### Outcomes & Retrospective
- Superseded by "Plan: Rust GPU realtime frame projection".

---

## Plan: Rust GPU realtime frame projection

- **Status:** `Implemented; hardware verification pending`
- **Owner:** AI
- **Created / Updated:** 2026-05-31 / 2026-05-31
- **Related:** Cargo.toml, pyproject.toml, src/projector_controller, rust renderer crate, docs/ARCHITECTURE.md

### Goal & Non-Goals
- **Goal:** Rust が window / event loop / GPU device / rendering loop を所有し、Python からリアルタイムフレームを投入してプロジェクタへ投影できる基盤を作る。
- **Non-Goals:** 動画ファイルデコード、音声同期、GUI 操作画面、台形補正式の確定、色補正式の確定は初期実装では扱わない。

### Context & Constraints
pygame backend は display / fullscreen / DPI の実機検証に成功したが、動画ファイル再生や高頻度フレーム送信の基盤としては弱い。今後は「動画を再生する」のではなく、外部生成された frame を低遅延で GPU texture に送り、shader で投影する frame sink を作る。

Rust 側は `wgpu` を第一候補にする。`wgpu` は Rust の native GPU API で、Vulkan / Metal / D3D12 / OpenGL 上で動作する。Windows では D3D12 / Vulkan 経由で GPU を使える可能性が高い。window / monitor / fullscreen は `winit` を候補にする。

AGENTS.md に従い、Rust workspace 追加、新規依存、公開 API、Python 連携方式は人間確認後に確定する。

### Approach（検討中の案）

| 案 | 概要 | 長所 | 短所 |
|----|------|------|------|
| A | PyO3 extension。Python process 内に Rust renderer を組み込み、`submit_frame()` を呼ぶ | Python API が自然。配布は Python package に統合しやすい | GUI/event loop と Python/GIL の境界が難しい。window thread 制約に注意が必要 |
| B | Rust renderer subprocess。Python が renderer を起動し、制御 IPC + frame transfer で送る | Rust が event loop と GPU を完全に所有できる。Python 側の GIL 影響を受けにくい。クラッシュ分離しやすい | IPC 設計が必要。初期実装は少し増える |
| C | Rust host application。Rust がメインアプリになり、必要な Python 処理を埋め込む/呼び出す | 最高性能・最小遅延を狙いやすい | Python ライブラリとしての使いやすさが下がり、プロジェクトの性格が大きく変わる |

- **推奨案:** B
- **理由:** 最も重要なのは Rust renderer が GPU と event loop を安定して握ること。Python は投影制御と frame producer に限定し、Rust subprocess を frame sink として扱うと、性能・堅牢性・将来の standalone 化のバランスがよい。

### Initial Architecture Sketch
- `projector-controller-renderer`: Rust binary。`winit` window + `wgpu` renderer を持つ。
- Python `ProjectionWindow` / 新 facade: Rust renderer process を起動し、display / fullscreen / size / position を渡す。
- 初期 frame format: `RGBA8` または `BGRA8` の連続メモリ（行間パディング無しの tightly-packed = `width * height * 4` bytes）。ヘッダで width / height / pixel format / fit mode を明示する（stride は実装せず、ヘッダの未使用 reserved u16 を将来の stride/flags 用に確保）。
- 初期転送: まずは copy ベースの IPC で correctness を作る。性能が足りない場合、shared memory + ring buffer に切り替える。
- Rust renderer: GPU texture を再利用し、frame 到着ごとに texture upload、fullscreen quad/triangle で描画する。
- fit mode: Rust 側で quad の頂点を再計算（`frame_vertices`）して `contain` / `cover` / `stretch` / `native` を扱う。

### Milestones / Steps
- [x] 人間が Python-Rust 接続方式（A/B/C）と初期転送方式を確認する
- [x] Rust toolchain / Cargo workspace / renderer crate の構成を追加する
- [x] `winit` window + `wgpu` swapchain の最小表示を実装する
- [ ] display / fullscreen / windowed position を Rust 側で実機再検証する
- [x] Python から renderer を起動/終了する wrapper を追加する
- [x] `submit_frame` 相当の API とサンプル frame producer を追加する
- [x] README / ARCHITECTURE / STATUS / MEMORY / EXPERIMENTS を更新する
- [x] Rust format / clippy / test と Python format / lint / typecheck / test を通す

### Risks & Compatibility
- `wgpu` / `winit` は API 変更があり得るため、Rust renderer crate の adapter 境界に閉じ込める。
- 初期 copy ベース IPC では 4K/60fps に届かない可能性がある。性能不足が見えたら shared memory / ring buffer を導入する。
- Windows fullscreen / display 番号 / DPI は pygame と挙動が異なる可能性があるため、再度 `docs/EXPERIMENTS.md` に実機ログを残す。
- Python API は既存 `ProjectionWindow` を保つか、新しい `RealtimeProjection` を追加するか確認が必要。

---

### Living Sections

#### Progress
- 2026-05-31: ユーザーが Rust renderer 方向を選択。
- 2026-05-31: Rust + GPU frame sink の案を整理。
- 2026-05-31: `projector-controller-renderer` Rust crate を追加。`winit` window + `wgpu` render pipeline + TCP frame protocol を実装し、`cargo check` 通過。
- 2026-05-31: Python `RealtimeProjection` facade、frame header encoder、サンプル `examples/realtime_frames.py` を追加。
- 2026-05-31: Python/Rust の検証スタックを通過。`RealtimeProjection` から Rust renderer へ 64x64 RGBA frame を送る windowed smoke test に成功。

#### Surprises & Discoveries
- なし。

#### Decision Log
- 2026-05-31: 動画ファイル再生より、リアルタイムフレーム送信に耐える Rust renderer 設計を優先する。
- 2026-05-31: 初期接続方式は Rust renderer subprocess + localhost TCP。まず copy-based protocol で correctness を作り、性能不足が見えたら shared memory / ring buffer に進める。

#### Outcomes & Retrospective
- Rust / wgpu renderer MVP を追加した。初期 protocol は localhost TCP の copy-based frame 転送で、Python API は `RealtimeProjection.submit_frame(...)`。外部 display / fullscreen / DPI / 座標挙動は `projtest-002` で実機確認する。

---

## Plan: モジュール化 / 配布準備（Phase 0: 土台固め）

- **Status:** `Done`
- **Owner:** AI
- **Created / Updated:** 2026-05-31 / 2026-05-31
- **Related:** src/projector_controller/realtime.py, pyproject.toml, tests/, README.md

### Goal & Non-Goals
- **Goal:** 「他の Python から呼び出す」ための土台を非破壊で固める。具体的には (1) Rust renderer バイナリの発見を repo の `target/` 依存から脱却させ、環境変数 / PATH も探すようにする、(2) PyPI 公開を見据えたパッケージメタデータを整備する、(3) `import projector_controller` の健全性（軽量 import・公開 API）をテストで保証する。
- **Non-Goals:** ビルドバックエンドの maturin 切替（Phase 1）、CI / クロスプラットフォーム wheel / PyPI 公開（Phase 2）、公開 API のシグネチャ破壊的変更。

### Context & Constraints
ユーザー判断: 最終配布先は **PyPI 公開**、Rust バイナリは **maturin で wheel 同梱**。ただし一気に進めず Phase 0 → 1 → 2 と段階化する（Phase 0 は配布方法に依存しない土台）。`find_renderer_binary()` は現状 `repo_root/target/{debug,release}` しか見ないため、`pip install` 環境では `RealtimeProjection` が `FileNotFoundError` になる。これが最初の実用上のギャップ。

### Approach（段階化）

| Phase | 内容 | 規約上の扱い |
|----|------|------|
| 0 | renderer 発見の堅牢化・メタデータ整備・import テスト（本プラン） | 非破壊 |
| 1 | build backend を maturin 化し Rust バイナリを wheel 同梱 | ビルド構成変更＋新規依存（要確認） |
| 2 | GitHub Actions でクロスプラットフォーム wheel、TestPyPI→PyPI 公開 | CI・公開（実機検証後を推奨） |

renderer 発見の探索順（Phase 0）: `renderer_path` 引数 → 環境変数 `PROJECTOR_CONTROLLER_RENDERER` → PATH（`shutil.which`、maturin の `bindings="bin"` install 先）→ repo の `target/{debug,release}`（開発時フォールバック）。環境変数が指す先が存在しない場合は黙ってフォールバックせず明示エラーにする（利用者の意図を尊重）。

### Milestones / Steps
- [x] `find_renderer_binary()` を env var / PATH / target の順で探索するよう堅牢化
- [x] pyproject に classifiers / keywords / urls を追加（license 方式は据え置き）
- [x] renderer 発見の探索順と、軽量 import / 公開 API のテストを追加
- [x] README に「同一マシンへ editable install して別 Python から import」手順を追記
- [x] format / lint / typecheck / test と `uv build`（メタデータ検証）を通す
- [x] STATUS / MEMORY を更新する

### Risks & Compatibility
- 非破壊。既存の `target/` フォールバックは維持するので開発時の挙動は変わらない。
- pyproject のメタデータ追加はビルドを壊さない範囲に限定し、`uv build` で検証する。
- maturin 切替（Phase 1）で build backend が変わるため、Phase 0 ではビルド構成に手を入れない。

### Living Sections

#### Progress
- 2026-05-31: Phase 化を決定（PyPI 公開 + maturin 同梱、ただし段階的に）。Phase 0 着手。
- 2026-05-31: Phase 0 完了。renderer 発見の堅牢化、pyproject メタデータ、import/発見テスト、README 追記を実装。`uv build` で wheel/sdist 生成、fresh venv に install して別ディレクトリから import・公開 API 利用・RealtimeProjection 構築・env var 経由 renderer 解決を実機確認。pytest 25 passed。

#### Outcomes & Retrospective
- 2026-05-31: 非破壊で「他の Python から呼び出す」土台が完成。`import projector_controller` は軽量（pygame 遅延ロード）、renderer は env var/PATH でも解決可能、メタデータは PyPI 公開を見据えた形に。次は Phase 1（maturin で Rust バイナリ wheel 同梱、ビルド構成変更のため人間確認後）。

---

## Plan: モジュール化 / 配布準備（Phase 1: 2 パッケージ分割で renderer を配布可能にする）

- **Status:** `Done`
- **Owner:** AI
- **Created / Updated:** 2026-05-31 / 2026-05-31
- **Related:** pyproject.toml, packages/renderer/{Cargo.toml,pyproject.toml}, src/projector_controller/realtime.py

### Goal & Non-Goals
- **Goal:** realtime 経路を `pip install` で動かせるようにする。配布単位を 2 パッケージに分割する: 本体 `projector-controller`（pure-python universal wheel + console_script, hatchling）と、Rust renderer を同梱する `projector-controller-renderer`（OS 別 wheel, maturin bin）。本体の `[realtime]` extras で renderer を引く。
- **Non-Goals:** CI でのクロスプラットフォーム wheel ビルドと PyPI 実公開（Phase 2）。protocol の shared memory 化。動画/音声。

### Context & Constraints（PoC で確定した事実）
2026-05-31 の PoC（`poc/maturin-bundle`、abandon 済み）で次を実機確認した:
- maturin `bin` バインディングで Rust バイナリ同梱 wheel をビルドでき（4.5MB, win_amd64）、install すると renderer が venv の `Scripts/` に入り実行できる。
- **ただし maturin bin は `[project.scripts]`（console_script）と同居できない**（"Defining scripts and working with a binary doesn't mix well"）。
- maturin wheel はプラットフォーム別になる。pygame のみの利用者にまで OS 別 wheel を強いるのは過剰。
- `module-name = "projector_controller"` の指定が必要だった（project 名がハイフン、モジュールが snake_case のため）。
- PoC では venv 非 activate での PATH 解決が漏れた。`find_renderer_binary()` に `sysconfig` の scripts ディレクトリ探索を足すと堅牢。

これらから、本体（pure-python + console_script）と renderer（maturin bin）を分けると各々が自然なビルドバックエンドを使え、PoC の制約に衝突しない。配布設計は案 A（2 パッケージ分割）をユーザー承認済み（2026-05-31）。

### Approach（ディレクトリ構成の検討案）

renderer パッケージ（maturin）の置き場所と cargo workspace の扱い。

| 案 | 概要 | 長所 | 短所 |
|----|------|------|------|
| L1 | renderer crate を独立パッケージ化し、`packages/renderer/` に `pyproject.toml`(maturin)+`Cargo.toml`+`src/` を自己完結で置く。workspace を解体 | sdist/wheel が自己完結。公開単位が明確 | crate 移動の差分が大きい |
| L2 | crate は現状の `crates/projector-controller-renderer/` のまま、そこに `pyproject.toml`(maturin) を追加。root workspace は維持し manifest-path で指す | 移動が最小 | sdist に workspace root が絡み、別パッケージとして公開する境界が曖昧。lock 共有 |
| L3 | monorepo を維持しつつ renderer 用に別 `pyproject.toml` を root に置き分け | - | 1 ディレクトリ 2 パッケージで極めて紛らわしい。却下 |

- **推奨案:** L1。理由: PyPI に独立パッケージとして出す以上、ビルド対象ディレクトリが自己完結している方が sdist・editable・CI すべてで素直。workspace を解体しても crate は 1 つなので失うものがない。
- **要人間確認:** ディレクトリ構成（永続フォーマット）は確定前に人間承認が必要（規約1）。

### Milestones / Steps
- [x] ディレクトリ構成（L1/L2）を人間が確定する → L1 採用（2026-05-31）
- [x] renderer crate を選定構成へ移動し、`cargo fmt/clippy/test` が通ることを確認
- [x] renderer パッケージの `pyproject.toml`（maturin bin。純バイナリのため python-source/module-name は不要）を作成
- [x] 本体 `pyproject.toml` に `[project.optional-dependencies] realtime = [...]` を追加（同バージョン pin）
- [x] `find_renderer_binary()` に sysconfig scripts ディレクトリ探索を追加（PoC 改善点）
- [x] fresh venv に本体 + renderer を install し、別ディレクトリから realtime が解決で動くことを実機確認（env var/PATH なしで sysconfig 経由 → 実フレーム投影まで完走）
- [x] 本体・renderer の検証スタックを通す（ruff/mypy/pytest, cargo fmt/clippy/test）
- [x] README / ARCHITECTURE / STATUS / MEMORY を更新
- [x] バージョン整合（2 パッケージの version を揃える運用）を決めて記録 → 当面は手動で同一 version を維持し、本体 `[realtime]` で `==` pin（Phase 2 で CI 同期を検討）

#### Outcomes & Retrospective
- 2026-05-31: Phase 1 完了。renderer を `packages/renderer/`（自己完結 maturin bin）に分離し workspace を解体。本体は pure-Python + console_script のまま維持。`pip install "projector-controller[realtime]"` 相当（本体 wheel + renderer wheel を install）で、env var なし・リポジトリ外から sysconfig 経由で renderer を解決し実フレーム投影まで完走を実機確認。残りは Phase 2（CI でクロスプラットフォーム wheel → PyPI 公開）。

#### Decision Log（追記）
- 2026-05-31: ディレクトリ構成は L1（`packages/renderer/` 自己完結）。cargo workspace は解体。renderer パッケージは純 Rust バイナリなので python-source/module-name を設定しない（PoC でこれらが mixed project 限定の設定だと判明）。
- 2026-05-31: 2 パッケージの version は当面手動で同一に保ち、本体 `[realtime]` で `==` pin する。CI による自動同期は Phase 2 で検討。

### Risks & Compatibility
- **破壊的変更の可能性:** workspace 解体・crate 移動・本体 pyproject 変更。いずれも公開前なので影響は限定的だが、ビルド/CLI 起動の回帰に注意。
- console_script は本体（hatchling）側に残すので `uv run projector-controller` は維持できる（PoC の同居不可問題を回避）。
- 2 パッケージのバージョン整合という新たな運用コストが発生する。
- editable install での realtime 利用は、renderer パッケージも editable で入れる手順を README に明記する。

### Living Sections

#### Progress
- 2026-05-31: PoC で maturin bin 同梱の可否と制約を確定。配布設計は案 A（2 パッケージ分割）に決定。Phase 1 を分割方針で再定義。

#### Decision Log
- 2026-05-31: 配布単位は 2 パッケージ（本体 pure-python + renderer maturin bin）。本体の `[realtime]` extras で renderer を引く（ユーザー承認）。
- 2026-05-31: console_script は本体側に残す。maturin bin と同居不可のため、renderer を分離することで CLI を維持する。

#### Surprises & Discoveries
- 2026-05-31: maturin bin は console_script と排他。これが 2 パッケージ分割を選ぶ決定的理由になった。

#### Decision Log
- 2026-05-31: 配布は PyPI、Rust バイナリは maturin で wheel 同梱とする（ユーザー判断）。実装は Phase 0（土台）→ 1（maturin）→ 2（CI/公開）に段階化。
- 2026-05-31: renderer バイナリ発見は env var `PROJECTOR_CONTROLLER_RENDERER` と PATH を追加。PATH は maturin の bin install 先を拾うため。

---

## Plan: CI 最小構成（検証スタックを push/PR で強制）

- **Status:** `Done`
- **Owner:** AI
- **Created / Updated:** 2026-05-31 / 2026-05-31
- **Related:** .github/workflows/ci.yml

### Goal & Non-Goals
- **Goal:** AGENTS.md §7 が必須化する検証スタックを、push（main）/ PR で自動実行して回帰を防ぐ。Python（ruff format --check / ruff check / mypy / pytest）と Rust renderer（cargo fmt --check / clippy -D warnings / test）を CI で強制する。
- **Non-Goals:** クロスプラットフォーム wheel のビルド、TestPyPI / PyPI への公開（いずれも配布 Phase 2）。Linux/macOS での実行（Phase 2 の wheel マトリクス導入時に追加）。ブランチ保護（マージ必須化）の設定（GitHub UI/API 側の操作）。

### Context & Constraints
レビューで「CI 不在で §7 が強制されていない」ことが最優先級の地盤課題として挙がった。最小構成として、配布（wheel/公開）と切り離し「検証の強制」だけを先に入れる。実行 OS は現在の唯一のサポート対象である Windows のみ（ユーザー承認 2026-05-31）。winit の Linux ビルド依存を避け、最速・最安定にするため。

### Approach（実行 OS の検討案）

| 案 | 概要 | 長所 | 短所 |
|----|------|------|------|
| A | Windows のみ | classifiers/STATUS の前提に一致。cargo が追加システム依存なしでビルド。最速・最安定 | クロスプラットフォーム回帰は見えない |
| B | Windows + Ubuntu | renderer の回帰検出が広がる | Linux で winit のビルド依存（libxkbcommon 等）を入れる必要 |
| C | Windows + Ubuntu + macOS | 将来の wheel 対象に最も近い | セットアップが重く CI 時間も長い。最小構成には過剰 |

- **採用案:** A（2026-05-31 ユーザー承認）
- **理由:** 最小構成で「§7 の強制」を確実に入れることを優先。Linux/macOS は Phase 2 で wheel マトリクスを組むときに同時導入する方が二重作業にならない。

### Milestones / Steps
- [x] 実行 OS を人間が確定する → Windows のみ採用（2026-05-31）
- [x] `.github/workflows/ci.yml` を作成（python / rust の 2 job、push(main)+PR トリガー）
- [x] 検証コマンドを手元（Windows）で実行して全緑を確認（ruff/mypy/pytest 26 passed、cargo fmt/clippy/test 2 passed）
- [x] STATUS / PLANS を更新
- [ ] （人間）GitHub のブランチ保護で本 CI を「マージ必須」に設定

### Risks & Compatibility
- 使用 Action（checkout / setup-uv / dtolnay/rust-toolchain / Swatinem/rust-cache）はいずれも標準的で、Python/Rust の依存（lockfile）は増えない。
- 実行 OS が Windows のみなので、Linux/macOS 固有の回帰は当面検出されない（Phase 2 で拡張）。

### Outcomes & Retrospective
- 2026-05-31: 最小 CI を追加し、push/PR で Python・Rust 双方の検証スタックを強制するようにした。両スタックは手元 Windows で全緑を確認済みなので初回 run も緑の見込み。残りは人間によるブランチ保護設定と、Phase 2（クロスプラットフォーム wheel→公開）。

---

## Plan: realtime frame IPC の性能（#1 copy-TCP → shm 判断）

- **Status:** `Done`（1080p60 を end-to-end 実測で達成。shm・受信バッファ再利用とも不要を確定。4K60 は将来課題）
- **Owner:** AI
- **Created / Updated:** 2026-06-01 / 2026-06-01
- **Related:** src/projector_controller/realtime.py, packages/renderer/src/{main,protocol,render}.rs

### Goal & Non-Goals
- **Goal:** realtime frame 投影を **1080p / 60fps**（人間確定の目標）で安定供給する。frame IPC のボトルネックを計測で特定し、安い改善から潰す。shm / ring buffer は「copy で足りない証拠が出たときだけ」導入する（既存ルール）。
- **Non-Goals:** 4K60 の最適化（将来。今回の目標外）。動画デコード / 音声（#2）。protocol の破壊的変更。

### Context & Constraints（計測で確定した事実）
- **2026-06-01 実機計測:** localhost TCP の copy 転送上限（Python `sendall` + 破棄 sink、TCP_NODELAY）は **~1615 MB/s（1080p で ~195 fps 相当）**。1080p60 必要帯域 ~498 MB/s に対し **約 3.2 倍の余裕**。→ **1080p60 では transport は壁ではなく、shm は現時点で不要。**
- 真の課題は transport ではなく:
  1. **フロー制御なし**: producer が renderer を追い越すと winit の user-event キューが無制限に伸び、遅延と**メモリが増大**（堅牢性バグ。レビューでも指摘済み）。
  2. Rust 受信側が frame ごとに `Vec<u8>` を確保（1080p で 8.3MB の alloc+zero / frame）。
  3. header と payload を別 `sendall`。NODELAY 未設定だと Nagle で小さな header が payload 待ちになり遅延し得る。

### Approach（次の一手の検討案）

| 案 | 概要 | 長所 | 短所 |
|----|------|------|------|
| A | 安い改善（latest-wins backpressure・受信バッファ再利用・NODELAY・header+payload 結合）→ 必要なら shm | 1080p60 を最小変更で確実に。backpressure は堅牢性修正でもある | shm は当面入れない（4K60 では将来再評価） |
| B | いきなり shm / ring buffer | 4K まで一気に伸びる | 計測上 1080p60 には過剰。cross-platform shm・同期・lifecycle で複雑。renderer は別パッケージで配布境界も跨ぐ |
| C | copy のまま何もしない | 楽 | backpressure 無しのメモリ増大バグが残る |

- **推奨案:** A。計測で transport は十分と判明したので、shm より先に backpressure（堅牢性）とアロケーション削減で 1080p60 を固める。
- **要人間確認:** latest-wins（renderer が遅れたら古いフレームを捨て最新を描く）は「全フレーム描画」を期待する用途とは非互換になり得る。realtime 投影では最新優先が自然だが、公開挙動に関わるので確定前に確認する（規約1）。

### Milestones / Steps
- [x] 目標確定（1080p60、人間） / transport 上限を実測（~1615 MB/s）
- [x] backpressure を **設定可能（既定 `latest` / `all`）** で実装。renderer に単一の frame inbox（`inbox.rs`）を置き、`latest`=1 スロット上書き（古いを破棄）/ `all`=小容量 FIFO＋満杯時 reader ブロックで、**無制限キュー増大を解消**（ユーザー確定: 設定可能・既定 latest）
- [x] TCP_NODELAY 設定（header の Nagle 遅延を解消。header+payload の concat は Windows で `sendmsg`/writev 不可・コピー増のため不採用、2 回 send のまま）
- [x] end-to-end 実測（手元実機・1080p, 300 frames）: `all`（全描画・cap3）= **113.9 fps / 945 MB/s**、`latest` = **130.9 fps / 1085 MB/s**。**1080p60 を約 1.9× の余裕で達成**。遅延は all=bounded（≤3 frame ≈26ms）/ latest=最新のみ。OOM・hang なし
- [x] shm 要否判断 → **不要を確定**（1080p60 達成・余裕あり）。4K60(~2GB/s) を本気で狙う段で再評価
- [x] Rust 受信 `Vec` 再利用 → **不要を確定**（per-frame alloc のままで 114fps 出る＝alloc は非支配）
- [x] 検証スタック（Python ruff/mypy/pytest 28 passed・Rust fmt/clippy/test 4 passed）+ latest/all 両モードの windowed smoke を通過

### Risks & Compatibility
- latest-wins の semantics 変更が公開挙動に影響し得る（用途により設定可能にするか要検討）。
- 受信バッファ再利用は「frame を event に move」する現設計と衝突しうる。ダブルバッファで対応。

### Living Sections

#### Progress
- 2026-06-01: ユーザーが目標を 1080p60 に確定。transport 上限を実機計測（~1615 MB/s, 1080p ~195fps 相当）。
- 2026-06-01: backpressure を設定可能（既定 latest）で実装。renderer に `inbox.rs`（単一 frame inbox）を追加し、`RendererEvent` を frame 同梱から `FrameReady` 通知に変更、frame 単位で inline present（all モードで取りこぼさない）。Python に `RealtimeProjection(backpressure=...)` と `TCP_NODELAY` を追加。検証スタック全緑＋ latest/all smoke 成功。

#### Decision Log
- 2026-06-01: 計測により 1080p60 では copy-TCP で十分（~3.2× 余裕）と判明。**shm は当面見送り**、案 A（backpressure + alloc 削減 + NODELAY）を優先する。
- 2026-06-01: backpressure は**設定可能・既定 `latest`**（ユーザー確定）。受信バッファ再利用は end-to-end 実測まで保留（1080p60 では alloc 非支配の見込み）。header+payload の単一送信は Windows の writev 不在のため不採用、NODELAY で代替。
- 2026-06-01: end-to-end 実測（1080p, 手元実機）で `all`=113.9 fps / `latest`=130.9 fps を確認。**1080p60 達成・余裕あり**のため shm も受信バッファ再利用も**不要を確定**。alloc は非支配（per-frame 確保のまま 114fps）。

#### Outcomes & Retrospective
- 2026-06-01: **#1 完了**。renderer に単一 frame inbox を導入して無制限キュー増大を解消し、backpressure を設定可能化（既定 latest）、TCP_NODELAY を追加。transport 上限 ~1615 MB/s、end-to-end は 1080p で all 113.9 fps / latest 130.9 fps と **1080p60 を ~1.9× 上回る**。shm・受信バッファ再利用とも不要を確定（4K60 を狙う段でのみ再評価）。次に性能で触るとすれば 4K60 で、その時に shm/ring buffer と present 方式（vsync 解除）を見直す。

---

## Plan: 動画デコード / 音声 — 専用 media プロセス（#2 案 C）

- **Status:** `Done`（映像 + 音声 + A/V 同期まで実装。renderer present 遅延の厳密計測のみ将来課題）
- **Owner:** AI
- **Created / Updated:** 2026-06-01 / 2026-06-01
- **Related:** 新規 media プロセス, packages/renderer（frame protocol 再利用）, src/projector_controller（orchestration）

### Goal & Non-Goals
- **Goal:** 動画ファイル（映像 + 音声）を投影できるようにする。**専用 media プロセス**がデコード・音声・A/V 同期を所有し、デコード結果フレームを**既存の frame protocol で Rust renderer に直接供給**する。Python は media プロセスと renderer を起動・統制する指揮者に徹する。
- **Non-Goals:** 台形 / 色補正、シーク UI、プレイリスト、編集。renderer 側 protocol の破壊的変更（できれば無改修で純 sink のまま）。

### Context & Constraints
- ユースケース「両方」確定 → renderer は live 生成フレーム（Python）と動画フレーム（media プロセス）を**同じ protocol**で受ける純 sink を維持できる（C を選ぶ最大の利点）。
- #1 の計測で 1080p60 の transport は十分と判明 → media プロセス→renderer も copy-TCP で 1080p60 を狙える。
- 配線: Python が renderer を起動（renderer が READY で bind アドレスを print）→ media プロセスにそのアドレスと動画ファイルを渡して起動 → media プロセスが renderer に直接接続して frame を push。renderer は無改修。
- **A/V 同期が最難関。** プロセスを跨ぐぶん、renderer の present 遅延を見込んだ音声オフセットが要る。

### Approach（要人間確認の sub-decisions）

**D1: media プロセスの実装言語 / デコーダ依存**

| 案 | 概要 | 長所 | 短所 |
|----|------|------|------|
| a | Python + PyAV（ffmpeg バインディング） | pip 配布が容易。PTS 取得で同期しやすい。Python-first と整合 | 音声出力は別ライブラリ。高 fps は実装次第 |
| b | Python + OpenCV | 導入容易 | PTS / 音声が弱く同期に不向き |
| c | Rust + ffmpeg / gstreamer | デコード・同期・音声を 1 プロセスで高性能に | renderer に続く 2 つ目の OS 別バイナリ。ビルド / 配布が重い |

- **採用案:** a（Python + PyAV）。**2026-06-01 ユーザー確定**。配布が pip で完結し、renderer の「別プロセスに feed」パターンを踏襲できる。性能不足が見えたら c に上げる。

**D2: 音声 + A/V 同期**
- media プロセスが音声を master clock とし、各フレームを音声 PTS に合わせて renderer に送る（動画プレイヤーの定石）。renderer の固定 present 遅延は一度実測してオフセット補正。
- 音声出力候補: PyAV でデコード→ `sounddevice` / `pyaudio` 等で再生（依存追加・要確認）、または当面は外部 player に委譲して映像のみ先行実装。

**D3: 制御チャネル（Python↔media）**
- MVP は起動引数のみ（ファイルを 1 回再生）。play / pause / seek は後追いで小さな line protocol を足す。

### MVP 実装設計（映像のみ）
- PyAV を**新規 optional extra `[video]`** として pyproject に追加（heavy・常用しないため `[realtime]` と別軸）。
- renderer 起動ロジック（process spawn + `READY` アドレス parse + stdout/stderr drain）を `realtime.py` から**再利用可能ヘルパに切り出し**、`RealtimeProjection` と新 facade で共有。
- frame protocol encode（`_encode_frame_header` 等）を media プロセスからも使えるよう共有。
- 新モジュール `projector_controller.media`（`python -m projector_controller.media --connect HOST:PORT --file PATH [--fit-mode]`）: PyAV でデコード→PTS でペース→既存 protocol で renderer に push（映像のみ）。
- `VideoPlayer` facade: renderer を `--backpressure all`（動画は落とさない）で起動し、media プロセスを起動・統制して終了まで待つ。Python は frame を触らない（案 C の肝）。

### Milestones / Steps
- [x] D1（デコーダ依存）= Python + PyAV 確定（2026-06-01）。D2（音声・同期）は MVP 後
- [x] PyAV を `[video]` optional extra として追加（pyproject / uv.lock。av 17.0.1）
- [x] renderer 起動ヘルパを切り出し（`RendererProcess` + `build_renderer_command`）、`RealtimeProjection` を非破壊で載せ替え
- [x] frame protocol encode を共有（media が `realtime._encode_frame_header` / `_encode_quit_header` を再利用）
- [x] `projector_controller.media` プロセス（PyAV デコード→stride 除去→PTS ペース→push、終了時 quit 送出）
- [x] `VideoPlayer` facade（renderer を `--backpressure all` で起動 + media プロセスを統制し終了待ち）
- [x] テスト: `_pack_rgba`（stride 除去）/ `_parse_address` / `stream_frames`（socketpair で protocol 検証）/ av デコード往復（合成クリップ、importorskip）。GUI 不要
- [x] 実機 smoke: 合成クリップを `VideoPlayer` で投影し returncode 0（renderer 起動→media デコード→push→quit→終了）
- [x] 音声再生 + A/V 同期（D2）: `AudioMaster` が別スレッドで音声を sounddevice 再生し `clock()` を提供、`stream_frames_synced` が映像を音声 master に同期。音声無し/デバイス無し/`--mute` は wall-clock 映像のみにフォールバック
- [~] renderer present 遅延の補正（D2）: 手動 `--av-offset-ms`（既定 0）で吸収。厳密計測（フレームが実際に表示される時刻の測定）は未実装＝将来課題
- [x] 検証スタック（Python ruff/mypy/pytest 41 passed）/ docs（README・ARCHITECTURE）/ STATUS / PLANS / MEMORY 更新
- [ ] （CI）av-gated デコードテストを CI で走らせるなら video job に `--extra video` を追加（現状は未導入だと importorskip でスキップ）

### Risks & Compatibility
- 新規依存（PyAV / 音声ライブラリ、または ffmpeg ビルド）。c を選ぶと 2 つ目の配布物が増える。
- cross-process A/V 同期の難しさ。present 遅延の実測値に依存。
- realtime の接続先が「Python 1 本」前提のコードに無い暗黙の仮定がないか確認（media プロセスも同じ renderer に接続するため）。

### Living Sections

#### Decision Log
- 2026-06-01: レイヤは案 C（専用 media プロセス）。renderer を純 frame sink に保ち、live 生成も動画も同一 protocol で供給する（ユーザー確定）。
- 2026-06-01: 実装順は #1（共有 IPC 基盤）を先に固めてから #2 へ。#2 は D1 / D2 確定後に MVP（映像のみ）→ 音声の順。
- 2026-06-01: D1 = **Python + PyAV**（ユーザー確定）。PyAV は heavy なので新規 optional extra `[video]` に置く。動画は backpressure=`all`（落とさない・PTS でペース配信）で投影する。

#### Outcomes & Retrospective
- 2026-06-01: **映像のみ MVP 完成**（`feature/realtime-video-mvp`）。renderer は無改修の純 sink。`RealtimeProjection` から renderer 起動を `RendererProcess` + `build_renderer_command` に切り出して共有し、`VideoPlayer` が renderer（`--backpressure all`）+ 別 media プロセスを統制。media（`python -m projector_controller.media`）が PyAV でデコード→stride 除去→PTS ペース→既存 protocol で renderer に直接 push、終了時に quit 送出。検証スタック全緑（Python 38 passed）＋合成クリップの投影 smoke 成功。
- 2026-06-01: **D2（音声 + A/V 同期）完成**。`AudioMaster` が別スレッドで音声を sounddevice 再生し `clock()`（書込済み秒 − 出力 latency）を提供、`stream_frames_synced` が映像を音声 master に同期（`--av-offset-ms` で renderer 遅延を手動補正、既定 0）。音声無し/デバイス無し/`--mute` は wall-clock 映像のみにフォールバック。PyAV 音声 plane も末尾パディングを持つため `samples*ch*2` に切る。`sounddevice` を `[video]` extra に追加。検証スタック全緑（Python 41 passed）＋**サイン波付き A/V クリップ**の同期再生 smoke 成功（returncode 0）。残るは present 遅延の厳密計測（将来）と CI の `--extra video`。
