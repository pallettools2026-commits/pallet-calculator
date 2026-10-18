import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.180.0/build/three.module.js';
import { OrbitControls } from 'https://cdn.jsdelivr.net/npm/three@0.180.0/examples/jsm/controls/OrbitControls.js';

const $ = id => document.getElementById(id);
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
  red:mat(0xb8171e,.26,.28),redDark:mat(0x7e0d13,.33,.22),redLight:mat(0xd42a2f,.24,.25),
  white:mat(0xf3f4f2,.30,.18),white2:mat(0xe5e8e6,.38,.18),tarp:mat(0xf1f2f0,.78,.02),
  chrome:mat(0xd8dedd,.12,.96),alu:mat(0xc2c9c7,.22,.88),alu2:mat(0x929b98,.30,.72),
  frame:mat(0x202524,.60,.66),dark:mat(0x111515,.64,.25),plastic:mat(0x202424,.76,.12),
  tire:mat(0x0d0f0f,.95,.01),rim:mat(0xdce2df,.18,.92),hub:mat(0x888f8e,.25,.86),floor:mat(0x746b61,.90,.03),
  amber:mat(0xe9a02a,.24,.04,{emissive:0x6a3b00,emissiveIntensity:.35}),redLamp:mat(0xc6312d,.25,.06,{emissive:0x60100e,emissiveIntensity:.26}),lamp:mat(0xf2f7ff,.10,.16,{emissive:0xaacbdf,emissiveIntensity:.25}),
  glass:new THREE.MeshPhysicalMaterial({color:0x26363f,roughness:.08,metalness:.03,transmission:.18,transparent:true,opacity:.72,side:THREE.DoubleSide}),
  wood:mat(0xb9844d,.82,.02),wood2:mat(0x8e6035,.88,.01),load:mat(0x6e9584,.66,.02),load2:mat(0x88a99d,.68,.02)
};

function box(w,h,d,m,x=0,y=0,z=0){const q=new THREE.Mesh(new THREE.BoxGeometry(w,h,d),m);q.position.set(x,y,z);q.castShadow=q.receiveShadow=true;return q;}
function cyl(r,h,m,segments=36){const q=new THREE.Mesh(new THREE.CylinderGeometry(r,r,h,segments),m);q.castShadow=q.receiveShadow=true;return q;}
function sphere(r,m,x=0,y=0,z=0,sx=1,sy=1,sz=1){const q=new THREE.Mesh(new THREE.SphereGeometry(r,28,18),m);q.position.set(x,y,z);q.scale.set(sx,sy,sz);q.castShadow=q.receiveShadow=true;return q;}
function roundedRectShape(w,h,r){const s=new THREE.Shape(),x=w/2,y=h/2;s.moveTo(-x+r,-y);s.lineTo(x-r,-y);s.quadraticCurveTo(x,-y,x,-y+r);s.lineTo(x,y-r);s.quadraticCurveTo(x,y,x-r,y);s.lineTo(-x+r,y);s.quadraticCurveTo(-x,y,-x,y-r);s.lineTo(-x,-y+r);s.quadraticCurveTo(-x,-y,-x+r,-y);return s;}
function roundedBox(w,h,d,r,m){const shape=roundedRectShape(d,h,r);const g=new THREE.ExtrudeGeometry(shape,{depth:w,bevelEnabled:false,curveSegments:12});g.translate(0,0,-w/2);g.rotateY(Math.PI/2);g.computeVertexNormals();const q=new THREE.Mesh(g,m);q.castShadow=q.receiveShadow=true;return q;}
function profileMesh(points,width,m,bevel=.035){const s=new THREE.Shape();points.forEach((p,i)=>i?s.lineTo(-p[0],p[1]):s.moveTo(-p[0],p[1]));s.closePath();const g=new THREE.ExtrudeGeometry(s,{depth:width,bevelEnabled:true,bevelThickness:bevel,bevelSize:bevel,bevelSegments:3,curveSegments:8});g.translate(0,0,-width/2);g.rotateY(Math.PI/2);g.computeVertexNormals();const q=new THREE.Mesh(g,m);q.castShadow=q.receiveShadow=true;return q;}
function quad(points,m){const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.BufferAttribute(new Float32Array(points.flat()),3));g.setIndex([0,1,2,0,2,3]);g.computeVertexNormals();const q=new THREE.Mesh(g,m);q.castShadow=true;return q;}
function sidePanel(x,pts,m,flip=false){const p=pts.map(([z,y])=>[x,y,z]);if(flip)p.reverse();return quad(p,m);}

function wheel(r=.47,w=.32){const g=new THREE.Group();const tire=cyl(r,w,M.tire,44);tire.rotation.z=Math.PI/2;g.add(tire);const rim=cyl(r*.67,w*.82,M.rim,40);rim.rotation.z=Math.PI/2;g.add(rim);const hub=cyl(r*.19,w*.90,M.hub,28);hub.rotation.z=Math.PI/2;g.add(hub);const ring=new THREE.Mesh(new THREE.TorusGeometry(r*.47,r*.045,10,40),M.chrome);ring.rotation.y=Math.PI/2;g.add(ring);for(let i=0;i<10;i++){const a=i/10*Math.PI*2;const b=cyl(r*.027,w*.94,M.dark,10);b.rotation.z=Math.PI/2;b.position.set(0,Math.cos(a)*r*.30,Math.sin(a)*r*.30);g.add(b);}return g;}
function addWheelPair(parent,z,width,r=.47,w=.32){const l=wheel(r,w),rr=wheel(r,w);l.position.set(-width/2-.18,.49,z);rr.position.set(width/2+.18,.49,z);parent.add(l,rr);}
function val(el,f=0){const n=Number(el?.value);return Number.isFinite(n)&&n>0?n:f;}
const mm=v=>`${Math.round(v).toLocaleString('ru-RU')} мм`,kg=v=>`${Math.round(v).toLocaleString('ru-RU')} кг`;

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

function buildCurtainSide(side,W,H,L,floorY){const g=new THREE.Group(),x=side*W/2;g.add(box(.024,H-.08,L-.08,M.tarp,x,floorY+H/2,0));const folds=Math.max(14,Math.round(L/.65));for(let i=1;i<folds;i++){const z=-L/2+i*L/folds;g.add(box(.012,H*.88,.018,M.alu2,x+side*.018,floorY+H*.52,z));}const straps=Math.max(16,Math.round(L/.58));for(let i=0;i<straps;i++){const z=-L/2+.35+i*((L-.7)/Math.max(1,straps-1));g.add(box(.022,.33,.035,M.dark,x+side*.035,floorY+.17,z));g.add(box(.06,.035,.05,M.alu2,x+side*.042,floorY+.035,z));}return g;}

function buildTrailer(v){
  const g=new THREE.Group(),L=v.L/1000,W=v.W/1000,H=v.H/1000,floorY=.92,front=-L/2,rear=L/2,top=floorY+H;
  g.add(box(W+.04,.12,L+.03,M.floor,0,floorY,0));g.add(box(W*.46,.18,L+.16,M.frame,0,.62,0));g.add(box(.11,.15,L+.12,M.frame,-W*.25,.62,0));g.add(box(.11,.15,L+.12,M.frame,W*.25,.62,0));
  for(let i=0;i<10;i++){const z=front+.7+i*((L-1.4)/9);g.add(box(W*.78,.07,.08,M.frame,0,.63,z));}
  for(const x of [-W/2,W/2])for(const z of [front,rear])g.add(box(.055,H+.08,.055,M.alu,x,floorY+H/2,z));
  g.add(box(W+.08,.075,.075,M.alu,0,top,front));g.add(box(W+.08,.075,.075,M.alu,0,top,rear));g.add(box(.065,.075,L,M.alu,-W/2,top,0));g.add(box(.065,.075,L,M.alu,W/2,top,0));g.add(box(W,H,.045,M.white2,0,floorY+H/2,front));
  curtainLeft=buildCurtainSide(-1,W,H,L,floorY);curtainRight=buildCurtainSide(1,W,H,L,floorY);g.add(curtainLeft,curtainRight);
  roofGroup=new THREE.Group();roofGroup.add(box(W,.05,L,M.white2,0,top,0));g.add(roofGroup);
  for(const side of [-1,1]){g.add(box(.06,.08,L*.43,M.alu,side*(W/2+.11),.54,-L*.04));g.add(box(.06,.42,L*.43,M.alu2,side*(W/2+.11),.51,-L*.04));}
  const legZ=front+.72;for(const x of [-W*.26,W*.26]){g.add(box(.075,.82,.075,M.frame,x,.43,legZ));g.add(box(.24,.05,.19,M.dark,x,.03,legZ));}
  const axleZ=[L*.245,L*.325,L*.405];axleZ.forEach(z=>{g.add(box(W*.8,.075,.08,M.frame,0,.50,z));addWheelPair(g,z,W,.455,.31);});
  for(const side of [-1,1])g.add(box(.30,.12,L*.25,M.plastic,side*(W/2+.10),.91,L*.325));
  for(let i=0;i<6;i++){const z=front+.7+i*((L-1.4)/5);for(const side of [-1,1])g.add(box(.025,.045,.075,M.amber,side*(W/2+.045),floorY+.10,z));}
  rearDoorLeft=new THREE.Group();rearDoorRight=new THREE.Group();const doorW=W*.49,doorH=H-.10;rearDoorLeft.position.set(-W/2,floorY+H/2,rear+.04);rearDoorRight.position.set(W/2,floorY+H/2,rear+.04);rearDoorLeft.add(box(doorW,doorH,.035,M.white2,doorW/2,0,0));rearDoorRight.add(box(doorW,doorH,.035,M.white2,-doorW/2,0,0));for(const d of [rearDoorLeft,rearDoorRight]){const sign=d===rearDoorLeft?1:-1;d.add(box(.04,doorH*.86,.04,M.alu2,sign*doorW*.14,0,.03));for(const y of [-doorH*.28,0,doorH*.28])d.add(box(.16,.05,.05,M.alu2,sign*doorW*.30,y,.03));}g.add(rearDoorLeft,rearDoorRight);
  g.add(box(W*.88,.13,.13,M.dark,0,.43,rear+.12));for(const x of [-W*.34,-W*.22,W*.22,W*.34])g.add(box(.11,.08,.04,M.redLamp,x,.54,rear+.19));g.add(box(.66,.37,.76,M.dark,W*.34,.35,rear-.72));
  return{group:g,floorY};
}

function addCabRoofMarkers(g,W,z,y){for(const x of [-.62,-.31,0,.31,.62])g.add(box(.09,.035,.04,M.amber,x*W/1.8,y,z));}
function addChromeGrille(g,W,frontZ){
  const frame=roundedBox(W*.72,.82,.12,.06,M.chrome);frame.position.set(0,1.08,frontZ);g.add(frame);
  const inset=roundedBox(W*.62,.67,.14,.05,M.dark);inset.position.set(0,1.08,frontZ-.015);g.add(inset);
  for(let i=0;i<5;i++)g.add(box(W*.58,.052,.028,M.chrome,0,.84+i*.125,frontZ-.095));
}

function buildTractor(v){
  const g=new THREE.Group();
  const W=Math.max(2.45,v.W/1000*.99),trailerFront=-v.L/1000/2;
  const sleeperZ=trailerFront-1.48,hoodZ=sleeperZ-2.10,bumperZ=hoodZ-1.16;
  const frontAxleZ=hoodZ-.48,drive1Z=sleeperZ+.72,drive2Z=sleeperZ+1.50;

  g.add(box(W*.50,.18,5.55,M.frame,0,.60,sleeperZ+.15));
  const fifth=cyl(.42,.09,M.dark,40);fifth.position.set(0,.88,trailerFront-.28);g.add(fifth);
  for(const side of [-1,1]){const tank=cyl(.31,1.24,M.chrome,36);tank.rotation.z=Math.PI/2;tank.position.set(side*W*.34,.78,sleeperZ+.18);g.add(tank);g.add(box(.42,.08,.56,M.chrome,side*W*.34,.42,sleeperZ-.62));}

  const sleeper=roundedBox(W*.88,2.42,1.72,.20,M.red);sleeper.position.set(0,1.73,sleeperZ);g.add(sleeper);
  const roof=sphere(1,M.redLight,0,2.95,sleeperZ-.03,W*.46,.42,.92);g.add(roof);
  const roofCap=roundedBox(W*.80,.34,1.48,.15,M.redLight);roofCap.position.set(0,3.05,sleeperZ+.04);g.add(roofCap);

  const wind=quad([[-W*.35,1.72,sleeperZ-.88],[W*.35,1.72,sleeperZ-.88],[W*.31,2.60,sleeperZ-.80],[-W*.31,2.60,sleeperZ-.80]],M.glass);g.add(wind);
  for(const side of [-1,1]){
    const sidePts=[[sleeperZ-.72,1.70],[sleeperZ-.67,2.52],[sleeperZ+.18,2.52],[sleeperZ+.35,1.74]];
    g.add(sidePanel(side*W*.445,sidePts,M.glass,side>0));
    const sleeperWin=roundedBox(.025,.38,.34,.06,M.glass);sleeperWin.position.set(side*W*.448,2.48,sleeperZ+.56);g.add(sleeperWin);
  }

  const hoodProfile=[[-1.18,.62],[-1.18,1.12],[-.98,1.48],[-.62,1.72],[.20,1.82],[.92,1.72],[1.12,1.48],[1.16,.66]];
  const hood=profileMesh(hoodProfile,W*.82,M.red,.045);hood.position.z=hoodZ;g.add(hood);
  const hoodTop=sphere(.9,M.redLight,0,1.66,hoodZ-.10,W*.42,.23,1.22);g.add(hoodTop);
  for(const side of [-1,1]){const vent=roundedBox(.035,.15,.44,.04,M.dark);vent.position.set(side*W*.415,1.54,hoodZ+.26);g.add(vent);}

  for(const side of [-1,1]){const fender=new THREE.Mesh(new THREE.TorusGeometry(.56,.09,10,36,Math.PI),M.redDark);fender.rotation.y=Math.PI/2;fender.rotation.z=Math.PI/2;fender.position.set(side*(W/2-.07),.60,frontAxleZ);g.add(fender);}

  const grilleZ=bumperZ-.04;addChromeGrille(g,W,grilleZ);
  const bumper=roundedBox(W*.84,.28,.26,.05,M.redDark);bumper.position.set(0,.55,bumperZ-.02);g.add(bumper);
  const lower=roundedBox(W*.55,.15,.16,.04,M.dark);lower.position.set(0,.49,bumperZ-.16);g.add(lower);
  for(const side of [-1,1]){const head=roundedBox(.36,.27,.09,.06,M.lamp);head.position.set(side*W*.33,.84,bumperZ-.14);head.rotation.z=side*.10;g.add(head);const fog=roundedBox(.13,.15,.07,.035,M.lamp);fog.position.set(side*W*.39,.48,bumperZ-.18);g.add(fog);}

  for(const side of [-1,1]){
    const arm=box(.035,.55,.035,M.dark,side*W*.52,2.16,sleeperZ-.78);arm.rotation.z=side*.16;g.add(arm);
    const mirror=roundedBox(.18,.38,.12,.045,M.chrome);mirror.position.set(side*W*.61,2.23,sleeperZ-.80);g.add(mirror);
    const antenna=box(.012,1.15,.012,M.dark,side*W*.32,3.50,sleeperZ+.12);g.add(antenna);
  }
  addCabRoofMarkers(g,W,sleeperZ-.86,2.88);

  addWheelPair(g,frontAxleZ,W,.50,.33);addWheelPair(g,drive1Z,W,.50,.35);addWheelPair(g,drive2Z,W,.50,.35);
  for(const z of [frontAxleZ,drive1Z,drive2Z]){g.add(box(.31,.13,.76,M.plastic,-W/2-.09,.92,z));g.add(box(.31,.13,.76,M.plastic,W/2+.09,.92,z));}

  g.add(box(W*.72,.24,1.10,M.redDark,0,.66,sleeperZ+.22));
  for(const side of [-1,1]){g.add(box(.045,1.25,.45,M.redDark,side*W*.43,1.62,sleeperZ+.50));g.add(box(.07,.05,.05,M.amber,side*W*.46,.63,sleeperZ-.35));}
  return g;
}

function makePallet(p,h,alt){const g=new THREE.Group(),L=p.L/1000,W=p.W/1000,H=Math.max(.28,h/1000);for(const x of [-W*.30,0,W*.30])g.add(box(.10,.09,L*.86,M.wood2,x,.04,0));for(let i=0;i<5;i++)g.add(box(.09,.022,L,M.wood,-W*.42+i*W*.21,.12,0));g.add(box(W*.92,H,L*.92,alt?M.load2:M.load,0,.14+H/2,0));return g;}

function renderSceneTruck(){
  if(truckRoot)scene.remove(truckRoot);if(cargoRoot)scene.remove(cargoRoot);
  truckRoot=new THREE.Group();const trailer=buildTrailer(S.v);truckRoot.add(trailer.group);truckRoot.add(buildTractor(S.v));scene.add(truckRoot);
  cargoRoot=new THREE.Group();let remaining=S.show;for(let layer=0;layer<S.layers&&remaining>0;layer++){const count=Math.min(S.floor,remaining);for(let i=0;i<count;i++){const pos=S.pk.pos[i],p=makePallet(S.p,S.h,(i+layer)%2===1);p.position.set(pos.x/1000,trailer.floorY+.08+layer*S.h/1000,pos.z/1000);p.rotation.y=-pos.r;cargoRoot.add(p);}remaining-=count;}scene.add(cargoRoot);
  const vis=E.curt.classList.contains('active');curtainLeft.visible=vis;curtainRight.visible=vis;roofGroup.visible=E.roof.classList.contains('active');const a=doorsOpen?Math.PI*.78:0;rearDoorLeft.rotation.y=a;rearDoorRight.rotation.y=-a;doorAnim=a;truckRoot.position.x=away?30:0;cargoRoot.position.x=truckRoot.position.x;driveAnim=truckRoot.position.x;resetView();
}

function init3D(){
  scene=new THREE.Scene();scene.background=new THREE.Color(0xf3f5f4);scene.fog=new THREE.Fog(0xf3f5f4,34,80);
  camera=new THREE.PerspectiveCamera(35,1,.05,150);renderer=new THREE.WebGLRenderer({antialias:true});renderer.setPixelRatio(Math.min(devicePixelRatio||1,2));renderer.shadowMap.enabled=true;renderer.shadowMap.type=THREE.PCFSoftShadowMap;renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.05;E.host.innerHTML='';E.host.appendChild(renderer.domElement);
  controls=new OrbitControls(camera,renderer.domElement);controls.enableDamping=true;controls.dampingFactor=.065;controls.maxPolarAngle=Math.PI*.49;controls.minDistance=6;controls.maxDistance=55;
  scene.add(new THREE.HemisphereLight(0xffffff,0x707a75,2.4));const key=new THREE.DirectionalLight(0xffffff,3.2);key.position.set(-12,17,9);key.castShadow=true;key.shadow.mapSize.set(2048,2048);key.shadow.camera.left=-30;key.shadow.camera.right=30;key.shadow.camera.top=30;key.shadow.camera.bottom=-30;scene.add(key);const fill=new THREE.DirectionalLight(0xe5edf5,1.25);fill.position.set(12,8,-14);scene.add(fill);const rim=new THREE.DirectionalLight(0xffffff,.85);rim.position.set(-8,6,-20);scene.add(rim);
  const ground=new THREE.Mesh(new THREE.PlaneGeometry(115,115),mat(0xe4e8e5,.98,0));ground.rotation.x=-Math.PI/2;ground.position.y=-.02;ground.receiveShadow=true;scene.add(ground);const grid=new THREE.GridHelper(68,68,0xbfc8c3,0xd5dcd8);grid.position.y=.004;grid.material.opacity=.15;grid.material.transparent=true;scene.add(grid);
  new ResizeObserver(()=>{const w=E.host.clientWidth,h=E.host.clientHeight||520;renderer.setSize(w,h,false);camera.aspect=w/h;camera.updateProjectionMatrix();}).observe(E.host);animate();
}
function resetView(){if(!S||!camera||!controls)return;const L=S.v.L/1000;camera.position.set(7.8,5.3,Math.max(12.5,L*.70));controls.target.set(0,1.55,-1.35);controls.update();}
function animate(){requestAnimationFrame(animate);const td=doorsOpen?Math.PI*.78:0;doorAnim+=(td-doorAnim)*.12;if(rearDoorLeft&&rearDoorRight){rearDoorLeft.rotation.y=doorAnim;rearDoorRight.rotation.y=-doorAnim;}const tx=away?30:0;driveAnim+=(tx-driveAnim)*.055;if(truckRoot&&cargoRoot){truckRoot.position.x=driveAnim;cargoRoot.position.x=driveAnim;}controls?.update();renderer?.render(scene,camera);}
function syncPresets(){const v=VEHICLES[E.v.value]||VEHICLES.semi136;E.cv.classList.toggle('show',E.v.value==='custom');E.L.value=v.L;E.W.value=v.W;E.H.value=v.H;E.pay.value=v.payload;const p=PALLETS[E.p.value]||PALLETS.eur;E.cp.classList.toggle('show',E.p.value==='custom');E.pL.value=p.L;E.pW.value=p.W;}
function bind(){E.v.addEventListener('change',()=>{syncPresets();calculate();});E.p.addEventListener('change',()=>{syncPresets();calculate();});[E.L,E.W,E.H,E.pay,E.pL,E.pW,E.loadH,E.pw,E.qty,E.gap,E.stack].forEach(el=>el.addEventListener('input',calculate));E.curt.addEventListener('click',()=>{E.curt.classList.toggle('active');const vis=E.curt.classList.contains('active');if(curtainLeft&&curtainRight){curtainLeft.visible=vis;curtainRight.visible=vis;}});E.roof.addEventListener('click',()=>{E.roof.classList.toggle('active');if(roofGroup)roofGroup.visible=E.roof.classList.contains('active');});E.doors.addEventListener('click',()=>{doorsOpen=!doorsOpen;E.doors.classList.toggle('active',doorsOpen);E.doors.textContent=doorsOpen?'Закрыть двери':'Открыть двери';});E.drive.addEventListener('click',()=>{away=!away;E.drive.classList.toggle('active',away);E.drive.textContent=away?'Вернуть фуру':'Уехал';});E.reset.addEventListener('click',()=>{doorsOpen=false;away=false;E.doors.classList.remove('active');E.doors.textContent='Открыть двери';E.drive.classList.remove('active');E.drive.textContent='Уехал';resetView();});}

init3D();syncPresets();bind();calculate();
