(()=>{
  const SELECTOR='.sideVersion,.mobileMoreVersion';
  const FALLBACK_VERSION='v1.1.16';

  function getVersion(text){
    const m=String(text||'').match(/v\d+(?:\.\d+)+/i);
    return m?m[0]:null;
  }

  function getUpdates(text){
    const out=[];
    const re=/обновление\s*№\s*(\d+)/gi;
    let m;
    while((m=re.exec(String(text||''))))out.push(Number(m[1]));
    return out.filter(Number.isFinite);
  }

  function normalize(){
    const nodes=[...document.querySelectorAll(SELECTOR)];
    if(!nodes.length)return;

    const combined=nodes.map(n=>n.textContent||'').join(' ');
    const version=getVersion(combined)||FALLBACK_VERSION;
    const updates=getUpdates(combined);
    const latest=updates.length?Math.max(...updates):null;
    const label=`Pallet Tools · ${version}${latest!==null?` · обновление №${latest}`:''}`;

    nodes.forEach(node=>{
      if(node.textContent.trim()!==label)node.textContent=label;
      node.style.whiteSpace='nowrap';
      node.style.overflow='hidden';
      node.style.textOverflow='ellipsis';
    });
  }

  function start(){
    normalize();
    const observer=new MutationObserver(()=>queueMicrotask(normalize));
    document.querySelectorAll(SELECTOR).forEach(node=>observer.observe(node,{childList:true,characterData:true,subtree:true}));
    window.addEventListener('load',normalize,{once:true});
    setTimeout(normalize,250);
    setTimeout(normalize,1200);
  }

  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',start,{once:true});
  else start();
})();
