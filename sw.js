const CACHE='minukimi-shell-v3';
const SHELL=['./manifest.webmanifest','./icons/icon.svg'];

self.addEventListener('install',e=>e.waitUntil(
  caches.open(CACHE).then(c=>c.addAll(SHELL)).then(()=>self.skipWaiting())
));

self.addEventListener('activate',e=>e.waitUntil(
  caches.keys()
    .then(keys=>Promise.all(keys.filter(k=>k!==CACHE).map(k=>caches.delete(k))))
    .then(()=>self.clients.claim())
));

self.addEventListener('fetch',e=>{
  if(e.request.method!=='GET') return;
  const url=new URL(e.request.url);

  // Always prefer the live app shell. During UX testing we must never let an
  // old cached profile/photo survive a deploy.
  if(e.request.mode==='navigate' || url.pathname==='/' || url.pathname.endsWith('/index.html')){
    e.respondWith(
      fetch(e.request,{cache:'no-store'})
        .then(r=>r)
        .catch(()=>caches.match('./index.html'))
    );
    return;
  }

  // Static assets can still use cache-first for PWA resilience.
  e.respondWith(
    caches.match(e.request).then(hit=>hit||fetch(e.request).then(r=>{
      if(url.origin===location.origin && r.ok){
        const copy=r.clone();
        caches.open(CACHE).then(c=>c.put(e.request,copy));
      }
      return r;
    }))
  );
});
