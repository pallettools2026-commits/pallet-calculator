from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')
old='assets/pallet3d-v9.js?v=100'
new='assets/pallet3d-v9.js?v=101'
if new in s:
    print('already bumped')
elif old in s:
    p.write_text(s.replace(old,new,1),encoding='utf-8')
    print('bumped to v101')
else:
    raise SystemExit('pallet3d script reference not found')
