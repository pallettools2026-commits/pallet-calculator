from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

# Replace manual date field with automatic date/time display while keeping hidden values
old='<div><label>Дата</label><input id="jobDate" type="date"></div>'
new='''<div class="autoDateTimeField"><label>Дата и время</label><div class="autoDateTimeValue" aria-live="polite"><span id="jobDateDisplay">—</span><strong id="jobTimeDisplay">—</strong></div><input id="jobDate" type="hidden"><input id="jobTime" type="hidden"><small>Автоматически по времени устройства</small></div>'''
if old not in s:
    raise SystemExit('manual date field marker missing')
s=s.replace(old,new,1)

# Styling for the automatic clock block
css='''\n/* autoDateTimeV1 */\n.autoDateTimeField{min-width:0}\n.autoDateTimeValue{min-height:48px;display:flex;align-items:center;justify-content:space-between;gap:12px;padding:10px 12px;border:1px solid var(--line);border-radius:11px;background:var(--surface-soft);color:var(--text);font-variant-numeric:tabular-nums}\n.autoDateTimeValue span{font-size:16px;font-weight:750}\n.autoDateTimeValue strong{font-size:18px;letter-spacing:.04em;color:var(--primary-deep)}\n.autoDateTimeField small{display:block;margin-top:5px;color:var(--muted);font-size:11px}\n'''
if '/* autoDateTimeV1 */' not in s:
    s=s.replace('</style>',css+'\n</style>',1)

# Save current time with calculations
old='  jobDate:document.getElementById("jobDate").value,\n  items'
new='  jobDate:document.getElementById("jobDate").value,\n  jobTime:document.getElementById("jobTime")?.value||"",\n  items'
if old not in s:
    raise SystemExit('record jobDate marker missing')
s=s.replace(old,new,1)

# Local saved-card metadata
old='${rec.jobDate ? ` • ${rec.jobDate}` : ""}</div>'
new='${rec.jobDate ? ` • ${rec.jobDate}${rec.jobTime ? ` ${rec.jobTime}` : ""}` : ""}</div>'
if old in s:
    s=s.replace(old,new,1)

# Print metadata includes time
old=''' const date=document.getElementById("jobDate").value||"—";\n document.getElementById("printMeta").textContent=`Заказ: ${order} • Сотрудник / смена: ${worker} • Дата: ${date}`;'''
new=''' const date=document.getElementById("jobDate").value||"—";\n const time=document.getElementById("jobTime")?.value||"";\n document.getElementById("printMeta").textContent=`Заказ: ${order} • Сотрудник / смена: ${worker} • Дата и время: ${date}${time?` ${time}`:""}`;'''
if old not in s:
    raise SystemExit('print metadata date marker missing')
s=s.replace(old,new,1)

# Replace one-time date initialization with live local date/time clock
old='''const dateInput=document.getElementById("jobDate");\nif(dateInput && !dateInput.value){\n const d=new Date(),y=d.getFullYear(),m=String(d.getMonth()+1).padStart(2,"0"),day=String(d.getDate()).padStart(2,"0");\n dateInput.value=`${y}-${m}-${day}`;\n}\n'''
new='''const dateInput=document.getElementById("jobDate");\nconst timeInput=document.getElementById("jobTime");\nfunction syncJobDateTime(){\n const d=new Date(),y=d.getFullYear(),m=String(d.getMonth()+1).padStart(2,"0"),day=String(d.getDate()).padStart(2,"0"),hh=String(d.getHours()).padStart(2,"0"),mm=String(d.getMinutes()).padStart(2,"0"),ss=String(d.getSeconds()).padStart(2,"0");\n const isoDate=`${y}-${m}-${day}`,clock=`${hh}:${mm}:${ss}`,pretty=d.toLocaleDateString("ru-RU",{day:"2-digit",month:"2-digit",year:"numeric"});\n if(dateInput)dateInput.value=isoDate;\n if(timeInput)timeInput.value=clock;\n const dateDisplay=document.getElementById("jobDateDisplay"),timeDisplay=document.getElementById("jobTimeDisplay");\n if(dateDisplay)dateDisplay.textContent=pretty;\n if(timeDisplay)timeDisplay.textContent=clock;\n const dashDate=document.getElementById("dashOrderDate");\n if(dashDate)dashDate.textContent=`${pretty} · ${clock}`;\n}\nsyncJobDateTime();\nsetInterval(syncJobDateTime,1000);\ndocument.addEventListener("visibilitychange",()=>{if(!document.hidden)syncJobDateTime();});\n'''
if old not in s:
    raise SystemExit('date initializer marker missing')
s=s.replace(old,new,1)

# Cloud record round-trip: store time in calculation_data without DB schema changes
old='return {id:payload.legacy_id||row.id,cloudId:row.id,created:new Date(row.created_at).toLocaleString("ru-RU"),palletLength:Number(row.pallet_length),palletWidth:Number(row.pallet_width),quantity:Number(row.pallet_count),orderNo:row.order_number||"",worker:row.employee_name||row.shift_name||"",jobDate:row.work_date||"",items:Array.isArray(payload.items)?payload.items:[]};'
new='return {id:payload.legacy_id||row.id,cloudId:row.id,created:new Date(row.created_at).toLocaleString("ru-RU"),palletLength:Number(row.pallet_length),palletWidth:Number(row.pallet_width),quantity:Number(row.pallet_count),orderNo:row.order_number||"",worker:row.employee_name||row.shift_name||"",jobDate:row.work_date||"",jobTime:payload.job_time||"",items:Array.isArray(payload.items)?payload.items:[]};'
if old not in s:
    raise SystemExit('dbRecord marker missing')
s=s.replace(old,new,1)

old='function toDb(rec){return {user_id:currentUser.id,order_number:rec.orderNo||null,shift_name:null,employee_name:rec.worker||null,work_date:rec.jobDate||new Date().toISOString().slice(0,10),pallet_length:rec.palletLength,pallet_width:rec.palletWidth,pallet_count:rec.quantity,calculation_data:{items:rec.items||[],legacy_id:rec.id}};}'
new='function toDb(rec){return {user_id:currentUser.id,order_number:rec.orderNo||null,shift_name:null,employee_name:rec.worker||null,work_date:rec.jobDate||new Date().toISOString().slice(0,10),pallet_length:rec.palletLength,pallet_width:rec.palletWidth,pallet_count:rec.quantity,calculation_data:{items:rec.items||[],legacy_id:rec.id,job_time:rec.jobTime||null}};}'
if old not in s:
    raise SystemExit('toDb marker missing')
s=s.replace(old,new,1)

# Cloud saved-card metadata shows time
old='${rec.jobDate?` • ${esc(rec.jobDate)}`:""}</div></div><button'
new='${rec.jobDate?` • ${esc(rec.jobDate)}${rec.jobTime?` ${esc(rec.jobTime)}`:""}`:""}</div></div><button'
if old not in s:
    raise SystemExit('cloud saved metadata marker missing')
s=s.replace(old,new,1)

# Dashboard should not overwrite the live automatic time with just a date
old="const L=num('pL'),W=num('pW'),Q=num('qty'),order=text('orderNo'),worker=text('worker'),date=$('jobDate')?.value||'—';"
new="const L=num('pL'),W=num('pW'),Q=num('qty'),order=text('orderNo'),worker=text('worker'),date=$('jobDate')?.value||'—',time=$('jobTime')?.value||'';"
if old not in s:
    raise SystemExit('dashboard date variable marker missing')
s=s.replace(old,new,1)

old="if($('dashOrderDate'))$('dashOrderDate').textContent=date!=='—'?date:'Укажите дату';"
new="if($('dashOrderDate')){const pretty=$('jobDateDisplay')?.textContent||date;$('dashOrderDate').textContent=date!=='—'?`${pretty}${time?` · ${time}`:''}`:'—';}"
if old not in s:
    raise SystemExit('dashboard date output marker missing')
s=s.replace(old,new,1)

p.write_text(s,encoding='utf-8')
print('Automatic date and live clock installed')
