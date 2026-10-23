const seed=[
{id:"sawmill",name:"Лесопильный участок",type:"Распил и подготовка пиломатериала",employees:34,plan:17,active:8,done:74,load:112,defect:3.2,downtime:4.1,status:"Норма"},
{id:"pallets",name:"Поддонный участок",type:"Производство и сборка поддонов",employees:26,plan:22,active:11,done:81,load:86,defect:1.8,downtime:2.3,status:"Норма"},
{id:"kiln",name:"Сушильный комплекс",type:"Камерная сушка древесины",employees:18,plan:12,active:7,done:69,load:94,defect:2.6,downtime:6.8,status:"Внимание"},
{id:"repair",name:"Ремонт поддонов",type:"Ремонт и сортировка возвратной тары",employees:21,plan:17,active:5,done:87,load:71,defect:1.1,downtime:1.4,status:"Норма"}];
let productions=seed;
try{productions=JSON.parse(localStorage.getItem("pp_demo_productions")||"null")||seed}catch(e){productions=seed;}
const orders=[
["ORD-2418","Лесопильный участок","Доска 22×100","В работе","34 м³","26.10",68],
["PAL-118","Поддонный участок","EUR/EPAL","В работе","680 шт","25.10",72],
["DRY-72","Сушильный комплекс","Сосна 50 мм","В работе","28 м³","24.10",81],
["REP-401","Ремонт поддонов","EUR/EPAL ремонт","План","220 шт","24.10",25],
["PAL-121","Поддонный участок","1200×1000","План","420 шт","27.10",18]
];
const warehouse=[["Доска сосна 22×100","38.6 м³","12.4 м³","Норма"],["Брус 75×75","14.2 м³","6.8 м³","Норма"],["Доска ель 25×150","7.9 м³","3.0 м³","Низкий остаток"],["Поддонная шашка","18 420 шт","4 200 шт","Норма"]];
const defects=[["23.10","Поддонный участок","Скол доски","18 шт","Средний"],["22.10","Лесопильный участок","Обзол","1.8 м³","Высокий"],["22.10","Ремонт поддонов","Повреждение блока","14 шт","Низкий"]];
const employees=[["Иван Петров","Лесопильный участок","Мастер","На смене"],["Алексей Соколов","Поддонный участок","Бригадир","На смене"],["Мария Орлова","Сушильный комплекс","Оператор","На смене"],["Сергей Волков","Ремонт поддонов","Сортировщик","Выходной"]];
const downtime=[["Сушильный комплекс","Сушильная камера №2","4.6 ч","Техобслуживание"],["Лесопильный участок","Линия распила","1.8 ч","Замена пилы"],["Поддонный участок","Сборочная линия","0.7 ч","Настройка"]];

const $=s=>document.querySelector(s), $$=s=>[...document.querySelectorAll(s)];
function esc(s){return String(s).replace(/[&<>"']/g,m=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[m]))}
function toast(msg){const t=$("#toast");t.textContent=msg;t.classList.add("show");setTimeout(()=>t.classList.remove("show"),1800)}
function saveLocal(){try{localStorage.setItem("pp_demo_productions",JSON.stringify(productions))}catch(e){}refreshSelect()}
function refreshSelect(){const s=$("#productionSelect");s.innerHTML='<option value="all">Все производства</option>'+productions.map(p=>`<option value="${p.id}">${esc(p.name)}</option>`).join("");$("#ownerSummary").textContent=`${productions.length} производства · ${productions.reduce((a,p)=>a+p.employees,0)} сотрудников`}
function setActive(page){$$("#nav button").forEach(b=>b.classList.toggle("active",b.dataset.page===page))}
function layout(title,subtitle,buttons=""){return `<div class="hero"><div><h1>${title}</h1><p>${subtitle}</p></div><div class="btns">${buttons}</div></div>`}
function kpis(items){return `<div class="kpis">${items.map(x=>`<div class="kpi"><span>${x[0]}</span><b>${x[1]}</b><small class="${x[3]||""}">${x[2]||""}</small></div>`).join("")}</div>`}
function table(headers,rows,clickable=false){return `<div class="panel"><table class="table"><thead><tr>${headers.map(h=>`<th>${h}</th>`).join("")}</tr></thead><tbody>${rows.map((r,i)=>`<tr ${clickable?`class="clickable" data-row="${i}"`:""}>${r.map(c=>`<td>${c}</td>`).join("")}</tr>`).join("")}</tbody></table></div>`}
function statusClass(p){return p.status==="Внимание"?"warn":"ok"}

function renderDashboard(){
 const totalPlan=productions.reduce((a,p)=>a+p.plan,0), totalActive=productions.reduce((a,p)=>a+p.active,0), avgDone=Math.round(productions.reduce((a,p)=>a+p.done,0)/productions.length), avgLoad=Math.round(productions.reduce((a,p)=>a+p.load,0)/productions.length), emp=productions.reduce((a,p)=>a+p.employees,0);
 $("#content").innerHTML=layout("Дашборд владельца","Все ключевые показатели производств на одном экране",`<button class="btn" id="exportBtn">Экспорт CSV</button><button class="btn primary" id="addProdBtn">+ Производство</button>`)+
 kpis([["Всего в плане",totalPlan,"заказов"],["Сейчас в работе",totalActive,"активных"],["Выполнено",avgDone+"%","+4% к периоду","good"],["Средняя загрузка",avgLoad+"%",productions.some(p=>p.load>100)?"Есть перегрузка":"В норме",productions.some(p=>p.load>100)?"bad":"good"],["Сотрудники",emp,"по компании"]])+
 `<div class="section"><div class="section-head"><h2>Показатели по каждому производству</h2><small>Кликните «Открыть»</small></div><div class="grid2">${productions.map(p=>`<div class="card"><div class="cardhead"><div><b>${esc(p.name)}</b><small>${esc(p.type)}</small></div><span class="status ${statusClass(p)}">${p.status}</span></div><div class="cardbody"><div class="mini"><div><span>В плане</span><b>${p.plan}</b></div><div><span>В работе</span><b>${p.active}</b></div><div><span>Выполнено</span><b>${p.done}%</b></div><div><span>Загрузка</span><b>${p.load}%</b></div><div><span>Сотрудники</span><b>${p.employees}</b></div></div><div class="progress"><i style="width:${Math.min(p.load,100)}%"></i></div><button class="open" data-open="${p.id}">Открыть производство →</button></div></div>`).join("")}</div></div>`;
 $$("[data-open]").forEach(b=>b.onclick=()=>renderProduction(b.dataset.open));
 $("#addProdBtn").onclick=openAddProduction; $("#exportBtn").onclick=exportCsv;
}
function renderProductions(){
 $("#content").innerHTML=layout("Все производства","Список производственных площадок",`<button class="btn primary" id="addProdBtn">+ Производство</button>`)+table(["Производство","Тип","Сотрудники","План","Загрузка","Статус"],productions.map(p=>[esc(p.name),esc(p.type),p.employees,p.plan,p.load+"%",`<span class="status ${statusClass(p)}">${p.status}</span>`]),true);
 $$(".clickable").forEach((tr,i)=>tr.onclick=()=>renderProduction(productions[i].id)); $("#addProdBtn").onclick=openAddProduction;
}
function renderPlan(){ $("#content").innerHTML=layout("План производства","Плановые задания по всем участкам",`<button class="btn primary" id="newPlan">+ Плановое задание</button>`)+table(["Производство","В плане","В работе","Выполнение","Загрузка"],productions.map(p=>[p.name,p.plan,p.active,p.done+"%",p.load+"%"])); $("#newPlan").onclick=()=>simpleModal("Новое плановое задание","Форма демо: выберите производство и количество.","Плановое задание создано");}
function renderOrders(){ $("#content").innerHTML=layout("Заказы","Текущие производственные заказы",`<button class="btn primary" id="newOrder">+ Заказ</button>`)+table(["№","Производство","Изделие","Статус","Количество","Срок","Прогресс"],orders.map(o=>[...o.slice(0,6),o[6]+"%"]),true); $("#newOrder").onclick=()=>simpleModal("Новый заказ","Демо-форма нового заказа.","Заказ добавлен"); $$(".clickable").forEach((tr,i)=>tr.onclick=()=>toast("Открыт заказ "+orders[i][0]));}
function renderWarehouse(){ $("#content").innerHTML=layout("Склад пиломатериала","Остатки и резерв сырья",`<button class="btn primary" id="receipt">+ Приход</button>`)+table(["Материал","Остаток","Резерв","Статус"],warehouse.map(r=>[r[0],r[1],r[2],r[3]==="Низкий остаток"?`<span class="status warn">${r[3]}</span>`:`<span class="status ok">${r[3]}</span>`])); $("#receipt").onclick=()=>simpleModal("Приход материала","Демо-форма прихода на склад.","Приход сохранён");}
function renderDefects(){ $("#content").innerHTML=layout("Журнал дефектов","Контроль брака и причин отклонений",`<button class="btn primary" id="newDef">+ Дефект</button>`)+table(["Дата","Производство","Дефект","Количество","Критичность"],defects); $("#newDef").onclick=()=>simpleModal("Новый дефект","Демо-форма регистрации дефекта.","Дефект зарегистрирован");}
function renderEmployees(){ $("#content").innerHTML=layout("Сотрудники","Сотрудники по всем производствам",`<button class="btn primary" id="newEmp">+ Сотрудник</button>`)+table(["Сотрудник","Производство","Роль","Статус"],employees); $("#newEmp").onclick=()=>simpleModal("Новый сотрудник","Демо-форма добавления сотрудника.","Сотрудник добавлен");}
function renderDowntime(){ const sum=downtime.reduce((a,r)=>a+parseFloat(r[2]),0).toFixed(1); $("#content").innerHTML=layout("Простои","Причины и длительность остановок")+kpis([["Простой сегодня",sum+" ч","по компании"],["Крупнейший","4.6 ч","Сушильная камера №2","bad"],["Активные причины","3","записи"]])+`<div class="section">${table(["Производство","Оборудование","Длительность","Причина"],downtime)}</div>`}
function renderSettings(){ $("#content").innerHTML=layout("Настройки","Демо-настройки отдельного чёрного сайта")+`<div class="panel" style="padding:14px"><div class="formgrid"><div class="field"><label>Название компании</label><input id="companyName" value="PalletTools Group"></div><div class="field"><label>Язык</label><select><option>Русский</option><option>English</option></select></div><div class="field"><label>Часовой пояс</label><select><option>Europe/Helsinki</option><option>Europe/Moscow</option></select></div><div class="field"><label>Уведомления</label><select><option>Включены</option><option>Выключены</option></select></div></div><button class="btn primary" id="saveSettings" style="margin-top:12px">Сохранить настройки</button></div>`; $("#saveSettings").onclick=()=>toast("Настройки сохранены в демо");}
function renderProduction(id){
 const p=productions.find(x=>x.id===id); if(!p)return;
 $("#productionSelect").value=id; $("#crumb").textContent="Производство · "+p.name; setActive("productions");
 $("#content").innerHTML=layout(p.name,p.type,`<button class="btn" id="back">← Все производства</button><button class="btn primary" id="editProd">Изменить</button>`)+
 kpis([["В плане",p.plan,"заказов"],["В работе",p.active,"активно"],["Выполнено",p.done+"%","за период"],["Загрузка",p.load+"%",p.load>100?"Перегрузка":"Норма",p.load>100?"bad":"good"],["Сотрудники",p.employees,"человек"]])+
 `<div class="section"><div class="tabs" id="prodTabs">${["План","Заказы","Наряд и табель","Факт","Бригада","Простои"].map((x,i)=>`<button class="${i===0?"active":""}" data-tab="${x}">${x}</button>`).join("")}</div><div id="tabBody" style="margin-top:10px"></div></div>`;
 $("#back").onclick=()=>go("productions"); $("#editProd").onclick=()=>editProduction(p);
 $$("#prodTabs button").forEach(b=>b.onclick=()=>{$$("#prodTabs button").forEach(x=>x.classList.remove("active"));b.classList.add("active");renderProdTab(p,b.dataset.tab)});
 renderProdTab(p,"План");
}
function renderProdTab(p,tab){
 const box=$("#tabBody");
 if(tab==="План") box.innerHTML=table(["Показатель","Значение"],[["Заказов в плане",p.plan],["В работе",p.active],["Выполнение",p.done+"%"],["Загрузка",p.load+"%"]]);
 else if(tab==="Заказы") box.innerHTML=table(["№","Изделие","Статус","Количество","Срок","Прогресс"],orders.filter(o=>o[1]===p.name).map(o=>[o[0],o[2],o[3],o[4],o[5],o[6]+"%"]));
 else if(tab==="Наряд и табель") box.innerHTML=table(["Смена","Работают","Часы","Статус"],[["Смена A",Math.ceil(p.employees*.55),"8 ч","Активна"],["Смена B",Math.floor(p.employees*.45),"8 ч","Следующая"]]);
 else if(tab==="Факт") box.innerHTML=kpis([["Выполнено",p.done+"%","плана"],["Брак",p.defect+"%","за период"],["Простои",p.downtime+" ч","за период"]]);
 else if(tab==="Бригада") box.innerHTML=table(["Показатель","Значение"],[["Сотрудники",p.employees],["На смене",Math.round(p.employees*.76)],["Отсутствуют",Math.round(p.employees*.24)]]);
 else box.innerHTML=table(["Показатель","Значение"],[["Простои",p.downtime+" ч"],["Основная причина",p.id==="kiln"?"Техобслуживание":"Настройка/замена инструмента"]]);
}
function openAddProduction(){
 $("#modalTitle").textContent="Добавить производство"; $("#modalBody").innerHTML=`<div class="formgrid"><div class="field"><label>Название</label><input id="mName" placeholder="Например: Цех №5"></div><div class="field"><label>Тип</label><input id="mType" placeholder="Направление производства"></div><div class="field"><label>Сотрудники</label><input id="mEmp" type="number" value="10"></div><div class="field"><label>План заказов</label><input id="mPlan" type="number" value="5"></div></div>`; $("#modalBack").classList.add("show");
 $("#modalSave").onclick=()=>{const name=$("#mName").value.trim();if(!name){toast("Введите название");return}productions.push({id:"p"+Date.now(),name,type:$("#mType").value||"Новое производство",employees:+$("#mEmp").value||0,plan:+$("#mPlan").value||0,active:0,done:0,load:0,defect:0,downtime:0,status:"Норма"});saveLocal();closeModal();renderDashboard();toast("Производство добавлено")};
}
function editProduction(p){
 $("#modalTitle").textContent="Изменить производство"; $("#modalBody").innerHTML=`<div class="formgrid"><div class="field"><label>Название</label><input id="mName" value="${esc(p.name)}"></div><div class="field"><label>Сотрудники</label><input id="mEmp" type="number" value="${p.employees}"></div><div class="field"><label>План</label><input id="mPlan" type="number" value="${p.plan}"></div><div class="field"><label>Загрузка, %</label><input id="mLoad" type="number" value="${p.load}"></div></div>`; $("#modalBack").classList.add("show");
 $("#modalSave").onclick=()=>{p.name=$("#mName").value||p.name;p.employees=+$("#mEmp").value||0;p.plan=+$("#mPlan").value||0;p.load=+$("#mLoad").value||0;saveLocal();closeModal();renderProduction(p.id);toast("Изменения сохранены")};
}
function simpleModal(title,text,success){$("#modalTitle").textContent=title;$("#modalBody").innerHTML=`<p style="color:#8b929d;font-size:9px">${text}</p><div class="field"><label>Комментарий</label><input id="demoComment" placeholder="Можно ввести текст"></div>`;$("#modalBack").classList.add("show");$("#modalSave").onclick=()=>{closeModal();toast(success)}}
function closeModal(){$("#modalBack").classList.remove("show")}
function exportCsv(){const rows=[["Производство","План","В работе","Выполнено","Загрузка","Сотрудники"],...productions.map(p=>[p.name,p.plan,p.active,p.done+"%",p.load+"%",p.employees])];const csv="\ufeff"+rows.map(r=>r.map(v=>`"${String(v).replace(/"/g,'""')}"`).join(";")).join("\n");const a=document.createElement("a");a.href=URL.createObjectURL(new Blob([csv],{type:"text/csv"}));a.download="production-pulse.csv";a.click();URL.revokeObjectURL(a.href);toast("CSV сформирован")}
function go(page){setActive(page);$("#productionSelect").value="all";const map={dashboard:["Дашборд владельца",renderDashboard],productions:["Все производства",renderProductions],plan:["План производства",renderPlan],orders:["Заказы",renderOrders],warehouse:["Склад пиломатериала",renderWarehouse],defects:["Журнал дефектов",renderDefects],employees:["Сотрудники",renderEmployees],downtime:["Простои",renderDowntime],settings:["Настройки",renderSettings]};$("#crumb").textContent=map[page][0];map[page][1]()}
$("#nav").onclick=e=>{const b=e.target.closest("button[data-page]");if(b)go(b.dataset.page)};
$("#productionSelect").onchange=e=>e.target.value==="all"?go("dashboard"):renderProduction(e.target.value);
$("#settingsBtn").onclick=()=>go("settings");
$("#notifyBtn").onclick=()=>simpleModal("Уведомления","1 производство требует внимания: Сушильный комплекс.","Просмотрено");
$("#modalCancel").onclick=closeModal;$("#modalBack").onclick=e=>{if(e.target.id==="modalBack")closeModal()};
$("#search").oninput=e=>{const q=e.target.value.toLowerCase().trim();if(!q)return;const p=productions.find(x=>(x.name+" "+x.type).toLowerCase().includes(q));if(p){renderProduction(p.id);return}const b=$$("#nav button").find(x=>x.textContent.toLowerCase().includes(q));if(b)go(b.dataset.page)};
refreshSelect();go("dashboard");