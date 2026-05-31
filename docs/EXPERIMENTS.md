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

- **Date:** 2026-05-31（local windowed smoke のみ実施。外部 display / fullscreen は未実施）
- **Commit:** `git hash`
- **Machine / OS:** Windows など
- **Projector / Display:** 機種名、接続方式、OS 上の display 番号
- **Resolution / Scaling:** 物理解像度、DPI スケール
- **Backend:** Rust renderer (`winit` + `wgpu`)
- **Media:** `examples/realtime_frames.py` 生成 RGBA frame
- **Window Settings:** display, x, y, width, height, fullscreen
- **Command:**
  ```powershell
  cargo build -p projector-controller-renderer
  uv run python examples\realtime_frames.py
  ```
- **Expected:** Rust renderer window が開き、生成グラデーション frame が滑らかに更新される。
- **Result:** local windowed smoke として、Python `RealtimeProjection` から Rust renderer を起動し、64x64 RGBA frame を 320x240 window に送信して終了できた。
- **Issues:** 外部 display / fullscreen / DPI / 座標挙動は未確認。
- **Conclusion:** Rust renderer の最小起動と frame IPC は動作。pygame backend と fullscreen 方式が異なるため、display 番号・fullscreen・DPI・座標挙動を改めて確認する。
