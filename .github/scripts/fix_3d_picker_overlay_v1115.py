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

# Keep a callable no-op available before the first draw; it is replaced later.
if 'let updatePickButtons=()=>{};' not in js:
    marker='    function draw(){'
    if marker not in js: raise SystemExit('draw function not found')
    js=js.replace(marker,'    let updatePickButtons=()=>{};\n'+marker,1)

old_draw="function draw(){if(mode==='top'){camera.up.set(0,0,-1);camera.position.set(0,Math.max(PW,PL)*2.55,.001);camera.lookAt(0,topY*.55,0);}else if(mode==='side'){camera.up.set(0,1,0);camera.position.set(Math.max(PW,PL)*2.0,Math.max(4.2,topY*2.0),0);camera.lookAt(0,topY*.55,0);}else{camera.up.set(0,1,0);const cy=Math.sin(pitch)*distance,rad=Math.cos(pitch)*distance;camera.position.set(Math.cos(yaw)*rad,cy+2.0,Math.sin(yaw)*rad);camera.lookAt(0,exploded?3.1:topY*.42,0);}renderer.render(scene,camera);updateOnModelMeasures();}"
new_draw="function draw(){if(mode==='top'){camera.up.set(0,0,-1);camera.position.set(0,Math.max(PW,PL)*2.55,.001);camera.lookAt(0,topY*.55,0);}else if(mode==='side'){camera.up.set(0,1,0);camera.position.set(Math.max(PW,PL)*2.0,Math.max(4.2,topY*2.0),0);camera.lookAt(0,topY*.55,0);}else{camera.up.set(0,1,0);const cy=Math.sin(pitch)*distance,rad=Math.cos(pitch)*distance;camera.position.set(Math.cos(yaw)*rad,cy+2.0,Math.sin(yaw)*rad);camera.lookAt(0,exploded?3.1:topY*.42,0);}renderer.render(scene,camera);updateOnModelMeasures();updatePickButtons();}"
if old_draw in js:
    js=js.replace(old_draw,new_draw,1)
elif new_draw not in js:
    raise SystemExit('draw body not found')

anchor="""    const canvas=renderer.domElement;\n    const partInspector=root.querySelector('.palletPartInspector');\n    const pickHint=root.querySelector('.palletPickHint');\n    const raycaster=new THREE.Raycaster(),pickPoint=new THREE.Vector2();\n"""
replacement="""    const canvas=renderer.domElement;\n    const partInspector=root.querySelector('.palletPartInspector');\n    const pickHint=root.querySelector('.palletPickHint');\n    const pickOverlay=document.createElement('div');pickOverlay.className='palletBoardPickOverlay';stage?.appendChild(pickOverlay);\n    const pickButtons=inspectable.map((mesh,i)=>{const btn=document.createElement('button');btn.type='button';btn.className='palletBoardPickZone';btn.setAttribute('aria-label',`Выбрать доску настила №${i+1}`);btn.dataset.board=String(i);btn.innerHTML=`<span>${i+1}</span>`;pickOverlay.appendChild(btn);return btn;});\n    const raycaster=new THREE.Raycaster(),pickPoint=new THREE.Vector2();\n"""
if 'palletBoardPickOverlay' not in js:
    if anchor not in js: raise SystemExit('picker anchor not found')
    js=js.replace(anchor,replacement,1)

anchor2="""    const selectAt=(clientX,clientY)=>{const projected=pickDeckByProjection(clientX,clientY);if(projected)return showInspect(projected.object);const hit=pickAt(clientX,clientY);return hit?showInspect(hit.object):false;};\n    canvas.addEventListener('pointerdown',e=>{inspectDown={x:e.clientX,y:e.clientY};},true);\n"""
replacement2="""    const selectAt=(clientX,clientY)=>{const projected=pickDeckByProjection(clientX,clientY);if(projected)return showInspect(projected.object);const hit=pickAt(clientX,clientY);return hit?showInspect(hit.object):false;};\n    updatePickButtons=()=>{\n      if(!stage||!pickButtons.length)return;\n      const sr=stage.getBoundingClientRect(),cr=canvas.getBoundingClientRect();\n      if(!sr.width||!sr.height||!cr.width||!cr.height)return;\n      scene.updateMatrixWorld(true);camera.updateMatrixWorld(true);\n      const deckLift=groups.deck.position.y||0,halfW=actualDeckW/2,halfL=deckL/2,y=topY+deckT/2+deckLift+.035;\n      const project=(x,z)=>{const v=new THREE.Vector3(x,y,z).project(camera);if(!Number.isFinite(v.x)||!Number.isFinite(v.y)||v.z<-1.1||v.z>1.1)return null;return{x:cr.left-sr.left+(v.x*.5+.5)*cr.width,y:cr.top-sr.top+(-v.y*.5+.5)*cr.height};};\n      pickButtons.forEach((btn,i)=>{const x=topXs[i]??inspectable[i]?.position.x??0,pts=[project(x-halfW,-halfL),project(x+halfW,-halfL),project(x+halfW,halfL),project(x-halfW,halfL)];if(pts.some(p=>!p)){btn.hidden=true;return;}let minX=Math.min(...pts.map(p=>p.x)),maxX=Math.max(...pts.map(p=>p.x)),minY=Math.min(...pts.map(p=>p.y)),maxY=Math.max(...pts.map(p=>p.y));const pad=7;minX-=pad;maxX+=pad;minY-=pad;maxY+=pad;btn.hidden=false;btn.style.left=`${minX}px`;btn.style.top=`${minY}px`;btn.style.width=`${Math.max(20,maxX-minX)}px`;btn.style.height=`${Math.max(30,maxY-minY)}px`;});\n    };\n    pickButtons.forEach((btn,i)=>btn.addEventListener('click',e=>{e.preventDefault();e.stopPropagation();const mesh=inspectable[i];if(mesh)showInspect(mesh);previewCard?.classList.remove('partPickMode');}));\n    updatePickButtons();\n    canvas.addEventListener('pointerdown',e=>{inspectDown={x:e.clientX,y:e.clientY};},true);\n"""
if 'pickButtons.forEach((btn,i)=>btn.addEventListener' not in js:
    if anchor2 not in js: raise SystemExit('selection anchor not found')
    js=js.replace(anchor2,replacement2,1)

smart=smart.replace("Режим выбора: нажмите прямо на верхнюю доску","Режим выбора: нажмите на подсвеченную область любой верхней доски",1)

if 'pickerOverlayV1115' not in css:
    css += r'''

/* pickerOverlayV1115 */
.palletBoardPickOverlay{position:absolute!important;inset:0!important;z-index:10!important;pointer-events:none!important;overflow:hidden!important}
.palletBoardPickZone{position:absolute!important;display:none!important;min-width:20px!important;min-height:30px!important;padding:0!important;border:2px solid transparent!important;border-radius:8px!important;background:transparent!important;box-shadow:none!important;pointer-events:none!important;touch-action:manipulation!important;cursor:pointer!important;transform:none!important}
.palletBoardPickZone span{display:none!important}
.previewCard.partPickMode .palletBoardPickZone:not([hidden]){display:block!important;pointer-events:auto!important;border-color:rgba(45,111,173,.68)!important;background:rgba(62,132,196,.16)!important;box-shadow:inset 0 0 0 1px rgba(255,255,255,.55),0 0 0 2px rgba(55,105,155,.09)!important}
.previewCard.partPickMode .palletBoardPickZone:hover,.previewCard.partPickMode .palletBoardPickZone:focus-visible{background:rgba(62,132,196,.28)!important;border-color:#2d6fad!important;outline:none!important;box-shadow:0 0 0 4px rgba(45,111,173,.18)!important}
.previewCard.partPickMode .palletBoardPickZone span{display:grid!important;place-items:center!important;position:absolute!important;left:50%!important;top:50%!important;transform:translate(-50%,-50%)!important;min-width:23px!important;height:23px!important;padding:0 5px!important;border-radius:999px!important;background:#234f78!important;color:#fff!important;font-size:10px!important;font-weight:900!important;line-height:1!important;box-shadow:0 2px 7px rgba(18,48,76,.28)!important}
html[data-theme="dark"] .previewCard.partPickMode .palletBoardPickZone:not([hidden]){border-color:rgba(107,169,224,.78)!important;background:rgba(71,137,196,.22)!important}
@media(max-width:620px){.previewCard.partPickMode .palletBoardPickZone:not([hidden]){background:rgba(62,132,196,.20)!important}.previewCard.partPickMode .palletBoardPickZone span{min-width:25px!important;height:25px!important;font-size:11px!important}}
'''

html=html.replace('Pallet Tools · v1.1.14</div>','Pallet Tools · v1.1.15</div>',1)
for pattern in [r'assets/theme-industrial-v130\.css\?v=(\d+)',r'assets/pallet3d-v10\.js\?v=(\d+)',r'assets/smart-tools-v1\.js\?v=(\d+)']:
    m=re.search(pattern,html)
    if not m: raise SystemExit(f'cache marker missing: {pattern}')
    html=html[:m.start(1)]+str(int(m.group(1))+1)+html[m.end(1):]
css=css.replace('Pallet Tools · v1.1.14','Pallet Tools · v1.1.15').replace('обновление №348','обновление №349')
js=js.replace('Pallet Tools · v1.1.14','Pallet Tools · v1.1.15')

html_path.write_text(html,encoding='utf-8')
css_path.write_text(css,encoding='utf-8')
js_path.write_text(js,encoding='utf-8')
smart_path.write_text(smart,encoding='utf-8')
