from pathlib import Path

js_path=Path('assets/pallet3d-v10.js')
idx_path=Path('index.html')
js=js_path.read_text(encoding='utf-8')
idx=idx_path.read_text(encoding='utf-8')

repls=[
("/* pallet3dReferenceV121 — flush-edge block pallet geometry */","/* pallet3dReferenceV122 — all pallet blocks rotated 90 degrees */"),
("const blockH=Math.max(.62,num(block1.t||block2.t,75)*S),blockXSize1=Math.max(.72,num(block1.w,98)*S),blockZSize1=Math.max(.72,num(block1.l,150)*S),blockXSize2=Math.max(.72,num(block2.w,100)*S),blockZSize2=Math.max(.72,num(block2.l,98)*S);","const blockH=Math.max(.62,num(block1.t||block2.t,75)*S),blockXSize1=Math.max(.72,num(block1.l,150)*S),blockZSize1=Math.max(.72,num(block1.w,98)*S),blockXSize2=Math.max(.72,num(block2.l,98)*S),blockZSize2=Math.max(.72,num(block2.w,100)*S);")
]
for old,new in repls:
    if old not in js:
        raise SystemExit(f'missing JS target: {old[:80]}')
    js=js.replace(old,new,1)
old_ref='assets/pallet3d-v10.js?v=121'
new_ref='assets/pallet3d-v10.js?v=122'
if old_ref not in idx:
    raise SystemExit('missing index cache target')
idx=idx.replace(old_ref,new_ref,1)
js_path.write_text(js,encoding='utf-8')
idx_path.write_text(idx,encoding='utf-8')
print('rotated all pallet block footprints by 90 degrees and bumped cache to v122')
