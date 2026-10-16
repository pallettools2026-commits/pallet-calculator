from pathlib import Path
import re

path = Path("index.html")
text = path.read_text(encoding="utf-8")

if "workshopHubV1" in text:
    print("Workshop tools already installed")
    raise SystemExit(0)

css = r'''
/* workshopHubV1 */
.workshopHub{margin:22px 0 20px;padding:22px;border:1px solid #dbe7e1;border-radius:22px;background:linear-gradient(180deg,#fff,#f8fbf9);box-shadow:0 12px 30px rgba(25,69,55,.07)}
.workshopTitle{display:flex;align-items:flex-start;justify-content:space-between;gap:14px;margin-bottom:16px}
.workshopTitle .eyebrow{font-size:11px;font-weight:900;letter-spacing:.13em;color:#1f6f5c;margin-bottom:5px}
.workshopTitle h2{margin:0 0 4px;font-size:25px;color:#173c33}
.workshopTitle p{margin:0;color:#66766e;font-size:13px;line-height:1.45;max-width:700px}
.shopPrimary,.shopGhost{border:0;border-radius:11px;padding:11px 14px;font-weight:800;cursor:pointer;transition:.16s;white-space:nowrap}
.shopPrimary{background:#176f4c;color:#fff;box-shadow:0 7px 17px rgba(23,111,76,.18)}
.shopPrimary:hover{filter:brightness(1.05);transform:translateY(-1px)}
.shopGhost{background:#eef4f1;color:#294d41;border:1px solid #d7e3dd}
.shopGhost:hover{background:#e5efea}
.shopKpis{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-bottom:14px}
.shopKpi{border:1px solid #dfe9e4;border-radius:14px;background:#fff;padding:13px}
.shopKpi small{display:block;color:#718078;font-size:10px;text-transform:uppercase;letter-spacing:.07em;font-weight:800}
.shopKpi strong{display:block;margin-top:4px;color:#143e31;font-size:23px;line-height:1.1}
.shopKpi span{display:block;margin-top:3px;color:#718078;font-size:11px}
.shopGrid{display:grid;grid-template-columns:minmax(0,.85fr) minmax(0,1.15fr);gap:14px;margin-top:14px}
.shopCard{border:1px solid #dfe8e3;border-radius:17px;background:#fff;padding:17px;min-width:0}
.shopCardHead{display:flex;align-items:flex-start;justify-content:space-between;gap:10px;margin-bottom:13px}
.shopCardHead h3{margin:0;color:#173c33;font-size:18px}
.shopCardHead p{margin:4px 0 0;color:#718078;font-size:12px;line-height:1.4}
.shopIcon{display:grid;place-items:center;flex:0 0 auto;width:42px;height:42px;border-radius:12px;background:#e6f3ed;color:#126541;font-size:21px}
.shopInputs{display:grid;grid-template-columns:repeat(2,1fr);gap:10px;margin-bottom:12px}
.shopInputs.four{grid-template-columns:repeat(4,1fr)}
.shopInputs label{font-size:11px}
.shopInputs input{min-height:42px;font-size:15px}
.shopInline{display:flex;align-items:end;gap:10px;flex-wrap:wrap}
.shopInline>div{flex:1 1 160px}
.sectionBreakdown{display:grid;gap:8px;margin-top:10px}
.sectionLine{display:grid;grid-template-columns:minmax(90px,.7fr) 1fr auto;gap:10px;align-items:center;border-top:1px solid #e7eeea;padding-top:8px}
.sectionLine:first-child{border-top:0;padding-top:0}
.sectionLine b{color:#1c4c3d}
.sectionLine small{color:#74827b}
.sectionLine strong{color:#173c33;white-space:nowrap}
.sawSummary{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin:12px 0}
.sawStat{background:#f4f8f6;border:1px solid #e0e9e4;border-radius:12px;padding:10px}
.sawStat small{display:block;color:#74827b;font-size:10px}
.sawStat b{display:block;color:#164536;font-size:18px;margin-top:2px}
.sawPlan{display:grid;gap:10px;margin-top:12px;max-height:520px;overflow:auto;padding-right:3px}
.sawGroup{border:1px solid #e0e9e4;border-radius:14px;padding:11px;background:#fbfdfc}
.sawGroupTitle{display:flex;justify-content:space-between;gap:8px;align-items:center;margin-bottom:8px}
.sawGroupTitle b{color:#173f33}
.sawGroupTitle span{font-size:11px;color:#6b7b73}
.stockBar{position:relative;height:30px;border-radius:8px;background:#e7eee9;overflow:hidden;margin:6px 0 3px;border:1px solid #dae5df}
.stockPieces{display:flex;height:100%;gap:1px;padding:2px}
.stockPiece{display:flex;align-items:center;justify-content:center;min-width:12px;border-radius:5px;background:linear-gradient(180deg,#cfaa72,#bc8d52);color:#fff;font-size:9px;font-weight:800;overflow:hidden;white-space:nowrap;padding:0 3px}
.stockOffcut{position:absolute;right:0;top:0;bottom:0;background:repeating-linear-gradient(135deg,#dfe8e3 0 6px,#edf3ef 6px 12px);border-left:1px solid #c9d7d0}
.stockMeta{display:flex;justify-content:space-between;gap:10px;color:#74827b;font-size:10px}
.moreBoards{font-size:11px;color:#6c7b74;margin-top:5px}
.presetRow{display:flex;gap:8px;flex-wrap:wrap}
.presetBtn{border:1px solid #cfe0d8;background:#f6faf8;color:#235447;border-radius:999px;padding:8px 11px;font-size:12px;font-weight:800;cursor:pointer}
.presetBtn:hover{background:#eaf4ef}
.shiftResult{border-radius:14px;background:linear-gradient(135deg,#123f33,#1a6650);color:#fff;padding:15px;margin-top:12px}
.shiftResult .big{font-size:26px;font-weight:900}
.shiftResult small{display:block;opacity:.76;margin-top:3px;line-height:1.4}
.shopNote{font-size:11px;color:#74827b;line-height:1.45;margin-top:9px}
@media(max-width:980px){.shopKpis{grid-template-columns:1fr 1fr}.shopGrid{grid-template-columns:1fr}.shopInputs.four{grid-template-columns:1fr 1fr}}
@media(max-width:560px){.workshopHub{padding:16px}.workshopTitle{flex-direction:column}.shopPrimary{width:100%}.shopKpis{grid-template-columns:1fr 1fr}.shopKpi strong{font-size:20px}.shopInputs,.shopInputs.four{grid-template-columns:1fr 1fr}.sawSummary{grid-template-columns:1fr 1fr}.sectionLine{grid-template-columns:1fr auto}.sectionLine small{grid-column:1/-1}.stockPiece{font-size:0}}
@media(max-width:380px){.shopKpis,.shopInputs,.shopInputs.four{grid-template-columns:1fr}}
@media print{.workshopHub{display:none!important}}
'''

nav_button = '''    <button class="navLink" type="button" data-scroll="workshop"><span class="navIcon">🪚</span>Распил</button>\n'''

html = r'''
<section class="workshopHub" id="workshop">
  <div class="workshopTitle">
    <div>
      <div class="eyebrow">ЦЕХ · ПИЛЕНИЕ · МАТЕРИАЛ</div>
      <h2>Инструменты производства</h2>
      <p>Расчёт пиломатериала, оптимизация распила досок с учётом пропила, контроль отходов и ориентировочный план загрузки пилы на смену.</p>
    </div>
    <button class="shopPrimary" id="shopRefresh" type="button">↻ Взять текущий расчёт</button>
  </div>
  <div class="shopKpis">
    <div class="shopKpi"><small>Пиломатериал</small><strong id="kpiM3">0 м³</strong><span>на текущий заказ</span></div>
    <div class="shopKpi"><small>Погонные метры</small><strong id="kpiLm">0 м</strong><span>всех деталей</span></div>
    <div class="shopKpi"><small>Деталей</small><strong id="kpiPieces">0</strong><span>нужно напилить</span></div>
    <div class="shopKpi"><small>Стоимость древесины</small><strong id="kpiCost">—</strong><span>по цене за м³</span></div>
  </div>
  <div class="shopGrid">
    <article class="shopCard">
      <div class="shopCardHead"><div><h3>Пиломатериал по сечениям</h3><p>Сводка толщины × ширины для закупки и подготовки сырья.</p></div><div class="shopIcon">🪵</div></div>
      <div class="shopInline"><div><label for="lumberPrice">Цена древесины за 1 м³</label><input id="lumberPrice" type="number" min="0" step="1" placeholder="Например, 250"></div><button class="shopGhost" id="recalcLumber" type="button">Пересчитать</button></div>
      <div class="sectionBreakdown" id="lumberSections"></div>
      <div class="shopNote">Стоимость — ориентировочная. Учитывается чистый объём деталей без припуска на пропил и торцовку.</div>
    </article>
    <article class="shopCard">
      <div class="shopCardHead"><div><h3>Оптимизатор распила досок</h3><p>Группирует детали по сечению и раскладывает их по стандартной длине доски.</p></div><div class="shopIcon">🪚</div></div>
      <div class="shopInputs four">
        <div><label for="stockLength">Длина сырья, мм</label><input id="stockLength" type="number" min="300" value="6000"></div>
        <div><label for="sawKerf">Пропил, мм</label><input id="sawKerf" type="number" min="0" step="0.1" value="4"></div>
        <div><label for="endTrim">Торцовка с края, мм</label><input id="endTrim" type="number" min="0" value="10"></div>
        <div><label for="keepOffcut">Сохранять остаток от, мм</label><input id="keepOffcut" type="number" min="0" value="500"></div>
      </div>
      <button class="shopPrimary" id="optimizeSaw" type="button">Рассчитать раскрой</button>
      <div class="sawSummary"><div class="sawStat"><small>Досок сырья</small><b id="sawBoards">—</b></div><div class="sawStat"><small>Выход материала</small><b id="sawYield">—</b></div><div class="sawStat"><small>Отход</small><b id="sawWaste">—</b></div><div class="sawStat"><small>Годных остатков</small><b id="sawOffcuts">—</b></div></div>
      <div class="sawPlan" id="sawPlan"><div class="shopNote">Нажмите «Рассчитать раскрой» — появится план по каждому сечению.</div></div>
      <div class="shopNote">Алгоритм даёт практичный раскрой по длине с учётом ширины пропила. Перед запуском партии проверьте настройки конкретной пилы.</div>
    </article>
  </div>
  <div class="shopGrid">
    <article class="shopCard">
      <div class="shopCardHead"><div><h3>Быстрые размеры поддона</h3><p>Меняет только габарит поддона. Автоматические длины деталей обновляются сами.</p></div><div class="shopIcon">📐</div></div>
      <div class="presetRow"><button class="presetBtn" data-pl="1200" data-pw="800" type="button">EUR / EPAL · 1200×800</button><button class="presetBtn" data-pl="1200" data-pw="1000" type="button">1200×1000</button><button class="presetBtn" data-pl="1250" data-pw="1180" type="button">1250×1180</button><button class="presetBtn" data-pl="1140" data-pw="1140" type="button">1140×1140</button></div>
      <div class="shopNote">Это только быстрый выбор внешнего размера, а не готовая сертифицированная конструкция поддона.</div>
    </article>
    <article class="shopCard">
      <div class="shopCardHead"><div><h3>План загрузки пилы на смену</h3><p>Оценивает, сколько времени займёт текущий раскрой на одном рабочем месте.</p></div><div class="shopIcon">⏱</div></div>
      <div class="shopInputs"><div><label for="cutsPerMin">Средняя скорость, резов/мин</label><input id="cutsPerMin" type="number" min="0.1" step="0.1" value="6"></div><div><label for="shiftHours">Смена, часов</label><input id="shiftHours" type="number" min="1" step="0.5" value="8"></div><div><label for="downtimePct">Простои, %</label><input id="downtimePct" type="number" min="0" max="90" value="15"></div><div><label for="operatorsCount">Рабочих мест / пил</label><input id="operatorsCount" type="number" min="1" value="1"></div></div>
      <button class="shopGhost" id="calcShift" type="button">Рассчитать смену</button>
      <div class="shiftResult" id="shiftResult"><div class="big">Сначала рассчитайте раскрой</div><small>После этого здесь появится оценка времени и загрузки смены.</small></div>
    </article>
  </div>
</section>
'''

js = r'''
/* workshopHubV1 */
let lastSawStats=null;
function workshopParts(){const q=Number(document.getElementById("qty")?.value||0);if(!q||q<1)return [];return data.map((p,i)=>{const per=Number(document.getElementById("n"+i)?.value||0),t=Number(document.getElementById("t"+i)?.value||0),w=Number(document.getElementById("w"+i)?.value||0),l=Number(document.getElementById("l"+i)?.value||0);return {name:p[0],per,qty:Math.max(0,Math.round(per*q)),t,w,l,section:`${t}×${w}`};}).filter(x=>x.qty>0&&x.t>0&&x.w>0&&x.l>0);}
function formatNumber(v,d=2){return Number(v||0).toLocaleString("ru-RU",{maximumFractionDigits:d});}
function updateLumberSummary(){const parts=workshopParts();let m3=0,lm=0,pieces=0;const sections=new Map();parts.forEach(p=>{const volume=p.t*p.w*p.l*p.qty/1e9,linear=p.l*p.qty/1000;m3+=volume;lm+=linear;pieces+=p.qty;const s=sections.get(p.section)||{m3:0,lm:0,pieces:0};s.m3+=volume;s.lm+=linear;s.pieces+=p.qty;sections.set(p.section,s);});const price=Math.max(0,Number(document.getElementById("lumberPrice")?.value||0));document.getElementById("kpiM3").textContent=`${formatNumber(m3,3)} м³`;document.getElementById("kpiLm").textContent=`${formatNumber(lm,1)} м`;document.getElementById("kpiPieces").textContent=pieces.toLocaleString("ru-RU");document.getElementById("kpiCost").textContent=price?formatNumber(m3*price,2):"—";const box=document.getElementById("lumberSections");if(!box)return;if(!sections.size){box.innerHTML='<div class="shopNote">Нет деталей для расчёта.</div>';return;}box.innerHTML=[...sections.entries()].sort((a,b)=>b[1].m3-a[1].m3).map(([key,s])=>`<div class="sectionLine"><b>${key} мм</b><small>${s.pieces.toLocaleString("ru-RU")} шт. · ${formatNumber(s.lm,1)} пог. м</small><strong>${formatNumber(s.m3,3)} м³</strong></div>`).join("");}
function optimizeSection(pieces,stock,kerf,trim){const usable=stock-2*trim,items=[];pieces.forEach(p=>{for(let i=0;i<p.qty;i++)items.push({len:p.l,name:p.name});});items.sort((a,b)=>b.len-a.len);const bins=[],overs=[];items.forEach(item=>{if(item.len>usable){overs.push(item);return;}let best=-1,bestRemain=Infinity;for(let i=0;i<bins.length;i++){const b=bins[i],extra=item.len+(b.items.length?kerf:0);if(extra<=b.remaining+1e-9){const r=b.remaining-extra;if(r<bestRemain){best=i;bestRemain=r;}}}if(best<0)bins.push({items:[item],remaining:usable-item.len});else{const b=bins[best],extra=item.len+(b.items.length?kerf:0);b.items.push(item);b.remaining-=extra;}});return {bins,overs,usable};}
function renderStockBar(bin,stock,usable,trim,index){const off=Math.max(0,bin.remaining),usableWidth=Math.max(1,usable);const pieces=bin.items.map(x=>{const pct=Math.max(2,(x.len/usableWidth)*100);return `<span class="stockPiece" style="width:${pct}%">${Math.round(x.len)}</span>`;}).join("");const offPct=Math.max(0,(off/usableWidth)*100);return `<div class="stockBar"><div class="stockPieces">${pieces}</div>${offPct>0.3?`<span class="stockOffcut" style="width:${offPct}%"></span>`:""}</div><div class="stockMeta"><span>Доска ${index+1} · ${bin.items.length} дет.</span><span>остаток ${formatNumber(off,0)} мм</span></div>`;}
function runSawOptimizer(){updateLumberSummary();const parts=workshopParts(),stock=Math.max(1,Number(document.getElementById("stockLength")?.value||6000)),kerf=Math.max(0,Number(document.getElementById("sawKerf")?.value||0)),trim=Math.max(0,Number(document.getElementById("endTrim")?.value||0)),keep=Math.max(0,Number(document.getElementById("keepOffcut")?.value||0));const groups=new Map();parts.forEach(p=>{const a=groups.get(p.section)||[];a.push(p);groups.set(p.section,a);});let boards=0,totalStock=0,totalPart=0,offcuts=0,totalCuts=0,overs=0;const rendered=[];groups.forEach((gp,key)=>{const res=optimizeSection(gp,stock,kerf,trim);boards+=res.bins.length;totalStock+=res.bins.length*stock;gp.forEach(p=>{totalPart+=p.l*p.qty;totalCuts+=p.qty;});res.bins.forEach(b=>{if(b.remaining>=keep)offcuts++;});overs+=res.overs.length;const preview=res.bins.slice(0,12).map((b,i)=>renderStockBar(b,stock,res.usable,trim,i)).join("");rendered.push(`<div class="sawGroup"><div class="sawGroupTitle"><b>${key} мм</b><span>${res.bins.length} досок сырья${res.overs.length?` · ⚠ ${res.overs.length} не помещ.`:""}</span></div>${preview}${res.bins.length>12?`<div class="moreBoards">Показаны первые 12 из ${res.bins.length} досок.</div>`:""}</div>`);});const yieldPct=totalStock?totalPart/totalStock*100:0,wastePct=totalStock?100-yieldPct:0;if(trim>0)totalCuts+=boards*2;document.getElementById("sawBoards").textContent=boards?boards.toLocaleString("ru-RU"):"—";document.getElementById("sawYield").textContent=boards?`${formatNumber(yieldPct,1)}%`:"—";document.getElementById("sawWaste").textContent=boards?`${formatNumber(wastePct,1)}%`:"—";document.getElementById("sawOffcuts").textContent=boards?offcuts.toLocaleString("ru-RU"):"—";document.getElementById("sawPlan").innerHTML=rendered.length?rendered.join(""):'<div class="shopNote">Нет деталей для раскроя.</div>';lastSawStats={boards,totalCuts,yieldPct,wastePct,offcuts,overs};updateShiftPlan();}
function updateShiftPlan(){const box=document.getElementById("shiftResult");if(!box)return;if(!lastSawStats||!lastSawStats.totalCuts){box.innerHTML='<div class="big">Сначала рассчитайте раскрой</div><small>После этого появится оценка времени.</small>';return;}const cpm=Math.max(.1,Number(document.getElementById("cutsPerMin")?.value||6)),hours=Math.max(1,Number(document.getElementById("shiftHours")?.value||8)),downtime=Math.min(90,Math.max(0,Number(document.getElementById("downtimePct")?.value||0))),stations=Math.max(1,Math.round(Number(document.getElementById("operatorsCount")?.value||1))),workMinutes=hours*60*(1-downtime/100)*stations,needMinutes=lastSawStats.totalCuts/cpm,shifts=needMinutes/workMinutes,load=workMinutes?needMinutes/workMinutes*100:0,verdict=load<=100?"План помещается в смену":"Нужно больше одной смены";box.innerHTML=`<div class="big">${verdict}</div><small>${lastSawStats.totalCuts.toLocaleString("ru-RU")} резов ≈ ${formatNumber(needMinutes/60,1)} ч работы пилы. Загрузка доступной мощности: ${formatNumber(load,0)}%. Эквивалент смен: ${formatNumber(shifts,2)}.</small>`;}
document.getElementById("shopRefresh")?.addEventListener("click",()=>{updateLumberSummary();runSawOptimizer();});
document.getElementById("recalcLumber")?.addEventListener("click",updateLumberSummary);
document.getElementById("lumberPrice")?.addEventListener("input",updateLumberSummary);
document.getElementById("optimizeSaw")?.addEventListener("click",runSawOptimizer);
document.getElementById("calcShift")?.addEventListener("click",updateShiftPlan);
["cutsPerMin","shiftHours","downtimePct","operatorsCount"].forEach(id=>document.getElementById(id)?.addEventListener("input",()=>{if(lastSawStats)updateShiftPlan();}));
document.querySelectorAll(".presetBtn").forEach(btn=>btn.addEventListener("click",()=>{document.getElementById("pL").value=btn.dataset.pl;document.getElementById("pW").value=btn.dataset.pw;syncAutoLengths();calc();updateLumberSummary();lastSawStats=null;document.getElementById("sawPlan").innerHTML='<div class="shopNote">Размер изменён. Нажмите «Рассчитать раскрой» для нового плана.</div>'; }));
document.addEventListener("input",e=>{if(e.target?.closest?.("#protectedApp")&&/^([ntwl]\d+|pL|pW|qty)$/.test(e.target.id||"")){updateLumberSummary();lastSawStats=null;}});
'''

text = text.replace("</style>", css + "\n</style>", 1)
m = re.search(r'(\s*<button class="navLink adminNav"[^>]*id="adminNav")', text)
if m:
    text = text[:m.start()] + "\n" + nav_button + text[m.start():]
else:
    print("WARN: admin nav marker not found")
m = re.search(r'<section class="savedBox"', text)
if not m:
    raise RuntimeError("savedBox marker not found")
text = text[:m.start()] + html + "\n\n" + text[m.start():]
marker = "syncAutoLengths();"
pos = text.rfind(marker)
if pos < 0:
    raise RuntimeError("startup marker not found")
text = text[:pos] + js + "\n\n" + text[pos:]
path.write_text(text, encoding="utf-8")
print("Workshop tools installed")
