# 랜딩 시안 검사 + 장면 스크린샷 -> design/landing/shots/<폭>/*.png
# 실행: 프로젝트 루트에서 python3 -m http.server 8791 --bind 127.0.0.1 을 띄운 뒤 python3 design/landing/verify.py
# 넓은 화면(1440)과 좁은 화면(390, 360) 모두 스크롤 소개: 설명 걸음을 스크롤하면 폰 장면이 바뀐다. 좁은 화면은 폰이 머리 아래 위쪽에 붙는다.
# 검사: 가로 넘침(폰 화면 안쪽 제외), 콘솔 오류, 누르는 영역 44 미만, 글의 em/en dash·큰따옴표, 로고 누르면 맨 위,
#       좁은 화면 첫 화면에 제목·한 줄 설명·시작하기, 폰 높이 비율, 위에서 아래로 스크롤하면 장면 0~5 가 차례로,
#       지금 걸음 글이 폰에 가리지 않음(기준선에 걸친 동안), 끝 시작하기, 기록 있으면 이어서 공부하기(자동 이동 없음),
#       움직임 줄이기(장면마다 끝 상태, 돌고 있는 움직임 0)
# 스플래시(휴대폰 세션 첫 방문): 390·360 에서 1.6초 안에 끝나고 시작하기가 보임, 도는 동안 스크롤 잠금, 누르면 바로 건너뜀(시작하기 자리를 눌러도 앱으로 안 감),
#       같은 세션 다시 열면 안 나옴, 1440·움직임 줄이기에서 안 나옴. 진행 프레임 shots/390/splash-*.png (0.1, 0.4, 0.8, 1.1, 1.4초)
# 모두 누르기(390·1440): 랜딩의 링크·버튼을 하나씩 실제로 눌러 누름 반응과 이동(앱 주소, 로고는 맨 위)을 잰다
import json, pathlib, re
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent
URL = 'http://127.0.0.1:8791/design/landing/index.html'
SIZES = [(390, 844), (360, 780), (1440, 900)]
# 장면마다 타임라인이 끝나는 시간(ms) + 여유
WAIT = [1600, 4600, 1900, 4500, 3900]
NAMES = ['01-reveal', '02-read', '03-tower', '04-sim', '05-conf']
SCR_END = ['q', 'q', 'tw', 'sim', 'toc']  # 걸음마다 타임라인이 끝난 뒤 보이는 폰 화면

# 넓은 화면: 걸음을 화면 가운데로. 좁은 화면: 걸음 위끝을 붙은 폰 아래 60 위로(글이 폰 바로 아래에 붙은 상태)
GO_STEP = """i => { const s = document.querySelectorAll('.lp-step')[i];
  window.scrollTo(0, s.getBoundingClientRect().top + scrollY - (innerHeight / 2 - s.offsetHeight / 2)); }"""
GO_N = """i => { const s = document.querySelectorAll('.lp-step')[i], under = document.querySelector('.lp-nav').offsetHeight + document.querySelector('.lp-pin').offsetHeight;
  window.scrollTo(0, s.getBoundingClientRect().top + scrollY - under + 60); }"""
SCENE = """() => ({ step: [...document.querySelectorAll('.lp-step')].findIndex(s => s.classList.contains('on')), scr: document.querySelector('.scr.on').id })"""
# 지금 걸음이 기준선(붙은 폰 아래 남은 자리의 가운데)에 걸쳐 있으면, 그 글의 제목 위끝이 폰 자리 아래, 설명 아래끝이 화면 안
COVER = """() => { const st = document.querySelector('.lp-step.on'); if (!st) return null;
  const pin = document.querySelector('.lp-pin'), L = Math.round((document.querySelector('.lp-nav').offsetHeight + pin.offsetHeight + innerHeight) / 2);
  const b = st.getBoundingClientRect(); if (b.top > L || b.bottom < L) return null;
  const h = st.querySelector('h2').getBoundingClientRect(), q = st.querySelector('p').getBoundingClientRect(), pb = pin.getBoundingClientRect().bottom;
  return { ok: h.top >= pb - .5 && q.bottom <= innerHeight + .5, h2_top: Math.round(h.top), p_bottom: Math.round(q.bottom), pin_bottom: Math.round(pb) }; }"""
# 폰 화면 안쪽과 스플래시 창 안쪽(확대되며 들어오는 사진 컷, 창 모양으로 잘림)은 잘려서 넘치지 않는다
OVERFLOW = """() => [...document.querySelectorAll('body *')].filter(e => !e.closest('.lp-screen') && !e.closest('.sp-w') && !e.closest('svg[width="0"]')).filter(e => {
  const r = e.getBoundingClientRect(); return r.width && (r.right > innerWidth + .5 || r.left < -.5); }).map(e => e.tagName + '.' + e.className).slice(0, 10)"""
TAPS = """() => [...document.querySelectorAll('a, button, input, select, textarea, [role=button], [tabindex]')].filter(e => !e.closest('[inert]')).filter(e => {
  const cs = getComputedStyle(e), r = e.getBoundingClientRect(); return cs.visibility !== 'hidden' && cs.display !== 'none' && r.width > 0; })
  .map(e => { const r = e.getBoundingClientRect(); return { t: e.textContent.trim().slice(0, 20) || e.getAttribute('aria-label'), w: Math.round(r.width), h: Math.round(r.height) }; })"""
TEXT = """() => { const t = document.body.innerText; return { emdash: (t.match(/\\u2014/g) || []).length, endash: (t.match(/\\u2013/g) || []).length,
  dquote: (t.match(/["\\u201C\\u201D]/g) || []).length }; }"""
FIRST = """() => { const r = s => document.querySelector(s).getBoundingClientRect(), H = innerHeight;
  return { viewport_h: H, h1_bottom: Math.round(r('.lp-h1').bottom), sub_bottom: Math.round(r('.lp-sub').bottom), start_bottom: Math.round(r('[data-hero-cta]').bottom),
    start_visible: r('[data-hero-cta]').bottom <= H, phone_h: Math.round(r('.lp-device').height), phone_ratio: +(r('.lp-device').height / H).toFixed(2) }; }"""
END_BTN = """() => { const b = document.querySelector('.lp-end .btn').getBoundingClientRect(); return { visible: b.top >= 0 && b.bottom <= innerHeight, w: Math.round(b.width), h: Math.round(b.height) }; }"""
# 움직임 줄이기 끝 상태: 1 답 펼침, 2 칸 두 개 이상 참, 3 블록 +1, 4 시뮬레이션 4번째 단계, 5 목차 헷갈림만
RM_END = """i => [() => document.querySelector('#q').classList.contains('rev'),
  () => [...document.querySelectorAll('#q [data-segs] b')].filter(b => b.style.getPropertyValue('--f') === '1').length >= 2,
  () => document.querySelector('#tw').classList.contains('plus'),
  () => document.querySelector('#sim [data-count]').textContent === '5단계 중 4번째',
  () => document.querySelector('#toc').classList.contains('cf') && document.querySelector('#toc').classList.contains('on')][i]()"""
RUNNING = """() => document.getAnimations().filter(a => a.playState === 'running' && (a.effect.getTiming().duration || 0) > 1).length"""

SP_ON = "() => document.documentElement.classList.contains('sp-on') && !!document.getElementById('sp')"
LOCKED = "() => getComputedStyle(document.documentElement).overflowY === 'hidden'"
# 스플래시가 없어지는 순간: 첫 그리기부터 몇 ms (탐색 시작부터도 같이)
SP_END = """() => new Promise(r => { const fp = (performance.getEntriesByName('first-paint')[0] || { startTime: 0 }).startTime;
  const iv = setInterval(() => { if (document.getElementById('sp')) return; clearInterval(iv);
    r({ end_from_first_paint_ms: Math.round(performance.now() - fp), end_from_nav_ms: Math.round(performance.now()) }); }, 10); })"""
# 첫 화면 시작하기가 화면 안에 있고, 그 자리를 덮은 것이 없음
START_SEEN = """() => { const b = document.querySelector('[data-hero-cta]'), r = b.getBoundingClientRect(), at = document.elementFromPoint(r.left + r.width / 2, r.top + r.height / 2);
  return { in_view: r.top >= 0 && r.bottom <= innerHeight, on_top: !!at && b.contains(at), opacity: getComputedStyle(b).opacity, scroll_y: scrollY }; }"""
SEEK = "t => document.getAnimations().forEach(a => { a.pause(); a.currentTime = t; })"
FRAMES = [100, 400, 800, 1100, 1400]

# 모두 누르기: 화면의 링크·버튼(폰 미리보기 안쪽 제외)에 번호를 붙인다
CLICKABLE = """() => [...document.querySelectorAll('a[href], button, [role=button]')].filter(e => !e.closest('[inert]') && !e.closest('#sp'))
  .map((e, i) => { e.dataset.ck = i; return { name: (e.textContent || e.getAttribute('aria-label') || '').trim().slice(0, 24), href: e.getAttribute('href') }; })"""
LOOK = "e => { const s = getComputedStyle(e); return [s.transform, s.opacity, s.filter, s.backgroundColor].join('|'); }"
ON_TOP = "e => { const r = e.getBoundingClientRect(), at = document.elementFromPoint(r.left + r.width / 2, r.top + r.height / 2); return !!at && e.contains(at); }"
APP_URL = URL.rsplit('/', 1)[0] + '/app/'


def press_all(b, w, h):
    # 링크·버튼마다 새로 열어 맨 아래(머리 시작하기가 보이는 자리)에서 시작, 화면 밖이면 보이게 내린 뒤 누른다
    mob = w < 960
    ctx = b.new_context(viewport={'width': w, 'height': h}, has_touch=mob, is_mobile=mob)
    ctx.add_init_script("try { sessionStorage.setItem('cs-sp', '1') } catch (e) {}")  # 스플래시는 따로 잰다
    ctx.route(re.compile(r'/design/landing/app/'), lambda r: r.fulfill(status=200, content_type='text/html', body='<!doctype html><title>app</title>'))
    pg = ctx.new_page(); errs = []
    pg.on('console', lambda m: m.type == 'error' and errs.append(m.text))
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto(URL); pg.wait_for_timeout(900)
    items, res = pg.evaluate(CLICKABLE), []
    for i, it in enumerate(items):
        pg.goto(URL); pg.wait_for_timeout(900); pg.evaluate(CLICKABLE)
        pg.evaluate('window.scrollTo(0, document.body.scrollHeight)'); pg.wait_for_timeout(500)
        el = pg.locator(f'[data-ck="{i}"]')
        el.scroll_into_view_if_needed(); pg.wait_for_timeout(400)
        y0, box, look0, top = pg.evaluate('scrollY'), el.bounding_box(), el.evaluate(LOOK), el.evaluate(ON_TOP)
        pg.mouse.move(box['x'] + box['width'] / 2, box['y'] + box['height'] / 2)
        pg.mouse.down(); pg.wait_for_timeout(220); look1 = el.evaluate(LOOK)
        pg.mouse.up(); pg.wait_for_timeout(1500)
        url, y1 = pg.url, (pg.evaluate('scrollY') if pg.url == URL else None)
        moved = url == APP_URL if it['href'] == './app/' else (url == URL and y1 == 0 and y0 > 0)
        res.append({**it, 'w': round(box['width']), 'h': round(box['height']), 'on_top': top, 'pressed': look1 != look0,
                    'went': url.replace(URL.rsplit('/', 1)[0], '') + ('' if y1 is None else f' y={y1}'), 'ok': top and look1 != look0 and moved})
    ctx.close()
    return {'count': len(res), 'bad': [x for x in res if not x['ok']], 'items': res, 'console_errors': errs}


def sweep(pg):
    # 맨 위에서 끝 섹션까지 40px 씩 내리며 장면 순서와 글 가림을 잰다
    end = int(pg.evaluate("document.querySelector('.lp-end').getBoundingClientRect().top + scrollY"))
    seq, bad, n = [], [], 0
    for y in range(0, end, 40):
        pg.evaluate(f'window.scrollTo(0, {y})'); pg.wait_for_timeout(80)
        sc = pg.evaluate(SCENE)['step'] + 1
        if not seq or seq[-1] != sc: seq.append(sc)
        c = pg.evaluate(COVER)
        if c is not None:
            n += 1
            if not c['ok']: bad.append({'y': y, **c})
    return {'scene_order': seq, 'cover_checked': n, 'covered': bad[:5], 'covered_count': len(bad)}


out = {}
with sync_playwright() as pw:
    b = pw.chromium.launch()
    for w, h in SIZES:
        d = ROOT / 'shots' / str(w); d.mkdir(parents=True, exist_ok=True)
        for f in d.glob('*.png'): f.unlink()
        desk = w >= 960
        ctx = b.new_context(viewport={'width': w, 'height': h}, device_scale_factor=2, has_touch=not desk, is_mobile=not desk)
        pg = ctx.new_page()
        errs = []
        pg.on('console', lambda m: m.type == 'error' and errs.append(m.text))
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto(URL, wait_until='domcontentloaded')
        if desk:
            sp = {'shown': pg.evaluate(SP_ON)}
        else:
            # 도는 동안: 0.4초에 보이는지, 잠금, 가로 넘침, 휠로 내려도 안 내려가는지. 끝나면 잠금 풀림과 시작하기
            pg.wait_for_timeout(400)
            sp = {'shown': pg.evaluate(SP_ON), 'locked': pg.evaluate(LOCKED), 'overflow_during': pg.evaluate(OVERFLOW),
                  'scroll_w': pg.evaluate('document.documentElement.scrollWidth')}
            pg.mouse.move(w / 2, h / 2); pg.mouse.wheel(0, 600); pg.wait_for_timeout(100); sp['scroll_y_after_wheel'] = pg.evaluate('scrollY')
            sp.update(pg.evaluate(SP_END)); sp['locked_after'] = pg.evaluate(LOCKED); sp['start_after'] = pg.evaluate(START_SEEN)
            sp['ok'] = sp['shown'] and sp['locked'] and not sp['overflow_during'] and sp['scroll_w'] <= w and sp['scroll_y_after_wheel'] == 0 and sp['end_from_first_paint_ms'] <= 1600 \
                and not sp['locked_after'] and sp['start_after']['in_view'] and sp['start_after']['on_top']
            # 같은 세션(같은 탭)에서 다시 열면 안 나온다
            pg.goto(URL, wait_until='domcontentloaded'); sp['shown_again_same_session'] = pg.evaluate(SP_ON)
        pg.evaluate('document.fonts.ready'); pg.wait_for_timeout(1500)
        r = {'splash': sp, 'overflow': [], 'small_taps': []}
        def look(name):
            pg.screenshot(path=str(d / f'{name}.png'))
            r['overflow'] += pg.evaluate(OVERFLOW)
            r['small_taps'] += [t for t in pg.evaluate(TAPS) if t['w'] < 44 or t['h'] < 44]
        if not desk: r['first_screen'] = pg.evaluate(FIRST)
        look('00-first')
        steps = []
        for i, name in enumerate(NAMES):
            pg.evaluate(GO_STEP if desk else GO_N, i); pg.wait_for_timeout(WAIT[i]); look(name)
            s = pg.evaluate(SCENE)
            steps.append({'step_on': s['step'], 'scr': s['scr'], 'ok': s['step'] == i and s['scr'] == SCR_END[i], **({} if desk else {'cover': pg.evaluate(COVER)})})
        r['steps'] = steps
        if desk:
            pg.evaluate("document.querySelector('.lp-subj').scrollIntoView()"); pg.wait_for_timeout(400); look('06-subjects')
            pg.evaluate('window.scrollTo(0, document.body.scrollHeight)'); pg.wait_for_timeout(400); look('07-end')
        else:
            pg.evaluate('window.scrollTo(0, document.body.scrollHeight)'); pg.wait_for_timeout(600); look('06-end')
            r['end_start'] = pg.evaluate(END_BTN)
            r['sweep'] = sweep(pg)
        # 로고: 끝에서 누르면 다시 불러오지 않고 맨 위로
        pg.evaluate('window.scrollTo(0, document.body.scrollHeight)'); pg.wait_for_timeout(300)
        pg.click('a.lp-brand'); pg.wait_for_timeout(1500)
        r['logo'] = {'scroll_y': pg.evaluate('scrollY'), 'url_same': pg.url == URL, 'scr_at_top': pg.evaluate(SCENE)['scr']}
        if not desk:
            p2 = ctx.new_page(); p2.on('console', lambda m: m.type == 'error' and errs.append(m.text)); p2.on('pageerror', lambda e: errs.append(str(e)))
            p2.goto(URL, wait_until='domcontentloaded'); p2.wait_for_timeout(300)
            shown = p2.evaluate(SP_ON); c = p2.evaluate("() => { const r = document.querySelector('[data-hero-cta]').getBoundingClientRect(); return [r.left + r.width / 2, r.top + r.height / 2]; }")
            p2.touchscreen.tap(*c); p2.wait_for_timeout(80)
            r['splash']['tap_skip'] = {'shown_before': shown, 'gone_80ms': not p2.evaluate("!!document.getElementById('sp')"), 'unlocked': not p2.evaluate(LOCKED), 'url_same': p2.url == URL}
            p2.close()
        r['text'] = pg.evaluate(TEXT)
        r['console_errors'] = errs
        r['small_taps'] = list({json.dumps(t, ensure_ascii=False): t for t in r['small_taps']}.values())
        r['overflow'] = sorted(set(r['overflow']))
        out[f'{w}x{h}'] = r
        ctx.close()

    # 움직임 줄이기 (390): 걸음마다 장면이 바로 끝 상태, 돌고 있는 움직임 0
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, has_touch=True, is_mobile=True, reduced_motion='reduce')
    pg = ctx.new_page(); pg.goto(URL, wait_until='domcontentloaded'); rm_splash = pg.evaluate(SP_ON)
    pg.evaluate('document.fonts.ready'); pg.wait_for_timeout(600)
    rm = []
    for i in range(5):
        pg.evaluate(GO_N, i); pg.wait_for_timeout(300)
        rm.append({'end_state': pg.evaluate(RM_END, i), 'running': pg.evaluate(RUNNING), 'scr': pg.evaluate(SCENE)['scr']})
    # 움직임 줄이기면 로고가 바로 맨 위로 뛴다: 그래도 폰이 홈 장면으로 돌아와야 한다
    pg.click('a.lp-brand'); pg.wait_for_timeout(300)
    out['reduced_motion_390'] = {'splash_shown': rm_splash, 'steps': rm, 'logo_scroll_y': pg.evaluate('scrollY'), 'logo_scr': pg.evaluate(SCENE)['scr']}
    ctx.close()

    # 기록이 있으면 시작하기 버튼 모두 이어서 공부하기, 자동 이동 없음 (390)
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, has_touch=True, is_mobile=True); pg = ctx.new_page()
    pg.goto(URL); pg.evaluate("localStorage.setItem('cs-chagok', JSON.stringify({ read: ['ds-array'], confused: [], last: null }))")
    pg.goto(URL); pg.wait_for_timeout(1000)
    out['record'] = {'url_unchanged': pg.url == URL,
                     'start_texts': pg.evaluate("""[...document.querySelectorAll('a.btn.pri[href="./app/"]')].map(a => a.textContent)""")}
    ctx.close()

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
