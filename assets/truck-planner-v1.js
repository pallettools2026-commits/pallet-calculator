import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.180.0/build/three.module.js';
import { OrbitControls } from 'https://cdn.jsdelivr.net/npm/three@0.180.0/examples/jsm/controls/OrbitControls.js';

const VEHICLES = {
  semi136: {name:'Еврофура / полуприцеп 13,6 м', length:13600, width:2450, height:2700, payload:24000, cab:true},
  rigid72: {name:'Грузовик 7,2 м', length:7200, width:2450, height:2400, payload:10000, cab:true},
  rigid62: {name:'Грузовик 6,2 м', length:6200, width:2450, height:2400, payload:8000, cab:true},
  van42: {name:'Фургон L4 / 4,2 м', length:4200, width:1780, height:1900, payload:1300, cab:true},
  custom: {name:'Свои размеры', length:10000, width:2450, height:2500, payload:12000, cab:true}
};
const PALLETS = {
  eur: {name:'EUR / EPAL', length:1200, width:800},
  fin: {name:'FIN', length:1200, width:1000},
  square: {name:'Квадратный', length:1200, width:1200},
  custom: {name:'Свои размеры', length:1250, width:1180}
};

const $ = id => document.getElementById(id);
const els = {
  vehicle:$('vehiclePreset'), customVehicle:$('customVehicle'), trailerL:$('trailerL'), trailerW:$('trailerW'), trailerH:$('trailerH'), payload:$('payload'),
  pallet:$('palletPreset'), customPallet:$('customPallet'), palletL:$('palletL'), palletW:$('palletW'), loadH:$('loadH'), palletWeight:$('palletWeight'), desiredQty:$('desiredQty'), stacking:$('stacking'),
  capacity:$('capacityMetric'), floor:$('floorMetric'), layers:$('layersMetric'), weight:$('weightMetric'), capacitySub:$('capacitySub'), floorSub:$('floorSub'), layersSub:$('layersSub'), weightSub:$('weightSub'),
  vehicleName:$('vehicleName'), vehicleDims:$('vehicleDims'), palletName:$('palletName'), palletDims:$('palletDims'), layoutName:$('layoutName'), usageText:$('usageText'), renderedText:$('renderedText'), warning:$('plannerWarning'),
  host:$('truck3d'), wallsBtn:$('toggleWalls'), roofBtn:$('toggleRoof'), resetBtn:$('resetView')
};

let state = null;
let scene, camera, renderer, controls, truckGroup, cargoGroup, wallGroup, roofGroup, resizeObserver;
const woodMat = new THREE.MeshStandardMaterial({color:0xb9834c,roughness:.78,metalness:.02});
const woodDarkMat = new THREE.MeshStandardMaterial({color:0x8e5d30,roughness:.85,metalness:.01});
const loadMat = new THREE.MeshStandardMaterial({color:0x5c8f7b,roughness:.68,metalness:.02});
const loadAltMat = new THREE.MeshStandardMaterial({color:0x789f91,roughness:.7,metalness:.02});
const metalMat = new THREE.MeshStandardMaterial({color:0x26322f,roughness:.42,metalness:.58});
const bodyMat = new THREE.MeshStandardMaterial({color:0xf1f3f2,roughness:.55,metalness:.18});
const greenMat = new THREE.MeshStandardMaterial({color:0x176b50,roughness:.48,metalness:.18});
const glassMat = new THREE.MeshPhysicalMaterial({color:0x5e7e88,roughness:.12,metalness:.05,transparent:true,opacity:.58,transmission:.2});
const wallMat = new THREE.MeshPhysicalMaterial({color:0xdce8e4,roughness:.18,transparent:true,opacity:.18,side:THREE.DoubleSide,depthWrite:false});
const floorMat = new THREE.MeshStandardMaterial({color:0x7b7368,roughness:.86,metalness:.02});
const tireMat = new THREE.MeshStandardMaterial({color:0x171b1a,roughness:.88,metalness:.04});

function numberValue(el, fallback=0){const v=Number(el.value);return Number.isFinite(v)&&v>0?v:fallback;}
function formatMm(v){return `${Math.round(v).toLocaleString('ru-RU')} мм`;}
function formatKg(v){return `${Math.round(v).toLocaleString('ru-RU')} кг`;}

function getVehicle(){
  const preset=VEHICLES[els.vehicle.value]||VEHICLES.semi136;
  if(els.vehicle.value!=='custom') return {...preset};
  return {...preset,length:numberValue(els.trailerL,10000),width:numberValue(els.trailerW,2450),height:numberValue(els.trailerH,2500),payload:numberValue(els.payload,12000)};
}
function getPallet(){
  const preset=PALLETS[els.pallet.value]||PALLETS.eur;
  if(els.pallet.value!=='custom') return {...preset};
  return {...preset,length:numberValue(els.palletL,1200),width:numberValue(els.palletW,800)};
}

function packByStrips(containerW,containerL,pL,pW){
  let best={count:0,placements:[],description:''};
  const orientations=[
    {rowW:pW,along:pL,rot:0,label:'вдоль'},
    {rowW:pL,along:pW,rot:Math.PI/2,label:'поперёк'}
  ];
  for(let a=0;a<=Math.floor(containerW/orientations[0].rowW);a++){
    for(let b=0;b<=Math.floor(containerW/orientations[1].rowW);b++){
      const used=a*orientations[0].rowW+b*orientations[1].rowW;
      if(used>containerW+0.01 || a+b===0) continue;
      const countA=a*Math.floor(containerL/orientations[0].along);
      const countB=b*Math.floor(containerL/orientations[1].along);
      const count=countA+countB;
      if(count<best.count) continue;
      const rows=[];
      for(let i=0;i<a;i++) rows.push(orientations[0]);
      for(let i=0;i<b;i++) rows.push(orientations[1]);
      const placements=[];
      let x=-used/2;
      rows.forEach((row,rowIndex)=>{
        const n=Math.floor(containerL/row.along);
        const zUsed=n*row.along;
        for(let i=0;i<n;i++){
          placements.push({x:x+row.rowW/2,z:-zUsed/2+row.along/2+i*row.along,rot:row.rot,row:rowIndex});
        }
        x+=row.rowW;
      });
      if(count>best.count || (count===best.count && used>(best.usedWidth||0))){
        best={count,placements,usedWidth:used,description:`${a} ряд. вдоль + ${b} ряд. поперёк`};
      }
    }
  }
  return best;
}

function rotatePacking(pack){
  return {...pack,placements:pack.placements.map(p=>({x:p.z,z:p.x,rot:p.rot+Math.PI/2,row:p.row})),description:`комбинированная схема: ${pack.description}`};
}
function bestPacking(L,W,pL,pW){
  const normal=packByStrips(W,L,pL,pW);
  const swapped=rotatePacking(packByStrips(L,W,pW,pL));
  return swapped.count>normal.count?swapped:normal;
}

function calculate(){
  const vehicle=getVehicle();
  const pallet=getPallet();
  const loadHeight=numberValue(els.loadH,1200);
  const palletWeight=numberValue(els.palletWeight,0);
  const desired=Math.max(0,Math.floor(numberValue(els.desiredQty,0)));
  const packing=bestPacking(vehicle.length,vehicle.width,pallet.length,pallet.width);
  const floorSpots=packing.count;
  const layers=els.stacking.checked?Math.max(1,Math.floor(vehicle.height/loadHeight)):1;
  const geometric=floorSpots*layers;
  const byWeight=palletWeight>0?Math.floor(vehicle.payload/palletWeight):Infinity;
  const capacity=Math.max(0,Math.min(geometric,byWeight));
  const renderCount=Math.min(capacity,desired>0?desired:capacity);
  const usedWeight=palletWeight*renderCount;
  const usage=capacity>0?Math.round(renderCount/capacity*100):0;
  state={vehicle,pallet,loadHeight,palletWeight,desired,packing,floorSpots,layers,geometric,byWeight,capacity,renderCount,usedWeight,usage};
  updateMetrics();
  renderTruck();
}

function updateMetrics(){
  const s=state;
  els.capacity.textContent=s.capacity.toLocaleString('ru-RU');
  els.floor.textContent=s.floorSpots.toLocaleString('ru-RU');
  els.layers.textContent=s.layers.toLocaleString('ru-RU');
  els.weight.textContent=Number.isFinite(s.byWeight)?s.byWeight.toLocaleString('ru-RU'):'∞';
  els.capacitySub.textContent=s.layers>1?'с учётом ярусности и массы':'итоговая вместимость';
  els.floorSub.textContent='мест на полу кузова';
  els.layersSub.textContent=els.stacking.checked?`по высоте ${formatMm(s.vehicle.height)}`:'штабелирование выключено';
  els.weightSub.textContent=s.palletWeight>0?`грузоподъёмность ${formatKg(s.vehicle.payload)}`:'масса паллеты не задана';
  els.vehicleName.textContent=s.vehicle.name;
  els.vehicleDims.textContent=`${formatMm(s.vehicle.length)} × ${formatMm(s.vehicle.width)} × ${formatMm(s.vehicle.height)}`;
  els.palletName.textContent=s.pallet.name;
  els.palletDims.textContent=`${formatMm(s.pallet.length)} × ${formatMm(s.pallet.width)} · высота груза ${formatMm(s.loadHeight)}`;
  els.layoutName.textContent=s.packing.description||'—';
  els.usageText.textContent=`${s.renderCount} из ${s.capacity} · ${s.usage}% заполнения`;
  els.renderedText.textContent=s.palletWeight>0?`Текущая масса: ${formatKg(s.usedWeight)} из ${formatKg(s.vehicle.payload)}`:`В 3D показано: ${s.renderCount} паллет`;
  const warnings=[];
  if(s.floorSpots===0) warnings.push('Паллета не помещается в заданный кузов по площади пола.');
  if(s.palletWeight>0 && s.byWeight<s.geometric) warnings.push(`Ограничение по массе: геометрически помещается ${s.geometric}, но по грузоподъёмности — ${s.byWeight}.`);
  if(s.desired>s.capacity) warnings.push(`Запрошено ${s.desired} паллет, максимум по текущим параметрам — ${s.capacity}.`);
  els.warning.hidden=warnings.length===0;
  els.warning.textContent=warnings.join(' ');
}

function initScene(){
  scene=new THREE.Scene();
  scene.fog=new THREE.Fog(0xe9ece8,18,38);
  camera=new THREE.PerspectiveCamera(42,1,.05,100);
  renderer=new THREE.WebGLRenderer({antialias:true,alpha:true});
  renderer.setPixelRatio(Math.min(window.devicePixelRatio||1,2));
  renderer.shadowMap.enabled=true;
  renderer.shadowMap.type=THREE.PCFSoftShadowMap;
  renderer.outputColorSpace=THREE.SRGBColorSpace;
  els.host.appendChild(renderer.domElement);
  controls=new OrbitControls(camera,renderer.domElement);
  controls.enableDamping=true;controls.dampingFactor=.07;controls.minDistance=5;controls.maxDistance=34;controls.maxPolarAngle=Math.PI*.49;
  scene.add(new THREE.HemisphereLight(0xffffff,0x69736d,2.25));
  const sun=new THREE.DirectionalLight(0xffffff,3.0);sun.position.set(-8,14,7);sun.castShadow=true;sun.shadow.mapSize.set(2048,2048);sun.shadow.camera.left=-18;sun.shadow.camera.right=18;sun.shadow.camera.top=18;sun.shadow.camera.bottom=-18;scene.add(sun);
  const ground=new THREE.Mesh(new THREE.PlaneGeometry(70,70),new THREE.MeshStandardMaterial({color:0xdfe4df,roughness:.96}));ground.rotation.x=-Math.PI/2;ground.position.y=-.02;ground.receiveShadow=true;scene.add(ground);
  const grid=new THREE.GridHelper(36,36,0xb7c2bc,0xd1d8d4);grid.position.y=.01;grid.material.opacity=.38;grid.material.transparent=true;scene.add(grid);
  resizeObserver=new ResizeObserver(resizeScene);resizeObserver.observe(els.host);
  animate();
}
function resizeScene(){
  if(!renderer||!camera)return;const w=els.host.clientWidth,h=els.host.clientHeight||500;renderer.setSize(w,h,false);camera.aspect=w/h;camera.updateProjectionMatrix();
}
function box(w,h,d,mat,x=0,y=0,z=0){const m=new THREE.Mesh(new THREE.BoxGeometry(w,h,d),mat);m.position.set(x,y,z);m.castShadow=true;m.receiveShadow=true;return m;}
function wheel(x,y,z,r=.43,width=.28){const m=new THREE.Mesh(new THREE.CylinderGeometry(r,r,width,28),tireMat);m.rotation.z=Math.PI/2;m.position.set(x,y,z);m.castShadow=true;return m;}

function createTruck(vehicle){
  const g=new THREE.Group();
  const L=vehicle.length/1000,W=vehicle.width/1000,H=vehicle.height/1000;
  const floorY=.72;
  g.add(box(W+.08,.13,L+.05,floorMat,0,floorY,0));
  g.add(box(W+.12,.16,L+.12,metalMat,0,.49,0));
  wallGroup=new THREE.Group();
  const t=.035;
  const left=box(t,H,L,wallMat,-W/2,floorY+H/2,0);const right=box(t,H,L,wallMat,W/2,floorY+H/2,0);const front=box(W,H,t,wallMat,0,floorY+H/2,-L/2);wallGroup.add(left,right,front);g.add(wallGroup);
  roofGroup=new THREE.Group();roofGroup.add(box(W,.04,L,wallMat,0,floorY+H,0));g.add(roofGroup);
  const frameMat=metalMat;
  [[-W/2,-L/2],[-W/2,L/2],[W/2,-L/2],[W/2,L/2]].forEach(([x,z])=>g.add(box(.055,H+.12,.055,frameMat,x,floorY+H/2,z)));
  g.add(box(W+.1,.08,.08,frameMat,0,floorY+H,-L/2));g.add(box(W+.1,.08,.08,frameMat,0,floorY+H,L/2));
  const axleZ=[L*.30,L*.38,L*.46];
  axleZ.forEach(z=>{g.add(wheel(-W/2-.18,.46,z));g.add(wheel(W/2+.18,.46,z));});
  const cab=new THREE.Group();const cabL=Math.min(2.6,Math.max(1.8,L*.22));const cabZ=-L/2-cabL*.54;
  cab.add(box(W*.92,1.75,cabL,greenMat,0,1.2,cabZ));
  cab.add(box(W*.82,.78,cabL*.62,greenMat,0,2.32,cabZ-.12));
  const windshield=box(W*.62,.5,.035,glassMat,0,2.34,cabZ-cabL*.32);windshield.rotation.x=-.08;cab.add(windshield);
  cab.add(box(W*.78,.12,.16,metalMat,0,.57,cabZ-cabL*.52));
  cab.add(box(W*.42,.17,.08,metalMat,0,1.1,cabZ-cabL*.51));
  const lightMat=new THREE.MeshStandardMaterial({color:0xfff1b6,emissive:0xffd37a,emissiveIntensity:.55});cab.add(box(.26,.16,.05,lightMat,-W*.31,1.03,cabZ-cabL*.54));cab.add(box(.26,.16,.05,lightMat,W*.31,1.03,cabZ-cabL*.54));
  const cabAxles=[cabZ-cabL*.30,cabZ+cabL*.25];cabAxles.forEach(z=>{cab.add(wheel(-W*.45-.12,.48,z,.45,.25));cab.add(wheel(W*.45+.12,.48,z,.45,.25));});
  g.add(cab);
  return {group:g,L,W,H,floorY,cabL};
}

function createPalletUnit(pallet,loadHeight,layerIndex,index){
  const pL=pallet.length/1000,pW=pallet.width/1000,baseH=.14;const loadH=Math.max(.08,loadHeight/1000-baseH);
  const group=new THREE.Group();
  const deckH=.045;const runnerH=.055;
  for(let i=-2;i<=2;i++){group.add(box(pW*.95,deckH,pL*.16,woodMat,0,baseH-deckH/2,i*pL*.19));}
  [-.36,0,.36].forEach(k=>group.add(box(pW*.14,runnerH,pL*.93,woodDarkMat,k*pW,runnerH/2+.005,0)));
  const load=box(pW*.91,loadH,pL*.91,index%2?loadAltMat:loadMat,0,baseH+loadH/2,0);group.add(load);
  group.position.y=layerIndex*(loadHeight/1000);
  return group;
}

function renderTruck(){
  if(!scene)initScene();
  if(truckGroup)scene.remove(truckGroup);if(cargoGroup)scene.remove(cargoGroup);
  const made=createTruck(state.vehicle);truckGroup=made.group;scene.add(truckGroup);
  cargoGroup=new THREE.Group();
  const maxPerLayer=state.floorSpots;let remaining=state.renderCount;
  for(let layer=0;layer<state.layers && remaining>0;layer++){
    const count=Math.min(maxPerLayer,remaining);
    for(let i=0;i<count;i++){
      const p=state.packing.placements[i];if(!p)continue;
      const unit=createPalletUnit(state.pallet,state.loadHeight,layer,i+layer*maxPerLayer);
      unit.position.x=p.x/1000;unit.position.z=p.z/1000;unit.position.y=made.floorY+.08+layer*(state.loadHeight/1000);unit.rotation.y=-p.rot;cargoGroup.add(unit);
    }
    remaining-=count;
  }
  scene.add(cargoGroup);
  wallGroup.visible=els.wallsBtn.classList.contains('active');roofGroup.visible=els.roofBtn.classList.contains('active');
  resetCamera();
}

function resetCamera(){
  if(!state||!camera||!controls)return;const L=state.vehicle.length/1000;const W=state.vehicle.width/1000;const target=new THREE.Vector3(0,1.2,0);camera.position.set(Math.max(7,W*2.7),Math.max(5.2,state.vehicle.height/1000*2.0),Math.max(8.5,L*.78));controls.target.copy(target);controls.update();
}
function animate(){requestAnimationFrame(animate);if(controls)controls.update();if(renderer&&scene&&camera)renderer.render(scene,camera);}

function syncPresetFields(){
  const v=VEHICLES[els.vehicle.value];els.customVehicle.classList.toggle('show',els.vehicle.value==='custom');
  if(v){els.trailerL.value=v.length;els.trailerW.value=v.width;els.trailerH.value=v.height;els.payload.value=v.payload;}
  const p=PALLETS[els.pallet.value];els.customPallet.classList.toggle('show',els.pallet.value==='custom');
  if(p){els.palletL.value=p.length;els.palletW.value=p.width;}
}

[els.vehicle,els.pallet].forEach(el=>el.addEventListener('change',()=>{syncPresetFields();calculate();}));
[els.trailerL,els.trailerW,els.trailerH,els.payload,els.palletL,els.palletW,els.loadH,els.palletWeight,els.desiredQty,els.stacking].forEach(el=>el.addEventListener('input',calculate));
els.wallsBtn.addEventListener('click',()=>{els.wallsBtn.classList.toggle('active');if(wallGroup)wallGroup.visible=els.wallsBtn.classList.contains('active');});
els.roofBtn.addEventListener('click',()=>{els.roofBtn.classList.toggle('active');if(roofGroup)roofGroup.visible=els.roofBtn.classList.contains('active');});
els.resetBtn.addEventListener('click',resetCamera);

syncPresetFields();
calculate();
