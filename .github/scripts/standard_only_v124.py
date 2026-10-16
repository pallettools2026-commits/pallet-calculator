from pathlib import Path
import re

js_path=Path('assets/pallet3d-v10.js')
idx_path=Path('index.html')
js=js_path.read_text(encoding='utf-8')
idx=idx_path.read_text(encoding='utf-8')

if 'pallet3dStandardOnlyV124' in js:
    raise SystemExit('already installed')

js=re.sub(r"/\* pallet3dReferenceV\d+[^\n]*\*/","/* pallet3dStandardOnlyV124 — standard pallet whitelist */",js,count=1)

new_profile=r'''  function resolveProfile(inputL,inputW){
    const a=Math.max(300,num(inputL,1200)),b=Math.max(300,num(inputW,800));
    const match=(x,y)=>(near(a,x)&&near(b,y))||(near(a,y)&&near(b,x));
    const width=b,length=a;
    if(match(1200,800))return {key:'epal1',width,length,deckMax:7,bindingCount:3,runnerLengths:[length,length,length],spec:`EUR / EPAL 1 · ${Math.round(length)} × ${Math.round(width)} мм`};
    if(match(1200,1000))return {key:'epal2',width,length,deckMax:9,bindingCount:3,runnerLengths:[length,length,length],spec:`EUR / EPAL 2 · ${Math.round(length)} × ${Math.round(width)} мм`};
    if(match(1000,1200))return {key:'epal3',width,length,deckMax:9,bindingCount:3,runnerLengths:[length,length,length],spec:`EUR / EPAL 3 · ${Math.round(length)} × ${Math.round(width)} мм`};
    if(match(800,600))return {key:'epal6',width,length,deckMax:7,bindingCount:3,runnerLengths:[length,length,length],spec:`EUR / EPAL 6 · ${Math.round(length)} × ${Math.round(width)} мм`};
    return {key:'unsupported',width,length,deckMax:0,bindingCount:0,runnerLengths:[],spec:'Нестандартный размер'};
  }
'''
js,n=re.subn(r"  function resolveProfile\(inputL,inputW\)\{.*?\n  \}\n\n  function setInput",new_profile+"\n  function setInput",js,count=1,flags=re.S)
if n!=1:
    raise SystemExit('resolveProfile replacement failed')

old="""    const profile=resolveProfile(inputL,inputW);syncProfileInputs(profile);"""
new="""    const profile=resolveProfile(inputL,inputW);
    if(profile.key==='unsupported'){
      state.mode='3d';state.selected='all';
      root.innerHTML=`<div style="min-height:390px;display:flex;align-items:center;justify-content:center;padding:28px"><div style="width:min(100%,680px);text-align:center;padding:34px 24px;border:1px solid #dce7e1;border-radius:22px;background:linear-gradient(145deg,#fff,#f3f7f5);box-shadow:0 14px 34px rgba(19,65,53,.07)"><div style="width:56px;height:56px;margin:0 auto 14px;border-radius:17px;display:grid;place-items:center;background:#e7f1ed;color:#1f6f5c;font-size:27px">▦</div><strong style="display:block;font-size:22px;color:#173c33">3D для ${Math.round(inputL)} × ${Math.round(inputW)} мм не предусмотрен</strong><p style="margin:10px auto 16px;max-width:540px;color:#65756d;line-height:1.5">Размер не входит в список стандартных поддонов. Расчёт материалов, раскрой, сохранение заказа и производство работают как обычно.</p><div style="display:inline-flex;max-width:100%;flex-wrap:wrap;justify-content:center;gap:6px;padding:9px 12px;border-radius:12px;background:#edf5f1;color:#31584c;font-size:12px;font-weight:800">3D: 1200 × 800 · 1200 × 1000 · 1000 × 1200 · 800 × 600</div></div></div>`;
      return;
    }
    syncProfileInputs(profile);"""
if old not in js:
    raise SystemExit('render profile line missing')
js=js.replace(old,new,1)
js=js.replace("    const isReference=profile.key==='1250x1180';","    const isReference=false;",1)
js=js.replace("Для 1250 × 1180 используется отдельная модель по вашим фото · вращайте мышкой или пальцем · колесо — масштаб","Стандартная 3D-модель · вращайте мышкой или пальцем · колесо — масштаб",1)

# Force browsers to load the new active renderer.
idx,n=re.subn(r"assets/pallet3d-v10\.js\?v=\d+","assets/pallet3d-v10.js?v=124",idx,count=1)
if n!=1:
    raise SystemExit('active v10 script reference not found in index')

js_path.write_text(js,encoding='utf-8')
idx_path.write_text(idx,encoding='utf-8')
print('standard-only active v10 3D installed; cache bumped to v124')
