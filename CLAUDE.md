# 化学ゲームラボ — プロジェクトガイド

高校化学(化学基礎・化学)の授業用学習ゲーム集。GitHub Pages で公開する完全静的サイト。
作者は高校化学教員。生徒(高校1〜3年)がスマホ/Chromebookで使う。

## 絶対に守るルール

- **全ページ自己完結のHTML 1ファイル**(CSS/JSをインラインに書く)。外部CDN・ビルドツール・フレームワーク禁止。
- **localStorage / sessionStorage は使わない**(スコア保存が必要ならメモリ内のみ)。
- Firebase等のバックエンドも使わない(このリポジトリは静的サイト専用)。
- スマホ縦画面(幅375px)で崩れないこと。タッチ操作対応(`touchstart`/`touchmove` は `{passive:false}`)。
- 化学式は `<sub>`/`<sup>` で表記(例: `H<sub>2</sub>O`)。日本語の教科書表記に合わせる(「共有結合の結晶」「物質量」など)。
- 新しいゲームを追加したら **必ず index.html の UNITS 配列にカードを追加**する。

## ファイル構成

```
index.html               … トップページ(周期表タイル風カード、単元別)
gen_quizzes.py           … クイズ型ゲームのジェネレータ(共通テンプレート+問題データ)
mol-sprint.html          … No.16 モル換算(生成問題)     ← gen_quizzes.py 由来
salt-judge.html          … No.32 塩の液性               ← 同上
gas-race.html            … No.51 PV=nRT                 ← 同上
colloid-match.html       … No.58 コロイド               ← 同上
le-chatelier.html        … No.66 平衡移動               ← 同上
precipitate-colors.html  … No.73 沈殿の色               ← 同上
detection-match.html     … No.89 有機の検出反応         ← 同上
polymer-quiz.html        … No.91 重合様式               ← 同上
oxidation-number.html    … No.36 酸化数(12択グリッド)   ← 同上
lewis-builder.html       … No.4  電子式→分子合成(canvas物理、手書き)
crystal-classify.html    … No.6  結晶分類+質問推理(手書き)
ion-formula.html         … No.10 イオン式・組成式(手書き、ion_learning-game由来)
polarity-3d.html         … No.8  3D極性判定(自作3D投影、手書き)
lattice-viewer.html      … No.14 結晶格子3D教材(自作3D投影、手書き)
electrolysis.html        … No.40 電気分解の手順ゲーム(手書き)
```

## デザイントークン(全ページ共通)

```css
--paper:#f3f6f5; --card:#fff; --ink:#1b2a33; --mut:#5b6f78; --line:#d5e0de;
--amber:#e8a13d; --bad:#d4566a; --ok:#2e9e6b;
/* アクセントは単元色: teal #0e7c86(物質の構成・物質量) / rose #c2607d(酸塩基・酸化還元)
   blue #3e77b6(気体) / green #5a9367(溶液・高分子) / purple #8a6bbf(平衡) / brown #b3702e(無機・有機) */
font-family:"Hiragino Kaku Gothic ProN","Hiragino Sans","Yu Gothic UI","Yu Gothic",Meiryo,sans-serif;
```

- ヘッダは「‹ 一覧」リンク(index.htmlへ) + タイトル + 単元チップ。下ボーダー3pxをアクセント色に。
- 画面は start / play / end の3セクション切替(`.hidden` クラス)。
- スコアは 正解100点+連続ボーナス(コンボ×10, 上限10) が基本形。

## クイズ型ゲームの増やし方(最頻の作業)

1. `gen_quizzes.py` に `make(...)` 呼び出しを1ブロック追加(既存8本を参考に)。
   - 固定問題: `staticGame(DB.map(...))`、生成問題: `const GAME={next:makeQ}`。
   - 問題オブジェクトは `{q, choices:[…], a:正解index, ex:'解説'}`。
2. `python3 gen_quizzes.py` を実行してHTMLを再生成。
3. `index.html` の UNITS 配列にカード `{no, f, sym, nm, ds, k}` を追加。
4. スマホ幅でスタート→回答→タイムアップまで一通り動作確認。

手書き型(アクション・3D・手順型)を作る場合も、上の3セクション構成・デザイントークン・ヘッダを踏襲する。

## 問題データの品質基準(化学の正確さ)

- 化学基礎/化学(発展)の範囲を守る。大学範囲の内容を混ぜない。
- 例外事項は必ず解説(`ex`)に書く: H₂O₂のO=−1、NaHのH=−1、NaHCO₃は塩基性、ZnSは白 など。
- 気体定数は R=8.3×10³ Pa·L/(K·mol)、アボガドロ定数は 6.0×10²³/mol、標準状態は 22.4 L/mol。
- 有効数字2桁を基本とする。

## デプロイ(GitHub Pages)

```bash
git add -A && git commit -m "..." && git push
```
リポジトリの Settings → Pages → Branch: main / root で公開。push後1〜2分で反映。
