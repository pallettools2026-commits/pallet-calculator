from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')
link='<link rel="stylesheet" href="assets/theme-industrial-v130.css?v=130">'
if link not in s:
    marker='</style>'
    if marker not in s:
        raise SystemExit('style marker missing')
    s=s.replace(marker, marker+'\n'+link, 1)
p.write_text(s,encoding='utf-8')
print('industrial theme linked')
