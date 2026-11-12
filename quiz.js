/* クイズ型ゲームの本体。
   <body data-game="salt-judge"> を見て data/salt-judge.json を読み、画面をつくって動かす。
   問題の形は3通り:
     全問で同じ選択肢 … データに "choices"、問題は {q,a,ex}
     誤答をそのつど選ぶ … データに "pool"、問題は {q,a,ex}
     問題ごとの選択肢 … 問題は {q,a,w:[誤答…],ex}
   どれも a は正解の文字そのもの。 */
(function(){
  const game=document.body.dataset.game,app=CG.$('app');
  let D=null,deck=[];
  let score=0,combo=0,maxCombo=0,ok=0,total=0,tLeft=0,timer=null,cur=null,locked=false,lastSec=-1;

  fetch('data/'+game+'.json')
    .then(r=>{if(!r.ok)throw new Error('HTTP '+r.status);return r.json();})
    .then(init)
    .catch(()=>{
      app.innerHTML='<main class="game"><div class="panel" style="margin-top:20px">'
        +CG.mascot('問題のデータを読みこめなかった。通信を確かめて、もう一度ひらいてみて。')
        +'<a class="btn white" href="index.html">一覧へ</a></div></main>';
    });

  function init(d){
    D=d;document.body.dataset.u=d.color;
    app.innerHTML=
      '<header class="top"><a class="back" href="index.html" aria-label="一覧へ">‹</a>'
      +'<div class="ttl">'+d.title+'</div><span class="chip">'+d.unit+'</span></header>'
      +'<main class="game">'
      +'<section id="start" class="panel start pop"><h1>'+d.title+'</h1>'
        +CG.mascot(d.desc)
        +'<ul class="rules">'+d.rules.map(r=>'<li>'+r+'</li>').join('')+'</ul>'
        +'<button class="btn" id="go">スタート</button></section>'
      +'<section id="play" class="hidden">'
        +'<div class="hud"><div><span class="lb">TIME</span><b id="time"></b></div>'
        +'<div><span class="lb">SCORE</span><b id="score">0</b></div>'
        +'<div><span class="lb">COMBO</span><b id="combo">0</b></div></div>'
        +'<div class="tbar"><div class="tfill" id="tfill"></div></div>'
        +'<div class="panel q" id="qtext"></div>'
        +'<div class="choices" id="choices"></div>'
        +'<div class="fb" id="fb"></div></section>'
      +'<section id="end" class="panel res hidden">'
        +'<div class="lb">RESULT</div>'
        +'<div><div class="rank" id="rank"></div></div>'
        +'<div class="score" id="fscore">0</div>'
        +'<div class="bestline" id="best"></div>'
        +'<div class="stats"><div><span class="lb">正答</span><b id="facc"></b></div>'
        +'<div><span class="lb">最大コンボ</span><b id="fcombo"></b></div></div>'
        +'<div id="fmsg"></div>'
        +'<button class="btn" id="again">もう一度</button>'
        +'<a class="btn white" href="index.html">一覧へ</a></section>'
      +'</main>';
    app.querySelector('.top').appendChild(CG.soundButton());
    CG.$('go').onclick=startGame;
    CG.$('again').onclick=startGame;
    CG.$('choices').style.gridTemplateColumns='repeat('+d.cols+',1fr)';
  }

  // 1問ぶんの選択肢をつくる
  function nextItem(){
    if(!deck.length)deck=CG.shuffle(D.questions.slice());
    const x=deck.pop();
    let list;
    if(x.w)list=CG.shuffle([x.a].concat(x.w));
    else if(D.pool)list=CG.shuffle([x.a].concat(CG.shuffle(D.pool.filter(c=>c!==x.a)).slice(0,3)));
    else list=D.choices;
    return {q:x.q,choices:list,a:list.indexOf(x.a),ex:x.ex||''};
  }

  function startGame(){
    score=0;combo=0;maxCombo=0;ok=0;total=0;tLeft=D.limit;lastSec=-1;deck=[];
    CG.$('start').classList.add('hidden');CG.$('end').classList.add('hidden');CG.$('play').classList.remove('hidden');
    CG.sfx.tap();
    upd();nextQ();clearInterval(timer);
    timer=setInterval(()=>{tLeft-=0.1;if(tLeft<=0){tLeft=0;drawT();finish();return;}drawT();},100);
    drawT();window.scrollTo(0,0);
  }
  function drawT(){
    const s=Math.ceil(tLeft);
    CG.$('time').textContent=s;
    const f=CG.$('tfill');f.style.width=(tLeft/D.limit*100)+'%';f.classList.toggle('low',tLeft<=10);
    if(s<=5&&s>0&&s!==lastSec){lastSec=s;CG.sfx.tick();}
  }
  function upd(){CG.$('score').textContent=CG.fmt(score);CG.$('combo').textContent=combo;}
  function bump(id){const e=CG.$(id);e.classList.remove('bump');void e.offsetWidth;e.classList.add('bump');}
  function nextQ(){
    if(tLeft<=0)return;
    locked=false;CG.$('fb').innerHTML='';cur=nextItem();
    CG.$('qtext').innerHTML='<span>'+cur.q+'</span>';
    const c=CG.$('choices');c.innerHTML='';
    cur.choices.forEach((ch,i)=>{
      const b=document.createElement('button');b.className='choice';b.innerHTML=ch;
      b.onclick=()=>answer(i,b);c.appendChild(b);
    });
  }
  function answer(i,btn){
    if(locked)return;locked=true;total++;
    const bs=CG.$('choices').children;
    bs[cur.a].classList.add('correct');
    if(i===cur.a){
      ok++;combo++;maxCombo=Math.max(maxCombo,combo);score+=100+Math.min(combo,10)*10;
      CG.sfx.ok(combo);bump('score');if(combo>=2)bump('combo');
      CG.$('fb').innerHTML='<b class="good">正解！</b>'+cur.ex;setTimeout(nextQ,750);
    }else{
      btn.classList.add('wrong');combo=0;CG.sfx.ng();
      CG.$('fb').innerHTML='<b class="bad">おしい！</b>'+cur.ex;setTimeout(nextQ,1700);
    }
    upd();
  }
  // ランクは1分あたりの得点で決める
  function rankOf(){
    const p=score/(D.limit/60);
    return p>=2400?'S':p>=1500?'A':p>=800?'B':'C';
  }
  const MSG={
    S:'かんぺき！ この単元はまかせた。',
    A:'いい調子。あと少しで S ランクだ。',
    B:'まずまず。解説を読みながら、もう1回！',
    C:'だいじょうぶ。解説がヒントになる。もう1回やってみよう。'
  };
  function finish(){
    clearInterval(timer);locked=true;
    CG.$('play').classList.add('hidden');
    const end=CG.$('end');end.classList.remove('hidden');end.classList.remove('pop');void end.offsetWidth;end.classList.add('pop');
    const r=rankOf(),rk=CG.$('rank');
    rk.textContent=r;rk.className='rank num r-'+r.toLowerCase();
    CG.countUp(CG.$('fscore'),score);
    CG.$('facc').textContent=ok+' / '+total;
    CG.$('fcombo').textContent='×'+maxCombo;
    const b=CG.best(game,score),bl=CG.$('best');
    if(!b.ok)bl.innerHTML='';
    else if(b.first)bl.innerHTML='<span>はじめての記録</span>';
    else if(b.isNew)bl.innerHTML='<span class="new">NEW BEST</span>';
    else bl.innerHTML='<span>自己ベスト '+CG.fmt(b.prev)+'</span>';
    CG.$('fmsg').innerHTML=CG.mascot(MSG[r]);
    CG.sfx.fin();window.scrollTo(0,0);
  }
  // パソコンでは数字キーでも答えられる
  document.addEventListener('keydown',e=>{
    if(locked||!cur||CG.$('play').classList.contains('hidden'))return;
    const n=parseInt(e.key,10);
    if(n>=1&&n<=cur.choices.length){const b=CG.$('choices').children[n-1];if(b)b.click();}
  });
})();
