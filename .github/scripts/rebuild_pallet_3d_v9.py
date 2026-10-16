from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

marker = '/* pallet3dWebGLV8 */'
if marker not in s:
    raise SystemExit('old WebGL marker not found')

m = s.index(marker)
start = s.rfind('<script>', 0, m)
end = s.find('</script>', m)
if start < 0 or end < 0:
    raise SystemExit('old WebGL script boundaries not found')
end += len('</script>')

new_script = r'''<script>
/* pallet3dWebGLV9 */
(function(){
  const fallback = window.renderDynamicPallet;
  if (typeof fallback !== 'function') return;

  let active = null;
  let pitch = 0.48;
  let distance = 19;

  function clamp(v,a,b){ return Math.max(a, Math.min(b, v)); }
  function part(i){
    return typeof pallet3DPart === 'function'
      ? pallet3DPart(i)
      : {n:0,t:0,w:0,l:0,name:'Деталь',index:i};
  }
  function disposeActive(){
    if(!active) return;
    try{
      active.scene.traverse(o=>{
        if(o.geometry) o.geometry.dispose?.();
        const mats = o.material ? (Array.isArray(o.material)?o.material:[o.material]) : [];
        mats.forEach(m=>{ m.map?.dispose?.(); m.dispose?.(); });
      });
      active.renderer.dispose();
    }catch(_){ }
    active = null;
  }

  function makeLongTexture(base, grain, seed){
    const c=document.createElement('canvas'); c.width=512; c.height=160;
    const x=c.getContext('2d'); x.fillStyle=base; x.fillRect(0,0,c.width,c.height);
    let s=seed||1; const rnd=()=>{s=(s*9301+49297)%233280;return s/233280;};
    for(let i=0;i<42;i++){
      const y=rnd()*c.height, amp=1.5+rnd()*5, period=90+rnd()*180;
      x.beginPath();
      for(let px=0;px<=c.width;px+=7){
        const yy=y+Math.sin((px+i*11)/period*Math.PI*2)*amp+(rnd()-.5)*.9;
        px?x.lineTo(px,yy):x.moveTo(px,yy);
      }
      x.strokeStyle=grain; x.globalAlpha=.07+rnd()*.13; x.lineWidth=.7+rnd()*1.2; x.stroke();
    }
    for(let k=0;k<3;k++){
      const cx=55+rnd()*(c.width-110), cy=20+rnd()*(c.height-40), rx=4+rnd()*10, ry=2+rnd()*4;
      x.globalAlpha=.14; x.strokeStyle='#6f472c'; x.lineWidth=1.1;
      x.beginPath(); x.ellipse(cx,cy,rx,ry,0,0,Math.PI*2); x.stroke();
      x.beginPath(); x.ellipse(cx,cy,rx*.45,ry*.45,0,0,Math.PI*2); x.stroke();
    }
    x.globalAlpha=1;
    const t=new THREE.CanvasTexture(c); t.wrapS=t.wrapT=THREE.RepeatWrapping; t.colorSpace=THREE.SRGBColorSpace; t.anisotropy=4;
    return t;
  }

  function makeEndTexture(seed){
    const c=document.createElement('canvas'); c.width=220; c.height=220;
    const x=c.getContext('2d'); x.fillStyle='#c99762'; x.fillRect(0,0,c.width,c.height);
    let s=seed||77; const rnd=()=>{s=(s*9301+49297)%233280;return s/233280;};
    const cx=108+(rnd()-.5)*14, cy=108+(rnd()-.5)*14;
    for(let i=1;i<15;i++){
      x.beginPath();
      x.ellipse(cx,cy,7+i*6.5,5+i*5.7,(rnd()-.5)*.12,0,Math.PI*2);
      x.strokeStyle=i%3===0?'rgba(84,50,28,.28)':'rgba(105,65,35,.16)';
      x.lineWidth=.8+(i%3===0?.5:0); x.stroke();
    }
    const t=new THREE.CanvasTexture(c); t.colorSpace=THREE.SRGBColorSpace; t.anisotropy=4;
    return t;
  }

  function materialSet(kind, idx, dims, selected, longTex, endTex){
    const activeSel = selected==='all' || selected===kind;
    const colors={deck:0xe0b477,cross:0xd5a268,runner:0xc78f55,block:0xb9824d};
    const sideMap=longTex[kind].clone(); sideMap.needsUpdate=true; sideMap.repeat.set(Math.max(1.5,Math.max(dims.x,dims.z)/2.4),1);
    sideMap.offset.x=(idx*.137)%1;
    const endMap=endTex.clone(); endMap.needsUpdate=true; endMap.center.set(.5,.5); endMap.rotation=((idx%3)-1)*.045;
    const common={roughness:.78,metalness:0,transparent:!activeSel,opacity:activeSel?1:.13,depthWrite:activeSel};
    const side=()=>new THREE.MeshStandardMaterial({...common,map:sideMap,color:activeSel?colors[kind]:0xaaa59d,emissive:selected===kind?0x173f31:0x000000,emissiveIntensity:selected===kind?.10:0});
    const top=()=>new THREE.MeshStandardMaterial({...common,map:sideMap,color:activeSel?colors[kind]:0xaaa59d,emissive:selected===kind?0x173f31:0x000000,emissiveIntensity:selected===kind?.10:0});
    const end=()=>new THREE.MeshStandardMaterial({...common,map:endMap,color:activeSel?0xd19d66:0xaaa59d});
    const longX=dims.x>=dims.z;
    return longX ? [end(),end(),top(),side(),side(),side()] : [side(),side(),top(),side(),end(),end()];
  }

  function updateCamera(){
    if(!active) return;
    const az=(Number(pallet3DState?.angle)||-28)*Math.PI/180;
    const d=distance*(active.exploded?1.12:1);
    const cp=Math.cos(pitch), sp=Math.sin(pitch);
    active.camera.position.set(Math.cos(az)*d*cp, d*sp, Math.sin(az)*d*cp);
    active.camera.lookAt(0,active.targetY,0);
    active.renderer.render(active.scene,active.camera);
  }

  function renderWebGL(L,W){
    const root=document.getElementById('palletPreview3D'); if(!root) return;
    const mode=pallet3DState?.mode||'3d';
    if(!window.THREE || mode==='top' || mode==='side'){
      disposeActive(); fallback(L,W); return;
    }

    try{
      disposeActive();
      L=Math.max(300,Number(L)||1200); W=Math.max(300,Number(W)||800);
      const p=[0,1,2,3,4,5,6].map(part), deck=p[0], cross=[p[1],p[2]], runners=[p[3],p[4]], blocks=[p[5],p[6]];
      const counts={deck:deck.n,cross:cross.reduce((a,b)=>a+b.n,0),runner:runners.reduce((a,b)=>a+b.n,0),block:blocks.reduce((a,b)=>a+b.n,0)};
      const exploded=mode==='explode', selected=pallet3DState?.selected||'all';

      const toolbar=`<div class="pallet3dToolbar" role="tablist" aria-label="Режим просмотра">
        <button type="button" data-p3d-mode="3d" class="${mode==='3d'?'active':''}">3D</button>
        <button type="button" data-p3d-mode="top">Сверху</button>
        <button type="button" data-p3d-mode="side">Сбоку</button>
        <button type="button" data-p3d-mode="explode" class="${exploded?'active':''}">${exploded?'Собрать':'Разнести'}</button>
      </div>`;
      const chip=(kind,label,count,cls)=>`<button type="button" data-p3d-part="${kind}" class="palletPartChip ${selected===kind?'active':''}"><i class="${cls}"></i>${label} <b>${count}</b></button>`;
      root.innerHTML=`${toolbar}
        <div class="pallet3dDragSurface palletWebGLSurface palletV9Surface">
          <div class="palletWebGLTitle">${exploded?'Разнесённая конструкция':'Реалистичная 3D-модель'} · ${Math.round(L)} × ${Math.round(W)} мм</div>
          <div class="palletWebGLHost"></div>
          <div class="palletWebGLBadge">3D V9</div>
        </div>
        <div class="palletModelLegend palletLegendInteractive">${chip('deck','Настил',counts.deck,'deck')}${chip('cross','Поперечины',counts.cross,'cross')}${chip('runner','Лыжи',counts.runner,'runner')}${chip('block','Шашки',counts.block,'block')}</div>
        <div class="palletModelHint">Мышь/палец — вращение · колесо — масштаб</div>`;

      root.querySelectorAll('[data-p3d-mode]').forEach(btn=>btn.addEventListener('click',()=>{
        const next=btn.dataset.p3dMode; pallet3DState.mode=(next==='explode'&&mode==='explode')?'3d':next;
        renderWebGL(L,W);
      }));
      root.querySelectorAll('[data-p3d-part]').forEach(btn=>btn.addEventListener('click',()=>{
        const k=btn.dataset.p3dPart; pallet3DState.selected=(selected===k?'all':k); renderWebGL(L,W);
      }));

      const host=root.querySelector('.palletWebGLHost');
      const width=Math.max(300,host.clientWidth||720), height=window.innerWidth<620?380:470;
      const renderer=new THREE.WebGLRenderer({antialias:true,alpha:true,powerPreference:'high-performance'});
      renderer.setPixelRatio(Math.min(window.devicePixelRatio||1,2)); renderer.setSize(width,height,false);
      renderer.shadowMap.enabled=true; renderer.shadowMap.type=THREE.PCFSoftShadowMap;
      renderer.outputColorSpace=THREE.SRGBColorSpace; renderer.toneMapping=THREE.ACESFilmicToneMapping; renderer.toneMappingExposure=1.08;
      host.appendChild(renderer.domElement);

      const scene=new THREE.Scene(); scene.fog=new THREE.Fog(0xf4f1ea,25,42);
      const camera=new THREE.PerspectiveCamera(35,width/height,.1,100);
      const world=new THREE.Group(); scene.add(world);

      scene.add(new THREE.HemisphereLight(0xfffbf2,0x76695e,1.8));
      const key=new THREE.DirectionalLight(0xfff0d6,3.6); key.position.set(-8,14,7); key.castShadow=true; key.shadow.mapSize.set(2048,2048); key.shadow.camera.left=-14; key.shadow.camera.right=14; key.shadow.camera.top=14; key.shadow.camera.bottom=-14; scene.add(key);
      const fill=new THREE.DirectionalLight(0xdbe7ff,1.15); fill.position.set(10,8,-8); scene.add(fill);

      const scale=.01, SL=L*scale, SW=W*scale;
      const longTex={deck:makeLongTexture('#e8bf82','#86542f',11),cross:makeLongTexture('#ddb176','#7d4c2b',21),runner:makeLongTexture('#cf9a61','#70411f',31),block:makeLongTexture('#c28b53','#693c1e',41)};
      const endTex=makeEndTexture(77);

      const runnerParts=[]; runners.forEach(r=>{for(let i=0;i<Math.min(10,r.n);i++)runnerParts.push(r)});
      const crossParts=[]; cross.forEach(r=>{for(let i=0;i<Math.min(10,r.n);i++)crossParts.push(r)});
      const blockParts=[]; blocks.forEach(r=>{for(let i=0;i<Math.min(16,r.n);i++)blockParts.push(r)});

      const runnerH=runnerParts.length?Math.max(...runnerParts.map(x=>Math.max(15,x.t||0)))*scale:0;
      const blockH=blockParts.length?Math.max(...blockParts.map(x=>Math.max(55,x.t||0)))*scale:0;
      const crossH=crossParts.length?Math.max(...crossParts.map(x=>Math.max(15,x.t||0)))*scale:0;
      const deckH=deck.n?Math.max(15,deck.t||0)*scale:0;

      const expRunner=0, expBlock=exploded?.85:0, expCross=exploded?1.75:0, expDeck=exploded?2.75:0;
      const runnerY=runnerH/2+expRunner;
      const blockY=runnerH+blockH/2+expBlock;
      const crossY=runnerH+blockH+crossH/2+expCross;
      const deckY=runnerH+blockH+crossH+deckH/2+expDeck;

      function distribute(count,span,item){
        if(count<=1) return [0];
        const usable=Math.max(0,span-item);
        return Array.from({length:count},(_,i)=>-usable/2+i*usable/(count-1));
      }
      function pick(arr,count,span){
        if(count<=1) return [arr.length?arr[Math.floor((arr.length-1)/2)]:0];
        if(arr.length>=count) return Array.from({length:count},(_,i)=>arr[Math.round(i*(arr.length-1)/(count-1))]);
        return Array.from({length:count},(_,i)=>-span/2+i*span/(count-1));
      }
      function addWood(kind,dims,pos,idx){
        const g=new THREE.BoxGeometry(dims.x,dims.y,dims.z);
        const mats=materialSet(kind,idx,dims,selected,longTex,endTex);
        const mesh=new THREE.Mesh(g,mats); mesh.position.set(pos.x,pos.y,pos.z); mesh.castShadow=true; mesh.receiveShadow=true; world.add(mesh);
        if(selected==='all'||selected===kind){
          const edges=new THREE.LineSegments(new THREE.EdgesGeometry(g),new THREE.LineBasicMaterial({color:0x6f4b31,transparent:true,opacity:.16}));
          edges.position.copy(mesh.position); world.add(edges);
        }
      }

      const nailGeo=new THREE.CylinderGeometry(.027,.027,.015,12);
      const nailMat=new THREE.MeshStandardMaterial({color:0x4b4a47,roughness:.32,metalness:.48});
      function nail(x,y,z){ const n=new THREE.Mesh(nailGeo,nailMat); n.position.set(x,y,z); n.castShadow=true; world.add(n); }

      let runnerZ=[];
      if(runnerParts.length){
        const avg=runnerParts.reduce((a,r)=>a+Math.max(65,r.w||0),0)/runnerParts.length*scale;
        runnerZ=distribute(runnerParts.length,SW*.90,avg);
        runnerParts.forEach((r,i)=>addWood('runner',{x:clamp((r.l||L)*scale,SL*.35,SL),y:Math.max(.15,(r.t||22)*scale),z:Math.max(.35,(r.w||95)*scale)},{x:0,y:runnerY,z:runnerZ[i]},i));
      }

      let crossX=[];
      if(crossParts.length){
        const avg=crossParts.reduce((a,r)=>a+Math.max(65,r.w||0),0)/crossParts.length*scale;
        crossX=distribute(crossParts.length,SL*.90,avg);
        crossParts.forEach((r,i)=>addWood('cross',{x:Math.max(.35,(r.w||95)*scale),y:Math.max(.15,(r.t||22)*scale),z:clamp((r.l||W)*scale,SW*.50,SW)},{x:crossX[i],y:crossY,z:0},i));
      }

      if(blockParts.length){
        const desiredCols=Math.min(Math.max(1,crossX.length),4);
        const desiredRows=Math.min(Math.max(1,runnerZ.length),4);
        const xs=pick(crossX,desiredCols,SL*.72), zs=pick(runnerZ,desiredRows,SW*.68);
        const slots=[]; zs.forEach(z=>xs.forEach(x=>slots.push([x,z])));
        blockParts.forEach((b,i)=>{
          const slot=slots[Math.min(i,slots.length-1)]||[0,0];
          addWood('block',{x:Math.max(.55,(b.l||120)*scale),y:Math.max(.55,(b.t||75)*scale),z:Math.max(.55,(b.w||100)*scale)},{x:slot[0],y:blockY,z:slot[1]},i);
        });
      }

      if(deck.n>0){
        const cnt=Math.min(20,deck.n), bw=Math.max(.35,(deck.w||95)*scale), zs=distribute(cnt,SW*.94,bw);
        const nailXs=pick(crossX,Math.min(5,Math.max(1,crossX.length||3)),SL*.72);
        for(let i=0;i<cnt;i++){
          const boardL=clamp((deck.l||L)*scale,SL*.50,SL), z=zs[i];
          addWood('deck',{x:boardL,y:deckH,z:bw},{x:0,y:deckY,z},i);
          if(selected==='all'||selected==='deck'){
            nailXs.filter(nx=>Math.abs(nx)<boardL/2-.08).forEach(nx=>{
              const dz=Math.min(.09,bw*.22), ny=deckY+deckH/2+.012;
              nail(nx,ny,z-dz); nail(nx,ny,z+dz);
            });
          }
        }
      }

      if(crossParts.length && runnerZ.length && (selected==='all'||selected==='cross')){
        const visibleX=pick(crossX,Math.min(4,crossX.length),SL*.72);
        visibleX.forEach(x=>runnerZ.forEach(z=>{
          if(Math.abs(z)<SW*.48){ const ny=crossY+crossH/2+.011; nail(x-.06,ny,z); nail(x+.06,ny,z); }
        }));
      }

      const floor=new THREE.Mesh(new THREE.PlaneGeometry(30,24),new THREE.MeshStandardMaterial({color:0xf0ede6,roughness:1,metalness:0}));
      floor.rotation.x=-Math.PI/2; floor.position.y=-.018; floor.receiveShadow=true; scene.add(floor);

      const totalH=runnerH+blockH+crossH+deckH+(exploded?2.75:0);
      distance=clamp(Math.max(SL,SW)*1.55,15,24); pitch=exploded?.55:.43;
      active={renderer,scene,camera,exploded,targetY:Math.max(.55,totalH*.42)};
      updateCamera();

      let dragging=false,lastX=0,lastY=0;
      const canvas=renderer.domElement;
      canvas.addEventListener('pointerdown',e=>{dragging=true;lastX=e.clientX;lastY=e.clientY;canvas.setPointerCapture?.(e.pointerId);});
      canvas.addEventListener('pointermove',e=>{
        if(!dragging)return;
        const dx=e.clientX-lastX,dy=e.clientY-lastY; lastX=e.clientX;lastY=e.clientY;
        pallet3DState.angle=(Number(pallet3DState.angle)||-28)+dx*.36; pitch=clamp(pitch-dy*.006,.20,1.05); updateCamera();
      });
      const stop=e=>{dragging=false;try{canvas.releasePointerCapture?.(e.pointerId)}catch(_){}};
      canvas.addEventListener('pointerup',stop); canvas.addEventListener('pointercancel',stop);
      canvas.addEventListener('wheel',e=>{e.preventDefault();distance=clamp(distance+e.deltaY*.012,10,30);updateCamera();},{passive:false});
      canvas.addEventListener('dblclick',()=>{pallet3DState.angle=-28;pitch=exploded?.55:.43;distance=clamp(Math.max(SL,SW)*1.55,15,24);updateCamera();});

      Object.values(longTex).forEach(t=>t.dispose()); endTex.dispose();
      if(document.getElementById('rotatePallet')) document.getElementById('rotatePallet').textContent='↻ Повернуть на 45°';
    }catch(err){
      console.warn('Pallet 3D V9 fallback',err); disposeActive(); fallback(L,W);
    }
  }

  window.renderDynamicPallet=renderWebGL;
  window.rerenderPallet3D=function(){
    if(active && (pallet3DState?.mode==='3d'||pallet3DState?.mode==='explode') && document.querySelector('.palletWebGLHost canvas')){ updateCamera(); return; }
    renderWebGL(Number(document.getElementById('pL')?.value),Number(document.getElementById('pW')?.value));
  };
  setTimeout(()=>window.rerenderPallet3D(),160);
  let rt; window.addEventListener('resize',()=>{clearTimeout(rt);rt=setTimeout(()=>renderWebGL(Number(document.getElementById('pL')?.value),Number(document.getElementById('pW')?.value)),180);});
})();
</script>'''

s = s[:start] + new_script + s[end:]

css = r'''
/* pallet3dWebGLV9 */
.palletV9Surface{background:radial-gradient(circle at 50% 18%,#fff 0,#faf8f3 42%,#ece8df 100%)!important}
.palletV9Surface .palletWebGLHost canvas{filter:saturate(.98) contrast(1.015)}
.palletModelLegend{align-items:center;justify-content:center;gap:8px;flex-wrap:wrap!important}
.palletPartChip{white-space:nowrap}
@media(max-width:620px){.palletModelLegend{display:grid!important;grid-template-columns:repeat(2,minmax(0,1fr));width:100%}.palletPartChip{width:100%;justify-content:center}.palletV9Surface{min-height:410px!important}.palletV9Surface .palletWebGLHost{height:380px!important}}
'''
pos = s.rfind('</style>')
if pos < 0:
    raise SystemExit('style close not found')
s = s[:pos] + css + s[pos:]

p.write_text(s, encoding='utf-8')
print('pallet3dWebGLV9 installed')
