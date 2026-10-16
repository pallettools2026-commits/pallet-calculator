from pathlib import Path

path = Path('index.html')
text = path.read_text(encoding='utf-8')

if 'dynamicPalletPreviewV1' in text:
    raise SystemExit('dynamic pallet preview already installed')

old_stage = '<div class="previewStage" id="previewStage"><img id="previewPallet" src="assets/pallet-clean-3d-2.webp" alt="3D вид деревянного поддона"></div>'
new_stage = '<div class="previewStage dynamicPalletStage" id="previewStage"><div id="palletPreview3D" class="dynamicPalletCanvas" role="img" aria-label="3D модель поддона по выбранным размерам"></div></div>'
if old_stage not in text:
    raise SystemExit('preview stage marker not found')
text = text.replace(old_stage, new_stage, 1)

css = r'''

/* dynamicPalletPreviewV1 */
.dynamicPalletStage{position:relative;overflow:hidden;background:radial-gradient(circle at 50% 38%,#ffffff 0,#fafbf9 50%,#f1f4f2 100%)}
.dynamicPalletCanvas{width:100%;height:100%;min-height:260px;display:flex;align-items:center;justify-content:center;padding:10px;transition:transform .25s ease;transform-origin:center}
.dynamicPalletSvg{display:block;width:100%;height:auto;max-width:650px;filter:drop-shadow(0 18px 18px rgba(71,57,34,.12));transition:transform .25s ease}
.dynamicPalletStage.zoomed .dynamicPalletCanvas{transform:scale(1.16)}
.palletDimensionLabel{font:800 14px Inter,ui-sans-serif,system-ui,sans-serif;fill:#1d624d;paint-order:stroke;stroke:#fff;stroke-width:4px;stroke-linejoin:round}
.palletDimensionLine{stroke:#4d8d79;stroke-width:1.5;stroke-dasharray:4 4;opacity:.75}
.palletDimensionDot{fill:#2d775f}
@media(max-width:560px){.dynamicPalletCanvas{min-height:230px;padding:4px}.palletDimensionLabel{font-size:13px}}
'''
if '</style>' not in text:
    raise SystemExit('style closing marker not found')
text = text.replace('\n</style>', css + '\n</style>', 1)

old_calc = 'const previewSize=document.getElementById("previewSize");if(previewSize)previewSize.textContent=(pl&&pw)?`${pl} × ${pw} мм`:"Размер не задан";'
new_calc = old_calc + '\n renderDynamicPallet(pl,pw);'
if old_calc not in text:
    raise SystemExit('calc preview marker not found')
text = text.replace(old_calc, new_calc, 1)

old_handlers = '''const previewImages=["assets/pallet-clean-3d-2.webp","assets/pallet-clean-3d-1.webp"];
let previewIndex=0;
document.getElementById("rotatePallet")?.addEventListener("click",()=>{previewIndex=(previewIndex+1)%previewImages.length;const img=document.getElementById("previewPallet");if(img)img.src=previewImages[previewIndex];});
document.getElementById("zoomPallet")?.addEventListener("click",()=>{document.getElementById("previewStage")?.classList.toggle("zoomed");});'''

new_handlers = r'''/* dynamicPalletPreviewV1 */
let palletPreviewAngle=0;
function renderDynamicPallet(lengthMm,widthMm){
 const root=document.getElementById("palletPreview3D");
 if(!root)return;
 const L=Math.max(300,Number(lengthMm)||1200),W=Math.max(300,Number(widthMm)||800),maxD=Math.max(L,W);
 const lenPx=235+95*(L/maxD),widPx=115+105*(W/maxD),mirror=palletPreviewAngle%2?-1:1;
 const vx=[mirror*lenPx,mirror*lenPx*.15],vy=[-mirror*widPx*.72,mirror*widPx*.40];
 const ox=350-(vx[0]+vy[0])/2,oy=70-Math.min(0,vx[1],vy[1],vx[1]+vy[1]);
 const V=(x,y)=>[x,y],add=(a,b)=>[a[0]+b[0],a[1]+b[1]],mul=(a,n)=>[a[0]*n,a[1]*n],pts=a=>a.map(p=>`${p[0].toFixed(1)},${p[1].toFixed(1)}`).join(" ");
 const box=(o,a,b,h,c)=>{const A=o,B=add(o,a),C=add(add(o,a),b),D=add(o,b),d=V(0,h),A2=add(A,d),B2=add(B,d),C2=add(C,d),D2=add(D,d);return `<polygon points="${pts([A,D,C,B])}" fill="${c[0]}" stroke="#b78b55" stroke-opacity=".22"/><polygon points="${pts([A,B,B2,A2])}" fill="${c[1]}" stroke="#a87742" stroke-opacity=".2"/><polygon points="${pts([D,C,C2,D2])}" fill="${c[2]}" stroke="#996b3d" stroke-opacity=".2"/>`;};
 const top=["#f3d5a5","#d8a66c","#c38d51"],mid=["#eac795","#ce985d","#b77d45"],block=["#e3b778","#c78d50","#ad713d"],bottom=["#e8c28b","#ca9255","#ad733f"];
 let s='';
 const center=add(add([ox,oy],mul(vx,.5)),mul(vy,.5));
 s+=`<ellipse cx="${center[0]}" cy="${center[1]+120}" rx="${Math.max(120,lenPx*.58)}" ry="34" fill="rgba(65,48,28,.09)"/>`;
 const slats=7,slat=.095,gap=(1-slats*slat)/(slats-1);
 for(let i=0;i<slats;i++){const pos=i*(slat+gap);s+=box(add([ox,oy],mul(vy,pos)),vx,mul(vy,slat),10,top);}
 [0.08,.46,.84].forEach(x=>{const o=add(add([ox,oy],mul(vx,x)),mul(vy,.04));s+=box(add(o,V(0,27)),mul(vx,.08),mul(vy,.92),8,mid);});
 [0.07,.46,.85].forEach(x=>[.07,.45,.83].forEach(y=>{const o=add(add([ox,oy],mul(vx,x)),mul(vy,y));s+=box(add(o,V(0,39)),mul(vx,.075),mul(vy,.10),48,block);}));
 [.07,.45,.83].forEach(y=>{const o=add(add([ox,oy],mul(vy,y)),V(0,91));s+=box(o,vx,mul(vy,.10),8,bottom);});
 const A=[ox,oy],B=add(A,vx),D=add(A,vy),lenMid=[(A[0]+B[0])/2,(A[1]+B[1])/2-24],widMid=[(A[0]+D[0])/2-18,(A[1]+D[1])/2+18];
 s+=`<line class="palletDimensionLine" x1="${A[0]}" y1="${A[1]-15}" x2="${B[0]}" y2="${B[1]-15}"/><circle class="palletDimensionDot" cx="${A[0]}" cy="${A[1]-15}" r="3"/><circle class="palletDimensionDot" cx="${B[0]}" cy="${B[1]-15}" r="3"/><text class="palletDimensionLabel" x="${lenMid[0]}" y="${lenMid[1]}" text-anchor="middle">${Math.round(L)} мм</text>`;
 s+=`<line class="palletDimensionLine" x1="${A[0]-10}" y1="${A[1]}" x2="${D[0]-10}" y2="${D[1]}"/><circle class="palletDimensionDot" cx="${A[0]-10}" cy="${A[1]}" r="3"/><circle class="palletDimensionDot" cx="${D[0]-10}" cy="${D[1]}" r="3"/><text class="palletDimensionLabel" x="${widMid[0]}" y="${widMid[1]}" text-anchor="middle">${Math.round(W)} мм</text>`;
 root.innerHTML=`<svg class="dynamicPalletSvg" viewBox="0 0 700 390" xmlns="http://www.w3.org/2000/svg" aria-label="Поддон ${Math.round(L)} на ${Math.round(W)} миллиметров">${s}</svg>`;
}
document.getElementById("rotatePallet")?.addEventListener("click",()=>{palletPreviewAngle=(palletPreviewAngle+1)%2;renderDynamicPallet(Number(document.getElementById("pL")?.value),Number(document.getElementById("pW")?.value));});
document.getElementById("zoomPallet")?.addEventListener("click",()=>{document.getElementById("previewStage")?.classList.toggle("zoomed");});'''

if old_handlers not in text:
    raise SystemExit('old preview handlers not found')
text = text.replace(old_handlers, new_handlers, 1)

path.write_text(text, encoding='utf-8')
print('dynamic pallet preview installed')
