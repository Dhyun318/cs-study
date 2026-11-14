// CS 차곡: 화면 그리기, hash 라우팅, 진도 저장(localStorage). 화면과 동작은 design/p-flow/index.html 폰 화면과 같다
'use strict';
const app = document.getElementById('app');
let D, Q = {}, SUB = {}, SIM = {}, ORDER = [];

const META = {
  ds: { icon: 't-stack-2', hint: 'Array, Queue, Hash, BST' },
  os: { icon: 't-cpu', hint: 'Process, Thread, Memory' },
  db: { icon: 't-database', hint: 'DB 설계, Transaction, Index' },
  net: { icon: 't-network', hint: 'TCP/IP, HTTP, Authorization' },
};
const SIM_ICON = { 'hash-table': 't-hash', 'context-switch': 't-arrows-exchange', 'bst-search': 't-binary-tree', 'transaction-lock': 't-lock', 'google-request': 't-world', 'tcp-handshake': 't-arrows-left-right' };
const HOME_SIMS = [['hash-table', 'Hash 저장과 충돌'], ['context-switch', 'Context switch'], ['bst-search', 'BST 검색'], ['transaction-lock', 'Transaction과 Lock'], ['google-request', 'google.com 입력 과정'], ['tcp-handshake', '3-way·4-way handshake']];
const inSub = k => D.questions.filter(q => q.s === k);
const nth = q => inSub(q.s).indexOf(q) + 1;
const simStars = x => Math.max(...x.qs.map(id => Q[id].stars));

// ===== 작은 조각 =====
const esc = s => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
const ic = (id, n = 16) => `<svg class="ic" width="${n}" height="${n}" aria-hidden="true"><use href="#${id}"/></svg>`;
const ti = (id, n = 24) => `<svg class="ti" width="${n}" height="${n}" aria-hidden="true"><use href="#${id}"/></svg>`;
const star = (n, label = `별 ${n}개`) => n ? `<span class="hotx num" role="img" aria-label="${label}">${ic('i-star', 12)}${n}</span>` : '';
const CHEV = ic('i-chev');
// 위 막대: 뒤로 + 제목. 화면에 따로 h1 이 없으면 제목을 h1 로
const subNav = (title, parent, h1) => `<header class="nav sub"><button class="back" data-act="back" data-parent="${parent}" aria-label="뒤로">${ic('i-chev', 20)}</button>${h1 ? `<h1>${title}</h1>` : `<b>${title}</b>`}</header>`;
const firstPara = html => { const t = document.createElement('template'); t.innerHTML = html; return (t.content.querySelector('p') || t.content).textContent; };

// ===== 저장: 읽음, 헷갈림, 마지막 위치 (localStorage). 처음 열면 모두 비어 있다 =====
const KEY = 'cs-chagok';
let S = (() => { try { const s = JSON.parse(localStorage.getItem(KEY)); if (s && Array.isArray(s.read) && Array.isArray(s.confused)) return s; } catch (e) {} return { read: [], confused: [], last: null }; })();
const save = () => { try { localStorage.setItem(KEY, JSON.stringify(S)); } catch (e) {} };
const isRead = id => S.read.includes(id);
const isConf = id => S.confused.includes(id);
function setIn(list, id, on) {
  const a = S[list], i = a.indexOf(id);
  if (on && i < 0) a.push(id);
  if (!on && i >= 0) a.splice(i, 1);
  save();
}

const qRow = q => `<a class="lr" href="#/q/${q.id}">
  <span class="as no num${isRead(q.id) ? ' done' : ''}">${isRead(q.id) ? ti('t-check', 18) + '<span class="sr">읽음</span>' : nth(q)}</span>
  <span class="tx"><b>${star(q.stars)}${esc(q.title)}</b>${q.tails.length ? `<small>꼬리질문 ${q.tails.length}개</small>` : ''}</span>
  <span class="rt">${isConf(q.id) ? '<span class="flag">헷갈림</span>' : ''}${CHEV}</span></a>`;
const freqRow = q => `<a class="lr" href="#/q/${q.id}">
  <span class="as st num" role="img" aria-label="별 ${q.stars}개">${ic('i-star', 14)}${q.stars}</span>
  <span class="tx"><b>${esc(q.title)}</b><small>${SUB[q.s].name}${q.tails.length ? `, 꼬리질문 ${q.tails.length}개` : ''}</small></span>
  ${isConf(q.id) ? `<span class="rt"><span class="flag">헷갈림</span>${CHEV}</span>` : isRead(q.id) ? '<span class="rt rd">읽음</span>' : `<span class="rt">${CHEV}</span>`}</a>`;
const relRow = q => `<a class="lr" href="#/q/${q.id}">
  <span class="as">${ti(META[q.s].icon, 22)}</span>
  <span class="tx"><b>${star(q.stars)}${esc(q.title)}</b><small>${SUB[q.s].name}, ${esc(q.sub)}</small></span>
  <span class="rt">${CHEV}</span></a>`;
const simTile = (x, short) => `<a class="tile" href="#/sim/${x.id}"><span class="top">${ti(SIM_ICON[x.id] || META[x.s].icon, 26)}${star(simStars(x), `연결 질문 별 ${simStars(x)}개`)}</span><b>${esc(short || x.title)}</b><small>${short ? SUB[x.s].name : esc(Q[x.qs[0]].title)}</small></a>`;

// ===== 화면 =====
function home() {
  const first = !S.last;
  const L = S.last && Q[S.last.id] ? S.last : { id: ORDER.find(id => !isRead(id)) || ORDER[0], pct: 0, text: '' };
  const q = Q[L.id];
  const freq = D.questions.filter(x => x.stars).sort((a, b) => b.stars - a.stars || isRead(a.id) - isRead(b.id) || a.i - b.i);
  return `<div class="page"><header class="nav"><h1>CS 차곡</h1></header>
  <main>
    <section class="grp hero" aria-label="${first ? '처음 읽을 질문' : '읽던 질문'}">
      <div class="hero-top">
        <div><small>${first ? '처음 읽을 질문' : '읽던 질문'}</small><p class="num">${SUB[q.s].name} ${nth(q)}번째 질문</p></div>
        <span class="ring num" style="--p:${L.pct}" role="img" aria-label="이 질문 ${L.pct}% 읽음">${L.pct}%</span>
      </div>
      <h2>${star(q.stars)}${esc(q.title)}</h2>
      <div class="sheet"><small>${L.text ? '멈춘 곳' : '첫 단락'}</small><p>${esc(L.text || firstPara(q.core))}</p></div>
      <a class="cta" href="#/q/${q.id}${first ? '' : '/resume'}">${first ? '첫 질문 읽기' : '이어 읽기'}</a>
    </section>

    <section class="grp rv">
      <a class="lr" href="#/review">
        <span class="as">${ti('t-repeat')}</span>
        <span class="tx"><b>복습할 질문</b><small>헷갈림 표시한 질문만 다시 봐요</small></span>
        <span class="rt"><span class="cnt num">${S.confused.length}<span>개</span></span>${ic('i-chev', 18)}</span>
      </a>
    </section>

    <section class="grp">
      <div class="lh">
        <div><h2>과목</h2><p class="num">${ORDER.length}문항 중 ${S.read.length}문항 읽음</p></div>
        <a href="#/toc">목차${CHEV}</a>
      </div>
      ${D.subjects.map(s => {
        const qs = inSub(s.key), r = qs.filter(x => isRead(x.id)).length, c = qs.filter(x => isConf(x.id)).length;
        const note = c ? `<small class="due">복습 ${c}</small>` : `<small>${r === 0 ? '시작 전' : r === qs.length ? '다 읽음' : '읽는 중'}</small>`;
        return `<a class="lr" href="#/toc/${s.key}">
          <span class="as">${ti(META[s.key].icon, 22)}</span>
          <span class="tx"><b>${s.name}</b><small>${META[s.key].hint}</small></span>
          <span class="rt"><span class="v num"><b>${r}/${qs.length}</b>${note}</span>${CHEV}</span></a>`;
      }).join('')}
    </section>

    <section class="grp">
      <div class="lh">
        <div><h2>자주 나온 질문</h2><p class="num">별 많은 순, ${freq.length}문항 중 ${freq.filter(x => isRead(x.id)).length}문항 읽음</p></div>
        <a href="#/toc/star">전체${CHEV}</a>
      </div>
      ${freq.slice(0, 3).map(freqRow).join('')}
    </section>

    <section class="grp">
      <div class="lh"><div><h2>동작으로 보기</h2><p>그림으로 따라가는 개념</p></div></div>
      <div class="hs">${HOME_SIMS.map(([id, t]) => simTile(SIM[id], t)).join('')}</div>
      <a class="lr" href="#/sims">
        <span class="tx"><b>시뮬레이션 전체 보기</b><small>과목별로 모두 보기</small></span>
        <span class="rt">${CHEV}</span>
      </a>
    </section>
  </main></div>`;
}

function toc(f) {
  const chips = [['all', '전체'], ...D.subjects.map(s => [s.key, s.name]), ['star', ic('i-star', 14) + '빈출순']];
  let body;
  if (f === 'star') {
    const list = D.questions.filter(q => q.stars).sort((a, b) => b.stars - a.stars || a.i - b.i);
    body = `<section class="grp"><div class="lh"><div><h2>자주 나온 질문</h2><p class="num">별 많은 순, ${list.length}문항 중 ${list.filter(q => isRead(q.id)).length}문항 읽음</p></div></div>${list.map(freqRow).join('')}</section>`;
  } else {
    body = D.subjects.filter(s => f === 'all' || s.key === f).map(s => {
      const qs = inSub(s.key);
      return `<section class="grp"><div class="lh"><div><h2>${s.name}</h2><p class="num">${qs.length}문항 중 ${qs.filter(q => isRead(q.id)).length}문항 읽음</p></div></div>
        ${s.subs.map(sub => `<h3 class="sub-h">${esc(sub)}</h3>${qs.filter(q => q.sub === sub).map(qRow).join('')}`).join('')}</section>`;
    }).join('');
  }
  return `<div class="page">${subNav('목차', '#/home', true)}
  <nav class="chips" aria-label="목차 보기 방식">${chips.map(([k, n]) => `<a class="chip" href="#/toc${k === 'all' ? '' : '/' + k}" data-replace${k === f ? ' aria-current="page"' : ''}>${n}</a>`).join('')}</nav>
  <main>${body}</main></div>`;
}

// mode: 없음 = 답 가림, resume = 펼치고 멈춘 단락으로
function question(id, mode) {
  const q = Q[id], prev = ORDER[q.i - 1], next = ORDER[q.i + 1], open = mode === 'resume';
  if (open) setIn('read', id, true);
  return `<div class="page has-bar">${subNav(SUB[q.s].name, '#/toc/' + q.s)}
  <main>
    <section class="grp qh"><small>${esc(q.sub)}</small><h1>${star(q.stars)}${esc(q.title)}</h1></section>
    <section class="grp">
      <div class="gate"${open ? ' hidden' : ''}><p>먼저 스스로 떠올려 본 다음 답을 열어 보세요.</p><button class="cta" data-act="reveal" aria-expanded="${open}" aria-controls="ans">답 보기</button></div>
      <div class="ans" id="ans"${open ? '' : ' hidden'}>
        <div class="ans-top"><small>핵심 답변</small><button class="link-btn" data-act="hide">답 가리기</button></div>
        <div class="core prose">${q.core}</div>
        <div class="body prose">${q.body}</div>
      </div>
    </section>
    ${q.sims.length ? `<section class="grp go"><div class="lh"><div><h2>동작으로 보기</h2><p>그림이 움직이며 단계별로 보여 줘요</p></div></div>
      ${q.sims.map(sid => `<a class="lr" href="#/sim/${sid}"><span class="as">${ti('t-player-play', 22)}</span><span class="tx"><b>${esc(SIM[sid].title)}</b><small>시뮬레이션</small></span><span class="rt">${CHEV}</span></a>`).join('')}</section>` : ''}
    ${q.tails.length ? `<section class="grp"><div class="lh"><div><h2>꼬리질문 ${q.tails.length}개</h2><p>눌러서 답을 펼쳐요</p></div></div>
      ${q.tails.map(t => `<details class="tq"><summary><span>${esc(t.q)}</span>${CHEV}</summary><div class="prose">${t.a}</div></details>`).join('')}</section>` : ''}
  </main>
  <div class="bar">
    <a class="btn sub ico" ${prev ? `href="#/q/${prev}" data-replace` : 'aria-disabled="true"'} aria-label="이전 질문">${ti('t-arrow-left', 22)}</a>
    ${confBtn(id)}
    <a class="btn pri" ${next ? `href="#/q/${next}" data-replace` : 'aria-disabled="true"'}>다음 질문${ti('t-arrow-right', 20)}</a>
  </div></div>`;
}
const confBtn = id => `<button class="btn sub" data-act="confuse" data-q="${id}" aria-pressed="${isConf(id)}">${isConf(id) ? ti('t-check', 20) + '헷갈림' : ti('t-help-circle', 20) + '헷갈려요'}</button>`;

function simsList() {
  return `<div class="page">${subNav('시뮬레이션', '#/home', true)}
  <main>${D.subjects.map(s => {
    const list = D.sims.filter(x => x.s === s.key);
    return `<section class="grp"><div class="lh"><div><h2>${s.name}</h2><p class="num">${list.length}개</p></div></div><div class="grid">${list.map(x => simTile(x)).join('')}</div></section>`;
  }).join('')}</main></div>`;
}

function sim(id) {
  const x = SIM[id];
  return `<div class="page">${subNav('시뮬레이션', '#/sims')}
  <main>
    <section class="grp qh"><small>${SUB[x.s].name}</small><h1>${esc(x.title)}</h1></section>
    <div class="frame"><iframe src="sims/${id}/index.html" title="${esc(x.title)} 시뮬레이션"></iframe></div>
    <section class="grp"><div class="lh"><div><h2>관련 질문</h2><p>본 다음 글로 정리해요</p></div></div>${x.qs.map(qid => relRow(Q[qid])).join('')}</section>
  </main></div>`;
}

// 복습: 들어올 때의 헷갈림 목록을 한 장씩. 이제 알아요 = 목록에서 빼기, 아직 헷갈려요 = 다음에 다시
let rv = null;
function review() {
  if (!rv) rv = { list: S.confused.slice(), i: 0, shown: false };
  const nav = subNav('복습', '#/home', true);
  if (!S.confused.length) return `<div class="page">${nav}
    <main><section class="grp empty">
      <span class="as">${ti('t-circle-check', 28)}</span>
      <h2>복습할 질문이 없어요</h2>
      <p>질문을 읽다가 헷갈려요를 누르면 여기에 모여요.</p>
      <a class="cta" href="#/toc">목차 보기</a>
    </section></main></div>`;
  if (rv.i >= rv.list.length) return `<div class="page">${nav}
    <main><section class="grp empty">
      <span class="as">${ti('t-repeat', 28)}</span>
      <h2>한 바퀴 다 봤어요</h2>
      <p class="num">아직 헷갈리는 질문이 ${S.confused.length}개 남아 있어요.</p>
      <button class="cta" data-act="again">다시 보기</button>
    </section></main></div>`;
  const q = Q[rv.list[rv.i]];
  return `<div class="page">${nav}
  <main><section class="grp card rise" aria-label="복습 카드">
    <div class="card-top"><span>${SUB[q.s].name}</span><span class="num">${rv.i + 1} / ${rv.list.length}</span></div>
    <h2>${star(q.stars)}${esc(q.title)}</h2>
    ${rv.shown ? `<div class="core prose rise">${q.core}</div>
      <a class="more" href="#/q/${q.id}">본문 전체 보기${CHEV}</a>
      <div class="duo"><button class="btn line" data-act="still">아직 헷갈려요</button><button class="btn pri" data-act="know">이제 알아요</button></div>`
    : `<button class="cta" data-act="peek">답 보기</button>`}
  </section></main></div>`;
}

function view(route) {
  const [r, a, b] = route.replace(/^#\/?/, '').split('/');
  if (r === 'toc') return toc(['ds', 'os', 'db', 'net', 'star'].includes(a) ? a : 'all');
  if (r === 'q' && Q[a]) return question(a, b);
  if (r === 'sims') return simsList();
  if (r === 'sim' && SIM[a]) return sim(a);
  if (r === 'review') return review();
  return home();
}

// ===== 이동: 주소 hash 가 화면. 기록 칸마다 { d: 앱 안 깊이, y: 스크롤 } 을 둔다 =====
let cur = '', depth = 0;
const navH = () => app.querySelector('.nav').offsetHeight;
const saveY = () => history.replaceState({ ...history.state, y: scrollY }, '');

// 질문 화면을 떠날 때: 읽던 위치(스크롤 %, 화면 맨 위에 보이는 단락, 꼬리질문 답 포함)를 저장
function leave() {
  if (!cur.startsWith('#/q/')) return;
  const max = document.documentElement.scrollHeight - innerHeight, top = navH() + 20;
  const p = [...app.querySelectorAll('.prose p')].find(p => p.getBoundingClientRect().height && p.getBoundingClientRect().bottom > top);
  S.last = { id: cur.split('/')[2], pct: max > 0 ? Math.min(100, Math.round(scrollY / max * 100)) : 0, text: p ? p.textContent : '' };
  save();
}

function paint() {
  app.innerHTML = view(cur);
  const t = app.querySelector('h1').textContent;
  document.title = t === 'CS 차곡' ? t : `${t} · CS 차곡`;
  const f = app.querySelector('.frame iframe');
  if (f) f.addEventListener('load', fit);
}

// 화면 바꾸기: 떠나는 화면 정리 → 새 화면 → 스크롤(이어 읽기면 멈춘 단락, 뒤로 왔으면 그때 위치)
function render() {
  leave();
  const route = location.hash || '#/home';
  if (cur.startsWith('#/review') && !route.startsWith('#/review')) rv = null;
  const first = !cur;
  cur = route;
  paint();
  if (!first) focusTop();
  const p = route.endsWith('/resume') && S.last && S.last.text && [...app.querySelectorAll('.prose p')].find(p => p.textContent === S.last.text);
  if (p && p.closest('details')) p.closest('details').open = true;
  scrollTo(0, p ? p.getBoundingClientRect().top + scrollY - navH() - 24 : (history.state && history.state.y) || 0);
}

// 새 화면 h1 에 초점, 복습 카드가 바뀌면 그 카드의 첫 버튼에
function focusTop() { const h = app.querySelector('h1'); h.tabIndex = -1; h.focus({ preventScroll: true }); }
const focusCard = () => app.querySelector('main button, main .cta').focus({ preventScroll: true });

// 같은 칸에서 바꾸기(목차 칩, 이전/다음 질문): 기록을 쌓지 않는다
function replace(route) {
  history.replaceState({ d: depth }, '', route);
  render();
}

// 시뮬레이션 iframe(같은 출처): 겹치는 자체 머리는 가리고, 높이를 내용에 맞춘다
function fit(e) {
  const f = e.target, d = f.contentDocument;
  if (!d || !d.body) return;
  d.head.insertAdjacentHTML('beforeend', '<style>.sim-top{display:none}.sim-page{min-height:0;padding-bottom:0}</style>');
  // 관련 질문 링크(kit 이 _top 으로 보냄)는 돌아올 스크롤만 저장, 다른 시뮬레이션 링크는 앱 화면으로 연다
  d.addEventListener('click', ev => {
    const a = ev.target.closest('a[href]');
    if (!a) return;
    const m = a.pathname.match(/\/sims\/([a-z0-9-]+)\/index\.html$/);
    if (m && SIM[m[1]]) { ev.preventDefault(); saveY(); location.hash = '#/sim/' + m[1]; }
    else if (a.target === '_top') saveY();
  });
  new f.contentWindow.ResizeObserver(() => { f.style.height = d.body.offsetHeight + 'px'; }).observe(d.body);
}

// ===== 누르기 =====
function setAnswer(open) {
  const ans = app.querySelector('.ans'), gate = app.querySelector('.gate');
  ans.hidden = !open; gate.hidden = open;
  gate.querySelector('button').setAttribute('aria-expanded', open);
  if (open) { ans.classList.add('rise'); setIn('read', cur.split('/')[2], true); ans.querySelector('.link-btn').focus({ preventScroll: true }); }
  else gate.querySelector('button').focus();
}
const ACT = {
  back: b => depth > 0 ? history.back() : replace(b.dataset.parent),
  reveal: () => setAnswer(true),
  hide: () => setAnswer(false),
  confuse: b => { const id = b.dataset.q; setIn('confused', id, !isConf(id)); b.outerHTML = confBtn(id); app.querySelector('[data-act="confuse"]').focus(); },
  peek: () => { rv.shown = true; paint(); focusCard(); },
  know: () => { setIn('confused', rv.list[rv.i], false); rv.i++; rv.shown = false; paint(); scrollTo(0, 0); focusCard(); },
  still: () => { rv.i++; rv.shown = false; paint(); scrollTo(0, 0); focusCard(); },
  again: () => { rv = null; paint(); scrollTo(0, 0); focusCard(); },
};
document.addEventListener('click', e => {
  const a = e.target.closest('a[href^="#/"]');
  if (a) {
    if (a.hasAttribute('data-replace')) { e.preventDefault(); replace(a.getAttribute('href')); } else saveY();
    return;
  }
  const b = e.target.closest('[data-act]');
  if (b && !b.disabled) ACT[b.dataset.act](b);
});
// 새 화면이면 깊이 +1, 뒤로·앞으로면 그 칸의 깊이
addEventListener('hashchange', () => {
  if (history.state && 'd' in history.state) depth = history.state.d;
  else history.replaceState({ d: ++depth }, '');
  render();
});
addEventListener('pagehide', leave);
document.addEventListener('visibilitychange', () => { if (document.visibilityState === 'hidden') leave(); });

// ===== 시작: 본문 불러오기 =====
history.scrollRestoration = 'manual';
if (location.pathname.endsWith('/index.html')) history.replaceState(history.state, '', location.pathname.slice(0, -10) + location.hash);
fetch('data/notes.json')
  .then(r => { if (!r.ok) throw new Error(r.status); return r.json(); })
  .then(data => {
    D = data;
    D.questions.forEach((q, i) => { q.i = i; Q[q.id] = q; });
    D.subjects.forEach(s => { SUB[s.key] = s; });
    D.sims.forEach(s => { SIM[s.id] = s; });
    ORDER = D.questions.map(q => q.id);
    // 예전에 저장한 진도 중 지금 없는 질문은 버린다
    S.read = S.read.filter(id => Q[id]); S.confused = S.confused.filter(id => Q[id]);
    if (S.last && !Q[S.last.id]) S.last = null;
    depth = history.state && 'd' in history.state ? history.state.d : 0;
    history.replaceState({ ...history.state, d: depth }, '');
    render();
  })
  .catch(() => {
    app.innerHTML = `<div class="page"><header class="nav"><h1>CS 차곡</h1></header><main><section class="grp empty">
      <h2>내용을 불러오지 못했어요</h2><p>인터넷 연결을 확인하고 다시 열어 주세요.</p>
      <button class="cta" onclick="location.reload()">다시 열기</button></section></main></div>`;
  });
