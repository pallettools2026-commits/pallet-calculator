(()=>{
  const VERSION='v1.1.16';
  const UPDATE_NO=365;
  const OWNER_USER_ID='8c7c190b-8d8c-4e51-adb6-580b519a44aa';
  const SELECTOR='.sideVersion,.mobileMoreVersion';

  function isOwner(){
    const user=(typeof currentUser!=='undefined'&&currentUser)||window.currentUser||null;
    const role=(typeof currentRole!=='undefined'&&currentRole)||window.currentRole||'employee';
    return role==='admin'&&user?.id===OWNER_USER_ID;
  }

  function removeDuplicates(){
    const sidebar=document.querySelector('.appSidebar');
    if(sidebar){
      const labels=[...sidebar.querySelectorAll('.sideVersion')];
      labels.slice(1).forEach(node=>node.remove());
    }
    document.querySelectorAll('.mobileMoreSheet').forEach(sheet=>{
      const labels=[...sheet.querySelectorAll('.mobileMoreVersion')];
      labels.slice(1).forEach(node=>node.remove());
    });
  }

  function installTruckPlannerLink(){
    const nav=document.querySelector('.appSidebar .sideNav');
    if(nav&&!document.getElementById('truckPlannerSideNav')){
      const link=document.createElement('a');
      link.id='truckPlannerSideNav';
      link.className='navLink appSideLink truckPlannerSideLink';
      link.href='truck-planner.html';
      link.innerHTML='<span>🚛</span>Планировщик фуры';
      const before=nav.querySelector('[data-screen="saved"]');
      nav.insertBefore(link,before||null);
    }

    const mobileActions=document.querySelector('.mobileMoreActions');
    if(mobileActions&&!document.getElementById('mobileTruckPlannerNav')){
      const link=document.createElement('a');
      link.id='mobileTruckPlannerNav';
      link.className='mobileMoreAction truckPlannerMobileLink';
      link.href='truck-planner.html';
      link.innerHTML='<span>🚛</span><b>Планировщик фуры</b><i>›</i>';
      const before=mobileActions.querySelector('#mobileProfileBtn');
      mobileActions.insertBefore(link,before||null);
    }
  }

  function installVisibilityGuard(){
    if(document.getElementById('versionLabelGuardV148'))return;
    ['versionLabelGuardV143','versionLabelGuardV145','versionLabelGuardV146','versionLabelGuardV147'].forEach(id=>document.getElementById(id)?.remove());
    const style=document.createElement('style');
    style.id='versionLabelGuardV148';
    style.textContent=`
      .appSidebar .sideVersion,.mobileMoreVersion{
        font-size:9px!important;
        white-space:normal!important;
        overflow:visible!important;
        text-overflow:clip!important;
        max-width:100%!important;
        line-height:1.35!important;
        text-align:center!important;
      }
      .appSidebar .sideVersion::after,.mobileMoreVersion::after{
        content:none!important;
        display:none!important;
      }
      .sideVersion .versionBase,.mobileMoreVersion .versionBase{display:block!important}
      .sideVersion .versionUpdate,.mobileMoreVersion .versionUpdate{
        display:block!important;
        margin-top:2px!important;
        font-size:.92em!important;
        white-space:nowrap!important;
      }
      .truckPlannerSideLink{text-decoration:none!important;box-sizing:border-box!important}
      .truckPlannerMobileLink{text-decoration:none!important;box-sizing:border-box!important}
      .mobileMoreSheet[hidden]{display:none!important}
      @media(min-width:761px){.mobileBottomNav,.mobileMoreSheet{display:none!important}}
      @media(max-width:760px){.appSidebar .sideVersion{display:none!important}}
    `;
    document.head.appendChild(style);
  }

  function normalize(){
    removeDuplicates();
    installTruckPlannerLink();
    const owner=isOwner();
    const baseText=`Pallet Tools · ${VERSION}`;
    const updateText=`обновление №${UPDATE_NO}`;
    const expected=owner?baseText+updateText:baseText;

    document.querySelectorAll(SELECTOR).forEach(node=>{
      if(node.dataset.versionLayout==='148'&&node.dataset.ownerVersion===String(owner)&&node.textContent.trim()===expected)return;
      const base=document.createElement('span');
      base.className='versionBase';
      base.textContent=baseText;
      const children=[base];
      if(owner){
        const update=document.createElement('span');
        update.className='versionUpdate';
        update.textContent=updateText;
        children.push(update);
      }
      node.replaceChildren(...children);
      node.dataset.versionLayout='148';
      node.dataset.ownerVersion=String(owner);
    });
  }

  function observe(root){
    if(!root)return;
    new MutationObserver(()=>queueMicrotask(normalize)).observe(root,{
      childList:true,
      characterData:true,
      subtree:true,
      attributes:true,
      attributeFilter:['hidden','style','class']
    });
  }

  function start(){
    installVisibilityGuard();
    installTruckPlannerLink();
    normalize();
    observe(document.getElementById('adminSideNav'));
    observe(document.querySelector('.appSidebar'));
    document.querySelectorAll('.mobileMoreSheet').forEach(observe);
    window.addEventListener('load',normalize,{once:true});
    [100,250,600,1200,2500].forEach(ms=>setTimeout(normalize,ms));
  }

  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',start,{once:true});
  else start();
})();
