"""Check the A SVG font floor, XML, and mobile text bounds; --render updates gallery.png."""
from pathlib import Path
import argparse, xml.etree.ElementTree as ET
P = Path(__file__).resolve().parent

def check():
    files = sorted((P / 'a').glob('*.svg'))
    assert len(files) == 31, f'Expected 31 files, found {len(files)}'
    for file in files:
        root = ET.parse(file).getroot()
        labels = list(root.iter('{http://www.w3.org/2000/svg}text'))
        minimum = min(float(t.attrib['font-size']) for t in labels)
        assert minimum >= 14, (file.name, minimum)
        assert file.stat().st_size < 30000, file.name
        assert not any(s in file.read_text() for s in ['base64', '@font-face', '\u2014'])
        print(f'{file.name:26} min={minimum:g}px  {file.stat().st_size} bytes')
    return files

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--render', action='store_true')
    args = parser.parse_args()
    files = check()
    if args.render:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True, channel='chrome')
            page = browser.new_page(viewport={'width': 1600, 'height': 1000})
            errors = []
            page.on('pageerror', lambda error: errors.append(str(error)))
            page.on('console', lambda msg: errors.append(msg.text) if msg.type == 'error' else None)
            for file in files:
                page.goto(file.as_uri())
                # Check the standalone image at both the design and in-app display widths.
                for width in [390, 340]:
                    page.locator('svg').evaluate('(svg, width) => {svg.style.width=width+"px";svg.style.height="auto"}', width)
                    outside = page.evaluate('''() => {
                        const svg=document.querySelector('svg'), s=svg.getBoundingClientRect();
                        return [...svg.querySelectorAll('text')].filter(t=>{
                            const r=t.getBoundingClientRect();
                            return r.left<s.left-.5 || r.right>s.right+.5 || r.top<s.top-.5 || r.bottom>s.bottom+.5;
                        }).map(t=>t.textContent);
                    }''')
                    assert not outside, (file.name, width, outside)
            page.goto((P / 'compare.html').as_uri())
            page.evaluate('document.fonts.ready')
            assert page.locator('.frame').count() == 31
            bad = page.evaluate('''() => [...document.querySelectorAll('.artboard text')].filter(t => {
                const r=t.getBoundingClientRect(), s=t.closest('svg').getBoundingClientRect();
                return r.left<s.left-.5 || r.right>s.right+.5 || r.top<s.top-.5 || r.bottom>s.bottom+.5;
            }).map(t=>({id:t.closest('.frame').dataset.id,text:t.textContent}))''')
            assert not bad, bad
            overlaps = page.evaluate('''() => [...document.querySelectorAll('.artboard>svg')].flatMap(svg=>{
                const labels=[...svg.querySelectorAll('text')], collisions=[];
                for(let i=0;i<labels.length;i++) for(let j=i+1;j<labels.length;j++){
                    const a=labels[i].getBoundingClientRect(), b=labels[j].getBoundingClientRect();
                    if(Math.min(a.right,b.right)-Math.max(a.left,b.left)>1 &&
                       Math.min(a.bottom,b.bottom)-Math.max(a.top,b.top)>1)
                        collisions.push([svg.closest('.frame').dataset.id,labels[i].textContent,labels[j].textContent]);
                }
                return collisions;
            })''')
            assert not overlaps, overlaps
            assert page.locator('.artboard text').evaluate_all('(ts)=>ts.every(t=>+t.getAttribute("font-size")>=14)')
            assert not errors, errors
            page.screenshot(path=str(P / 'gallery.png'), full_page=True)
            browser.close()
            print('Gallery rendered; 340/390px standalone bounds, gallery bounds and text overlap checks passed; browser errors: 0.')
