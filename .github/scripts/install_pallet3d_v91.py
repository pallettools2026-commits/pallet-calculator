from pathlib import Path

js=Path('assets/pallet3d-v9.js')
j=js.read_text(encoding='utf-8')
j=j.replace("roughness:isEnd?.86:.74","roughness:isEnd ? .86 : .74")
j=j.replace("opacity:(selected==='all'||selected===kind)?.16:.035","opacity:(selected==='all'||selected===kind) ? .16 : .035")
js.write_text(j,encoding='utf-8')

p=Path('index.html')
s=p.read_text(encoding='utf-8')
marker='/* pallet3dWebGLV8 */'
if marker in s:
    m=s.index(marker)
    start=s.rfind('<script',0,m)
    end=s.find('</script>',m)
    if start<0 or end<0:
        raise SystemExit('3D script boundaries not found')
    end+=len('</script>')
    s=s[:start]+'<script src="assets/pallet3d-v9.js?v=91"></script>'+s[end:]
elif 'assets/pallet3d-v9.js' not in s:
    raise SystemExit('3D insertion point not found')

css='<link rel="stylesheet" href="assets/pallet3d-v9.css?v=91">'
if 'assets/pallet3d-v9.css' not in s:
    s=s.replace('</head>',css+'\n</head>',1)
p.write_text(s,encoding='utf-8')
print('pallet 3D v91 installed')
