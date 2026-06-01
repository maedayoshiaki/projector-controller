# STATUS.md — 今の状態

**現在**を扱うファイル。「今この瞬間、何がどうなっているか」のスナップショット。
各セッションの最初に読み、最後に更新する。確定した事項は `MEMORY.md` へ昇格する。

- **Last updated:** 2026-06-01
- **Current focus:** realtime #2（動画, 案 C）は**映像 + 音声 + A/V 同期まで完成**（VideoPlayer + media プロセス + PyAV + sounddevice 音声 master）。次は #1 の end-to-end 実測（1080p60 達成・遅延累積の確認）
- **Working branch:** feature/realtime-video-mvp（#2 映像 MVP。#1 は feature/realtime-frame-ipc にコミット済み）

---

## Now

- pygame backend の MVP 実装は完了。
- ウィンドウ位置仕様を確定し実装: `--x/--y` はデスクトップ絶対座標、省略時は `--display` の中央。
  これに伴い、windowed 時に常に (0,0) へ固定されていた既存バグを修正。
- 実機検証は完了し、Windows DPI 対応後の display / fullscreen / windowed 表示は期待通り動作した。
- 関連プラン: `PLANS.md` の "Plan: pygame MVP 実装" は `Done`、"Plan: ウィンドウ位置(x,y)" も `Done`。
- 動画ファイル再生ではなく、Rust renderer によるリアルタイムフレーム投影へ方針転換する。
- Rust `projector-controller-renderer`（`winit` + `wgpu`）と Python `RealtimeProjection` を追加済み。
- Python から Rust renderer を起動し、RGBA frame を 1 枚送る windowed smoke test は成功。
- これまで未コミットだった Rust renderer + `RealtimeProjection` 一式を `feature/rust-realtime-renderer` にコミット済み（`b5f252d`）。
- renderer の stdout/stderr をバックグラウンド drain する修正を追加（パイプバッファ満杯による write ブロック対策）。
- display 番号の backend 間不一致に対応: realtime 経路は Rust renderer(winit) 列挙を権威とし、`--list-monitors` / `list_renderer_monitors()` を追加。単一モニタでは pygame 列挙と番号・物理解像度が一致することを実機確認。
- モジュール化 / 配布準備の Phase 0（土台固め）を実装: `find_renderer_binary()` を env var `PROJECTOR_CONTROLLER_RENDERER` → PATH → repo target の順で探索するよう堅牢化、pyproject に classifiers/keywords/urls を追加、import 健全性と renderer 発見のテストを追加。fresh venv に wheel を install し別ディレクトリから import・公開 API 利用・RealtimeProjection 構築を実機確認。`uv build` で wheel/sdist 生成も確認。
- 配布準備 Phase 1（2 パッケージ分割）を実装: renderer crate を `packages/renderer/`（自己完結 maturin bin パッケージ）へ移動し cargo workspace を解体。本体 pyproject に `[realtime]` extras を追加。`find_renderer_binary()` に sysconfig scripts ディレクトリ探索を追加（PoC 改善点）。本体 wheel + renderer wheel を fresh venv に install し、env var なし・リポジトリ外から sysconfig 経由で renderer 解決 → 実フレーム投影まで完走を実機確認。CLI（console_script）は本体に残し維持。
- 事前に PoC（`poc/maturin-bundle`, abandon 済み）で maturin bin 同梱の可否と「console_script と同居不可」の制約を確定し、2 パッケージ分割を採用。
- ローカル PyPI 配布リハーサルを実施（一時環境のみ・コミットなし）。両パッケージの wheel/sdist をビルド → `twine check` PASSED → ローカル `pypiserver` の simple index に両パッケージ列挙 → fresh venv で `pip install --index-url http://localhost:... "projector-controller[realtime]"` が解決成功（本体・renderer・pygame を取得、INSTALL exit 0）→ index install 後に env var/PATH なし・リポジトリ外から sysconfig 経由で renderer 解決 → 実フレーム投影まで完走（E2E exit 0）。`pip install "projector-controller[realtime]"` 一発で realtime が動くことを手元で実証。

## Next

- `docs/EXPERIMENTS.md` の `projtest-002` として Rust renderer の外部 display / fullscreen / DPI / 座標挙動を実機確認する。あわせて `M0`（pygame と winit の display 番号一致）を複数モニタで確認する。
- 配布準備 Phase 2: GitHub Actions でクロスプラットフォーム wheel をビルドし PyPI 公開（CI シークレット必要）。ローカルリハーサルの申し送りを反映する: (1) 2 パッケージ両方を公開しないと `[realtime]` が壊れる、(2) 公開順は renderer → 本体、(3) maturin の出力先フラグは `--out`（`--out-dir` 不可）、(4) renderer wheel は OS/アーキ別なので CI でマルチプラットフォームビルドが必須。
- realtime #1（性能, 1080p60）: backpressure（**設定可能・既定 latest**。renderer に単一 frame inbox を追加し無制限キュー増大を解消）と TCP_NODELAY を実装済み（検証スタック全緑＋latest/all smoke OK）。残: paced producer での **end-to-end 実測**（1080p60 達成・遅延累積の確認）、必要なら受信バッファ再利用。shm は当面見送り。
- realtime #2（動画/音声, 案 C）: **映像 + 音声 + A/V 同期まで完成**（`VideoPlayer` + media プロセス + PyAV + sounddevice 音声 master。検証全緑＋A/V クリップ同期再生 smoke OK）。残: renderer present 遅延の厳密計測（将来。今は `--av-offset-ms` 手動）、CI で av-gated テストを走らせるなら video job に `--extra video`。
- 設定ファイル形式を導入するか判断する（#3、トリガ待ちで据え置き）。

## Blocked

- Rust renderer の外部 display / fullscreen 実機確認 — **理由:** local windowed smoke test は成功。winit borderless fullscreen は pygame fullscreen と方式が異なるため、プロジェクタまたは外部モニタで再検証が必要。

## Recently Done

- 2026-06-01 realtime #2 の **D2（音声 + A/V 同期）完成**（`feature/realtime-video-mvp`）。`sounddevice` を `[video]` extra に追加。`AudioMaster` が別スレッドで音声を再生し `clock()`（書込済み秒 − 出力 latency）を提供、`stream_frames_synced` が映像を**音声 master clock** に同期。`--av-offset-ms`（既定 0）で renderer 遅延を手動補正。音声無し/出力デバイス無し/`--mute` は wall-clock 映像のみにフォールバック。PyAV の音声 plane も末尾パディングを持つため `samples*ch*2` に切る。検証スタック全緑（Python 41 passed）＋**サイン波付き A/V クリップ**の同期再生 smoke 成功（returncode 0）。MEMORY に realtime の確定事項を昇格。
- 2026-06-01 realtime #2（動画, 案 C）の**映像のみ MVP** を実装（`feature/realtime-video-mvp`）。PyAV を `[video]` extra で追加（av 17.0.1）。renderer 起動を `RendererProcess` + `build_renderer_command` に切り出して `RealtimeProjection` と共有（非破壊）。新規 `projector_controller.media`（PyAV デコード→stride 除去→PTS ペース→既存 protocol で renderer に push、終了時 quit）と `VideoPlayer` facade（renderer を `--backpressure all` で起動し media プロセスを統制）を追加・公開 API に。renderer は無改修の純 sink のまま。検証スタック全緑（Python ruff/mypy/pytest 38 passed）、合成クリップの投影 smoke 成功（returncode 0）。残りは D2（音声 + A/V 同期）。
- 2026-06-01 realtime #1（性能）の中核を実装。renderer に単一 frame inbox（`packages/renderer/src/inbox.rs`）を追加し、`RendererEvent` を frame 同梱から `FrameReady` 通知へ変更、frame 単位で inline present。backpressure を **設定可能（既定 `latest`＝最新優先で破棄 / `all`＝全描画・満杯時ブロックで producer をペース）** にし、**無制限キュー増大を解消**。Python に `RealtimeProjection(backpressure=...)` と `TCP_NODELAY` を追加。README/ARCHITECTURE を更新。検証スタック全緑（Python 28 passed・Rust 4 passed）、latest/all 両モードの windowed smoke 成功。`feature/realtime-frame-ipc` で作業（未コミット）。
- 2026-06-01 realtime #1 / #2 の方向をユーザーが確定（ユースケース=両方 / 目標=1080p60 / #2 レイヤ=案 C 専用 media プロセス）。#1 は実機で copy-TCP の転送上限 ~1615 MB/s（1080p ~195fps 相当、1080p60 の ~3.2 倍）を計測し、**shm は当面見送り**と判断。`PLANS.md` に「realtime frame IPC の性能（#1）」と「動画デコード/音声 — 専用 media プロセス（#2）」を追加。#1 は backpressure / alloc 削減 / NODELAY、#2 は D1（デコーダ依存）/D2（音声・同期）確定後に MVP（映像のみ）の順。
- 2026-06-01 `projtest-002`（Rust renderer 実機確認）の手順を `docs/EXPERIMENTS.md` に具体化。ハードウェア接続時に上から実行すれば終わる形にした: M0（pygame vs winit の番号一致・複数モニタ）+ R1〜R4（windowed 中央 / 絶対座標 / fullscreen / fit mode）を、`RealtimeProjection` を駆動するパラメータ可変フィーダ（here-string → `uv run python -`）と「確認の着眼点（DPI/物理座標・borderless fullscreen・番号一致・vsync）」付きで記述。CLI は pygame 専用で realtime は `--list-monitors` のみ、という構造も明記。既存の smoke / M0 単一モニタ結果は保持。ドキュメントのみ・非破壊。
- 2026-05-31 CI 最小構成を追加（`.github/workflows/ci.yml`）。push(main)/PR で検証スタックを強制: Python job（ruff format --check / ruff check / mypy / pytest）と Rust renderer job（cargo fmt --check / clippy -D warnings / test）。実行 OS は Windows のみ（ユーザー承認）。手元 Windows で両スタック全緑を確認（ruff/mypy/pytest 26 passed、cargo 2 passed）。残りは人間によるブランチ保護（マージ必須化）と Phase 2（クロスプラットフォーム wheel→公開）。
- 2026-05-31 リポジトリ全体レビュー（多観点＋反証検証）を実施。確定した doc-mismatch のうち人間判断不要なものを修正: PLANS Phase-1 を `Done` 化、Related の旧 `crates/` パスを `packages/renderer/` に、初期スケッチの未実装 stride / 「shader uniform」記述を実装（tightly-packed / quad 頂点更新）に整合、AGENTS のツリーに `packages/renderer/` 追加・`media/` を未作成扱いに、ARCHITECTURE の `DisplaySpec` 記述を実装（index/name/size）に整合。レビューで挙がった大物（CI 不在、realtime のフロー制御＆生存通知、テスト空白）は人間判断待ち。
- 2026-05-31 配布準備 Phase 1（2 パッケージ分割）を実装・main にマージ（`f579a16`）。続けてローカル PyPI 配布リハーサルを実施し、`pip install "projector-controller[realtime]"` が index 経由で解決〜実フレーム投影まで完走することを実証（一時環境のみ・コミットなし）。
- 2026-05-31 配布準備 Phase 0（土台固め）を実装・main にマージ（`3c2b90b`）。
- 2026-05-31 未コミットだった Rust/wgpu realtime 投影一式を `feature/rust-realtime-renderer` にコミット（`main` 上に放置されていたのを解消）。検証スタック（ruff/mypy/pytest, cargo fmt/clippy/test）を全通過。
- 2026-05-31 renderer の stdout/stderr drain 修正、および display 番号の権威化（`--list-monitors` 追加）を実装・コミット。pytest 19 passed。
- 2026-05-31 実機テストで Windows DPI 200% による表示サイズ崩れを発見・修正。`SDL_WINDOWS_DPI_AWARENESS=permonitorv2` で物理ピクセル化（fullscreen は `pygame.FULLSCREEN` 方式のまま）。一度 desktop-style borderless に変えたが指示に反したため revert した。
- 2026-05-31 ユーザー報告により、Windows DPI 対応後の実機検証が成功したことを確認。
- 2026-05-31 動画ファイル再生案を見直し、Rust で GPU 性能を引き出すリアルタイムフレーム投影設計へ切り替える方針を確認。
- 2026-05-31 Rust renderer crate、TCP frame protocol、Python `RealtimeProjection`、`examples/realtime_frames.py` を追加。windowed smoke test 成功。
- 2026-05-31 ウィンドウ位置(x,y)を「絶対座標＋display中央デフォルト」で確定・実装。`ProjectionConfig` を `geometry` から `position`/`size` へ変更し、windowed の (0,0) 固定バグを修正。テスト・README・ARCHITECTURE を更新。
- 2026-05-30 テンプレート文書を整理し、README、AGENTS、設計、用語、表示設計、投影テストログを projector-controller 向けに更新。
- 2026-05-30 テンプレート専用の `TEMPLATE_GUIDE.md` を削除し、ADR テンプレートをプロジェクト用に調整。
- 2026-05-30 Python 3.12 + uv 環境、`ProjectionWindow` API、pygame backend、CLI、examples、tests を追加。
- 2026-05-30 `uv run ruff format .`、`uv run ruff check .`、`uv run mypy src tests`、`uv run pytest` を通過。
- 2026-05-30 `uv run projector-controller --list-displays` で display 0 `1440x900`、display 1 `1280x800` を確認。

## Open Questions for the Human

- [x] 目標解像度 / FPS = **1080p / 60fps**（2026-06-01 確定）。許容遅延は未定（end-to-end 実測時に詰める）。
- [x] shm / ring buffer の導入時期 → **当面見送り**。2026-06-01 実機計測で copy-TCP は ~1615 MB/s（1080p60 必要帯域の ~3.2 倍）。1080p60 では shm 不要。4K60 を本気で狙う段で再評価。
- [x] #2 media プロセス（案 C）のデコーダ依存 = **Python + PyAV**（2026-06-01 確定）。PyAV は新規 optional extra `[video]` に置く。
- [ ] #2 の音声出力と A/V 同期方式（media プロセスが音声 master / 外部 player 委譲 など）。
- [ ] 設定ファイル形式を導入するか。導入する場合は TOML / YAML / JSON のどれにするか（#3、トリガ待ち）。

## Environment Notes

- `uv sync --dev` で `.venv` を作成済み。
- `.python-version` は `3.12`。
- CLI は `uv run projector-controller ...` で実行する。
