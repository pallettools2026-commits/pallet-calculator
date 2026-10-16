/* pallet3dReferenceV110 — realistic connected pallet geometry */
(function(){
  const state=window.pallet3DState||(window.pallet3DState={mode:'3d',angle:-32,selected:'all'});
  let active=null,raf=0,syncQueued=false;
  const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
  const near=(a,b,t=2)=>Math.abs(Number(a)-Number(b))<=t;
  const distribute=(count,span,item=0)=>count<=1?[0]:Array.from({length:count},(_,i)=>-span/2+item/2+i*(span-item)/(count-1));
  const part=i=>typeof window.pallet3DPart==='function'?window.pallet3DPart(i):{n:0,t:0,w:0,l:0,name:'Деталь',index:i};

  function profileFor(L,W){
    if(near(L,1180)&&near(W,1250)) return {
      key:'w1250-l1180',deckMax:9,bindingCount:3,runnerLengths:[1180,1050,1050,1050,1180],
      spec:'1250 × 1180 · 5 лыж: 2×1180 + 3×1050 · обвязка обязательна · настил до 9'
    };
    if(near(L,1200)&&near(W,800)) return {
      key:'w800-l1200',deckMax:7,bindingCount:3,runnerLengths:[1200,1200,1200],
      spec:'800 × 1200 · 3 лыжи по 1200 · обвязка обязательна · настил до 7'
    };
    return {key:'dynamic',deckMax:W<=850?7:9,bindingCount:3,runnerLengths:null,
      spec:`${Math.round(W)} × ${Math.round(L)} · геометрия по текущим размерам · настил до ${W<=850?7:9}`};
  }

  function setInput(id,value){const el=document.getElementById(id);if(!el)return false;const next=String(value);if(el.value===next)return false;el.value=next;return true;}
  function syncProfileInputs(profile){
    let changed=false;const deck=document.getElementById('n0');
    if(deck){deck.max=String(profile.deckMax);const n=Math.max(0,Math.round(Number(deck.value)||0));if(n>profile.deckMax){deck.value=String(profile.deckMax);changed=true;}}
    if(profile.key==='w1250-l1180'){
      changed=setInput('n3',2)||changed;changed=setInput('l3',1180)||changed;
      changed=setInput('n4',3)||changed;changed=setInput('l4',1050)||changed;
      const n1=document.getElementById('n1');if(n1&&Number(n1.value||0)<3){n1.value='3';changed=true;}
    } else if(profile.key==='w800-l1200'){
      changed=setInput('n3',3)||changed;changed=setInput('l3',1200)||changed;
      changed=setInput('n4',0)||changed;changed=setInput('l4',1200)||changed;
      const n1=document.getElementById('n1');if(n1&&Number(n1.value||0)<3){n1.value='3';changed=true;}
    }
    if(changed&&!syncQueued&&typeof window.calc==='function'){
      syncQueued=true;setTimeout(()=>{syncQueued=false;try{window.calc();}catch(_){}},0);
    }
  }

  function dispose(){
    cancelAnimationFrame(raf);if(!active)return;
    try{
      active.observer?.disconnect();
      active.scene?.traverse(o=>{o.geometry?.dispose?.();if(o.material)(Array.isArray(o.material)?o.material:[o.material]).forEach(m=>{m.map?.dispose?.();m.dispose?.();});});
      active.renderer?.dispose?.();
    }catch(_){}
    active=null;
  }

  function woodTexture(seed,base='#ead4af',grain='#8e714a'){
    const c=document.createElement('canvas');c.width=768;c.height=192;const x=c.getContext('2d');x.fillStyle=base;x.fillRect(0,0,c.width,c.height);
    let s=seed||1;const rnd=()=>{s=(s*1664525+1013904223)>>>0;return s/4294967296;};
    for(let i=0;i<64;i++){
      const y=rnd()*c.height,amp=1+rnd()*4.5,period=100+rnd()*220;x.beginPath();
      for(let px=0;px<=c.width;px+=8){const yy=y+Math.sin((px+rnd()*3)/period*Math.PI*2)*amp+(rnd()-.5)*.9;px?x.lineTo(px,yy):x.moveTo(px,yy);}
      x.strokeStyle=grain;x.globalAlpha=.035+rnd()*.095;x.lineWidth=.55+rnd()*.95;x.stroke();
    }
    for(let k=0;k<5;k++){
      const cx=45+rnd()*(c.width-90),cy=14+rnd()*(c.height-28),rx=4+rnd()*12,ry=2+rnd()*5;x.globalAlpha=.12;x.strokeStyle='#705335';x.lineWidth=1;
      x.beginPath();x.ellipse(cx,cy,rx,ry,(rnd()-.5)*.15,0,Math.PI*2);x.stroke();
    }
    x.globalAlpha=1;const t=new THREE.CanvasTexture(c);t.wrapS=t.wrapT=THREE.RepeatWrapping;t.colorSpace=THREE.SRGBColorSpace;t.anisotropy=8;return t;
  }
  function endTexture(seed){
    const c=document.createElement('canvas');c.width=256;c.height=256;const x=c.getContext('2d');x.fillStyle='#dcc49d';x.fillRect(0,0,256,256);
    let s=seed||9;const rnd=()=>{s=(s*1103515245+12345)&0x7fffffff;return s/0x7fffffff;};const cx=116+rnd()*24,cy=116+rnd()*24;
    for(let i=1;i<13;i++){x.beginPath();x.ellipse(cx,cy,7+i*7.4,5+i*6.5,(rnd()-.5)*.12,0,Math.PI*2);x.strokeStyle=i%3===0?'rgba(91,61,35,.22)':'rgba(105,75,47,.13)';x.lineWidth=1.1;x.stroke();}
    const t=new THREE.CanvasTexture(c);t.colorSpace=THREE.SRGBColorSpace;t.anisotropy=8;return t;
  }

  function render(L,W){
    const root=document.getElementById('palletPreview3D');if(!root)return;
    if(!window.THREE){root.innerHTML='<div class="pallet3dFallback">3D недоступен в этом браузере</div>';return;}
    dispose();L=Math.max(300,Number(L)||1200);W=Math.max(300,Number(W)||800);
    const profile=profileFor(L,W);syncProfileInputs(profile);
    const p=[0,1,2,3,4,5,6].map(part),deck=p[0],crossParts=[p[1],p[2]],runnerParts=[p[3],p[4]],blockParts=[p[5],p[6]];
    const raw={deck:Math.max(0,deck.n||0),cross:crossParts.reduce((a,b)=>a+Math.max(0,b.n||0),0),runner:runnerParts.reduce((a,b)=>a+Math.max(0,b.n||0),0),block:blockParts.reduce((a,b)=>a+Math.max(0,b.n||0),0)};
    const counts={deck:Math.min(profile.deckMax,raw.deck),cross:Math.max(profile.bindingCount,raw.cross),runner:profile.runnerLengths?profile.runnerLengths.length:raw.runner,block:raw.block};
    const mode=state.mode||'3d',chip=(k,label,c)=>`<button type="button" class="palletPartChip ${state.selected===k?'active':''}" data-p3d-part="${k}">${label}<b>${c}</b></button>`;
    root.innerHTML=`<div class="pallet3dToolbar" role="tablist"><button type="button" data-p3d-mode="3d" class="${mode==='3d'?'active':''}">3D</button><button type="button" data-p3d-mode="top" class="${mode==='top'?'active':''}">Сверху</button><button type="button" data-p3d-mode="side" class="${mode==='side'?'active':''}">Сбоку</button><button type="button" data-p3d-mode="explode" class="${mode==='explode'?'active':''}">${mode==='explode'?'Собрать':'Разнести'}</button></div><div class="pallet3dSpec" style="display:flex;justify-content:center;align-items:center;text-align:center;flex-wrap:wrap;gap:6px;margin:8px auto 2px;padding:8px 12px;max-width:760px;border:1px solid rgba(31,111,92,.14);border-radius:12px;background:rgba(238,247,243,.9);color:#31584c;font-size:11px;font-weight:750;line-height:1.35">${profile.spec}</div><div class="palletReferenceStage"><div class="palletReferenceTitle"><strong>Ширина ${Math.round(W)} × длина ${Math.round(L)} мм</strong><span>${mode==='explode'?'Разнесённая конструкция':'Реалистичная сборка поддона'}</span></div><div class="palletReferenceHost"></div></div><div class="palletModelLegend">${chip('deck','Настил',counts.deck)}${chip('cross','Обвязка',counts.cross)}${chip('runner','Лыжи',counts.runner)}${chip('block','Шашки',counts.block)}</div><div class="palletModelHint">Размеры и количество деталей меняют 3D автоматически · тяните для вращения · колесо — масштаб</div>`;

    const host=root.querySelector('.palletReferenceHost');
    const initialW=Math.max(280,host.clientWidth||760),initialH=window.innerWidth<620?390:500;
    const renderer=new THREE.WebGLRenderer({antialias:true,alpha:true,powerPreference:'high-performance'});renderer.setPixelRatio(Math.min(window.devicePixelRatio||1,2));renderer.setSize(initialW,initialH,false);renderer.setClearColor(0x000000,0);renderer.shadowMap.enabled=true;renderer.shadowMap.type=THREE.PCFSoftShadowMap;renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.04;host.appendChild(renderer.domElement);
    const scene=new THREE.Scene(),camera=new THREE.PerspectiveCamera(34,initialW/initialH,.1,120),world=new THREE.Group();scene.add(world);
    const groups={runner:new THREE.Group(),block:new THREE.Group(),cross:new THREE.Group(),deck:new THREE.Group()};Object.values(groups).forEach(g=>world.add(g));
    scene.add(new THREE.HemisphereLight(0xfffcf5,0x827569,2.35));
    const key=new THREE.DirectionalLight(0xfff2d7,4.0);key.position.set(-11,17,12);key.castShadow=true;key.shadow.mapSize.set(2048,2048);key.shadow.camera.near=.5;key.shadow.camera.far=60;key.shadow.camera.left=-18;key.shadow.camera.right=18;key.shadow.camera.top=18;key.shadow.camera.bottom=-18;scene.add(key);
    const fill=new THREE.DirectionalLight(0xe5edff,1.0);fill.position.set(13,9,-12);scene.add(fill);
    const floor=new THREE.Mesh(new THREE.PlaneGeometry(38,34),new THREE.ShadowMaterial({color:0x6e6256,opacity:.16}));floor.rotation.x=-Math.PI/2;floor.position.y=-.02;floor.receiveShadow=true;scene.add(floor);

    const scale=.01,SL=L*scale,SW=W*scale,selected=state.selected||'all';
    const longTex=woodTexture(21),crossTex=woodTexture(33,'#e5c99f','#8f7049'),runnerTex=woodTexture(45,'#ddbc8f','#856442'),blockTex=woodTexture(57,'#d8b382','#805e3c'),endTex=endTexture(71);
    longTex.repeat.set(3.4,1);crossTex.repeat.set(3.0,1);runnerTex.repeat.set(3.5,1);blockTex.repeat.set(1.4,1);
    const palette={deck:[0xf0d8b4,0xe8cda5,0xf4dfbe,0xe5c79d],cross:[0xe2c094,0xe8cba2,0xdab485],runner:[0xd5ad7b,0xcfa36d,0xddb887],block:[0xcda06c,0xd5aa76,0xc59660]},texMap={deck:longTex,cross:crossTex,runner:runnerTex,block:blockTex};
    function material(kind,idx,isEnd=false){const on=selected==='all'||selected===kind,map=(isEnd?endTex:texMap[kind]).clone();map.needsUpdate=true;if(!isEnd){map.offset.x=(idx*.137)%1;map.offset.y=(idx*.071)%1;}return new THREE.MeshStandardMaterial({map,color:on?palette[kind][idx%palette[kind].length]:0xc6c0b7,roughness:isEnd?.9:.78,metalness:0,transparent:!on,opacity:on?1:.16,depthWrite:on,emissive:selected===kind?0x18382f:0x000000,emissiveIntensity:selected===kind?.08:0});}
    function box(kind,dims,pos,idx,group,longAxis='x'){
      const g=new THREE.BoxGeometry(dims.x,dims.y,dims.z),mats=Array.from({length:6},()=>material(kind,idx,false));const e1=material(kind,idx,true),e2=material(kind,idx+17,true);if(longAxis==='x'){mats[0]=e1;mats[1]=e2;}else{mats[4]=e1;mats[5]=e2;}
      const m=new THREE.Mesh(g,mats);m.position.set(pos.x,pos.y,pos.z);m.castShadow=true;m.receiveShadow=true;group.add(m);
      const edge=new THREE.LineSegments(new THREE.EdgesGeometry(g,28),new THREE.LineBasicMaterial({color:0x775b3d,transparent:true,opacity:onOpacity(kind)}));edge.position.copy(m.position);group.add(edge);return m;
    }
    function onOpacity(kind){return (selected==='all'||selected===kind)?.11:.025;}
    const nailGeo=new THREE.CylinderGeometry(.027,.027,.018,12),nailMat=new THREE.MeshStandardMaterial({color:0x55524d,roughness:.38,metalness:.4});
    function nail(group,x,y,z){const n=new THREE.Mesh(nailGeo,nailMat);n.position.set(x,y,z);n.castShadow=true;group.add(n);}

    const runnerList=[],crossList=[],blockList=[];
    runnerParts.forEach(r=>{for(let i=0;i<Math.min(9,Math.max(0,r.n||0));i++)runnerList.push({...r});});
    crossParts.forEach(r=>{for(let i=0;i<Math.min(8,Math.max(0,r.n||0));i++)crossList.push({...r});});
    blockParts.forEach(r=>{for(let i=0;i<Math.min(18,Math.max(0,r.n||0));i++)blockList.push({...r});});
    if(profile.runnerLengths){runnerList.length=0;const t=[runnerParts[0]||{},runnerParts[1]||runnerParts[0]||{}];profile.runnerLengths.forEach((len,i)=>runnerList.push({...t[(i===0||i===profile.runnerLengths.length-1)?0:1],l:len,n:1}));}

    const runnerCount=Math.max(1,runnerList.length||Math.min(3,counts.runner||3)),runnerW=Math.max(.62,((runnerList[0]?.w)||95)*scale),runnerH=Math.max(.16,((runnerList[0]?.t)||22)*scale),runnerZ=distribute(runnerCount,SW*.94,runnerW);
    for(let i=0;i<runnerCount;i++){const r=runnerList[i]||runnerParts[0]||{},rw=Math.max(.54,(r.w||95)*scale),rh=Math.max(.15,(r.t||22)*scale),rl=clamp((r.l||L)*scale,Math.min(SL*.45,10.5),SL);box('runner',{x:rl,y:rh,z:rw},{x:0,y:rh/2,z:runnerZ[i]||0},i,groups.runner,'x');}

    const runnerSupportRows=runnerCount>=3?[runnerZ[0],runnerZ[Math.floor((runnerCount-1)/2)],runnerZ[runnerCount-1]]:distribute(3,SW*.72,0);
    const blockH=Math.max(.58,((blockList[0]?.t)||78)*scale),blockCount=Math.min(18,blockList.length||counts.block||9),blockX=[-SL*.39,0,SL*.39];
    if(blockCount){const cols=Math.min(3,Math.max(1,Math.ceil(Math.sqrt(blockCount)))),rows=Math.ceil(blockCount/cols),xs=cols===3?blockX:distribute(cols,SL*.78,0),zs=rows===3?runnerSupportRows:distribute(rows,SW*.72,0);for(let i=0;i<blockCount;i++){const b=blockList[i]||blockParts[0]||{},bw=Math.max(.62,(b.w||100)*scale),bl=Math.max(.62,(b.l||100)*scale),bh=Math.max(.56,(b.t||78)*scale),x=xs[i%cols],z=zs[Math.floor(i/cols)];box('block',{x:bl,y:bh,z:bw},{x,y:runnerH+bh/2,z},i,groups.block,'x');}}

    const crossCount=Math.max(profile.bindingCount,Math.min(6,crossList.length||counts.cross||profile.bindingCount)),crossH=Math.max(.15,((crossList[0]?.t)||22)*scale),crossX=crossCount===3?blockX:distribute(crossCount,SL*.90,Math.max(.5,((crossList[0]?.w)||95)*scale)),crossY=runnerH+blockH+crossH/2;
    for(let i=0;i<crossCount;i++){const r=crossList[i%Math.max(1,crossList.length)]||crossParts[i%2]||{},cw=Math.max(.5,(r.w||95)*scale),ch=Math.max(.15,(r.t||22)*scale);box('cross',{x:cw,y:ch,z:SW},{x:crossX[i]||0,y:crossY,z:0},i,groups.cross,'z');}

    const deckCount=clamp(raw.deck,0,profile.deckMax),deckW=Math.max(.52,(deck.w||95)*scale),deckH=Math.max(.15,(deck.t||22)*scale),deckLen=clamp((deck.l||L)*scale,SL*.70,SL),deckY=runnerH+blockH+crossH+deckH/2,deckZ=deckCount?distribute(deckCount,SW*.96,Math.min(deckW,SW*.84/Math.max(1,deckCount))):[];
    for(let i=0;i<deckCount;i++){const z=deckZ[i],bw=Math.min(deckW,SW*.90/Math.max(1,deckCount)*.82);box('deck',{x:deckLen,y:deckH,z:bw},{x:0,y:deckY,z},i,groups.deck,'x');if(selected==='all'||selected==='deck')crossX.forEach(nx=>{if(Math.abs(nx)<deckLen/2-.08){const dz=Math.min(.07,bw*.24);nail(groups.deck,nx,deckY+deckH/2+.014,z-dz);nail(groups.deck,nx,deckY+deckH/2+.014,z+dz);}});}

    const exploded=mode==='explode',offsets={block:1.2,cross:2.45,deck:3.8};let yaw=((Number(state.angle)||-32)*Math.PI/180),pitch=.42,distance=clamp(Math.max(SL,SW)*(exploded?2.05:1.72),16,30);
    function positionCamera(){if(mode==='top'){camera.up.set(0,0,-1);camera.position.set(0,Math.max(SL,SW)*2.05,.001);camera.lookAt(0,1,0);}else if(mode==='side'){camera.up.set(0,1,0);camera.position.set(Math.max(SL,SW)*2.05,Math.max(4.4,deckY*2.15),0);camera.lookAt(0,deckY*.65,0);}else{camera.up.set(0,1,0);const cy=Math.sin(pitch)*distance,rad=Math.cos(pitch)*distance;camera.position.set(Math.cos(yaw)*rad,cy+2,Math.sin(yaw)*rad);camera.lookAt(0,exploded?3.3:1.0,0);}renderer.render(scene,camera);}
    const observer=new ResizeObserver(entries=>{const r=entries[0]?.contentRect;if(!r||r.width<50)return;const h=window.innerWidth<620?390:500;renderer.setSize(r.width,h,false);camera.aspect=r.width/h;camera.updateProjectionMatrix();positionCamera();});observer.observe(host);
    active={renderer,scene,camera,groups,mode,positionCamera,observer};
    if(exploded){const t0=performance.now();const animate=t=>{const q=clamp((t-t0)/430,0,1),e=1-Math.pow(1-q,3);groups.block.position.y=offsets.block*e;groups.cross.position.y=offsets.cross*e;groups.deck.position.y=offsets.deck*e;positionCamera();if(q<1)raf=requestAnimationFrame(animate);};raf=requestAnimationFrame(animate);}else positionCamera();

    const canvas=renderer.domElement;let dragging=false,lastX=0,lastY=0;
    canvas.addEventListener('pointerdown',e=>{if(mode==='top'||mode==='side')return;dragging=true;lastX=e.clientX;lastY=e.clientY;canvas.setPointerCapture?.(e.pointerId);});
    canvas.addEventListener('pointermove',e=>{if(!dragging||mode==='top'||mode==='side')return;const dx=e.clientX-lastX,dy=e.clientY-lastY;lastX=e.clientX;lastY=e.clientY;yaw-=dx*.009;pitch=clamp(pitch-dy*.006,.16,.92);state.angle=yaw*180/Math.PI;positionCamera();});
    const stop=()=>dragging=false;canvas.addEventListener('pointerup',stop);canvas.addEventListener('pointercancel',stop);
    canvas.addEventListener('wheel',e=>{if(mode==='top'||mode==='side')return;e.preventDefault();distance=clamp(distance*(e.deltaY>0?1.08:.92),11,38);positionCamera();},{passive:false});
    root.querySelectorAll('[data-p3d-mode]').forEach(btn=>btn.addEventListener('click',()=>{const next=btn.dataset.p3dMode;state.mode=(next==='explode'&&state.mode==='explode')?'3d':next;render(L,W);}));
    root.querySelectorAll('[data-p3d-part]').forEach(btn=>btn.addEventListener('click',()=>{const k=btn.dataset.p3dPart;state.selected=state.selected===k?'all':k;render(L,W);}));
  }

  window.renderDynamicPallet=render;
  window.rerenderPallet3D=()=>render(Number(document.getElementById('pL')?.value),Number(document.getElementById('pW')?.value));
  setTimeout(()=>window.rerenderPallet3D(),120);
})();
