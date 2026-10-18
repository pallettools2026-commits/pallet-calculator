from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')
old='assets/version-label-fix-v142.js?v=142'
new='assets/version-label-fix-v142.js?v=143'
if old in s:
    s=s.replace(old,new,1)
elif new not in s:
    raise SystemExit('version label script reference not found')
p.write_text(s,encoding='utf-8')
print('version label cache bumped to v143')
