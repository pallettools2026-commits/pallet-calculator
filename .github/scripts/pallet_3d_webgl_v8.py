from pathlib import Path

path=Path('index.html')
text=path.read_text(encoding='utf-8')
if 'pallet3dWebGLV8' in text:
    raise SystemExit('pallet3dWebGLV8 already installed')

three='<script src="https://cdn.jsdelivr.net/npm/three@0.170.0/build/three.min.js"></script>\n'
if three not in text:
    text=text.replace('</body>',three+'</body>',1)

script=r'''
<script>
/* pallet3dWebGLV8 */
(function(){
 const fallback=window.renderDynamicPallet;
 if(typeof fallback!=="function")return;
 function clamp(v,a,b){return Math.max(a,Math.min(b,v));}
 function part(i){return typeof pallet3DPart==='function'?pallet3DPart(i):{n:0,t:0,w:0,l:0,name:'Деталь',index:i};}
 function woodTexture(base,grain,seed){
   const c=document.createElement('canvas');c.width=512;c.height=160;const x=c.getContext('2d');x.fillStyle=base;x.fillRect(0,0,c.width,c.height);
   let s=seed||1;const rnd=()=>{s=(s*9301+49297)%233280;return s/233280;};
   x.lineWidth=1;
   for(let i=0;i<34;i++){
     const y=rnd()*c.height,amp=2+rnd()*7,period=80+rnd()*150;x.beginPath();
     for(let px=0;px<=c.width;px+=8){const yy=y+Math.sin((px+rnd()*8)/period*Math.PI*2)*amp+(rnd()-.5)*1.2;px?x.lineTo(px,yy):x.moveTo(px,yy);}x.strokeStyle=grain;x.globalAlpha=.10+rnd()*.13;x.stroke();
   }
   for(let k=0;k<4;k++){const cx=40+rnd()*(c.width-80),cy=18+rnd()*(c.height-36),rx=5+rnd()*11,ry=2+rnd()*5;x.globalAlpha=.16;x.strokeStyle='#6f4529';x.lineWidth=1.2;x.beginPath();x.ellipse(cx,cy,rx,ry,0,0,Math.PI*2);x.stroke();x.beginPath();x.ellipse(cx,cy,rx*.48,ry*.48,0,0,Math.PI*2);x.stroke();}
   x.globalAlpha=1;
   const t=new THREE.CanvasTexture(c);t.wrapS=t.wrapT=THREE.RepeatWrapping;t.colorSpace=THREE.SRGBColorSpace;t.anisotropy=4;return t;
 }
 function renderWebGL(L,W){
   const root=document.getElementById('palletPreview3D');if(!root)return;
   if(!window.THREE || pallet3DState.mode==='top' || pallet3DState.mode==='side'){fallback(L,W);return;}
   try{
     L=Math.max(300,Number(L)||1200);W=Math.max(300,Number(W)||800);
     const p=[0,1,2,3,4,5,6].map(part),deck=p[0],cross=[p[1],p[2]],runners=[p[3],p[4]],blocks=[p[5],p[6]];
     const counts={deck:deck.n,cross:cross.reduce((s,x)=>s+x.n,0),runner:runners.reduce((s,x)=>s+x.n,0),block:blocks.reduce((s,x)=>s+x.n,0)};
     const toolbar=`<div class="pallet3dToolbar" role="tablist" aria-label="Режим просмотра"><button type="button" data-p3d-mode="3d" class="${pallet3DState.mode==='3d'?'active':''}">3D</button><button type="button" data-p3d-mode="top">Сверху</button><button type="button" data-p3d-mode="side">Сбоку</button><button type="button" data-p3d-mode="explode" class="${pallet3DState.mode==='explode'?'active':''}">${pallet3DState.mode==='explode'?'Собрать':'Разнести'}</button></div>`;
     const chip=(kind,label,count,cls)=>`<button type="button" data-p3d-part="${kind}" class="palletPartChip ${pallet3DState.selected===kind?'active':''}"><i class="${cls}"></i>${label} <b>${count}</b></button>`;
     root.innerHTML=`${toolbar}<div class="pallet3dDragSurface palletWebGLSurface"><div class="palletWebGLTitle">${pallet3DState.mode==='explode'?'Разнесённая модель':'3D модель'} · ${Math.round(L)} × ${Math.round(W)} мм</div><div class="palletWebGLHost"></div><div class="palletWebGLBadge">REAL 3D</div></div><div class="palletModelLegend palletLegendInteractive">${chip('deck','Настил',counts.deck,'deck')}${chip('cross','Поперечины',counts.cross,'cross')}${chip('runner','Лыжи',counts.runner,'runner')}${chip('block','Шашки',counts.block,'block')}</div><div class="palletModelHint">Проведите пальцем или мышкой по модели, чтобы вращать на 360°</div>`;
     root.querySelectorAll('[data-p3d-mode]').forEach(btn=>btn.addEventListener('click',()=>{const next=btn.dataset.p3dMode;pallet3DState.mode=(next==='explode'&&pallet3DState.mode==='explode')?'3d':next;renderWebGL(L,W);}));
     root.querySelectorAll('[data-p3d-part]').forEach(btn=>btn.addEventListener('click',()=>{const k=btn.dataset.p3dPart;pallet3DState.selected=pallet3DState.selected===k?'all':k;renderWebGL(L,W);}));
     const host=root.querySelector('.palletWebGLHost'),width=Math.max(300,host.clientWidth||720),height=window.innerWidth<620?360:440;
     const renderer=new THREE.WebGLRenderer({antialias:true,alpha:true,powerPreference:'high-performance'});renderer.setPixelRatio(Math.min(window.devicePixelRatio||1,2));renderer.setSize(width,height,false);renderer.shadowMap.enabled=true;renderer.shadowMap.type=THREE.PCFSoftShadowMap;renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.05;host.appendChild(renderer.domElement);
     const scene=new THREE.Scene();scene.fog=new THREE.Fog(0xf5f3ee,26,48);
     const camera=new THREE.PerspectiveCamera(34,width/height,.1,100);const world=new THREE.Group();scene.add(world);
     const hemi=new THREE.HemisphereLight(0xfff9ee,0x827466,2.0);scene.add(hemi);
     const key=new THREE.DirectionalLight(0xfff3d9,4.3);key.position.set(-9,15,8);key.castShadow=true;key.shadow.mapSize.set(2048,2048);key.shadow.camera.near=.5;key.shadow.camera.far=45;key.shadow.camera.left=-14;key.shadow.camera.right=14;key.shadow.camera.top=14;key.shadow.camera.bottom=-14;scene.add(key);
     const fill=new THREE.DirectionalLight(0xdde9ff,1.45);fill.position.set(10,7,-10);scene.add(fill);
     const scale=0.01,SL=L*scale,SW=W*scale,exploded=pallet3DState.mode==='explode';
     const tex={deck:woodTexture('#e8c087','#8f5a32',11),cross:woodTexture('#ddb078','#82502c',23),runner:woodTexture('#cf9a61','#744422',37),block:woodTexture('#c79158','#6d4021',53)};
     Object.values(tex).forEach(t=>{t.repeat.set(2.8,1);});
     const baseMat={deck:0xe3b77b,cross:0xd6a46c,runner:0xc38e55,block:0xb9824b};
     const selected=pallet3DState.selected;
     function mat(kind,idx){const active=selected==='all'||selected===kind;const m=new THREE.MeshStandardMaterial({map:tex[kind],color:active?baseMat[kind]:0xb8b0a5,roughness:.72,metalness:0,transparent:!active,opacity:active?1:.16,emissive:selected===kind?0x143e2f:0x000000,emissiveIntensity:selected===kind?.16:0});m.map=tex[kind].clone();m.map.needsUpdate=true;m.map.offset.x=((idx*0.173)%1);return m;}
     function addBox(kind,dims,pos,idx,nails){
       const g=new THREE.BoxGeometry(dims.x,dims.y,dims.z,1,1,1);const mesh=new THREE.Mesh(g,mat(kind,idx));mesh.position.set(pos.x,pos.y,pos.z);mesh.castShadow=true;mesh.receiveShadow=true;world.add(mesh);
       const edgeOpacity=(selected==='all'||selected===kind)?.28:.05;const edges=new THREE.LineSegments(new THREE.EdgesGeometry(g,20),new THREE.LineBasicMaterial({color:0x6b4528,transparent:true,opacity:edgeOpacity}));edges.position.copy(mesh.position);world.add(edges);
       if(nails && (selected==='all'||selected===kind)){
         const nailMat=new THREE.MeshStandardMaterial({color:0x4f4c48,roughness:.38,metalness:.28});const ng=new THREE.CylinderGeometry(.027,.027,.016,12);const dx=dims.x*.34,dz=dims.z*.27;
         [[-dx,-dz],[dx,-dz],[-dx,dz],[dx,dz]].forEach(([nx,nz])=>{const n=new THREE.Mesh(ng,nailMat);n.position.set(pos.x+nx,pos.y+dims.y/2+.008,pos.z+nz);n.castShadow=true;world.add(n);});
       }
     }
     const runnerParts=[];runners.forEach(r=>{for(let i=0;i<Math.min(12,r.n);i++)runnerParts.push(r)});const crossParts=[];cross.forEach(r=>{for(let i=0;i<Math.min(12,r.n);i++)crossParts.push(r)});const blockParts=[];blocks.forEach(r=>{for(let i=0;i<Math.min(18,r.n);i++)blockParts.push(r)});
     const maxRunnerT=Math.max(18,...runners.map(x=>x.t||0))*scale,maxBlockT=Math.max(55,...blocks.map(x=>x.t||0))*scale,maxCrossT=Math.max(18,...cross.map(x=>x.t||0))*scale,deckT=Math.max(15,deck.t||0)*scale;
     const runnerY=maxRunnerT/2,blockY=maxRunnerT+maxBlockT/2+(exploded?1.25:0),crossY=maxRunnerT+maxBlockT+maxCrossT/2+(exploded?2.55:0),deckY=maxRunnerT+maxBlockT+maxCrossT+deckT/2+(exploded?3.95:0);
     const distribute=(count,span,item)=>count<=1?[0]:Array.from({length:count},(_,i)=>-span/2+item/2+i*(span-item)/(count-1));
     if(runnerParts.length){const avgW=runnerParts.reduce((s,x)=>s+(x.w||98),0)/runnerParts.length*scale,zz=distribute(runnerParts.length,SW*.92,avgW);runnerParts.forEach((r,i)=>addBox('runner',{x:clamp((r.l||L)*scale,SL*.2,SL),y:Math.max(.12,(r.t||22)*scale),z:Math.max(.18,(r.w||98)*scale)},{x:0,y:runnerY,z:zz[i]},i,false));}
     if(blockParts.length){const cols=Math.min(3,blockParts.length),rows=Math.ceil(blockParts.length/cols);blockParts.forEach((b,i)=>{const col=i%cols,row=Math.floor(i/cols),bx=cols<=1?0:-SL*.38+col*(SL*.76/(cols-1)),bz=rows<=1?0:-SW*.34+row*(SW*.68/Math.max(1,rows-1));addBox('block',{x:Math.max(.55,(b.l||120)*scale),y:Math.max(.55,(b.t||75)*scale),z:Math.max(.55,(b.w||100)*scale)},{x:bx,y:blockY,z:bz},i,false);});}
     if(crossParts.length){const avgW=crossParts.reduce((s,x)=>s+(x.w||98),0)/crossParts.length*scale,xx=distribute(crossParts.length,SL*.92,avgW);crossParts.forEach((r,i)=>addBox('cross',{x:Math.max(.18,(r.w||98)*scale),y:Math.max(.12,(r.t||22)*scale),z:clamp((r.l||W)*scale,SW*.25,SW)},{x:xx[i],y:crossY,z:0},i,true));}
     if(deck.n>0){const cnt=Math.min(20,deck.n),bw=Math.max(.18,(deck.w||98)*scale),zz=distribute(cnt,SW*.94,bw);for(let i=0;i<cnt;i++)addBox('deck',{x:clamp((deck.l||L)*scale,SL*.25,SL),y:Math.max(.12,(deck.t||22)*scale),z:bw},{x:0,y:deckY,z:zz[i]},i,true);}
     const floor=new THREE.Mesh(new THREE.PlaneGeometry(28,22),new THREE.MeshStandardMaterial({color:0xf1eee7,roughness:1,metalness:0}));floor.rotation.x=-Math.PI/2;floor.position.y=-.025;floor.receiveShadow=true;scene.add(floor);
     const a=(Number(pallet3DState.angle)||-28)*Math.PI/180,dist=exploded?22:19,camY=exploded?11.5:8.8,targetY=exploded?3.1:1.1;camera.position.set(Math.cos(a)*dist,camY,Math.sin(a)*dist);camera.lookAt(0,targetY,0);
     renderer.render(scene,camera);
     if(document.getElementById('rotatePallet'))document.getElementById('rotatePallet').textContent='↻ Повернуть на 45°';
   }catch(err){console.warn('WebGL pallet fallback',err);fallback(L,W);}
 }
 window.renderDynamicPallet=renderWebGL;
 window.rerenderPallet3D=function(){renderWebGL(Number(document.getElementById('pL')?.value),Number(document.getElementById('pW')?.value));};
 setTimeout(()=>window.rerenderPallet3D(),120);
 let rt;window.addEventListener('resize',()=>{clearTimeout(rt);rt=setTimeout(()=>{if(pallet3DState.mode==='3d'||pallet3DState.mode==='explode')window.rerenderPallet3D();},180);});
})();
</script>
'''
text=text.replace('</body>',script+'\n</body>',1)

css=r'''
/* pallet3dWebGLV8 */
.palletWebGLSurface{position:relative;min-height:470px;overflow:hidden!important;background:radial-gradient(circle at 50% 22%,#fff 0,#f8f6f1 45%,#ece9e2 100%)!important;border:1px solid rgba(111,91,64,.09);box-shadow:inset 0 1px 0 rgba(255,255,255,.9),0 14px 34px rgba(54,43,31,.08)}
.palletWebGLHost{width:100%;height:440px;position:relative}
.palletWebGLHost canvas{display:block;width:100%!important;height:100%!important;touch-action:none;cursor:grab}
.isDragging .palletWebGLHost canvas{cursor:grabbing}
.palletWebGLTitle{position:absolute;z-index:3;top:16px;left:50%;transform:translateX(-50%);font-weight:800;color:#274d40;font-size:13px;letter-spacing:.02em;white-space:nowrap;pointer-events:none;text-shadow:0 1px 0 #fff}
.palletWebGLBadge{position:absolute;right:14px;bottom:12px;z-index:3;font-size:9px;letter-spacing:.12em;font-weight:900;color:#176b50;background:rgba(255,255,255,.82);backdrop-filter:blur(6px);border:1px solid rgba(23,107,80,.16);border-radius:999px;padding:6px 9px;pointer-events:none}
.previewStage.zoomed .palletWebGLSurface{min-height:560px}.previewStage.zoomed .palletWebGLHost{height:530px}
@media(max-width:620px){.palletWebGLSurface{min-height:390px}.palletWebGLHost{height:360px}.palletWebGLTitle{font-size:11px;top:12px}.palletWebGLBadge{right:9px;bottom:8px}.previewStage.zoomed .palletWebGLSurface{min-height:455px}.previewStage.zoomed .palletWebGLHost{height:425px}}
'''
style_end=text.rfind('</style>')
if style_end<0: raise SystemExit('style end not found')
text=text[:style_end]+css+'\n'+text[style_end:]
path.write_text(text,encoding='utf-8')
print('pallet3dWebGLV8 installed')
