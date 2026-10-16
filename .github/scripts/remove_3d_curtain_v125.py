from pathlib import Path
import re

js_path=Path('assets/pallet3d-v10.js')
idx_path=Path('index.html')
js=js_path.read_text(encoding='utf-8')
idx=idx_path.read_text(encoding='utf-8')

old="""    const profile=resolveProfile(inputL,inputW);
    if(profile.key==='unsupported'){
      state.mode='3d';state.selected='all';
      root.innerHTML=`<div style=\"min-height:390px;display:flex;align-items:center;justify-content:center;padding:28px\"><div style=\"width:min(100%,680px);text-align:center;padding:34px 24px;border:1px solid #dce7e1;border-radius:22px;background:linear-gradient(145deg,#fff,#f3f7f5);box-shadow:0 14px 34px rgba(19,65,53,.07)\"><div style=\"width:56px;height:56px;margin:0 auto 14px;border-radius:17px;display:grid;place-items:center;background:#e7f1ed;color:#1f6f5c;font-size:27px\">▦</div><strong style=\"display:block;font-size:22px;color:#173c33\">3D для ${Math.round(inputL)} × ${Math.round(inputW)} мм не предусмотрен</strong><p style=\"margin:10px auto 16px;max-width:540px;color:#65756d;line-height:1.5\">Размер не входит в список стандартных поддонов. Расчёт материалов, раскрой, сохранение заказа и производство работают как обычно.</p><div style=\"display:inline-flex;max-width:100%;flex-wrap:wrap;justify-content:center;gap:6px;padding:9px 12px;border-radius:12px;background:#edf5f1;color:#31584c;font-size:12px;font-weight:800\">3D: 1200 × 800 · 1200 × 1000 · 1000 × 1200 · 800 × 600</div></div></div>`;
      return;
    }
    syncProfileInputs(profile);"""
new="""    const profile=resolveProfile(inputL,inputW);
    const previewCard=root.closest('.previewCard');
    if(profile.key==='unsupported'){
      state.mode='3d';state.selected='all';
      root.innerHTML='';
      if(previewCard)previewCard.style.display='none';
      return;
    }
    if(previewCard)previewCard.style.display='';
    syncProfileInputs(profile);"""
if old not in js:
    raise SystemExit('unsupported 3D curtain block not found')
js=js.replace(old,new,1)
js=js.replace('/* pallet3dStandardOnlyV124 — standard pallet whitelist */','/* pallet3dStandardOnlyV125 — hide unsupported preview without curtain */',1)
idx,n=re.subn(r'assets/pallet3d-v10\.js\?v=\d+','assets/pallet3d-v10.js?v=125',idx,count=1)
if n!=1:
    raise SystemExit('active 3D asset reference not found')
js_path.write_text(js,encoding='utf-8')
idx_path.write_text(idx,encoding='utf-8')
print('removed unsupported 3D curtain and bumped asset to v125')
