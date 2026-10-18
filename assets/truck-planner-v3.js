import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.180.0/build/three.module.js';
import { OrbitControls } from 'https://cdn.jsdelivr.net/npm/three@0.180.0/examples/jsm/controls/OrbitControls.js';

const $ = id => document.getElementById(id);
const VEHICLES = {
  semi136: ['Еврофура / полуприцеп 13,6 м',13600,2450,2700,24000],
  rigid72: ['Грузовик 7,2 м',7200,2450,2400,10000],
  rigid62: ['Грузовик 6,2 м',6200,2450,2400,8000],
  van42: ['Фургон L4 / 4,2 м',4200,1780,1900,1300],
  custom: ['Свои размеры',10000,2450,2500,12000]
};
const PALLETS = {
  eur:['EUR / EPAL',1200,800], fin:['FIN',1200,1000], square:['Квадратный',1200,1200], custom:['Свои размеры',1250,1180]
};
const E = {
  v:$('vehiclePreset'), cv:$('customVehicle'), L:$('trailerL'), W:$('trailerW'), H:$('trailerH'), pay:$('payload'),
  p:$('palletPreset'), cp:$('customPallet'), pL:$('palletL'), pW:$('palletW'), loadH:$('loadH'), pw:$('palletWeight'), qty:$('desiredQty'), gap:$('clearance'), stack:$('stacking'),
  cap:$('capacityMetric'), floor:$('floorMetric'), layers:$('layersMetric'), weight:$('weightMetric'), capSub:$('capacitySub'), floorSub:$('floorSub'), layersSub:$('layersSub'), weightSub:$('weightSub'),
  vn:$('vehicleName'), vd:$('vehicleDims'), pn:$('palletName'), pd:$('palletDims'), layout:$('layoutName'), usage:$('usageText'), rendered:$('renderedText'), warn:$('plannerWarning'),
  host:$('truck3d'), curt:$('toggleCurtains'), roof:$('toggleRoof'), doors:$('toggleRearDoors'), drive:$('driveAway'), reset:$('resetView')
};

let state, scene, camera, renderer, controls, truckGroup, cargoGroup;
let curtainLeft, curtainRight, roofGroup, rearDoorLeft, rearDoorRight;
let doorsOpen = false, truckAway = false;
let doorAnim = 0, doorTarget = 0, driveX = 0, driveTarget = 0;

const std = (color, rough=.6, metal=.1, opacity=1) => new THREE.MeshStandardMaterial({color,roughness:rough,metalness:metal,transparent:opacity<1,opacity,side:THREE.DoubleSide,depthWrite:opacity>=1});
const MAT = {
  cab: std(0xf8f8f6,.34,.22),
  cabShadow: std(0xd9dcda,.5,.26),
  tarp: new THREE.MeshPhysicalMaterial({color:0xf5f5f2,roughness:.72,metalness:.02,clearcoat:.08,clearcoatRoughness:.72,side:THREE.DoubleSide}),
  roof: std(0xf3f4f1,.62,.06),
  frame: std(0x303534,.58,.62),
  silver: std(0xbfc5c4,.26,.83),
  dark: std(0x202322,.66,.46),
  tire: std(0x161918,.92,.03),
  rim: std(0xd7dcdb,.22,.9),
  glass: new THREE.MeshPhysicalMaterial({color:0x60727a,roughness:.08,metalness:.06,transmission:.18,transparent:true,opacity:.72}),
  floor: std(0x6f6559,.9,.03),
  amber: std(0xe7a431,.34,.08),
  red: std(0xce3b35,.34,.08),
  lamp: new THREE.MeshStandardMaterial({color:0xf3f7ff,emissive:0xaac8df,emissiveIntensity:.45,roughness:.18,metalness:.12}),
  wood: std(0xb98149,.82,.02),
  wood2: std(0x89562d,.87,.02),
  load: std(0x6c9585,.7,.02),
  load2: std(0x87a99c,.72,.02)
};

const num = (el,d=0) => { const x=Number(el?.value); return Number.isFinite(x)&&x>0?x:d; };
const mm = x => `${Math.round(x).toLocaleString('ru-RU')} мм`;
const kg = x => `${Math.round(x).toLocaleString('ru-RU')} кг`;
function box(w,h,d,mat,x=0,y=0,z=0){ const m=new THREE.Mesh(new THREE.BoxGeometry(w,h,d),mat); m.position.set(x,y,z); m.castShadow=m.receiveShadow=true; return m; }
function cylinder(r,h,mat,segments=28){ const m=new THREE.Mesh(new THREE.CylinderGeometry(r,r,h,segments),mat); m.castShadow=m.receiveShadow=true; return m; }

function getVehicle(){
  const a=VEHICLES[E.v.value]||VEHICLES.semi136;
  return E.v.value==='custom' ? {name:a[0],L:num(E.L,a[1]),W:num(E.W,a[2]),H:num(E.H,a[3]),pay:num(E.pay,a[4])} : {name:a[0],L:a[1],W:a[2],H:a[3],pay:a[4]};
}
function getPallet(){
  const a=PALLETS[E.p.value]||PALLETS.eur;
  return E.p.value==='custom' ? {name:a[0],L:num(E.pL,a[1]),W:num(E.pW,a[2])} : {name:a[0],L:a[1],W:a[2]};
}
function pack(L,W,pL,pW){
  let best={count:0,pos:[],text:''};
  for(let rot=0;rot<2;rot++){
    const along=rot?pW:pL, across=rot?pL:pW;
    const cols=Math.floor(W/across), rows=Math.floor(L/along), count=cols*rows;
    if(count<best.count) continue;
    const pos=[];
    for(let x=0;x<cols;x++) for(let z=0;z<rows;z++) pos.push({x:-cols*across/2+across/2+x*across,z:-rows*along/2+along/2+z*along,r:rot?Math.PI/2:0});
    if(count>best.count) best={count,pos,text:`${cols} × ${rows} · ${rot?'поперёк':'вдоль'}`};
  }
  return best;
}
function calculate(){
  const v=getVehicle(), p=getPallet(), h=num(E.loadH,1200), w=num(E.pw,0), gap=Math.max(0,Number(E.gap.value)||0);
  const pk=pack(v.L,v.W,p.L+gap,p.W+gap), floor=pk.count, layers=E.stack.checked?Math.max(1,Math.floor(v.H/h)):1, geo=floor*layers;
  const byWeight=w?Math.floor(v.pay/w):Infinity, cap=Math.max(0,Math.min(geo,byWeight)), want=Math.max(0,Math.floor(Number(E.qty.value)||0)), show=Math.min(cap,want||cap);
  state={v,p,h,w,gap,pk,floor,layers,geo,byWeight,cap,show};
  E.cap.textContent=cap.toLocaleString('ru-RU'); E.floor.textContent=floor.toLocaleString('ru-RU'); E.layers.textContent=layers.toLocaleString('ru-RU'); E.weight.textContent=Number.isFinite(byWeight)?byWeight.toLocaleString('ru-RU'):'∞';
  E.capSub.textContent=layers>1?'с учётом ярусности и массы':'итоговая вместимость'; E.floorSub.textContent='мест на полу кузова'; E.layersSub.textContent=E.stack.checked?`по высоте ${mm(v.H)}`:'штабелирование выключено'; E.weightSub.textContent=w?`грузоподъёмность ${kg(v.pay)}`:'масса не задана';
  E.vn.textContent=v.name; E.vd.textContent=`${mm(v.L)} × ${mm(v.W)} × ${mm(v.H)}`; E.pn.textContent=p.name; E.pd.textContent=`${mm(p.L)} × ${mm(p.W)} · высота ${mm(h)} · зазор ${gap} мм`; E.layout.textContent=pk.text;
  E.usage.textContent=`${show} из ${cap} · ${cap?Math.round(show/cap*100):0}% заполнения`; E.rendered.textContent=w?`Текущая масса: ${kg(show*w)} из ${kg(v.pay)}`:`В 3D показано: ${show} паллет`;
  const warns=[]; if(!floor) warns.push('Паллета не помещается в кузов.'); if(w&&byWeight<geo) warns.push(`Ограничение по массе: максимум ${byWeight}.`); if(want>cap) warns.push(`Запрошено ${want}, максимум ${cap}.`);
  E.warn.hidden=!warns.length; E.warn.textContent=warns.join(' ');
  renderTruck();
}

function cabSideProfileGeometry(width,height,depth){
  const s=new THREE.Shape(), x=width/2, y=height/2;
  s.moveTo(-x,-y); s.lineTo(x*.72,-y); s.quadraticCurveTo(x,-y,x,y*.02); s.lineTo(x,y*.48); s.quadraticCurveTo(x*.92,y*.72,x*.62,y*.86); s.lineTo(x*.18,y); s.lineTo(-x*.82,y); s.quadraticCurveTo(-x,y*.92,-x,y*.62); s.lineTo(-x,-y);
  const geo=new THREE.ExtrudeGeometry(s,{depth,bevelEnabled:false,curveSegments:16}); geo.translate(0,0,-depth/2); return geo;
}
function wheel(radius=.45,width=.31){
  const g=new THREE.Group(); const tire=cylinder(radius,width,MAT.tire,36); tire.rotation.z=Math.PI/2; g.add(tire); const rim=cylinder(radius*.62,width*.82,MAT.rim,32); rim.rotation.z=Math.PI/2; g.add(rim); const hub=cylinder(radius*.18,width*.9,MAT.silver,24); hub.rotation.z=Math.PI/2; g.add(hub);
  for(let i=0;i<8;i++){ const lug=cylinder(radius*.035,width*.94,MAT.dark,12); lug.rotation.z=Math.PI/2; const a=i/8*Math.PI*2; lug.position.set(0,Math.cos(a)*radius*.31,Math.sin(a)*radius*.31); g.add(lug); }
  return g;
}
function wheelPair(group,z,W,r=.45,w=.31){ const a=wheel(r,w),b=wheel(r,w); a.position.set(-W/2-.19,.47,z); b.position.set(W/2+.19,.47,z); group.add(a,b); }
function addMarker(group,x,y,z,mat){ group.add(box(.055,.035,.075,mat,x,y,z)); }

function buildTruck(v){
  const root=new THREE.Group(); const L=v.L/1000, W=v.W/1000, H=v.H/1000, floorY=.83, front=-L/2, rear=L/2;
  const tr=new THREE.Group(); const chassisW=Math.max(.92,W*.46);
  tr.add(box(W+.06,.09,L+.06,MAT.floor,0,floorY,0)); tr.add(box(chassisW,.16,L+.18,MAT.frame,0,.57,0)); tr.add(box(.12,.14,L+.05,MAT.frame,-chassisW*.68,.55,0),box(.12,.14,L+.05,MAT.frame,chassisW*.68,.55,0));
  for(const x of [-W/2-.07,W/2+.07]){ tr.add(box(.055,.055,L*.42,MAT.silver,x,.42,L*.02)); tr.add(box(.055,.055,L*.42,MAT.silver,x,.62,L*.02)); }
  const crossBars=10; for(let i=0;i<crossBars;i++) tr.add(box(W*.72,.045,.07,MAT.frame,0,.61,-L*.43+i*(L*.86/(crossBars-1))));

  curtainLeft=new THREE.Group(); curtainRight=new THREE.Group(); const curtainH=H-.05;
  curtainLeft.add(box(.028,curtainH,L-.04,MAT.tarp,-W/2,floorY+curtainH/2,0)); curtainRight.add(box(.028,curtainH,L-.04,MAT.tarp,W/2,floorY+curtainH/2,0));
  for(const side of [-1,1]){ const x=side*(W/2+.025); tr.add(box(.035,.055,L-.08,MAT.silver,x,floorY+.11,0)); const buckleCount=Math.max(12,Math.round(L/.75)); for(let i=0;i<buckleCount;i++){ const z=-L/2+.32+i*((L-.64)/(buckleCount-1)); tr.add(box(.04,.22,.025,MAT.dark,x,floorY+.24,z)); addMarker(tr,x,floorY+.08,z,MAT.amber); } }
  tr.add(curtainLeft,curtainRight); tr.add(box(W,H,.045,MAT.roof,0,floorY+H/2,front)); roofGroup=new THREE.Group(); roofGroup.add(box(W+.04,.045,L+.04,MAT.roof,0,floorY+H,0)); tr.add(roofGroup);
  for(const [x,z] of [[-W/2,front],[-W/2,rear],[W/2,front],[W/2,rear]]) tr.add(box(.055,H+.07,.055,MAT.silver,x,floorY+H/2,z)); tr.add(box(W+.1,.07,.07,MAT.silver,0,floorY+H,front),box(W+.1,.07,.07,MAT.silver,0,floorY+H,rear));

  tr.add(box(W+.05,H+.03,.055,MAT.silver,0,floorY+H/2,rear+.01)); const doorW=W*.485, doorH=H-.16; rearDoorLeft=new THREE.Group(); rearDoorRight=new THREE.Group(); rearDoorLeft.position.set(-W/2,floorY+H/2,rear+.045); rearDoorRight.position.set(W/2,floorY+H/2,rear+.045);
  rearDoorLeft.add(box(doorW,doorH,.03,MAT.roof,doorW/2,0,0)); rearDoorRight.add(box(doorW,doorH,.03,MAT.roof,-doorW/2,0,0)); rearDoorLeft.add(box(.035,doorH*.9,.04,MAT.silver,doorW*.12,0,.02)); rearDoorRight.add(box(.035,doorH*.9,.04,MAT.silver,-doorW*.12,0,.02)); tr.add(rearDoorLeft,rearDoorRight);
  tr.add(box(.12,.08,.08,MAT.red,-W*.35,.62,rear+.08),box(.12,.08,.08,MAT.red,W*.35,.62,rear+.08),box(.12,.045,.08,MAT.lamp,-W*.18,.62,rear+.08),box(.12,.045,.08,MAT.lamp,W*.18,.62,rear+.08));
  tr.add(box(.075,.82,.075,MAT.frame,-chassisW*.33,.4,front+.68),box(.075,.82,.075,MAT.frame,chassisW*.33,.4,front+.68)); tr.add(box(chassisW*.76,.055,.055,MAT.silver,0,.04,front+.68));
  for(const z of [L*.23,L*.31,L*.39]){ tr.add(box(W*.75,.08,.08,MAT.frame,0,.50,z)); tr.add(box(.31,.18,.78,MAT.dark,-W/2-.09,.84,z),box(.31,.18,.78,MAT.dark,W/2+.09,.84,z)); wheelPair(tr,z,W,.43,.30); }
  tr.add(box(.34,.31,1.05,MAT.dark,-W/2+.24,.48,L*.44),box(.34,.31,1.05,MAT.dark,W/2-.24,.48,L*.44)); root.add(tr);

  const tractor=new THREE.Group(); const cabL=2.65, cabW=W*.94, cabH=2.35, cabZ=front-cabL*.62-.34;
  tractor.add(box(Math.max(.9,W*.45),.16,cabL+1.55,MAT.frame,0,.58,cabZ+.34)); tractor.add(box(W*.78,.1,1.38,MAT.frame,0,.76,front-.52));
  const shell=new THREE.Mesh(cabSideProfileGeometry(cabW,cabH,cabL),MAT.cab); shell.position.set(0,1.43,cabZ); shell.castShadow=shell.receiveShadow=true; tractor.add(shell);
  const roofFairing=box(cabW*.86,.42,cabL*.56,MAT.cab,0,2.67,cabZ+.28); roofFairing.rotation.x=-.04; tractor.add(roofFairing); tractor.add(box(cabW*.9,.10,cabL*.72,MAT.cabShadow,0,2.34,cabZ+.18));
  const ws=box(cabW*.66,.62,.045,MAT.glass,0,1.98,cabZ-cabL*.285); ws.rotation.x=-.13; tractor.add(ws); tractor.add(box(.045,.58,cabL*.34,MAT.glass,-cabW*.425,1.84,cabZ-.12),box(.045,.58,cabL*.34,MAT.glass,cabW*.425,1.84,cabZ-.12));
  tractor.add(box(.02,1.16,.04,MAT.cabShadow,-cabW*.43,1.35,cabZ+.34),box(.02,1.16,.04,MAT.cabShadow,cabW*.43,1.35,cabZ+.34)); tractor.add(box(.02,.04,.20,MAT.dark,-cabW*.445,1.47,cabZ+.06),box(.02,.04,.20,MAT.dark,cabW*.445,1.47,cabZ+.06));
  tractor.add(box(cabW*.95,.20,.30,MAT.cabShadow,0,.98,cabZ-cabL/2-.05)); tractor.add(box(cabW*.55,.34,.035,MAT.dark,0,1.33,cabZ-cabL/2-.18)); for(let i=0;i<5;i++) tractor.add(box(cabW*.52,.018,.024,MAT.silver,0,1.21+i*.065,cabZ-cabL/2-.205));
  tractor.add(box(.28,.12,.045,MAT.lamp,-cabW*.31,1.03,cabZ-cabL/2-.2),box(.28,.12,.045,MAT.lamp,cabW*.31,1.03,cabZ-cabL/2-.2)); addMarker(tractor,-cabW*.43,1.01,cabZ-cabL/2-.19,MAT.amber); addMarker(tractor,cabW*.43,1.01,cabZ-cabL/2-.19,MAT.amber);
  tractor.add(box(.045,.34,.045,MAT.dark,-cabW*.51,1.93,cabZ-cabL*.19),box(.045,.34,.045,MAT.dark,cabW*.51,1.93,cabZ-cabL*.19)); tractor.add(box(.15,.23,.07,MAT.dark,-cabW*.59,2.02,cabZ-cabL*.17),box(.15,.23,.07,MAT.dark,cabW*.59,2.02,cabZ-cabL*.17));
  tractor.add(box(cabW*.92,.31,cabL*.72,MAT.cabShadow,0,.68,cabZ+.22)); const tankL=cylinder(.27,1.02,MAT.silver,28); tankL.rotation.z=Math.PI/2; tankL.position.set(-W*.27,.72,cabZ+.60); tractor.add(tankL); const tankR=tankL.clone(); tankR.position.x=W*.27; tractor.add(tankR); tractor.add(box(.24,.09,.46,MAT.silver,-W*.36,.52,cabZ-.36),box(.24,.09,.46,MAT.silver,W*.36,.52,cabZ-.36));
  const frontAxle=cabZ-cabL*.30, driveAxle=cabZ+cabL*.60; for(const z of [frontAxle,driveAxle]){ tractor.add(box(W*.72,.08,.08,MAT.frame,0,.5,z)); wheelPair(tractor,z,W,.45,.31); tractor.add(box(.29,.20,.72,MAT.dark,-W/2-.09,.84,z),box(.29,.20,.72,MAT.dark,W/2+.09,.84,z)); }
  const fifth=cylinder(.34,.08,MAT.dark,28); fifth.position.set(0,.86,front-.28); tractor.add(fifth); root.add(tractor);
  return {root,floorY};
}

function createPallet(p,h,alt){ const g=new THREE.Group(), L=p.L/1000, W=p.W/1000, H=Math.max(.28,h/1000); for(const x of [-W*.3,0,W*.3]) g.add(box(.10,.09,L*.86,MAT.wood2,x,.045,0)); for(let i=0;i<5;i++) g.add(box(.09,.022,L,MAT.wood,-W*.42+i*W*.21,.12,0)); g.add(box(W*.92,H,L*.92,alt?MAT.load2:MAT.load,0,.14+H/2,0)); return g; }
function renderTruck(){
  if(!scene||!state) return; if(truckGroup) scene.remove(truckGroup); if(cargoGroup) scene.remove(cargoGroup); const built=buildTruck(state.v); truckGroup=built.root; scene.add(truckGroup); cargoGroup=new THREE.Group(); let left=state.show;
  for(let y=0;y<state.layers&&left>0;y++){ const count=Math.min(state.floor,left); for(let i=0;i<count;i++){ const p=state.pk.pos[i], u=createPallet(state.p,state.h,(i+y)%2===1); u.position.set(p.x/1000,built.floorY+.08+y*state.h/1000,p.z/1000); u.rotation.y=-p.r; cargoGroup.add(u); } left-=count; }
  scene.add(cargoGroup); curtainLeft.visible=E.curt.classList.contains('active'); curtainRight.visible=E.curt.classList.contains('active'); roofGroup.visible=E.roof.classList.contains('active'); doorAnim=doorsOpen?1:0; doorTarget=doorAnim; driveX=truckAway?30:0; driveTarget=driveX; truckGroup.position.x=driveX; cargoGroup.position.x=driveX; setDoorRotation(); resetView();
}
function setDoorRotation(){ if(!rearDoorLeft||!rearDoorRight) return; const a=doorAnim*Math.PI*.72; rearDoorLeft.rotation.y=-a; rearDoorRight.rotation.y=a; }

function initScene(){
  scene=new THREE.Scene(); scene.fog=new THREE.Fog(0xe9ecea,24,55); camera=new THREE.PerspectiveCamera(40,1,.05,120); renderer=new THREE.WebGLRenderer({antialias:true,alpha:true}); renderer.setPixelRatio(Math.min(devicePixelRatio||1,2)); renderer.shadowMap.enabled=true; renderer.shadowMap.type=THREE.PCFSoftShadowMap; renderer.outputColorSpace=THREE.SRGBColorSpace; renderer.toneMapping=THREE.ACESFilmicToneMapping; renderer.toneMappingExposure=1.05; E.host.appendChild(renderer.domElement);
  controls=new OrbitControls(camera,renderer.domElement); controls.enableDamping=true; controls.dampingFactor=.07; controls.maxPolarAngle=Math.PI*.49; controls.minDistance=5; controls.maxDistance=45;
  scene.add(new THREE.HemisphereLight(0xffffff,0x778078,2.35)); const key=new THREE.DirectionalLight(0xffffff,3.15); key.position.set(-10,16,8); key.castShadow=true; key.shadow.mapSize.set(2048,2048); scene.add(key); const fill=new THREE.DirectionalLight(0xdfe9ff,.9); fill.position.set(10,7,-12); scene.add(fill);
  const ground=new THREE.Mesh(new THREE.PlaneGeometry(90,90),std(0xe2e5e2,.98,0)); ground.rotation.x=-Math.PI/2; ground.position.y=-.02; ground.receiveShadow=true; scene.add(ground); const grid=new THREE.GridHelper(48,48,0xbfc5c1,0xd8dcda); grid.material.opacity=.26; grid.material.transparent=true; scene.add(grid);
  new ResizeObserver(()=>{ const w=E.host.clientWidth,h=E.host.clientHeight||500; renderer.setSize(w,h,false); camera.aspect=w/h; camera.updateProjectionMatrix(); }).observe(E.host); animate();
}
function resetView(){ if(!state||!camera||!controls) return; const L=state.v.L/1000,W=state.v.W/1000,H=state.v.H/1000; camera.position.set(Math.max(7.2,W*2.7),Math.max(5.2,H*1.9),Math.max(9.5,L*.78)); controls.target.set(0,1.45,0); controls.update(); }
function animate(){ requestAnimationFrame(animate); doorAnim += (doorTarget-doorAnim)*.12; setDoorRotation(); driveX += (driveTarget-driveX)*.055; if(truckGroup&&cargoGroup){truckGroup.position.x=driveX;cargoGroup.position.x=driveX;} controls?.update(); renderer?.render(scene,camera); }
function syncPresets(){ const v=VEHICLES[E.v.value]; E.cv.classList.toggle('show',E.v.value==='custom'); if(v){E.L.value=v[1];E.W.value=v[2];E.H.value=v[3];E.pay.value=v[4];} const p=PALLETS[E.p.value]; E.cp.classList.toggle('show',E.p.value==='custom'); if(p){E.pL.value=p[1];E.pW.value=p[2];} }
function attach(){
  E.v.addEventListener('change',()=>{syncPresets();calculate();}); E.p.addEventListener('change',()=>{syncPresets();calculate();}); [E.L,E.W,E.H,E.pay,E.pL,E.pW,E.loadH,E.pw,E.qty,E.gap,E.stack].forEach(el=>el.addEventListener('input',calculate));
  E.curt.addEventListener('click',()=>{E.curt.classList.toggle('active'); if(curtainLeft){const show=E.curt.classList.contains('active');curtainLeft.visible=show;curtainRight.visible=show;}}); E.roof.addEventListener('click',()=>{E.roof.classList.toggle('active'); if(roofGroup)roofGroup.visible=E.roof.classList.contains('active');});
  E.doors.addEventListener('click',()=>{doorsOpen=!doorsOpen;doorTarget=doorsOpen?1:0;E.doors.classList.toggle('active',doorsOpen);E.doors.textContent=doorsOpen?'Закрыть двери':'Открыть двери';}); E.drive.addEventListener('click',()=>{truckAway=!truckAway;driveTarget=truckAway?30:0;E.drive.classList.toggle('active',truckAway);E.drive.textContent=truckAway?'Вернуть фуру':'Уехал';});
  E.reset.addEventListener('click',()=>{doorsOpen=false;doorTarget=0;truckAway=false;driveTarget=0;E.doors.classList.remove('active');E.doors.textContent='Открыть двери';E.drive.classList.remove('active');E.drive.textContent='Уехал';resetView();});
}

initScene(); syncPresets(); attach(); calculate();
