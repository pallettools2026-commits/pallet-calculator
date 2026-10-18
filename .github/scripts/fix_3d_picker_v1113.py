from pathlib import Path
import re

html_path=Path('index.html')
css_path=Path('assets/theme-industrial-v130.css')
js_path=Path('assets/pallet3d-v10.js')
smart_path=Path('assets/smart-tools-v1.js')

html=html_path.read_text(encoding='utf-8')
css=css_path.read_text(encoding='utf-8')
js=js_path.read_text(encoding='utf-8')
smart=smart_path.read_text(encoding='utf-8')

# v1.1.14 — make deck-board selection deterministic in screen space.
old_select="    const selectAt=(clientX,clientY)=>{const hit=pickAt(clientX,clientY);return hit?showInspect(hit.object):false;};"
new_select="""    const pointInPolygon=(x,y,poly)=>{let inside=false;for(let i=0,j=poly.length-1;i<poly.length;j=i++){const a=poly[i],b=poly[j];if(((a.y>y)!==(b.y>y))&&(x<(b.x-a.x)*(y-a.y)/((b.y-a.y)||1e-9)+a.x))inside=!inside;}return inside;};
    const projectToCanvas=(x,y,z,rect)=>{const v=new THREE.Vector3(x,y,z).project(camera);if(!Number.isFinite(v.x)||!Number.isFinite(v.y)||v.z<-1.1||v.z>1.1)return null;return{x:(v.x*.5+.5)*rect.width,y:(-v.y*.5+.5)*rect.height};};
    const pickDeckByProjection=(clientX,clientY)=>{
      const rect=canvas.getBoundingClientRect();if(!rect.width||!rect.height||!inspectable.length)return null;
      const px=clientX-rect.left,py=clientY-rect.top;
      scene.updateMatrixWorld(true);camera.updateMatrixWorld(true);
      const y=topY+deckT/2+groups.deck.position.y+.025,halfW=actualDeckW/2+.09,halfL=deckL/2+.07;
      const candidates=[];
      inspectable.forEach((mesh,i)=>{
        const x=topXs[i]??mesh.position.x;
        const poly=[projectToCanvas(x-halfW,y,-halfL,rect),projectToCanvas(x+halfW,y,-halfL,rect),projectToCanvas(x+halfW,y,halfL,rect),projectToCanvas(x-halfW,y,halfL,rect)];
        if(poly.some(p=>!p))return;
        if(pointInPolygon(px,py,poly)){
          const c=projectToCanvas(x,y,0,rect),d=c?Math.hypot(px-c.x,py-c.y):0;
          candidates.push({object:mesh,d});
        }
      });
      if(candidates.length){candidates.sort((a,b)=>a.d-b.d);return candidates[0];}
      return null;
    };
    const selectAt=(clientX,clientY)=>{const projected=pickDeckByProjection(clientX,clientY);if(projected)return showInspect(projected.object);const hit=pickAt(clientX,clientY);return hit?showInspect(hit.object):false;};"""
if 'const pickDeckByProjection=(clientX,clientY)' not in js:
    if old_select not in js:
        raise SystemExit('selectAt marker not found')
    js=js.replace(old_select,new_select,1)

# Make the action button force the real 3D view before the user taps a board.
old_button="""    $('smartSelect3D')?.addEventListener('click',()=>{
      const preview=$('palletPreview3D')?.closest('.previewCard');
      preview?.classList.add('partPickMode');
      preview?.scrollIntoView({behavior:'smooth',block:'center'});
      const hint=document.querySelector('.palletPickHint');
      if(hint){hint.textContent='Нажмите на любую верхнюю доску';hint.classList.add('attention');}
      setTimeout(()=>hint?.classList.remove('attention'),2200);
    });"""
new_button="""    $('smartSelect3D')?.addEventListener('click',()=>{
      const preview=$('palletPreview3D')?.closest('.previewCard');
      const mode3d=$('palletPreview3D')?.querySelector('[data-p3d-mode="3d"]');
      if(mode3d&&!mode3d.classList.contains('active'))mode3d.click();
      setTimeout(()=>{
        const livePreview=$('palletPreview3D')?.closest('.previewCard')||preview;
        livePreview?.classList.add('partPickMode');
        livePreview?.scrollIntoView({behavior:'smooth',block:'center'});
        const hint=document.querySelector('.palletPickHint');
        if(hint){hint.textContent='Режим выбора: нажмите прямо на верхнюю доску';hint.classList.add('attention');}
        setTimeout(()=>hint?.classList.remove('attention'),2600);
      },90);
    });"""
if new_button not in smart:
    if old_button not in smart:
        raise SystemExit('smart 3D button handler not found')
    smart=smart.replace(old_button,new_button,1)

# Keep the smart card visibly confirmed after a successful selection.
old_listener="window.addEventListener('pallet3d:partselect',e=>{selectedPart=e.detail||null;document.querySelector('.previewCard')?.classList.remove('partPickMode');document.querySelector('.palletPickHint')?.classList.remove('attention');renderSelected();});"
new_listener="window.addEventListener('pallet3d:partselect',e=>{selectedPart=e.detail||null;document.querySelector('.previewCard')?.classList.remove('partPickMode');document.querySelector('.palletPickHint')?.classList.remove('attention');const card=$('smartSelectedTitle')?.closest('.smartToolCard');card?.classList.add('hasSelection');renderSelected();});"
if new_listener not in smart:
    if old_listener not in smart:
        raise SystemExit('partselect listener not found')
    smart=smart.replace(old_listener,new_listener,1)

smart=smart.replace('/* Pallet Tools smart production helpers v1.1.12 */','/* Pallet Tools smart production helpers v1.1.14 */',1)

if 'partPickerFixV1114' not in css:
    css += r'''

/* partPickerFixV1114 */
.previewCard.partPickMode .palletReferenceStage{outline:3px solid rgba(48,112,167,.25)!important;outline-offset:2px!important}
.previewCard.partPickMode .palletPickHint{background:#244f75!important;border-color:#3978ad!important;color:#fff!important;box-shadow:0 0 0 6px rgba(55,105,155,.12),0 8px 24px rgba(25,55,82,.22)!important}
.smartToolCard.selected.hasSelection{border-color:#bad8c7!important;box-shadow:0 8px 24px rgba(42,111,78,.10)!important}.smartToolCard.selected.hasSelection .smartSelectedQty{background:#edf7f1!important;color:#315f49!important}
html[data-theme="dark"] .smartToolCard.selected.hasSelection{border-color:#3f6b55!important}html[data-theme="dark"] .smartToolCard.selected.hasSelection .smartSelectedQty{background:#20372c!important;color:#c5e1d1!important}
'''

# App version + cache busts.
for path_text_name in ('html','css','js','smart'):
    pass
html=html.replace('Pallet Tools · v1.1.13</div>','Pallet Tools · v1.1.14</div>',1)
for pattern in [r'assets/theme-industrial-v130\.css\?v=(\d+)',r'assets/pallet3d-v10\.js\?v=(\d+)',r'assets/smart-tools-v1\.js\?v=(\d+)']:
    m=re.search(pattern,html)
    if not m:
        raise SystemExit(f'cache marker missing: {pattern}')
    html=html[:m.start(1)]+str(int(m.group(1))+1)+html[m.end(1):]

css=css.replace('Pallet Tools · v1.1.13','Pallet Tools · v1.1.14').replace('обновление №347','обновление №348')
js=js.replace('Pallet Tools · v1.1.13','Pallet Tools · v1.1.14')
smart=smart.replace('Pallet Tools · v1.1.13','Pallet Tools · v1.1.14')

html_path.write_text(html,encoding='utf-8')
css_path.write_text(css,encoding='utf-8')
js_path.write_text(js,encoding='utf-8')
smart_path.write_text(smart,encoding='utf-8')
