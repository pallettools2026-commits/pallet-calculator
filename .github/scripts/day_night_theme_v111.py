from pathlib import Path
import re

html_path = Path('index.html')
css_path = Path('assets/theme-industrial-v130.css')
js_path = Path('assets/pallet3d-v10.js')

html = html_path.read_text(encoding='utf-8')
css = css_path.read_text(encoding='utf-8')
js = js_path.read_text(encoding='utf-8')

bootstrap = '''<script id="themeBootstrapV111">
(function(){try{var t=localStorage.getItem('pallettools:theme');document.documentElement.dataset.theme=t==='dark'?'dark':'light';document.documentElement.style.colorScheme=t==='dark'?'dark':'light';}catch(_){document.documentElement.dataset.theme='light';}})();
</script>'''
viewport = '<meta name="viewport" content="width=device-width,initial-scale=1">'
if 'themeBootstrapV111' not in html:
    if viewport not in html:
        raise SystemExit('viewport marker not found')
    html = html.replace(viewport, viewport + '\n' + bootstrap, 1)

desktop_anchor = '    <div class="appTopChip shift"><span class="liveDot"></span><div><small>Текущая смена</small><b id="dashboardShift">Смена</b></div></div>'
if 'class="themeToggle"' not in html:
    if desktop_anchor not in html:
        raise SystemExit('desktop theme anchor not found')
    html = html.replace(desktop_anchor, desktop_anchor + '\n    <button class="themeToggle" type="button" data-theme-toggle aria-label="Переключить дневной и ночной режим" title="Дневной / ночной режим"><span class="themeIcon" aria-hidden="true">☾</span><span class="themeText">Ночь</span></button>', 1)

auth_anchor = '    <div class="authAccent"></div>'
if 'class="authThemeToggle"' not in html:
    if auth_anchor not in html:
        raise SystemExit('auth theme anchor not found')
    html = html.replace(auth_anchor, auth_anchor + '\n    <button class="authThemeToggle" type="button" data-theme-toggle aria-label="Переключить дневной и ночной режим" title="Дневной / ночной режим"><span class="themeIcon" aria-hidden="true">☾</span></button>', 1)

mobile_anchor = '      <button class="mobileMoreAction appSideLink adminSideLink" id="mobileAdminNav" type="button" data-screen="admin" hidden><span>⚙</span><b>Админ-панель</b><i>›</i></button>'
if 'themeMobileToggle' not in html:
    if mobile_anchor not in html:
        raise SystemExit('mobile theme anchor not found')
    html = html.replace(mobile_anchor, mobile_anchor + '\n      <button class="mobileMoreAction themeMobileToggle" type="button" data-theme-toggle><span class="themeIcon" aria-hidden="true">☾</span><b class="themeText">Ночной режим</b><i>›</i></button>', 1)

runtime = '''<script id="themeRuntimeV111">
(function(){
  const KEY='pallettools:theme',root=document.documentElement;
  const apply=theme=>{
    const dark=theme==='dark';
    root.dataset.theme=dark?'dark':'light';
    root.style.colorScheme=dark?'dark':'light';
    document.querySelectorAll('[data-theme-toggle]').forEach(btn=>{
      const icon=btn.querySelector('.themeIcon'),text=btn.querySelector('.themeText');
      if(icon)icon.textContent=dark?'☀':'☾';
      if(text)text.textContent=btn.classList.contains('themeMobileToggle')?(dark?'Дневной режим':'Ночной режим'):(dark?'День':'Ночь');
      btn.setAttribute('aria-pressed',dark?'true':'false');
      btn.setAttribute('title',dark?'Включить дневной режим':'Включить ночной режим');
    });
  };
  let saved='light';try{saved=localStorage.getItem(KEY)==='dark'?'dark':'light';}catch(_){}
  apply(saved);
  document.addEventListener('click',e=>{const btn=e.target.closest('[data-theme-toggle]');if(!btn)return;const next=root.dataset.theme==='dark'?'light':'dark';try{localStorage.setItem(KEY,next);}catch(_){}apply(next);});
})();
</script>'''
if 'themeRuntimeV111' not in html:
    if '</body>' not in html:
        raise SystemExit('body end marker not found')
    html = html.replace('</body>', runtime + '\n</body>', 1)

html = html.replace('Pallet Tools · v1.1.10</div>', 'Pallet Tools · v1.1.11</div>', 1)
for pattern in [r'assets/theme-industrial-v130\.css\?v=(\d+)', r'assets/pallet3d-v10\.js\?v=(\d+)']:
    m = re.search(pattern, html)
    if not m:
        raise SystemExit(f'cache marker not found: {pattern}')
    html = html[:m.start(1)] + str(int(m.group(1)) + 1) + html[m.end(1):]
html_path.write_text(html, encoding='utf-8')

dark_css = r'''

/* dayNightThemeV111 */
.themeToggle{height:44px;display:inline-flex;align-items:center;justify-content:center;gap:7px;flex:0 0 auto;padding:0 12px;border:1px solid #ddd8d0;border-radius:11px;background:#fff;color:#4c5356;font-size:12px;font-weight:850;box-shadow:0 3px 10px rgba(35,40,43,.04);transition:background .18s,border-color .18s,color .18s,transform .18s}
.themeToggle:hover{background:#f3eee8;border-color:#cfc3b5;transform:translateY(-1px)}
.themeIcon{font-size:17px;line-height:1}.themeText{white-space:nowrap}
.authThemeToggle{position:absolute;right:15px;top:15px;z-index:3;width:42px;height:42px;display:grid;place-items:center;border:1px solid #dde3e8;border-radius:12px;background:rgba(255,255,255,.88);color:#535c6b;font-weight:900;box-shadow:0 5px 16px rgba(25,35,50,.07);backdrop-filter:blur(10px)}
.authThemeToggle:hover{background:#fff}.themeMobileToggle{display:flex!important}
@media(max-width:1180px){.themeToggle .themeText{display:none}.themeToggle{width:44px;padding:0}}
html[data-theme="dark"]{--bg:#111416;--surface:#1b2022;--surface-soft:#202628;--text:#edf1ef;--muted:#9aa4a0;--line:#353c3e;--primary:#c58a4e;--primary-dark:#dfa462;--primary-deep:#f1f3f2;--accent:#3a2d22;--warning-bg:#3a3020;--warning-text:#f0c77f;--danger:#e17b70;--shadow:0 12px 30px rgba(0,0,0,.24);background:#111416!important;color-scheme:dark}
html[data-theme="dark"] body{background:linear-gradient(180deg,#111416 0,#15191b 360px,#121618 100%)!important;color:#edf1ef!important}html[data-theme="dark"] main{background:transparent!important}
html[data-theme="dark"] h1,html[data-theme="dark"] h2,html[data-theme="dark"] h3,html[data-theme="dark"] .dashIntro h1,html[data-theme="dark"] .orderFocusMain h2,html[data-theme="dark"] .dashPanelHead h3,html[data-theme="dark"] .savedTitle,html[data-theme="dark"] .adminCalcTitle,html[data-theme="dark"] .materialsHeader h2{color:#f0f3f1!important}
html[data-theme="dark"] p,html[data-theme="dark"] small,html[data-theme="dark"] .dim,html[data-theme="dark"] .adminSub,html[data-theme="dark"] .shopCardHead p,html[data-theme="dark"] .prodCardHead p,html[data-theme="dark"] .materialsHeader p{color:#9ba5a1!important}html[data-theme="dark"] label{color:#c6ceca!important}
html[data-theme="dark"] input,html[data-theme="dark"] select,html[data-theme="dark"] textarea,html[data-theme="dark"] .adminRole{background:#14191b!important;color:#edf2ef!important;border-color:#394143!important}html[data-theme="dark"] input::placeholder,html[data-theme="dark"] textarea::placeholder{color:#737d79!important}html[data-theme="dark"] input:hover,html[data-theme="dark"] select:hover{border-color:#545d5f!important}html[data-theme="dark"] input:focus,html[data-theme="dark"] select:focus,html[data-theme="dark"] textarea:focus{border-color:#c58a4e!important;box-shadow:0 0 0 4px rgba(197,138,78,.16)!important}
html[data-theme="dark"] .topNav{background:rgba(20,24,26,.96)!important;border-bottom-color:#303739!important;box-shadow:0 5px 20px rgba(0,0,0,.25)!important}html[data-theme="dark"] .brandTitle,html[data-theme="dark"] .accountMain strong{color:#f0f3f1!important}html[data-theme="dark"] .brandTitle span{color:#d2995f!important}html[data-theme="dark"] .brandSub,html[data-theme="dark"] .accountMain small,html[data-theme="dark"] .accountArrow{color:#97a19d!important}
html[data-theme="dark"] .appSearch,html[data-theme="dark"] .appTopChip,html[data-theme="dark"] .topAccount,html[data-theme="dark"] .themeToggle{background:#1b2022!important;border-color:#353d3f!important;color:#d9dfdc!important}html[data-theme="dark"] .appSearch input{background:transparent!important;color:#edf2ef!important}html[data-theme="dark"] .appSearch span,html[data-theme="dark"] .appTopChip small{color:#8f9a95!important}html[data-theme="dark"] .appTopChip b{color:#e5eae7!important}html[data-theme="dark"] .themeToggle:hover{background:#252b2e!important;border-color:#51595c!important}
html[data-theme="dark"] .accountShield{background:#332b23!important;color:#e5aa6d!important}html[data-theme="dark"] .accountDropdown{background:#1b2022!important;border-color:#353d3f!important;box-shadow:0 18px 45px rgba(0,0,0,.38)!important}html[data-theme="dark"] .accountDropIdentity strong,html[data-theme="dark"] .accountDropAction b{color:#edf2ef!important}html[data-theme="dark"] .accountDropIdentity span,html[data-theme="dark"] .accountDropEmail{color:#9aa5a0!important}html[data-theme="dark"] .accountDropRole{background:#302a24!important;color:#dfa462!important}html[data-theme="dark"] .accountDropDivider{background:#343b3d!important}html[data-theme="dark"] .accountDropAction:hover{background:#252b2d!important}
html[data-theme="dark"] .appSidebar{background:linear-gradient(180deg,#171b1d 0%,#121618 72%,#0e1113 100%)!important;box-shadow:10px 0 30px rgba(0,0,0,.28)!important}html[data-theme="dark"] .appSideLink{color:#c8cfcc!important}html[data-theme="dark"] .appSideLink:hover,html[data-theme="dark"] .appSideLink.active{background:rgba(197,138,78,.15)!important;color:#fff!important}html[data-theme="dark"] .appSideLink.active{box-shadow:inset 3px 0 #c58a4e!important}html[data-theme="dark"] .sideFactoryCard{background:linear-gradient(145deg,rgba(255,255,255,.04),rgba(197,138,78,.10))!important;border-color:#343a3c!important}
html[data-theme="dark"] .productionDashboardV3,html[data-theme="dark"] .workshopHub,html[data-theme="dark"] .productionHub,html[data-theme="dark"] .savedBox,html[data-theme="dark"] .adminPanel{color:#e9eeeb!important}
html[data-theme="dark"] .card,html[data-theme="dark"] .savedBox,html[data-theme="dark"] .dashPanel,html[data-theme="dark"] .dashKpi,html[data-theme="dark"] .adminPanel,html[data-theme="dark"] .shopCard,html[data-theme="dark"] .prodCard,html[data-theme="dark"] .previewCard,html[data-theme="dark"] .orderFocus,html[data-theme="dark"] .shiftMini div,html[data-theme="dark"] .adminStat,html[data-theme="dark"] .adminBox,html[data-theme="dark"] .savedItem,html[data-theme="dark"] .routeStep,html[data-theme="dark"] .costStat,html[data-theme="dark"] .flowStat,html[data-theme="dark"] .inventoryRow,html[data-theme="dark"] .inventoryEstimate,html[data-theme="dark"] .sawGroup,html[data-theme="dark"] .sawStat,html[data-theme="dark"] .shopKpi{background:#1b2022!important;border-color:#353d3f!important;box-shadow:0 8px 22px rgba(0,0,0,.18)!important}
html[data-theme="dark"] .orderFocus,html[data-theme="dark"] .shiftMini div,html[data-theme="dark"] .adminStat,html[data-theme="dark"] .adminBox,html[data-theme="dark"] .savedItem,html[data-theme="dark"] .routeStep,html[data-theme="dark"] .costStat,html[data-theme="dark"] .flowStat,html[data-theme="dark"] .inventoryRow,html[data-theme="dark"] .inventoryEstimate,html[data-theme="dark"] .sawGroup,html[data-theme="dark"] .sawStat{background:#202628!important}
html[data-theme="dark"] .dashKpi strong,html[data-theme="dark"] .miniMetric strong,html[data-theme="dark"] .sectionLine strong,html[data-theme="dark"] .sawStat b,html[data-theme="dark"] .flowStat b,html[data-theme="dark"] .costStat b,html[data-theme="dark"] .inventoryRow b{color:#e9eeeb!important}
html[data-theme="dark"] .dashPanelHead button,html[data-theme="dark"] .shopGhost,html[data-theme="dark"] .clearBtn,html[data-theme="dark"] .previewActions button,html[data-theme="dark"] .adminRefresh,html[data-theme="dark"] .presetBtn,html[data-theme="dark"] .autoBtn{background:#252b2d!important;color:#dce2df!important;border-color:#3c4547!important}html[data-theme="dark"] .quickGrid button{background:#202628!important;border-color:#353d3f!important;color:#dbe1de!important}html[data-theme="dark"] .quickGrid button:hover{background:#2a3032!important;border-color:#55483c!important}
html[data-theme="dark"] .dashBar,html[data-theme="dark"] .miniBar,html[data-theme="dark"] .flowBar,html[data-theme="dark"] .stockBar{background:#303739!important;border-color:#3b4345!important}html[data-theme="dark"] .orderBadges span,html[data-theme="dark"] .inventoryPill,html[data-theme="dark"] .statusPill{background:#292f31!important;color:#c3cbc7!important;border-color:#3a4244!important}html[data-theme="dark"] .orderBadges .statusLive{background:#193329!important;color:#7ad3a5!important}
html[data-theme="dark"] .previewStage,html[data-theme="dark"] .dynamicPalletStage,html[data-theme="dark"] .palletReferenceStage{background:radial-gradient(circle at 50% 30%,#2a2f31 0,#1b2022 58%,#14181a 100%)!important;border-color:#363e40!important}html[data-theme="dark"] .pallet3dToolbar{background:#202628!important;border-color:#374043!important}html[data-theme="dark"] .pallet3dToolbar button{color:#bec6c2!important}html[data-theme="dark"] .pallet3dToolbar button.active{background:#b8793d!important;color:#fff!important}
html[data-theme="dark"] .result,html[data-theme="dark"] .costTotal,html[data-theme="dark"] .shiftResult{background:linear-gradient(145deg,#242a2d,#171b1d)!important;border-color:#353c3e!important;box-shadow:0 16px 38px rgba(0,0,0,.28)!important}html[data-theme="dark"] .result .top span,html[data-theme="dark"] .result .dim{color:#c1c9c5!important}html[data-theme="dark"] .result .top b{color:#f4d7b5!important}
html[data-theme="dark"] .productionHub,html[data-theme="dark"] .workshopHub{background:linear-gradient(180deg,#171c1e,#131719)!important;border-color:#343c3e!important;box-shadow:0 12px 30px rgba(0,0,0,.22)!important}html[data-theme="dark"] .adminPanel{background:linear-gradient(180deg,#191e20,#14181a)!important}html[data-theme="dark"] .adminUser,html[data-theme="dark"] .adminCalc{background:linear-gradient(145deg,#202628,#1a1f21)!important;border-color:#343c3e!important}html[data-theme="dark"] .adminEmail,html[data-theme="dark"] .adminCalcTitle{color:#e9eeeb!important}html[data-theme="dark"] .adminMeta{color:#949e99!important}
html[data-theme="dark"] .mobileBottomNav,html[data-theme="dark"] .mobileMorePanel{background:#171c1e!important;border-color:#343c3e!important;color:#edf2ef!important}html[data-theme="dark"] .mobileNavBtn,html[data-theme="dark"] .mobileMoreAction{color:#bfc8c3!important;background:transparent!important;border-color:#333b3d!important}html[data-theme="dark"] .mobileNavBtn.active,html[data-theme="dark"] .mobileMoreAction:hover{color:#e6aa6d!important;background:#242a2c!important}
html[data-theme="dark"] .authCard.authScreenV2{background:linear-gradient(135deg,#11161a 0%,#171b20 45%,#1c1714 100%)!important;color:#edf2ef!important}html[data-theme="dark"] .authGlowOne{background:#1c3855!important}html[data-theme="dark"] .authGlowTwo{background:#5a3425!important}html[data-theme="dark"] .authLoginPanel{background:rgba(24,29,33,.96)!important;border-color:#394146!important;box-shadow:0 25px 60px rgba(0,0,0,.42)!important}html[data-theme="dark"] .authWelcome h2,html[data-theme="dark"] .authBrandName strong{color:#f0f3f1!important}html[data-theme="dark"] .authWelcome p{color:#9ba5ad!important}html[data-theme="dark"] .authInputWrap input{background:#111619!important;color:#eef2f0!important;border-color:#3a4348!important}html[data-theme="dark"] .authRegisterBtn{background:#20262a!important;color:#e5e9e7!important;border-color:#3a4348!important}html[data-theme="dark"] .authNotice{background:#30241e!important;border-color:#634431!important;color:#e5a16e!important}html[data-theme="dark"] .authThemeToggle{background:rgba(28,34,38,.92)!important;border-color:#3b4449!important;color:#f0c18b!important;box-shadow:0 5px 16px rgba(0,0,0,.22)!important}html[data-theme="dark"] .profilePanel{background:#1b2022!important;border-color:#394143!important;color:#edf2ef!important}html[data-theme="dark"] .profileEmailRow>div{background:#202628!important;border-color:#394143!important;color:#dfe5e2!important}
html[data-theme="dark"] .deleteSaved,html[data-theme="dark"] .inventoryDelete{background:#262c2e!important;border-color:#454d50!important;color:#e3b0aa!important}html[data-theme="dark"] .stockOffcut{background:repeating-linear-gradient(135deg,#3a4244 0 6px,#303739 6px 12px)!important;border-color:#4a5355!important}html[data-theme="dark"] .stockMeta,html[data-theme="dark"] .sawGroupTitle span,html[data-theme="dark"] .shopNote,html[data-theme="dark"] .prodNote{color:#98a29d!important}html[data-theme="dark"] .moreBoards{background:#252b2d!important;color:#aeb7b2!important}
html[data-theme="dark"] .sideVersion:after{content:"Pallet Tools · v1.1.11"!important}html[data-theme="dark"] .appSidebar:has(#adminSideNav:not([hidden])) .sideVersion:after{content:"Pallet Tools · v1.1.11 · обновление №345"!important}
'''
if 'dayNightThemeV111' not in css:
    css += dark_css
css = css.replace('content:"Pallet Tools · v1.1.10"', 'content:"Pallet Tools · v1.1.11"')
css = css.replace('content:"Pallet Tools · v1.1.10 · обновление №344"', 'content:"Pallet Tools · v1.1.11 · обновление №345"')
css_path.write_text(css, encoding='utf-8')

old_ver = "node.textContent=admin?'Pallet Tools · v1.1.10 · обновление №344':'Pallet Tools · v1.1.10';"
new_ver = "node.textContent=admin?'Pallet Tools · v1.1.11 · обновление №345':'Pallet Tools · v1.1.11';"
if old_ver not in js:
    raise SystemExit('JS version marker not found')
js = js.replace(old_ver, new_ver, 1)
js_path.write_text(js, encoding='utf-8')
