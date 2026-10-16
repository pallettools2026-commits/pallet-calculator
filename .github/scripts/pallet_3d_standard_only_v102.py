from pathlib import Path

p=Path('assets/pallet3d-v9.js')
s=p.read_text(encoding='utf-8')

if 'pallet3dStandardOnlyV102' in s:
    raise SystemExit('already installed')

if '/* pallet3dReferenceV101 */' not in s:
    raise SystemExit('expected pallet3dReferenceV101 marker not found')

s=s.replace('/* pallet3dReferenceV101 */','/* pallet3dReferenceV102 */',1)

needle="""  const near=(a,b,t=2)=>Math.abs(Number(a)-Number(b))<=t;\n"""
insert="""  const near=(a,b,t=2)=>Math.abs(Number(a)-Number(b))<=t;\n  /* pallet3dStandardOnlyV102 */\n  const STANDARD_3D_PALLETS=[\n    {l:1200,w:800,name:'EUR / EPAL 1'},\n    {l:1200,w:1000,name:'EUR / EPAL 2'},\n    {l:1000,w:1200,name:'EUR / EPAL 3'},\n    {l:800,w:600,name:'EUR / EPAL 6'}\n  ];\n  function standard3DProfile(L,W){return STANDARD_3D_PALLETS.find(x=>near(L,x.l)&&near(W,x.w))||null;}\n"""
if needle not in s:
    raise SystemExit('near marker not found')
s=s.replace(needle,insert,1)

old="""    L=Math.max(300,Number(L)||1250);W=Math.max(300,Number(W)||1180);\n    const profile=profileFor(L,W),reference=profile.reference,mode=state.mode||'3d';\n"""
new="""    L=Math.max(300,Number(L)||1200);W=Math.max(300,Number(W)||800);\n    const standard=standard3DProfile(L,W);\n    if(!standard){\n      state.mode='3d';state.selected='all';\n      const supported=STANDARD_3D_PALLETS.map(x=>`${x.l} × ${x.w}`).join(' · ');\n      root.innerHTML=`<div style=\"min-height:390px;display:flex;align-items:center;justify-content:center;padding:28px\"><div style=\"width:min(100%,680px);text-align:center;padding:34px 24px;border:1px solid #dce7e1;border-radius:22px;background:linear-gradient(145deg,#fff,#f3f7f5);box-shadow:0 14px 34px rgba(19,65,53,.07)\"><div style=\"width:56px;height:56px;margin:0 auto 14px;border-radius:17px;display:grid;place-items:center;background:#e7f1ed;color:#1f6f5c;font-size:27px\">▦</div><strong style=\"display:block;font-size:22px;color:#173c33\">3D для ${Math.round(L)} × ${Math.round(W)} мм не предусмотрен</strong><p style=\"margin:10px auto 16px;max-width:520px;color:#65756d;line-height:1.5\">Это нестандартный размер. Расчёт материалов, раскрой, сохранение заказа и производство продолжают работать без 3D-модели.</p><div style=\"display:inline-flex;max-width:100%;flex-wrap:wrap;justify-content:center;gap:6px;padding:9px 12px;border-radius:12px;background:#edf5f1;color:#31584c;font-size:12px;font-weight:800\">3D доступен: ${supported}</div></div></div>`;\n      return;\n    }\n    const profile=profileFor(L,W),reference=false,mode=state.mode||'3d';\n    profile.spec=`${standard.name} · стандартный поддон ${standard.l} × ${standard.w} мм`;\n"""
if old not in s:
    raise SystemExit('render profile block not found')
s=s.replace(old,new,1)

s=s.replace("${reference?'Поддон по образцу':'Динамическая модель'} · ${mode==='explode'?'разнесённый вид':'реальный 3D'}","${standard.name} · ${mode==='explode'?'разнесённый вид':'реальный 3D'}",1)

p.write_text(s,encoding='utf-8')
print('pallet3dStandardOnlyV102 installed')
