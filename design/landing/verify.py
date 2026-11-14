# 랜딩 시안 검사 + 섹션 스크린샷 -> design/landing/shots/<폭>/*.png
# 실행: 프로젝트 루트에서 python3 -m http.server 8791 --bind 127.0.0.1 을 띄운 뒤 python3 design/landing/verify.py
# 구조(두 화면 같은 순서): 첫 화면 -> 기능 5개(휴대폰은 묶음 제목) -> 과목(머리에 숫자 4칸, 질문 카드는 앱의 그 질문 링크) -> 자주 묻는 질문 -> 끝 시작하기 -> 바닥글
# 넓은 화면(1440): 기능 5개는 붙은 폰 + 스크롤 걸음. 머리 시작하기는 첫 시작하기가 안 보일 때만.
# 좁은 화면(390, 360, 375x667 + 낮은 화면 390x664, 375x548, 320x568): 첫 화면은 한 화면 안(제목, 한 줄 설명, 시작하기, 폰 자동 재생, 점, 멈춤, 한 줄), 아래로 스크롤.
#       폰 폭 목표: 120(375x548, 320x568) / 150(나머지). 모자라면 폰 아래를 자른다.
#       기능 5개는 걸음마다 앱 화면 조각. 하단 고정 시작하기는 첫 시작하기도 끝 시작하기도 안 보일 때만.
# 검사: 가로 넘침(폰 화면 안쪽 제외, 섹션마다), 콘솔 오류, 누르는 영역 44 미만, 글의 em/en dash·큰따옴표(접힌 답 포함), 로고 누르면 맨 위,
#       첫 화면 배치(위에서 아래로 겹치지 않고 화면 안), 하단 고정·머리 시작하기가 보이는 조건(스크롤 위치마다),
#       자주 묻는 질문 하나씩 열고 닫기(aria-expanded, 답 칸 높이),
#       자동 재생(1초·5초·10초에 장면이 다름, 한 바퀴 1 2 3 4 5 뒤 1), 점 누르면 그 장면을 끝까지 보여 준 뒤 자동으로 다음,
#       탭 숨김이면 멈추고 다시 보이면 그 장면부터 이어서, 움직임 줄이기(자동 재생 없음, 점마다 끝 상태, 돌고 있는 움직임 0),
#       기록 있으면 시작하기 모두 이어서 공부하기(자동 이동 없음), 가로로 든 휴대폰(844x390)은 넘침·오류만
# 스플래시(휴대폰 세션 첫 방문): 1.6초 안에 끝나고 시작하기가 보임, 도는 동안 스크롤 잠금·자동 재생 안 함, 끝나면 첫 장면부터 자동 재생,
#       누르면 바로 건너뜀(시작하기 자리를 눌러도 앱으로 안 감), 같은 세션 다시 열면 안 나옴, 1440·움직임 줄이기에서 안 나옴.
#       진행 프레임 shots/390/splash-*.png (0.1, 0.4, 0.8, 1.1, 1.4초)
# 모두 누르기(390·1440): 보이는 링크·버튼·점·질문·멈춤·답 보기 조각·과목 질문 링크를 하나씩 새로 열어 실제로 눌러 누름 반응과 결과
#       (앱 주소, 과목 질문은 앱이 그 질문을 엶, 로고는 맨 위, 점은 그 장면, 질문은 열림, 멈춤은 장면 그대로, 답 보기는 답이 열림)를 잰다
# 그 밖(390): 폰 누르면 다음 장면, 멈춤 버튼(멈춤과 다시 이어짐), 폰이 화면 밖이면 자동 재생 쉼, 마지막 질문 답이 하단 버튼에 안 가림.
# 글자 대비: 폰 미리보기·스플래시 밖 글자가 4.5:1(큰 글자 3:1) 이상(섹션 스크린샷마다).
# 1440: 머리 시작하기는 끝 시작하기가 보여도 숨음, 첫 화면 QR
# 2회차 평가 뒤 더한 것: 장면 결과 상태(펼친 답, 다 찬 칸, +1 블록, ESTABLISHED, 헷갈림만 목록)가 0.8초 이상 보이는지 실측(390, 그리기마다 기록),
#       과목 질문 링크 8개가 notes.json 의 id·제목과 같은지, 누르면 앱(app/ 을 그대로 내줌)이 그 질문을 여는지(모두 누르기 안),
#       하단 고정 버튼 바탕이 과목 섹션(회색) 위에서 회색 픽셀, 흰 섹션 위에서 흰 픽셀(390),
#       줄 첫머리에 가운데점이 없고(첫 화면 한 줄) 숫자 설명 끝 줄이 한 단어만 남지 않음, 휴대폰 기능 묶음 제목이 걸음 1 위,
#       폭 300·310(사파리 글자 확대 125% 대용)에서 섹션마다 넘침·44·대비·오류, 스플래시 사본 사진(photos/sp) 840x840·장당 80KB 이하
import io, json, pathlib, re
from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent
APP_DIR = ROOT.parents[1] / 'app'
NOTES = {q['id']: q for q in json.loads((APP_DIR / 'data/notes.json').read_text(encoding='utf-8'))['questions']}
URL = 'http://127.0.0.1:8791/design/landing/index.html'
MOBILE = [(390, 844), (360, 780), (375, 667), (390, 664), (375, 548), (320, 568)]
NARROW = [(310, 675), (300, 534)]  # 사파리 글자 확대 125%: 390x844 -> 312, 375x667 -> 300
OLD_SHOTS = {(390, 844), (360, 780), (375, 667)}  # 예전 폴더 이름(폭만) 그대로, 새 크기는 폭x높이
PHONE_MIN = {(375, 548): 120, (320, 568): 120}  # 그 밖은 150
NO_SPLASH = "try { sessionStorage.setItem('cs-sp', '1') } catch (e) {}"
# 넓은 화면: 장면마다 타임라인이 끝나는 시간(ms) + 여유
WAIT = [2100, 4300, 2200, 3500, 3000]  # 걸음 5 는 컴퓨터만 거르기 2260
# 좁은 화면은 장면 안 시간을 SP=.55 배로 줄이고 0.8초 멈춘 뒤 다음(52fb3ee, HOLD 800 은 2회차 디자인 평가).
# 장면 1~5 가 자동으로 넘어가는 시간 NEXT_M = DUR * .55 + 800 (DUR 1900, 3600, 1800, 3100, 2800), 타임라인이 끝나 끝 상태가 보이는 시간 WAIT_M(< NEXT_M)
# 결과 상태가 되는 시간(ms * .55): 장면 1 펼침 1780, 2 마지막 칸 300 + 5 * 640, 3 +1 블록 1700, 4 마지막 단계 3 * 1100 - 300, 5 거르기 2660
NEXT_M = [1845, 2780, 1790, 2505, 2340]
WAIT_M = [1300, 2600, 1300, 2100, 1900]
HOLD_MIN = 800  # 장면 결과 상태가 보여야 하는 최소 시간
NAMES = ['01-reveal', '02-read', '03-tower', '04-sim', '05-conf']
SCR_END = ['q', 'q', 'tw', 'sim', 'toc']  # 장면마다 타임라인이 끝난 뒤 보이는 폰 화면
TITLES = ['답은 가려 두고, 먼저 떠올려요', '읽은 만큼 칸이 차요', '다 읽은 질문은 블록으로 쌓여요', '글로 어려운 건 움직여 봐요', '헷갈린 것만 다시 모아요']

# 넓은 화면: 걸음을 화면 가운데로
GO_STEP = """i => { const s = document.querySelectorAll('.lp-step')[i];
  window.scrollTo(0, s.getBoundingClientRect().top + scrollY - (innerHeight / 2 - s.offsetHeight / 2)); }"""
SCENE = """() => ({ step: [...document.querySelectorAll('.lp-step')].findIndex(s => s.classList.contains('on')), scr: document.querySelector('.scr.on').id })"""
# 좁은 화면 지금 장면: 점 번호 + 1 (점이 없으면 0), 폰 화면, 한 줄 설명
NOW = """() => ({ n: [...document.querySelectorAll('.lp-dots button')].findIndex(d => d.getAttribute('aria-current') === 'step') + 1,
  scr: document.querySelector('.scr.on').id, cap: document.querySelector('.lp-cap').textContent })"""
# 폰 화면 안쪽과 스플래시 창 안쪽(확대되며 들어오는 사진 컷, 창 모양으로 잘림)은 잘려서 넘치지 않는다
OVERFLOW = """() => [...document.querySelectorAll('body *')].filter(e => !e.closest('.lp-screen') && !e.closest('.sp-w') && !e.closest('svg[width="0"]')).filter(e => {
  const r = e.getBoundingClientRect(); return r.width && (r.right > innerWidth + .5 || r.left < -.5); }).map(e => e.tagName + '.' + e.className).slice(0, 10)"""
TAPS = """() => [...document.querySelectorAll('a, button, input, select, textarea, [role=button], [tabindex]')].filter(e => !e.closest('[inert]')).filter(e => {
  const cs = getComputedStyle(e), r = e.getBoundingClientRect(); return cs.visibility !== 'hidden' && cs.display !== 'none' && r.width > 0; })
  .map(e => { const r = e.getBoundingClientRect(); return { t: e.textContent.trim().slice(0, 20) || e.getAttribute('aria-label'), w: Math.round(r.width), h: Math.round(r.height) }; })"""
TEXT = """() => { const c = document.body.cloneNode(true); c.querySelectorAll('script, style, svg').forEach(e => e.remove()); const t = c.textContent; return { emdash: (t.match(/\\u2014/g) || []).length, endash: (t.match(/\\u2013/g) || []).length,
  dquote: (t.match(/["\\u201C\\u201D]/g) || []).length }; }"""
NO_SCROLL = "() => ({ scroll_h: document.scrollingElement.scrollHeight, inner_h: innerHeight, ok: document.scrollingElement.scrollHeight <= innerHeight })"
# 첫 화면 배치: 위에서 아래로 겹치지 않고, 모두 화면 안
FIRST = """() => { const H = innerHeight, order = ['.lp-h1', '.lp-sub', '[data-hero-cta]', '.lp-device', '.lp-dots', '.lp-cap'];
  const r = order.map(s => document.querySelector(s).getBoundingClientRect());
  return { viewport_h: H, bottoms: Object.fromEntries(order.map((s, i) => [s, Math.round(r[i].bottom)])),
    in_view: r.every(b => b.top >= 0 && b.bottom <= H + .5), stacked: r.every((b, i) => !i || r[i - 1].bottom <= b.top + .5),
    phone_w: Math.round(r[3].width), phone_h: Math.round(r[3].height), scale: document.querySelector('.lp-device').style.getPropertyValue('--s') }; }"""
# 움직임 줄이기 끝 상태: 1 답 가림, 2 칸 두 개 이상 참, 3 블록 +1, 4 시뮬레이션 4번째 단계, 5 목차 헷갈림만
# 장면 1 끝 그림은 가린 상태(한 줄 설명이 가린 것을 말함)
RM_END = """i => [() => document.querySelector('#q').classList.contains('on') && !document.querySelector('#q').classList.contains('rev'),
  () => [...document.querySelectorAll('#q [data-segs] b')].filter(b => b.style.getPropertyValue('--f') === '1').length >= 2,
  () => document.querySelector('#tw').classList.contains('plus'),
  () => document.querySelector('#sim [data-count]').textContent === '5단계 중 4번째',
  () => document.querySelector('#toc').classList.contains('cf') && document.querySelector('#toc').classList.contains('on')][i]()"""
RUNNING = """() => document.getAnimations().filter(a => a.playState === 'running' && (a.effect.getTiming().duration || 0) > 1).length"""
Q_REV = "() => document.querySelector('#q').classList.contains('rev')"
Q_FULL = "() => [...document.querySelectorAll('#q [data-segs] b')].every(b => b.style.getPropertyValue('--f') === '1')"
# 탭 숨김 흉내: document.hidden 을 바꾸고 visibilitychange 를 보낸다
HIDE = """h => { Object.defineProperty(document, 'hidden', { configurable: true, get: () => h });
  Object.defineProperty(document, 'visibilityState', { configurable: true, get: () => h ? 'hidden' : 'visible' }); document.dispatchEvent(new Event('visibilitychange')); }"""

SP_ON = "() => document.documentElement.classList.contains('sp-on') && !!document.getElementById('sp')"
LOCKED = "() => getComputedStyle(document.documentElement).overflowY === 'hidden'"
# 스플래시가 없어지는 순간: 첫 그리기부터 몇 ms, 그 순간의 장면(첫 장면 처음이면 점 1, 질문 화면, 답은 아직 가림)
SP_END = """() => new Promise(r => { const fp = (performance.getEntriesByName('first-paint')[0] || { startTime: 0 }).startTime;
  const iv = setInterval(() => { if (document.getElementById('sp')) return; clearInterval(iv);
    r({ end_from_first_paint_ms: Math.round(performance.now() - fp), end_from_nav_ms: Math.round(performance.now()),
        dot_at_end: [...document.querySelectorAll('.lp-dots button')].findIndex(d => d.hasAttribute('aria-current')) + 1,
        scr_at_end: document.querySelector('.scr.on').id, answer_open_at_end: document.querySelector('#q').classList.contains('rev') }); }, 10); })"""
# 첫 화면 시작하기가 화면 안에 있고, 그 자리를 덮은 것이 없음
START_SEEN = """() => { const b = document.querySelector('[data-hero-cta]'), r = b.getBoundingClientRect(), at = document.elementFromPoint(r.left + r.width / 2, r.top + r.height / 2);
  return { in_view: r.top >= 0 && r.bottom <= innerHeight, on_top: !!at && b.contains(at), opacity: getComputedStyle(b).opacity, scroll_y: scrollY }; }"""
# 섹션 스크린샷 자리(이름, 맨 위에 올 요소)
SECTIONS_M = [('09-steps-head', '.lp-steps-h')] + [(f'1{i}-feat-{i + 1}', f'.lp-step:nth-child({i + 1})') for i in range(5)] + [
    ('21-subjects', '.lp-subj'), ('22-faq', '.lp-faq'), ('24-end', '.lp-end')]
SECTIONS_D = [('07-subjects', '.lp-subj'), ('08-faq', '.lp-faq'), ('10-end', '.lp-end')]
TO_TOP = "s => document.querySelector(s).scrollIntoView({ block: 'start' })"
# 지금 스크롤 자리에서: 첫·끝 시작하기가 보이는지(머리 아래), 고정 시작하기가 보이는지, 덮인 것 없는지
CTA_NOW = """sel => { const vis = r => r.bottom > document.querySelector('.lp-nav').offsetHeight && r.top < innerHeight;
  const e = document.querySelector('[data-end-cta]').getBoundingClientRect();
  const hero = vis(document.querySelector('[data-hero-cta]').getBoundingClientRect()), end = e.bottom > 0 && e.top < innerHeight;
  const f = document.querySelector(sel), cs = getComputedStyle(f), r = f.getBoundingClientRect();
  const shown = cs.display !== 'none' && cs.visibility === 'visible' && +cs.opacity > .5 && r.top >= 0 && r.bottom <= innerHeight + .5;
  const at = shown && document.elementFromPoint(r.left + r.width / 2, r.top + r.height / 2);
  return { y: Math.round(scrollY), hero, end, shown, on_top: !shown || (!!at && f.contains(at)) }; }"""
# 자주 묻는 질문 i 번째: 펼침 상태, 답 칸 높이와 보임
QA = """i => { const b = document.querySelectorAll('.qa button')[i], a = document.getElementById(b.getAttribute('aria-controls'));
  return { q: b.textContent.trim(), expanded: b.getAttribute('aria-expanded'), h: Math.round(a.getBoundingClientRect().height), vis: getComputedStyle(a).visibility,
    others_open: [...document.querySelectorAll('.qa button')].filter(x => x !== b && x.getAttribute('aria-expanded') === 'true').length }; }"""
# 글자 대비: 글이 직접 든 요소마다 글자색(조상 투명도까지 섞음) 대 가장 가까운 바탕색. 폰 미리보기와 스플래시는 그림이라 뺀다
CONTRAST = """() => { const lin = v => (v /= 255) <= .03928 ? v / 12.92 : ((v + .055) / 1.055) ** 2.4;
  const lum = c => .2126 * lin(c[0]) + .7152 * lin(c[1]) + .0722 * lin(c[2]), rgba = s => (s.match(/[\\d.]+/g) || []).map(Number), bad = [];
  for (const e of document.querySelectorAll('body *')) {
    if (e.closest('.lp-screen, #sp, svg, script, style') || ![...e.childNodes].some(n => n.nodeType === 3 && n.textContent.trim())) continue;
    const cs = getComputedStyle(e); if (cs.visibility !== 'visible' || !e.getClientRects().length) continue;
    let op = 1, bg = null;
    for (let p = e; p && p !== document.documentElement; p = p.parentElement) { const s = getComputedStyle(p); op *= +s.opacity; const c = rgba(s.backgroundColor); if (!bg && (c.length === 3 || c[3] > 0)) bg = c; }
    if (op < .05) continue;  // 아직 올라오기 전
    bg = (bg || [255, 255, 255]).slice(0, 3);
    const f = rgba(cs.color), a = (f.length > 3 ? f[3] : 1) * op, fg = [0, 1, 2].map(i => f[i] * a + bg[i] * (1 - a));
    const l1 = lum(fg), l2 = lum(bg), ratio = (Math.max(l1, l2) + .05) / (Math.min(l1, l2) + .05);
    const px = parseFloat(cs.fontSize), large = px >= 24 || (px >= 18.66 && +cs.fontWeight >= 700);
    if (ratio < (large ? 3 : 4.5) - .005) bad.push(e.textContent.trim().slice(0, 20) + ' ' + ratio.toFixed(2));
  }
  return bad; }"""
# 마지막 질문을 연 뒤: 답 글 아래 끝이 하단 고정 시작하기(올라와 있으면) 위에 있음
LAST_FAQ = """() => { const q = [...document.querySelectorAll('.qa')].pop(), p = q.querySelector('.fa p').getBoundingClientRect(), d = document.querySelector('.lp-dock');
  const on = d.classList.contains('on'), top = on ? d.querySelector('.btn').getBoundingClientRect().top : innerHeight;
  return { text_bottom: Math.round(p.bottom - 20), limit: Math.round(top), dock_on: on, ok: p.bottom - 20 <= top + .5 }; }"""
PAUSED = "() => document.querySelector('.lp-pause').getAttribute('aria-pressed')"
# 글 줄: 요소마다 줄별 글(글자 하나씩 Range 로 위치를 재서 줄을 나눈다, 안 보이는 칸은 뺌)
LINES = """sel => [...document.querySelectorAll(sel)].filter(e => e.getClientRects().length).map(el => { const w = document.createTreeWalker(el, NodeFilter.SHOW_TEXT), out = []; let top = -1e9, n;
  while ((n = w.nextNode())) { if (!n.parentElement.getClientRects().length) continue;
    for (let i = 0; i < n.length; i++) { const r = document.createRange(); r.setStart(n, i); r.setEnd(n, i + 1); const b = r.getBoundingClientRect(); if (!b.width) continue;
      if (b.top > top + 4) { top = b.top; out.push(''); } out[out.length - 1] += n.data[i]; } }
  return out; })"""
# 장면 결과 상태 기록: 그리기마다 (점 번호 + 결과면 R) 이 바뀐 때를 적는다 -> [[ms, '2'], [ms, '2R'], [ms, '3'], ...]
HOLD_LOG = """ms => new Promise(res => { const t0 = performance.now(), log = []; let last = '';
  const st = () => { const n = [...document.querySelectorAll('.lp-dots button')].findIndex(d => d.hasAttribute('aria-current')) + 1, q = document.querySelector('#q'), toc = document.querySelector('#toc');
    const done = [false, q.classList.contains('rev'), [...q.querySelectorAll('[data-segs] b')].every(b => b.style.getPropertyValue('--f') === '1'),
      document.querySelector('#tw').classList.contains('plus'), document.querySelector('#sim [data-count]').textContent === '5단계 중 4번째',
      toc.classList.contains('cf') && toc.classList.contains('on')][n];
    return n + (done ? 'R' : ''); };
  const f = () => { const s = st(), t = performance.now() - t0; if (s !== last) { log.push([Math.round(t), s]); last = s; } t < ms ? requestAnimationFrame(f) : res(log); };
  f(); })"""
SUBJ_LINKS = """() => [...document.querySelectorAll('.lp-subj .subs > li')].map((li, k) => [...li.querySelectorAll('.qs a')].map(a => ({ k, href: a.getAttribute('href'), title: a.textContent.trim() }))).flat()"""
STEPS_HEAD = """() => { const h = document.querySelector('.lp-steps-h'), r = h.getBoundingClientRect(), s = document.querySelector('.lp-step').getBoundingClientRect();
  return { text: h.textContent, tag: h.tagName, visible: getComputedStyle(h).display !== 'none' && r.height > 20, above_step1: r.bottom <= s.top, step_tag: document.querySelector('.lp-step h3') ? 'H3' : '' }; }"""
SUBJ_KEYS = ['ds', 'os', 'db', 'net']


def lines_check(pg):
    # 줄 첫머리 가운데점 0(첫 화면 한 줄), 숫자 설명 끝 줄에 짧은 한 단어만 남은 것 0
    # (끝 줄이 한 단어이고 윗줄의 절반보다 짧을 때. 2회차 지적 `...따로 모아` / `봐요` 꼴. `움직여 보는` / `시뮬레이션` 처럼 고르게 나뉜 것은 괜찮음)
    sub, ks = pg.evaluate(LINES, '.lp-sub'), pg.evaluate(LINES, '.lp-subj .nums .k')
    starts = [ln[0] for el in sub for ln in el if ln]
    orphans = [el for el in ks if len(el) > 1 and ' ' not in el[-1].strip() and len(el[-1].strip()) * 2 < len(el[-2].strip())]
    return {'sub_lines': sub[0] if sub else [], 'line_start_dot': sum(c in '·' for c in starts), 'num_orphans': len(orphans), 'num_lines': ks}


def px(png, x, y):
    return Image.open(io.BytesIO(png)).convert('RGB').getpixel((x, y))
SEEK = "t => document.getAnimations().forEach(a => { a.pause(); a.currentTime = t; })"
FRAMES = [100, 400, 800, 1100, 1400]

# 모두 누르기: 보이는 링크·버튼(폰 미리보기 안쪽, 스플래시 제외)에 번호와 종류를 붙인다
CLICKABLE = """() => [...document.querySelectorAll('a[href], button, [role=button]')].filter(e => !e.closest('[inert]') && !e.closest('#sp') && e.getClientRects().length)
  .map((e, i) => { e.dataset.ck = i; const d = e.closest('.lp-dots') ? [...e.parentNode.children].indexOf(e) : -1;
    const kind = e.getAttribute('href') === './app/' ? 'start' : (e.getAttribute('href') || '').startsWith('./app/#/q/') ? 'subj' : d >= 0 ? 'dot' : e.closest('.qa') ? 'faq' : e.classList.contains('lp-brand') ? 'logo'
      : e.classList.contains('lp-pause') ? 'pause' : e.closest('[data-reveal]') ? 'reveal' : 'other';
    return { name: (e.textContent || e.getAttribute('aria-label') || '').trim().slice(0, 24), kind, dot: d, href: e.getAttribute('href'), title: e.textContent.trim(),
             where: e.closest('.lp-dock') ? 'dock' : e.closest('.lp-nav') ? 'nav' : e.closest('.lp-end') ? 'end' : e.closest('.lp-intro') ? 'hero' : '' }; })"""
LOOK = "e => { const s = getComputedStyle(e); return [s.transform, s.opacity, s.filter, s.backgroundColor].join('|'); }"
ON_TOP = "e => { const r = e.getBoundingClientRect(), at = document.elementFromPoint(r.left + r.width / 2, r.top + r.height / 2); return !!at && e.contains(at); }"
APP_URL = URL.rsplit('/', 1)[0] + '/app/'


def serve_app(route):
    rest = route.request.url.split('#')[0].split('?')[0].split('/design/landing/app/', 1)[1] or 'index.html'
    f = APP_DIR / rest
    route.fulfill(path=str(f)) if f.is_file() else route.fulfill(status=404, body='')


def dot(pg, i):
    pg.evaluate(f'document.querySelectorAll(".lp-dots button")[{i}].click()')


def watch(pg, errs):
    pg.on('console', lambda m: m.type == 'error' and errs.append(m.text))
    pg.on('pageerror', lambda e: errs.append(str(e)))
    return pg


def mctx(b, w=390, h=844, **kw):
    # 좁은 화면 문맥. 스플래시는 따로 재므로 기본은 건너뛴다
    ctx = b.new_context(viewport={'width': w, 'height': h}, has_touch=True, is_mobile=True, **kw)
    ctx.add_init_script(NO_SPLASH)
    return ctx


def press_all(b, w, h):
    # 하나씩 새로 열고, 머리·하단 고정은 가운데 자리(과목 섹션)로 내린 뒤, 나머지는 화면 가운데로 옮겨 누른다
    mob = w < 960
    ctx = b.new_context(viewport={'width': w, 'height': h}, has_touch=mob, is_mobile=mob, service_workers='block')
    ctx.add_init_script(NO_SPLASH)
    # 랜딩의 ./app/ 은 배포 구조(/ 랜딩, /app/ 앱) 기준이라, 로컬에서는 app/ 폴더를 그 주소로 그대로 내준다(과목 질문 링크가 앱의 그 질문을 여는지 보려고)
    ctx.route(re.compile(r'/design/landing/app/'), serve_app)
    # 콘솔 오류는 랜딩에서 난 것만 센다. 눌러서 넘어간 앱 쪽 오류는 따로 적는다(서비스 워커를 막으면 register 가 undefined 로 끝나 앱의 watchSw 가 reg.active 에서 멈춤, 검사 환경 탓)
    errs, app_errs = [], []; pg = ctx.new_page()
    pg.on('console', lambda m: m.type == 'error' and (app_errs if pg.url.startswith(APP_URL) else errs).append(m.text))
    pg.on('pageerror', lambda e: (app_errs if pg.url.startswith(APP_URL) else errs).append(str(e)))
    pg.goto(URL); pg.wait_for_timeout(900)
    items, res, hidden = pg.evaluate(CLICKABLE), [], []
    for i, it in enumerate(items):
        pg.goto(URL); pg.wait_for_timeout(900); pg.evaluate(CLICKABLE)
        el = pg.locator(f'[data-ck="{i}"]')
        if it['where'] in ('dock', 'nav'):
            pg.evaluate(TO_TOP, '.lp-subj'); pg.wait_for_timeout(700)
        else:
            el.evaluate("e => e.scrollIntoView({ block: 'center' })"); pg.wait_for_timeout(600)
        if el.evaluate("e => getComputedStyle(e).visibility === 'hidden'"):
            hidden.append(it['name']); continue
        y0, box, look0, top = pg.evaluate('scrollY'), el.bounding_box(), el.evaluate(LOOK), el.evaluate(ON_TOP)
        pg.mouse.move(box['x'] + box['width'] / 2, box['y'] + box['height'] / 2)
        pg.mouse.down(); pg.wait_for_timeout(220); look1 = el.evaluate(LOOK)
        pg.mouse.up(); pg.wait_for_timeout(300 if it['kind'] == 'dot' else 1500)
        url, y1 = pg.url, (pg.evaluate('scrollY') if pg.url == URL else None)
        k = it['kind']
        if k == 'start': moved = url == APP_URL
        elif k == 'subj':
            # 앱 주소 #/q/<id> 로 가고, 앱이 그 질문을 연다(문서 제목 = 질문 제목 · CS 차곡)
            moved = url == APP_URL + it['href'][len('./app/'):] and pg.title() == f"{it['title']} · CS 차곡"
        elif k == 'dot':
            now = pg.evaluate(NOW); moved = url == URL and now['n'] == it['dot'] + 1 and now['cap'] == TITLES[it['dot']]
        elif k == 'faq':
            qa = pg.evaluate(QA, pg.evaluate("e => [...document.querySelectorAll('.qa button')].indexOf(e)", el.element_handle()))
            moved = url == URL and qa['expanded'] == 'true' and qa['vis'] == 'visible' and qa['h'] > 20
        elif k == 'logo': moved = url == URL and y1 == 0 and y0 > 0
        elif k == 'pause':
            # 눌림(aria-pressed true)이고 3초 동안 장면이 그대로
            seq = sample(pg, 3000); moved = url == URL and pg.evaluate(PAUSED) == 'true' and len(set(n for _, n in seq)) == 1
        elif k == 'reveal':
            moved = url == URL and pg.evaluate("""() => { const f = document.querySelector('[data-reveal]'), a = f.querySelector('.ans');
              return f.classList.contains('rev') && a.getBoundingClientRect().height > 20 && !f.querySelector('.recall').getClientRects().length; }""")
        else: moved = False
        res.append({**it, 'w': round(box['width']), 'h': round(box['height']), 'on_top': top, 'pressed': look1 != look0,
                    'went': url.replace(URL.rsplit('/', 1)[0], '') + ('' if y1 is None else f' y={y1}'), 'ok': top and look1 != look0 and moved})
    ctx.close()
    kinds = {}
    for x in res: kinds[x['kind']] = kinds.get(x['kind'], 0) + 1
    return {'pressed_count': len(res), 'fail_count': sum(not x['ok'] for x in res), 'by_kind': kinds, 'bad': [x for x in res if not x['ok']],
            'hidden_not_pressed': hidden, 'items': res, 'console_errors': errs, 'app_side_errors': sorted(set(app_errs))}


def cta_check(pg, sel, use_end):
    # 맨 위부터 끝까지 화면 높이의 1/3 씩 내리며 고정 시작하기가 보이는 조건을 잰다.
    # 보여야 할 때: 첫 시작하기가 안 보임(그리고 휴대폰은 끝 시작하기도 안 보임). 그 밖에는 숨음
    H = pg.evaluate('document.documentElement.scrollHeight - innerHeight'); h = pg.evaluate('innerHeight')
    ys = sorted(set(list(range(0, H, max(1, h // 3))) + [H]))
    rows, bad = [], []
    for y in ys:
        pg.evaluate(f'window.scrollTo(0, {y})'); pg.wait_for_timeout(480)
        r = pg.evaluate(CTA_NOW, sel)
        want = not r['hero'] and not (use_end and r['end'])
        rows.append(r)
        if r['shown'] != want or not r['on_top'] or (r['shown'] and r['hero']): bad.append(r)
    pg.evaluate('window.scrollTo(0, 0)'); pg.wait_for_timeout(480); back = pg.evaluate(CTA_NOW, sel)
    return {'samples': len(rows), 'shown_count': sum(r['shown'] for r in rows), 'both_with_hero': sum(r['shown'] and r['hero'] for r in rows),
            'bad': bad, 'top_again_hidden': not back['shown'], 'ok': not bad and not back['shown'] and any(r['shown'] for r in rows)}


def faq_check(pg):
    # 질문마다 눌러 열고(aria-expanded true, 답 칸 보임) 다시 눌러 닫는다(false, 높이 0, 숨김). 다른 질문은 그대로
    n = pg.evaluate("document.querySelectorAll('.qa button').length"); out = []
    for i in range(n):
        btn = pg.locator('.qa button').nth(i)
        btn.evaluate("e => e.scrollIntoView({ block: 'center' })"); pg.wait_for_timeout(300)
        before = pg.evaluate(QA, i); btn.click(); pg.wait_for_timeout(450); opened = pg.evaluate(QA, i)
        btn.click(); pg.wait_for_timeout(450); closed = pg.evaluate(QA, i)
        ok = before['expanded'] == 'false' and before['h'] == 0 and before['vis'] == 'hidden' \
            and opened['expanded'] == 'true' and opened['h'] > 20 and opened['vis'] == 'visible' and opened['others_open'] == 0 \
            and closed['expanded'] == 'false' and closed['h'] == 0 and closed['vis'] == 'hidden'
        out.append({'q': before['q'], 'open_h': opened['h'], 'ok': ok})
    return {'count': n, 'ok': n >= 3 and all(x['ok'] for x in out), 'items': out}


def sample(pg, until_ms, every=250):
    # 열고 나서 until_ms 까지 every 마다 지금 장면을 적는다 -> [(ms, 장면)]
    t0 = pg.evaluate('performance.now()'); out = []
    while True:
        t = pg.evaluate('performance.now()') - t0
        if t > until_ms: return out
        out.append((round(t), pg.evaluate(NOW)['n'])); pg.wait_for_timeout(every)


def at(seq, ms):
    return next((n for t, n in reversed(seq) if t <= ms), None)


def order(seq):
    o = []
    for _, n in seq:
        if not o or o[-1] != n: o.append(n)
    return o


out = {}
with sync_playwright() as pw:
    b = pw.chromium.launch()

    # ---- 좁은 화면: 스플래시, 첫 화면, 장면 스크린샷(점 눌러서), 로고 ----
    for w, h in MOBILE:
        d = ROOT / 'shots' / (str(w) if (w, h) in OLD_SHOTS else f'{w}x{h}'); d.mkdir(parents=True, exist_ok=True)
        for f in d.glob('*.png'): f.unlink()
        ctx = b.new_context(viewport={'width': w, 'height': h}, device_scale_factor=2, has_touch=True, is_mobile=True)
        errs = []; pg = watch(ctx.new_page(), errs)
        pg.goto(URL, wait_until='domcontentloaded')
        # 도는 동안: 0.4초에 보이는지, 잠금, 가로 넘침, 휠로 안 내려감, 자동 재생 안 함(점 없음, 폰은 홈)
        pg.wait_for_timeout(400)
        sp = {'shown': pg.evaluate(SP_ON), 'locked': pg.evaluate(LOCKED), 'overflow_during': pg.evaluate(OVERFLOW),
              'scroll_w': pg.evaluate('document.documentElement.scrollWidth'), 'scene_during': pg.evaluate(NOW)['n'], 'scr_during': pg.evaluate(NOW)['scr']}
        pg.mouse.move(w / 2, h / 2); pg.mouse.wheel(0, 600); pg.wait_for_timeout(100); sp['scroll_y_after_wheel'] = pg.evaluate('scrollY')
        sp.update(pg.evaluate(SP_END)); sp['locked_after'] = pg.evaluate(LOCKED); sp['start_after'] = pg.evaluate(START_SEEN)
        pg.wait_for_timeout(1200); sp['answer_open_1200ms_after'] = pg.evaluate(Q_REV); sp['scene_1200ms_after'] = pg.evaluate(NOW)['n']  # 첫 장면을 처음부터 돌렸다는 증거
        sp['ok'] = sp['shown'] and sp['locked'] and not sp['overflow_during'] and sp['scroll_w'] <= w and sp['scroll_y_after_wheel'] == 0 \
            and sp['scene_during'] == 0 and sp['scr_during'] == 'home' and sp['end_from_first_paint_ms'] <= 1600 \
            and not sp['locked_after'] and sp['start_after']['in_view'] and sp['start_after']['on_top'] \
            and sp['dot_at_end'] == 1 and sp['scr_at_end'] == 'q' and not sp['answer_open_at_end'] and sp['answer_open_1200ms_after'] and sp['scene_1200ms_after'] == 1
        # 같은 세션(같은 탭)에서 다시 열면 안 나온다
        pg.goto(URL, wait_until='domcontentloaded'); sp['shown_again_same_session'] = pg.evaluate(SP_ON)
        pg.evaluate('document.fonts.ready'); pg.wait_for_timeout(1500)
        r = {'splash': sp, 'overflow': [], 'small_taps': [], 'scroll_w': [], 'low_contrast': [], 'first_screen': pg.evaluate(FIRST)}
        r['first_screen']['page_scrolls'] = pg.evaluate('document.documentElement.scrollHeight > innerHeight')
        r['first_screen']['phone_cut'] = pg.evaluate("document.querySelector('.lp-device').classList.contains('cut')")
        r['first_screen']['phone_min'] = PHONE_MIN.get((w, h), 150)
        r['lines'] = lines_check(pg)
        r['steps_head'] = pg.evaluate(STEPS_HEAD); r['steps_head']['ok'] = r['steps_head']['visible'] and r['steps_head']['above_step1'] and r['steps_head']['tag'] == 'H2' and r['steps_head']['step_tag'] == 'H3'
        def look(name):
            pg.screenshot(path=str(d / f'{name}.png'))
            r['overflow'] += pg.evaluate(OVERFLOW)
            r['low_contrast'] += pg.evaluate(CONTRAST)
            r['small_taps'] += [t for t in pg.evaluate(TAPS) if t['w'] < 44 or t['h'] < 44]
            r['scroll_w'].append(pg.evaluate('document.documentElement.scrollWidth'))
        look('00-first')
        steps = []
        for i, name in enumerate(NAMES):
            dot(pg, i); pg.wait_for_timeout(WAIT_M[i]); look(name)
            s = pg.evaluate(NOW)
            steps.append({**s, 'ok': s['n'] == i + 1 and s['scr'] == SCR_END[i] and s['cap'] == TITLES[i]})
        r['steps'] = steps
        # 첫 화면 아래 섹션: 기능 5개(앱 화면 조각), 숫자, 과목, 질문(첫 질문 연 것도), 끝, 맨 아래
        for name, sel in SECTIONS_M:
            pg.evaluate(TO_TOP, sel); pg.wait_for_timeout(700); look(name)
        pg.evaluate(TO_TOP, '.lp-faq'); pg.wait_for_timeout(300)
        pg.locator('.qa button').first.click(); pg.wait_for_timeout(450); look('23-faq-open')
        pg.locator('.qa button').first.click(); pg.wait_for_timeout(450)
        pg.evaluate('window.scrollTo(0, document.body.scrollHeight)'); pg.wait_for_timeout(700); look('25-bottom')
        # 휴대폰은 머리 시작하기 대신 하단 고정 시작하기
        r['nav_cta_display'] = pg.evaluate("getComputedStyle(document.querySelector('.lp-nav .btn')).display")
        r['dock'] = cta_check(pg, '.lp-dock', True)
        r['faq'] = faq_check(pg)
        # 로고: 내려간 자리에서 누르면 다시 불러오지 않고 맨 위
        pg.evaluate(TO_TOP, '.lp-subj'); pg.wait_for_timeout(500); y0 = pg.evaluate('scrollY')
        pg.click('a.lp-brand'); pg.wait_for_timeout(1500)
        r['logo'] = {'from_y': y0, 'scroll_y': pg.evaluate('scrollY'), 'url_same': pg.url == URL}
        r['logo']['ok'] = y0 > 0 and r['logo']['scroll_y'] == 0 and r['logo']['url_same']
        # 시작하기 자리를 눌러 스플래시를 건너뛰어도 앱으로 안 간다(새 탭 = 새 세션)
        p2 = watch(ctx.new_page(), errs)
        p2.goto(URL, wait_until='domcontentloaded'); p2.wait_for_timeout(300)
        shown = p2.evaluate(SP_ON); c = p2.evaluate("() => { const r = document.querySelector('[data-hero-cta]').getBoundingClientRect(); return [r.left + r.width / 2, r.top + r.height / 2]; }")
        p2.touchscreen.tap(*c); p2.wait_for_timeout(80)
        r['splash']['tap_skip'] = {'shown_before': shown, 'gone_80ms': not p2.evaluate("!!document.getElementById('sp')"), 'unlocked': not p2.evaluate(LOCKED),
                                   'url_same': p2.url == URL, 'scene_after': p2.evaluate(NOW)['n']}
        p2.close()
        r['text'] = pg.evaluate(TEXT)
        if (w, h) == (390, 844):
            links = pg.evaluate(SUBJ_LINKS)
            for x in links:
                q = NOTES.get(x['href'].rsplit('/', 1)[-1]); x['ok'] = x['href'].startswith('./app/#/q/') and bool(q) and q['title'] == x['title'] and q['s'] == SUBJ_KEYS[x['k']]
            out['subj_links'] = {'count': len(links), 'items': links, 'ok': len(links) == 8 and all(x['ok'] for x in links)}
        r['console_errors'] = errs
        r['small_taps'] = list({json.dumps(t, ensure_ascii=False): t for t in r['small_taps']}.values())
        r['overflow'] = sorted(set(r['overflow']))
        r['scroll_w_max'] = max(r.pop('scroll_w'))
        r['low_contrast'] = sorted(set(r['low_contrast']))
        out[f'{w}x{h}'] = r
        ctx.close()

    # ---- 넓은 화면(1440): 스크롤 장면 그대로 ----
    w, h = 1440, 900
    d = ROOT / 'shots' / str(w); d.mkdir(parents=True, exist_ok=True)
    for f in d.glob('*.png'): f.unlink()
    ctx = b.new_context(viewport={'width': w, 'height': h}, device_scale_factor=2)
    errs = []; pg = watch(ctx.new_page(), errs)
    pg.goto(URL, wait_until='domcontentloaded')
    r = {'splash': {'shown': pg.evaluate(SP_ON)}, 'overflow': [], 'small_taps': [], 'low_contrast': []}
    pg.evaluate('document.fonts.ready'); pg.wait_for_timeout(1500)
    # 첫 화면: 글 묶음이 폰과 세로 가운데, 시작하기 아래 QR
    r['first'] = pg.evaluate("""() => { const i = document.querySelector('.lp-intro'), k = [...i.children].filter(e => e.getClientRects().length).map(e => e.getBoundingClientRect());
      const mid = (k[0].top + k[k.length - 1].bottom) / 2, d = document.querySelector('.lp-device').getBoundingClientRect(), q = document.querySelector('.lp-qr svg').getBoundingClientRect();
      return { text_mid: Math.round(mid), phone_mid: Math.round((d.top + d.bottom) / 2), qr_w: Math.round(q.width), qr_below_start: q.top > document.querySelector('[data-hero-cta]').getBoundingClientRect().bottom }; }""")
    r['first']['ok'] = abs(r['first']['text_mid'] - r['first']['phone_mid']) <= 40 and r['first']['qr_w'] >= 80 and r['first']['qr_below_start']
    r['lines'] = lines_check(pg); r['steps_head_hidden'] = not pg.evaluate(STEPS_HEAD)['visible']
    def look(name):
        pg.screenshot(path=str(d / f'{name}.png'))
        r['overflow'] += pg.evaluate(OVERFLOW)
        r['low_contrast'] += pg.evaluate(CONTRAST)
        r['small_taps'] += [t for t in pg.evaluate(TAPS) if t['w'] < 44 or t['h'] < 44]
    look('00-first')
    r['dots_cap_hidden'] = pg.evaluate("() => !document.querySelector('.lp-dots').getClientRects().length && !document.querySelector('.lp-cap').getClientRects().length")
    steps = []
    for i, name in enumerate(NAMES):
        pg.evaluate(GO_STEP, i); pg.wait_for_timeout(WAIT[i]); look(name)
        s = pg.evaluate(SCENE)
        steps.append({'step_on': s['step'], 'scr': s['scr'], 'ok': s['step'] == i and s['scr'] == SCR_END[i]})
    r['steps'] = steps
    for name, sel in SECTIONS_D:
        pg.evaluate(TO_TOP, sel); pg.wait_for_timeout(700); look(name)
    pg.evaluate(TO_TOP, '.lp-faq'); pg.wait_for_timeout(300)
    pg.locator('.qa button').first.click(); pg.wait_for_timeout(450); look('09-faq-open')
    pg.locator('.qa button').first.click(); pg.wait_for_timeout(450)
    pg.evaluate('window.scrollTo(0, document.body.scrollHeight)'); pg.wait_for_timeout(700); look('11-bottom')
    r['scroll_w'] = pg.evaluate('document.documentElement.scrollWidth')
    r['dock_display'] = pg.evaluate("getComputedStyle(document.querySelector('.lp-dock')).display")
    r['nav_cta'] = cta_check(pg, '.lp-nav .btn', True)  # 끝 시작하기가 보이면 머리 시작하기도 숨음
    r['faq'] = faq_check(pg)
    pg.evaluate('window.scrollTo(0, document.body.scrollHeight)'); pg.wait_for_timeout(500); y0 = pg.evaluate('scrollY')
    pg.click('a.lp-brand'); pg.wait_for_timeout(1500)
    r['logo'] = {'from_y': y0, 'scroll_y': pg.evaluate('scrollY'), 'url_same': pg.url == URL, 'scr_at_top': pg.evaluate(SCENE)['scr']}
    r['logo']['ok'] = y0 > 0 and r['logo']['scroll_y'] == 0 and r['logo']['url_same'] and r['logo']['scr_at_top'] == 'home'
    r['text'] = pg.evaluate(TEXT); r['console_errors'] = errs
    r['small_taps'] = list({json.dumps(t, ensure_ascii=False): t for t in r['small_taps']}.values())
    r['overflow'] = sorted(set(r['overflow'])); r['low_contrast'] = sorted(set(r['low_contrast']))
    out['1440x900'] = r
    ctx.close()

    # ---- 자동 재생(390): 열고 23초 동안 장면을 적는다. 1초·5초·10초 장면이 서로 다르고, 1 2 3 4 5 다음 1 ----
    ctx = mctx(b); errs = []; pg = watch(ctx.new_page(), errs)
    pg.goto(URL, wait_until='domcontentloaded')
    seq = sample(pg, 23000)
    a1, a5, a10 = at(seq, 1000), at(seq, 5000), at(seq, 10000)
    out['autoplay_390'] = {'at_1s': a1, 'at_5s': a5, 'at_10s': a10, 'order': order(seq), 'console_errors': errs,
                           'ok': len({a1, a5, a10}) == 3 and order(seq)[:6] == [1, 2, 3, 4, 5, 1]}
    ctx.close()

    # ---- 장면 결과 상태 실측(390): 한 바퀴 넘게 그리기마다 기록. 결과가 된 때부터 다음 장면까지 0.8초 이상 ----
    ctx = mctx(b); errs = []; pg = watch(ctx.new_page(), errs)
    pg.goto(URL, wait_until='domcontentloaded')
    log = pg.evaluate(HOLD_LOG, 13500); holds = {}
    for i, (t, s) in enumerate(log):
        if s.endswith('R') and s[:-1] not in holds:
            nxt = next((t2 for t2, s2 in log[i + 1:] if s2.rstrip('R') != s[:-1]), None)
            if nxt is not None: holds[s[:-1]] = nxt - t
    starts = [t for t, s in log if s == '1']
    out['result_hold_390'] = {'hold_ms': holds, 'min_ms': min(holds.values()) if holds else 0, 'cycle_ms': starts[1] - starts[0] if len(starts) > 1 else None,
                              'log': log, 'console_errors': errs, 'ok': sorted(holds) == ['1', '2', '3', '4', '5'] and min(holds.values()) >= HOLD_MIN}
    ctx.close()

    # ---- 하단 고정 버튼 바탕(390): 과목 섹션(회색) 가운데에서 버튼 위·아래 픽셀이 회색, 자주 묻는 질문(흰)에서는 흰색 ----
    ctx = mctx(b); errs = []; pg = watch(ctx.new_page(), errs)
    pg.goto(URL); pg.evaluate('document.fonts.ready'); pg.wait_for_timeout(600)
    dk = {}
    for name, sel in [('subjects', '.lp-subj'), ('faq', '.lp-faq')]:
        pg.evaluate("s => { const e = document.querySelector(s); scrollTo(0, e.getBoundingClientRect().top + scrollY + e.offsetHeight / 2 - innerHeight / 2); }", sel); pg.wait_for_timeout(700)
        bx = pg.evaluate("() => { const r = document.querySelector('.lp-dock .btn').getBoundingClientRect(); return { top: r.top, bottom: r.bottom, on: document.querySelector('.lp-dock').classList.contains('on') }; }")
        png = pg.screenshot(); dk[name] = {'dock_on': bx['on'], 'above': px(png, 8, int(bx['top']) - 4), 'below': px(png, 8, int(bx['bottom']) + 4)}
    near = lambda c, ref: all(abs(x - y) <= 2 for x, y in zip(c, ref))
    out['dock_bg_390'] = {**dk, 'console_errors': errs, 'ok': all(v['dock_on'] for v in dk.values())
                          and near(dk['subjects']['above'], (242, 244, 246)) and near(dk['subjects']['below'], (242, 244, 246))
                          and near(dk['faq']['above'], (255, 255, 255)) and near(dk['faq']['below'], (255, 255, 255))}
    ctx.close()

    # ---- 좁은 폭(310x675, 300x534): 섹션마다 가로 넘침, 누르는 영역 44, 대비, 콘솔 오류, 줄 첫머리 가운데점, 멈춤 버튼이 점과 안 겹침 ----
    for w, h in NARROW:
        ctx = mctx(b, w, h); errs = []; pg = watch(ctx.new_page(), errs)
        pg.goto(URL); pg.evaluate('document.fonts.ready'); pg.wait_for_timeout(1200)
        nr = {'overflow': [], 'small_taps': [], 'low_contrast': [], 'scroll_w': []}
        for sel in [None, '.lp-steps-h', '.lp-step:nth-child(3)', '.lp-subj', '.lp-faq', '.lp-end']:
            if sel: pg.evaluate(TO_TOP, sel); pg.wait_for_timeout(600)
            nr['overflow'] += pg.evaluate(OVERFLOW); nr['low_contrast'] += pg.evaluate(CONTRAST)
            nr['small_taps'] += [t for t in pg.evaluate(TAPS) if t['w'] < 44 or t['h'] < 44]; nr['scroll_w'].append(pg.evaluate('document.documentElement.scrollWidth'))
        pg.evaluate('window.scrollTo(0, 0)'); pg.wait_for_timeout(400)
        nr['pause_box'] = pg.evaluate("() => { const r = document.querySelector('.lp-pause').getBoundingClientRect(), d = document.querySelector('.lp-dots').getBoundingClientRect(); return { left: Math.round(r.left), right: Math.round(r.right), dots_right: Math.round(d.right), in_view: r.right <= innerWidth, no_overlap: r.left >= d.right - .5 }; }")
        nr['lines'] = lines_check(pg)
        nr['overflow'] = sorted(set(nr['overflow'])); nr['low_contrast'] = sorted(set(nr['low_contrast']))
        nr['small_taps'] = list({json.dumps(t, ensure_ascii=False): t for t in nr['small_taps']}.values()); nr['scroll_w_max'] = max(nr.pop('scroll_w'))
        nr['scroll_w_ok'] = nr['scroll_w_max'] <= w
        nr['console_errors'] = errs
        out[f'narrow_{w}x{h}'] = nr
        ctx.close()

    # ---- 점 누르기(390): 장면 1 이 넘어가기 직전(1.4초)에 점 2 를 누르면, 장면 2 를 끝까지 보여 준 뒤 3 으로. 점 5 다음은 1 ----
    ctx = mctx(b); errs = []; pg = watch(ctx.new_page(), errs)
    pg.goto(URL, wait_until='domcontentloaded'); pg.wait_for_timeout(1400)
    n = lambda: pg.evaluate(NOW)['n']
    before = n(); dot(pg, 1)
    pg.wait_for_timeout(600); a = n()  # 장면 1 이 넘어갈 1.85초를 지나도 장면 2
    pg.wait_for_timeout(NEXT_M[1] - 400 - 600); b_, full = n(), pg.evaluate(Q_FULL)  # 넘어가기 0.4초 전: 아직 2, 칸이 다 참(끝까지 보여 줌)
    pg.wait_for_timeout(1200); c = n()  # 그다음 자동으로 3
    dot(pg, 4); pg.wait_for_timeout(NEXT_M[4] - 400); d5, cf = n(), pg.evaluate("document.querySelector('#toc').classList.contains('cf')")
    pg.wait_for_timeout(1000); e1 = n()  # 5 다음은 1
    dot2 = {'scene_before_press': before, 'at_0_6s': a, 'at_next_minus_0_4s': b_, 'segs_full_before_next': full, 'at_next_plus_0_8s': c,
            'dot5_at_next_minus_0_4s': d5, 'dot5_conf_filtered': cf, 'dot5_at_next_plus_0_6s': e1,
            'ok': before == 1 and a == 2 and b_ == 2 and full and c == 3 and d5 == 5 and cf and e1 == 1}
    dot2['console_errors'] = errs
    out['dot_then_auto_390'] = dot2
    ctx.close()

    # ---- 탭 숨김(390): 0.5초에 숨기고 4초 기다려도 장면 1 그대로, 다시 보이면 장면 1 부터 이어서 1.5초 뒤 장면 2 ----
    ctx = mctx(b); errs = []; pg = watch(ctx.new_page(), errs)
    pg.goto(URL, wait_until='domcontentloaded'); pg.wait_for_timeout(500)
    pg.evaluate(HIDE, True); hid = pg.evaluate(NOW)['n']; pg.wait_for_timeout(4000); still_hidden = pg.evaluate(NOW)['n']
    pg.evaluate(HIDE, False); pg.wait_for_timeout(300); back = pg.evaluate(NOW)['n']; open_at_300 = pg.evaluate(Q_REV)
    pg.wait_for_timeout(NEXT_M[0] - 300 + 500); after = pg.evaluate(NOW)['n']
    out['tab_hidden_390'] = {'scene_when_hidden': hid, 'scene_after_4s_hidden': still_hidden, 'scene_300ms_after_back': back,
                             'answer_open_300ms_after_back': open_at_300, 'scene_3s_after_back': after, 'console_errors': errs,
                             'ok': hid == 1 and still_hidden == 1 and back == 1 and not open_at_300 and after == 2}
    ctx.close()

    # ---- 폰 누르기(390): 첫 화면 폰을 누르면 바로 다음 장면 ----
    ctx = mctx(b); errs = []; pg = watch(ctx.new_page(), errs)
    pg.goto(URL); pg.wait_for_timeout(600); n0 = pg.evaluate(NOW)['n']
    pg.locator('.lp-device').tap(); pg.wait_for_timeout(150); n1 = pg.evaluate(NOW)['n']
    pg.locator('.lp-device').tap(); pg.wait_for_timeout(150); n2 = pg.evaluate(NOW)['n']
    out['phone_tap_390'] = {'before': n0, 'after_tap': n1, 'after_tap2': n2, 'console_errors': errs, 'ok': n1 == n0 % 5 + 1 and n2 == n1 % 5 + 1}
    ctx.close()

    # ---- 멈춤 버튼(390): 누르면 aria-pressed true, 4초 동안 장면 그대로. 다시 누르면 false, 3.5초 안에 다음 장면 ----
    ctx = mctx(b); errs = []; pg = watch(ctx.new_page(), errs)
    pg.goto(URL); pg.wait_for_timeout(600)
    pg.locator('.lp-pause').tap(); p1 = pg.evaluate(PAUSED); s1 = sample(pg, 4000)
    pg.locator('.lp-pause').tap(); p2 = pg.evaluate(PAUSED); s2 = sample(pg, 3500)
    out['pause_390'] = {'pressed_after_1st': p1, 'scenes_while_paused': order(s1), 'pressed_after_2nd': p2, 'scenes_after_resume': order(s2), 'console_errors': errs,
                        'ok': p1 == 'true' and len(order(s1)) == 1 and p2 == 'false' and len(order(s2)) >= 2}
    ctx.close()

    # ---- 화면 밖(390): 자주 묻는 질문까지 내리면 4초 동안 장면 그대로, 다시 올라오면 3.5초 안에 다음 장면 ----
    ctx = mctx(b); errs = []; pg = watch(ctx.new_page(), errs)
    pg.goto(URL); pg.wait_for_timeout(600)
    pg.evaluate(TO_TOP, '.lp-faq'); pg.wait_for_timeout(200); s1 = sample(pg, 4000)
    pg.evaluate('window.scrollTo(0, 0)'); pg.wait_for_timeout(200); s2 = sample(pg, 3500)
    out['offscreen_390'] = {'scenes_while_away': order(s1), 'scenes_after_back': order(s2), 'console_errors': errs,
                            'ok': len(order(s1)) == 1 and len(order(s2)) >= 2}
    ctx.close()

    # ---- 마지막 질문(390): 하단 고정 시작하기 바로 위에서 열어도 답 글이 그 버튼에 안 가림 ----
    ctx = mctx(b); errs = []; pg = watch(ctx.new_page(), errs)
    pg.goto(URL); pg.wait_for_timeout(600)
    pg.evaluate("() => { const b = [...document.querySelectorAll('.qa button')].pop(); scrollTo(0, b.getBoundingClientRect().bottom + scrollY - (innerHeight - 100)); }")
    pg.wait_for_timeout(600); dock_before = pg.evaluate("document.querySelector('.lp-dock').classList.contains('on')")
    pg.locator('.qa button').last.click(); pg.wait_for_timeout(1000)
    out['last_faq_390'] = {**pg.evaluate(LAST_FAQ), 'dock_on_before': dock_before, 'console_errors': errs}
    ctx.close()

    # ---- 움직임 줄이기(390): 스플래시 없음, 자동 재생 없음(6초 뒤에도 장면 1), 점마다 바로 끝 상태, 돌고 있는 움직임 0 ----
    # 스플래시가 안 나오는 것도 재므로 건너뛰기 스크립트 없이 연다
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, has_touch=True, is_mobile=True, reduced_motion='reduce')
    errs = []; pg = watch(ctx.new_page(), errs)
    pg.goto(URL, wait_until='domcontentloaded'); rm_splash = pg.evaluate(SP_ON)
    pg.evaluate('document.fonts.ready'); pg.wait_for_timeout(6000)
    first = {'scene': pg.evaluate(NOW)['n'], 'end_state': pg.evaluate(RM_END, 0), 'running': pg.evaluate(RUNNING)}
    rm = []
    for i in range(5):
        dot(pg, i); pg.wait_for_timeout(300)
        rm.append({'scene': pg.evaluate(NOW)['n'], 'end_state': pg.evaluate(RM_END, i), 'running': pg.evaluate(RUNNING), 'scr': pg.evaluate(NOW)['scr']})
    pg.wait_for_timeout(6000); last = pg.evaluate(NOW)['n']
    out['reduced_motion_390'] = {'splash_shown': rm_splash, 'after_6s': first, 'dots': rm, 'scene_6s_after_last_dot': last, 'console_errors': errs,
                                 'ok': not rm_splash and first['scene'] == 1 and first['end_state'] and first['running'] == 0
                                 and all(x['scene'] == i + 1 and x['end_state'] and x['running'] == 0 for i, x in enumerate(rm)) and last == 5}
    ctx.close()

    # ---- 기록이 있으면 시작하기 버튼 모두 이어서 공부하기, 자동 이동 없음 (390) ----
    ctx = mctx(b); pg = ctx.new_page()
    pg.goto(URL); pg.evaluate("localStorage.setItem('cs-chagok', JSON.stringify({ read: ['ds-array'], confused: [], last: null }))")
    pg.goto(URL); pg.wait_for_timeout(1000)
    out['record'] = {'url_unchanged': pg.url == URL,
                     'start_texts': pg.evaluate("""[...document.querySelectorAll('a.btn.pri[href="./app/"]')].map(a => a.textContent)""")}
    out['record']['ok'] = out['record']['url_unchanged'] and len(out['record']['start_texts']) == 4 and all(t == '이어서 공부하기' for t in out['record']['start_texts'])
    ctx.close()

    # ---- 가로로 든 휴대폰(844x390): 아주 낮은 화면은 스크롤 허용. 가로 넘침과 오류만 ----
    ctx = mctx(b, 844, 390); errs = []; pg = watch(ctx.new_page(), errs)
    pg.goto(URL); pg.evaluate('document.fonts.ready'); pg.wait_for_timeout(1200)
    out['landscape_844x390'] = {'overflow': pg.evaluate(OVERFLOW), 'scroll': pg.evaluate(NO_SCROLL), 'console_errors': errs}
    ctx.close()

    # ---- 스플래시 진행 프레임 (390) ----
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, has_touch=True, is_mobile=True); pg = ctx.new_page()
    pg.clock.install(); pg.goto(URL)  # load 는 사진을 다 받은 뒤
    out['splash_frames_390'] = {'photos_loaded': pg.evaluate("[...document.querySelectorAll('#sp .sp-ph')].map(e => e.classList.contains('ok'))"), 'files': []}
    for t in FRAMES:
        pg.evaluate(SEEK, t); pg.wait_for_timeout(100)
        f = ROOT / 'shots' / '390' / f'splash-{t:04d}.png'; pg.screenshot(path=str(f)); out['splash_frames_390']['files'].append(f.name)
    ctx.close()

    out['press_all'] = {f'{w}x{h}': press_all(b, w, h) for w, h in [(390, 844), (1440, 900)]}
    b.close()

# 한눈에 보는 요약(맨 위) + 자세한 값(detail)
S = {}
for w, h in MOBILE:
    k = f'{w}x{h}'; r = out[k]; ts = r['splash']['tap_skip']; fs = r['first_screen']
    S[k] = {'phone_w': fs['phone_w'], 'phone_ok': fs['phone_w'] >= fs['phone_min'], 'phone_cut': fs['phone_cut'], 'low_contrast': len(r['low_contrast']), 'overflow': len(r['overflow']), 'scroll_w_max': r['scroll_w_max'], 'small_taps': len(r['small_taps']), 'console_errors': len(r['console_errors']),
            'first_screen_in_view': r['first_screen']['in_view'] and r['first_screen']['stacked'], 'page_scrolls': r['first_screen']['page_scrolls'],
            'scenes_ok': all(x['ok'] for x in r['steps']), 'splash_ok': r['splash']['ok'] and not r['splash']['shown_again_same_session']
            and ts['shown_before'] and ts['gone_80ms'] and ts['unlocked'] and ts['url_same'], 'dock_ok': r['dock']['ok'],
            'dock_samples': r['dock']['samples'], 'dock_shown': r['dock']['shown_count'], 'dock_with_hero': r['dock']['both_with_hero'],
            'faq_ok': r['faq']['ok'], 'logo_ok': r['logo']['ok'], 'nav_cta_hidden': r['nav_cta_display'] == 'none', 'text': r['text'],
            'line_start_dot': r['lines']['line_start_dot'], 'num_orphans': r['lines']['num_orphans'], 'steps_head_ok': r['steps_head']['ok']}
for w, h in NARROW:
    r = out[f'narrow_{w}x{h}']
    S[f'narrow_{w}x{h}'] = {'overflow': len(r['overflow']), 'scroll_w_ok': r['scroll_w_ok'], 'small_taps': len(r['small_taps']), 'low_contrast': len(r['low_contrast']),
                            'console_errors': len(r['console_errors']), 'line_start_dot': r['lines']['line_start_dot'], 'num_orphans': r['lines']['num_orphans'],
                            'pause_in_view': r['pause_box']['in_view'], 'pause_no_overlap': r['pause_box']['no_overlap']}
r = out['1440x900']
S['1440x900'] = {'first_ok': r['first']['ok'], 'low_contrast': len(r['low_contrast']), 'overflow': len(r['overflow']), 'scroll_w': r['scroll_w'], 'small_taps': len(r['small_taps']), 'console_errors': len(r['console_errors']),
                 'splash_shown': r['splash']['shown'], 'scenes_ok': all(x['ok'] for x in r['steps']), 'dots_cap_hidden': r['dots_cap_hidden'],
                 'nav_cta_ok': r['nav_cta']['ok'], 'nav_samples': r['nav_cta']['samples'], 'nav_with_hero': r['nav_cta']['both_with_hero'],
                 'dock_hidden': r['dock_display'] == 'none', 'faq_ok': r['faq']['ok'], 'logo_ok': r['logo']['ok'], 'text': r['text'],
                 'line_start_dot': r['lines']['line_start_dot'], 'num_orphans': r['lines']['num_orphans'], 'steps_head_hidden': r['steps_head_hidden']}
S['last_faq_390'] = out['last_faq_390']['ok']
for k in ['autoplay_390', 'dot_then_auto_390', 'tab_hidden_390', 'phone_tap_390', 'pause_390', 'offscreen_390', 'reduced_motion_390', 'record',
          'result_hold_390', 'dock_bg_390', 'subj_links']:
    S[k] = out[k]['ok']
S['result_hold_ms'] = out['result_hold_390']['hold_ms']; S['cycle_ms'] = out['result_hold_390']['cycle_ms']
S['other_tests'] = {'console_errors': sum(len(out[k]['console_errors']) for k in ['autoplay_390', 'dot_then_auto_390', 'tab_hidden_390', 'phone_tap_390',
                    'pause_390', 'offscreen_390', 'last_faq_390', 'reduced_motion_390', 'result_hold_390', 'dock_bg_390'])}
# 스플래시 사본 사진: 840x840, 장당 80KB 이하(원본 photos/ 는 그대로)
SP_FILES = [ROOT / 'photos' / 'sp' / f'photo-{i}.webp' for i in range(1, 7)]
S['splash_sp_kb'] = [round(f.stat().st_size / 1000) if f.is_file() else 0 for f in SP_FILES]
S['splash_sp_ok'] = all(f.is_file() and f.stat().st_size <= 80000 and Image.open(f).size == (840, 840) for f in SP_FILES)
S['landscape_844x390'] = {'overflow': len(out['landscape_844x390']['overflow']), 'console_errors': len(out['landscape_844x390']['console_errors'])}
S['splash_photos_loaded'] = out['splash_frames_390']['photos_loaded']
S['press_all'] = {k: {'pressed': v['pressed_count'], 'fail': v['fail_count'], 'by_kind': v['by_kind'], 'hidden_not_pressed': v['hidden_not_pressed'],
                      'console_errors': len(v['console_errors'])} for k, v in out['press_all'].items()}
# 실패 목록: 참이어야 할 것이 거짓이거나, 0 이어야 할 수가 0 이 아닌 항목 이름
ZERO = {'overflow', 'small_taps', 'console_errors', 'low_contrast', 'fail', 'emdash', 'endash', 'dquote', 'line_start_dot', 'num_orphans'}
TRUE = {'phone_ok', 'first_screen_in_view', 'page_scrolls', 'scenes_ok', 'splash_ok', 'dock_ok', 'faq_ok', 'logo_ok', 'nav_cta_hidden',
        'first_ok', 'dots_cap_hidden', 'nav_cta_ok', 'dock_hidden', 'steps_head_ok', 'steps_head_hidden', 'scroll_w_ok', 'pause_in_view', 'pause_no_overlap'}
def fails(x, path=''):
    if isinstance(x, dict):
        return [f for k, v in x.items() for f in fails(v, f'{path}.{k}' if path else k)]
    if isinstance(x, list): return [] if all(x) else [path]
    key = path.rsplit('.', 1)[-1]
    if isinstance(x, bool) and (key in TRUE or '.' not in path): return [] if x else [path]
    if key in ZERO and isinstance(x, int) and not isinstance(x, bool): return [path] if x else []
    if key == 'splash_shown' and x: return [path]
    return []
S['failures'] = fails(S)
print(json.dumps({'summary': S, 'detail': out}, ensure_ascii=False, indent=1))
