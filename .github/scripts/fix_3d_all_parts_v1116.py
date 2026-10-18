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

# 1) Selection is for every physical pallet part, not only the top deck.
old="""    const inspectable=[];\n    function mat(kind,i){const on=selected==='all'||selected===kind,map=textures[kind].clone();map.needsUpdate=true;map.offset.x=(i*.149)%1;return new THREE.MeshStandardMaterial({map,color:on?colors[kind][i%colors[kind].length]:0xbdb8b0,roughness:.78,metalness:0,transparent:!on,opacity:on?1:.15,depthWrite:on,emissive:selected===kind?0x14382e:0,emissiveIntensity:selected===kind?.09:0});}\n    function piece(kind,dx,dy,dz,x,y,z,i,group){const g=roundedBoxGeometry(dx,dy,dz,kind==='block'?.055:.035),m=new THREE.Mesh(g,mat(kind,i));m.position.set(x,y,z);m.castShadow=true;m.receiveShadow=true;if(kind==='deck'){m.userData.palletInspect={name:'Настил',index:i,t:deckThicknessMm,w:deckWidthMm,l:deckLengthMm,n:deckCount};m.userData.baseEmissiveHex=selected===kind?0x14382e:0;m.userData.baseEmissiveIntensity=selected===kind?.09:0;inspectable.push(m);}group.add(m);return m;}\n"""
new="""    const inspectable=[];\n    const inspectShort={deck:'Н',cross:'П',runner:'Л',block:'Ш'};\n    function mat(kind,i){const on=selected==='all'||selected===kind,map=textures[kind].clone();map.needsUpdate=true;map.offset.x=(i*.149)%1;return new THREE.MeshStandardMaterial({map,color:on?colors[kind][i%colors[kind].length]:0xbdb8b0,roughness:.78,metalness:0,transparent:!on,opacity:on?1:.15,depthWrite:on,emissive:selected===kind?0x14382e:0,emissiveIntensity:selected===kind?.09:0});}\n    function piece(kind,dx,dy,dz,x,y,z,i,group){const g=roundedBoxGeometry(dx,dy,dz,kind==='block'?.055:.035),m=new THREE.Mesh(g,mat(kind,i));m.position.set(x,y,z);m.castShadow=true;m.receiveShadow=true;group.add(m);return m;}\n    function registerInspectable(mesh,kind,index,name,t,w,l,n){if(!mesh)return mesh;mesh.userData.palletInspect={name,kind,index,short:inspectShort[kind]||'',t:num(t),w:num(w),l:num(l),n:Math.max(1,Math.round(num(n,1)))};mesh.userData.baseEmissiveHex=selected===kind?0x14382e:0;mesh.userData.baseEmissiveIntensity=selected===kind?.09:0;inspectable.push(mesh);return mesh;}\n"""
if old not in js:
    raise SystemExit('inspectable/piece block not found')
js=js.replace(old,new,1)

old_runner="""    runnerLengths.forEach((mm,i)=>{const rz=clamp(mm*S,Math.min(PL*.55,10.5),PL);piece('runner',runnerActualW,runnerT,rz,runnerXs[i],runnerT/2,0,i,groups.runner);});\n"""
new_runner="""    runnerLengths.forEach((mm,i)=>{const rz=clamp(mm*S,Math.min(PL*.55,10.5),PL),mesh=piece('runner',runnerActualW,runnerT,rz,runnerXs[i],runnerT/2,0,i,groups.runner);registerInspectable(mesh,'runner',i,'Лыжа',runnerT/S,runnerActualW/S,rz/S,runnerLengths.length);});\n"""
if old_runner not in js: raise SystemExit('runner loop not found')
js=js.replace(old_runner,new_runner,1)

old_block="""    for(let zi=0;zi<3;zi++)for(let xi=0;xi<3;xi++){const idx=zi*3+xi;if(idx>=blockCount)continue;const centerType=(xi===1),bx=centerType?blockXSize2:blockXSize1,bz=centerType?blockZSize2:blockZSize1;const sx=xi===0?-1:xi===2?1:0,sz=zi===0?-1:zi===2?1:0;const bxPos=sx===0?0:sx*Math.max(0,PW/2-bx/2-.03),bzPos=sz===0?0:sz*Math.max(0,PL/2-bz/2-.03);blockRows[zi]=bzPos;blockPoints.push({x:bxPos,z:bzPos,bx,bz});piece('block',bx,blockH,bz,bxPos,blockY,bzPos,idx,groups.block);}\n"""
new_block="""    for(let zi=0;zi<3;zi++)for(let xi=0;xi<3;xi++){const idx=zi*3+xi;if(idx>=blockCount)continue;const centerType=(xi===1),bx=centerType?blockXSize2:blockXSize1,bz=centerType?blockZSize2:blockZSize1;const sx=xi===0?-1:xi===2?1:0,sz=zi===0?-1:zi===2?1:0;const bxPos=sx===0?0:sx*Math.max(0,PW/2-bx/2-.03),bzPos=sz===0?0:sz*Math.max(0,PL/2-bz/2-.03);blockRows[zi]=bzPos;blockPoints.push({x:bxPos,z:bzPos,bx,bz});const mesh=piece('block',bx,blockH,bz,bxPos,blockY,bzPos,idx,groups.block);registerInspectable(mesh,'block',idx,'Шашка',blockH/S,bx/S,bz/S,blockCount);}\n"""
if old_block not in js: raise SystemExit('block loop not found')
js=js.replace(old_block,new_block,1)

old_cross="""    const bindY=runnerT+blockH+bindT/2,bindZ=[-PL/2+bindDepth/2+.02,0,PL/2-bindDepth/2-.02];bindZ.forEach((z,i)=>piece('cross',PW,bindT,bindDepth,0,bindY,z,i,groups.cross));\n"""
new_cross="""    const bindY=runnerT+blockH+bindT/2,bindZ=[-PL/2+bindDepth/2+.02,0,PL/2-bindDepth/2-.02];bindZ.forEach((z,i)=>{const mesh=piece('cross',PW,bindT,bindDepth,0,bindY,z,i,groups.cross);registerInspectable(mesh,'cross',i,'Поперечина',bindT/S,bindDepth/S,PW/S,bindZ.length);});\n"""
if old_cross not in js: raise SystemExit('cross loop not found')
js=js.replace(old_cross,new_cross,1)

old_deck="""    topXs.forEach((x,i)=>{piece('deck',actualDeckW,deckT,deckL,x,topY,0,i,groups.deck);if(selected==='all'||selected==='deck')bindZ.forEach((z,zi)=>{const edgeBoard=i===0||i===topXs.length-1,edgeCross=zi===0||zi===bindZ.length-1;if(edgeBoard&&edgeCross)cornerTriple(x,nailY,z,Math.min(.08,actualDeckW*.24));else pairNails(nail40,groups.deck,x,nailY,z,Math.min(.06,actualDeckW*.22),-1);});});\n"""
new_deck="""    topXs.forEach((x,i)=>{const mesh=piece('deck',actualDeckW,deckT,deckL,x,topY,0,i,groups.deck);registerInspectable(mesh,'deck',i,'Настил',deckThicknessMm,deckWidthMm,deckLengthMm,deckCount);if(selected==='all'||selected==='deck')bindZ.forEach((z,zi)=>{const edgeBoard=i===0||i===topXs.length-1,edgeCross=zi===0||zi===bindZ.length-1;if(edgeBoard&&edgeCross)cornerTriple(x,nailY,z,Math.min(.08,actualDeckW*.24));else pairNails(nail40,groups.deck,x,nailY,z,Math.min(.06,actualDeckW*.22),-1);});});\n"""
if old_deck not in js: raise SystemExit('deck loop not found')
js=js.replace(old_deck,new_deck,1)

# 2) Generic wording and no picker at all in normal 3D mode.
js=js.replace('<div class="palletPickHint">Нажмите на верхнюю доску — покажу её размер и количество</div>','<div class="palletPickHint" '+"${mode==='3d'?'hidden':''}"+'>Выберите деталь: настил, поперечину, лыжу или шашку</div>',1)

old_overlay="""    const pickOverlay=document.createElement('div');pickOverlay.className='palletBoardPickOverlay';stage?.appendChild(pickOverlay);\n    const pickButtons=inspectable.map((mesh,i)=>{const btn=document.createElement('button');btn.type='button';btn.className='palletBoardPickZone';btn.setAttribute('aria-label',`Выбрать доску настила №${i+1}`);btn.dataset.board=String(i);btn.innerHTML=`<span>${i+1}</span>`;pickOverlay.appendChild(btn);return btn;});\n"""
new_overlay="""    const pickerEnabled=mode==='top'||mode==='side'||mode==='explode';\n    const pickOverlay=document.createElement('div');pickOverlay.className='palletBoardPickOverlay';pickOverlay.hidden=!pickerEnabled;stage?.appendChild(pickOverlay);\n    const pickButtons=inspectable.map((mesh,i)=>{const info=mesh.userData.palletInspect||{},btn=document.createElement('button');btn.type='button';btn.className='palletBoardPickZone';btn.dataset.pickIndex=String(i);btn.dataset.kind=info.kind||'';btn.setAttribute('aria-label',`Выбрать ${String(info.name||'деталь').toLowerCase()} №${Number(info.index||0)+1}`);btn.innerHTML=`<span>${info.short||''}${Number(info.index||0)+1}</span>`;pickOverlay.appendChild(btn);return btn;});\n"""
if old_overlay not in js: raise SystemExit('picker overlay block not found')
js=js.replace(old_overlay,new_overlay,1)

old_show="""    const showInspect=(mesh)=>{const info=mesh?.userData?.palletInspect;if(!info)return false;resetInspectHighlight();mesh.material.emissive.setHex(0x8a5525);mesh.material.emissiveIntensity=.42;const boardNo=Number(info.index||0)+1,qty=Math.max(1,Math.round(num(el('qty')?.value,1))),total=info.n*qty;if(partInspector){partInspector.hidden=false;partInspector.querySelector('strong').textContent=`Настил №${boardNo}`;partInspector.querySelector('span').textContent=`${fmtMm(info.t)} × ${fmtMm(info.w)} × ${fmtMm(info.l)} мм`;partInspector.querySelector('b').textContent=`${info.n} шт. / поддон · ${total.toLocaleString('ru-RU')} шт. / заказ`;}setPickHint(`Выбрана доска №${boardNo} · ${fmtMm(info.t)} × ${fmtMm(info.w)} × ${fmtMm(info.l)} мм`,true);window.dispatchEvent(new CustomEvent('pallet3d:partselect',{detail:{...info,boardNo,per:info.n,total}}));renderer.render(scene,camera);lastInspectAt=performance.now();return true;};\n"""
new_show="""    const showInspect=(mesh)=>{const info=mesh?.userData?.palletInspect;if(!info)return false;resetInspectHighlight();mesh.material.emissive.setHex(0x8a5525);mesh.material.emissiveIntensity=.42;const itemNo=Number(info.index||0)+1,qty=Math.max(1,Math.round(num(el('qty')?.value,1))),total=info.n*qty;if(partInspector){partInspector.hidden=false;partInspector.querySelector('strong').textContent=`${info.name} №${itemNo}`;partInspector.querySelector('span').textContent=`${fmtMm(info.t)} × ${fmtMm(info.w)} × ${fmtMm(info.l)} мм`;partInspector.querySelector('b').textContent=`${info.n} шт. / поддон · ${total.toLocaleString('ru-RU')} шт. / заказ`;}setPickHint(`Выбрано: ${info.name} №${itemNo} · ${fmtMm(info.t)} × ${fmtMm(info.w)} × ${fmtMm(info.l)} мм`,true);window.dispatchEvent(new CustomEvent('pallet3d:partselect',{detail:{...info,itemNo,boardNo:itemNo,per:info.n,total}}));renderer.render(scene,camera);lastInspectAt=performance.now();return true;};\n"""
if old_show not in js: raise SystemExit('showInspect block not found')
js=js.replace(old_show,new_show,1)

# 3) Replace deck-only rectangle positioning with projected bounding boxes for every part.
pattern=re.compile(r"    updatePickButtons=\(\)=>\{\n      if\(!stage\|\|!pickButtons\.length\)return;\n.*?\n    \};\n    pickButtons\.forEach\(\(btn,i\)=>btn\.addEventListener\('click',e=>\{e\.preventDefault\(\);e\.stopPropagation\(\);const mesh=inspectable\[i\];if\(mesh\)showInspect\(mesh\);previewCard\?\.classList\.remove\('partPickMode'\);\}\)\);",re.S)
m=pattern.search(js)
if not m: raise SystemExit('updatePickButtons block not found')
new_pick="""    updatePickButtons=()=>{\n      if(!stage||!pickButtons.length)return;\n      if(!pickerEnabled){pickOverlay.hidden=true;pickButtons.forEach(btn=>btn.hidden=true);return;}\n      pickOverlay.hidden=false;\n      const sr=stage.getBoundingClientRect(),cr=canvas.getBoundingClientRect();\n      if(!sr.width||!sr.height||!cr.width||!cr.height)return;\n      scene.updateMatrixWorld(true);camera.updateMatrixWorld(true);\n      const visibleKinds=mode==='top'?new Set(['deck','cross']):new Set(['deck','cross','runner','block']);\n      const cornerBits=[[-1,-1,-1],[1,-1,-1],[-1,1,-1],[1,1,-1],[-1,-1,1],[1,-1,1],[-1,1,1],[1,1,1]];\n      pickButtons.forEach((btn,i)=>{\n        const mesh=inspectable[i],info=mesh?.userData?.palletInspect;if(!mesh||!info||!visibleKinds.has(info.kind)){btn.hidden=true;return;}\n        mesh.geometry.computeBoundingBox?.();const bb=mesh.geometry.boundingBox;if(!bb){btn.hidden=true;return;}\n        const cx=(bb.min.x+bb.max.x)/2,cy=(bb.min.y+bb.max.y)/2,cz=(bb.min.z+bb.max.z)/2,hx=(bb.max.x-bb.min.x)/2,hy=(bb.max.y-bb.min.y)/2,hz=(bb.max.z-bb.min.z)/2,pts=[];\n        for(const [sx,sy,sz] of cornerBits){const v=new THREE.Vector3(cx+sx*hx,cy+sy*hy,cz+sz*hz).applyMatrix4(mesh.matrixWorld).project(camera);if(!Number.isFinite(v.x)||!Number.isFinite(v.y)||v.z<-1.1||v.z>1.1)continue;pts.push({x:cr.left-sr.left+(v.x*.5+.5)*cr.width,y:cr.top-sr.top+(-v.y*.5+.5)*cr.height});}\n        if(pts.length<4){btn.hidden=true;return;}\n        let minX=Math.min(...pts.map(p=>p.x)),maxX=Math.max(...pts.map(p=>p.x)),minY=Math.min(...pts.map(p=>p.y)),maxY=Math.max(...pts.map(p=>p.y));\n        if(maxX<0||maxY<0||minX>sr.width||minY>sr.height){btn.hidden=true;return;}\n        const pad=info.kind==='block'?8:6;minX=clamp(minX-pad,0,sr.width-18);maxX=clamp(maxX+pad,18,sr.width);minY=clamp(minY-pad,0,sr.height-24);maxY=clamp(maxY+pad,24,sr.height);\n        btn.hidden=false;btn.style.left=`${minX}px`;btn.style.top=`${minY}px`;btn.style.width=`${Math.max(20,maxX-minX)}px`;btn.style.height=`${Math.max(28,maxY-minY)}px`;btn.style.zIndex=String(info.kind==='deck'?4:info.kind==='cross'?3:info.kind==='block'?2:1);\n      });\n    };\n    pickButtons.forEach((btn,i)=>btn.addEventListener('click',e=>{e.preventDefault();e.stopPropagation();if(!pickerEnabled)return;const mesh=inspectable[i];if(mesh)showInspect(mesh);previewCard?.classList.remove('partPickMode');}));"""
js=js[:m.start()]+new_pick+js[m.end():]

# Stop all canvas picking and pointer affordance in normal 3D mode.
js=js.replace("const selectAt=(clientX,clientY)=>{const projected=pickDeckByProjection(clientX,clientY);if(projected)return showInspect(projected.object);const hit=pickAt(clientX,clientY);return hit?showInspect(hit.object):false;};","const selectAt=(clientX,clientY)=>{if(!pickerEnabled)return false;const projected=pickDeckByProjection(clientX,clientY);if(projected)return showInspect(projected.object);const hit=pickAt(clientX,clientY);return hit?showInspect(hit.object):false;};",1)
js=js.replace("canvas.addEventListener('pointermove',e=>{if(e.buttons!==0)return;const hit=pickAt(e.clientX,e.clientY);canvas.style.cursor=hit?'pointer':((mode==='top'||mode==='side')?'default':'grab');},true);","canvas.addEventListener('pointermove',e=>{if(e.buttons!==0)return;if(!pickerEnabled){canvas.style.cursor='grab';return;}const hit=pickAt(e.clientX,e.clientY);canvas.style.cursor=hit?'pointer':((mode==='top'||mode==='side')?'default':'grab');},true);",1)

# 4) Smart-tool wording and selection flow: default to Top view, never expose pick zones in normal 3D.
smart=smart.replace('/* Pallet Tools smart production helpers v1.1.14 */','/* Pallet Tools smart production helpers v1.1.16 */',1)
smart=smart.replace('<small>3 · ДЕТАЛЬ ИЗ 3D</small><h3 id="smartSelectedTitle">Выберите доску</h3><p id="smartSelectedDims">Нажмите на верхнюю доску прямо на 3D-модели.</p><div class="smartSelectedQty" id="smartSelectedQty">Размеры и количество появятся здесь.</div><button class="smartSelect3D" id="smartSelect3D" type="button">Показать 3D и выбрать доску</button>','<small>3 · ДЕТАЛЬ ИЗ МОДЕЛИ</small><h3 id="smartSelectedTitle">Выберите деталь</h3><p id="smartSelectedDims">Можно выбрать настил, поперечину, лыжу или шашку.</p><div class="smartSelectedQty" id="smartSelectedQty">Размеры и количество появятся здесь.</div><button class="smartSelect3D" id="smartSelect3D" type="button">Показать модель и выбрать деталь</button>',1)

old_click="""    $('smartSelect3D')?.addEventListener('click',()=>{\n      const preview=$('palletPreview3D')?.closest('.previewCard');\n      const mode3d=$('palletPreview3D')?.querySelector('[data-p3d-mode=\"3d\"]');\n      if(mode3d&&!mode3d.classList.contains('active'))mode3d.click();\n      setTimeout(()=>{\n        const livePreview=$('palletPreview3D')?.closest('.previewCard')||preview;\n        livePreview?.classList.add('partPickMode');\n        livePreview?.scrollIntoView({behavior:'smooth',block:'center'});\n        const hint=document.querySelector('.palletPickHint');\n        if(hint){hint.textContent='Режим выбора: нажмите на подсвеченную область любой верхней доски';hint.classList.add('attention');}\n        setTimeout(()=>hint?.classList.remove('attention'),2600);\n      },90);\n    });\n"""
new_click="""    $('smartSelect3D')?.addEventListener('click',()=>{\n      const preview=$('palletPreview3D')?.closest('.previewCard');\n      const active=$('palletPreview3D')?.querySelector('[data-p3d-mode].active');\n      if(!active||active.dataset.p3dMode==='3d')$('palletPreview3D')?.querySelector('[data-p3d-mode=\"top\"]')?.click();\n      setTimeout(()=>{\n        const livePreview=$('palletPreview3D')?.closest('.previewCard')||preview;\n        livePreview?.classList.add('partPickMode');\n        livePreview?.scrollIntoView({behavior:'smooth',block:'center'});\n        const hint=document.querySelector('.palletPickHint');\n        if(hint){hint.hidden=false;hint.textContent='Режим выбора: нажмите на подсвеченную деталь';hint.classList.add('attention');}\n        setTimeout(()=>hint?.classList.remove('attention'),2600);\n      },90);\n    });\n"""
if old_click not in smart: raise SystemExit('smart picker click block not found')
smart=smart.replace(old_click,new_click,1)

old_empty="""    if(!selectedPart){title.textContent='Выберите доску';dims.textContent='Нажмите кнопку ниже — откроется 3D. Затем нажмите на любую верхнюю доску.';qty.textContent='Выбранная доска подсветится, а размеры появятся здесь.';return;}\n    title.textContent=`${selectedPart.name} №${selectedPart.boardNo}`;\n"""
new_empty="""    if(!selectedPart){title.textContent='Выберите деталь';dims.textContent='Нажмите кнопку ниже. Выбор доступен в режимах «Сверху», «Сбоку» и «Разнести».';qty.textContent='Настил, поперечина, лыжа или шашка подсветится, а размеры появятся здесь.';return;}\n    title.textContent=`${selectedPart.name} №${selectedPart.itemNo||selectedPart.boardNo||1}`;\n"""
if old_empty not in smart: raise SystemExit('smart empty block not found')
smart=smart.replace(old_empty,new_empty,1)

# 5) Selection overlay styling: abbreviations identify the type of part.
if 'allPartPickerV1116' not in css:
    css += r'''

/* allPartPickerV1116 */
.palletBoardPickZone[data-kind="deck"] span{background:#234f78!important}
.palletBoardPickZone[data-kind="cross"] span{background:#6d4d2f!important}
.palletBoardPickZone[data-kind="runner"] span{background:#2d6652!important}
.palletBoardPickZone[data-kind="block"] span{background:#8a5b2f!important}
.palletBoardPickOverlay[hidden],.palletPickHint[hidden]{display:none!important}
'''

# 6) Version and cache bump.
if 'Pallet Tools · v1.1.15' not in html: raise SystemExit('html version marker missing')
html=html.replace('Pallet Tools · v1.1.15','Pallet Tools · v1.1.16')
for pattern in [r'assets/theme-industrial-v130\.css\?v=(\d+)',r'assets/pallet3d-v10\.js\?v=(\d+)',r'assets/smart-tools-v1\.js\?v=(\d+)']:
    m=re.search(pattern,html)
    if not m: raise SystemExit(f'cache marker missing: {pattern}')
    html=html[:m.start(1)]+str(int(m.group(1))+1)+html[m.end(1):]
css=css.replace('Pallet Tools · v1.1.15','Pallet Tools · v1.1.16').replace('обновление №349','обновление №350')
js=js.replace('Pallet Tools · v1.1.15','Pallet Tools · v1.1.16')

html_path.write_text(html,encoding='utf-8')
css_path.write_text(css,encoding='utf-8')
js_path.write_text(js,encoding='utf-8')
smart_path.write_text(smart,encoding='utf-8')
