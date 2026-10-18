/* pallet3dStandardOnlyV126 — clean visible standard 3D */
(function(){
  const state=window.pallet3DState||(window.pallet3DState={mode:'3d',angle:-34,selected:'all'});
  if(typeof state.showDimensions!=='boolean')state.showDimensions=true;
  let active=null,raf=0,syncQueued=false,resizeTimer=0;
  const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
  const near=(a,b,t=2)=>Math.abs(Number(a)-Number(b))<=t;
  const num=(v,d=0)=>Number.isFinite(Number(v))?Number(v):d;
  const el=id=>document.getElementById(id);
  const part=i=>typeof window.pallet3DPart==='function'?window.pallet3DPart(i):{n:0,t:22,w:98,l:0,name:'Деталь',index:i};
  const spread=(count,span,item=0)=>count<=1?[0]:Array.from({length:count},(_,i)=>-span/2+item/2+i*(span-item)/(count-1));

  function resolveProfile(inputL,inputW){
    const a=Math.max(300,num(inputL,1200)),b=Math.max(300,num(inputW,800));
    const match=(x,y)=>(near(a,x)&&near(b,y))||(near(a,y)&&near(b,x));
    const width=b,length=a;
    if(match(1200,800))return {key:'epal1',width,length,deckMax:8,bindingCount:3,runnerLengths:[length,length,length],spec:`EUR / EPAL 1 · ${Math.round(length)} × ${Math.round(width)} мм`};
    if(match(1200,1000))return {key:'epal2',width,length,deckMax:9,bindingCount:3,runnerLengths:[length,length,length],spec:`EUR / EPAL 2 · ${Math.round(length)} × ${Math.round(width)} мм`};
    if(match(1000,1200))return {key:'epal3',width,length,deckMax:9,bindingCount:3,runnerLengths:[length,length,length],spec:`EUR / EPAL 3 · ${Math.round(length)} × ${Math.round(width)} мм`};
    if(match(800,600))return {key:'epal6',width,length,deckMax:7,bindingCount:3,runnerLengths:[length,length,length],spec:`EUR / EPAL 6 · ${Math.round(length)} × ${Math.round(width)} мм`};
    return {key:'unsupported',width,length,deckMax:0,bindingCount:0,runnerLengths:[],spec:'Нестандартный размер'};
  }

  function setInput(id,value){const x=el(id);if(!x)return false;const v=String(value);if(x.value===v)return false;x.value=v;return true;}
  function syncProfileInputs(profile){
    const deck=el('n0');
    if(deck)deck.max=String(profile.deckMax);
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
    const profile=resolveProfile(inputL,inputW);
    const previewCard=root.closest('.previewCard');
    const previewStage=el('previewStage');
    const previewActions=previewCard?.querySelector('.previewActions');
    if(profile.key==='unsupported'){
      state.mode='3d';state.selected='all';root.innerHTML='';
      if(previewCard)previewCard.style.display='';if(previewStage)previewStage.style.display='none';if(previewActions)previewActions.style.display='none';return;
    }
    if(previewCard)previewCard.style.display='';if(previewStage)previewStage.style.display='flex';if(previewActions)previewActions.style.display='flex';root.style.display='block';root.style.width='100%';root.style.padding='0';root.style.minHeight='0';
    syncProfileInputs(profile);
    const P=[0,1,2,3,4,5,6].map(part),deck=P[0],bindParts=[P[1],P[2]],runnerParts=[P[3],P[4]],block1=P[5],block2=P[6];
    const isReference=false;
    const rawDeck=Math.max(0,Math.round(num(deck.n))),deckCount=isReference?9:Math.min(profile.deckMax,rawDeck);
    const rawBlocks=Math.max(0,Math.round(num(block1.n)))+Math.max(0,Math.round(num(block2.n))),blockCount=isReference?9:Math.min(9,rawBlocks||9);
    const runnerCount=isReference?3:(profile.runnerLengths?profile.runnerLengths.length:Math.max(1,Math.min(7,Math.round(num(runnerParts[0].n)+num(runnerParts[1].n))||3)));
    const mode=state.mode||'3d';
    const showDimensions=mode!=='3d'&&state.showDimensions!==false;
    root.classList.toggle('palletDimsHidden',!showDimensions);
    const deckThicknessMm=Math.max(0,num(deck.t,22)),deckWidthMm=Math.max(0,num(deck.w,98)),deckLengthMm=Math.max(0,num(deck.l,profile.length));
    const remainingMm=profile.width-deckCount*deckWidthMm,rawGapMm=deckCount>1?remainingMm/(deckCount-1):0,gapBad=deckCount>1&&rawGapMm<0;
    const fmtMm=v=>{const x=Math.round(num(v,0)*10)/10;return Number.isInteger(x)?String(x):x.toFixed(1).replace('.',',');};
    const gapText=deckCount>1?(gapBad?`−${fmtMm(Math.abs(rawGapMm))} мм`:`${fmtMm(rawGapMm)} мм`):'—';
    const dimensionOverlay='<div class="palletOnModelMeasures" aria-label="Полная размерная схема поддона"></div>';
    const fastenerLegend=mode==='explode'?'<div style="display:flex;justify-content:center;gap:12px;flex-wrap:wrap;margin:7px auto 0;font-size:11px;font-weight:800;color:#46514d"><span>● 2,8×80 мм — поперечины над шашками и лыжи</span><span>● 2,5×40 мм — настил к поперечинам</span></div>':'';
    root.innerHTML=`<div class="pallet3dToolbar" role="tablist"><button type="button" data-p3d-mode="3d" class="${mode==='3d'?'active':''}">3D</button><button type="button" data-p3d-mode="top" class="${mode==='top'?'active':''}">Сверху</button><button type="button" data-p3d-mode="side" class="${mode==='side'?'active':''}">Сбоку</button><button type="button" data-p3d-mode="explode" class="${mode==='explode'?'active':''}">${mode==='explode'?'Собрать':'Разнести'}</button><button type="button" data-p3d-dims aria-pressed="${showDimensions?'true':'false'}" class="${showDimensions?'active':''}" ${mode==='3d'?'hidden':''}>Размеры</button></div>${fastenerLegend}<div class="palletReferenceStage" style="width:100%;position:relative;overflow:hidden;background:radial-gradient(circle at 50% 30%,#fff 0,#faf8f3 52%,#efede7 100%);border-radius:14px;margin-top:8px"><div class="palletReferenceHost" style="width:100%;min-height:390px;position:relative"></div>${dimensionOverlay}<div class="palletPickHint" ${mode==='3d'?'hidden':''}>Выберите деталь: настил, поперечину, лыжу или шашку</div><div class="palletPartInspector" hidden><strong></strong><span></span><b></b></div></div>`;
    const host=root.querySelector('.palletReferenceHost'),cw=Math.max(280,host.clientWidth||760),ch=window.innerWidth<620?390:510;
    const stage=root.querySelector('.palletReferenceStage');
    const renderer=new THREE.WebGLRenderer({antialias:true,alpha:true,powerPreference:'high-performance'});renderer.setPixelRatio(Math.min(window.devicePixelRatio||1,2));renderer.setSize(cw,ch,false);renderer.setClearColor(0,0);renderer.shadowMap.enabled=true;renderer.shadowMap.type=THREE.PCFSoftShadowMap;renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.08;host.appendChild(renderer.domElement);
    const scene=new THREE.Scene(),camera=new THREE.PerspectiveCamera(33,cw/ch,.1,120),world=new THREE.Group();scene.add(world);
    const groups={runner:new THREE.Group(),block:new THREE.Group(),cross:new THREE.Group(),deck:new THREE.Group()};Object.values(groups).forEach(g=>world.add(g));
    scene.add(new THREE.HemisphereLight(0xfffcf4,0x766b61,2.45));
    const key=new THREE.DirectionalLight(0xfff0d2,4.5);key.position.set(-12,18,12);key.castShadow=true;key.shadow.mapSize.set(2048,2048);key.shadow.camera.near=.5;key.shadow.camera.far=65;key.shadow.camera.left=-18;key.shadow.camera.right=18;key.shadow.camera.top=18;key.shadow.camera.bottom=-18;scene.add(key);
    const fill=new THREE.DirectionalLight(0xe4efff,1.15);fill.position.set(12,8,-10);scene.add(fill);
    const floor=new THREE.Mesh(new THREE.PlaneGeometry(40,36),new THREE.ShadowMaterial({color:0x64584e,opacity:.13}));floor.rotation.x=-Math.PI/2;floor.position.y=-.025;floor.receiveShadow=true;scene.add(floor);
    const S=.01,PW=profile.width*S,PL=profile.length*S,selected=state.selected||'all';
    const textures={deck:woodTexture(17,'#f3dfbd','#9a724b'),cross:woodTexture(31,'#ecd2a8','#906642'),runner:woodTexture(47,'#e8ca9a','#875d39'),block:woodTexture(61,'#dfbb86','#805433')};Object.values(textures).forEach((t,i)=>t.repeat.set(i===3?1.4:3.2,1));
    const colors={deck:[0xf3dab2,0xefd1a4,0xf6e0bf],cross:[0xeccda0,0xe6c18f,0xf0d5ad],runner:[0xe4c08d,0xddb47f,0xe9ca9a],block:[0xd8aa72,0xdfb783,0xd2a069]};
    const inspectable=[];
    const inspectShort={deck:'Н',cross:'П',runner:'Л',block:'Ш'};
    function mat(kind,i){const on=selected==='all'||selected===kind,map=textures[kind].clone();map.needsUpdate=true;map.offset.x=(i*.149)%1;return new THREE.MeshStandardMaterial({map,color:on?colors[kind][i%colors[kind].length]:0xbdb8b0,roughness:.78,metalness:0,transparent:!on,opacity:on?1:.15,depthWrite:on,emissive:selected===kind?0x14382e:0,emissiveIntensity:selected===kind?.09:0});}
    function piece(kind,dx,dy,dz,x,y,z,i,group){const g=roundedBoxGeometry(dx,dy,dz,kind==='block'?.055:.035),m=new THREE.Mesh(g,mat(kind,i));m.position.set(x,y,z);m.castShadow=true;m.receiveShadow=true;group.add(m);return m;}
    function registerInspectable(mesh,kind,index,name,t,w,l,n){if(!mesh)return mesh;mesh.userData.palletInspect={name,kind,index,short:inspectShort[kind]||'',t:num(t),w:num(w),l:num(l),n:Math.max(1,Math.round(num(n,1)))};mesh.userData.baseEmissiveHex=selected===kind?0x14382e:0;mesh.userData.baseEmissiveIntensity=selected===kind?.09:0;inspectable.push(mesh);return mesh;}
    const nail40Length=.40,nail80Length=.80;
    const nail40HeadGeo=new THREE.CylinderGeometry(.044,.044,.026,16),nail80HeadGeo=new THREE.CylinderGeometry(.052,.052,.030,18);
    const nail40ShankGeo=new THREE.CylinderGeometry(.018,.020,nail40Length,12),nail80ShankGeo=new THREE.CylinderGeometry(.022,.025,nail80Length,12);
    const nail40Mat=new THREE.MeshStandardMaterial({color:0x596166,roughness:.34,metalness:.58}),nail80Mat=new THREE.MeshStandardMaterial({color:0x3f4549,roughness:.30,metalness:.66});
    function addNail(group,headGeo,shankGeo,mat,x,y,z,direction=-1){const head=new THREE.Mesh(headGeo,mat);head.position.set(x,y,z);head.castShadow=true;group.add(head);if(mode==='explode'){const shank=new THREE.Mesh(shankGeo,mat),len=shankGeo.parameters.height||.4;shank.position.set(x,y+direction*len/2,z);shank.castShadow=true;group.add(shank);}}
    const nail40=(group,x,y,z,direction=-1)=>addNail(group,nail40HeadGeo,nail40ShankGeo,nail40Mat,x,y,z,direction),nail80=(group,x,y,z,direction=-1)=>addNail(group,nail80HeadGeo,nail80ShankGeo,nail80Mat,x,y,z,direction);
    const pairNails=(fn,group,x,y,z,dx,direction=-1)=>{fn(group,x-dx,y,z,direction);fn(group,x+dx,y,z,direction);};
    const cornerTriple=(x,y,z,dx)=>{const inward=z<0?1:-1;nail80(groups.deck,x-dx,y,z-.03*inward,-1);nail80(groups.deck,x+dx,y,z-.03*inward,-1);nail80(groups.deck,x,y,z+.05*inward,-1);};
    const runnerT=isReference?.22:Math.max(.15,num(runnerParts[0].t,22)*S),runnerW=isReference?.98:Math.max(.58,num(runnerParts[0].w,98)*S);
    const blockH=.75,blockXSize1=.95,blockZSize1=.95,blockXSize2=.95,blockZSize2=.95;
    const bindT=isReference?.22:Math.max(.15,num(bindParts[0].t,22)*S),bindDepth=isReference?.98:Math.max(.58,num(bindParts[0].w,98)*S);
    const deckT=isReference?.22:Math.max(.01,deckThicknessMm*S),deckW=isReference?.98:Math.max(.01,deckWidthMm*S),deckL=Math.max(.01,deckLengthMm*S);
    const runnerLengths=profile.runnerLengths||Array.from({length:runnerCount},(_,i)=>Math.min(profile.length,num((i<Math.max(0,num(runnerParts[0].n)))?runnerParts[0].l:runnerParts[1].l,profile.length)));
    const runnerActualW=Math.min(runnerW,PW/Math.max(3,runnerLengths.length)*.56),edgeRunnerX=Math.max(0,PW/2-runnerActualW/2-.03);
    let runnerXs;if(runnerLengths.length===5)runnerXs=[-edgeRunnerX,-edgeRunnerX*.5,0,edgeRunnerX*.5,edgeRunnerX];else if(runnerLengths.length===3)runnerXs=[-edgeRunnerX,0,edgeRunnerX];else runnerXs=spread(runnerLengths.length,PW,runnerActualW);
    runnerLengths.forEach((mm,i)=>{const rz=clamp(mm*S,Math.min(PL*.55,10.5),PL),mesh=piece('runner',runnerActualW,runnerT,rz,runnerXs[i],runnerT/2,0,i,groups.runner);registerInspectable(mesh,'runner',i,'Лыжа',runnerT/S,runnerActualW/S,rz/S,runnerLengths.length);});
    const blockY=runnerT+blockH/2,blockRows=[],blockPoints=[];
    for(let zi=0;zi<3;zi++)for(let xi=0;xi<3;xi++){const idx=zi*3+xi;if(idx>=blockCount)continue;const centerType=(xi===1),bx=centerType?blockXSize2:blockXSize1,bz=centerType?blockZSize2:blockZSize1;const sx=xi===0?-1:xi===2?1:0,sz=zi===0?-1:zi===2?1:0;const bxPos=sx===0?0:sx*Math.max(0,PW/2-bx/2-.03),bzPos=sz===0?0:sz*Math.max(0,PL/2-bz/2-.03);blockRows[zi]=bzPos;blockPoints.push({x:bxPos,z:bzPos,bx,bz});const mesh=piece('block',bx,blockH,bz,bxPos,blockY,bzPos,idx,groups.block);registerInspectable(mesh,'block',idx,'Шашка',blockH/S,bx/S,bz/S,blockCount);}
    if(selected==='all'||selected==='runner'){runnerXs.forEach((x,xi)=>blockRows.forEach((z,zi)=>{if(z==null||zi*3+Math.min(xi,2)>=blockCount)return;pairNails(nail80,groups.runner,x,runnerT+.014,z,Math.min(.072,runnerActualW*.22),1);}));}
    const bindY=runnerT+blockH+bindT/2,bindZ=[-PL/2+bindDepth/2+.02,0,PL/2-bindDepth/2-.02];bindZ.forEach((z,i)=>{const mesh=piece('cross',PW,bindT,bindDepth,0,bindY,z,i,groups.cross);registerInspectable(mesh,'cross',i,'Поперечина',bindT/S,bindDepth/S,PW/S,bindZ.length);});
    const topY=runnerT+blockH+bindT+deckT/2,actualDeckW=deckCount?Math.min(deckW,PW):deckW,topXs=deckCount?spread(deckCount,PW,actualDeckW):[],nailY=topY+deckT/2+.014;
    const pairNailsDepth=(fn,group,x,y,z,dz,direction=-1)=>{fn(group,x,y,z-dz,direction);fn(group,x,y,z+dz,direction);};
    if(selected==='all'||selected==='cross'){blockPoints.forEach(p=>pairNailsDepth(nail80,groups.cross,p.x,bindY+bindT/2+.014,p.z,Math.min(.13,bindDepth*.18),-1));}
    topXs.forEach((x,i)=>{const mesh=piece('deck',actualDeckW,deckT,deckL,x,topY,0,i,groups.deck);registerInspectable(mesh,'deck',i,'Настил',deckThicknessMm,deckWidthMm,deckLengthMm,deckCount);if(selected==='all'||selected==='deck')bindZ.forEach((z,zi)=>{const edgeBoard=i===0||i===topXs.length-1,edgeCross=zi===0||zi===bindZ.length-1;if(edgeBoard&&edgeCross)cornerTriple(x,nailY,z,Math.min(.08,actualDeckW*.24));else pairNails(nail40,groups.deck,x,nailY,z,Math.min(.06,actualDeckW*.22),-1);});});
    const exploded=mode==='explode',offsets={runner:0,block:exploded?1.25:0,cross:exploded?2.55:0,deck:exploded?3.85:0};let yaw=num(state.angle,-34)*Math.PI/180,pitch=.43,distance=clamp(Math.max(PW,PL)*1.68,15,28);
    const projectMeasurePoint=(x,y,z)=>{if(!stage||!renderer.domElement)return null;const v=new THREE.Vector3(x,y,z).project(camera);if(!Number.isFinite(v.x)||!Number.isFinite(v.y)||v.z<-1.1||v.z>1.1)return null;const cr=renderer.domElement.getBoundingClientRect(),sr=stage.getBoundingClientRect();return{x:cr.left-sr.left+(v.x*.5+.5)*cr.width,y:cr.top-sr.top+(-v.y*.5+.5)*cr.height};};
    const overlay=root.querySelector('.palletOnModelMeasures');
    const measureMarks={};
    let measureLabelBoxes=[];
    const ensureMeasure=(name,kind='normal')=>{let mark=measureMarks[name];if(mark)return mark;mark=document.createElement('div');mark.className=`palletMeasureMark ${kind}`;mark.innerHTML='<i class="measureLine"></i><em class="measureTick tickA"></em><em class="measureTick tickB"></em><span></span>';overlay?.appendChild(mark);measureMarks[name]=mark;return mark;};
    const clearMeasures=()=>{measureLabelBoxes=[];Object.values(measureMarks).forEach(mark=>mark.style.display='none');};
    const paintMeasure=(name,a,b,text,opts={})=>{
      const mark=ensureMeasure(name,opts.kind||'normal');
      const p1=projectMeasurePoint(a[0],a[1],a[2]),p2=projectMeasurePoint(b[0],b[1],b[2]);
      if(!p1||!p2){mark.style.display='none';return;}
      const dx=p2.x-p1.x,dy=p2.y-p1.y,dist=Math.hypot(dx,dy);
      if(dist<(opts.minPx||4)){mark.style.display='none';return;}
      const angle=Math.atan2(dy,dx)*180/Math.PI,mx=(p1.x+p2.x)/2,my=(p1.y+p2.y)/2;
      const line=mark.querySelector('.measureLine'),tickA=mark.querySelector('.tickA'),tickB=mark.querySelector('.tickB'),label=mark.querySelector('span');
      mark.style.display='block';mark.classList.toggle('bad',!!opts.bad);mark.classList.toggle('major',!!opts.major);mark.classList.toggle('compact',!!opts.compact);
      if(line){line.style.left=`${p1.x}px`;line.style.top=`${p1.y}px`;line.style.width=`${dist}px`;line.style.transform=`rotate(${angle}deg)`;}
      [[tickA,p1],[tickB,p2]].forEach(([tick,p])=>{if(!tick)return;tick.style.left=`${p.x}px`;tick.style.top=`${p.y}px`;tick.style.transform=`translate(-50%,-50%) rotate(${angle+90}deg)`;});
      if(label){
        label.textContent=text;
        const stageW=Math.max(1,stage?.clientWidth||renderer.domElement.clientWidth||cw),stageH=Math.max(1,stage?.clientHeight||renderer.domElement.clientHeight||ch);
        const charW=opts.compact?6.1:(opts.major?8.0:7.0),labelW=Math.max(opts.compact?28:(opts.major?54:38),String(text).length*charW+(opts.compact?10:16)),labelH=opts.compact?18:(opts.major?28:22);
        const pad=6;
        let lx=mx+(opts.labelDx||0),ly=my+(opts.labelDy||0);
        lx=clamp(lx,labelW/2+pad,stageW-labelW/2-pad);ly=clamp(ly,labelH/2+pad,stageH-labelH/2-pad);
        const box={left:lx-labelW/2-3,right:lx+labelW/2+3,top:ly-labelH/2-3,bottom:ly+labelH/2+3};
        if(opts.avoidOverlap&&measureLabelBoxes.some(b=>box.left<b.right&&box.right>b.left&&box.top<b.bottom&&box.bottom>b.top)){mark.style.display='none';return;}
        measureLabelBoxes.push(box);
        label.style.left=`${lx}px`;label.style.top=`${ly}px`;
      }
      return mark;
    };
    const updateOnModelMeasures=()=>{
      clearMeasures();
      if(!topXs.length)return;
      const topView=mode==='top',sideView=mode==='side';
      const deckOffset=groups.deck.position.y;
      const topSurface=topY+deckT/2+deckOffset+.08;
      const leftX=-PW/2,rightX=PW/2,totalTop=runnerT+blockH+bindT+deckT;
      const leftOutsideX=-PW/2-(topView?.62:.72),rightOutsideX=PW/2+(topView?.72:(sideView?.72:.38));
      const frontOutsideZ=PL/2+(topView?.92:.70);
      const showDeckLength=Math.abs(deckLengthMm-profile.length)>1;

      paintMeasure('overall-length',[leftOutsideX,.08,-PL/2],[leftOutsideX,.08,PL/2],`${fmtMm(profile.length)} мм`,{major:true,labelDx:topView?-4:-8});
      if(!sideView)paintMeasure('overall-width',[leftX,.08,frontOutsideZ],[rightX,.08,frontOutsideZ],`${fmtMm(profile.width)} мм`,{major:true,labelDy:topView?0:14});
      if(!topView)paintMeasure('overall-height',[rightOutsideX,0,PL*.36],[rightOutsideX,totalTop,PL*.36],`${fmtMm(totalTop/S)} мм`,{major:true,labelDx:18});

      if(showDeckLength&&!sideView){
        const focusIndex=Math.floor((topXs.length-1)/2),focusX=topXs[focusIndex];
        paintMeasure('deck-length',[focusX,topSurface,-deckL/2],[focusX,topSurface,deckL/2],`${fmtMm(deckLengthMm)} мм`,{labelDx:22});
      }

      if(!sideView){
        const edgeZ=Math.min(deckL/2,PL/2);
        const boardFront=topView?edgeZ+.18:edgeZ-.10;
        const gapFront=topView?edgeZ+.50:edgeZ+.36;
        topXs.forEach((x,i)=>{
          paintMeasure(`board-width-${i}`,[x-actualDeckW/2,topSurface,boardFront],[x+actualDeckW/2,topSurface,boardFront],fmtMm(deckWidthMm),{compact:true,kind:'board',labelDy:topView?0:(i%2?10:-10),minPx:topView?7:16,avoidOverlap:!topView});
        });
        if(topXs.length>1){
          for(let i=0;i<topXs.length-1;i++){
            const a=topXs[i]+actualDeckW/2,b=topXs[i+1]-actualDeckW/2;
            paintMeasure(`gap-${i}`,[a,topSurface,gapFront],[b,topSurface,gapFront],gapBad?`−${fmtMm(Math.abs(rawGapMm))}`:fmtMm(rawGapMm),{compact:true,kind:'gap',bad:gapBad,labelDy:topView?0:(i%2?-11:11),minPx:topView?5:13,avoidOverlap:!topView});
          }
        }
      }

      if(!topView){
        const stackX=-PW/2-.28,stackZ=PL*.33;
        const y0=0,y1=runnerT,y2=runnerT+blockH,y3=runnerT+blockH+bindT;
        paintMeasure('layer-runner',[stackX,y0,stackZ],[stackX,y1,stackZ],fmtMm(runnerT/S),{compact:true,kind:'layer',labelDx:-24,minPx:5});
        paintMeasure('layer-block',[stackX,y1,stackZ],[stackX,y2,stackZ],fmtMm(blockH/S),{compact:true,kind:'layer',labelDx:-24,minPx:5});
        paintMeasure('layer-bind',[stackX,y2,stackZ],[stackX,y3,stackZ],fmtMm(bindT/S),{compact:true,kind:'layer',labelDx:-24,minPx:5});
        const deckBottom=topY-deckT/2+deckOffset,deckTop=topY+deckT/2+deckOffset;
        paintMeasure('layer-deck',[stackX,deckBottom,stackZ],[stackX,deckTop,stackZ],fmtMm(deckThicknessMm),{compact:true,kind:'layer',labelDx:-24,minPx:5});
      }
    };
    let updatePickButtons=()=>{};
    function draw(){if(mode==='top'){camera.up.set(0,0,-1);camera.position.set(0,Math.max(PW,PL)*2.55,.001);camera.lookAt(0,topY*.55,0);}else if(mode==='side'){camera.up.set(0,1,0);camera.position.set(Math.max(PW,PL)*2.0,Math.max(4.2,topY*2.0),0);camera.lookAt(0,topY*.55,0);}else{camera.up.set(0,1,0);const cy=Math.sin(pitch)*distance,rad=Math.cos(pitch)*distance;camera.position.set(Math.cos(yaw)*rad,cy+2.0,Math.sin(yaw)*rad);camera.lookAt(0,exploded?3.1:topY*.42,0);}renderer.render(scene,camera);updateOnModelMeasures();updatePickButtons();}
    active={renderer,scene,camera,groups,mode,signature:currentSignature(),draw,profile};
    if(exploded){const t0=performance.now();const animate=t=>{const q=clamp((t-t0)/420,0,1),e=1-Math.pow(1-q,3);groups.block.position.y=offsets.block*e;groups.cross.position.y=offsets.cross*e;groups.deck.position.y=offsets.deck*e;draw();if(q<1)raf=requestAnimationFrame(animate);};raf=requestAnimationFrame(animate);}else draw();
    const canvas=renderer.domElement;
    const partInspector=root.querySelector('.palletPartInspector');
    const pickHint=root.querySelector('.palletPickHint');
    const pickerEnabled=mode==='top'||mode==='side'||mode==='explode';
    const pickOverlay=document.createElement('div');pickOverlay.className='palletBoardPickOverlay';pickOverlay.hidden=!pickerEnabled;stage?.appendChild(pickOverlay);
    const pickButtons=inspectable.map((mesh,i)=>{const info=mesh.userData.palletInspect||{},btn=document.createElement('button');btn.type='button';btn.className='palletBoardPickZone';btn.dataset.pickIndex=String(i);btn.dataset.kind=info.kind||'';btn.setAttribute('aria-label',`Выбрать ${String(info.name||'деталь').toLowerCase()} №${Number(info.index||0)+1}`);const dimLabel=`${fmtMm(info.t)} × ${fmtMm(info.w)} × ${fmtMm(info.l)} мм`;btn.title=dimLabel;btn.innerHTML=`<span>${dimLabel}</span>`;pickOverlay.appendChild(btn);return btn;});
    const raycaster=new THREE.Raycaster(),pickPoint=new THREE.Vector2();
    let inspectDown=null,lastInspectAt=0;
    const resetInspectHighlight=()=>inspectable.forEach(mesh=>{if(!mesh.material)return;mesh.material.emissive.setHex(mesh.userData.baseEmissiveHex||0);mesh.material.emissiveIntensity=mesh.userData.baseEmissiveIntensity||0;});
    const setPickHint=(text,selected=false)=>{if(!pickHint)return;pickHint.textContent=text;pickHint.classList.toggle('selected',selected);};
    const showInspect=(mesh)=>{const info=mesh?.userData?.palletInspect;if(!info)return false;resetInspectHighlight();mesh.material.emissive.setHex(0xb66a2d);mesh.material.emissiveIntensity=.50;const itemNo=Number(info.index||0)+1,qty=Math.max(1,Math.round(num(el('qty')?.value,1))),total=info.n*qty;if(partInspector){partInspector.hidden=false;partInspector.dataset.kind=info.kind||'';partInspector.querySelector('strong').textContent=`${info.name} №${itemNo}`;partInspector.querySelector('span').textContent=`${fmtMm(info.t)} × ${fmtMm(info.w)} × ${fmtMm(info.l)} мм`;partInspector.querySelector('b').textContent=`На поддон: ${info.n} шт. · На заказ: ${total.toLocaleString('ru-RU')} шт.`;}setPickHint(`Выбрано: ${info.name} №${itemNo} · ${fmtMm(info.t)} × ${fmtMm(info.w)} × ${fmtMm(info.l)} мм`,true);window.dispatchEvent(new CustomEvent('pallet3d:partselect',{detail:{...info,itemNo,boardNo:itemNo,per:info.n,total}}));renderer.render(scene,camera);lastInspectAt=performance.now();return true;};
    const pickAt=(clientX,clientY)=>{const rect=canvas.getBoundingClientRect();if(!rect.width||!rect.height)return null;pickPoint.x=((clientX-rect.left)/rect.width)*2-1;pickPoint.y=-((clientY-rect.top)/rect.height)*2+1;scene.updateMatrixWorld(true);camera.updateMatrixWorld(true);raycaster.setFromCamera(pickPoint,camera);return raycaster.intersectObjects(inspectable,false).find(hit=>hit.object?.userData?.palletInspect)||null;};
    const pointInPolygon=(x,y,poly)=>{let inside=false;for(let i=0,j=poly.length-1;i<poly.length;j=i++){const a=poly[i],b=poly[j];if(((a.y>y)!==(b.y>y))&&(x<(b.x-a.x)*(y-a.y)/((b.y-a.y)||1e-9)+a.x))inside=!inside;}return inside;};
    const projectToCanvas=(x,y,z,rect)=>{const v=new THREE.Vector3(x,y,z).project(camera);if(!Number.isFinite(v.x)||!Number.isFinite(v.y)||v.z<-1.1||v.z>1.1)return null;return{x:(v.x*.5+.5)*rect.width,y:(-v.y*.5+.5)*rect.height};};
    const deckInspectables=inspectable.filter(mesh=>mesh?.userData?.palletInspect?.kind==='deck');
    const pickDeckByProjection=(clientX,clientY)=>{
      const rect=canvas.getBoundingClientRect();if(!rect.width||!rect.height||!deckInspectables.length)return null;
      const px=clientX-rect.left,py=clientY-rect.top;
      scene.updateMatrixWorld(true);camera.updateMatrixWorld(true);
      const y=topY+deckT/2+groups.deck.position.y+.025,halfW=actualDeckW/2+.09,halfL=deckL/2+.07;
      const candidates=[];
      deckInspectables.forEach((mesh,i)=>{
        const x=topXs[i]??mesh.position.x;
        const poly=[projectToCanvas(x-halfW,y,-halfL,rect),projectToCanvas(x+halfW,y,-halfL,rect),projectToCanvas(x+halfW,y,halfL,rect),projectToCanvas(x-halfW,y,halfL,rect)];
        if(poly.some(p=>!p))return;
        if(pointInPolygon(px,py,poly)){
          const c=projectToCanvas(x,y,0,rect),d=c?Math.hypot(px-c.x,py-c.y):0;
          candidates.push({object:mesh,d});
        }
      });
      if(candidates.length){candidates.sort((a,b)=>a.d-b.d);return candidates[0];}
      return null;
    };
    const selectAt=(clientX,clientY)=>{if(!pickerEnabled)return false;const hit=pickAt(clientX,clientY);if(hit)return showInspect(hit.object);if(mode==='top'){const projected=pickDeckByProjection(clientX,clientY);if(projected)return showInspect(projected.object);}return false;};
    updatePickButtons=()=>{
      if(!stage||!pickButtons.length)return;
      if(!pickerEnabled){pickOverlay.hidden=true;pickButtons.forEach(btn=>btn.hidden=true);return;}
      pickOverlay.hidden=false;
      const sr=stage.getBoundingClientRect(),cr=canvas.getBoundingClientRect();
      if(!sr.width||!sr.height||!cr.width||!cr.height)return;
      scene.updateMatrixWorld(true);camera.updateMatrixWorld(true);
      const visibleKinds=mode==='top'?new Set(['deck','cross']):new Set(['deck','cross','runner','block']);
      const cornerBits=[[-1,-1,-1],[1,-1,-1],[-1,1,-1],[1,1,-1],[-1,-1,1],[1,-1,1],[-1,1,1],[1,1,1]];
      pickButtons.forEach((btn,i)=>{
        const mesh=inspectable[i],info=mesh?.userData?.palletInspect;if(!mesh||!info||!visibleKinds.has(info.kind)){btn.hidden=true;return;}
        mesh.geometry.computeBoundingBox?.();const bb=mesh.geometry.boundingBox;if(!bb){btn.hidden=true;return;}
        const cx=(bb.min.x+bb.max.x)/2,cy=(bb.min.y+bb.max.y)/2,cz=(bb.min.z+bb.max.z)/2,hx=(bb.max.x-bb.min.x)/2,hy=(bb.max.y-bb.min.y)/2,hz=(bb.max.z-bb.min.z)/2,pts=[];
        for(const [sx,sy,sz] of cornerBits){const v=new THREE.Vector3(cx+sx*hx,cy+sy*hy,cz+sz*hz).applyMatrix4(mesh.matrixWorld).project(camera);if(!Number.isFinite(v.x)||!Number.isFinite(v.y)||v.z<-1.1||v.z>1.1)continue;pts.push({x:cr.left-sr.left+(v.x*.5+.5)*cr.width,y:cr.top-sr.top+(-v.y*.5+.5)*cr.height});}
        if(pts.length<4){btn.hidden=true;return;}
        let minX=Math.min(...pts.map(p=>p.x)),maxX=Math.max(...pts.map(p=>p.x)),minY=Math.min(...pts.map(p=>p.y)),maxY=Math.max(...pts.map(p=>p.y));
        if(maxX<0||maxY<0||minX>sr.width||minY>sr.height){btn.hidden=true;return;}
        const pad=info.kind==='block'?8:6;minX=clamp(minX-pad,0,sr.width-18);maxX=clamp(maxX+pad,18,sr.width);minY=clamp(minY-pad,0,sr.height-24);maxY=clamp(maxY+pad,24,sr.height);
        btn.hidden=false;btn.style.left=`${minX}px`;btn.style.top=`${minY}px`;btn.style.width=`${Math.max(20,maxX-minX)}px`;btn.style.height=`${Math.max(28,maxY-minY)}px`;btn.style.zIndex=String(info.kind==='deck'?4:info.kind==='cross'?3:info.kind==='block'?2:1);
      });
    };
    pickButtons.forEach((btn,i)=>btn.addEventListener('click',e=>{e.preventDefault();e.stopPropagation();if(!pickerEnabled)return;const mesh=inspectable[i];if(mesh)showInspect(mesh);previewCard?.classList.remove('partPickMode');}));
    updatePickButtons();
    canvas.addEventListener('pointerdown',e=>{inspectDown={x:e.clientX,y:e.clientY};},true);
    canvas.addEventListener('pointerup',e=>{if(!inspectDown)return;const moved=Math.hypot(e.clientX-inspectDown.x,e.clientY-inspectDown.y);inspectDown=null;if(moved<=18)selectAt(e.clientX,e.clientY);},true);
    canvas.addEventListener('click',e=>{if(performance.now()-lastInspectAt>220)selectAt(e.clientX,e.clientY);});
    canvas.addEventListener('pointermove',e=>{if(e.buttons!==0)return;if(!pickerEnabled){canvas.style.cursor='grab';return;}const hit=pickAt(e.clientX,e.clientY);canvas.style.cursor=hit?'pointer':((mode==='top'||mode==='side')?'default':'grab');},true);
    let dragging=false,lastX=0,lastY=0;
    canvas.addEventListener('pointerdown',e=>{if(mode==='top'||mode==='side')return;dragging=true;lastX=e.clientX;lastY=e.clientY;canvas.setPointerCapture?.(e.pointerId);canvas.classList.add('dragging');});
    canvas.addEventListener('pointermove',e=>{if(!dragging||mode==='top'||mode==='side')return;const dx=e.clientX-lastX,dy=e.clientY-lastY;lastX=e.clientX;lastY=e.clientY;yaw-=dx*.009;pitch=clamp(pitch-dy*.006,.15,.95);state.angle=yaw*180/Math.PI;draw();});
    const stop=()=>{dragging=false;canvas.classList.remove('dragging');};canvas.addEventListener('pointerup',stop);canvas.addEventListener('pointercancel',stop);
    canvas.addEventListener('wheel',e=>{if(mode==='top'||mode==='side')return;e.preventDefault();distance=clamp(distance*(e.deltaY>0?1.08:.92),10,38);draw();},{passive:false});
    root.querySelectorAll('[data-p3d-mode]').forEach(btn=>btn.addEventListener('click',()=>{state.mode=btn.dataset.p3dMode;render(num(el('pL')?.value),num(el('pW')?.value));}));
    root.querySelector('[data-p3d-dims]')?.addEventListener('click',()=>{state.showDimensions=!state.showDimensions;render(num(el('pL')?.value),num(el('pW')?.value));});
    root.querySelectorAll('[data-p3d-part]').forEach(btn=>btn.addEventListener('click',()=>{const k=btn.dataset.p3dPart;state.selected=state.selected===k?'all':k;render(num(el('pL')?.value),num(el('pW')?.value));}));
    if(window.ResizeObserver){const observer=new ResizeObserver(()=>{clearTimeout(resizeTimer);resizeTimer=setTimeout(()=>{if(!active||!host.isConnected)return;const w=Math.max(280,host.clientWidth),h=window.innerWidth<620?390:510;renderer.setSize(w,h,false);camera.aspect=w/h;camera.updateProjectionMatrix();draw();},100);});observer.observe(host);active.observer=observer;}
  }

  function setupLivePalletDimensions(){
    const refresh=()=>{if(syncQueued)return;syncQueued=true;requestAnimationFrame(()=>{syncQueued=false;window.rerenderPallet3D?.();});};
    ['pL','pW','n0','t0','w0','l0'].forEach(id=>{const input=el(id);if(!input||input.dataset.palletMeasureReady==='1')return;input.dataset.palletMeasureReady='1';input.addEventListener('input',refresh);input.addEventListener('change',refresh);});
  }

  function setupDeckCountControl(){
    const qty=el('qty'),deck=el('n0');if(!qty||!deck||el('deckQty'))return;const cell=qty.parentElement;if(!cell)return;
    const label=document.createElement('label');label.htmlFor='deckQty';label.textContent='Количество настила';label.style.marginTop='10px';
    const input=document.createElement('input');input.id='deckQty';input.type='number';input.min='0';input.step='1';input.value=deck.value||'0';
    const syncLimit=()=>{const profile=resolveProfile(num(el('pL')?.value,1200),num(el('pW')?.value,800));if(profile.deckMax>0)input.max=String(profile.deckMax);};
    input.addEventListener('input',()=>{syncLimit();const max=num(input.max,99),value=clamp(Math.round(num(input.value,0)),0,max);input.value=String(value);deck.value=String(value);deck.dispatchEvent(new Event('input',{bubbles:true}));});
    deck.addEventListener('input',()=>{input.value=deck.value||'0';syncLimit();});el('pL')?.addEventListener('input',syncLimit);el('pW')?.addEventListener('input',syncLimit);cell.append(label,input);syncLimit();
  }

  function setupAdminEmployeeDelete(){
    const usersBox=el('adminUsersList');if(!usersBox||usersBox.dataset.employeeDeleteReady==='1')return;usersBox.dataset.employeeDeleteReady='1';
    const decorate=()=>{if(typeof currentRole==='undefined'||currentRole!=='admin')return;usersBox.querySelectorAll('.adminUser').forEach(row=>{const roleSelect=row.querySelector('.adminRole');if(!roleSelect||roleSelect.disabled||roleSelect.value!=='employee'||row.querySelector('.adminDeleteEmployee'))return;const btn=document.createElement('button');btn.type='button';btn.className='adminDeleteEmployee';btn.textContent='Удалить';btn.style.cssText='min-height:36px;border:1px solid #e2b8b4;border-radius:9px;padding:7px 10px;background:#fff6f5;color:#8a2f28;font-weight:800;cursor:pointer;';btn.addEventListener('click',async()=>{const label=row.querySelector('.adminEmail')?.textContent?.trim()||'этого сотрудника';if(!confirm(`Удалить сотрудника ${label}? Доступ к аккаунту будет закрыт. Его прошлые расчёты останутся в истории.`))return;btn.disabled=true;btn.textContent='Удаление…';try{const {data,error}=await sb.functions.invoke('admin-delete-employee',{body:{user_id:roleSelect.dataset.user}});if(error||!data?.ok)throw new Error(data?.error||error?.message||'Не удалось удалить сотрудника');alert('Сотрудник удалён. Прошлые расчёты сохранены в истории.');if(typeof loadAdminData==='function')await loadAdminData();}catch(err){alert('Не удалось удалить сотрудника: '+(err?.message||'неизвестная ошибка'));btn.disabled=false;btn.textContent='Удалить';}});row.appendChild(btn);});};
    if(window.MutationObserver)new MutationObserver(()=>queueMicrotask(decorate)).observe(usersBox,{childList:true,subtree:true});decorate();
  }

  function setupAdminEmployeeInvite(){
    const usersBox=el('adminUsersList');if(!usersBox||el('adminInviteEmployee'))return;const box=usersBox.closest('.adminBox');if(!box)return;
    const btn=document.createElement('button');btn.type='button';btn.id='adminInviteEmployee';btn.textContent='+ Добавить сотрудника';btn.style.cssText='width:100%;margin:0 0 10px;min-height:40px;border:0;border-radius:10px;background:#176b4c;color:#fff;font-weight:850;cursor:pointer;';
    const linkBox=document.createElement('div');linkBox.id='adminInviteLinkBox';linkBox.hidden=true;linkBox.style.cssText='margin:0 0 10px;padding:10px;border:1px solid #d7e5de;border-radius:10px;background:#f6fbf8;';
    const linkLabel=document.createElement('div');linkLabel.style.cssText='font-size:12px;font-weight:800;color:#31584c;margin-bottom:7px;';
    const linkRow=document.createElement('div');linkRow.style.cssText='display:flex;gap:7px;align-items:center;';
    const linkInput=document.createElement('input');linkInput.type='text';linkInput.readOnly=true;linkInput.setAttribute('aria-label','Ссылка приглашения');linkInput.style.cssText='flex:1;min-width:0;height:38px;border:1px solid #cfded7;border-radius:8px;padding:0 9px;background:#fff;font-size:11px;';
    const copyBtn=document.createElement('button');copyBtn.type='button';copyBtn.textContent='Скопировать ссылку';copyBtn.style.cssText='min-height:38px;border:0;border-radius:8px;padding:0 10px;background:#31584c;color:#fff;font-weight:850;cursor:pointer;white-space:nowrap;';
    const showInviteLink=(link,email)=>{linkInput.value=link||'';linkLabel.textContent=`Резервная ссылка для ${email||'сотрудника'}`;linkBox.hidden=!link;};
    copyBtn.addEventListener('click',async()=>{const link=linkInput.value;if(!link)return;let copied=false;try{await navigator.clipboard.writeText(link);copied=true;}catch(_){try{linkInput.focus();linkInput.select();copied=document.execCommand('copy');}catch(__){copied=false;}}copyBtn.textContent=copied?'Скопировано ✓':'Не удалось';setTimeout(()=>copyBtn.textContent='Скопировать ссылку',1600);});
    linkRow.append(linkInput,copyBtn);linkBox.append(linkLabel,linkRow);
    btn.addEventListener('click',async()=>{if(typeof currentRole==='undefined'||currentRole!=='admin')return;const fullName=(prompt('Ф.И.О. нового сотрудника:')||'').trim();if(!fullName)return;const position=(prompt('Должность сотрудника:')||'').trim();if(!position)return;const email=(prompt('Email сотрудника:')||'').trim().toLowerCase();if(!email)return;btn.disabled=true;btn.textContent='Отправляем приглашение…';try{const {data,error}=await sb.functions.invoke('admin-invite-employee',{body:{email,full_name:fullName,position}});if(error||!data?.ok)throw new Error(data?.error||error?.message||'Не удалось создать приглашение');if(data.email_sent){showInviteLink('',email);alert(`Сотрудник создан. Письмо со ссылкой для создания пароля автоматически отправлено на ${email}.`);}else if(data.invite_link){showInviteLink(data.invite_link,email);alert('Сотрудник создан. Лимит почты исчерпан, поэтому резервная ссылка показана в админ-панели. Нажмите «Скопировать ссылку» и отправьте её сотруднику.');}else{throw new Error(data?.warning||data?.error||'Не удалось получить ссылку приглашения');}if(typeof loadAdminData==='function')await loadAdminData();}catch(err){alert('Не удалось добавить сотрудника: '+(err?.message||'неизвестная ошибка'));}btn.disabled=false;btn.textContent='+ Добавить сотрудника';});
    box.insertBefore(btn,usersBox);box.insertBefore(linkBox,usersBox);
  }

  function setupPrivateRegistration(){
    const signup=el('signupBtn'),reg=el('authRegisterOnly'),divider=document.querySelector('.authDivider');if(signup){signup.hidden=true;signup.style.display='none';}if(reg)reg.hidden=true;if(divider){divider.hidden=true;divider.style.display='none';}const welcome=document.querySelector('.authWelcome p');if(welcome)welcome.innerHTML='Вход только для сотрудников,<br>добавленных администратором';
  }

  function setupPasswordRecovery(){
    const email=el('authEmail'),password=el('authPassword'),login=el('loginBtn'),signup=el('signupBtn'),authFields=el('authFields');if(!email||!password||!login||!authFields||el('forgotPasswordBtn')||typeof sb==='undefined')return;
    const forgot=document.createElement('button');forgot.type='button';forgot.id='forgotPasswordBtn';forgot.textContent='Забыли пароль?';forgot.style.cssText='border:0;background:transparent;color:#4d6f96;font-size:11px;font-weight:800;cursor:pointer;margin:-6px 0 0 auto;padding:2px 0;';password.closest('.authField')?.appendChild(forgot);
    let recoveryMode=false;
    const showRecovery=()=>{recoveryMode=true;const card=el('authCard'),reg=el('authRegisterOnly');card?.classList.remove('loggedIn');authFields.style.display='grid';if(reg)reg.hidden=true;if(signup)signup.style.display='none';email.closest('.authField')?.setAttribute('hidden','');forgot.style.display='none';password.value='';password.placeholder='Новый пароль, минимум 6 символов';password.autocomplete='new-password';login.innerHTML='Сохранить новый пароль <span>→</span>';if(typeof setAuthMessage==='function')setAuthMessage('Введите новый пароль минимум из 6 символов.');setTimeout(()=>password.focus(),40);};
    forgot.addEventListener('click',async()=>{const address=email.value.trim();if(!address){if(typeof setAuthMessage==='function')setAuthMessage('Введите email, затем нажмите «Забыли пароль?».',true);email.focus();return;}forgot.disabled=true;forgot.textContent='Отправляем…';const {error}=await sb.auth.resetPasswordForEmail(address,{redirectTo:typeof SITE_URL!=='undefined'?SITE_URL:location.origin+location.pathname});forgot.disabled=false;forgot.textContent='Забыли пароль?';if(error){if(typeof setAuthMessage==='function')setAuthMessage('Не удалось отправить письмо: '+error.message,true);return;}if(typeof setAuthMessage==='function')setAuthMessage('Письмо для восстановления отправлено. Откройте ссылку из письма и задайте новый пароль.');});
    login.addEventListener('click',async e=>{if(!recoveryMode)return;e.preventDefault();e.stopImmediatePropagation();const next=password.value;if(next.length<6){if(typeof setAuthMessage==='function')setAuthMessage('Новый пароль должен содержать минимум 6 символов.',true);return;}login.disabled=true;const {error}=await sb.auth.updateUser({password:next});login.disabled=false;if(error){if(typeof setAuthMessage==='function')setAuthMessage('Не удалось изменить пароль: '+error.message,true);return;}if(typeof setAuthMessage==='function')setAuthMessage('Пароль установлен. Теперь войдите с новым паролем.');await sb.auth.signOut();recoveryMode=false;email.closest('.authField')?.removeAttribute('hidden');forgot.style.display='';password.value='';password.placeholder='Минимум 6 символов';password.autocomplete='current-password';login.innerHTML='Войти <span>→</span>';setupPrivateRegistration();},true);
    const linkType=new URLSearchParams((location.hash||'').replace(/^#/,'' )).get('type');if(linkType==='invite'||linkType==='recovery')setTimeout(showRecovery,0);sb.auth.onAuthStateChange((event)=>{if(event==='PASSWORD_RECOVERY')setTimeout(showRecovery,0);});
  }

  function setupUserPresence(){
    if(typeof sb==='undefined'||window.__palletPresenceReady)return;window.__palletPresenceReady=true;
    let lastActive=Date.now(),lastSent=0,sending=false;
    const send=async(force=false)=>{if(sending||(!force&&document.hidden))return;const now=Date.now();if(!force&&now-lastSent<10000)return;const {data}=await sb.auth.getSession();const user=data?.session?.user;if(!user)return;sending=true;lastSent=now;const stamp=new Date(now).toISOString();try{const {error}=await sb.from('user_presence').upsert({user_id:user.id,last_seen:stamp,last_active:new Date(lastActive).toISOString(),updated_at:stamp},{onConflict:'user_id'});if(error)console.warn('Presence update failed',error.message);}catch(err){console.warn('Presence update failed',err);}sending=false;};
    const touch=()=>{lastActive=Date.now();send(false);};['pointerdown','keydown','input','click','touchstart'].forEach(name=>document.addEventListener(name,touch,{passive:true,capture:true}));document.addEventListener('visibilitychange',()=>{if(!document.hidden){lastActive=Date.now();send(true);}});setInterval(()=>send(false),30000);sb.auth.onAuthStateChange((_event,session)=>{if(session){lastActive=Date.now();setTimeout(()=>send(true),300);}});setTimeout(()=>send(true),900);
  }

  function setupAdminPresenceStatus(){
    const usersBox=el('adminUsersList');if(!usersBox||usersBox.dataset.presenceReady==='1'||typeof sb==='undefined')return;usersBox.dataset.presenceReady='1';const box=usersBox.closest('.adminBox');let busy=false,timer=0;
    const ago=ms=>{const min=Math.max(1,Math.round(ms/60000));if(min<60)return `${min} мин назад`;const h=Math.round(min/60);return h<24?`${h} ч назад`:`${Math.round(h/24)} дн назад`;};
    const refresh=async()=>{if(busy||typeof currentRole==='undefined'||currentRole!=='admin')return;busy=true;try{const {data,error}=await sb.from('user_presence').select('user_id,last_seen,last_active');if(error)throw error;const map=new Map((data||[]).map(p=>[p.user_id,p])),now=Date.now();let onlineCount=0,activeCount=0;usersBox.querySelectorAll('.adminUser').forEach(row=>{const role=row.querySelector('.adminRole'),id=role?.dataset?.user;if(!id)return;const p=map.get(id),seen=p?now-new Date(p.last_seen).getTime():Infinity,act=p?now-new Date(p.last_active).getTime():Infinity;const online=seen<=75000,activeNow=online&&act<=120000;if(online)onlineCount++;if(activeNow)activeCount++;let badge=row.querySelector('.adminPresence');if(!badge){badge=document.createElement('div');badge.className='adminPresence';badge.style.cssText='font-size:11px;font-weight:850;margin-top:4px;white-space:nowrap;';row.appendChild(badge);}if(activeNow){badge.textContent='● Онлайн · активно работает';badge.style.color='#16804f';}else if(online){badge.textContent='● Онлайн · без действий';badge.style.color='#5f7b70';}else if(p){badge.textContent='○ Не в сети · '+ago(seen);badge.style.color='#87938d';}else{badge.textContent='○ Ещё не заходил';badge.style.color='#9aa39f';}});if(box){let summary=el('adminPresenceSummary');if(!summary){summary=document.createElement('div');summary.id='adminPresenceSummary';summary.style.cssText='margin:0 0 10px;padding:9px 11px;border:1px solid #dbe8e1;border-radius:10px;background:#f6fbf8;color:#31584c;font-size:12px;font-weight:800;';box.insertBefore(summary,usersBox);}summary.textContent=`Сейчас онлайн: ${onlineCount} · Активно работают: ${activeCount}`;}}catch(err){console.warn('Presence read failed',err);}finally{busy=false;}};
    const schedule=()=>{clearTimeout(timer);timer=setTimeout(refresh,350);};if(window.MutationObserver)new MutationObserver(schedule).observe(usersBox,{childList:true,subtree:true});setInterval(refresh,20000);setTimeout(refresh,1800);
  }

  function setupDashboardPalletPreview(){
    const orderImg=document.querySelector('.orderFocus>img'),viewImg=document.querySelector('.dashPalletImage img');
    if(!orderImg&&!viewImg)return;
    let lastSignature='';
    const pts=a=>a.map(v=>`${v[0].toFixed(1)},${v[1].toFixed(1)}`).join(' ');
    const makeSvg=(length,width,deckCount)=>{
      length=Math.max(300,num(length,1200));width=Math.max(300,num(width,800));deckCount=clamp(Math.round(num(deckCount,7)),3,12);
      const fitX=.76*width+.42*length,fitY=.15*width+.20*length,scale=Math.min(430/fitX,150/fitY),W=width*scale,L=length*scale,cx=270,baseY=171;
      const p=(x,z,y=0)=>[cx+x*.76-z*.42,baseY+x*.15+z*.20-y];
      const prism=(x0,z0,x1,z1,y,h,top,front,side)=>{const A=p(x0,z0,y+h),B=p(x1,z0,y+h),C=p(x1,z1,y+h),D=p(x0,z1,y+h),B0=p(x1,z0,y),C0=p(x1,z1,y),D0=p(x0,z1,y);return `<polygon points="${pts([D,C,C0,D0])}" fill="${front}"/><polygon points="${pts([B,C,C0,B0])}" fill="${side}"/><polygon points="${pts([A,B,C,D])}" fill="${top}" stroke="#8d623b" stroke-opacity=".24" stroke-width=".8"/>`;};
      let shape='';
      const runnerCenters=[-W*.34,0,W*.34],runnerW=Math.max(11,W*.12),runnerH=11;
      runnerCenters.forEach(x=>shape+=prism(x-runnerW/2,-L*.37,x+runnerW/2,L*.37,0,runnerH,'url(#runnerTop)','#b6783f','#925b31'));
      const blockW=Math.max(15,W*.16),blockL=Math.max(15,L*.11),blockH=28;
      runnerCenters.forEach(x=>[-L*.32,0,L*.32].forEach(z=>shape+=prism(x-blockW/2,z-blockL/2,x+blockW/2,z+blockL/2,runnerH,blockH,'url(#blockTop)','#c4874d','#9d6337')));
      const crossH=9,crossDepth=Math.max(9,L*.055);
      [-L*.32,0,L*.32].forEach(z=>shape+=prism(-W*.47,z-crossDepth/2,W*.47,z+crossDepth/2,runnerH+blockH,crossH,'url(#crossTop)','#d7a46d','#af7744'));
      const deckH=9,deckW=Math.max(8,Math.min(W*.13,W*.84/deckCount));
      for(let i=0;i<deckCount;i++){const x=-W*.47+deckW/2+i*(W*.94-deckW)/(deckCount-1);shape+=prism(x-deckW/2,-L*.47,x+deckW/2,L*.47,runnerH+blockH+crossH,deckH,'url(#deckTop)','#e1b77f','#bd8952');}
      const shadowRx=Math.min(190,(W*.76+L*.42)*.43);
      const svg=`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 540 300" role="img" aria-label="Поддон ${Math.round(length)} на ${Math.round(width)} миллиметров"><defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#fff"/><stop offset="1" stop-color="#f3eee6"/></linearGradient><linearGradient id="deckTop" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#f6d7aa"/><stop offset=".52" stop-color="#e8bd83"/><stop offset="1" stop-color="#d9a86d"/></linearGradient><linearGradient id="crossTop" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#efc994"/><stop offset="1" stop-color="#dca66b"/></linearGradient><linearGradient id="blockTop" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#e4b57b"/><stop offset="1" stop-color="#c98d52"/></linearGradient><linearGradient id="runnerTop" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#dca86d"/><stop offset="1" stop-color="#bd7d43"/></linearGradient><filter id="soft"><feGaussianBlur stdDeviation="8"/></filter></defs><rect width="540" height="300" rx="24" fill="#fbfaf7"/><ellipse cx="270" cy="235" rx="${shadowRx.toFixed(1)}" ry="24" fill="#66513b" opacity=".15" filter="url(#soft)"/>${shape}<text x="270" y="282" text-anchor="middle" font-family="Arial, sans-serif" font-size="13" font-weight="700" fill="#75695d">${Math.round(length)} × ${Math.round(width)} мм · настил ${deckCount} шт.</text></svg>`;
      return 'data:image/svg+xml;charset=UTF-8,'+encodeURIComponent(svg);
    };
    const refresh=()=>{const length=num(el('pL')?.value,1200),width=num(el('pW')?.value,800),deckCount=num(el('n0')?.value,7),signature=`${length}|${width}|${deckCount}`;if(signature===lastSignature)return;lastSignature=signature;const src=makeSvg(length,width,deckCount);[orderImg,viewImg].forEach(img=>{if(!img)return;img.src=src;img.alt=`Поддон ${Math.round(length)} × ${Math.round(width)} мм`;img.classList.add('dashDynamicPallet');});};
    ['pL','pW','n0'].forEach(id=>{const input=el(id);if(!input||input.dataset.dashboardPreviewReady==='1')return;input.dataset.dashboardPreviewReady='1';input.addEventListener('input',refresh);input.addEventListener('change',refresh);});
    refresh();setInterval(refresh,1500);
  }

  function updateSiteVersion(){const node=document.querySelector('.sideVersion');if(!node)return;const admin=typeof currentRole!=='undefined'&&currentRole==='admin';node.textContent=admin?'Pallet Tools · v1.1.16 · обновление №346':'Pallet Tools · v1.1.16';}
  window.updateSiteVersion=updateSiteVersion;
  const adminVersionTarget=el('adminSideNav');if(adminVersionTarget&&window.MutationObserver){new MutationObserver(updateSiteVersion).observe(adminVersionTarget,{attributes:true,attributeFilter:['hidden','style']});}

  window.renderDynamicPallet=render;
  window.rerenderPallet3D=function(){const sig=currentSignature();if(active&&active.signature===sig&&active.mode===(state.mode||'3d')&&document.querySelector('.palletReferenceHost canvas')){active.draw();return;}render(num(el('pL')?.value),num(el('pW')?.value));};
  setupDeckCountControl();setupLivePalletDimensions();setupAdminEmployeeDelete();setupAdminEmployeeInvite();setupPrivateRegistration();setupPasswordRecovery();setupUserPresence();setupAdminPresenceStatus();setupDashboardPalletPreview();updateSiteVersion();
  setTimeout(()=>render(num(el('pL')?.value),num(el('pW')?.value)),120);
  window.addEventListener('resize',()=>{clearTimeout(resizeTimer);resizeTimer=setTimeout(()=>window.rerenderPallet3D?.(),160);});
})();
