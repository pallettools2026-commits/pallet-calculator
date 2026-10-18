import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.180.0/build/three.module.js';
import { OrbitControls } from 'https://cdn.jsdelivr.net/npm/three@0.180.0/examples/jsm/controls/OrbitControls.js';
import { RoundedBoxGeometry } from 'https://cdn.jsdelivr.net/npm/three@0.180.0/examples/jsm/geometries/RoundedBoxGeometry.js';
import { RoomEnvironment } from 'https://cdn.jsdelivr.net/npm/three@0.180.0/examples/jsm/environments/RoomEnvironment.js';

const $=id=>document.getElementById(id);
const VEHICLES={
  semi136:{name:'Еврофура / полуприцеп 13,6 м',L:13600,W:2450,H:2700,payload:24000},
  rigid72:{name:'Грузовик 7,2 м',L:7200,W:2450,H:2400,payload:10000},
  rigid62:{name:'Грузовик 6,2 м',L:6200,W:2450,H:2400,payload:8000},
  van42:{name:'Фургон L4 / 4,2 м',L:4200,W:1780,H:1900,payload:1300},
  custom:{name:'Свои размеры',L:10000,W:2450,H:2500,payload:12000}
};
const PALLETS={eur:{name:'EUR / EPAL',L:1200,W:800},fin:{name:'FIN',L:1200,W:1000},square:{name:'Квадратный',L:1200,W:1200},custom:{name:'Свои размеры',L:1250,W:1180}};
const E={
  v:$('vehiclePreset'),cv:$('customVehicle'),L:$('trailerL'),W:$('trailerW'),H:$('trailerH'),pay:$('payload'),
  p:$('palletPreset'),cp:$('customPallet'),pL:$('palletL'),pW:$('palletW'),loadH:$('loadH'),pw:$('palletWeight'),qty:$('desiredQty'),gap:$('clearance'),stack:$('stacking'),
  cap:$('capacityMetric'),floor:$('floorMetric'),layers:$('layersMetric'),weight:$('weightMetric'),capSub:$('capacitySub'),floorSub:$('floorSub'),layersSub:$('layersSub'),weightSub:$('weightSub'),
  vn:$('vehicleName'),vd:$('vehicleDims'),pn:$('palletName'),pd:$('palletDims'),layout:$('layoutName'),usage:$('usageText'),rendered:$('renderedText'),warn:$('plannerWarning'),
  host:$('truck3d'),curt:$('toggleCurtains'),roof:$('toggleRoof'),doors:$('toggleRearDoors'),drive:$('driveAway'),reset:$('resetView')
};
let S,scene,camera,renderer,controls,truckRoot,cargoRoot,curtainLeft,curtainRight,roofGroup,rearDoorLeft,rearDoorRight;
let doorsOpen=false,away=false,doorAnim=0,driveAnim=0;

const std=(color,rough=.5,metal=.1,extra={})=>new THREE.MeshStandardMaterial({color,roughness:rough,metalness:metal,...extra});
const phys=(color,rough=.25,metal=.3,extra={})=>new THREE.MeshPhysicalMaterial({color,roughness:rough,metalness:metal,...extra});
const M={
  red:phys(0xa70f17,.18,.42,{clearcoat:1,clearcoatRoughness:.1}), red2:phys(0xc51c24,.22,.36,{clearcoat:.9,clearcoatRoughness:.12}),
  white:phys(0xf5f6f4,.36,.12,{clearcoat:.45,clearcoatRoughness:.22}), tarp:std(0xf2f3f1,.76,.02),
  chrome:phys(0xd9dfdf,.10,.96,{clearcoat:.35,clearcoatRoughness:.08}), alu:std(0xbec6c4,.24,.86), alu2:std(0x939c99,.32,.72),
  frame:std(0x1e2323,.58,.72), dark:std(0x101414,.63,.25), plastic:std(0x242929,.74,.12), tire:std(0x101111,.96,.01),
  glass:new THREE.MeshPhysicalMaterial({color:0x263840,roughness:.04,metalness:.04,transmission:.18,transparent:true,opacity:.78,clearcoat:.3}),
  lamp:phys(0xeef6ff,.08,.14,{emissive:0xb6d8f4,emissiveIntensity:.28}), amber:std(0xf2a526,.2,.05,{emissive:0x7b4300,emissiveIntensity:.55}), redLamp:std(0xc92c2c,.2,.05,{emissive:0x650c0c,emissiveIntensity:.45}),
  floor:std(0x766d63,.9,.02), wood:std(0xb8834c,.82,.02), wood2:std(0x8b5d33,.88,.01), load:std(0x719888,.66,.02), load2:std(0x91afa4,.68,.02)
};

function box(w,h,d,m,x=0,y=0,z=0){const q=new THREE.Mesh(new THREE.BoxGeometry(w,h,d),m);q.position.set(x,y,z);q.castShadow=q.receiveShadow=true;return q;}
function rounded(w,h,d,r,m,x=0,y=0,z=0){const q=new THREE.Mesh(new RoundedBoxGeometry(w,h,d,5,r),m);q.position.set(x,y,z);q.castShadow=q.receiveShadow=true;return q;}
function cyl(r,h,m,seg=36){const q=new THREE.Mesh(new THREE.CylinderGeometry(r,r,h,seg),m);q.castShadow=q.receiveShadow=true;return q;}
function val(el,f=0){const n=Number(el?.value);return Number.isFinite(n)&&n>0?n:f;}
const mm=v=>`${Math.round(v).toLocaleString('ru-RU')} мм`,kg=v=>`${Math.round(v).toLocaleString('ru-RU')} кг`;

function wheel(r=.48,w=.34){
  const g=new THREE.Group();
  const tire=cyl(r,w,M.tire,48);tire.rotation.z=Math.PI/2;g.add(tire);
  const rim=cyl(r*.68,w*.84,M.chrome,40);rim.rotation.z=Math.PI/2;g.add(rim);
  const hub=cyl(r*.18,w*.9,M.alu2,32);hub.rotation.z=Math.PI/2;g.add(hub);
  const ring=new THREE.Mesh(new THREE.TorusGeometry(r*.47,r*.037,12,40),M.alu);ring.rotation.y=Math.PI/2;g.add(ring);
  for(let i=0;i<10;i++){const a=i/10*Math.PI*2,b=cyl(r*.028,w*.94,M.dark,12);b.rotation.z=Math.PI/2;b.position.set(0,Math.cos(a)*r*.31,Math.sin(a)*r*.31);g.add(b);}
  return g;
}
function addWheelPair(parent,z,width,r=.48,w=.34){const a=wheel(r,w),b=wheel(r,w);a.position.set(-width/2-.18,.50,z);b.position.set(width/2+.18,.50,z);parent.add(a,b);}

function getVehicle(){const p=VEHICLES[E.v.value]||VEHICLES.semi136;if(E.v.value!=='custom')return{...p};return{name:p.name,L:val(E.L,p.L),W:val(E.W,p.W),H:val(E.H,p.H),payload:val(E.pay,p.payload)};}
function getPallet(){const p=PALLETS[E.p.value]||PALLETS.eur;if(E.p.value!=='custom')return{...p};return{name:p.name,L:val(E.pL,p.L),W:val(E.pW,p.W)};}
function bestPacking(L,W,pL,pW){let best={count:0,pos:[],text:''};for(let rot=0;rot<2;rot++){const along=rot?pW:pL,across=rot?pL:pW,cols=Math.floor(W/across),rows=Math.floor(L/along),count=cols*rows,pos=[];for(let c=0;c<cols;c++)for(let r=0;r<rows;r++)pos.push({x:-cols*across/2+across/2+c*across,z:-rows*along/2+along/2+r*along,r:rot?Math.PI/2:0});if(count>best.count)best={count,pos,text:`${cols} × ${rows} · ${rot?'поперёк':'вдоль'}`};}return best;}

function calculate(){
  const v=getVehicle(),p=getPallet(),h=val(E.loadH,1200),w=Number(E.pw.value)||0,gap=Math.max(0,Number(E.gap.value)||0),pk=bestPacking(v.L,v.W,p.L+gap,p.W+gap);
  const floor=pk.count,layers=E.stack.checked?Math.max(1,Math.floor(v.H/h)):1,geo=floor*layers,byWeight=w>0?Math.floor(v.payload/w):Infinity,cap=Math.max(0,Math.min(geo,byWeight)),desired=Math.max(0,Math.floor(Number(E.qty.value)||0)),show=Math.min(cap,desired||cap);
  S={v,p,h,w,gap,pk,floor,layers,geo,byWeight,cap,show};
  E.cap.textContent=cap.toLocaleString('ru-RU');E.floor.textContent=floor.toLocaleString('ru-RU');E.layers.textContent=layers.toLocaleString('ru-RU');E.weight.textContent=Number.isFinite(byWeight)?byWeight.toLocaleString('ru-RU'):'∞';
  E.capSub.textContent=layers>1?'с учётом ярусности и массы':'итоговая вместимость';E.floorSub.textContent='мест на полу кузова';E.layersSub.textContent=E.stack.checked?`по высоте ${mm(v.H)}`:'штабелирование выключено';E.weightSub.textContent=w?`грузоподъёмность ${kg(v.payload)}`:'масса не задана';
  E.vn.textContent=v.name;E.vd.textContent=`${mm(v.L)} × ${mm(v.W)} × ${mm(v.H)}`;E.pn.textContent=p.name;E.pd.textContent=`${mm(p.L)} × ${mm(p.W)} · высота ${mm(h)} · зазор ${gap} мм`;E.layout.textContent=pk.text;E.usage.textContent=`${show} из ${cap} · ${cap?Math.round(show/cap*100):0}% заполнения`;E.rendered.textContent=w?`Текущая масса: ${kg(show*w)} из ${kg(v.payload)}`:`В 3D показано: ${show} паллет`;
  const warn=[];if(!floor)warn.push('Паллета не помещается в кузов.');if(w&&byWeight<geo)warn.push(`Ограничение по массе: максимум ${byWeight}.`);if(desired>cap)warn.push(`Запрошено ${desired}, максимум ${cap}.`);E.warn.hidden=!warn.length;E.warn.textContent=warn.join(' ');
  renderSceneTruck();
}

function buildCurtainSide(side,W,H,L,floorY){
  const g=new THREE.Group(),x=side*W/2;
  g.add(box(.026,H-.07,L-.08,M.tarp,x,floorY+H/2,0));
  const folds=Math.max(14,Math.round(L/.66));for(let i=1;i<folds;i++){const z=-L/2+i*L/folds;g.add(box(.014,H*.88,.018,M.alu2,x+side*.018,floorY+H*.52,z));}
  const straps=Math.max(16,Math.round(L/.6));for(let i=0;i<straps;i++){const z=-L/2+.35+i*((L-.7)/Math.max(1,straps-1));g.add(box(.023,.34,.035,M.dark,x+side*.035,floorY+.17,z));g.add(box(.06,.035,.05,M.alu2,x+side*.042,floorY+.035,z));}
  return g;
}

function buildTrailer(v){
  const g=new THREE.Group(),L=v.L/1000,W=v.W/1000,H=v.H/1000,floorY=.94,front=-L/2,rear=L/2,top=floorY+H;
  g.add(box(W+.04,.12,L+.03,M.floor,0,floorY,0));g.add(box(W*.46,.18,L+.16,M.frame,0,.63,0));g.add(box(.11,.15,L+.12,M.frame,-W*.25,.63,0));g.add(box(.11,.15,L+.12,M.frame,W*.25,.63,0));
  for(let i=0;i<10;i++){const z=front+.7+i*((L-1.4)/9);g.add(box(W*.78,.07,.08,M.frame,0,.64,z));}
  for(const x of [-W/2,W/2])for(const z of [front,rear])g.add(box(.055,H+.08,.055,M.alu,x,floorY+H/2,z));
  g.add(box(W+.08,.075,.075,M.alu,0,top,front));g.add(box(W+.08,.075,.075,M.alu,0,top,rear));g.add(box(.065,.075,L,M.alu,-W/2,top,0));g.add(box(.065,.075,L,M.alu,W/2,top,0));g.add(box(W,H,.045,M.white,0,floorY+H/2,front));
  curtainLeft=buildCurtainSide(-1,W,H,L,floorY);curtainRight=buildCurtainSide(1,W,H,L,floorY);g.add(curtainLeft,curtainRight);
  roofGroup=new THREE.Group();roofGroup.add(box(W,.05,L,M.white,0,top,0));g.add(roofGroup);
  for(const side of [-1,1]){g.add(box(.06,.08,L*.43,M.alu,side*(W/2+.11),.54,-L*.04));g.add(box(.06,.42,L*.43,M.alu2,side*(W/2+.11),.51,-L*.04));}
  const legZ=front+.72;for(const x of [-W*.26,W*.26]){g.add(box(.075,.82,.075,M.frame,x,.43,legZ));g.add(box(.24,.05,.19,M.dark,x,.03,legZ));}
  const axleZ=[L*.245,L*.325,L*.405];axleZ.forEach(z=>{g.add(box(W*.8,.075,.08,M.frame,0,.50,z));addWheelPair(g,z,W,.455,.31);});
  for(const side of [-1,1])g.add(rounded(.30,.14,L*.25,.04,M.plastic,side*(W/2+.10),.91,L*.325));
  for(let i=0;i<7;i++){const z=front+.65+i*((L-1.3)/6);for(const side of [-1,1])g.add(box(.025,.045,.075,M.amber,side*(W/2+.045),floorY+.11,z));}
  rearDoorLeft=new THREE.Group();rearDoorRight=new THREE.Group();const dw=W*.49,dh=H-.10;rearDoorLeft.position.set(-W/2,floorY+H/2,rear+.04);rearDoorRight.position.set(W/2,floorY+H/2,rear+.04);rearDoorLeft.add(box(dw,dh,.035,M.white,dw/2,0,0));rearDoorRight.add(box(dw,dh,.035,M.white,-dw/2,0,0));g.add(rearDoorLeft,rearDoorRight);
  g.add(box(W*.88,.13,.13,M.dark,0,.43,rear+.12));for(const x of [-W*.34,-W*.22,W*.22,W*.34])g.add(box(.11,.08,.04,M.redLamp,x,.54,rear+.19));
  return{group:g,floorY};
}

function buildTractor(v){
  const g=new THREE.Group(),W=Math.max(2.45,v.W/1000),tf=-v.L/1000/2;
  const sleeperZ=tf-1.55,hoodZ=tf-3.35,noseZ=tf-4.15;
  const frontAx=tf-3.22,drive1=tf-.92,drive2=tf-.28;
  g.add(box(W*.50,.18,4.95,M.frame,0,.61,tf-2.05));
  g.add(box(W*.46,.11,1.25,M.frame,0,.79,tf-.42));
  const fifth=cyl(.42,.10,M.dark,40);fifth.position.set(0,.89,tf-.30);g.add(fifth);
  g.add(rounded(W*.87,2.15,2.05,.16,M.red,0,1.74,sleeperZ));
  g.add(rounded(W*.82,.56,1.80,.20,M.red2,0,3.04,sleeperZ+.03));
  const roofFair=new THREE.Mesh(new THREE.SphereGeometry(1,40,24,0,Math.PI*2,0,Math.PI/2),M.red2);roofFair.scale.set(W*.44,.52,.90);roofFair.rotation.x=Math.PI;roofFair.position.set(0,3.25,sleeperZ+.02);roofFair.castShadow=true;g.add(roofFair);
  g.add(rounded(W*.74,.78,1.78,.18,M.red,0,1.34,hoodZ));
  g.add(rounded(W*.66,.22,1.55,.10,M.red2,0,1.78,hoodZ-.06));
  g.add(rounded(W*.78,.48,.42,.09,M.red,0,1.06,noseZ));
  g.add(rounded(W*.56,.84,.08,.05,M.chrome,0,1.20,noseZ-.24));
  g.add(rounded(W*.47,.70,.095,.04,M.dark,0,1.20,noseZ-.285));
  for(let i=0;i<5;i++)g.add(rounded(W*.45,.055,.045,.018,M.chrome,0,.95+i*.125,noseZ-.34));
  g.add(rounded(W*.80,.20,.28,.06,M.red,0,.68,noseZ-.05));
  g.add(box(W*.75,.08,.24,M.dark,0,.54,noseZ-.07));
  for(const side of [-1,1]){const x=side*W*.31;g.add(rounded(.42,.27,.07,.05,M.dark,x,1.02,noseZ-.26));g.add(rounded(.34,.20,.078,.045,M.lamp,x,1.03,noseZ-.30));g.add(box(.055,.06,.085,M.amber,x+side*.18,.98,noseZ-.31));}
  const wind=rounded(W*.67,.72,.055,.07,M.glass,0,2.42,sleeperZ-1.05);wind.rotation.x=-.16;g.add(wind);
  g.add(box(.025,.72,.065,M.dark,0,2.42,sleeperZ-1.075));
  for(const side of [-1,1]){g.add(rounded(.045,.70,.70,.06,M.glass,side*W*.44,2.33,sleeperZ-.45));g.add(rounded(.05,.32,.38,.05,M.glass,side*W*.44,2.52,sleeperZ+.63));}
  for(const side of [-1,1]){const x=side*W*.445;g.add(box(.024,1.25,.90,M.red2,x,1.60,sleeperZ+.15));g.add(box(.03,.44,.55,M.red,x,1.78,sleeperZ+.72));g.add(box(.038,.06,.22,M.chrome,x,1.62,sleeperZ+.26));}
  for(const side of [-1,1]){const arm=box(.035,.46,.035,M.dark,side*W*.51,2.38,sleeperZ-.69);arm.rotation.z=side*.10;g.add(arm);g.add(rounded(.17,.34,.13,.04,M.chrome,side*W*.60,2.48,sleeperZ-.70));g.add(rounded(.13,.29,.135,.035,M.glass,side*W*.605,2.48,sleeperZ-.70));}
  for(const x of [-.55,-.28,0,.28,.55])g.add(rounded(.10,.055,.07,.02,M.amber,x,3.24,sleeperZ-1.0));
  for(const side of [-1,1]){const ant=cyl(.012,1.05,M.dark,10);ant.position.set(side*W*.39,3.48,sleeperZ-.76);g.add(ant);}
  for(const side of [-1,1]){const tank=cyl(.30,1.12,M.chrome,36);tank.rotation.z=Math.PI/2;tank.position.set(side*W*.35,.81,tf-1.45);g.add(tank);g.add(rounded(.42,.07,.62,.025,M.chrome,side*W*.34,.47,tf-2.10));g.add(rounded(.38,.07,.46,.025,M.chrome,side*W*.34,.62,tf-2.10));}
  addWheelPair(g,frontAx,W,.50,.34);addWheelPair(g,drive1,W,.50,.36);addWheelPair(g,drive2,W,.50,.36);
  for(const z of [frontAx,drive1,drive2]){g.add(rounded(.32,.14,.82,.06,M.plastic,-W/2-.10,.92,z));g.add(rounded(.32,.14,.82,.06,M.plastic,W/2+.10,.92,z));}
  for(const side of [-1,1]){g.add(box(.22,.46,.035,M.dark,side*W*.40,.53,tf-.04));const ex=cyl(.055,1.55,M.chrome,20);ex.position.set(side*W*.39,2.15,tf-.72);g.add(ex);}
  return g;
}

function makePallet(p,h,alt){const g=new THREE.Group(),L=p.L/1000,W=p.W/1000,H=Math.max(.28,h/1000);for(const x of [-W*.30,0,W*.30])g.add(box(.10,.09,L*.86,M.wood2,x,.04,0));for(let i=0;i<5;i++)g.add(box(.09,.022,L,M.wood,-W*.42+i*W*.21,.12,0));g.add(box(W*.92,H,L*.92,alt?M.load2:M.load,0,.14+H/2,0));return g;}
function renderSceneTruck(){
  if(truckRoot)scene.remove(truckRoot);if(cargoRoot)scene.remove(cargoRoot);truckRoot=new THREE.Group();const trailer=buildTrailer(S.v);truckRoot.add(trailer.group);truckRoot.add(buildTractor(S.v));scene.add(truckRoot);
  cargoRoot=new THREE.Group();let rem=S.show;for(let layer=0;layer<S.layers&&rem>0;layer++){const count=Math.min(S.floor,rem);for(let i=0;i<count;i++){const pos=S.pk.pos[i],p=makePallet(S.p,S.h,(i+layer)%2===1);p.position.set(pos.x/1000,trailer.floorY+.08+layer*S.h/1000,pos.z/1000);p.rotation.y=-pos.r;cargoRoot.add(p);}rem-=count;}scene.add(cargoRoot);
  const vis=E.curt.classList.contains('active');curtainLeft.visible=vis;curtainRight.visible=vis;roofGroup.visible=E.roof.classList.contains('active');const a=doorsOpen?Math.PI*.78:0;rearDoorLeft.rotation.y=a;rearDoorRight.rotation.y=-a;doorAnim=a;truckRoot.position.x=away?34:0;cargoRoot.position.x=truckRoot.position.x;driveAnim=truckRoot.position.x;resetView();
}

function init3D(){
  scene=new THREE.Scene();scene.background=new THREE.Color(0xf1f3f2);scene.fog=new THREE.Fog(0xf1f3f2,34,78);
  camera=new THREE.PerspectiveCamera(34,1,.05,160);renderer=new THREE.WebGLRenderer({antialias:true});renderer.setPixelRatio(Math.min(devicePixelRatio||1,2));renderer.shadowMap.enabled=true;renderer.shadowMap.type=THREE.PCFSoftShadowMap;renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.05;
  E.host.innerHTML='';E.host.appendChild(renderer.domElement);
  const pmrem=new THREE.PMREMGenerator(renderer);scene.environment=pmrem.fromScene(new RoomEnvironment(),.035).texture;pmrem.dispose();
  controls=new OrbitControls(camera,renderer.domElement);controls.enableDamping=true;controls.dampingFactor=.065;controls.maxPolarAngle=Math.PI*.49;controls.minDistance=6;controls.maxDistance=55;
  scene.add(new THREE.HemisphereLight(0xffffff,0x66706b,2.2));const key=new THREE.DirectionalLight(0xffffff,3.4);key.position.set(-13,18,10);key.castShadow=true;key.shadow.mapSize.set(2048,2048);key.shadow.camera.left=-30;key.shadow.camera.right=30;key.shadow.camera.top=30;key.shadow.camera.bottom=-30;scene.add(key);const fill=new THREE.DirectionalLight(0xe8f0ff,1.15);fill.position.set(13,7,-15);scene.add(fill);
  const ground=new THREE.Mesh(new THREE.PlaneGeometry(120,120),std(0xe2e6e3,.98,0));ground.rotation.x=-Math.PI/2;ground.position.y=-.02;ground.receiveShadow=true;scene.add(ground);const grid=new THREE.GridHelper(68,68,0xbcc5c0,0xd3dad6);grid.position.y=.004;grid.material.opacity=.14;grid.material.transparent=true;scene.add(grid);
  new ResizeObserver(()=>{const w=E.host.clientWidth,h=E.host.clientHeight||520;renderer.setSize(w,h,false);camera.aspect=w/h;camera.updateProjectionMatrix();}).observe(E.host);animate();
}
function resetView(){if(!S||!camera||!controls)return;const L=S.v.L/1000;camera.position.set(7.6,5.0,Math.max(13,L*.72));controls.target.set(0,1.55,-1.0);controls.update();}
function animate(){requestAnimationFrame(animate);const td=doorsOpen?Math.PI*.78:0;doorAnim+=(td-doorAnim)*.12;if(rearDoorLeft&&rearDoorRight){rearDoorLeft.rotation.y=doorAnim;rearDoorRight.rotation.y=-doorAnim;}const tx=away?34:0;driveAnim+=(tx-driveAnim)*.055;if(truckRoot&&cargoRoot){truckRoot.position.x=driveAnim;cargoRoot.position.x=driveAnim;}controls?.update();renderer?.render(scene,camera);}
function syncPresets(){const v=VEHICLES[E.v.value]||VEHICLES.semi136;E.cv.classList.toggle('show',E.v.value==='custom');E.L.value=v.L;E.W.value=v.W;E.H.value=v.H;E.pay.value=v.payload;const p=PALLETS[E.p.value]||PALLETS.eur;E.cp.classList.toggle('show',E.p.value==='custom');E.pL.value=p.L;E.pW.value=p.W;}
function bind(){
  E.v.addEventListener('change',()=>{syncPresets();calculate();});E.p.addEventListener('change',()=>{syncPresets();calculate();});[E.L,E.W,E.H,E.pay,E.pL,E.pW,E.loadH,E.pw,E.qty,E.gap,E.stack].forEach(el=>el.addEventListener('input',calculate));
  E.curt.addEventListener('click',()=>{E.curt.classList.toggle('active');const vis=E.curt.classList.contains('active');if(curtainLeft&&curtainRight){curtainLeft.visible=vis;curtainRight.visible=vis;}});
  E.roof.addEventListener('click',()=>{E.roof.classList.toggle('active');if(roofGroup)roofGroup.visible=E.roof.classList.contains('active');});
  E.doors.addEventListener('click',()=>{doorsOpen=!doorsOpen;E.doors.classList.toggle('active',doorsOpen);E.doors.textContent=doorsOpen?'Закрыть двери':'Открыть двери';});
  E.drive.addEventListener('click',()=>{away=!away;E.drive.classList.toggle('active',away);E.drive.textContent=away?'Вернуть фуру':'Уехал';});
  E.reset.addEventListener('click',()=>{doorsOpen=false;away=false;E.doors.classList.remove('active');E.doors.textContent='Открыть двери';E.drive.classList.remove('active');E.drive.textContent='Уехал';resetView();});
}
init3D();syncPresets();bind();calculate();
