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

  // ---- BGM(sound/<名前>-bgm.ogg を継ぎ目なくループ。予備に .m4a) ----
  // 呼んだページだけで動く(読みこみ時には何もしない)。AudioContext はゲーム側のものを使う。
  //   const bgm=CG.bgm({ctx:ac, name:'sound/formula-tower-bgm', len:27.429, vol:.22});
  //   bgm.load()            … 最初のユーザー操作の中で呼ぶ(読みこみ・デコード。読めた時点で条件がそろえば鳴る)
  //   bgm.screen(on,fromTop)… 画面の切りかえで「この画面で流すか」。fromTop=true で頭から
  //   bgm.setOn(on)         … ON/OFF(ミュートボタンなど。保存はゲーム側で)
  //   bgm.hold(sec)         … sec 秒だけ止めて続きから(お手本の再生など)
  //   bgm.duck(sec,k)       … sec 秒だけ音量を k 倍に下げる(ジングルを聞かせる)
  //   bgm.playing() / bgm.fade / bgm.state('idle'|'loading'|'ready'|'failed')
  // 読みこめない・デコードできないときは何も鳴らさないだけで、ゲームは普通に動く。
  // タブが裏に回ると止まり、戻ると続きから鳴る。
  function bgm(o){
    const len=o.len,vol=o.vol==null?.25:o.vol,fade=o.fade==null?.4:o.fade;
    let buf=null,loopStart=0,loopEnd=0,want=o.want!==false,on=o.on!==false,
        hold=false,holdT=0,src=null,g=null,duckG=null,lvG=null,level=1,t0=0,pos=0;
    const B={state:'idle',fmt:'',fade:fade};
    function decode(c,ab){ // 古い Safari は Promise を返さないのでコールバックで包む
      return new Promise((ok,ng)=>{
        try{const p=c.decodeAudioData(ab,ok,ng);if(p&&p.then)p.then(ok,ng);}catch(e){ng(e);}
      });
    }
    function get(c,ext){
      return fetch(o.name+'.'+ext)
        .then(r=>{if(!r.ok)throw new Error(r.status);return r.arrayBuffer();})
        .then(ab=>decode(c,ab));
    }
    B.load=function(){
      if(B.state!=='idle')return;
      let c=null;try{c=o.ctx();}catch(e){}
      if(!c||!window.fetch||!window.Promise){B.state='failed';return;}
      B.state='loading';
      get(c,'ogg').then(b=>{B.fmt='ogg';return b;},
        ()=>get(c,'m4a').then(b=>{B.fmt='m4a';return b;}))
      .then(b=>{
        buf=b;
        // AAC は先頭にエンコーダの無音(priming)が入ることがある。最初に音が出る位置からループさせる
        loopStart=0;loopEnd=Math.min(b.duration,len);
        if(B.fmt==='m4a'&&b.duration>len+.002){
          const n=Math.floor((b.duration-len)*b.sampleRate);
          let i=0;
          search:for(;i<n;i++)for(let ch=0;ch<b.numberOfChannels;ch++)
            if(Math.abs(b.getChannelData(ch)[i])>.003)break search;
          loopStart=i/b.sampleRate;loopEnd=Math.min(b.duration,loopStart+len);
        }
        B.state='ready';update();
      }).catch(()=>{B.state='failed';});
    };
    function can(){return B.state==='ready'&&want&&!hold&&on&&!document.hidden;}
    function update(){ // いまの状態に合わせて鳴らす・止める
      if(B.state!=='ready')return;
      try{
        if(can()){if(!src)start();}
        else if(src)stop();
      }catch(e){}
    }
    function start(){
      const c=o.ctx();if(!c)return;
      if(c.state==='suspended'&&c.resume)c.resume();
      if(!duckG){ // 音量(setVol) → ダッキング(duck) → スピーカー
        lvG=c.createGain();lvG.gain.value=level;lvG.connect(c.destination);
        duckG=c.createGain();duckG.connect(lvG);
      }
      const t=c.currentTime,s=c.createBufferSource(),gg=c.createGain();
      s.buffer=buf;s.loop=true;s.loopStart=loopStart;s.loopEnd=loopEnd;
      gg.gain.setValueAtTime(0,t);gg.gain.linearRampToValueAtTime(vol,t+fade);
      s.connect(gg);gg.connect(duckG);
      s.start(t,loopStart+pos);
      src=s;g=gg;t0=t-pos;
    }
    function stop(){
      const c=o.ctx(),t=c.currentTime,s=src,gg=g;
      pos=((t-t0)%len+len)%len; // 続きから再開できるように位置を覚える
      gg.gain.cancelScheduledValues(t);gg.gain.setValueAtTime(gg.gain.value,t);
      gg.gain.linearRampToValueAtTime(0,t+fade);
      try{s.stop(t+fade+.05);}catch(e){}
      setTimeout(()=>{try{s.disconnect();gg.disconnect();}catch(e){}},(fade+.2)*1000);
      src=null;g=null;
    }
    B.screen=function(v,fromTop){
      want=!!v;
      if(fromTop){if(src)stop();pos=0;}
      clearTimeout(holdT);hold=false;
      update();
    };
    B.setOn=function(v){on=!!v;update();};
    B.isOn=function(){return on;};
    B.setVol=function(k){ // 音量の倍率(1 = ゲームが決めた vol)。なめらかに変える
      level=Math.max(0,+k||0);
      if(lvG){try{const c=o.ctx();lvG.gain.setTargetAtTime(level,c.currentTime,.04);}catch(e){}}
    };
    B.hold=function(sec){
      if(!want)return;
      hold=true;update();
      clearTimeout(holdT);
      holdT=setTimeout(()=>{hold=false;update();},sec*1000);
    };
    B.duck=function(sec,k){
      if(!duckG)return;
      try{
        const c=o.ctx(),t=c.currentTime,p=duckG.gain;
        p.cancelScheduledValues(t);p.setValueAtTime(p.value,t);
        p.linearRampToValueAtTime(k==null?.25:k,t+.08);
        p.setValueAtTime(k==null?.25:k,t+sec);
        p.linearRampToValueAtTime(1,t+sec+.6);
      }catch(e){}
    };
    B.playing=function(){return !!src;};
    B.gain=function(){return g?g.gain.value*(duckG?duckG.gain.value:1)*(lvG?lvG.gain.value:1):0;}; // 確認用
    document.addEventListener('visibilitychange',update);
    return B;
  }

  // ---- 音量パネル(BGM と効果音を別々に。上の帯の音ボタンから開く) ----
  //   const vp=CG.volumePanel({game:'formula-tower',
  //     bgm:{max:1.6}, sfx:{max:1.6, min:0, note:''},
  //     onChange:v=>{ v.bgm / v.sfx は音量の倍率(0=消す、1=ゲームの元の音量) },
  //     sample:()=>{ 効果音の見本を1回鳴らす }, onOpen:()=>{ 最初の操作で音を準備するなど }});
  //   document.querySelector('.top').appendChild(vp.button);
  // スライダーは 0〜100。60 が元の音量(倍率1)、100 で max 倍。sfx.min を付けるとそれより下げられない(OFF も出さない)。
  // 保存は chemgames:<game>:vol に {bgm,sfx,bgmOn,sfxOn}。init で旧設定を渡せる(なければ既定)。
  // 読みこみ時には何もしない。onChange は作った直後に1回呼ぶ。
  function volumePanel(o){
    const DEF=60,key=o.game+':vol',bc=o.bgm||{},sc=o.sfx||{},sMin=sc.min||0;
    let st={bgm:DEF,sfx:DEF,bgmOn:true,sfxOn:true};
    if(o.init)for(const k in o.init)st[k]=o.init[k];
    try{const v=JSON.parse(load(key)||'null');if(v&&typeof v==='object')for(const k in st)if(k in v)st[k]=v[k];}catch(e){}
    const num=(x,d)=>{x=+x;return isFinite(x)?Math.max(0,Math.min(100,Math.round(x))):d;};
    st.bgm=num(st.bgm,DEF);st.sfx=Math.max(sMin,num(st.sfx,DEF));st.bgmOn=st.bgmOn!==false;
    st.sfxOn=sMin>0?true:st.sfxOn!==false;
    const mul=(v,max)=>v<=DEF?v/DEF:1+(v-DEF)/(100-DEF)*((max||1.6)-1);
    function vals(){
      return {bgm:st.bgmOn?mul(st.bgm,bc.max):0,sfx:st.sfxOn?mul(st.sfx,sc.max):0};
    }
    function fire(){try{o.onChange&&o.onChange(vals());}catch(e){}}

    const btn=document.createElement('button');
    btn.type='button';btn.className='snd cgvol-btn';btn.textContent='♪';btn.title='音量';
    btn.setAttribute('aria-label','音量の調整');btn.setAttribute('aria-haspopup','dialog');btn.setAttribute('aria-expanded','false');
    const pn=document.createElement('div');
    pn.className='cgvol';pn.hidden=true;pn.setAttribute('role','dialog');pn.setAttribute('aria-label','音量');
    pn.innerHTML='<div class="cgvol-hd"><span>音量</span><button type="button" class="cgvol-x" aria-label="閉じる">✕</button></div>'
      +row('bgm','BGM')+row('sfx','効果音')
      +(sc.note?'<p class="cgvol-note">'+sc.note+'</p>':'');
    function row(k,lb){
      return '<div class="cgvol-row"><span class="cgvol-lb">'+lb+'</span>'
        +'<button type="button" class="cgvol-tg" data-k="'+k+'" aria-label="'+lb+'のオン・オフ">♪</button>'
        +'<input type="range" class="cgvol-rg" data-k="'+k+'" min="'+(k==='sfx'?sMin:0)+'" max="100" step="1" aria-label="'+lb+'の音量">'
        +'<span class="cgvol-v num" data-k="'+k+'"></span></div>';
    }
    const q=(c,k)=>pn.querySelector('.'+c+'[data-k="'+k+'"]');
    function draw(){
      ['bgm','sfx'].forEach(k=>{
        const on=st[k+'On']&&st[k]>0,r=q('cgvol-rg',k),t=q('cgvol-tg',k);
        r.value=st[k];r.style.setProperty('--p',((st[k]-r.min)/(100-r.min)*100)+'%');
        r.setAttribute('aria-valuetext',on?st[k]+'%':'オフ');
        q('cgvol-v',k).textContent=on?st[k]+'%':'OFF';
        t.classList.toggle('off',!on);t.setAttribute('aria-pressed',String(on));
        if(k==='sfx'&&sMin>0){t.disabled=true;t.title='リズムの音は消せません';}
      });
      btn.classList.toggle('off',!(st.bgmOn&&st.bgm>0)&&!(st.sfxOn&&st.sfx>0));
    }
    function store(){save(key,JSON.stringify(st));}
    pn.addEventListener('input',e=>{
      const k=e.target.dataset&&e.target.dataset.k;if(!k||!e.target.classList.contains('cgvol-rg'))return;
      st[k]=num(e.target.value,DEF);if(st[k]>0)st[k+'On']=true;
      draw();fire();store();
    });
    pn.addEventListener('change',e=>{ // 指をはなしたら効果音の見本
      if(e.target.dataset&&e.target.dataset.k==='sfx'&&o.sample)try{o.sample();}catch(err){}
    });
    pn.addEventListener('click',e=>{
      const t=e.target.closest&&e.target.closest('.cgvol-tg,.cgvol-x');if(!t)return;
      if(t.classList.contains('cgvol-x')){close();return;}
      const k=t.dataset.k;
      if(st[k]===0){st[k]=DEF;st[k+'On']=true;}else st[k+'On']=!st[k+'On'];
      draw();fire();store();
      if(k==='sfx'&&st.sfxOn&&o.sample)try{o.sample();}catch(err){}
    });
    function place(){
      const r=btn.getBoundingClientRect();
      pn.style.top=Math.round(r.bottom+10)+'px';
      pn.style.right=Math.max(10,Math.round(window.innerWidth-r.right))+'px';
    }
    function open(){
      if(!pn.parentNode)document.body.appendChild(pn);
      place();pn.hidden=false;btn.setAttribute('aria-expanded','true');
      try{o.onOpen&&o.onOpen();}catch(e){}
      document.addEventListener('pointerdown',outside,true);
      document.addEventListener('keydown',esc);
    }
    function close(){
      pn.hidden=true;btn.setAttribute('aria-expanded','false');
      document.removeEventListener('pointerdown',outside,true);
      document.removeEventListener('keydown',esc);
    }
    function outside(e){if(!pn.contains(e.target)&&!btn.contains(e.target))close();}
    function esc(e){if(e.key==='Escape')close();}
    btn.onclick=()=>{pn.hidden?open():close();};
    draw();fire();
    return {button:btn,panel:pn,open:open,close:close,values:vals,state:()=>Object.assign({},st)};
  }

  return {$:$,shuffle:shuffle,pick:pick,fmt:fmt,load:load,save:save,best:best,sfx:sfx,
          isMuted:isMuted,setMuted:setMuted,soundButton:soundButton,countUp:countUp,mascot:mascot,PRE:PRE,
          bgm:bgm,volumePanel:volumePanel};
})();
