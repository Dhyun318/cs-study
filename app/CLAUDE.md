# app/ 배포 폴더

버셀에 올리는 정적 앱(CS 차곡). 프레임워크 없음. 배포 때 `dist/app/` 으로 복사된다.
기준: 화면과 동작은 `../design/v2/index.html` 시안과 `../design/v2/spec/00~06`. 기능 범위는 `../docs/features.md`. p-flow 는 옛 기준이라 따르지 않는다.

## 파일
- 손으로 쓴 것:
  - `index.html`(틀, Tabler 아이콘 모음), `app.js`(화면, hash 라우팅, 저장).
  - `app.css`: 시안 CSS 를 옮겼다. 캔버스 틀은 뺐고, 컨테이너 질의는 미디어 질의로 바꿨다.
  - `manifest.webmanifest`: 흰 색 띠(#FFFFFF).
  - `icons/`: v2 브랜드(`icon.svg`, `favicon.svg`, `icon-192.png`, `icon-512.png`, `apple-touch-icon.png`, `og.png`). 원본은 `../design/v2/brand`.
  - `sw.js`: 서비스 워커. 다른 작업자가 썼다. build.py 가 `const VERSION = '...'` 한 줄만 빌드마다 바꾼다.
- 생성물(직접 고치지 않는다): `data/notes.json`, `data/precache.json`, `sims/`, `illustrations/`. `python3 scripts/build.py`(프로젝트 루트 기준)가 지우고 다시 만든다.
  - `notes.json`: `subjects`, `questions`(core/body/tails HTML), `sims`(id, s, title, qs, fig, poster{vb, fade}), `figs`{도식 id: {h, alt}}.
    - 본문 도식 자리는 `<figure class="fig" data-fig="도식 id" data-sim="시뮬레이션 id">` 로 둔다. app.js 가 그림과 `시뮬레이션으로 보기` 입구를 그린다.
  - `precache.json`: sw.js 가 설치 때 받을 sims, illustrations 파일 목록. sw.js 기준 상대 경로. 글꼴 조각은 넣지 않는다(처음 쓸 때 캐시).
  - `illustrations/`: `../illustrations/a` 의 A안 도식 SVG 31장(색을 v2 토큰으로 맞춤) + `../illustrations/v2` 의 일러스트 PNG 12장(장면 5, 기호 4, 상태 3).
    - 포스터 자리는 `../illustrations/a/posters.json` 을 build.py 가 notes.json 에 넣는다. `scripts/posters.py` 가 만들고, 도식을 고쳤을 때만 다시 돌린다(Playwright 필요).
  - `sims/`: `../sims/` 사본(검사 스크립트, 템플릿, 문서 제외). 사본의 `_kit/kit.js` 만 `qUrl` 을 앱 질문 화면(`../../#/q/<id>`, target _top)으로 바꾼다. 원본 `../sims/` 는 고치지 않는다.
- 내용(notes, sims, 그림)을 고쳤으면 build.py 를 다시 돌린다.

## 구조 결정 (2026-11-14)
- 주소: `#/home`, `#/toc`, `#/toc/<ds|os|db|net|star|conf>`, `#/q/<id>`, `#/sims`, `#/sims/<과목>`, `#/sim/<id>`. hash 라우팅이라 서버 설정이 필요 없다.
  - 질문 주소에 맥락을 붙이지 않는다. 공유한 주소가 깨끗해야 해서다(spec 00 7.1).
  - 옛 주소 `#/q/<id>/resume`, `#/random`, `#/review` 는 새 주소로 바꿔 끼운다(replaceState). 북마크가 깨지지 않게.
- 기록 칸(history.state): `{ d, k, y, focus, ctx, open/tails, sim, fromQ, rnd, fig }`.
  - `d`: 앱 안 깊이. `k`: 칸 표시. `y`: 스크롤. `focus`: 들어갈 때 누른 것(data-k).
  - `ctx`: 질문 맥락 `{ kind: book|star|conf|resume|next|random|sim, from: home|toc|sims, list(헷갈림 고정 목록), sim }`. 주소 대신 기록 칸에 둔다.
  - `open/tails`: 답 펼침. `sim`: `{ mode, step, tried, vals }`(시뮬레이션 되살림). `rnd`: 랜덤 카드.
- 뒤로: 깊이 1 이상이면 `history.back()`, 0(주소로 바로 들어옴)이면 spec 00 7.2 표의 뒤로 목적지로 바꿔 끼운다. 사이트 밖으로 튕기지 않게.
- 기록을 쌓지 않는 것: 목차 분할 선택, 장 이동, 이전/다음 질문, 다른 질문. 뒤로 가기가 한 단계씩 쌓이지 않게.
- 초점(4회차 UX 지적):
  - 새 화면은 h1(tabindex -1)로 옮긴다. 홈, 목차, 시뮬레이션 목록은 보이지 않는 h1(`홈`, `목차`, `시뮬레이션`).
  - 뒤로 오면 들어갈 때 누른 행이나 카드(data-k)로 간다. 홈 탑에서 연 목차 장은 그 장의 첫 안 읽은 행.
  - 읽음 표시와 취소 뒤에는 같은 자리 버튼. 결과 줄은 aria-live. 초기화 뒤에는 알림의 되돌리기.
  - 이유: 화면 읽기 도구와 키보드 사용자가 길을 잃지 않게.
- 저장: localStorage `cs-chagok` = `{ v: 2, read, conf, everConf, prog, last: { id, chunk, para, at }, seen }`(spec 00 6.5). 처음엔 비어 있다.
  - 옛 형식 `{ read, confused, last: { id, pct, text } }` 은 읽을 때 옮긴다. confused 는 conf, 스크롤 %는 가장 가까운 단락, text 앞 16자는 para. 모르는 id 만 버린다.
  - JSON 이 깨졌으면 원본을 `cs-chagok-bak` 에 남기고 새로 시작하며 홈에 안내 줄. 쓰기 실패면 메모리로만 쓰고 홈에 안내 줄.
  - 다른 탭 변경(storage 이벤트)은 읽음과 헷갈림을 합집합으로 합친다. 한쪽 기록이 지워지지 않게.
- 읽음 판정: 끝 영역이 50% 이상 보이고, 답을 연 지 max(10초, 예상 시간의 30%)가 지나면 자동. 예상 시간은 글자 수 / 500 분. `읽음으로 표시` 로 바로 쌓을 수도 있다.
  - `읽음 취소` 를 누르면 그 열람 동안 자동 판정을 끄고, 끝 영역 글을 `직접 표시하기 전에는 쌓이지 않아요` 로 바꾼다. `아직` 이라고 하면 저절로 다시 쌓일 것처럼 읽혀서다(4회차 UX 필수 2).
  - 끝 영역을 누르는 동안은 자동 판정을 미룬다. 자동으로 쌓인 뒤 0.6초 안의 `읽음 취소` 누름은 무시한다. 같은 자리 버튼이 반대 뜻으로 바뀔 때의 잘못 누름을 막으려고(4회차 UX 권장 4).
- 질문 머리 남은 양 글(사용자 결정): 진행 칸 옆에 둔다. 답 가림 `N단락`, 읽는 중 `남은 N단락`, 마지막 단락 `마지막 단락`, 끝 영역이 보이면 `끝까지 왔어요`.
  - `다 읽었어요` 대신 `끝까지 왔어요`: 읽음(블록 쌓임)은 시간 조건이 따로 있어서, 끝 영역의 `아직 쌓이지 않았어요` 와 같이 보여도 말이 어긋나지 않게.
  - 질문 끝에 `읽음으로 표시` / `읽음 취소` 버튼을 둔다.
- 홈 히어로 위치 글: 읽던 질문은 `6단락 중 3번째`, 아직 안 읽은 질문은 `5단락 · 안 읽음`. 옛 `처음부터 5단락` 은 무엇의 처음인지 모호했다(4회차 UX 권장 9). 단락이라는 말은 사용자 결정으로 유지.
- 못 불러옴 그림: 오프라인이든 연결 실패든 `ill-offline`, 없는 주소는 `ill-notfound`. 그림 하나가 세 뜻에 쓰였던 것을 나눴다(4회차 지적).
- 글자 200%(폭 340 미만):
  - 분할 선택은 이름 / 개수 두 줄이고 `헷갈림만` 의 `만` 은 숨긴다.
  - 장 머리는 기호 32 + 이름 17px + 개수 아랫줄. 장 이동 줄은 넘친 쪽 끝을 흐리게(IntersectionObserver).
  - 블록 한 칸이 12 미만이면 이어진 막대로 그린다. 히어로 그림은 줄여 맞춘다.
- 시뮬레이션 화면: `sims/<id>/index.html?embed=1` 을 iframe 으로 넣는다(같은 출처).
  - kit 이 embed 일 때 자기 머리, 관련 질문, 설명, 조작, 모드 탭을 숨기고 겉모양(무대 판, 직접 해 보기 판, 입력 오류)을 맞춘다.
  - 앱은 kit 의 `window.Sim`(state, go, pick, play, reset, onShow)으로 모드 분할 선택과 하단 단계 막대를 그린다.
  - kit 이 단계마다 바뀐 물체 자리(u, pop, low)를 onShow 로 알리고, 앱이 그 자리가 머리와 막대 사이에 오게 스크롤한다(spec 05 4절).
  - `글로 읽기` 는 지금 모드의 관련 질문(kit 의 보이는 .sim-q)으로 간다. 그 질문에서 연 시뮬레이션이면 `history.back()`.
  - 8초 안에 kit 이 안 뜨면 `시뮬레이션을 열지 못했어요` + 다시 시도 + 그림으로 보기. iframe 높이는 ResizeObserver 로 내용에 맞춘다.
  - 버린 대안: 앱이 iframe 안에 스타일과 MutationObserver 를 덧씌우기(시안 방식). kit 이 직접 하면 30개 시뮬레이션을 안 고치고 한 곳에서 끝난다.
- 오프라인: sw.js 는 html, app.js, app.css, manifest, notes.json 은 네트워크 먼저(4초 넘으면 캐시), 나머지는 캐시 먼저 + 뒤에서 갱신한다. 글 내용은 최신, 그림과 시뮬레이션은 빠르게.
  - 홈 `이 기기에 저장` 행은 저장됨 / 저장하는 중 / 다시 시도. sw.js 가 진행률을 알리지 않아 %는 없다.
  - 처음 저장이 끝나면 알림 한 번 `이제 인터넷 없이도 볼 수 있어요`. 새 판이 자리를 넘겨받으면 `새 내용이 있어요` + 새로 고침.
  - 오프라인이면 모든 화면 머리 아래에 안내 줄.
- 시안에서 뺀 것: 캔버스(흐름 지도, 장면 예시 진도, 폭 버튼), 일러스트 대체 SVG 그림(앱 빌드가 PNG 12장을 늘 넣으므로).
- 경로는 모두 상대 경로(fetch, 그림, sims, manifest 의 start_url 과 scope, sw.js 등록). 나중에 앱을 `/app/` 아래로 옮겨도 그대로 돈다. 첫 주소에는 랜딩이 올 예정(사용자 결정).

## 배포
- 프로젝트 루트에서 `npx vercel deploy --prod`. 루트 `../vercel.json` 의 buildCommand 가 `python3 scripts/assemble_site.py` 를 불러 `dist/` 를 만든다(내부에서 `scripts/build.py` 먼저 실행). 출력 폴더는 `dist/`.
  - `dist/index.html` 은 `design/landing`(랜딩), `dist/app/` 은 `app/`(CLAUDE.md 제외). `/app` 은 `/app/` 로 리다이렉트.
  - 루트 `../.vercelignore` 는 docs/ 중 `docs/simulations.md` 만 남긴다. build.py 가 시뮬레이션 제목 표를 읽기 때문이다.
- 배포 전 확인(전부 통과해야 한다):
  - `python3 scripts/build.py`
  - `python3 sims/_kit/check.py`
  - `python3 scripts/check_app.py`: 흐름, 넘침, 콘솔, 누르는 영역, 형광펜 40/40, 오프라인 새로고침.
  - `python3 scripts/check_sim_cover.py`: 시뮬레이션 가림, 픽셀 비교.
  - em/en dash 0: `grep -rlI -e $'\xe2\x80\x94' -e $'\xe2\x80\x93' app notes sims illustrations` 가 아무것도 안 나와야 한다.

## 절대 넣지 않는다 (저작권, 루트 CLAUDE.md)
- `../_reference/`(책 원문 md, 책 그림, 원본 PDF, 옛 시안), `../design/`, `../docs/`.
- 책 문장, 책 예시 값, 원 출판사 이름과 브랜딩.
