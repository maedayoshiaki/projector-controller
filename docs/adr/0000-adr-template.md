# ADR-0000: Decision Title

Architecture Decision Record（重い意思決定の正式記録）のテンプレート。
軽い決定は `MEMORY.md` の Decisions テーブルで十分。根拠を厚く残したい重要決定だけここに残す。

使い方: このファイルをコピーし、`docs/adr/0001-short-title.md` のように連番で増やす。

- **Status:** `Proposed` / `Accepted` / `Deprecated` / `Superseded by ADR-XXXX`
- **Date:** YYYY-MM-DD
- **Deciders:** decision makers

## Context

なぜこの決定が必要になったか。問題、制約、前提を書く。

## Decision

何を決めたかを能動態で明確に書く。

## Alternatives Considered

複数案を残すのが ADR の価値。採用案だけでなく、不採用案と理由も書く。

| 案 | 概要 | 不採用の理由 |
|----|------|------|
| A | 採用候補または採用案 | 採用案なら `-` |
| B | 代替案 | 不採用の理由 |
| C | 代替案 | 不採用の理由 |

## Consequences

- **良い影響:** 決定によって良くなること。
- **悪い影響 / トレードオフ:** コスト、制約、将来の変更しにくさ。
- **今後の課題:** 後続作業や確認事項。
