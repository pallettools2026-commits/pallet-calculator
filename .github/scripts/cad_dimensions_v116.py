from pathlib import Path

js_path = Path('assets/pallet3d-v10.js')
css_path = Path('assets/theme-industrial-v130.css')
html_path = Path('index.html')

js = js_path.read_text(encoding='utf-8')
start = js.index('    const projectMeasurePoint=')
end = js.index('    function draw(){', start)
new_measure_code = '''    const projectMeasurePoint=(x,y,z)=>{if(!stage||!renderer.domElement)return null;const v=new THREE.Vector3(x,y,z).project(camera);if(!Number.isFinite(v.x)||!Number.isFinite(v.y)||v.z<-1.1||v.z>1.1)return null;const cr=renderer.domElement.getBoundingClientRect(),sr=stage.getBoundingClientRect();return{x:cr.left-sr.left+(v.x*.5+.5)*cr.width,y:cr.top-sr.top+(-v.y*.5+.5)*cr.height};};
    const overlay=root.querySelector('.palletOnModelMeasures');
    const measureMarks={};
    const ensureMeasure=(name,kind='normal')=>{let mark=measureMarks[name];if(mark)return mark;mark=document.createElement('div');mark.className=`palletMeasureMark ${kind}`;mark.innerHTML='<i class="measureLine"></i><em class="measureTick tickA"></em><em class="measureTick tickB"></em><span></span>';overlay?.appendChild(mark);measureMarks[name]=mark;return mark;};
    const clearMeasures=()=>Object.values(measureMarks).forEach(mark=>mark.style.display='none');
    const paintMeasure=(name,a,b,text,opts={})=>{const mark=ensureMeasure(name,opts.kind||'normal');const p1=projectMeasurePoint(a[0],a[1],a[2]),p2=projectMeasurePoint(b[0],b[1],b[2]);if(!p1||!p2){mark.style.display='none';return;}const dx=p2.x-p1.x,dy=p2.y-p1.y,dist=Math.hypot(dx,dy);if(dist<(opts.minPx||4)){mark.style.display='none';return;}const angle=Math.atan2(dy,dx)*180/Math.PI,mx=(p1.x+p2.x)/2,my=(p1.y+p2.y)/2,line=mark.querySelector('.measureLine'),tickA=mark.querySelector('.tickA'),tickB=mark.querySelector('.tickB'),label=mark.querySelector('span');mark.style.display='block';mark.classList.toggle('bad',!!opts.bad);mark.classList.toggle('major',!!opts.major);mark.classList.toggle('compact',!!opts.compact);if(line){line.style.left=`${p1.x}px`;line.style.top=`${p1.y}px`;line.style.width=`${dist}px`;line.style.transform=`rotate(${angle}deg)`;}[[tickA,p1],[tickB,p2]].forEach(([tick,p])=>{if(!tick)return;tick.style.left=`${p.x}px`;tick.style.top=`${p.y}px`;tick.style.transform=`translate(-50%,-50%) rotate(${angle+90}deg)`;});if(label){label.textContent=text;label.style.left=`${mx+(opts.labelDx||0)}px`;label.style.top=`${my+(opts.labelDy||0)}px`;}return mark;};
    const updateOnModelMeasures=()=>{
      clearMeasures();
      if(!topXs.length)return;
      const deckOffset=groups.deck.position.y;
      const topSurface=topY+deckT/2+deckOffset+.08;
      const frontZ=Math.min(PL/2,deckL/2)+.08;
      const leftX=-PW/2,rightX=PW/2,frontOutsideZ=PL/2+.70,leftOutsideX=-PW/2-.72,rightOutsideX=PW/2+.72;
      const totalTop=runnerT+blockH+bindT+deckT;
      paintMeasure('overall-length',[leftOutsideX,.08,-PL/2],[leftOutsideX,.08,PL/2],`${fmtMm(profile.length)} мм`,{major:true,labelDx:-8});
      paintMeasure('overall-width',[leftX,.08,frontOutsideZ],[rightX,.08,frontOutsideZ],`${fmtMm(profile.width)} мм`,{major:true,labelDy:14});
      paintMeasure('overall-height',[rightOutsideX,0,PL*.36],[rightOutsideX,totalTop,PL*.36],`${fmtMm(totalTop/S)} мм`,{major:true,labelDx:28});
      const focusIndex=Math.floor((topXs.length-1)/2),focusX=topXs[focusIndex];
      paintMeasure('deck-length',[focusX,topSurface,-deckL/2],[focusX,topSurface,deckL/2],`${fmtMm(deckLengthMm)} мм`,{labelDx:22});
      topXs.forEach((x,i)=>{
        const boardFront=Math.min(deckL/2,PL/2)-.12;
        paintMeasure(`board-width-${i}`,[x-actualDeckW/2,topSurface,boardFront],[x+actualDeckW/2,topSurface,boardFront],fmtMm(deckWidthMm),{compact:true,kind:'board',labelDy:i%2?10:-10,minPx:7});
      });
      if(topXs.length>1){
        for(let i=0;i<topXs.length-1;i++){
          const a=topXs[i]+actualDeckW/2,b=topXs[i+1]-actualDeckW/2;
          paintMeasure(`gap-${i}`,[a,topSurface,frontZ+.28],[b,topSurface,frontZ+.28],gapBad?`−${fmtMm(Math.abs(rawGapMm))}`:fmtMm(rawGapMm),{compact:true,kind:'gap',bad:gapBad,labelDy:i%2?-11:11,minPx:5});
        }
      }
      const stackX=-PW/2-.28,stackZ=PL*.33;
      const y0=0,y1=runnerT,y2=runnerT+blockH,y3=runnerT+blockH+bindT,y4=totalTop;
      paintMeasure('layer-runner',[stackX,y0,stackZ],[stackX,y1,stackZ],fmtMm(runnerT/S),{compact:true,kind:'layer',labelDx:-24,minPx:5});
      paintMeasure('layer-block',[stackX,y1,stackZ],[stackX,y2,stackZ],fmtMm(blockH/S),{compact:true,kind:'layer',labelDx:-24,minPx:5});
      paintMeasure('layer-bind',[stackX,y2,stackZ],[stackX,y3,stackZ],fmtMm(bindT/S),{compact:true,kind:'layer',labelDx:-24,minPx:5});
      const deckBottom=topY-deckT/2+deckOffset,deckTop=topY+deckT/2+deckOffset;
      paintMeasure('layer-deck',[stackX,deckBottom,stackZ],[stackX,deckTop,stackZ],fmtMm(deckThicknessMm),{compact:true,kind:'layer',labelDx:-24,minPx:5});
    };
'''
js = js[:start] + new_measure_code + js[end:]
old_overlay = 'const dimensionOverlay=`<div class="palletOnModelMeasures" aria-label="Размеры настила на модели"><div class="palletMeasureMark length" data-measure="length"><i></i><span></span></div><div class="palletMeasureMark width" data-measure="width"><i></i><span></span></div><div class="palletMeasureMark thickness" data-measure="thickness"><i></i><span></span></div><div class="palletMeasureMark gap" data-measure="gap"><i></i><span></span></div></div>`;'
if old_overlay not in js:
    raise SystemExit('old dimension overlay not found')
js = js.replace(old_overlay, 'const dimensionOverlay=\'<div class="palletOnModelMeasures" aria-label="Полная размерная схема поддона"></div>\';', 1)
old_stage = "    const stage=root.querySelector('.palletReferenceStage'),measureMarks={};root.querySelectorAll('.palletMeasureMark').forEach(mark=>{measureMarks[mark.dataset.measure]=mark;});\n"
if old_stage not in js:
    raise SystemExit('old stage setup not found')
js = js.replace(old_stage, "    const stage=root.querySelector('.palletReferenceStage');\n", 1)
js_path.write_text(js, encoding='utf-8')

css = css_path.read_text(encoding='utf-8')
css += '''

/* Full CAD dimension scheme v1.1.6 */
.palletOnModelMeasures{position:absolute!important;inset:0!important;z-index:8!important;overflow:hidden!important;pointer-events:none!important;font-family:Inter,ui-sans-serif,system-ui,-apple-system,"Segoe UI",Arial,sans-serif}
.palletMeasureMark{--measure:#37699b;position:absolute!important;inset:0!important;display:none!important;color:#fff!important;font-variant-numeric:tabular-nums!important}
.palletMeasureMark[style*="display: block"]{display:block!important}
.palletMeasureMark .measureLine{position:absolute!important;height:2px!important;transform-origin:0 50%!important;background:var(--measure)!important;box-shadow:0 0 0 1px rgba(255,255,255,.28)!important;border-radius:2px!important}
.palletMeasureMark .measureTick{position:absolute!important;width:10px!important;height:2px!important;background:var(--measure)!important;display:block!important;border-radius:2px!important;box-shadow:0 0 0 1px rgba(255,255,255,.18)!important}
.palletMeasureMark span{position:absolute!important;transform:translate(-50%,-50%)!important;display:block!important;white-space:nowrap!important;padding:4px 7px!important;border-radius:5px!important;background:#1f2c3c!important;border:1px solid rgba(120,165,214,.55)!important;color:#fff!important;font-size:11px!important;line-height:1!important;font-weight:900!important;letter-spacing:.01em!important;box-shadow:0 2px 6px rgba(12,24,38,.30)!important;text-shadow:0 1px 1px rgba(0,0,0,.25)!important}
.palletMeasureMark.major .measureLine{height:2.5px!important}.palletMeasureMark.major .measureTick{width:14px!important;height:2.5px!important}.palletMeasureMark.major span{padding:6px 9px!important;font-size:13px!important;border-radius:6px!important;background:#172638!important}
.palletMeasureMark.compact .measureLine{height:1.5px!important}.palletMeasureMark.compact .measureTick{width:7px!important;height:1.5px!important}.palletMeasureMark.compact span{padding:3px 5px!important;font-size:9px!important;border-radius:4px!important}
.palletMeasureMark.board{--measure:#3f78b3!important}.palletMeasureMark.gap{--measure:#2877b8!important}.palletMeasureMark.gap span{background:#19364f!important}.palletMeasureMark.layer{--measure:#477fb5!important}.palletMeasureMark.bad{--measure:#c84238!important}.palletMeasureMark.bad span{background:#8e2f2a!important;border-color:#df7a72!important}
@media(max-width:620px){.palletMeasureMark span{font-size:9px!important;padding:3px 5px!important}.palletMeasureMark.major span{font-size:11px!important;padding:5px 7px!important}.palletMeasureMark.compact span{font-size:8px!important;padding:2px 4px!important}.palletMeasureMark .measureTick{width:8px!important}.palletMeasureMark.major .measureTick{width:11px!important}}
'''
if 'Pallet Tools · v1.1.5' not in css:
    raise SystemExit('version marker not found in css')
css = css.replace('Pallet Tools · v1.1.5', 'Pallet Tools · v1.1.6')
css = css.replace('Pallet Tools · v1.1.6 · обновление №339', 'Pallet Tools · v1.1.6 · обновление №340')
css_path.write_text(css, encoding='utf-8')

html = html_path.read_text(encoding='utf-8')
for old,new in [
    ('assets/theme-industrial-v130.css?v=153','assets/theme-industrial-v130.css?v=154'),
    ('assets/pallet3d-v10.js?v=149','assets/pallet3d-v10.js?v=150'),
    ('v1.1.5','v1.1.6'),
    ('обновление №339','обновление №340'),
]:
    html = html.replace(old,new)
html_path.write_text(html, encoding='utf-8')
