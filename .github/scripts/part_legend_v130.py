from pathlib import Path
import re

js = Path('assets/pallet3d-v10.js')
s = js.read_text(encoding='utf-8')

# Persist hidden groups in the viewer state.
anchor = "  if(typeof state.showDimensions!=='boolean')state.showDimensions=true;"
insert = anchor + "\n  if(!Array.isArray(state.hiddenKinds))state.hiddenKinds=[];"
if "Array.isArray(state.hiddenKinds)" not in s:
    if anchor not in s:
        raise SystemExit('state anchor not found')
    s = s.replace(anchor, insert, 1)

# Add visibility helpers. Hidden groups apply only outside normal 3D.
anchor = "    const mode=state.mode||'3d';\n    const showDimensions=mode!=='3d'&&state.showDimensions!==false;"
replacement = "    const mode=state.mode||'3d';\n    const hiddenKinds=new Set(Array.isArray(state.hiddenKinds)?state.hiddenKinds:[]);\n    const kindVisible=kind=>mode==='3d'||!hiddenKinds.has(kind);\n    const showDimensions=mode!=='3d'&&state.showDimensions!==false;"
if "const hiddenKinds=new Set" not in s:
    if anchor not in s:
        raise SystemExit('mode anchor not found')
    s = s.replace(anchor, replacement, 1)

# Add compact warm-color legend with group toggles.
anchor = "    const fastenerLegend=mode==='explode'?'<div style=\"display:flex;justify-content:center;gap:12px;flex-wrap:wrap;margin:7px auto 0;font-size:11px;font-weight:800;color:#46514d\"><span>● 2,8×80 мм — поперечины над шашками и лыжи</span><span>● 2,5×40 мм — настил к поперечинам</span></div>':'';"
legend = anchor + "\n    const legendItems=[['deck','Настил'],['cross','Поперечины'],['runner','Лыжи'],['block','Шашки']];\n    const partLegend=mode==='3d'?'':`<div class=\"palletPartLegend\" aria-label=\"Группы деталей\"><span class=\"palletPartLegendTitle\">ДЕТАЛИ</span>${legendItems.map(([kind,label])=>`<button type=\"button\" data-p3d-kind-toggle=\"${kind}\" class=\"${kindVisible(kind)?'active':'off'}\" aria-pressed=\"${kindVisible(kind)?'true':'false'}\"><i class=\"legendDot ${kind}\"></i><span>${label}</span></button>`).join('')}<button type=\"button\" class=\"palletPartLegendReset\" data-p3d-kind-reset ${hiddenKinds.size?'':'hidden'}>Показать все</button></div>`;"
if "const partLegend=mode==='3d'" not in s:
    if anchor not in s:
        raise SystemExit('legend anchor not found')
    s = s.replace(anchor, legend, 1)

# Insert legend below the mode toolbar.
old = "</button></div>${fastenerLegend}<div class=\"palletReferenceStage\""
new = "</button></div>${partLegend}${fastenerLegend}<div class=\"palletReferenceStage\""
if "${partLegend}${fastenerLegend}" not in s:
    if old not in s:
        raise SystemExit('toolbar insertion target not found')
    s = s.replace(old, new, 1)

# Make group colors more distinct while staying in a warm timber palette.
old_textures = "    const textures={deck:woodTexture(17,'#f3dfbd','#9a724b'),cross:woodTexture(31,'#ecd2a8','#906642'),runner:woodTexture(47,'#e8ca9a','#875d39'),block:woodTexture(61,'#dfbb86','#805433')};Object.values(textures).forEach((t,i)=>t.repeat.set(i===3?1.4:3.2,1));\n    const colors={deck:[0xf3dab2,0xefd1a4,0xf6e0bf],cross:[0xeccda0,0xe6c18f,0xf0d5ad],runner:[0xe4c08d,0xddb47f,0xe9ca9a],block:[0xd8aa72,0xdfb783,0xd2a069]};"
new_textures = "    const textures={deck:woodTexture(17,'#f3dfbd','#9a724b'),cross:woodTexture(31,'#e4bd86','#895d37'),runner:woodTexture(47,'#c99361','#70482d'),block:woodTexture(61,'#a86f49','#583722')};Object.values(textures).forEach((t,i)=>t.repeat.set(i===3?1.4:3.2,1));\n    const colors={deck:[0xf4ddb9,0xefd1a4,0xf7e3c5],cross:[0xdfb477,0xd6a666,0xe8c08a],runner:[0xbd7f4e,0xb27145,0xc98d5d],block:[0x955d3c,0x9e6947,0x875235]};"
if old_textures in s:
    s = s.replace(old_textures, new_textures, 1)

# Do not render hidden group meshes outside 3D.
old_piece = "    function piece(kind,dx,dy,dz,x,y,z,i,group){const g=roundedBoxGeometry(dx,dy,dz,kind==='block'?.055:.035),m=new THREE.Mesh(g,mat(kind,i));m.position.set(x,y,z);m.castShadow=true;m.receiveShadow=true;group.add(m);return m;}"
new_piece = "    function piece(kind,dx,dy,dz,x,y,z,i,group){const g=roundedBoxGeometry(dx,dy,dz,kind==='block'?.055:.035),m=new THREE.Mesh(g,mat(kind,i));m.position.set(x,y,z);m.visible=kindVisible(kind);m.castShadow=true;m.receiveShadow=true;group.add(m);return m;}"
if "m.visible=kindVisible(kind)" not in s:
    if old_piece not in s:
        raise SystemExit('piece target not found')
    s = s.replace(old_piece, new_piece, 1)

# Hidden groups must not be ray-picked.
old_pick = "    const pickAt=(clientX,clientY)=>{const rect=canvas.getBoundingClientRect();if(!rect.width||!rect.height)return null;pickPoint.x=((clientX-rect.left)/rect.width)*2-1;pickPoint.y=-((clientY-rect.top)/rect.height)*2+1;scene.updateMatrixWorld(true);camera.updateMatrixWorld(true);raycaster.setFromCamera(pickPoint,camera);return raycaster.intersectObjects(inspectable,false).find(hit=>hit.object?.userData?.palletInspect)||null;};"
new_pick = "    const pickAt=(clientX,clientY)=>{const rect=canvas.getBoundingClientRect();if(!rect.width||!rect.height)return null;pickPoint.x=((clientX-rect.left)/rect.width)*2-1;pickPoint.y=-((clientY-rect.top)/rect.height)*2+1;scene.updateMatrixWorld(true);camera.updateMatrixWorld(true);raycaster.setFromCamera(pickPoint,camera);const candidates=inspectable.filter(mesh=>kindVisible(mesh?.userData?.palletInspect?.kind));return raycaster.intersectObjects(candidates,false).find(hit=>hit.object?.userData?.palletInspect)||null;};"
if "const candidates=inspectable.filter(mesh=>kindVisible" not in s:
    if old_pick not in s:
        raise SystemExit('pickAt target not found')
    s = s.replace(old_pick, new_pick, 1)

# Hide projected click zones for hidden groups.
old_cond = "if(!mesh||!info||!visibleKinds.has(info.kind)){btn.hidden=true;return;}"
new_cond = "if(!mesh||!info||!kindVisible(info.kind)||!visibleKinds.has(info.kind)){btn.hidden=true;return;}"
if new_cond not in s:
    if old_cond not in s:
        raise SystemExit('pick button condition target not found')
    s = s.replace(old_cond, new_cond, 1)

# Add legend interactions before existing part selector handlers.
anchor = "    root.querySelector('[data-p3d-dims]')?.addEventListener('click',()=>{state.showDimensions=!state.showDimensions;render(num(el('pL')?.value),num(el('pW')?.value));});\n    root.querySelectorAll('[data-p3d-part]').forEach(btn=>btn.addEventListener('click',()=>{const k=btn.dataset.p3dPart;state.selected=state.selected===k?'all':k;render(num(el('pL')?.value),num(el('pW')?.value));}));"
replacement = "    root.querySelector('[data-p3d-dims]')?.addEventListener('click',()=>{state.showDimensions=!state.showDimensions;render(num(el('pL')?.value),num(el('pW')?.value));});\n    root.querySelectorAll('[data-p3d-kind-toggle]').forEach(btn=>btn.addEventListener('click',()=>{const kind=btn.dataset.p3dKindToggle,next=new Set(Array.isArray(state.hiddenKinds)?state.hiddenKinds:[]);next.has(kind)?next.delete(kind):next.add(kind);state.hiddenKinds=[...next];render(num(el('pL')?.value),num(el('pW')?.value));}));\n    root.querySelector('[data-p3d-kind-reset]')?.addEventListener('click',()=>{state.hiddenKinds=[];render(num(el('pL')?.value),num(el('pW')?.value));});\n    root.querySelectorAll('[data-p3d-part]').forEach(btn=>btn.addEventListener('click',()=>{const k=btn.dataset.p3dPart;state.selected=state.selected===k?'all':k;render(num(el('pL')?.value),num(el('pW')?.value));}));"
if "data-p3d-kind-toggle]').forEach" not in s:
    if anchor not in s:
        raise SystemExit('listener target not found')
    s = s.replace(anchor, replacement, 1)

# Respect hidden groups in detailed layer dimensions.
s = s.replace("        paintMeasure('layer-runner',[stackX,y0,stackZ],[stackX,y1,stackZ],fmtMm(runnerT/S),{compact:true,kind:'layer',labelDx:-24,minPx:5});", "        if(kindVisible('runner'))paintMeasure('layer-runner',[stackX,y0,stackZ],[stackX,y1,stackZ],fmtMm(runnerT/S),{compact:true,kind:'layer',labelDx:-24,minPx:5});", 1)
s = s.replace("        paintMeasure('layer-block',[stackX,y1,stackZ],[stackX,y2,stackZ],fmtMm(blockH/S),{compact:true,kind:'layer',labelDx:-24,minPx:5});", "        if(kindVisible('block'))paintMeasure('layer-block',[stackX,y1,stackZ],[stackX,y2,stackZ],fmtMm(blockH/S),{compact:true,kind:'layer',labelDx:-24,minPx:5});", 1)
s = s.replace("        paintMeasure('layer-bind',[stackX,y2,stackZ],[stackX,y3,stackZ],fmtMm(bindT/S),{compact:true,kind:'layer',labelDx:-24,minPx:5});", "        if(kindVisible('cross'))paintMeasure('layer-bind',[stackX,y2,stackZ],[stackX,y3,stackZ],fmtMm(bindT/S),{compact:true,kind:'layer',labelDx:-24,minPx:5});", 1)
s = s.replace("        paintMeasure('layer-deck',[stackX,deckBottom,stackZ],[stackX,deckTop,stackZ],fmtMm(deckThicknessMm),{compact:true,kind:'layer',labelDx:-24,minPx:5});", "        if(kindVisible('deck'))paintMeasure('layer-deck',[stackX,deckBottom,stackZ],[stackX,deckTop,stackZ],fmtMm(deckThicknessMm),{compact:true,kind:'layer',labelDx:-24,minPx:5});", 1)

js.write_text(s, encoding='utf-8')

css = Path('assets/theme-industrial-v130.css')
c = css.read_text(encoding='utf-8')
marker = '/* palletPartLegendV1130 */'
patch = r'''
/* palletPartLegendV1130 */
.palletPartLegend{display:flex;align-items:center;justify-content:center;gap:7px;flex-wrap:wrap;margin:8px auto 2px;padding:6px 8px;width:max-content;max-width:100%;border:1px solid #e5ddd3;border-radius:12px;background:rgba(255,252,247,.9);box-shadow:0 5px 16px rgba(75,53,34,.05)}
.palletPartLegendTitle{padding:0 3px;color:#9b7656;font-size:9px;font-weight:900;letter-spacing:.11em}
.palletPartLegend button{display:inline-flex;align-items:center;gap:6px;min-height:30px;padding:5px 9px;border:1px solid #e0d4c7;border-radius:9px;background:#fff;color:#5b5149;font-size:10px;font-weight:850;box-shadow:none;transition:opacity .16s,border-color .16s,background .16s,transform .16s}
.palletPartLegend button:hover{transform:translateY(-1px);border-color:#cdb79f;background:#fffaf3}
.palletPartLegend button.off{opacity:.42;background:#f4f1ed;text-decoration:line-through}
.palletPartLegend button.off .legendDot{filter:grayscale(.8)}
.legendDot{display:inline-block;flex:0 0 10px;width:10px;height:10px;border-radius:3px;box-shadow:inset 0 0 0 1px rgba(70,42,20,.12)}
.legendDot.deck{background:#efd1a4}.legendDot.cross{background:#d9aa6b}.legendDot.runner{background:#b97849}.legendDot.block{background:#915b3b}
.palletPartLegendReset{color:#8b5b31!important;border-color:#dec8ae!important;background:#f8ecdd!important}
.palletPartLegendReset[hidden]{display:none!important}
html[data-theme="dark"] .palletPartLegend{background:rgba(41,35,30,.94);border-color:#4b4037}
html[data-theme="dark"] .palletPartLegendTitle{color:#caa47f}
html[data-theme="dark"] .palletPartLegend button{background:#302a25;color:#e8ddd2;border-color:#4d4035}
html[data-theme="dark"] .palletPartLegend button:hover{background:#3a3028;border-color:#6b513c}
html[data-theme="dark"] .palletPartLegend button.off{background:#272421;color:#9e9690}
html[data-theme="dark"] .palletPartLegendReset{background:#3e3126!important;color:#edc99f!important;border-color:#634b38!important}
@media(max-width:620px){.palletPartLegend{gap:5px;padding:5px 6px;margin-top:6px}.palletPartLegendTitle{width:100%;text-align:center}.palletPartLegend button{min-height:34px;padding:6px 8px;font-size:9px}.legendDot{width:9px;height:9px;flex-basis:9px}}
'''
if marker not in c:
    css.write_text(c + '\n\n' + patch, encoding='utf-8')

idx = Path('index.html')
h = idx.read_text(encoding='utf-8')
h = re.sub(r'assets/theme-industrial-v130\.css\?v=\d+', 'assets/theme-industrial-v130.css?v=180', h)
h = re.sub(r'assets/pallet3d-v10\.js\?v=\d+', 'assets/pallet3d-v10.js?v=130', h)
idx.write_text(h, encoding='utf-8')
