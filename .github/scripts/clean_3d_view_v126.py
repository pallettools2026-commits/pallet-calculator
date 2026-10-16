from pathlib import Path
import re

js_path=Path('assets/pallet3d-v10.js')
idx_path=Path('index.html')
js=js_path.read_text(encoding='utf-8')
idx=idx_path.read_text(encoding='utf-8')

# Version marker
js=re.sub(r'/\* pallet3dStandardOnlyV\d+[^\n]*\*/','/* pallet3dStandardOnlyV126 — clean visible standard 3D */',js,count=1)

# Keep unsupported sizes non-3D, but remove any curtain/overlay and restore clean card behavior for supported sizes.
old=re.compile(r"    const profile=resolveProfile\(inputL,inputW\);\n    const previewCard=root\.closest\('\.previewCard'\);\n    if\(profile\.key==='unsupported'\)\{.*?    syncProfileInputs\(profile\);",re.S)
new="""    const profile=resolveProfile(inputL,inputW);
    const previewCard=root.closest('.previewCard');
    const previewStage=el('previewStage');
    const previewActions=previewCard?.querySelector('.previewActions');
    if(profile.key==='unsupported'){
      state.mode='3d';state.selected='all';
      root.innerHTML='';
      if(previewCard)previewCard.style.display='';
      if(previewStage)previewStage.style.display='none';
      if(previewActions)previewActions.style.display='none';
      return;
    }
    if(previewCard)previewCard.style.display='';
    if(previewStage)previewStage.style.display='flex';
    if(previewActions)previewActions.style.display='flex';
    root.style.display='block';
    root.style.width='100%';
    root.style.padding='0';
    root.style.minHeight='0';
    syncProfileInputs(profile);"""
js,n=old.subn(new,js,count=1)
if n!=1:
    raise SystemExit('profile/unsupported block replacement failed')

# Remove the visual strip/title that sat above the model and give the canvas a clean full-width stage.
pattern=re.compile(r"    const chip=\(k,label,c\)=>.*?    root\.innerHTML=`.*?`;\n",re.S)
replacement="""    const chip=(k,label,c)=>`<button type=\"button\" class=\"palletPartChip ${state.selected===k?'active':''}\" data-p3d-part=\"${k}\">${label}<b>${c}</b></button>`;
    root.innerHTML=`<div class=\"pallet3dToolbar\" role=\"tablist\"><button type=\"button\" data-p3d-mode=\"3d\" class=\"${mode==='3d'?'active':''}\">3D</button><button type=\"button\" data-p3d-mode=\"top\" class=\"${mode==='top'?'active':''}\">Сверху</button><button type=\"button\" data-p3d-mode=\"side\" class=\"${mode==='side'?'active':''}\">Сбоку</button><button type=\"button\" data-p3d-mode=\"explode\" class=\"${mode==='explode'?'active':''}\">${mode==='explode'?'Собрать':'Разнести'}</button></div><div class=\"palletReferenceStage\" style=\"width:100%;position:relative;overflow:hidden;background:radial-gradient(circle at 50% 30%,#fff 0,#faf8f3 52%,#efede7 100%);border-radius:14px;margin-top:8px\"><div class=\"palletReferenceHost\" style=\"width:100%;min-height:390px;position:relative\"></div></div><div class=\"palletModelLegend\">${chip('deck','Настил',deckCount)}${chip('cross','Обвязка',3)}${chip('runner','Лыжи',runnerCount)}${chip('block','Шашки',blockCount)}</div>`;
"""
js,n=pattern.subn(replacement,js,count=1)
if n!=1:
    raise SystemExit('3D header/curtain markup replacement failed')

# User-specified block size for the visible pallet model: 95 x 95 x 75 mm.
js,n=re.subn(r"    const blockH=.*?;\n", "    const blockH=.75,blockXSize1=.95,blockZSize1=.95,blockXSize2=.95,blockZSize2=.95;\n", js, count=1)
if n!=1:
    raise SystemExit('block geometry replacement failed')

# Default calculator/display now opens on the supported 1200 x 800 standard pallet.
repls={
    '<input id=\"pL\" type=\"number\" value=\"1250\">':'<input id=\"pL\" type=\"number\" value=\"1200\">',
    '<input id=\"pW\" type=\"number\" value=\"1180\">':'<input id=\"pW\" type=\"number\" value=\"800\">',
    'id=\"previewSize\">1250 × 1180 мм':'id=\"previewSize\">1200 × 800 мм',
    'id=\"dashPreviewSize\">1250 × 1180 мм':'id=\"dashPreviewSize\">1200 × 800 мм',
    'id=\"dashOrderTitle\">Поддон 1250 × 1180':'id=\"dashOrderTitle\">Поддон 1200 × 800',
    'id=\"palletSize\">1250 × 1180 мм':'id=\"palletSize\">1200 × 800 мм'
}
for a,b in repls.items():
    if a not in idx:
        raise SystemExit('missing index fragment: '+a)
    idx=idx.replace(a,b,1)

idx,n=re.subn(r'assets/pallet3d-v10\.js\?v=\d+','assets/pallet3d-v10.js?v=126',idx,count=1)
if n!=1:
    raise SystemExit('active 3D script ref not found')

js_path.write_text(js,encoding='utf-8')
idx_path.write_text(idx,encoding='utf-8')
print('clean 3D view installed; blocks 95x95x75; default 1200x800; cache v126')
