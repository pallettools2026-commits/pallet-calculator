from pathlib import Path

JS = Path('assets/pallet3d-v10.js')
CSS = Path('assets/theme-industrial-v130.css')
HTML = Path('index.html')

js = JS.read_text(encoding='utf-8')
css = CSS.read_text(encoding='utf-8')
html = HTML.read_text(encoding='utf-8')

old = """    const mode=state.mode||'3d';
    const fastenerLegend=mode==='explode'?'<div style=\"display:flex;justify-content:center;gap:12px;flex-wrap:wrap;margin:7px auto 0;font-size:11px;font-weight:800;color:#46514d\"><span>● 2,8×80 мм — поперечины над шашками и лыжи</span><span>● 2,5×40 мм — настил к поперечинам</span></div>':'';
    root.innerHTML=`<div class=\"pallet3dToolbar\" role=\"tablist\"><button type=\"button\" data-p3d-mode=\"3d\" class=\"${mode==='3d'?'active':''}\">3D</button><button type=\"button\" data-p3d-mode=\"top\" class=\"${mode==='top'?'active':''}\">Сверху</button><button type=\"button\" data-p3d-mode=\"side\" class=\"${mode==='side'?'active':''}\">Сбоку</button><button type=\"button\" data-p3d-mode=\"explode\" class=\"${mode==='explode'?'active':''}\">${mode==='explode'?'Собрать':'Разнести'}</button></div>${fastenerLegend}<div class=\"palletReferenceStage\" style=\"width:100%;position:relative;overflow:hidden;background:radial-gradient(circle at 50% 30%,#fff 0,#faf8f3 52%,#efede7 100%);border-radius:14px;margin-top:8px\"><div class=\"palletReferenceHost\" style=\"width:100%;min-height:390px;position:relative\"></div></div>`;
"""
new = """    const mode=state.mode||'3d';
    const deckThicknessMm=Math.max(0,num(deck.t,22)),deckWidthMm=Math.max(0,num(deck.w,98)),deckLengthMm=Math.max(0,num(deck.l,profile.length));
    const remainingMm=profile.width-deckCount*deckWidthMm,rawGapMm=deckCount>1?remainingMm/(deckCount-1):0,gapBad=deckCount>1&&rawGapMm<0;
    const fmtMm=v=>{const x=Math.round(num(v,0)*10)/10;return Number.isInteger(x)?String(x):x.toFixed(1).replace('.',',');};
    const gapText=deckCount>1?`${fmtMm(Math.max(0,rawGapMm))} мм`:'—';
    const fitNote=gapBad?`Не хватает ${fmtMm(Math.abs(remainingMm))} мм по ширине`:`Остаток ${fmtMm(Math.max(0,remainingMm))} мм`;
    const dimensionHud=`<div class=\"palletDimensionHud\" aria-label=\"Размеры настила\"><div class=\"palletMeasure deck\"><span>Доска настила</span><strong>${fmtMm(deckThicknessMm)} × ${fmtMm(deckWidthMm)} × ${fmtMm(deckLengthMm)} мм</strong><small>толщина × ширина × длина</small></div><div class=\"palletMeasure gap ${gapBad?'bad':''}\"><span>Между досками</span><strong>${gapText}</strong><small>${deckCount} шт. · ${fitNote}</small></div></div>`;
    const fastenerLegend=mode==='explode'?'<div style=\"display:flex;justify-content:center;gap:12px;flex-wrap:wrap;margin:7px auto 0;font-size:11px;font-weight:800;color:#46514d\"><span>● 2,8×80 мм — поперечины над шашками и лыжи</span><span>● 2,5×40 мм — настил к поперечинам</span></div>':'';
    root.innerHTML=`<div class=\"pallet3dToolbar\" role=\"tablist\"><button type=\"button\" data-p3d-mode=\"3d\" class=\"${mode==='3d'?'active':''}\">3D</button><button type=\"button\" data-p3d-mode=\"top\" class=\"${mode==='top'?'active':''}\">Сверху</button><button type=\"button\" data-p3d-mode=\"side\" class=\"${mode==='side'?'active':''}\">Сбоку</button><button type=\"button\" data-p3d-mode=\"explode\" class=\"${mode==='explode'?'active':''}\">${mode==='explode'?'Собрать':'Разнести'}</button></div>${fastenerLegend}<div class=\"palletReferenceStage\" style=\"width:100%;position:relative;overflow:hidden;background:radial-gradient(circle at 50% 30%,#fff 0,#faf8f3 52%,#efede7 100%);border-radius:14px;margin-top:8px\"><div class=\"palletReferenceHost\" style=\"width:100%;min-height:390px;position:relative\"></div>${dimensionHud}</div>`;
"""
assert old in js, '3D toolbar/stage block changed; aborting'
js = js.replace(old, new, 1)

old = """    const bindT=isReference?.22:Math.max(.15,num(bindParts[0].t,22)*S),bindDepth=isReference?.98:Math.max(.58,num(bindParts[0].w,98)*S);
    const deckT=isReference?.22:Math.max(.15,num(deck.t,22)*S),deckW=isReference?.98:Math.max(.58,num(deck.w,98)*S);
"""
new = """    const bindT=isReference?.22:Math.max(.15,num(bindParts[0].t,22)*S),bindDepth=isReference?.98:Math.max(.58,num(bindParts[0].w,98)*S);
    const deckT=isReference?.22:Math.max(.01,deckThicknessMm*S),deckW=isReference?.98:Math.max(.01,deckWidthMm*S),deckL=Math.max(.01,deckLengthMm*S);
"""
assert old in js, 'deck dimensions block changed; aborting'
js = js.replace(old, new, 1)

old = """    const topY=runnerT+blockH+bindT+deckT/2,actualDeckW=deckCount?Math.min(deckW,(PW*.92/Math.max(1,deckCount))*.78):deckW,topXs=deckCount?spread(deckCount,PW,actualDeckW):[],nailY=topY+deckT/2+.014;
"""
new = """    const topY=runnerT+blockH+bindT+deckT/2,actualDeckW=deckCount?Math.min(deckW,PW):deckW,topXs=deckCount?spread(deckCount,PW,actualDeckW):[],nailY=topY+deckT/2+.014;
"""
assert old in js, 'deck layout block changed; aborting'
js = js.replace(old, new, 1)

old = """    topXs.forEach((x,i)=>{piece('deck',actualDeckW,deckT,PL,x,topY,0,i,groups.deck);if(selected==='all'||selected==='deck')bindZ.forEach((z,zi)=>{const edgeBoard=i===0||i===topXs.length-1,edgeCross=zi===0||zi===bindZ.length-1;if(edgeBoard&&edgeCross)cornerTriple(x,nailY,z,Math.min(.08,actualDeckW*.24));else pairNails(nail40,groups.deck,x,nailY,z,Math.min(.06,actualDeckW*.22),-1);});});
"""
new = """    topXs.forEach((x,i)=>{piece('deck',actualDeckW,deckT,deckL,x,topY,0,i,groups.deck);if(selected==='all'||selected==='deck')bindZ.forEach((z,zi)=>{const edgeBoard=i===0||i===topXs.length-1,edgeCross=zi===0||zi===bindZ.length-1;if(edgeBoard&&edgeCross)cornerTriple(x,nailY,z,Math.min(.08,actualDeckW*.24));else pairNails(nail40,groups.deck,x,nailY,z,Math.min(.06,actualDeckW*.22),-1);});});
"""
assert old in js, 'deck piece block changed; aborting'
js = js.replace(old, new, 1)

insert_before = """  function setupDeckCountControl(){
"""
live = """  function setupLivePalletDimensions(){
    const refresh=()=>{if(syncQueued)return;syncQueued=true;requestAnimationFrame(()=>{syncQueued=false;window.rerenderPallet3D?.();});};
    ['pL','pW','n0','t0','w0','l0'].forEach(id=>{const input=el(id);if(!input||input.dataset.palletMeasureReady==='1')return;input.dataset.palletMeasureReady='1';input.addEventListener('input',refresh);input.addEventListener('change',refresh);});
  }

"""
assert insert_before in js, 'setupDeckCountControl not found; aborting'
js = js.replace(insert_before, live + insert_before, 1)

old = """  function updateSiteVersion(){const node=document.querySelector('.sideVersion');if(!node)return;const admin=typeof currentRole!=='undefined'&&currentRole==='admin';node.textContent=admin?'Pallet Tools · v1.1.3 · обновление №337':'Pallet Tools · v1.1.3';}
"""
new = """  function updateSiteVersion(){const node=document.querySelector('.sideVersion');if(!node)return;const admin=typeof currentRole!=='undefined'&&currentRole==='admin';node.textContent=admin?'Pallet Tools · v1.1.4 · обновление №338':'Pallet Tools · v1.1.4';}
"""
assert old in js, 'JS version string changed; aborting'
js = js.replace(old, new, 1)

old = """  setupDeckCountControl();setupAdminEmployeeDelete();setupAdminEmployeeInvite();setupPrivateRegistration();setupPasswordRecovery();setupUserPresence();setupAdminPresenceStatus();setupDashboardPalletPreview();updateSiteVersion();
"""
new = """  setupDeckCountControl();setupLivePalletDimensions();setupAdminEmployeeDelete();setupAdminEmployeeInvite();setupPrivateRegistration();setupPasswordRecovery();setupUserPresence();setupAdminPresenceStatus();setupDashboardPalletPreview();updateSiteVersion();
"""
assert old in js, 'initialization line changed; aborting'
js = js.replace(old, new, 1)

css_add = """

/* 3D live dimensions v1.1.4 */
.palletDimensionHud{position:absolute;left:12px;right:12px;bottom:12px;z-index:4;display:flex;gap:8px;flex-wrap:wrap;align-items:stretch;pointer-events:none}
.palletMeasure{min-width:0;padding:9px 11px;border:1px solid rgba(187,169,148,.55);border-radius:12px;background:rgba(255,255,255,.92);box-shadow:0 5px 15px rgba(58,49,39,.08);-webkit-backdrop-filter:blur(5px);backdrop-filter:blur(5px);color:#4a433d}
.palletMeasure.deck{flex:1 1 260px}
.palletMeasure.gap{flex:0 1 190px;background:rgba(239,248,243,.94);border-color:#cfe3d7;color:#315f4e}
.palletMeasure.gap.bad{background:rgba(255,241,239,.96);border-color:#ebc7c1;color:#92463f}
.palletMeasure span{display:block;font-size:9px;font-weight:900;letter-spacing:.09em;text-transform:uppercase;opacity:.7}
.palletMeasure strong{display:block;margin-top:2px;font-size:15px;line-height:1.2;font-weight:900}
.palletMeasure small{display:block;margin-top:3px;font-size:10px;line-height:1.25;font-weight:750;opacity:.72}
@media(max-width:620px){.palletDimensionHud{left:8px;right:8px;bottom:8px;gap:6px}.palletMeasure{padding:7px 9px;border-radius:10px}.palletMeasure.deck,.palletMeasure.gap{flex:1 1 100%}.palletMeasure strong{font-size:13px}.palletMeasure small{font-size:9px}}
"""
assert '/* 3D live dimensions v1.1.4 */' not in css, 'dimension CSS already present; aborting'
css += css_add
css = css.replace('content:"Pallet Tools · v1.1.3";font-size:11px!important', 'content:"Pallet Tools · v1.1.4";font-size:11px!important', 1)
css = css.replace('content:"Pallet Tools · v1.1.3 · обновление №337"', 'content:"Pallet Tools · v1.1.4 · обновление №338"', 1)

assert 'assets/theme-industrial-v130.css?v=151' in html, 'CSS cache buster changed; aborting'
assert 'assets/pallet3d-v10.js?v=147' in html, 'JS cache buster changed; aborting'
html = html.replace('assets/theme-industrial-v130.css?v=151', 'assets/theme-industrial-v130.css?v=152', 1)
html = html.replace('assets/pallet3d-v10.js?v=147', 'assets/pallet3d-v10.js?v=148', 1)

JS.write_text(js, encoding='utf-8')
CSS.write_text(css, encoding='utf-8')
HTML.write_text(html, encoding='utf-8')
print('Applied live 3D dimensions v1.1.4')
