/* 化学ゲームラボ 共通の部品。各ページの変数名とぶつからないよう CG にまとめる */
const CG=(function(){
  const PRE='chemgames:';
  const $=id=>document.getElementById(id);
  function shuffle(a){for(let i=a.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[a[i],a[j]]=[a[j],a[i]];}return a;}
  function pick(a){return a[Math.floor(Math.random()*a.length)];}
  const fmt=n=>Number(n).toLocaleString('en-US');

  // ---- localStorage(保存できない環境では何もしない) ----
  function load(key){try{return localStorage.getItem(PRE+key);}catch(e){return null;}}
  function save(key,v){try{localStorage.setItem(PRE+key,String(v));return true;}catch(e){return false;}}

  // 自己ベスト。ok=false なら保存が使えない環境
  function best(game,score,sub){
    const key=game+':best'+(sub?':'+sub:'');
    let prev=null,ok=true;
    try{
      const v=parseInt(localStorage.getItem(PRE+key),10);if(isFinite(v))prev=v;
      if(prev===null||score>prev)localStorage.setItem(PRE+key,String(score));
    }catch(e){ok=false;}
    return {ok:ok,prev:prev,first:ok&&prev===null,isNew:ok&&prev!==null&&score>prev};
  }

  // ---- 効果音(Web Audio。最初の操作で初期化) ----
  let ac=null,muted=load('mute')==='1';
  function ctx(){if(!ac){try{ac=new (window.AudioContext||window.webkitAudioContext)();}catch(e){ac=null;}}return ac;}
  function tone(f,d,type,g0,at){
    if(muted)return;const c=ctx();if(!c)return;
    const t=c.currentTime+(at||0),o=c.createOscillator(),g=c.createGain();
    o.type=type||'square';o.frequency.value=f;
    g.gain.setValueAtTime(g0||0.05,t);g.gain.exponentialRampToValueAtTime(0.0001,t+d);
    o.connect(g);g.connect(c.destination);o.start(t);o.stop(t+d);
  }
  const sfx={
    tap(){tone(520,0.05,'square',0.03);},
    ok(n){const b=660+Math.min(n||0,10)*28;tone(b,0.09,'triangle',0.07);tone(b*1.5,0.14,'triangle',0.06,0.07);},
    ng(){tone(190,0.16,'sawtooth',0.05);tone(140,0.2,'sawtooth',0.05,0.1);},
    tick(){tone(900,0.04,'square',0.03);},
    fin(){[523,659,784,1047].forEach((f,i)=>tone(f,0.16,'triangle',0.07,i*0.1));}
  };
  function isMuted(){return muted;}
  function setMuted(m){muted=!!m;save('mute',muted?'1':'0');}
  // 音のON/OFFボタンをつくる
  function soundButton(){
    const b=document.createElement('button');
    b.className='snd'+(muted?' off':'');b.textContent='♪';b.title='音';
    b.setAttribute('aria-label','音のオン・オフ');
    b.onclick=()=>{setMuted(!muted);b.classList.toggle('off',muted);if(!muted)sfx.tap();};
    return b;
  }

  // 数字が 0 から数え上がる
  function countUp(el,to,ms){
    const t0=performance.now(),dur=ms||900;
    (function step(t){
      const k=Math.min(1,(t-t0)/dur),e=1-Math.pow(1-k,3);
      el.textContent=fmt(Math.round(to*e));
      if(k<1)requestAnimationFrame(step);
    })(t0);
  }

  // 説明役のキャラクターと吹き出し
  function mascot(html){
    return '<div class="mascot"><img src="img/gorilla.png" alt="" width="84" height="84">'
      +'<div class="bubble">'+html+'</div></div>';
  }

  return {$:$,shuffle:shuffle,pick:pick,fmt:fmt,load:load,save:save,best:best,sfx:sfx,
          isMuted:isMuted,setMuted:setMuted,soundButton:soundButton,countUp:countUp,mascot:mascot,PRE:PRE};
})();
