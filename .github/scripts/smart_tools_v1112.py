from pathlib import Path
import re

html_path=Path('index.html')
css_path=Path('assets/theme-industrial-v130.css')
p3d_path=Path('assets/pallet3d-v10.js')
smart_path=Path('assets/smart-tools-v1.js')

html=html_path.read_text(encoding='utf-8')
css=css_path.read_text(encoding='utf-8')
p3d=p3d_path.read_text(encoding='utf-8')

smart_js=r'''/* Pallet Tools smart production helpers v1.1.12 */
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
        <article class="smartToolCard selected"><div class="smartToolIcon">◇</div><div class="smartToolBody"><small>3 · ДЕТАЛЬ ИЗ 3D</small><h3 id="smartSelectedTitle">Выберите доску</h3><p id="smartSelectedDims">Нажмите на верхнюю доску прямо на 3D-модели.</p><div class="smartSelectedQty" id="smartSelectedQty">Размеры и количество появятся здесь.</div></div></article>
        <article class="smartToolCard material"><div class="smartToolIcon">m³</div><div class="smartToolBody"><small>4 · ДРЕВЕСИНА И ВЕС</small><div class="smartDensity"><label for="smartDensity">Плотность древесины, кг/м³</label><input id="smartDensity" type="number" min="250" max="1000" step="10" value="500"></div><div class="smartMetrics"><div><span>На 1 поддон</span><b id="smartM3Per">0,000 м³</b></div><div><span>На заказ</span><b id="smartM3Batch">0,000 м³</b></div><div><span>Вес 1 поддона</span><b id="smartWeightPer">0 кг</b></div><div><span>Вес древесины заказа</span><b id="smartWeightBatch">0 кг</b></div></div></div></article>
      </div>`;
    calc.insertAdjacentElement('afterend',panel);
    try{const saved=Number(localStorage.getItem('pallettools:woodDensity'));if(saved>=250&&saved<=1000)$('smartDensity').value=String(saved);}catch(_){}
    $('smartOptimizeApply')?.addEventListener('click',applySuggestion);
    $('smartDensity')?.addEventListener('input',()=>{try{localStorage.setItem('pallettools:woodDensity',$('smartDensity').value);}catch(_){}update();});
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
    if(!selectedPart){title.textContent='Выберите доску';dims.textContent='Нажмите на верхнюю доску прямо на 3D-модели.';qty.textContent='Размеры и количество появятся здесь.';return;}
    title.textContent=`${selectedPart.name} №${selectedPart.boardNo}`;
    dims.textContent=`${fmt(selectedPart.t)} × ${fmt(selectedPart.w)} × ${fmt(selectedPart.l)} мм`;
    qty.textContent=`${selectedPart.per} шт. на поддон · ${Number(selectedPart.total||0).toLocaleString('ru-RU')} шт. на заказ`;
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
    window.addEventListener('pallet3d:partselect',e=>{selectedPart=e.detail||null;renderSelected();});
    update();
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});else init();
})();
'''
smart_path.write_text(smart_js,encoding='utf-8')

if 'assets/smart-tools-v1.js' not in html:
    m=re.search(r'(<script src="assets/pallet3d-v10\.js\?v=\d+"></script>)',html)
    if not m: raise SystemExit('pallet3d script marker not found')
    html=html[:m.end()]+"\n<script src=\"assets/smart-tools-v1.js?v=1\"></script>"+html[m.end():]
for pattern in [r'assets/theme-industrial-v130\.css\?v=(\d+)',r'assets/pallet3d-v10\.js\?v=(\d+)']:
    m=re.search(pattern,html)
    if not m: raise SystemExit('cache marker missing '+pattern)
    html=html[:m.start(1)]+str(int(m.group(1))+1)+html[m.end(1):]
html=html.replace('Pallet Tools · v1.1.11','Pallet Tools · v1.1.12')
html_path.write_text(html,encoding='utf-8')

css=css.replace('Pallet Tools · v1.1.11','Pallet Tools · v1.1.12').replace('обновление №345','обновление №346')
if 'smartToolsCssV1112' not in css:
    css+=r'''

/* smartToolsCssV1112 */
.smartToolsPanel{margin:14px 0 20px;padding:18px;border:1px solid #dfddd7;border-radius:20px;background:linear-gradient(180deg,#fff,#faf9f6);box-shadow:0 8px 24px rgba(35,40,43,.055)}
.smartToolsHead{display:flex;align-items:flex-end;justify-content:space-between;gap:12px;margin-bottom:13px}.smartToolsHead span{display:block;color:#9a642f;font-size:10px;font-weight:900;letter-spacing:.12em}.smartToolsHead h2{margin:3px 0 2px;font-size:22px;color:#252b2e}.smartToolsHead p{margin:0;color:#777e7b;font-size:12px}
.smartToolsGrid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}.smartToolCard{display:flex;gap:12px;min-width:0;padding:15px;border:1px solid #e4e0d9;border-radius:16px;background:#fff}.smartToolIcon{display:grid;place-items:center;flex:0 0 40px;width:40px;height:40px;border-radius:12px;background:#f3e8db;color:#8b592d;font-size:16px;font-weight:900}.smartToolBody{min-width:0;flex:1}.smartToolBody>small{display:block;color:#8b918e;font-size:9px;font-weight:900;letter-spacing:.08em}.smartToolBody h3{margin:6px 0 3px;color:#303638;font-size:18px}.smartToolBody p{margin:0;color:#747b78;font-size:11px;line-height:1.45}.smartToolBody button{margin-top:11px;min-height:38px;padding:0 12px;border:1px solid #b8793d;border-radius:10px;background:#b8793d;color:#fff;font-size:11px;font-weight:850}.smartToolBody button:disabled{opacity:.45;cursor:not-allowed}
.smartCheckStatus{display:inline-flex;margin:7px 0 8px;padding:5px 8px;border-radius:999px;font-size:10px;font-weight:900}.smartCheckStatus.ok{background:#e7f3ec;color:#26724f}.smartCheckStatus.warn{background:#fff2dc;color:#8a5e20}.smartCheckStatus.bad{background:#fde9e6;color:#a3483f}.smartCheckList{display:grid;gap:5px}.smartCheckItem{display:flex;align-items:flex-start;gap:7px;font-size:10px;line-height:1.35;color:#59615e}.smartCheckItem i{display:grid;place-items:center;flex:0 0 18px;width:18px;height:18px;border-radius:50%;font-style:normal;font-size:9px;font-weight:900}.smartCheckItem.ok i{background:#e8f3ed;color:#26724f}.smartCheckItem.warn i{background:#fff0d5;color:#9a642f}.smartCheckItem.bad i{background:#fde9e6;color:#a3483f}
.smartSelectedQty{margin-top:8px;padding:8px 10px;border-radius:10px;background:#f7f5f0;color:#725132;font-size:10px;font-weight:800}.smartDensity{display:grid;grid-template-columns:1fr 92px;align-items:end;gap:8px;margin:8px 0}.smartDensity label{font-size:10px!important}.smartDensity input{min-height:38px!important;padding:7px 9px!important;font-size:13px!important}.smartMetrics{display:grid;grid-template-columns:1fr 1fr;gap:7px}.smartMetrics div{padding:8px 9px;border:1px solid #e6e2db;border-radius:10px;background:#faf9f6}.smartMetrics span{display:block;color:#7b827f;font-size:9px}.smartMetrics b{display:block;margin-top:2px;color:#5d4a38;font-size:14px}
.palletPartInspector{position:absolute;left:14px;bottom:14px;z-index:8;display:grid;gap:2px;max-width:min(310px,calc(100% - 28px));padding:9px 11px;border:1px solid rgba(45,57,62,.16);border-radius:11px;background:rgba(18,29,34,.90);color:#fff;box-shadow:0 8px 22px rgba(0,0,0,.18);backdrop-filter:blur(9px);pointer-events:none}.palletPartInspector[hidden]{display:none!important}.palletPartInspector strong{font-size:11px}.palletPartInspector span{font-size:10px;color:#dce5e1}.palletPartInspector b{font-size:10px;color:#f1c38f}
@media(max-width:760px){.smartToolsGrid{grid-template-columns:1fr}.smartToolsPanel{padding:14px}.smartToolsHead h2{font-size:19px}.smartMetrics{grid-template-columns:1fr 1fr}}
@media(max-width:420px){.smartMetrics{grid-template-columns:1fr}.smartDensity{grid-template-columns:1fr 86px}}
html[data-theme="dark"] .smartToolsPanel{background:linear-gradient(180deg,#181d1f,#15191b)!important;border-color:#353d3f!important;box-shadow:0 10px 26px rgba(0,0,0,.22)!important}html[data-theme="dark"] .smartToolsHead h2,html[data-theme="dark"] .smartToolBody h3{color:#edf1ef!important}html[data-theme="dark"] .smartToolsHead p,html[data-theme="dark"] .smartToolBody p,html[data-theme="dark"] .smartCheckItem{color:#9aa4a0!important}html[data-theme="dark"] .smartToolCard{background:#1b2022!important;border-color:#353d3f!important}html[data-theme="dark"] .smartToolIcon{background:#332b23!important;color:#e0a466!important}html[data-theme="dark"] .smartSelectedQty,html[data-theme="dark"] .smartMetrics div{background:#202628!important;border-color:#353d3f!important;color:#d9dfdc!important}html[data-theme="dark"] .smartMetrics b{color:#e7c49e!important}
'''
css_path.write_text(css,encoding='utf-8')

p3d=p3d.replace("Pallet Tools · v1.1.11 · обновление №345","Pallet Tools · v1.1.12 · обновление №346").replace("Pallet Tools · v1.1.11'","Pallet Tools · v1.1.12'")
if 'palletPartInspector' not in p3d:
    anchor="${dimensionOverlay}</div>`;"
    repl="${dimensionOverlay}<div class=\"palletPartInspector\" hidden><strong></strong><span></span><b></b></div></div>`;"
    if anchor not in p3d: raise SystemExit('3D inspector stage anchor missing')
    p3d=p3d.replace(anchor,repl,1)
if 'const inspectable=[];' not in p3d:
    anchor="    function mat(kind,i){"
    if anchor not in p3d: raise SystemExit('3D material anchor missing')
    p3d=p3d.replace(anchor,"    const inspectable=[];\n"+anchor,1)
old_piece="    function piece(kind,dx,dy,dz,x,y,z,i,group){const g=roundedBoxGeometry(dx,dy,dz,kind==='block'?.055:.035),m=new THREE.Mesh(g,mat(kind,i));m.position.set(x,y,z);m.castShadow=true;m.receiveShadow=true;group.add(m);return m;}"
new_piece="    function piece(kind,dx,dy,dz,x,y,z,i,group){const g=roundedBoxGeometry(dx,dy,dz,kind==='block'?.055:.035),m=new THREE.Mesh(g,mat(kind,i));m.position.set(x,y,z);m.castShadow=true;m.receiveShadow=true;if(kind==='deck'){m.userData.palletInspect={name:'Настил',index:i,t:deckThicknessMm,w:deckWidthMm,l:deckLengthMm,n:deckCount};m.userData.baseEmissiveHex=selected===kind?0x14382e:0;m.userData.baseEmissiveIntensity=selected===kind?.09:0;inspectable.push(m);}group.add(m);return m;}"
if old_piece in p3d:p3d=p3d.replace(old_piece,new_piece,1)
elif 'm.userData.palletInspect' not in p3d: raise SystemExit('3D piece anchor missing')

canvas_anchor="    const canvas=renderer.domElement;let dragging=false,lastX=0,lastY=0;"
if 'const raycaster=new THREE.Raycaster()' not in p3d:
    inspector_code=r'''    const canvas=renderer.domElement;
    const partInspector=root.querySelector('.palletPartInspector');
    const raycaster=new THREE.Raycaster(),pickPoint=new THREE.Vector2();
    let inspectDown=null;
    const resetInspectHighlight=()=>inspectable.forEach(mesh=>{if(!mesh.material)return;mesh.material.emissive.setHex(mesh.userData.baseEmissiveHex||0);mesh.material.emissiveIntensity=mesh.userData.baseEmissiveIntensity||0;});
    const showInspect=(mesh)=>{const info=mesh?.userData?.palletInspect;if(!info)return;resetInspectHighlight();mesh.material.emissive.setHex(0x8a5525);mesh.material.emissiveIntensity=.42;const boardNo=Number(info.index||0)+1,qty=Math.max(1,Math.round(num(el('qty')?.value,1))),total=info.n*qty;if(partInspector){partInspector.hidden=false;partInspector.querySelector('strong').textContent=`Настил №${boardNo}`;partInspector.querySelector('span').textContent=`${fmtMm(info.t)} × ${fmtMm(info.w)} × ${fmtMm(info.l)} мм`;partInspector.querySelector('b').textContent=`${info.n} шт. / поддон · ${total.toLocaleString('ru-RU')} шт. / заказ`;}window.dispatchEvent(new CustomEvent('pallet3d:partselect',{detail:{...info,boardNo,per:info.n,total}}));renderer.render(scene,camera);};
    canvas.addEventListener('pointerdown',e=>{inspectDown={x:e.clientX,y:e.clientY};},true);
    canvas.addEventListener('pointerup',e=>{if(!inspectDown)return;const moved=Math.hypot(e.clientX-inspectDown.x,e.clientY-inspectDown.y);inspectDown=null;if(moved>7)return;const rect=canvas.getBoundingClientRect();if(!rect.width||!rect.height)return;pickPoint.x=((e.clientX-rect.left)/rect.width)*2-1;pickPoint.y=-((e.clientY-rect.top)/rect.height)*2+1;raycaster.setFromCamera(pickPoint,camera);const hit=raycaster.intersectObjects(inspectable,false)[0];if(hit)showInspect(hit.object);},true);
    let dragging=false,lastX=0,lastY=0;'''
    if canvas_anchor not in p3d: raise SystemExit('3D canvas anchor missing')
    p3d=p3d.replace(canvas_anchor,inspector_code,1)

p3d_path.write_text(p3d,encoding='utf-8')
