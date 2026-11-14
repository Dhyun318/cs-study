#!/usr/bin/env python3
"""시뮬레이션 가림 검사. 실행: 프로젝트 루트에서 python3 scripts/check_sim_cover.py [id,id,...]   (먼저 python3 scripts/build.py)
30개 시뮬레이션을 앱의 #/sim/<id> 로 열고 모든 모드의 모든 단계를 다음 버튼으로 넘긴다.
같은 폭의 아주 긴 창에서 단계 전후 무대 사진을 픽셀로 비교해 실제로 바뀐 줄을 찾고(앱의 바뀐 물체 찾기 코드는 쓰지 않음),
짧은 창에서 같은 단계를 눌렀을 때 그 줄이 고정 머리 아래, 하단 막대 위에 있는지 잰다. 가림이 있으면 exit 1.
앱 구조 가정(design/v2/index.html 기준): iframe[data-sim](다 붙으면 data-ready), iframe 안 #sim-stage, [data-bar] 하단 막대,
.simbar [data-k=next] 다음 버튼(마지막 단계에서는 data-k=toq 로 바뀜), [data-modes] button 모드 버튼, 머리 .hs 또는 header."""
import http.server, io, json, pathlib, sys, threading
import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

APP = pathlib.Path(__file__).resolve().parents[1] / 'app'
VIEWPORTS = [(390, 664), (375, 548), (360, 640)]  # 사파리 툴바가 펼쳐진 높이
TOL, GAP, MAX_STEPS, MIN_STEPS = 2, 16, 60, 100

# 무대, 머리, 막대 위치. 구조가 없으면 {err} 로 이유를 돌려준다
GEO = """() => {
  const fr = document.querySelector('iframe[data-sim]'); if (!fr) return { err: 'iframe[data-sim] 없음' };
  let d; try { d = fr.contentDocument; } catch (e) { return { err: 'iframe 안을 못 읽음' }; }
  const stage = d && d.querySelector('#sim-stage'); if (!stage) return { err: 'iframe 안에 #sim-stage 없음' };
  const bar = document.querySelector('[data-bar]'); if (!bar) return { err: '[data-bar] 하단 막대 없음' };
  const hd = document.querySelector('.hs, header'), sc = document.querySelector('.scroll');
  const s = stage.getBoundingClientRect(), f = fr.getBoundingClientRect();
  return { top: f.top + s.top, left: f.left + s.left, w: s.width, h: s.height, bar: bar.getBoundingClientRect().top,
    head: Math.max(hd ? hd.getBoundingClientRect().bottom : 0, sc ? sc.getBoundingClientRect().top : 0) }; }"""
READY = "async () => { for (let i = 0; i < 120; i++) { const f = document.querySelector('iframe[data-sim]'); if (f && f.dataset.ready) return true; await new Promise(r => setTimeout(r, 100)); } return false; }"
HAS_NEXT = "(() => { const b = document.querySelector('.simbar [data-k=next]'); return !!b && !b.disabled && b.getAttribute('aria-disabled') !== 'true'; })()"
CLICK_NEXT = "document.querySelector('.simbar [data-k=next]').click()"

# 무대 사진(회색조)
def stage_px(pg):
    g = pg.evaluate(GEO)
    return np.asarray(Image.open(io.BytesIO(pg.screenshot(clip={'x': g['left'], 'y': g['top'], 'width': g['w'], 'height': g['h']}))).convert('L'), dtype=np.int16)

# 두 사진에서 24 넘게 달라진 줄을 묶음(틈 16 이하는 한 묶음)으로 돌려준다
def changed_bands(a, b):
    h, w = max(a.shape[0], b.shape[0]), max(a.shape[1], b.shape[1])
    A, B = np.full((h, w), 255, np.int16), np.full((h, w), 255, np.int16)
    A[:a.shape[0], :a.shape[1]], B[:b.shape[0], :b.shape[1]] = a, b
    out = []
    for y in np.flatnonzero((np.abs(A - B) > 24).any(axis=1)):
        if out and y - out[-1][1] <= GAP: out[-1][1] = y + 1
        else: out.append([y, y + 1])
    return out

# 한 화면 크기에서 시뮬레이션 전부. {id: [가림 설명]} 과 통계를 돌려준다
def run_size(b, base, w, h, sims):
    tall = b.new_page(viewport={'width': w, 'height': 2400}, reduced_motion='reduce')
    short = b.new_page(viewport={'width': w, 'height': h}, reduced_motion='reduce')
    hidden, stat = {}, {'steps': 0, 'big': 0}

    def open_both(sid):
        for pg in (tall, short):
            pg.goto('about:blank'); pg.goto(f'{base}/#/sim/{sid}', wait_until='domcontentloaded')
            try: pg.wait_for_selector('iframe[data-sim]', state='attached', timeout=4000)
            except PWTimeout: raise LookupError('iframe[data-sim] 없음(앱이 시뮬레이션을 iframe[data-sim] 으로 안 넣음)')
            if not pg.evaluate(READY): raise RuntimeError('iframe[data-sim] 가 12초 안에 data-ready 가 안 됨')
            pg.wait_for_timeout(300)

    for n, sid in enumerate(sims):
        try:
            try: open_both(sid)
            except LookupError as e:  # 구조가 없으면 나머지 시뮬레이션도 같은 이유라 바로 전부 실패로 적는다
                for rest in sims[n:]: hidden[rest] = ['검사 못 함: ' + str(e)]
                break
            g = short.evaluate(GEO)
            if 'err' in g:  # 앱 구조가 맞지 않으면 나머지도 같은 이유라 바로 전부 실패로 적는다
                for rest in sims[n:]: hidden[rest] = ['검사 못 함: ' + g['err']]
                break
            if not tall.evaluate(HAS_NEXT): raise RuntimeError('.simbar [data-k=next] 다음 버튼 없음')
            modes = tall.evaluate("document.querySelectorAll('[data-modes] button').length")
            for m in range(max(1, modes)):
                if modes:  # 모드 바꾸기: 두 창 모두
                    for pg in (tall, short): pg.evaluate(f"document.querySelectorAll('[data-modes] button')[{m}].click()")
                    tall.wait_for_timeout(300)
                for s in range(MAX_STEPS):
                    if not tall.evaluate(HAS_NEXT): break
                    before = stage_px(tall)
                    for pg in (tall, short): pg.evaluate(CLICK_NEXT)
                    tall.wait_for_timeout(300)  # 짧은 창도 같은 시간 동안 스크롤을 끝낸다
                    bands = changed_bands(before, stage_px(tall)); stat['steps'] += 1
                    if not bands: continue
                    g = short.evaluate(GEO); space = g['bar'] - g['head']
                    seen = lambda y0, y1: g['top'] + y0 >= g['head'] - TOL and g['top'] + y1 <= g['bar'] + TOL
                    top, bot = bands[0][0], bands[-1][1]
                    where = f'모드{m + 1} 단계{s + 2} 바뀐 {round(g["top"] + top)}..{round(g["top"] + bot)} 막대 {round(g["bar"])} 머리 {round(g["head"])}'
                    if bot - top <= space - 2 * TOL:  # 바뀐 영역 전체가 자리에 들어가면 전부 보여야 함
                        if not seen(top, bot): hidden.setdefault(sid, []).append(where)
                    else:  # 자리보다 크면 가장 아래 묶음(새 물체)이 보여야 함. 그 묶음마저 자리보다 크면 셀 수 없음(design/v2/verify.py 와 같음)
                        stat['big'] += 1
                        lo = bands[-1]
                        if lo[1] - lo[0] <= space and not seen(*lo): hidden.setdefault(sid, []).append(where + ' (큰 변화, 아래 묶음 가림)')
        except Exception as e:
            hidden.setdefault(sid, []).append(f'검사 못 함: {type(e).__name__} {str(e).splitlines()[0][:120]}')
        print(f'  {w}x{h} {sid}: {len(hidden.get(sid, []))}', flush=True)
    tall.close(); short.close()
    return hidden, stat

class Quiet(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k): super().__init__(*a, directory=str(APP), **k)
    def log_message(self, *a): pass

def main():
    notes_path = APP / 'data' / 'notes.json'
    if not notes_path.exists():
        print('FAIL  app/data/notes.json 이 없음. 먼저 python3 scripts/build.py'); return 1
    sims = sys.argv[1].split(',') if len(sys.argv) > 1 else [s['id'] for s in json.loads(notes_path.read_text())['sims']]
    srv = http.server.ThreadingHTTPServer(('127.0.0.1', 0), Quiet)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    base = f'http://127.0.0.1:{srv.server_address[1]}'
    total, lines = 0, []
    try:
        with sync_playwright() as pw:
            b = pw.chromium.launch()
            try:
                for w, h in VIEWPORTS:
                    hidden, stat = run_size(b, base, w, h, sims)
                    n = sum(len(v) for v in hidden.values()); total += n
                    if len(sys.argv) < 2 and stat['steps'] < MIN_STEPS:  # 전체 실행인데 넘긴 단계가 너무 적으면 다음 버튼이 고장 난 것
                        n += 1; total += 1; hidden['(전체)'] = [f'넘긴 단계 {stat["steps"]}개 < {MIN_STEPS}']
                    lines.append(f'{"FAIL" if n else "PASS"}  {w}x{h} 가림 {n}건 (시뮬레이션 {len(sims)}개, 검사한 단계 {stat["steps"]}, 바뀐 영역이 자리보다 큰 단계 {stat["big"]})')
                    lines += [f'      {sid}: {x}' for sid, v in hidden.items() for x in v]
            finally:
                b.close()
    finally:
        srv.shutdown(); srv.server_close()
    print('\n' + '\n'.join(lines))
    print(f'\n{"FAIL" if total else "PASS"}: 가림 총 {total}건')
    return 1 if total else 0

sys.exit(main())
