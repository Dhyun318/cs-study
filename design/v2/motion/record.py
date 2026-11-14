# 모션 증거 4개 (6초 이하): 탑 쌓기, 답 펼침, 분할 조각 이동, 시뮬레이션 단계 넘김 -> design/v2/motion/*.mp4
# 실행: 프로젝트 루트에서 python3 -m http.server 8765 를 띄운 뒤 python3 design/v2/motion/record.py [영상 이름 ...]  (ffmpeg 필요, 이름이 없으면 4개 전부)
import pathlib, subprocess, sys, time, urllib.parse
from playwright.sync_api import sync_playwright

OUT = pathlib.Path(__file__).resolve().parent
BASE = 'http://127.0.0.1:8765/design/v2/index.html?only=1&r='
SCROLL = "document.querySelector('.screen.on .scroll')"

def tower(pg):
    pg.wait_for_timeout(900)
    pg.evaluate(f"{SCROLL}.scrollTo({{ top: document.querySelector('[data-towers]').offsetTop - 260, behavior: 'smooth' }})")
    pg.wait_for_timeout(2600)

def reveal(pg):
    pg.wait_for_timeout(1000)
    pg.click('[data-act=reveal]'); pg.wait_for_timeout(1400)
    pg.evaluate(f"{SCROLL}.scrollBy({{ top: 700, behavior: 'smooth' }})"); pg.wait_for_timeout(1800)

def pill(pg):
    pg.wait_for_timeout(800)
    for v in ('star', 'conf', 'all'):
        pg.click(f'.segc [data-v={v}]'); pg.wait_for_timeout(1200)

def simstep(pg):
    pg.wait_for_timeout(700)
    for _ in range(4):
        pg.click('.simbar [data-k=next]'); pg.wait_for_timeout(1050)

CLIPS = [('tower-stack', 'home', tower, (390, 844)), ('answer-reveal', 'q/db-transaction?ctx=book', reveal, (390, 844)),
         ('segmented-pill', 'toc', pill, (390, 844)), ('sim-step', 'sim/tcp-handshake', simstep, (390, 664))]
PICK = sys.argv[1:]
with sync_playwright() as pw:
    b = pw.chromium.launch()
    for name, route, act, (w, h) in CLIPS:
        if PICK and name not in PICK: continue
        ctx = b.new_context(viewport={'width': w, 'height': h}, record_video_dir=str(OUT / 'raw'), record_video_size={'width': w, 'height': h})
        t0 = time.time(); pg = ctx.new_page()
        pg.goto(BASE + urllib.parse.quote(route, safe='')); pg.evaluate('document.fonts.ready')
        start = time.time() - t0
        act(pg); raw = pg.video.path(); ctx.close()
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-ss', f'{start + 0.3:.2f}', '-i', raw, '-t', '6', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-an', str(OUT / f'{name}.mp4')], check=True)
        pathlib.Path(raw).unlink()
    b.close()
(OUT / 'raw').rmdir()
print(sorted(p.name for p in OUT.glob('*.mp4')))
