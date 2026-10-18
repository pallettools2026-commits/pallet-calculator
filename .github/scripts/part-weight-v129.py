from pathlib import Path
import re

repo = Path('.')
js = repo / 'assets/pallet3d-v10.js'
s = js.read_text(encoding='utf-8')

pattern = re.compile(r"    const showInspect=\(mesh\)=>\{.*?return true;\};", re.S)
m = pattern.search(s)
if not m:
    raise SystemExit('showInspect not found')

replacement = r"""    const showInspect=(mesh)=>{
      const info=mesh?.userData?.palletInspect;
      if(!info)return false;
      resetInspectHighlight();
      mesh.material.emissive.setHex(0xb66a2d);
      mesh.material.emissiveIntensity=.50;
      const itemNo=Number(info.index||0)+1;
      const qty=Math.max(1,Math.round(num(el('qty')?.value,1)));
      const total=info.n*qty;
      let density=num(el('smartDensity')?.value,0);
      if(!(density>=250&&density<=1000)){
        try{density=num(localStorage.getItem('pallettools:woodDensity'),500);}catch(_){density=500;}
      }
      density=clamp(density||500,250,1000);
      const pieceVolume=Math.max(0,num(info.t))*Math.max(0,num(info.w))*Math.max(0,num(info.l))/1e9;
      const pieceWeight=pieceVolume*density;
      const palletWeight=pieceWeight*info.n;
      const orderWeight=pieceWeight*total;
      const fmtKg=v=>{
        const x=Math.max(0,num(v,0));
        if(x<1)return `${(Math.round(x*100)/100).toLocaleString('ru-RU',{maximumFractionDigits:2})} кг`;
        if(x<100)return `${(Math.round(x*10)/10).toLocaleString('ru-RU',{maximumFractionDigits:1})} кг`;
        return `${Math.round(x).toLocaleString('ru-RU')} кг`;
      };
      if(partInspector){
        partInspector.hidden=false;
        partInspector.dataset.kind=info.kind||'';
        partInspector.querySelector('strong').textContent=`${info.name} №${itemNo}`;
        partInspector.querySelector('span').textContent=`${fmtMm(info.t)} × ${fmtMm(info.w)} × ${fmtMm(info.l)} мм`;
        partInspector.querySelector('b').textContent=`На поддон: ${info.n} шт. · На заказ: ${total.toLocaleString('ru-RU')} шт.`;
        let weightLine=partInspector.querySelector('.palletPartWeight');
        if(!weightLine){weightLine=document.createElement('em');weightLine.className='palletPartWeight';partInspector.appendChild(weightLine);}
        weightLine.textContent=`Вес 1 шт.: ${fmtKg(pieceWeight)} · На поддон: ${fmtKg(palletWeight)} · Заказ: ${fmtKg(orderWeight)} · ${Math.round(density)} кг/м³`;
      }
      setPickHint(`Выбрано: ${info.name} №${itemNo} · ${fmtMm(info.t)} × ${fmtMm(info.w)} × ${fmtMm(info.l)} мм`,true);
      window.dispatchEvent(new CustomEvent('pallet3d:partselect',{detail:{...info,itemNo,boardNo:itemNo,per:info.n,total,density,pieceWeightKg:pieceWeight,palletWeightKg:palletWeight,orderWeightKg:orderWeight}}));
      renderer.render(scene,camera);
      lastInspectAt=performance.now();
      return true;
    };"""
s = s[:m.start()] + replacement + s[m.end():]
js.write_text(s, encoding='utf-8')

smart = repo / 'assets/smart-tools-v1.js'
ss = smart.read_text(encoding='utf-8')
old = "    qty.textContent=`${selectedPart.per} шт. на поддон · ${Number(selectedPart.total||0).toLocaleString('ru-RU')} шт. на заказ`;"
new = """    const weightOne=Number(selectedPart.pieceWeightKg||0),weightOrder=Number(selectedPart.orderWeightKg||0);
    const weightText=weightOne>0?` · вес 1 шт. ${fmt(weightOne)} кг · заказ ${Math.round(weightOrder).toLocaleString('ru-RU')} кг`:'';
    qty.textContent=`${selectedPart.per} шт. на поддон · ${Number(selectedPart.total||0).toLocaleString('ru-RU')} шт. на заказ${weightText}`;"""
if old not in ss:
    raise SystemExit('smart selected qty line not found')
ss = ss.replace(old, new, 1)
smart.write_text(ss, encoding='utf-8')

css = repo / 'assets/theme-industrial-v130.css'
c = css.read_text(encoding='utf-8')
marker = '/* selectedPartWeightV1129 */'
if marker not in c:
    c += r'''

/* selectedPartWeightV1129 */
.palletPartInspector .palletPartWeight{
  display:block!important;
  margin-top:5px!important;
  padding-top:6px!important;
  border-top:1px solid rgba(139,91,45,.18)!important;
  color:#7a512c!important;
  font-size:10px!important;
  font-style:normal!important;
  font-weight:850!important;
  line-height:1.35!important;
}
html[data-theme="dark"] .palletPartInspector .palletPartWeight{
  border-top-color:rgba(232,202,154,.18)!important;
  color:#efc998!important;
}
@media(max-width:620px){
  .palletPartInspector .palletPartWeight{font-size:9px!important}
}
'''
    css.write_text(c, encoding='utf-8')

idx = repo / 'index.html'
h = idx.read_text(encoding='utf-8')
h = re.sub(r'assets/pallet3d-v10\.js\?v=\d+', 'assets/pallet3d-v10.js?v=129', h)
h = re.sub(r'assets/smart-tools-v1\.js\?v=\d+', 'assets/smart-tools-v1.js?v=129', h)
h = re.sub(r'assets/theme-industrial-v130\.css\?v=\d+', 'assets/theme-industrial-v130.css?v=179', h)
idx.write_text(h, encoding='utf-8')
