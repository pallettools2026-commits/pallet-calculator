from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')
old='["Шашка 1",6,75,98,150],'
new='["Шашка 1",9,75,98,150],'
if new in s:
    raise SystemExit('already updated')
if old not in s:
    raise SystemExit('target not found')
p.write_text(s.replace(old,new,1),encoding='utf-8')
