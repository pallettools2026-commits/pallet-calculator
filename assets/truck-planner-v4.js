import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.180.0/build/three.module.js';
import { OrbitControls } from 'https://cdn.jsdelivr.net/npm/three@0.180.0/examples/jsm/controls/OrbitControls.js';
const $ = (id) => document.getElementById(id);
const VEHICLES = {
  semi136: { name:'Еврофура / полуприцеп 13,6 м', L:13600, W:2450, H:2700, payload:24000 },
  rigid72: { name:'Грузовик 7,2 м', L:7200, W:2450, H:2400, payload:10000 },
  rigid62: { name:'Грузовик 6,2 м', L:6200, W:2450, H:2400, payload:8000 },
  van42:   { name:'Фургон L4 / 4,2 м', L:4200, W:1780, H:1900, payload:1300 },
  custom:  { name:'Свои размеры', L:10000, W:2450, H:2500, payload:12000 }
};
const PALLETS = {
  eur:    { name:'EUR / EPAL', L:1200, W:800 },
  fin:    { name:'FIN', L:1200, W:1000 },
  square: { name:'Квадратный', L:1200, W:1200 },
  custom: { name:'Свои размеры', L:1250, W:1180 }
};
const E = {
  v:$('vehiclePreset'), cv:$('customVehicle'), L:$('trailerL'), W:$('trailerW'), H:$('trailerH'), pay:$('payload'),
  p:$('palletPreset'), cp:$('customPallet'), pL:$('palletL'), pW:$('palletW'), loadH:$('loadH'), pw:$('palletWeight'), qty:$('desiredQty'), gap:$('clearance'), stack:$('stacking'),
  cap:$('capacityMetric'), floor:$('floorMetric'), layers:$('layersMetric'), weight:$('weightMetric'), capSub:$('capacitySub'), floorSub:$('floorSub'), layersSub:$('layersSub'), weightSub:$('weightSub'),
  vn:$('vehicleName'), vd:$('vehicleDims'), pn:$('palletName'), pd:$('palletDims'), layout:$('layoutName'), usage:$('usageText'), rendered:$('renderedText'), warn:$('plannerWarning'),
  host:$('truck3d'), curt:$('toggleCurtains'), roof:$('toggleRoof'), doors:$('toggleRearDoors'), drive:$('driveAway'), reset:$('resetView')
};
let S;
let scene, camera, renderer, controls;
let truckRoot, cargoRoot;
let curtainLeft, curtainRight, roofGroup, rearDoorLeft, rearDoorRight;
let doorsOpen = false;
let away = false;
let doorAnim = 0;
let driveAnim = 0;
function std(color, roughness=.55, metalness=.12){
  return new THREE.MeshStandardMaterial({ color, roughness, metalness });
}
function physical(color, opacity=.55){
  return new THREE.MeshPhysicalMaterial({
    color, transparent:true, opacity, roughness:.18, metalness:.05,
    transmission:.12, side:THREE.DoubleSide, depthWrite:false
  });
}
const M = {
  cab: std(0xf4f4f2,.34,.26),
  cab2: std(0xe6e8e7,.42,.2),
  trailer: std(0xf3f4f2,.66,.08),
  tarp: std(0xf1f2f0,.82,.02),
  tarpEdge: std(0xbcc2c1,.34,.72),
  frame: std(0x242928,.64,.64),
  dark: std(0x141818,.72,.28),
  plastic: std(0x252a2a,.72,.16),
  steel: std(0xbfc5c3,.24,.88),
  steel2: std(0x8f9795,.34,.72),
  floor: std(0x776f66,.9,.03),
  tire: std(0x121414,.94,.02),
  rim: std(0xd7dddb,.22,.9),
  hub: std(0x8b9291,.28,.88),
  glass: new THREE.MeshPhysicalMaterial({ color:0x5f737d, roughness:.08, metalness:.06, transmission:.16, transparent:true, opacity:.66 }),
  lamp: std(0xeef4fb,.12,.18),
  red: std(0xc73632,.28,.08),
  amber: std(0xe3a12f,.3,.04),
  wood: std(0xb7824d,.82,.02),
  wood2: std(0x8c5e34,.88,.01),
  load: std(0x6f9686,.66,.02),
  load2: std(0x89ab9e,.68,.02),
  transparentWall: physical(0xe8ece9,.2)
};
function val(el, fallback=0){
  const n = Number(el?.value);
  return Number.isFinite(n) && n > 0 ? n : fallback;
}
function mm(v){ return `${Math.round(v).toLocaleString('ru-RU')} мм`; }
function kg(v){ return `${Math.round(v).toLocaleString('ru-RU')} кг`; }
function box(w,h,d,mat,x=0,y=0,z=0){
  const mesh = new THREE.Mesh(new THREE.BoxGeometry(w,h,d), mat);
  mesh.position.set(x,y,z);
  mesh.castShadow = true;
  mesh.receiveShadow = true;
  return mesh;
}
function cylinder(r,h,mat,radial=30){
  const mesh = new THREE.Mesh(new THREE.CylinderGeometry(r,r,h,radial), mat);
  mesh.castShadow = true;
  mesh.receiveShadow = true;
  return mesh;
}
function wheel(radius=.46, width=.30){
  const g = new THREE.Group();
  const tire = cylinder(radius,width,M.tire,36);
  tire.rotation.z = Math.PI/2;
  g.add(tire);
  const rim = cylinder(radius*.66,width*.82,M.rim,30);
  rim.rotation.z = Math.PI/2;
  g.add(rim);
  const hub = cylinder(radius*.18,width*.88,M.hub,24);
  hub.rotation.z = Math.PI/2;
  g.add(hub);
  for(let i=0;i<8;i++){
    const a = i/8*Math.PI*2;
    const bolt = cylinder(radius*.035,width*.9,M.dark,12);
    bolt.rotation.z = Math.PI/2;
    bolt.position.set(0,Math.cos(a)*radius*.29,Math.sin(a)*radius*.29);
    g.add(bolt);
  }
  return g;
}
function addWheelPair(parent,z,width,r=.46,w=.3){
  const left = wheel(r,w), right = wheel(r,w);
  left.position.set(-width/2-.19,.47,z);
  right.position.set(width/2+.19,.47,z);
  parent.add(left,right);
}
function extrudedSideProfile(points, width, material){
  const shape = new THREE.Shape();
  points.forEach((p,i)=>{
    if(i===0) shape.moveTo(p[0],p[1]);
    else shape.lineTo(p[0],p[1]);
  });
  shape.closePath();
  const geo = new THREE.ExtrudeGeometry(shape,{ depth:width, bevelEnabled:false, curveSegments:6 });
  geo.translate(0,0,-width/2);
  geo.rotateY(Math.PI/2);
  geo.computeVertexNormals();
  const mesh = new THREE.Mesh(geo, material);
  mesh.castShadow = true;
  mesh.receiveShadow = true;
  return mesh;
}
function roundedRectShape(w,h,r){
  const s = new THREE.Shape();
  const x=w/2,y=h/2;
  s.moveTo(-x+r,-y);
  s.lineTo(x-r,-y); s.quadraticCurveTo(x,-y,x,-y+r);
  s.lineTo(x,y-r); s.quadraticCurveTo(x,y,x-r,y);
  s.lineTo(-x+r,y); s.quadraticCurveTo(-x,y,-x,y-r);
  s.lineTo(-x,-y+r); s.quadraticCurveTo(-x,-y,-x+r,-y);
  return s;
}
function roundedBox(w,h,d,r,material){
  const shape = roundedRectShape(d,h,r);
  const geo = new THREE.ExtrudeGeometry(shape,{ depth:w, bevelEnabled:false, curveSegments:10 });
  geo.translate(0,0,-w/2);
  geo.rotateY(Math.PI/2);
  geo.computeVertexNormals();
  const mesh = new THREE.Mesh(geo,material);
  mesh.castShadow=true;
  mesh.receiveShadow=true;
  return mesh;
}
function getVehicle(){
  const p = VEHICLES[E.v.value] || VEHICLES.semi136;
  if(E.v.value!=='custom') return {...p};
  return { name:p.name, L:val(E.L,p.L), W:val(E.W,p.W), H:val(E.H,p.H), payload:val(E.pay,p.payload) };
}
function getPallet(){
  const p = PALLETS[E.p.value] || PALLETS.eur;
  if(E.p.value!=='custom') return {...p};
  return { name:p.name, L:val(E.pL,p.L), W:val(E.pW,p.W) };
}
function bestPacking(L,W,pL,pW){
  let best={count:0,pos:[],text:''};
  for(let rot=0;rot<2;rot++){
    const along = rot ? pW : pL;
    const across = rot ? pL : pW;
    const cols = Math.floor(W/across);
    const rows = Math.floor(L/along);
    const count = cols*rows;
    const pos=[];
    for(let c=0;c<cols;c++){
      for(let r=0;r<rows;r++){
        pos.push({
          x:-cols*across/2+across/2+c*across,
          z:-rows*along/2+along/2+r*along,
          r:rot?Math.PI/2:0
        });
      }
    }
    if(count>best.count) best={count,pos,text:`${cols} × ${rows} · ${rot?'поперёк':'вдоль'}`};
  }
  return best;
}
function calculate(){
  const v=getVehicle(), p=getPallet();
  const h=val(E.loadH,1200);
  const w=Number(E.pw.value)||0;
  const gap=Math.max(0,Number(E.gap.value)||0);
  const pk=bestPacking(v.L,v.W,p.L+gap,p.W+gap);
  const floor=pk.count;
  const layers=E.stack.checked?Math.max(1,Math.floor(v.H/h)):1;
  const geo=floor*layers;
  const byWeight=w>0?Math.floor(v.payload/w):Infinity;
  const cap=Math.max(0,Math.min(geo,byWeight));
  const desired=Math.max(0,Math.floor(Number(E.qty.value)||0));
  const show=Math.min(cap,desired||cap);
  S={v,p,h,w,gap,pk,floor,layers,geo,byWeight,cap,show};
  E.cap.textContent=cap.toLocaleString('ru-RU');
  E.floor.textContent=floor.toLocaleString('ru-RU');
  E.layers.textContent=layers.toLocaleString('ru-RU');
  E.weight.textContent=Number.isFinite(byWeight)?byWeight.toLocaleString('ru-RU'):'∞';
  E.capSub.textContent=layers>1?'с учётом ярусности и массы':'итоговая вместимость';
  E.floorSub.textContent='мест на полу кузова';
  E.layersSub.textContent=E.stack.checked?`по высоте ${mm(v.H)}`:'штабелирование выключено';
  E.weightSub.textContent=w?`грузоподъёмность ${kg(v.payload)}`:'масса не задана';
  E.vn.textContent=v.name;
  E.vd.textContent=`${mm(v.L)} × ${mm(v.W)} × ${mm(v.H)}`;
  E.pn.textContent=p.name;
  E.pd.textContent=`${mm(p.L)} × ${mm(p.W)} · высота ${mm(h)} · зазор ${gap} мм`;
  E.layout.textContent=pk.text;
  E.usage.textContent=`${show} из ${cap} · ${cap?Math.round(show/cap*100):0}% заполнения`;
  E.rendered.textContent=w?`Текущая масса: ${kg(show*w)} из ${kg(v.payload)}`:`В 3D показано: ${show} паллет`;
  const warnings=[];
  if(!floor) warnings.push('Паллета не помещается в кузов.');
  if(w&&byWeight<geo) warnings.push(`Ограничение по массе: максимум ${byWeight}.`);
  if(desired>cap) warnings.push(`Запрошено ${desired}, максимум ${cap}.`);
  E.warn.hidden=!warnings.length;
  E.warn.textContent=warnings.join(' ');
  renderSceneTruck();
}
function buildTrailer(v){
  const g=new THREE.Group();
  const L=v.L/1000, W=v.W/1000, H=v.H/1000;
  const floorY=.90;
  const rear=L/2, front=-L/2;
  g.add(box(W+.05,.12,L+.02,M.floor,0,floorY,0));
  g.add(box(W*.44,.16,L+.18,M.frame,0,.62,0));
  g.add(box(.10,.16,L+.10,M.frame,-W*.24,.60,0));
  g.add(box(.10,.16,L+.10,M.frame, W*.24,.60,0));
  g.add(box(.08,.08,L*.53,M.steel2,-W/2-.09,.47,-L*.08));
  g.add(box(.08,.08,L*.53,M.steel2, W/2+.09,.47,-L*.08));
  g.add(box(.05,.42,L*.50,M.steel,-W/2-.10,.48,-L*.06));
  g.add(box(.05,.42,L*.50,M.steel, W/2+.10,.48,-L*.06));
  const railY=floorY+H;
  for(const x of [-W/2,W/2]){
    for(const z of [front,rear]) g.add(box(.055,H+.05,.055,M.tarpEdge,x,floorY+H/2,z));
  }
  g.add(box(W+.08,.07,.07,M.tarpEdge,0,railY,front));
  g.add(box(W+.08,.07,.07,M.tarpEdge,0,railY,rear));
  g.add(box(.06,.08,L,M.tarpEdge,-W/2,railY,0));
  g.add(box(.06,.08,L,M.tarpEdge, W/2,railY,0));
  curtainLeft=new THREE.Group();
  curtainRight=new THREE.Group();
  curtainLeft.add(box(.026,H,L,M.tarp,-W/2,floorY+H/2,0));
  curtainRight.add(box(.026,H,L,M.tarp, W/2,floorY+H/2,0));
  g.add(curtainLeft,curtainRight);
  const folds=Math.max(8,Math.round(L/.8));
  for(let i=1;i<folds;i++){
    const z=front+i*(L/folds);
    const l=box(.012,H*.9,.012,M.tarpEdge,-W/2-.015,floorY+H*.52,z);
    const r=l.clone(); r.position.x=W/2+.015;
    l.material=M.tarpEdge; r.material=M.tarpEdge;
    g.add(l,r);
  }
  const straps=Math.max(12,Math.round(L/.65));
  for(let i=0;i<straps;i++){
    const z=front+.35+i*((L-.7)/Math.max(1,straps-1));
    const b1=box(.025,.28,.035,M.dark,-W/2-.035,floorY+.14,z);
    const b2=b1.clone(); b2.position.x=W/2+.035;
    g.add(b1,b2);
    const a1=box(.055,.025,.05,M.amber,-W/2-.045,floorY+.02,z);
    const a2=a1.clone(); a2.position.x=W/2+.045;
    g.add(a1,a2);
  }
  g.add(box(W,H,.035,M.trailer,0,floorY+H/2,front));
  roofGroup=new THREE.Group();
  roofGroup.add(box(W,.04,L,M.trailer,0,floorY+H,0));
  g.add(roofGroup);
  const legZ=front+.60;
  for(const x of [-W*.25,W*.25]){
    g.add(box(.07,.82,.07,M.frame,x,.43,legZ));
    g.add(box(.22,.05,.18,M.dark,x,.035,legZ));
  }
  const axleZ=[L*.245,L*.325,L*.405];
  axleZ.forEach((z)=>{
    g.add(box(W*.78,.07,.08,M.frame,0,.50,z));
    addWheelPair(g,z,W,.45,.30);
  });
  axleZ.forEach(z=>{
    g.add(box(.30,.10,.62,M.plastic,-W/2-.10,.90,z));
    g.add(box(.30,.10,.62,M.plastic, W/2+.10,.90,z));
  });
  g.add(box(W*.84,.11,.12,M.dark,0,.43,rear+.08));
  for(const x of [-W*.32,-W*.18,W*.18,W*.32]) g.add(box(.10,.08,.035,M.red,x,.53,rear+.145));
  g.add(box(W*.26,.05,.04,M.steel,0,.53,rear+.145));
  rearDoorLeft=new THREE.Group();
  rearDoorRight=new THREE.Group();
  const doorW=W*.49, doorH=H-.10;
  rearDoorLeft.position.set(-W/2,floorY+H/2,rear+.03);
  rearDoorRight.position.set(W/2,floorY+H/2,rear+.03);
  rearDoorLeft.add(box(doorW,doorH,.028,M.trailer,-doorW/2,0,0));
  rearDoorRight.add(box(doorW,doorH,.028,M.trailer, doorW/2,0,0));
  for(const group of [rearDoorLeft,rearDoorRight]){
    for(const yy of [-H*.3,0,H*.3]) group.add(box(.05,.12,.05,M.steel2,group===rearDoorLeft?-doorW+.04:doorW-.04,yy,.03));
  }
  g.add(rearDoorLeft,rearDoorRight);
  g.add(box(.62,.34,.72,M.dark,W*.34,.34,rear-.68));
  return {group:g,floorY};
}
function buildTractor(v){
  const g=new THREE.Group();
  const W=Math.max(2.35,v.W/1000*.96);
  const trailerFront=-v.L/1000/2;
  const cabLength=2.45;
  const cabCenterZ=trailerFront-cabLength*.61-.34;
  const frontFace=cabCenterZ-cabLength/2;
  const rearFace=cabCenterZ+cabLength/2;
  g.add(box(W*.52,.16,3.65,M.frame,0,.58,cabCenterZ+.88));
  g.add(box(W*.48,.10,1.48,M.frame,0,.76,trailerFront-.36));
  const fifth=cylinder(.38,.08,M.dark,36); fifth.position.set(0,.85,trailerFront-.28); g.add(fifth);
  for(const x of [-W*.34,W*.34]){
    const tank=cylinder(.27,.92,M.steel,28); tank.rotation.z=Math.PI/2; tank.position.set(x,.78,cabCenterZ+.78); g.add(tank);
  }
  g.add(box(W*.72,.34,1.05,M.cab2,0,.73,cabCenterZ+.48));
  g.add(box(W*.73,.16,.92,M.cab,0,.58,cabCenterZ-.12));
  const steerZ=cabCenterZ-.72;
  const driveZ=cabCenterZ+.88;
  addWheelPair(g,steerZ,W,.47,.31);
  addWheelPair(g,driveZ,W,.48,.34);
  for(const z of [steerZ,driveZ]){
    g.add(box(.31,.12,.70,M.plastic,-W/2-.08,.88,z));
    g.add(box(.31,.12,.70,M.plastic, W/2+.08,.88,z));
  }
  const sideProfile=[
    [-1.18,.48],[-1.20,.78],[-1.15,1.20],[-1.08,1.72],[-.94,2.20],[-.76,2.62],[-.42,2.88],
    [.36,2.92],[.72,2.82],[1.02,2.48],[1.13,2.10],[1.16,1.05],[1.08,.62],[.82,.48]
  ];
  const shell=extrudedSideProfile(sideProfile,W*.86,M.cab);
  shell.position.z=cabCenterZ;
  g.add(shell);
  const roofProfile=[[-.75,2.76],[-.55,3.08],[.15,3.12],[.72,2.96],[.86,2.76]];
  const fairing=extrudedSideProfile(roofProfile,W*.82,M.cab);
  fairing.position.z=cabCenterZ;
  g.add(fairing);
  const wind=box(W*.66,.72,.045,M.glass,0,2.20,frontFace+.43);
  wind.rotation.x=-.33;
  g.add(wind);
  g.add(box(.028,.74,.055,M.dark,0,2.19,frontFace+.43));
  for(const x of [-W*.405,W*.405]){
    const side=box(.045,.66,.70,M.glass,x,2.02,cabCenterZ-.26);
    side.rotation.x=-.03;
    g.add(side);
  }
  for(const x of [-W*.435,W*.435]){
    g.add(box(.018,.95,.018,M.steel2,x,1.42,cabCenterZ+.20));
    g.add(box(.035,.05,.22,M.dark,x,1.62,cabCenterZ+.38));
  }
  g.add(box(W*.58,.42,.07,M.dark,0,1.18,frontFace-.02));
  for(let i=0;i<5;i++) g.add(box(W*.48,.025,.02,M.steel2,0,1.04+i*.075,frontFace-.06));
  g.add(box(W*.80,.18,.20,M.cab2,0,.67,frontFace-.02));
  g.add(box(W*.35,.10,.13,M.dark,0,.49,frontFace-.12));
  for(const x of [-W*.31,W*.31]){
    g.add(box(.24,.13,.05,M.lamp,x,.91,frontFace-.13));
    g.add(box(.08,.05,.06,M.amber,x + (x<0?-0.15:0.15),.89,frontFace-.14));
  }
  for(const sign of [-1,1]){
    const arm=box(.03,.42,.03,M.dark,sign*W*.49,2.08,cabCenterZ-.62);
    arm.rotation.z=sign*.10;
    g.add(arm);
    const mirror=roundedBox(.15,.28,.10,.03,M.dark);
    mirror.position.set(sign*W*.58,2.19,cabCenterZ-.64);
    g.add(mirror);
  }
  for(const x of [-W*.34,W*.34]){
    g.add(box(.11,.05,.04,M.amber,x,.59,cabCenterZ+.10));
    g.add(box(.33,.06,.38,M.steel,x,.42,cabCenterZ-.28));
  }
  g.add(box(.05,1.80,.40,M.cab2,-W*.43,1.65,rearFace-.13));
  g.add(box(.05,1.80,.40,M.cab2, W*.43,1.65,rearFace-.13));
  return g;
}
function makePallet(p,h,alt){
  const g=new THREE.Group();
  const L=p.L/1000,W=p.W/1000,H=Math.max(.28,h/1000);
  for(const x of [-W*.30,0,W*.30]) g.add(box(.10,.09,L*.86,M.wood2,x,.04,0));
  for(let i=0;i<5;i++) g.add(box(.09,.022,L,M.wood,-W*.42+i*W*.21,.12,0));
  g.add(box(W*.92,H,L*.92,alt?M.load2:M.load,0,.14+H/2,0));
  return g;
}
function renderSceneTruck(){
  if(truckRoot) scene.remove(truckRoot);
  if(cargoRoot) scene.remove(cargoRoot);
  truckRoot=new THREE.Group();
  const trailer=buildTrailer(S.v);
  truckRoot.add(trailer.group);
  truckRoot.add(buildTractor(S.v));
  scene.add(truckRoot);
  cargoRoot=new THREE.Group();
  let remaining=S.show;
  for(let layer=0;layer<S.layers&&remaining>0;layer++){
    const count=Math.min(S.floor,remaining);
    for(let i=0;i<count;i++){
      const pos=S.pk.pos[i];
      const p=makePallet(S.p,S.h,(i+layer)%2===1);
      p.position.set(pos.x/1000,trailer.floorY+.08+layer*S.h/1000,pos.z/1000);
      p.rotation.y=-pos.r;
      cargoRoot.add(p);
    }
    remaining-=count;
  }
  scene.add(cargoRoot);
  const curtainsVisible=E.curt.classList.contains('active');
  curtainLeft.visible=curtainsVisible;
  curtainRight.visible=curtainsVisible;
  roofGroup.visible=E.roof.classList.contains('active');
  const openAngle=doorsOpen?Math.PI*.78:0;
  rearDoorLeft.rotation.y=openAngle;
  rearDoorRight.rotation.y=-openAngle;
  doorAnim=openAngle;
  truckRoot.position.x=away?30:0;
  cargoRoot.position.x=truckRoot.position.x;
  driveAnim=truckRoot.position.x;
  resetView();
}
function init3D(){
  scene=new THREE.Scene();
  scene.background=new THREE.Color(0xf6f7f5);
  scene.fog=new THREE.Fog(0xf6f7f5,28,64);
  camera=new THREE.PerspectiveCamera(36,1,.05,120);
  renderer=new THREE.WebGLRenderer({antialias:true,alpha:false});
  renderer.setPixelRatio(Math.min(window.devicePixelRatio||1,2));
  renderer.shadowMap.enabled=true;
  renderer.shadowMap.type=THREE.PCFSoftShadowMap;
  renderer.outputColorSpace=THREE.SRGBColorSpace;
  renderer.toneMapping=THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure=1.1;
  E.host.innerHTML='';
  E.host.appendChild(renderer.domElement);
  controls=new OrbitControls(camera,renderer.domElement);
  controls.enableDamping=true;
  controls.dampingFactor=.07;
  controls.maxPolarAngle=Math.PI*.49;
  controls.minDistance=7;
  controls.maxDistance=46;
  scene.add(new THREE.HemisphereLight(0xffffff,0x768079,2.7));
  const key=new THREE.DirectionalLight(0xffffff,3.1);
  key.position.set(-10,16,8);
  key.castShadow=true;
  key.shadow.mapSize.set(2048,2048);
  key.shadow.camera.left=-24; key.shadow.camera.right=24; key.shadow.camera.top=24; key.shadow.camera.bottom=-24;
  scene.add(key);
  const fill=new THREE.DirectionalLight(0xe7eef5,1.25); fill.position.set(12,7,-14); scene.add(fill);
  const rim=new THREE.DirectionalLight(0xffffff,.7); rim.position.set(-6,5,-18); scene.add(rim);
  const ground=new THREE.Mesh(new THREE.PlaneGeometry(100,100),std(0xe8ebe7,.97,0));
  ground.rotation.x=-Math.PI/2;
  ground.position.y=-.02;
  ground.receiveShadow=true;
  scene.add(ground);
  const grid=new THREE.GridHelper(60,60,0xc4cbc7,0xd9dedb);
  grid.position.y=.005;
  grid.material.opacity=.22;
  grid.material.transparent=true;
  scene.add(grid);
  new ResizeObserver(()=>{
    const w=E.host.clientWidth;
    const h=E.host.clientHeight||520;
    renderer.setSize(w,h,false);
    camera.aspect=w/h;
    camera.updateProjectionMatrix();
  }).observe(E.host);
  animate();
}
function resetView(){
  if(!S||!camera||!controls) return;
  const L=S.v.L/1000;
  camera.position.set(7.4,5.4,Math.max(11,L*.68));
  controls.target.set(0,1.45,-.3);
  controls.update();
}
function animate(){
  requestAnimationFrame(animate);
  const targetDoor=doorsOpen?Math.PI*.78:0;
  doorAnim += (targetDoor-doorAnim)*.12;
  if(rearDoorLeft && rearDoorRight){
    rearDoorLeft.rotation.y=doorAnim;
    rearDoorRight.rotation.y=-doorAnim;
  }
  const targetX=away?30:0;
  driveAnim += (targetX-driveAnim)*.055;
  if(truckRoot&&cargoRoot){
    truckRoot.position.x=driveAnim;
    cargoRoot.position.x=driveAnim;
  }
  controls?.update();
  renderer?.render(scene,camera);
}
function syncPresets(){
  const v=VEHICLES[E.v.value]||VEHICLES.semi136;
  E.cv.classList.toggle('show',E.v.value==='custom');
  E.L.value=v.L; E.W.value=v.W; E.H.value=v.H; E.pay.value=v.payload;
  const p=PALLETS[E.p.value]||PALLETS.eur;
  E.cp.classList.toggle('show',E.p.value==='custom');
  E.pL.value=p.L; E.pW.value=p.W;
}
function bind(){
  E.v.addEventListener('change',()=>{syncPresets();calculate();});
  E.p.addEventListener('change',()=>{syncPresets();calculate();});
  [E.L,E.W,E.H,E.pay,E.pL,E.pW,E.loadH,E.pw,E.qty,E.gap,E.stack].forEach(el=>el.addEventListener('input',calculate));
  E.curt.addEventListener('click',()=>{
    E.curt.classList.toggle('active');
    const vis=E.curt.classList.contains('active');
    if(curtainLeft&&curtainRight){curtainLeft.visible=vis;curtainRight.visible=vis;}
  });
  E.roof.addEventListener('click',()=>{
    E.roof.classList.toggle('active');
    if(roofGroup) roofGroup.visible=E.roof.classList.contains('active');
  });
  E.doors.addEventListener('click',()=>{
    doorsOpen=!doorsOpen;
    E.doors.classList.toggle('active',doorsOpen);
    E.doors.textContent=doorsOpen?'Закрыть двери':'Открыть двери';
  });
  E.drive.addEventListener('click',()=>{
    away=!away;
    E.drive.classList.toggle('active',away);
    E.drive.textContent=away?'Вернуть фуру':'Уехал';
  });
  E.reset.addEventListener('click',()=>{
    doorsOpen=false; away=false;
    E.doors.classList.remove('active'); E.doors.textContent='Открыть двери';
    E.drive.classList.remove('active'); E.drive.textContent='Уехал';
    resetView();
  });
}
init3D();
syncPresets();
bind();
calculate();
