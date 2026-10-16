from pathlib import Path
p=Path('index.html')
s=p.read_text(encoding='utf-8')
old='assets/pallet3d-v9.js?v=92'
new='assets/pallet3d-v9.js?v=100'
if new in s:
    raise SystemExit('already bumped')
if old not in s:
    raise SystemExit('pallet3d asset reference not found')
p.write_text(s.replace(old,new,1),encoding='utf-8')
print('pallet3d cache version bumped to 100')
