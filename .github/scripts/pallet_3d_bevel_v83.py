from pathlib import Path
p=Path('index.html')
s=p.read_text(encoding='utf-8')
if 'pallet3dBevelV83' in s: raise SystemExit('already installed')
start=s.find('/* pallet3dWebGLV8 */')
if start<0: raise SystemExit('webgl block missing')
old="""     function mat(kind,idx){const active=selected==='all'||selected===kind;const m=new THREE.MeshStandardMaterial({map:tex[kind],color:active?baseMat[kind]:0xb8b0a5,roughness:.72,metalness:0,transparent:!active,opacity:active?1:.16,emissive:selected===kind?0x143e2f:0x000000,emissiveIntensity:selected===kind?.16:0});m.map=tex[kind].clone();m.map.needsUpdate=true;m.map.offset.x=((idx*0.173)%1);return m;}\n     function addBox(kind,dims,pos,idx,nails){\n       const g=new THREE.BoxGeometry(dims.x,dims.y,dims.z,1,1,1);const mesh=new THREE.Mesh(g,mat(kind,idx));mesh.position.set(pos.x,pos.y,pos.z);mesh.castShadow=true;mesh.receiveShadow=true;world.add(mesh);"""
new="""     function mat(kind,idx){const active=selected==='all'||selected===kind;const m=new THREE.MeshStandardMaterial({map:tex[kind],color:active?baseMat[kind]:0xb8b0a5,roughness:.72,metalness:0,transparent:!active,opacity:active?1:.16,depthWrite:active,emissive:selected===kind?0x143e2f:0x000000,emissiveIntensity:selected===kind?.16:0});m.map=tex[kind].clone();m.map.needsUpdate=true;m.map.offset.x=((idx*0.173)%1);return m;}\n     /* pallet3dBevelV83 */\n     function bevelBoxGeometry(dims,kind){\n       const bx=Math.max(.006,Math.min(kind==='block'?.055:.035,dims.y*.16,dims.z*.09,dims.x*.025));\n       const sh=new THREE.Shape();sh.moveTo(-dims.x/2,-dims.z/2);sh.lineTo(dims.x/2,-dims.z/2);sh.lineTo(dims.x/2,dims.z/2);sh.lineTo(-dims.x/2,dims.z/2);sh.closePath();\n       const g=new THREE.ExtrudeGeometry(sh,{depth:dims.y,steps:1,bevelEnabled:true,bevelThickness:bx,bevelSize:bx,bevelSegments:1,curveSegments:1});g.center();g.rotateX(Math.PI/2);g.computeVertexNormals();return g;\n     }\n     function addBox(kind,dims,pos,idx,nails){\n       const g=bevelBoxGeometry(dims,kind);const mesh=new THREE.Mesh(g,mat(kind,idx));mesh.position.set(pos.x,pos.y,pos.z);mesh.castShadow=true;mesh.receiveShadow=true;world.add(mesh);"""
if old not in s[start:]: raise SystemExit('material/box block not found')
s=s.replace(old,new,1)
old2="""     active3D={renderer,scene,camera,exploded,mode:pallet3DState.mode};"""
new2="""     Object.values(tex).forEach(t=>t.dispose());\n     active3D={renderer,scene,camera,exploded,mode:pallet3DState.mode};"""
if old2 not in s[start:]: raise SystemExit('active scene marker not found')
s=s.replace(old2,new2,1)
css='''\n/* pallet3dBevelV83 */\n.palletWebGLBadge::before{content:"◆";font-size:7px;margin-right:5px;opacity:.75}\n'''
pos=s.rfind('</style>')
s=s[:pos]+css+s[pos:]
p.write_text(s,encoding='utf-8')
print('pallet3dBevelV83 installed')
