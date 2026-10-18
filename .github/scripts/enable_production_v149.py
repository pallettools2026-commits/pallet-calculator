from pathlib import Path
import re

p = Path('index.html')
s = p.read_text(encoding='utf-8')
link = '<link rel="stylesheet" href="assets/ui-production-v149.css?v=149">'
if link not in s:
    pattern = r'(<link rel="stylesheet" href="assets/ui-overview-v141\.css\?v=\d+">)'
    if not re.search(pattern, s):
        raise SystemExit('overview stylesheet anchor not found')
    s = re.sub(pattern, r'\1\n' + link, s, count=1)
p.write_text(s, encoding='utf-8')
print('production v149 enabled')
