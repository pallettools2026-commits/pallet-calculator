from pathlib import Path
import re

html_path = Path('truck-planner.html')
js_path = Path('assets/truck-planner-v9.js')
html = html_path.read_text(encoding='utf-8')
js = js_path.read_text(encoding='utf-8')

old_html = '''        <div class="tp-inline">
          <div class="tp-field"><label for="loadH">Высота 1 поддона <small>мм</small></label><input id="loadH" type="number" min="50" step="1" value="144" readonly title="EUR/EPAL: 22 + 78 + 22 + 22 = 144 мм"></div>
          <div class="tp-field"><label for="palletWeight">Масса 1 паллеты <small>кг</small></label><input id="palletWeight" type="number" min="0" step="1" value="25"></div>
        </div>'''
new_html = old_html + '''
        <div class="tp-inline">
          <div class="tp-field">
            <label for="packMode">Укладка в пачке</label>
            <select id="packMode">
              <option value="oneByOne">Один на один · до 20 шт.</option>
              <option value="mamaPapa">Мама‑папа · до 35 шт.</option>
            </select>
          </div>
          <div class="tp-field"><label for="packQty">Поддонов в пачке <small>шт.</small></label><input id="packQty" type="number" min="1" max="20" step="1" value="1"></div>
        </div>
        <div class="tp-note" id="packHint">Один на один: 1–20 поддонов в пачке. Высота считается по 144 мм на каждый поддон.</div>'''
if 'id="packMode"' not in html:
    assert old_html in html, 'HTML pallet controls block not found'
    html = html.replace(old_html, new_html, 1)
html = re.sub(r'truck-planner-v9\.js\?v=[0-9-]+', 'truck-planner-v9.js?v=20261018-2310', html, count=1)

old_e = "  p:$('palletPreset'),cp:$('customPallet'),pL:$('palletL'),pW:$('palletW'),loadH:$('loadH'),pw:$('palletWeight'),qty:$('desiredQty'),gap:$('clearance'),stack:$('stacking'),"
new_e = "  p:$('palletPreset'),cp:$('customPallet'),pL:$('palletL'),pW:$('palletW'),loadH:$('loadH'),pw:$('palletWeight'),packMode:$('packMode'),packQty:$('packQty'),packHint:$('packHint'),qty:$('desiredQty'),gap:$('clearance'),stack:$('stacking'),"
if old_e in js:
    js = js.replace(old_e, new_e, 1)
elif "packMode:$('packMode')" not in js:
    raise SystemExit('JS controls map block not found')

new_calc = r'''function calculate(){
  const v=getVehicle(),p=getPallet(),h=p.H||144,w=Number(E.pw.value)||0,gap=Math.max(0,Number(E.gap.value)||0),pk=bestPacking(v.L,v.W,p.L+gap,p.W+gap);
  const packMode=E.packMode?.value==='mamaPapa'?'mamaPapa':'oneByOne',maxPerPack=packMode==='mamaPapa'?35:20;
  const packQty=Math.max(1,Math.min(maxPerPack,Math.floor(Number(E.packQty?.value)||1)));
  if(E.packQty){E.packQty.max=maxPerPack;if(Number(E.packQty.value)!==packQty)E.packQty.value=packQty;}
  const nestedStep=100,packStep=packMode==='mamaPapa'?nestedStep:h,packH=h+(packQty-1)*packStep;
  const floor=pk.count,fitsHeight=packH<=v.H,layers=fitsHeight?(E.stack.checked?Math.max(1,Math.floor(v.H/packH)):1):0;
  const geo=floor*layers*packQty,byWeight=w>0?Math.floor(v.payload/w):Infinity,cap=Math.max(0,Math.min(geo,byWeight)),desired=Math.max(0,Math.floor(Number(E.qty.value)||0)),show=Math.min(cap,desired||cap);
  S={v,p,h,w,gap,pk,floor,layers,geo,byWeight,cap,show,packMode,packQty,packH,maxPerPack,packStep};
  E.cap.textContent=cap.toLocaleString('ru-RU');E.floor.textContent=floor.toLocaleString('ru-RU');E.layers.textContent=layers.toLocaleString('ru-RU');E.weight.textContent=Number.isFinite(byWeight)?byWeight.toLocaleString('ru-RU'):'∞';
  E.capSub.textContent=`поддонов · ${packQty} шт. в пачке`;E.floorSub.textContent='мест под пачки на полу кузова';E.layersSub.textContent=E.stack.checked?`пачек по высоте · пачка ${mm(packH)}`:`1 ярус пачек · пачка ${mm(packH)}`;E.weightSub.textContent=w?`грузоподъёмность ${kg(v.payload)}`:'масса не задана';
  if(E.packHint)E.packHint.textContent=packMode==='mamaPapa'?`Мама‑папа: 1–35 поддонов в пачке. Первый поддон ${h} мм, следующий шаг по высоте ${nestedStep} мм (доска 22 мм + шашка 78 мм).`:`Один на один: 1–20 поддонов в пачке. Каждый следующий поддон добавляет ${h} мм.`;
  E.vn.textContent=v.name;E.vd.textContent=`${mm(v.L)} × ${mm(v.W)} × ${mm(v.H)}`;E.pn.textContent=p.name;E.pd.textContent=`${mm(p.L)} × ${mm(p.W)} · 1 поддон ${mm(h)} · пачка ${packQty} шт. = ${mm(packH)}`;E.layout.textContent=`${pk.text} · ${packMode==='mamaPapa'?'мама‑папа':'один на один'}`;E.usage.textContent=`${show} из ${cap} поддонов · ${cap?Math.round(show/cap*100):0}% заполнения`;E.rendered.textContent=w?`Текущая масса: ${kg(show*w)} из ${kg(v.payload)}`:`В 3D: ${show} поддонов · до ${maxPerPack} в пачке`;
  const warn=[];if(!floor)warn.push('Пачка не помещается по длине или ширине кузова.');if(!fitsHeight)warn.push(`Пачка высотой ${Math.round(packH)} мм выше кузова ${Math.round(v.H)} мм.`);if(w&&byWeight<geo)warn.push(`Ограничение по массе: максимум ${byWeight} поддонов.`);if(desired>cap)warn.push(`Запрошено ${desired}, максимум ${cap}.`);E.warn.hidden=!warn.length;E.warn.textContent=warn.join(' ');renderSceneTruck();
}'''
pattern_calc = r"function calculate\(\)\{.*?\n\}\n\nfunction buildCurtainSide"
js, n = re.subn(pattern_calc, new_calc + "\n\nfunction buildCurtainSide", js, count=1, flags=re.S)
assert n == 1, f'calculate replacement count={n}'

pack_fn = r'''
function makePalletPack(p,count,mode,altSeed=0){
  const g=new THREE.Group(),fullH=(p.H||144)/1000,step=(mode==='mamaPapa'?0.100:fullH);
  for(let i=0;i<count;i++){
    const q=makePallet(p,p.H||144,(i+altSeed)%2===1);
    if(mode==='mamaPapa'&&i%2===1){q.rotation.x=Math.PI;q.rotation.y=Math.PI;q.position.y=i*step+fullH;}
    else{q.position.y=i*step;}
    g.add(q);
  }
  return g;
}
'''
if 'function makePalletPack(' not in js:
    marker='\nfunction renderSceneTruck(){'
    assert marker in js, 'renderSceneTruck marker missing'
    js=js.replace(marker, pack_fn+marker, 1)

new_render = r'''function renderSceneTruck(){
  if(truckRoot)scene.remove(truckRoot);if(cargoRoot)scene.remove(cargoRoot);truckRoot=new THREE.Group();const trailer=buildTrailer(S.v);truckRoot.add(trailer.group);truckRoot.add(buildTractor(S.v));scene.add(truckRoot);
  cargoRoot=new THREE.Group();let remaining=S.show,packIndex=0;for(let layer=0;layer<S.layers&&remaining>0;layer++){for(let i=0;i<S.floor&&remaining>0;i++){const pos=S.pk.pos[i],inPack=Math.min(S.packQty,remaining),p=makePalletPack(S.p,inPack,S.packMode,packIndex);p.position.set(pos.x/1000,trailer.floorY+.08+layer*S.packH/1000,pos.z/1000);p.rotation.y=-pos.r;cargoRoot.add(p);remaining-=inPack;packIndex++;}}scene.add(cargoRoot);
  const vis=E.curt.classList.contains('active');curtainLeft.visible=vis;curtainRight.visible=vis;roofGroup.visible=E.roof.classList.contains('active');const a=doorsOpen?Math.PI*.78:0;rearDoorLeft.rotation.y=-a;rearDoorRight.rotation.y=a;doorAnim=a;truckRoot.position.x=away?34:0;cargoRoot.position.x=truckRoot.position.x;driveAnim=truckRoot.position.x;resetView();
}'''
pattern_render=r"function renderSceneTruck\(\)\{.*?\n\}\n\nfunction init3D"
js,n=re.subn(pattern_render,new_render+"\n\nfunction init3D",js,count=1,flags=re.S)
assert n==1, f'render replacement count={n}'

new_tail = r'''function syncPresets(){const v=VEHICLES[E.v.value]||VEHICLES.semi136;E.cv.classList.toggle('show',E.v.value==='custom');E.L.value=v.L;E.W.value=v.W;E.H.value=v.H;E.pay.value=v.payload;const p=PALLETS[E.p.value]||PALLETS.eur;E.cp.classList.toggle('show',E.p.value==='custom');E.pL.value=p.L;E.pW.value=p.W;E.loadH.readOnly=E.p.value!=='custom';if(E.p.value!=='custom')E.loadH.value=p.H||144;}
function syncPackMode(){if(!E.packMode||!E.packQty)return;const max=E.packMode.value==='mamaPapa'?35:20;E.packQty.max=max;const n=Math.max(1,Math.min(max,Math.floor(Number(E.packQty.value)||1)));E.packQty.value=n;}
function bind(){E.v.addEventListener('change',()=>{syncPresets();syncPackMode();calculate();});E.p.addEventListener('change',()=>{syncPresets();syncPackMode();calculate();});E.packMode?.addEventListener('change',()=>{syncPackMode();calculate();});[E.L,E.W,E.H,E.pay,E.pL,E.pW,E.loadH,E.pw,E.packQty,E.qty,E.gap,E.stack].filter(Boolean).forEach(el=>el.addEventListener('input',calculate));E.curt.addEventListener('click',()=>{E.curt.classList.toggle('active');const vis=E.curt.classList.contains('active');if(curtainLeft&&curtainRight){curtainLeft.visible=vis;curtainRight.visible=vis;}});E.roof.addEventListener('click',()=>{E.roof.classList.toggle('active');if(roofGroup)roofGroup.visible=E.roof.classList.contains('active');});E.doors.addEventListener('click',()=>{doorsOpen=!doorsOpen;E.doors.classList.toggle('active',doorsOpen);E.doors.textContent=doorsOpen?'Закрыть двери':'Открыть двери';});E.drive.addEventListener('click',()=>{away=!away;E.drive.classList.toggle('active',away);E.drive.textContent=away?'Вернуть фуру':'Уехал';});E.reset.addEventListener('click',()=>{doorsOpen=false;away=false;E.doors.classList.remove('active');E.doors.textContent='Открыть двери';E.drive.classList.remove('active');E.drive.textContent='Уехал';resetView();});}
init3D();syncPresets();syncPackMode();bind();calculate();'''
pattern_tail=r"function syncPresets\(\).*?init3D\(\);syncPresets\(\);bind\(\);calculate\(\);"
js,n=re.subn(pattern_tail,new_tail,js,count=1,flags=re.S)
assert n==1, f'tail replacement count={n}'

html_path.write_text(html,encoding='utf-8')
js_path.write_text(js,encoding='utf-8')
