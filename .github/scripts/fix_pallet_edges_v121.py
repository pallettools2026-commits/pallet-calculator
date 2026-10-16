from pathlib import Path

p=Path('assets/pallet3d-v10.js')
s=p.read_text(encoding='utf-8')
s=s.replace('/* pallet3dReferenceV120 — photo-matched block pallet geometry */','/* pallet3dReferenceV121 — flush-edge block pallet geometry */',1)

old="""    const runnerLengths=profile.runnerLengths||Array.from({length:runnerCount},(_,i)=>Math.min(profile.length,num((i<Math.max(0,num(runnerParts[0].n)))?runnerParts[0].l:runnerParts[1].l,profile.length)));
    const runnerXs=spread(runnerLengths.length,PW*.94,Math.min(runnerW,PW*.12));
    runnerLengths.forEach((mm,i)=>{const rz=clamp(mm*S,Math.min(PL*.55,10.5),PL),rw=Math.min(runnerW,PW/Math.max(3,runnerLengths.length)*.56);piece('runner',rw,runnerT,rz,runnerXs[i],runnerT/2,0,i,groups.runner);});

    const supportX=[-PW*.39,0,PW*.39],supportZ=[-PL*.40,0,PL*.40];
    const blockY=runnerT+blockH/2;
    for(let zi=0;zi<3;zi++)for(let xi=0;xi<3;xi++){
      const idx=zi*3+xi;if(idx>=blockCount)continue;
      const centerType=(xi===1),bx=centerType?blockXSize2:blockXSize1,bz=centerType?blockZSize2:blockZSize1;
      piece('block',bx,blockH,bz,supportX[xi],blockY,supportZ[zi],idx,groups.block);
    }

    const bindY=runnerT+blockH+bindT/2;
    supportZ.forEach((z,i)=>piece('cross',PW,bindT,bindDepth,0,bindY,z,i,groups.cross));

    const topY=runnerT+blockH+bindT+deckT/2,topXs=deckCount?spread(deckCount,PW*.98,Math.min(deckW,PW*.90/Math.max(1,deckCount))):[];
    const actualDeckW=deckCount?Math.min(deckW,(PW*.92/Math.max(1,deckCount))*.78):deckW;
    topXs.forEach((x,i)=>{
      piece('deck',actualDeckW,deckT,PL,x,topY,0,i,groups.deck);
      if(selected==='all'||selected==='deck')supportZ.forEach(z=>{const dx=Math.min(.07,actualDeckW*.23);nail(x-dx,topY+deckT/2+.014,z);nail(x+dx,topY+deckT/2+.014,z);});
    });
"""
new="""    const runnerLengths=profile.runnerLengths||Array.from({length:runnerCount},(_,i)=>Math.min(profile.length,num((i<Math.max(0,num(runnerParts[0].n)))?runnerParts[0].l:runnerParts[1].l,profile.length)));
    const runnerActualW=Math.min(runnerW,PW/Math.max(3,runnerLengths.length)*.56);
    const edgeRunnerX=Math.max(0,PW/2-runnerActualW/2-.03);
    let runnerXs;
    if(runnerLengths.length===5) runnerXs=[-edgeRunnerX,-edgeRunnerX*.5,0,edgeRunnerX*.5,edgeRunnerX];
    else if(runnerLengths.length===3) runnerXs=[-edgeRunnerX,0,edgeRunnerX];
    else runnerXs=spread(runnerLengths.length,PW,runnerActualW);
    runnerLengths.forEach((mm,i)=>{const rz=clamp(mm*S,Math.min(PL*.55,10.5),PL);piece('runner',runnerActualW,runnerT,rz,runnerXs[i],runnerT/2,0,i,groups.runner);});

    const blockY=runnerT+blockH/2;
    for(let zi=0;zi<3;zi++)for(let xi=0;xi<3;xi++){
      const idx=zi*3+xi;if(idx>=blockCount)continue;
      const centerType=(xi===1),bx=centerType?blockXSize2:blockXSize1,bz=centerType?blockZSize2:blockZSize1;
      const sx=xi===0?-1:xi===2?1:0,sz=zi===0?-1:zi===2?1:0;
      const bxPos=sx===0?0:sx*Math.max(0,PW/2-bx/2-.03);
      const bzPos=sz===0?0:sz*Math.max(0,PL/2-bz/2-.03);
      piece('block',bx,blockH,bz,bxPos,blockY,bzPos,idx,groups.block);
    }

    const bindY=runnerT+blockH+bindT/2;
    const bindZ=[-PL/2+bindDepth/2+.02,0,PL/2-bindDepth/2-.02];
    bindZ.forEach((z,i)=>piece('cross',PW,bindT,bindDepth,0,bindY,z,i,groups.cross));

    const topY=runnerT+blockH+bindT+deckT/2;
    const actualDeckW=deckCount?Math.min(deckW,(PW*.92/Math.max(1,deckCount))*.78):deckW;
    const topXs=deckCount?spread(deckCount,PW,actualDeckW):[];
    topXs.forEach((x,i)=>{
      piece('deck',actualDeckW,deckT,PL,x,topY,0,i,groups.deck);
      if(selected==='all'||selected==='deck')bindZ.forEach(z=>{const dx=Math.min(.07,actualDeckW*.23);nail(x-dx,topY+deckT/2+.014,z);nail(x+dx,topY+deckT/2+.014,z);});
    });
"""
if old not in s:
    raise SystemExit('target pallet geometry block not found')
s=s.replace(old,new,1)
p.write_text(s,encoding='utf-8')

idx=Path('index.html')
h=idx.read_text(encoding='utf-8')
if 'assets/pallet3d-v10.js?v=120' not in h:
    raise SystemExit('v120 asset reference not found')
h=h.replace('assets/pallet3d-v10.js?v=120','assets/pallet3d-v10.js?v=121',1)
idx.write_text(h,encoding='utf-8')
print('fixed pallet edge/block alignment and bumped to v121')
