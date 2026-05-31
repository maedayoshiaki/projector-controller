# STATUS.md — 今の状態

**現在**を扱うファイル。「今この瞬間、何がどうなっているか」のスナップショット。
各セッションの最初に読み、最後に更新する。確定した事項は `MEMORY.md` へ昇格する。

- **Last updated:** 2026-05-31
- **Current focus:** 配布準備 Phase 1（2 パッケージ分割）を実装。外部 display / fullscreen 実機検証待ち
- **Working branch:** feature/packaging-phase1-split

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
- 必要なら frame IPC を copy-based TCP から shared memory / ring buffer に移す。
- 設定ファイル形式を導入するか判断する。

## Blocked

- Rust renderer の外部 display / fullscreen 実機確認 — **理由:** local windowed smoke test は成功。winit borderless fullscreen は pygame fullscreen と方式が異なるため、プロジェクタまたは外部モニタで再検証が必要。

## Recently Done

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

- [ ] 目標解像度 / FPS / 許容遅延をどこに置くか。
- [ ] copy-based TCP で足りない場合、shared memory / ring buffer をどのタイミングで導入するか。
- [ ] 設定ファイル形式を導入するか。導入する場合は TOML / YAML / JSON のどれにするか。

## Environment Notes

- `uv sync --dev` で `.venv` を作成済み。
- `.python-version` は `3.12`。
- CLI は `uv run projector-controller ...` で実行する。
