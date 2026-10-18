from pathlib import Path

root = Path('.')
site = root / 'truck-site'
assets = site / 'assets'
assets.mkdir(parents=True, exist_ok=True)

source_html = root / 'truck-planner.html'
source_css = root / 'assets' / 'truck-planner-v1.css'
source_js = root / 'assets' / 'truck-planner-v10.js'
source_img = root / 'assets' / 'pallet-clean-3d-2.webp'

for p in (source_html, source_css, source_js, source_img):
    if not p.exists():
        raise SystemExit(f'missing source: {p}')

html = source_html.read_text(encoding='utf-8')
html = html.replace('<title>Pallet Tools — загрузка фуры</title>', '<title>Truck Load Planner — Pallet Tools</title>')
html = html.replace('href="index.html"', 'href="./"')
html = html.replace('← В Pallet Tools', 'Truck Load Planner')
html = html.replace('TRUCK LOAD PLANNER · RESILIENT INTERACTIVE 3D', 'TRUCK LOAD PLANNER · ОТДЕЛЬНЫЙ САЙТ · INTERACTIVE 3D')
html = html.replace('3D V9', '3D LAB')
html = html.replace('PALLET TOOLS · RED LONG-HOOD TRUCK · SAFE 3D FALLBACK · V9', 'TRUCK LOAD PLANNER · PALLET TOOLS · 3D LAB')
html = html.replace('assets/truck-planner-v10.js?v=20261018-2025', 'assets/truck-planner-v10.js?v=1')
html = html.replace('assets/truck-planner-v1.css?v=1', 'assets/truck-planner-v1.css?v=1')

(site / 'index.html').write_text(html, encoding='utf-8')
(assets / 'truck-planner-v1.css').write_bytes(source_css.read_bytes())
(assets / 'truck-planner-v10.js').write_bytes(source_js.read_bytes())
(assets / 'pallet-clean-3d-2.webp').write_bytes(source_img.read_bytes())

(site / 'vercel.json').write_text('''{
  "cleanUrls": true,
  "trailingSlash": false,
  "headers": [
    {
      "source": "/assets/(.*)",
      "headers": [{"key": "Cache-Control", "value": "public, max-age=3600"}]
    }
  ]
}\n''', encoding='utf-8')

# Remove the old public Truck Planner page from the main Pallet Tools site.
source_html.unlink()

print('Separated truck planner into truck-site/ and removed root truck-planner.html')
