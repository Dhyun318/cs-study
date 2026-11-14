# 시뮬레이션 포스터 자리(illustrations/a/posters.json)를 도식 SVG 에서 잰다. 도식을 고쳤을 때만 다시 돌린다(로컬, Playwright 필요)
# 자리 = 제목 아래 첫 묶음(세로 틈 16 넘게 벌어지기 전까지, 높이 120 이상)의 테두리 + 8. 묶음이 폭보다 높으면 폭 x .9 에서 끊고 아래를 흐린다(fade)
# design/v2/make-data.py 의 같은 계산을 옮긴 것. 실행: python3 scripts/posters.py
import json, pathlib
from playwright.sync_api import sync_playwright

A = pathlib.Path(__file__).resolve().parents[1] / 'illustrations/a'
REGION = """() => {
  const svg = document.querySelector('svg'), o = svg.getBoundingClientRect();
  const bs = [...svg.querySelectorAll('rect,circle,ellipse,path,line,polyline,polygon,text,image')]
    .filter(e => !e.closest('defs,marker'))
    .map(e => { const r = e.getBoundingClientRect(); return { x: r.left - o.left, y: r.top - o.top, r: r.right - o.left, b: r.bottom - o.top }; })
    .filter(b => b.y >= 98 && b.r > b.x).sort((a, b) => a.y - b.y);
  let top = bs[0].y, bot = bs[0].b, x0 = 390, x1 = 0;
  for (const b of bs) { if (b.y > bot + 16 && bot - top >= 120) break; bot = Math.max(bot, b.b); x0 = Math.min(x0, b.x); x1 = Math.max(x1, b.r); }
  return [x0, top, x1, bot];
}"""

out = {}
with sync_playwright() as pw:
    b = pw.chromium.launch(); pg = b.new_page()
    for p in sorted(A.glob('*.svg')):
        pg.set_content(f'<body style="margin:0">{p.read_text()}</body>')
        x0, y0, x1, y1 = pg.evaluate(REGION)
        x0, y0, x1, y1 = max(0, x0 - 8), y0 - 8, min(390, x1 + 8), y1 + 8
        w, h = x1 - x0, y1 - y0
        fade = h > w * .9
        out[p.stem] = {'vb': f'{x0:.0f} {y0:.0f} {w:.0f} {(w * .9 if fade else h):.0f}', 'fade': fade}
    b.close()
(A / 'posters.json').write_text(json.dumps(out, indent=1) + '\n')
print(len(out), 'posters, fade:', [k for k, v in out.items() if v['fade']])
