from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')
if 'pallet3dJoineryV84' in s:
    raise SystemExit('already installed')
if '/* pallet3dWebGLV8 */' not in s or '/* pallet3dBevelV83 */' not in s:
    raise SystemExit('required 3D markers missing')

# Add a dedicated end-grain texture generator before the WebGL renderer.
needle=""" function renderWebGL(L,W){"""
insert=r''' function endGrainTexture(seed){
   const c=document.createElement('canvas');c.width=220;c.height=220;const x=c.getContext('2d');
   x.fillStyle='#c9955e';x.fillRect(0,0,c.width,c.height);
   let s=seed||71;const rnd=()=>{s=(s*9301+49297)%233280;return s/233280;};
   const cx=c.width*(.45+rnd()*.1),cy=c.height*(.45+rnd()*.1);
   x.lineWidth=1.4;
   for(let i=1;i<=13;i++){
     const rx=8+i*7.1+rnd()*3,ry=6+i*6.2+rnd()*3;
     x.beginPath();x.ellipse(cx,cy,rx,ry,(rnd()-.5)*.18,0,Math.PI*2);
     x.strokeStyle=i%3===0?'rgba(91,54,28,.30)':'rgba(116,72,38,.18)';x.stroke();
   }
   for(let i=0;i<11;i++){
     const a=rnd()*Math.PI*2,len=38+rnd()*62;x.beginPath();x.moveTo(cx,cy);x.lineTo(cx+Math.cos(a)*len,cy+Math.sin(a)*len);x.strokeStyle='rgba(95,58,32,.12)';x.lineWidth=.7+rnd()*.8;x.stroke();
   }
   const t=new THREE.CanvasTexture(c);t.wrapS=t.wrapT=THREE.ClampToEdgeWrapping;t.colorSpace=THREE.SRGBColorSpace;t.anisotropy=4;return t;
 }
 function renderWebGL(L,W){'''
if needle not in s:
    raise SystemExit('render marker not found')
s=s.replace(needle,insert,1)

# Create an end-grain base texture beside the longitudinal wood textures.
old="""     const tex={deck:woodTexture('#e8c087','#8f5a32',11),cross:woodTexture('#ddb078','#82502c',23),runner:woodTexture('#cf9a61','#744422',37),block:woodTexture('#c79158','#6d4021',53)};
     Object.values(tex).forEach(t=>{t.repeat.set(2.8,1);});"""
new="""     const tex={deck:woodTexture('#e8c087','#8f5a32',11),cross:woodTexture('#ddb078','#82502c',23),runner:woodTexture('#cf9a61','#744422',37),block:woodTexture('#c79158','#6d4021',53)};
     const endTex=endGrainTexture(71);
     Object.values(tex).forEach(t=>{t.repeat.set(2.8,1);});"""
if old not in s:
    raise SystemExit('wood texture block not found')
s=s.replace(old,new,1)

# Replace generic decorative nails with real end caps and joint-oriented nail helpers.
old=r'''     function addBox(kind,dims,pos,idx,nails){
       const g=bevelBoxGeometry(dims,kind);const mesh=new THREE.Mesh(g,mat(kind,idx));mesh.position.set(pos.x,pos.y,pos.z);mesh.castShadow=true;mesh.receiveShadow=true;world.add(mesh);
       const edgeOpacity=(selected==='all'||selected===kind)?.28:.05;const edges=new THREE.LineSegments(new THREE.EdgesGeometry(g,20),new THREE.LineBasicMaterial({color:0x6b4528,transparent:true,opacity:edgeOpacity}));edges.position.copy(mesh.position);world.add(edges);
       if(nails && (selected==='all'||selected===kind)){
         const nailMat=new THREE.MeshStandardMaterial({color:0x4f4c48,roughness:.38,metalness:.28});const ng=new THREE.CylinderGeometry(.027,.027,.016,12);const dx=dims.x*.34,dz=dims.z*.27;
         [[-dx,-dz],[dx,-dz],[-dx,dz],[dx,dz]].forEach(([nx,nz])=>{const n=new THREE.Mesh(ng,nailMat);n.position.set(pos.x+nx,pos.y+dims.y/2+.008,pos.z+nz);n.castShadow=true;world.add(n);});
       }
     }'''
new=r'''     /* pallet3dJoineryV84 */
     function endMaterial(kind,idx){
       const active=selected==='all'||selected===kind,m=new THREE.MeshStandardMaterial({map:endTex.clone(),color:active?0xd1a06b:0xb7afa5,roughness:.86,metalness:0,transparent:!active,opacity:active?.97:.15,depthWrite:active,side:THREE.DoubleSide});
       m.map.needsUpdate=true;m.map.rotation=((idx%3)-1)*.05;m.map.center.set(.5,.5);return m;
     }
     function addEndCaps(kind,dims,pos,idx){
       if(kind==='block')return;
       const longX=dims.x>=dims.z,matEnd=endMaterial(kind,idx),eps=.009;
       if(longX){
         [-1,1].forEach(sign=>{const g=new THREE.PlaneGeometry(Math.max(.06,dims.z*.92),Math.max(.05,dims.y*.82)),cap=new THREE.Mesh(g,matEnd);cap.rotation.y=Math.PI/2;cap.position.set(pos.x+sign*(dims.x/2+eps),pos.y,pos.z);cap.castShadow=false;world.add(cap);});
       }else{
         [-1,1].forEach(sign=>{const g=new THREE.PlaneGeometry(Math.max(.06,dims.x*.92),Math.max(.05,dims.y*.82)),cap=new THREE.Mesh(g,matEnd);cap.position.set(pos.x,pos.y,pos.z+sign*(dims.z/2+eps));cap.castShadow=false;world.add(cap);});
       }
     }
     const nailGeometry=new THREE.CylinderGeometry(.031,.031,.018,14);
     const nailMaterial=new THREE.MeshStandardMaterial({color:0x4a4a46,roughness:.34,metalness:.42});
     function addNail(x,y,z){const n=new THREE.Mesh(nailGeometry,nailMaterial);n.position.set(x,y,z);n.castShadow=true;world.add(n);}
     function addBox(kind,dims,pos,idx,nails){
       const g=bevelBoxGeometry(dims,kind);const mesh=new THREE.Mesh(g,mat(kind,idx));mesh.position.set(pos.x,pos.y,pos.z);mesh.castShadow=true;mesh.receiveShadow=true;world.add(mesh);
       const edgeOpacity=(selected==='all'||selected===kind)?.25:.045;const edges=new THREE.LineSegments(new THREE.EdgesGeometry(g,20),new THREE.LineBasicMaterial({color:0x6b4528,transparent:true,opacity:edgeOpacity}));edges.position.copy(mesh.position);world.add(edges);
       addEndCaps(kind,dims,pos,idx);
     }'''
if old not in s:
    raise SystemExit('addBox block not found')
s=s.replace(old,new,1)

# Rebuild supports so blocks sit on runner/cross intersections and nails line up with the cross supports.
old=r'''     if(runnerParts.length){const avgW=runnerParts.reduce((s,x)=>s+(x.w||98),0)/runnerParts.length*scale,zz=distribute(runnerParts.length,SW*.92,avgW);runnerParts.forEach((r,i)=>addBox('runner',{x:clamp((r.l||L)*scale,SL*.2,SL),y:Math.max(.12,(r.t||22)*scale),z:Math.max(.18,(r.w||98)*scale)},{x:0,y:runnerY,z:zz[i]},i,false));}
     if(blockParts.length){const cols=Math.min(3,blockParts.length),rows=Math.ceil(blockParts.length/cols);blockParts.forEach((b,i)=>{const col=i%cols,row=Math.floor(i/cols),bx=cols<=1?0:-SL*.38+col*(SL*.76/(cols-1)),bz=rows<=1?0:-SW*.34+row*(SW*.68/Math.max(1,rows-1));addBox('block',{x:Math.max(.55,(b.l||120)*scale),y:Math.max(.55,(b.t||75)*scale),z:Math.max(.55,(b.w||100)*scale)},{x:bx,y:blockY,z:bz},i,false);});}
     if(crossParts.length){const avgW=crossParts.reduce((s,x)=>s+(x.w||98),0)/crossParts.length*scale,xx=distribute(crossParts.length,SL*.92,avgW);crossParts.forEach((r,i)=>addBox('cross',{x:Math.max(.18,(r.w||98)*scale),y:Math.max(.12,(r.t||22)*scale),z:clamp((r.l||W)*scale,SW*.25,SW)},{x:xx[i],y:crossY,z:0},i,true));}
     if(deck.n>0){const cnt=Math.min(20,deck.n),bw=Math.max(.18,(deck.w||98)*scale),zz=distribute(cnt,SW*.94,bw);for(let i=0;i<cnt;i++)addBox('deck',{x:clamp((deck.l||L)*scale,SL*.25,SL),y:Math.max(.12,(deck.t||22)*scale),z:bw},{x:0,y:deckY,z:zz[i]},i,true);}'''
new=r'''     function pickPositions(arr,count,span){
       if(count<=1)return [arr.length?arr[Math.floor((arr.length-1)/2)]:0];
       if(arr.length>=count)return Array.from({length:count},(_,i)=>arr[Math.round(i*(arr.length-1)/(count-1))]);
       return Array.from({length:count},(_,i)=>-span/2+i*span/(count-1));
     }
     let runnerZs=[],crossXs=[];
     if(runnerParts.length){
       const avgW=runnerParts.reduce((s,x)=>s+(x.w||98),0)/runnerParts.length*scale;runnerZs=distribute(runnerParts.length,SW*.92,avgW);
       runnerParts.forEach((r,i)=>{const h=Math.max(.12,(r.t||22)*scale);addBox('runner',{x:clamp((r.l||L)*scale,SL*.2,SL),y:h,z:Math.max(.18,(r.w||98)*scale)},{x:0,y:h/2,z:runnerZs[i]},i,false);});
     }
     if(crossParts.length){
       const avgW=crossParts.reduce((s,x)=>s+(x.w||98),0)/crossParts.length*scale;crossXs=distribute(crossParts.length,SL*.92,avgW);
       crossParts.forEach((r,i)=>addBox('cross',{x:Math.max(.18,(r.w||98)*scale),y:Math.max(.12,(r.t||22)*scale),z:clamp((r.l||W)*scale,SW*.25,SW)},{x:crossXs[i],y:crossY,z:0},i,false));
     }
     if(blockParts.length){
       let cols=Math.min(4,Math.max(1,Math.ceil(Math.sqrt(blockParts.length*Math.max(.65,L/W))))),rows=Math.max(1,Math.ceil(blockParts.length/cols));
       if(rows>4){rows=4;cols=Math.ceil(blockParts.length/rows);}
       const supportX=pickPositions(crossXs,cols,SL*.76),supportZ=pickPositions(runnerZs,rows,SW*.70);
       blockParts.forEach((b,i)=>{const col=i%cols,row=Math.min(rows-1,Math.floor(i/cols)),bh=Math.max(.55,(b.t||75)*scale);addBox('block',{x:Math.max(.55,(b.l||120)*scale),y:bh,z:Math.max(.55,(b.w||100)*scale)},{x:supportX[col],y:maxRunnerT+bh/2+(exploded?1.25:0),z:supportZ[row]},i,false);});
     }
     if(deck.n>0){
       const cnt=Math.min(20,deck.n),bw=Math.max(.18,(deck.w||98)*scale),zz=distribute(cnt,SW*.94,bw),nailXs=pickPositions(crossXs,Math.min(3,Math.max(1,crossXs.length||3)),SL*.72);
       for(let i=0;i<cnt;i++){
         const boardL=clamp((deck.l||L)*scale,SL*.25,SL),zc=zz[i];addBox('deck',{x:boardL,y:Math.max(.12,(deck.t||22)*scale),z:bw},{x:0,y:deckY,z:zc},i,false);
         if(selected==='all'||selected==='deck')nailXs.filter(nx=>Math.abs(nx)<boardL/2-.07).forEach(nx=>{const dz=Math.min(.085,bw*.23),ny=deckY+deckH/2+.016;addNail(nx,ny,zc-dz);addNail(nx,ny,zc+dz);});
       }
     }'''
if old not in s:
    raise SystemExit('support placement block not found')
s=s.replace(old,new,1)

# Dispose the shared end texture after per-part clones have been created.
old="""     Object.values(tex).forEach(t=>t.dispose());"""
new="""     Object.values(tex).forEach(t=>t.dispose());endTex.dispose();"""
if old not in s:
    raise SystemExit('texture disposal marker not found')
s=s.replace(old,new,1)

css='''\n/* pallet3dJoineryV84 */\n.palletWebGLBadge{box-shadow:0 5px 18px rgba(54,43,31,.07)}\n'''
pos=s.rfind('</style>')
if pos<0: raise SystemExit('style close missing')
s=s[:pos]+css+s[pos:]
p.write_text(s,encoding='utf-8')
print('pallet3dJoineryV84 installed')
