#!/usr/bin/env python3
"""시뮬레이션 자동 검사. 실행: python3 sims/_kit/check.py
목록(sims/index.html), 템플릿, sims/*/index.html 을 headless Chromium 360px, 390px 폭으로 열어
콘솔 에러, 가로 넘침(모든 모드의 모든 단계), em/en dash 를 본다. 하나라도 실패하면 종료 코드 1."""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

SIMS = Path(__file__).resolve().parent.parent
PAGES = [SIMS / 'index.html', SIMS / '_kit' / 'template.html'] + sorted(
    p for p in SIMS.glob('*/index.html') if p.parent.name != '_kit')
OVERFLOW = 'document.documentElement.scrollWidth > document.documentElement.clientWidth'
fails = []

# em dash, en dash 는 sims 안 어떤 글에도 쓰지 않는다
for f in SIMS.rglob('*'):
    if f.suffix in ('.html', '.css', '.js', '.md') and any(c in f.read_text() for c in '\u2014\u2013'):
        fails.append(f'{f.relative_to(SIMS)}: em/en dash')

with sync_playwright() as pw:
    browser = pw.chromium.launch()
    for path in PAGES:
        for width in (360, 390):
            name = f'{path.relative_to(SIMS)} @{width}'
            page = browser.new_page(viewport={'width': width, 'height': 844})
            errors = []
            page.on('console', lambda m: errors.append(m.text) if m.type == 'error' else None)
            page.on('pageerror', lambda e: errors.append(str(e)))
            page.goto(path.as_uri(), wait_until='networkidle')
            # 모드마다 첫 단계부터 끝 단계까지 넘기며 가로 넘침을 본다
            tabs, nxt = page.locator('.sim-tabs button'), page.locator('[data-act=next]')
            for t in range(max(tabs.count(), 1)):
                if tabs.count():
                    tabs.nth(t).click()
                while True:
                    if page.evaluate(OVERFLOW):
                        step = page.evaluate("document.querySelector('.sim-count')?.textContent || '-'")
                        fails.append(f'{name}: 가로 넘침 (모드 {t + 1}, 단계 {step})')
                    if not nxt.count() or nxt.is_disabled():
                        break
                    nxt.click()
            fails += [f'{name}: 콘솔 에러 {e}' for e in errors]
            page.close()
            print(f'checked {name}')
    browser.close()

print('\n'.join(['FAIL ' + f for f in fails] or ['PASS: 콘솔 에러 0, 가로 넘침 0, em/en dash 0']))
sys.exit(1 if fails else 0)
