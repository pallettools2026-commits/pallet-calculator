from pathlib import Path
p=Path('index.html')
s=p.read_text(encoding='utf-8')
old='assets/pallet3d-v9.js?v=100'
new='assets/pallet3d-v10.js?v=110'
if new in s:
    raise SystemExit('already switched')
if old not in s:
    raise SystemExit('old pallet3d reference not found')
p.write_text(s.replace(old,new,1),encoding='utf-8')
print('switched pallet 3D to v110')
