/* pallet3dReferenceV102 */
(function(){
  const state=window.pallet3DState||(window.pallet3DState={mode:'3d',angle:-34,selected:'all'});
  let active=null,raf=0;
  const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
  const near=(a,b,t=2)=>Math.abs(Number(a)-Number(b))<=t;
  /* pallet3dStandardOnlyV102 */
  const STANDARD_3D_PALLETS=[
    {l:1200,w:800,name:'EUR / EPAL 1'},
    {l:1200,w:1000,name:'EUR / EPAL 2'},
    {l:1000,w:1200,name:'EUR / EPAL 3'},
    {l:800,w:600,name:'EUR / EPAL 6'}
  ];
  function standard3DProfile(L,W){return STANDARD_3D_PALLETS.find(x=>near(L,x.l)&&near(W,x.w))||null;}
  const part=i=>typeof window.pallet3DPart==='function'?window.pallet3DPart(i):{n:0,t:0,w:0,l:0,name:'Деталь',index:i};
  const distribute=(count,span,item=0)=>count<=1?[0]:Array.from({length:count},(_,i)=>-span/2+item/2+i*(span-item)/(count-1));

  function profileFor(L,W){
    if(near(L,1250)&&near(W,1180))return{
      key:'reference-1250x1180',reference:true,name:'1250 × 1180',
      spec:'Эталон 1250 × 1180 · модель по живому образцу · натуральное дерево',
      counts:{deck:9,cross:3,runner:3,block:9}
    };
    return{
      key:'dynamic',reference:false,name:'Динамический',
      spec:`Длина ${Math.round(L)} × ширина ${Math.round(W)} · универсальная модель`,
      counts:null
    };
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

  function woodTexture(seed,base='#efd6aa',grain='#9b7049'){
    const c=document.createElement('canvas');c.width=1024;c.height=256;const x=c.getContext('2d');
    x.fillStyle=base;x.fillRect(0,0,c.width,c.height);
    let s=seed||1;const rnd=()=>{s=(s*1664525+1013904223)>>>0;return s/4294967296;};
    for(let i=0;i<76;i++){
      const y=rnd()*c.height,amp=1+rnd()*5.2,period=120+rnd()*290;x.beginPath();
      for(let px=0;px<=c.width;px+=10){const yy=y+Math.sin((px+rnd()*5)/period*Math.PI*2)*amp+(rnd()-.5)*.9;px?x.lineTo(px,yy):x.moveTo(px,yy);}
      x.strokeStyle=grain;x.globalAlpha=.035+rnd()*.105;x.lineWidth=.55+rnd()*.95;x.stroke();
    }
    for(let k=0;k<9;k++){
      const cx=70+rnd()*(c.width-140),cy=22+rnd()*(c.height-44),rx=5+rnd()*16,ry=2+rnd()*7;x.globalAlpha=.11+rnd()*.08;x.strokeStyle='#7b5132';x.lineWidth=.85+rnd()*.55;
      x.beginPath();x.ellipse(cx,cy,rx,ry,(rnd()-.5)*.18,0,Math.PI*2);x.stroke();
      x.beginPath();x.ellipse(cx,cy,rx*.48,ry*.48,(rnd()-.5)*.18,0,Math.PI*2);x.stroke();
    }
    x.globalAlpha=1;
    const t=new THREE.CanvasTexture(c);t.wrapS=t.wrapT=THREE.RepeatWrapping;t.colorSpace=THREE.SRGBColorSpace;t.anisotropy=8;return t;
  }

  function endTexture(seed){
    const c=document.createElement('canvas');c.width=256;c.height=256;const x=c.getContext('2d');x.fillStyle='#d9b17d';x.fillRect(0,0,256,256);
    let s=seed||9;const rnd=()=>{s=(s*1103515245+12345)&0x7fffffff;return s/0x7fffffff;};const cx=116+rnd()*24,cy=116+rnd()*24;
    for(let i=1;i<14;i++){x.beginPath();x.ellipse(cx,cy,7+i*7.5,5+i*6.5,(rnd()-.5)*.16,0,Math.PI*2);x.strokeStyle=i%3===0?'rgba(90,57,30,.27)':'rgba(110,72,40,.16)';x.lineWidth=1.15;x.stroke();}
    for(let i=0;i<10;i++){const a=rnd()*Math.PI*2,l=35+rnd()*72;x.beginPath();x.moveTo(cx,cy);x.lineTo(cx+Math.cos(a)*l,cy+Math.sin(a)*l);x.strokeStyle='rgba(90,55,30,.10)';x.lineWidth=.75;x.stroke();}
    const t=new THREE.CanvasTexture(c);t.colorSpace=THREE.SRGBColorSpace;t.anisotropy=8;return t;
  }

  function render(L,W){
    const root=document.getElementById('palletPreview3D');if(!root)return;
    if(!window.THREE){root.innerHTML='<div class="pallet3dFallback">3D недоступен в этом браузере</div>';return;}
    dispose();
    L=Math.max(300,Number(L)||1200);W=Math.max(300,Number(W)||800);
    const standard=standard3DProfile(L,W);
    if(!standard){
      state.mode='3d';state.selected='all';
      const supported=STANDARD_3D_PALLETS.map(x=>`${x.l} × ${x.w}`).join(' · ');
      root.innerHTML=`<div style="min-height:390px;display:flex;align-items:center;justify-content:center;padding:28px"><div style="width:min(100%,680px);text-align:center;padding:34px 24px;border:1px solid #dce7e1;border-radius:22px;background:linear-gradient(145deg,#fff,#f3f7f5);box-shadow:0 14px 34px rgba(19,65,53,.07)"><div style="width:56px;height:56px;margin:0 auto 14px;border-radius:17px;display:grid;place-items:center;background:#e7f1ed;color:#1f6f5c;font-size:27px">▦</div><strong style="display:block;font-size:22px;color:#173c33">3D для ${Math.round(L)} × ${Math.round(W)} мм не предусмотрен</strong><p style="margin:10px auto 16px;max-width:520px;color:#65756d;line-height:1.5">Это нестандартный размер. Расчёт материалов, раскрой, сохранение заказа и производство продолжают работать без 3D-модели.</p><div style="display:inline-flex;max-width:100%;flex-wrap:wrap;justify-content:center;gap:6px;padding:9px 12px;border-radius:12px;background:#edf5f1;color:#31584c;font-size:12px;font-weight:800">3D доступен: ${supported}</div></div></div>`;
      return;
    }
    const profile=profileFor(L,W),reference=false,mode=state.mode||'3d';
    profile.spec=`${standard.name} · стандартный поддон ${standard.l} × ${standard.w} мм`;
    const p=[0,1,2,3,4,5,6].map(part),deck=p[0],crossParts=[p[1],p[2]],runnerParts=[p[3],p[4]],blockParts=[p[5],p[6]];
    const rawCounts={
      deck:Math.max(0,Math.round(deck.n||0)),
      cross:crossParts.reduce((a,b)=>a+Math.max(0,Math.round(b.n||0)),0),
      runner:runnerParts.reduce((a,b)=>a+Math.max(0,Math.round(b.n||0)),0),
      block:blockParts.reduce((a,b)=>a+Math.max(0,Math.round(b.n||0)),0)
    };
    const counts=reference?profile.counts:{
      deck:Math.min(18,rawCounts.deck),cross:Math.min(8,rawCounts.cross||3),runner:Math.min(8,rawCounts.runner||3),block:Math.min(18,rawCounts.block||9)
    };
    const chip=(k,label,c)=>`<button type="button" class="palletPartChip ${state.selected===k?'active':''}" data-p3d-part="${k}">${label}<b>${c}</b></button>`;
    const specStyle='display:flex;justify-content:center;align-items:center;text-align:center;flex-wrap:wrap;gap:6px;margin:8px auto 2px;padding:8px 12px;max-width:760px;border:1px solid rgba(31,111,92,.14);border-radius:12px;background:rgba(247,250,248,.95);color:#31584c;font-size:11px;font-weight:800;line-height:1.35';
    const referenceBadge=reference?'<span style="display:inline-flex;align-items:center;padding:3px 7px;border-radius:999px;background:#173f35;color:#fff;font-size:10px;font-weight:850;letter-spacing:.03em">ФОТО-ЭТАЛОН</span>':'';
    root.innerHTML=`<div class="pallet3dToolbar" role="tablist"><button type="button" data-p3d-mode="3d" class="${mode==='3d'?'active':''}">3D</button><button type="button" data-p3d-mode="top" class="${mode==='top'?'active':''}">Сверху</button><button type="button" data-p3d-mode="side" class="${mode==='side'?'active':''}">Сбоку</button><button type="button" data-p3d-mode="explode" class="${mode==='explode'?'active':''}">${mode==='explode'?'Собрать':'Разнести'}</button></div><div style="${specStyle}">${referenceBadge}<span>${profile.spec}</span></div><div class="palletReferenceStage"><div class="palletReferenceTitle"><strong>${Math.round(L)} × ${Math.round(W)} мм</strong><span>${standard.name} · ${mode==='explode'?'разнесённый вид':'реальный 3D'}</span></div><div class="palletReferenceHost"></div></div><div class="palletModelLegend">${chip('deck','Настил',counts.deck)}${chip('cross','Поперечины',counts.cross)}${chip('runner','Лыжи',counts.runner)}${chip('block','Шашки',counts.block)}</div><div class="palletModelHint">Перетаскивайте модель для вращения · колесо — масштаб · кнопки сверху — технические виды</div>`;

    const host=root.querySelector('.palletReferenceHost'),width=Math.max(320,host.clientWidth||760),height=window.innerWidth<620?390:500;
    const renderer=new THREE.WebGLRenderer({antialias:true,alpha:true,powerPreference:'high-performance'});
    renderer.setPixelRatio(Math.min(window.devicePixelRatio||1,2));renderer.setSize(width,height,false);renderer.shadowMap.enabled=true;renderer.shadowMap.type=THREE.PCFSoftShadowMap;renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.03;host.appendChild(renderer.domElement);
    const scene=new THREE.Scene();scene.background=new THREE.Color(0xf8f8f6);scene.fog=new THREE.Fog(0xf8f8f6,28,62);
    const camera=new THREE.PerspectiveCamera(34,width/height,.1,100),world=new THREE.Group();scene.add(world);
    const groups={runner:new THREE.Group(),block:new THREE.Group(),cross:new THREE.Group(),deck:new THREE.Group()};Object.values(groups).forEach(g=>world.add(g));
    scene.add(new THREE.HemisphereLight(0xffffff,0x756b61,2.4));
    const key=new THREE.DirectionalLight(0xfff4df,4.0);key.position.set(-11,17,12);key.castShadow=true;key.shadow.mapSize.set(2048,2048);key.shadow.camera.near=.5;key.shadow.camera.far=55;key.shadow.camera.left=-17;key.shadow.camera.right=17;key.shadow.camera.top=17;key.shadow.camera.bottom=-17;scene.add(key);
    const fill=new THREE.DirectionalLight(0xe7efff,1.0);fill.position.set(13,9,-10);scene.add(fill);
    const floor=new THREE.Mesh(new THREE.PlaneGeometry(36,32),new THREE.MeshStandardMaterial({color:0xf1f0ec,roughness:1}));floor.rotation.x=-Math.PI/2;floor.position.y=-.025;floor.receiveShadow=true;scene.add(floor);

    const scale=.01,SL=L*scale,SW=W*scale;
    const deckTex=woodTexture(21,'#f0d9b2','#9c714b'),crossTex=woodTexture(33,'#ead0a5','#946942'),runnerTex=woodTexture(45,'#e6c99a','#8c603a'),blockTex=woodTexture(57,'#ddb985','#845833'),endTex=endTexture(71);
    deckTex.repeat.set(3.7,1);crossTex.repeat.set(3.1,1);runnerTex.repeat.set(3.8,1);blockTex.repeat.set(1.2,1);
    const palette={deck:[0xf0d3a6,0xebc99a,0xf3d9b0,0xe8c28f],cross:[0xe6c18f,0xe2bb87,0xeac99b],runner:[0xddb681,0xd9ae77,0xe2bc87],block:[0xd3a66f,0xdab27d,0xca9862]},texMap={deck:deckTex,cross:crossTex,runner:runnerTex,block:blockTex},selected=state.selected||'all';
    function material(kind,idx,isEnd=false){
      const active=selected==='all'||selected===kind,color=active?palette[kind][idx%palette[kind].length]:0xc7c3bc,map=(isEnd?endTex:texMap[kind]).clone();map.needsUpdate=true;
      if(!isEnd){map.offset.x=(idx*.137)%1;map.offset.y=(idx*.071)%1;}
      return new THREE.MeshStandardMaterial({map,color,roughness:isEnd?.88:.78,metalness:0,transparent:!active,opacity:active?1:.16,depthWrite:active,emissive:selected===kind?0x173d33:0x000000,emissiveIntensity:selected===kind?.08:0});
    }
    function box(kind,dims,pos,idx,group,longAxis='x'){
      const g=new THREE.BoxGeometry(dims.x,dims.y,dims.z),mats=[];for(let i=0;i<6;i++)mats.push(material(kind,idx,false));
      const e1=material(kind,idx,true),e2=material(kind,idx+11,true);if(longAxis==='x'){mats[0]=e1;mats[1]=e2;}else if(longAxis==='z'){mats[4]=e1;mats[5]=e2;}
      const mesh=new THREE.Mesh(g,mats);mesh.position.set(pos.x,pos.y,pos.z);mesh.castShadow=true;mesh.receiveShadow=true;group.add(mesh);
      const edge=new THREE.LineSegments(new THREE.EdgesGeometry(g),new THREE.LineBasicMaterial({color:0x7b5a3d,transparent:true,opacity:(selected==='all'||selected===kind)?.11:.025}));edge.position.copy(mesh.position);group.add(edge);return mesh;
    }
    const nailHeadGeo=new THREE.CylinderGeometry(.042,.042,.028,16),nailShankGeo=new THREE.CylinderGeometry(.016,.019,1.34,10),nailMat=new THREE.MeshStandardMaterial({color:0x555450,roughness:.34,metalness:.42});
    function nail(group,x,y,z){
      const head=new THREE.Mesh(nailHeadGeo,nailMat);head.position.set(x,y,z);head.castShadow=true;group.add(head);
      if(mode==='explode'){
        const shank=new THREE.Mesh(nailShankGeo,nailMat);shank.position.set(x,y-.67,z);shank.castShadow=true;group.add(shank);
      }
    }

    let runnerH=.22,blockH=.78,crossH=.22,deckH=.22,deckY=0,crossX=[];

    if(reference){
      const runnerW=.98,runnerZ=[-SW/2+.49,0,SW/2-.49];
      runnerZ.forEach((z,i)=>box('runner',{x:SL,y:runnerH,z:runnerW},{x:0,y:runnerH/2,z},i,groups.runner,'x'));

      const rowX=[-SL/2+.49,0,SL/2-.49];
      const outerZ=[-SW/2+.75,SW/2-.75];
      const centreZ=0;
      rowX.forEach((x,ri)=>{
        box('block',{x:.98,y:blockH,z:1.50},{x,y:runnerH+blockH/2,z:outerZ[0]},ri*3,groups.block,'z');
        box('block',{x:1.00,y:blockH,z:.98},{x,y:runnerH+blockH/2,z:centreZ},ri*3+1,groups.block,'z');
        box('block',{x:.98,y:blockH,z:1.50},{x,y:runnerH+blockH/2,z:outerZ[1]},ri*3+2,groups.block,'z');
      });

      crossX=rowX;
      const crossY=runnerH+blockH+crossH/2;
      crossX.forEach((x,i)=>box('cross',{x:.98,y:crossH,z:SW},{x,y:crossY,z:0},i,groups.cross,'z'));

      deckY=runnerH+blockH+crossH+deckH/2;
      const deckW=.98,deckZ=distribute(9,SW,deckW);
      deckZ.forEach((z,i)=>{
        box('deck',{x:SL,y:deckH,z:deckW},{x:0,y:deckY,z},i,groups.deck,'x');
        if(selected==='all'||selected==='deck')crossX.forEach(x=>{
          const dz=Math.min(.15,deckW*.22),ny=deckY+deckH/2+.013;
          nail(groups.deck,x,ny,z-dz);nail(groups.deck,x,ny,z+dz);
        });
      });
    }else{
      const runnerList=[],crossList=[],blockList=[];
      runnerParts.forEach(r=>{for(let i=0;i<Math.min(8,Math.max(0,Math.round(r.n||0)));i++)runnerList.push({...r});});
      crossParts.forEach(r=>{for(let i=0;i<Math.min(8,Math.max(0,Math.round(r.n||0)));i++)crossList.push({...r});});
      blockParts.forEach(r=>{for(let i=0;i<Math.min(18,Math.max(0,Math.round(r.n||0)));i++)blockList.push({...r});});
      const runnerCount=Math.max(1,runnerList.length||3),runnerW=Math.max(.55,((runnerList[0]?.w)||98)*scale);runnerH=Math.max(.15,((runnerList[0]?.t)||22)*scale);
      const runnerZ=distribute(runnerCount,SW*.94,Math.min(runnerW,SW*.8/runnerCount));
      for(let i=0;i<runnerCount;i++){const r=runnerList[i]||runnerParts[0]||{},rw=Math.max(.5,(r.w||98)*scale),rl=clamp((r.l||L)*scale,SL*.35,SL);box('runner',{x:rl,y:runnerH,z:rw},{x:0,y:runnerH/2,z:runnerZ[i]??0},i,groups.runner,'x');}

      const blockCount=Math.max(0,Math.min(18,blockList.length||counts.block)),cols=Math.min(3,Math.max(1,Math.ceil(Math.sqrt(blockCount||9)))),rows=Math.max(1,Math.ceil((blockCount||9)/cols));blockH=Math.max(.55,((blockList[0]?.t)||75)*scale);
      const bx=distribute(cols,SL*.78,0),bz=distribute(rows,SW*.72,0);
      for(let i=0;i<blockCount;i++){const b=blockList[i]||blockParts[0]||{},c=i%cols,r=Math.floor(i/cols),dx=Math.max(.58,(b.l||110)*scale),dz=Math.max(.58,(b.w||100)*scale);box('block',{x:dx,y:blockH,z:dz},{x:bx[c],y:runnerH+blockH/2,z:bz[r]},i,groups.block,'x');}

      const crossCount=Math.max(1,counts.cross||3),crossW=Math.max(.5,((crossList[0]?.w)||98)*scale);crossH=Math.max(.15,((crossList[0]?.t)||22)*scale);crossX=distribute(crossCount,SL*.94,Math.min(crossW,SL*.8/crossCount));
      const crossY=runnerH+blockH+crossH/2;
      crossX.forEach((x,i)=>box('cross',{x:crossW,y:crossH,z:SW},{x,y:crossY,z:0},i,groups.cross,'z'));

      const deckCount=Math.max(0,Math.min(18,counts.deck)),dw=Math.max(.5,(deck.w||98)*scale);deckH=Math.max(.15,(deck.t||22)*scale);deckY=runnerH+blockH+crossH+deckH/2;
      const deckLen=clamp((deck.l||L)*scale,SL*.55,SL),deckZ=deckCount?distribute(deckCount,SW*.96,Math.min(dw,SW*.82/Math.max(1,deckCount))):[];
      deckZ.forEach((z,i)=>{const bw=Math.min(dw,SW*.9/Math.max(1,deckCount)*.84);box('deck',{x:deckLen,y:deckH,z:bw},{x:0,y:deckY,z},i,groups.deck,'x');if(selected==='all'||selected==='deck')crossX.forEach(x=>{if(Math.abs(x)<deckLen/2-.05){const dz=Math.min(.075,bw*.22),ny=deckY+deckH/2+.013;nail(groups.deck,x,ny,z-dz);nail(groups.deck,x,ny,z+dz);}});});
    }

    const exploded=mode==='explode',offsets={runner:0,block:exploded?1.05:0,cross:exploded?2.15:0,deck:exploded?3.35:0};Object.values(groups).forEach(g=>g.position.y=0);
    let yaw=((Number(state.angle)||-34)*Math.PI/180),pitch=.43,distance=clamp(Math.max(SL,SW)*(exploded?2.08:1.72),16,29);
    function positionCamera(){
      if(mode==='top'){camera.up.set(0,0,-1);camera.position.set(0,Math.max(SL,SW)*1.92,.001);camera.lookAt(0,deckY*.45,0);}
      else if(mode==='side'){camera.up.set(0,1,0);camera.position.set(0,Math.max(3.5,deckY*2.2),Math.max(SL,SW)*1.95);camera.lookAt(0,deckY*.55,0);}
      else{camera.up.set(0,1,0);const cy=Math.sin(pitch)*distance,rad=Math.cos(pitch)*distance;camera.position.set(Math.cos(yaw)*rad,cy+1.7,Math.sin(yaw)*rad);camera.lookAt(0,exploded?3.05:1.0,0);}
      renderer.render(scene,camera);
    }
    active={renderer,scene,camera,groups,mode,exploded,positionCamera,L,W};
    if(exploded){const t0=performance.now();const animate=t=>{const q=clamp((t-t0)/430,0,1),e=1-Math.pow(1-q,3);groups.block.position.y=offsets.block*e;groups.cross.position.y=offsets.cross*e;groups.deck.position.y=offsets.deck*e;positionCamera();if(q<1)raf=requestAnimationFrame(animate);};raf=requestAnimationFrame(animate);}else positionCamera();

    const canvas=renderer.domElement;let dragging=false,lastX=0,lastY=0;
    canvas.addEventListener('pointerdown',e=>{e.stopPropagation();if(mode==='top'||mode==='side')return;dragging=true;lastX=e.clientX;lastY=e.clientY;canvas.setPointerCapture?.(e.pointerId);canvas.classList.add('dragging');});
    canvas.addEventListener('pointermove',e=>{e.stopPropagation();if(!dragging||mode==='top'||mode==='side')return;const dx=e.clientX-lastX,dy=e.clientY-lastY;lastX=e.clientX;lastY=e.clientY;yaw-=dx*.009;pitch=clamp(pitch-dy*.006,.14,.94);state.angle=yaw*180/Math.PI;positionCamera();});
    const stop=e=>{e?.stopPropagation?.();dragging=false;canvas.classList.remove('dragging');};canvas.addEventListener('pointerup',stop);canvas.addEventListener('pointercancel',stop);
    canvas.addEventListener('wheel',e=>{if(mode==='top'||mode==='side')return;e.preventDefault();e.stopPropagation();distance=clamp(distance*(e.deltaY>0?1.08:.92),10,36);positionCamera();},{passive:false});

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
    if(active&&near(active.L,L,.01)&&near(active.W,W,.01)&&(state.mode==='3d'||state.mode==='explode')&&document.querySelector('.palletReferenceHost canvas')){active.positionCamera();return;}
    render(L,W);
  };
  setTimeout(()=>render(Number(document.getElementById('pL')?.value),Number(document.getElementById('pW')?.value)),120);
  let rz;window.addEventListener('resize',()=>{clearTimeout(rz);rz=setTimeout(()=>render(Number(document.getElementById('pL')?.value),Number(document.getElementById('pW')?.value)),180);});
})();