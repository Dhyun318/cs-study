#!/usr/bin/env python3
"""앱 흐름 검사. 실행: 프로젝트 루트에서 python3 scripts/check_app.py   (먼저 python3 scripts/build.py)
app/ 을 빈 포트로 직접 띄우고 390x844, 360x780 에서 홈 → 목차 → 질문 → ... → 진도 초기화를 실제로 누른다.
셀렉터는 design/v2/index.html 의 class, data-act, aria 기준. 못 찾으면 이유를 그대로 출력한다. FAIL 이 하나라도 있으면 exit 1."""
import http.server, json, pathlib, re, sys, threading
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

APP = pathlib.Path(__file__).resolve().parents[1] / 'app'
VIEWPORTS = [(390, 844), (360, 780)]
NAV = 'nav[aria-label="주요 화면"]'
QLINK = 'a[href*="#/q/"]'      # 질문으로 가는 행·카드
SIMLINK = 'a[href*="#/sim/"]'  # 시뮬레이션으로 가는 링크
results = []

# ---------- 작은 도구 ----------
def report(name, ok, detail=''):
    ok = bool(ok); results.append(ok)
    print(('PASS  ' if ok else 'FAIL  ') + name + (f'  | {detail}' if detail else ''), flush=True)

# 한 항목을 돌려서 PASS/FAIL 로 적는다. 함수는 통과하면 설명 글을 돌려주고, 실패하면 AssertionError 를 던진다
def step(name, fn):
    try:
        report(name, True, fn() or '')
    except AssertionError as e:
        report(name, False, str(e))
    except Exception as e:
        report(name, False, f'{type(e).__name__}: {str(e).splitlines()[0][:150]}')

def need(pg, sel, what, state='visible', t=2500):
    try:
        pg.wait_for_selector(sel, state=state, timeout=t)
    except PWTimeout:
        raise AssertionError(f'{what}: 셀렉터 {sel} 를 못 찾음')
    return pg.locator(sel).first

# 누르기: 못 찾거나 못 누르면 무엇을 누르려 했는지 적은 FAIL 로
def press(loc, what):
    try:
        loc.first.click(timeout=3000)
    except PWTimeout:
        raise AssertionError(f'{what}: 요소를 못 찾았거나 누를 수 없음')

def qids(pg):
    got = pg.evaluate(f"[...document.querySelectorAll('{QLINK}')].map(e => e.getAttribute('href') || '')")
    return list(dict.fromkeys(m.group(1) for g in got if (m := re.search(r'q/([\w-]+)', g))))  # 같은 질문으로 가는 요약 버튼과 행은 하나로

# 가로 넘침: 문서 폭, 그리고 화면 폭을 벗어난 요소(옆으로 미는 줄 안은 제외)
OVERFLOW_JS = """() => { const vw = innerWidth, out = [];
  if (document.documentElement.scrollWidth > vw) out.push('문서 ' + document.documentElement.scrollWidth + '>' + vw);
  const scroller = el => { for (let p = el.parentElement; p && p !== document.body; p = p.parentElement) { const o = getComputedStyle(p).overflowX; if (o === 'auto' || o === 'scroll') return true; } return false; };
  document.querySelectorAll('body *').forEach(el => {
    if (el.closest('svg,iframe,pre,.sr,[hidden],[inert]')) return;
    const r = el.getBoundingClientRect(); if (!r.width || !r.height) return;
    if ((r.right > vw + .5 || r.left < -.5) && !scroller(el)) out.push(el.tagName + '.' + el.className + ' ' + Math.round(r.left) + '..' + Math.round(r.right));
  });
  return [...new Set(out)].slice(0, 4); }"""
# 누르는 영역: 화면에 보이고 가운데가 다른 것에 덮이지 않은 요소의 상자가 44x44 미만이면 보고
TAP_JS = """() => { const out = [], vw = innerWidth, vh = innerHeight;
  document.querySelectorAll('a[href], button, [role=tab], [role=button], input, select, summary').forEach(el => {
    if (el.disabled || el.closest('[inert],.sr,.fake')) return;
    const r = el.getBoundingClientRect();
    if (!r.width || !r.height || r.bottom <= 0 || r.top >= vh || r.right <= 0 || r.left >= vw) return;
    const hit = document.elementFromPoint(Math.min(Math.max(r.left + r.width / 2, 1), vw - 1), Math.min(Math.max(r.top + r.height / 2, 1), vh - 1));
    if (!hit || !(el === hit || el.contains(hit))) return;
    if (r.width < 43.5 || r.height < 43.5) out.push((el.getAttribute('aria-label') || el.textContent.trim()).slice(0, 14) + ' ' + Math.round(r.width) + 'x' + Math.round(r.height));
  }); return [...new Set(out)]; }"""
SCROLL_END = "scrollTo(0, 1e9); document.querySelectorAll('.scroll, main').forEach(e => e.scrollTop = 1e9)"
READ_TOTAL = "[...document.querySelectorAll('[data-towers] a')].reduce((s, a) => s + +((a.getAttribute('aria-label') || '').match(/(\\d+)문항 읽음/) || [0, 0])[1], 0)"

# ---------- 한 크기에서 흐름 전체 ----------
def flow(b, base, w, h, notes):
    tag = f'{w}x{h}'
    ctx = b.new_context(viewport={'width': w, 'height': h}, reduced_motion='reduce')
    ctx.route(re.compile(r'^https?://(?!127\.0\.0\.1)'), lambda r: r.fulfill(status=200, body=''))  # 바깥 글꼴 주소는 빈 응답
    pg = ctx.new_page()
    errors, overflow, small, focus = [], [], [], []
    pg.on('console', lambda m: errors.append(m.text[:100]) if m.type == 'error' else None)
    pg.on('pageerror', lambda e: errors.append('pageerror ' + str(e)[:100]))
    first_q, st = notes['questions'][0]['id'], {}

    def sweep(label):  # 지금 화면을 맨 위, 맨 아래에서 넘침과 누르는 영역을 잰다
        pg.evaluate('document.fonts.ready'); pg.wait_for_timeout(200)
        for end in (0, 1):
            if end: pg.evaluate(SCROLL_END); pg.wait_for_timeout(200)
            overflow.extend(f'{label}: {x}' for x in pg.evaluate(OVERFLOW_JS))
            small.extend(f'{label}: {x}' for x in pg.evaluate(TAP_JS))
        pg.evaluate("scrollTo(0, 0); document.querySelectorAll('.scroll, main').forEach(e => e.scrollTop = 0)")

    def landed(label, prefix, back_ok=False):  # 눌러서 화면이 바뀐 뒤: 주소 확인, 초점이 h1 인지 기록. 뒤로 돌아온 화면은 들어갈 때 누른 것([data-k])도 맞음(spec 00 7.4)
        pg.wait_for_timeout(500)
        hs = pg.evaluate('location.hash')
        assert hs.startswith(prefix), f'{label}: 주소가 {prefix} 로 시작해야 하는데 {hs or "(없음)"}'
        js = "(b) => { const a = document.activeElement; return !!a && (a.tagName === 'H1' || (b && !!a.closest('[data-k]'))); }"
        focus.append((label, pg.evaluate(js, back_ok)))

    def visit(route):  # 주소만 바꿔 화면을 연다(흐름을 다시 시작하는 자리)
        pg.evaluate(f"location.hash = '#/{route}'"); pg.wait_for_timeout(500)

    def nav(name):
        press(pg.locator(f'{NAV} a', has_text=name), f'머리 탭 {name}')

    def reveal():
        need(pg, '[data-act=reveal]', '답 보기 버튼').click(); pg.wait_for_timeout(500)

    def s_home():
        pg.goto(base + '/#/home'); need(pg, 'h1', '홈 h1', 'attached'); pg.wait_for_timeout(600)
        sweep('홈'); need(pg, '.hero', '이어 읽기 카드'); need(pg, '[data-towers]', '과목 진도 탑')

    def s_toc():
        nav('목차'); landed('홈→목차', '#/toc'); sweep('목차'); need(pg, '[role=tab]', '목차 분할 탭')

    def s_sims():
        nav('시뮬레이션'); landed('목차→시뮬레이션', '#/sims'); sweep('시뮬레이션 목록'); nav('목차'); landed('시뮬레이션→목차', '#/toc')

    def s_question():
        press(pg.locator(QLINK), '목차의 질문 행'); landed('목차→질문', '#/q/')
        st['q1'] = pg.evaluate('location.hash').split('/')[2].split('?')[0]
        assert need(pg, '[data-act=reveal]', '답 보기 버튼').get_attribute('aria-expanded') == 'false', '처음엔 답이 가려져 있어야 함'
        sweep('질문(답 가림)')

    def s_reveal():
        reveal(); sweep('질문(답 펼침)'); need(pg, '.t-core', '핵심 영역(.t-core)')
        vt = pg.evaluate("[...document.querySelectorAll('[role=progressbar]')].map(e => e.getAttribute('aria-valuetext') || '')")
        assert any('단락' in v for v in vt), f'질문 진행 칸의 aria-valuetext 에 단락 글이 없음 {vt}'

    def s_conf():
        btn = need(pg, '[data-act=conf]', '헷갈려요 버튼'); btn.click(); pg.wait_for_timeout(300)
        assert btn.get_attribute('aria-pressed') == 'true', '누른 뒤 aria-pressed=true 가 아님'
        pg.reload(); pg.wait_for_timeout(800)
        assert need(pg, '[data-act=conf]', '새로고침 뒤 헷갈려요 버튼').get_attribute('aria-pressed') == 'true', '새로고침 뒤 표시가 사라짐(저장 안 됨)'

    def s_next():
        press(pg.locator('[data-bar]').get_by_text('다음 질문'), '하단 막대 [data-bar] 의 `다음 질문`'); landed('질문→다음 질문', '#/q/')
        assert pg.evaluate('location.hash').split('/')[2].split('?')[0] != st['q1'], '다음 질문인데 같은 질문'
        assert need(pg, '[data-act=conf]', '헷갈려요 버튼').get_attribute('aria-pressed') == 'false', '새 질문이 헷갈림으로 표시돼 있음'

    def s_sim():
        q = next(q for q in notes['questions'] if q['sims'])
        visit('q/' + q['id']); reveal()
        press(pg.locator(SIMLINK), '질문 안 시뮬레이션 링크'); landed('질문→시뮬레이션', '#/sim/')
        st['sim'] = pg.evaluate('location.hash').split('/')[2].split('?')[0]
        need(pg, 'iframe', '시뮬레이션 iframe'); pg.wait_for_timeout(1500); sweep('시뮬레이션')

    def s_related():
        sec = pg.locator('section', has=pg.locator('h2', has_text='관련 질문'))
        assert sec.count(), '`관련 질문` 제목의 section 을 못 찾음'
        press(sec.locator(QLINK), '관련 질문 행'); landed('시뮬레이션→관련 질문', '#/q/', back_ok=True)  # 그 질문에서 연 시뮬레이션이면 뒤로(00 7.3)
        qid = pg.evaluate('location.hash').split('/')[2].split('?')[0]
        sims = {s['id']: s for s in notes['sims']}
        assert qid in sims[st['sim']]['qs'] or st['sim'] == 'hash-table', f'{qid} 는 {st["sim"]} 의 관련 질문이 아님'

    def s_random():
        nav('홈'); landed('질문→홈', '#/home'); card = need(pg, '.rnd .card', '랜덤 질문 카드'); before = card.inner_text()
        need(pg, '[data-act=shuffle]', '섞기 버튼').click(); pg.wait_for_timeout(600)
        assert card.inner_text() != before, '섞기를 눌러도 카드가 안 바뀜'
        card.click(); landed('홈→랜덤 질문', '#/q/')
        assert need(pg, '[data-act=reveal]', '답 보기 버튼').get_attribute('aria-expanded') == 'false', '랜덤 질문은 답이 가려져야 함'
        here = pg.evaluate('location.hash')
        press(pg.locator('[data-bar]').get_by_text('다른 질문'), '하단 막대 [data-bar] 의 `다른 질문`'); pg.wait_for_timeout(500)
        assert pg.evaluate('location.hash') != here, '다른 질문을 눌러도 주소가 안 바뀜'

    def s_conf_only():
        visit('toc'); press(pg.get_by_role('tab', name=re.compile('헷갈림만')), '목차 탭 `헷갈림만`(role=tab)'); pg.wait_for_timeout(500)
        assert qids(pg) == [st['q1']], f'헷갈림만 목록이 {qids(pg)} (기대 [{st["q1"]}])'
        sweep('목차 헷갈림만')

    def s_review_row():
        nav('홈'); landed('목차→홈', '#/home')
        press(pg.get_by_text(re.compile(r'헷갈림 \d+문항 다시 보기')), '홈 `헷갈림 N문항 다시 보기` 줄'); landed('홈→헷갈림 다시 보기', '#/toc/conf')
        assert qids(pg) == [st['q1']], f'목록이 {qids(pg)} (기대 [{st["q1"]}])'

    def s_read_mark():
        visit('q/' + st['q1']); reveal(); pg.evaluate(SCROLL_END); pg.wait_for_timeout(600)
        need(pg, '[data-end]', '끝 영역([data-end])')
        if not pg.locator('[data-act=unread]').count(): press(pg.locator('[data-act=markRead]'), '`읽음으로 표시`([data-act=markRead])'); pg.wait_for_timeout(400)
        need(pg, '[data-act=unread]', '읽음 취소 버튼'); visit('home')
        assert pg.evaluate(READ_TOTAL) == 1, f'읽음으로 표시했는데 홈 읽음 합계 {pg.evaluate(READ_TOTAL)}'
        visit('q/' + st['q1']); reveal(); pg.evaluate(SCROLL_END); pg.wait_for_timeout(400)
        press(pg.locator('[data-act=unread]'), '`읽음 취소`([data-act=unread])'); pg.wait_for_timeout(400)
        need(pg, '[data-act=markRead]', '읽음 취소 뒤 `읽음으로 표시` 버튼'); visit('home')
        assert pg.evaluate(READ_TOTAL) == 0, f'읽음 취소했는데 홈 읽음 합계 {pg.evaluate(READ_TOTAL)}'

    def s_hero_text():
        txt = pg.evaluate("(() => { const p = document.querySelector('.hero [role=progressbar]'); return p ? p.parentElement.innerText : null; })()")
        assert txt is not None, '홈 히어로에 [role=progressbar] 진행 칸이 없음'
        assert '단락' in txt, f'진행 칸 옆 글에 `단락` 이 없음: {txt!r}'
        return repr(txt.strip())

    def s_reset():
        need(pg, '[data-act=reset]', '진도 초기화 행').click(); dlg = need(pg, '[role=dialog]', '확인 시트')
        assert pg.evaluate("!!document.activeElement.closest('[role=dialog]')"), '시트가 열렸는데 초점이 시트 안에 없음'
        press(dlg.get_by_text('취소', exact=True), '시트 `취소`'); pg.wait_for_timeout(400)
        assert not pg.locator('[role=dialog]').count(), '취소했는데 시트가 남음'
        assert pg.get_by_text(re.compile(r'헷갈림 \d+문항 다시 보기')).count(), '취소했는데 진도가 지워짐(확인 없이 지워지면 안 됨)'
        pg.locator('[data-act=reset]').click(); need(pg, '[data-act=doReset]', '시트 초기화 버튼').click(); pg.wait_for_timeout(600)
        assert not pg.locator('[role=dialog]').count(), '초기화 뒤 시트가 안 닫힘'
        assert not pg.get_by_text(re.compile(r'헷갈림 \d+문항 다시 보기')).count(), '초기화 뒤에도 헷갈림 다시 보기 줄이 있음'
        assert '첫 질문' in pg.locator('.hero').inner_text(), '초기화 뒤 히어로가 첫 실행 모양(`첫 질문 읽기`)이 아님'
        assert pg.evaluate(READ_TOTAL) == 0, '초기화 뒤 읽음 합계가 0 이 아님'
        need(pg, '.toast', '초기화 알림(.toast)'); assert '되돌리기' in pg.locator('.toast').inner_text(), '알림에 `되돌리기` 가 없음'
        rs = pg.locator('[data-act=reset]')
        assert rs.is_disabled() or rs.get_attribute('aria-disabled') == 'true', '지울 진도가 없는데 초기화 행이 꺼지지 않음'

    for name, fn in [('홈 열기', s_home), ('홈 → 목차', s_toc), ('목차 ↔ 시뮬레이션 목록', s_sims), ('목차 → 질문', s_question),
                     ('답 펼침', s_reveal), ('헷갈림 표시(새로고침 뒤에도)', s_conf), ('다음 질문', s_next), ('동작으로 보기(질문 → 시뮬레이션)', s_sim),
                     ('시뮬레이션 → 관련 질문', s_related), ('랜덤 질문, 다른 질문', s_random), ('목차 헷갈림만', s_conf_only),
                     ('홈 헷갈림 다시 보기 줄', s_review_row), ('읽음으로 표시 / 읽음 취소', s_read_mark)]:
        step(f'{tag} {name}', fn)
    visit('home')
    step(f'{tag} 진행 칸 옆 단락 글(홈 히어로)', s_hero_text)
    step(f'{tag} 진도 초기화(확인, 취소, 알림)', s_reset)
    # 이 크기 전체에서 센 것
    report(f'{tag} 가로 넘침 0', not overflow, f'{len(overflow)}건 {overflow[:3]}' if overflow else '')
    report(f'{tag} 누르는 요소 44x44 미만 0', not small, f'{len(small)}건 {small[:4]}' if small else '')
    report(f'{tag} 콘솔 오류 0', not errors, f'{len(errors)}건 {sorted(set(errors))[:2]}' if errors else '')
    bad = [l for l, ok in focus if not ok]
    report(f'{tag} 화면 이동 뒤 초점이 새 h1', focus and not bad, f'{len(focus) - len(bad)}/{len(focus)}' + (f' 안 맞음: {bad}' if bad else ''))
    ctx.close()

# ---------- 크기와 상관없는 검사 ----------
# 핵심 첫 문장 형광펜: 질문 40개를 열어 <mark> 글이 핵심 첫 문장과 같은지(기대값은 notes.json 에서 따로 계산)
def highlight(b, base, notes):
    strip = lambda s: re.sub(r'<[^>]+>', '', s)
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, reduced_motion='reduce'); pg = ctx.new_page(); bad = {}
    for i, q in enumerate(notes['questions']):
        p = strip(re.search(r'<p>(.*?)</p>', q['core'], re.S).group(1)); m = re.search(r'\.(?=\s|$)', p); want = p[:m.end()] if m else ''
        pg.goto(f'{base}/?q={i}#/q/{q["id"]}'); pg.wait_for_selector('h1', state='attached'); pg.wait_for_timeout(250)
        if pg.locator('[data-act=reveal]').count(): pg.locator('[data-act=reveal]').first.click(); pg.wait_for_timeout(250)
        got = ''.join(pg.locator('mark').all_inner_texts())
        if not want or ''.join(got.split()) != ''.join(want.split()): bad[q['id']] = (got[:30], want[:30])
    ctx.close()
    n = len(notes['questions']) - len(bad)
    report(f'핵심 첫 문장 형광펜 {n}/{len(notes["questions"])}', not bad, f'안 맞는 것 {list(bad.items())[:2]}' if bad else '')

# 글자 200%: 목차와 시뮬레이션 목록의 장 머리 이름 칸이 2em 이상이어야 한 글자씩 쌓이지 않는다(확대는 폭 195 창, 글자는 html font-size)
def zoom200(b, base):
    js = "[...document.querySelectorAll('.ch .nm')].map(e => { const h = e.querySelector('h2') || e; return {t: h.textContent.trim().slice(0, 8), w: Math.round(e.getBoundingClientRect().width), em: parseFloat(getComputedStyle(h).fontSize)}; })"
    for name, vp, css in [('화면 확대 200%(폭 195)', (195, 422), None), ('글자 200%(html font-size)', (390, 844), 'html { font-size: 200% !important }')]:
        def run():
            ctx = b.new_context(viewport={'width': vp[0], 'height': vp[1]}, reduced_motion='reduce'); pg = ctx.new_page(); out = []
            for route in ('toc', 'sims'):
                pg.goto(f'{base}/#/{route}'); pg.wait_for_timeout(700)
                if css: pg.add_style_tag(content=css); pg.wait_for_timeout(300)
                heads = pg.evaluate(js)
                assert heads, f'#/{route}: `.ch .nm` 장 머리 이름 칸을 못 찾음'
                narrow = [x for x in heads if x['w'] < 2 * x['em']]
                assert not narrow, f'#/{route}: 이름 칸 폭이 2em 미만 {narrow[:2]}'
                out.append(f'{route} 최소 {min(x["w"] / x["em"] for x in heads):.1f}em')
            ctx.close(); return ', '.join(out)
        step(f'{name} 장 머리 이름 칸 폭 >= 2em', run)

# 오프라인: sw.js 가 없으면 FAIL. 등록, 캐시 저장 뒤 오프라인으로 홈과 질문 하나를 새로고침해서 본다
def offline(b, base, notes):
    assert (APP / 'sw.js').exists(), 'app/sw.js 파일이 없음(서비스 워커 미구현)'
    ctx = b.new_context(viewport={'width': 390, 'height': 844}); pg = ctx.new_page()
    try:
        pg.goto(base + '/#/home'); pg.wait_for_selector('h1', state='attached')
        ready = pg.evaluate("Promise.race([navigator.serviceWorker.ready.then(() => 'ok'), new Promise(r => setTimeout(() => r('timeout'), 8000))])")
        assert ready == 'ok', '서비스 워커가 8초 안에 등록되지 않음(앱이 navigator.serviceWorker.register 를 안 부름)'
        try:
            pg.wait_for_function("caches.keys().then(async ks => { for (const k of ks) if (await (await caches.open(k)).match('data/notes.json', {ignoreSearch: true})) return true; return false; })", timeout=30000)
        except PWTimeout:
            raise AssertionError('30초 안에 data/notes.json 이 캐시에 안 들어감')
        pg.reload(); pg.wait_for_timeout(500); ctx.set_offline(True)
        pg.reload(); pg.wait_for_selector('h1', state='attached', timeout=5000)
        assert pg.locator('.hero').count() and '불러오지 못' not in pg.inner_text('body'), '오프라인 새로고침 뒤 홈이 안 뜸'
        pg.evaluate(f"location.hash = '#/q/{notes['questions'][0]['id']}'"); pg.reload(); pg.wait_for_selector('h1', state='attached', timeout=5000)
        assert pg.locator('h1').first.inner_text().strip() and pg.locator('[data-act=reveal]').count(), '오프라인 새로고침 뒤 질문이 안 뜸'
        assert pg.evaluate('navigator.onLine') is False
        return '등록, 저장, 오프라인 새로고침에서 홈과 질문 표시'
    finally:
        ctx.close()

# ---------- 시작 ----------
class Quiet(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k): super().__init__(*a, directory=str(APP), **k)
    def log_message(self, *a): pass

def main():
    if not (APP / 'data' / 'notes.json').exists():
        print('FAIL  app/data/notes.json 이 없음. 먼저 python3 scripts/build.py'); return 1
    notes = json.loads((APP / 'data' / 'notes.json').read_text())
    srv = http.server.ThreadingHTTPServer(('127.0.0.1', 0), Quiet)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    base = f'http://127.0.0.1:{srv.server_address[1]}'
    try:
        with sync_playwright() as pw:
            b = pw.chromium.launch()
            try:
                for w, h in VIEWPORTS: flow(b, base, w, h, notes)
                highlight(b, base, notes)
                zoom200(b, base)
                step('오프라인(서비스 워커)', lambda: offline(b, base, notes))
            finally:
                b.close()
    finally:
        srv.shutdown(); srv.server_close()
    fails = results.count(False)
    print(f'\n{"FAIL" if fails else "PASS"}: 총 {len(results)}항목, FAIL {fails}')
    return 1 if fails else 0

sys.exit(main())
