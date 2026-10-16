from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

# Sidebar: clicks switch application screens instead of scrolling the long page.
repls={
'<button class="navLink appSideLink active" type="button" data-scroll="productionDashboard"><span>⌂</span>Обзор</button>':'<button class="navLink appSideLink active" type="button" data-screen="overview"><span>⌂</span>Обзор</button>',
'<button class="navLink appSideLink" type="button" data-scroll="production"><span>▥</span>Производство</button>':'<button class="navLink appSideLink" type="button" data-screen="production"><span>▥</span>Производство</button>',
'<button class="navLink appSideLink" type="button" data-scroll="calculator"><span>▦</span>Калькулятор</button>':'<button class="navLink appSideLink" type="button" data-screen="calculator"><span>▦</span>Калькулятор</button>',
'<button class="navLink appSideLink" type="button" data-scroll="workshop"><span>⌁</span>Распил досок</button>':'<button class="navLink appSideLink" type="button" data-screen="workshop"><span>⌁</span>Распил досок</button>',
'<button class="navLink appSideLink" type="button" data-scroll="savedBox"><span>▤</span>Мои расчёты</button>':'<button class="navLink appSideLink" type="button" data-screen="saved"><span>▤</span>Мои расчёты</button>',
'<button class="navLink appSideLink adminSideLink" type="button" data-scroll="adminPanel"><span>⚙</span>Админ-панель</button>':'<button class="navLink appSideLink adminSideLink" id="adminSideNav" type="button" data-screen="admin" hidden><span>⚙</span>Админ-панель</button>',
}
for old,new in repls.items():
    if old not in s: raise SystemExit('sidebar marker missing: '+old[:50])
    s=s.replace(old,new,1)

# Turn the long document into separate app screens.
repls2={
'<section class="productionDashboardV3" id="productionDashboard">':'<section class="productionDashboardV3" id="productionDashboard" data-app-screen="overview">',
'<div class="actions">':'<div class="actions" data-app-screen="calculator" hidden>',
'<section class="card jobCard">':'<section class="card jobCard" data-app-screen="calculator" hidden>',
'<section class="dashboardCards" id="calculator">':'<section class="dashboardCards" id="calculator" data-app-screen="calculator" hidden>',
'<div class="materialsHeader">':'<div class="materialsHeader" data-app-screen="calculator" hidden>',
'<div id="parts" class="parts"></div>':'<div id="parts" class="parts" data-app-screen="calculator" hidden></div>',
'<section class="adminPanel" id="adminPanel" style="display:none">':'<section class="adminPanel" id="adminPanel" data-app-screen="admin" style="display:none" hidden>',
'<section class="result">':'<section class="result" data-app-screen="calculator" hidden>',
'<section class="workshopHub" id="workshop">':'<section class="workshopHub" id="workshop" data-app-screen="workshop" hidden>',
'<section class="productionHub" id="production">':'<section class="productionHub" id="production" data-app-screen="production" hidden>',
'<section class="savedBox" id="savedBox">':'<section class="savedBox" id="savedBox" data-app-screen="saved" hidden>',
}
for old,new in repls2.items():
    if old not in s: raise SystemExit('screen marker missing: '+old)
    s=s.replace(old,new,1)

# Result must belong only to Calculator, not wrap workshop/production/saved screens.
needle='<div id="results"></div>\n\n\n<section class="workshopHub" id="workshop" data-app-screen="workshop" hidden>'
if needle not in s: raise SystemExit('result/workshop boundary missing')
s=s.replace(needle,'<div id="results"></div>\n</section>\n\n\n<section class="workshopHub" id="workshop" data-app-screen="workshop" hidden>',1)

css='''\n/* appSectionSwitchV1 */\n[data-app-screen][hidden]{display:none!important}\n.adminSideLink[hidden]{display:none!important}\n'''
if '/* appSectionSwitchV1 */' not in s:
    s=s.replace('</style>',css+'\n</style>',1)

# Existing navigation helpers route into the same screen controller.
old='document.querySelectorAll("[data-scroll]").forEach(btn=>btn.addEventListener("click",()=>{const el=document.getElementById(btn.dataset.scroll);if(el)el.scrollIntoView({behavior:"smooth",block:"start"});}));'
new='document.querySelectorAll("[data-scroll]").forEach(btn=>btn.addEventListener("click",()=>window.switchAppScreen?.(btn.dataset.scroll)));'
if old not in s: raise SystemExit('data-scroll handler missing')
s=s.replace(old,new,1)

old="document.querySelectorAll('[data-jump]').forEach(b=>b.addEventListener('click',()=>document.getElementById(b.dataset.jump)?.scrollIntoView({behavior:'smooth',block:'start'})));"
new="document.querySelectorAll('[data-jump]').forEach(b=>b.addEventListener('click',()=>window.switchAppScreen?.(b.dataset.jump)));"
if old not in s: raise SystemExit('data-jump handler missing')
s=s.replace(old,new,1)

old="const search=$('appSearchInput');if(search)search.addEventListener('keydown',e=>{if(e.key!=='Enter')return;const q=search.value.trim().toLowerCase();const target=q.includes('расп')?'workshop':q.includes('производ')?'production':q.includes('сохран')||q.includes('расчёт')?'savedBox':'calculator';document.getElementById(target)?.scrollIntoView({behavior:'smooth'});});"
new="const search=$('appSearchInput');if(search)search.addEventListener('keydown',e=>{if(e.key!=='Enter')return;const q=search.value.trim().toLowerCase();const target=q.includes('расп')?'workshop':q.includes('производ')?'production':q.includes('сохран')||q.includes('расчёт')?'savedBox':'calculator';window.switchAppScreen?.(target);});"
if old not in s: raise SystemExit('search navigation handler missing')
s=s.replace(old,new,1)

# Admin menu is shown only after the role from profiles is resolved as admin.
login_old='if(adminNav)adminNav.style.display=admin?"inline-flex":"none";'
login_new='if(adminNav)adminNav.style.display=admin?"inline-flex":"none";const adminSideNav=document.getElementById("adminSideNav");if(adminSideNav){adminSideNav.hidden=!admin;adminSideNav.style.display=admin?"flex":"none";}if(typeof window.syncAdminNavigation==="function")window.syncAdminNavigation();'
if login_old not in s: raise SystemExit('admin login visibility marker missing')
s=s.replace(login_old,login_new,1)

logout_old='if(adminNav)adminNav.style.display="none";'
logout_new='if(adminNav)adminNav.style.display="none";const adminSideNav=document.getElementById("adminSideNav");if(adminSideNav){adminSideNav.hidden=true;adminSideNav.style.display="none";}if(typeof window.syncAdminNavigation==="function")window.syncAdminNavigation();'
if logout_old not in s: raise SystemExit('admin logout visibility marker missing')
s=s.replace(logout_old,logout_new,1)

controller='''\n<script>\n/* appSectionSwitchV1 */\n(function(){\n const map={home:'overview',productionDashboard:'overview',overview:'overview',calculator:'calculator',workshop:'workshop',production:'production',savedBox:'saved',saved:'saved',adminPanel:'admin',admin:'admin'};\n let current='overview';\n function isAdmin(){return typeof currentRole!=='undefined'&&currentRole==='admin';}\n function syncAdminNavigation(){\n   const allowed=isAdmin();\n   document.querySelectorAll('.adminSideLink').forEach(el=>{el.hidden=!allowed;el.style.display=allowed?'flex':'none';});\n   document.querySelectorAll('.adminNav').forEach(el=>{el.style.display=allowed?'inline-flex':'none';});\n   if(!allowed&&current==='admin')switchAppScreen('overview');\n   return allowed;\n }\n function switchAppScreen(target){\n   let screen=map[target]||target||'overview';\n   if(screen==='admin'&&!isAdmin())screen='overview';\n   current=screen;\n   document.querySelectorAll('[data-app-screen]').forEach(el=>{el.hidden=el.dataset.appScreen!==screen;});\n   document.querySelectorAll('.appSideLink[data-screen]').forEach(btn=>btn.classList.toggle('active',btn.dataset.screen===screen));\n   if(screen==='admin'){const panel=document.getElementById('adminPanel');if(panel)panel.style.display='block';if(typeof loadAdminData==='function')loadAdminData();}\n   if(screen==='workshop'&&typeof updateLumberSummary==='function')updateLumberSummary();\n   if(screen==='production'&&typeof refreshProduction==='function')refreshProduction();\n   if(screen==='overview'&&typeof window.updateProductionDashboard==='function')window.updateProductionDashboard();\n   if(screen==='calculator'&&typeof window.rerenderPallet3D==='function')setTimeout(()=>window.rerenderPallet3D(),30);\n }\n window.switchAppScreen=switchAppScreen;\n window.syncAdminNavigation=syncAdminNavigation;\n document.querySelectorAll('.appSideLink[data-screen]').forEach(btn=>btn.addEventListener('click',e=>{e.preventDefault();switchAppScreen(btn.dataset.screen);}));\n syncAdminNavigation();\n switchAppScreen('overview');\n})();\n</script>\n'''
anchor='<script src="https://cdn.jsdelivr.net/npm/three@0.159.0/build/three.min.js"></script>'
if anchor not in s: raise SystemExit('three anchor missing')
if '/* appSectionSwitchV1 */\n(function(){' not in s:
    s=s.replace(anchor,controller+'\n'+anchor,1)

p.write_text(s,encoding='utf-8')
print('App screen navigation installed; admin screen is role-gated')
