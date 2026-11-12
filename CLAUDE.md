# 化学ゲームラボ — プロジェクトガイド

高校化学(化学基礎・化学)の授業用学習ゲーム集。GitHub Pages で公開する完全静的サイト。
作者は高校化学教員。生徒(高校1〜3年)がスマホ/Chromebookで使う。

## 絶対に守るルール

- **公開済みのURLを変えない**。各ゲームのリンクはすでに生徒に配ってある。HTMLのファイル名を変えたり消したりしない。作りを変えるときも同じファイル名のまま中身を入れかえる。
- **外部CDN・ビルドツール・フレームワーク禁止**。読みこんでよいのはこのリポジトリ内のファイルだけ(`common.css` `common.js` `quiz.js` `data/*.json` `img/*`)。
- **見た目と共通部品は共通ファイルに置く**(下の「共通ファイル」)。同じCSSやJSを各HTMLに書き写さない。
  - 手書き型(アクション・3D・手順型)は、共通ファイルを読んだうえで、ゲーム固有の見た目と動きだけを各HTMLの `<style>` `<script>` に書く。
- **localStorage は使ってよい**。ただし用途は自己ベスト・クリア済みの印・まちがえた問題の記録など、**消えても困らないもの**に限る。成績評価の根拠になるものや個人情報は保存しない。
  - 読み書きは必ず `try/catch` で包む。保存できない環境(プライベートブラウズ、共用端末の制限など)でも記録なしで普通に遊べること。
  - キーは `chemgames:<ファイル名>:<項目>` にそろえる(例: `chemgames:formula-tower:best`)。同じ github.io の他のページとぶつからないようにするため。
  - 端末・ブラウザごとの保存で、教師からは見えない。集計や提出には使えない前提で設計する。
  - sessionStorage は使わない。
- Firebase等のバックエンドも使わない(このリポジトリは静的サイト専用)。
- スマホ縦画面(幅375px)で崩れないこと。タッチ操作対応(`touchstart`/`touchmove` は `{passive:false}`)。
- 化学式は `<sub>`/`<sup>` で表記(例: `H<sub>2</sub>O`)。日本語の教科書表記に合わせる(「共有結合の結晶」「物質量」など)。
- 新しいゲームを追加したら **必ず index.html の UNITS 配列にカードを追加**する。

## ファイル構成

```
index.html               … トップページ(単元別のタイル。記録の表示つき)
common.css               … 共通の見た目「ARCADE POP」(配色・パネル・ボタン・HUD・結果画面・一覧)
common.js                … 共通の部品 CG(自己ベスト、効果音、数え上げ、キャラクターの吹き出し など)
quiz.js                  … クイズ型ゲームの本体(data/<名前>.json を読んで動く)
data/<名前>.json         … クイズ型の題名・説明・ルール・問題
img/gorilla.png          … 説明役のキャラクター(背景透明、320px)

クイズ型(HTMLは十数行の入れ物。中身は quiz.js と data/ がつくる)
salt-judge.html          … No.32 塩の液性
gas-race.html            … No.51 PV=nRT
colloid-match.html       … No.58 コロイド
le-chatelier.html        … No.66 平衡移動
precipitate-colors.html  … No.73 沈殿の色
detection-match.html     … No.89 有機の検出反応
polymer-quiz.html        … No.91 重合様式
oxidation-number.html    … No.36 酸化数(12択グリッド)

手書き型(common.css / common.js を読む。ゲーム固有の部分は各HTMLの中)
lewis-builder.html       … No.4  電子式→分子合成(canvas物理)
crystal-classify.html    … No.6  結晶分類+質問推理
ion-formula.html         … No.10 イオン式・組成式(ion_learning-game由来)
formula-tower.html       … No.11 物質名→化学式(ミニ周期表を押して組立、SVGモンスター)
polarity-3d.html         … No.8  3D極性判定(自作3D投影)
lattice-viewer.html      … No.14 結晶格子3D教材(自作3D投影)
gas-sim.html             … No.50 気体分子運動シミュレータ(理想/実在気体)
element-match.html       … No.1  元素記号マッチング(elemental-master-118由来)
element-position.html    … No.2  周期表の位置あて(同上)
stoichiometry.html       … No.18 量的関係を5ステップで解く
excess-reagent.html      … No.19 過不足ある反応(反応前/変化/反応後の表+テンキー)
sig-figs.html            … No.15 有効数字ドリル(10進文字列で正確に丸め)
mol-sprint.html          … No.16 モル換算(次元解析で単位を約分、1〜2段階)
sugar-rhythm.html        … No.93 単糖リズム(Haworth投影式+Web Audio)
electrolysis.html        … No.40 電気分解の手順ゲーム
equilibrium-travel.html  … No.64 太平洋トラベラー(日本⇌アメリカの人の移動で平衡を体感。実戦/シミュレーション/H2+I2の3モード、canvasグラフ自作)
```

## 共通ファイル

### 見た目「ARCADE POP」(common.css)

紫の水玉の背景に白いパネル。太い紺のフチ(3px)と、下にずれた段差の影(ぼかさない)。黄色い主ボタン。数字は幅のせまい書体(`.num`)。

```css
--navy:#1c1740(フチ・影・文字); --bg1:#6f5dff; --bg2:#4330d9; --mut:#6b6690;
--yellow:#ffcc00(主ボタン); --pink:#ff4f8b; --ok:#19c37d; --bad:#ff4f5e;
/* 単元色 --u。<body data-u="rose"> で切りかわる:
   teal #10b3c7(物質の構成・物質量) / rose #ff5f93(酸塩基・酸化還元) / blue #3d8bff(気体)
   green #2fbf71(溶液・高分子) / purple #a070ff(平衡) / brown #f08a24(無機・有機) */
```

- 上の帯 `.top`: 丸い「‹」(index.htmlへ) + タイトル + 単元チップ + 音ボタン。
- 画面は start / play / end の3セクション切替(`.hidden` クラス)。
- 主な部品: `.panel` `.btn`(`.white`) `.hud` `.tbar/.tfill` `.q` `.choices/.choice` `.rank` `.score` `.stats` `.mascot/.bubble`。
- スコアは 正解100点+連続ボーナス(コンボ×10, 上限10) が基本形。
- 淡い色・細い枠線・ぼかした影の「白いカード」には戻さない。

### 部品 CG(common.js)

各ページの変数とぶつからないよう、すべて `CG.` の下にある。

- `CG.best(ゲーム名, score, sub)` … 自己ベストを読んで更新。`{ok, prev, first, isNew}` を返す。
- `CG.sfx.tap() / ok(combo) / ng() / tick() / fin()` と `CG.soundButton()`(音のON/OFFは端末に保存)。
- `CG.countUp(el, 数)` … 数え上がる表示。`CG.fmt(数)` … 3桁区切り。
- `CG.mascot(html)` … キャラクターと吹き出しのHTML。
- `CG.$ / CG.shuffle / CG.pick`。

### キャラクター

ゴリラ(`img/gorilla.png`)は説明役。スタート画面でゲームの説明、結果画面でひとこと、一覧ページであいさつ。主役にはしない。

## クイズ型ゲームの増やし方(最頻の作業)

1. `data/<名前>.json` をつくる(既存の8本を写して直す)。
   - 共通の項目: `title` `unit` `color`(単元色の名前) `desc` `rules`(配列) `limit`(秒) `cols`(選択肢の列数) `questions`。
   - 問題の形は3通り。どれも `a` は**正解の文字そのもの**。
     - 全問で同じ選択肢: データに `"choices":[…]`、問題は `{"q","a","ex"}`
     - 誤答をそのつど選ぶ: データに `"pool":[…]`、問題は `{"q","a","ex"}`(poolから誤答3つ)
     - 問題ごとの選択肢: 問題は `{"q","a","w":[誤答…],"ex"}`
2. `<名前>.html` をつくる(既存のクイズ型HTMLを写し、`<title>` と `data-game` `data-u` を直すだけ)。
3. `index.html` の UNITS 配列にカード `{no, f, sym, nm, ds, k}` を追加。
4. スマホ幅でスタート→回答→タイムアップまで一通り動作確認。

JSON は `fetch` で読むので、HTMLをダブルクリックで開いた状態(`file://`)では動かない。確認はローカルサーバーか公開サイトで行う。

手書き型(アクション・3D・手順型)を新しく作るときは、`common.css` と `common.js` を読み、上の3セクション構成と部品を使う。
- `<body data-u="単元色">`、上の帯は `<header class="top">`、本文は `<main class="game">`(広い画面が要るときは `main.game{max-width:…}` を足す)。
- ボタンは `.btn`(主)と `.btn.white`(副)。スタート画面の説明は `.mascot` の吹き出しに入れる。
- ゲーム固有の部品も、太い紺のフチ(2〜3px)と下にずれた影にそろえる(各HTMLの「ARCADE POP に合わせる(部品)」を参考に)。
- `common.css` のクラス名(`.bubble` `.unit` `.q` など)と同じ名前をゲーム固有の部品に使わない。ぶつかると見た目がこわれる。

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
共通ファイル(`common.css` など)を変えたときは、それを読む全ページを確かめてから push する。
