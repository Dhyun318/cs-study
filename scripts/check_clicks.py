# 누를 수 있는 것을 전부 눌러 본다: 배포 구조(dist/)를 띄우고 랜딩(/)과 앱(/app/) 화면마다
# 보이는 a·button 을 하나씩 눌러, 누르는 동안 모양이 바뀌는지(누름 반응)와 누른 뒤 주소나 화면이 바뀌는지 잰다.
# 실행: python3 scripts/assemble_site.py && python3 scripts/check_clicks.py   (반응 없는 것이 있으면 exit 1)
import http.server, socketserver, sys, threading
from functools import partial
from pathlib import Path
from playwright.sync_api import sync_playwright

DIST = Path(__file__).resolve().parents[1] / "dist"
PAGES = ["/", "/app/#/home", "/app/#/toc", "/app/#/toc/conf", "/app/#/q/ds-stack", "/app/#/sims", "/app/#/sim/tcp-handshake"]
SIZES = [(390, 844), (1440, 900)]

# 눌러 볼 요소 목록: 화면에 보이고 꺼져 있지 않은 a, button
LIST_JS = """() => [...document.querySelectorAll('a[href], button, [role=button]')].filter(e => {
  const r = e.getBoundingClientRect(), s = getComputedStyle(e);
  return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && s.display !== 'none' && !e.disabled && e.getAttribute('aria-disabled') !== 'true';
}).map((e, i) => { e.dataset.ck = i; return { i, tag: e.tagName, text: (e.innerText || e.getAttribute('aria-label') || '').trim().slice(0, 24) }; })"""
# 모양 지문: 누름 반응을 비교할 값
LOOK_JS = "e => { const s = getComputedStyle(e); return [s.transform, s.opacity, s.backgroundColor, s.color, s.boxShadow, s.filter].join('|'); }"
STATE_JS = "() => location.href + '#' + document.body.innerHTML.length + '#' + scrollX + ',' + scrollY + '#' + [...document.querySelectorAll('[aria-pressed],[aria-selected],[aria-current],[aria-expanded]')].map(e => e.getAttribute('aria-pressed') + e.getAttribute('aria-selected') + e.getAttribute('aria-current') + e.getAttribute('aria-expanded')).join('')"


def serve():
    h = partial(http.server.SimpleHTTPRequestHandler, directory=str(DIST))
    h = type('Q', (http.server.SimpleHTTPRequestHandler,), {'log_message': lambda *a: None})
    h = partial(h, directory=str(DIST))
    srv = socketserver.TCPServer(("127.0.0.1", 0), h)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


def main():
    srv = serve()
    base = f"http://127.0.0.1:{srv.server_address[1]}"
    bad, total = [], 0
    with sync_playwright() as p:
        b = p.chromium.launch()
        for w, h in SIZES:
            for page in PAGES:
                pg = b.new_page(viewport={"width": w, "height": h})
                pg.goto(base + page); pg.wait_for_timeout(900)
                items = pg.evaluate(LIST_JS)
                pg.close()
                for it in items:
                    total += 1
                    try:
                        check_one(b, base, page, w, h, it, bad)
                    except Exception as e:  # 한 요소에서 브라우저가 멈춰도 나머지는 계속 잰다
                        bad.append(f"{w} {page} [{it['tag']} {it['text']}]: 검사 실패 {str(e)[:60]}")
        b.close()
    srv.shutdown()
    for line in bad:
        print("FAIL ", line)
    print(f"{'PASS' if not bad else 'FAIL'}: 누른 것 {total}개, 문제 {len(bad)}개")
    sys.exit(1 if bad else 0)


# 요소 하나를 새 페이지에서 눌러 본다
def check_one(b, base, page, w, h, it, bad):
                    pg = b.new_page(viewport={"width": w, "height": h})
                    errs = []
                    pg.on("pageerror", lambda e: errs.append(str(e)))
                    pg.goto(base + page); pg.wait_for_timeout(900)
                    pg.evaluate(LIST_JS)
                    el = pg.locator(f'[data-ck="{it["i"]}"]')
                    if not el.count():
                        pg.close(); return
                    el.scroll_into_view_if_needed()
                    # 누르는 동안 모양 변화
                    box = el.bounding_box()
                    before_look = el.evaluate(LOOK_JS)
                    pg.mouse.move(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
                    pg.mouse.down(); pg.wait_for_timeout(220)
                    press_look = el.evaluate(LOOK_JS) if el.count() else before_look + "x"
                    before = pg.evaluate(STATE_JS)
                    pg.mouse.up(); pg.wait_for_timeout(700)
                    after = pg.evaluate(STATE_JS)
                    pressed = press_look != before_look
                    moved = after != before
                    tag = f"{w} {page} [{it['tag']} {it['text']}]"
                    cur = el.evaluate("e => e.matches('[aria-current], [aria-selected=true], [aria-pressed=true]') || (e.closest('.lp-brand') && scrollY === 0)")
                    if (not moved and not cur) or errs:
                        bad.append(f"{tag}: 누른 뒤 변화 없음" if not moved else f"{tag}: 오류 {errs[0][:80]}")
                    elif not pressed:
                        bad.append(f"{tag}: 누름 반응 없음")
                    pg.close()


if __name__ == "__main__":
    main()
