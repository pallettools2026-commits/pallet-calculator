from pathlib import Path

path = Path('index.html')
text = path.read_text(encoding='utf-8')
old = 'assets/version-label-fix-v142.js?v=143'
new = 'assets/version-label-fix-v142.js?v=145'
if old not in text and new not in text:
    raise SystemExit('version label script reference not found')
text = text.replace(old, new)
path.write_text(text, encoding='utf-8')
