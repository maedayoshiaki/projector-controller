# DESIGN.md — UI デザイン仕様

**UI を持つプロジェクトのみ**使用。AI エージェントに一貫した（特に日本語の）UI を作らせるための仕様書。
`AGENTS.md`（作り方）と対になる「見た目と雰囲気」の定義。
フォーマットは Google Stitch の DESIGN.md と awesome-design-md-jp（CJK タイポグラフィ拡張）に準拠。
**規約：見出し（`##`）は英語、値の説明・Do/Don't は日本語**（AI 可読性と人間理解の両立）。

---

## 1. Visual Theme & Atmosphere
{{全体の雰囲気を言語化。例: 余白広め、静かで信頼感、角丸は控えめ}}

## 2. Color Palette & Roles

| 役割 | 値 | 用途 |
|------|------|------|
| Primary | `{{#0000ff}}` | {{主要アクション}} |
| Background | `{{#ffffff}}` | {{背景}} |
| Text | `{{#1a1a1a}}` | {{本文}} |
| Border | `{{#e0e0e0}}` | {{境界線}} |

## 3. Typography Rules（日本語拡張の核心）

### 3.1 和文フォント
{{例: Noto Sans JP / 游ゴシック。見出しと本文で分けるなら明記}}

### 3.2 欧文フォント
{{例: Inter / SF Pro。数字・英字に適用}}

### 3.3 font-family 指定（フォールバック込み）
```css
font-family: {{"Inter", "Noto Sans JP", -apple-system, "Hiragino Kaku Gothic ProN", "Yu Gothic", sans-serif}};
```
> 並び順：欧文 → 和文 → generic。和文より欧文を先に置くと英数字が欧文フォントで組まれる。

### 3.4 文字サイズ・ウェイト階層

| 用途 | size | weight | line-height |
|------|------|------|------|
| H1 | {{32px}} | {{700}} | {{1.4}} |
| Body | {{16px}} | {{400}} | {{1.8}} |
| Caption | {{13px}} | {{400}} | {{1.6}} |

### 3.5 行間・字間
- line-height: 本文 **{{1.7〜1.9}}**（和文は欧文の 1.4〜1.5 より広め）。
- letter-spacing: 本文 **{{0.04em}}** 程度。

### 3.6 禁則処理・改行ルール
- `line-break: strict;` と `overflow-wrap: anywhere;`（または `word-break: auto-phrase;`）で句読点・括弧の行頭/行末を制御。
- {{長い英単語・URL の折り返し方針}}

### 3.7 OpenType 機能
```css
font-feature-settings: {{"palt" 1, "kern" 1}};  /* 和文プロポーショナル + カーニング */
```

### 3.8 縦書き（該当する場合）
{{`writing-mode: vertical-rl;` を使うか。使わないなら「横書きのみ」と明記}}

## 4. Component Stylings
- ボタン: {{角丸・高さ・パディング・hover}}
- 入力欄: {{...}}
- カード: {{...}}

## 5. Layout Principles
{{グリッド、最大幅、余白の取り方、セクション間隔}}

## 6. Depth & Elevation
{{影の段階。例: shadow-sm / md / lg の値}}

## 7. Do's and Don'ts
- ✅ {{例: 本文 line-height は 1.7 以上}}
- ✅ {{例: 英数字は欧文フォントで組む}}
- ❌ {{例: 和文に letter-spacing 0 で詰めない}}
- ❌ {{例: 句読点を行頭に置かない（禁則を無効化しない）}}

## 8. Responsive Behavior
{{ブレークポイント、モバイルでの字サイズ・余白の調整}}

## 9. Agent Prompt Guide

> AI に UI を作らせるときの一言指示テンプレ。

{{例: 「DESIGN.md の §3 のフォント指定とフォールバックを厳守し、本文 line-height 1.8 / letter-spacing 0.04em で組むこと。句読点の禁則を無効化しないこと」}}
