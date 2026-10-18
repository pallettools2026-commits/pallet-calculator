from pathlib import Path

index = Path('index.html')
css = Path('assets/ui-layout-v138.css')

html = index.read_text(encoding='utf-8')
html = html.replace('src="assets/pallet-clean-3d-1.webp" alt=""', 'src="assets/pallet-hero-3d.webp?v=140" alt="3D деревянный поддон"', 1)
html = html.replace('assets/ui-layout-v138.css?v=138', 'assets/ui-layout-v138.css?v=140')
index.write_text(html, encoding='utf-8')

style = css.read_text(encoding='utf-8')
marker = '/* sidebarBrand3DV140 */'
if marker not in style:
    style += r'''

/* sidebarBrand3DV140 */
@media(min-width:1151px){
  .sideBrand{gap:10px!important;padding:6px 8px 14px!important;align-items:center!important}
  .sideBrand img{
    display:block!important;
    width:54px!important;
    height:42px!important;
    object-fit:contain!important;
    flex:0 0 54px!important;
    border:0!important;
    border-radius:0!important;
    background:transparent!important;
    box-shadow:none!important;
    filter:drop-shadow(0 7px 7px rgba(0,0,0,.22))!important;
    transform:translateY(-1px) scale(1.08)!important;
  }
  .sideBrand>div{min-width:0!important}
  .sideBrand strong{font-size:16px!important;letter-spacing:-.2px!important}
  .sideBrand span{font-size:10px!important;margin-top:4px!important}
}
'''
css.write_text(style, encoding='utf-8')
