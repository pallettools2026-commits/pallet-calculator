from pathlib import Path
import re

js_path = Path('assets/pallet3d-v10.js')
css_path = Path('assets/theme-industrial-v130.css')
index_path = Path('index.html')

js = js_path.read_text(encoding='utf-8')
css = css_path.read_text(encoding='utf-8')
index = index_path.read_text(encoding='utf-8')

if 'palletMaterialV1135' not in js:
    state_marker = "  if(typeof state.showValidation!=='boolean')state.showValidation=false;\n"
    state_add = state_marker + "  if(typeof state.showMaterial!=='boolean')state.showMaterial=false;\n  if(![0,5,10].includes(Number(state.materialReserve)))state.materialReserve=5;\n"
    if state_marker not in js:
        raise SystemExit('material state marker not found')
    js = js.replace(state_marker, state_add, 1)

    sig_marker = "+'|validation:'+(state.showValidation?'open':'closed')+'|assembly:'+(state.assemblyStep||0)+'|'"
    sig_repl = "+'|validation:'+(state.showValidation?'open':'closed')+'|material:'+(state.showMaterial?'open':'closed')+':' +(state.materialReserve||0)+'|assembly:'+(state.assemblyStep||0)+'|'"
    if sig_marker not in js:
        raise SystemExit('material signature marker not found')
    js = js.replace(sig_marker, sig_repl, 1)

    material_code = r'''    /* palletMaterialV1135 — timber volume and reserve estimate */
    const materialReserve=[0,5,10].includes(Number(state.materialReserve))?Number(state.materialReserve):5;
    const showMaterial=!assemblyActive&&state.showMaterial===true;
    const fmtM3=v=>{const x=Math.max(0,num(v,0));return x.toLocaleString('ru-RU',{minimumFractionDigits:3,maximumFractionDigits:x<1?4:3});};
    const materialKindMeta={
      deck:{label:'Настил',note:'верхние доски'},
      cross:{label:'Поперечины',note:'связующие доски'},
      runner:{label:'Лыжи',note:'нижние продольные'},
      block:{label:'Шашки',note:'опорные элементы'}
    };
    const materialGroups=['deck','cross','runner','block'].map(kind=>{
      const rows=compositionRows.filter(r=>r.kind===kind);
      const perPallet=rows.reduce((sum,r)=>sum+(Math.max(0,r.t)*Math.max(0,r.w)*Math.max(0,r.l)/1e9*Math.max(0,r.qty)),0);
      const piecesPerPallet=rows.reduce((sum,r)=>sum+Math.max(0,r.qty),0);
      const piecesOrder=piecesPerPallet*orderQty;
      const orderVolume=perPallet*orderQty;
      const withReserve=orderVolume*(1+materialReserve/100);
      return {kind,label:materialKindMeta[kind].label,note:materialKindMeta[kind].note,perPallet,piecesPerPallet,piecesOrder,orderVolume,withReserve};
    }).filter(r=>r.piecesPerPallet>0);
    const materialPerPallet=materialGroups.reduce((sum,r)=>sum+r.perPallet,0);
    const materialOrderBase=materialPerPallet*orderQty;
    const materialReserveVolume=materialOrderBase*materialReserve/100;
    const materialOrderTotal=materialOrderBase+materialReserveVolume;
    const materialPanel=showMaterial?`<section class="palletMaterialPanel" aria-label="Расчёт пиломатериала"><div class="palletMaterialHead"><div><small>ПИЛОМАТЕРИАЛ</small><strong>Оценка древесины на заказ</strong><p>Объём считается по фактическим размерам и количеству деталей.</p></div><span>${orderQty.toLocaleString('ru-RU')} подд.</span></div><div class="palletMaterialSummary"><div><small>На 1 поддон</small><b>${fmtM3(materialPerPallet)} м³</b></div><div><small>Заказ без запаса</small><b>${fmtM3(materialOrderBase)} м³</b></div><div class="accent"><small>К заказу</small><b>${fmtM3(materialOrderTotal)} м³</b><em>${materialReserve?`запас +${materialReserve}% · ${fmtM3(materialReserveVolume)} м³`:'без запаса'}</em></div></div><div class="palletMaterialReserve"><span>Запас материала</span><div>${[0,5,10].map(v=>`<button type="button" data-p3d-material-reserve="${v}" class="${materialReserve===v?'active':''}">${v?`+${v}%`:'0%'}</button>`).join('')}</div></div><div class="palletMaterialRows">${materialGroups.length?materialGroups.map(r=>`<div class="palletMaterialRow" data-kind="${r.kind}"><div class="palletMaterialName"><i class="legendDot ${r.kind}"></i><div><b>${r.label}</b><span>${r.note}</span></div></div><div class="palletMaterialMetrics"><span><small>Деталей</small><b>${r.piecesOrder.toLocaleString('ru-RU')} шт.</b></span><span><small>Без запаса</small><b>${fmtM3(r.orderVolume)} м³</b></span><span><small>К заказу</small><b>${fmtM3(r.withReserve)} м³</b></span></div></div>`).join(''):'<div class="palletMaterialEmpty">Добавьте детали, чтобы рассчитать объём древесины.</div>'}</div><div class="palletMaterialFoot"><span>Итого: <b>${fmtM3(materialOrderTotal)} м³</b></span><em>Запас применяется к каждой группе пропорционально. Это ориентир для закупки, без учёта сортировки и фактической схемы раскроя.</em></div></section>`:'';
'''
    insert_marker = "    /* palletValidationV1134 — automatic construction checks */\n"
    if insert_marker not in js:
        raise SystemExit('material insertion marker not found')
    js = js.replace(insert_marker, material_code + insert_marker, 1)

    toolbar_marker = '>${validationButtonLabel}</button></div>${validationPanel}${assemblyPanel}'
    toolbar_repl = '>${validationButtonLabel}</button><button type="button" data-p3d-material aria-pressed="${showMaterial?\'true\':\'false\'}" class="palletMaterialButton ${showMaterial?\'active\':\'\'}" ${assemblyActive?\'hidden\':\'\'}>Материал</button></div>${validationPanel}${materialPanel}${assemblyPanel}'
    if toolbar_marker not in js:
        raise SystemExit('material toolbar marker not found')
    js = js.replace(toolbar_marker, toolbar_repl, 1)

    event_marker = "    root.querySelector('[data-p3d-validation]')?.addEventListener('click',()=>{state.showValidation=!state.showValidation;render(num(el('pL')?.value),num(el('pW')?.value));});\n"
    event_code = r'''    root.querySelector('[data-p3d-material]')?.addEventListener('click',()=>{state.showMaterial=!state.showMaterial;if(state.showMaterial){state.showComposition=false;state.showValidation=false;}render(num(el('pL')?.value),num(el('pW')?.value));});
    root.querySelectorAll('[data-p3d-material-reserve]').forEach(btn=>btn.addEventListener('click',()=>{state.materialReserve=Number(btn.dataset.p3dMaterialReserve)||0;render(num(el('pL')?.value),num(el('pW')?.value));}));
'''
    if event_marker not in js:
        raise SystemExit('material event marker not found')
    js = js.replace(event_marker, event_marker + event_code, 1)

    assembly_marker = "else{state.assemblyStep=1;state.mode='explode';state.showComposition=false;state.hiddenKinds=[];}"
    if assembly_marker in js:
        js = js.replace(assembly_marker, "else{state.assemblyStep=1;state.mode='explode';state.showComposition=false;state.showMaterial=false;state.hiddenKinds=[];}", 1)

if '/* palletMaterialV1135 */' not in css:
    css += r'''

/* palletMaterialV1135 */
#palletPreview3D .palletMaterialButton{min-width:82px;font-weight:900!important}
#palletPreview3D .palletMaterialButton.active{border-color:#a97846!important;background:#f3e4d2!important;color:#70461f!important;box-shadow:0 0 0 2px rgba(147,92,43,.09)!important}
.palletMaterialPanel{margin:9px 0 3px;border:1px solid #dfd3c6;border-radius:15px;background:linear-gradient(180deg,#fffdf9,#faf5ee);box-shadow:0 9px 24px rgba(75,53,34,.08);overflow:hidden;color:#3d342c}
.palletMaterialHead{display:flex;justify-content:space-between;gap:12px;align-items:flex-start;padding:13px 14px 11px;border-bottom:1px solid #eadfd3;background:rgba(248,239,228,.68)}
.palletMaterialHead small{display:block;margin-bottom:3px;color:#a36c39;font-size:8px;font-weight:950;letter-spacing:.14em}
.palletMaterialHead strong{display:block;color:#352c25;font-size:15px;line-height:1.2}
.palletMaterialHead p{margin:4px 0 0;color:#7e7064;font-size:9px;font-weight:700;line-height:1.35}
.palletMaterialHead>span{flex:0 0 auto;padding:5px 8px;border:1px solid #dec9b3;border-radius:999px;background:#fff8ee;color:#7d532f;font-size:9px;font-weight:900;white-space:nowrap}
.palletMaterialSummary{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px;padding:11px 12px}
.palletMaterialSummary>div{display:grid;gap:3px;min-width:0;padding:10px 11px;border:1px solid #eadfd4;border-radius:11px;background:#fff}
.palletMaterialSummary small{color:#87796d;font-size:8px;font-weight:800}.palletMaterialSummary b{color:#4b3827;font-size:15px;line-height:1.15}.palletMaterialSummary em{color:#916239;font-size:8px;font-style:normal;font-weight:800;line-height:1.25}
.palletMaterialSummary>div.accent{border-color:#d6b48d;background:#fbefdf}.palletMaterialSummary>div.accent b{color:#76471f}
.palletMaterialReserve{display:flex;justify-content:space-between;align-items:center;gap:10px;padding:0 12px 11px}.palletMaterialReserve>span{color:#6e6258;font-size:9px;font-weight:850}.palletMaterialReserve>div{display:flex;gap:5px}
.palletMaterialReserve button{min-height:30px;padding:5px 10px;border:1px solid #dfd1c3;border-radius:8px;background:#fff;color:#6f6054;font-size:9px;font-weight:900;box-shadow:none}.palletMaterialReserve button.active{border-color:#a76c36;background:#a76c36;color:#fff}
.palletMaterialRows{display:grid;border-top:1px solid #eee4da}
.palletMaterialRow{display:grid;grid-template-columns:minmax(150px,1fr) minmax(280px,1.4fr);gap:10px;align-items:center;padding:10px 12px;border-bottom:1px solid #eee7df;background:#fff}.palletMaterialRow:last-child{border-bottom:0}
.palletMaterialName{display:flex;align-items:center;gap:8px;min-width:0}.palletMaterialName>div{display:grid;gap:2px;min-width:0}.palletMaterialName b{color:#493b31;font-size:10px}.palletMaterialName span{color:#8a7d71;font-size:8px;font-weight:700}
.palletMaterialMetrics{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:6px}.palletMaterialMetrics>span{display:grid;gap:2px;padding:6px 7px;border:1px solid #eee6de;border-radius:8px;background:#fcfaf7}.palletMaterialMetrics small{color:#918478;font-size:7px;font-weight:800}.palletMaterialMetrics b{color:#5a4737;font-size:9px;white-space:nowrap}
.palletMaterialFoot{display:flex;justify-content:space-between;gap:14px;align-items:center;padding:9px 12px;border-top:1px solid #e9ded3;background:#f8f2ea}.palletMaterialFoot span{color:#655548;font-size:9px;font-weight:800;white-space:nowrap}.palletMaterialFoot span b{color:#72471f;font-size:12px}.palletMaterialFoot em{max-width:560px;color:#8c7f73;font-size:8px;font-style:normal;font-weight:700;line-height:1.35;text-align:right}.palletMaterialEmpty{padding:14px;color:#8c7f74;font-size:10px;text-align:center}
html[data-theme="dark"] .palletMaterialPanel{border-color:#554537;background:linear-gradient(180deg,#302a25,#292520);color:#eee1d4}html[data-theme="dark"] .palletMaterialHead{border-color:#4b4037;background:#352d26}html[data-theme="dark"] .palletMaterialHead strong{color:#f3e7db}html[data-theme="dark"] .palletMaterialHead p{color:#b8aca1}html[data-theme="dark"] .palletMaterialHead>span{border-color:#624b38;background:#3d3026;color:#e6c09a}
html[data-theme="dark"] .palletMaterialSummary>div{border-color:#4b4036;background:#302a25}html[data-theme="dark"] .palletMaterialSummary>div.accent{border-color:#725538;background:#3e3023}html[data-theme="dark"] .palletMaterialSummary small{color:#b5a99e}html[data-theme="dark"] .palletMaterialSummary b{color:#efd3b5}html[data-theme="dark"] .palletMaterialSummary em{color:#d5aa7c}
html[data-theme="dark"] .palletMaterialReserve>span{color:#c1b5aa}html[data-theme="dark"] .palletMaterialReserve button{border-color:#504238;background:#302a25;color:#d6c9bd}html[data-theme="dark"] .palletMaterialReserve button.active{border-color:#a76c36;background:#9b6232;color:#fff}
html[data-theme="dark"] .palletMaterialRows{border-color:#483d34}html[data-theme="dark"] .palletMaterialRow{border-color:#433a33;background:#2d2824}html[data-theme="dark"] .palletMaterialName b{color:#eee2d6}html[data-theme="dark"] .palletMaterialName span{color:#aea297}html[data-theme="dark"] .palletMaterialMetrics>span{border-color:#463c34;background:#312b26}html[data-theme="dark"] .palletMaterialMetrics small{color:#a99d91}html[data-theme="dark"] .palletMaterialMetrics b{color:#e8d4c0}html[data-theme="dark"] .palletMaterialFoot{border-color:#493e35;background:#332b24}html[data-theme="dark"] .palletMaterialFoot span{color:#cfbca9}html[data-theme="dark"] .palletMaterialFoot span b{color:#efc394}html[data-theme="dark"] .palletMaterialFoot em{color:#a99c90}
@media(max-width:720px){.palletMaterialSummary{grid-template-columns:1fr}.palletMaterialRow{grid-template-columns:1fr}.palletMaterialMetrics{grid-template-columns:repeat(3,minmax(0,1fr))}.palletMaterialFoot{display:grid}.palletMaterialFoot em{text-align:left}.palletMaterialReserve{align-items:flex-start;flex-direction:column}}
@media(max-width:480px){.palletMaterialMetrics{grid-template-columns:1fr}.palletMaterialMetrics>span{grid-template-columns:1fr auto;align-items:center}.palletMaterialHead{display:grid}.palletMaterialHead>span{justify-self:start}}
'''

def bump_asset_version(text, asset_name):
    pattern = re.escape(asset_name) + r'\?v=(\d+)'
    m = re.search(pattern, text)
    if not m:
        return text
    old = int(m.group(1))
    return text[:m.start(1)] + str(old + 1) + text[m.end(1):]

index = bump_asset_version(index, 'assets/theme-industrial-v130.css')
index = bump_asset_version(index, 'assets/pallet3d-v10.js')

js_path.write_text(js, encoding='utf-8')
css_path.write_text(css, encoding='utf-8')
index_path.write_text(index, encoding='utf-8')
