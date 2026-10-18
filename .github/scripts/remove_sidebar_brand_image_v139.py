from pathlib import Path

path = Path('assets/ui-layout-v138.css')
text = path.read_text(encoding='utf-8')
marker = '/* sidebarBrandTextOnlyV139 */'
if marker in text:
    raise SystemExit('sidebar brand patch already applied')

text += '''\n\n/* sidebarBrandTextOnlyV139 */\n@media(min-width:1151px){\n  .sideBrand{gap:0!important;padding-left:10px!important;padding-right:10px!important}\n  .sideBrand img{display:none!important}\n  .sideBrand strong{font-size:16px!important;letter-spacing:-.2px!important}\n  .sideBrand span{font-size:10px!important;margin-top:4px!important}\n}\n'''
path.write_text(text, encoding='utf-8')
print('Removed sidebar brand image; colors unchanged.')
