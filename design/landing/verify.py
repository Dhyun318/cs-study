# 랜딩 시안 검사 + 장면 스크린샷 -> design/landing/shots/<폭>/*.png
# 실행: 프로젝트 루트에서 python3 -m http.server 8791 --bind 127.0.0.1 을 띄운 뒤 python3 design/landing/verify.py
# 넓은 화면(1440): 스크롤 소개. 설명 걸음을 스크롤하면 폰 장면이 바뀐다.
# 좁은 화면(390, 360, 375x667): 스크롤 없는 한 화면. 폰 속 장면 5개가 자동으로 넘어가고, 폰 아래 점 5개와 지금 장면 한 줄.
# 검사: 가로 넘침(폰 화면 안쪽 제외), 콘솔 오류, 누르는 영역 44 미만, 글의 em/en dash·큰따옴표, 로고 누르면 맨 위,
#       좁은 화면 세로 스크롤 0(scrollHeight <= innerHeight)과 첫 화면 배치(제목, 한 줄 설명, 시작하기, 폰, 점, 설명이 위에서 아래로 겹치지 않고 화면 안),
#       자동 재생(1초·5초·10초에 장면이 다름, 한 바퀴 1 2 3 4 5 뒤 1), 점 누르면 그 장면을 끝까지 보여 준 뒤 자동으로 다음,
#       탭 숨김이면 멈추고 다시 보이면 그 장면부터 이어서, 움직임 줄이기(자동 재생 없음, 점마다 끝 상태, 돌고 있는 움직임 0),
#       기록 있으면 이어서 공부하기(자동 이동 없음), 가로로 든 휴대폰(844x390)은 스크롤 허용(넘침·오류만 잰다)
# 스플래시(휴대폰 세션 첫 방문): 1.6초 안에 끝나고 시작하기가 보임, 도는 동안 스크롤 잠금·자동 재생 안 함, 끝나면 첫 장면부터 자동 재생,
#       누르면 바로 건너뜀(시작하기 자리를 눌러도 앱으로 안 감), 같은 세션 다시 열면 안 나옴, 1440·움직임 줄이기에서 안 나옴.
#       진행 프레임 shots/390/splash-*.png (0.1, 0.4, 0.8, 1.1, 1.4초)
# 모두 누르기(390·1440): 보이는 링크·버튼·점을 하나씩 실제로 눌러 누름 반응과 이동(앱 주소, 로고는 맨 위, 점은 그 장면)을 잰다
import json, pathlib, re
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent
URL = 'http://127.0.0.1:8791/design/landing/index.html'
MOBILE = [(390, 844), (360, 780), (375, 667)]
NO_SPLASH = "try { sessionStorage.setItem('cs-sp', '1') } catch (e) {}"
# 장면마다 타임라인이 끝나는 시간(ms) + 여유. 자동 재생이 다음으로 넘어가는 시간(DUR + 1400)보다 짧다
WAIT = [1600, 4600, 1900, 4500, 3900]
NEXT = [2500, 5500, 3100, 5400, 4800]  # 장면 1~5 가 자동으로 넘어가는 시간
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
TEXT = """() => { const t = document.body.innerText; return { emdash: (t.match(/\\u2014/g) || []).length, endash: (t.match(/\\u2013/g) || []).length,
  dquote: (t.match(/["\\u201C\\u201D]/g) || []).length }; }"""
NO_SCROLL = "() => ({ scroll_h: document.scrollingElement.scrollHeight, inner_h: innerHeight, ok: document.scrollingElement.scrollHeight <= innerHeight })"
# 첫 화면 배치: 위에서 아래로 겹치지 않고, 모두 화면 안
FIRST = """() => { const H = innerHeight, order = ['.lp-h1', '.lp-sub', '[data-hero-cta]', '.lp-device', '.lp-dots', '.lp-cap'];
  const r = order.map(s => document.querySelector(s).getBoundingClientRect());
  return { viewport_h: H, bottoms: Object.fromEntries(order.map((s, i) => [s, Math.round(r[i].bottom)])),
    in_view: r.every(b => b.top >= 0 && b.bottom <= H + .5), stacked: r.every((b, i) => !i || r[i - 1].bottom <= b.top + .5),
    phone_w: Math.round(r[3].width), phone_h: Math.round(r[3].height), scale: document.querySelector('.lp-device').style.getPropertyValue('--s') }; }"""
# 움직임 줄이기 끝 상태: 1 답 펼침, 2 칸 두 개 이상 참, 3 블록 +1, 4 시뮬레이션 4번째 단계, 5 목차 헷갈림만
RM_END = """i => [() => document.querySelector('#q').classList.contains('rev'),
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
SEEK = "t => document.getAnimations().forEach(a => { a.pause(); a.currentTime = t; })"
FRAMES = [100, 400, 800, 1100, 1400]

# 모두 누르기: 보이는 링크·버튼(폰 미리보기 안쪽, 스플래시 제외)에 번호를 붙인다. 점은 몇 번째 점인지도
CLICKABLE = """() => [...document.querySelectorAll('a[href], button, [role=button]')].filter(e => !e.closest('[inert]') && !e.closest('#sp') && e.getClientRects().length)
  .map((e, i) => { e.dataset.ck = i; const d = e.closest('.lp-dots') ? [...e.parentNode.children].indexOf(e) : -1;
    return { name: (e.textContent || e.getAttribute('aria-label') || '').trim().slice(0, 24), href: e.getAttribute('href'), dot: d }; })"""
LOOK = "e => { const s = getComputedStyle(e); return [s.transform, s.opacity, s.filter, s.backgroundColor].join('|'); }"
ON_TOP = "e => { const r = e.getBoundingClientRect(), at = document.elementFromPoint(r.left + r.width / 2, r.top + r.height / 2); return !!at && e.contains(at); }"
APP_URL = URL.rsplit('/', 1)[0] + '/app/'


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
    # 링크·버튼·점마다 새로 열어 맨 아래에서 시작(넓은 화면은 머리 시작하기가 보이는 자리), 화면 밖이면 보이게 내린 뒤 누른다
    mob = w < 960
    ctx = b.new_context(viewport={'width': w, 'height': h}, has_touch=mob, is_mobile=mob)
    ctx.add_init_script(NO_SPLASH)
    ctx.route(re.compile(r'/design/landing/app/'), lambda r: r.fulfill(status=200, content_type='text/html', body='<!doctype html><title>app</title>'))
    errs = []; pg = watch(ctx.new_page(), errs)
    pg.goto(URL); pg.wait_for_timeout(900)
    items, res, hidden = pg.evaluate(CLICKABLE), [], []
    for i, it in enumerate(items):
        pg.goto(URL); pg.wait_for_timeout(900); pg.evaluate(CLICKABLE)
        pg.evaluate('window.scrollTo(0, document.body.scrollHeight)'); pg.wait_for_timeout(500)
        el = pg.locator(f'[data-ck="{i}"]')
        el.scroll_into_view_if_needed(); pg.wait_for_timeout(400)
        # 일부러 숨긴 것(좁은 화면 머리 시작하기: 첫 화면 시작하기가 늘 보여서 안 나타남)은 누르지 않고 따로 적는다
        if el.evaluate("e => getComputedStyle(e).visibility === 'hidden'"):
            hidden.append(it['name']); continue
        y0, box, look0, top = pg.evaluate('scrollY'), el.bounding_box(), el.evaluate(LOOK), el.evaluate(ON_TOP)
        pg.mouse.move(box['x'] + box['width'] / 2, box['y'] + box['height'] / 2)
        pg.mouse.down(); pg.wait_for_timeout(220); look1 = el.evaluate(LOOK)
        pg.mouse.up(); pg.wait_for_timeout(1500)
        url, y1 = pg.url, (pg.evaluate('scrollY') if pg.url == URL else None)
        if it['href'] == './app/': moved = url == APP_URL
        elif it['dot'] >= 0:
            now = pg.evaluate(NOW); moved = url == URL and now['n'] == it['dot'] + 1 and now['cap'] == TITLES[it['dot']]
        else: moved = url == URL and y1 == 0 and (mob or y0 > 0)  # 로고: 좁은 화면은 스크롤이 없어 이미 맨 위
        res.append({**it, 'w': round(box['width']), 'h': round(box['height']), 'on_top': top, 'pressed': look1 != look0,
                    'went': url.replace(URL.rsplit('/', 1)[0], '') + ('' if y1 is None else f' y={y1}'), 'ok': top and look1 != look0 and moved})
    ctx.close()
    return {'pressed_count': len(res), 'fail_count': sum(not x['ok'] for x in res), 'bad': [x for x in res if not x['ok']],
            'hidden_not_pressed': hidden, 'items': res, 'console_errors': errs}


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
    errs_all = []

    # ---- 좁은 화면: 스플래시, 첫 화면, 장면 스크린샷(점 눌러서), 로고 ----
    for w, h in MOBILE:
        d = ROOT / 'shots' / str(w); d.mkdir(parents=True, exist_ok=True)
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
        pg.wait_for_timeout(1300); sp['answer_open_1300ms_after'] = pg.evaluate(Q_REV)  # 첫 장면을 처음부터 돌렸다는 증거
        sp['ok'] = sp['shown'] and sp['locked'] and not sp['overflow_during'] and sp['scroll_w'] <= w and sp['scroll_y_after_wheel'] == 0 \
            and sp['scene_during'] == 0 and sp['scr_during'] == 'home' and sp['end_from_first_paint_ms'] <= 1600 \
            and not sp['locked_after'] and sp['start_after']['in_view'] and sp['start_after']['on_top'] \
            and sp['dot_at_end'] == 1 and sp['scr_at_end'] == 'q' and not sp['answer_open_at_end'] and sp['answer_open_1300ms_after']
        # 같은 세션(같은 탭)에서 다시 열면 안 나온다
        pg.goto(URL, wait_until='domcontentloaded'); sp['shown_again_same_session'] = pg.evaluate(SP_ON)
        pg.evaluate('document.fonts.ready'); pg.wait_for_timeout(1500)
        r = {'splash': sp, 'overflow': [], 'small_taps': [], 'no_scroll': [], 'first_screen': pg.evaluate(FIRST)}
        def look(name):
            pg.screenshot(path=str(d / f'{name}.png'))
            r['overflow'] += pg.evaluate(OVERFLOW)
            r['small_taps'] += [t for t in pg.evaluate(TAPS) if t['w'] < 44 or t['h'] < 44]
            r['no_scroll'].append(pg.evaluate(NO_SCROLL)['ok'])
        look('00-first')
        r['first_screen']['no_scroll'] = pg.evaluate(NO_SCROLL)
        steps = []
        for i, name in enumerate(NAMES):
            dot(pg, i); pg.wait_for_timeout(WAIT[i]); look(name)
            s = pg.evaluate(NOW)
            steps.append({**s, 'ok': s['n'] == i + 1 and s['scr'] == SCR_END[i] and s['cap'] == TITLES[i]})
        r['steps'] = steps
        # 로고: 다시 불러오지 않고 맨 위(좁은 화면은 스크롤이 없어 그대로 맨 위)
        pg.click('a.lp-brand'); pg.wait_for_timeout(600)
        r['logo'] = {'scroll_y': pg.evaluate('scrollY'), 'url_same': pg.url == URL}
        # 시작하기 자리를 눌러 스플래시를 건너뛰어도 앱으로 안 간다(새 탭 = 새 세션)
        p2 = watch(ctx.new_page(), errs)
        p2.goto(URL, wait_until='domcontentloaded'); p2.wait_for_timeout(300)
        shown = p2.evaluate(SP_ON); c = p2.evaluate("() => { const r = document.querySelector('[data-hero-cta]').getBoundingClientRect(); return [r.left + r.width / 2, r.top + r.height / 2]; }")
        p2.touchscreen.tap(*c); p2.wait_for_timeout(80)
        r['splash']['tap_skip'] = {'shown_before': shown, 'gone_80ms': not p2.evaluate("!!document.getElementById('sp')"), 'unlocked': not p2.evaluate(LOCKED),
                                   'url_same': p2.url == URL, 'scene_after': p2.evaluate(NOW)['n']}
        p2.close()
        r['text'] = pg.evaluate(TEXT)
        r['console_errors'] = errs
        r['small_taps'] = list({json.dumps(t, ensure_ascii=False): t for t in r['small_taps']}.values())
        r['overflow'] = sorted(set(r['overflow']))
        r['no_scroll_all'] = all(r['no_scroll']); del r['no_scroll']
        out[f'{w}x{h}'] = r
        ctx.close()

    # ---- 넓은 화면(1440): 스크롤 장면 그대로 ----
    w, h = 1440, 900
    d = ROOT / 'shots' / str(w); d.mkdir(parents=True, exist_ok=True)
    for f in d.glob('*.png'): f.unlink()
    ctx = b.new_context(viewport={'width': w, 'height': h}, device_scale_factor=2)
    errs = []; pg = watch(ctx.new_page(), errs)
    pg.goto(URL, wait_until='domcontentloaded')
    r = {'splash': {'shown': pg.evaluate(SP_ON)}, 'overflow': [], 'small_taps': []}
    pg.evaluate('document.fonts.ready'); pg.wait_for_timeout(1500)
    def look(name):
        pg.screenshot(path=str(d / f'{name}.png'))
        r['overflow'] += pg.evaluate(OVERFLOW)
        r['small_taps'] += [t for t in pg.evaluate(TAPS) if t['w'] < 44 or t['h'] < 44]
    look('00-first')
    r['dots_cap_hidden'] = pg.evaluate("() => !document.querySelector('.lp-dots').getClientRects().length && !document.querySelector('.lp-cap').getClientRects().length")
    steps = []
    for i, name in enumerate(NAMES):
        pg.evaluate(GO_STEP, i); pg.wait_for_timeout(WAIT[i]); look(name)
        s = pg.evaluate(SCENE)
        steps.append({'step_on': s['step'], 'scr': s['scr'], 'ok': s['step'] == i and s['scr'] == SCR_END[i]})
    r['steps'] = steps
    pg.evaluate("document.querySelector('.lp-subj').scrollIntoView()"); pg.wait_for_timeout(400); look('06-subjects')
    pg.evaluate('window.scrollTo(0, document.body.scrollHeight)'); pg.wait_for_timeout(400); look('07-end')
    pg.click('a.lp-brand'); pg.wait_for_timeout(1500)
    r['logo'] = {'scroll_y': pg.evaluate('scrollY'), 'url_same': pg.url == URL, 'scr_at_top': pg.evaluate(SCENE)['scr']}
    r['text'] = pg.evaluate(TEXT); r['console_errors'] = errs
    r['small_taps'] = list({json.dumps(t, ensure_ascii=False): t for t in r['small_taps']}.values())
    r['overflow'] = sorted(set(r['overflow']))
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

    # ---- 점 누르기(390): 장면 1 이 넘어가기 직전(2.1초)에 점 2 를 누르면, 장면 2 를 끝까지 보여 준 뒤 3 으로. 점 5 다음은 1 ----
    ctx = mctx(b); errs = []; pg = watch(ctx.new_page(), errs)
    pg.goto(URL, wait_until='domcontentloaded'); pg.wait_for_timeout(2100)
    n = lambda: pg.evaluate(NOW)['n']
    before = n(); dot(pg, 1)
    pg.wait_for_timeout(600); a = n()  # 장면 1 이 넘어갈 2.5초를 지나도 장면 2
    pg.wait_for_timeout(NEXT[1] - 400 - 600); b_, full = n(), pg.evaluate(Q_FULL)  # 넘어가기 0.4초 전: 아직 2, 칸이 다 참(끝까지 보여 줌)
    pg.wait_for_timeout(1200); c = n()  # 그다음 자동으로 3
    dot(pg, 4); pg.wait_for_timeout(NEXT[4] - 400); d5, cf = n(), pg.evaluate("document.querySelector('#toc').classList.contains('cf')")
    pg.wait_for_timeout(1000); e1 = n()  # 5 다음은 1
    dot2 = {'scene_before_press': before, 'at_0_6s': a, 'at_next_minus_0_4s': b_, 'segs_full_before_next': full, 'at_next_plus_0_8s': c,
            'dot5_at_next_minus_0_4s': d5, 'dot5_conf_filtered': cf, 'dot5_at_next_plus_0_6s': e1,
            'ok': before == 1 and a == 2 and b_ == 2 and full and c == 3 and d5 == 5 and cf and e1 == 1}
    dot2['console_errors'] = errs
    out['dot_then_auto_390'] = dot2
    ctx.close()

    # ---- 탭 숨김(390): 1초에 숨기고 4초 기다려도 장면 1 그대로, 다시 보이면 장면 1 부터 이어서 2.5초 뒤 장면 2 ----
    ctx = mctx(b); errs = []; pg = watch(ctx.new_page(), errs)
    pg.goto(URL, wait_until='domcontentloaded'); pg.wait_for_timeout(1000)
    pg.evaluate(HIDE, True); hid = pg.evaluate(NOW)['n']; pg.wait_for_timeout(4000); still_hidden = pg.evaluate(NOW)['n']
    pg.evaluate(HIDE, False); pg.wait_for_timeout(300); back = pg.evaluate(NOW)['n']; open_at_300 = pg.evaluate(Q_REV)
    pg.wait_for_timeout(NEXT[0] - 300 + 500); after = pg.evaluate(NOW)['n']
    out['tab_hidden_390'] = {'scene_when_hidden': hid, 'scene_after_4s_hidden': still_hidden, 'scene_300ms_after_back': back,
                             'answer_open_300ms_after_back': open_at_300, 'scene_3s_after_back': after, 'console_errors': errs,
                             'ok': hid == 1 and still_hidden == 1 and back == 1 and not open_at_300 and after == 2}
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

print(json.dumps(out, ensure_ascii=False, indent=1))
