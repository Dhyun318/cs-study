# 장면 녹화 3개 -> design/landing/motion/*.mp4
# 실행: 프로젝트 루트에서 python3 -m http.server 8791 --bind 127.0.0.1 을 띄운 뒤 python3 design/landing/motion/record.py [영상 이름 ...]  (ffmpeg 필요, 이름이 없으면 둘 다)
# auto-390: 좁은 화면 한 화면 자동 재생을 손대지 않고 15초 (390 x 844, 스플래시는 splash-390 에서 따로 보므로 건너뜀)
# scroll-1440: 탑 쌓기 → 시뮬레이션 단계 → 헷갈림만 거르기 스크롤 10초 (1440 x 900)
# splash-390: 휴대폰 첫 방문 스플래시(사진 6컷 → 마크 → 본 화면)를 열자마자부터 3초 (390 x 844, 새 세션)
# scroll-390: 휴대폰 스크롤 등장 15초. 기능 조각 5개가 화면에 들어올 때마다 동작(답 펼침, 칸 참, 탑 쌓기 +1, TCP 화살표, 헷갈림만 거르기), 숫자가 0 에서 올라가고, 과목·질문·끝이 올라옴
# swipe-390: 첫 화면 폰을 손가락으로 밀어 장면 넘기기 11초(왼쪽 다음, 오른쪽 이전, 1 앞 5, 5 다음 1). 손가락 자리는 회색 점(녹화에만 그림), 터치는 CDP 로 흉내
import pathlib, subprocess, sys, time
from playwright.sync_api import sync_playwright

OUT = pathlib.Path(__file__).resolve().parent
URL = 'http://127.0.0.1:8791/design/landing/index.html'
GO = """i => { const s = document.querySelectorAll('.lp-step')[i], d = innerWidth >= 960, pinH = document.querySelector('.lp-pin').offsetHeight;
  const y = s.getBoundingClientRect().top + scrollY - (d ? innerHeight / 2 - s.offsetHeight / 2 : 56 + pinH); window.scrollTo({ top: y, behavior: '%s' }); }"""

def auto_390(pg):
    pg.wait_for_timeout(15400)

def scroll_1440(pg):
    pg.evaluate(GO % 'instant', 2); pg.wait_for_timeout(1800)
    for i, ms in ((3, 4500), (4, 3900)):
        pg.evaluate(GO % 'smooth', i); pg.wait_for_timeout(ms)

def splash_390(pg):
    pg.wait_for_timeout(3000)

# 요소를 화면 가운데로 ms 동안 부드럽게 내린다(사람이 넘기는 속도처럼, 녹화용)
GLIDE = """([sel, ms]) => new Promise(r => { const e = document.querySelector(sel), y0 = scrollY;
  const y1 = Math.min(document.documentElement.scrollHeight - innerHeight, e.getBoundingClientRect().top + scrollY - (innerHeight - e.offsetHeight) / 2);
  const t0 = performance.now(), f = t => { const p = Math.min(1, (t - t0) / ms), k = p < .5 ? 2 * p * p : 1 - (-2 * p + 2) ** 2 / 2;
    scrollTo(0, y0 + (y1 - y0) * k); p < 1 ? requestAnimationFrame(f) : r(); }; requestAnimationFrame(f); })"""

def scroll_390(pg):
    pg.wait_for_timeout(400)
    for sel, hold in [('.lp-step:nth-child(1) .lp-frag', 1700), ('.lp-step:nth-child(2) .lp-frag', 1100), ('.lp-step:nth-child(3) .lp-frag', 1300),
                      ('.lp-step:nth-child(4) .lp-frag', 1900), ('.lp-step:nth-child(5) .lp-frag', 1100), ('.nums', 900),
                      ('.subs > li:nth-child(2)', 500), ('.lp-faq .list', 600), ('.lp-end', 600)]:
        pg.evaluate(GLIDE, [sel, 500]); pg.wait_for_timeout(hold)

# 손가락 자리 표시(녹화에만): 닿은 동안 회색 점이 손가락을 따라간다
FINGER = """addEventListener('DOMContentLoaded', () => { const d = document.createElement('div');
  d.style.cssText = 'position:fixed;left:0;top:0;width:40px;height:40px;margin:-20px 0 0 -20px;border-radius:50%;background:rgba(25,31,40,.28);box-shadow:0 0 0 2px rgba(255,255,255,.85);pointer-events:none;z-index:99;opacity:0;transition:opacity .12s';
  document.body.append(d);
  const at = e => { const t = e.touches[0]; if (t) { d.style.left = t.clientX + 'px'; d.style.top = t.clientY + 'px'; d.style.opacity = 1; } };
  addEventListener('touchstart', at, { passive: true, capture: true }); addEventListener('touchmove', at, { passive: true, capture: true });
  addEventListener('touchend', () => { d.style.opacity = 0; }, { capture: true }); })"""

def swipe_390(pg):
    cdp = pg.context.new_cdp_session(pg)
    def sw(dx):  # 폰 가운데를 지나게 dx 만큼 약 0.22초에 민다
        x, y = pg.evaluate("() => { const r = document.querySelector('.lp-device').getBoundingClientRect(); return [r.left + r.width / 2, r.top + r.height / 2]; }")
        x0 = x - dx / 2; cdp.send('Input.dispatchTouchEvent', {'type': 'touchStart', 'touchPoints': [{'x': x0, 'y': y}]})
        for i in range(1, 15):
            pg.wait_for_timeout(16); cdp.send('Input.dispatchTouchEvent', {'type': 'touchMove', 'touchPoints': [{'x': x0 + dx * i / 14, 'y': y - 6 * i / 14}]})
        cdp.send('Input.dispatchTouchEvent', {'type': 'touchEnd', 'touchPoints': []})
    pg.wait_for_timeout(1200)
    for dx, hold in [(-150, 1500), (-150, 1500), (150, 1100), (150, 1100), (150, 1500), (-150, 1000)]:  # 1 -> 2 -> 3 -> 2 -> 1 -> 5 -> 1
        sw(dx); pg.wait_for_timeout(hold)

# (이름, 크기, 동작, 초, 여는 순간부터 자를지)
CLIPS = [('auto-390', (390, 844), auto_390, 15, False), ('scroll-1440', (1440, 900), scroll_1440, 10, False), ('splash-390', (390, 844), splash_390, 3, True),
         ('scroll-390', (390, 844), scroll_390, 15, False), ('swipe-390', (390, 844), swipe_390, 11, False)]
TOUCH = {'scroll-390', 'swipe-390'}  # 휴대폰 터치 문맥
PICK = sys.argv[1:]
with sync_playwright() as pw:
    b = pw.chromium.launch()
    for name, (w, h), act, sec, from_open in CLIPS:
        if PICK and name not in PICK: continue
        ctx = b.new_context(viewport={'width': w, 'height': h}, record_video_dir=str(OUT / 'raw'), record_video_size={'width': w, 'height': h},
                            **({'has_touch': True, 'is_mobile': True} if name in TOUCH else {}))
        if name in ('auto-390', *TOUCH): ctx.add_init_script("sessionStorage.setItem('cs-sp', '1')")
        if name == 'swipe-390': ctx.add_init_script(FINGER)
        t0 = time.time(); pg = ctx.new_page()
        opened = time.time() - t0
        pg.goto(URL); pg.evaluate('document.fonts.ready')
        start = opened + 0.2 if from_open else time.time() - t0
        act(pg); raw = pg.video.path(); ctx.close()
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-ss', f'{max(0, start - 0.2):.2f}', '-i', raw, '-t', str(sec), '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-an', str(OUT / f'{name}.mp4')], check=True)
        pathlib.Path(raw).unlink()
    b.close()
(OUT / 'raw').rmdir()
print(sorted(p.name for p in OUT.glob('*.mp4')))
