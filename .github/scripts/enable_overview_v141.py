from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')
link = '<link rel="stylesheet" href="assets/ui-overview-v141.css?v=141">'
anchor = '<link rel="stylesheet" href="assets/ui-layout-v138.css?v=138">'
if link not in s:
    if anchor not in s:
        raise SystemExit('ui layout stylesheet anchor not found')
    s = s.replace(anchor, anchor + '\n' + link, 1)
p.write_text(s, encoding='utf-8')
print('overview v141 enabled')
