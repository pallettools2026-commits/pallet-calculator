from pathlib import Path

path=Path('index.html')
text=path.read_text(encoding='utf-8')
if 'pallet3dGeometryV6' in text:
    raise SystemExit('pallet3dGeometryV6 already installed')

marker='/* pallet3dInteractiveV4 */'
start=text.find(marker)
if start<0:
    raise SystemExit('3D block not found')

old_box='''   const box=(o,a,b,h,c,kind,title)=>{const A=o,B=add(o,a),C=add(add(o,a),b),D=add(o,b),d=[0,h],A2=add(A,d),B2=add(B,d),C2=add(C,d),D2=add(D,d),n1=add(add(A,mul(a,.09)),mul(b,.22)),n2=add(add(A,mul(a,.91)),mul(b,.78)),nails=(kind==='deck'||kind==='cross')?`<circle class="palletNail" cx="${n1[0]}" cy="${n1[1]}" r="1.8"/><circle class="palletNail" cx="${n2[0]}" cy="${n2[1]}" r="1.8"/>`:'';return `<g class="palletModelPart palletModel-${kind}${pallet3DClass(kind)}" filter="url(#wood-part-shadow)"><title>${safe(title)}</title><polygon points="${pts([A,D,C,B])}" fill="${c[0]}" stroke="#8c5b31" stroke-width="1.15"/><polygon points="${pts([A,B,B2,A2])}" fill="${c[1]}" stroke="#7d4d28" stroke-width=".65"/><polygon points="${pts([D,C,C2,D2])}" fill="${c[2]}" stroke="#714421" stroke-width=".65"/><polyline points="${pts([A,D,C,B])}" fill="none" stroke="rgba(255,255,255,.45)" stroke-width=".7"/>${nails}</g>`}'''
new_box='''   /* pallet3dGeometryV6 */\n   const box=(o,a,b,h,c,kind,title)=>{\n     const A=o,B=add(o,a),C=add(add(o,a),b),D=add(o,b),d=[0,h],A2=add(A,d),B2=add(B,d),C2=add(C,d),D2=add(D,d);\n     const n1=add(add(A,mul(a,.10)),mul(b,.22)),n2=add(add(A,mul(a,.90)),mul(b,.22)),n3=add(add(A,mul(a,.10)),mul(b,.78)),n4=add(add(A,mul(a,.90)),mul(b,.78));\n     const nails=(kind==='deck'||kind==='cross')?`<g class="palletNails"><circle class="palletNail" cx="${n1[0]}" cy="${n1[1]}" r="1.7"/><circle class="palletNail" cx="${n2[0]}" cy="${n2[1]}" r="1.7"/><circle class="palletNail" cx="${n3[0]}" cy="${n3[1]}" r="1.7"/><circle class="palletNail" cx="${n4[0]}" cy="${n4[1]}" r="1.7"/></g>`:'';\n     const endFill=kind==='block'?'url(#wood-block)':'url(#wood-end)';\n     return `<g class="palletModelPart palletModel-${kind}${pallet3DClass(kind)}" filter="url(#wood-part-shadow)"><title>${safe(title)}</title>\n       <polygon class="palletFace palletFaceTop" points="${pts([A,D,C,B])}" fill="${c[0]}"/>\n       <polygon class="palletFace palletFaceLongA" points="${pts([A,B,B2,A2])}" fill="${c[1]}"/>\n       <polygon class="palletFace palletFaceLongB" points="${pts([D,C,C2,D2])}" fill="${c[2]}"/>\n       <polygon class="palletFace palletFaceEndA" points="${pts([A,D,D2,A2])}" fill="${endFill}"/>\n       <polygon class="palletFace palletFaceEndB" points="${pts([B,C,C2,B2])}" fill="${endFill}"/>\n       <polyline class="palletBevel palletBevelTop" points="${pts([A,D,C,B,A])}"/>\n       <polyline class="palletEdgeShadow" points="${pts([A2,B2,C2,D2,A2])}"/>${nails}</g>`\n   }'''
if old_box not in text:
    raise SystemExit('box renderer signature not found')
text=text.replace(old_box,new_box,1)

# Add end-grain texture into SVG defs, once.
needle='<linearGradient id="wood-side-light"'
insert='''<pattern id="wood-end" width="30" height="30" patternUnits="userSpaceOnUse"><rect width="30" height="30" fill="#c9965d"/><path d="M3 15 C7 4 23 4 27 15 C23 26 7 26 3 15 Z M8 15 C11 9 19 9 22 15 C19 21 11 21 8 15 Z" fill="none" stroke="#7e4c28" stroke-opacity=".28" stroke-width="1"/><path d="M15 0 V30" stroke="#a46838" stroke-opacity=".16"/></pattern>\n  '''
pos=text.find(needle,start)
if pos<0:
    raise SystemExit('SVG defs marker not found')
text=text[:pos]+insert+text[pos:]

# More generous exploded spacing and a taller viewBox so lower runners are never clipped.
text=text.replace("crossOffset=exploded?62:deckH+6,blockOffset=exploded?138:deckH+crossH+14,runnerOffset=exploded?225:deckH+crossH+blockH+22", "crossOffset=exploded?76:deckH+6,blockOffset=exploded?168:deckH+crossH+14,runnerOffset=exploded?278:deckH+crossH+blockH+22", 1)
text=text.replace('viewBox="0 0 760 455"', 'viewBox="0 0 760 540"', 1)

# Improve block proportions: solid cuboids and a clean 3x3-ish grid.
old_blocks="""if(blockPieces.length){const cols=3,rows=Math.ceil(blockPieces.length/cols);blockPieces.forEach((x,i)=>{const col=i%cols,row=Math.floor(i/cols),xf=.08+col*.41,yf=rows<=1?.45:.08+row*(.84/Math.max(1,rows-1)),lf=clamp((x.l||120)/L,.05,.2),wf=clamp((x.w||100)/W,.05,.2),o=add(add(add(base,mul(vx,clamp(xf,0,1-lf))),mul(vy,clamp(yf,0,1-wf))),[0,blockOffset]);svg+=box(o,mul(vx,lf),mul(vy,wf),clamp((x.t||75)*.46,24,48),colors.block,'block',`${x.name}: ${Math.round(x.t)}×${Math.round(x.w)}×${Math.round(x.l)} мм`)})}"""
new_blocks="""if(blockPieces.length){const cols=Math.min(3,Math.max(1,blockPieces.length)),rows=Math.ceil(blockPieces.length/cols);blockPieces.forEach((x,i)=>{const col=i%cols,row=Math.floor(i/cols),lf=clamp((x.l||120)/L,.075,.19),wf=clamp((x.w||100)/W,.075,.19),xf=cols<=1?.5-lf/2:.06+col*((.88-lf)/(cols-1)),yf=rows<=1?.5-wf/2:.08+row*((.84-wf)/Math.max(1,rows-1)),o=add(add(add(base,mul(vx,clamp(xf,0,1-lf))),mul(vy,clamp(yf,0,1-wf))),[0,blockOffset]);svg+=box(o,mul(vx,lf),mul(vy,wf),clamp((x.t||75)*.54,30,58),colors.block,'block',`${x.name}: ${Math.round(x.t)}×${Math.round(x.w)}×${Math.round(x.l)} мм`)})}"""
if old_blocks in text:
    text=text.replace(old_blocks,new_blocks,1)

css=r'''
/* pallet3dGeometryV6 */
.palletFace{stroke:#86552e;stroke-width:.8;stroke-linejoin:round}
.palletFaceTop{stroke-width:1.05}
.palletFaceEndA,.palletFaceEndB{stroke:#70431f;stroke-width:.75}
.palletBevel{fill:none;stroke:rgba(255,255,255,.55);stroke-width:1.15;stroke-linejoin:round;pointer-events:none}
.palletEdgeShadow{fill:none;stroke:rgba(74,43,21,.32);stroke-width:.9;pointer-events:none}
.palletModel-block .palletFace{stroke-width:1}
.palletModel-block .palletBevel{stroke:rgba(255,255,255,.38)}
.palletLegendInteractive{display:flex!important;flex-wrap:wrap!important;justify-content:center!important;align-items:center!important;gap:8px!important;width:min(680px,96%)!important;margin:8px auto 0!important;position:relative!important;z-index:4}
.palletLegendInteractive .palletPartChip{flex:0 1 auto!important;min-width:132px;justify-content:center;white-space:nowrap}
.pallet3dDragSurface{overflow:visible!important;padding-bottom:4px}
.palletModelSvgV4{max-height:455px!important;overflow:visible!important}
@media(max-width:700px){.palletLegendInteractive .palletPartChip{min-width:calc(50% - 8px)}.palletModelSvgV4{max-height:390px!important}}
@media(max-width:440px){.palletLegendInteractive{gap:6px!important}.palletLegendInteractive .palletPartChip{min-width:calc(50% - 6px);font-size:9px;padding:7px 8px}.palletModelSvgV4{max-height:350px!important}}
'''
style_end=text.rfind('</style>')
if style_end<0:
    raise SystemExit('style end not found')
text=text[:style_end]+css+'\n'+text[style_end:]

path.write_text(text,encoding='utf-8')
print('pallet3dGeometryV6 installed')
