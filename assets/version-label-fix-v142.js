(()=>{
  const VERSION='v1.1.16';
  const UPDATE_NO=352;
  const OWNER_USER_ID='8c7c190b-8d8c-4e51-adb6-580b519a44aa';
  const SELECTOR='.sideVersion,.mobileMoreVersion';

  function isOwner(){
    const user=(typeof currentUser!=='undefined'&&currentUser)||window.currentUser||null;
    const role=(typeof currentRole!=='undefined'&&currentRole)||window.currentRole||'employee';
    return role==='admin'&&user?.id===OWNER_USER_ID;
  }

  function label(){
    return isOwner()
      ? `Pallet Tools · ${VERSION} · обновление №${UPDATE_NO}`
      : `Pallet Tools · ${VERSION}`;
  }

  function installVisibilityGuard(){
    if(document.getElementById('versionLabelGuardV146'))return;
    document.getElementById('versionLabelGuardV143')?.remove();
    document.getElementById('versionLabelGuardV145')?.remove();
    const style=document.createElement('style');
    style.id='versionLabelGuardV146';
    style.textContent=`
      .sideVersion,.mobileMoreVersion{white-space:nowrap!important;overflow:hidden!important;text-overflow:ellipsis!important}
      .mobileMoreSheet[hidden]{display:none!important}
      @media(min-width:761px){.mobileBottomNav,.mobileMoreSheet{display:none!important}}
      @media(max-width:760px){.appSidebar .sideVersion{display:none!important}}
    `;
    document.head.appendChild(style);
  }

  function normalize(){
    const next=label();
    document.querySelectorAll(SELECTOR).forEach(node=>{
      if(node.textContent.trim()!==next)node.replaceChildren(document.createTextNode(next));
    });
  }

  function start(){
    installVisibilityGuard();
    normalize();

    const adminNav=document.getElementById('adminSideNav');
    if(adminNav){
      new MutationObserver(()=>queueMicrotask(normalize)).observe(adminNav,{
        attributes:true,
        attributeFilter:['hidden','style','class']
      });
    }

    const labels=[...document.querySelectorAll(SELECTOR)];
    labels.forEach(node=>{
      new MutationObserver(()=>queueMicrotask(normalize)).observe(node,{
        childList:true,
        characterData:true,
        subtree:true
      });
    });

    window.addEventListener('load',normalize,{once:true});
    [100,250,600,1200,2500].forEach(ms=>setTimeout(normalize,ms));
  }

  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',start,{once:true});
  else start();
})();
