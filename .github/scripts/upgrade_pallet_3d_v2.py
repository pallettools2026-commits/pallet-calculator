from pathlib import Path

path = Path('index.html')
text = path.read_text(encoding='utf-8')

if 'dynamicPalletModelV2' in text:
    raise SystemExit('dynamicPalletModelV2 already installed')

text = text.replace('Наглядный пример чистого нового поддона', 'Модель строится по текущим деталям и размерам', 1)

start_marker = '/* dynamicPalletPreviewV1 */'
end_marker = 'document.getElementById("zoomPallet")?.addEventListener("click",()=>{document.getElementById("previewStage")?.classList.toggle("zoomed");});'
start = text.find(start_marker)
if start < 0:
    raise SystemExit('dynamic pallet preview start marker not found')
end = text.find(end_marker, start)
if end < 0:
    raise SystemExit('dynamic pallet preview end marker not found')
end += len(end_marker)

new_js = r'''/* dynamicPalletModelV2 */
let palletPreviewAngle=0;
function pallet3DPart(index){
 const n=Math.max(0,Number(document.getElementById("n"+index)?.value||0));
 const t=Math.max(0,Number(document.getElementById("t"+index)?.value||0));
 const w=Math.max(0,Number(document.getElementById("w"+index)?.value||0));
 const l=Math.max(0,Number(document.getElementById("l"+index)?.value||0));
 return {n:Math.round(n),t,w,l,name:data[index]?.[0]||"Деталь",index};
}
function renderDynamicPallet(lengthMm,widthMm){
 const root=document.getElementById("palletPreview3D");
 if(!root)return;
 const L=Math.max(300,Number(lengthMm)||1200),W=Math.max(300,Number(widthMm)||800),maxD=Math.max(L,W);
 const parts3D=[0,1,2,3,4,5,6].map(pallet3DPart);
 const deck=parts3D[0],cross=[parts3D[1],parts3D[2]],runners=[parts3D[3],parts3D[4]],blocks=[parts3D[5],parts3D[6]];
 const crossPieces=[];cross.forEach(p=>{for(let i=0;i<Math.min(p.n,20);i++)crossPieces.push(p);});
 const runnerPieces=[];runners.forEach(p=>{for(let i=0;i<Math.min(p.n,20);i++)runnerPieces.push(p);});
 const blockPieces=[];blocks.forEach(p=>{for(let i=0;i<Math.min(p.n,30);i++)blockPieces.push(p);});
 const lenPx=Math.max(155,360*(L/maxD)),widPx=Math.max(95,235*(W/maxD)),mirror=palletPreviewAngle%2?-1:1;
 const vx=[mirror*lenPx,mirror*lenPx*.16],vy=[-mirror*widPx*.72,mirror*widPx*.40];
 const add=(a,b)=>[a[0]+b[0],a[1]+b[1]],mul=(a,n)=>[a[0]*n,a[1]*n],pts=a=>a.map(p=>`${p[0].toFixed(1)},${p[1].toFixed(1)}`).join(" ");
 const corners=[[0,0],vx,vy,add(vx,vy)],xs=corners.map(p=>p[0]),ys=corners.map(p=>p[1]);
 const ox=380-(Math.min(...xs)+Math.max(...xs))/2,oy=72-Math.min(...ys),base=[ox,oy];
 const clamp=(v,min,max)=>Math.max(min,Math.min(max,v));
 const hScale=.46;
 const deckH=clamp((deck.t||22)*hScale,6,18),crossH=clamp(Math.max(...cross.map(p=>p.t||0),22)*hScale,6,18),blockH=clamp(Math.max(...blocks.map(p=>p.t||0),75)*hScale,22,48),runnerH=clamp(Math.max(...runners.map(p=>p.t||0),22)*hScale,6,18);
 const crossOffset=deckH+5,blockOffset=crossOffset+crossH+6,runnerOffset=blockOffset+blockH+7;
 const colors={deck:["#f4d6a5","#d9a86c","#c18b50"],cross:["#edc995","#cf985c","#b87d45"],runner:["#e8c18a","#ca9255","#ad733f"],block:["#e2b577","#c58b4d","#a96d3a"]};
 const safeTitle=s=>String(s).replace(/[&<>]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;"}[c]));
 const box=(o,a,b,h,c,kind,title)=>{const A=o,B=add(o,a),C=add(add(o,a),b),D=add(o,b),d=[0,h],A2=add(A,d),B2=add(B,d),C2=add(C,d),D2=add(D,d);return `<g class="palletModelPart palletModel-${kind}"><title>${safeTitle(title)}</title><polygon points="${pts([A,D,C,B])}" fill="${c[0]}" stroke="#9c6b39" stroke-opacity=".25"/><polygon points="${pts([A,B,B2,A2])}" fill="${c[1]}" stroke="#8c5d31" stroke-opacity=".24"/><polygon points="${pts([D,C,C2,D2])}" fill="${c[2]}" stroke="#80532b" stroke-opacity=".22"/></g>`;};
 const distributed=(count,sizeFrac)=>{if(count<=1)return [.5-sizeFrac/2];const usable=Math.max(0,1-sizeFrac);return Array.from({length:count},(_,i)=>usable*i/(count-1));};
 let svg='';
 const center=add(add(base,mul(vx,.5)),mul(vy,.5));
 svg+=`<ellipse cx="${center[0]}" cy="${center[1]+runnerOffset+54}" rx="${Math.max(120,lenPx*.58)}" ry="34" fill="rgba(65,48,28,.09)"/>`;

 // Нижние лыжи — реальные количества и размеры из калькулятора.
 if(runnerPieces.length){
   const avgW=runnerPieces.reduce((s,p)=>s+(p.w||98),0)/runnerPieces.length;
   let wFrac=clamp(avgW/W,.025,.32);if(wFrac*runnerPieces.length>.92)wFrac=.92/runnerPieces.length;
   const pos=distributed(runnerPieces.length,wFrac);
   runnerPieces.forEach((p,i)=>{const lf=clamp((p.l||L)/L,.12,1),start=(1-lf)/2,o=add(add(add(base,mul(vx,start)),mul(vy,pos[i])),[0,runnerOffset]);svg+=box(o,mul(vx,lf),mul(vy,wFrac),clamp((p.t||22)*hScale,6,18),colors.runner,'runner',`${p.name}: ${Math.round(p.t)}×${Math.round(p.w)}×${Math.round(p.l)} мм`);});
 }

 // Шашки.
 if(blockPieces.length){
   const cols=Math.min(3,Math.max(1,blockPieces.length)),rows=Math.ceil(blockPieces.length/cols);
   blockPieces.forEach((p,i)=>{const col=i%cols,row=Math.floor(i/cols),xf=cols===1?.5:(.09+col*(.82/(cols-1))),yf=rows===1?.5:(.09+row*(.82/Math.max(1,rows-1))),lf=clamp((p.l||120)/L,.045,.22),wf=clamp((p.w||100)/W,.045,.22),o=add(add(add(base,mul(vx,clamp(xf-lf/2,0,1-lf))),mul(vy,clamp(yf-wf/2,0,1-wf))),[0,blockOffset]);svg+=box(o,mul(vx,lf),mul(vy,wf),clamp((p.t||75)*hScale,20,48),colors.block,'block',`${p.name}: ${Math.round(p.t)}×${Math.round(p.w)}×${Math.round(p.l)} мм`);});
 }

 // Поперечные доски под верхним настилом.
 if(crossPieces.length){
   const avgW=crossPieces.reduce((s,p)=>s+(p.w||98),0)/crossPieces.length;
   let xFrac=clamp(avgW/L,.025,.28);if(xFrac*crossPieces.length>.88)xFrac=.88/crossPieces.length;
   const pos=distributed(crossPieces.length,xFrac);
   crossPieces.forEach((p,i)=>{const wf=clamp((p.l||W)/W,.15,1),ystart=(1-wf)/2,o=add(add(add(base,mul(vx,pos[i])),mul(vy,ystart)),[0,crossOffset]);svg+=box(o,mul(vx,xFrac),mul(vy,wf),clamp((p.t||22)*hScale,6,18),colors.cross,'cross',`${p.name}: ${Math.round(p.t)}×${Math.round(p.w)}×${Math.round(p.l)} мм`);});
 }

 // Верхний настил.
 if(deck.n>0){
   const count=Math.min(deck.n,24);let wFrac=clamp((deck.w||98)/W,.025,.32);if(wFrac*count>.94)wFrac=.94/count;
   const pos=distributed(count,wFrac),lf=clamp((deck.l||L)/L,.15,1),xstart=(1-lf)/2;
   pos.forEach((y,i)=>{const o=add(add(base,mul(vx,xstart)),mul(vy,y));svg+=box(o,mul(vx,lf),mul(vy,wFrac),clamp((deck.t||22)*hScale,6,18),colors.deck,'deck',`${deck.name} ${i+1}: ${Math.round(deck.t)}×${Math.round(deck.w)}×${Math.round(deck.l)} мм`);});
 }

 const A=base,B=add(base,vx),D=add(base,vy),lenMid=[(A[0]+B[0])/2,(A[1]+B[1])/2-25],widMid=[(A[0]+D[0])/2-20,(A[1]+D[1])/2+20];
 svg+=`<line class="palletDimensionLine" x1="${A[0]}" y1="${A[1]-16}" x2="${B[0]}" y2="${B[1]-16}"/><circle class="palletDimensionDot" cx="${A[0]}" cy="${A[1]-16}" r="3"/><circle class="palletDimensionDot" cx="${B[0]}" cy="${B[1]-16}" r="3"/><text class="palletDimensionLabel" x="${lenMid[0]}" y="${lenMid[1]}" text-anchor="middle">${Math.round(L)} мм</text>`;
 svg+=`<line class="palletDimensionLine" x1="${A[0]-11}" y1="${A[1]}" x2="${D[0]-11}" y2="${D[1]}"/><circle class="palletDimensionDot" cx="${A[0]-11}" cy="${A[1]}" r="3"/><circle class="palletDimensionDot" cx="${D[0]-11}" cy="${D[1]}" r="3"/><text class="palletDimensionLabel" x="${widMid[0]}" y="${widMid[1]}" text-anchor="middle">${Math.round(W)} мм</text>`;
 const deckCount=deck.n,crossCount=cross.reduce((s,p)=>s+p.n,0),runnerCount=runners.reduce((s,p)=>s+p.n,0),blockCount=blocks.reduce((s,p)=>s+p.n,0);
 root.innerHTML=`<svg class="dynamicPalletSvg palletModelSvgV2" viewBox="0 0 760 455" xmlns="http://www.w3.org/2000/svg" aria-label="3D модель поддона ${Math.round(L)} на ${Math.round(W)} миллиметров">${svg}</svg><div class="palletModelLegend" aria-label="Состав 3D модели"><span><i class="deck"></i>Настил <b>${deckCount}</b></span><span><i class="cross"></i>Поперечины <b>${crossCount}</b></span><span><i class="runner"></i>Лыжи <b>${runnerCount}</b></span><span><i class="block"></i>Шашки <b>${blockCount}</b></span></div><div class="palletModelHint">3D строится из текущих размеров деталей · наведите на деталь для её размера</div>`;
 const rotate=document.getElementById("rotatePallet");if(rotate)rotate.innerHTML='↻ &nbsp; Повернуть модель';
}
document.getElementById("rotatePallet")?.addEventListener("click",()=>{palletPreviewAngle=(palletPreviewAngle+1)%2;renderDynamicPallet(Number(document.getElementById("pL")?.value),Number(document.getElementById("pW")?.value));});
document.getElementById("zoomPallet")?.addEventListener("click",()=>{document.getElementById("previewStage")?.classList.toggle("zoomed");});'''

text = text[:start] + new_js + text[end:]

css = r'''
/* dynamicPalletModelV2 */
.dynamicPalletCanvas{flex-direction:column;gap:5px;min-width:0}
.palletModelSvgV2{max-height:390px}
.palletModelPart{cursor:default;transition:filter .15s ease,opacity .15s ease}
.palletModelPart:hover{filter:brightness(1.07) drop-shadow(0 3px 2px rgba(91,61,27,.14))}
.palletModelLegend{display:flex;justify-content:center;gap:7px;flex-wrap:wrap;width:100%;padding:0 6px}
.palletModelLegend span{display:inline-flex;align-items:center;gap:5px;padding:5px 8px;border:1px solid #e0e7e3;border-radius:999px;background:rgba(255,255,255,.9);color:#56665e;font-size:9px;font-weight:750;white-space:nowrap}
.palletModelLegend b{color:#173d31;font-size:10px}.palletModelLegend i{width:8px;height:8px;border-radius:3px;display:inline-block}.palletModelLegend i.deck{background:#e7bd82}.palletModelLegend i.cross{background:#ce965a}.palletModelLegend i.runner{background:#b87c43}.palletModelLegend i.block{background:#c58b4d}
.palletModelHint{text-align:center;color:#829089;font-size:9px;line-height:1.35;padding:0 8px 3px}
@media(max-width:560px){.palletModelSvgV2{max-height:330px}.palletModelLegend{gap:4px}.palletModelLegend span{padding:4px 6px;font-size:8px}.palletModelHint{font-size:8px}.dynamicPalletCanvas{min-height:270px}}
'''
if '\n</style>' not in text:
    raise SystemExit('style closing tag not found')
text = text.replace('\n</style>', css + '\n</style>', 1)

path.write_text(text, encoding='utf-8')
print('dynamicPalletModelV2 installed')
