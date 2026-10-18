from pathlib import Path
import re

js_path=Path('assets/pallet3d-v10.js')
html_path=Path('index.html')
js=js_path.read_text(encoding='utf-8')
html=html_path.read_text(encoding='utf-8')
old="      if(!sideView){\n        const edgeZ=Math.min(deckL/2,PL/2);"
new="      if(!sideView&&kindVisible('deck')){\n        const edgeZ=Math.min(deckL/2,PL/2);"
if old not in js:
    raise SystemExit('deck measure visibility target not found')
js=js.replace(old,new,1)
html=re.sub(r'assets/pallet3d-v10\.js\?v=\d+','assets/pallet3d-v10.js?v=133',html)
js_path.write_text(js,encoding='utf-8')
html_path.write_text(html,encoding='utf-8')
print('assembly measure visibility fixed')
