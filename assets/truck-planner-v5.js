import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.180.0/build/three.module.js';
import { OrbitControls } from 'https://cdn.jsdelivr.net/npm/three@0.180.0/examples/jsm/controls/OrbitControls.js';

const $ = (id) => document.getElementById(id);
const VEHICLES = {
  semi136:{name:'Еврофура / полуприцеп 13,6 м',L:13600,W:2450,H:2700,payload:24000},
  rigid72:{name:'Грузовик 7,2 м',L:7200,W:2450,H:2400,payload:10000},
  rigid62:{name:'Грузовик 6,2 м',L:6200,W:2450,H:2400,payload:8000},
  van42:{name:'Фургон L4 / 4,2 м',L:4200,W:1780,H:1900,payload:1300},
  custom:{name:'Свои размеры',L:10000,W:2450,H:2500,payload:12000}
};
const PALLETS = {
  eur:{name:'EUR / EPAL',L:1200,W:800},
  fin:{name:'FIN',L:1200,W:1000},
  square:{name:'Квадратный',L:1200,W:1200},
  custom:{name:'Свои размеры',L:1250,W:1180}
};
const E={
  v:$('vehiclePreset'),cv:$('customVehicle'),L:$('trailerL'),W:$('trailerW'),H:$('trailerH'),pay:$('payload'),
  p:$('palletPreset'),cp:$('customPallet'),pL:$('palletL'),pW:$('palletW'),loadH:$('loadH'),pw:$('palletWeight'),qty:$('desiredQty'),gap:$('clearance'),stack:$('stacking'),
  cap:$('capacityMetric'),floor:$('floorMetric'),layers:$('layersMetric'),weight:$('weightMetric'),capSub:$('capacitySub'),floorSub:$('floorSub'),layersSub:$('layersSub'),weightSub:$('weightSub'),
  vn:$('vehicleName'),vd:$('vehicleDims'),pn:$('palletName'),pd:$('palletDims'),layout:$('layoutName'),usage:$('usageText'),rendered:$('renderedText'),warn:$('plannerWarning'),
  host:$('truck3d'),curt:$('toggleCurtains'),roof:$('toggleRoof'),doors:$('toggleRearDoors'),drive:$('driveAway'),reset:$('resetView')
};
let S,scene,camera,renderer,controls,truckRoot,cargoRoot;
let curtainLeft,curtainRight,roofGroup,rearDoorLeft,rearDoorRight;
let doorsOpen=false,away=false,doorAnim=0,driveAnim=0;

const mat=(color,rough=.5,metal=.1,extra={})=>new THREE.MeshStandardMaterial({color,roughness:rough,metalness:metal,...extra});
const M={
  white:mat(0xf4f5f3,.28,.24),white2:mat(0xe5e8e6,.34,.2),tarp:mat(0xf1f2f0,.78,.02),
  alu:mat(0xc7cecc,.22,.88),alu2:mat(0x9ca4a2,.3,.72),frame:mat(0x242827,.58,.68),dark:mat(0x151919,.65,.25),plastic:mat(0x202525,.72,.14),
  tire:mat(0x101212,.94,.01),rim:mat(0xd7dddb,.18,.92),hub:mat(0x8d9593,.24,.88),floor:mat(0x746c62,.9,.03),
  amber:mat(0xe4a12c,.26,.06,{emissive:0x5a3800,emissiveIntensity:.2}),red:mat(0xc73531,.25,.06,{emissive:0x50100e,emissiveIntensity:.24}),lamp:mat(0xf5f8ff,.12,.18,{emissive:0xa6c8dc,emissiveIntensity:.18}),
  glass:new THREE.MeshPhysicalMaterial({color:0x5b6e77,roughness:.06,metalness:.02,transmission:.2,transparent:true,opacity:.62,side:THREE.DoubleSide}),
  wood:mat(0xb8844c,.82,.02),wood2:mat(0x8e6035,.88,.01),load:mat(0x6e9584,.66,.02),load2:mat(0x88a99d,.68,.02)
};

function box(w,h,d,m,x=0,y=0,z=0){const q=new THREE.Mesh(new THREE.BoxGeometry(w,h,d),m);q.position.set(x,y,z);q.castShadow=q.receiveShadow=true;return q;}
function cyl(r,h,m,segments=32){const q=new THREE.Mesh(new THREE.CylinderGeometry(r,r,h,segments),m);q.castShadow=q.receiveShadow=true;return q;}
function roundedBox(w,h,d,r,m){
  const s=new THREE.Shape(),a=d/2,b=h/2;
  s.moveTo(-a+r,-b);s.lineTo(a-r,-b);s.quadraticCurveTo(a,-b,a,-b+r);s.lineTo(a,b-r);s.quadraticCurveTo(a,b,a-r,b);
  s.lineTo(-a+r,b);s.quadraticCurveTo(-a,b,-a,b-r);s.lineTo(-a,-b+r);s.quadraticCurveTo(-a,-b,-a+r,-b);
  const g=new THREE.ExtrudeGeometry(s,{depth:w,bevelEnabled:false,curveSegments:8});g.translate(0,0,-w/2);g.rotateY(Math.PI/2);g.computeVertexNormals();
  const q=new THREE.Mesh(g,m);q.castShadow=q.receiveShadow=true;return q;
}
function profileMesh(points,width,m){
  const s=new THREE.Shape();
  points.forEach((p,i)=>{const sx=-p[0],sy=p[1];i?s.lineTo(sx,sy):s.moveTo(sx,sy);});s.closePath();
  const g=new THREE.ExtrudeGeometry(s,{depth:width,bevelEnabled:true,bevelThickness:.035,bevelSize:.035,bevelSegments:2,curveSegments:6});
  g.translate(0,0,-width/2);g.rotateY(Math.PI/2);g.computeVertexNormals();
  const q=new THREE.Mesh(g,m);q.castShadow=q.receiveShadow=true;return q;
}
function quad(points,m){
  const g=new THREE.BufferGeometry();
  const v=new Float32Array(points.flat());g.setAttribute('position',new THREE.BufferAttribute(v,3));g.setIndex([0,1,2,0,2,3]);g.computeVertexNormals();
  const q=new THREE.Mesh(g,m);q.castShadow=true;return q;
}
function sidePanel(x,pts,m,flip=false){
  const p=pts.map(([z,y])=>[x,y,z]);if(flip)p.reverse();return quad(p,m);
}
function wheel(r=.47,w=.32){
  const g=new THREE.Group();
  const tire=cyl(r,w,M.tire,40);tire.rotation.z=Math.PI/2;g.add(tire);
  const rim=cyl(r*.68,w*.84,M.rim,36);rim.rotation.z=Math.PI/2;g.add(rim);
  const hub=cyl(r*.18,w*.9,M.hub,28);hub.rotation.z=Math.PI/2;g.add(hub);
  const ring=new THREE.Mesh(new THREE.TorusGeometry(r*.47,r*.045,10,36),M.hub);ring.rotation.y=Math.PI/2;g.add(ring);
  for(let i=0;i<10;i++){const a=i/10*Math.PI*2;const b=cyl(r*.026,w*.94,M.dark,10);b.rotation.z=Math.PI/2;b.position.set(0,Math.cos(a)*r*.31,Math.sin(a)*r*.31);g.add(b);}
  return g;
}
function addWheelPair(parent,z,width,r=.47,w=.32){const l=wheel(r,w),rr=wheel(r,w);l.position.set(-width/2-.18,.49,z);rr.position.set(width/2+.18,.49,z);parent.add(l,rr);}
function val(el,f=0){const n=Number(el?.value);return Number.isFinite(n)&&n>0?n:f;}
const mm=v=>`${Math.round(v).toLocaleString('ru-RU')} мм`;const kg=v=>`${Math.round(v).toLocaleString('ru-RU')} кг`;
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
  const warnings=[];if(!floor)warnings.push('Паллета не помещается в кузов.');if(w&&byWeight<geo)warnings.push(`Ограничение по массе: максимум ${byWeight}.`);if(desired>cap)warnings.push(`Запрошено ${desired}, максимум ${cap}.`);E.warn.hidden=!warnings.length;E.warn.textContent=warnings.join(' ');
  renderSceneTruck();
}

function buildCurtainSide(side,W,H,L,floorY){
  const g=new THREE.Group(),x=side*W/2;
  g.add(box(.024,H-.08,L-.08,M.tarp,x,floorY+H/2,0));
  const folds=Math.max(14,Math.round(L/.65));
  for(let i=1;i<folds;i++){const z=-L/2+i*L/folds;g.add(box(.012,H*.88,.018,M.alu2,x+side*.018,floorY+H*.52,z));}
  const straps=Math.max(16,Math.round(L/.58));
  for(let i=0;i<straps;i++){const z=-L/2+.35+i*((L-.7)/Math.max(1,straps-1));g.add(box(.022,.33,.035,M.dark,x+side*.035,floorY+.17,z));g.add(box(.06,.035,.05,M.alu2,x+side*.042,floorY+.035,z));}
  return g;
}

function buildTrailer(v){
  const g=new THREE.Group(),L=v.L/1000,W=v.W/1000,H=v.H/1000,floorY=.92,front=-L/2,rear=L/2,top=floorY+H;
  g.add(box(W+.04,.12,L+.03,M.floor,0,floorY,0));
  g.add(box(W*.46,.18,L+.16,M.frame,0,.62,0));g.add(box(.11,.15,L+.12,M.frame,-W*.25,.62,0));g.add(box(.11,.15,L+.12,M.frame,W*.25,.62,0));
  for(let i=0;i<10;i++){const z=front+.7+i*((L-1.4)/9);g.add(box(W*.78,.07,.08,M.frame,0,.63,z));}
  for(const x of [-W/2,W/2])for(const z of [front,rear])g.add(box(.055,H+.08,.055,M.alu,x,floorY+H/2,z));
  g.add(box(W+.08,.075,.075,M.alu,0,top,front));g.add(box(W+.08,.075,.075,M.alu,0,top,rear));g.add(box(.065,.075,L,M.alu,-W/2,top,0));g.add(box(.065,.075,L,M.alu,W/2,top,0));
  g.add(box(W,H,.045,M.white2,0,floorY+H/2,front));
  curtainLeft=buildCurtainSide(-1,W,H,L,floorY);curtainRight=buildCurtainSide(1,W,H,L,floorY);g.add(curtainLeft,curtainRight);
  roofGroup=new THREE.Group();roofGroup.add(box(W,.05,L,M.white2,0,top,0));g.add(roofGroup);
  for(const side of [-1,1]){g.add(box(.06,.08,L*.43,M.alu,side*(W/2+.11),.54,-L*.04));g.add(box(.06,.42,L*.43,M.alu2,side*(W/2+.11),.51,-L*.04));}
  const legZ=front+.72;for(const x of [-W*.26,W*.26]){g.add(box(.075,.82,.075,M.frame,x,.43,legZ));g.add(box(.24,.05,.19,M.dark,x,.03,legZ));}
  const axleZ=[L*.245,L*.325,L*.405];
  axleZ.forEach(z=>{g.add(box(W*.8,.075,.08,M.frame,0,.50,z));addWheelPair(g,z,W,.455,.31);});
  for(const side of [-1,1]){const x=side*(W/2+.10);g.add(box(.30,.12,L*.25,M.plastic,x,.91,L*.325));}
  for(let i=0;i<6;i++){const z=front+.7+i*((L-1.4)/5);for(const side of [-1,1])g.add(box(.025,.045,.075,M.amber,side*(W/2+.045),floorY+.10,z));}
  rearDoorLeft=new THREE.Group();rearDoorRight=new THREE.Group();const doorW=W*.49,doorH=H-.10;
  rearDoorLeft.position.set(-W/2,floorY+H/2,rear+.04);rearDoorRight.position.set(W/2,floorY+H/2,rear+.04);
  rearDoorLeft.add(box(doorW,doorH,.035,M.white2,doorW/2,0,0));rearDoorRight.add(box(doorW,doorH,.035,M.white2,-doorW/2,0,0));
  for(const d of [rearDoorLeft,rearDoorRight]){const sign=d===rearDoorLeft?1:-1;d.add(box(.04,doorH*.86,.04,M.alu2,sign*doorW*.14,0,.03));for(const y of [-doorH*.28,0,doorH*.28])d.add(box(.16,.05,.05,M.alu2,sign*doorW*.30,y,.03));}
  g.add(rearDoorLeft,rearDoorRight);
  g.add(box(W*.88,.13,.13,M.dark,0,.43,rear+.12));for(const x of [-W*.34,-W*.22,W*.22,W*.34])g.add(box(.11,.08,.04,M.red,x,.54,rear+.19));g.add(box(.66,.37,.76,M.dark,W*.34,.35,rear-.72));
  return{group:g,floorY};
}

function buildTractor(v){
  const g=new THREE.Group(),W=Math.max(2.38,v.W/1000*.97),frontTrailer=-v.L/1000/2;
  const cabCenter=frontTrailer-1.72,frontZ=cabCenter-1.48,rearZ=cabCenter+1.25;
  g.add(box(W*.52,.17,4.05,M.frame,0,.60,cabCenter+.70));g.add(box(W*.48,.11,1.35,M.frame,0,.78,frontTrailer-.35));const fifth=cyl(.40,.09,M.dark,36);fifth.position.set(0,.87,frontTrailer-.27);g.add(fifth);
  for(const side of [-1,1]){const tank=cyl(.28,.96,M.alu,30);tank.rotation.z=Math.PI/2;tank.position.set(side*W*.34,.80,cabCenter+.72);g.add(tank);g.add(box(.34,.06,.42,M.alu2,side*W*.34,.44,cabCenter-.25));}
  g.add(box(W*.74,.30,1.20,M.white2,0,.73,cabCenter+.55));
  const steerZ=cabCenter-.75,driveZ=cabCenter+.88;addWheelPair(g,steerZ,W,.48,.32);addWheelPair(g,driveZ,W,.49,.35);
  const p=[[-1.48,.58],[-1.50,.82],[-1.46,1.22],[-1.37,1.70],[-1.23,2.15],[-1.05,2.55],[-.76,2.92],[-.42,3.16],[.10,3.24],[.72,3.24],[1.02,3.10],[1.19,2.72],[1.24,1.02],[1.15,.68],[.91,.58]];
  const shell=profileMesh(p,W*.86,M.white);shell.position.z=cabCenter;g.add(shell);
  const rp=[[-.72,3.12],[-.52,3.36],[.12,3.42],[.72,3.38],[1.02,3.22],[1.10,3.10]];const roof=profileMesh(rp,W*.82,M.white);roof.position.z=cabCenter;g.add(roof);
  const wx=W*.36;g.add(quad([[-wx,1.76,frontZ+.10],[wx,1.76,frontZ+.10],[wx,2.67,frontZ+.37],[-wx,2.67,frontZ+.37]],M.dark));
  g.add(quad([[-wx*.94,1.82,frontZ+.095],[wx*.94,1.82,frontZ+.095],[wx*.94,2.60,frontZ+.34],[-wx*.94,2.60,frontZ+.34]],M.glass));
  g.add(box(W*.70,.10,.16,M.dark,0,2.77,frontZ+.34));for(const x of [-.26,.26]){const wiper=box(.025,.40,.018,M.dark,x,1.95,frontZ+.045);wiper.rotation.z=x<0?-.28:.28;g.add(wiper);}
  const sideWin=[[-.92,1.72],[-.88,2.58],[.18,2.67],[.42,1.76]];
  g.add(sidePanel(-W*.435,sideWin.map(([z,y])=>[cabCenter+z,y]),M.glass,false));g.add(sidePanel(W*.435,sideWin.map(([z,y])=>[cabCenter+z,y]),M.glass,true));
  for(const side of [-1,1]){const x=side*W*.445;g.add(box(.025,.92,.026,M.alu2,x,1.28,cabCenter+.22));g.add(box(.04,.05,.24,M.dark,x,1.55,cabCenter+.46));}
  g.add(roundedBox(W*.61,.48,.09,.04,M.dark));g.children[g.children.length-1].position.set(0,1.15,frontZ-.035);
  for(let i=0;i<4;i++)g.add(box(W*.50,.028,.022,M.alu2,0,1.02+i*.095,frontZ-.09));
  g.add(box(W*.78,.20,.22,M.white2,0,.70,frontZ-.03));g.add(box(W*.45,.12,.14,M.dark,0,.52,frontZ-.14));
  for(const side of [-1,1]){const x=side*W*.30;g.add(roundedBox(.25,.23,.06,.035,M.lamp));g.children[g.children.length-1].position.set(x,.93,frontZ-.12);g.add(box(.075,.055,.07,M.amber,side*W*.42,.83,frontZ-.12));}
  for(const side of [-1,1]){const arm=box(.035,.48,.035,M.dark,side*W*.49,2.20,cabCenter-.72);arm.rotation.z=side*.08;g.add(arm);const mir=roundedBox(.16,.31,.11,.035,M.dark);mir.position.set(side*W*.59,2.33,cabCenter-.73);g.add(mir);}
  g.add(box(W*.73,.23,.95,M.white2,0,.64,cabCenter+.48));
  for(const z of [steerZ,driveZ]){g.add(box(.30,.13,.76,M.plastic,-W/2-.08,.91,z));g.add(box(.30,.13,.76,M.plastic,W/2+.08,.91,z));}
  g.add(box(.05,1.96,.42,M.white2,-W*.43,1.62,rearZ-.11));g.add(box(.05,1.96,.42,M.white2,W*.43,1.62,rearZ-.11));
  return g;
}

function makePallet(p,h,alt){const g=new THREE.Group(),L=p.L/1000,W=p.W/1000,H=Math.max(.28,h/1000);for(const x of [-W*.30,0,W*.30])g.add(box(.10,.09,L*.86,M.wood2,x,.04,0));for(let i=0;i<5;i++)g.add(box(.09,.022,L,M.wood,-W*.42+i*W*.21,.12,0));g.add(box(W*.92,H,L*.92,alt?M.load2:M.load,0,.14+H/2,0));return g;}
function renderSceneTruck(){
  if(truckRoot)scene.remove(truckRoot);if(cargoRoot)scene.remove(cargoRoot);truckRoot=new THREE.Group();const trailer=buildTrailer(S.v);truckRoot.add(trailer.group);truckRoot.add(buildTractor(S.v));scene.add(truckRoot);
  cargoRoot=new THREE.Group();let remaining=S.show;for(let layer=0;layer<S.layers&&remaining>0;layer++){const count=Math.min(S.floor,remaining);for(let i=0;i<count;i++){const pos=S.pk.pos[i],p=makePallet(S.p,S.h,(i+layer)%2===1);p.position.set(pos.x/1000,trailer.floorY+.08+layer*S.h/1000,pos.z/1000);p.rotation.y=-pos.r;cargoRoot.add(p);}remaining-=count;}scene.add(cargoRoot);
  const vis=E.curt.classList.contains('active');curtainLeft.visible=vis;curtainRight.visible=vis;roofGroup.visible=E.roof.classList.contains('active');const a=doorsOpen?Math.PI*.78:0;rearDoorLeft.rotation.y=a;rearDoorRight.rotation.y=-a;doorAnim=a;truckRoot.position.x=away?30:0;cargoRoot.position.x=truckRoot.position.x;driveAnim=truckRoot.position.x;resetView();
}
function init3D(){
  scene=new THREE.Scene();scene.background=new THREE.Color(0xf3f5f4);scene.fog=new THREE.Fog(0xf3f5f4,32,72);camera=new THREE.PerspectiveCamera(35,1,.05,140);renderer=new THREE.WebGLRenderer({antialias:true});renderer.setPixelRatio(Math.min(devicePixelRatio||1,2));renderer.shadowMap.enabled=true;renderer.shadowMap.type=THREE.PCFSoftShadowMap;renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.05;E.host.innerHTML='';E.host.appendChild(renderer.domElement);
  controls=new OrbitControls(camera,renderer.domElement);controls.enableDamping=true;controls.dampingFactor=.065;controls.maxPolarAngle=Math.PI*.49;controls.minDistance=6;controls.maxDistance=50;
  scene.add(new THREE.HemisphereLight(0xffffff,0x6e7772,2.5));const key=new THREE.DirectionalLight(0xffffff,3.2);key.position.set(-12,17,9);key.castShadow=true;key.shadow.mapSize.set(2048,2048);key.shadow.camera.left=-28;key.shadow.camera.right=28;key.shadow.camera.top=28;key.shadow.camera.bottom=-28;scene.add(key);const fill=new THREE.DirectionalLight(0xe5edf5,1.2);fill.position.set(12,8,-14);scene.add(fill);const rim=new THREE.DirectionalLight(0xffffff,.8);rim.position.set(-8,6,-20);scene.add(rim);
  const ground=new THREE.Mesh(new THREE.PlaneGeometry(110,110),mat(0xe4e8e5,.98,0));ground.rotation.x=-Math.PI/2;ground.position.y=-.02;ground.receiveShadow=true;scene.add(ground);const grid=new THREE.GridHelper(64,64,0xbfc8c3,0xd5dcd8);grid.position.y=.004;grid.material.opacity=.16;grid.material.transparent=true;scene.add(grid);
  new ResizeObserver(()=>{const w=E.host.clientWidth,h=E.host.clientHeight||520;renderer.setSize(w,h,false);camera.aspect=w/h;camera.updateProjectionMatrix();}).observe(E.host);animate();
}
function resetView(){if(!S||!camera||!controls)return;const L=S.v.L/1000;camera.position.set(6.9,4.8,Math.max(11.5,L*.66));controls.target.set(0,1.55,-.6);controls.update();}
function animate(){requestAnimationFrame(animate);const td=doorsOpen?Math.PI*.78:0;doorAnim+=(td-doorAnim)*.12;if(rearDoorLeft&&rearDoorRight){rearDoorLeft.rotation.y=doorAnim;rearDoorRight.rotation.y=-doorAnim;}const tx=away?30:0;driveAnim+=(tx-driveAnim)*.055;if(truckRoot&&cargoRoot){truckRoot.position.x=driveAnim;cargoRoot.position.x=driveAnim;}controls?.update();renderer?.render(scene,camera);}
function syncPresets(){const v=VEHICLES[E.v.value]||VEHICLES.semi136;E.cv.classList.toggle('show',E.v.value==='custom');E.L.value=v.L;E.W.value=v.W;E.H.value=v.H;E.pay.value=v.payload;const p=PALLETS[E.p.value]||PALLETS.eur;E.cp.classList.toggle('show',E.p.value==='custom');E.pL.value=p.L;E.pW.value=p.W;}
function bind(){E.v.addEventListener('change',()=>{syncPresets();calculate();});E.p.addEventListener('change',()=>{syncPresets();calculate();});[E.L,E.W,E.H,E.pay,E.pL,E.pW,E.loadH,E.pw,E.qty,E.gap,E.stack].forEach(el=>el.addEventListener('input',calculate));E.curt.addEventListener('click',()=>{E.curt.classList.toggle('active');const vis=E.curt.classList.contains('active');if(curtainLeft&&curtainRight){curtainLeft.visible=vis;curtainRight.visible=vis;}});E.roof.addEventListener('click',()=>{E.roof.classList.toggle('active');if(roofGroup)roofGroup.visible=E.roof.classList.contains('active');});E.doors.addEventListener('click',()=>{doorsOpen=!doorsOpen;E.doors.classList.toggle('active',doorsOpen);E.doors.textContent=doorsOpen?'Закрыть двери':'Открыть двери';});E.drive.addEventListener('click',()=>{away=!away;E.drive.classList.toggle('active',away);E.drive.textContent=away?'Вернуть фуру':'Уехал';});E.reset.addEventListener('click',()=>{doorsOpen=false;away=false;E.doors.classList.remove('active');E.doors.textContent='Открыть двери';E.drive.classList.remove('active');E.drive.textContent='Уехал';resetView();});}

init3D();syncPresets();bind();calculate();
