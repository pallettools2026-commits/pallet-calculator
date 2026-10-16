from pathlib import Path

path = Path('index.html')
text = path.read_text(encoding='utf-8')

if 'pallet3dWorkbenchV3' in text:
    raise SystemExit('pallet3dWorkbenchV3 already installed')

start_marker = '/* dynamicPalletModelV2 */'
end_marker = 'document.getElementById("zoomPallet")?.addEventListener("click",()=>{document.getElementById("previewStage")?.classList.toggle("zoomed");});'
start = text.rfind(start_marker)
if start < 0:
    raise SystemExit('3D JS start marker not found')
end = text.find(end_marker, start)
if end < 0:
    raise SystemExit('3D JS end marker not found')
end += len(end_marker)

new_js = r'''/* pallet3dWorkbenchV3 */
const pallet3DState={angle:0,mode:"3d"};
function pallet3DPart(index){
 const el=id=>document.getElementById(id+index);
 const n=Math.max(0,Number(el("n")?.value||0));
 const t=Math.max(0,Number(el("t")?.value||0));
 const w=Math.max(0,Number(el("w")?.value||0));
 const l=Math.max(0,Number(el("l")?.value||0));
 return {n:Math.round(n),t,w,l,name:data[index]?.[0]||"Деталь",index};
}
function renderDynamicPallet(lengthMm,widthMm){
 const root=document.getElementById("palletPreview3D");if(!root)return;
 const L=Math.max(300,Number(lengthMm)||1200),W=Math.max(300,Number(widthMm)||800),maxD=Math.max(L,W);
 const p=[0,1,2,3,4,5,6].map(pallet3DPart),deck=p[0],cross=[p[1],p[2]],runners=[p[3],p[4]],blocks=[p[5],p[6]];
 const crossPieces=[];cross.forEach(x=>{for(let i=0;i<Math.min(x.n,20);i++)crossPieces.push(x)});
 const runnerPieces=[];runners.forEach(x=>{for(let i=0;i<Math.min(x.n,20);i++)runnerPieces.push(x)});
 const blockPieces=[];blocks.forEach(x=>{for(let i=0;i<Math.min(x.n,30);i++)blockPieces.push(x)});
 const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
 const toolbar=`<div class="pallet3dToolbar" role="tablist" aria-label="Режим просмотра"><button data-p3d-mode="3d" class="${pallet3DState.mode==='3d'?'active':''}">3D</button><button data-p3d-mode="top" class="${pallet3DState.mode==='top'?'active':''}">Сверху</button><button data-p3d-mode="side" class="${pallet3DState.mode==='side'?'active':''}">Сбоку</button><button data-p3d-mode="explode" class="${pallet3DState.mode==='explode'?'active':''}">Разнести</button></div>`;
 let svg='';
 if(pallet3DState.mode==='top'){
   const bw=500,bh=500*(W/L),x0=130,y0=210-bh/2;
   svg+=`<rect x="${x0}" y="${y0}" width="${bw}" height="${bh}" rx="8" fill="#f8f3ea" stroke="#cbb18c" stroke-width="2"/>`;
   crossPieces.forEach((x,i)=>{const ww=clamp((x.w||98)/L*bw,10,80),xx=x0+(crossPieces.length<=1?(bw-ww)/2:i*(bw-ww)/(crossPieces.length-1));svg+=`<rect x="${xx}" y="${y0}" width="${ww}" height="${bh}" rx="4" fill="#d3a268" opacity=".78"/>`});
   const cnt=Math.max(1,Math.min(deck.n,24)),dh=clamp((deck.w||98)/W*bh,8,70);
   for(let i=0;i<cnt;i++){const yy=y0+(cnt<=1?(bh-dh)/2:i*(bh-dh)/(cnt-1));svg+=`<rect x="${x0}" y="${yy}" width="${bw}" height="${dh}" rx="4" fill="#edc995" stroke="#c89559" stroke-width="1"/>`}
   svg+=`<text class="pallet3dViewTitle" x="380" y="52" text-anchor="middle">Вид сверху · ${Math.round(L)} × ${Math.round(W)} мм</text>`;
 }else if(pallet3DState.mode==='side'){
   const x0=110,yBase=330,bw=540,deckH=18,blockH=70,runnerH=16;
   svg+=`<text class="pallet3dViewTitle" x="380" y="52" text-anchor="middle">Вид сбоку · длина ${Math.round(L)} мм</text>`;
   svg+=`<rect x="${x0}" y="${yBase}" width="${bw}" height="${runnerH}" rx="3" fill="#b77b43"/>`;
   const blockCount=Math.max(3,Math.min(blockPieces.length||3,6));for(let i=0;i<blockCount;i++){const bx=x0+30+i*(bw-100)/(blockCount-1);svg+=`<rect x="${bx}" y="${yBase-blockH}" width="70" height="${blockH}" rx="4" fill="#c58b4d"/>`}
   svg+=`<rect x="${x0}" y="${yBase-blockH-24}" width="${bw}" height="18" rx="3" fill="#cf985c"/>`;
   const dc=Math.max(3,Math.min(deck.n,12));for(let i=0;i<dc;i++){const dw=bw/dc-5;svg+=`<rect x="${x0+i*bw/dc}" y="${yBase-blockH-48}" width="${dw}" height="${deckH}" rx="3" fill="#efcc98"/>`}
   svg+=`<line class="palletDimensionLine" x1="${x0}" y1="382" x2="${x0+bw}" y2="382"/><text class="palletDimensionLabel" x="380" y="405" text-anchor="middle">${Math.round(L)} мм</text>`;
 }else{
   const exploded=pallet3DState.mode==='explode';
   const lenPx=Math.max(170,370*(L/maxD)),widPx=Math.max(100,245*(W/maxD)),mirror=pallet3DState.angle%2?-1:1;
   const vx=[mirror*lenPx,mirror*lenPx*.17],vy=[-mirror*widPx*.72,mirror*widPx*.40];
   const add=(a,b)=>[a[0]+b[0],a[1]+b[1]],mul=(a,n)=>[a[0]*n,a[1]*n],pts=a=>a.map(q=>`${q[0].toFixed(1)},${q[1].toFixed(1)}`).join(" ");
   const corners=[[0,0],vx,vy,add(vx,vy)],xs=corners.map(q=>q[0]),ys=corners.map(q=>q[1]);
   const base=[380-(Math.min(...xs)+Math.max(...xs))/2,80-Math.min(...ys)];
   const colors={deck:["#f4d6a5","#d9a86c","#c18b50"],cross:["#edc995","#cf985c","#b87d45"],runner:["#e8c18a","#ca9255","#ad733f"],block:["#e2b577","#c58b4d","#a96d3a"]};
   const box=(o,a,b,h,c,kind,title)=>{const A=o,B=add(o,a),C=add(add(o,a),b),D=add(o,b),d=[0,h],A2=add(A,d),B2=add(B,d),C2=add(C,d),D2=add(D,d);return `<g class="palletModelPart palletModel-${kind}"><title>${String(title).replace(/[&<>]/g,'')}</title><polygon points="${pts([A,D,C,B])}" fill="${c[0]}" stroke="#96673b" stroke-width="1"/><polygon points="${pts([A,B,B2,A2])}" fill="${c[1]}"/><polygon points="${pts([D,C,C2,D2])}" fill="${c[2]}"/></g>`};
   const distributed=(count,size)=>count<=1?[.5-size/2]:Array.from({length:count},(_,i)=>(1-size)*i/(count-1));
   const deckH=clamp((deck.t||22)*.46,7,18),crossH=clamp(Math.max(...cross.map(x=>x.t||0),22)*.46,7,18),blockH=clamp(Math.max(...blocks.map(x=>x.t||0),75)*.46,25,48);
   const crossOffset=exploded?55:deckH+6,blockOffset=exploded?125:deckH+crossH+14,runnerOffset=exploded?205:deckH+crossH+blockH+22;
   const center=add(add(base,mul(vx,.5)),mul(vy,.5));svg+=`<ellipse cx="${center[0]}" cy="${center[1]+runnerOffset+48}" rx="${Math.max(125,lenPx*.6)}" ry="32" fill="rgba(60,43,26,.09)"/>`;
   if(runnerPieces.length){let wf=clamp((runnerPieces.reduce((s,x)=>s+(x.w||98),0)/runnerPieces.length)/W,.03,.28);if(wf*runnerPieces.length>.9)wf=.9/runnerPieces.length;distributed(runnerPieces.length,wf).forEach((y,i)=>{const x=runnerPieces[i],lf=clamp((x.l||L)/L,.15,1),o=add(add(add(base,mul(vx,(1-lf)/2)),mul(vy,y)),[0,runnerOffset]);svg+=box(o,mul(vx,lf),mul(vy,wf),clamp((x.t||22)*.46,7,18),colors.runner,'runner',`${x.name}: ${Math.round(x.t)}×${Math.round(x.w)}×${Math.round(x.l)} мм`)})}
   if(blockPieces.length){const cols=3,rows=Math.ceil(blockPieces.length/cols);blockPieces.forEach((x,i)=>{const col=i%cols,row=Math.floor(i/cols),xf=.08+col*.41,yf=rows<=1?.45:.08+row*(.84/Math.max(1,rows-1)),lf=clamp((x.l||120)/L,.05,.2),wf=clamp((x.w||100)/W,.05,.2),o=add(add(add(base,mul(vx,clamp(xf,0,1-lf))),mul(vy,clamp(yf,0,1-wf))),[0,blockOffset]);svg+=box(o,mul(vx,lf),mul(vy,wf),clamp((x.t||75)*.46,24,48),colors.block,'block',`${x.name}: ${Math.round(x.t)}×${Math.round(x.w)}×${Math.round(x.l)} мм`)})}
   if(crossPieces.length){let xf=clamp((crossPieces.reduce((s,x)=>s+(x.w||98),0)/crossPieces.length)/L,.03,.25);if(xf*crossPieces.length>.9)xf=.9/crossPieces.length;distributed(crossPieces.length,xf).forEach((xpos,i)=>{const x=crossPieces[i],wf=clamp((x.l||W)/W,.2,1),o=add(add(add(base,mul(vx,xpos)),mul(vy,(1-wf)/2)),[0,crossOffset]);svg+=box(o,mul(vx,xf),mul(vy,wf),clamp((x.t||22)*.46,7,18),colors.cross,'cross',`${x.name}: ${Math.round(x.t)}×${Math.round(x.w)}×${Math.round(x.l)} мм`)})}
   if(deck.n>0){const cnt=Math.min(deck.n,24);let wf=clamp((deck.w||98)/W,.03,.3);if(wf*cnt>.94)wf=.94/cnt;distributed(cnt,wf).forEach((y,i)=>{const lf=clamp((deck.l||L)/L,.2,1),o=add(add(base,mul(vx,(1-lf)/2)),mul(vy,y));svg+=box(o,mul(vx,lf),mul(vy,wf),deckH,colors.deck,'deck',`${deck.name} ${i+1}: ${Math.round(deck.t)}×${Math.round(deck.w)}×${Math.round(deck.l)} мм`)})}
   svg+=`<text class="pallet3dViewTitle" x="380" y="35" text-anchor="middle">${exploded?'Разнесённая модель':'3D модель'} · ${Math.round(L)} × ${Math.round(W)} мм</text>`;
 }
 const counts={deck:deck.n,cross:cross.reduce((s,x)=>s+x.n,0),runner:runners.reduce((s,x)=>s+x.n,0),block:blocks.reduce((s,x)=>s+x.n,0)};
 root.innerHTML=`${toolbar}<svg class="dynamicPalletSvg palletModelSvgV3" viewBox="0 0 760 455" xmlns="http://www.w3.org/2000/svg">${svg}</svg><div class="palletModelLegend"><span><i class="deck"></i>Настил <b>${counts.deck}</b></span><span><i class="cross"></i>Поперечины <b>${counts.cross}</b></span><span><i class="runner"></i>Лыжи <b>${counts.runner}</b></span><span><i class="block"></i>Шашки <b>${counts.block}</b></span></div><div class="palletModelHint">Модель обновляется вместе с размерами деталей калькулятора</div>`;
 root.querySelectorAll('[data-p3d-mode]').forEach(btn=>btn.addEventListener('click',()=>{pallet3DState.mode=btn.dataset.p3dMode;renderDynamicPallet(L,W)}));
 const rotate=document.getElementById('rotatePallet');if(rotate)rotate.textContent='↻ Повернуть модель';
}
document.getElementById("rotatePallet")?.addEventListener("click",()=>{pallet3DState.angle=(pallet3DState.angle+1)%2;if(pallet3DState.mode==='top'||pallet3DState.mode==='side')pallet3DState.mode='3d';renderDynamicPallet(Number(document.getElementById("pL")?.value),Number(document.getElementById("pW")?.value));});
document.getElementById("zoomPallet")?.addEventListener("click",()=>{document.getElementById("previewStage")?.classList.toggle("zoomed");});'''

text = text[:start] + new_js + text[end:]

css = r'''
/* pallet3dWorkbenchV3 */
.pallet3dToolbar{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:6px;width:min(560px,96%);margin:8px auto 0;padding:4px;border:1px solid #dbe6e0;border-radius:12px;background:#f4f8f6}
.pallet3dToolbar button{border:0;border-radius:9px;padding:8px 7px;background:transparent;color:#587067;font-size:10px;font-weight:800;cursor:pointer;white-space:nowrap}
.pallet3dToolbar button.active{background:#176b50;color:#fff;box-shadow:0 3px 10px rgba(23,107,80,.18)}
.palletModelSvgV3{width:100%;max-width:720px;max-height:390px;overflow:visible}
.pallet3dViewTitle{fill:#234c3d;font-size:17px;font-weight:800;letter-spacing:.2px}
.previewStage.zoomed .palletModelSvgV3{transform:scale(1.1)}
@media(max-width:560px){.pallet3dToolbar{gap:3px;width:98%;padding:3px}.pallet3dToolbar button{font-size:8px;padding:7px 3px}.palletModelSvgV3{max-height:315px}.pallet3dViewTitle{font-size:14px}}
'''
style_end = text.rfind('</style>')
if style_end < 0:
    raise SystemExit('style closing tag not found')
text = text[:style_end] + css + '\n' + text[style_end:]
path.write_text(text,encoding='utf-8')
print('pallet3dWorkbenchV3 installed')
