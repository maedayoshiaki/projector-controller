# STATUS.md — 今の状態

**現在**を扱うファイル。「今この瞬間、何がどうなっているか」のスナップショット。
各セッションの最初に読み、最後に更新する。確定した事項は `MEMORY.md` へ昇格する。

- **Last updated:** 2026-05-30 18:01
- **Current focus:** pygame MVP 実装完了。次は実機投影テスト
- **Working branch:** main

---

## Now

- pygame backend の MVP 実装は完了。
- 関連プラン: `PLANS.md` の "Plan: pygame MVP 実装" は `Done`。

## Next

- 実機プロジェクタまたは外部ディスプレイで `uv run projector-controller --display 1 --fullscreen` を試す。
- 実機検証結果を `docs/EXPERIMENTS.md` に `projtest-001` として記録する。
- 動画再生を pygame で拡張するか、PySide6 / Qt を検討するか決める。
- 設定ファイル形式を導入するか判断する。

## Blocked

- 実機投影での fullscreen / 座標挙動確認 — **理由:** プロジェクタまたは外部ディスプレイでの手動確認待ち。

## Recently Done

- 2026-05-30 テンプレート文書を整理し、README、AGENTS、設計、用語、表示設計、投影テストログを projector-controller 向けに更新。
- 2026-05-30 テンプレート専用の `TEMPLATE_GUIDE.md` を削除し、ADR テンプレートをプロジェクト用に調整。
- 2026-05-30 Python 3.12 + uv 環境、`ProjectionWindow` API、pygame backend、CLI、examples、tests を追加。
- 2026-05-30 `uv run ruff format .`、`uv run ruff check .`、`uv run mypy src tests`、`uv run pytest` を通過。
- 2026-05-30 `uv run projector-controller --list-displays` で display 0 `1440x900`、display 1 `1280x800` を確認。

## Open Questions for the Human

- [ ] 動画再生で音声を扱う必要があるか。
- [ ] 動画再生を pygame で続けるか、PySide6 / Qt などへ広げるか。
- [ ] 設定ファイル形式を導入するか。導入する場合は TOML / YAML / JSON のどれにするか。

## Environment Notes

- `uv sync --dev` で `.venv` を作成済み。
- `.python-version` は `3.12`。
- CLI は `uv run projector-controller ...` で実行する。
