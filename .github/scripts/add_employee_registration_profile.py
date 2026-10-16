from pathlib import Path

path=Path('index.html')
text=path.read_text(encoding='utf-8')
if 'employeeRegistrationProfileV1' in text:
    raise SystemExit('employeeRegistrationProfileV1 already installed')

marker='<div class="authFields" id="authFields">\n'
extra='''<div class="authRegisterOnly" id="authRegisterOnly" hidden>\n  <div class="authField">\n    <label for="authFullName">♙ &nbsp; Ф.И.О.</label>\n    <div class="authInputWrap"><span class="authInputIcon">♙</span><input id="authFullName" type="text" autocomplete="name" placeholder="Иванов Иван Иванович"></div>\n  </div>\n  <div class="authField">\n    <label for="authPosition">▣ &nbsp; ДОЛЖНОСТЬ</label>\n    <div class="authInputWrap"><span class="authInputIcon">▣</span><input id="authPosition" type="text" autocomplete="organization-title" placeholder="Например: мастер участка"></div>\n  </div>\n</div>\n'''
if marker not in text:
    raise SystemExit('auth fields marker not found')
text=text.replace(marker,marker+extra,1)

notice='    <div class="authNotice"><span>ⓘ</span><div id="authState">Войдите или создайте аккаунт.</div></div>\n'
card='''    <div class="lastEmployeeCard" id="lastEmployeeCard" hidden>\n      <div class="lastEmployeeAvatar">👤</div>\n      <div class="lastEmployeeInfo"><small>Ф.И.О.</small><strong id="lastEmployeeName">—</strong><small>Должность</small><span id="lastEmployeePosition">—</span></div>\n    </div>\n'''
if notice not in text:
    raise SystemExit('auth notice marker not found')
text=text.replace(notice,notice+card,1)

old='''document.getElementById("signupBtn").addEventListener("click",async()=>{\n const email=authEmail.value.trim(), password=authPassword.value;\n if(!email||password.length<6){setAuthMessage("Введите email и пароль минимум из 6 символов.",true);return;}\n setAuthMessage("Создаём аккаунт…");\n const {data,error}=await sb.auth.signUp({email,password,options:{emailRedirectTo:SITE_URL}});'''
new='''document.getElementById("signupBtn").addEventListener("click",async()=>{\n const signupBtn=document.getElementById("signupBtn");\n const reg=document.getElementById("authRegisterOnly");\n if(signupBtn.dataset.mode!=="register"){\n   signupBtn.dataset.mode="register";\n   if(reg)reg.hidden=false;\n   signupBtn.innerHTML="Создать аккаунт <span>→</span>";\n   setAuthMessage("Заполните Ф.И.О., должность, email и пароль.");\n   document.getElementById("authFullName")?.focus();\n   return;\n }\n const fullName=(document.getElementById("authFullName")?.value||"").trim();\n const position=(document.getElementById("authPosition")?.value||"").trim();\n const email=authEmail.value.trim(), password=authPassword.value;\n if(!fullName||!position||!email||password.length<6){setAuthMessage("Заполните Ф.И.О., должность, email и пароль минимум из 6 символов.",true);return;}\n setAuthMessage("Создаём аккаунт сотрудника…");\n const {data,error}=await sb.auth.signUp({email,password,options:{emailRedirectTo:SITE_URL,data:{full_name:fullName,position}}});'''
if old not in text:
    raise SystemExit('signup handler marker not found')
text=text.replace(old,new,1)

text=text.replace('.select("role,email")','.select("role,email,full_name,position")',1)
role_line='''   if(data?.role)role=data.role;}catch(e){}'''
role_new='''   if(data?.role)role=data.role;\n   const remembered={email:user.email||data?.email||"",full_name:data?.full_name||user.user_metadata?.full_name||"",position:data?.position||user.user_metadata?.position||"",role};\n   try{localStorage.setItem("pallettools:lastEmployee",JSON.stringify(remembered));}catch(e){}\n  }catch(e){\n   const remembered={email:user.email||"",full_name:user.user_metadata?.full_name||"",position:user.user_metadata?.position||"",role};\n   try{localStorage.setItem("pallettools:lastEmployee",JSON.stringify(remembered));}catch(_){}\n  }'''
if role_line not in text:
    raise SystemExit('profile role line not found')
text=text.replace(role_line,role_new,1)

else_line='''   authState.textContent="Войдите или создайте аккаунт.";'''
else_new='''   authState.textContent="Войдите или создайте аккаунт.";\n   if(typeof renderLastEmployeeCard==="function")renderLastEmployeeCard();'''
text=text.replace(else_line,else_new,1)

css='''\n/* employeeRegistrationProfileV1 */\n.authRegisterOnly{display:grid;gap:14px}.authRegisterOnly[hidden]{display:none!important}.lastEmployeeCard{display:grid;grid-template-columns:42px 1fr;gap:10px;align-items:center;margin:-6px 0 16px;padding:11px 12px;border:1px solid #dbe5ef;border-radius:11px;background:linear-gradient(180deg,#f6faff,#eef6ff)}.lastEmployeeAvatar{display:grid;place-items:center;width:38px;height:38px;border-radius:10px;background:#fff;color:#5878a6;border:1px solid #dce6f0}.lastEmployeeInfo{display:grid;grid-template-columns:78px 1fr;gap:3px 10px;align-items:center;min-width:0}.lastEmployeeInfo small{font-size:9px;text-transform:uppercase;letter-spacing:.08em;color:#8a94a5;font-weight:850}.lastEmployeeInfo strong,.lastEmployeeInfo span{font-size:11px;color:#293247;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.lastEmployeeInfo strong{font-weight:850}.authRegisterBtn[data-mode="register"]{background:#176b4c!important;color:#fff!important;border-color:#176b4c!important}\n'''
text=text.replace('\n</style>',css+'\n</style>',1)

script='''\n<script>\n/* employeeRegistrationProfileV1 */\nfunction renderLastEmployeeCard(){\n const card=document.getElementById('lastEmployeeCard');\n if(!card)return;\n let info=null;\n try{info=JSON.parse(localStorage.getItem('pallettools:lastEmployee')||'null');}catch(e){}\n if(!info||(!info.full_name&&!info.email)){card.hidden=true;return;}\n const name=document.getElementById('lastEmployeeName');\n const pos=document.getElementById('lastEmployeePosition');\n if(name)name.textContent=info.full_name||info.email||'Сотрудник';\n if(pos)pos.textContent=info.position||(info.role==='admin'?'Администратор':'Сотрудник');\n card.hidden=false;\n const email=document.getElementById('authEmail');\n if(email&&!email.value&&info.email)email.value=info.email;\n}\nwindow.addEventListener('DOMContentLoaded',renderLastEmployeeCard);\n</script>\n'''
text=text.replace('</body>',script+'\n</body>',1)

path.write_text(text,encoding='utf-8')
print('employeeRegistrationProfileV1 installed')
