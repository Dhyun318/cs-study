# 장면 녹화 3개 -> design/landing/motion/*.mp4
# 실행: 프로젝트 루트에서 python3 -m http.server 8791 --bind 127.0.0.1 을 띄운 뒤 python3 design/landing/motion/record.py [영상 이름 ...]  (ffmpeg 필요, 이름이 없으면 둘 다)
# auto-390: 좁은 화면 한 화면 자동 재생을 손대지 않고 15초 (390 x 844)
# scroll-1440: 탑 쌓기 → 시뮬레이션 단계 → 헷갈림만 거르기 스크롤 10초 (1440 x 900)
# splash-390: 휴대폰 첫 방문 스플래시(사진 6컷 → 마크 → 본 화면)를 열자마자부터 3초 (390 x 844, 새 세션)
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

# (이름, 크기, 동작, 초, 여는 순간부터 자를지)
CLIPS = [('auto-390', (390, 844), auto_390, 15, False), ('scroll-1440', (1440, 900), scroll_1440, 10, False), ('splash-390', (390, 844), splash_390, 3, True)]
PICK = sys.argv[1:]
with sync_playwright() as pw:
    b = pw.chromium.launch()
    for name, (w, h), act, sec, from_open in CLIPS:
        if PICK and name not in PICK: continue
        ctx = b.new_context(viewport={'width': w, 'height': h}, record_video_dir=str(OUT / 'raw'), record_video_size={'width': w, 'height': h})
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
