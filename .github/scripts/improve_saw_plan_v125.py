from pathlib import Path
import re

index_path = Path('index.html')
index = index_path.read_text(encoding='utf-8')

pattern = re.compile(r'function renderStockBar\(bin,stock,usable,trim,index\)\{.*?\}\nfunction runSawOptimizer', re.S)
replacement = r'''function renderStockBar(bin,stock,usable,trim,index){
  const off=Math.max(0,bin.remaining),usableWidth=Math.max(1,usable),groups=[];
  bin.items.forEach(item=>{const last=groups[groups.length-1];if(last&&Math.abs(last.len-item.len)<.01)last.count++;else groups.push({len:item.len,count:1});});
  const used=bin.items.reduce((sum,item)=>sum+item.len,0);
  const pieces=groups.map(g=>{const total=g.len*g.count,pct=Math.max(1,(total/usableWidth)*100),label=g.count>1?`${g.count} × ${Math.round(g.len)} мм`:`${Math.round(g.len)} мм`;return `<span class="stockPiece stockPieceGroup" style="width:${pct}%" title="${label}">${label}</span>`;}).join("");
  const offPct=Math.max(0,(off/usableWidth)*100);
  return `<div class="stockBar"><div class="stockPieces">${pieces}</div>${offPct>0.3?`<span class="stockOffcut" style="width:${offPct}%" title="Остаток ${formatNumber(off,0)} мм"></span>`:""}</div><div class="stockMeta"><span><b>Доска ${index+1}</b> · ${bin.items.length} дет. · ${formatNumber(used,0)} мм деталей</span><span class="stockRemain">остаток <b>${formatNumber(off,0)} мм</b></span></div>`;
}
function runSawOptimizer'''
index, count = pattern.subn(replacement, index, count=1)
if count != 1:
    raise SystemExit('renderStockBar marker not found')

old_assign = 'document.getElementById("sawPlan").innerHTML=rendered.length?rendered.join(""):\'<div class="shopNote">Нет деталей для раскроя.</div>\';'
new_assign = 'const sawLegend=\'<div class="sawLegend"><span><i class="sawLegendPiece"></i>Коричневое — детали</span><span><i class="sawLegendOffcut"></i>Светлое — остаток</span><span><b>38 × 150 мм</b> = 38 деталей по 150 мм</span></div>\';document.getElementById("sawPlan").innerHTML=rendered.length?sawLegend+rendered.join(""):\'<div class="shopNote">Нет деталей для раскроя.</div>\';'
if old_assign not in index:
    raise SystemExit('sawPlan assignment marker not found')
index = index.replace(old_assign, new_assign, 1)

old_note = '<div class="shopNote">Алгоритм даёт практичный раскрой по длине с учётом ширины пропила. Перед запуском партии проверьте настройки конкретной пилы.</div>'
new_note = '<div class="shopNote">Каждая строка — одна доска сырья. Например, «38 × 150 мм» означает 38 деталей длиной 150 мм из этой доски. Светлая зона справа — остаток. Расчёт учитывает ширину пропила и торцовку.</div>'
if old_note not in index:
    raise SystemExit('saw note marker not found')
index = index.replace(old_note, new_note, 1)

css_override = r'''

/* sawPlanReadabilityV2 */
.sawLegend{position:sticky;top:0;z-index:5;display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin:0 0 10px;padding:10px 12px;border:1px solid #e1ddd5;border-radius:12px;background:rgba(255,255,255,.96);box-shadow:0 4px 12px rgba(35,40,43,.05);font-size:11px;color:#646b6e}
.sawLegend span{display:inline-flex;align-items:center;gap:6px;min-width:0}
.sawLegend i{display:inline-block;width:18px;height:10px;border-radius:4px;flex:0 0 auto}
.sawLegendPiece{background:linear-gradient(180deg,#cfaa72,#bc8d52)}
.sawLegendOffcut{background:repeating-linear-gradient(135deg,#dfe8e3 0 5px,#edf3ef 5px 10px);border:1px solid #ced9d3}
.stockBar{height:44px!important;border-radius:10px!important;background:#f1f3f1!important;margin:8px 0 5px!important}
.stockPieces{gap:3px!important;padding:3px!important;align-items:stretch!important}
.stockPiece.stockPieceGroup{min-width:44px!important;flex-shrink:1!important;padding:0 8px!important;font-size:11px!important;line-height:1.1!important;font-weight:850!important;letter-spacing:.01em!important;text-overflow:ellipsis!important;box-shadow:inset 0 -1px rgba(92,57,27,.12)!important}
.stockOffcut{opacity:.92!important;border-left:2px solid #c7d2cc!important}
.stockMeta{font-size:11px!important;line-height:1.35!important;color:#6f7778!important;align-items:center!important}
.stockMeta b{color:#343a3d!important;font-weight:850!important}
.stockRemain{margin-left:auto!important;padding:3px 7px!important;border-radius:999px!important;background:#f0f1ee!important;white-space:nowrap!important}
.stockRemain b{color:#70583f!important}
@media(max-width:560px){.sawLegend{position:static;padding:9px 10px;gap:7px;font-size:10px}.stockBar{height:40px!important}.stockPiece.stockPieceGroup{font-size:10px!important;min-width:36px!important;padding:0 5px!important}.stockMeta{font-size:10px!important;gap:5px!important}.stockRemain{margin-left:0!important}}
'''
if '/* sawPlanReadabilityV2 */' not in index:
    index = index.replace('</style>', css_override + '\n</style>', 1)

if 'assets/theme-industrial-v130.css?v=145' not in index:
    raise SystemExit('theme cache marker not found')
if 'assets/pallet3d-v10.js?v=141' not in index:
    raise SystemExit('js cache marker not found')
index = index.replace('assets/theme-industrial-v130.css?v=145','assets/theme-industrial-v130.css?v=146',1)
index = index.replace('assets/pallet3d-v10.js?v=141','assets/pallet3d-v10.js?v=142',1)
index_path.write_text(index, encoding='utf-8')

js_path = Path('assets/pallet3d-v10.js')
js = js_path.read_text(encoding='utf-8')
if 'Pallet Tools · v1.0.24 · обновление №321' not in js:
    raise SystemExit('js version marker not found')
js = js.replace('Pallet Tools · v1.0.24 · обновление №321','Pallet Tools · v1.0.25 · обновление №325')
js = js.replace("Pallet Tools · v1.0.24'","Pallet Tools · v1.0.25'")
js_path.write_text(js, encoding='utf-8')

theme_path = Path('assets/theme-industrial-v130.css')
theme = theme_path.read_text(encoding='utf-8')
if 'Pallet Tools · v1.0.24 · обновление №321' not in theme:
    raise SystemExit('theme version marker not found')
theme = theme.replace('Pallet Tools · v1.0.24 · обновление №321','Pallet Tools · v1.0.25 · обновление №325')
theme = theme.replace('Pallet Tools · v1.0.24','Pallet Tools · v1.0.25')
theme_path.write_text(theme, encoding='utf-8')

workflow = Path('.github/workflows/improve-saw-plan-v125.yml')
script = Path('.github/scripts/improve_saw_plan_v125.py')
if workflow.exists():
    workflow.unlink()
if script.exists():
    script.unlink()
