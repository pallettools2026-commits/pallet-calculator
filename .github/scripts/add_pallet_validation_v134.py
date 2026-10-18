from pathlib import Path
import re

js_path = Path('assets/pallet3d-v10.js')
css_path = Path('assets/theme-industrial-v130.css')
index_path = Path('index.html')

js = js_path.read_text(encoding='utf-8')
css = css_path.read_text(encoding='utf-8')
index = index_path.read_text(encoding='utf-8')

if 'palletValidationV1134' not in js:
    old = "  if(typeof state.showComposition!=='boolean')state.showComposition=false;\n"
    new = old + "  if(typeof state.showValidation!=='boolean')state.showValidation=false;\n"
    if old not in js:
        raise SystemExit('state insertion marker not found')
    js = js.replace(old, new, 1)

    old_sig = "+'|'+(state.showComposition?'composition':'model')+'|assembly:'+(state.assemblyStep||0)+'|'"
    new_sig = "+'|'+(state.showComposition?'composition':'model')+'|validation:'+(state.showValidation?'open':'closed')+'|assembly:'+(state.assemblyStep||0)+'|'"
    if old_sig not in js:
        raise SystemExit('signature marker not found')
    js = js.replace(old_sig, new_sig, 1)

    validation_code = r'''    /* palletValidationV1134 — automatic construction checks */
    const validationIssues=[];
    const addValidationIssue=(level,title,detail,target='')=>validationIssues.push({level,title,detail,target});
    const rawCross=Math.max(0,Math.round(num(bindParts[0].n)))+Math.max(0,Math.round(num(bindParts[1].n)));
    const rawRunner=Math.max(0,Math.round(num(runnerParts[0].n)))+Math.max(0,Math.round(num(runnerParts[1].n)));
    const rawOrderQty=num(el('qty')?.value,1);
    const densityInput=el('smartDensity');
    const densityRaw=densityInput?num(densityInput.value,500):500;

    if(rawOrderQty<=0)addValidationIssue('error','Количество заказа должно быть больше нуля','Укажите минимум 1 поддон в заказе.','qty');
    if(rawDeck<=0)addValidationIssue('error','Настил отсутствует','Добавьте хотя бы одну доску настила.','n0');
    if(rawDeck>profile.deckMax)addValidationIssue('error','Слишком много досок настила',`Для этой схемы максимум ${profile.deckMax} шт., сейчас указано ${rawDeck}.`,'n0');
    if(deckCount>1&&gapBad)addValidationIssue('error','Настил не помещается',`Доски перекрываются примерно на ${fmtMm(Math.abs(rawGapMm))} мм. Уменьшите ширину доски или количество настила.`,'w0');
    if(deckCount>1&&!gapBad&&rawGapMm>100)addValidationIssue('warn','Слишком большой зазор настила',`Текущий зазор около ${fmtMm(rawGapMm)} мм. Проверьте ширину и количество досок.`,'w0');
    if(rawCross<=0)addValidationIssue('error','Поперечины отсутствуют','Для сборки поддона нужны поперечины.','n1');
    else if(rawCross!==profile.bindingCount)addValidationIssue('warn','Количество поперечин отличается от 3D-схемы',`В расчёте ${rawCross} шт., стандартная 3D-схема использует ${profile.bindingCount} шт.`,'n1');
    if(rawRunner<=0)addValidationIssue('error','Лыжи отсутствуют','Добавьте лыжи для нижней части поддона.','n3');
    else if(rawRunner!==profile.runnerLengths.length)addValidationIssue('warn','Количество лыж отличается от 3D-схемы',`В расчёте ${rawRunner} шт., стандартная 3D-схема использует ${profile.runnerLengths.length} шт.`,'n3');
    if(rawBlocks<=0)addValidationIssue('error','Шашки отсутствуют','Добавьте шашки между лыжами и поперечинами.','n5');
    else if(rawBlocks!==9)addValidationIssue('warn','Нестандартное количество шашек',`Сейчас ${rawBlocks} шт. Для стандартной схемы ожидается 9 шт.`,'n5');

    P.forEach((p,i)=>{
      const q=Math.max(0,Math.round(num(p.n,0)));if(!q)return;
      const dims=[['t','толщина'],['w','ширина'],['l','длина']];
      dims.forEach(([key,label])=>{if(num(p[key],0)<=0)addValidationIssue('error',`${partNames[i]||`Деталь ${i+1}`}: неверный размер`,`Поле «${label}» должно быть больше 0 мм.`,`${key}${i}`);});
    });
    if(rawDeck>0&&deckLengthMm>profile.length+2)addValidationIssue('warn','Настил длиннее габарита поддона',`Длина доски ${fmtMm(deckLengthMm)} мм, габарит поддона ${fmtMm(profile.length)} мм.`,'l0');
    if(rawDeck>0&&deckLengthMm<profile.length-2)addValidationIssue('warn','Настил короче габарита поддона',`Длина доски ${fmtMm(deckLengthMm)} мм, габарит поддона ${fmtMm(profile.length)} мм.`,'l0');
    if(densityInput&&(densityRaw<250||densityRaw>1000))addValidationIssue('warn','Проверьте плотность древесины',`Указано ${fmtMm(densityRaw)} кг/м³. Рабочий диапазон калькулятора: 250–1000 кг/м³.`,'smartDensity');

    const validationErrors=validationIssues.filter(x=>x.level==='error').length;
    const validationWarnings=validationIssues.filter(x=>x.level==='warn').length;
    const validationStatus=validationErrors?'error':validationWarnings?'warn':'ok';
    const validationButtonLabel=validationErrors?`Ошибки ${validationErrors}`:validationWarnings?`Внимание ${validationWarnings}`:'Проверка ✓';
    const validationSummary=validationErrors?`${validationErrors} критич. · ${validationWarnings} предупрежд.`:validationWarnings?`${validationWarnings} предупрежд.`:'Ошибок не найдено';
    const validationPanel=state.showValidation?`<section class="palletValidationPanel ${validationStatus}" aria-label="Контроль ошибок конструкции"><div class="palletValidationHead"><div><small>КОНТРОЛЬ КОНСТРУКЦИИ</small><strong>${validationErrors?'Нужно исправить ошибки':validationWarnings?'Есть моменты для проверки':'Конструкция выглядит корректно'}</strong></div><span>${validationSummary}</span></div>${validationIssues.length?`<div class="palletValidationList">${validationIssues.map(issue=>`<button type="button" class="palletValidationIssue ${issue.level}" ${issue.target?`data-validation-target="${issue.target}"`:''}><i>${issue.level==='error'?'!':'?'}</i><span><b>${issue.title}</b><em>${issue.detail}</em></span>${issue.target?'<strong>Исправить →</strong>':''}</button>`).join('')}</div>`:`<div class="palletValidationOk"><b>✓ Основные проверки пройдены</b><span>Габариты, состав и размеры деталей не содержат очевидных конфликтов.</span></div>`}<div class="palletValidationFoot">Проверяется автоматически при каждом изменении размеров и количества деталей.</div></section>`:'';
'''
    marker = "    const assemblySteps=[\n"
    if marker not in js:
        raise SystemExit('validation insertion marker not found')
    js = js.replace(marker, validation_code + marker, 1)

    toolbar_marker = '>Состав</button></div>${assemblyPanel}'
    toolbar_replacement = '>Состав</button><button type="button" data-p3d-validation aria-pressed="${state.showValidation?\'true\':\'false\'}" class="palletValidationButton ${validationStatus} ${state.showValidation?\'active\':\'\'}">${validationButtonLabel}</button></div>${validationPanel}${assemblyPanel}'
    if toolbar_marker not in js:
        raise SystemExit('toolbar marker not found')
    js = js.replace(toolbar_marker, toolbar_replacement, 1)

    event_marker = "    root.querySelector('[data-p3d-composition]')?.addEventListener('click',()=>{state.showComposition=!state.showComposition;render(num(el('pL')?.value),num(el('pW')?.value));});\n"
    event_code = r'''    root.querySelector('[data-p3d-validation]')?.addEventListener('click',()=>{state.showValidation=!state.showValidation;render(num(el('pL')?.value),num(el('pW')?.value));});
    root.querySelectorAll('[data-validation-target]').forEach(btn=>btn.addEventListener('click',()=>{const target=el(btn.dataset.validationTarget);if(!target)return;target.scrollIntoView?.({behavior:'smooth',block:'center'});setTimeout(()=>{target.focus?.();target.select?.();},260);}));
'''
    if event_marker not in js:
        raise SystemExit('validation event marker not found')
    js = js.replace(event_marker, event_marker + event_code, 1)

css_marker = '/* palletValidationV1134 */'
if css_marker not in css:
    css += r'''

/* palletValidationV1134 */
#palletPreview3D .palletValidationButton{min-width:94px;font-weight:900!important}
#palletPreview3D .palletValidationButton.ok{border-color:#b9d2be!important;background:#eef7f0!important;color:#376543!important}
#palletPreview3D .palletValidationButton.warn{border-color:#e2c38d!important;background:#fff7e8!important;color:#8a5d18!important}
#palletPreview3D .palletValidationButton.error{border-color:#ddb0aa!important;background:#fff0ee!important;color:#9b3d34!important}
#palletPreview3D .palletValidationButton.ok.active{background:#dfeee2!important;box-shadow:0 0 0 2px rgba(67,116,78,.10)!important}
#palletPreview3D .palletValidationButton.warn.active{background:#f7e8c8!important;box-shadow:0 0 0 2px rgba(166,111,28,.10)!important}
#palletPreview3D .palletValidationButton.error.active{background:#f5dcd8!important;box-shadow:0 0 0 2px rgba(155,61,52,.10)!important}
.palletValidationPanel{margin:9px 0 3px;border:1px solid #ded7cf;border-radius:14px;background:#fffdf9;box-shadow:0 8px 22px rgba(72,53,38,.07);overflow:hidden;color:#3c342d}
.palletValidationPanel.error{border-color:#e2bbb6}.palletValidationPanel.warn{border-color:#e5cfaa}.palletValidationPanel.ok{border-color:#c8d9cb}
.palletValidationHead{display:flex;justify-content:space-between;gap:12px;align-items:flex-start;padding:12px 13px;border-bottom:1px solid #eee6dd;background:#faf6f1}
.palletValidationHead small{display:block;margin-bottom:3px;color:#9d795a;font-size:8px;font-weight:950;letter-spacing:.13em}
.palletValidationHead strong{display:block;color:#382f28;font-size:14px;line-height:1.2}
.palletValidationHead>span{flex:0 0 auto;padding:5px 8px;border-radius:999px;background:#fff;border:1px solid #e5ddd4;color:#796b60;font-size:8px;font-weight:900;white-space:nowrap}
.palletValidationPanel.error .palletValidationHead>span{border-color:#e2bbb6;background:#fff2f0;color:#963c34}
.palletValidationPanel.warn .palletValidationHead>span{border-color:#e5cb9d;background:#fff8e9;color:#88601e}
.palletValidationPanel.ok .palletValidationHead>span{border-color:#c6d8ca;background:#f1f8f2;color:#426e4b}
.palletValidationList{display:grid;gap:0}
.palletValidationIssue{display:grid;grid-template-columns:28px minmax(0,1fr) auto;gap:9px;align-items:center;width:100%;padding:10px 12px;border:0;border-bottom:1px solid #eee8e1;border-radius:0;background:#fff;text-align:left;box-shadow:none;cursor:pointer}
.palletValidationIssue:last-child{border-bottom:0}
.palletValidationIssue>i{display:grid;place-items:center;width:24px;height:24px;border-radius:50%;font-size:12px;font-style:normal;font-weight:950}
.palletValidationIssue.error>i{background:#f7dfdc;color:#a5453a}.palletValidationIssue.warn>i{background:#faedcf;color:#97671c}
.palletValidationIssue span{min-width:0}.palletValidationIssue span b{display:block;color:#493d34;font-size:10px;line-height:1.25}.palletValidationIssue span em{display:block;margin-top:2px;color:#81746a;font-size:9px;font-style:normal;font-weight:700;line-height:1.35}
.palletValidationIssue>strong{color:#956238;font-size:8px;font-weight:900;white-space:nowrap}
.palletValidationIssue:hover{background:#fffaf4}
.palletValidationOk{display:grid;gap:3px;padding:13px}.palletValidationOk b{color:#477151;font-size:11px}.palletValidationOk span{color:#7c746d;font-size:9px;line-height:1.4}
.palletValidationFoot{padding:8px 12px;border-top:1px solid #eee7df;background:#faf7f3;color:#91867c;font-size:8px;font-weight:750;line-height:1.3}
html[data-theme="dark"] .palletValidationPanel{background:#2b2723;border-color:#4d433b;color:#eee3d7}
html[data-theme="dark"] .palletValidationHead{background:#332d28;border-color:#4a413a}
html[data-theme="dark"] .palletValidationHead strong{color:#f3e8dc}
html[data-theme="dark"] .palletValidationIssue{background:#2c2824;border-color:#423a34}
html[data-theme="dark"] .palletValidationIssue:hover{background:#352e28}
html[data-theme="dark"] .palletValidationIssue span b{color:#eee2d6}
html[data-theme="dark"] .palletValidationIssue span em{color:#b7aba0}
html[data-theme="dark"] .palletValidationFoot{background:#302a25;border-color:#463d36;color:#a99d92}
html[data-theme="dark"] .palletValidationOk b{color:#9fc7a6}
html[data-theme="dark"] .palletValidationOk span{color:#b8aea4}
@media(max-width:620px){
  #palletPreview3D .palletValidationButton{min-width:0}
  .palletValidationHead{display:grid;gap:7px;padding:10px}
  .palletValidationHead>span{justify-self:start}
  .palletValidationIssue{grid-template-columns:26px minmax(0,1fr);padding:10px}
  .palletValidationIssue>strong{grid-column:2;margin-top:1px}
  .palletValidationFoot{padding:8px 10px}
}
'''

# Bump both cache-busting query strings if they are present.
def bump_asset_version(text, asset_pattern):
    m = re.search(asset_pattern + r'\?v=(\d+)', text)
    if not m:
        return text
    old = int(m.group(1))
    return text[:m.start(1)] + str(old + 1) + text[m.end(1):]

index = bump_asset_version(index, r'assets/pallet3d-v10\.js')
index = bump_asset_version(index, r'assets/theme-industrial-v130\.css')

js_path.write_text(js, encoding='utf-8')
css_path.write_text(css, encoding='utf-8')
index_path.write_text(index, encoding='utf-8')
print('pallet validation v134 applied')
