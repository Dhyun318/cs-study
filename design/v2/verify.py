# v2 시안 검사: 장면마다 3가지 폰 크기로 찍고(shots/), 넘침·잘림·말줄임·콘솔 오류, 모양 찌그러짐, 누르는 영역 44,
# 질문 끝 진행 칸 100%, 핵심 형광펜 40/40, 글자 200% 막대 비율, 시뮬레이션 가림(단계 전후 픽셀 비교, 앱의 감지 함수는 쓰지 않음)을 센다
# 실행: 프로젝트 루트에서 python3 -m http.server 8765 를 띄운 뒤 python3 design/v2/verify.py [장면,장면]  (끝에 failures 0 이 기준)
#       가림만: python3 design/v2/verify.py sim [390x664,375x548] [tcp-handshake,heap]   주소는 V2_BASE 로 바꿀 수 있음
import io, json, os, pathlib, re, sys, urllib.parse
import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright

V2 = pathlib.Path(__file__).resolve().parent
BASE = os.environ.get('V2_BASE', 'http://127.0.0.1:8765/design/v2/index.html')
SIZES = [(390, 844), (360, 780), (375, 667)]
SIM_VP = [(390, 664), (375, 548), (360, 640), (375, 667)]  # 사파리 툴바 펼침 높이 포함 (UX 3)
SIM_MODE = len(sys.argv) > 1 and sys.argv[1] == 'sim'
ids = re.findall(r"\n  \['(\w+)', '", (V2 / 'index.html').read_text())
only = sys.argv[1].split(',') if len(sys.argv) > 1 and not SIM_MODE else ids
full = len(only) == len(ids)

CHECK = """() => {
  const vw = innerWidth, out = [];
  const sc = document.querySelector('.screen.on .scroll');
  if (document.documentElement.scrollWidth > vw) out.push('doc-overflow ' + document.documentElement.scrollWidth);
  if (sc && sc.scrollWidth > sc.clientWidth) out.push('scroll-overflow ' + sc.scrollWidth);
  document.querySelectorAll('.screen.on *').forEach(el => {
    if (el.closest('pre,.tbl,.jump,svg,iframe')) return;
    const r = el.getBoundingClientRect(); if (!r.width || !r.height) return;
    if (r.right > vw + 0.5 || r.left < -0.5) out.push('edge ' + el.tagName + '.' + el.className + ' ' + Math.round(r.left) + '..' + Math.round(r.right));
    const cs = getComputedStyle(el);
    if (cs.textOverflow === 'ellipsis' || +cs.webkitLineClamp > 0) out.push('ellipsis ' + el.className);
    if (['hidden', 'clip'].includes(cs.overflowX) && el.scrollWidth > el.clientWidth + 1 && !el.matches('.scroll,.screen,.sr')) out.push('clipx ' + el.tagName + '.' + el.className);
    if (['hidden', 'clip'].includes(cs.overflowY) && el.scrollHeight > el.clientHeight + 1 && el.textContent.trim() && !el.matches('.scroll,.screen,.sr')) out.push('clipy ' + el.tagName + '.' + el.className);
  });
  const fr = document.querySelector('.screen.on iframe');
  if (fr) { try { const d = fr.contentDocument; if (d.documentElement.scrollWidth > fr.clientWidth + 1) out.push('iframe-overflow ' + d.documentElement.scrollWidth + '>' + fr.clientWidth); } catch (e) { out.push('iframe-noaccess'); } }
  return [...new Set(out)];
}"""

# 모양 찌그러짐: 가로·세로 배율이 다른 transform 이 모서리 둥근 요소나 그림자 있는 요소에 걸리면 실패 (분할 조각 scaleX 같은 것)
SHAPE = """() => {
  const out = [];
  document.querySelectorAll('.screen.on *').forEach(el => {
    for (const pe of [null, '::before', '::after']) {
      const cs = getComputedStyle(el, pe);
      if (pe && cs.content === 'none') continue;
      const m = (cs.transform || '').match(/matrix\\(([^)]+)\\)/); if (!m) continue;
      const [a, b, c, d] = m[1].split(',').map(Number), sx = Math.hypot(a, b), sy = Math.hypot(c, d);
      if (Math.abs(sx - sy) < 0.01) continue;
      if (parseFloat(cs.borderTopLeftRadius) > 0 || parseFloat(cs.borderBottomRightRadius) > 0 || cs.boxShadow !== 'none') out.push('distort ' + el.tagName + '.' + el.className + (pe || '') + ' ' + sx.toFixed(2) + 'x' + sy.toFixed(2));
    }
  });
  return [...new Set(out)];
}"""

# 누르는 영역: 지금 화면에서 누를 수 있는 것(가운데가 다른 것에 덮이지 않은 것)의 실제 상자가 44 x 44 이상
TAP = """() => {
  const out = [], vw = innerWidth, vh = innerHeight;
  document.querySelectorAll('.screen.on a[href], .screen.on button, .screen.on [role=tab], .screen.on input, .screen.on select').forEach(el => {
    if (el.disabled || el.closest('[inert],.sr,.fake') || getComputedStyle(el).pointerEvents === 'none') return;
    const r = el.getBoundingClientRect();
    if (!r.width || !r.height || r.bottom <= 0 || r.top >= vh || r.right <= 0 || r.left >= vw) return;
    const hit = document.elementFromPoint(Math.min(Math.max(r.left + r.width / 2, 1), vw - 1), Math.min(Math.max(r.top + r.height / 2, 1), vh - 1));
    if (!hit || !(el === hit || el.contains(hit))) return;
    if (r.width < 43.5 || r.height < 43.5) out.push('tap<44 ' + (el.getAttribute('aria-label') || el.textContent.trim()).slice(0, 16) + ' ' + Math.round(r.width) + 'x' + Math.round(r.height));
  });
  return [...new Set(out)];
}"""

MEASURE = """(t) => {
  const r = {};
  const put = (sel, lh) => { const el = document.querySelector(sel); if (!el) return null; const keep = el.textContent; el.textContent = t; const n = Math.round(el.getBoundingClientRect().height / lh); el.textContent = keep; return n; };
  r.hero = put('.screen.on .hero h2', 28); r.random = put('.screen.on .rnd .t-row', 26); r.row = put('.screen.on .rows .row .tx b', 26);
  return r;
}"""
MEASURE_Q = """(t) => { const h = document.querySelector('.screen.on .qh h1'); h.className = t.length > 40 ? 't-title2' : 't-title1'; h.textContent = t; return Math.round(h.getBoundingClientRect().height / (t.length > 40 ? 28 : 32)); }"""

# 질문 맨 아래에서 머리 진행 칸이 모두 찼는지 (각 칸 scaleX)
PROG = """() => [...document.querySelectorAll('.screen.on .hs .seg i b')].map(b => { const m = getComputedStyle(b).transform.match(/matrix\\(([^,]+)/); return m ? +(+m[1]).toFixed(3) : 1; })"""

# 시뮬레이션 가림 (앱과 다른 방법): 같은 폭의 아주 긴 창에서 단계 전후 무대를 사진으로 찍어 실제로 바뀐 픽셀 줄을 찾고,
# 짧은 창에서 같은 단계를 눌렀을 때 그 줄들이 머리 아래, 막대 위에 있는지 센다. 바뀐 영역이 자리보다 크면 가장 아래 묶음(새 물체)이 보여야 한다
SIM_GEO = """() => { const sc = document.querySelector('.screen.on'), fr = sc.querySelector('iframe[data-sim]');
  const st = fr.contentDocument.querySelector('#sim-stage').getBoundingClientRect(), f = fr.getBoundingClientRect();
  return { top: f.top + st.top, left: f.left + st.left, w: st.width, h: st.height, bar: sc.querySelector('[data-bar]').getBoundingClientRect().top,
    head: Math.max(sc.querySelector('.hs').getBoundingClientRect().bottom, sc.querySelector('.scroll').getBoundingClientRect().top) }; }"""
SIM_READY = "async () => { for (let g = 0; g < 120; g++) { const fr = document.querySelector('.screen.on iframe[data-sim]'); if (fr && fr.dataset.ready) return true; await new Promise(r => setTimeout(r, 100)); } return false; }"
NEXT = "document.querySelector('.screen.on .simbar [data-k=next]')"
TOL = 2

def stage_px(pg):
    g = pg.evaluate(SIM_GEO)
    return np.asarray(Image.open(io.BytesIO(pg.screenshot(clip={'x': g['left'], 'y': g['top'], 'width': g['w'], 'height': g['h']}))).convert('L'), dtype=np.int16)

def changed_bands(a, b, gap=16):
    h, w = max(a.shape[0], b.shape[0]), max(a.shape[1], b.shape[1])
    A = np.full((h, w), 255, np.int16); A[:a.shape[0], :a.shape[1]] = a
    B = np.full((h, w), 255, np.int16); B[:b.shape[0], :b.shape[1]] = b
    rows = np.flatnonzero((np.abs(A - B) > 24).any(axis=1))
    out = []
    for y in rows:
        if out and y - out[-1][1] <= gap: out[-1][1] = y + 1
        else: out.append([y, y + 1])
    return out

def sim_occlusion(br, w, h, sims, log=None):
    tall = br.new_page(viewport={'width': w, 'height': 2400}, reduced_motion='reduce')
    short = br.new_page(viewport={'width': w, 'height': h}, reduced_motion='reduce')
    res = {'steps': 0, 'hidden': {}, 'big': {}}
    for sid in sims:
        try:
            for pg in (tall, short):
                pg.goto(url(r=f'sim/{sid}'), wait_until='domcontentloaded'); pg.evaluate(SIM_READY); pg.wait_for_timeout(300)
            nm = tall.evaluate("document.querySelectorAll('.screen.on [data-modes] button').length")
            for m in range(max(1, nm)):
                if nm:
                    for pg in (tall, short): pg.evaluate(f"document.querySelectorAll('.screen.on [data-modes] button')[{m}].click()")
                    tall.wait_for_timeout(300)
                for s in range(60):
                    if not tall.evaluate(NEXT): break
                    before = stage_px(tall)
                    for pg in (tall, short): pg.evaluate(NEXT + '.click()')
                    tall.wait_for_timeout(300); short.wait_for_timeout(120)
                    bands = changed_bands(before, stage_px(tall)); res['steps'] += 1
                    if not bands: continue
                    g = short.evaluate(SIM_GEO); space = g['bar'] - g['head']
                    vis = lambda b0, b1: g['top'] + b0 >= g['head'] - TOL and g['top'] + b1 <= g['bar'] + TOL
                    top, bot = bands[0][0], bands[-1][1]
                    where = f'm{m} s{s + 2} {round(g["top"] + top)}..{round(g["top"] + bot)} bar {round(g["bar"])} head {round(g["head"])}'
                    if bot - top <= space - 2 * TOL:
                        if not vis(top, bot): res['hidden'].setdefault(sid, []).append(where)
                    else:
                        res['big'].setdefault(sid, []).append(where)
                        lo = bands[-1]
                        if lo[1] - lo[0] <= space and not vis(*lo): res['hidden'].setdefault(sid, []).append(where + ' (큰 변화, 아래 묶음 가림)')
        except Exception as e:
            res['hidden'].setdefault(sid, []).append('error ' + str(e)[:160])
        if log: log(sid, res['hidden'].get(sid, []))
    tall.close(); short.close()
    return res

def quant(p):
    im = Image.open(p).convert('RGB')
    im.quantize(colors=256, method=Image.Quantize.MEDIANCUT).save(p, optimize=True)

def url(**k):
    return BASE + '?only=1&' + '&'.join(f'{a}={urllib.parse.quote(str(b), safe="")}' for a, b in k.items())

notes = json.loads((V2.parents[1] / 'app/data/notes.json').read_text())
titles = {k: next(q['title'] for q in notes['questions'] if q['id'] == k) for k in ['db-bplus', 'net-google', 'ds-collision', 'ds-stack']}
long_sim = max(notes['sims'], key=lambda s: len(s['title']))['title']
strip = lambda h: re.sub(r'<[^>]+>', '', h)
size = {q['id']: len(strip(q['core'] + q['body']) + ''.join(t['q'] + strip(t['a']) for t in q['tails'])) for q in notes['questions']}
short_q, long_q = min(size, key=size.get), max(size, key=size.get)

report = {'issues': {}, 'errors': [], 'lines': {}, 'prog': {}, 'mark': {}, 'sim': {}, 'extra': {}}
errs = lambda tag: (lambda m: report['errors'].append(f'{tag} {m.type} {m.text}') if m.type in ('error', 'warning') else None)

# 핵심 첫 문장(형광펜 기대값): 핵심 첫 문단의 글에서 처음 나오는 `. `(또는 문단 끝 .) 까지. 앱 코드와 따로 계산한다
def first_sentence(core):
    p = strip(re.search(r'<p>(.*?)</p>', core, re.S).group(1))
    m = re.search(r'\.(?=\s|$)', p)
    return p[:m.end()] if m else ''

def sims_only():
    vps = [tuple(map(int, x.split('x'))) for x in sys.argv[2].split(',')] if len(sys.argv) > 2 else SIM_VP[:3]
    sims = sys.argv[3].split(',') if len(sys.argv) > 3 else [s['id'] for s in notes['sims']]
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        for w, h in vps:
            r = sim_occlusion(b, w, h, sims, log=lambda sid, x: print(f'{w}x{h} {sid} {len(x)}', flush=True))
            report['sim'][f'{w}x{h}'] = r
        b.close()
    report['failures'] = sum(len(x) for v in report['sim'].values() for x in v['hidden'].values())
    print(json.dumps(report, ensure_ascii=False, indent=1))

if SIM_MODE:
    sims_only(); sys.exit()

with sync_playwright() as pw:
    b = pw.chromium.launch()
    def page(w, h, tag, **kw):
        pg = b.new_page(viewport={'width': w, 'height': h}, **kw)
        pg.on('console', errs(tag)); pg.on('pageerror', lambda e: report['errors'].append(f'{tag} pageerror {e}'))
        return pg
    def check(pg, key):
        iss = pg.evaluate(CHECK) + pg.evaluate(SHAPE) + pg.evaluate(TAP)
        if iss: report['issues'][key] = iss

    # 1) 장면 x 3 크기
    for w, h in SIZES:
        (V2 / 'shots' / str(w)).mkdir(parents=True, exist_ok=True)
        pg = page(w, h, w)
        for i in only:
            pg.goto(url(s=i)); pg.wait_for_timeout(2600 if i.startswith('sim') else 1400)
            check(pg, f'{w}/{i}')
            path = V2 / 'shots' / str(w) / f'{i}.png'
            pg.screenshot(path=str(path)); quant(path)
            if i == 'home' and w in (390, 360):
                report['lines'][w] = {k: pg.evaluate(MEASURE, t) for k, t in titles.items()}
            if i == 'q' and w in (390, 360):
                for k, t in titles.items(): report['lines'][w][k]['question'] = pg.evaluate(MEASURE_Q, t)
            if i == 'sims' and w in (390, 360):
                report['lines'][w]['sim44'] = pg.evaluate("(t) => { const el = document.querySelector('.screen.on .simc .t-row'); el.textContent = t; return Math.round(el.getBoundingClientRect().height / 26); }", long_sim)
        pg.close()
    if not full:
        b.close(); print(json.dumps(report, ensure_ascii=False, indent=1)); sys.exit()

    # 2) 질문 끝에서 진행 칸 100% (가장 짧은 답, 가장 긴 답)
    pg = page(390, 844, 'prog')
    for qid in (short_q, long_q):
        pg.goto(url(r=f'q/{qid}?ctx=book&open=1')); pg.wait_for_timeout(1200)
        top = pg.evaluate(PROG)
        pg.evaluate("document.querySelector('.screen.on .scroll').scrollTop = 1e6"); pg.wait_for_timeout(800)
        end = pg.evaluate(PROG)
        report['prog'][f'{qid} ({size[qid]}자)'] = {'top': top, 'end': end, 'ok': all(x >= .999 for x in end) and not all(x >= .999 for x in top)}

    # 2-1) 핵심 첫 문장 형광펜: 40문항을 답 펼친 채로 열어 <mark> 글이 기대값과 같은지
    bad = {}
    for q in notes['questions']:
        got = pg.evaluate("(id) => { paint('q/' + id + '?ctx=book&open=1'); return [...document.querySelectorAll('.screen.on .t-core mark')].map(m => m.textContent).join(''); }", q['id'])
        want = first_sentence(q['core'])
        if not want or got.strip() != want.strip(): bad[q['id']] = {'got': got[:60], 'want': want[:60]}
    report['mark'] = {'ok': len(notes['questions']) - len(bad), 'of': len(notes['questions']), 'bad': bad}
    pg.close()

    # 3) 시뮬레이션 가림: 30개 x 모든 모드·단계 x 4 화면 높이 (픽셀 비교, 위 sim_occlusion)
    for w, h in SIM_VP:
        report['sim'][f'{w}x{h}'] = sim_occlusion(b, w, h, [s['id'] for s in notes['sims']])
    # 증거 사진: 마지막 단계로 바로 열지 않고 `다음` 을 눌러 넘긴 화면
    (V2 / 'shots' / 'simvp').mkdir(exist_ok=True)
    for w, h in SIM_VP:
        pg = page(w, h, f'simvp{w}x{h}', reduced_motion='reduce')
        pg.goto(url(r='sim/tcp-handshake')); pg.evaluate(SIM_READY); pg.wait_for_timeout(400)
        for i, n in (('sim', 1), ('simLast', 60)):
            for _ in range(n):
                if not pg.evaluate(NEXT): break
                pg.evaluate(NEXT + '.click()'); pg.wait_for_timeout(250)
            pg.wait_for_timeout(300)
            f = V2 / 'shots' / 'simvp' / f'{w}x{h}-{i}.png'; pg.screenshot(path=str(f)); quant(f)
        pg.close()

    # 4) 증거 사진: 포스터 30장 한 장(360), 글자 200%(폭 195, 하단 막대는 화면 높이의 35% 이하), 노치·홈 표시줄, 넓은 화면, 가로 모드
    ex = V2 / 'shots' / 'extra'; ex.mkdir(exist_ok=True)
    def shot(w, h, name, q, tag, **kw):
        pg = page(w, h, tag, **kw); pg.goto(url(**q)); pg.wait_for_timeout(2600)
        iss = pg.evaluate(CHECK) + pg.evaluate(SHAPE)
        if name.startswith('zoom200'):
            ratio = pg.evaluate("(() => { const b = document.querySelector('.screen.on [data-bar]'); return b ? b.getBoundingClientRect().height / innerHeight : 0; })()")
            report.setdefault('bar200', {})[name] = round(ratio, 3)
            if ratio > .35: iss.append(f'bar {ratio:.0%} > 35%')
        if iss: report['extra'][name] = iss
        pg.screenshot(path=str(ex / f'{name}.png')); quant(ex / f'{name}.png'); pg.close()
    shot(360, 5600, 'posters-360', {'s': 'sims'}, 'posters')
    for i in ('home', 'q', 'qa', 'sim', 'simLast'): shot(195, 422, f'zoom200-{i}', {'s': i}, 'zoom200', device_scale_factor=4)
    for i in ('home', 'q', 'sim'): shot(390, 844, f'safe-{i}', {'s': i, 'safe': 1}, 'safe')
    shot(1024, 768, 'wide-home', {'s': 'home'}, 'wide')
    for i in ('home', 'q', 'sim'): shot(844, 390, f'landscape-{i}', {'s': i}, 'landscape')

    # 5) 캔버스 1440
    pg = page(1440, 900, 'canvas')
    pg.goto(BASE); pg.wait_for_timeout(9000)
    report['canvas_overflow'] = pg.evaluate('document.documentElement.scrollWidth > innerWidth')
    pg.screenshot(path=str(V2 / 'shots' / 'canvas-1440.png'), full_page=True); quant(V2 / 'shots' / 'canvas-1440.png')
    pg.close()
    b.close()

total = sum(p.stat().st_size for p in (V2 / 'shots').rglob('*.png'))
report['shots'] = {'count': len(list((V2 / 'shots').rglob('*.png'))), 'MB': round(total / 1e6, 2)}
report['failures'] = (sum(len(v) for v in report['issues'].values()) + len(report['errors']) + sum(not v['ok'] for v in report['prog'].values())
                      + len(report['mark']['bad']) + sum(len(x) for v in report['sim'].values() for x in v['hidden'].values())
                      + sum(len(v) for v in report['extra'].values()) + int(bool(report.get('canvas_overflow'))))
print(json.dumps(report, ensure_ascii=False, indent=1))
