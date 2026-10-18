from pathlib import Path
import subprocess

EXPECTED_BASE = "5987c5390b529fe8b22324ed902bbf5a0cb96583"

def run(*args):
    print("+", " ".join(args), flush=True)
    subprocess.run(args, check=True)

def replace_once(text, old, new, label):
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected exactly one match, found {count}")
    return text.replace(old, new, 1)

run("git", "config", "user.name", "github-actions[bot]")
run("git", "config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com")
run("git", "fetch", "origin", "main")
head = subprocess.check_output(["git", "rev-parse", "origin/main"], text=True).strip()
if head != EXPECTED_BASE:
    raise RuntimeError(f"main moved: expected {EXPECTED_BASE}, got {head}")
run("git", "checkout", "-B", "main", "origin/main")

js_path = Path("assets/pallet3d-v10.js")
css_path = Path("assets/theme-industrial-v130.css")
html_path = Path("index.html")
js = js_path.read_text(encoding="utf-8")
css = css_path.read_text(encoding="utf-8")
html = html_path.read_text(encoding="utf-8")

old_measure = """    const gapText=deckCount>1?`${fmtMm(Math.max(0,rawGapMm))} мм`:'—';
    const fitNote=gapBad?`Не хватает ${fmtMm(Math.abs(remainingMm))} мм по ширине`:`Остаток ${fmtMm(Math.max(0,remainingMm))} мм`;
    const dimensionHud=`<div class="palletDimensionHud" aria-label="Размеры настила"><div class="palletMeasure deck"><span>Доска настила</span><strong>${fmtMm(deckThicknessMm)} × ${fmtMm(deckWidthMm)} × ${fmtMm(deckLengthMm)} мм</strong><small>толщина × ширина × длина</small></div><div class="palletMeasure gap ${gapBad?'bad':''}"><span>Между досками</span><strong>${gapText}</strong><small>${deckCount} шт. · ${fitNote}</small></div></div>`;
"""
new_measure = """    const gapText=deckCount>1?(gapBad?`−${fmtMm(Math.abs(rawGapMm))} мм`:`${fmtMm(rawGapMm)} мм`):'—';
    const dimensionOverlay=`<div class="palletOnModelMeasures" aria-label="Размеры настила на модели"><div class="palletMeasureMark length" data-measure="length"><i></i><span></span></div><div class="palletMeasureMark width" data-measure="width"><i></i><span></span></div><div class="palletMeasureMark thickness" data-measure="thickness"><i></i><span></span></div><div class="palletMeasureMark gap" data-measure="gap"><i></i><span></span></div></div>`;
"""
js = replace_once(js, old_measure, new_measure, "dimension overlay block")
js = replace_once(js, "${dimensionHud}</div>`;", "${dimensionOverlay}</div>`;", "stage overlay markup")

old_host = """    const host=root.querySelector('.palletReferenceHost'),cw=Math.max(280,host.clientWidth||760),ch=window.innerWidth<620?390:510;
"""
new_host = """    const host=root.querySelector('.palletReferenceHost'),cw=Math.max(280,host.clientWidth||760),ch=window.innerWidth<620?390:510;
    const stage=root.querySelector('.palletReferenceStage'),measureMarks={};root.querySelectorAll('.palletMeasureMark').forEach(mark=>{measureMarks[mark.dataset.measure]=mark;});
"""
js = replace_once(js, old_host, new_host, "measure overlay handles")

old_draw = """    const exploded=mode==='explode',offsets={runner:0,block:exploded?1.25:0,cross:exploded?2.55:0,deck:exploded?3.85:0};let yaw=num(state.angle,-34)*Math.PI/180,pitch=.43,distance=clamp(Math.max(PW,PL)*1.68,15,28);
    function draw(){if(mode==='top'){camera.up.set(0,0,-1);camera.position.set(0,Math.max(PW,PL)*2.0,.001);camera.lookAt(0,topY*.55,0);}else if(mode==='side'){camera.up.set(0,1,0);camera.position.set(Math.max(PW,PL)*2.0,Math.max(4.2,topY*2.0),0);camera.lookAt(0,topY*.55,0);}else{camera.up.set(0,1,0);const cy=Math.sin(pitch)*distance,rad=Math.cos(pitch)*distance;camera.position.set(Math.cos(yaw)*rad,cy+2.0,Math.sin(yaw)*rad);camera.lookAt(0,exploded?3.1:topY*.42,0);}renderer.render(scene,camera);}
"""
new_draw = """    const exploded=mode==='explode',offsets={runner:0,block:exploded?1.25:0,cross:exploded?2.55:0,deck:exploded?3.85:0};let yaw=num(state.angle,-34)*Math.PI/180,pitch=.43,distance=clamp(Math.max(PW,PL)*1.68,15,28);
    const projectMeasurePoint=(x,y,z)=>{if(!stage||!renderer.domElement)return null;const v=new THREE.Vector3(x,y,z).project(camera);if(!Number.isFinite(v.x)||!Number.isFinite(v.y)||v.z<-1.1||v.z>1.1)return null;const cr=renderer.domElement.getBoundingClientRect(),sr=stage.getBoundingClientRect();return{x:cr.left-sr.left+(v.x*.5+.5)*cr.width,y:cr.top-sr.top+(-v.y*.5+.5)*cr.height};};
    const hideMeasure=name=>{const mark=measureMarks[name];if(mark)mark.style.display='none';};
    const paintMeasure=(name,a,b,text,bad=false)=>{const mark=measureMarks[name];if(!mark)return;const p1=projectMeasurePoint(a[0],a[1],a[2]),p2=projectMeasurePoint(b[0],b[1],b[2]);if(!p1||!p2){mark.style.display='none';return;}const dx=p2.x-p1.x,dy=p2.y-p1.y,dist=Math.hypot(dx,dy);if(dist<2.5){mark.style.display='none';return;}const mx=(p1.x+p2.x)/2,my=(p1.y+p2.y)/2,angle=Math.atan2(dy,dx)*180/Math.PI,line=mark.querySelector('i'),label=mark.querySelector('span');mark.style.display='block';mark.style.left=`${mx}px`;mark.style.top=`${my}px`;if(line){line.style.width=`${dist}px`;line.style.transform=`translate(-50%,-50%) rotate(${angle}deg)`;}if(label)label.textContent=text;mark.classList.toggle('bad',!!bad);};
    const updateOnModelMeasures=()=>{if(!topXs.length){Object.keys(measureMarks).forEach(hideMeasure);return;}const deckOffset=groups.deck.position.y,topSurface=topY+deckT/2+deckOffset+.07,focusIndex=Math.floor((topXs.length-1)/2),boardX=topXs[focusIndex];paintMeasure('length',[boardX,topSurface,-deckL/2],[boardX,topSurface,deckL/2],`Длина ${fmtMm(deckLengthMm)} мм`);const widthZ=-deckL*.28;paintMeasure('width',[boardX-actualDeckW/2,topSurface,widthZ],[boardX+actualDeckW/2,topSurface,widthZ],`Ширина ${fmtMm(deckWidthMm)} мм`);const edgeX=boardX+actualDeckW/2+.04,thicknessZ=deckL*.34;paintMeasure('thickness',[edgeX,topY-deckT/2+deckOffset,thicknessZ],[edgeX,topY+deckT/2+deckOffset,thicknessZ],`Толщина ${fmtMm(deckThicknessMm)} мм`);if(topXs.length>1){const gi=Math.max(0,Math.min(topXs.length-2,Math.floor(topXs.length/2)-1)),left=topXs[gi]+actualDeckW/2,right=topXs[gi+1]-actualDeckW/2;paintMeasure('gap',[left,topSurface,deckL*.12],[right,topSurface,deckL*.12],`Зазор ${gapText}`,gapBad);}else hideMeasure('gap');};
    function draw(){if(mode==='top'){camera.up.set(0,0,-1);camera.position.set(0,Math.max(PW,PL)*2.0,.001);camera.lookAt(0,topY*.55,0);}else if(mode==='side'){camera.up.set(0,1,0);camera.position.set(Math.max(PW,PL)*2.0,Math.max(4.2,topY*2.0),0);camera.lookAt(0,topY*.55,0);}else{camera.up.set(0,1,0);const cy=Math.sin(pitch)*distance,rad=Math.cos(pitch)*distance;camera.position.set(Math.cos(yaw)*rad,cy+2.0,Math.sin(yaw)*rad);camera.lookAt(0,exploded?3.1:topY*.42,0);}renderer.render(scene,camera);updateOnModelMeasures();}
"""
js = replace_once(js, old_draw, new_draw, "projected dimensions")

js = replace_once(js, "Pallet Tools · v1.1.4 · обновление №338", "Pallet Tools · v1.1.5 · обновление №339", "js admin version")
js = replace_once(js, "Pallet Tools · v1.1.4';", "Pallet Tools · v1.1.5';", "js user version")

css = replace_once(css, 'content:"Pallet Tools · v1.1.4";', 'content:"Pallet Tools · v1.1.5";', "css user version")
css = replace_once(css, 'content:"Pallet Tools · v1.1.4 · обновление №338"', 'content:"Pallet Tools · v1.1.5 · обновление №339"', "css admin version")
css += r"""

/* 3D on-model dimensions v1.1.5 */
.palletDimensionHud{display:none!important}
.palletOnModelMeasures{position:absolute!important;inset:0!important;z-index:6!important;overflow:hidden!important;pointer-events:none!important}
.palletMeasureMark{--measure:#9a642f;position:absolute!important;width:0!important;height:0!important;display:none;color:#4e3e30}
.palletMeasureMark.gap{--measure:#287253;color:#245d47}
.palletMeasureMark.bad{--measure:#a3483f!important;color:#873c35!important}
.palletMeasureMark i{position:absolute!important;left:0!important;top:0!important;height:2px!important;background:var(--measure)!important;border-radius:2px!important;transform-origin:50% 50%!important;box-shadow:0 0 0 1px rgba(255,255,255,.75),0 1px 4px rgba(55,45,35,.16)!important}
.palletMeasureMark i:before,.palletMeasureMark i:after{content:"";position:absolute!important;top:50%!important;width:2px!important;height:10px!important;background:var(--measure)!important;border-radius:2px!important;transform:translateY(-50%)!important;box-shadow:0 0 0 1px rgba(255,255,255,.62)!important}
.palletMeasureMark i:before{left:0!important}.palletMeasureMark i:after{right:0!important}
.palletMeasureMark span{position:absolute!important;left:0!important;top:-10px!important;transform:translate(-50%,-100%)!important;display:block!important;white-space:nowrap!important;padding:4px 7px!important;border:1px solid rgba(151,105,60,.36)!important;border-radius:999px!important;background:rgba(255,252,247,.94)!important;box-shadow:0 3px 10px rgba(55,45,35,.12)!important;color:inherit!important;font-size:11px!important;line-height:1.15!important;font-weight:900!important;letter-spacing:.01em!important}
.palletMeasureMark.gap span{border-color:rgba(40,114,83,.34)!important;background:rgba(240,249,244,.96)!important}
.palletMeasureMark.bad span{border-color:rgba(163,72,63,.4)!important;background:rgba(255,243,241,.97)!important}
.palletMeasureMark.width span{top:10px!important;transform:translate(-50%,0)!important}
.palletMeasureMark.thickness span{left:10px!important;top:0!important;transform:translate(0,-50%)!important}
@media(max-width:620px){.palletMeasureMark span{font-size:9.5px!important;padding:3px 5px!important}.palletMeasureMark i:before,.palletMeasureMark i:after{height:8px!important}.palletMeasureMark.thickness span{left:7px!important}}
"""

html = replace_once(html, "assets/theme-industrial-v130.css?v=152", "assets/theme-industrial-v130.css?v=153", "theme cache")
html = replace_once(html, "assets/pallet3d-v10.js?v=148", "assets/pallet3d-v10.js?v=149", "js cache")

js_path.write_text(js, encoding="utf-8")
css_path.write_text(css, encoding="utf-8")
html_path.write_text(html, encoding="utf-8")

run("node", "--check", str(js_path))
run("git", "diff", "--check")
if "palletOnModelMeasures" not in js or "updateOnModelMeasures" not in js:
    raise RuntimeError("on-model measures missing")
if "v1.1.5" not in js or "v1.1.5" not in css:
    raise RuntimeError("version bump missing")
run("git", "add", str(js_path), str(css_path), str(html_path))
run("git", "commit", "-m", "Place pallet dimensions on 3D model")
run("git", "push", "origin", "main")
