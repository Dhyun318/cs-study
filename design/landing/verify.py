# 랜딩 시안 검사 + 장 스크린샷 -> design/landing/shots/<폭>/*.png
# 실행: 프로젝트 루트에서 python3 -m http.server 8791 --bind 127.0.0.1 을 띄운 뒤 python3 design/landing/verify.py
# 넓은 화면(1440): 스크롤로 폰 장면을 넘긴다. 좁은 화면(390, 360): 가로로 넘기는 소개 4장(스와이프, 다음, 점).
# 검사: 가로 넘침(넘기는 장 안쪽은 그 장 폭 기준, 폰 화면 안쪽 제외), 콘솔 오류, 누르는 영역 44 미만, 글의 em/en dash·큰따옴표,
#       좁은 화면 첫 화면에 다음 버튼·점·건너뛰기가 들어오는지, 세로 스크롤 없음, 사진 4장 불러옴, 스와이프·다음·점·건너뛰기 동작,
#       마지막 장 시작하기, 기록 있으면 이어서 공부하기, 움직임 줄이기(처음부터 끝 상태, 돌고 있는 움직임 0), 사진 실패 시 일러스트
import json, pathlib
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent
URL = 'http://127.0.0.1:8791/design/landing/index.html'
SIZES = [(390, 844), (360, 780), (1440, 900)]
# 넓은 화면 장면마다 타임라인이 끝나는 시간(ms) + 여유
WAIT = [1600, 4600, 1900, 4500, 3900]
NAMES = ['01-reveal', '02-read', '03-tower', '04-sim', '05-conf']
OB_NAMES = ['01-recall', '02-sim', '03-tower', '04-conf']
OB_WAIT = 1800  # 넘김(부드러운 스크롤) + 조각 움직임(최대 980ms + 240ms) + 여유

GO_STEP = """i => { const s = document.querySelectorAll('.lp-step')[i];
  window.scrollTo(0, s.getBoundingClientRect().top + scrollY - (innerHeight / 2 - s.offsetHeight / 2)); }"""
CUR = "() => [...document.querySelectorAll('.ob-dots button')].findIndex(b => b.hasAttribute('aria-current'))"
DOT = "i => document.querySelectorAll('.ob-dots button')[i].click()"
NEXT = "() => document.querySelector('[data-next]').click()"
OVERFLOW = """() => [...document.querySelectorAll('body *')].filter(e => !e.closest('.lp-screen') && !e.closest('svg[width="0"]')).filter(e => {
  const s = e.closest('.ob-sl'), box = s ? s.getBoundingClientRect() : { left: 0, right: innerWidth };
  const r = e.getBoundingClientRect(); return r.width && (r.right > box.right + .5 || r.left < box.left - .5); }).map(e => e.tagName + '.' + e.className).slice(0, 10)"""
TAPS = """() => [...document.querySelectorAll('a, button, input, select, textarea, [role=button], [tabindex]')].filter(e => !e.closest('[inert]')).filter(e => {
  const cs = getComputedStyle(e), r = e.getBoundingClientRect(); return cs.visibility !== 'hidden' && cs.display !== 'none' && r.width > 0; })
  .map(e => { const r = e.getBoundingClientRect(); return { t: e.textContent.trim().slice(0, 20) || e.getAttribute('aria-label'), w: Math.round(r.width), h: Math.round(r.height) }; })"""
TEXT = """() => { const t = document.body.innerText; return { emdash: (t.match(/\\u2014/g) || []).length, endash: (t.match(/\\u2013/g) || []).length,
  dquote: (t.match(/["\\u201C\\u201D]/g) || []).length }; }"""
FIRST = """() => { const r = s => document.querySelector(s).getBoundingClientRect(), eb = document.querySelector('.ob-eb');
  return { viewport_h: innerHeight, next_bottom: Math.round(r('[data-next]').bottom), dots_bottom: Math.round(r('.ob-dots').bottom),
    skip_bottom: Math.round(r('.ob-skip').bottom), page_h: document.documentElement.scrollHeight,
    eyebrow_fits: eb.scrollWidth <= eb.parentElement.clientWidth, titles_one_line: [...document.querySelectorAll('.ob-tx h2, .ob-tx p')].every(e => e.offsetHeight <= 36),
    photo_h: [...document.querySelectorAll('.ob-ph')].map(e => Math.round(e.offsetHeight)) }; }"""
STATE = """() => ({ cur: [...document.querySelectorAll('.ob-dots button')].findIndex(b => b.hasAttribute('aria-current')),
  next_hidden: document.querySelector('[data-next]').hidden, start_hidden: document.querySelector('[data-start]').hidden,
  start_text: document.querySelector('[data-start]').textContent, next_text: document.querySelector('[data-next]').textContent,
  skip_visible: getComputedStyle(document.querySelector('.ob-skip')).visibility !== 'hidden' })"""
# 조각 끝 상태 클래스: 1 rev, 2 go, 3 plus, 4 cf. FL_END 는 네 장 모두, FL_CUR 은 지금 장만
FL_END = """() => { const f = document.querySelectorAll('.fl'); return ['rev', 'go', 'plus', 'cf'].every((c, i) => f[i].classList.contains(c)); }"""
FL_CUR = """() => { const f = document.querySelectorAll('.fl'), i = [...document.querySelectorAll('.ob-dots button')].findIndex(b => b.hasAttribute('aria-current'));
  return f[i].classList.contains(['rev', 'go', 'plus', 'cf'][i]); }"""
RUNNING = """() => document.getAnimations().filter(a => a.playState === 'running' && (a.effect.getTiming().duration || 0) > 1).length"""


def swipe(pg, w, h):
    # 손가락으로 왼쪽으로 쓸기 (Chromium 터치 제스처)
    cdp = pg.context.new_cdp_session(pg)
    cdp.send('Input.synthesizeScrollGesture', {'x': w * 0.8, 'y': h * 0.35, 'xDistance': -int(w * 0.7), 'yDistance': 0,
                                               'gestureSourceType': 'touch', 'speed': 1600})


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
        pg.goto(URL); pg.evaluate('document.fonts.ready'); pg.wait_for_timeout(1500)
        r = {'overflow': [], 'small_taps': []}
        def look(name):
            pg.screenshot(path=str(d / f'{name}.png'))
            r['overflow'] += pg.evaluate(OVERFLOW)
            r['small_taps'] += [t for t in pg.evaluate(TAPS) if t['w'] < 44 or t['h'] < 44]
        if desk:
            r['ob_display'] = pg.evaluate("getComputedStyle(document.querySelector('.ob')).display")
            look('00-first')
            for i, name in enumerate(NAMES):
                pg.evaluate(GO_STEP, i); pg.wait_for_timeout(WAIT[i]); look(name)
            pg.evaluate("document.querySelector('.lp-subj').scrollIntoView()"); pg.wait_for_timeout(400); look('06-subjects')
            pg.evaluate('window.scrollTo(0, document.body.scrollHeight)'); pg.wait_for_timeout(400); look('07-end')
            r['scene_end'] = pg.evaluate("document.querySelector('.scr.on').id")
        else:
            r['first_screen'] = pg.evaluate(FIRST)
            r['photos_loaded'] = pg.evaluate("document.querySelectorAll('.ob-ph.ok').length")
            look(OB_NAMES[0])
            pg.wait_for_timeout(2500); r['no_autoplay_after_4s'] = pg.evaluate(CUR) == 0
            # 1 -> 2 다음 버튼, 2 -> 3 스와이프, 3 -> 4 점, 마지막 장 상태
            nav = {}
            pg.evaluate(NEXT); pg.wait_for_timeout(OB_WAIT); nav['after_next'] = pg.evaluate(CUR); look(OB_NAMES[1])
            swipe(pg, w, h); pg.wait_for_timeout(OB_WAIT); nav['after_swipe'] = pg.evaluate(CUR); look(OB_NAMES[2])
            pg.evaluate(DOT, 3); pg.wait_for_timeout(OB_WAIT); nav['after_dot4'] = pg.evaluate(CUR); look(OB_NAMES[3])
            nav['last'] = pg.evaluate(STATE)
            nav['current_fragment_end_state'] = pg.evaluate(FL_CUR)
            nav['start_href'] = pg.evaluate("document.querySelector('[data-start]').href")
            pg.evaluate(DOT, 0); pg.wait_for_timeout(OB_WAIT); nav['back_to_1'] = pg.evaluate(STATE)
            r['nav'] = nav
            r['page_scroll_y_max'] = pg.evaluate('document.documentElement.scrollHeight - innerHeight')
        r['text'] = pg.evaluate(TEXT)
        r['console_errors'] = errs
        r['small_taps'] = list({json.dumps(t, ensure_ascii=False): t for t in r['small_taps']}.values())
        r['overflow'] = sorted(set(r['overflow']))
        out[f'{w}x{h}'] = r
        ctx.close()

    # 건너뛰기: 첫 장에서 눌러 ./app/ 으로 (390)
    ctx = b.new_context(viewport={'width': 390, 'height': 844}); pg = ctx.new_page(); pg.goto(URL); pg.wait_for_timeout(400)
    pg.click('.ob-skip'); pg.wait_for_timeout(400); out['skip_goes_to'] = pg.url
    ctx.close()

    # 움직임 줄이기 (390): 넘기지 않아도 네 조각 모두 끝 상태, 넘긴 뒤 돌고 있는 움직임 0
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, reduced_motion='reduce')
    pg = ctx.new_page(); pg.goto(URL); pg.evaluate('document.fonts.ready'); pg.wait_for_timeout(600)
    rm = {'fragments_end_state_at_load': pg.evaluate(FL_END)}
    pg.screenshot(path=str(ROOT / 'shots' / '390' / 'rm-01-recall.png'))
    for i in range(4):
        pg.evaluate(DOT, i); pg.wait_for_timeout(200); rm[f'slide{i + 1}_running'] = pg.evaluate(RUNNING); rm[f'slide{i + 1}_cur'] = pg.evaluate(CUR)
    out['reduced_motion_390'] = rm
    ctx.close()

    # 사진이 없을 때 (390): 앱 일러스트로 바뀌고 깨지지 않음 (콘솔 404 는 일부러 낸 것이라 세지 않음)
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2); pg = ctx.new_page()
    pg.route('**/photos/*.webp', lambda route: route.fulfill(status=404, body=''))
    pg.goto(URL); pg.evaluate('document.fonts.ready'); pg.wait_for_timeout(1500)
    out['photo_fallback_390'] = {'fallback_slides': pg.evaluate("document.querySelectorAll('.ob-ph.nf').length"),
                                 'photo_mode_slides': pg.evaluate("document.querySelectorAll('.ob-ph.ok').length")}
    pg.screenshot(path=str(ROOT / 'shots' / '390' / 'fb-01-recall.png'))
    ctx.close()

    # 기록이 있으면 마지막 장 버튼이 이어서 공부하기 (자동 이동 없음), 다음 버튼은 그대로 다음
    ctx = b.new_context(viewport={'width': 390, 'height': 844}); pg = ctx.new_page()
    pg.goto(URL); pg.evaluate("localStorage.setItem('cs-chagok', JSON.stringify({ read: ['ds-array'], confused: [], last: null }))")
    pg.goto(URL); pg.wait_for_timeout(500)
    first = pg.evaluate(STATE)
    pg.evaluate(DOT, 3); pg.wait_for_timeout(1200)
    last = pg.evaluate(STATE)
    out['record'] = {'url_unchanged': pg.url == URL, 'first_next_text': first['next_text'], 'last_start_text': last['start_text'], 'last_start_visible': not last['start_hidden']}
    ctx.close()
    b.close()

print(json.dumps(out, ensure_ascii=False, indent=1))
