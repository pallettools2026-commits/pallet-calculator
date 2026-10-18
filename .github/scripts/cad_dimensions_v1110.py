from pathlib import Path
import re

js_path = Path('assets/pallet3d-v10.js')
css_path = Path('assets/theme-industrial-v130.css')
html_path = Path('index.html')

js = js_path.read_text(encoding='utf-8')

old_marks = "    const measureMarks={};\n"
new_marks = "    const measureMarks={};\n    let measureLabelBoxes=[];\n"
if old_marks not in js:
    raise SystemExit('measureMarks marker not found')
js = js.replace(old_marks, new_marks, 1)

start = js.find("    const clearMeasures=()=>")
end = js.find("    const updateOnModelMeasures=()=>", start)
if start < 0 or end < 0:
    raise SystemExit('measure renderer block not found')
replacement = r'''    const clearMeasures=()=>{measureLabelBoxes=[];Object.values(measureMarks).forEach(mark=>mark.style.display='none');};
    const paintMeasure=(name,a,b,text,opts={})=>{
      const mark=ensureMeasure(name,opts.kind||'normal');
      const p1=projectMeasurePoint(a[0],a[1],a[2]),p2=projectMeasurePoint(b[0],b[1],b[2]);
      if(!p1||!p2){mark.style.display='none';return;}
      const dx=p2.x-p1.x,dy=p2.y-p1.y,dist=Math.hypot(dx,dy);
      if(dist<(opts.minPx||4)){mark.style.display='none';return;}
      const angle=Math.atan2(dy,dx)*180/Math.PI,mx=(p1.x+p2.x)/2,my=(p1.y+p2.y)/2;
      const line=mark.querySelector('.measureLine'),tickA=mark.querySelector('.tickA'),tickB=mark.querySelector('.tickB'),label=mark.querySelector('span');
      mark.style.display='block';mark.classList.toggle('bad',!!opts.bad);mark.classList.toggle('major',!!opts.major);mark.classList.toggle('compact',!!opts.compact);
      if(line){line.style.left=`${p1.x}px`;line.style.top=`${p1.y}px`;line.style.width=`${dist}px`;line.style.transform=`rotate(${angle}deg)`;}
      [[tickA,p1],[tickB,p2]].forEach(([tick,p])=>{if(!tick)return;tick.style.left=`${p.x}px`;tick.style.top=`${p.y}px`;tick.style.transform=`translate(-50%,-50%) rotate(${angle+90}deg)`;});
      if(label){
        label.textContent=text;
        const stageW=Math.max(1,stage?.clientWidth||renderer.domElement.clientWidth||cw),stageH=Math.max(1,stage?.clientHeight||renderer.domElement.clientHeight||ch);
        const charW=opts.compact?6.1:(opts.major?8.0:7.0),labelW=Math.max(opts.compact?28:(opts.major?54:38),String(text).length*charW+(opts.compact?10:16)),labelH=opts.compact?18:(opts.major?28:22);
        const pad=6;
        let lx=mx+(opts.labelDx||0),ly=my+(opts.labelDy||0);
        lx=clamp(lx,labelW/2+pad,stageW-labelW/2-pad);ly=clamp(ly,labelH/2+pad,stageH-labelH/2-pad);
        const box={left:lx-labelW/2-3,right:lx+labelW/2+3,top:ly-labelH/2-3,bottom:ly+labelH/2+3};
        if(opts.avoidOverlap&&measureLabelBoxes.some(b=>box.left<b.right&&box.right>b.left&&box.top<b.bottom&&box.bottom>b.top)){mark.style.display='none';return;}
        measureLabelBoxes.push(box);
        label.style.left=`${lx}px`;label.style.top=`${ly}px`;
      }
      return mark;
    };
'''
js = js[:start] + replacement + js[end:]

replacements = [
    ("const leftOutsideX=-PW/2-(topView?.62:.72),rightOutsideX=PW/2+.72;", "const leftOutsideX=-PW/2-(topView?.62:.72),rightOutsideX=PW/2+(topView?.72:(sideView?.72:.38));"),
    ("{major:true,labelDx:28}", "{major:true,labelDx:18}"),
    ("{compact:true,kind:'board',labelDy:topView?0:(i%2?10:-10),minPx:7}", "{compact:true,kind:'board',labelDy:topView?0:(i%2?10:-10),minPx:topView?7:16,avoidOverlap:!topView}"),
    ("{compact:true,kind:'gap',bad:gapBad,labelDy:topView?0:(i%2?-11:11),minPx:5}", "{compact:true,kind:'gap',bad:gapBad,labelDy:topView?0:(i%2?-11:11),minPx:topView?5:13,avoidOverlap:!topView}"),
    ("node.textContent=admin?'Pallet Tools · v1.1.5 · обновление №339':'Pallet Tools · v1.1.5';", "node.textContent=admin?'Pallet Tools · v1.1.10 · обновление №344':'Pallet Tools · v1.1.10';")
]
for old, new in replacements:
    if old not in js:
        raise SystemExit(f'JS marker not found: {old[:90]}')
    js = js.replace(old, new, 1)
js_path.write_text(js, encoding='utf-8')

css = css_path.read_text(encoding='utf-8')
if 'Pallet Tools · v1.1.9' not in css or 'обновление №343' not in css:
    raise SystemExit('CSS version markers not found')
css = css.replace('Pallet Tools · v1.1.9', 'Pallet Tools · v1.1.10')
css = css.replace('обновление №343', 'обновление №344')
css_path.write_text(css, encoding='utf-8')

html = html_path.read_text(encoding='utf-8')
if 'Pallet Tools · v1.1.3</div>' in html:
    html = html.replace('Pallet Tools · v1.1.3</div>', 'Pallet Tools · v1.1.10</div>', 1)
for pattern in [r'assets/theme-industrial-v130\.css\?v=(\d+)', r'assets/pallet3d-v10\.js\?v=(\d+)']:
    m = re.search(pattern, html)
    if not m:
        raise SystemExit(f'cache marker not found: {pattern}')
    html = html[:m.start(1)] + str(int(m.group(1)) + 1) + html[m.end(1):]
html_path.write_text(html, encoding='utf-8')
