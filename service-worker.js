const CACHE_VERSION='pallet-tools-pwa-v1';
const STATIC_CACHE=`${CACHE_VERSION}-static`;
const RUNTIME_CACHE=`${CACHE_VERSION}-runtime`;
const CORE=['./','./index.html','./manifest.webmanifest','./assets/pwa-icon.svg'];
const STATIC_CDN_HOSTS=new Set(['cdn.jsdelivr.net']);

self.addEventListener('install',event=>{
  event.waitUntil((async()=>{
    const cache=await caches.open(STATIC_CACHE);
    await Promise.allSettled(CORE.map(url=>cache.add(url)));
    await self.skipWaiting();
  })());
});

self.addEventListener('activate',event=>{
  event.waitUntil((async()=>{
    const keys=await caches.keys();
    await Promise.all(keys.filter(key=>key.startsWith('pallet-tools-pwa-')&&!key.startsWith(CACHE_VERSION)).map(key=>caches.delete(key)));
    await self.clients.claim();
  })());
});

async function networkFirstNavigation(request){
  const cache=await caches.open(RUNTIME_CACHE);
  try{
    const response=await fetch(request);
    if(response&&response.ok) await cache.put('./index.html',response.clone());
    return response;
  }catch(_){
    return (await cache.match('./index.html')) || (await caches.match('./index.html')) || (await caches.match('./')) || Response.error();
  }
}

async function staleWhileRevalidate(request,cacheName){
  const cache=await caches.open(cacheName);
  const cached=await cache.match(request);
  const networkPromise=fetch(request).then(async response=>{
    if(response&&(response.ok||response.type==='opaque')){
      try{await cache.put(request,response.clone());}catch(_){ }
    }
    return response;
  }).catch(()=>null);
  return cached || (await networkPromise) || Response.error();
}

self.addEventListener('fetch',event=>{
  const request=event.request;
  if(request.method!=='GET') return;
  const url=new URL(request.url);
  if(url.protocol!=='http:'&&url.protocol!=='https:') return;

  if(request.mode==='navigate'&&url.origin===self.location.origin){
    event.respondWith(networkFirstNavigation(request));
    return;
  }

  if(url.origin===self.location.origin){
    event.respondWith(staleWhileRevalidate(request,RUNTIME_CACHE));
    return;
  }

  if(STATIC_CDN_HOSTS.has(url.hostname)){
    event.respondWith(staleWhileRevalidate(request,RUNTIME_CACHE));
  }
});
