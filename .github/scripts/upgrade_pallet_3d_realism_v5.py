from pathlib import Path

path=Path('index.html')
text=path.read_text(encoding='utf-8')
marker='/* pallet3dInteractiveV4 */'
if marker not in text:
    raise SystemExit('pallet3dInteractiveV4 not found')
if 'pallet3dRealismV5' in text:
    raise SystemExit('pallet3dRealismV5 already installed')

start=text.index(marker)

needle=" const toolbar=`<div class=\"pallet3dToolbar\" role=\"tablist\" aria-label=\"Режим просмотра\"><button type=\"button\" data-p3d-mode=\"3d\" class=\"${pallet3DState.mode==='3d'?'active':''}\">3D</button><button type=\"button\" data-p3d-mode=\"top\" class=\"${pallet3DState.mode==='top'?'active':''}\">Сверху</button><button type=\"button\" data-p3d-mode=\"side\" class=\"${pallet3DState.mode==='side'?'active':''}\">Сбоку</button><button type=\"button\" data-p3d-mode=\"explode\" class=\"${pallet3DState.mode==='explode'?'active':''}\">Разнести</button></div>`;\n let svg='';"
if needle not in text[start:]:
    raise SystemExit('toolbar/svg marker not found')
wood_defs=""" const toolbar=`<div class=\"pallet3dToolbar\" role=\"tablist\" aria-label=\"Режим просмотра\"><button type=\"button\" data-p3d-mode=\"3d\" class=\"${pallet3DState.mode==='3d'?'active':''}\">3D</button><button type=\"button\" data-p3d-mode=\"top\" class=\"${pallet3DState.mode==='top'?'active':''}\">Сверху</button><button type=\"button\" data-p3d-mode=\"side\" class=\"${pallet3DState.mode==='side'?'active':''}\">Сбоку</button><button type=\"button\" data-p3d-mode=\"explode\" class=\"${pallet3DState.mode==='explode'?'active':''}\">Разнести</button></div>`;
 let svg='';
 const woodDefs=`<defs>
  <pattern id=\"wood-deck\" width=\"96\" height=\"28\" patternUnits=\"userSpaceOnUse\"><rect width=\"96\" height=\"28\" fill=\"#edc994\"/><path d=\"M0 6 C20 1 42 12 96 5 M0 15 C28 10 57 22 96 14 M0 24 C30 18 66 30 96 22\" fill=\"none\" stroke=\"#b98149\" stroke-opacity=\".24\" stroke-width=\"1.2\"/><ellipse cx=\"69\" cy=\"12\" rx=\"5\" ry=\"2.2\" fill=\"none\" stroke=\"#9d6738\" stroke-opacity=\".28\"/></pattern>
  <pattern id=\"wood-cross\" width=\"90\" height=\"26\" patternUnits=\"userSpaceOnUse\"><rect width=\"90\" height=\"26\" fill=\"#ddb47d\"/><path d=\"M0 5 C22 0 45 10 90 4 M0 14 C20 9 58 20 90 13 M0 23 C32 17 63 29 90 21\" fill=\"none\" stroke=\"#a96e3c\" stroke-opacity=\".27\" stroke-width=\"1.1\"/><ellipse cx=\"33\" cy=\"16\" rx=\"4.5\" ry=\"2\" fill=\"none\" stroke=\"#8f592e\" stroke-opacity=\".25\"/></pattern>
  <pattern id=\"wood-runner\" width=\"92\" height=\"25\" patternUnits=\"userSpaceOnUse\"><rect width=\"92\" height=\"25\" fill=\"#d2a36a\"/><path d=\"M0 6 C18 2 52 12 92 5 M0 15 C27 10 57 20 92 14 M0 23 C30 18 61 28 92 21\" fill=\"none\" stroke=\"#8f592f\" stroke-opacity=\".3\" stroke-width=\"1.1\"/></pattern>
  <pattern id=\"wood-block\" width=\"52\" height=\"30\" patternUnits=\"userSpaceOnUse\"><rect width=\"52\" height=\"30\" fill=\"#c9975c\"/><path d=\"M0 7 C14 3 31 12 52 6 M0 18 C17 12 35 24 52 17 M0 27 C16 22 34 31 52 25\" fill=\"none\" stroke=\"#845029\" stroke-opacity=\".28\" stroke-width=\"1\"/><ellipse cx=\"29\" cy=\"13\" rx=\"4\" ry=\"2.1\" fill=\"none\" stroke=\"#70431f\" stroke-opacity=\".28\"/></pattern>
  <linearGradient id=\"wood-side-light\" x1=\"0\" y1=\"0\" x2=\"0\" y2=\"1\"><stop offset=\"0\" stop-color=\"#d5a466\"/><stop offset=\"1\" stop-color=\"#a96d39\"/></linearGradient>
  <linearGradient id=\"wood-side-dark\" x1=\"0\" y1=\"0\" x2=\"1\" y2=\"1\"><stop offset=\"0\" stop-color=\"#bd8248\"/><stop offset=\"1\" stop-color=\"#855126\"/></linearGradient>
  <filter id=\"wood-part-shadow\" x=\"-20%\" y=\"-20%\" width=\"140%\" height=\"150%\"><feDropShadow dx=\"0\" dy=\"2.5\" stdDeviation=\"2.2\" flood-color=\"#4b321d\" flood-opacity=\".18\"/></filter>
 </defs>`;
 svg+=woodDefs;"""
text=text.replace(needle,wood_defs,1)

# Make orthographic modes use wood textures too.
repls={
 'fill=\"#d3a268\" opacity=\".82\"':'fill=\"url(#wood-cross)\" opacity=\".92\"',
 'fill=\"#efcd9a\" stroke=\"#ca975c\"':'fill=\"url(#wood-deck)\" stroke=\"#b47b43\"',
 'fill=\"#b77b43\"':'fill=\"url(#wood-runner)\"',
 'fill=\"#c58b4d\"':'fill=\"url(#wood-block)\"',
 'fill=\"#cf985c\"':'fill=\"url(#wood-cross)\"',
 'fill=\"#efcc98\"':'fill=\"url(#wood-deck)\"'
}
for a,b in repls.items():
    text=text.replace(a,b)

seg_start=text.index('   const colors=', start)
seg_end=text.index(',distributed=(count,size)=>', seg_start)
old=text[seg_start:seg_end]
new=r'''   const colors={deck:["url(#wood-deck)","url(#wood-side-light)","url(#wood-side-dark)"],cross:["url(#wood-cross)","url(#wood-side-light)","url(#wood-side-dark)"],runner:["url(#wood-runner)","url(#wood-side-light)","url(#wood-side-dark)"],block:["url(#wood-block)","url(#wood-side-light)","url(#wood-side-dark)"]},safe=s=>String(s).replace(/[&<>]/g,'');
   const box=(o,a,b,h,c,kind,title)=>{const A=o,B=add(o,a),C=add(add(o,a),b),D=add(o,b),d=[0,h],A2=add(A,d),B2=add(B,d),C2=add(C,d),D2=add(D,d),n1=add(add(A,mul(a,.09)),mul(b,.22)),n2=add(add(A,mul(a,.91)),mul(b,.78)),nails=(kind==='deck'||kind==='cross')?`<circle class="palletNail" cx="${n1[0]}" cy="${n1[1]}" r="1.8"/><circle class="palletNail" cx="${n2[0]}" cy="${n2[1]}" r="1.8"/>`:'';return `<g class="palletModelPart palletModel-${kind}${pallet3DClass(kind)}" filter="url(#wood-part-shadow)"><title>${safe(title)}</title><polygon points="${pts([A,D,C,B])}" fill="${c[0]}" stroke="#8c5b31" stroke-width="1.15"/><polygon points="${pts([A,B,B2,A2])}" fill="${c[1]}" stroke="#7d4d28" stroke-width=".65"/><polygon points="${pts([D,C,C2,D2])}" fill="${c[2]}" stroke="#714421" stroke-width=".65"/><polyline points="${pts([A,D,C,B])}" fill="none" stroke="rgba(255,255,255,.45)" stroke-width=".7"/>${nails}</g>`}'''
text=text[:seg_start]+new+text[seg_end:]

css=r'''
/* pallet3dRealismV5 */
.dynamicPalletStage{background:radial-gradient(circle at 50% 34%,#ffffff 0,#f7f5f0 48%,#eceae4 100%)}
.pallet3dDragSurface{position:relative;border-radius:16px;background:linear-gradient(180deg,rgba(255,255,255,.86),rgba(244,241,234,.55));box-shadow:inset 0 0 0 1px rgba(119,99,70,.08)}
.palletModelSvgV4{filter:drop-shadow(0 14px 18px rgba(72,48,27,.12))}
.palletNail{fill:#62574e;stroke:#2f2b27;stroke-width:.55;opacity:.8;pointer-events:none}
.palletModelPart{transition:opacity .18s ease,filter .18s ease}
.palletModelPart.isSelected{filter:brightness(1.06) saturate(1.08) drop-shadow(0 0 5px rgba(23,107,80,.34))}
.palletModelPart.isDimmed{opacity:.16!important;filter:grayscale(.25)}
.palletModelPart:hover:not(.isDimmed){filter:brightness(1.055) saturate(1.04)}
@media(max-width:560px){.pallet3dDragSurface{border-radius:12px}.palletNail{r:1.5}}
'''
style_end=text.rfind('</style>')
if style_end<0:
    raise SystemExit('style end not found')
text=text[:style_end]+css+'\n'+text[style_end:]

path.write_text(text,encoding='utf-8')
print('pallet3dRealismV5 installed')
