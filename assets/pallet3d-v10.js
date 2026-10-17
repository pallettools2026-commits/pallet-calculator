/* pallet3dStandardOnlyV126 — clean visible standard 3D */
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
    const profile=resolveProfile(inputL,inputW);
    const previewCard=root.closest('.previewCard');
    const previewStage=el('previewStage');
    const previewActions=previewCard?.querySelector('.previewActions');
    if(profile.key==='unsupported'){
      state.mode='3d';state.selected='all';
      root.innerHTML='';
      if(previewCard)previewCard.style.display='';
      if(previewStage)previewStage.style.display='none';
      if(previewActions)previewActions.style.display='none';
      return;
    }
    if(previewCard)previewCard.style.display='';
    if(previewStage)previewStage.style.display='flex';
    if(previewActions)previewActions.style.display='flex';
    root.style.display='block';
    root.style.width='100%';
    root.style.padding='0';
    root.style.minHeight='0';
    syncProfileInputs(profile);
    const P=[0,1,2,3,4,5,6].map(part),deck=P[0],bindParts=[P[1],P[2]],runnerParts=[P[3],P[4]],block1=P[5],block2=P[6];
    const isReference=false;
    const rawDeck=Math.max(0,Math.round(num(deck.n))),deckCount=isReference?9:Math.min(profile.deckMax,rawDeck);
    const rawBlocks=Math.max(0,Math.round(num(block1.n)))+Math.max(0,Math.round(num(block2.n))),blockCount=isReference?9:Math.min(9,rawBlocks||9);
    const runnerCount=isReference?3:(profile.runnerLengths?profile.runnerLengths.length:Math.max(1,Math.min(7,Math.round(num(runnerParts[0].n)+num(runnerParts[1].n))||3)));
    const mode=state.mode||'3d';
    const chip=(k,label,c)=>`<button type="button" class="palletPartChip ${state.selected===k?'active':''}" data-p3d-part="${k}">${label}<b>${c}</b></button>`;
    const fastenerLegend=mode==='explode'?'<div style="display:flex;justify-content:center;gap:12px;flex-wrap:wrap;margin:7px auto 0;font-size:11px;font-weight:800;color:#46514d"><span>● 2,8×80 мм — поперечины над шашками и лыжи</span><span>● 2,5×40 мм — настил к поперечинам</span></div>':'';
    root.innerHTML=`<div class="pallet3dToolbar" role="tablist"><button type="button" data-p3d-mode="3d" class="${mode==='3d'?'active':''}">3D</button><button type="button" data-p3d-mode="top" class="${mode==='top'?'active':''}">Сверху</button><button type="button" data-p3d-mode="side" class="${mode==='side'?'active':''}">Сбоку</button><button type="button" data-p3d-mode="explode" class="${mode==='explode'?'active':''}">${mode==='explode'?'Собрать':'Разнести'}</button></div>${fastenerLegend}<div class="palletReferenceStage" style="width:100%;position:relative;overflow:hidden;background:radial-gradient(circle at 50% 30%,#fff 0,#faf8f3 52%,#efede7 100%);border-radius:14px;margin-top:8px"><div class="palletReferenceHost" style="width:100%;min-height:390px;position:relative"></div></div>`;

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
    const nail40Length=.40,nail80Length=.80;
    // Крепёж слегка утолщён только визуально, чтобы реальные 2,5/2,8 мм не терялись на экране.
    const nail40HeadGeo=new THREE.CylinderGeometry(.044,.044,.026,16),nail80HeadGeo=new THREE.CylinderGeometry(.052,.052,.030,18);
    const nail40ShankGeo=new THREE.CylinderGeometry(.018,.020,nail40Length,12),nail80ShankGeo=new THREE.CylinderGeometry(.022,.025,nail80Length,12);
    const nail40Mat=new THREE.MeshStandardMaterial({color:0x596166,roughness:.34,metalness:.58});
    const nail80Mat=new THREE.MeshStandardMaterial({color:0x3f4549,roughness:.30,metalness:.66});
    function addNail(group,headGeo,shankGeo,mat,x,y,z,direction=-1){
      const head=new THREE.Mesh(headGeo,mat);head.position.set(x,y,z);head.castShadow=true;group.add(head);
      if(mode==='explode'){
        const shank=new THREE.Mesh(shankGeo,mat),len=shankGeo.parameters.height||.4;
        shank.position.set(x,y+direction*len/2,z);shank.castShadow=true;group.add(shank);
      }
    }
    const nail40=(group,x,y,z,direction=-1)=>addNail(group,nail40HeadGeo,nail40ShankGeo,nail40Mat,x,y,z,direction);
    const nail80=(group,x,y,z,direction=-1)=>addNail(group,nail80HeadGeo,nail80ShankGeo,nail80Mat,x,y,z,direction);
    const pairNails=(fn,group,x,y,z,dx,direction=-1)=>{fn(group,x-dx,y,z,direction);fn(group,x+dx,y,z,direction);};
    const cornerTriple=(x,y,z,dx)=>{
      const inward=z<0?1:-1;
      nail80(groups.deck,x-dx,y,z-.03*inward,-1);
      nail80(groups.deck,x+dx,y,z-.03*inward,-1);
      nail80(groups.deck,x,y,z+.05*inward,-1);
    };

    const runnerT=isReference?.22:Math.max(.15,num(runnerParts[0].t,22)*S),runnerW=isReference?.98:Math.max(.58,num(runnerParts[0].w,98)*S);
    const blockH=.75,blockXSize1=.95,blockZSize1=.95,blockXSize2=.95,blockZSize2=.95;
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

    const blockY=runnerT+blockH/2,blockRows=[],blockPoints=[];
    for(let zi=0;zi<3;zi++)for(let xi=0;xi<3;xi++){
      const idx=zi*3+xi;if(idx>=blockCount)continue;
      const centerType=(xi===1),bx=centerType?blockXSize2:blockXSize1,bz=centerType?blockZSize2:blockZSize1;
      const sx=xi===0?-1:xi===2?1:0,sz=zi===0?-1:zi===2?1:0;
      const bxPos=sx===0?0:sx*Math.max(0,PW/2-bx/2-.03);
      const bzPos=sz===0?0:sz*Math.max(0,PL/2-bz/2-.03);
      blockRows[zi]=bzPos;
      blockPoints.push({x:bxPos,z:bzPos,bx,bz});
      piece('block',bx,blockH,bz,bxPos,blockY,bzPos,idx,groups.block);
    }
    if(selected==='all'||selected==='runner'){
      runnerXs.forEach((x,xi)=>blockRows.forEach((z,zi)=>{
        if(z==null||zi*3+Math.min(xi,2)>=blockCount)return;
        pairNails(nail80,groups.runner,x,runnerT+.014,z,Math.min(.072,runnerActualW*.22),1);
      }));
    }

    const bindY=runnerT+blockH+bindT/2;
    const bindZ=[-PL/2+bindDepth/2+.02,0,PL/2-bindDepth/2-.02];
    bindZ.forEach((z,i)=>piece('cross',PW,bindT,bindDepth,0,bindY,z,i,groups.cross));

    const topY=runnerT+blockH+bindT+deckT/2;
    const actualDeckW=deckCount?Math.min(deckW,(PW*.92/Math.max(1,deckCount))*.78):deckW;
    const topXs=deckCount?spread(deckCount,PW,actualDeckW):[];
    const nailY=topY+deckT/2+.014;
    const pairNailsDepth=(fn,group,x,y,z,dz,direction=-1)=>{fn(group,x,y,z-dz,direction);fn(group,x,y,z+dz,direction);};
    if(selected==='all'||selected==='cross'){
      // Гвозди поперечина → шашка остаются строго над реальной шашкой.
      // Если сверху проходит доска настила, в собранном виде она естественно скрывает этот крепёж.
      blockPoints.forEach(p=>{
        pairNailsDepth(nail80,groups.cross,p.x,bindY+bindT/2+.014,p.z,Math.min(.13,bindDepth*.18),-1);
      });
    }
    topXs.forEach((x,i)=>{
      piece('deck',actualDeckW,deckT,PL,x,topY,0,i,groups.deck);
      if(selected==='all'||selected==='deck')bindZ.forEach((z,zi)=>{
        const edgeBoard=i===0||i===topXs.length-1;
        const edgeCross=zi===0||zi===bindZ.length-1;
        if(edgeBoard&&edgeCross)cornerTriple(x,nailY,z,Math.min(.08,actualDeckW*.24));
        else pairNails(nail40,groups.deck,x,nailY,z,Math.min(.06,actualDeckW*.22),-1);
      });
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

  function setupDeckCountControl(){
    const qty=el('qty'),deck=el('n0');
    if(!qty||!deck||el('deckQty'))return;
    const cell=qty.parentElement;if(!cell)return;
    const label=document.createElement('label');label.htmlFor='deckQty';label.textContent='Количество настила';label.style.marginTop='10px';
    const input=document.createElement('input');input.id='deckQty';input.type='number';input.min='0';input.step='1';input.value=deck.value||'0';
    const syncLimit=()=>{const profile=resolveProfile(num(el('pL')?.value,1200),num(el('pW')?.value,800));if(profile.deckMax>0)input.max=String(profile.deckMax);};
    input.addEventListener('input',()=>{syncLimit();const max=num(input.max,99),value=clamp(Math.round(num(input.value,0)),0,max);input.value=String(value);deck.value=String(value);deck.dispatchEvent(new Event('input',{bubbles:true}));});
    deck.addEventListener('input',()=>{input.value=deck.value||'0';syncLimit();});
    el('pL')?.addEventListener('input',syncLimit);el('pW')?.addEventListener('input',syncLimit);
    cell.append(label,input);syncLimit();
  }

  function setupAdminEmployeeDelete(){
    const usersBox=el('adminUsersList');
    if(!usersBox||usersBox.dataset.employeeDeleteReady==='1')return;
    usersBox.dataset.employeeDeleteReady='1';
    const decorate=()=>{
      if(typeof currentRole==='undefined'||currentRole!=='admin')return;
      usersBox.querySelectorAll('.adminUser').forEach(row=>{
        const roleSelect=row.querySelector('.adminRole');
        if(!roleSelect||roleSelect.disabled||roleSelect.value!=='employee'||row.querySelector('.adminDeleteEmployee'))return;
        const btn=document.createElement('button');
        btn.type='button';
        btn.className='adminDeleteEmployee';
        btn.textContent='Удалить';
        btn.style.cssText='min-height:36px;border:1px solid #e2b8b4;border-radius:9px;padding:7px 10px;background:#fff6f5;color:#8a2f28;font-weight:800;cursor:pointer;';
        btn.addEventListener('click',async()=>{
          const label=row.querySelector('.adminEmail')?.textContent?.trim()||'этого сотрудника';
          if(!confirm(`Удалить сотрудника ${label}? Доступ к аккаунту будет закрыт. Его прошлые расчёты останутся в истории.`))return;
          btn.disabled=true;btn.textContent='Удаление…';
          try{
            const {data,error}=await sb.functions.invoke('admin-delete-employee',{body:{user_id:roleSelect.dataset.user}});
            if(error||!data?.ok)throw new Error(data?.error||error?.message||'Не удалось удалить сотрудника');
            alert('Сотрудник удалён. Прошлые расчёты сохранены в истории.');
            if(typeof loadAdminData==='function')await loadAdminData();
          }catch(err){
            alert('Не удалось удалить сотрудника: '+(err?.message||'неизвестная ошибка'));
            btn.disabled=false;btn.textContent='Удалить';
          }
        });
        row.appendChild(btn);
      });
    };
    if(window.MutationObserver)new MutationObserver(()=>queueMicrotask(decorate)).observe(usersBox,{childList:true,subtree:true});
    decorate();
  }

  function setupPasswordRecovery(){
    const email=el('authEmail'),password=el('authPassword'),login=el('loginBtn'),signup=el('signupBtn'),authFields=el('authFields');
    if(!email||!password||!login||!authFields||el('forgotPasswordBtn')||!window.sb)return;
    const forgot=document.createElement('button');
    forgot.type='button';forgot.id='forgotPasswordBtn';forgot.textContent='Забыли пароль?';
    forgot.style.cssText='border:0;background:transparent;color:#4d6f96;font-size:11px;font-weight:800;cursor:pointer;margin:-6px 0 0 auto;padding:2px 0;';
    const passwordField=password.closest('.authField');
    passwordField?.appendChild(forgot);
    let recoveryMode=false;
    const showRecovery=()=>{
      recoveryMode=true;
      const card=el('authCard'),reg=el('authRegisterOnly');
      card?.classList.remove('loggedIn');
      if(authFields)authFields.style.display='grid';
      if(reg)reg.hidden=true;
      if(signup)signup.style.display='none';
      email.closest('.authField')?.setAttribute('hidden','');
      forgot.style.display='none';
      password.value='';password.placeholder='Новый пароль, минимум 6 символов';password.autocomplete='new-password';
      login.innerHTML='Сохранить новый пароль <span>→</span>';
      if(typeof setAuthMessage==='function')setAuthMessage('Введите новый пароль минимум из 6 символов.');
      setTimeout(()=>password.focus(),40);
    };
    forgot.addEventListener('click',async()=>{
      const address=email.value.trim();
      if(!address){if(typeof setAuthMessage==='function')setAuthMessage('Введите email, затем нажмите «Забыли пароль?».',true);email.focus();return;}
      forgot.disabled=true;forgot.textContent='Отправляем…';
      const {error}=await sb.auth.resetPasswordForEmail(address,{redirectTo:typeof SITE_URL!=='undefined'?SITE_URL:location.origin+location.pathname});
      forgot.disabled=false;forgot.textContent='Забыли пароль?';
      if(error){if(typeof setAuthMessage==='function')setAuthMessage('Не удалось отправить письмо: '+error.message,true);return;}
      if(typeof setAuthMessage==='function')setAuthMessage('Письмо для восстановления отправлено. Откройте ссылку из письма и задайте новый пароль.');
    });
    login.addEventListener('click',async e=>{
      if(!recoveryMode)return;
      e.preventDefault();e.stopImmediatePropagation();
      const next=password.value;
      if(next.length<6){if(typeof setAuthMessage==='function')setAuthMessage('Новый пароль должен содержать минимум 6 символов.',true);return;}
      login.disabled=true;
      const {error}=await sb.auth.updateUser({password:next});
      login.disabled=false;
      if(error){if(typeof setAuthMessage==='function')setAuthMessage('Не удалось изменить пароль: '+error.message,true);return;}
      if(typeof setAuthMessage==='function')setAuthMessage('Пароль изменён. Выполните вход с новым паролем.');
      await sb.auth.signOut();
      recoveryMode=false;
      email.closest('.authField')?.removeAttribute('hidden');
      forgot.style.display='';
      if(signup)signup.style.display='';
      password.value='';password.placeholder='Минимум 6 символов';password.autocomplete='current-password';
      login.innerHTML='Войти <span>→</span>';
    },true);
    sb.auth.onAuthStateChange((event)=>{if(event==='PASSWORD_RECOVERY')setTimeout(showRecovery,0);});
  }

  function updateSiteVersion(){
    const node=document.querySelector('.sideVersion');
    if(!node)return;
    const admin=typeof currentRole!=='undefined'&&currentRole==='admin';
    node.textContent=admin?'Pallet Tools · v1.0.4 · обновление №270':'Pallet Tools · v1.0.4';
  }
  window.updateSiteVersion=updateSiteVersion;
  const adminVersionTarget=el('adminSideNav');
  if(adminVersionTarget&&window.MutationObserver){
    new MutationObserver(updateSiteVersion).observe(adminVersionTarget,{attributes:true,attributeFilter:['hidden','style']});
  }

  window.renderDynamicPallet=render;
  window.rerenderPallet3D=function(){
    const sig=currentSignature();
    if(active&&active.signature===sig&&active.mode===(state.mode||'3d')&&document.querySelector('.palletReferenceHost canvas')){active.draw();return;}
    render(num(el('pL')?.value),num(el('pW')?.value));
  };
  setupDeckCountControl();
  setupAdminEmployeeDelete();
  setupPasswordRecovery();
  updateSiteVersion();
  setTimeout(()=>render(num(el('pL')?.value),num(el('pW')?.value)),120);
  window.addEventListener('resize',()=>{clearTimeout(resizeTimer);resizeTimer=setTimeout(()=>window.rerenderPallet3D?.(),160);});
})();
