from pathlib import Path
import re

src_path = Path('assets/truck-planner-v9.js')
out_path = Path('assets/truck-planner-v10.js')
html_path = Path('truck-planner.html')
js = src_path.read_text(encoding='utf-8')
html = html_path.read_text(encoding='utf-8')

old = "let S,scene,camera,renderer,controls,truckRoot,cargoRoot,curtainLeft,curtainRight,roofGroup,rearDoorLeft,rearDoorRight;\nlet doorsOpen=false,away=false,doorAnim=0,driveAnim=0;\nlet tractorTemplate=null,tractorLoading=false,tractorFailed=false;"
new = "let S,scene,camera,renderer,controls,truckRoot,cargoRoot,curtainLeft,curtainRight,roofGroup,rearDoorLeft,rearDoorRight;\nlet doorsOpen=false,away=false,doorAnim=0,driveAnim=0;\nlet tractorTemplate=null,tractorLoading=false,tractorFailed=false,currentTrailerFloorY=.94,calcTimer=0;"
assert old in js, 'state block not found'
js = js.replace(old, new, 1)

old = "function buildTractor(v){\n  if(!tractorTemplate){if(!tractorLoading&&!tractorFailed)requestTractor();return buildFallbackTractor(v);}"
new = "function buildTractor(v){\n  if(!tractorTemplate)return buildFallbackTractor(v);"
assert old in js, 'buildTractor block not found'
js = js.replace(old, new, 1)

old = "    tractorTemplate=gltf.scene;tractorLoading=false;\n    tractorTemplate.traverse(o=>{if(o.isMesh){o.castShadow=true;o.receiveShadow=true;}});\n    if(S)renderSceneTruck();"
new = "    tractorTemplate=gltf.scene;tractorLoading=false;\n    tractorTemplate.traverse(o=>{if(o.isMesh){o.castShadow=true;o.receiveShadow=true;o.userData.sharedAsset=true;}});\n    if(S)renderSceneTruck(true);"
assert old in js, 'tractor load block not found'
js = js.replace(old, new, 1)

old = """  widths.forEach((bw,i)=>{\n    const x=cursor+bw/2;\n    g.add(box(bw,deckH,L*.985,i%2?woodB:woodA,x,topY,0));\n    cursor+=bw+(i<widths.length-1?gap:0);\n  });\n  return g;\n}\n\nfunction makePalletPack(p,count,mode,altSeed=0){"""
new = """  widths.forEach((bw,i)=>{\n    const x=cursor+bw/2;\n    g.add(box(bw,deckH,L*.985,i%2?woodB:woodA,x,topY,0));\n    cursor+=bw+(i<widths.length-1?gap:0);\n  });\n  g.traverse(o=>{if(o.isMesh){o.castShadow=false;o.receiveShadow=true;}});\n  return g;\n}\n\nfunction makePalletLite(p,alt){\n  const g=new THREE.Group(),L=p.L/1000,W=p.W/1000,wood=alt?M.wood2:M.wood;\n  g.add(box(W*.98,.024,L*.98,wood,0,.132,0));\n  for(const x of [-W*.38,0,W*.38])g.add(box(Math.max(.075,W*.10),.096,L*.94,wood,x,.072,0));\n  g.add(box(W*.98,.024,L*.98,wood,0,.012,0));\n  g.traverse(o=>{if(o.isMesh){o.castShadow=false;o.receiveShadow=true;}});\n  return g;\n}\n\nfunction makePalletPack(p,count,mode,altSeed=0){"""
assert old in js, 'makePallet tail not found'
js = js.replace(old, new, 1)

old = "    const q=makePallet(p,p.H||144,(i+altSeed)%2===1);"
new = "    const alt=(i+altSeed)%2===1,q=S?.show>140?makePalletLite(p,alt):makePallet(p,p.H||144,alt);"
assert old in js, 'pack pallet creation not found'
js = js.replace(old, new, 1)

old = """function renderSceneTruck(){\n  if(truckRoot)scene.remove(truckRoot);if(cargoRoot)scene.remove(cargoRoot);truckRoot=new THREE.Group();const trailer=buildTrailer(S.v);truckRoot.add(trailer.group);truckRoot.add(buildTractor(S.v));scene.add(truckRoot);\n  cargoRoot=new THREE.Group();let remaining=S.show,packIndex=0;for(let layer=0;layer<S.layers&&remaining>0;layer++){for(let i=0;i<S.floor&&remaining>0;i++){const pos=S.pk.pos[i],inPack=Math.min(S.packQty,remaining),p=makePalletPack(S.p,inPack,S.packMode,packIndex);p.position.set(pos.x/1000,trailer.floorY+.08+layer*S.packH/1000,pos.z/1000);p.rotation.y=-pos.r;cargoRoot.add(p);remaining-=inPack;packIndex++;}}scene.add(cargoRoot);\n  const vis=E.curt.classList.contains('active');curtainLeft.visible=vis;curtainRight.visible=vis;roofGroup.visible=E.roof.classList.contains('active');const a=doorsOpen?Math.PI*.78:0;rearDoorLeft.rotation.y=-a;rearDoorRight.rotation.y=a;doorAnim=a;truckRoot.position.x=away?34:0;cargoRoot.position.x=truckRoot.position.x;driveAnim=truckRoot.position.x;resetView();\n}"""
new = """function disposeGenerated(root){\n  if(!root)return;\n  root.traverse(o=>{\n    if(!o.isMesh)return;\n    if(o.geometry&&!o.userData.sharedAsset)o.geometry.dispose();\n    if(o.userData.sharedAsset&&o.material){const mats=Array.isArray(o.material)?o.material:[o.material];mats.forEach(m=>m?.dispose?.());}\n  });\n}\n\nfunction renderSceneTruck(forceTruck=false){\n  const signature=`${S.v.L}|${S.v.W}|${S.v.H}|${tractorTemplate?'gltf':'fallback'}`;\n  const rebuild=forceTruck||!truckRoot||truckRoot.userData.signature!==signature;\n  if(rebuild){\n    if(truckRoot){scene.remove(truckRoot);disposeGenerated(truckRoot);}\n    truckRoot=new THREE.Group();const trailer=buildTrailer(S.v);currentTrailerFloorY=trailer.floorY;truckRoot.add(trailer.group);truckRoot.add(buildTractor(S.v));truckRoot.userData.signature=signature;scene.add(truckRoot);\n  }\n  if(cargoRoot){scene.remove(cargoRoot);disposeGenerated(cargoRoot);}\n  cargoRoot=new THREE.Group();let remaining=S.show,packIndex=0;for(let layer=0;layer<S.layers&&remaining>0;layer++){for(let i=0;i<S.floor&&remaining>0;i++){const pos=S.pk.pos[i],inPack=Math.min(S.packQty,remaining),p=makePalletPack(S.p,inPack,S.packMode,packIndex);p.position.set(pos.x/1000,currentTrailerFloorY+.08+layer*S.packH/1000,pos.z/1000);p.rotation.y=-pos.r;cargoRoot.add(p);remaining-=inPack;packIndex++;}}scene.add(cargoRoot);\n  const vis=E.curt.classList.contains('active');curtainLeft.visible=vis;curtainRight.visible=vis;roofGroup.visible=E.roof.classList.contains('active');const a=doorsOpen?Math.PI*.78:0;rearDoorLeft.rotation.y=-a;rearDoorRight.rotation.y=a;doorAnim=a;truckRoot.position.x=away?34:0;cargoRoot.position.x=truckRoot.position.x;driveAnim=truckRoot.position.x;if(rebuild)resetView();\n}"""
assert old in js, 'renderSceneTruck block not found'
js = js.replace(old, new, 1)

old = "renderer=new THREE.WebGLRenderer({antialias:true});renderer.setPixelRatio(Math.min(devicePixelRatio||1,2));renderer.shadowMap.enabled=true;"
new = "renderer=new THREE.WebGLRenderer({antialias:window.innerWidth>=900,powerPreference:'high-performance'});renderer.setPixelRatio(window.innerWidth<900?1:Math.min(devicePixelRatio||1,1.5));renderer.shadowMap.enabled=true;"
assert old in js, 'renderer setup not found'
js = js.replace(old, new, 1)

js = js.replace("key.shadow.mapSize.set(2048,2048);", "key.shadow.mapSize.set(1024,1024);", 1)

old = "}).observe(E.host);requestTractor();animate();"
new = "}).observe(E.host);const lazyLoad=()=>requestTractor();if('requestIdleCallback' in window)requestIdleCallback(lazyLoad,{timeout:900});else setTimeout(lazyLoad,350);animate();"
assert old in js, 'init tail not found'
js = js.replace(old, new, 1)

old = "function bind(){E.v.addEventListener('change',()=>{syncPresets();syncPackMode();calculate();});E.p.addEventListener('change',()=>{syncPresets();syncPackMode();calculate();});E.packMode?.addEventListener('change',()=>{syncPackMode();calculate();});[E.L,E.W,E.H,E.pay,E.pL,E.pW,E.loadH,E.pw,E.packQty,E.qty,E.gap,E.stack].filter(Boolean).forEach(el=>el.addEventListener('input',calculate));"
new = "function scheduleCalculate(){clearTimeout(calcTimer);calcTimer=setTimeout(calculate,120);}\nfunction bind(){E.v.addEventListener('change',()=>{syncPresets();syncPackMode();calculate();});E.p.addEventListener('change',()=>{syncPresets();syncPackMode();calculate();});E.packMode?.addEventListener('change',()=>{syncPackMode();calculate();});[E.L,E.W,E.H,E.pay,E.pL,E.pW,E.loadH,E.pw,E.packQty,E.qty,E.gap,E.stack].filter(Boolean).forEach(el=>el.addEventListener('input',scheduleCalculate));"
assert old in js, 'bind block not found'
js = js.replace(old, new, 1)

# Cache-bust and switch page to v10.
html, n = re.subn(r'assets/truck-planner-v9\.js\?v=[0-9-]+', 'assets/truck-planner-v10.js?v=20261018-2025', html, count=1)
assert n == 1, 'HTML v9 script reference not found'

out_path.write_text(js, encoding='utf-8')
html_path.write_text(html, encoding='utf-8')
print('v10 optimization patch written')
