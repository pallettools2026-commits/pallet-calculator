from pathlib import Path
p=Path('index.html')
s=p.read_text(encoding='utf-8')
if 'pallet3dWebGLPerfV81' in s: raise SystemExit('already installed')
marker='/* pallet3dWebGLV8 */'
if marker not in s: raise SystemExit('WebGL V8 missing')
start=s.index(marker)

old='''(function(){\n const fallback=window.renderDynamicPallet;\n if(typeof fallback!=="function")return;'''
new='''(function(){\n const fallback=window.renderDynamicPallet;\n if(typeof fallback!=="function")return;\n /* pallet3dWebGLPerfV81 */\n let active3D=null;\n function disposeActive(){\n   if(!active3D)return;\n   try{active3D.scene.traverse(o=>{if(o.geometry)o.geometry.dispose?.();if(o.material){const ms=Array.isArray(o.material)?o.material:[o.material];ms.forEach(m=>{m.map?.dispose?.();m.dispose?.();});}});active3D.renderer.dispose();}catch(_){}\n   active3D=null;\n }\n function updateCameraOnly(){\n   if(!active3D)return false;\n   const a=(Number(pallet3DState.angle)||-28)*Math.PI/180,dist=active3D.exploded?22:19,camY=active3D.exploded?11.5:8.8,targetY=active3D.exploded?3.1:1.1;\n   active3D.camera.position.set(Math.cos(a)*dist,camY,Math.sin(a)*dist);active3D.camera.lookAt(0,targetY,0);active3D.renderer.render(active3D.scene,active3D.camera);return true;\n }'''
if old not in s[start:]: raise SystemExit('closure start not found')
s=s.replace(old,new,1)

old="""   if(!window.THREE || pallet3DState.mode==='top' || pallet3DState.mode==='side'){fallback(L,W);return;}"""
new="""   if(!window.THREE || pallet3DState.mode==='top' || pallet3DState.mode==='side'){disposeActive();fallback(L,W);return;}"""
s=s.replace(old,new,1)

needle="""     const chip=(kind,label,count,cls)=>`<button type=\"button\" data-p3d-part=\"${kind}\" class=\"palletPartChip ${pallet3DState.selected===kind?'active':''}\"><i class=\"${cls}\"></i>${label} <b>${count}</b></button>`;\n     root.innerHTML="""
repl="""     const chip=(kind,label,count,cls)=>`<button type=\"button\" data-p3d-part=\"${kind}\" class=\"palletPartChip ${pallet3DState.selected===kind?'active':''}\"><i class=\"${cls}\"></i>${label} <b>${count}</b></button>`;\n     disposeActive();\n     root.innerHTML="""
if needle not in s[start:]: raise SystemExit('root marker not found')
s=s.replace(needle,repl,1)

old="""     const a=(Number(pallet3DState.angle)||-28)*Math.PI/180,dist=exploded?22:19,camY=exploded?11.5:8.8,targetY=exploded?3.1:1.1;camera.position.set(Math.cos(a)*dist,camY,Math.sin(a)*dist);camera.lookAt(0,targetY,0);\n     renderer.render(scene,camera);"""
new="""     active3D={renderer,scene,camera,exploded,mode:pallet3DState.mode};\n     updateCameraOnly();"""
if old not in s[start:]: raise SystemExit('camera block not found')
s=s.replace(old,new,1)

old=""" window.rerenderPallet3D=function(){renderWebGL(Number(document.getElementById('pL')?.value),Number(document.getElementById('pW')?.value));};"""
new=""" window.rerenderPallet3D=function(){if(active3D&&active3D.mode===pallet3DState.mode&&document.querySelector('.palletWebGLHost canvas')){updateCameraOnly();return;}renderWebGL(Number(document.getElementById('pL')?.value),Number(document.getElementById('pW')?.value));};"""
if old not in s[start:]: raise SystemExit('rerender block not found')
s=s.replace(old,new,1)

old=""" let rt;window.addEventListener('resize',()=>{clearTimeout(rt);rt=setTimeout(()=>{if(pallet3DState.mode==='3d'||pallet3DState.mode==='explode')window.rerenderPallet3D();},180);});"""
new=""" let rt;window.addEventListener('resize',()=>{clearTimeout(rt);rt=setTimeout(()=>{if(pallet3DState.mode==='3d'||pallet3DState.mode==='explode')renderWebGL(Number(document.getElementById('pL')?.value),Number(document.getElementById('pW')?.value));},180);});"""
if old not in s[start:]: raise SystemExit('resize block not found')
s=s.replace(old,new,1)

p.write_text(s,encoding='utf-8')
print('pallet3dWebGLPerfV81 installed')
