from pathlib import Path
import re

JS = Path('assets/pallet3d-v10.js')
CSS = Path('assets/theme-industrial-v130.css')
HTML = Path('index.html')

js = JS.read_text(encoding='utf-8')
css = CSS.read_text(encoding='utf-8')
html = HTML.read_text(encoding='utf-8')


def must_replace(text, old, new, label):
    if old not in text:
        raise SystemExit(f'Patch target not found: {label}')
    return text.replace(old, new, 1)

js = must_replace(
    js,
    "  if(typeof state.showComposition!=='boolean')state.showComposition=false;\n  if(!Array.isArray(state.hiddenKinds))state.hiddenKinds=[];",
    "  if(typeof state.showComposition!=='boolean')state.showComposition=false;\n  if(!Number.isInteger(state.assemblyStep))state.assemblyStep=0;\n  if(!Array.isArray(state.hiddenKinds))state.hiddenKinds=[];",
    'assembly state init',
)

js = must_replace(
    js,
    "    return ids.map(id=>el(id)?.value??'').join('|')+'|'+(state.mode||'3d')+'|'+(state.selected||'all')+'|'+(state.showComposition?'composition':'model')+'|'+(Array.isArray(state.hiddenKinds)?state.hiddenKinds.join(','):'');",
    "    return ids.map(id=>el(id)?.value??'').join('|')+'|'+(state.mode||'3d')+'|'+(state.selected||'all')+'|'+(state.showComposition?'composition':'model')+'|assembly:'+(state.assemblyStep||0)+'|'+(Array.isArray(state.hiddenKinds)?state.hiddenKinds.join(','):'');",
    'signature assembly state',
)

js = must_replace(
    js,
    "    const mode=state.mode||'3d';\n    const hiddenKinds=new Set(Array.isArray(state.hiddenKinds)?state.hiddenKinds:[]);\n    const kindVisible=kind=>mode==='3d'||!hiddenKinds.has(kind);\n    const showDimensions=mode!=='3d'&&state.showDimensions!==false;",
    "    const mode=state.mode||'3d';\n    const hiddenKinds=new Set(Array.isArray(state.hiddenKinds)?state.hiddenKinds:[]);\n    const assemblyStep=clamp(Math.round(num(state.assemblyStep,0)),0,4);\n    const assemblyActive=assemblyStep>0;\n    const assemblyOrder={runner:1,block:2,cross:3,deck:4};\n    const assemblyKinds=['runner','block','cross','deck'];\n    const assemblyCurrentKind=assemblyActive?assemblyKinds[assemblyStep-1]:null;\n    const kindVisible=kind=>assemblyActive?(assemblyOrder[kind]||99)<=assemblyStep:(mode==='3d'||!hiddenKinds.has(kind));\n    const showDimensions=mode!=='3d'&&state.showDimensions!==false;",
    'assembly visibility',
)

js = must_replace(
    js,
    "    const showComposition=mode!=='3d'&&state.showComposition===true;",
    "    const showComposition=mode!=='3d'&&!assemblyActive&&state.showComposition===true;",
    'composition hidden during assembly',
)

assembly_block = r'''    const assemblySteps=[
      {kind:'runner',label:'Лыжи',title:'Установите лыжи',text:'Разложите лыжи параллельно по длине поддона и проверьте их положение.'},
      {kind:'block',label:'Шашки',title:'Установите шашки',text:'Поставьте шашки на лыжи по схеме поддона и закрепите соединение.'},
      {kind:'cross',label:'Поперечины',title:'Уложите поперечины',text:'Установите поперечины на шашки и закрепите гвоздями 2,8 × 80 мм.'},
      {kind:'deck',label:'Настил',title:'Уложите настил',text:'Разложите доски настила с рассчитанными зазорами и закрепите гвоздями 2,5 × 40 мм.'}
    ];
    const currentAssembly=assemblyActive?assemblySteps[assemblyStep-1]:null;
    const assemblyCurrentRows=assemblyActive?compositionRows.filter(r=>r.kind===assemblyCurrentKind):[];
    const assemblyDetail=assemblyCurrentRows.map(r=>`${r.qty} шт. · ${fmtMm(r.t)} × ${fmtMm(r.w)} × ${fmtMm(r.l)} мм`).join(' · ');
    const assemblyPanel=assemblyActive?`<section class="palletAssemblyPanel" aria-label="Пошаговая сборка поддона"><div class="palletAssemblyHead"><div><small>ПОШАГОВАЯ СБОРКА</small><strong>Шаг ${assemblyStep} из 4 · ${currentAssembly.title}</strong><p>${currentAssembly.text}</p>${assemblyDetail?`<em>${assemblyDetail}</em>`:''}</div><button type="button" data-p3d-assembly-close aria-label="Закрыть режим сборки">×</button></div><div class="palletAssemblySteps">${assemblySteps.map((s,i)=>`<button type="button" data-p3d-assembly-step="${i+1}" class="${i+1===assemblyStep?'active':i+1<assemblyStep?'done':''}"><b>${i+1}</b><span>${s.label}</span></button>`).join('')}</div><div class="palletAssemblyActions"><button type="button" data-p3d-assembly-prev ${assemblyStep===1?'disabled':''}>← Назад</button><button type="button" class="primary" data-p3d-assembly-next>${assemblyStep===4?'Готово ✓':'Далее →'}</button></div></section>`:'';
    const pickHintText=assemblyActive?`Шаг ${assemblyStep}/4 · ${currentAssembly.label}: нажмите деталь, чтобы увидеть размер и вес`:'Выберите деталь: настил, поперечину, лыжу или шашку';
'''

js = must_replace(
    js,
    "    const dimensionOverlay='<div class=\"palletOnModelMeasures\" aria-label=\"Полная размерная схема поддона\"></div>';",
    assembly_block + "    const dimensionOverlay='<div class=\"palletOnModelMeasures\" aria-label=\"Полная размерная схема поддона\"></div>';",
    'assembly panel',
)

js = must_replace(
    js,
    "    const fastenerLegend=mode==='explode'?'<div style=\"display:flex;justify-content:center;gap:12px;flex-wrap:wrap;margin:7px auto 0;font-size:11px;font-weight:800;color:#46514d\"><span>● 2,8×80 мм — поперечины над шашками и лыжи</span><span>● 2,5×40 мм — настил к поперечинам</span></div>':'';",
    "    const fastenerLegend=mode==='explode'&&!assemblyActive?'<div style=\"display:flex;justify-content:center;gap:12px;flex-wrap:wrap;margin:7px auto 0;font-size:11px;font-weight:800;color:#46514d\"><span>● 2,8×80 мм — поперечины над шашками и лыжи</span><span>● 2,5×40 мм — настил к поперечинам</span></div>':'';",
    'fastener legend assembly',
)

js = must_replace(
    js,
    "    const partLegend=mode==='3d'?'':`<div class=\"palletPartLegend\" aria-label=\"Группы деталей\"><span class=\"palletPartLegendTitle\">ДЕТАЛИ</span>${legendItems.map(([kind,label])=>`<button type=\"button\" data-p3d-kind-toggle=\"${kind}\" class=\"${kindVisible(kind)?'active':'off'}\" aria-pressed=\"${kindVisible(kind)?'true':'false'}\"><i class=\"legendDot ${kind}\"></i><span>${label}</span></button>`).join('')}<button type=\"button\" class=\"palletPartLegendReset\" data-p3d-kind-reset ${hiddenKinds.size?'':'hidden'}>Показать все</button></div>`;",
    "    const partLegend=mode==='3d'||assemblyActive?'':`<div class=\"palletPartLegend\" aria-label=\"Группы деталей\"><span class=\"palletPartLegendTitle\">ДЕТАЛИ</span>${legendItems.map(([kind,label])=>`<button type=\"button\" data-p3d-kind-toggle=\"${kind}\" class=\"${kindVisible(kind)?'active':'off'}\" aria-pressed=\"${kindVisible(kind)?'true':'false'}\"><i class=\"legendDot ${kind}\"></i><span>${label}</span></button>`).join('')}<button type=\"button\" class=\"palletPartLegendReset\" data-p3d-kind-reset ${hiddenKinds.size?'':'hidden'}>Показать все</button></div>`;",
    'hide part legend assembly',
)

js = must_replace(
    js,
    "<button type=\"button\" data-p3d-mode=\"explode\" class=\"${mode==='explode'?'active':''}\">${mode==='explode'?'Собрать':'Разнести'}</button><button type=\"button\" data-p3d-dims",
    "<button type=\"button\" data-p3d-mode=\"explode\" class=\"${mode==='explode'&&!assemblyActive?'active':''}\">${mode==='explode'&&!assemblyActive?'Собрать':'Разнести'}</button><button type=\"button\" data-p3d-assembly class=\"${assemblyActive?'active':''}\" aria-pressed=\"${assemblyActive?'true':'false'}\">Сборка</button><button type=\"button\" data-p3d-dims",
    'assembly toolbar button',
)

js = must_replace(
    js,
    "<button type=\"button\" data-p3d-composition aria-pressed=\"${showComposition?'true':'false'}\" class=\"${showComposition?'active':''}\" ${mode==='3d'?'hidden':''}>Состав</button></div>${partLegend}${fastenerLegend}",
    "<button type=\"button\" data-p3d-composition aria-pressed=\"${showComposition?'true':'false'}\" class=\"${showComposition?'active':''}\" ${mode==='3d'||assemblyActive?'hidden':''}>Состав</button></div>${assemblyPanel}${partLegend}${fastenerLegend}",
    'assembly panel placement',
)

js = must_replace(
    js,
    "<div class=\"palletPickHint\" ${mode==='3d'?'hidden':''}>Выберите деталь: настил, поперечину, лыжу или шашку</div>",
    "<div class=\"palletPickHint\" ${mode==='3d'&&!assemblyActive?'hidden':''}>${pickHintText}</div>",
    'assembly pick hint',
)

js = must_replace(
    js,
    "    function mat(kind,i){const on=selected==='all'||selected===kind,map=textures[kind].clone();map.needsUpdate=true;map.offset.x=(i*.149)%1;return new THREE.MeshStandardMaterial({map,color:on?colors[kind][i%colors[kind].length]:0xbdb8b0,roughness:.78,metalness:0,transparent:!on,opacity:on?1:.15,depthWrite:on,emissive:selected===kind?0x14382e:0,emissiveIntensity:selected===kind?.09:0});}",
    "    function mat(kind,i){const on=assemblyActive?true:(selected==='all'||selected===kind),isCurrent=assemblyActive&&kind===assemblyCurrentKind,map=textures[kind].clone();map.needsUpdate=true;map.offset.x=(i*.149)%1;return new THREE.MeshStandardMaterial({map,color:on?colors[kind][i%colors[kind].length]:0xbdb8b0,roughness:.78,metalness:0,transparent:!on,opacity:on?1:.15,depthWrite:on,emissive:isCurrent?0x6b3515:(selected===kind?0x14382e:0),emissiveIntensity:isCurrent?.24:(selected===kind?.09:0)});}",
    'assembly material highlight',
)

js = must_replace(
    js,
    "mesh.userData.baseEmissiveHex=selected===kind?0x14382e:0;mesh.userData.baseEmissiveIntensity=selected===kind?.09:0;",
    "mesh.userData.baseEmissiveHex=assemblyActive&&kind===assemblyCurrentKind?0x6b3515:(selected===kind?0x14382e:0);mesh.userData.baseEmissiveIntensity=assemblyActive&&kind===assemblyCurrentKind?.24:(selected===kind?.09:0);",
    'assembly base highlight',
)

js = must_replace(
    js,
    "    if(selected==='all'||selected==='runner'){runnerXs.forEach((x,xi)=>blockRows.forEach((z,zi)=>{if(z==null||zi*3+Math.min(xi,2)>=blockCount)return;pairNails(nail80,groups.runner,x,runnerT+.014,z,Math.min(.072,runnerActualW*.22),1);}));}",
    "    if((!assemblyActive&&(selected==='all'||selected==='runner'))||(assemblyActive&&assemblyStep>=2)){runnerXs.forEach((x,xi)=>blockRows.forEach((z,zi)=>{if(z==null||zi*3+Math.min(xi,2)>=blockCount)return;pairNails(nail80,groups.runner,x,runnerT+.014,z,Math.min(.072,runnerActualW*.22),1);}));}",
    'assembly runner fasteners',
)

js = must_replace(
    js,
    "    if(selected==='all'||selected==='cross'){blockPoints.forEach(p=>pairNailsDepth(nail80,groups.cross,p.x,bindY+bindT/2+.014,p.z,Math.min(.13,bindDepth*.18),-1));}",
    "    if((!assemblyActive&&(selected==='all'||selected==='cross'))||(assemblyActive&&assemblyStep>=3)){blockPoints.forEach(p=>pairNailsDepth(nail80,groups.cross,p.x,bindY+bindT/2+.014,p.z,Math.min(.13,bindDepth*.18),-1));}",
    'assembly cross fasteners',
)

js = must_replace(
    js,
    "if(selected==='all'||selected==='deck')bindZ.forEach((z,zi)=>{",
    "if((!assemblyActive&&(selected==='all'||selected==='deck'))||(assemblyActive&&assemblyStep>=4))bindZ.forEach((z,zi)=>{",
    'assembly deck fasteners',
)

js = must_replace(
    js,
    "    const exploded=mode==='explode',offsets={runner:0,block:exploded?1.25:0,cross:exploded?2.55:0,deck:exploded?3.85:0};",
    "    Object.entries(groups).forEach(([kind,group])=>{group.visible=kindVisible(kind);});\n    const exploded=mode==='explode'&&!assemblyActive,offsets={runner:0,block:exploded?1.25:0,cross:exploded?2.55:0,deck:exploded?3.85:0};",
    'assembly group visibility',
)

js = must_replace(
    js,
    "    if(exploded){const t0=performance.now();const animate=t=>{const q=clamp((t-t0)/420,0,1),e=1-Math.pow(1-q,3);groups.block.position.y=offsets.block*e;groups.cross.position.y=offsets.cross*e;groups.deck.position.y=offsets.deck*e;draw();if(q<1)raf=requestAnimationFrame(animate);};raf=requestAnimationFrame(animate);}else draw();",
    "    if(assemblyActive&&assemblyCurrentKind&&groups[assemblyCurrentKind]){const currentGroup=groups[assemblyCurrentKind],startY=1.15;currentGroup.position.y=startY;const t0=performance.now();const animate=t=>{const q=clamp((t-t0)/520,0,1),e=1-Math.pow(1-q,3);currentGroup.position.y=startY*(1-e);draw();if(q<1)raf=requestAnimationFrame(animate);};raf=requestAnimationFrame(animate);}else if(exploded){const t0=performance.now();const animate=t=>{const q=clamp((t-t0)/420,0,1),e=1-Math.pow(1-q,3);groups.block.position.y=offsets.block*e;groups.cross.position.y=offsets.cross*e;groups.deck.position.y=offsets.deck*e;draw();if(q<1)raf=requestAnimationFrame(animate);};raf=requestAnimationFrame(animate);}else draw();",
    'assembly drop animation',
)

js = must_replace(
    js,
    "    root.querySelectorAll('[data-p3d-mode]').forEach(btn=>btn.addEventListener('click',()=>{state.mode=btn.dataset.p3dMode;render(num(el('pL')?.value),num(el('pW')?.value));}));",
    "    root.querySelectorAll('[data-p3d-mode]').forEach(btn=>btn.addEventListener('click',()=>{state.assemblyStep=0;state.mode=btn.dataset.p3dMode;render(num(el('pL')?.value),num(el('pW')?.value));}));\n    root.querySelector('[data-p3d-assembly]')?.addEventListener('click',()=>{if(assemblyActive){state.assemblyStep=0;state.mode='3d';}else{state.assemblyStep=1;state.mode='explode';state.showComposition=false;state.hiddenKinds=[];}render(num(el('pL')?.value),num(el('pW')?.value));});\n    root.querySelectorAll('[data-p3d-assembly-step]').forEach(btn=>btn.addEventListener('click',()=>{state.assemblyStep=clamp(Math.round(num(btn.dataset.p3dAssemblyStep,1)),1,4);state.mode='explode';render(num(el('pL')?.value),num(el('pW')?.value));}));\n    root.querySelector('[data-p3d-assembly-prev]')?.addEventListener('click',()=>{state.assemblyStep=clamp(assemblyStep-1,1,4);render(num(el('pL')?.value),num(el('pW')?.value));});\n    root.querySelector('[data-p3d-assembly-next]')?.addEventListener('click',()=>{if(assemblyStep>=4){state.assemblyStep=0;state.mode='3d';}else state.assemblyStep=assemblyStep+1;render(num(el('pL')?.value),num(el('pW')?.value));});\n    root.querySelector('[data-p3d-assembly-close]')?.addEventListener('click',()=>{state.assemblyStep=0;state.mode='3d';render(num(el('pL')?.value),num(el('pW')?.value));});",
    'assembly controls',
)

css_marker = '/* palletAssemblyV1132 */'
if css_marker not in css:
    css += r'''

/* palletAssemblyV1132 */
#palletPreview3D [data-p3d-assembly]{min-width:82px}
#palletPreview3D [data-p3d-assembly].active{background:#8d5a32!important;border-color:#8d5a32!important;color:#fff!important;box-shadow:0 5px 14px rgba(112,66,31,.18)!important}
.palletAssemblyPanel{margin:9px 0 3px;padding:12px 13px 11px;border:1px solid #dfd2c3;border-radius:14px;background:linear-gradient(135deg,#fffaf3,#f7ede1);box-shadow:0 8px 22px rgba(79,53,31,.08);color:#40352c}
.palletAssemblyHead{display:flex;justify-content:space-between;gap:12px;align-items:flex-start}
.palletAssemblyHead small{display:block;margin-bottom:4px;color:#a36a36;font-size:8px;font-weight:950;letter-spacing:.14em}
.palletAssemblyHead strong{display:block;color:#362c24;font-size:14px;line-height:1.2}
.palletAssemblyHead p{margin:5px 0 0;color:#74665a;font-size:10px;font-weight:720;line-height:1.4}
.palletAssemblyHead em{display:inline-block;margin-top:7px;padding:4px 7px;border:1px solid #e2cdb5;border-radius:7px;background:#fff8ef;color:#795331;font-size:9px;font-style:normal;font-weight:850;line-height:1.25}
.palletAssemblyHead>button{flex:0 0 30px;width:30px;height:30px;min-height:30px;padding:0;border:1px solid #dfd1c3;border-radius:9px;background:#fff;color:#8a7563;font-size:18px;line-height:1;box-shadow:none}
.palletAssemblySteps{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:6px;margin-top:11px}
.palletAssemblySteps button{display:flex;align-items:center;justify-content:center;gap:6px;min-width:0;min-height:36px;padding:6px 7px;border:1px solid #e2d6ca;border-radius:10px;background:#fff;color:#837366;font-size:9px;font-weight:850;box-shadow:none}
.palletAssemblySteps button b{display:grid;place-items:center;flex:0 0 20px;width:20px;height:20px;border-radius:50%;background:#eee7df;color:#75665a;font-size:9px}
.palletAssemblySteps button.done{border-color:#ddc4a8;background:#fff7ed;color:#825a37}
.palletAssemblySteps button.done b{background:#dca96f;color:#fff}
.palletAssemblySteps button.active{border-color:#b8793d;background:#f5e5d2;color:#633e20;box-shadow:inset 0 0 0 1px rgba(184,121,61,.10)}
.palletAssemblySteps button.active b{background:#9d6232;color:#fff;box-shadow:0 0 0 3px rgba(184,121,61,.14)}
.palletAssemblyActions{display:flex;justify-content:flex-end;gap:7px;margin-top:10px}
.palletAssemblyActions button{min-height:36px;padding:7px 12px;border:1px solid #ddcfc1;border-radius:9px;background:#fff;color:#66584d;font-size:10px;font-weight:900;box-shadow:none}
.palletAssemblyActions button.primary{border-color:#9d6232;background:#9d6232;color:#fff;box-shadow:0 5px 13px rgba(117,67,29,.16)}
.palletAssemblyActions button:disabled{opacity:.38;cursor:not-allowed}
html[data-theme="dark"] .palletAssemblyPanel{border-color:#564537;background:linear-gradient(135deg,#312a24,#2a2521);color:#efe2d4}
html[data-theme="dark"] .palletAssemblyHead strong{color:#f5eadf}
html[data-theme="dark"] .palletAssemblyHead p{color:#bdb0a4}
html[data-theme="dark"] .palletAssemblyHead em{border-color:#5d4633;background:#392e25;color:#e7c298}
html[data-theme="dark"] .palletAssemblyHead>button,html[data-theme="dark"] .palletAssemblySteps button,html[data-theme="dark"] .palletAssemblyActions button{border-color:#4e4035;background:#302a25;color:#d9cdc1}
html[data-theme="dark"] .palletAssemblySteps button.done{border-color:#624b36;background:#382e26;color:#d7b28c}
html[data-theme="dark"] .palletAssemblySteps button.active{border-color:#a86e39;background:#493522;color:#f1cfaa}
html[data-theme="dark"] .palletAssemblyActions button.primary{border-color:#a86e39;background:#9a6233;color:#fff}
@media(max-width:620px){
  .palletAssemblyPanel{padding:10px;margin-top:7px}
  .palletAssemblyHead strong{font-size:13px}
  .palletAssemblyHead p{font-size:9px}
  .palletAssemblySteps{grid-template-columns:repeat(2,minmax(0,1fr));gap:5px}
  .palletAssemblySteps button{justify-content:flex-start;min-height:38px}
  .palletAssemblyActions{display:grid;grid-template-columns:1fr 1fr}
  .palletAssemblyActions button{min-height:42px}
}
'''

# Cache-bust the edited JS/CSS so browsers receive the new mode immediately.
html = re.sub(r'assets/pallet3d-v10\.js\?v=\d+', 'assets/pallet3d-v10.js?v=132', html)
html = re.sub(r'assets/theme-industrial-v130\.css\?v=\d+', 'assets/theme-industrial-v130.css?v=132', html)

JS.write_text(js, encoding='utf-8')
CSS.write_text(css, encoding='utf-8')
HTML.write_text(html, encoding='utf-8')
print('assembly mode v132 patched')
