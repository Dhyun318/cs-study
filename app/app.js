// CS 차곡: 화면 그리기, hash 라우팅, 진도 저장(localStorage). 화면과 동작의 기준은 design/v2/index.html 시안과 design/v2/spec/
'use strict';
const app = document.getElementById('app');
const KEYS = ['ds', 'os', 'db', 'net'];
const NAMES = { ds: '자료구조', os: '운영체제', db: '데이터베이스', net: '네트워크' }; // 본문을 받기 전(불러오는 중 화면)에도 쓰는 과목 이름
// id 조회 객체는 프로토타입이 없어야 #/q/constructor 같은 주소와 저장값의 constructor 키가 안 걸린다
let D, Q = Object.create(null), SUB = Object.create(null), SIM = Object.create(null), ORDER = [], STARS = [];
const inSub = k => D.questions.filter(q => q.s === k);
const txt = h => h.replace(/<[^>]+>/g, '');
const esc = s => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
const simStars = s => Math.max(0, ...s.qs.map(id => Q[id].stars));
const reduce = () => matchMedia('(prefers-reduced-motion: reduce)').matches;
const SCROLL_TL = CSS.supports('animation-timeline: --a') && CSS.supports('view-timeline: --a block');

// 단락 (00 6.2): 핵심 + 도입 + 소제목마다 + 꼬리질문 묶음
function chunks(q) {
  if (q._c) return q._c;
  const out = [{ t: '핵심', core: true }];
  q.body.split(/(?=<h3>)/).filter(Boolean).forEach(p => {
    const m = p.match(/^<h3>(.*?)<\/h3>/);
    out.push({ t: m ? m[1] : '', html: m ? p.slice(m[0].length) : p });
  });
  if (q.tails.length) out.push({ t: '꼬리질문', tails: true });
  return q._c = out;
}
const chars = q => (txt(q.core + q.body) + q.tails.map(t => t.q + txt(t.a)).join('')).length;
const minutes = q => Math.max(1, Math.ceil(chars(q) / 500)); // 예상 시간 = 글자 수 / 500 분 (화면에는 올림)

// ===== 저장 (00 6.5): localStorage `cs-chagok`, v 2. 옛 형식 { read, confused, last: { id, pct, text } } 은 옮긴다 =====
const KEY = 'cs-chagok';
let S = null, RAW = null, STORE = 'ok'; // STORE: ok | off(쓰기 실패) | broken(값이 깨져 새로 시작)
const blank = () => ({ read: new Set(), conf: new Set(), everConf: false, prog: Object.create(null), last: null, seen: {} });
function readStore() {
  try { localStorage.setItem(KEY + '-t', '1'); localStorage.removeItem(KEY + '-t'); RAW = localStorage.getItem(KEY); } catch (e) { STORE = 'off'; return; }
  if (!RAW) return;
  try { RAW = JSON.parse(RAW); if (!RAW || typeof RAW !== 'object' || Array.isArray(RAW)) throw 0; }
  catch (e) { try { localStorage.setItem(KEY + '-bak', RAW); } catch (e2) {} RAW = null; STORE = 'broken'; }
}
// 저장값 → 메모리. 모르는 id 는 버리고, 옛 형식의 스크롤 % 는 가장 가까운 단락으로
function fixStore(o) {
  const s = blank();
  if (!o) return s;
  const ids = a => (Array.isArray(a) ? a : []).filter(id => Q[id]);
  s.read = new Set(ids(o.read));
  s.conf = new Set(ids(o.v ? o.conf : o.confused));
  s.everConf = !!o.everConf || s.conf.size > 0;
  if (o.prog && typeof o.prog === 'object') Object.entries(o.prog).forEach(([id, n]) => { if (Q[id] && n > 0) s.prog[id] = Math.min(chunks(Q[id]).length, n | 0); });
  const L = o.last;
  if (L && Q[L.id]) {
    const n = chunks(Q[L.id]).length, ch = o.v ? L.chunk : Math.round((+L.pct || 0) / 100 * (n - 1)) + 1;
    s.last = { id: L.id, chunk: Math.min(n, Math.max(1, ch | 0)), para: String((o.v ? L.para : L.text) || '').slice(0, 16), at: +L.at || Date.now() };
    s.prog[L.id] = Math.max(s.prog[L.id] || 0, s.last.chunk);
  }
  if (o.seen && typeof o.seen === 'object') s.seen = { ...o.seen };
  return s;
}
function save() {
  if (STORE === 'off') return;
  try { localStorage.setItem(KEY, JSON.stringify({ v: 2, read: [...S.read], conf: [...S.conf], everConf: S.everConf, prog: S.prog, last: S.last, seen: S.seen })); }
  catch (e) { STORE = 'off'; repaintNotes(); }
}
const isRead = id => S.read.has(id), isConf = id => S.conf.has(id);
const prog = id => isRead(id) ? 1 : Math.min(1, (S.prog[id] || 0) / chunks(Q[id]).length);
const subRead = k => inSub(k).filter(q => isRead(q.id)).length;

// ===== 그리는 도구 =====
const ic = (id, cls = '') => `<svg class="ic ${cls}" aria-hidden="true"><use href="#i-${id}"/></svg>`;
const MARK = `<svg class="mark" viewBox="0 0 32 32" aria-hidden="true"><rect width="32" height="32" rx="7" fill="#03257B"/><g transform="translate(5 6.5) scale(1.16)"><rect x="5" width="14" height="4" rx="2" fill="#6194F8"/><rect y="6" width="18" height="4" rx="2" fill="#fff"/><rect x="3" y="12" width="16" height="4" rx="2" fill="#fff"/></g></svg>`;
const starTag = n => n ? `<span class="tag star num" aria-label="빈출 별 ${n}개">${ic('star', 'f')}${n}</span>` : '';
const confTag = (t = '헷갈림') => `<span class="tag conf">${t}</span>`;
function glyph(id) {
  if (isRead(id)) return `<span class="gl done" role="img" aria-label="읽음">${ic('check')}</span>`;
  const p = prog(id);
  if (p > 0) return `<span class="gl ing" style="--p:${p}" role="img" aria-label="읽는 중, ${chunks(Q[id]).length}단락 중 ${S.prog[id]}"></span>`;
  return '<span class="gl" role="img" aria-label="안 읽음"></span>';
}
const blockOf = (id, extra = '', k = 0) => `<i class="blk${isRead(id) ? ' r' : prog(id) > 0 ? ' i' : ''}${isConf(id) ? ' c' : ''}${extra}" style="--p:${prog(id)};--k:${k}"></i>`;
// 쌓는 순서: 읽음 → 읽는 중 → 안 읽음, 같은 무리 안에서는 헷갈림 먼저
const rank = id => (isRead(id) ? 0 : prog(id) > 0 ? 2 : 4) + (isConf(id) ? 0 : 1);
const stackOrder = k => inSub(k).map(q => q.id).sort((a, b) => rank(a) - rank(b) || Q[a].i - Q[b].i);
const segs = (n, filled, live, unit = '단락') => `<span class="seg${live ? ' live' : ''}" role="progressbar" aria-valuemin="0" aria-valuemax="${n}" aria-valuenow="${Math.round(filled)}" aria-valuetext="${n}${unit} 중 ${Math.max(1, Math.ceil(filled))}번째">${Array.from({ length: n }, (_, i) => `<i><b style="--f:${Math.max(0, Math.min(1, filled - i))}"></b></i>`).join('')}</span>`;
const ill = (id, cls = '') => `<span class="ill ${cls}"><img src="illustrations/${id}.png" alt=""></span>`;
const nw = s => esc(s).replace(/(\S+\/\S+)/g, '<span class="nw">$1</span>');
const tt = s => esc(s).replace(/(\S{1,8}\)[가-힣]+)/g, '<span class="nw">$1</span>'); // 제목: 괄호 뒤 조사가 다음 줄로 떨어지지 않게
const band = '<div class="band" aria-hidden="true"></div>';
// 포스터 (04 4절): 자기 도식의 첫 묶음 자리를 줄여 넣는다(meet, 잘림 없음). 안쪽 svg 가 자리 밖을 잘라 낸다
function poster(id) {
  const s = SIM[id], p = s.poster, [x, y, w, h] = p.vb.split(' ');
  return `<svg class="pst${p.fade ? ' fade' : ''}" viewBox="${p.vb}" preserveAspectRatio="xMidYMid meet" aria-hidden="true"><svg x="${x}" y="${y}" width="${w}" height="${h}" viewBox="${p.vb}"><image href="illustrations/${s.fig}.svg" width="390" height="${D.figs[s.fig].h}"/></svg></svg>`;
}
const pAr = id => { const [, , w, h] = SIM[id].poster.vb.split(' ').map(Number); return w / h; };
// 본문 도식 (03 5.4): 위 머리표 줄 42 를 잘라 보인다
const figure = f => `<svg viewBox="0 42 390 ${D.figs[f].h - 42}" role="img" aria-label="${esc(D.figs[f].alt)}"><image href="illustrations/${f}.svg" width="390" height="${D.figs[f].h}"/></svg>`;

// ===== 머리 =====
function hmain(on, title) {
  const t = (k, n) => `<a href="#/${k}" class="t-title2"${on === k ? ' aria-current="page"' : ''}><span>${n}</span></a>`;
  return `<header class="hm"><a href="../" class="r1" aria-label="CS 차곡 소개 페이지로">${MARK}<span class="t-row">CS 차곡</span></a><nav class="r2" aria-label="주요 화면">${t('home', '홈')}${t('toc', '목차')}${t('sims', '시뮬레이션')}<i class="ul" aria-hidden="true"></i></nav></header><div class="sent" data-sent></div>${title ? `<h1 class="sr" tabindex="-1">${title}</h1>` : ''}<div data-notes>${notes(on === 'home')}</div>`;
}
function hsub(k, on, progress = '', cls = '') {
  const t = (r, n) => `<a href="#/${r}" class="t-ui"${on === r ? ' aria-current="page"' : ''}>${n}</a>`;
  return `<header class="hs${cls}"><div class="row1"><button class="ib" data-act="back" aria-label="뒤로">${ic('back')}</button><span class="sub t-ui">${k ? NAMES[k] : ''}</span><nav class="stabs" aria-label="주요 화면">${t('home', '홈')}${t('toc', '목차')}${t('sims', '시뮬레이션')}</nav></div>${progress ? `<div class="prog">${progress}</div>` : ''}</header><div data-notes>${notes(false)}</div>`;
}
// 화면 위 안내 줄 (06 3.4, 5): 오프라인은 모든 화면, 진도 저장 문제는 홈만
let NET = navigator.onLine, OFF = null, noteClosed = false; // OFF: 오프라인 저장 상태 saving | saved | fail (null 이면 브라우저가 지원 안 함)
function notes(home) {
  let h = '';
  if (!NET) h += `<div class="note t-ui" role="status">${ic('wifioff')}<p>${OFF === 'saved' ? '오프라인이에요. 저장된 내용으로 보고 있어요.' : '오프라인이에요. 저장이 끝난 내용만 볼 수 있어요.'}</p></div>`;
  if (home && !noteClosed && STORE !== 'ok') h += `<div class="note t-ui" role="status">${ic('info')}<p>${STORE === 'off' ? '이 브라우저에서는 진도가 저장되지 않아요. 앱을 닫으면 처음 상태로 돌아가요.' : '저장된 진도를 읽지 못해 새로 시작했어요.'}</p><button class="ib" data-act="closeNote" aria-label="안내 닫기">${ic('x')}</button></div>`;
  return h;
}
const repaintNotes = () => app.querySelectorAll('[data-notes]').forEach(n => { n.innerHTML = notes(V && V.kind === 'home'); });

// ===== 홈 (01) =====
function nextUnread(after) {
  const start = after ? ORDER.indexOf(after) + 1 : 0;
  for (let k = 0; k < ORDER.length; k++) { const id = ORDER[(start + k) % ORDER.length]; if (!isRead(id)) return id; }
  return null;
}
function heroState() {
  if (S.read.size === ORDER.length) return { kind: 'done' };
  if (S.last && !isRead(S.last.id)) return { kind: 'resume', id: S.last.id };
  return { kind: S.read.size || S.last ? 'next' : 'first', id: nextUnread(S.last && S.last.id) };
}
function heroCard() {
  const h = heroState();
  if (h.kind === 'done') {
    const nc = S.conf.size, go = nc ? 'toc/conf' : 'toc/star', btn = nc ? '헷갈림만 다시 읽기' : '빈출부터 다시 읽기';
    return `<a href="#/${go}" class="card hero done" data-k="hero" aria-label="40문항을 모두 쌓았어요, ${btn}"><div class="strip">${ill('hero-done')}</div><div class="bd"><p class="t-label c-a">한 바퀴 끝</p><h2 class="t-title2">40문항을 모두 쌓았어요</h2><p class="t-label c-3" style="margin-top:12px">${nc ? `헷갈림 ${nc}문항이 남아 있어요` : '헷갈린 질문 없이 끝냈어요'}</p><span class="btn l pri fake">${btn}</span></div></a>`;
  }
  const q = Q[h.id], n = chunks(q).length, resume = h.kind === 'resume', ch = resume ? S.last.chunk : 0;
  const btn = { resume: '이어 읽기', next: '다음 질문 읽기', first: '첫 질문 읽기' }[h.kind];
  // 위치: 읽던 질문은 `6단락 중 3번째`, 아직 안 읽은 질문은 `5단락 · 안 읽음` (UX 4회차 권장 9, 단락이라는 말은 유지)
  const pos = resume ? `${n}단락 중 ${ch}번째` : `${n}단락 · 안 읽음`;
  return `<a href="#/q/${q.id}" class="card hero" data-ctx="${resume ? 'resume' : 'next'}" data-from="home" data-k="hero" aria-label="${btn}, ${esc(q.title)}, ${pos}"><div class="strip">${ill('hero-' + q.s)}</div><div class="bd"><p class="t-label c-a">${SUB[q.s].name} · ${esc(q.sub)}</p><h2 class="t-title2">${tt(q.title)}</h2><div class="posr">${segs(n, resume ? S.prog[q.id] || ch : 0)}<span class="t-label c-3 num">${pos}</span></div><span class="btn l pri fake">${btn}</span></div></a>`;
}
// 랜덤 (7.2): 바로 전에 나온 질문과 읽던 질문은 빼고, 안 읽은 질문이 두 배 자주
let RND = null;
function pickRandom() {
  const pool = ORDER.filter(id => id !== RND && !(S.last && id === S.last.id));
  const w = pool.flatMap(id => isRead(id) ? [id] : [id, id]);
  return RND = w[Math.floor(Math.random() * w.length)];
}
const rndInner = id => { const q = Q[id]; return `<div class="top"><p class="t-label c-a">${SUB[q.s].name} · ${esc(q.sub)}</p>${starTag(q.stars)}</div><h3 class="t-row">${tt(q.title)}</h3><p class="hid t-label c-3">${ic('eyeoff')}답은 가려져 있어요</p>`; };
let homeSeen = null; // 지난번 홈에서 본 읽음 (새로 읽은 블록만 튀어오름, 9.3)
function homeView(st) {
  if (!st.rnd || !Q[st.rnd]) { st.rnd = pickRandom(); history.replaceState(st, ''); }
  RND = st.rnd;
  const sum = S.read.size, popOf = id => homeSeen && isRead(id) && !homeSeen.has(id) && !reduce() ? ' pop' : '';
  const towers = KEYS.map(k => {
    const ids = stackOrder(k), nc = inSub(k).filter(q => isConf(q.id)).length, r = subRead(k), n = ids.length;
    return `<a href="#/toc/${k}" class="tw" data-k="tw:${k}" aria-label="${SUB[k].name}, ${n}문항 중 ${r}문항 읽음${nc ? `, 헷갈림 ${nc}` : ''}"><span class="stack">${ids.map((id, j) => blockOf(id, popOf(id), j)).join('')}</span>${ill('sym-' + k)}<span class="t-caption">${SUB[k].name}</span><span class="t-label c-3 num">읽음 ${r} / ${n}</span>${nc ? `<span class="t-label cf num">헷갈림 ${nc}</span>` : ''}</a>`;
  }).join('');
  const starIds = [...STARS.filter(id => !isRead(id)), ...STARS.filter(isRead)].slice(0, 3);
  const h = heroState(), lastSims = S.last && h.kind === 'resume' ? Q[S.last.id].sims : [];
  const simId = lastSims.length ? lastSims[0] : 'hash-table', sm = SIM[simId];
  const hasProg = S.read.size || S.conf.size || Object.keys(S.prog).length || S.last;
  return hmain('home', '홈') + `
  <section class="sec" style="padding-top:16px">${heroCard()}</section>${band}
  <section class="sec rnd"><div class="sh"><h2 class="t-head">랜덤 질문</h2><button class="ib" data-act="shuffle" aria-label="다른 질문">${ic('shuffle')}</button></div><a href="#/q/${RND}" class="card" data-ctx="random" data-from="home" data-k="rnd" aria-label="랜덤 질문, ${esc(Q[RND].title)}, 답은 가려져 있어요"><div class="bd swap">${rndInner(RND)}</div></a><span class="sr" role="status" data-live></span></section>${band}
  <section class="sec"><div class="sh"><h2 class="t-head">과목 진도</h2><p class="sum"><span class="t-label c-3">읽음&nbsp;</span><b class="t-display c-a num">${sum}</b><span class="t-label c-3 num">&nbsp;/ ${ORDER.length}</span></p></div><div class="towers" data-towers>${towers}</div>${sum ? '' : '<p class="hint t-ui c-2">질문을 다 읽을 때마다 여기에 한 칸씩 쌓여요</p>'}${S.conf.size ? `<div class="rows revrow"><a href="#/toc/conf" class="row" data-k="rev">${ic('help', 'ri')}<div class="tx"><b>헷갈림 ${S.conf.size}문항 다시 보기</b></div>${ic('right', 'ri')}</a></div>` : ''}</section>${band}
  <section class="sec" style="padding-bottom:16px"><div class="sh"><h2 class="t-head">자주 나온 질문</h2><a href="#/toc/star" class="lnk t-label">전체 ${STARS.length}${ic('right')}</a></div><div class="rows">${starIds.map(id => row(id, 'star', true, { from: 'home' })).join('')}</div></section>${band}
  <section class="sec"><div class="sh"><h2 class="t-head">시뮬레이션</h2></div><a href="#/sim/${simId}" class="card simcard" data-k="sim:${simId}" aria-label="${esc(sm.title)}, ${SUB[sm.s].name}${simStars(sm) ? `, 빈출 별 ${simStars(sm)}개` : ''}"><div class="pf" style="--ar:${Math.max(pAr(simId), 1.6).toFixed(3)}">${poster(simId)}</div><div class="bd"><div class="nm"><b class="t-row">${nw(sm.title)}</b>${starTag(simStars(sm))}</div><p class="t-label c-3" style="margin-top:4px">${SUB[sm.s].name} · ${lastSims.length ? '읽던 질문과 이어져요' : `관련 질문 ${sm.qs.length}`}</p></div></a></section>${band}
  <section class="sec dev" style="padding-bottom:8px"><div class="sh" style="margin-bottom:4px"><h2 class="t-head">이 기기에 저장</h2></div><div class="rows">
    ${OFF ? `<div class="row static">${ic('cloud', 'ri')}<div class="tx"><b>오프라인 저장</b><p class="meta t-label">인터넷 없이도 본문과 시뮬레이션을 봐요</p></div><span data-off>${offSt()}</span></div>` : ''}
    <button class="row${hasProg ? '' : ' off'}" data-act="reset" data-k="reset" style="width:100%;text-align:left"${hasProg ? '' : ' disabled'}>${ic('restore', 'ri')}<div class="tx"><b>진도 초기화</b><p class="meta t-label num">${hasProg ? (S.read.size === ORDER.length ? '처음부터 다시 하려면 진도를 초기화해 주세요' : `읽음 ${S.read.size} · 헷갈림 ${S.conf.size}`) : '지울 진도가 없어요'}</p></div></button>
  </div></section><div class="tail-space"></div>`;
}
const offSt = () => ({ saved: `<span class="st t-label c-a">${ic('check')}저장됨</span>`, saving: '<span class="st t-label c-3">저장하는 중</span>', fail: '<button class="st t-label lnk" data-act="offRetry">다시 시도</button>' })[OFF];
function row(id, ctx, showSub, o = {}) {
  const q = Q[id], reading = S.last && S.last.id === id && !isRead(id) && ctx === 'book';
  const words = [showSub ? SUB[q.s].name : '', q.tails.length ? `꼬리질문 ${q.tails.length}` : ''].filter(Boolean).join(' · ');
  const meta = [reading ? '<span class="t-caption c-a">읽던 곳</span>' : '', o.noStar ? '' : starTag(q.stars), ctx !== 'conf' && isConf(id) ? confTag() : '', words ? `<span>${words}</span>` : ''].filter(Boolean);
  return `<a href="#/q/${id}" class="row${reading ? ' reading' : ''}" data-ctx="${reading ? 'resume' : ctx}"${o.from ? ` data-from="${o.from}"` : ''}${o.sim ? ` data-sim="${o.sim}"` : ''} data-k="q:${id}">${glyph(id)}<div class="tx"><b>${tt(q.title)}</b>${meta.length ? `<p class="meta t-label">${meta.join('')}</p>` : ''}</div></a>`;
}

// ===== 목차 (02) =====
// 분할 선택: 이름 + 개수. 폭 340 미만에서는 이름 / 개수 두 줄이고 `헷갈림만` 의 `만` 은 숨긴다(UX 4회차 필수 1)
function segc(items, sel, act) {
  const si = Math.max(0, items.findIndex(([k]) => k === sel));
  return `<div class="segc" role="tablist" style="--n:${items.length}">${items.map(([k, label]) => `<button role="tab" class="t-ui num" aria-selected="${k === sel}" tabindex="${k === sel ? 0 : -1}" data-act="${act}" data-v="${esc(k)}">${label}</button>`).join('')}<i class="th" style="--i:${si}" aria-hidden="true"></i></div>`;
}
const chHead = (k, right, extra = '') => `<div class="ch" id="ch-${k}"><div class="l1">${ill('sym-' + k)}<div class="nm"><h2 class="t-title2" tabindex="-1">${SUB[k].name}</h2>${extra}</div><span class="t-label c-3 num">${right}</span></div>`;
const jumpNav = cur => `<nav class="jump" aria-label="장 이동">${KEYS.map(k => `<a href="#/${V_JUMP}/${k}" class="t-ui" data-act="jump" data-k="${k}"${k === cur ? ' aria-current="location"' : ''}>${NAMES[k]}</a>`).join('')}</nav>`;
let V_JUMP = 'toc';
function tocView(view, k) {
  const nc = S.conf.size;
  V_JUMP = 'toc';
  let h = hmain('toc', '목차') + `<div class="segbar">${segc([['all', `전체 <span class="n">${ORDER.length}</span>`], ['star', `빈출 <span class="n">${STARS.length}</span>`], ['conf', `헷갈림<span class="w">만</span>${nc ? ` <span class="n">${nc}</span>` : ''}`]], view, 'tocview')}</div>`;
  if (view === 'all') {
    h += jumpNav(k || 'ds') + '<div role="tabpanel" data-panel>';
    KEYS.forEach((s, ki) => {
      const nck = inSub(s).filter(q => isConf(q.id)).length;
      h += `${ki ? band : ''}<section data-ch="${s}">${chHead(s, `읽음 ${subRead(s)} / ${inSub(s).length}`, nck ? confTag('헷갈림 ' + nck) : '')}<div class="brow" aria-hidden="true">${stackOrder(s).map(id => blockOf(id)).join('')}</div></div>`;
      SUB[s].subs.forEach(sb => {
        const qs = inSub(s).filter(q => q.sub === sb);
        h += `<p class="topic t-label">${esc(sb)} · ${qs.length}</p>${qs.map(q => row(q.id, 'book')).join('')}`;
      });
      h += '</section>';
    });
    h += '</div>';
  } else if (view === 'star') {
    // 별 무리로 나눈 보기라 행마다 별 꼬리표를 다시 달지 않는다
    h += '<div role="tabpanel" data-panel>';
    [4, 2, 1].forEach(n => {
      const ids = STARS.filter(id => Q[id].stars === n);
      h += `<div class="grp">${starTag(n)}<span class="t-label c-3">${ids.length}문항</span></div>${ids.map(id => row(id, 'star', true, { noStar: 1, from: 'toc' })).join('')}`;
    });
    h += `<div class="endnote"><p class="t-ui">별이 없는 ${ORDER.length - STARS.length}문항은 전체에서 볼 수 있어요</p><button class="lnk t-ui" data-act="tocview" data-v="all">전체 보기</button></div></div>`;
  } else {
    const ids = ORDER.filter(isConf);
    if (!ids.length) {
      const cleared = S.everConf;
      h += `<div role="tabpanel" class="empty" data-panel>${ill('ill-empty-conf')}<h2 class="t-title2">${cleared ? '헷갈림을 모두 풀었어요' : '헷갈리는 질문이 없어요'}</h2><p class="t-ui c-2">${cleared ? '다시 볼 질문이 생기면 여기에 모여요' : '읽다가 헷갈리면 질문 아래 헷갈려요를 눌러 두세요'}</p><button class="btn sec" data-act="tocview" data-v="star">빈출 ${STARS.length} 보기</button></div>`;
    } else {
      h += `<div role="tabpanel" data-panel><div class="confsum"><p class="sum"><b class="t-display num">${ids.length}</b><span class="t-label c-3">문항</span></p><p class="t-ui c-2">이해했다면 질문 아래에서 헷갈림을 꺼 주세요</p><a href="#/q/${ids[0]}" class="btn l pri" data-ctx="conf" data-k="confgo">첫 문항부터 다시 읽기</a></div><div>${ids.map(id => row(id, 'conf', true)).join('')}</div></div>`;
    }
  }
  return h + '<div class="tail-space"></div>';
}

// ===== 질문 (03) =====
const TAB = { random: 'home', next: 'home', sim: 'sims' }; // 머리의 켜진 탭 = 뒤로 목적지 (00 7.2)
function ctxOf(kind, id, from) {
  const c = { kind, from: from || TAB[kind] || 'toc' };
  if (kind === 'conf') { const l = ORDER.filter(isConf); c.list = l.includes(id) ? l : [...l, id].sort((a, b) => Q[a].i - Q[b].i); }
  return c;
}
const ctxList = c => c.kind === 'star' ? STARS : c.kind === 'conf' ? c.list : c.kind === 'random' ? [] : ORDER;
// 위치는 분수 대신 `N개 중 k번째` (분수는 읽은 수에만, 00 12절)
function posText(q, c) {
  if (c.kind === 'random') return '';
  if (c.kind === 'star') return `빈출 ${STARS.length}개 중 ${STARS.indexOf(q.id) + 1}번째`;
  if (c.kind === 'conf') return `헷갈림 ${c.list.length}개 중 ${c.list.indexOf(q.id) + 1}번째`;
  return `${inSub(q.s).length}개 중 ${inSub(q.s).indexOf(q) + 1}번째`;
}
// 핵심 첫 문장 형광펜 (00 5.6): 첫 문단 글에서 처음 나오는 `. ` 까지, 태그를 넘어 DOM 범위로 <mark>
function firstSentence(html) {
  const t = document.createElement('template'); t.innerHTML = html;
  const p = t.content.querySelector('p'); if (!p) return html;
  const w = document.createTreeWalker(p, NodeFilter.SHOW_TEXT);
  for (let n; (n = w.nextNode());) {
    const m = /\.(?=\s|$)/.exec(n.data); if (!m) continue;
    const r = document.createRange(), mk = document.createElement('mark');
    r.setStart(p, 0); r.setEnd(n, m.index + 1); mk.appendChild(r.extractContents()); p.prepend(mk);
    return t.innerHTML;
  }
  return html;
}
// 본문 도식 자리(build.py) → 도식 + 바로 아래 시뮬레이션 입구
const renderFigs = html => html.replace(/<figure class="fig" data-fig="([\w-]+)" data-sim="([\w-]*)"><\/figure>/g, (_, f, sid) => `<figure class="fig">${figure(f)}</figure>${SIM[sid] ? `<a href="#/sim/${sid}" class="simgo" data-simgo="${sid}" data-k="go:${sid}"><span class="pv">${poster(sid)}</span><span class="tx"><b>시뮬레이션으로 보기</b><span class="t-label c-2">${nw(SIM[sid].title)}</span></span>${ic('right')}</a>` : ''}`);
const leftText = (n, cur, end, open) => !open ? `${n}단락` : end ? '끝까지 왔어요' : cur >= n ? '마지막 단락' : `남은 ${n - cur}단락`;
function qView(id, c, o) {
  const q = Q[id], cs = chunks(q), n = cs.length, pos = posText(q, c), long = q.title.length > 40;
  const pg = `${segs(n, 0, o.open)}<span class="left t-caption num" data-left>${leftText(n, 1, false, o.open)}</span>`;
  let h = hsub(q.s, c.from, pg) + `
  <div class="qh"><div class="top"><p class="l"><span class="t-label c-a">${esc(q.sub)}</span></p>${pos ? `<span class="t-label c-3 num" style="white-space:nowrap">${pos}</span>` : ''}</div>
  <h1 class="${long ? 't-title2' : 't-title1'}" tabindex="-1">${tt(q.title)}</h1><p class="info t-label c-3">${starTag(q.stars)}<span>약 ${minutes(q)}분${q.tails.length ? ` · 꼬리질문 ${q.tails.length}` : ''}</span></p></div>`;
  if (!o.open) {
    // 답 자리: 판이 막대 위까지 늘어나 문제 카드 앞면처럼 선다. 과목 기호만, 답 글은 없음 (00 7.5)
    h += `<div class="recall"><div class="mid">${ill('sym-' + q.s)}<h2 class="t-head">먼저 떠올려 보세요</h2><p class="t-ui c-2">${S.seen.recallTip ? '핵심을 한두 문장으로 정리해 본 뒤 답을 열어 보세요.' : '답은 가려 뒀어요. 핵심을 한두 문장으로 떠올린 뒤 열어 보세요.'}</p></div><button class="btn l pri" data-act="reveal" aria-expanded="false" aria-controls="ans">${ic('eye')}답 보기</button></div>`;
  } else {
    const here = i => o.mark === i + 1 ? ' <span class="tag here here-in" data-here>멈춘 곳</span>' : '';
    h += `<div class="ans${o.anim ? ' in' : ''}" id="ans"><div class="prose">`;
    cs.forEach((ch, i) => {
      if (ch.core) h += `<div class="chunk" data-c="${i}" style="view-timeline-name:--c${i}"><div class="coreh"><span class="t-label c-a">핵심</span><button class="lnk t-ui" data-act="hide">다시 가리기</button></div><div class="t-core c-ink" tabindex="-1" data-core>${firstSentence(q.core)}</div></div>`;
      else if (!ch.tails) h += `<div class="chunk${ch.t ? '' : ' intro'}" data-c="${i}" style="view-timeline-name:--c${i}">${ch.t ? `<h3>${ch.t}${here(i)}</h3>` : (here(i) ? `<p class="t-label">${here(i)}</p>` : '')}${renderFigs(ch.html)}</div>`;
    });
    h += '</div></div>';
    if (q.tails.length) {
      const i = n - 1, open = new Set(o.tails || []);
      h += `${band}<section class="tails chunk" data-c="${i}" style="view-timeline-name:--c${i}"><h2 class="t-head">꼬리질문 ${q.tails.length}${here(i)}</h2>${q.tails.map((t, j) => `<button class="tq t-row" data-act="tail" data-j="${j}" aria-expanded="${open.has(j)}"><span>${esc(t.q)}</span>${ic('down')}</button>${open.has(j) ? tailAns(q, j) : ''}`).join('')}</section>`;
    }
    h += band + endZone(q, { book: ctxList(c) === ORDER });
  }
  const list = ctxList(c), k = list.indexOf(id), prev = k > 0 ? list[k - 1] : null, next = k >= 0 && k < list.length - 1 ? list[k + 1] : null;
  const nextLabel = c.kind === 'random' ? '다른 질문' : next ? '다음 질문' : (c.kind === 'star' || c.kind === 'conf' ? '목록으로' : '목차로');
  const endGo = c.kind === 'star' ? (c.from === 'home' ? 'home' : 'toc/star') : c.kind === 'conf' ? 'toc/conf' : 'toc';
  const cls = `btn ${o.open ? 'pri' : 'sec'} grow2`;
  const nextBtn = c.kind === 'random' ? `<button class="${cls}" data-act="another">${nextLabel}${ic('next')}</button>`
    : next ? `<a href="#/q/${next}" class="${cls}" data-ctx="keep" data-replace>${nextLabel}${ic('next')}</a>` : `<a href="#/${endGo}" class="${cls}" data-replace>${nextLabel}</a>`;
  const prevBtn = c.kind === 'random' ? '' : prev ? `<a href="#/q/${prev}" class="btn sec ico" data-ctx="keep" data-replace aria-label="이전 질문">${ic('prev')}</a>` : `<button class="btn sec ico" aria-label="이전 질문" disabled>${ic('prev')}</button>`;
  const bar = `<div class="bar" data-bar>${prevBtn}${confBtn(id)}${nextBtn}</div>`;
  return { html: h + '<div class="tail-space"></div>', bar, cls: 'has-bar' + (o.open ? '' : ' qflex') };
}
const confBtn = id => `<button class="btn sec grow cfb" data-act="conf" aria-pressed="${isConf(id)}" aria-label="헷갈림 표시">${ic(isConf(id) ? 'check' : 'help')}<span class="lbl">헷갈려요</span></button>`;
const tailAns = (q, j) => `<div class="ta prose">${renderFigs(q.tails[j].a)}</div>`;
// 끝 영역 (03 5.6). 결과 글 줄(.l2)은 aria-live 로 남겨 두고 안만 바꾼다
function endZone(q, o) {
  return `<section class="endz" data-end><div class="l1">${endBlocks(q, o)}</div><div class="l2" data-msg aria-live="polite">${endMsg(q, o)}</div>${endNotes(q, o)}</section>`;
}
const endBlocks = (q, o) => `<div class="brow" style="flex:1">${stackOrder(q.s).map(id => blockOf(id, o.justRead === id && !reduce() ? ' pop' : '')).join('')}</div><span class="t-label c-3 num">읽음 ${subRead(q.s)} / ${inSub(q.s).length}</span>`;
function endMsg(q, o) {
  if (isRead(q.id)) return `<p class="t-head">${o.justRead ? `${SUB[q.s].name}에 한 칸 쌓였어요` : '읽은 질문이에요'}</p><button class="lnk t-ui" data-act="unread">읽음 취소</button>`;
  // 읽음 취소 뒤에는 이 열람 동안 자동으로 다시 쌓지 않는다 (UX 4회차 필수 2)
  return `<p class="t-ui c-2">${o.canceled ? '직접 표시하기 전에는 쌓이지 않아요' : '아직 쌓이지 않았어요'}</p><button class="lnk t-ui on" data-act="markRead">읽음으로 표시</button>`;
}
function endNotes(q, o) {
  const nx = ORDER[ORDER.indexOf(q.id) + 1], cross = o.book && nx && Q[nx].s !== q.s;
  return (o.justRead && o.first ? '<p class="t-label c-3">홈의 과목 진도에도 쌓여요</p>' : '') + (cross ? `<p class="t-label c-3">${SUB[q.s].name}의 마지막 질문이에요. 다음은 ${SUB[Q[nx].s].name}예요</p>` : '');
}
function endRedraw(o = {}, focus) {
  const end = app.querySelector('[data-end]'); if (!end || !V || V.kind !== 'q') return;
  const q = Q[V.id];
  o.book = ctxList(V.ctx) === ORDER;
  end.querySelector('.l1').innerHTML = endBlocks(q, o);
  end.querySelector('[data-msg]').innerHTML = endMsg(q, o);
  end.querySelectorAll(':scope > .t-label').forEach(x => x.remove());
  end.insertAdjacentHTML('beforeend', endNotes(q, o));
  contSegs();
  if (focus) end.querySelector('[data-msg] button').focus({ preventScroll: true });
}

// ===== 시뮬레이션 목록 (04), 시뮬레이션 (05) =====
function simsView(k) {
  V_JUMP = 'sims';
  let h = hmain('sims', '시뮬레이션') + jumpNav(k || 'ds');
  KEYS.forEach((s, i) => {
    const ss = D.sims.filter(x => x.s === s);
    h += `${i ? band : ''}<section data-ch="${s}">${chHead(s, `${ss.length}개`)}</div><div class="simgrid">${ss.map(x => `<a href="#/sim/${x.id}" class="simc" data-k="sim:${x.id}" aria-label="${esc(x.title)}, ${SUB[s].name}${simStars(x) ? `, 빈출 별 ${simStars(x)}개` : ''}"><div class="pf">${poster(x.id)}</div><p class="t-row">${nw(x.title)}</p>${starTag(simStars(x))}</a>`).join('')}</div></section>`;
  });
  return h + '<div class="tail-space"></div>';
}
function simView(id, st) {
  const s = SIM[id], sub = Q[s.qs[0]].sub, qs = s.qs;
  const rel = `${band}<section class="related"><h2 class="t-head">관련 질문 ${qs.length}</h2>${qs.map(x => row(x, 'sim', true, { sim: id })).join('')}</section><div class="tail-space"></div>`;
  const head = hsub(s.s, 'sims', '', ' flow') + `<div class="simh"><p class="t-label c-a">${esc(sub)}</p><h1 class="t-title2" tabindex="-1">${nw(s.title)}</h1><div data-modes></div></div>`;
  if (st.fig) return { html: head + `<div class="stage figv">${figure(s.fig)}</div>` + rel, bar: `<div class="bar" data-bar><button class="btn pri grow" data-act="sim" data-k="toq">글로 읽기${ic('next')}</button></div>`, cls: 'has-bar' };
  const stage = `<div class="stage" data-stage style="--ar:${(390 / (D.figs[s.fig].h - 42)).toFixed(3)}"><iframe title="${esc(s.title)} 시뮬레이션" src="sims/${id}/index.html?embed=1" data-sim="${id}"></iframe><div class="msg" data-ld hidden><p class="t-ui c-2">시뮬레이션을 불러오는 중</p></div></div>`;
  const capflow = '<div class="capflow" data-capflow><span class="tag here" data-ctag hidden>직접 넣은 값</span><p class="t-ui" aria-live="polite" data-capf></p><button class="lnk t-ui" data-act="sim" data-k="try" hidden>직접 해 보기</button></div>';
  const bar = `<div class="bar simbar" data-bar data-simbar><div class="st1"><span class="seg" data-segs></span><span class="t-label c-3 num" data-count></span><span class="tag here" data-tag hidden>직접 넣은 값</span><button class="lnk t-label" data-act="sim" data-k="try" data-try hidden>직접 해 보기</button></div><p class="cap t-read" data-cap aria-live="polite">&nbsp;</p><div class="bts"><button class="btn sec ico" data-act="sim" data-k="prev" aria-label="이전 단계" disabled>${ic('prev')}</button><button class="btn sec ico" data-act="sim" data-k="play" aria-label="재생">${ic('play')}</button><button class="btn pri grow" data-act="sim" data-k="next">다음${ic('next')}</button></div></div>`;
  return { html: head + capflow + stage + rel, bar, cls: 'has-bar' };
}
function simFail(id) {
  const st = app.querySelector('[data-stage]'); if (!st) return;
  st.outerHTML = `<div class="stage" style="height:262px"><div class="msg"><p class="t-row">시뮬레이션을 열지 못했어요</p><p class="t-ui c-2">${!NET && OFF !== 'saved' ? '오프라인 저장이 끝나기 전이라 아직 열 수 없어요' : '인터넷 연결을 확인하고 다시 시도해 주세요'}</p><div class="acts"><button class="btn sec" data-act="simRetry">다시 시도</button><button class="lnk t-ui" data-act="simFig">그림으로 보기</button></div></div></div>`;
  app.querySelector('[data-bar]').remove(); app.querySelector('[data-capflow]').remove(); app.className = '';
  setBarH();
}

// ===== 상태 화면 (06) =====
function notFound(kind) {
  const sim = kind === 'sim';
  return { html: hsub(null, sim ? 'sims' : 'toc') + `<div class="empty">${ill('ill-notfound')}<h1 class="t-title2" tabindex="-1">${sim ? '찾는 시뮬레이션이 없어요' : '찾는 질문이 없어요'}</h1><p class="t-ui c-2">주소가 바뀌었을 수 있어요</p><a href="#/${sim ? 'sims' : 'toc'}" class="btn l pri" data-replace style="margin-top:32px">${sim ? '시뮬레이션 목록으로' : '목차로'}</a></div>`, title: sim ? '찾는 시뮬레이션이 없어요' : '찾는 질문이 없어요' };
}
// 불러오는 중 자리 모양 (06 3.1): 회색 면만, 움직이지 않음. 400ms 안에 끝나면 그리지 않는다
const loadingHome = () => hmain('home') + `<section class="sec" style="padding-top:16px" aria-busy="true"><div class="card"><div style="height:120px;background:var(--stage)"></div><div class="bd"><div class="ph" style="height:14px;width:42%"></div><div class="ph" style="height:22px;width:88%;margin-top:12px"></div><div class="ph" style="height:22px;width:56%;margin-top:8px"></div><div class="ph" style="height:56px;border-radius:14px;margin-top:24px"></div></div></div></section>${band}<section class="sec"><div class="ph" style="height:20px;width:30%"></div><div class="ph" style="height:120px;border-radius:16px;margin-top:16px"></div></section><span class="sr" role="status">불러오는 중</span>`;
const loadingQ = () => hsub(null, 'toc', segs(5, 0)) + '<div class="qh" aria-busy="true"><div class="ph" style="height:14px;width:36%"></div><div class="ph" style="height:24px;width:84%;margin-top:16px"></div><div class="ph" style="height:14px;width:28%;margin-top:16px"></div></div><span class="sr" role="status">불러오는 중</span>';
const loadingSims = () => hmain('sims') + `<nav class="jump" aria-label="장 이동">${KEYS.map((k, i) => `<a class="t-ui"${i ? '' : ' aria-current="location"'}>${NAMES[k]}</a>`).join('')}</nav><div class="ch"><div class="l1">${ill('sym-ds')}<div class="nm"><h2 class="t-title2">${NAMES.ds}</h2></div></div></div><div class="simgrid" aria-busy="true">${Array.from({ length: 6 }, () => '<div class="simc"><div class="pf"></div><div class="ph" style="height:16px;width:80%;margin-top:12px"></div><div class="ph" style="height:16px;width:48%;margin-top:8px"></div></div>').join('')}</div><span class="sr" role="status">불러오는 중</span>`;
// 못 불러옴: 오프라인·연결 실패는 구름 그림 ill-offline (없는 주소는 ill-notfound, 4회차 지적)
const loadFail = q => (q ? hsub(null, 'toc') : hmain('home')) + `<div class="empty">${ill('ill-offline')}<h1 class="t-title2" tabindex="-1">${q ? '질문을 불러오지 못했어요' : '내용을 불러오지 못했어요'}</h1><p class="t-ui c-2">${NET ? '인터넷 연결을 확인하고 다시 시도해 주세요' : '인터넷에 연결되면 처음 한 번 내용을 받아 와요'}</p><button class="btn l pri" data-act="retry" style="margin-top:32px">다시 시도</button></div>`;
const sheetHtml = () => `<div class="scrim" data-act="closeSheet"></div><div class="sheet" role="dialog" aria-modal="true" aria-labelledby="shT"><h2 class="t-title2" id="shT" tabindex="-1">진도를 처음부터 다시 할까요?</h2><p class="t-ui c-2">읽음 ${S.read.size}문항, 헷갈림 ${S.conf.size}문항, 이어 읽기 위치가 모두 지워져요.</p><div class="bts"><button class="btn sec" data-act="closeSheet">취소</button><button class="btn del" data-act="doReset">초기화</button></div></div>`;

// ===== 이동 (00 7절): 주소 hash 가 화면, 맥락·스크롤·펼침은 기록 칸(history.state)에 =====
// 기록 칸: { d: 앱 안 깊이, k: 칸 표시, y: 스크롤, focus: 들어갈 때 누른 것, ctx: 질문 맥락, open/tails: 답 펼침, sim: 시뮬레이션 단계, fromQ, rnd, fig }
let depth = 0, V = null, lastK = null;
const uid = () => Date.now().toString(36) + Math.random().toString(36).slice(2, 6);
const routeOf = () => location.hash.replace(/^#\/?/, '') || 'home';
// 떠나는 칸에 스크롤·누른 것·화면 속 상태를 남긴다 (뒤로 오면 되살림)
function saveHere(key) {
  const st = { ...history.state, y: scrollY, focus: key || null };
  if (V && V.kind === 'q') { st.open = V.open; st.tails = [...app.querySelectorAll('.tq[aria-expanded="true"]')].map(b => +b.dataset.j); }
  if (V && V.kind === 'sim' && V.sim) {
    const s = V.sim.state(), form = V.doc.querySelector('form.sim-try');
    st.sim = { mode: s.mode, step: s.i, tried: s.tried, vals: s.tried && form ? [...form.elements].filter(x => x.name).map(x => x.value) : null };
  }
  history.replaceState(st, '');
}
function go(route, extra = {}, replace = false, key) {
  if (!replace) saveHere(key);
  const st = { ...extra, d: replace ? depth : depth + 1, k: uid() };
  history[replace ? 'replaceState' : 'pushState'](st, '', '#/' + route);
  depth = st.d;
  render(true);
}
// 링크 누름: 질문이면 맥락을 붙이고, 시뮬레이션에서 그 질문으로 돌아가는 것이면 뒤로 (00 7.3)
function follow(a) {
  const route = a.getAttribute('href').slice(2), [r, id] = route.split('/'), extra = {};
  if (route === routeOf() && !a.hasAttribute('data-replace')) { scrollTo({ top: 0, behavior: reduce() ? 'auto' : 'smooth' }); return; }
  if (r === 'q') {
    const kind = a.dataset.ctx || 'book';
    if (kind === 'keep') extra.ctx = { ...V.ctx, kind: ['resume', 'next', 'sim'].includes(V.ctx.kind) ? 'book' : V.ctx.kind, sim: undefined };
    else extra.ctx = ctxOf(kind, id, a.dataset.from || (V && V.kind === 'home' ? 'home' : V && V.kind === 'sim' ? 'sims' : 'toc'));
    if (kind === 'sim') { extra.ctx.sim = a.dataset.sim; if (V.fromQ === id && depth > 0) { history.back(); return; } }
  }
  if (r === 'sim' && V && V.kind === 'q') extra.fromQ = V.id;
  go(route, extra, a.hasAttribute('data-replace'), a.dataset.k);
}
// 뒤로 버튼: 앱 안 깊이가 있으면 기록 뒤로, 주소로 바로 들어왔으면 위 화면으로 바꿔 끼움
function parentOf() {
  if (!V) return 'home';
  if (V.kind === 'q') { const c = V.ctx; return c.kind === 'sim' && c.sim ? `sim/${c.sim}` : c.kind === 'conf' ? 'toc/conf' : c.kind === 'star' && c.from === 'toc' ? 'toc/star' : c.from === 'home' ? 'home' : 'toc'; }
  return V.kind === 'sim' || V.kind === 'nosim' ? 'sims' : 'toc';
}
function onNav() {
  if (!D) return;
  if (!history.state || !history.state.k) history.replaceState({ ...history.state, d: depth + 1, k: uid() }, '');
  if (history.state.k === lastK) return;
  depth = history.state.d;
  render(true);
}
addEventListener('popstate', onNav);
addEventListener('hashchange', onNav);

// 떠나는 화면 정리: 관찰자, 시간, 읽던 위치 저장
function leave() {
  if (!V) return;
  if (V.kind === 'q') saveLast();
  if (V.kind === 'home') { homeSeen = new Set(S.read); undoBox = null; }
  if (V.kind === 'sim' && V.sim) try { V.sim.play(false); V.sim.onShow = null; } catch (e) {}
  (V.io || []).forEach(o => o.disconnect()); (V.tm || []).forEach(clearTimeout);
  V = null;
}
// 바꿔 끼우는 주소: 옛 앱의 #/random, #/review, #/q/<id>/resume
function redirect(route, extra) { history.replaceState({ ...history.state, ...extra }, '', '#/' + route); render(true); }
function render(nav) {
  leave();
  const st = history.state || {};
  lastK = st.k;
  const [r, a, b] = routeOf().split('/');
  if (r === 'random') return redirect(`q/${pickRandom()}`, { ctx: ctxOf('random') });
  if (r === 'review') return redirect('toc/conf');
  if (r === 'q' && b === 'resume') return redirect(`q/${a}`, { ctx: ctxOf(S.last && S.last.id === a ? 'resume' : 'book', a, 'home') });
  document.querySelectorAll('.toast,.scrim,.sheet').forEach(x => x.remove()); clearTimeout(toastT);
  let v, title;
  V = { kind: r, io: [], tm: [] };
  if (r === 'toc') { const view = ['star', 'conf'].includes(a) ? a : 'all'; v = { html: tocView(view, KEYS.includes(a) ? a : null) }; title = '목차'; V.chap = KEYS.includes(a) ? a : null; }
  else if (r === 'sims') { v = { html: simsView(KEYS.includes(a) ? a : null) }; title = '시뮬레이션'; V.chap = KEYS.includes(a) ? a : null; }
  else if (r === 'q' && Q[a]) {
    const c = st.ctx && st.ctx.kind ? st.ctx : ctxOf('book', a);
    if (c.kind === 'conf' && !c.list) c.list = ORDER.filter(isConf);
    const resume = c.kind === 'resume' && S.last && S.last.id === a && !isRead(a);
    const open = !!(resume || c.kind === 'sim' || st.open);
    Object.assign(V, { id: a, ctx: c, open, t0: Date.now(), cur: 1, mark: resume ? S.last.chunk : 0 });
    v = qView(a, c, { open, tails: st.tails, mark: V.mark });
    title = Q[a].title;
  }
  else if (r === 'sim' && SIM[a]) { Object.assign(V, { id: a, fromQ: st.fromQ }); v = simView(a, st); title = SIM[a].title; }
  else if (r === 'q' || r === 'sim') { V.kind = r === 'sim' ? 'nosim' : 'noq'; v = notFound(r); title = v.title; }
  else { if (r !== 'home') history.replaceState(st, '', '#/home'); V.kind = 'home'; v = { html: homeView(st) }; title = 'CS 차곡'; }
  document.title = title === 'CS 차곡' ? title : `${title} · CS 차곡`;
  app.className = v.cls || '';
  app.innerHTML = v.html + (v.bar || '');
  setBarH();
  wire(st);
  settle(st, nav);
}
// 스크롤과 초점 (7.4): 뒤로 오면 그때 자리와 누른 것, 새 화면이면 맨 위(또는 맞는 자리)와 제목
function settle(st, nav) {
  const focusEl = st.focus && app.querySelector(`[data-k="${CSS.escape(st.focus)}"]`);
  const back = st.y != null;
  const place = () => {
    if (back) scrollTo(0, st.y);
    else if (V.kind === 'q' && V.mark) toChunk(V.mark);
    else if (V.kind === 'q' && V.ctx.kind === 'sim') { const g = app.querySelector(`[data-simgo="${V.ctx.sim}"]`); g ? scrollTo(0, g.previousElementSibling.getBoundingClientRect().top + scrollY - headBottom() - 12) : scrollTo(0, 0); }
    else if (V.chap) scrollTo(0, chapY(V.chap));
    else scrollTo(0, 0);
  };
  place();
  if (V.kind === 'q' && (V.mark || V.ctx.kind === 'sim') && !back) document.fonts.ready.then(() => { if (V && V.kind === 'q') place(); }); // 글꼴이 늦게 와 위치가 밀리는 것 방지
  if (!nav) return;
  const firstUnread = V.chap && V.kind === 'toc' && !back && [...app.querySelectorAll(`[data-ch="${V.chap}"] .row`)].find(r => !r.querySelector('.gl.done'));
  (focusEl || firstUnread || app.querySelector('h1[tabindex]')).focus({ preventScroll: true });
}
const headBottom = () => { const h = app.querySelector('.hs'); return h && getComputedStyle(h).position === 'sticky' ? h.getBoundingClientRect().bottom - h.getBoundingClientRect().top : 0; };
const stickTop = () => { const j = app.querySelector('.jump'); return j ? parseFloat(getComputedStyle(j).top) + j.offsetHeight : 48; };
const chapY = k => { const t = app.querySelector('#ch-' + k); return t ? t.getBoundingClientRect().top + scrollY - stickTop() : 0; };
function toChunk(n) {
  // 저장된 단락이 지금 단락 수보다 크거나 문단을 못 찾으면(내용 갱신) 핵심으로 (6.4)
  const c = app.querySelector(`[data-c="${n - 1}"]`), para = S.last && S.last.para;
  const ok = c && (!para || c.textContent.replace(/\s+/g, ' ').includes(para.replace(/\s+/g, ' ')));
  const t = ok ? c : app.querySelector('[data-c="0"]');
  if (t) scrollTo(0, t.getBoundingClientRect().top + scrollY - headBottom() - 12);
}

// 화면마다 관찰자 달기: 머리 접힘, 지금 장, 질문 진행과 읽음 판정, 시뮬레이션
function wire(st) {
  const io = (fn, opt, els) => { const o = new IntersectionObserver(fn, opt); [].concat(els).forEach(e => e && o.observe(e)); V.io.push(o); return o; };
  const sent = app.querySelector('[data-sent]'), hm = app.querySelector('.hm');
  if (sent && hm) io(es => hm.classList.toggle('cl', !es[0].isIntersecting), { rootMargin: '-12px 0px 0px 0px' }, sent);
  placeLines(false);
  contSegs();
  const jump = app.querySelector('.jump');
  if (jump) {
    io(es => es.forEach(e => { if (e.isIntersecting) jump.querySelectorAll('a').forEach(a => a.toggleAttribute('aria-current', a.dataset.k === e.target.dataset.ch)); }), { rootMargin: '-35% 0px -64% 0px' }, [...app.querySelectorAll('[data-ch]')]);
    // 장 이동 줄이 넘치면 가려진 쪽 끝을 흐린다
    const links = jump.querySelectorAll('a');
    io(es => es.forEach(e => jump.classList.toggle(e.target === links[0] ? 'fl' : 'fr', e.intersectionRatio < .99)), { root: jump, threshold: [.99] }, [links[0], links[links.length - 1]]);
  }
  if (V.kind === 'home') wireHome();
  if (V.kind === 'q') wireQ();
  if (V.kind === 'sim') wireSim(st);
}
function wireHome() {
  // 과목 탑 첫 등장(세션 1번, 50% 보일 때) 블록이 아래부터 쌓임
  const tw = app.querySelector('[data-towers]');
  if (!homeSeen && tw && !reduce()) { const o = new IntersectionObserver(es => { if (es[0].intersectionRatio >= .5) { tw.classList.add('stackin'); o.disconnect(); } }, { threshold: [.5] }); o.observe(tw); V.io.push(o); }
  if (!homeSeen) homeSeen = new Set(S.read);
}
function wireQ() {
  const q = Q[V.id], n = chunks(q).length;
  if (!V.open) return;
  const seg = app.querySelector('.seg.live'), left = app.querySelector('[data-left]'), end = app.querySelector('[data-end]');
  const fill = () => { if (!SCROLL_TL && seg) seg.querySelectorAll('i b').forEach((b, i) => b.style.setProperty('--f', i < V.cur ? 1 : 0)); left.textContent = leftText(n, V.cur, V.endIn, true); };
  // 지금 단락 = 읽기 선(보이는 높이의 35%)을 지나는 단락. prog 는 닿은 가장 큰 단락 (6.2)
  const chunkEls = [...app.querySelectorAll('[data-c]')];
  // 읽기 선을 단락 윗변이 지날 때마다 다시 센다: 지금 단락 = 윗변이 선 위로 올라간 단락 수 (핵심은 늘 1)
  const o = new IntersectionObserver(() => {
    const line = innerHeight * .35;
    V.cur = Math.max(1, chunkEls.filter(c => c.getBoundingClientRect().top < line).length);
    reach(V.cur); fill(); saveLast();
  }, { rootMargin: '-35% 0px -64% 0px' });
  chunkEls.forEach(c => o.observe(c)); V.io.push(o);
  // 끝 영역: 보이면 진행 칸을 모두 채우고, 50% 이상 보이고 시간이 차면 읽음 (6.3)
  const need = Math.max(10000, chars(q) / 500 * 60000 * .3); // 예상 시간의 30%, 최소 10초
  let tm = null;
  const oe = new IntersectionObserver(es => {
    const e = es[0];
    V.endIn = e.isIntersecting;
    if (seg) seg.classList.toggle('full', e.isIntersecting);
    if (e.isIntersecting) reach(n);
    fill();
    clearTimeout(tm);
    if (e.intersectionRatio >= .5 && !isRead(V.id) && !V.noAuto) { tm = setTimeout(autoRead, Math.max(0, need - (Date.now() - V.t0))); V.tm.push(tm); }
  }, { threshold: [0, .5] });
  oe.observe(end); V.io.push(oe);
  // 자동으로 쌓이는 순간 손가락 밑 버튼이 바뀌지 않게: 끝 영역을 누르는 동안은 미룬다 (UX 4회차 권장 4)
  end.addEventListener('pointerdown', () => { V.press = true; });
  // `멈춘 곳` 은 첫 터치(또는 휠·키)까지 남는다
  const here = app.querySelector('[data-here]');
  if (here) {
    const evs = ['pointerdown', 'wheel', 'keydown'];
    const off = () => { here.style.transition = 'opacity var(--fade) var(--std)'; here.style.opacity = 0; evs.forEach(x => removeEventListener(x, off)); };
    setTimeout(() => evs.forEach(x => addEventListener(x, off, { passive: true })), 0);
  }
}
// 누름이 끝나면(손을 떼거나 스크롤로 취소돼도) 미뤄 둔 자동 읽음을 실행
const pressEnd = () => { if (V && V.press) { V.press = false; if (V.after) { const f = V.after; V.after = null; setTimeout(f, 0); } } };
['pointerup', 'pointercancel'].forEach(t => addEventListener(t, pressEnd));
function reach(k) {
  const id = V.id;
  if ((S.prog[id] || 0) < k) { S.prog[id] = k; save(); }
}
// 읽던 위치 (6.4): 답을 펼쳤고 둘째 단락에 닿은 질문만. 단락 번호 + 그 단락에서 맨 위에 보이던 문단 첫 16자
function saveLast() {
  if (!V || V.kind !== 'q' || !V.open || (S.prog[V.id] || 0) < 2) return;
  const c = app.querySelector(`[data-c="${V.cur - 1}"]`), top = headBottom() + 12;
  const p = c && [...c.querySelectorAll('p, li, h3')].find(x => x.getBoundingClientRect().bottom > top);
  S.last = { id: V.id, chunk: V.cur, para: p ? p.textContent.trim().slice(0, 16) : '', at: Date.now() };
  save();
}
addEventListener('pagehide', () => saveLast());
document.addEventListener('visibilitychange', () => { if (document.visibilityState === 'hidden') saveLast(); });
function autoRead() {
  if (!V || V.kind !== 'q' || isRead(V.id) || V.noAuto) return;
  if (V.press) { V.after = autoRead; return; }
  V.autoAt = Date.now();
  markRead(false);
}
function markRead(focus) {
  const id = V.id, first = !S.seen.firstRead;
  S.read.add(id); S.seen.firstRead = 1; S.prog[id] = chunks(Q[id]).length; save();
  endRedraw({ justRead: id, first }, focus);
}

// ===== 시뮬레이션 iframe (05 7절): kit 머리·조작은 kit 이 숨기고(embed=1) 앱 막대가 대신 그린다 =====
function wireSim(st) {
  const fr = app.querySelector('iframe[data-sim]');
  if (!fr) return;
  const stage = fr.parentElement, id = V.id, view = V;
  let done = false;
  const fail = () => { if (done || V !== view) return; done = true; simFail(id); };
  V.tm.push(setTimeout(() => { if (!done) stage.querySelector('[data-ld]').hidden = false; }, 400), setTimeout(fail, 8000));
  fr.addEventListener('error', fail);
  fr.addEventListener('load', () => {
    if (V !== view || done) return;
    let doc, W; try { doc = fr.contentDocument; W = fr.contentWindow; } catch (e) {}
    if (!doc || !W || !W.Sim || !doc.querySelector('.sim-ctrl')) return fail();
    done = true;
    stage.classList.add('ok'); stage.querySelector('[data-ld]').hidden = true;
    const page = doc.querySelector('.sim-page'), form = doc.querySelector('form.sim-try');
    const fit = () => { fr.style.height = Math.ceil(page.getBoundingClientRect().height) + 'px'; };
    const ro = new ResizeObserver(fit); ro.observe(page); V.io.push(ro); fit();
    V.sim = W.Sim; V.doc = doc; V.form = form;
    // 시뮬레이션 안의 다른 시뮬레이션 링크는 앱 화면으로
    doc.addEventListener('click', e => { const a = e.target.closest('a[href]'), m = a && a.pathname.match(/\/sims\/([a-z0-9-]+)\/index\.html$/); if (m && SIM[m[1]]) { e.preventDefault(); go('sim/' + m[1], {}, false); } });
    const s0 = W.Sim.state();
    if (s0.modes.length > 1) { app.querySelector('[data-modes]').innerHTML = segc(s0.modes.map(m => [m, esc(m)]), s0.mode, 'mode'); placeLines(false); }
    W.Sim.onShow = s => { if (V !== view) return; fit(); syncSim(s); if (s.changed && !view.quiet) revealChange(fr, s.changed); };
    // 뒤로 왔으면 떠날 때의 모드, 직접 넣은 값, 단계를 되살린다
    const r = st.sim;
    view.quiet = true;
    if (r) {
      if (r.mode !== s0.mode && s0.modes.includes(r.mode)) W.Sim.pick(r.mode);
      if (r.tried && r.vals && form) { [...form.elements].filter(x => x.name).forEach((x, k) => { if (r.vals[k] != null) x.value = r.vals[k]; }); form.requestSubmit(); W.Sim.play(false); }
      W.Sim.go(r.step);
      setMode(W.Sim.state().mode);
    }
    view.quiet = false;
    syncSim(W.Sim.state());
    fit();
    if (st.y != null) scrollTo(0, st.y);
    fr.dataset.ready = 1;
  });
}
// 앱 막대: 진행 칸, `N단계 중 k번째`, 설명, 이전·재생(마지막이면 처음부터)·다음(마지막이면 글로 읽기)
function syncSim(s) {
  const bar = app.querySelector('[data-simbar]'); if (!bar) return;
  const last = s.i === s.n - 1, cap = bar.querySelector('[data-cap]');
  if (cap.textContent !== s.caption) { cap.textContent = s.caption; cap.classList.remove('swap'); void cap.offsetWidth; cap.classList.add('swap'); }
  const cf = app.querySelector('[data-capflow]');
  cf.querySelector('[data-capf]').textContent = s.caption;
  bar.querySelector('[data-count]').textContent = `${s.n}단계 중 ${s.i + 1}번째`;
  bar.querySelector('[data-segs]').outerHTML = segs(s.n, s.i + 1, false, '단계').replace('class="seg"', 'class="seg" data-segs');
  bar.querySelector('[data-tag]').hidden = cf.querySelector('[data-ctag]').hidden = !s.tried;
  bar.querySelector('[data-try]').hidden = cf.querySelector('[data-k=try]').hidden = !(last && V.form);
  const [pv, pl, nx] = bar.querySelectorAll('.bts .btn');
  pv.disabled = s.i === 0;
  if (last) { pl.className = 'btn sec'; pl.dataset.k = 'restart'; pl.removeAttribute('aria-label'); pl.textContent = '처음부터'; }
  else { pl.className = 'btn sec ico'; pl.dataset.k = 'play'; pl.setAttribute('aria-label', s.playing ? '멈춤' : '재생'); pl.innerHTML = ic(s.playing ? 'pause' : 'play'); }
  nx.dataset.k = last ? 'toq' : 'next'; nx.innerHTML = (last ? '글로 읽기' : '다음') + ic('next');
  setMode(s.mode);
  setBarH();
  contSegs();
}
function setMode(m) {
  const sg = app.querySelector('[data-modes] .segc'); if (!sg) return;
  sg.querySelectorAll('button').forEach(b => { const on = b.dataset.v === m; b.setAttribute('aria-selected', on); b.tabIndex = on ? 0 : -1; });
  placeLines(true);
}
// 바뀐 물체 보이기 (05 4절): 묶음이 머리와 막대 사이(여백 12)에 들어가면 그 안에, 크면 가운데를 보이되 새 물체(pop)와 가장 아래 것(low)을. 둘이 함께 안 들어가면 새 물체
function revealChange(fr, ch) {
  const f = fr.getBoundingClientRect(), at = r => r && { top: f.top + r.top, bottom: f.top + r.bottom, left: f.left + r.left, right: f.left + r.right };
  const u = at(ch.u), pop = at(ch.pop), low = at(ch.low), cf = app.querySelector('[data-capflow]');
  // 좁은 열에서는 무대 위 흐름의 단계 설명도 같이 보이게
  if (cf && cf.offsetHeight) { const r = cf.getBoundingClientRect(); u.top = Math.min(u.top, r.top); }
  showX(pop || u);
  const bar = app.querySelector('[data-bar]'), hd = app.querySelector('.hs');
  const top0 = getComputedStyle(hd).position === 'sticky' ? hd.getBoundingClientRect().bottom : 0, bot0 = bar.getBoundingClientRect().top;
  const room = bot0 - top0, h = u.bottom - u.top;
  let d = 0;
  if (h <= room) {
    const m = Math.min(12, (room - h) / 2);
    if (u.bottom > bot0 - m) d = u.bottom - (bot0 - m);
    else if (u.top < top0 + m) d = u.top - (top0 + m);
  } else {
    const fit = [pop, low].filter(x => x && x.bottom - x.top <= room);
    const keep = fit.length === 2 && Math.max(pop.bottom, low.bottom) - Math.min(pop.top, low.top) > room ? [pop] : fit;
    let w = (u.top + u.bottom - room) / 2;
    if (keep.length) w = Math.min(Math.max(w, Math.max(...keep.map(x => x.bottom)) - room), Math.min(...keep.map(x => x.top)));
    d = w - top0;
  }
  if (Math.abs(d) >= 1) scrollBy({ top: d, behavior: reduce() ? 'auto' : 'smooth' });
}
// 좁은 열(글자 200%)에서 무대가 옆으로 밀릴 때: 새 물체의 가로 범위가 보이게, 넓으면 가운데로
function showX(x) {
  const st = app.querySelector('.stage[data-stage]'); if (!st || st.scrollWidth <= st.clientWidth + 1) return;
  const s = st.getBoundingClientRect();
  st.scrollLeft += x.right - x.left > s.width ? (x.left + x.right - s.left - s.right) / 2 : x.right > s.right ? x.right - s.right : x.left < s.left ? x.left - s.left : 0;
}
// 글로 읽기: 지금 모드의 관련 질문(kit 의 보이는 .sim-q). 그 질문에서 연 시뮬레이션이면 뒤로 (05 7절, 00 7.2)
function simQuestion() {
  const a = V.doc && V.doc.querySelector('.sim-q[data-q]:not([hidden])'), m = a && (a.getAttribute('href') || '').match(/#\/q\/([\w-]+)/);
  return m && Q[m[1]] ? m[1] : SIM[V.id].qs[0];
}
function toQuestion() {
  const qid = simQuestion();
  if (V.fromQ === qid && depth > 0) { history.back(); return; }
  go('q/' + qid, { ctx: { ...ctxOf('sim', qid), sim: V.id } });
}

// ===== 작은 움직임 도구 =====
// 진행 칸·블록 줄: 칸 하나의 폭이 12 미만이면 이어진 막대 하나로 (00 5.6)
function contSegs() {
  app.querySelectorAll('.seg, .brow').forEach(s => { s.classList.remove('cont'); const i = s.firstElementChild; if (i && i.offsetWidth && i.offsetWidth < 12) s.classList.add('cont'); });
}
addEventListener('resize', () => { contSegs(); placeLines(false); });
// 큰 탭 밑줄(글자 폭), 분할 조각(칸 번호만 바꿔 translateX)
function placeLines(animate) {
  app.querySelectorAll('.hm .r2').forEach(nav => {
    const a = nav.querySelector('[aria-current]'), s = a && a.querySelector('span'), ul = nav.querySelector('.ul');
    if (!s || !ul) return;
    if (!animate) ul.style.transition = 'none';
    ul.style.transform = `translateX(${a.offsetLeft + s.offsetLeft}px) scaleX(${s.offsetWidth / 10})`;
    if (!animate) { void ul.offsetWidth; ul.style.transition = ''; }
  });
  app.querySelectorAll('.segc').forEach(sg => {
    const i = [...sg.querySelectorAll('button')].findIndex(b => b.getAttribute('aria-selected') === 'true'), th = sg.querySelector('.th');
    if (!th || i < 0) return;
    if (!animate) th.style.transition = 'none';
    th.style.setProperty('--i', i);
    if (!animate) { void th.offsetWidth; th.style.transition = ''; }
  });
}
function setBarH() {
  const bar = app.querySelector('[data-bar]');
  document.documentElement.style.setProperty('--barh', (bar ? bar.offsetHeight : 0) + 'px');
}
new ResizeObserver(setBarH).observe(app);
// 알림 한 줄 (00 5.11): 2.4초, 동작이 있으면 5초. 초기화 되돌리기는 10초이고 누르거나 초점이 있는 동안 멈춘다
let toastT = null, undoBox = null;
function toast(msg, act, focus) {
  document.querySelectorAll('.toast').forEach(t => t.remove()); clearTimeout(toastT);
  const bar = app.querySelector('[data-bar]'), end = app.querySelector('[data-end]'), hd = app.querySelector('.hm, .hs');
  const up = !bar || (end && end.getBoundingClientRect().top < bar.getBoundingClientRect().top);
  document.body.insertAdjacentHTML('beforeend', `<div class="toast t-ui${up ? ' top' : ''}" role="status"><span>${msg}</span>${act ? `<button class="t-ui" data-act="${act[1]}">${act[0]}</button>` : ''}</div>`);
  const el = document.body.lastElementChild, undo = act && act[1] === 'undo';
  if (up) el.style.setProperty('--tt', ((hd && getComputedStyle(hd).position === 'sticky' ? Math.max(0, hd.getBoundingClientRect().bottom) : 0) + 12) + 'px');
  let left = undo ? 10000 : act ? 5000 : 2400, t0 = 0, held = false;
  const kill = () => { el.remove(); if (undo) undoBox = null; };
  const run = () => { held = false; clearTimeout(toastT); t0 = Date.now(); toastT = setTimeout(kill, left); };
  const hold = () => { if (held) return; held = true; clearTimeout(toastT); left -= Date.now() - t0; };
  if (act) { ['pointerdown', 'focusin'].forEach(e => el.addEventListener(e, hold)); ['pointerup', 'pointercancel', 'focusout'].forEach(e => el.addEventListener(e, run)); }
  run();
  if (focus && act) el.querySelector('button').focus();
}
const closeToast = () => { document.querySelectorAll('.toast').forEach(t => t.remove()); clearTimeout(toastT); };

// ===== 누르기 =====
const ACT = {
  back: () => depth > 0 ? history.back() : go(parentOf(), {}, true),
  retry: () => boot(),
  closeNote: b => { noteClosed = true; b.closest('.note').remove(); },
  // 답 보기: 판이 흐려진 뒤 본문이 올라옴, 초점은 핵심 (03 7절)
  reveal: b => {
    const rc = b.closest('.recall'); if (!rc || rc.dataset.out) return; rc.dataset.out = 1;
    const y = scrollY;
    const open = () => {
      if (!rc.isConnected) return;
      S.seen.recallTip = 1; reach(1);
      history.replaceState({ ...history.state, open: true }, '');
      const view = V; leave(); V = { ...view, io: [], tm: [], open: true, t0: Date.now(), cur: 1, mark: 0 };
      const v = qView(V.id, V.ctx, { open: true, anim: !reduce() });
      app.className = v.cls; app.innerHTML = v.html + v.bar; setBarH(); wire({}); scrollTo(0, y);
      app.querySelector('[data-core]').focus({ preventScroll: true });
    };
    rc.style.transition = 'opacity var(--fade) var(--std)'; rc.style.opacity = 0;
    rc.addEventListener('transitionend', e => { if (e.target === rc) open(); }); setTimeout(open, 200);
  },
  hide: () => {
    history.replaceState({ ...history.state, open: false, tails: [] }, '');
    saveLast();
    const view = V; leave(); V = { ...view, io: [], tm: [], open: false, mark: 0 };
    const v = qView(V.id, V.ctx, { open: false });
    app.className = v.cls; app.innerHTML = v.html + v.bar; setBarH(); wire({}); scrollTo(0, 0);
    app.querySelector('[data-act=reveal]').focus();
  },
  tail: b => {
    const j = +b.dataset.j, on = b.getAttribute('aria-expanded') !== 'true';
    b.setAttribute('aria-expanded', on);
    if (on) b.insertAdjacentHTML('afterend', tailAns(Q[V.id], j)); else if (b.nextElementSibling && b.nextElementSibling.matches('.ta')) b.nextElementSibling.remove();
  },
  conf: b => {
    const id = V.id, on = !isConf(id);
    on ? S.conf.add(id) : S.conf.delete(id); if (on) S.everConf = true; save();
    b.setAttribute('aria-pressed', on); b.innerHTML = ic(on ? 'check' : 'help') + '<span class="lbl">헷갈려요</span>';
    b.classList.remove('popi'); void b.offsetWidth; if (!reduce()) b.classList.add('popi');
    if (on && !S.seen.confToast) { S.seen.confToast = 1; save(); toast('목차의 헷갈림만에서 모아 볼 수 있어요'); }
  },
  markRead: () => markRead(true),
  unread: () => {
    if (V.autoAt && Date.now() - V.autoAt < 600) return; // 방금 자동으로 쌓인 순간의 잘못 누름은 무시
    S.read.delete(V.id); V.noAuto = true; save();
    endRedraw({ canceled: true }, true);
    toast('읽음을 취소했어요', ['되돌리기', 'reread']);
  },
  reread: () => { S.read.add(V.id); save(); endRedraw({}, true); closeToast(); },
  another: () => go(`q/${pickRandom()}`, { ctx: ctxOf('random') }, true),
  shuffle: b => {
    if (b.dataset.busy) return; b.dataset.busy = 1;
    const card = app.querySelector('.rnd .card'), box = card.querySelector('.swap');
    box.classList.add('out');
    setTimeout(() => {
      const id = pickRandom();
      history.replaceState({ ...history.state, rnd: id }, '');
      box.innerHTML = rndInner(id); card.setAttribute('href', '#/q/' + id); card.setAttribute('aria-label', `랜덤 질문, ${Q[id].title}, 답은 가려져 있어요`);
      box.classList.remove('out'); box.classList.add('in');
      app.querySelector('[data-live]').textContent = '새 질문: ' + Q[id].title;
      const done = () => { box.classList.remove('in'); delete b.dataset.busy; };
      reduce() ? done() : box.addEventListener('animationend', done, { once: true });
    }, reduce() ? 0 : 120);
  },
  // 분할 선택: 조각을 먼저 미끄러뜨리고 목록을 바꾼다. 기록은 바꿔 끼움 (7.3)
  tocview: b => {
    const sg = b.closest('.segc'), v = b.dataset.v;
    if (sg) { sg.querySelectorAll('button').forEach(x => x.setAttribute('aria-selected', x === b)); placeLines(true); }
    setTimeout(() => {
      history.replaceState({ d: depth, k: uid() }, '', '#/' + (v === 'all' ? 'toc' : 'toc/' + v));
      render(false);
      const p = app.querySelector('[data-panel]'); if (p && !reduce()) p.classList.add('list-in');
      [...p.querySelectorAll('.row')].slice(0, 8).forEach((r, k) => r.style.setProperty('--k', k));
      (app.querySelector(`.segc [data-v="${v}"]`) || app.querySelector('h1')).focus({ preventScroll: true });
    }, sg && !reduce() ? 160 : 0);
  },
  // 장 이동: 그 장 머리가 장 이동 줄 바로 아래로, 주소는 바꿔 끼움, 초점은 장 머리 (02 4절)
  jump: b => {
    const k = b.dataset.k;
    history.replaceState({ ...history.state, y: null }, '', `#/${V_JUMP}/${k}`); lastK = history.state.k;
    scrollTo({ top: chapY(k), behavior: reduce() ? 'auto' : 'smooth' });
    app.querySelector(`#ch-${k} h2`).focus({ preventScroll: true });
  },
  reset: () => { document.body.insertAdjacentHTML('beforeend', sheetHtml()); document.getElementById('shT').focus(); },
  closeSheet: () => { document.querySelectorAll('.scrim,.sheet').forEach(e => e.remove()); const r = app.querySelector('[data-act=reset]'); if (r) r.focus(); },
  doReset: () => {
    undoBox = S;
    S = Object.assign(blank(), { seen: S.seen }); save();
    document.querySelectorAll('.scrim,.sheet').forEach(e => e.remove());
    const box = undoBox; render(false); undoBox = box;
    toast('진도를 초기화했어요', ['되돌리기', 'undo'], true);
  },
  undo: () => { if (undoBox) { S = undoBox; undoBox = null; save(); render(false); app.querySelector('[data-act=reset]').focus(); } closeToast(); },
  reload: () => location.reload(),
  offRetry: () => { setOff('saving'); navigator.serviceWorker.register('sw.js').then(watchSw, () => setOff('fail')); },
  mode: b => { if (V.sim) V.sim.pick(b.dataset.v); },
  simRetry: () => render(false),
  simFig: () => { history.replaceState({ ...history.state, fig: 1 }, ''); render(false); },
  sim: b => {
    const k = b.dataset.k;
    if (k === 'toq') return toQuestion();
    const W = V.sim; if (!W) return;
    const s = W.state();
    if (k === 'prev') W.go(s.i - 1);
    else if (k === 'next') W.go(s.i + 1);
    else if (k === 'play') W.play();
    else if (k === 'restart') W.reset();
    else if (k === 'try') { // 직접 해 보기 폼으로: 폼 윗변을 머리 아래로, 초점은 첫 입력
      const fr = app.querySelector('iframe[data-sim]'), f = V.form;
      scrollBy({ top: fr.getBoundingClientRect().top + f.getBoundingClientRect().top - headBottom() - 12, behavior: reduce() ? 'auto' : 'smooth' });
      const inp = f.querySelector('input,select,button'); if (inp) inp.focus({ preventScroll: true });
    }
  },
};
document.addEventListener('click', e => {
  if (e.button || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
  const a = e.target.closest('a[href^="#/"]');
  if (a && D) { e.preventDefault(); if (!a.hasAttribute('data-act')) { follow(a); return; } }
  const b = e.target.closest('[data-act]');
  if (b && !b.disabled && ACT[b.dataset.act]) { e.preventDefault(); ACT[b.dataset.act](b); }
});
// 분할 선택 좌우 화살표 (5.7), 시트 Esc 와 초점 가두기 (5.13)
document.addEventListener('keydown', e => {
  const tab = e.target.closest && e.target.closest('[role=tab]');
  if (tab && (e.key === 'ArrowRight' || e.key === 'ArrowLeft')) {
    const all = [...tab.parentElement.querySelectorAll('[role=tab]')], n = all[(all.indexOf(tab) + (e.key === 'ArrowRight' ? 1 : all.length - 1)) % all.length];
    n.focus(); n.click(); e.preventDefault(); return;
  }
  const sh = document.querySelector('.sheet');
  if (!sh) return;
  if (e.key === 'Escape') ACT.closeSheet();
  if (e.key === 'Tab') {
    const f = [...sh.querySelectorAll('button')], i = f.indexOf(document.activeElement);
    if (e.shiftKey && i <= 0) { f[f.length - 1].focus(); e.preventDefault(); }
    else if (!e.shiftKey && i === f.length - 1) { f[0].focus(); e.preventDefault(); }
  }
});
// 여러 탭 (6.6): 다른 탭에서 바뀐 진도를 받아 읽음·헷갈림은 합치고, 지금 질문의 펼침과 스크롤은 건드리지 않는다
addEventListener('storage', e => {
  if (e.key !== KEY || !e.newValue || !D) return;
  let o; try { o = fixStore(JSON.parse(e.newValue)); } catch (x) { return; }
  o.read.forEach(id => S.read.add(id)); o.conf.forEach(id => S.conf.add(id));
  Object.entries(o.prog).forEach(([id, n]) => { S.prog[id] = Math.max(S.prog[id] || 0, n); }); // 질문별 최댓값
  if (o.last && (!S.last || o.last.at > S.last.at)) S.last = o.last; // 더 최근 기록만
  S.seen = { ...S.seen, ...o.seen }; S.everConf = S.everConf || o.everConf;
  if (V && V.kind === 'q') { if (V.open) endRedraw({}); const c = app.querySelector('[data-act=conf]'); if (c) c.outerHTML = confBtn(V.id); }
  else if (V && ['home', 'toc', 'sims'].includes(V.kind)) { const y = scrollY; render(false); scrollTo(0, y); }
});
// 오프라인 안내 줄
addEventListener('online', () => { NET = true; repaintNotes(); });
addEventListener('offline', () => { NET = false; repaintNotes(); });

// ===== 오프라인 저장 (서비스 워커 app/sw.js): 홈 이 기기 행의 상태 =====
if ('serviceWorker' in navigator) navigator.serviceWorker.register('sw.js').then(watchSw, () => setOff('fail'));
function setOff(v) {
  OFF = v;
  const el = app.querySelector('[data-off]');
  if (el) el.innerHTML = offSt();
  repaintNotes();
}
function watchSw(reg) {
  if (reg.active) { OFF = 'saved'; S && (S.seen.offlineDone = 1); return; }
  if (D) setOff('saving'); else OFF = 'saving';
  const w = reg.installing || reg.waiting;
  if (w) w.addEventListener('statechange', () => { if (w.state === 'redundant' && !reg.active) setOff('fail'); });
  navigator.serviceWorker.ready.then(() => {
    setOff('saved');
    if (S && !S.seen.offlineDone) { S.seen.offlineDone = 1; save(); }
  });
}
// 새 판이 자리를 넘겨받으면(새 서비스 워커) 새로 고침을 권한다. 처음 설치는 빼고
if ('serviceWorker' in navigator && navigator.serviceWorker.controller) navigator.serviceWorker.addEventListener('controllerchange', () => toast('새 내용이 있어요', ['새로 고침', 'reload']));

// ===== 시작: 본문 불러오기 (400ms 넘으면 자리 모양, 10초 넘거나 실패하면 못 불러옴) =====
history.scrollRestoration = 'manual';
if (location.pathname.endsWith('/index.html')) history.replaceState(history.state, '', location.pathname.slice(0, -10) + location.search + location.hash);
readStore();
function boot() {
  const r0 = routeOf().split('/')[0], paintStatic = h => { app.className = ''; app.innerHTML = h; setBarH(); placeLines(false); };
  const lt = setTimeout(() => { if (!D) paintStatic(r0 === 'q' ? loadingQ() : r0 === 'sims' || r0 === 'sim' ? loadingSims() : loadingHome()); }, 400);
  const ac = new AbortController(), at = setTimeout(() => ac.abort(), 10000);
  fetch('data/notes.json', { signal: ac.signal })
    .then(r => { if (!r.ok) throw new Error(r.status); return r.json(); })
    .then(data => {
      D = data;
      D.questions.forEach((q, i) => { q.i = i; Q[q.id] = q; });
      D.subjects.forEach(s => { SUB[s.key] = s; });
      D.sims.forEach(s => { SIM[s.id] = s; });
      ORDER = D.questions.map(q => q.id);
      STARS = D.questions.filter(q => q.stars).sort((a, b) => b.stars - a.stars || a.i - b.i).map(q => q.id);
      S = fixStore(RAW);
      if (OFF === 'saved') S.seen.offlineDone = 1;
      depth = history.state && history.state.d != null ? history.state.d : 0;
      history.replaceState({ ...history.state, d: depth, k: (history.state && history.state.k) || uid() }, '');
      render(false);
    })
    .catch(() => { if (!D) paintStatic(loadFail(r0 === 'q')); })
    .finally(() => { clearTimeout(lt); clearTimeout(at); });
}
boot();
document.fonts.ready.then(() => { placeLines(false); contSegs(); }); // 글꼴이 늦게 오면 밑줄 자리와 칸 폭을 다시 잰다
