# EXPERIMENTS.md — 投影テストログ

実機プロジェクタ、外部ディスプレイ、ウィンドウ位置、フルスクリーン表示などの検証結果を記録する。コードだけでは再現しにくい環境差を残すためのファイル。

## How To Log

- テストごとに ID（`projtest-NNN`）を振る。
- 再現に必要な情報を書く: 日付、OS、Python / ライブラリ版、プロジェクタやディスプレイ、解像度、スケーリング、接続方式。
- コマンドやスクリプト名、設定値、素材名を残す。
- 成功 / 失敗だけでなく、画面位置、ちらつき、フルスクリーン挙動、色や明るさの気づきを書く。
- 現場固有の秘密情報や個人情報は書かない。

---

## Template

````markdown
## projtest-001: テストタイトル

- **Date:** 2026-05-30
- **Commit:** `git hash`
- **Machine / OS:** Windows など
- **Projector / Display:** 機種名、接続方式、OS 上の display 番号
- **Resolution / Scaling:** 1920x1080, 100% など
- **Backend:** 使用ライブラリ。未確定なら手動表示など
- **Media:** 使用した画像・動画・テストパターン
- **Window Settings:** display, x, y, width, height, fullscreen
- **Command:**
  ```powershell
  実行コマンド
  ```
- **Expected:** 期待する表示
- **Result:** 実際の表示
- **Issues:** 位置ずれ、ちらつき、色、操作性など
- **Conclusion:** 次に活かす判断
````

---

## Logs

## projtest-001: ウィンドウ位置・fullscreen・fit mode の実機確認

- **Date:** 2026-05-31
- **Commit:** `ab3ae58`
- **Machine / OS:** Windows 11 Home (10.0.26200)
- **Projector / Display:** プロジェクタ未接続。外部モニタを使用（OS 上の display 番号: 0 と 1 のどちらが外部かは下の T0 で確認）
- **Resolution / Scaling:** DPI **200%** 環境。物理解像度 = display 0: 2880x1800 / display 1: 1920x1200。DPI 対応化（`SDL_WINDOWS_DPI_AWARENESS=permonitorv2`）により `--list-displays` もこの物理値を報告する（対応前は半分の 1440x900 / 1280x800 を返していた）。
- **Backend:** pygame 2.6.1 (SDL 2.28.4), Python 3.12.12
- **Media:** 生成テストパターン（`show_test_pattern`）。画像は任意で各自用意。
- **共通操作:** Esc またはウィンドウの閉じる操作で終了。`--duration N` で N 秒後に自動終了。

### 手順（上から順に実行。各 Result / Issues を埋める）

各テストパターンには `display=N WxH windowed/fullscreen` のラベルが左上に出る。
これと実際に出た画面・位置・解像度が一致するかを見る。

#### T0: ディスプレイ列挙

```powershell
uv run projector-controller --list-displays
```

- **Expected:** 接続中のディスプレイが番号付きで一覧表示される。どの番号が外部モニタか確認する。
- **Result:** ユーザー報告により、実機検証は完了し期待通り動作したことを確認。
- **どちらが外部モニタ:** 詳細未記録

#### T1: 指定ディスプレイ中央に windowed 表示（位置省略 → 中央）

```powershell
# 下の N は T0 で確認した外部モニタの番号に置き換える
uv run projector-controller --display N --width 1280 --height 720 --duration 8
```

- **Expected:** 外部モニタの中央付近に 1280x720 のウィンドウが開き、テストパターンが出る。ラベルが `display=N 1280x720 windowed`。
- **Result:** ユーザー報告により成功。
- **Issues:** 詳細未記録。

#### T2: デスクトップ絶対座標に windowed 表示

```powershell
# 外部モニタの左上付近の絶対座標を指定。値は環境に合わせて調整。
uv run projector-controller --x 1500 --y 100 --width 800 --height 600 --duration 8
```

- **Expected:** デスクトップ絶対座標 (1500, 100) にウィンドウ左上が来る。外部モニタが主モニタの右側にある等、配置によって出る画面が変わる。
- **Result:** ユーザー報告により成功。
- **Issues:** 詳細未記録。

#### T3: fullscreen 表示

```powershell
uv run projector-controller --display N --fullscreen --duration 8
```

- **Expected:** 外部モニタ全体を覆う。枠・タイトルバー・OS カーソルが投影面に出ない。ラベルは `display=N <実解像度> fullscreen`。
- **Result:** ユーザー報告により成功。
- **Issues:** 詳細未記録。

#### T4: fit mode（任意・画像を用意できる場合）

```powershell
# 縦横比の異なる画像で contain / cover / stretch / native を比較
uv run projector-controller --image path\to\image.png --display N --fit-mode contain --duration 6
uv run projector-controller --image path\to\image.png --display N --fit-mode cover   --duration 6
uv run projector-controller --image path\to\image.png --display N --fit-mode stretch --duration 6
uv run projector-controller --image path\to\image.png --display N --fit-mode native  --duration 6
```

- **Expected:** contain=全体が収まる（余白可）, cover=画面を覆う（はみ出し可）, stretch=縦横比無視で全面, native=原寸中央。
- **Result:** 詳細未記録。
- **Issues:** 詳細未記録。

### Conclusion

- 2026-05-31 ユーザー報告により、Windows DPI 対応後の実機検証は完了し、期待通り動作したことを確認した。
- 詳細な display 番号、座標、機材情報は未記録。必要になったら次回の投影テストで追記する。

## projtest-002: Rust GPU renderer の実機確認

realtime 経路（`RealtimeProjection` → Rust `winit` + `wgpu` renderer）の display 番号 / fullscreen /
座標 / DPI / fit mode を外部モニタ・プロジェクタで確認する。**pygame backend とは window/fullscreen の
実装方式が異なる**（winit の borderless fullscreen vs pygame `FULLSCREEN`）ため、projtest-001 とは別に取り直す。

- **Date:** 2026-06-01（外部モニタで M0 複数モニタ + R1〜R4 + 1080p スループットを実施。local smoke と M0 単一モニタは 2026-05-31）
- **Commit:** `005185a`（`feature/realtime-video-mvp`。renderer は #1 backpressure 版）
- **Machine / OS:** Windows 11 Home (10.0.26200), Intel Arc 130V GPU
- **Projector / Display:** 外部モニタ接続。内蔵 = display 0、**外部 = display 1**（winit `\\.\DISPLAY2`、原点 (511,-1200) ＝内蔵の上に配置）
- **Resolution / Scaling:** 内蔵 2880x1800 @scale 2.0 / 外部 1920x1200 @scale 1.5（**混在 DPI**）
- **Backend:** Rust renderer (`winit` + `wgpu`), Python `RealtimeProjection`
- **Media:** 下のフィーダが生成する RGBA グラデーション frame（R=左→右, G=上→下 で向きが分かる）

> **注意:** CLI `projector-controller` は **pygame 経路専用**で、realtime は `--list-monitors` の列挙表示のみ。
> renderer の投影検証は下の Python フィーダ（`RealtimeProjection`）で行う。

### 既に取れている結果（2026-05-31）

- **local windowed smoke:** `RealtimeProjection` から renderer を起動し、64x64 RGBA frame を
  320x240 window に送って終了できた。frame IPC と最小起動は動作。
- **M0 単一モニタ:** `--list-displays` → `0: 2880x1800`、`--list-monitors` →
  `0: 2880x1800 @(0,0) scale=2.0 \\.\DISPLAY1`。番号・物理解像度・DPI(scale=2.0) が一致。

### 実機が来たら上から順に実行（各 Result / Issues を埋める）

#### M0: display / monitor 番号の一致（複数モニタで要確認）

```powershell
uv run projector-controller --list-displays    # pygame 列挙
uv run projector-controller --list-monitors    # Rust renderer (winit) 列挙＝realtime の権威
```

- **Expected:** 同じ物理モニタが両列挙で同じ番号・同じ物理解像度で並ぶ。外部モニタ接続時に番号順が一致するか。
- **以降の N:** `--list-monitors` で確認した**外部モニタの番号**を、下のフィーダの `DISPLAY` に使う。
- **Result（複数モニタ・2026-06-01）:** **PASS（完全一致）**。`--list-displays` → `0: 2880x1800` / `1: 1920x1200`、`--list-monitors` → `0: 2880x1800 @(0,0) scale=2.0 \\.\DISPLAY1` / `1: 1920x1200 @(511,-1200) scale=1.5 \\.\DISPLAY2`。番号・物理解像度ともに 2 モニタで一致。外部 = **index 1**。winit は per-monitor スケール（2.0 / 1.5）を物理ピクセルで報告。
- **Issues:** なし。番号ずれは発生せず、`--list-monitors` の番号がそのまま使えた。

#### フィーダ（R1〜R4 共通。先頭のパラメータだけ各テストで変える）

```powershell
@'
import time
from projector_controller import RealtimeProjection

# === 各テストでここだけ変える ===
DISPLAY      = 1           # 外部モニタの番号（--list-monitors の値）
FULLSCREEN   = False
X, Y         = None, None  # 絶対座標。None,None で DISPLAY 中央
W, H         = 1280, 720   # ウィンドウ物理サイズ（FULLSCREEN 時は無視）
FIT          = "contain"   # contain / cover / stretch / native
SRC_W, SRC_H = 480, 480    # 送るフレーム（正方形：どのアスペクト比のモニタでも fit の差が出る）
DURATION     = 8           # 秒
# ================================

def make_frame(w, h):
    buf = bytearray(w * h * 4)
    for y in range(h):
        gy = (y * 255) // max(1, h - 1)
        for x in range(w):
            o = (y * w + x) * 4
            buf[o]     = (x * 255) // max(1, w - 1)  # R: 左→右
            buf[o + 1] = gy                          # G: 上→下
            buf[o + 2] = 64
            buf[o + 3] = 255
    return buf

pos = None if (X is None and Y is None) else (X, Y)
frame = make_frame(SRC_W, SRC_H)
with RealtimeProjection(display=DISPLAY, fullscreen=FULLSCREEN, position=pos,
                        size=(W, H), fit_mode=FIT) as p:
    end = time.perf_counter() + DURATION
    while time.perf_counter() < end:
        p.submit_frame(frame, width=SRC_W, height=SRC_H, pixel_format="rgba8")
        time.sleep(0.1)
'@ | uv run python -
```

| Test | DISPLAY | FULLSCREEN | X,Y | W,H | FIT | Expected |
|------|---------|-----------|-----|-----|-----|----------|
| R1 windowed 中央 | N | False | None,None | 1280,720 | contain | 外部モニタ中央に 1280x720。R 左→右 / G 上→下のグラデが正しい向きで出る |
| R2 絶対座標 | 任意 | False | 1500,100 | 800,600 | contain | デスクトップ絶対 (1500,100) にウィンドウ左上（値は配置に合わせ調整） |
| R3 fullscreen | N | True | - | - | contain | 外部モニタ全体を覆う。枠/タイトルバー/OS カーソル/タスクバーが投影面に出ない |
| R4 fit modes | N | True | - | - | contain→cover→stretch→native | 正方形 SRC の収まり方を比較（16:9 モニタ例: contain=左右余白, cover=上下クロップ, stretch=横に歪み, native=原寸中央） |

各テストの Result / Issues（2026-06-01・外部 = display 1。実施値は DISPLAY=1, R2 は X,Y=700,-1100）:
- **R1:** **PASS**。外部ディスプレイの中央に 1280x720 のグラデが、正しい大きさ・向き（R 左→右 / G 上→下）で出た。scale 1.5 の混在 DPI でもサイズ崩れなし。
- **R2:** **PASS**。デスクトップ絶対座標 (700,-1100)（外部は原点が負 Y）で外部の左上付近に 800x600 が出た。負 Y 座標も正しく扱えた。
- **R3:** **PASS**。外部全体をクリーンに覆い、枠・タイトルバー・OS カーソル・タスクバーは投影面に出なかった（winit borderless fullscreen）。
- **R4:** **概ね PASS**（ユーザーは fit の差を判別しづらかったが「多分うまくいっている」）。fit mode の意味は README に追記した。
- **追加: 1080p スループット（外部 display 1）:** `all`=112.9 fps / 936 MB/s、`latest`=117.1 fps / 971 MB/s。外部（scale 1.5）でも **1080p60 を達成**（内蔵とほぼ同等）。
- **追加: 動画フルスクリーン（#2 VideoPlayer, display 1）:** A/V クリップを外部 fullscreen 再生して体感評価。
  - 初回: **カクつき + 同期ずれ**を確認。計測（push 間隔 / 音声 clock vs pts）で原因を特定 = 音声 master clock が「書込済み秒（チャンク状・バースト）」で進み映像が乱れていた（interval max 503ms・>50ms が 22/120）。→ **clock を「音声開始からの wall-time」に修正**（映像は `started()` まで待機）。再計測で interval 33.3ms 固定・stutter 0、ユーザーも「滑らかになった」と確認（commit `f015b4a`）。
  - 次に **ノイズ**を指摘。切り分けの結果、**テスト内容**（全チャンネル `%256` 剰余ラップ + 動き＝コーデック / YUV420 に最悪）が原因と判明。**素直な静止グラデ（R1〜R4 と同パターン）を高画質 libx264 で動画化すると「綺麗・ノイズなし」**＝ renderer / パイプラインは正常、実写動画は綺麗に出る見込み。
  - **実写動画で最終確認（iPhone 縦撮り HEVC/Dolby Vision .MOV, 1920x1080@30, 42.7s, AAC 48kHz）:** 当初 **横倒し**で再生 → 回転メタ（display matrix）未適用の実バグと判明。frame の `DISPLAYMATRIX` を自前で解いて自動回転を実装（clock/cclock）。再生し直して **向き・画質・音すべて OK＝完璧**（ユーザー確認）。HEVC 1080p ソフトデコードは ~84fps で 30fps 再生に十分。
  - 残: A/V リップシンクの厳密評価、起動時 ~0.8s の音声デバイス open 待ちの短縮（任意）。

### 確認の着眼点（コードから）

- **DPI / 座標:** winit は**物理座標**で配置する（`render.rs` の `--x/--y` と中央計算）。スケールの違う非主
  モニタで、`W,H` が指定どおりの物理ピクセルで出るか、中央 / 絶対座標がずれないか。
- **fullscreen 方式:** winit の **borderless** fullscreen（`Fullscreen::Borderless`）。pygame の
  `FULLSCREEN` とは別方式なので、排他モードのモード切替・点滅・解像度変更が起きないか、プロジェクタが
  ネイティブ解像度を受けるか。
- **番号一致 (M0):** pygame と winit の列挙番号が複数モニタで一致するか（realtime の唯一の未検証ポイント）。
- **描画:** present mode は Fifo(vsync) 既定。ティアリングなく滑らかか。renderer は frame 到着ごとに redraw する。

### Conclusion

- 2026-05-31: local windowed smoke と M0 単一モニタの一致を確認。
- **2026-06-01: 外部モニタで全項目 PASS。** M0（複数モニタで pygame/winit 番号一致）、R1（中央）、R2（絶対座標・負 Y 含む）、
  R3（borderless fullscreen クリーン被覆）、R4（fit 切替・概ね良好）。混在 DPI（内蔵 2.0 / 外部 1.5）でもサイズ・
  座標崩れなし。外部での 1080p スループットも all 112.9 / latest 117.1 fps で 1080p60 達成。#2 の動画フルスクリーン
  再生（映像 + 音声）も完走。→ **Rust renderer の外部 display / fullscreen / DPI / 座標は実機で確認済み**（STATUS の
  Blocked を解消）。
- 残: プロジェクタ実機（外部モニタとは別の投影面）での再確認、A/V 同期の体感評価、present 遅延の厳密計測。
