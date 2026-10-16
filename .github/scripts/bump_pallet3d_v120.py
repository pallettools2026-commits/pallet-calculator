from pathlib import Path
p=Path('index.html')
s=p.read_text(encoding='utf-8')
old='assets/pallet3d-v10.js?v=110'
new='assets/pallet3d-v10.js?v=120'
if new in s:
    raise SystemExit('already bumped')
if old not in s:
    raise SystemExit('pallet 3D asset reference not found')
p.write_text(s.replace(old,new,1),encoding='utf-8')
print('pallet 3D cache version bumped to 120')
