from pathlib import Path

path = Path('index.html')
text = path.read_text(encoding='utf-8')
if 'logoutPrivacyCleanupV1' in text:
    raise SystemExit('logoutPrivacyCleanupV1 already installed')

old = '''   authState.textContent="Войдите или создайте аккаунт.";authFields.style.display="grid";logoutBtn.style.display="none";protectedApp.classList.add("appLocked");if(panel)panel.style.display="none";\n   if(typeof renderLastEmployeeCard==="function")renderLastEmployeeCard();\n   setAuthMessage("После регистрации Supabase отправит письмо для подтверждения email.");'''
new = '''   authState.textContent="Войдите или создайте аккаунт.";authFields.style.display="grid";logoutBtn.style.display="none";protectedApp.classList.add("appLocked");if(panel)panel.style.display="none";\n   // logoutPrivacyCleanupV1 — после выхода не оставляем данные прошлого сотрудника на экране входа\n   try{localStorage.removeItem("pallettools:lastEmployee");}catch(_){}\n   if(authEmail)authEmail.value="";\n   if(authPassword)authPassword.value="";\n   const fullNameInput=document.getElementById("authFullName"),positionInput=document.getElementById("authPosition");\n   if(fullNameInput)fullNameInput.value="";\n   if(positionInput)positionInput.value="";\n   const reg=document.getElementById("authRegisterOnly"),signup=document.getElementById("signupBtn");\n   if(reg)reg.hidden=true;\n   if(signup){delete signup.dataset.mode;signup.innerHTML='<span>♙</span> Регистрация';}\n   const lastCard=document.getElementById("lastEmployeeCard");\n   if(lastCard)lastCard.hidden=true;\n   const lastName=document.getElementById("lastEmployeeName"),lastPosition=document.getElementById("lastEmployeePosition");\n   if(lastName)lastName.textContent="—";\n   if(lastPosition)lastPosition.textContent="—";\n   if(typeof closeEmployeeProfile==="function")closeEmployeeProfile();\n   setAuthMessage("После регистрации Supabase отправит письмо для подтверждения email.");'''
if old not in text:
    raise SystemExit('logged-out session block not found')
text = text.replace(old, new, 1)

old_profile_logout = '''document.getElementById('profileLogout')?.addEventListener('click',async()=>{\n closeEmployeeProfile();\n const {error}=await sb.auth.signOut();\n if(error&&typeof setAuthMessage==='function')setAuthMessage('Ошибка выхода: '+error.message,true);\n});'''
new_profile_logout = '''document.getElementById('profileLogout')?.addEventListener('click',async()=>{\n closeEmployeeProfile();\n try{localStorage.removeItem('pallettools:lastEmployee');}catch(_){}\n const {error}=await sb.auth.signOut();\n if(error&&typeof setAuthMessage==='function')setAuthMessage('Ошибка выхода: '+error.message,true);\n});'''
if old_profile_logout not in text:
    raise SystemExit('profile logout handler not found')
text = text.replace(old_profile_logout, new_profile_logout, 1)

old_plain_logout = '''logoutBtn.addEventListener("click",async()=>{const {error}=await sb.auth.signOut();if(error)setAuthMessage("Ошибка выхода: "+error.message,true);});'''
new_plain_logout = '''logoutBtn.addEventListener("click",async()=>{try{localStorage.removeItem("pallettools:lastEmployee");}catch(_){}const {error}=await sb.auth.signOut();if(error)setAuthMessage("Ошибка выхода: "+error.message,true);});'''
if old_plain_logout in text:
    text = text.replace(old_plain_logout, new_plain_logout, 1)

path.write_text(text, encoding='utf-8')
print('logoutPrivacyCleanupV1 installed')
