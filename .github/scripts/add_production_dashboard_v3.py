from pathlib import Path

path=Path('index.html')
text=path.read_text(encoding='utf-8')
if 'productionDashboardV3' in text:
    raise SystemExit('productionDashboardV3 already installed')

account_marker='  <button class="topAccount" id="topAccount" type="button" title="Аккаунт">'
if account_marker not in text:
    raise SystemExit('top account marker not found')
header_extra=r'''  <div class="appTopTools">
    <div class="appSearch"><span>⌕</span><input id="appSearchInput" type="search" placeholder="Поиск по заказам, размерам, материалам…"></div>
    <div class="appTopChip"><span>▣</span><div><small>Сегодня</small><b id="dashboardToday">—</b></div></div>
    <div class="appTopChip shift"><span class="liveDot"></span><div><small>Текущая смена</small><b id="dashboardShift">Смена</b></div></div>
  </div>
'''
text=text.replace(account_marker,header_extra+account_marker,1)

protected='<div id="protectedApp" class="appLocked">'
if protected not in text:
    raise SystemExit('protected app marker not found')

dashboard=r'''
<!-- productionDashboardV3 -->
<aside class="appSidebar" aria-label="Разделы Pallet Tools">
  <div class="sideBrand"><img src="assets/pallet-clean-3d-2.webp" alt=""><div><strong>Pallet Tools</strong><span>производство поддонов</span></div></div>
  <nav class="sideNav">
    <button class="navLink appSideLink active" type="button" data-scroll="productionDashboard"><span>⌂</span>Обзор</button>
    <button class="navLink appSideLink" type="button" data-scroll="production"><span>▥</span>Производство</button>
    <button class="navLink appSideLink" type="button" data-scroll="calculator"><span>▦</span>Калькулятор</button>
    <button class="navLink appSideLink" type="button" data-scroll="workshop"><span>⌁</span>Распил досок</button>
    <button class="navLink appSideLink" type="button" data-scroll="savedBox"><span>▤</span>Мои расчёты</button>
    <button class="navLink appSideLink adminSideLink" type="button" data-scroll="adminPanel"><span>⚙</span>Админ-панель</button>
  </nav>
  <div class="sideFactoryCard"><span>🪵</span><b>Цех под контролем</b><small>Расчёт, распил и производство в одном месте.</small></div>
  <div class="sideVersion">Pallet Tools · 2026</div>
</aside>

<section class="productionDashboardV3" id="productionDashboard">
  <div class="dashIntro">
    <div><div class="dashEyebrow">РАБОЧИЙ ЦЕНТР</div><h1>Панель производства</h1><p>Текущий заказ, загрузка пиления и основные показатели цеха.</p></div>
    <div class="dashIntroActions"><button type="button" data-jump="calculator">+ Новый расчёт</button><button class="secondary" type="button" data-jump="workshop">Открыть распил →</button></div>
  </div>

  <div class="dashKpis">
    <article class="dashKpi"><div class="dashKpiIcon green">▤</div><div><small>Текущий заказ</small><strong id="dashOrder">Без номера</strong><span id="dashOrderDate">Укажите заказ</span></div></article>
    <article class="dashKpi"><div class="dashKpiIcon wood">▦</div><div><small>Поддонов в партии</small><strong id="dashQty">0 шт.</strong><span id="dashSize">— × — мм</span></div></article>
    <article class="dashKpi"><div class="dashKpiIcon blue">✓</div><div><small>Готовность</small><strong id="dashReady">0%</strong><span id="dashReadyText">Статус производства</span></div></article>
    <article class="dashKpi"><div class="dashKpiIcon amber">⌁</div><div><small>Пиломатериал</small><strong id="dashWood">0 м³</strong><span id="dashBoards">раскрой не рассчитан</span></div></article>
  </div>

  <div class="dashLayout">
    <div class="dashMainCol">
      <article class="dashPanel currentOrderPanel">
        <div class="dashPanelHead"><div><span class="dashPanelIcon">▤</span><div><h3>Активный заказ</h3><p>Данные берутся из текущего расчёта Pallet Tools.</p></div></div><button type="button" data-jump="calculator">Изменить →</button></div>
        <div class="orderFocus">
          <img src="assets/pallet-clean-3d-2.webp" alt="Чистый деревянный поддон">
          <div class="orderFocusMain"><div class="orderBadges"><span class="statusLive">● В работе</span><span id="dashOrderBadge">Новый заказ</span></div><h2 id="dashOrderTitle">Поддон 1250 × 1180</h2><p id="dashOrderMeta">Заполните номер заказа и данные смены.</p><div class="orderProgress"><div class="orderProgressTop"><span>Выполнение</span><b id="dashProgressLabel">0 / 100</b></div><div class="dashBar"><i id="dashProgressBar" style="width:0%"></i></div></div></div>
          <div class="orderFocusAside"><small>Ответственный</small><b id="dashWorker">Не указан</b><small>Дата</small><b id="dashWorkDate">—</b></div>
        </div>
      </article>

      <div class="dashMiniGrid">
        <article class="dashPanel compact"><div class="dashPanelHead"><div><span class="dashPanelIcon">⌁</span><div><h3>Очередь пиления</h3><p>Текущий план раскроя</p></div></div><button type="button" data-jump="workshop">Распил →</button></div><div class="miniMetric"><strong id="dashSawBoards">—</strong><span>досок сырья</span></div><div class="miniBar"><i id="dashSawYieldBar" style="width:0%"></i></div><div class="miniFoot"><span>Выход материала</span><b id="dashSawYield">—</b></div></article>
        <article class="dashPanel compact"><div class="dashPanelHead"><div><span class="dashPanelIcon">◫</span><div><h3>Смена</h3><p>Производственный поток</p></div></div><button type="button" data-jump="production">Подробнее →</button></div><div class="shiftMini"><div><small>Напилено</small><b id="dashCut">0</b></div><div><small>Собрано</small><b id="dashAssembled">0</b></div><div><small>ОТК</small><b id="dashQc">0</b></div></div></article>
      </div>
    </div>

    <div class="dashSideCol">
      <article class="dashPanel palletViewPanel"><div class="dashPanelHead"><div><span class="dashPanelIcon">◇</span><div><h3>Вид поддона</h3><p id="dashPreviewSize">1250 × 1180 мм</p></div></div><button type="button" data-jump="calculator">Открыть</button></div><div class="dashPalletImage"><img src="assets/pallet-clean-3d-2.webp" alt="Деревянный поддон"></div></article>
      <article class="dashPanel quickPanel"><div class="dashPanelHead"><div><span class="dashPanelIcon">⚡</span><div><h3>Быстрые действия</h3><p>Основные инструменты</p></div></div></div><div class="quickGrid"><button type="button" data-jump="calculator"><span>▦</span>Расчёт поддона</button><button type="button" data-jump="workshop"><span>⌁</span>План распила</button><button type="button" data-jump="production"><span>▥</span>Статус заказа</button><button type="button" data-jump="savedBox"><span>▤</span>Мои расчёты</button></div></article>
    </div>
  </div>
</section>
'''
text=text.replace(protected,protected+dashboard,1)

css=r'''

/* productionDashboardV3 */
.siteHero{display:none!important}.navLinks{display:none!important}
.appTopTools{display:flex;align-items:center;justify-content:center;gap:10px;min-width:0}.appSearch{height:44px;min-width:260px;max-width:520px;flex:1;display:flex;align-items:center;gap:9px;border:1px solid #dfe7e3;background:#f8faf9;border-radius:11px;padding:0 12px}.appSearch span{font-size:20px;color:#597068}.appSearch input{min-height:0;height:38px;padding:0;border:0;background:transparent;font-size:13px;box-shadow:none}.appSearch input:focus{box-shadow:none}.appTopChip{height:44px;display:flex;align-items:center;gap:8px;border:1px solid #dfe7e3;border-radius:11px;background:#fff;padding:6px 11px;color:#315248}.appTopChip small{display:block;font-size:9px;color:#839089}.appTopChip b{display:block;font-size:11px;white-space:nowrap}.liveDot{width:9px;height:9px;border-radius:50%;background:#20a466;box-shadow:0 0 0 4px #e4f6ed}
#protectedApp{position:relative;margin-left:230px;min-width:0}.appSidebar{position:fixed;z-index:45;left:0;top:84px;bottom:0;width:218px;padding:18px 13px 16px;background:linear-gradient(180deg,#103d32,#0b2e27 75%,#102f28);color:#fff;display:flex;flex-direction:column;box-shadow:10px 0 30px rgba(12,43,35,.08)}.sideBrand{display:none}.sideNav{display:grid;gap:6px}.appSideLink{width:100%;justify-content:flex-start!important;gap:11px!important;border:0!important;border-radius:11px!important;padding:12px 13px!important;color:#dbeae4!important;background:transparent!important;font-size:13px!important;font-weight:750!important;text-align:left}.appSideLink span{display:inline-grid;place-items:center;width:22px;font-size:17px}.appSideLink:hover,.appSideLink.active{background:rgba(255,255,255,.11)!important;color:#fff!important}.appSideLink.active{box-shadow:inset 3px 0 #4bd18e}.adminSideLink{display:none}.sideFactoryCard{margin-top:auto;border:1px solid rgba(255,255,255,.10);border-radius:14px;padding:13px;background:linear-gradient(145deg,rgba(255,255,255,.08),rgba(194,146,83,.10))}.sideFactoryCard span{font-size:25px}.sideFactoryCard b{display:block;margin-top:6px;font-size:12px}.sideFactoryCard small{display:block;margin-top:4px;color:#bcd0c8;font-size:10px;line-height:1.45}.sideVersion{margin-top:12px;color:#71978a;font-size:9px;text-align:center}
.productionDashboardV3{margin:18px 0 22px;color:#17221e}.dashIntro{display:flex;align-items:flex-end;justify-content:space-between;gap:18px;margin-bottom:16px}.dashEyebrow{font-size:10px;font-weight:900;letter-spacing:.14em;color:#2c7d5f;margin-bottom:4px}.dashIntro h1{margin:0!important;font-size:31px!important;color:#111b17!important;letter-spacing:-.7px}.dashIntro p{margin:5px 0 0;color:#6d7a74;font-size:13px}.dashIntroActions{display:flex;gap:8px}.dashIntroActions button,.dashPanelHead button{border:1px solid #d9e4df;background:#176b4c;color:#fff;border-radius:10px;padding:9px 12px;font-size:11px;font-weight:800;cursor:pointer}.dashIntroActions button.secondary,.dashPanelHead button{background:#fff;color:#35534a}.dashIntroActions button:hover,.dashPanelHead button:hover{filter:brightness(.98);transform:translateY(-1px)}
.dashKpis{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:11px;margin-bottom:12px}.dashKpi{min-width:0;display:flex;align-items:center;gap:12px;background:#fff;border:1px solid #e0e8e4;border-radius:15px;padding:14px;box-shadow:0 5px 16px rgba(20,60,46,.045)}.dashKpiIcon{width:44px;height:44px;flex:0 0 auto;display:grid;place-items:center;border-radius:12px;font-size:20px;font-weight:900}.dashKpiIcon.green{background:#e7f5ed;color:#19704d}.dashKpiIcon.wood{background:#fff1df;color:#a36b2c}.dashKpiIcon.blue{background:#e9f2ff;color:#3975bc}.dashKpiIcon.amber{background:#fff3dd;color:#ba7a20}.dashKpi small{display:block;color:#78867f;font-size:10px}.dashKpi strong{display:block;margin-top:2px;color:#16231e;font-size:20px;line-height:1.1;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.dashKpi span{display:block;margin-top:3px;color:#7a8881;font-size:10px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.dashLayout{display:grid;grid-template-columns:minmax(0,1.55fr) minmax(285px,.65fr);gap:12px}.dashMainCol,.dashSideCol{display:grid;gap:12px;align-content:start}.dashPanel{background:#fff;border:1px solid #e0e8e4;border-radius:16px;padding:15px;box-shadow:0 5px 18px rgba(20,60,46,.045);min-width:0}.dashPanelHead{display:flex;align-items:flex-start;justify-content:space-between;gap:10px;margin-bottom:12px}.dashPanelHead>div{display:flex;align-items:center;gap:9px;min-width:0}.dashPanelIcon{display:grid;place-items:center;width:34px;height:34px;border-radius:9px;background:#edf6f1;color:#176b4c;font-size:16px}.dashPanelHead h3{margin:0;color:#1b2924;font-size:15px}.dashPanelHead p{margin:2px 0 0;color:#7b8882;font-size:10px}.orderFocus{display:grid;grid-template-columns:105px minmax(0,1fr) 150px;gap:14px;align-items:center;padding:12px;border:1px solid #e7ece9;border-radius:13px;background:#fbfcfb}.orderFocus>img{width:100%;height:80px;object-fit:contain;filter:drop-shadow(0 8px 10px rgba(89,61,29,.12))}.orderBadges{display:flex;gap:6px;flex-wrap:wrap}.orderBadges span{border-radius:999px;padding:4px 7px;background:#edf1ef;color:#63716b;font-size:9px;font-weight:800}.orderBadges .statusLive{background:#e4f5eb;color:#18704b}.orderFocusMain h2{margin:7px 0 3px;font-size:18px;color:#16231e}.orderFocusMain p{margin:0;color:#74817b;font-size:10px}.orderProgress{margin-top:12px}.orderProgressTop,.miniFoot{display:flex;justify-content:space-between;gap:8px;color:#6d7b75;font-size:9px;margin-bottom:5px}.orderProgressTop b,.miniFoot b{color:#314e44}.dashBar,.miniBar{height:8px;border-radius:999px;background:#e9efec;overflow:hidden}.dashBar i,.miniBar i{display:block;height:100%;border-radius:999px;background:linear-gradient(90deg,#1b9a66,#43c989);transition:width .25s}.orderFocusAside{border-left:1px solid #e6ece9;padding-left:13px;display:grid;gap:2px}.orderFocusAside small{font-size:8px;color:#8a9690;text-transform:uppercase;letter-spacing:.06em}.orderFocusAside b{font-size:11px;color:#344b43;margin-bottom:7px;overflow-wrap:anywhere}.dashMiniGrid{display:grid;grid-template-columns:1fr 1fr;gap:12px}.dashPanel.compact{min-height:170px}.miniMetric{display:flex;align-items:baseline;gap:7px;margin:14px 0 8px}.miniMetric strong{font-size:28px;color:#173d31}.miniMetric span{font-size:10px;color:#7a8781}.shiftMini{display:grid;grid-template-columns:repeat(3,1fr);gap:7px;margin-top:17px}.shiftMini div{padding:10px;border:1px solid #e6ece9;border-radius:11px;background:#f8fbf9}.shiftMini small{display:block;color:#7d8b84;font-size:9px}.shiftMini b{display:block;margin-top:2px;font-size:20px;color:#1b5e47}.dashPalletImage{height:220px;border-radius:13px;background:radial-gradient(circle at 50% 35%,#fff,#f4f6f4);display:flex;align-items:center;justify-content:center;overflow:hidden}.dashPalletImage img{width:94%;height:90%;object-fit:contain;filter:drop-shadow(0 14px 15px rgba(79,56,28,.16))}.quickGrid{display:grid;grid-template-columns:1fr 1fr;gap:8px}.quickGrid button{border:1px solid #e0e8e4;background:#f8faf9;color:#355249;border-radius:11px;padding:11px 9px;text-align:left;font-size:10px;font-weight:800;cursor:pointer}.quickGrid button:hover{background:#edf6f1;border-color:#cfe2d9}.quickGrid span{display:block;font-size:17px;color:#176b4c;margin-bottom:5px}
@media(max-width:1150px){#protectedApp{margin-left:0}.appSidebar{position:static;width:auto;height:auto;margin:0 0 12px;padding:9px;background:#123c32;border-radius:13px}.sideNav{display:flex;overflow-x:auto;gap:5px}.appSideLink{width:auto!important;white-space:nowrap!important;padding:9px 11px!important}.sideFactoryCard,.sideVersion{display:none}.dashKpis{grid-template-columns:1fr 1fr}.dashLayout{grid-template-columns:1fr}.dashSideCol{grid-template-columns:1fr 1fr}.appTopTools{display:none}}
@media(max-width:720px){main{padding-left:12px!important;padding-right:12px!important}.productionDashboardV3{margin-top:12px}.dashIntro{align-items:flex-start;flex-direction:column}.dashIntroActions{width:100%}.dashIntroActions button{flex:1}.dashKpis{grid-template-columns:1fr 1fr}.orderFocus{grid-template-columns:78px 1fr}.orderFocusAside{grid-column:1/-1;border-left:0;border-top:1px solid #e6ece9;padding:9px 0 0;grid-template-columns:auto 1fr auto 1fr;align-items:center}.orderFocusAside b{margin:0}.dashMiniGrid,.dashSideCol{grid-template-columns:1fr}.dashPalletImage{height:190px}}
@media(max-width:460px){.dashKpis{grid-template-columns:1fr}.dashIntro h1{font-size:26px!important}.orderFocus{grid-template-columns:1fr}.orderFocus>img{height:95px}.orderFocusAside{grid-template-columns:1fr 1fr}.quickGrid{grid-template-columns:1fr 1fr}}
@media print{.appSidebar,.productionDashboardV3,.appTopTools{display:none!important}#protectedApp{margin-left:0!important}}
'''
if '</style>' not in text:
    raise SystemExit('style close not found')
text=text.replace('\n</style>',css+'\n</style>',1)

js=r'''
<script>
/* productionDashboardV3 */
(function(){
 const $=id=>document.getElementById(id);
 const num=id=>Number($(id)?.value)||0;
 const text=id=>($(id)?.value||'').trim();
 const fmt=n=>Number(n||0).toLocaleString('ru-RU');
 function updateDash(){
   const L=num('pL'),W=num('pW'),Q=num('qty'),order=text('orderNo'),worker=text('worker'),date=$('jobDate')?.value||'—';
   const cut=num('flowCut'),assembled=num('flowAssembled'),qc=num('flowQc');
   const ready=Q?Math.min(100,Math.round(qc/Q*100)):0;
   const kpiM3=$('kpiM3')?.textContent||'0 м³',sawBoards=$('sawBoards')?.textContent||'—',yieldText=$('sawYield')?.textContent||'—';
   if($('dashOrder'))$('dashOrder').textContent=order||'Без номера';
   if($('dashOrderDate'))$('dashOrderDate').textContent=date!=='—'?date:'Укажите дату';
   if($('dashQty'))$('dashQty').textContent=fmt(Q)+' шт.';
   if($('dashSize'))$('dashSize').textContent=(L&&W)?`${L} × ${W} мм`:'Размер не задан';
   if($('dashReady'))$('dashReady').textContent=ready+'%';
   if($('dashReadyText'))$('dashReadyText').textContent=qc?`${fmt(qc)} принято ОТК`:'Производство не отмечено';
   if($('dashWood'))$('dashWood').textContent=kpiM3;
   if($('dashBoards'))$('dashBoards').textContent=sawBoards==='—'?'раскрой не рассчитан':`${sawBoards} досок сырья`;
   if($('dashOrderBadge'))$('dashOrderBadge').textContent=order?`Заказ ${order}`:'Новый заказ';
   if($('dashOrderTitle'))$('dashOrderTitle').textContent=(L&&W)?`Поддон ${L} × ${W}`:'Поддон — размер не задан';
   if($('dashOrderMeta'))$('dashOrderMeta').textContent=worker?`Смена / сотрудник: ${worker}`:'Заполните сотрудника или смену.';
   if($('dashProgressLabel'))$('dashProgressLabel').textContent=`${fmt(qc)} / ${fmt(Q)}`;
   if($('dashProgressBar'))$('dashProgressBar').style.width=ready+'%';
   if($('dashWorker'))$('dashWorker').textContent=worker||'Не указан';
   if($('dashWorkDate'))$('dashWorkDate').textContent=date;
   if($('dashSawBoards'))$('dashSawBoards').textContent=sawBoards;
   if($('dashSawYield'))$('dashSawYield').textContent=yieldText;
   const y=parseFloat(String(yieldText).replace(',','.'))||0;if($('dashSawYieldBar'))$('dashSawYieldBar').style.width=Math.max(0,Math.min(100,y))+'%';
   if($('dashCut'))$('dashCut').textContent=fmt(cut);if($('dashAssembled'))$('dashAssembled').textContent=fmt(assembled);if($('dashQc'))$('dashQc').textContent=fmt(qc);
   if($('dashPreviewSize'))$('dashPreviewSize').textContent=(L&&W)?`${L} × ${W} мм`:'Размер не задан';
   const shift=text('worker');if($('dashboardShift'))$('dashboardShift').textContent=shift||'Смена';
 }
 function dateLabel(){const d=new Date();const s=d.toLocaleDateString('ru-RU',{day:'2-digit',month:'short'}).replace('.','');if($('dashboardToday'))$('dashboardToday').textContent=s;}
 document.querySelectorAll('[data-jump]').forEach(b=>b.addEventListener('click',()=>document.getElementById(b.dataset.jump)?.scrollIntoView({behavior:'smooth',block:'start'})));
 ['pL','pW','qty','orderNo','worker','jobDate','flowCut','flowAssembled','flowQc'].forEach(id=>$(id)?.addEventListener('input',updateDash));
 ['optimizeSaw','shopRefresh','refreshProduction'].forEach(id=>$(id)?.addEventListener('click',()=>setTimeout(updateDash,80)));
 const search=$('appSearchInput');if(search)search.addEventListener('keydown',e=>{if(e.key!=='Enter')return;const q=search.value.trim().toLowerCase();const target=q.includes('расп')?'workshop':q.includes('производ')?'production':q.includes('сохран')||q.includes('расчёт')?'savedBox':'calculator';document.getElementById(target)?.scrollIntoView({behavior:'smooth'});});
 dateLabel();setTimeout(updateDash,0);window.updateProductionDashboard=updateDash;
 const observer=new MutationObserver(updateDash);['kpiM3','sawBoards','sawYield','flowDone'].forEach(id=>{const el=$(id);if(el)observer.observe(el,{childList:true,subtree:true,characterData:true});});
})();
</script>
'''
if '</body>' not in text:
    raise SystemExit('body close not found')
text=text.replace('</body>',js+'\n</body>',1)

path.write_text(text,encoding='utf-8')
print('productionDashboardV3 installed')
