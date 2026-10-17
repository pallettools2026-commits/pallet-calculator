from pathlib import Path

index_path = Path('index.html')
index = index_path.read_text()

old_order = '''          <div class="orderFocusAside"><small>Ответственный</small><b id="dashWorker">Не указан</b><small>Дата</small><b id="dashWorkDate">—</b></div>
        </div>
      </article>'''
new_order = '''          <div class="orderFocusAside"><small>Ответственный</small><b id="dashWorker">Не указан</b><small>Дата</small><b id="dashWorkDate">—</b></div>
        </div>
        <div class="orderReadiness" id="dashOrderReadiness" aria-live="polite">
          <div class="orderReadinessIcon" id="dashReadinessIcon">!</div>
          <div class="orderReadinessMain"><strong id="dashReadinessTitle">Проверка данных заказа</strong><span id="dashReadinessText">Заполните основные данные перед запуском производства.</span><div class="orderReadinessChips" id="dashReadinessChips"></div></div>
          <button class="orderReadinessAction" id="dashReadinessAction" type="button" data-jump="calculator">Заполнить →</button>
        </div>
      </article>'''
if old_order not in index:
    raise SystemExit('Active order marker not found')
index = index.replace(old_order, new_order, 1)

old_dash_end = '''   const shift=text('worker');if($('dashboardShift'))$('dashboardShift').textContent=shift||'Смена';
 }'''
new_dash_end = '''   const shift=text('worker');if($('dashboardShift'))$('dashboardShift').textContent=shift||'Смена';
   const checks=[['Номер заказа',!!order],['Размер',L>0&&W>0],['Количество',Q>0],['Ответственный',!!worker],['Дата',date&&date!=='—']];
   const done=checks.filter(([,ok])=>ok).length,allReady=done===checks.length,missing=checks.filter(([,ok])=>!ok).map(([label])=>label.toLowerCase());
   const readiness=$('dashOrderReadiness'),readinessTitle=$('dashReadinessTitle'),readinessText=$('dashReadinessText'),readinessIcon=$('dashReadinessIcon'),readinessChips=$('dashReadinessChips'),readinessAction=$('dashReadinessAction');
   if(readiness){readiness.classList.toggle('ready',allReady);readiness.classList.toggle('needsAttention',!allReady);}
   if(readinessIcon)readinessIcon.textContent=allReady?'✓':'!';
   if(readinessTitle)readinessTitle.textContent=allReady?'Данные заказа готовы':`Подготовка заказа: ${done} / ${checks.length}`;
   if(readinessText)readinessText.textContent=allReady?'Можно переходить к производству и отмечать выполнение.':`Нужно заполнить: ${missing.join(', ')}.`;
   if(readinessChips)readinessChips.innerHTML=checks.map(([label,ok])=>`<span class="orderCheck${ok?' done':''}">${ok?'✓':'○'} ${label}</span>`).join('');
   if(readinessAction){readinessAction.textContent=allReady?'К производству →':'Заполнить →';readinessAction.dataset.jump=allReady?'production':'calculator';}
 }'''
if old_dash_end not in index:
    raise SystemExit('Dashboard update marker not found')
index = index.replace(old_dash_end, new_dash_end, 1)

if 'assets/theme-industrial-v130.css?v=142' not in index or 'assets/pallet3d-v10.js?v=138' not in index:
    raise SystemExit('Expected cache versions not found')
index = index.replace('assets/theme-industrial-v130.css?v=142', 'assets/theme-industrial-v130.css?v=143', 1)
index = index.replace('assets/pallet3d-v10.js?v=138', 'assets/pallet3d-v10.js?v=139', 1)
index_path.write_text(index)

css_path = Path('assets/theme-industrial-v130.css')
css = css_path.read_text()
if 'content:"Pallet Tools · v1.0.22"' not in css or 'content:"Pallet Tools · v1.0.22 · обновление №311"' not in css:
    raise SystemExit('CSS version strings not found')
css = css.replace('content:"Pallet Tools · v1.0.22"', 'content:"Pallet Tools · v1.0.23"', 1)
css = css.replace('content:"Pallet Tools · v1.0.22 · обновление №311"', 'content:"Pallet Tools · v1.0.23 · обновление №315"', 1)
css += '''\n\n/* Order readiness assistant v1.0.23 */\n.orderReadiness{display:grid;grid-template-columns:auto minmax(0,1fr) auto;align-items:center;gap:12px;margin-top:12px;padding:13px 14px;border:1px solid #ead9c6;border-radius:15px;background:linear-gradient(135deg,#fffaf4,#faf6ef);transition:border-color .18s,background .18s,box-shadow .18s}\n.orderReadinessIcon{display:grid;place-items:center;width:34px;height:34px;border-radius:10px;background:#f3e3cf;color:#9a622f;font-size:19px;font-weight:950}\n.orderReadinessMain{min-width:0}.orderReadinessMain strong{display:block;color:#343a3d;font-size:13px;font-weight:900;line-height:1.25}.orderReadinessMain>span{display:block;margin-top:3px;color:#777d7b;font-size:11px;line-height:1.35}\n.orderReadinessChips{display:flex;flex-wrap:wrap;gap:5px;margin-top:8px}.orderCheck{display:inline-flex;align-items:center;min-height:23px;padding:3px 7px;border:1px solid #e4ded5;border-radius:999px;background:#fff;color:#858a88;font-size:9px;font-weight:850;white-space:nowrap}.orderCheck.done{border-color:#cfe3d8;background:#edf7f1;color:#2c7757}\n.orderReadinessAction{min-height:38px;padding:0 12px;border:1px solid #ddd3c6;border-radius:10px;background:#fff;color:#6f512f;font-size:11px;font-weight:900;white-space:nowrap}.orderReadinessAction:hover{border-color:#cda980;background:#f8efe4}\n.orderReadiness.ready{border-color:#c9dfd3;background:linear-gradient(135deg,#f3faf6,#fbfdfb);box-shadow:0 5px 16px rgba(42,111,81,.06)}.orderReadiness.ready .orderReadinessIcon{background:#dff1e7;color:#267552}.orderReadiness.ready .orderReadinessAction{border-color:#bad6c8;background:#e9f5ee;color:#236a4b}\n@media(max-width:720px){.orderReadiness{grid-template-columns:auto minmax(0,1fr)}.orderReadinessAction{grid-column:1/-1;width:100%}}\n'''
css_path.write_text(css)

js_path = Path('assets/pallet3d-v10.js')
js = js_path.read_text()
old_js = "node.textContent=admin?'Pallet Tools · v1.0.22 · обновление №311':'Pallet Tools · v1.0.22';"
new_js = "node.textContent=admin?'Pallet Tools · v1.0.23 · обновление №315':'Pallet Tools · v1.0.23';"
if old_js not in js:
    raise SystemExit('JS version string not found')
js_path.write_text(js.replace(old_js, new_js, 1))
