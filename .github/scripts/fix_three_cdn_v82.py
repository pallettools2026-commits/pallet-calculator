from pathlib import Path
p=Path('index.html')
s=p.read_text(encoding='utf-8')
old='https://cdn.jsdelivr.net/npm/three@0.170.0/build/three.min.js'
new='https://cdn.jsdelivr.net/npm/three@0.159.0/build/three.min.js'
if old not in s:
    if new in s: raise SystemExit('already fixed')
    raise SystemExit('three cdn reference not found')
s=s.replace(old,new,1)
p.write_text(s,encoding='utf-8')
print('Three.js compatibility CDN fixed')
