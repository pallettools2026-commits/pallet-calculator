from pathlib import Path
import re

js_path = Path('assets/pallet3d-v10.js')
idx_path = Path('index.html')
js = js_path.read_text(encoding='utf-8')
idx = idx_path.read_text(encoding='utf-8')

old = "<div class=\"palletModelLegend\">${chip('deck','Настил',deckCount)}${chip('cross','Обвязка',3)}${chip('runner','Лыжи',runnerCount)}${chip('block','Шашки',blockCount)}</div>"
if old in js:
    js = js.replace(old, '', 1)
else:
    # Fallback in case whitespace/minor formatting changed.
    js, n = re.subn(r'<div class=\"palletModelLegend\">.*?</div>', '', js, count=1)
    if n != 1:
        raise SystemExit('palletModelLegend block not found')

# Bump active asset version so browsers load the updated renderer immediately.
idx, n = re.subn(r'assets/pallet3d-v10\.js\?v=\d+', 'assets/pallet3d-v10.js?v=127', idx, count=1)
if n != 1:
    raise SystemExit('active pallet3d-v10 reference not found')

js_path.write_text(js, encoding='utf-8')
idx_path.write_text(idx, encoding='utf-8')
print('Removed 3D part legend chips and bumped cache to v127')
