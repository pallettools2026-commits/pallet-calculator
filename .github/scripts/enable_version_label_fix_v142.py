from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')
tag='<script src="assets/version-label-fix-v142.js?v=142"></script>'
if tag not in s:
    anchor='</body>'
    if anchor not in s:
        raise SystemExit('body closing tag not found')
    s=s.replace(anchor,tag+'\n'+anchor,1)
p.write_text(s,encoding='utf-8')
print('version label fix v142 enabled')
