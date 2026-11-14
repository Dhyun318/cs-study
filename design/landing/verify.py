# 랜딩 시안 검사 + 장면 스크린샷 -> design/landing/shots/<폭>/*.png
# 실행: 프로젝트 루트에서 python3 -m http.server 8791 --bind 127.0.0.1 을 띄운 뒤 python3 design/landing/verify.py
# 넓은 화면(1440): 스크롤로 장면을 넘긴다. 좁은 화면(390, 360): 한 화면 자동 재생, 장면 점을 눌러 넘긴다.
# 검사: 가로 넘침(폰 화면 안쪽 제외 모든 요소가 화면 폭 안), 콘솔 오류, 누르는 영역 44 미만, 글의 em/en dash·큰따옴표,
#       좁은 화면 첫 화면에 시작하기·폰·장면 점이 들어오는지, 자동 재생(저절로 넘어감, 점 누르면 멈춤, 탭이 안 보이면 멈춤),
#       움직임 줄이기(자동 재생 없음, 돌고 있는 움직임 0), 기록 있으면 앱으로 넘김(?stay=1 이면 안 넘김)
import json, pathlib
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent
URL = 'http://127.0.0.1:8791/design/landing/index.html'
SIZES = [(390, 844), (360, 780), (1440, 900)]
# 장면마다 타임라인이 끝나는 시간(ms) + 여유
WAIT = [1600, 4600, 1900, 4500, 3900]
NAMES = ['01-reveal', '02-read', '03-tower', '04-sim', '05-conf']

GO_STEP = """i => { const s = document.querySelectorAll('.lp-step')[i];
  window.scrollTo(0, s.getBoundingClientRect().top + scrollY - (innerHeight / 2 - s.offsetHeight / 2)); }"""
DOT = "i => document.querySelectorAll('.lp-dots button')[i].click()"
CUR = "() => [...document.querySelectorAll('.lp-dots button')].findIndex(b => b.hasAttribute('aria-current')) + 1"
OVERFLOW = """() => [...document.querySelectorAll('body *')].filter(e => !e.closest('.lp-screen') && !e.closest('svg[width="0"]')).filter(e => {
  const r = e.getBoundingClientRect(); return r.width && (r.right > innerWidth + .5 || r.left < -.5); }).map(e => e.tagName + '.' + e.className).slice(0, 10)"""
TAPS = """() => [...document.querySelectorAll('a, button, input, select, textarea, [role=button], [tabindex]')].filter(e => !e.closest('[inert]')).filter(e => {
  const cs = getComputedStyle(e), r = e.getBoundingClientRect(); return cs.visibility !== 'hidden' && cs.display !== 'none' && r.width > 0; })
  .map(e => { const r = e.getBoundingClientRect(); return { t: e.textContent.trim().slice(0, 20) || e.getAttribute('aria-label'), w: Math.round(r.width), h: Math.round(r.height) }; })"""
TEXT = """() => { const t = document.body.innerText; return { emdash: (t.match(/\\u2014/g) || []).length, endash: (t.match(/\\u2013/g) || []).length,
  dquote: (t.match(/["\\u201C\\u201D]/g) || []).length }; }"""
FIRST = """() => { const b = s => Math.round(document.querySelector(s).getBoundingClientRect().bottom);
  return { viewport_h: innerHeight, cta_bottom: b('[data-hero-cta]'), phone_bottom: b('.lp-device'), dots_bottom: b('.lp-dots'), caption_bottom: b('.lp-cap'), page_h: document.documentElement.scrollHeight }; }"""
RUNNING = """() => document.getAnimations().filter(a => a.playState === 'running' && (a.effect.getTiming().duration || 0) > 1).length"""
HIDE = """h => { Object.defineProperty(document, 'hidden', { value: h, configurable: true }); document.dispatchEvent(new Event('visibilitychange')); }"""

out = {}
with sync_playwright() as pw:
    b = pw.chromium.launch()
    for w, h in SIZES:
        d = ROOT / 'shots' / str(w); d.mkdir(parents=True, exist_ok=True)
        for f in d.glob('*.png'): f.unlink()
        pg = b.new_page(viewport={'width': w, 'height': h}, device_scale_factor=2)
        errs = []
        pg.on('console', lambda m: m.type == 'error' and errs.append(m.text))
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto(URL); pg.evaluate('document.fonts.ready'); pg.wait_for_timeout(1200)
        r = {'overflow': [], 'small_taps': []}
        def look(name):
            pg.screenshot(path=str(d / f'{name}.png'))
            r['overflow'] += pg.evaluate(OVERFLOW)
            r['small_taps'] += [t for t in pg.evaluate(TAPS) if t['w'] < 44 or t['h'] < 44]
        desk = w >= 960
        if not desk:
            r['first_screen'] = pg.evaluate(FIRST)
            # 자동 재생: 손대지 않으면 장면이 저절로 넘어간다
            a0 = pg.evaluate(CUR); pg.wait_for_timeout(2600); a1 = pg.evaluate(CUR)
            r['autoplay'] = {'scene_at_1s': a0, 'scene_at_4s': a1}
        look('00-first')
        for i, name in enumerate(NAMES):
            pg.evaluate(DOT if not desk else GO_STEP, i); pg.wait_for_timeout(WAIT[i]); look(name)
        if desk:
            pg.evaluate("document.querySelector('.lp-subj').scrollIntoView()"); pg.wait_for_timeout(400); look('06-subjects')
        else:
            # 점을 누른 뒤에는 자동 재생이 멈춰 있어야 한다 (마지막으로 누른 5번 그대로)
            pg.wait_for_timeout(3000); r['autoplay']['after_dot_click_stays'] = pg.evaluate(CUR)
        pg.evaluate('window.scrollTo(0, document.body.scrollHeight)'); pg.wait_for_timeout(400); look('07-end' if desk else '06-bottom')
        r['scene_end'] = pg.evaluate("document.querySelector('.scr.on').id")
        r['text'] = pg.evaluate(TEXT)
        r['console_errors'] = errs
        r['small_taps'] = list({json.dumps(t, ensure_ascii=False): t for t in r['small_taps']}.values())
        r['overflow'] = sorted(set(r['overflow']))
        out[f'{w}x{h}'] = r
        pg.close()

    # 탭이 안 보이면 자동 재생이 멈추고, 다시 보이면 이어진다 (390)
    pg = b.new_page(viewport={'width': 390, 'height': 844}); pg.goto(URL); pg.wait_for_timeout(500)
    pg.evaluate(HIDE, True); s0 = pg.evaluate(CUR); pg.wait_for_timeout(6500); s1 = pg.evaluate(CUR)
    pg.evaluate(HIDE, False); pg.wait_for_timeout(6500); s2 = pg.evaluate(CUR)
    out['visibility_pause_390'] = {'hidden_start': s0, 'hidden_after_6_5s': s1, 'visible_after_6_5s': s2}
    pg.close()

    # 움직임 줄이기 (390): 자동 재생 없음, 점으로 넘기면 끝 상태 그림, 돌고 있는 움직임 0
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, reduced_motion='reduce')
    pg = ctx.new_page(); pg.goto(URL); pg.evaluate('document.fonts.ready'); pg.wait_for_timeout(600)
    rm = {'scene_at_start': pg.evaluate(CUR)}
    pg.wait_for_timeout(5000); rm['scene_after_5s_no_autoplay'] = pg.evaluate(CUR)
    for i, name in enumerate(NAMES):
        pg.evaluate(DOT, i); pg.wait_for_timeout(150)
        rm[name + '_running'] = pg.evaluate(RUNNING)
        if name in ('02-read', '04-sim'): pg.screenshot(path=str(ROOT / 'shots' / '390' / f'rm-{name}.png'))
    rm['sim_count_text'] = pg.evaluate("document.querySelector('#sim [data-count]').textContent")
    rm['toc_filtered'] = pg.evaluate("document.querySelector('#toc').classList.contains('cf')")
    out['reduced_motion_390'] = rm
    ctx.close()

    # 기록이 있으면 ./app/ 으로, ?stay=1 이면 그대로
    ctx = b.new_context(); pg = ctx.new_page()
    pg.goto(URL); pg.evaluate("localStorage.setItem('cs-chagok', JSON.stringify({ read: ['ds-array'], confused: [], last: null }))")
    pg.goto(URL + '?stay=1'); stay = pg.url
    pg.goto(URL); pg.wait_for_timeout(300); moved = pg.url
    out['redirect'] = {'with_stay': stay, 'without_stay': moved}
    ctx.close()
    b.close()

print(json.dumps(out, ensure_ascii=False, indent=1))
