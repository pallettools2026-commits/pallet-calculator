from pathlib import Path

path = Path('index.html')
text = path.read_text(encoding='utf-8')
if 'accountDropdownV1' in text:
    raise SystemExit('accountDropdownV1 already installed')

old_html = '''  <button class="topAccount" id="topAccount" type="button" title="Аккаунт">\n    <span class="accountShield">♜</span>\n    <span class="accountMain"><strong id="topAccountText">Войти</strong><small id="topAccountSub">Аккаунт</small></span>\n    <span class="accountArrow">⌄</span>\n  </button>\n</header>'''
new_html = '''  <button class="topAccount" id="topAccount" type="button" title="Аккаунт" aria-haspopup="menu" aria-expanded="false">\n    <span class="accountShield">♜</span>\n    <span class="accountMain"><strong id="topAccountText">Войти</strong><small id="topAccountSub">Аккаунт</small></span>\n    <span class="accountArrow">⌄</span>\n  </button>\n  <!-- accountDropdownV1 -->\n  <div class="accountDropdown" id="accountDropdown" role="menu" hidden>\n    <div class="accountDropHead">\n      <div class="accountDropAvatar" id="accountDropAvatar">PT</div>\n      <div class="accountDropIdentity"><strong id="accountDropName">Сотрудник</strong><span id="accountDropPosition">Pallet Tools</span></div>\n    </div>\n    <div class="accountDropEmail"><span>✉</span><span id="accountDropEmail">—</span></div>\n    <div class="accountDropRole" id="accountDropRole">Сотрудник</div>\n    <div class="accountDropDivider"></div>\n    <button class="accountDropAction" id="accountDropProfile" type="button" role="menuitem"><span>👤</span><b>Мой профиль</b><i>›</i></button>\n    <button class="accountDropAction danger" id="accountDropLogout" type="button" role="menuitem"><span>↪</span><b>Выйти</b><i>›</i></button>\n  </div>\n</header>'''
if old_html not in text:
    raise SystemExit('top account html marker not found')
text = text.replace(old_html, new_html, 1)

old_listener = '''document.getElementById("topAccount")?.addEventListener("click",async()=>{if(currentUser){if(typeof openEmployeeProfile==="function")await openEmployeeProfile();}else{document.getElementById("authCard")?.scrollIntoView({behavior:"smooth",block:"center"});}});'''
new_listener = '''document.getElementById("topAccount")?.addEventListener("click",async()=>{if(currentUser){if(typeof toggleAccountDropdown==="function")await toggleAccountDropdown();}else{document.getElementById("authCard")?.scrollIntoView({behavior:"smooth",block:"center"});}});'''
if old_listener not in text:
    raise SystemExit('top account listener marker not found')
text = text.replace(old_listener, new_listener, 1)

# Keep the dropdown in sync after profile edits.
old_profile_sync = ''' if(typeof renderLastEmployeeCard==='function')renderLastEmployeeCard();\n btn.disabled=false;if(msg){msg.textContent='Профиль сохранён.';msg.style.color='#176b4c';}'''
new_profile_sync = ''' if(typeof renderLastEmployeeCard==='function')renderLastEmployeeCard();\n if(typeof refreshAccountDropdown==='function')refreshAccountDropdown();\n btn.disabled=false;if(msg){msg.textContent='Профиль сохранён.';msg.style.color='#176b4c';}'''
if old_profile_sync in text:
    text = text.replace(old_profile_sync, new_profile_sync, 1)

css = r'''
/* accountDropdownV1 */
.accountDropdown[hidden]{display:none!important}.accountDropdown{position:fixed;z-index:12000;width:min(300px,calc(100vw - 20px));padding:12px;background:#fff;border:1px solid #dfe8e3;border-radius:16px;box-shadow:0 18px 50px rgba(16,48,38,.18);animation:accountDropIn .14s ease-out}.accountDropHead{display:flex;align-items:center;gap:10px;padding:4px 3px 10px}.accountDropAvatar{display:grid;place-items:center;flex:0 0 42px;height:42px;border-radius:12px;background:linear-gradient(135deg,#dff4e9,#f1faf5);border:1px solid #cee8dc;color:#176b4c;font-size:12px;font-weight:900;letter-spacing:.04em}.accountDropIdentity{min-width:0}.accountDropIdentity strong{display:block;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;color:#182720;font-size:13px}.accountDropIdentity span{display:block;margin-top:2px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;color:#718078;font-size:10px}.accountDropEmail{display:flex;align-items:center;gap:7px;padding:8px 9px;border-radius:9px;background:#f6f9f7;color:#607169;font-size:10px;overflow:hidden}.accountDropEmail span:last-child{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.accountDropRole{display:inline-flex;align-items:center;margin-top:8px;padding:5px 8px;border-radius:999px;background:#eaf6f0;color:#176b4c;font-size:9px;font-weight:850}.accountDropDivider{height:1px;background:#e7ece9;margin:10px 0 6px}.accountDropAction{width:100%;display:grid;grid-template-columns:25px 1fr 16px;align-items:center;gap:6px;min-height:40px;padding:6px 9px;border:0;border-radius:10px;background:transparent;color:#33433c;text-align:left;cursor:pointer}.accountDropAction:hover{background:#f3f8f5}.accountDropAction span{font-size:14px}.accountDropAction b{font-size:11px;font-weight:800}.accountDropAction i{font-style:normal;color:#97a29d;font-size:18px}.accountDropAction.danger{color:#9d4038}.accountDropAction.danger:hover{background:#fff4f2}.topAccount[aria-expanded="true"]{border-color:#acd2c1!important;box-shadow:0 0 0 3px rgba(32,120,84,.08)}.topAccount[aria-expanded="true"] .accountArrow{transform:rotate(180deg)}.accountArrow{transition:transform .15s ease}@keyframes accountDropIn{from{opacity:0;transform:translateY(-5px) scale(.98)}to{opacity:1;transform:translateY(0) scale(1)}}
@media(max-width:680px){.accountDropdown{width:min(290px,calc(100vw - 16px));border-radius:14px}.accountDropAction{min-height:44px}}
'''
if '\n</style>' not in text:
    raise SystemExit('style closing tag not found')
text = text.replace('\n</style>', css + '\n</style>', 1)

script = r'''
<script>
/* accountDropdownV1 */
function accountDropdownInitials(name,email){
 const source=(name||'').trim();
 if(source){const p=source.split(/\s+/).filter(Boolean);return ((p[0]?.[0]||'')+(p[1]?.[0]||'')).toUpperCase()||'PT';}
 return ((email||'P')[0]||'P').toUpperCase();
}
function positionAccountDropdown(){
 const btn=document.getElementById('topAccount'),menu=document.getElementById('accountDropdown');
 if(!btn||!menu)return;
 const r=btn.getBoundingClientRect();
 const right=Math.max(10,window.innerWidth-r.right);
 menu.style.top=Math.min(window.innerHeight-10,r.bottom+8)+'px';
 menu.style.right=right+'px';
}
function closeAccountDropdown(){
 const menu=document.getElementById('accountDropdown'),btn=document.getElementById('topAccount');
 if(menu)menu.hidden=true;
 if(btn)btn.setAttribute('aria-expanded','false');
}
async function refreshAccountDropdown(){
 if(!currentUser)return;
 let fullName=currentUser.user_metadata?.full_name||'';
 let position=currentUser.user_metadata?.position||'';
 let email=currentUser.email||'';
 let role=currentRole||currentUser.app_metadata?.role||'employee';
 try{
   const {data}=await sb.from('profiles').select('email,full_name,position,role').eq('id',currentUser.id).single();
   if(data){fullName=data.full_name||fullName;position=data.position||position;email=data.email||email;role=data.role||role;}
 }catch(_){ }
 const roleText=role==='admin'?'Администратор':'Сотрудник';
 const nameEl=document.getElementById('accountDropName'),posEl=document.getElementById('accountDropPosition'),emailEl=document.getElementById('accountDropEmail'),roleEl=document.getElementById('accountDropRole'),avatar=document.getElementById('accountDropAvatar');
 if(nameEl)nameEl.textContent=fullName||roleText;
 if(posEl)posEl.textContent=position||roleText;
 if(emailEl)emailEl.textContent=email||'—';
 if(roleEl)roleEl.textContent=roleText;
 if(avatar)avatar.textContent=accountDropdownInitials(fullName,email);
}
async function toggleAccountDropdown(){
 const menu=document.getElementById('accountDropdown'),btn=document.getElementById('topAccount');
 if(!menu||!btn||!currentUser)return;
 if(!menu.hidden){closeAccountDropdown();return;}
 await refreshAccountDropdown();
 positionAccountDropdown();
 menu.hidden=false;
 btn.setAttribute('aria-expanded','true');
}
document.getElementById('accountDropProfile')?.addEventListener('click',async()=>{closeAccountDropdown();if(typeof openEmployeeProfile==='function')await openEmployeeProfile();});
document.getElementById('accountDropLogout')?.addEventListener('click',async()=>{
 closeAccountDropdown();
 try{localStorage.removeItem('pallettools:lastEmployee');}catch(_){}
 const {error}=await sb.auth.signOut();
 if(error&&typeof setAuthMessage==='function')setAuthMessage('Ошибка выхода: '+error.message,true);
});
document.addEventListener('click',e=>{
 const menu=document.getElementById('accountDropdown'),btn=document.getElementById('topAccount');
 if(!menu||menu.hidden)return;
 if(!menu.contains(e.target)&&!btn?.contains(e.target))closeAccountDropdown();
});
document.addEventListener('keydown',e=>{if(e.key==='Escape')closeAccountDropdown();});
window.addEventListener('resize',()=>{const menu=document.getElementById('accountDropdown');if(menu&&!menu.hidden)positionAccountDropdown();});
window.addEventListener('scroll',()=>{const menu=document.getElementById('accountDropdown');if(menu&&!menu.hidden)positionAccountDropdown();},{passive:true});
</script>
'''
if '</body>' not in text:
    raise SystemExit('body closing tag not found')
text = text.replace('</body>', script + '\n</body>', 1)

path.write_text(text,encoding='utf-8')
print('accountDropdownV1 installed')
