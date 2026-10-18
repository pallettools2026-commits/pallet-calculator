from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')
old = 'const pallet3DState={angle:-28,mode:"3d",selected:"all",dragging:false,startX:0,startAngle:-28,pointerId:null};'
new = 'const pallet3DState=window.pallet3DState||(window.pallet3DState={angle:-28,mode:"3d",selected:"all",dragging:false,startX:0,startAngle:-28,pointerId:null});'
if old not in s:
    raise SystemExit('pallet3DState anchor not found')
s = s.replace(old, new, 1)
p.write_text(s, encoding='utf-8')
print('Unified pallet 3D state; 45-degree rotation now controls the active Three.js view')
