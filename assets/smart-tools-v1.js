/* Pallet Tools smart production helpers v1.1.16 */
(function(){
  'use strict';
  const $=id=>document.getElementById(id);
  const val=(id,d=0)=>{const x=Number($(id)?.value);return Number.isFinite(x)?x:d;};
  const fmt=v=>{const x=Math.round(Number(v||0)*10)/10;return Number.isInteger(x)?String(x):x.toFixed(1).replace('.',',');};
  const fmt3=v=>(Math.round(Number(v||0)*1000)/1000).toLocaleString('ru-RU',{minimumFractionDigits:3,maximumFractionDigits:3});
  let selectedPart=null;

  function deckState(){
    const W=Math.max(0,val('pW')),L=Math.max(0,val('pL'));
    const n=Math.max(0,Math.round(val('n0'))),t=Math.max(0,val('t0')),w=Math.max(0,val('w0')),l=Math.max(0,val('l0'));
    const remaining=W-n*w;
    const gap=n>1?remaining/(n-1):0;
    return {W,L,n,t,w,l,remaining,gap};
  }

  function suggestion(){
    const s=deckState();
    if(!s.W)return null;
    const currentN=Math.max(3,s.n||6),currentW=Math.max(1,s.w||98);
    const maxN=Math.max(3,Math.min(12,Number($('n0')?.max)||12));
    const widths=[currentW,75,80,90,95,98,100,110,120,145,150].filter(x=>x>0&&x<s.W);
    const unique=[...new Set(widths.map(x=>Math.round(x*10)/10))];
    let best=null;
    for(let n=3;n<=maxN;n++){
      for(const w of unique){
        const remaining=s.W-n*w;if(remaining<0)continue;
        const gap=n>1?remaining/(n-1):0;
        const working=gap>=15&&gap<=80;
        const score=(working?0:1000)+Math.abs(gap-25)*1.6+Math.abs(w-currentW)*.08+Math.abs(n-currentN)*.6;
        if(!best||score<best.score)best={n,w,gap,remaining,score,working};
      }
    }
    return best;
  }

  function constructionChecks(){
    const s=deckState(),items=[];
    const push=(level,text)=>items.push({level,text});
    if(s.n<2)push('bad','Для настила задано меньше двух досок.');
    if(s.n>1){
      if(s.gap<0)push('bad',`Доски не помещаются: не хватает ${fmt(Math.abs(s.remaining))} мм.`);
      else if(s.gap<10)push('warn',`Малый зазор между досками: ${fmt(s.gap)} мм.`);
      else if(s.gap>100)push('warn',`Большой зазор между досками: ${fmt(s.gap)} мм.`);
      else push('ok',`Зазор настила: ${fmt(s.gap)} мм.`);
    }
    if(s.t>0&&s.t<15)push('warn',`Толщина настила ${fmt(s.t)} мм — проверьте конструкцию.`);
    if(s.w>0&&(s.w<50||s.w>200))push('warn',`Ширина настила ${fmt(s.w)} мм выглядит нетипично.`);
    if(s.L&&s.l&&Math.abs(s.L-s.l)>2)push('warn',`Длина настила ${fmt(s.l)} мм не совпадает с длиной поддона ${fmt(s.L)} мм.`);
    for(let i=0;i<7;i++){
      const n=Math.max(0,Math.round(val('n'+i))),t=val('t'+i),w=val('w'+i),l=val('l'+i);
      if(n>0&&(t<=0||w<=0||l<=0))push('bad',`У детали №${i+1} есть количество, но не заполнены все размеры.`);
    }
    if(!items.some(x=>x.level==='bad'||x.level==='warn'))push('ok','Критичных несоответствий в текущих размерах не найдено.');
    return items;
  }

  function volumeStats(){
    let per=0;
    for(let i=0;i<7;i++){
      const n=Math.max(0,Math.round(val('n'+i))),t=Math.max(0,val('t'+i)),w=Math.max(0,val('w'+i)),l=Math.max(0,val('l'+i));
      per+=n*t*w*l/1e9;
    }
    const qty=Math.max(1,Math.round(val('qty',1)));
    const density=Math.max(250,Math.min(1000,val('smartDensity',500)||500));
    return {per,batch:per*qty,weight:per*density,batchWeight:per*qty*density,qty,density};
  }

  function ensurePanel(){
    let panel=$('smartToolsPanel');if(panel)return panel;
    const calc=$('calculator');if(!calc)return null;
    panel=document.createElement('section');
    panel.id='smartToolsPanel';panel.className='smartToolsPanel';panel.dataset.appScreen='calculator';panel.hidden=calc.hidden;
    panel.innerHTML=`
      <div class="smartToolsHead"><div><span>УМНЫЕ ИНСТРУМЕНТЫ</span><h2>Проверка и оптимизация поддона</h2><p>Четыре помощника работают по текущим размерам и обновляются автоматически.</p></div></div>
      <div class="smartToolsGrid">
        <article class="smartToolCard optimizer"><div class="smartToolIcon">◎</div><div class="smartToolBody"><small>1 · ОПТИМИЗАТОР НАСТИЛА</small><h3 id="smartOptimizeMain">Расчёт…</h3><p id="smartOptimizeSub">Подбираем количество, ширину и равномерный зазор.</p><button id="smartOptimizeApply" type="button">Применить вариант</button></div></article>
        <article class="smartToolCard checker"><div class="smartToolIcon">✓</div><div class="smartToolBody"><small>2 · ПРОВЕРКА КОНСТРУКЦИИ</small><div class="smartCheckStatus" id="smartCheckStatus">Проверка…</div><div class="smartCheckList" id="smartCheckList"></div></div></article>
        <article class="smartToolCard selected"><div class="smartToolIcon">◇</div><div class="smartToolBody"><small>3 · ДЕТАЛЬ ИЗ МОДЕЛИ</small><h3 id="smartSelectedTitle">Выберите деталь</h3><p id="smartSelectedDims">Можно выбрать настил, поперечину, лыжу или шашку.</p><div class="smartSelectedQty" id="smartSelectedQty">Размеры и количество появятся здесь.</div><button class="smartSelect3D" id="smartSelect3D" type="button">Показать модель и выбрать деталь</button></div></article>
        <article class="smartToolCard material"><div class="smartToolIcon">m³</div><div class="smartToolBody"><small>4 · ДРЕВЕСИНА И ВЕС</small><div class="smartDensity"><label for="smartDensity">Плотность древесины, кг/м³</label><input id="smartDensity" type="number" min="250" max="1000" step="10" value="500"></div><div class="smartMetrics"><div><span>На 1 поддон</span><b id="smartM3Per">0,000 м³</b></div><div><span>На заказ</span><b id="smartM3Batch">0,000 м³</b></div><div><span>Вес 1 поддона</span><b id="smartWeightPer">0 кг</b></div><div><span>Вес древесины заказа</span><b id="smartWeightBatch">0 кг</b></div></div></div></article>
      </div>`;
    calc.insertAdjacentElement('afterend',panel);
    try{const saved=Number(localStorage.getItem('pallettools:woodDensity'));if(saved>=250&&saved<=1000)$('smartDensity').value=String(saved);}catch(_){}
    $('smartOptimizeApply')?.addEventListener('click',applySuggestion);
    $('smartDensity')?.addEventListener('input',()=>{try{localStorage.setItem('pallettools:woodDensity',$('smartDensity').value);}catch(_){}update();});
    $('smartSelect3D')?.addEventListener('click',()=>{
      const preview=$('palletPreview3D')?.closest('.previewCard');
      const active=$('palletPreview3D')?.querySelector('[data-p3d-mode].active');
      if(!active||active.dataset.p3dMode==='3d')$('palletPreview3D')?.querySelector('[data-p3d-mode="top"]')?.click();
      setTimeout(()=>{
        const livePreview=$('palletPreview3D')?.closest('.previewCard')||preview;
        livePreview?.classList.add('partPickMode');
        livePreview?.scrollIntoView({behavior:'smooth',block:'center'});
        const hint=document.querySelector('.palletPickHint');
        if(hint){hint.hidden=false;hint.textContent='Режим выбора: нажмите на подсвеченную деталь';hint.classList.add('attention');}
        setTimeout(()=>hint?.classList.remove('attention'),2600);
      },90);
    });
    return panel;
  }

  function applySuggestion(){
    const best=suggestion();if(!best)return;
    const values={n0:best.n,w0:best.w,l0:Math.round(val('pL'))};
    Object.entries(values).forEach(([id,v])=>{const input=$(id);if(!input)return;input.value=String(v);input.dispatchEvent(new Event('input',{bubbles:true}));input.dispatchEvent(new Event('change',{bubbles:true}));});
    if(typeof window.rerenderPallet3D==='function')setTimeout(()=>window.rerenderPallet3D(),30);
    update();
  }

  function renderSelected(){
    const title=$('smartSelectedTitle'),dims=$('smartSelectedDims'),qty=$('smartSelectedQty');if(!title||!dims||!qty)return;
    if(!selectedPart){title.textContent='Выберите деталь';dims.textContent='Нажмите кнопку ниже. Выбор доступен в режимах «Сверху», «Сбоку» и «Разнести».';qty.textContent='Настил, поперечина, лыжа или шашка подсветится, а размеры появятся здесь.';return;}
    title.textContent=`${selectedPart.name} №${selectedPart.itemNo||selectedPart.boardNo||1}`;
    dims.textContent=`${fmt(selectedPart.t)} × ${fmt(selectedPart.w)} × ${fmt(selectedPart.l)} мм`;
    const weightOne=Number(selectedPart.pieceWeightKg||0),weightOrder=Number(selectedPart.orderWeightKg||0);
    const weightText=weightOne>0?` · вес 1 шт. ${fmt(weightOne)} кг · заказ ${Math.round(weightOrder).toLocaleString('ru-RU')} кг`:'';
    qty.textContent=`${selectedPart.per} шт. на поддон · ${Number(selectedPart.total||0).toLocaleString('ru-RU')} шт. на заказ${weightText}`;
  }

  function update(){
    if(!ensurePanel())return;
    const best=suggestion(),main=$('smartOptimizeMain'),sub=$('smartOptimizeSub'),apply=$('smartOptimizeApply');
    if(best){main.textContent=`${best.n} досок × ${fmt(best.w)} мм`;sub.textContent=`Равномерный зазор ${fmt(best.gap)} мм · остаток по ширине ${fmt(best.remaining)} мм`;if(apply)apply.disabled=false;}
    else{main.textContent='Нет подходящего варианта';sub.textContent='Проверьте ширину поддона и размеры настила.';if(apply)apply.disabled=true;}

    const checks=constructionChecks(),bad=checks.filter(x=>x.level==='bad').length,warn=checks.filter(x=>x.level==='warn').length,status=$('smartCheckStatus'),list=$('smartCheckList');
    if(status){status.className='smartCheckStatus '+(bad?'bad':warn?'warn':'ok');status.textContent=bad?`Ошибок: ${bad}`:warn?`Нужно проверить: ${warn}`:'Размеры согласованы';}
    if(list)list.innerHTML=checks.slice(0,5).map(x=>`<div class="smartCheckItem ${x.level}"><i>${x.level==='bad'?'!':x.level==='warn'?'△':'✓'}</i><span>${x.text}</span></div>`).join('');

    const v=volumeStats();
    if($('smartM3Per'))$('smartM3Per').textContent=`${fmt3(v.per)} м³`;
    if($('smartM3Batch'))$('smartM3Batch').textContent=`${fmt3(v.batch)} м³`;
    if($('smartWeightPer'))$('smartWeightPer').textContent=`${fmt(v.weight)} кг`;
    if($('smartWeightBatch'))$('smartWeightBatch').textContent=`${Math.round(v.batchWeight).toLocaleString('ru-RU')} кг`;
    renderSelected();
  }

  function init(){
    if(!ensurePanel())return;
    document.addEventListener('input',e=>{if(e.target?.id&&/^(pL|pW|qty|n[0-6]|t[0-6]|w[0-6]|l[0-6])$/.test(e.target.id))requestAnimationFrame(update);});
    document.addEventListener('change',e=>{if(e.target?.id&&/^(pL|pW|qty|n[0-6]|t[0-6]|w[0-6]|l[0-6])$/.test(e.target.id))requestAnimationFrame(update);});
    window.addEventListener('pallet3d:partselect',e=>{selectedPart=e.detail||null;document.querySelector('.previewCard')?.classList.remove('partPickMode');document.querySelector('.palletPickHint')?.classList.remove('attention');const card=$('smartSelectedTitle')?.closest('.smartToolCard');card?.classList.add('hasSelection');renderSelected();});
    update();
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});else init();
})();
