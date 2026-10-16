/* pallet3dReferenceV123 — workshop photo reference 1250x1180 */
(function(){
  const state=window.pallet3DState||(window.pallet3DState={mode:'3d',angle:-34,selected:'all'});
  let active=null,raf=0,syncQueued=false,resizeTimer=0;
  const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
  const near=(a,b,t=2)=>Math.abs(Number(a)-Number(b))<=t;
  const num=(v,d=0)=>Number.isFinite(Number(v))?Number(v):d;
  const el=id=>document.getElementById(id);
  const part=i=>typeof window.pallet3DPart==='function'?window.pallet3DPart(i):{n:0,t:22,w:98,l:0,name:'Деталь',index:i};
  const spread=(count,span,item=0)=>count<=1?[0]:Array.from({length:count},(_,i)=>-span/2+item/2+i*(span-item)/(count-1));

  function resolveProfile(inputL,inputW){
    const a=Math.max(300,num(inputL,1250)),b=Math.max(300,num(inputW,1180));
    if((near(a,1250)&&near(b,1180))||(near(a,1180)&&near(b,1250))){
      return {key:'1250x1180',width:1250,length:1180,deckMax:9,bindingCount:3,runnerLengths:[1180,1180,1180],spec:'Фото-эталон 1250 × 1180 · 9 досок настила · 3 поперечины · 9 шашек · 3 нижние лыжи'};
    }
    if((near(a,800)&&near(b,1200))||(near(a,1200)&&near(b,800))){
      return {key:'800x1200',width:800,length:1200,deckMax:7,bindingCount:3,runnerLengths:[1200,1200,1200],spec:'Ширина 800 × длина 1200 · 3 лыжи по 1200 · обвязка 3 · настил до 7'};
    }
    const width=b,length=a;
    return {key:'dynamic',width,length,deckMax:width<=850?7:9,bindingCount:3,runnerLengths:null,spec:`Ширина ${Math.round(width)} × длина ${Math.round(length)} · динамическая геометрия · настил до ${width<=850?7:9}`};
  }

  function setInput(id,value){const x=el(id);if(!x)return false;const v=String(value);if(x.value===v)return false;x.value=v;return true;}
  function syncProfileInputs(profile){
    const deck=el('n0');
    if(deck)deck.max=String(profile.deckMax);
    // 3D reference must never rewrite production calculator values.
  }

  function currentSignature(){
    const ids=['pL','pW','n0','n1','n2','n3','n4','n5','n6','t0','t1','t2','t3','t4','t5','t6','w0','w1','w2','w3','w4','w5','w6','l0','l1','l2','l3','l4','l5','l6'];
    return ids.map(id=>el(id)?.value??'').join('|')+'|'+(state.mode||'3d')+'|'+(state.selected||'all');
  }

  function dispose(){
    cancelAnimationFrame(raf);clearTimeout(resizeTimer);
    if(!active)return;
    try{
      active.observer?.disconnect();
      active.scene?.traverse(o=>{
        o.geometry?.dispose?.();
        if(o.material)(Array.isArray(o.material)?o.material:[o.material]).forEach(m=>{m.map?.dispose?.();m.dispose?.();});
      });
      active.renderer?.dispose?.();
    }catch(_){}
    active=null;
  }

  function woodTexture(seed,base='#e7c28f',grain='#91663d'){
    const c=document.createElement('canvas');c.width=1024;c.height=256;const x=c.getContext('2d');x.fillStyle=base;x.fillRect(0,0,c.width,c.height);
    let s=seed||1;const rnd=()=>{s=(s*1664525+1013904223)>>>0;return s/4294967296;};
    for(let i=0;i<78;i++){
      const y=rnd()*c.height,amp=.8+rnd()*5,period=120+rnd()*260;x.beginPath();
      for(let px=0;px<=c.width;px+=8){const yy=y+Math.sin((px+rnd()*4)/period*Math.PI*2)*amp+(rnd()-.5)*1.15;px?x.lineTo(px,yy):x.moveTo(px,yy);}
      x.strokeStyle=grain;x.globalAlpha=.035+rnd()*.09;x.lineWidth=.55+rnd()*1.05;x.stroke();
    }
    for(let k=0;k<8;k++){
      const cx=60+rnd()*(c.width-120),cy=22+rnd()*(c.height-44),rx=5+rnd()*18,ry=2+rnd()*7;x.globalAlpha=.13;x.strokeStyle='#765034';x.lineWidth=1.15;
      x.beginPath();x.ellipse(cx,cy,rx,ry,(rnd()-.5)*.18,0,Math.PI*2);x.stroke();
      x.beginPath();x.ellipse(cx,cy,rx*.5,ry*.5,(rnd()-.5)*.18,0,Math.PI*2);x.stroke();
    }
    x.globalAlpha=1;const t=new THREE.CanvasTexture(c);t.wrapS=t.wrapT=THREE.RepeatWrapping;t.colorSpace=THREE.SRGBColorSpace;t.anisotropy=8;return t;
  }

  function roundedBoxGeometry(dx,dy,dz,r=.035){
    const radius=Math.max(.008,Math.min(r,dx*.045,dz*.10,dy*.18));
    const sh=new THREE.Shape(),x=-dx/2,z=-dz/2,w=dx,h=dz,rr=Math.min(radius,w/2,h/2);
    sh.moveTo(x+rr,z);sh.lineTo(x+w-rr,z);sh.quadraticCurveTo(x+w,z,x+w,z+rr);sh.lineTo(x+w,z+h-rr);sh.quadraticCurveTo(x+w,z+h,x+w-rr,z+h);sh.lineTo(x+rr,z+h);sh.quadraticCurveTo(x,z+h,x,z+h-rr);sh.lineTo(x,z+rr);sh.quadraticCurveTo(x,z,x+rr,z);
    const g=new THREE.ExtrudeGeometry(sh,{depth:dy,steps:1,bevelEnabled:true,bevelSegments:1,bevelSize:Math.min(rr*.55,.028),bevelThickness:Math.min(dy*.12,.025),curveSegments:2});
    g.center();g.rotateX(Math.PI/2);g.computeVertexNormals();return g;
  }

  function render(inputL,inputW){
    const root=el('palletPreview3D');if(!root)return;
    if(!window.THREE){root.innerHTML='<div class="pallet3dFallback">3D недоступен в этом браузере</div>';return;}
    dispose();
    const profile=resolveProfile(inputL,inputW);syncProfileInputs(profile);
    const P=[0,1,2,3,4,5,6].map(part),deck=P[0],bindParts=[P[1],P[2]],runnerParts=[P[3],P[4]],block1=P[5],block2=P[6];
    const isReference=profile.key==='1250x1180';
    const rawDeck=Math.max(0,Math.round(num(deck.n))),deckCount=isReference?9:Math.min(profile.deckMax,rawDeck);
    const rawBlocks=Math.max(0,Math.round(num(block1.n)))+Math.max(0,Math.round(num(block2.n))),blockCount=isReference?9:Math.min(9,rawBlocks||9);
    const runnerCount=isReference?3:(profile.runnerLengths?profile.runnerLengths.length:Math.max(1,Math.min(7,Math.round(num(runnerParts[0].n)+num(runnerParts[1].n))||3)));
    const mode=state.mode||'3d';
    const chip=(k,label,c)=>`<button type="button" class="palletPartChip ${state.selected===k?'active':''}" data-p3d-part="${k}">${label}<b>${c}</b></button>`;
    const refTag=isReference?'<span style="display:inline-flex;margin-right:7px;padding:3px 7px;border-radius:999px;background:#173f35;color:#fff;font-size:10px;font-weight:900;letter-spacing:.04em">ФОТО-ЭТАЛОН</span>':'';
    root.innerHTML=`<div class="pallet3dToolbar" role="tablist"><button type="button" data-p3d-mode="3d" class="${mode==='3d'?'active':''}">3D</button><button type="button" data-p3d-mode="top" class="${mode==='top'?'active':''}">Сверху</button><button type="button" data-p3d-mode="side" class="${mode==='side'?'active':''}">Сбоку</button><button type="button" data-p3d-mode="explode" class="${mode==='explode'?'active':''}">${mode==='explode'?'Собрать':'Разнести'}</button></div><div class="pallet3dSpec" style="display:flex;justify-content:center;text-align:center;margin:8px auto 2px;padding:8px 12px;max-width:780px;border:1px solid rgba(31,111,92,.15);border-radius:12px;background:rgba(240,248,244,.92);color:#31584c;font-size:11px;font-weight:800;line-height:1.4">${refTag}${profile.spec}</div><div class="palletReferenceStage"><div class="palletReferenceTitle"><strong>${Math.round(profile.width)} × ${Math.round(profile.length)} мм</strong><span>${mode==='explode'?'Разнесённая конструкция':'Конструкция по образцу'}</span></div><div class="palletReferenceHost"></div></div><div class="palletModelLegend">${chip('deck','Настил',deckCount)}${chip('cross','Обвязка',3)}${chip('runner','Лыжи',runnerCount)}${chip('block','Шашки',blockCount)}</div><div class="palletModelHint">Для 1250 × 1180 используется отдельная модель по вашим фото · вращайте мышкой или пальцем · колесо — масштаб</div>`;

    const host=root.querySelector('.palletReferenceHost'),cw=Math.max(280,host.clientWidth||760),ch=window.innerWidth<620?390:510;
    const renderer=new THREE.WebGLRenderer({antialias:true,alpha:true,powerPreference:'high-performance'});renderer.setPixelRatio(Math.min(window.devicePixelRatio||1,2));renderer.setSize(cw,ch,false);renderer.setClearColor(0,0);renderer.shadowMap.enabled=true;renderer.shadowMap.type=THREE.PCFSoftShadowMap;renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.08;host.appendChild(renderer.domElement);
    const scene=new THREE.Scene(),camera=new THREE.PerspectiveCamera(33,cw/ch,.1,120),world=new THREE.Group();scene.add(world);
    const groups={runner:new THREE.Group(),block:new THREE.Group(),cross:new THREE.Group(),deck:new THREE.Group()};Object.values(groups).forEach(g=>world.add(g));
    scene.add(new THREE.HemisphereLight(0xfffcf4,0x766b61,2.45));
    const key=new THREE.DirectionalLight(0xfff0d2,4.5);key.position.set(-12,18,12);key.castShadow=true;key.shadow.mapSize.set(2048,2048);key.shadow.camera.near=.5;key.shadow.camera.far=65;key.shadow.camera.left=-18;key.shadow.camera.right=18;key.shadow.camera.top=18;key.shadow.camera.bottom=-18;scene.add(key);
    const fill=new THREE.DirectionalLight(0xe4efff,1.15);fill.position.set(12,8,-10);scene.add(fill);
    const floor=new THREE.Mesh(new THREE.PlaneGeometry(40,36),new THREE.ShadowMaterial({color:0x64584e,opacity:.13}));floor.rotation.x=-Math.PI/2;floor.position.y=-.025;floor.receiveShadow=true;scene.add(floor);

    const S=.01,PW=profile.width*S,PL=profile.length*S,selected=state.selected||'all';
    const textures={deck:woodTexture(17,'#f3dfbd','#9a724b'),cross:woodTexture(31,'#ecd2a8','#906642'),runner:woodTexture(47,'#e8ca9a','#875d39'),block:woodTexture(61,'#dfbb86','#805433')};
    Object.values(textures).forEach((t,i)=>t.repeat.set(i===3?1.4:3.2,1));
    const colors={deck:[0xf3dab2,0xefd1a4,0xf6e0bf],cross:[0xeccda0,0xe6c18f,0xf0d5ad],runner:[0xe4c08d,0xddb47f,0xe9ca9a],block:[0xd8aa72,0xdfb783,0xd2a069]};
    function mat(kind,i){const on=selected==='all'||selected===kind,map=textures[kind].clone();map.needsUpdate=true;map.offset.x=(i*.149)%1;return new THREE.MeshStandardMaterial({map,color:on?colors[kind][i%colors[kind].length]:0xbdb8b0,roughness:.78,metalness:0,transparent:!on,opacity:on?1:.15,depthWrite:on,emissive:selected===kind?0x14382e:0,emissiveIntensity:selected===kind?.09:0});}
    function piece(kind,dx,dy,dz,x,y,z,i,group){const g=roundedBoxGeometry(dx,dy,dz,kind==='block'?.055:.035),m=new THREE.Mesh(g,mat(kind,i));m.position.set(x,y,z);m.castShadow=true;m.receiveShadow=true;group.add(m);return m;}
    const nailGeo=new THREE.CylinderGeometry(.026,.026,.016,12),nailMat=new THREE.MeshStandardMaterial({color:0x5d5a56,roughness:.38,metalness:.45});
    function nail(x,y,z){const n=new THREE.Mesh(nailGeo,nailMat);n.position.set(x,y,z);n.castShadow=true;groups.deck.add(n);}

    const runnerT=isReference?.22:Math.max(.15,num(runnerParts[0].t,22)*S),runnerW=isReference?.98:Math.max(.58,num(runnerParts[0].w,98)*S);
    const blockH=isReference?.78:Math.max(.62,num(block1.t||block2.t,75)*S),blockXSize1=isReference?1.50:Math.max(.72,num(block1.l,150)*S),blockZSize1=isReference?.98:Math.max(.72,num(block1.w,98)*S),blockXSize2=isReference?.98:Math.max(.72,num(block2.l,98)*S),blockZSize2=isReference?1.00:Math.max(.72,num(block2.w,100)*S);
    const bindT=isReference?.22:Math.max(.15,num(bindParts[0].t,22)*S),bindDepth=isReference?.98:Math.max(.58,num(bindParts[0].w,98)*S);
    const deckT=isReference?.22:Math.max(.15,num(deck.t,22)*S),deckW=isReference?.98:Math.max(.58,num(deck.w,98)*S);

    const runnerLengths=profile.runnerLengths||Array.from({length:runnerCount},(_,i)=>Math.min(profile.length,num((i<Math.max(0,num(runnerParts[0].n)))?runnerParts[0].l:runnerParts[1].l,profile.length)));
    const runnerActualW=Math.min(runnerW,PW/Math.max(3,runnerLengths.length)*.56);
    const edgeRunnerX=Math.max(0,PW/2-runnerActualW/2-.03);
    let runnerXs;
    if(runnerLengths.length===5) runnerXs=[-edgeRunnerX,-edgeRunnerX*.5,0,edgeRunnerX*.5,edgeRunnerX];
    else if(runnerLengths.length===3) runnerXs=[-edgeRunnerX,0,edgeRunnerX];
    else runnerXs=spread(runnerLengths.length,PW,runnerActualW);
    runnerLengths.forEach((mm,i)=>{const rz=clamp(mm*S,Math.min(PL*.55,10.5),PL);piece('runner',runnerActualW,runnerT,rz,runnerXs[i],runnerT/2,0,i,groups.runner);});

    const blockY=runnerT+blockH/2;
    for(let zi=0;zi<3;zi++)for(let xi=0;xi<3;xi++){
      const idx=zi*3+xi;if(idx>=blockCount)continue;
      const centerType=(xi===1),bx=centerType?blockXSize2:blockXSize1,bz=centerType?blockZSize2:blockZSize1;
      const sx=xi===0?-1:xi===2?1:0,sz=zi===0?-1:zi===2?1:0;
      const bxPos=sx===0?0:sx*Math.max(0,PW/2-bx/2-.03);
      const bzPos=sz===0?0:sz*Math.max(0,PL/2-bz/2-.03);
      piece('block',bx,blockH,bz,bxPos,blockY,bzPos,idx,groups.block);
    }

    const bindY=runnerT+blockH+bindT/2;
    const bindZ=[-PL/2+bindDepth/2+.02,0,PL/2-bindDepth/2-.02];
    bindZ.forEach((z,i)=>piece('cross',PW,bindT,bindDepth,0,bindY,z,i,groups.cross));

    const topY=runnerT+blockH+bindT+deckT/2;
    const actualDeckW=deckCount?Math.min(deckW,(PW*.92/Math.max(1,deckCount))*.78):deckW;
    const topXs=deckCount?spread(deckCount,PW,actualDeckW):[];
    topXs.forEach((x,i)=>{
      piece('deck',actualDeckW,deckT,PL,x,topY,0,i,groups.deck);
      if(selected==='all'||selected==='deck')bindZ.forEach(z=>{const dx=Math.min(.07,actualDeckW*.23);nail(x-dx,topY+deckT/2+.014,z);nail(x+dx,topY+deckT/2+.014,z);});
    });

    const exploded=mode==='explode',offsets={runner:0,block:exploded?1.25:0,cross:exploded?2.55:0,deck:exploded?3.85:0};
    let yaw=num(state.angle,-34)*Math.PI/180,pitch=.43,distance=clamp(Math.max(PW,PL)*1.68,15,28);
    function draw(){
      if(mode==='top'){camera.up.set(0,0,-1);camera.position.set(0,Math.max(PW,PL)*2.0,.001);camera.lookAt(0,topY*.55,0);}
      else if(mode==='side'){camera.up.set(0,1,0);camera.position.set(Math.max(PW,PL)*2.0,Math.max(4.2,topY*2.0),0);camera.lookAt(0,topY*.55,0);}
      else{camera.up.set(0,1,0);const cy=Math.sin(pitch)*distance,rad=Math.cos(pitch)*distance;camera.position.set(Math.cos(yaw)*rad,cy+2.0,Math.sin(yaw)*rad);camera.lookAt(0,exploded?3.1:topY*.42,0);}
      renderer.render(scene,camera);
    }
    active={renderer,scene,camera,groups,mode,signature:currentSignature(),draw,profile};
    if(exploded){const t0=performance.now();const animate=t=>{const q=clamp((t-t0)/420,0,1),e=1-Math.pow(1-q,3);groups.block.position.y=offsets.block*e;groups.cross.position.y=offsets.cross*e;groups.deck.position.y=offsets.deck*e;draw();if(q<1)raf=requestAnimationFrame(animate);};raf=requestAnimationFrame(animate);}else draw();

    const canvas=renderer.domElement;let dragging=false,lastX=0,lastY=0;
    canvas.addEventListener('pointerdown',e=>{if(mode==='top'||mode==='side')return;dragging=true;lastX=e.clientX;lastY=e.clientY;canvas.setPointerCapture?.(e.pointerId);canvas.classList.add('dragging');});
    canvas.addEventListener('pointermove',e=>{if(!dragging||mode==='top'||mode==='side')return;const dx=e.clientX-lastX,dy=e.clientY-lastY;lastX=e.clientX;lastY=e.clientY;yaw-=dx*.009;pitch=clamp(pitch-dy*.006,.15,.95);state.angle=yaw*180/Math.PI;draw();});
    const stop=()=>{dragging=false;canvas.classList.remove('dragging');};canvas.addEventListener('pointerup',stop);canvas.addEventListener('pointercancel',stop);
    canvas.addEventListener('wheel',e=>{if(mode==='top'||mode==='side')return;e.preventDefault();distance=clamp(distance*(e.deltaY>0?1.08:.92),10,38);draw();},{passive:false});

    root.querySelectorAll('[data-p3d-mode]').forEach(btn=>btn.addEventListener('click',()=>{state.mode=btn.dataset.p3dMode;render(num(el('pL')?.value),num(el('pW')?.value));}));
    root.querySelectorAll('[data-p3d-part]').forEach(btn=>btn.addEventListener('click',()=>{const k=btn.dataset.p3dPart;state.selected=state.selected===k?'all':k;render(num(el('pL')?.value),num(el('pW')?.value));}));

    if(window.ResizeObserver){
      const observer=new ResizeObserver(()=>{clearTimeout(resizeTimer);resizeTimer=setTimeout(()=>{if(!active||!host.isConnected)return;const w=Math.max(280,host.clientWidth),h=window.innerWidth<620?390:510;renderer.setSize(w,h,false);camera.aspect=w/h;camera.updateProjectionMatrix();draw();},100);});observer.observe(host);active.observer=observer;
    }
  }

  window.renderDynamicPallet=render;
  window.rerenderPallet3D=function(){
    const sig=currentSignature();
    if(active&&active.signature===sig&&active.mode===(state.mode||'3d')&&document.querySelector('.palletReferenceHost canvas')){active.draw();return;}
    render(num(el('pL')?.value),num(el('pW')?.value));
  };
  setTimeout(()=>render(num(el('pL')?.value),num(el('pW')?.value)),120);
  window.addEventListener('resize',()=>{clearTimeout(resizeTimer);resizeTimer=setTimeout(()=>window.rerenderPallet3D?.(),160);});
})();
