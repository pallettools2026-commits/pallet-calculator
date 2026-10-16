from pathlib import Path

path = Path('index.html')
text = path.read_text(encoding='utf-8')

if 'authScreenV2' in text:
    raise SystemExit('authScreenV2 already installed')

start = text.find('<section class="authCard" id="authCard">')
if start < 0:
    raise SystemExit('authCard start not found')
end = text.find('</section>', start)
if end < 0:
    raise SystemExit('authCard end not found')
end += len('</section>')

new_auth = r'''<section class="authCard authScreenV2" id="authCard">
  <div class="authBackdropGlow authGlowOne"></div>
  <div class="authBackdropGlow authGlowTwo"></div>
  <div class="authLoginPanel">
    <div class="authAccent"></div>
    <div class="authBrand">
      <img src="assets/pallet-clean-3d-2.webp" alt="Pallet Tools">
      <div class="authBrandName"><strong>PALLET</strong><span>TOOLS</span></div>
    </div>
    <div class="authWelcome">
      <h2>Добро пожаловать</h2>
      <p>Войдите или создайте аккаунт<br>для работы с Pallet Tools</p>
    </div>
    <div class="authNotice"><span>ⓘ</span><div id="authState">Войдите или создайте аккаунт.</div></div>
    <div class="authFields" id="authFields">
      <div class="authField">
        <label for="authEmail">✉ &nbsp; ЭЛЕКТРОННАЯ ПОЧТА</label>
        <div class="authInputWrap"><span class="authInputIcon">✉</span><input id="authEmail" type="email" autocomplete="email" placeholder="name@example.com"></div>
      </div>
      <div class="authField">
        <label for="authPassword">♙ &nbsp; ПАРОЛЬ</label>
        <div class="authInputWrap"><span class="authInputIcon">⌑</span><input id="authPassword" type="password" autocomplete="current-password" minlength="6" placeholder="Минимум 6 символов"><button class="passwordToggle" id="passwordToggle" type="button" aria-label="Показать пароль">◉</button></div>
      </div>
      <button class="authBtn authLoginPrimary" id="loginBtn" type="button">Войти <span>→</span></button>
      <div class="authDivider"><span></span><b>или</b><span></span></div>
      <button class="authBtn secondary authRegisterBtn" id="signupBtn" type="button"><span>♙</span> Регистрация</button>
    </div>
    <div class="authMessage" id="authMessage">После регистрации мы отправим письмо для подтверждения email.</div>
    <button class="authBtn logout" id="logoutBtn" type="button" style="display:none">Выйти</button>
    <div class="authDots"><i></i><i></i><i></i></div>
    <div class="authVersion">Pallet Tools · secure access</div>
  </div>
</section>'''

text = text[:start] + new_auth + text[end:]

css = r'''

/* authScreenV2 */
.authCard.authScreenV2{position:fixed;inset:0;z-index:10000;margin:0!important;padding:24px!important;max-width:none!important;border:0!important;border-radius:0!important;background:linear-gradient(135deg,#eef5ff 0%,#f7f9fb 45%,#fff4ef 100%)!important;display:grid;place-items:center;overflow:auto;box-shadow:none!important;color:#191d2d}
.authCard.authScreenV2.loggedIn{display:none!important}
.authBackdropGlow{position:absolute;border-radius:50%;filter:blur(80px);opacity:.38;pointer-events:none}.authGlowOne{width:360px;height:360px;left:-80px;top:-60px;background:#cfe2ff}.authGlowTwo{width:390px;height:390px;right:-100px;bottom:-80px;background:#f6d8d0}
.authLoginPanel{position:relative;width:min(100%,420px);background:rgba(255,255,255,.94);border:1px solid rgba(218,225,232,.9);border-radius:24px;padding:34px 34px 26px;box-shadow:0 25px 60px rgba(24,35,52,.14);overflow:hidden;backdrop-filter:blur(18px)}
.authAccent{position:absolute;left:0;right:0;top:0;height:3px;background:linear-gradient(90deg,#8b7cff,#76d8bf,#f2a174)}
.authBrand{display:flex;flex-direction:column;align-items:center;gap:5px;margin-bottom:22px}.authBrand img{width:74px;height:58px;object-fit:contain;filter:drop-shadow(0 7px 10px rgba(130,84,41,.14))}.authBrandName{display:flex;flex-direction:column;align-items:center;line-height:1}.authBrandName strong{font-size:20px;letter-spacing:.15em;color:#171a27}.authBrandName span{font-size:11px;letter-spacing:.42em;color:#aa6c38;margin-left:.42em;margin-top:4px;font-weight:900}
.authWelcome{text-align:center}.authWelcome h2{margin:0;color:#191d2d;font-size:27px;line-height:1.15;font-weight:900}.authWelcome p{margin:8px 0 0;color:#7b8292;font-size:13px;line-height:1.5}
.authNotice{display:flex;align-items:center;justify-content:center;gap:8px;margin:22px 0 18px;padding:10px 12px;border:1px solid #f8cfbc;border-radius:10px;background:#fff3ed;color:#d36b3f;font-size:12px;font-weight:800}.authNotice>span{font-size:16px}.authNotice #authState{color:inherit;font-size:inherit;margin:0}
.authFields{display:grid!important;grid-template-columns:1fr!important;gap:14px!important}.authField{display:grid;gap:6px}.authField label{font-size:10px!important;letter-spacing:.11em;color:#747c8d!important;font-weight:900!important}.authInputWrap{position:relative}.authInputWrap input{width:100%;min-height:50px;border:1px solid #dfe4eb!important;border-radius:11px!important;background:#fff!important;padding:12px 44px 12px 42px!important;font-size:14px!important;color:#202636!important;box-shadow:inset 0 1px 2px rgba(20,30,45,.02)}.authInputWrap input:focus{border-color:#93b9ff!important;box-shadow:0 0 0 3px rgba(83,135,235,.11)!important;outline:none}.authInputIcon{position:absolute;left:14px;top:50%;transform:translateY(-50%);color:#8f98a9;font-size:16px;z-index:2;pointer-events:none}.passwordToggle{position:absolute;right:10px;top:50%;transform:translateY(-50%);width:34px;height:34px;border:0;background:transparent;color:#7f8797;font-size:16px;cursor:pointer;border-radius:8px}.passwordToggle:hover{background:#f2f4f7}
.authLoginPrimary{min-height:52px!important;margin-top:2px!important;border-radius:11px!important;background:#17192d!important;color:#fff!important;border:0!important;font-size:14px!important;font-weight:900!important;box-shadow:0 10px 20px rgba(23,25,45,.16)!important}.authLoginPrimary:hover{transform:translateY(-1px);filter:brightness(1.06)}.authLoginPrimary span{margin-left:7px;font-size:18px}
.authDivider{display:grid;grid-template-columns:1fr auto 1fr;gap:11px;align-items:center;color:#a0a7b4;font-size:10px;text-transform:uppercase;letter-spacing:.1em}.authDivider span{height:1px;background:#e4e7eb}.authDivider b{font-weight:800}
.authRegisterBtn{min-height:48px!important;border-radius:11px!important;border:1px solid #dfe4eb!important;background:#fff!important;color:#252b3b!important;font-size:13px!important;font-weight:850!important}.authRegisterBtn:hover{background:#f8fafb!important}.authRegisterBtn span{margin-right:7px}
.authMessage{text-align:center!important;color:#9299a7!important;font-size:10px!important;line-height:1.45!important;margin-top:13px!important;min-height:14px}.authDots{display:flex;justify-content:center;gap:8px;margin-top:17px}.authDots i{width:7px;height:7px;border-radius:50%;background:#dfe3ea}.authDots i:first-child{background:#747b8d}.authVersion{text-align:center;margin-top:10px;color:#b0b6c1;font-size:9px;letter-spacing:.07em}.authCard .logout{display:none!important}
@media(max-width:560px){.authCard.authScreenV2{padding:16px!important}.authLoginPanel{width:100%;padding:28px 20px 22px;border-radius:21px}.authBrand{margin-bottom:18px}.authWelcome h2{font-size:24px}.authNotice{margin:18px 0 16px;font-size:11px}.authInputWrap input{min-height:52px;font-size:16px!important}.authLoginPrimary,.authRegisterBtn{min-height:52px!important}}
@media(max-height:720px){.authLoginPanel{padding-top:24px;padding-bottom:18px}.authBrand{margin-bottom:12px}.authBrand img{width:58px;height:44px}.authWelcome h2{font-size:23px}.authWelcome p{margin-top:4px}.authNotice{margin:13px 0}.authFields{gap:10px!important}.authDots,.authVersion{display:none}}
'''
if '</style>' not in text:
    raise SystemExit('style close not found')
text = text.replace('\n</style>', css + '\n</style>', 1)

js = r'''
<script>
/* authScreenV2 interactions */
(function(){
 const pwd=document.getElementById('authPassword');
 const toggle=document.getElementById('passwordToggle');
 if(pwd&&toggle){toggle.addEventListener('click',()=>{const show=pwd.type==='password';pwd.type=show?'text':'password';toggle.textContent=show?'◌':'◉';toggle.setAttribute('aria-label',show?'Скрыть пароль':'Показать пароль');});}
 const account=document.getElementById('topAccount');
 if(account){account.addEventListener('click',async()=>{try{if(typeof currentUser!=='undefined'&&currentUser&&window.sb){if(confirm('Выйти из Pallet Tools?'))await sb.auth.signOut();}}catch(e){console.warn(e);}});}
})();
</script>
'''
if '</body>' not in text:
    raise SystemExit('body close not found')
text = text.replace('</body>', js + '\n</body>', 1)

path.write_text(text, encoding='utf-8')
print('authScreenV2 installed')
