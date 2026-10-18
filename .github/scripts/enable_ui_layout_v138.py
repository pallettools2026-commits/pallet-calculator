from pathlib import Path

path = Path('index.html')
text = path.read_text(encoding='utf-8')
marker = '<link rel="stylesheet" href="assets/theme-industrial-v130.css?v=134">\n'
link = '<link rel="stylesheet" href="assets/ui-layout-v138.css?v=138">\n'

if link in text:
    print('ui layout already enabled')
else:
    if marker not in text:
        raise SystemExit('theme stylesheet marker not found')
    text = text.replace(marker, marker + link, 1)
    path.write_text(text, encoding='utf-8')
    print('enabled ui layout v138')
