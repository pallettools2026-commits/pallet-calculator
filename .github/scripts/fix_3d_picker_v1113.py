from pathlib import Path
import re

html_path=Path('index.html')
css_path=Path('assets/theme-industrial-v130.css')
js_path=Path('assets/pallet3d-v10.js')
smart_path=Path('assets/smart-tools-v1.js')

html=html_path.read_text(encoding='utf-8')
css=css_path.read_text(encoding='utf-8')
js=js_path.read_text(encoding='utf-8')
smart=smart_path.read_text(encoding='utf-8')

# 1) Make the 3D selection state obvious inside the actual 3D stage.
old_stage='${dimensionOverlay}<div class="palletPartInspector" hidden><strong></strong><span></span><b></b></div></div>`;'
new_stage='${dimensionOverlay}<div class="palletPickHint">Нажмите на верхнюю доску — покажу её размер и количество</div><div class="palletPartInspector" hidden><strong></strong><span></span><b></b></div></div>`;'
if 'class="palletPickHint"' not in js:
    if old_stage not in js:
        raise SystemExit('3D stage marker not found')
    js=js.replace(old_stage,new_stage,1)

# 2) Replace the fragile 7 px pointer-up picker with a robust click/tap picker.
start="""    const canvas=renderer.domElement;\n    const partInspector=root.querySelector('.palletPartInspector');\n    const raycaster=new THREE.Raycaster(),pickPoint=new THREE.Vector2();\n    let inspectDown=null;\n    const resetInspectHighlight=()=>inspectable.forEach(mesh=>{if(!mesh.material)return;mesh.material.emissive.setHex(mesh.userData.baseEmissiveHex||0);mesh.material.emissiveIntensity=mesh.userData.baseEmissiveIntensity||0;});\n    const showInspect=(mesh)=>{const info=mesh?.userData?.palletInspect;if(!info)return;resetInspectHighlight();mesh.material.emissive.setHex(0x8a5525);mesh.material.emissiveIntensity=.42;const boardNo=Number(info.index||0)+1,qty=Math.max(1,Math.round(num(el('qty')?.value,1))),total=info.n*qty;if(partInspector){partInspector.hidden=false;partInspector.querySelector('strong').textContent=`Настил №${boardNo}`;partInspector.querySelector('span').textContent=`${fmtMm(info.t)} × ${fmtMm(info.w)} × ${fmtMm(info.l)} мм`;partInspector.querySelector('b').textContent=`${info.n} шт. / поддон · ${total.toLocaleString('ru-RU')} шт. / заказ`;}window.dispatchEvent(new CustomEvent('pallet3d:partselect',{detail:{...info,boardNo,per:info.n,total}}));renderer.render(scene,camera);};\n    canvas.addEventListener('pointerdown',e=>{inspectDown={x:e.clientX,y:e.clientY};},true);\n    canvas.addEventListener('pointerup',e=>{if(!inspectDown)return;const moved=Math.hypot(e.clientX-inspectDown.x,e.clientY-inspectDown.y);inspectDown=null;if(moved>7)return;const rect=canvas.getBoundingClientRect();if(!rect.width||!rect.height)return;pickPoint.x=((e.clientX-rect.left)/rect.width)*2-1;pickPoint.y=-((e.clientY-rect.top)/rect.height)*2+1;raycaster.setFromCamera(pickPoint,camera);const hit=raycaster.intersectObjects(inspectable,false)[0];if(hit)showInspect(hit.object);},true);\n"""
replacement="""    const canvas=renderer.domElement;\n    const partInspector=root.querySelector('.palletPartInspector');\n    const pickHint=root.querySelector('.palletPickHint');\n    const raycaster=new THREE.Raycaster(),pickPoint=new THREE.Vector2();\n    let inspectDown=null,lastInspectAt=0;\n    const resetInspectHighlight=()=>inspectable.forEach(mesh=>{if(!mesh.material)return;mesh.material.emissive.setHex(mesh.userData.baseEmissiveHex||0);mesh.material.emissiveIntensity=mesh.userData.baseEmissiveIntensity||0;});\n    const setPickHint=(text,selected=false)=>{if(!pickHint)return;pickHint.textContent=text;pickHint.classList.toggle('selected',selected);};\n    const showInspect=(mesh)=>{const info=mesh?.userData?.palletInspect;if(!info)return false;resetInspectHighlight();mesh.material.emissive.setHex(0x8a5525);mesh.material.emissiveIntensity=.42;const boardNo=Number(info.index||0)+1,qty=Math.max(1,Math.round(num(el('qty')?.value,1))),total=info.n*qty;if(partInspector){partInspector.hidden=false;partInspector.querySelector('strong').textContent=`Настил №${boardNo}`;partInspector.querySelector('span').textContent=`${fmtMm(info.t)} × ${fmtMm(info.w)} × ${fmtMm(info.l)} мм`;partInspector.querySelector('b').textContent=`${info.n} шт. / поддон · ${total.toLocaleString('ru-RU')} шт. / заказ`;}setPickHint(`Выбрана доска №${boardNo} · ${fmtMm(info.t)} × ${fmtMm(info.w)} × ${fmtMm(info.l)} мм`,true);window.dispatchEvent(new CustomEvent('pallet3d:partselect',{detail:{...info,boardNo,per:info.n,total}}));renderer.render(scene,camera);lastInspectAt=performance.now();return true;};\n    const pickAt=(clientX,clientY)=>{const rect=canvas.getBoundingClientRect();if(!rect.width||!rect.height)return null;pickPoint.x=((clientX-rect.left)/rect.width)*2-1;pickPoint.y=-((clientY-rect.top)/rect.height)*2+1;scene.updateMatrixWorld(true);camera.updateMatrixWorld(true);raycaster.setFromCamera(pickPoint,camera);return raycaster.intersectObjects(inspectable,false).find(hit=>hit.object?.userData?.palletInspect)||null;};\n    const selectAt=(clientX,clientY)=>{const hit=pickAt(clientX,clientY);return hit?showInspect(hit.object):false;};\n    canvas.addEventListener('pointerdown',e=>{inspectDown={x:e.clientX,y:e.clientY};},true);\n    canvas.addEventListener('pointerup',e=>{if(!inspectDown)return;const moved=Math.hypot(e.clientX-inspectDown.x,e.clientY-inspectDown.y);inspectDown=null;if(moved<=18)selectAt(e.clientX,e.clientY);},true);\n    canvas.addEventListener('click',e=>{if(performance.now()-lastInspectAt>220)selectAt(e.clientX,e.clientY);});\n    canvas.addEventListener('pointermove',e=>{if(e.buttons!==0)return;const hit=pickAt(e.clientX,e.clientY);canvas.style.cursor=hit?'pointer':((mode==='top'||mode==='side')?'default':'grab');},true);\n"""
if 'const pickAt=(clientX,clientY)' not in js:
    if start not in js:
        raise SystemExit('old picker block not found')
    js=js.replace(start,replacement,1)

# 3) Add a clear action button to the smart-tool card so the user does not have to guess where to click.
old_card='<div class="smartSelectedQty" id="smartSelectedQty">Размеры и количество появятся здесь.</div></div></article>'
new_card='<div class="smartSelectedQty" id="smartSelectedQty">Размеры и количество появятся здесь.</div><button class="smartSelect3D" id="smartSelect3D" type="button">Показать 3D и выбрать доску</button></div></article>'
if 'id="smartSelect3D"' not in smart:
    if old_card not in smart:
        raise SystemExit('smart selected card marker not found')
    smart=smart.replace(old_card,new_card,1)

old_bind="""    $('smartOptimizeApply')?.addEventListener('click',applySuggestion);\n    $('smartDensity')?.addEventListener('input',()=>{try{localStorage.setItem('pallettools:woodDensity',$('smartDensity').value);}catch(_){}update();});\n    return panel;\n"""
new_bind="""    $('smartOptimizeApply')?.addEventListener('click',applySuggestion);\n    $('smartDensity')?.addEventListener('input',()=>{try{localStorage.setItem('pallettools:woodDensity',$('smartDensity').value);}catch(_){}update();});\n    $('smartSelect3D')?.addEventListener('click',()=>{\n      const preview=$('palletPreview3D')?.closest('.previewCard');\n      preview?.classList.add('partPickMode');\n      preview?.scrollIntoView({behavior:'smooth',block:'center'});\n      const hint=document.querySelector('.palletPickHint');\n      if(hint){hint.textContent='Нажмите на любую верхнюю доску';hint.classList.add('attention');}\n      setTimeout(()=>hint?.classList.remove('attention'),2200);\n    });\n    return panel;\n"""
if "$('smartSelect3D')?.addEventListener" not in smart:
    if old_bind not in smart:
        raise SystemExit('smart binding marker not found')
    smart=smart.replace(old_bind,new_bind,1)

old_listener="window.addEventListener('pallet3d:partselect',e=>{selectedPart=e.detail||null;renderSelected();});"
new_listener="window.addEventListener('pallet3d:partselect',e=>{selectedPart=e.detail||null;document.querySelector('.previewCard')?.classList.remove('partPickMode');document.querySelector('.palletPickHint')?.classList.remove('attention');renderSelected();});"
if new_listener not in smart:
    if old_listener not in smart:
        raise SystemExit('partselect listener marker not found')
    smart=smart.replace(old_listener,new_listener,1)

# Make the empty-state instruction more explicit.
smart=smart.replace("dims.textContent='Нажмите на верхнюю доску прямо на 3D-модели.';qty.textContent='Размеры и количество появятся здесь.';return;","dims.textContent='Нажмите кнопку ниже — откроется 3D. Затем нажмите на любую верхнюю доску.';qty.textContent='Выбранная доска подсветится, а размеры появятся здесь.';return;",1)

# 4) Add strong visual affordances for selection, desktop and mobile, including dark theme.
if 'partPickerFixV1113' not in css:
    css += r'''

/* partPickerFixV1113 */
.palletPickHint{position:absolute!important;z-index:11!important;left:50%!important;top:66px!important;transform:translateX(-50%)!important;max-width:calc(100% - 28px)!important;padding:7px 11px!important;border:1px solid rgba(55,105,155,.22)!important;border-radius:999px!important;background:rgba(255,255,255,.93)!important;color:#315d87!important;font-size:10px!important;line-height:1.2!important;font-weight:900!important;box-shadow:0 5px 18px rgba(38,67,94,.10)!important;backdrop-filter:blur(7px)!important;pointer-events:none!important;white-space:nowrap!important;overflow:hidden!important;text-overflow:ellipsis!important;transition:transform .18s,box-shadow .18s,background .18s!important}
.palletPickHint.selected{background:rgba(241,249,244,.96)!important;border-color:#b9d9c7!important;color:#286047!important}
.palletPickHint.attention{transform:translateX(-50%) scale(1.04)!important;box-shadow:0 0 0 5px rgba(55,105,155,.13),0 7px 20px rgba(38,67,94,.15)!important}
.palletPartInspector{position:absolute!important;z-index:12!important;right:12px!important;bottom:12px!important;display:grid!important;gap:2px!important;min-width:205px!important;max-width:calc(100% - 24px)!important;padding:10px 12px!important;border:1px solid rgba(157,112,69,.34)!important;border-radius:12px!important;background:rgba(37,43,46,.93)!important;color:#fff!important;box-shadow:0 9px 24px rgba(31,35,37,.20)!important;backdrop-filter:blur(8px)!important;pointer-events:none!important}
.palletPartInspector[hidden]{display:none!important}.palletPartInspector strong{font-size:12px!important}.palletPartInspector span{font-size:11px!important;color:#f1d8b9!important}.palletPartInspector b{font-size:10px!important;color:#d5ddd9!important}
.previewCard.partPickMode .palletReferenceStage{box-shadow:0 0 0 4px rgba(55,105,155,.14),0 12px 30px rgba(41,64,84,.10)!important}.previewCard.partPickMode .palletReferenceHost canvas{cursor:pointer!important}
.smartSelect3D{width:100%!important;min-height:38px!important;margin-top:10px!important;border:1px solid #d7c1a8!important;border-radius:10px!important;background:#f5e8d9!important;color:#81552e!important;font-size:11px!important;font-weight:900!important;box-shadow:none!important}.smartSelect3D:hover{background:#edd9c3!important;border-color:#c9a985!important}
html[data-theme="dark"] .palletPickHint{background:rgba(28,34,36,.94)!important;border-color:#465e73!important;color:#c3d7ea!important}html[data-theme="dark"] .palletPickHint.selected{background:rgba(31,48,41,.95)!important;border-color:#426957!important;color:#bfe0cd!important}html[data-theme="dark"] .smartSelect3D{background:#342b23!important;border-color:#5b4939!important;color:#e0ac76!important}html[data-theme="dark"] .smartSelect3D:hover{background:#42352a!important}
@media(max-width:620px){.palletPickHint{top:58px!important;font-size:9px!important;max-width:calc(100% - 18px)!important;padding:6px 9px!important}.palletPartInspector{left:8px!important;right:8px!important;bottom:8px!important;min-width:0!important;max-width:none!important}.smartSelect3D{min-height:44px!important;font-size:12px!important}}
'''

# Version and cache busts.
html=html.replace('Pallet Tools · v1.1.12</div>','Pallet Tools · v1.1.13</div>',1)
for pattern in [r'assets/theme-industrial-v130\.css\?v=(\d+)',r'assets/pallet3d-v10\.js\?v=(\d+)',r'assets/smart-tools-v1\.js\?v=(\d+)']:
    m=re.search(pattern,html)
    if not m:
        raise SystemExit(f'cache marker missing: {pattern}')
    html=html[:m.start(1)]+str(int(m.group(1))+1)+html[m.end(1):]

css=css.replace('Pallet Tools · v1.1.12','Pallet Tools · v1.1.13').replace('обновление №346','обновление №347')
js=js.replace('Pallet Tools · v1.1.12','Pallet Tools · v1.1.13')

html_path.write_text(html,encoding='utf-8')
css_path.write_text(css,encoding='utf-8')
js_path.write_text(js,encoding='utf-8')
smart_path.write_text(smart,encoding='utf-8')
