# STATUS.md — 今の状態

**現在**を扱うファイル。「今この瞬間、何がどうなっているか」のスナップショット。
各セッションの最初に読み、最後に更新する。確定した事項は `MEMORY.md` へ昇格する。

- **Last updated:** 2026-05-30 17:42
- **Current focus:** 初期ドキュメント整理完了。次は実装方針の人間判断待ち
- **Working branch:** main

---

## Now

- 初期ドキュメント整理は完了。
- 関連プラン: `PLANS.md` の "Plan: Projector Controller 文書初期整理" は `Done`。

## Next

- Python 実装環境をどう作るか決める。
- 最初の公開 API 形状を決める。
- GUI / メディア再生バックエンド候補を比較し、人間確認後に選ぶ。
- `src/projector_controller/` と `tests/` を追加する場合は、事前に計画を作る。

## Blocked

- 公開 API、依存ライブラリ、バックエンドの確定 — **理由:** 人間の判断待ち。

## Recently Done

- 2026-05-30 テンプレート文書を整理し、README、AGENTS、設計、用語、表示設計、投影テストログを projector-controller 向けに更新。
- 2026-05-30 テンプレート専用の `TEMPLATE_GUIDE.md` を削除し、ADR テンプレートをプロジェクト用に調整。

## Open Questions for the Human

- [ ] 最初の公開 API は、関数ベース、ウィンドウオブジェクトベース、設定ファイルベースのどれを優先するか。
- [ ] GUI / メディア再生バックエンドはどの候補から検証するか。
- [ ] Python バージョンと依存管理方式をどうするか。
- [ ] 動画再生で音声を扱う必要があるか。

## Environment Notes

- 現時点では `pyproject.toml`、`src/`、`tests/`、実行コマンドは未作成。
- ドキュメントのみの変更なので、Python の検証スタックはまだ対象外。
