from pathlib import Path

js=Path('assets/pallet3d-v10.js')
s=js.read_text(encoding='utf-8')
old="""  function updateSiteVersion(){const node=document.querySelector('.sideVersion');if(!node)return;const admin=typeof currentRole!=='undefined'&&currentRole==='admin';node.textContent=admin?'Pallet Tools · v1.1.16 · обновление №346':'Pallet Tools · v1.1.16';}\n  window.updateSiteVersion=updateSiteVersion;\n  const adminVersionTarget=el('adminSideNav');if(adminVersionTarget&&window.MutationObserver){new MutationObserver(updateSiteVersion).observe(adminVersionTarget,{attributes:true,attributeFilter:['hidden','style']});}\n"""
new="""  function updateSiteVersion(){\n    const node=document.querySelector('.sideVersion');\n    if(node)node.textContent='Pallet Tools · v1.1.16';\n  }\n  window.updateSiteVersion=updateSiteVersion;\n"""
if old not in s:
    raise SystemExit('version source block not found')
s=s.replace(old,new,1)
js.write_text(s,encoding='utf-8')

p=Path('index.html')
h=p.read_text(encoding='utf-8')
h=h.replace('assets/pallet3d-v10.js?v=135','assets/pallet3d-v10.js?v=144')
p.write_text(h,encoding='utf-8')
print('removed competing sidebar version source')
