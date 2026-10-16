from pathlib import Path

path=Path('index.html')
text=path.read_text(encoding='utf-8')
if 'employeeProfilePanelV1' in text:
    raise SystemExit('employeeProfilePanelV1 already installed')

protected='<div id="protectedApp" class="appLocked">'
if protected not in text:
    raise SystemExit('protected app marker not found')

modal=r'''
<!-- employeeProfilePanelV1 -->
<div class="profileModal" id="profileModal" hidden>
  <div class="profileModalBackdrop" data-profile-close></div>
  <section class="profilePanel" role="dialog" aria-modal="true" aria-labelledby="profileTitle">
    <div class="profilePanelHead">
      <div><div class="profileEyebrow">СОТРУДНИК</div><h2 id="profileTitle">Мой профиль</h2><p>Ф.И.О. и должность используются в Pallet Tools и на экране входа.</p></div>
      <button class="profileClose" id="profileClose" type="button" aria-label="Закрыть">×</button>
    </div>
    <div class="profileIdentity">
      <div class="profileAvatar">👤</div>
      <div><strong id="profileIdentityName">Сотрудник</strong><span id="profileIdentityRole">Профиль Pallet Tools</span></div>
    </div>
    <div class="profileForm">
      <div><label for="profileFullName">Ф.И.О.</label><input id="profileFullName" type="text" autocomplete="name" placeholder="Иванов Иван Иванович"></div>
      <div><label for="profilePosition">Должность</label><input id="profilePosition" type="text" autocomplete="organization-title" placeholder="Например: мастер участка"></div>
      <div class="profileEmailRow"><label>Email</label><div id="profileEmail">—</div></div>
    </div>
    <div class="profileMessage" id="profileMessage">Заполните данные и нажмите «Сохранить».</div>
    <div class="profileActions">
      <button class="profileLogout" id="profileLogout" type="button">Выйти из аккаунта</button>
      <button class="profileSave" id="profileSave" type="button">Сохранить профиль</button>
    </div>
  </section>
</div>
'''
text=text.replace(protected,modal+'\n'+protected,1)

side_marker='''    <button class="navLink appSideLink adminSideLink" type="button" data-scroll="adminPanel"><span>⚙</span>Админ-панель</button>'''
side_new='''    <button class="navLink appSideLink" id="profileSideBtn" type="button"><span>👤</span>Мой профиль</button>\n'''+side_marker
if side_marker in text:
    text=text.replace(side_marker,side_new,1)

old_top='''document.getElementById("topAccount")?.addEventListener("click",async()=>{if(currentUser){await sb.auth.signOut();}else{document.getElementById("authCard")?.scrollIntoView({behavior:"smooth",block:"center"});}});'''
new_top='''document.getElementById("topAccount")?.addEventListener("click",async()=>{if(currentUser){if(typeof openEmployeeProfile==="function")await openEmployeeProfile();}else{document.getElementById("authCard")?.scrollIntoView({behavior:"smooth",block:"center"});}});'''
if old_top not in text:
    raise SystemExit('top account listener marker not found')
text=text.replace(old_top,new_top,1)

css=r'''
/* employeeProfilePanelV1 */
.profileModal[hidden]{display:none!important}.profileModal{position:fixed;inset:0;z-index:11000;display:grid;place-items:center;padding:18px}.profileModalBackdrop{position:absolute;inset:0;background:rgba(12,27,23,.42);backdrop-filter:blur(5px)}.profilePanel{position:relative;width:min(100%,470px);max-height:calc(100vh - 36px);overflow:auto;background:#fff;border:1px solid #dce7e2;border-radius:20px;padding:22px;box-shadow:0 28px 70px rgba(9,42,32,.24)}.profilePanelHead{display:flex;align-items:flex-start;justify-content:space-between;gap:14px}.profileEyebrow{font-size:9px;letter-spacing:.14em;font-weight:900;color:#247357;margin-bottom:4px}.profilePanelHead h2{margin:0!important;font-size:23px!important;color:#17231f!important}.profilePanelHead p{margin:5px 0 0;color:#718078;font-size:11px;line-height:1.45;max-width:330px}.profileClose{width:36px;height:36px;flex:0 0 auto;border:1px solid #e0e7e3;border-radius:10px;background:#f7faf8;color:#53655d;font-size:22px;line-height:1;cursor:pointer}.profileIdentity{display:flex;align-items:center;gap:11px;margin:18px 0;padding:12px;border:1px solid #dfe9e4;border-radius:13px;background:linear-gradient(135deg,#f4faf7,#fbfcfb)}.profileAvatar{display:grid;place-items:center;width:43px;height:43px;border-radius:12px;background:#e4f4ec;font-size:21px}.profileIdentity strong{display:block;color:#1b2b25;font-size:14px}.profileIdentity span{display:block;margin-top:2px;color:#718078;font-size:10px}.profileForm{display:grid;gap:12px}.profileForm label{font-size:10px!important;letter-spacing:.06em;text-transform:uppercase;color:#627269!important;font-weight:850!important}.profileForm input{min-height:47px!important;font-size:14px!important;border-radius:11px!important}.profileEmailRow{display:grid;gap:6px}.profileEmailRow>div{padding:12px;border:1px solid #e1e8e4;border-radius:11px;background:#f8faf9;color:#5d6d65;font-size:13px;overflow-wrap:anywhere}.profileMessage{min-height:17px;margin-top:12px;color:#718078;font-size:11px;line-height:1.4}.profileActions{display:flex;justify-content:space-between;gap:9px;margin-top:16px}.profileActions button{min-height:45px;border-radius:11px;padding:10px 14px;font-size:12px;font-weight:850;cursor:pointer}.profileLogout{border:1px solid #e0e5e3;background:#f6f8f7;color:#6a504d}.profileSave{border:0;background:#176b4c;color:#fff;box-shadow:0 8px 18px rgba(23,107,76,.18)}.profileSave:disabled{opacity:.6;cursor:wait}
@media(max-width:560px){.profileModal{padding:10px;align-items:end}.profilePanel{width:100%;max-height:88vh;border-radius:20px 20px 14px 14px;padding:19px}.profileActions{flex-direction:column-reverse}.profileActions button{width:100%;min-height:49px}}
'''
text=text.replace('\n</style>',css+'\n</style>',1)

script=r'''
<script>
/* employeeProfilePanelV1 */
function closeEmployeeProfile(){
 const modal=document.getElementById('profileModal');
 if(modal)modal.hidden=true;
}
async function openEmployeeProfile(){
 const modal=document.getElementById('profileModal');
 const msg=document.getElementById('profileMessage');
 if(!modal||!currentUser)return;
 modal.hidden=false;
 if(msg){msg.textContent='Загружаем профиль…';msg.style.color='#718078';}
 const {data,error}=await sb.from('profiles').select('email,full_name,position,role').eq('id',currentUser.id).single();
 if(error){if(msg){msg.textContent='Не удалось загрузить профиль: '+error.message;msg.style.color='#a12622';}return;}
 const fullName=data?.full_name||currentUser.user_metadata?.full_name||'';
 const position=data?.position||currentUser.user_metadata?.position||'';
 const role=data?.role||currentRole||'employee';
 const nameInput=document.getElementById('profileFullName'),posInput=document.getElementById('profilePosition');
 if(nameInput)nameInput.value=fullName;
 if(posInput)posInput.value=position;
 const email=document.getElementById('profileEmail');if(email)email.textContent=data?.email||currentUser.email||'—';
 const ident=document.getElementById('profileIdentityName');if(ident)ident.textContent=fullName||'Сотрудник';
 const roleEl=document.getElementById('profileIdentityRole');if(roleEl)roleEl.textContent=position||(role==='admin'?'Администратор':'Сотрудник');
 if(msg){msg.textContent=fullName&&position?'Данные профиля заполнены.':'Заполните Ф.И.О. и должность.';msg.style.color='#718078';}
 setTimeout(()=>nameInput?.focus(),40);
}
document.getElementById('profileClose')?.addEventListener('click',closeEmployeeProfile);
document.querySelector('[data-profile-close]')?.addEventListener('click',closeEmployeeProfile);
document.getElementById('profileSideBtn')?.addEventListener('click',openEmployeeProfile);
document.addEventListener('keydown',e=>{if(e.key==='Escape')closeEmployeeProfile();});
document.getElementById('profileSave')?.addEventListener('click',async e=>{
 if(!currentUser)return;
 const btn=e.currentTarget,msg=document.getElementById('profileMessage');
 const fullName=(document.getElementById('profileFullName')?.value||'').trim();
 const position=(document.getElementById('profilePosition')?.value||'').trim();
 if(!fullName||!position){if(msg){msg.textContent='Введите Ф.И.О. и должность.';msg.style.color='#a12622';}return;}
 btn.disabled=true;if(msg){msg.textContent='Сохраняем…';msg.style.color='#718078';}
 const {error}=await sb.rpc('update_own_profile',{p_full_name:fullName,p_position:position});
 if(error){btn.disabled=false;if(msg){msg.textContent='Не удалось сохранить: '+error.message;msg.style.color='#a12622';}return;}
 try{await sb.auth.updateUser({data:{full_name:fullName,position}});}catch(_){ }
 const remembered={email:currentUser.email||'',full_name:fullName,position,role:currentRole||'employee'};
 try{localStorage.setItem('pallettools:lastEmployee',JSON.stringify(remembered));}catch(_){ }
 const ident=document.getElementById('profileIdentityName');if(ident)ident.textContent=fullName;
 const roleEl=document.getElementById('profileIdentityRole');if(roleEl)roleEl.textContent=position;
 const topName=document.getElementById('topAccountText');if(topName)topName.textContent=fullName;
 const topSub=document.getElementById('topAccountSub');if(topSub)topSub.textContent=position;
 if(typeof renderLastEmployeeCard==='function')renderLastEmployeeCard();
 btn.disabled=false;if(msg){msg.textContent='Профиль сохранён.';msg.style.color='#176b4c';}
});
document.getElementById('profileLogout')?.addEventListener('click',async()=>{
 closeEmployeeProfile();
 const {error}=await sb.auth.signOut();
 if(error&&typeof setAuthMessage==='function')setAuthMessage('Ошибка выхода: '+error.message,true);
});
</script>
'''
text=text.replace('</body>',script+'\n</body>',1)

path.write_text(text,encoding='utf-8')
print('employeeProfilePanelV1 installed')
