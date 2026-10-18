(()=>{
  if(window.__palletToolsPwaV1)return;
  window.__palletToolsPwaV1=true;

  function ensureLink(rel,href,extra={}){
    let node=document.querySelector(`link[rel="${rel}"]`);
    if(!node){
      node=document.createElement('link');
      node.rel=rel;
      document.head.appendChild(node);
    }
    node.href=href;
    Object.entries(extra).forEach(([key,value])=>node.setAttribute(key,value));
  }

  function ensureMeta(name,content){
    let node=document.querySelector(`meta[name="${name}"]`);
    if(!node){
      node=document.createElement('meta');
      node.name=name;
      document.head.appendChild(node);
    }
    node.content=content;
  }

  ensureLink('manifest','manifest.webmanifest?v=1');
  ensureLink('icon','assets/pwa-icon.svg',{type:'image/svg+xml'});
  ensureMeta('theme-color','#0d392f');
  ensureMeta('mobile-web-app-capable','yes');
  ensureMeta('apple-mobile-web-app-capable','yes');
  ensureMeta('apple-mobile-web-app-status-bar-style','default');
  ensureMeta('apple-mobile-web-app-title','Pallet Tools');

  if('serviceWorker' in navigator && location.protocol==='https:'){
    window.addEventListener('load',async()=>{
      try{
        const reg=await navigator.serviceWorker.register('./service-worker.js',{scope:'./'});
        reg.update().catch(()=>{});
      }catch(err){
        console.warn('Pallet Tools PWA registration skipped:',err);
      }
    },{once:true});
  }
})();
