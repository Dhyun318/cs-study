# 배포 폴더 dist/ 를 만든다: / 는 랜딩(design/landing), /app/ 은 웹앱(app/). 버셀 buildCommand 가 이걸 부른다.
# 실행: python3 scripts/assemble_site.py  (표준 라이브러리만, 어디서 실행해도 된다)
import re, shutil, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST, LANDING = ROOT / "dist", ROOT / "design/landing"
APP_ICON = {"favicon.svg", "og.png"}  # 랜딩의 파비콘과 og 이미지는 앱 것을 가리킨다

# app/ 생성물(data, sims, illustrations)을 먼저 만든다. 실패하면 여기서 멈춘다
subprocess.run([sys.executable, str(ROOT / "scripts/build.py")], check=True)

# dist/ 를 새로 만들고 app/ 을 dist/app/ 으로 복사한다(app/CLAUDE.md 제외)
shutil.rmtree(DIST, ignore_errors=True)
shutil.copytree(ROOT / "app", DIST / "app", ignore=shutil.ignore_patterns("CLAUDE.md"))

# 랜딩이 ../ 로 가리키는 자원을 dist/assets/ 로 복사하고 경로를 바꿔 쓴다
html = (LANDING / "index.html").read_text(encoding="utf-8")


def move(m):
    src = (LANDING / m[2]).resolve()
    if src.name in APP_ICON:
        return f"{m[1]}./app/icons/{src.name}"
    (DIST / "assets").mkdir(exist_ok=True)
    shutil.copy(src, DIST / "assets" / src.name)  # 없는 파일이면 여기서 오류로 멈춘다
    return f"{m[1]}./assets/{src.name}"


(DIST / "index.html").write_text(re.sub(r"""(["'(])(\.\./[^"')]+)""", move, html), encoding="utf-8")
print(f"dist/ 완성: {sum(1 for p in DIST.rglob('*') if p.is_file())}개 파일")
