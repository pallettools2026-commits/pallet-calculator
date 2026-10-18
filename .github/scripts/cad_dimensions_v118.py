from pathlib import Path
import re

js_path = Path('assets/pallet3d-v10.js')
css_path = Path('assets/theme-industrial-v130.css')
html_path = Path('index.html')

js = js_path.read_text(encoding='utf-8')
start = js.index('    const updateOnModelMeasures=()=>{')
end = js.index('    function draw(){', start)
new_block = r'''    const updateOnModelMeasures=()=>{
      clearMeasures();
      if(!topXs.length)return;
      const topView=mode==='top',sideView=mode==='side';
      const deckOffset=groups.deck.position.y;
      const topSurface=topY+deckT/2+deckOffset+.08;
      const leftX=-PW/2,rightX=PW/2,totalTop=runnerT+blockH+bindT+deckT;
      const leftOutsideX=-PW/2-(topView?.46:.72),rightOutsideX=PW/2+.72;
      const frontOutsideZ=PL/2+(topView?.58:.70);
      const showDeckLength=Math.abs(deckLengthMm-profile.length)>1;

      paintMeasure('overall-length',[leftOutsideX,.08,-PL/2],[leftOutsideX,.08,PL/2],`${fmtMm(profile.length)} мм`,{major:true,labelDx:topView?-4:-8});
      if(!sideView)paintMeasure('overall-width',[leftX,.08,frontOutsideZ],[rightX,.08,frontOutsideZ],`${fmtMm(profile.width)} мм`,{major:true,labelDy:topView?-12:14});
      if(!topView)paintMeasure('overall-height',[rightOutsideX,0,PL*.36],[rightOutsideX,totalTop,PL*.36],`${fmtMm(totalTop/S)} мм`,{major:true,labelDx:28});

      if(showDeckLength&&!sideView){
        const focusIndex=Math.floor((topXs.length-1)/2),focusX=topXs[focusIndex];
        paintMeasure('deck-length',[focusX,topSurface,-deckL/2],[focusX,topSurface,deckL/2],`${fmtMm(deckLengthMm)} мм`,{labelDx:22});
      }

      if(!sideView){
        const boardFront=Math.min(deckL/2,PL/2)-.10;
        const gapFront=topView?Math.min(PL/2,deckL/2)+.14:Math.min(PL/2,deckL/2)+.36;
        topXs.forEach((x,i)=>{
          paintMeasure(`board-width-${i}`,[x-actualDeckW/2,topSurface,boardFront],[x+actualDeckW/2,topSurface,boardFront],fmtMm(deckWidthMm),{compact:true,kind:'board',labelDy:topView?-17:(i%2?10:-10),minPx:7});
        });
        if(topXs.length>1){
          for(let i=0;i<topXs.length-1;i++){
            const a=topXs[i]+actualDeckW/2,b=topXs[i+1]-actualDeckW/2;
            paintMeasure(`gap-${i}`,[a,topSurface,gapFront],[b,topSurface,gapFront],gapBad?`−${fmtMm(Math.abs(rawGapMm))}`:fmtMm(rawGapMm),{compact:true,kind:'gap',bad:gapBad,labelDy:topView?17:(i%2?-11:11),minPx:5});
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
'''
js = js[:start] + new_block + js[end:]
js_path.write_text(js, encoding='utf-8')

css = css_path.read_text(encoding='utf-8')
if 'v1.1.7' not in css:
    raise SystemExit('CSS version marker v1.1.7 not found')
css = css.replace('v1.1.7', 'v1.1.8')
css = css.replace('обновление №341', 'обновление №342')
css_path.write_text(css, encoding='utf-8')

html = html_path.read_text(encoding='utf-8')
if 'v1.1.7' not in html:
    raise SystemExit('HTML version marker v1.1.7 not found')
html = html.replace('v1.1.7', 'v1.1.8')
html = html.replace('обновление №341', 'обновление №342')
m = re.search(r'assets/pallet3d-v10\.js\?v=(\d+)', html)
if not m:
    raise SystemExit('pallet3d cache marker not found')
html = html[:m.start(1)] + str(int(m.group(1)) + 1) + html[m.end(1):]
html_path.write_text(html, encoding='utf-8')
