from pathlib import Path
import re

js = Path('assets/pallet3d-v10.js')
s = js.read_text(encoding='utf-8')

# 1) Persistent UI state.
if "state.showComposition" not in s:
    needle = "  if(typeof state.showDimensions!=='boolean')state.showDimensions=true;\n"
    if needle not in s:
        raise SystemExit('showDimensions state target not found')
    s = s.replace(needle, needle + "  if(typeof state.showComposition!=='boolean')state.showComposition=false;\n", 1)

# 2) Make the render signature aware of the new panel and hidden groups.
old_sig = "    return ids.map(id=>el(id)?.value??'').join('|')+'|'+(state.mode||'3d')+'|'+(state.selected||'all');"
new_sig = "    return ids.map(id=>el(id)?.value??'').join('|')+'|'+(state.mode||'3d')+'|'+(state.selected||'all')+'|'+(state.showComposition?'composition':'model')+'|'+(Array.isArray(state.hiddenKinds)?state.hiddenKinds.join(','):'');"
if old_sig in s:
    s = s.replace(old_sig, new_sig, 1)

# 3) Build a compact bill of materials from the same seven calculator part rows.
marker = "const compositionRows=P.map"
if marker not in s:
    anchor = "    const gapText=deckCount>1?(gapBad?`−${fmtMm(Math.abs(rawGapMm))} мм`:`${fmtMm(rawGapMm)} мм`):'—';\n    const dimensionOverlay='<div class=\"palletOnModelMeasures\" aria-label=\"Полная размерная схема поддона\"></div>';"
    if anchor not in s:
        raise SystemExit('composition insertion anchor not found')
    block = """    const gapText=deckCount>1?(gapBad?`−${fmtMm(Math.abs(rawGapMm))} мм`:`${fmtMm(rawGapMm)} мм`):'—';
    const showComposition=mode!=='3d'&&state.showComposition===true;
    const orderQty=Math.max(1,Math.round(num(el('qty')?.value,1)));
    const density=clamp(num(el('smartDensity')?.value,500)||500,250,1000);
    const fmtKg=v=>Number(v||0).toLocaleString('ru-RU',{minimumFractionDigits:v>0&&v<10?2:1,maximumFractionDigits:v>0&&v<10?2:1});
    const partNames=['Настил','Поперечина 1','Поперечина 2','Лыжа 1','Лыжа 2','Шашка 1','Шашка 2'];
    const partKinds=['deck','cross','cross','runner','runner','block','block'];
    const compositionRows=P.map((p,i)=>{
      const qty=Math.max(0,Math.round(num(p.n,0)));if(!qty)return null;
      const t=Math.max(0,num(p.t,0)),w=Math.max(0,num(p.w,0)),l=Math.max(0,num(p.l,0));
      const oneWeight=t*w*l/1e9*density,perWeight=oneWeight*qty,batchWeight=perWeight*orderQty;
      return {name:partNames[i]||p.name||`Деталь ${i+1}`,kind:partKinds[i]||'deck',qty,t,w,l,oneWeight,perWeight,batchWeight};
    }).filter(Boolean);
    const compositionCount=compositionRows.reduce((a,r)=>a+r.qty,0);
    const compositionOrderCount=compositionCount*orderQty;
    const compositionPerWeight=compositionRows.reduce((a,r)=>a+r.perWeight,0);
    const compositionBatchWeight=compositionPerWeight*orderQty;
    const compositionPanel=showComposition?`<aside class=\"palletCompositionPanel\" aria-label=\"Состав поддона\"><div class=\"palletCompositionHead\"><div><small>СПЕЦИФИКАЦИЯ</small><strong>Состав поддона</strong></div><span>${orderQty.toLocaleString('ru-RU')} подд.</span></div><div class=\"palletCompositionRows\">${compositionRows.length?compositionRows.map(r=>`<div class=\"palletCompositionRow\" data-kind=\"${r.kind}\"><div class=\"palletCompositionName\"><i class=\"legendDot ${r.kind}\"></i><div><b>${r.name}</b><span>${fmtMm(r.t)} × ${fmtMm(r.w)} × ${fmtMm(r.l)} мм</span></div></div><div class=\"palletCompositionMetrics\"><span><small>На поддон</small><b>${r.qty} шт.</b></span><span><small>Вес 1 шт.</small><b>${fmtKg(r.oneWeight)} кг</b></span><span><small>На заказ</small><b>${fmtKg(r.batchWeight)} кг</b></span></div></div>`).join(''):'<div class=\"palletCompositionEmpty\">Добавьте детали в калькулятор, чтобы увидеть состав.</div>'}</div><div class=\"palletCompositionTotal\"><div><span>Деталей</span><b>${compositionCount.toLocaleString('ru-RU')} шт. / поддон</b></div><div><span>Вес древесины</span><b>${fmtKg(compositionPerWeight)} кг / поддон</b></div><div><span>Весь заказ</span><b>${compositionOrderCount.toLocaleString('ru-RU')} шт. · ${fmtKg(compositionBatchWeight)} кг</b></div><small>Плотность: ${Math.round(density)} кг/м³</small></div></aside>`:'';
    const dimensionOverlay='<div class=\"palletOnModelMeasures\" aria-label=\"Полная размерная схема поддона\"></div>';"""
    s = s.replace(anchor, block, 1)

# 4) Add the toolbar switch and two-column workspace around the model.
if 'data-p3d-composition' not in s:
    needle = '>Размеры</button></div>${partLegend}${fastenerLegend}<div class="palletReferenceStage"'
    repl = '>Размеры</button><button type="button" data-p3d-composition aria-pressed="${showComposition?\'true\':\'false\'}" class="${showComposition?\'active\':\'\'}" ${mode===\'3d\'?\'hidden\':\'\'}>Состав</button></div>${partLegend}${fastenerLegend}<div class="palletModelWorkspace ${showComposition?\'hasComposition\':\'\'}"><div class="palletReferenceStage"'
    if needle not in s:
        raise SystemExit('toolbar composition target not found')
    s = s.replace(needle, repl, 1)
    close = '<div class="palletPartInspector" hidden><strong></strong><span></span><b></b></div></div>`;'
    close_new = '<div class="palletPartInspector" hidden><strong></strong><span></span><b></b></div></div>${compositionPanel}</div>`;'
    if close not in s:
        raise SystemExit('workspace close target not found')
    s = s.replace(close, close_new, 1)

# 5) Toggle the panel.
if "root.querySelector('[data-p3d-composition]')" not in s:
    needle = "    root.querySelector('[data-p3d-dims]')?.addEventListener('click',()=>{state.showDimensions=!state.showDimensions;render(num(el('pL')?.value),num(el('pW')?.value));});\n"
    if needle not in s:
        raise SystemExit('composition event target not found')
    s = s.replace(needle, needle + "    root.querySelector('[data-p3d-composition]')?.addEventListener('click',()=>{state.showComposition=!state.showComposition;render(num(el('pL')?.value),num(el('pW')?.value));});\n", 1)

# 6) Keep the composition live when quantities, sizes or density change.
old_live = "    ['pL','pW','n0','t0','w0','l0'].forEach(id=>{const input=el(id);if(!input||input.dataset.palletMeasureReady==='1')return;input.dataset.palletMeasureReady='1';input.addEventListener('input',refresh);input.addEventListener('change',refresh);});"
new_live = "    ['pL','pW','qty',...Array.from({length:7},(_,i)=>['n'+i,'t'+i,'w'+i,'l'+i]).flat()].forEach(id=>{const input=el(id);if(!input||input.dataset.palletMeasureReady==='1')return;input.dataset.palletMeasureReady='1';input.addEventListener('input',refresh);input.addEventListener('change',refresh);});if(!window.__palletCompositionDensityReady){window.__palletCompositionDensityReady=true;document.addEventListener('input',e=>{if(e.target?.id==='smartDensity')refresh();});document.addEventListener('change',e=>{if(e.target?.id==='smartDensity')refresh();});}"
if old_live in s:
    s = s.replace(old_live, new_live, 1)

js.write_text(s, encoding='utf-8')

# 7) Styling: right-side specification on desktop, below the model on smaller screens.
css = Path('assets/theme-industrial-v130.css')
c = css.read_text(encoding='utf-8')
css_marker = '/* palletCompositionV1131 */'
if css_marker not in c:
    patch = r'''

/* palletCompositionV1131 */
.palletModelWorkspace{display:grid;grid-template-columns:minmax(0,1fr);gap:12px;align-items:start;width:100%}
.palletModelWorkspace.hasComposition{grid-template-columns:minmax(0,1fr) 320px}
.palletCompositionPanel{margin-top:8px;min-width:0;border:1px solid #e3dbd1;border-radius:14px;background:linear-gradient(180deg,#fffdf9,#faf6f0);box-shadow:0 10px 26px rgba(75,53,34,.08);overflow:hidden;color:#3d342d}
.palletCompositionHead{display:flex;justify-content:space-between;gap:10px;align-items:flex-start;padding:13px 13px 11px;border-bottom:1px solid #ece3d8;background:rgba(249,241,231,.64)}
.palletCompositionHead small{display:block;margin-bottom:3px;color:#a16d3e;font-size:8px;font-weight:900;letter-spacing:.13em}
.palletCompositionHead strong{display:block;font-size:15px;line-height:1.15;color:#332b25}
.palletCompositionHead>span{padding:4px 7px;border:1px solid #e1cfbc;border-radius:999px;background:#fff8ef;color:#815631;font-size:9px;font-weight:900;white-space:nowrap}
.palletCompositionRows{display:grid;gap:0}
.palletCompositionRow{padding:11px 12px;border-bottom:1px solid #eee7df}
.palletCompositionRow:last-child{border-bottom:0}
.palletCompositionName{display:flex;align-items:flex-start;gap:8px;min-width:0}
.palletCompositionName .legendDot{margin-top:3px;flex:0 0 auto}
.palletCompositionName div{min-width:0}
.palletCompositionName b{display:block;color:#3f3730;font-size:11px;line-height:1.2}
.palletCompositionName span{display:block;margin-top:2px;color:#8a7b6d;font-size:9px;font-weight:750;line-height:1.25;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.palletCompositionMetrics{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:5px;margin-top:8px}
.palletCompositionMetrics>span{min-width:0;padding:6px 5px;border:1px solid #ece2d7;border-radius:8px;background:#fff}
.palletCompositionMetrics small{display:block;color:#9b8b7e;font-size:7px;font-weight:850;line-height:1.1;text-transform:uppercase;letter-spacing:.035em}
.palletCompositionMetrics b{display:block;margin-top:3px;color:#5a4432;font-size:9px;line-height:1.15;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.palletCompositionTotal{display:grid;gap:7px;padding:11px 12px 12px;border-top:1px solid #e8ddd1;background:#f7eee3}
.palletCompositionTotal>div{display:flex;justify-content:space-between;gap:10px;align-items:baseline}
.palletCompositionTotal span{color:#806f60;font-size:9px;font-weight:800}
.palletCompositionTotal b{color:#4a3829;font-size:10px;text-align:right}
.palletCompositionTotal>small{padding-top:5px;border-top:1px solid rgba(139,102,66,.14);color:#94795f;font-size:8px;font-weight:800}
.palletCompositionEmpty{padding:18px 13px;color:#8f8277;font-size:10px;line-height:1.4;text-align:center}
html[data-theme="dark"] .palletCompositionPanel{border-color:#514236;background:linear-gradient(180deg,#2d2824,#27231f);color:#eee1d2}
html[data-theme="dark"] .palletCompositionHead{border-color:#4b3d33;background:#332b25}
html[data-theme="dark"] .palletCompositionHead strong,html[data-theme="dark"] .palletCompositionName b{color:#f4e9dc}
html[data-theme="dark"] .palletCompositionHead>span{border-color:#5d4735;background:#3b3027;color:#e8c49e}
html[data-theme="dark"] .palletCompositionRow{border-color:#443a32}
html[data-theme="dark"] .palletCompositionName span{color:#b7a99c}
html[data-theme="dark"] .palletCompositionMetrics>span{border-color:#493c32;background:#312a25}
html[data-theme="dark"] .palletCompositionMetrics b{color:#ead0b3}
html[data-theme="dark"] .palletCompositionTotal{border-color:#4a3d33;background:#332a23}
html[data-theme="dark"] .palletCompositionTotal b{color:#f0d5b8}
@media(max-width:1040px){.palletModelWorkspace.hasComposition{grid-template-columns:minmax(0,1fr)}.palletCompositionPanel{margin-top:0}.palletCompositionRows{grid-template-columns:repeat(2,minmax(0,1fr))}.palletCompositionRow:nth-child(odd){border-right:1px solid #eee7df}}
@media(max-width:620px){.palletCompositionRows{grid-template-columns:1fr}.palletCompositionRow:nth-child(odd){border-right:0}.palletCompositionMetrics{gap:4px}.palletCompositionPanel{border-radius:12px}.palletCompositionHead{padding:11px}.palletCompositionRow{padding:10px}.palletCompositionTotal{padding:10px}}
'''
    css.write_text(c + patch, encoding='utf-8')

# 8) Cache bust both changed assets.
idx = Path('index.html')
h = idx.read_text(encoding='utf-8')
h = re.sub(r'assets/theme-industrial-v130\.css\?v=\d+', 'assets/theme-industrial-v130.css?v=181', h)
h = re.sub(r'assets/pallet3d-v10\.js\?v=\d+', 'assets/pallet3d-v10.js?v=131', h)
idx.write_text(h, encoding='utf-8')
