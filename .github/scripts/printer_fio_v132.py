from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

old='''function updatePrintMeta(){\n const order=document.getElementById("orderNo").value.trim()||"—";\n const worker=document.getElementById("worker").value.trim()||"—";\n const date=document.getElementById("jobDate").value||"—";\n const time=document.getElementById("jobTime")?.value||"";\n document.getElementById("printMeta").textContent=`Заказ: ${order} • Сотрудник / смена: ${worker} • Дата и время: ${date}${time?` ${time}`:""}`;\n}\ndocument.getElementById("printBtn").addEventListener("click",()=>{updatePrintMeta();window.print();});'''

new='''function currentPrinterFullName(){\n let name=currentUser?.user_metadata?.full_name||"";\n try{\n  const remembered=JSON.parse(localStorage.getItem("pallettools:lastEmployee")||"null");\n  if(remembered?.full_name)name=remembered.full_name;\n }catch(_){ }\n return name||"Ф.И.О. не указано";\n}\n\nfunction updatePrintMeta(){\n const order=document.getElementById("orderNo").value.trim()||"—";\n const worker=document.getElementById("worker").value.trim()||"—";\n const date=document.getElementById("jobDate").value||"—";\n const time=document.getElementById("jobTime")?.value||"";\n const printer=currentPrinterFullName();\n document.getElementById("printMeta").textContent=`Заказ: ${order} • Сотрудник / смена: ${worker} • Дата и время: ${date}${time?` ${time}`:""} • Распечатал: ${printer}`;\n}\ndocument.getElementById("printBtn").addEventListener("click",()=>{updatePrintMeta();window.print();});'''

if old not in s:
    raise SystemExit('updatePrintMeta block not found')
s=s.replace(old,new,1)

old_all='''document.getElementById("printAllBtn").addEventListener("click",()=>{\n if(saved.length===0){\n  alert("Сначала сохрани хотя бы один расчёт.");\n  return;\n }\n window.print();'''
new_all='''document.getElementById("printAllBtn").addEventListener("click",()=>{\n if(saved.length===0){\n  alert("Сначала сохрани хотя бы один расчёт.");\n  return;\n }\n updatePrintMeta();\n window.print();'''
if old_all not in s:
    raise SystemExit('printAll block not found')
s=s.replace(old_all,new_all,1)

p.write_text(s,encoding='utf-8')
print('printer full name added to both print modes')
