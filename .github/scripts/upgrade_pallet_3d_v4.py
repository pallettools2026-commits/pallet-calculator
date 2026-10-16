from pathlib import Path

path = Path('index.html')
text = path.read_text(encoding='utf-8')

if 'pallet3dInteractiveV4' in text:
    raise SystemExit('pallet3dInteractiveV4 already installed')

start_marker = '/* pallet3dWorkbenchV3 */'
end_marker = 'document.getElementById("zoomPallet")?.addEventListener("click",()=>{document.getElementById("previewStage")?.classList.toggle("zoomed");});'
start = text.rfind(start_marker)
if start < 0:
    raise SystemExit('V3 3D marker not found')
end = text.find(end_marker, start)
if end < 0:
    raise SystemExit('V3 3D end marker not found')
end += len(end_marker)

new_js = r'''/* pallet3dInteractiveV4 */
const pallet3DState={angle:-28,mode:"3d",selected:"all",dragging:false,startX:0,startAngle:-28,pointerId:null};
function pallet3DPart(index){
 const el=id=>document.getElementById(id+index);
 return {n:Math.max(0,Math.round(Number(el("n")?.value||0))),t:Math.max(0,Number(el("t")?.value||0)),w:Math.max(0,Number(el("w")?.value||0)),l:Math.max(0,Number(el("l")?.value||0)),name:data[index]?.[0]||"Деталь",index};
}
function pallet3DClass(kind){if(pallet3DState.selected==="all")return "";return pallet3DState.selected===kind?" isSelected":" isDimmed";}
function renderDynamicPallet(lengthMm,widthMm){
 const root=document.getElementById("palletPreview3D");if(!root)return;
 const L=Math.max(300,Number(lengthMm)||1200),W=Math.max(300,Number(widthMm)||800),maxD=Math.max(L,W);
 const p=[0,1,2,3,4,5,6].map(pallet3DPart),deck=p[0],cross=[p[1],p[2]],runners=[p[3],p[4]],blocks=[p[5],p[6]];
 const crossPieces=[];cross.forEach(x=>{for(let i=0;i<Math.min(x.n,20);i++)crossPieces.push(x)});const runnerPieces=[];runners.forEach(x=>{for(let i=0;i<Math.min(x.n,20);i++)runnerPieces.push(x)});const blockPieces=[];blocks.forEach(x=>{for(let i=0;i<Math.min(x.n,30);i++)blockPieces.push(x)});
 const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
 const toolbar=`<div class="pallet3dToolbar" role="tablist" aria-label="Режим просмотра"><button type="button" data-p3d-mode="3d" class="${pallet3DState.mode==='3d'?'active':''}">3D</button><button type="button" data-p3d-mode="top" class="${pallet3DState.mode==='top'?'active':''}">Сверху</button><button type="button" data-p3d-mode="side" class="${pallet3DState.mode==='side'?'active':''}">Сбоку</button><button type="button" data-p3d-mode="explode" class="${pallet3DState.mode==='explode'?'active':''}">Разнести</button></div>`;
 let svg='';
 if(pallet3DState.mode==='top'){
   const bw=500,bh=Math.min(330,500*(W/L)),x0=130,y0=225-bh/2;svg+=`<rect x="${x0}" y="${y0}" width="${bw}" height="${bh}" rx="8" fill="#faf7f1" stroke="#d7c19f" stroke-width="2"/>`;
   crossPieces.forEach((x,i)=>{const ww=clamp((x.w||98)/L*bw,10,75),xx=x0+(crossPieces.length<=1?(bw-ww)/2:i*(bw-ww)/(crossPieces.length-1));svg+=`<rect class="palletModelPart palletModel-cross${pallet3DClass('cross')}" x="${xx}" y="${y0}" width="${ww}" height="${bh}" rx="4" fill="#d3a268" opacity=".82"/>`});
   const cnt=Math.max(1,Math.min(deck.n,24)),dh=clamp((deck.w||98)/W*bh,8,65);for(let i=0;i<cnt;i++){const yy=y0+(cnt<=1?(bh-dh)/2:i*(bh-dh)/(cnt-1));svg+=`<rect class="palletModelPart palletModel-deck${pallet3DClass('deck')}" x="${x0}" y="${yy}" width="${bw}" height="${dh}" rx="4" fill="#efcd9a" stroke="#ca975c" stroke-width="1"/>`}svg+=`<text class="pallet3dViewTitle" x="380" y="48" text-anchor="middle">Вид сверху · ${Math.round(L)} × ${Math.round(W)} мм</text>`;
 }else if(pallet3DState.mode==='side'){
   const x0=110,yBase=330,bw=540,deckH=18,blockH=70,runnerH=16;svg+=`<text class="pallet3dViewTitle" x="380" y="48" text-anchor="middle">Вид сбоку · длина ${Math.round(L)} мм</text>`;svg+=`<rect class="palletModelPart palletModel-runner${pallet3DClass('runner')}" x="${x0}" y="${yBase}" width="${bw}" height="${runnerH}" rx="3" fill="#b77b43"/>`;
   const blockCount=Math.max(3,Math.min(blockPieces.length||3,6));for(let i=0;i<blockCount;i++){const bx=x0+30+i*(bw-100)/(blockCount-1);svg+=`<rect class="palletModelPart palletModel-block${pallet3DClass('block')}" x="${bx}" y="${yBase-blockH}" width="70" height="${blockH}" rx="4" fill="#c58b4d"/>`}svg+=`<rect class="palletModelPart palletModel-cross${pallet3DClass('cross')}" x="${x0}" y="${yBase-blockH-24}" width="${bw}" height="18" rx="3" fill="#cf985c"/>`;const dc=Math.max(3,Math.min(deck.n,12));for(let i=0;i<dc;i++){const dw=bw/dc-5;svg+=`<rect class="palletModelPart palletModel-deck${pallet3DClass('deck')}" x="${x0+i*bw/dc}" y="${yBase-blockH-48}" width="${dw}" height="${deckH}" rx="3" fill="#efcc98"/>`}svg+=`<line class="palletDimensionLine" x1="${x0}" y1="382" x2="${x0+bw}" y2="382"/><text class="palletDimensionLabel" x="380" y="405" text-anchor="middle">${Math.round(L)} мм</text>`;
 }else{
   const exploded=pallet3DState.mode==='explode',angle=pallet3DState.angle*Math.PI/180,lenPx=Math.max(180,370*(L/maxD)),widPx=Math.max(110,260*(W/maxD)),vx=[Math.cos(angle)*lenPx,Math.sin(angle)*lenPx*.46],vy=[-Math.sin(angle)*widPx,Math.cos(angle)*widPx*.46];
   const add=(a,b)=>[a[0]+b[0],a[1]+b[1]],mul=(a,n)=>[a[0]*n,a[1]*n],pts=a=>a.map(q=>`${q[0].toFixed(1)},${q[1].toFixed(1)}`).join(" "),corners=[[0,0],vx,vy,add(vx,vy)],xs=corners.map(q=>q[0]),ys=corners.map(q=>q[1]),base=[380-(Math.min(...xs)+Math.max(...xs))/2,92-Math.min(...ys)];
   const colors={deck:["#f4d6a5","#d9a86c","#c18b50"],cross:["#edc995","#cf985c","#b87d45"],runner:["#e8c18a","#ca9255","#ad733f"],block:["#e2b577","#c58b4d","#a96d3a"]},safe=s=>String(s).replace(/[&<>]/g,'');
   const box=(o,a,b,h,c,kind,title)=>{const A=o,B=add(o,a),C=add(add(o,a),b),D=add(o,b),d=[0,h],A2=add(A,d),B2=add(B,d),C2=add(C,d),D2=add(D,d);return `<g class="palletModelPart palletModel-${kind}${pallet3DClass(kind)}"><title>${safe(title)}</title><polygon points="${pts([A,D,C,B])}" fill="${c[0]}" stroke="#96673b" stroke-width="1"/><polygon points="${pts([A,B,B2,A2])}" fill="${c[1]}"/><polygon points="${pts([D,C,C2,D2])}" fill="${c[2]}"/></g>`},distributed=(count,size)=>count<=1?[.5-size/2]:Array.from({length:count},(_,i)=>(1-size)*i/(count-1));
   const deckH=clamp((deck.t||22)*.46,7,18),crossH=clamp(Math.max(...cross.map(x=>x.t||0),22)*.46,7,18),blockH=clamp(Math.max(...blocks.map(x=>x.t||0),75)*.46,25,48),crossOffset=exploded?62:deckH+6,blockOffset=exploded?138:deckH+crossH+14,runnerOffset=exploded?225:deckH+crossH+blockH+22,center=add(add(base,mul(vx,.5)),mul(vy,.5));svg+=`<ellipse cx="${center[0]}" cy="${center[1]+runnerOffset+48}" rx="${Math.max(125,lenPx*.58)}" ry="31" fill="rgba(60,43,26,.08)"/>`;
   if(runnerPieces.length){let wf=clamp((runnerPieces.reduce((s,x)=>s+(x.w||98),0)/runnerPieces.length)/W,.03,.28);if(wf*runnerPieces.length>.9)wf=.9/runnerPieces.length;distributed(runnerPieces.length,wf).forEach((y,i)=>{const x=runnerPieces[i],lf=clamp((x.l||L)/L,.15,1),o=add(add(add(base,mul(vx,(1-lf)/2)),mul(vy,y)),[0,runnerOffset]);svg+=box(o,mul(vx,lf),mul(vy,wf),clamp((x.t||22)*.46,7,18),colors.runner,'runner',`${x.name}: ${Math.round(x.t)}×${Math.round(x.w)}×${Math.round(x.l)} мм`)})}
   if(blockPieces.length){const cols=3,rows=Math.ceil(blockPieces.length/cols);blockPieces.forEach((x,i)=>{const col=i%cols,row=Math.floor(i/cols),xf=.08+col*.41,yf=rows<=1?.45:.08+row*(.84/Math.max(1,rows-1)),lf=clamp((x.l||120)/L,.05,.2),wf=clamp((x.w||100)/W,.05,.2),o=add(add(add(base,mul(vx,clamp(xf,0,1-lf))),mul(vy,clamp(yf,0,1-wf))),[0,blockOffset]);svg+=box(o,mul(vx,lf),mul(vy,wf),clamp((x.t||75)*.46,24,48),colors.block,'block',`${x.name}: ${Math.round(x.t)}×${Math.round(x.w)}×${Math.round(x.l)} мм`)})}
   if(crossPieces.length){let xf=clamp((crossPieces.reduce((s,x)=>s+(x.w||98),0)/crossPieces.length)/L,.03,.25);if(xf*crossPieces.length>.9)xf=.9/crossPieces.length;distributed(crossPieces.length,xf).forEach((xpos,i)=>{const x=crossPieces[i],wf=clamp((x.l||W)/W,.2,1),o=add(add(add(base,mul(vx,xpos)),mul(vy,(1-wf)/2)),[0,crossOffset]);svg+=box(o,mul(vx,xf),mul(vy,wf),clamp((x.t||22)*.46,7,18),colors.cross,'cross',`${x.name}: ${Math.round(x.t)}×${Math.round(x.w)}×${Math.round(x.l)} мм`)})}
   if(deck.n>0){const cnt=Math.min(deck.n,24);let wf=clamp((deck.w||98)/W,.03,.3);if(wf*cnt>.94)wf=.94/cnt;distributed(cnt,wf).forEach((y,i)=>{const lf=clamp((deck.l||L)/L,.2,1),o=add(add(base,mul(vx,(1-lf)/2)),mul(vy,y));svg+=box(o,mul(vx,lf),mul(vy,wf),deckH,colors.deck,'deck',`${deck.name} ${i+1}: ${Math.round(deck.t)}×${Math.round(deck.w)}×${Math.round(deck.l)} мм`)})}svg+=`<text class="pallet3dViewTitle" x="380" y="34" text-anchor="middle">${exploded?'Разнесённая модель':'3D модель'} · ${Math.round(L)} × ${Math.round(W)} мм</text>`;
 }
 const counts={deck:deck.n,cross:cross.reduce((s,x)=>s+x.n,0),runner:runners.reduce((s,x)=>s+x.n,0),block:blocks.reduce((s,x)=>s+x.n,0)},chip=(kind,label,count,cls)=>`<button type="button" data-p3d-part="${kind}" class="palletPartChip ${pallet3DState.selected===kind?'active':''}"><i class="${cls}"></i>${label} <b>${count}</b></button>`,dragHint=(pallet3DState.mode==='3d'||pallet3DState.mode==='explode')?'Проведите пальцем или мышкой по модели, чтобы вращать на 360°':'Нажмите на группу деталей, чтобы подсветить её';
 root.innerHTML=`${toolbar}<div class="pallet3dDragSurface"><svg class="dynamicPalletSvg palletModelSvgV4" viewBox="0 0 760 455" xmlns="http://www.w3.org/2000/svg">${svg}</svg></div><div class="palletModelLegend palletLegendInteractive">${chip('deck','Настил',counts.deck,'deck')}${chip('cross','Поперечины',counts.cross,'cross')}${chip('runner','Лыжи',counts.runner,'runner')}${chip('block','Шашки',counts.block,'block')}</div><div class="palletModelHint">${dragHint}</div>`;
 root.querySelectorAll('[data-p3d-mode]').forEach(btn=>btn.addEventListener('click',()=>{pallet3DState.mode=btn.dataset.p3dMode;renderDynamicPallet(L,W)}));root.querySelectorAll('[data-p3d-part]').forEach(btn=>btn.addEventListener('click',()=>{const kind=btn.dataset.p3dPart;pallet3DState.selected=pallet3DState.selected===kind?'all':kind;renderDynamicPallet(L,W)}));const rotate=document.getElementById('rotatePallet');if(rotate)rotate.textContent='↻ Повернуть на 45°';
}
function rerenderPallet3D(){renderDynamicPallet(Number(document.getElementById("pL")?.value),Number(document.getElementById("pW")?.value));}
document.getElementById("rotatePallet")?.addEventListener("click",()=>{if(pallet3DState.mode==='top'||pallet3DState.mode==='side')pallet3DState.mode='3d';pallet3DState.angle=(pallet3DState.angle+45)%360;rerenderPallet3D();});
document.getElementById("zoomPallet")?.addEventListener("click",()=>{document.getElementById("previewStage")?.classList.toggle("zoomed");});
const pallet3DStage=document.getElementById('previewStage');if(pallet3DStage){pallet3DStage.addEventListener('pointerdown',e=>{if(!(pallet3DState.mode==='3d'||pallet3DState.mode==='explode')||e.target.closest('button'))return;pallet3DState.dragging=true;pallet3DState.startX=e.clientX;pallet3DState.startAngle=pallet3DState.angle;pallet3DState.pointerId=e.pointerId;pallet3DStage.classList.add('isDragging');try{pallet3DStage.setPointerCapture(e.pointerId)}catch(_e){}});pallet3DStage.addEventListener('pointermove',e=>{if(!pallet3DState.dragging||e.pointerId!==pallet3DState.pointerId)return;pallet3DState.angle=(pallet3DState.startAngle+(e.clientX-pallet3DState.startX)*.65)%360;rerenderPallet3D();e.preventDefault()},{passive:false});const endDrag=e=>{if(!pallet3DState.dragging)return;pallet3DState.dragging=false;pallet3DStage.classList.remove('isDragging');try{pallet3DStage.releasePointerCapture(e.pointerId)}catch(_e){}};pallet3DStage.addEventListener('pointerup',endDrag);pallet3DStage.addEventListener('pointercancel',endDrag);}
'''
text = text[:start] + new_js + text[end:]
css = r'''
/* pallet3dInteractiveV4 */
.pallet3dDragSurface{width:100%;display:flex;justify-content:center;touch-action:none;cursor:grab;user-select:none;-webkit-user-select:none}.previewStage.isDragging .pallet3dDragSurface{cursor:grabbing}.palletModelSvgV4{width:100%;max-width:720px;max-height:390px;overflow:visible;transition:filter .15s ease}.palletModelPart{transition:opacity .18s ease,filter .18s ease}.palletModelPart.isDimmed{opacity:.13;filter:saturate(.35)}.palletModelPart.isSelected{opacity:1;filter:brightness(1.09) drop-shadow(0 4px 3px rgba(96,61,25,.18))}.palletLegendInteractive{gap:7px}.palletPartChip{appearance:none;border:1px solid #d9e2dd;border-radius:999px;background:#fff;color:#58675f;padding:7px 10px;display:inline-flex;align-items:center;gap:6px;font:inherit;font-size:10px;font-weight:750;cursor:pointer;box-shadow:0 1px 3px rgba(22,55,43,.04)}.palletPartChip b{font-size:12px;color:#173d31}.palletPartChip i{width:10px;height:10px;border-radius:3px;display:inline-block}.palletPartChip i.deck{background:#e7bd82}.palletPartChip i.cross{background:#ce965a}.palletPartChip i.runner{background:#b87c43}.palletPartChip i.block{background:#c58b4d}.palletPartChip.active{border-color:#1b7b5e;background:#eaf6f1;color:#176b50;box-shadow:0 0 0 2px rgba(27,123,94,.08)}.previewStage.zoomed .palletModelSvgV4{transform:scale(1.1)}@media(max-width:560px){.palletModelSvgV4{max-height:315px}.palletPartChip{padding:6px 8px;font-size:9px;gap:5px}.palletPartChip b{font-size:11px}.pallet3dDragSurface{min-height:250px;align-items:center}}
'''
style_end=text.rfind('</style>')
if style_end<0:raise SystemExit('style closing tag not found')
text=text[:style_end]+css+'\n'+text[style_end:]
path.write_text(text,encoding='utf-8')
print('pallet3dInteractiveV4 installed')
