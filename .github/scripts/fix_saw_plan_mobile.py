from pathlib import Path
path=Path('index.html')
text=path.read_text(encoding='utf-8')
marker='/* sawPlanResponsiveFixV1 */'
if marker in text: raise SystemExit('already installed')
css='''
/* sawPlanResponsiveFixV1 */
.sawPlan{width:100%;max-width:100%;min-width:0;overflow-y:auto;overflow-x:hidden;padding-right:3px}
.sawGroup{width:100%;max-width:100%;min-width:0;overflow:hidden}
.sawGroupTitle{min-width:0;flex-wrap:wrap}.sawGroupTitle b,.sawGroupTitle span{min-width:0;max-width:100%;overflow-wrap:anywhere}
.stockBar{width:100%;max-width:100%;min-width:0;overflow:hidden}
.stockPieces{width:100%;max-width:100%;min-width:0;gap:1px;overflow:hidden}
.stockPiece{min-width:0;max-width:100%;flex-shrink:1;padding-left:2px;padding-right:2px;text-overflow:ellipsis}
.stockOffcut{max-width:100%}
.stockMeta{min-width:0;max-width:100%;flex-wrap:wrap}.stockMeta span{min-width:0;max-width:100%;overflow-wrap:anywhere}
@media(max-width:560px){.shopCard{overflow:hidden}.sawPlan{padding-right:0;gap:8px}.sawGroup{padding:9px}.stockBar{height:28px;margin-top:5px}.stockPieces{padding:2px;gap:1px}.stockPiece{font-size:0;min-width:0;padding:0}.stockMeta{gap:4px;font-size:9px}.stockMeta span:last-child{margin-left:auto;text-align:right}}
'''
if '\n</style>' not in text: raise SystemExit('style tag not found')
text=text.replace('\n</style>',css+'\n</style>',1)
path.write_text(text,encoding='utf-8')
print('installed')
