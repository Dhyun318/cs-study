// 오프라인 지원 서비스 워커. 모든 경로는 이 파일 위치 기준 상대 경로.
const VERSION = 'd2043364'; // 배포 때 올리면 옛 캐시가 지워진다
const CACHE = 'cs-chagok-' + VERSION;
const SHELL = ['./', 'index.html', 'app.css', 'app.js', 'manifest.webmanifest', 'data/notes.json',
  'icons/icon.svg', 'icons/icon-192.png', 'icons/icon-512.png', 'icons/apple-touch-icon.png'];

// 설치: 앱 껍데기는 반드시 캐시, precache.json 목록(있으면)은 되는 만큼만 캐시
self.addEventListener('install', e => {
  e.waitUntil((async () => {
    const cache = await caches.open(CACHE);
    await cache.addAll(SHELL.map(u => new Request(u, { cache: 'reload' })));
    const list = await fetch('data/precache.json', { cache: 'no-cache' })
      .then(r => (r.ok ? r.json() : []), () => []);
    await Promise.allSettled(list.map(u => cache.add(u)));
    await self.skipWaiting();
  })());
});

// 활성화: 옛 버전 캐시 삭제 후 열린 탭을 바로 넘겨받음
self.addEventListener('activate', e => {
  e.waitUntil((async () => {
    for (const k of await caches.keys()) if (k.startsWith('cs-chagok-') && k !== CACHE) await caches.delete(k);
    await self.clients.claim();
  })());
});

// 네트워크 우선(4초 안에 못 받으면 캐시), 실패해도 캐시 (html, js, css, manifest, notes.json)
async function networkFirst(req) {
  const cache = await caches.open(CACHE);
  try {
    const res = await Promise.race([fetch(req), new Promise((_, no) => setTimeout(no, 4000))]);
    if (res.ok) cache.put(req, res.clone());
    return res;
  } catch (err) {
    return (await cache.match(req, { ignoreSearch: true })) || cache.match('index.html');
  }
}

// 캐시 먼저 주고 뒤에서 갱신 (sims, illustrations, 글꼴 등). 다른 출처는 opaque 응답도 저장
async function staleWhileRevalidate(req) {
  const cache = await caches.open(CACHE);
  const cached = await cache.match(req);
  const fresh = fetch(req).then(res => {
    if (res.ok || res.type === 'opaque') cache.put(req, res.clone());
    return res;
  });
  if (cached) { fresh.catch(() => {}); return cached; }
  return fresh;
}

self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  const isPage = req.mode === 'navigate' || url.pathname.endsWith('.html');
  const isCore = url.origin === location.origin && /\/(data\/notes\.json|app\.js|app\.css|manifest\.webmanifest)$/.test(url.pathname);
  e.respondWith(isPage || isCore ? networkFirst(req) : staleWhileRevalidate(req));
});
