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

まだ投影テストは記録されていない。
