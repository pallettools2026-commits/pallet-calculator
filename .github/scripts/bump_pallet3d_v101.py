from pathlib import Path
import re

js=Path('assets/pallet3d-v10.js')
s=js.read_text(encoding='utf-8')

if 'pallet3dReferenceV123' not in s:
    old='/* pallet3dReferenceV122 — all pallet blocks rotated 90 degrees */'
    if old not in s:
        raise SystemExit('V122 marker not found')
    s=s.replace(old,'/* pallet3dReferenceV123 — workshop photo reference 1250x1180 */',1)

    old="return {key:'1250x1180',width:1250,length:1180,deckMax:9,bindingCount:3,runnerLengths:[1180,1050,1050,1050,1180],spec:'Ширина 1250 × длина 1180 · 5 лыж: 2×1180 + 3×1050 · обвязка 3 · настил до 9'};"
    new="return {key:'1250x1180',width:1250,length:1180,deckMax:9,bindingCount:3,runnerLengths:[1180,1180,1180],spec:'Фото-эталон 1250 × 1180 · 9 досок настила · 3 поперечины · 9 шашек · 3 нижние лыжи'};"
    if old not in s:
        raise SystemExit('1250 profile not found')
    s=s.replace(old,new,1)

    pattern=r"  function syncProfileInputs\(profile\)\{.*?\n  \}\n\n  function currentSignature\(\)\{"
    repl="""  function syncProfileInputs(profile){
    const deck=el('n0');
    if(deck)deck.max=String(profile.deckMax);
    // 3D reference must never rewrite production calculator values.
  }

  function currentSignature(){"""
    s,n=re.subn(pattern,repl,s,count=1,flags=re.S)
    if n!=1:
        raise SystemExit('syncProfileInputs block not found')

    old="""    const rawDeck=Math.max(0,Math.round(num(deck.n))),deckCount=Math.min(profile.deckMax,rawDeck);
    const rawBlocks=Math.max(0,Math.round(num(block1.n)))+Math.max(0,Math.round(num(block2.n))),blockCount=Math.min(9,rawBlocks||9);
    const runnerCount=profile.runnerLengths?profile.runnerLengths.length:Math.max(1,Math.min(7,Math.round(num(runnerParts[0].n)+num(runnerParts[1].n))||3));"""
    new="""    const isReference=profile.key==='1250x1180';
    const rawDeck=Math.max(0,Math.round(num(deck.n))),deckCount=isReference?9:Math.min(profile.deckMax,rawDeck);
    const rawBlocks=Math.max(0,Math.round(num(block1.n)))+Math.max(0,Math.round(num(block2.n))),blockCount=isReference?9:Math.min(9,rawBlocks||9);
    const runnerCount=isReference?3:(profile.runnerLengths?profile.runnerLengths.length:Math.max(1,Math.min(7,Math.round(num(runnerParts[0].n)+num(runnerParts[1].n))||3)));"""
    if old not in s:
        raise SystemExit('count block not found')
    s=s.replace(old,new,1)

    old="""    const mode=state.mode||'3d';
    const chip=(k,label,c)=>`<button type=\"button\" class=\"palletPartChip ${state.selected===k?'active':''}\" data-p3d-part=\"${k}\">${label}<b>${c}</b></button>`;
    root.innerHTML=`"""
    new="""    const mode=state.mode||'3d';
    const chip=(k,label,c)=>`<button type=\"button\" class=\"palletPartChip ${state.selected===k?'active':''}\" data-p3d-part=\"${k}\">${label}<b>${c}</b></button>`;
    const refTag=isReference?'<span style=\"display:inline-flex;margin-right:7px;padding:3px 7px;border-radius:999px;background:#173f35;color:#fff;font-size:10px;font-weight:900;letter-spacing:.04em\">ФОТО-ЭТАЛОН</span>':'';
    root.innerHTML=`"""
    if old not in s:
        raise SystemExit('toolbar insertion point not found')
    s=s.replace(old,new,1)
    s=s.replace('>${profile.spec}</div><div class="palletReferenceStage">','>${refTag}${profile.spec}</div><div class="palletReferenceStage">',1)
    s=s.replace('Настил идёт по длине · обвязка поперёк · шашки 3×3 · размеры перестраивают модель автоматически','Для 1250 × 1180 используется отдельная модель по вашим фото · вращайте мышкой или пальцем · колесо — масштаб',1)

    old="""    const textures={deck:woodTexture(17,'#edc998','#8d6138'),cross:woodTexture(31,'#e4be89','#855a35'),runner:woodTexture(47,'#ddb27b','#7b5130'),block:woodTexture(61,'#d6a56d','#764c2e')};
    Object.values(textures).forEach((t,i)=>t.repeat.set(i===3?1.4:3.2,1));
    const colors={deck:[0xf0d2a5,0xe8c28e,0xf2d7ad],cross:[0xe4bd87,0xdbad76,0xe9c795],runner:[0xd8aa70,0xcf9c61,0xdfb57e],block:[0xc9955e,0xd2a16b,0xc48c55]};"""
    new="""    const textures={deck:woodTexture(17,'#f3dfbd','#9a724b'),cross:woodTexture(31,'#ecd2a8','#906642'),runner:woodTexture(47,'#e8ca9a','#875d39'),block:woodTexture(61,'#dfbb86','#805433')};
    Object.values(textures).forEach((t,i)=>t.repeat.set(i===3?1.4:3.2,1));
    const colors={deck:[0xf3dab2,0xefd1a4,0xf6e0bf],cross:[0xeccda0,0xe6c18f,0xf0d5ad],runner:[0xe4c08d,0xddb47f,0xe9ca9a],block:[0xd8aa72,0xdfb783,0xd2a069]};"""
    if old not in s:
        raise SystemExit('wood palette block not found')
    s=s.replace(old,new,1)

    old="""    const runnerT=Math.max(.15,num(runnerParts[0].t,22)*S),runnerW=Math.max(.58,num(runnerParts[0].w,98)*S);
    const blockH=Math.max(.62,num(block1.t||block2.t,75)*S),blockXSize1=Math.max(.72,num(block1.l,150)*S),blockZSize1=Math.max(.72,num(block1.w,98)*S),blockXSize2=Math.max(.72,num(block2.l,98)*S),blockZSize2=Math.max(.72,num(block2.w,100)*S);
    const bindT=Math.max(.15,num(bindParts[0].t,22)*S),bindDepth=Math.max(.58,num(bindParts[0].w,98)*S);
    const deckT=Math.max(.15,num(deck.t,22)*S),deckW=Math.max(.58,num(deck.w,98)*S);"""
    new="""    const runnerT=isReference?.22:Math.max(.15,num(runnerParts[0].t,22)*S),runnerW=isReference?.98:Math.max(.58,num(runnerParts[0].w,98)*S);
    const blockH=isReference?.78:Math.max(.62,num(block1.t||block2.t,75)*S),blockXSize1=isReference?1.50:Math.max(.72,num(block1.l,150)*S),blockZSize1=isReference?.98:Math.max(.72,num(block1.w,98)*S),blockXSize2=isReference?.98:Math.max(.72,num(block2.l,98)*S),blockZSize2=isReference?1.00:Math.max(.72,num(block2.w,100)*S);
    const bindT=isReference?.22:Math.max(.15,num(bindParts[0].t,22)*S),bindDepth=isReference?.98:Math.max(.58,num(bindParts[0].w,98)*S);
    const deckT=isReference?.22:Math.max(.15,num(deck.t,22)*S),deckW=isReference?.98:Math.max(.58,num(deck.w,98)*S);"""
    if old not in s:
        raise SystemExit('dimension block not found')
    s=s.replace(old,new,1)

    js.write_text(s,encoding='utf-8')
    print('pallet3d-v10 upgraded to photo reference V123')
else:
    print('pallet3d-v10 already V123')

idx=Path('index.html')
h=idx.read_text(encoding='utf-8')
if 'assets/pallet3d-v10.js?v=123' not in h:
    old='assets/pallet3d-v10.js?v=122'
    if old not in h:
        raise SystemExit('active v10 script reference not found')
    h=h.replace(old,'assets/pallet3d-v10.js?v=123',1)
    idx.write_text(h,encoding='utf-8')
    print('index cache-busted to v123')
else:
    print('index already v123')
