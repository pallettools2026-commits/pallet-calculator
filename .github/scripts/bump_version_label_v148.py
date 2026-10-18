from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')
old = 'assets/version-label-fix-v142.js?v=147'
new = 'assets/version-label-fix-v142.js?v=148'
if new in s:
    print('version label cache already v148')
elif old in s:
    p.write_text(s.replace(old, new, 1), encoding='utf-8')
    print('bumped version label cache to v148')
else:
    raise SystemExit('version label script reference not found')
