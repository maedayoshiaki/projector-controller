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
| 2026-05-31 | ウィンドウ位置 `--x/--y` はデスクトップ絶対座標とし、省略時は `--display` 中央。ディスプレイ相対座標は将来課題 | pygame 2.6.1(classic/SDL2.28.4) の公開 API にディスプレイ原点取得が無く、相対座標は ctypes 直叩きが必要で「小さく始める」方針に反するため | config.py、window.py、cli.py、pygame_backend.py、docs/ARCHITECTURE.md |
| 2026-05-31 | Windows DPI 対応は `SDL_WINDOWS_DPI_AWARENESS=permonitorv2`（ヒント方式）で行う | 実機が DPI 200% で、非対応だと SDL が論理サイズ(半分)しか見えずウィンドウ/全画面が崩れる。ヒント方式は OS 分岐不要・上書き可・新規依存なし。実機で物理値取得を確認 | pygame_backend.py、docs/ARCHITECTURE.md |
| 2026-05-31 | fullscreen は `pygame.FULLSCREEN`（`set_mode((0,0))`）方式を維持する | 人間の指示。DPI 対応により (0,0) が物理解像度を選ぶため、解像度切替方式でも崩れない。一度 desktop-style borderless に変更したが指示に反したため戻した | pygame_backend.py、docs/ARCHITECTURE.md |
| 2026-05-31 | Windows DPI 対応後の実機検証は成功 | ユーザーが「実機検証は完了」「うまく行っています」と報告 | STATUS.md、docs/EXPERIMENTS.md |
| 2026-05-31 | 動画ファイル再生ではなく、Rust で GPU 性能を引き出すリアルタイムフレーム投影設計へ切り替える | ユーザーが OpenGL 等のレンダリング手段と GPU 活用を重視し、Rust 採用を選択 | PLANS.md、STATUS.md、今後の Rust renderer 実装 |
| 2026-05-31 | Rust renderer の初期接続方式は subprocess + localhost TCP + copy-based frame protocol | Rust が window / event loop / GPU device を所有し、Python/GIL から描画ループを分離するため。shared memory / ring buffer は性能不足が見えてから導入する | crates/projector-controller-renderer、src/projector_controller/realtime.py |
| 2026-05-31 | Rust renderer MVP の windowed smoke test は成功 | `RealtimeProjection` から Rust renderer を起動し、64x64 RGBA frame を 320x240 window に送信して終了できた | src/projector_controller/realtime.py、crates/projector-controller-renderer |
| 2026-05-31 | realtime 経路の display 番号は Rust renderer(winit) 列挙を権威にする | pygame と winit で列挙元が別系統で番号がずれ得る。realtime で使う番号を renderer 自身の列挙(`--list-monitors` / `list_renderer_monitors()`)で見せれば、`--display N` と原理的に一致し追加依存不要。pygame は原点取得 API が無くマッチング案は ctypes 依存になり「小さく始める」に反する | main.rs(`--list-monitors`)、realtime.py(`list_renderer_monitors`/`RendererMonitor`)、cli.py、docs/ARCHITECTURE.md |
| 2026-05-31 | renderer の stdout/stderr は daemon thread で drain する | READY 後に読み出さないと OS パイプバッファ満杯で renderer が write ブロックし描画が止まり得る。bounded deque に保持し異常終了診断に使う | src/projector_controller/realtime.py |
| 2026-05-31 | 配布は PyPI 公開 + Rust バイナリを maturin で wheel 同梱とする。実装は Phase 0(土台)→1(maturin)→2(CI/公開) に段階化 | 一気に進めると手戻りが大きく、Rust 入り wheel はプラットフォーム別 CI が前提。土台(renderer 発見の堅牢化等)は配布方法に依存せず先に固められる | pyproject.toml、realtime.py、PLANS.md、将来の CI |
| 2026-05-31 | renderer バイナリ発見順を `renderer_path` 引数 → env var `PROJECTOR_CONTROLLER_RENDERER` → PATH(`shutil.which`) → sysconfig scripts dir → `packages/renderer/target` に堅牢化 | repo の target/ 依存だと pip install 環境で FileNotFoundError になる。PATH は activate 時、sysconfig scripts dir は activate せず install した renderer を拾う。env var が set かつ不在なら黙ってフォールバックせず明示エラー(利用者の意図尊重) | src/projector_controller/realtime.py |
| 2026-05-31 | 配布は 2 パッケージ分割: 本体 `projector-controller`(pure-Python universal wheel, hatchling, console_script) + `projector-controller-renderer`(OS 別 wheel, maturin bin)。本体 `[realtime]` extras で renderer を同 version pin | maturin bin は console_script と同居不可("Defining scripts and working with a binary doesn't mix well")。maturin wheel は OS 別なので本体を maturin 化すると pygame だけの利用者にも OS 別 wheel を強いる。分割で各々が自然なビルドバックエンドを使え CLI も維持できる | pyproject.toml、packages/renderer/、docs/ARCHITECTURE.md |
| 2026-05-31 | renderer crate は `packages/renderer/`(自己完結 maturin bin)に置き cargo workspace を解体 | PyPI 独立パッケージとして sdist/editable/CI が素直になる。crate は 1 つなので workspace を失う不利益なし | packages/renderer/、Cargo.toml(削除) |
| 2026-05-31 | Phase 1 受け入れ確認成功 | 本体 wheel + renderer wheel を fresh venv に install し、env var/PATH なし・リポジトリ外から sysconfig 経由で renderer 解決 → 実フレーム投影まで完走 | packages/renderer/、src/projector_controller/realtime.py |
| 2026-05-31 | ローカル PyPI 配布リハーサル成功（実環境に最も近い検証） | 両パッケージの wheel/sdist を `pypiserver` で配信し、fresh venv で `pip install --index-url http://localhost:... "projector-controller[realtime]"` が解決成功(本体・renderer・pygame)、index install 後に sysconfig 経由で renderer 解決→実フレーム投影まで完走(E2E exit 0)。`pip install "projector-controller[realtime]"` 一発で realtime が動くことを実証 | 一時環境のみ(コミットなし)。Phase 2 の PyPI 公開手順の裏付け |
| 2026-06-01 | realtime frame IPC は copy-based TCP を維持し shared memory は当面見送る。renderer に単一 frame inbox を置き backpressure を設定可能化（既定 `latest`=最新優先で古いを破棄 / `all`=全描画・満杯時 reader ブロックで producer をペース）。Python 側は TCP_NODELAY | 手元実機で copy-TCP 転送上限 ~1615 MB/s（1080p60 必要 ~498 MB/s の ~3.2 倍）。1080p60 では shm 不要。無制限キュー増大（堅牢性バグ）は inbox で解消。4K60(~2GB/s) を本気で狙う段で shm 再評価 | packages/renderer/src/{inbox,main,render}.rs、realtime.py、docs/ARCHITECTURE.md |
| 2026-06-01 | 動画再生は案 C（専用 media プロセス）。renderer は無改修の純 frame sink のまま、`VideoPlayer` が renderer(`--backpressure all`) + 別 media プロセス(`python -m projector_controller.media`)を統制。media は PyAV でデコード→既存 protocol で push、音声は sounddevice で再生し**音声 master clock**で映像を同期 | renderer を sink に保てば live 生成も動画も同一 protocol。プロセス分離で decode が Python 本体の GIL/スケジューリングに影響しない。音声 master は動画プレイヤーの定石 | media.py、video.py、pyproject `[video]` extra(av/sounddevice)、docs/ARCHITECTURE.md |

## Conventions

- **文書:** 人間向け入口は `README.md`、AI 向け規約は `AGENTS.md`、現在地は `STATUS.md`、確定事項は `MEMORY.md` に分ける。
- **用語:** コード上は「モニター」より `display` を優先する。例外として、Rust renderer(winit) 由来の権威的なモニタ列挙は `RendererMonitor` / `--list-monitors` と呼び分ける。
- **投影表示:** 投影ウィンドウの既定背景は黒を基本候補にする。
- **設計:** GUI / メディア再生バックエンド固有処理は adapter に隔離する。

## Gotchas & Pitfalls

- Python 実装環境は `uv sync --dev` で作成する。
- フルスクリーン、ウィンドウ座標、ディスプレイ選択は OS と接続環境の影響を受けるため、実機テストログを残す必要がある。
- pygame 2.6.1 (classic) はディスプレイ原点取得 API（`get_desktop_rects` / `_sdl2.video.get_displays`）を持たない。原点が必要になったら pygame-ce 移行か ctypes(SDL_GetDisplayBounds) を検討する。
- pygame 2.6.1 (classic) には `pygame.movie` が無い。mp4 などの一般的な動画ファイルを pygame の投影面へ出すには、別のデコーダでフレームを読み、pygame Surface に変換して描画する必要がある。
- windowed の絶対位置指定は `SDL_VIDEO_WINDOW_POS` 環境変数で行う。位置未指定時は設定せず `set_mode(display=N)` に中央配置を任せる（旧実装は常に (0,0) を渡して固定されるバグがあった）。
- Windows DPI スケーリング（実機は 200%）で SDL が論理サイズしか見えず、ウィンドウ/全画面サイズが崩れる。`SDL_WINDOWS_DPI_AWARENESS=permonitorv2` を pygame import 前に設定して物理ピクセルで扱う。診断は「`get_desktop_sizes()` の値 ×スケール = 物理解像度（`Get-CimInstance Win32_VideoController`）」で判別できる。
- Rust renderer は pygame backend と fullscreen 実装が異なる（winit borderless fullscreen）。display 番号 / DPI / 座標挙動は **2026-06-01 に外部モニタで実機検証し全 PASS**（projtest-002）: 中央配置・絶対座標（負 Y 含む）・borderless fullscreen のクリーン被覆（枠/カーソル/タスクバー出ず）・混在 DPI（内蔵 scale2.0 / 外部 scale1.5）でのサイズ崩れなし。外部でも 1080p60 達成（all 112.9 / latest 117.1 fps）。
- display 番号は backend で 2 系統（pygame=`--list-displays`、Rust renderer=`--list-monitors`）。realtime の `--display` は必ず `--list-monitors` の番号を使う。番号一致は **2026-06-01 に 2 モニタ（内蔵 2880x1800 / 外部 1920x1200）で完全一致を実機確認**（単一モニタも確認済み）。外部は index 1、原点 (511,-1200) の負 Y 配置でも正しく扱えた。
- renderer subprocess の stdout/stderr を PIPE にしたら必ず drain する。READY 行だけ読んで放置すると OS パイプバッファ満杯で renderer が write ブロックする。
- `import projector_controller` は軽量に保つ（pygame は `ProjectionWindow` 利用時に遅延ロード）。`tests/test_package.py` が「import で pygame を読まない」「公開 API が出ている」を保証する。壊したら配布物の使い勝手が落ちる。
- パッケージ検証は fresh venv に `uv build` の wheel を install し、リポジトリ外ディレクトリから import して行う（ソースツリーからの import と混同しない）。この環境のツール出力が破損しやすいので、判定は print ではなく exit code に載せる（[[tool-output-corruption]]）。
- maturin `bin` バインディングは `[project.scripts]`（console_script）と同居できない。Rust バイナリと CLI entry point を両方出したいなら別パッケージに分ける。
- PyPI 公開（Phase 2）の必須要件（ローカルリハーサルで確定）: (1) 本体と renderer の **2 パッケージ両方を公開しないと `[realtime]` extras が解決できず壊れる**、(2) 公開順は **renderer → 本体**（依存解決の順）、(3) maturin の出力先フラグは **`--out`**（`--out-dir` は不可）、(4) renderer wheel は **OS/アーキ別**なので CI でマルチプラットフォームビルドが必須。
- ローカル PyPI 配布リハーサルの手順: 両パッケージの wheel/sdist を 1 つの dist ディレクトリに集め、`uv run --no-project --with pypiserver pypi-server run -p <port> <dist>` で配信、fresh venv で `pip install --index-url http://localhost:<port>/simple/ --extra-index-url https://pypi.org/simple/ --trusted-host localhost "projector-controller[realtime]"`。`twine check <dist>/*` でメタデータも確認できる。
- workspace 解体後は `cargo ... -p <crate>` が使えない。`cargo <cmd> --manifest-path packages/renderer/Cargo.toml` を使う（README/EXPERIMENTS/ARCHITECTURE のコマンド例も更新済み）。
- maturin の純バイナリパッケージ（Python モジュールを含まない）は `python-source` / `module-name` を設定しない。設定すると「python module が存在しない」エラーになる（mixed project 限定の設定）。
- PyAV の plane はパディングを持つ。映像 `reformat("rgba")` は行ごとに `line_size > width*4`、音声 `resample("s16")` は plane が `buffer_size > samples*ch*2`。renderer protocol は tightly-packed なので必ず tight 長に切る（映像=`_pack_rgba` で行ごと、音声=`bytes(plane)[:samples*ch*2]`）。
- `av` / `sounddevice` は `[video]` extra（heavy）。`media.py` で遅延 import し、`import projector_controller` には影響させない。音声ストリーム無し / 出力デバイス無し / `--mute` 時は wall-clock の映像のみにフォールバック（`AudioMaster.start()` が False を返す）。
- realtime の copy-TCP 転送上限は手元実機で ~1615 MB/s（1080p ~195fps 相当）。end-to-end でも 1080p で `all`=113.9fps / `latest`=130.9fps を確認し、**1080p60 を ~1.9× 達成**（shm も受信バッファ再利用も不要、per-frame alloc のまま）。4K60(~2GB/s) を狙うなら shm/ring buffer と present 方式(vsync 解除)を再評価する。
- A/V 同期は音声 master。`AudioMaster` が別スレッドで音声を再生し、`clock()` ＝**音声開始からの wall-time**を返す（音声は実時間で鳴るので滑らか）。`stream_frames_synced` が映像を `clock()+offset` で出し、`play()` は映像ループ前に `started()` を待って起動カクつきを防ぐ。**注意:** 当初は clock を「書込済み秒 − 出力 latency」にしていたが、sounddevice の blocking write が**チャンク状・バースト**で進むため映像がカクついた（実測 interval max 503ms・>50ms が 22/120 フレーム）。wall-time 基準に変えて interval 33.3ms 固定・stutter 0 に改善。renderer present 遅延は手動 `--av-offset-ms`（既定 0）で吸収、厳密計測は未実装。
- 動画のテストクリップを自前生成するときは**符号化品質に注意**。低ビットレート mpeg4 ＋ 動くグラデ（圧縮に不利）＋ 低解像度をフルスクリーン拡大すると、renderer は無実でもブロックノイズが目立つ。品質確認は高ビットレート/高解像度クリップか実動画で行う（直接フレーム経路 R1〜R4 はコーデック非経由で綺麗）。スマホ動画は **Dolby Vision HEVC（DOVI side data 有り）** のこともある。
- **動画の回転メタ（display matrix）を必ず適用する**。スマホ縦撮りは landscape 保存＋回転フラグなので、無視すると横倒しに出る（実写 .MOV で露見した実バグ）。PyAV 17 は `stream.metadata['rotate']` も `stream.side_data` も出さず、`SideData.rotation` も None。**frame.side_data[Type.DISPLAYMATRIX] の 36byte（9×int32, 16.16 固定小数）を自前で解く**。時計回り角 = `atan2(m[1], m[0])`（ffmpeg の av_display_rotation_get が atan2 を負にし get_rotation が再度負にするので二重否定で相殺）。`media._rotation_from_matrix` で 0/90/180/270 に丸め、av の `transpose`（clock/cclock）フィルタで適用。`decode_video_frames(rotate=)` / `VideoPlayer.play(rotate=)` で手動上書き可。実写 iPhone 縦動画（90°）で自動回転＝正しい向き・画質・音 OK を実機確認。
- realtime media プロセスの実機検証は**ファイル先頭を時間 cap**（`itertools.takewhile(lambda f: f.pts < CAP, decode_video_frames(...))`）して行うと、長尺動画でも短時間で確認できる。HEVC 1080p のソフトデコードは手元実機で ~84fps（30fps 再生に十分）。

## Domain Facts

- 投影対象は静止画と映像を想定する。
- 投影時にウィンドウ位置指定とフルスクリーン表示へ対応したい。
- 現時点ではプロジェクションマッピング、台形補正、色補正などの数式は未定義。

## Glossary Pointer

用語の定義・和英対応は `docs/GLOSSARY.md` に集約する。
