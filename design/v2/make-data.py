# v2 시안 데이터: app/data/notes.json 을 시안용 data.js 로 바꾼다 (도식 높이, 그림 자리 표시, 포스터 자리 포함)
# 실행: python3 design/v2/make-data.py  (프로젝트 루트 기준, 다시 돌려도 같은 결과)
import json, re, pathlib
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parents[2]
V2 = ROOT / 'design/v2'
notes = json.loads((ROOT / 'app/data/notes.json').read_text())

# 도식 색을 00 3.1 토큰 값으로 바꾼 사본 (fig/). 원본 illustrations/a/ 에도 같은 치환을 해야 한다 (시안은 design/v2 밖을 고치지 않음)
HEX = {'#596273': '#4E5968', '#EAF1FF': '#EAF1FE', '#E3E6EB': '#E5E8EB', '#F2F3F5': '#F2F4F6', '#F7F9FC': '#FFFFFF'}
(V2 / 'fig').mkdir(exist_ok=True)
svgs = {}
for p in sorted((ROOT / 'illustrations/a').glob('*.svg')):
    t = p.read_text()
    for a, b in HEX.items():
        t = re.sub(a, b, t, flags=re.I)
    # 겹친 판 모서리: 도식의 폭 넓은 흰 판은 모서리 8 (카드 16 - 간격 8). 포스터·본문 도식 판 안에서 안쪽이 바깥보다 둥글지 않게
    t = re.sub(r'(<rect x="24" y="[\d.]+" width="342" height="[\d.]+" rx=")\d+(" fill="#FFFFFF")', r'\g<1>8\2', t)
    (V2 / 'fig' / p.name).write_text(t)
    svgs[p.stem] = t

# 도식 원본 높이 (모두 폭 390)
fig_h = {k: int(re.search(r'height="(\d+)"', t).group(1)) for k, t in svgs.items()}

# 본문 그림: <figure class="ill"><img src="illustrations/X.svg" ...><a href="#/sim/Y">...</a></figure> -> 시안이 그릴 자리 표시
fig_re = re.compile(r'<figure class="ill"><img src="illustrations/([\w-]+)\.svg"[^>]*>(?:<a class="ill-go" href="#/sim/([\w-]+)">.*?</a>)?</figure>')
def figs(html):
    return fig_re.sub(lambda m: f'<figure class="fig" data-fig="{m.group(1)}" data-sim="{m.group(2) or ""}"></figure>', html)

for q in notes['questions']:
    q['body'] = figs(q['body'])
    for t in q['tails']:
        t['a'] = figs(t['a'])

# 시뮬레이션 포스터 원본: 자기 도식 (hash-table 은 hash-collision)
for s in notes['sims']:
    s['fig'] = 'hash-collision' if s['id'] == 'hash-table' else s['id']

# 포스터 자리 (04 4절): 제목 아래 첫 묶음(세로 틈 16 넘게 벌어지기 전까지, 높이 120 이상)의 테두리 + 8.
# 잘리는 물체가 없게 묶음 전체를 담고(meet), 묶음이 폭보다 높으면 폭 x .9 에서 끊고 아래를 흐리게(fade)
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
poster = {}
with sync_playwright() as pw:
    b = pw.chromium.launch(); pg = b.new_page()
    for s in notes['sims']:
        pg.set_content(f'<body style="margin:0">{svgs[s["fig"]]}</body>')
        x0, y0, x1, y1 = pg.evaluate(REGION)
        x0, y0, x1, y1 = max(0, x0 - 8), y0 - 8, min(390, x1 + 8), y1 + 8
        w, h = x1 - x0, y1 - y0
        fade = h > w * .9
        if fade: h = w * .9
        poster[s['id']] = {'vb': f'{x0:.0f} {y0:.0f} {w:.0f} {h:.0f}', 'fade': fade}
    b.close()

out = 'window.DATA = ' + json.dumps({**notes, 'figH': fig_h, 'poster': poster}, ensure_ascii=False) + ';\n'
(V2 / 'data.js').write_text(out)
print('data.js', len(out), 'bytes,', len(notes['questions']), 'questions,', len(notes['sims']), 'sims, fade:', [k for k, v in poster.items() if v['fade']])
