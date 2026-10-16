/* pallet3dReferenceV100 */
(function(){
  const state=window.pallet3DState||(window.pallet3DState={mode:'3d',angle:-32,selected:'all'});
  let active=null,raf=0,syncQueued=false;
  const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
  const part=i=>typeof window.pallet3DPart==='function'?window.pallet3DPart(i):{n:0,t:0,w:0,l:0,name:'Деталь',index:i};
  const distribute=(count,span,item=0)=>count<=1?[0]:Array.from({length:count},(_,i)=>-span/2+item/2+i*(span-item)/(count-1));
  const near=(a,b,t=2)=>Math.abs(Number(a)-Number(b))<=t;

  function profileFor(L,W){
    if(near(L,1180)&&near(W,1250))return{
      key:'w1250-l1180',name:'1250 × 1180',deckMax:9,bindingCount:3,
      runnerLengths:[1180,1050,1050,1050,1180],
      spec:'Ширина 1250 · длина 1180 · лыжи 2×1180 + 3×1050 · настил до 9'
    };
    if(near(L,1200)&&near(W,800))return{
      key:'w800-l1200',name:'800 × 1200',deckMax:7,bindingCount:3,
      runnerLengths:[1200,1200,1200],
      spec:'Ширина 800 · длина 1200 · лыжи 3×1200 · настил до 7'
    };
    return{
      key:'dynamic',name:'Динамический',deckMax:W<=850?7:9,bindingCount:3,runnerLengths:null,
      spec:`Ширина ${Math.round(W)} · длина ${Math.round(L)} · настил до ${W<=850?7:9}`
    };
  }

  function setInput(id,value){
    const el=document.getElementById(id);if(!el)return false;
    const next=String(value);if(el.value===next)return false;el.value=next;return true;
  }

  function syncProfileInputs(profile,L,W){
    let changed=false;
    const deck=document.getElementById('n0');
    if(deck){
      deck.max=String(profile.deckMax);
      const current=Math.max(0,Math.round(Number(deck.value)||0));
      if(current>profile.deckMax){deck.value=String(profile.deckMax);changed=true;}
    }
    if(profile.key==='w1250-l1180'){
      changed=setInput('n3',2)||changed;changed=setInput('l3',1180)||changed;
      changed=setInput('n4',3)||changed;changed=setInput('l4',1050)||changed;
      const n1=document.getElementById('n1');if(n1&&Number(n1.value||0)<3){n1.value='3';changed=true;}
    }else if(profile.key==='w800-l1200'){
      changed=setInput('n3',3)||changed;changed=setInput('l3',1200)||changed;
      changed=setInput('n4',0)||changed;changed=setInput('l4',1200)||changed;
      const n1=document.getElementById('n1');if(n1&&Number(n1.value||0)<3){n1.value='3';changed=true;}
    }
    if(changed&&!syncQueued&&typeof window.calc==='function'){
      syncQueued=true;setTimeout(()=>{syncQueued=false;try{window.calc();}catch(_){ }},0);
    }
  }

  function dispose(){
    cancelAnimationFrame(raf);
    if(!active)return;
    try{
      active.scene.traverse(o=>{
        if(o.geometry)o.geometry.dispose?.();
        if(o.material){(Array.isArray(o.material)?o.material:[o.material]).forEach(m=>{m.map?.dispose?.();m.dispose?.();});}
      });
      active.renderer.dispose();
    }catch(_){ }
    active=null;
  }

  function woodTexture(seed,base='#e1b173',grain='#8b5b31'){
    const c=document.createElement('canvas');c.width=768;c.height=192;const x=c.getContext('2d');
    x.fillStyle=base;x.fillRect(0,0,c.width,c.height);
    let s=seed||1;const rnd=()=>{s=(s*1664525+1013904223)>>>0;return s/4294967296;};
    for(let i=0;i<58;i++){
      const y=rnd()*c.height,amp=1.5+rnd()*5.5,period=95+rnd()*210;x.beginPath();
      for(let px=0;px<=c.width;px+=9){const yy=y+Math.sin((px+rnd()*4)/period*Math.PI*2)*amp+(rnd()-.5)*1.1;px?x.lineTo(px,yy):x.moveTo(px,yy);}
      x.strokeStyle=grain;x.globalAlpha=.055+rnd()*.12;x.lineWidth=.65+rnd()*1.1;x.stroke();
    }
    for(let k=0;k<6;k++){
      const cx=55+rnd()*(c.width-110),cy=18+rnd()*(c.height-36),rx=5+rnd()*14,ry=2+rnd()*6;x.globalAlpha=.14;x.strokeStyle='#6f472b';x.lineWidth=1.05;
      x.beginPath();x.ellipse(cx,cy,rx,ry,(rnd()-.5)*.15,0,Math.PI*2);x.stroke();x.beginPath();x.ellipse(cx,cy,rx*.47,ry*.47,(rnd()-.5)*.15,0,Math.PI*2);x.stroke();
    }
    x.globalAlpha=1;const t=new THREE.CanvasTexture(c);t.wrapS=t.wrapT=THREE.RepeatWrapping;t.colorSpace=THREE.SRGBColorSpace;t.anisotropy=8;return t;
  }

  function endTexture(seed){
    const c=document.createElement('canvas');c.width=256;c.height=256;const x=c.getContext('2d');x.fillStyle='#c8945e';x.fillRect(0,0,256,256);
    let s=seed||9;const rnd=()=>{s=(s*1103515245+12345)&0x7fffffff;return s/0x7fffffff;};const cx=118+rnd()*20,cy=116+rnd()*20;
    for(let i=1;i<14;i++){x.beginPath();x.ellipse(cx,cy,7+i*7.5,5+i*6.7,(rnd()-.5)*.14,0,Math.PI*2);x.strokeStyle=i%3===0?'rgba(83,49,24,.28)':'rgba(99,60,31,.16)';x.lineWidth=1.2;x.stroke();}
    for(let i=0;i<12;i++){const a=rnd()*Math.PI*2,l=38+rnd()*72;x.beginPath();x.moveTo(cx,cy);x.lineTo(cx+Math.cos(a)*l,cy+Math.sin(a)*l);x.strokeStyle='rgba(92,54,28,.10)';x.lineWidth=.8;x.stroke();}
    const t=new THREE.CanvasTexture(c);t.colorSpace=THREE.SRGBColorSpace;t.anisotropy=8;return t;
  }

  function render(L,W){
    const root=document.getElementById('palletPreview3D');if(!root)return;
    if(!window.THREE){root.innerHTML='<div class="pallet3dFallback">3D недоступен в этом браузере</div>';return;}
    dispose();
    L=Math.max(300,Number(L)||1200);W=Math.max(300,Number(W)||800);
    const profile=profileFor(L,W);syncProfileInputs(profile,L,W);
    const p=[0,1,2,3,4,5,6].map(part),deck=p[0],crossParts=[p[1],p[2]],runnerParts=[p[3],p[4]],blockParts=[p[5],p[6]];
    const rawCounts={deck:Math.max(0,deck.n||0),cross:crossParts.reduce((a,b)=>a+Math.max(0,b.n||0),0),runner:runnerParts.reduce((a,b)=>a+Math.max(0,b.n||0),0),block:blockParts.reduce((a,b)=>a+Math.max(0,b.n||0),0)};
    const counts={
      deck:Math.min(profile.deckMax,rawCounts.deck),
      cross:Math.max(profile.bindingCount,rawCounts.cross),
      runner:profile.runnerLengths?profile.runnerLengths.length:rawCounts.runner,
      block:rawCounts.block
    };
    const mode=state.mode||'3d';
    const chip=(k,label,c)=>`<button type="button" class="palletPartChip ${state.selected===k?'active':''}" data-p3d-part="${k}">${label}<b>${c}</b></button>`;
    const specStyle='display:flex;justify-content:center;align-items:center;text-align:center;flex-wrap:wrap;gap:6px;margin:8px auto 2px;padding:8px 12px;max-width:760px;border:1px solid rgba(31,111,92,.14);border-radius:12px;background:rgba(238,247,243,.9);color:#31584c;font-size:11px;font-weight:750;line-height:1.35';
    root.innerHTML=`<div class="pallet3dToolbar" role="tablist"><button type="button" data-p3d-mode="3d" class="${mode==='3d'?'active':''}">3D</button><button type="button" data-p3d-mode="top" class="${mode==='top'?'active':''}">Сверху</button><button type="button" data-p3d-mode="side" class="${mode==='side'?'active':''}">Сбоку</button><button type="button" data-p3d-mode="explode" class="${mode==='explode'?'active':''}">${mode==='explode'?'Собрать':'Разнести'}</button></div><div style="${specStyle}">${profile.spec}</div><div class="palletReferenceStage"><div class="palletReferenceTitle"><strong>Длина ${Math.round(L)} × ширина ${Math.round(W)} мм</strong><span>${mode==='explode'?'Разнесённая конструкция':'Реалистичная модель поддона'}</span></div><div class="palletReferenceHost"></div></div><div class="palletModelLegend">${chip('deck','Настил',counts.deck)}${chip('cross','Обвязка',counts.cross)}${chip('runner','Лыжи',counts.runner)}${chip('block','Шашки',counts.block)}</div><div class="palletModelHint">Размеры меняют геометрию модели автоматически · перетаскивайте для вращения · колесо — масштаб</div>`;

    const host=root.querySelector('.palletReferenceHost'),width=Math.max(320,host.clientWidth||760),height=window.innerWidth<620?390:500;
    const renderer=new THREE.WebGLRenderer({antialias:true,alpha:true,powerPreference:'high-performance'});renderer.setPixelRatio(Math.min(window.devicePixelRatio||1,2));renderer.setSize(width,height,false);renderer.shadowMap.enabled=true;renderer.shadowMap.type=THREE.PCFSoftShadowMap;renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.08;host.appendChild(renderer.domElement);
    const scene=new THREE.Scene();scene.background=new THREE.Color(0xf7f6f2);scene.fog=new THREE.Fog(0xf7f6f2,30,58);
    const camera=new THREE.PerspectiveCamera(34,width/height,.1,100),world=new THREE.Group();scene.add(world);
    const groups={runner:new THREE.Group(),block:new THREE.Group(),cross:new THREE.Group(),deck:new THREE.Group()};Object.values(groups).forEach(g=>world.add(g));
    scene.add(new THREE.HemisphereLight(0xfffbf2,0x7c6d5f,2.2));
    const key=new THREE.DirectionalLight(0xfff2d7,4.2);key.position.set(-10,16,11);key.castShadow=true;key.shadow.mapSize.set(2048,2048);key.shadow.camera.near=.5;key.shadow.camera.far=55;key.shadow.camera.left=-16;key.shadow.camera.right=16;key.shadow.camera.top=16;key.shadow.camera.bottom=-16;scene.add(key);
    const fill=new THREE.DirectionalLight(0xdfeaff,1.15);fill.position.set(12,8,-11);scene.add(fill);const rim=new THREE.DirectionalLight(0xffe2b7,.75);rim.position.set(2,5,13);scene.add(rim);
    const floor=new THREE.Mesh(new THREE.PlaneGeometry(34,30),new THREE.MeshStandardMaterial({color:0xf0eee8,roughness:1}));floor.rotation.x=-Math.PI/2;floor.position.y=-.03;floor.receiveShadow=true;scene.add(floor);

    const scale=.01,SL=L*scale,SW=W*scale;
    const longTex=woodTexture(21),crossTex=woodTexture(33,'#ddb176','#87562f'),runnerTex=woodTexture(45,'#cf9b62','#774725'),blockTex=woodTexture(57,'#c58d56','#70411f'),endTex=endTexture(71);
    longTex.repeat.set(3.5,1);crossTex.repeat.set(3.2,1);runnerTex.repeat.set(3.8,1);blockTex.repeat.set(1.5,1);
    const palette={deck:[0xe9bd83,0xe3b579,0xedc58d,0xdfae70],cross:[0xd9a66d,0xd3a066,0xe0b079],runner:[0xc99359,0xc1874e,0xd09b60],block:[0xbf8550,0xc78d55,0xb97b45]},texMap={deck:longTex,cross:crossTex,runner:runnerTex,block:blockTex},selected=state.selected||'all';
    function material(kind,idx,isEnd=false){const active=selected==='all'||selected===kind,color=active?palette[kind][idx%palette[kind].length]:0xb9b3aa,map=(isEnd?endTex:texMap[kind]).clone();map.needsUpdate=true;if(!isEnd){map.offset.x=(idx*.137)%1;map.offset.y=(idx*.071)%1;}return new THREE.MeshStandardMaterial({map,color,roughness:isEnd?.86:.74,metalness:0,transparent:!active,opacity:active?1:.17,depthWrite:active,emissive:selected===kind?0x15392f:0x000000,emissiveIntensity:selected===kind?.11:0});}
    function box(kind,dims,pos,idx,group,longAxis='x'){
      const g=new THREE.BoxGeometry(dims.x,dims.y,dims.z),mats=[];for(let i=0;i<6;i++)mats.push(material(kind,idx,false));const e1=material(kind,idx,true),e2=material(kind,idx+11,true);if(longAxis==='x'){mats[0]=e1;mats[1]=e2;}else if(longAxis==='z'){mats[4]=e1;mats[5]=e2;}
      const mesh=new THREE.Mesh(g,mats);mesh.position.set(pos.x,pos.y,pos.z);mesh.castShadow=true;mesh.receiveShadow=true;group.add(mesh);
      const edge=new THREE.LineSegments(new THREE.EdgesGeometry(g),new THREE.LineBasicMaterial({color:0x735033,transparent:true,opacity:(selected==='all'||selected===kind)?.16:.035}));edge.position.copy(mesh.position);group.add(edge);return mesh;
    }
    const nailGeo=new THREE.CylinderGeometry(.028,.028,.018,14),nailMat=new THREE.MeshStandardMaterial({color:0x4d4b47,roughness:.32,metalness:.48});
    function nail(group,x,y,z){const n=new THREE.Mesh(nailGeo,nailMat);n.position.set(x,y,z);n.castShadow=true;group.add(n);}

    const runnerList=[],crossList=[],blockList=[];
    runnerParts.forEach(r=>{for(let i=0;i<Math.min(9,Math.max(0,r.n||0));i++)runnerList.push({...r});});
    crossParts.forEach(r=>{for(let i=0;i<Math.min(8,Math.max(0,r.n||0));i++)crossList.push({...r});});
    blockParts.forEach(r=>{for(let i=0;i<Math.min(18,Math.max(0,r.n||0));i++)blockList.push({...r});});

    if(profile.runnerLengths){
      runnerList.length=0;
      const templates=[runnerParts[0]||{},runnerParts[1]||runnerParts[0]||{}];
      profile.runnerLengths.forEach((len,i)=>runnerList.push({...templates[i===0||i===profile.runnerLengths.length-1?0:1],l:len,n:1}));
    }
    const runnerCount=Math.max(1,runnerList.length||Math.min(3,counts.runner||3)),crossCount=Math.max(profile.bindingCount,Math.min(6,crossList.length||counts.cross||profile.bindingCount)),blockCount=Math.min(18,blockList.length||counts.block||9);
    const runnerW=Math.max(.62,((runnerList[0]?.w)||95)*scale),runnerH=Math.max(.16,((runnerList[0]?.t)||22)*scale),runnerZ=distribute(runnerCount,SW*.92,runnerW);
    for(let i=0;i<runnerCount;i++){
      const r=runnerList[i]||runnerParts[0]||{},rw=Math.max(.54,(r.w||95)*scale),rh=Math.max(.15,(r.t||22)*scale),rl=clamp((r.l||L)*scale,Math.min(SL*.45,10.5),SL);
      box('runner',{x:rl,y:rh,z:rw},{x:0,y:rh/2,z:runnerZ[i]??0},i,groups.runner,'x');
    }

    const supportZ=runnerCount>=3?[runnerZ[0],runnerZ[Math.floor((runnerCount-1)/2)],runnerZ[runnerCount-1]]:distribute(3,SW*.72,0);
    const blockH=Math.max(.58,((blockList[0]?.t)||78)*scale),blockXDefault=[-SL*.39,0,SL*.39],blockPositions=[];
    if(blockCount>0){
      const cols=Math.min(3,Math.max(1,Math.ceil(Math.sqrt(blockCount)))),rows=Math.ceil(blockCount/cols),xs=cols===3?blockXDefault.slice(0,3):distribute(cols,SL*.78,0),zs=rows===3?supportZ.slice(0,3):distribute(rows,SW*.72,0);
      for(let i=0;i<blockCount;i++){const c=i%cols,r=Math.floor(i/cols);blockPositions.push([xs[c],zs[r]]);}
      blockPositions.forEach(([bx,bz],i)=>{const b=blockList[i]||blockParts[0]||{},bw=Math.max(.62,(b.w||100)*scale),bl=Math.max(.62,(b.l||100)*scale),bh=Math.max(.56,(b.t||78)*scale);box('block',{x:bl,y:bh,z:bw},{x:bx,y:runnerH+bh/2,z:bz},i,groups.block,'x');});
    }

    const crossH=Math.max(.15,((crossList[0]?.t)||22)*scale),crossX=crossCount===3?blockXDefault.slice(0,3):distribute(crossCount,SL*.90,Math.max(.5,((crossList[0]?.w)||95)*scale)),crossY=runnerH+blockH+crossH/2;
    for(let i=0;i<crossCount;i++){
      const r=crossList[i%Math.max(1,crossList.length)]||crossParts[i%2]||{},cw=Math.max(.5,(r.w||95)*scale),ch=Math.max(.15,(r.t||22)*scale),cl=SW;
      box('cross',{x:cw,y:ch,z:cl},{x:crossX[i]??0,y:crossY,z:0},i,groups.cross,'z');
    }

    const deckCount=clamp(rawCounts.deck,0,profile.deckMax),deckW=Math.max(.52,(deck.w||95)*scale),deckH=Math.max(.15,(deck.t||22)*scale),deckLen=clamp((deck.l||L)*scale,SL*.70,SL),deckY=runnerH+blockH+crossH+deckH/2,nailXs=crossX.length?crossX:[-SL*.38,0,SL*.38];
    const deckZ=deckCount?distribute(deckCount,SW*.96,Math.min(deckW,SW*.84/Math.max(1,deckCount))):[];
    for(let i=0;i<deckCount;i++){
      const z=deckZ[i],maxBoard=SW*.90/Math.max(1,deckCount)*.82,bw=Math.min(deckW,maxBoard);
      box('deck',{x:deckLen,y:deckH,z:bw},{x:0,y:deckY,z},i,groups.deck,'x');
      if(selected==='all'||selected==='deck')nailXs.forEach(nx=>{if(Math.abs(nx)<deckLen/2-.08){const dz=Math.min(.075,bw*.25);nail(groups.deck,nx,deckY+deckH/2+.014,z-dz);nail(groups.deck,nx,deckY+deckH/2+.014,z+dz);}});
    }

    const exploded=mode==='explode',offsets={runner:0,block:exploded?1.15:0,cross:exploded?2.35:0,deck:exploded?3.65:0};Object.values(groups).forEach(g=>g.position.y=0);
    let yaw=((Number(state.angle)||-32)*Math.PI/180),pitch=.42,distance=clamp(Math.max(SL,SW)*(exploded?2.05:1.72),16,28);
    function positionCamera(){
      if(mode==='top'){camera.up.set(0,0,-1);camera.position.set(0,Math.max(SL,SW)*1.95,.001);camera.lookAt(0,1.2,0);}
      else if(mode==='side'){camera.up.set(0,1,0);camera.position.set(Math.max(SL,SW)*1.95,Math.max(4.3,deckY*2.2),0);camera.lookAt(0,deckY*.65,0);}
      else{camera.up.set(0,1,0);const cy=Math.sin(pitch)*distance,rad=Math.cos(pitch)*distance;camera.position.set(Math.cos(yaw)*rad,cy+2,Math.sin(yaw)*rad);camera.lookAt(0,exploded?3.25:1.05,0);}
      renderer.render(scene,camera);
    }
    active={renderer,scene,camera,groups,mode,exploded,positionCamera};
    if(exploded){const t0=performance.now();const animate=t=>{const q=clamp((t-t0)/430,0,1),e=1-Math.pow(1-q,3);groups.block.position.y=offsets.block*e;groups.cross.position.y=offsets.cross*e;groups.deck.position.y=offsets.deck*e;positionCamera();if(q<1)raf=requestAnimationFrame(animate);};raf=requestAnimationFrame(animate);}else positionCamera();

    const canvas=renderer.domElement;let dragging=false,lastX=0,lastY=0;
    canvas.addEventListener('pointerdown',e=>{if(mode==='top'||mode==='side')return;dragging=true;lastX=e.clientX;lastY=e.clientY;canvas.setPointerCapture?.(e.pointerId);canvas.classList.add('dragging');});
    canvas.addEventListener('pointermove',e=>{if(!dragging||mode==='top'||mode==='side')return;const dx=e.clientX-lastX,dy=e.clientY-lastY;lastX=e.clientX;lastY=e.clientY;yaw-=dx*.009;pitch=clamp(pitch-dy*.006,.16,.92);state.angle=yaw*180/Math.PI;positionCamera();});
    const stop=()=>{dragging=false;canvas.classList.remove('dragging');};canvas.addEventListener('pointerup',stop);canvas.addEventListener('pointercancel',stop);
    canvas.addEventListener('wheel',e=>{if(mode==='top'||mode==='side')return;e.preventDefault();distance=clamp(distance*(e.deltaY>0?1.08:.92),11,36);positionCamera();},{passive:false});

    root.querySelectorAll('[data-p3d-mode]').forEach(btn=>btn.addEventListener('click',()=>{
      const next=btn.dataset.p3dMode;
      if(next==='explode'&&state.mode==='explode'){
        const t0=performance.now(),from={b:groups.block.position.y,c:groups.cross.position.y,d:groups.deck.position.y};
        const collapse=t=>{const q=clamp((t-t0)/330,0,1),e=Math.pow(1-q,2);groups.block.position.y=from.b*e;groups.cross.position.y=from.c*e;groups.deck.position.y=from.d*e;positionCamera();if(q<1)raf=requestAnimationFrame(collapse);else{state.mode='3d';render(L,W);}};raf=requestAnimationFrame(collapse);return;
      }
      state.mode=next;render(L,W);
    }));
    root.querySelectorAll('[data-p3d-part]').forEach(btn=>btn.addEventListener('click',()=>{const k=btn.dataset.p3dPart;state.selected=state.selected===k?'all':k;render(L,W);}));
  }

  window.renderDynamicPallet=render;
  window.rerenderPallet3D=function(){
    const L=Number(document.getElementById('pL')?.value),W=Number(document.getElementById('pW')?.value);
    if(active&&(state.mode==='3d'||state.mode==='explode')&&document.querySelector('.palletReferenceHost canvas')){active.positionCamera();return;}
    render(L,W);
  };
  setTimeout(()=>render(Number(document.getElementById('pL')?.value),Number(document.getElementById('pW')?.value)),120);
  let rz;window.addEventListener('resize',()=>{clearTimeout(rz);rz=setTimeout(()=>render(Number(document.getElementById('pL')?.value),Number(document.getElementById('pW')?.value)),180);});
})();
