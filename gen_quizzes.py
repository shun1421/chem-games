# -*- coding: utf-8 -*-
"""共通テンプレートからクイズ型ゲームHTMLを生成する"""
import os

OUT = "."
os.makedirs(OUT, exist_ok=True)

TEMPLATE = r"""<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>@@TITLE@@ | 化学ゲームラボ</title>
<style>
:root{--paper:#f3f6f5;--card:#fff;--ink:#1b2a33;--mut:#5b6f78;--line:#d5e0de;
--acc:@@ACCENT@@;--bad:#d4566a;--ok:#2e9e6b;
--mono:"SFMono-Regular",Consolas,"Courier New",monospace}
*{box-sizing:border-box}
body{margin:0;background:var(--paper);color:var(--ink);
font-family:"Hiragino Kaku Gothic ProN","Hiragino Sans","Yu Gothic UI","Yu Gothic",Meiryo,sans-serif}
header{display:flex;align-items:center;gap:12px;padding:10px 16px;background:var(--card);border-bottom:3px solid var(--acc)}
.back{color:var(--acc);text-decoration:none;font-weight:700;font-size:14px}
.htitle{font-weight:800;letter-spacing:.05em}
.chip{margin-left:auto;font-size:12px;color:var(--acc);border:1px solid var(--acc);border-radius:999px;padding:2px 10px;white-space:nowrap}
main{max-width:720px;margin:0 auto;padding:20px 14px}
.panel{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:22px;box-shadow:0 2px 10px rgba(27,42,51,.05)}
.hidden{display:none}
h1{font-size:22px;margin:0 0 8px;letter-spacing:.04em}
.desc{color:var(--mut);margin:.4em 0}
.rules{color:var(--mut);font-size:14px;padding-left:20px;line-height:1.8}
button.primary{display:block;width:100%;margin-top:14px;padding:14px;font-size:17px;font-weight:800;color:#fff;background:var(--acc);border:0;border-radius:10px;cursor:pointer}
button.primary:active{transform:translateY(1px)}
.ghost{display:block;text-align:center;margin-top:12px;color:var(--acc);font-weight:700;text-decoration:none}
.hud{display:flex;gap:8px;justify-content:space-between;font-size:13px;color:var(--mut)}
.hud b{font-family:var(--mono);font-size:18px;color:var(--ink);margin-left:4px}
#tbar{height:6px;background:var(--line);border-radius:3px;margin:10px 0}
#tfill{height:100%;width:100%;background:var(--acc);border-radius:3px;transition:width .1s linear}
#qtext{min-height:86px;display:flex;align-items:center;justify-content:center;text-align:center;font-size:22px;font-weight:700;margin:8px 0;line-height:1.5}
#choices{display:grid;gap:10px}
#choices button{padding:14px 6px;font-size:16px;font-weight:700;background:#fff;border:2px solid var(--line);border-radius:10px;cursor:pointer;color:var(--ink)}
#choices button.correct{border-color:var(--ok);background:#e9f7f0}
#choices button.wrong{border-color:var(--bad);background:#fbeef0}
#fb{min-height:44px;margin-top:12px;font-size:14px;color:var(--mut);text-align:center;line-height:1.6}
#fb .good{color:var(--ok);font-weight:800}
#fb .bad{color:var(--bad);font-weight:800}
.result{font-size:18px;text-align:center;line-height:2}
.result b{font-family:var(--mono);font-size:34px;color:var(--acc)}
sub,sup{font-size:.62em}
@media(max-width:480px){#qtext{font-size:19px}}
</style>
</head>
<body>
<header>
  <a class="back" href="index.html">‹ 一覧</a>
  <div class="htitle">@@TITLE@@</div>
  <span class="chip">@@UNIT@@</span>
</header>
<main>
  <section id="start" class="panel">
    <h1>@@TITLE@@</h1>
    <p class="desc">@@DESC@@</p>
    <ul class="rules">@@RULES@@</ul>
    <button class="primary" onclick="startGame()">スタート</button>
  </section>
  <section id="play" class="panel hidden">
    <div class="hud">
      <div>のこり<b id="time"></b>秒</div>
      <div>スコア<b id="score">0</b></div>
      <div>連続<b id="combo">0</b></div>
    </div>
    <div id="tbar"><div id="tfill"></div></div>
    <div id="qtext"></div>
    <div id="choices"></div>
    <div id="fb"></div>
  </section>
  <section id="end" class="panel hidden">
    <h1>タイムアップ！</h1>
    <p class="result">スコア <b id="fscore"></b><br>正答 <span id="facc"></span></p>
    <button class="primary" onclick="startGame()">もう一度</button>
    <a class="ghost" href="index.html">一覧へ戻る</a>
  </section>
</main>
<script>
function shuffle(a){for(let i=a.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[a[i],a[j]]=[a[j],a[i]];}return a}
function pick(a){return a[Math.floor(Math.random()*a.length)]}
function fmt(x){return (Math.round(x*1000)/1000).toString()}
function finalize(q,list,correct,ex){
  const arr=list.map((s,i)=>({s:s,c:i===correct}));shuffle(arr);
  return {q:q,choices:arr.map(o=>o.s),a:arr.findIndex(o=>o.c),ex:ex};
}
function qnum(q,ans,wrongs,unit,ex){
  let vals=[ans];
  for(const w of wrongs){if(vals.every(v=>Math.abs(v-w)>1e-9))vals.push(w);if(vals.length>=4)break;}
  while(vals.length<4)vals.push(ans*(vals.length+5));
  return finalize(q,vals.map(v=>fmt(v)+" "+unit),0,ex);
}
function staticGame(list){let pool=[];return{next(){if(!pool.length)pool=shuffle(list.slice());return pool.pop();}}}
@@GAME_JS@@
const LIMIT=@@LIMIT@@;
let score=0,combo=0,ok=0,total=0,tLeft=0,timer=null,cur=null,locked=false;
const $=id=>document.getElementById(id);
function startGame(){
  score=0;combo=0;ok=0;total=0;tLeft=LIMIT;
  $('start').classList.add('hidden');$('end').classList.add('hidden');$('play').classList.remove('hidden');
  upd();nextQ();clearInterval(timer);
  timer=setInterval(()=>{tLeft-=0.1;if(tLeft<=0){tLeft=0;finish();}drawT();},100);drawT();
}
function drawT(){$('time').textContent=Math.ceil(tLeft);$('tfill').style.width=(tLeft/LIMIT*100)+'%';}
function upd(){$('score').textContent=score;$('combo').textContent=combo;}
function nextQ(){
  locked=false;$('fb').innerHTML='';cur=GAME.next();
  $('qtext').innerHTML=cur.q;
  const c=$('choices');c.innerHTML='';
  c.style.gridTemplateColumns='repeat(@@COLS@@,1fr)';
  cur.choices.forEach((ch,i)=>{const b=document.createElement('button');b.innerHTML=ch;b.onclick=()=>answer(i,b);c.appendChild(b);});
}
function answer(i,btn){
  if(locked)return;locked=true;total++;
  const bs=$('choices').children;bs[cur.a].classList.add('correct');
  if(i===cur.a){ok++;combo++;score+=100+Math.min(combo,10)*10;
    $('fb').innerHTML='<span class="good">正解！</span> '+(cur.ex||'');setTimeout(nextQ,750);}
  else{btn.classList.add('wrong');combo=0;
    $('fb').innerHTML='<span class="bad">おしい！</span> '+(cur.ex||'');setTimeout(nextQ,1700);}
  upd();
}
function finish(){clearInterval(timer);$('play').classList.add('hidden');$('end').classList.remove('hidden');
  $('fscore').textContent=score;$('facc').textContent=ok+' 問 / '+total+' 問';}
</script>
</body>
</html>
"""

def make(fname, title, unit, desc, rules, game_js, limit=60, cols=2, accent="#0e7c86"):
    html = (TEMPLATE
            .replace("@@TITLE@@", title)
            .replace("@@UNIT@@", unit)
            .replace("@@DESC@@", desc)
            .replace("@@RULES@@", "".join(f"<li>{r}</li>" for r in rules))
            .replace("@@GAME_JS@@", game_js)
            .replace("@@LIMIT@@", str(limit))
            .replace("@@COLS@@", str(cols))
            .replace("@@ACCENT@@", accent))
    with open(os.path.join(OUT, fname), "w", encoding="utf-8") as f:
        f.write(html)
    print("wrote", fname)

# ============ No.16 モル換算スプリント ============
mol_js = r"""
const SUBS=[['H<sub>2</sub>O',18],['CO<sub>2</sub>',44],['O<sub>2</sub>',32],['N<sub>2</sub>',28],
['CH<sub>4</sub>',16],['NH<sub>3</sub>',17],['NaCl',58.5],['Al',27],['Fe',56],['C',12]];
const NS=[0.25,0.5,1,1.5,2,2.5,3,4,5];
function sci(n){let v=n*6.0,e=23;while(v>=10){v/=10;e++;}while(v<1&&e>20){v*=10;e--;}
  v=Math.round(v*100)/100;return fmt(v)+'×10<sup>'+e+'</sup>';}
function makeQ(){
  const t=Math.floor(Math.random()*6);const s=pick(SUBS),f=s[0],M=s[1];const n=pick(NS);
  if(t===0){const m=M*n;
    return qnum(f+'(モル質量 '+M+' g/mol)が '+fmt(m)+' g ある。物質量は？',n,[n*2,n/2,n*10],'mol',
      fmt(m)+' g ÷ '+M+' g/mol = '+fmt(n)+' mol');}
  if(t===1){const m=M*n;
    return qnum(f+'(モル質量 '+M+' g/mol)が '+fmt(n)+' mol ある。質量は？',m,[m*2,m/2,M+n],'g',
      M+' g/mol × '+fmt(n)+' mol = '+fmt(m)+' g');}
  if(t===2){const list=[sci(n),sci(n*2),sci(n/2),sci(n*5)].map(x=>x+' 個');
    return finalize(f+'が '+fmt(n)+' mol ある。粒子の数は？(アボガドロ定数 6.0×10<sup>23</sup>/mol)',list,0,
      fmt(n)+' mol × 6.0×10<sup>23</sup>/mol = '+sci(n)+' 個');}
  if(t===3){return qnum(f+'の粒子が '+sci(n)+' 個ある。物質量は？',n,[n*2,n/2,n*10],'mol',
      '個数 ÷ 6.0×10<sup>23</sup>/mol = '+fmt(n)+' mol');}
  if(t===4){const v=22.4*n;
    return qnum('標準状態で '+f+'(気体)が '+fmt(n)+' mol ある。体積は？',v,[v*2,v/2,n],'L',
      '22.4 L/mol × '+fmt(n)+' mol = '+fmt(v)+' L');}
  const v=22.4*n;
  return qnum('標準状態で '+f+'(気体)が '+fmt(v)+' L ある。物質量は？',n,[n*2,n/2,v],'mol',
    fmt(v)+' L ÷ 22.4 L/mol = '+fmt(n)+' mol');
}
const GAME={next:makeQ};
"""
make("mol-sprint.html","モル換算スプリント","物質量",
     "質量・個数・体積・molの換算を、時間内にできるだけ多く正解しよう。",
     ["制限時間は60秒","連続正解でボーナスが増える","気体の体積は標準状態(22.4 L/mol)で考える"],
     mol_js, 60, 2, "#0e7c86")

# ============ No.32 塩の液性ジャッジ ============
salt_js = r"""
const CH=['酸性','中性','塩基性'];
const DB=[
['NaCl',1,'強酸(HCl)+強塩基(NaOH)の塩 → 中性'],
['KNO<sub>3</sub>',1,'強酸(HNO<sub>3</sub>)+強塩基(KOH)の塩 → 中性'],
['Na<sub>2</sub>SO<sub>4</sub>',1,'強酸(H<sub>2</sub>SO<sub>4</sub>)+強塩基(NaOH)の塩 → 中性'],
['NH<sub>4</sub>Cl',0,'強酸(HCl)+弱塩基(NH<sub>3</sub>)の塩 → 酸性'],
['NH<sub>4</sub>NO<sub>3</sub>',0,'強酸(HNO<sub>3</sub>)+弱塩基(NH<sub>3</sub>)の塩 → 酸性'],
['(NH<sub>4</sub>)<sub>2</sub>SO<sub>4</sub>',0,'強酸(H<sub>2</sub>SO<sub>4</sub>)+弱塩基(NH<sub>3</sub>)の塩 → 酸性'],
['CuSO<sub>4</sub>',0,'強酸+弱塩基(Cu(OH)<sub>2</sub>)の塩 → 酸性'],
['CH<sub>3</sub>COONa',2,'弱酸(酢酸)+強塩基(NaOH)の塩 → 塩基性'],
['Na<sub>2</sub>CO<sub>3</sub>',2,'弱酸(炭酸)+強塩基(NaOH)の塩 → 塩基性'],
['NaHCO<sub>3</sub>',2,'酸性塩だが水溶液は塩基性(弱酸+強塩基由来)。名前にだまされない！'],
['NaHSO<sub>4</sub>',0,'酸性塩で、水溶液も酸性(強酸H<sub>2</sub>SO<sub>4</sub>由来でH<sup>+</sup>を出す)'],
['K<sub>2</sub>CO<sub>3</sub>',2,'弱酸(炭酸)+強塩基(KOH)の塩 → 塩基性'],
['FeCl<sub>3</sub>',0,'強酸+弱塩基(Fe(OH)<sub>3</sub>)の塩 → 酸性'],
['CH<sub>3</sub>COOK',2,'弱酸(酢酸)+強塩基(KOH)の塩 → 塩基性'],
['CaCl<sub>2</sub>',1,'強酸(HCl)+強塩基(Ca(OH)<sub>2</sub>)の塩 → 中性'],
];
const GAME=staticGame(DB.map(d=>({q:d[0]+' の水溶液の液性は？',choices:CH,a:d[1],ex:d[2]})));
"""
make("salt-judge.html","塩の液性ジャッジ","酸と塩基",
     "塩の水溶液が酸性・中性・塩基性のどれかを見きわめよう。もとの酸と塩基の強弱がヒント。",
     ["制限時間は60秒","「強酸+強塩基→中性」「強酸+弱塩基→酸性」「弱酸+強塩基→塩基性」","酸性塩(NaHCO<sub>3</sub>など)はひっかけ注意"],
     salt_js, 60, 3, "#c2607d")

# ============ No.51 気体方程式レース ============
gas_js = r"""
const DB=[
{q:'n=2.0 mol, T=300 K, V=8.3 L のとき圧力Pは？',a:'6.0×10<sup>5</sup> Pa',w:['3.0×10<sup>5</sup> Pa','1.2×10<sup>6</sup> Pa','6.0×10<sup>4</sup> Pa'],ex:'P=nRT/V=2.0×8.3×10<sup>3</sup>×300÷8.3'},
{q:'n=1.0 mol, T=400 K, V=8.3 L のとき圧力Pは？',a:'4.0×10<sup>5</sup> Pa',w:['2.0×10<sup>5</sup> Pa','8.0×10<sup>5</sup> Pa','4.0×10<sup>4</sup> Pa'],ex:'P=nRT/V=1.0×8.3×10<sup>3</sup>×400÷8.3'},
{q:'n=0.50 mol, T=600 K, V=8.3 L のとき圧力Pは？',a:'3.0×10<sup>5</sup> Pa',w:['6.0×10<sup>5</sup> Pa','1.5×10<sup>5</sup> Pa','3.0×10<sup>4</sup> Pa'],ex:'P=nRT/V=0.50×8.3×10<sup>3</sup>×600÷8.3'},
{q:'n=0.25 mol, T=400 K, V=8.3 L のとき圧力Pは？',a:'1.0×10<sup>5</sup> Pa',w:['2.0×10<sup>5</sup> Pa','5.0×10<sup>4</sup> Pa','1.0×10<sup>6</sup> Pa'],ex:'P=nRT/V=0.25×8.3×10<sup>3</sup>×400÷8.3'},
{q:'P=1.0×10<sup>5</sup> Pa, n=1.0 mol, T=300 K のとき体積Vは？',a:'約 25 L',w:['約 12 L','約 50 L','約 2.5 L'],ex:'V=nRT/P=8.3×10<sup>3</sup>×300÷10<sup>5</sup>=24.9 L'},
{q:'P=1.0×10<sup>5</sup> Pa, n=2.0 mol, T=300 K のとき体積Vは？',a:'約 50 L',w:['約 25 L','約 100 L','約 5.0 L'],ex:'V=nRT/P=2.0×8.3×10<sup>3</sup>×300÷10<sup>5</sup>=49.8 L'},
{q:'P=1.0×10<sup>5</sup> Pa, V=8.3 L, T=250 K のとき物質量nは？',a:'0.40 mol',w:['0.80 mol','0.20 mol','4.0 mol'],ex:'n=PV/RT=10<sup>5</sup>×8.3÷(8.3×10<sup>3</sup>×250)'},
{q:'P=2.0×10<sup>5</sup> Pa, V=8.3 L, T=400 K のとき物質量nは？',a:'0.50 mol',w:['1.0 mol','0.25 mol','5.0 mol'],ex:'n=PV/RT=2.0×10<sup>5</sup>×8.3÷(8.3×10<sup>3</sup>×400)'},
{q:'P=1.0×10<sup>5</sup> Pa, V=8.3 L, n=0.50 mol のとき温度Tは？',a:'200 K',w:['400 K','100 K','300 K'],ex:'T=PV/nR=10<sup>5</sup>×8.3÷(0.50×8.3×10<sup>3</sup>)'},
{q:'P=3.0×10<sup>5</sup> Pa, V=8.3 L, n=1.0 mol のとき温度Tは？',a:'300 K',w:['600 K','150 K','83 K'],ex:'T=PV/nR=3.0×10<sup>5</sup>×8.3÷(1.0×8.3×10<sup>3</sup>)'},
];
const GAME=staticGame(DB.map(d=>finalize('PV=nRT で考える。<br>'+d.q,[d.a].concat(d.w),0,d.ex)));
"""
make("gas-race.html","気体方程式レース","気体・状態変化",
     "気体の状態方程式 PV=nRT の計算レース。R=8.3×10<sup>3</sup> Pa・L/(K・mol) とする。",
     ["制限時間は90秒","V=8.3 L の問題が多い理由を考えると暗算が速くなる","単位(Pa・L・K・mol)に注目"],
     gas_js, 90, 2, "#3e77b6")

# ============ No.58 コロイドマッチ ============
colloid_js = r"""
const DB=[
{q:'コロイド溶液に横から強い光を当てると、光の通り道が明るく見える現象は？',a:'チンダル現象',w:['ブラウン運動','電気泳動','透析'],ex:'コロイド粒子が光を散乱するため。'},
{q:'限外顕微鏡で見える、コロイド粒子の不規則な運動は？',a:'ブラウン運動',w:['チンダル現象','凝析','電気泳動'],ex:'熱運動する水分子が粒子に衝突して起こる。'},
{q:'コロイド溶液に直流電圧をかけると、粒子が一方の電極へ移動する現象は？',a:'電気泳動',w:['塩析','透析','チンダル現象'],ex:'コロイド粒子が帯電しているため。'},
{q:'半透膜を使って、コロイド粒子と小さな分子・イオンを分ける操作は？',a:'透析',w:['ろ過','蒸留','電気泳動'],ex:'コロイド粒子は半透膜を通れない。人工透析にも応用。'},
{q:'疎水コロイドに<b>少量</b>の電解質を加えると沈殿する現象は？',a:'凝析',w:['塩析','透析','ゲル化'],ex:'反対符号のイオンが電荷を打ち消して集まる。価数の大きいイオンほど有効。'},
{q:'親水コロイドに<b>多量</b>の電解質を加えると沈殿する現象は？',a:'塩析',w:['凝析','電気泳動','チンダル現象'],ex:'水和している水分子がうばわれて沈殿する。'},
{q:'疎水コロイドを凝析しにくくするために加える親水コロイドを何という？',a:'保護コロイド',w:['会合コロイド','分子コロイド','ゲル'],ex:'例:墨汁のにかわ。'},
{q:'流動性を失って固まったコロイドを何という？',a:'ゲル',w:['ゾル','エーロゾル','ミセル'],ex:'例:豆腐、ゼリー。流動性があるものはゾル。'},
{q:'Fe(OH)<sub>3</sub>コロイドの凝析にもっとも有効なイオンは？(正コロイドとする)',a:'PO<sub>4</sub><sup>3−</sup>',w:['Cl<sup>−</sup>','Na<sup>+</sup>','SO<sub>4</sub><sup>2−</sup>…Clと同等'],ex:'反対符号で価数が大きいイオンほど凝析させやすい。'},
{q:'セッケン水のように、分子が集まってできるコロイドを何という？',a:'会合コロイド(ミセル)',w:['分子コロイド','保護コロイド','ゲル'],ex:'デンプンやタンパク質は1分子で大きい「分子コロイド」。'},
{q:'空気中に液体や固体の微粒子が分散しているコロイドは？',a:'エーロゾル',w:['ゾル','ゲル','エマルション'],ex:'例:霧、煙。'},
{q:'牛乳のように、液体中に液体が分散しているコロイドは？',a:'エマルション(乳濁液)',w:['サスペンション','エーロゾル','ゲル'],ex:'固体が分散していればサスペンション(懸濁液)。'},
];
const GAME=staticGame(DB.map(d=>finalize(d.q,[d.a].concat(d.w),0,d.ex)));
"""
make("colloid-match.html","コロイドマッチ","溶液",
     "コロイドの現象・用語を高速マッチング。用語と現象を結びつけよう。",
     ["制限時間は60秒","チンダル・ブラウン・電気泳動・透析・凝析・塩析…混同しがちな用語を整理"],
     colloid_js, 60, 2, "#5a9367")

# ============ No.66 平衡移動よそう ============
lechat_js = r"""
const CH=['右に移動','左に移動','移動しない'];
const NH3='N<sub>2</sub> + 3H<sub>2</sub> ⇌ 2NH<sub>3</sub>(正反応は発熱)';
const SO3='2SO<sub>2</sub> + O<sub>2</sub> ⇌ 2SO<sub>3</sub>(正反応は発熱)';
const HI='H<sub>2</sub> + I<sub>2</sub> ⇌ 2HI(すべて気体)';
const NO2='N<sub>2</sub>O<sub>4</sub> ⇌ 2NO<sub>2</sub>(正反応は吸熱)';
const CO='C(固) + CO<sub>2</sub> ⇌ 2CO(正反応は吸熱)';
const DB=[
[NH3,'圧力を高くする',0,'気体分子数が減る右(4分子→2分子)へ移動。'],
[NH3,'温度を上げる',1,'吸熱方向=左へ移動して熱をやわらげる。'],
[NH3,'NH<sub>3</sub>を取り除く',0,'NH<sub>3</sub>を補う右へ移動。'],
[NH3,'触媒を加える',2,'触媒は平衡に達する時間を短くするだけで、平衡は移動しない。'],
[NH3,'N<sub>2</sub>を加える(体積一定)',0,'N<sub>2</sub>を減らす右へ移動。'],
[NH3,'体積一定でアルゴンを加える',2,'各気体の濃度(分圧)が変わらないので移動しない。'],
[NH3,'全圧一定でアルゴンを加える',1,'体積が増えて各分圧が下がる → 分子数が増える左へ。難問！'],
[SO3,'圧力を高くする',0,'気体分子数が減る右(3分子→2分子)へ。'],
[SO3,'温度を下げる',0,'発熱方向=右へ移動。工業的には速度との兼ね合いで400〜600℃。'],
[HI,'圧力を高くする',2,'両辺とも気体2分子なので圧力では移動しない。'],
[HI,'H<sub>2</sub>を加える(体積一定)',0,'H<sub>2</sub>を減らす右へ移動。'],
[NO2,'温度を上げる',0,'吸熱方向=右へ。赤褐色(NO<sub>2</sub>)が濃くなる。'],
[NO2,'圧力を低くする',0,'気体分子数が増える右(1分子→2分子)へ。'],
[CO,'圧力を高くする',1,'固体は数えない。気体は右2分子・左1分子なので左へ。'],
[CO,'温度を上げる',0,'吸熱方向=右へ移動。'],
];
const GAME=staticGame(DB.map(d=>({q:d[0]+'<br><span style="color:#5b6f78;font-size:.8em">条件変化:</span> '+d[1],choices:CH,a:d[2],ex:d[3]})));
"""
make("le-chatelier.html","平衡移動よそう","化学平衡",
     "ルシャトリエの原理で平衡の移動方向を予想しよう。「変化をやわらげる向き」が合言葉。",
     ["制限時間は90秒","圧力→気体分子数、温度→発熱/吸熱に注目","触媒・不活性気体のひっかけに注意"],
     lechat_js, 90, 3, "#8a6bbf")

# ============ No.73 沈殿カラー図鑑 ============
ppt_js = r"""
const COLORS=['白','黒','黄','淡黄','赤褐','青白','緑白','暗赤','淡赤(桃)'];
const DB=[
['AgCl','白','塩化銀。感光して黒ずむ。アンモニア水に溶ける。'],
['AgBr','淡黄','臭化銀。写真フィルムに利用。'],
['AgI','黄','ヨウ化銀。ハロゲン化銀はCl→Iの順に黄色が濃くなる。'],
['Ag<sub>2</sub>CrO<sub>4</sub>','暗赤','クロム酸銀。暗赤(赤褐)色。'],
['BaSO<sub>4</sub>','白','硫酸バリウム。X線造影剤。酸にも溶けない。'],
['CaCO<sub>3</sub>','白','炭酸カルシウム。石灰水の白濁の正体。'],
['PbS','黒','硫化鉛。硫化物の多くは黒。'],
['CuS','黒','硫化銅(II)。酸性でもH<sub>2</sub>Sで沈殿する。'],
['ZnS','白','硫化亜鉛。硫化物では例外的に白!'],
['CdS','黄','硫化カドミウム。黄色の代表。絵の具のカドミウムイエロー。'],
['MnS','淡赤(桃)','硫化マンガン(II)。淡赤(桃)色。'],
['Fe(OH)<sub>3</sub>','赤褐','水酸化鉄(III)。赤褐色。'],
['Cu(OH)<sub>2</sub>','青白','水酸化銅(II)。加熱すると黒色CuOに。'],
['Cr(OH)<sub>3</sub>','緑白','水酸化クロム(III)。灰緑色。'],
['PbI<sub>2</sub>','黄','ヨウ化鉛(II)。熱水に溶け、冷やすと黄色の結晶が再び出る。'],
['PbCrO<sub>4</sub>','黄','クロム酸鉛(II)。黄色顔料(クロムイエロー)。'],
['BaCrO<sub>4</sub>','黄','クロム酸バリウム。黄色。'],
['PbCl<sub>2</sub>','白','塩化鉛(II)。熱水には溶ける。'],
];
const GAME=staticGame(DB.map(d=>{
  const wrongs=shuffle(COLORS.filter(c=>c!==d[1])).slice(0,3);
  return finalize('沈殿 '+d[0]+' の色は？',[d[1]].concat(wrongs),0,d[2]);
}));
"""
make("precipitate-colors.html","沈殿カラー図鑑","無機化学",
     "沈殿の色をコンプリートしよう。系統分析・入試の頻出知識。",
     ["制限時間は90秒","硫化物は基本黒、ZnSは白・CdSは黄・MnSは淡赤","クロム酸塩は黄系が多い"],
     ppt_js, 90, 2, "#b3702e")

# ============ No.89 検出反応マッチ ============
detect_js = r"""
const DB=[
{q:'アンモニア性硝酸銀水溶液を加えて温めると銀が析出(銀鏡反応)。存在する官能基は？',a:'ホルミル基(アルデヒド)',w:['ヒドロキシ基','カルボキシ基','エーテル結合'],ex:'アルデヒドの還元性による。'},
{q:'フェーリング液を加えて加熱すると赤色沈殿。この沈殿は？',a:'Cu<sub>2</sub>O',w:['CuO','Cu(OH)<sub>2</sub>','Cu'],ex:'アルデヒドがCu<sup>2+</sup>を還元して酸化銅(I)を生じる。'},
{q:'ヨウ素と水酸化ナトリウム水溶液を加えて温めると黄色沈殿(ヨードホルム反応)。陽性になる構造は？',a:'CH<sub>3</sub>CO−R または CH<sub>3</sub>CH(OH)−R',w:['−COOH','−CHOすべて','ベンゼン環'],ex:'アセトン・エタノールは陽性、メタノール・酢酸は陰性。'},
{q:'臭素水を加えると赤褐色が消える。存在する構造は？',a:'C=C 二重結合(不飽和結合)',w:['ヒドロキシ基','エステル結合','アミノ基'],ex:'付加反応により臭素が消費される。'},
{q:'塩化鉄(III)水溶液を加えると青紫〜赤紫に呈色。存在するのは？',a:'フェノール類',w:['アルコール','カルボン酸','アルデヒド'],ex:'ベンゼン環に直接−OHがつくフェノール類の検出法。'},
{q:'ナトリウムの単体を加えると水素が発生。存在する官能基は？',a:'ヒドロキシ基(−OH)',w:['ニトロ基','C=C二重結合','エーテル結合'],ex:'アルコール・フェノール・カルボン酸などで陽性。エーテルは陰性。'},
{q:'炭酸水素ナトリウム水溶液を加えると気体(CO<sub>2</sub>)が発生。存在する官能基は？',a:'カルボキシ基(−COOH)',w:['ヒドロキシ基','ホルミル基','ケトン基'],ex:'炭酸より強い酸であるカルボン酸の検出。フェノールは陰性。'},
{q:'ニンヒドリン水溶液を加えて温めると紫に呈色。検出されるのは？',a:'アミノ酸・タンパク質',w:['糖','油脂','フェノール類'],ex:'アミノ基との反応。指紋の検出にも使われる。'},
{q:'水酸化ナトリウムと硫酸銅(II)水溶液で赤紫に呈色(ビウレット反応)。陽性となるのは？',a:'トリペプチド以上のペプチド',w:['アミノ酸1分子','単糖','ジペプチド以下すべて'],ex:'ペプチド結合が2つ以上必要。'},
{q:'濃硝酸を加えて加熱すると黄色になる(キサントプロテイン反応)。検出されるのは？',a:'ベンゼン環をもつアミノ酸',w:['硫黄をもつアミノ酸','グリシン','デンプン'],ex:'ベンゼン環のニトロ化による。'},
{q:'さらし粉水溶液で赤紫に呈色する芳香族化合物は？',a:'アニリン',w:['フェノール','安息香酸','トルエン'],ex:'アニリンの代表的な検出反応。'},
{q:'デンプンに加えると青紫に呈色するのは？',a:'ヨウ素ヨウ化カリウム水溶液',w:['フェーリング液','臭素水','塩化鉄(III)水溶液'],ex:'ヨウ素デンプン反応。らせん構造にI<sub>2</sub>が取り込まれる。'},
];
const GAME=staticGame(DB.map(d=>finalize(d.q,[d.a].concat(d.w),0,d.ex)));
"""
make("detection-match.html","検出反応マッチ","有機化学",
     "有機化合物の検出反応と官能基・構造を結びつけよう。構造決定問題の武器になる。",
     ["制限時間は90秒","「試薬+変化」→「構造」の対応を瞬時に","ヨードホルム・銀鏡は構造決定の最頻出ヒント"],
     detect_js, 90, 2, "#b3702e")

# ============ No.91 重合しきわけ ============
poly_js = r"""
const CH=['付加重合','縮合重合','開環重合','付加縮合'];
const DB=[
['ポリエチレン(原料:エチレン)',0,'C=Cが開いてつながる付加重合。'],
['ポリプロピレン(原料:プロペン)',0,'C=Cの付加重合。'],
['ポリ塩化ビニル(原料:塩化ビニル)',0,'C=Cの付加重合。'],
['ポリスチレン(原料:スチレン)',0,'C=Cの付加重合。'],
['ポリ酢酸ビニル(原料:酢酸ビニル)',0,'C=Cの付加重合。ビニロンの原料。'],
['ポリエチレンテレフタラート(PET)',1,'テレフタル酸+エチレングリコール。水がとれてつながる縮合重合。'],
['ナイロン66',1,'アジピン酸+ヘキサメチレンジアミン。アミド結合をつくる縮合重合。'],
['ナイロン6(原料:ε-カプロラクタム)',2,'環状のカプロラクタムが開いてつながる開環重合。'],
['フェノール樹脂(フェノール+ホルムアルデヒド)',3,'付加と縮合をくり返す付加縮合。ベークライト。'],
['尿素樹脂(尿素+ホルムアルデヒド)',3,'付加縮合。熱硬化性樹脂。'],
['メラミン樹脂(メラミン+ホルムアルデヒド)',3,'付加縮合。食器などに利用。'],
['ポリメタクリル酸メチル(アクリル樹脂)',0,'C=Cの付加重合。水族館の水槽にも。'],
['ポリブタジエン(合成ゴム)',0,'共役ジエンの付加重合。1,4-付加が主。'],
['シリコーンゴム…ではなくポリ乳酸(生分解性)',1,'乳酸の−OHと−COOHの縮合重合。'],
];
const GAME=staticGame(DB.map(d=>({q:d[0]+'<br>の重合様式は？',choices:CH,a:d[1],ex:d[2]})));
"""
make("polymer-quiz.html","重合しきわけ","高分子化合物",
     "高分子の名前・原料から重合様式(付加・縮合・開環・付加縮合)を見きわめよう。",
     ["制限時間は90秒","C=Cがあれば付加、水がとれるなら縮合","ナイロン6と66のちがいに注意"],
     poly_js, 90, 2, "#5a9367")

# ============ No.36 酸化数バトル ============
ox_js = r"""
const CH=['−4','−3','−2','−1','0','+1','+2','+3','+4','+5','+6','+7'];
function T(s){return '<span style="color:#e8a13d">'+s+'</span>'}
const DB=[
['H<sub>2</sub>'+T('S'),'−2','Hは+1×2、全体は0 → S=−2'],
[T('S')+'O<sub>2</sub>','+4','Oは−2×2、全体は0 → S=+4'],
['H<sub>2</sub>'+T('S')+'O<sub>4</sub>','+6','H:+1×2, O:−2×4 → S=+6'],
[T('S')+'O<sub>4</sub><sup>2−</sup>','+6','O:−2×4、全体は−2 → S=+6'],
['N'+'H<sub>3</sub>…の'+T('N'),'−3','H:+1×3、全体0 → N=−3'],
['H'+T('N')+'O<sub>3</sub>','+5','H:+1, O:−2×3 → N=+5'],
[T('N')+'O<sub>2</sub>','+4','O:−2×2 → N=+4'],
[T('N')+'O','+2','O:−2 → N=+2'],
[T('N')+'<sub>2</sub>','0','単体の酸化数は0'],
['K'+T('Mn')+'O<sub>4</sub>','+7','K:+1, O:−2×4 → Mn=+7'],
[T('Mn')+'O<sub>2</sub>','+4','O:−2×2 → Mn=+4'],
[T('Mn')+'<sup>2+</sup>','+2','単原子イオンは電荷がそのまま酸化数'],
[T('Cr')+'<sub>2</sub>O<sub>7</sub><sup>2−</sup>','+6','O:−2×7、全体−2 → Cr2個で+12 → +6'],
['H<sub>2</sub>'+T('O')+'<sub>2</sub>','−1','過酸化水素のOは例外的に−1！'],
['Fe<sub>2</sub>'+T('O')+'<sub>3</sub>…のO','−2','化合物中のOはふつう−2'],
[T('Fe')+'<sub>2</sub>O<sub>3</sub>','+3','O:−2×3 → Fe2個で+6 → +3'],
[T('Fe')+'SO<sub>4</sub>','+2','SO<sub>4</sub><sup>2−</sup>とみて Fe=+2'],
[T('Cl')+'<sub>2</sub>','0','単体の酸化数は0'],
['H'+T('Cl')+'O','+1','次亜塩素酸。H:+1, O:−2 → Cl=+1'],
['K'+T('Cl')+'O<sub>3</sub>','+5','K:+1, O:−2×3 → Cl=+5'],
['H'+T('Cl')+'O<sub>4</sub>','+7','過塩素酸。Cl=+7(最高酸化数)'],
['Na'+T('H'),'−1','金属の水素化物ではHは例外的に−1！'],
[T('C')+'O<sub>2</sub>','+4','O:−2×2 → C=+4'],
[T('C')+'H<sub>4</sub>','−4','H:+1×4 → C=−4'],
['Cu<sub>2</sub>'+T('O')+'…のO','−2','Oは−2。ちなみにCuは+1。'],
[T('Cu')+'<sub>2</sub>O','+1','O:−2 → Cu2個で+2 → +1'],
];
const GAME=staticGame(DB.map(d=>({q:'オレンジ色の原子の酸化数は？<br>'+d[0],choices:CH,a:CH.indexOf(d[1]),ex:d[2]})));
"""
make("oxidation-number.html","酸化数バトル","酸化還元",
     "指定された原子(オレンジ色)の酸化数を素早く判定。連続正解でスコアが伸びる。",
     ["制限時間は90秒","単体は0、H:+1、O:−2が基本ルール","H<sub>2</sub>O<sub>2</sub>のOとNaHのHは例外！"],
     ox_js, 90, 4, "#c2607d")

print("done")
