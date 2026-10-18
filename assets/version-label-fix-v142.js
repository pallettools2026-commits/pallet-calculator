(()=>{
  const LABEL='Pallet Tools · v1.1.16';
  const SELECTOR='.sideVersion,.mobileMoreVersion';

  function installVisibilityGuard(){
    if(document.getElementById('versionLabelGuardV143'))return;
    const style=document.createElement('style');
    style.id='versionLabelGuardV143';
    style.textContent=`
      .sideVersion,.mobileMoreVersion{white-space:nowrap!important;overflow:hidden!important;text-overflow:ellipsis!important}
      .mobileMoreSheet[hidden]{display:none!important}
      @media(min-width:761px){.mobileBottomNav,.mobileMoreSheet{display:none!important}}
      @media(max-width:760px){.appSidebar .sideVersion{display:none!important}}
    `;
    document.head.appendChild(style);
  }

  function normalize(){
    document.querySelectorAll(SELECTOR).forEach(node=>{
      if(node.textContent.trim()!==LABEL)node.replaceChildren(document.createTextNode(LABEL));
    });
  }

  function start(){
    installVisibilityGuard();
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
