# app/ 배포 폴더

버셀에 그대로 올리는 정적 앱(CS 차곡). 프레임워크·빌드 없음. 이 폴더가 버셀 출력 폴더다.
화면과 동작의 기준은 `../design/p-flow/index.html`(폰 화면 부분). 기능 범위는 `../docs/features.md`.

## 파일
- 손으로 쓴 것: `index.html`(틀, 아이콘 모음), `app.css`, `app.js`(화면, hash 라우팅, localStorage), `manifest.webmanifest`, `icons/`, `.vercelignore`.
- 생성물(직접 고치지 않는다): `data/notes.json`, `sims/`, `illustrations/`. `python3 scripts/build.py`(프로젝트 루트 기준)가 지우고 다시 만든다.
  - `notes.json`: `../notes/*.md` 를 변환. `[[sim:id]]` 는 그림(`illustrations/<id>.svg`) + 동작으로 보기 링크(`#/sim/<id>`). `hash-storage`, `hash-collision` 은 `hash-table`.
  - `sims/`: `../sims/` 사본(검사 스크립트, 템플릿, 문서 제외). 사본의 `_kit/kit.js` 만 `qUrl` 을 앱 질문 화면(`../../#/q/<id>`, target _top)으로 바꾼다. 원본 `../sims/` 는 고치지 않는다.
- 내용(notes, sims, 그림)을 고쳤으면 build.py 를 다시 돌린다.

## 구조 결정 (2026-11-14)
- 주소: `#/home`, `#/toc(/ds|os|db|net|star)`, `#/q/<id>(/resume)`, `#/sims`, `#/sim/<id>`, `#/review`. hash 라우팅이라 서버 설정(rewrite)이 필요 없다.
- 뒤로: 기록 칸마다 `{ d: 앱 안 깊이, y: 스크롤 }`. 깊이 0(주소로 바로 들어옴)이면 뒤로 화살표는 상위 화면으로 간다. 목차 칩, 이전/다음 질문은 기록을 쌓지 않는다(시안과 같음).
- 저장: localStorage `cs-chagok` = `{ read: [], confused: [], last: { id, pct, text } }`. 처음엔 비어 있다(시안의 예시 진도는 뺐다).
- 시뮬레이션 화면: `sims/<id>/index.html` 을 iframe 으로 넣는다. 같은 출처라 앱이 iframe 안에 스타일을 넣어 겹치는 머리를 가리고, 높이를 내용에 맞춘다(ResizeObserver). 시뮬레이션 안의 다른 시뮬레이션 링크(이어서 보기)는 앱이 가로채 `#/sim/<id>` 로 연다. 버린 대안: 높이 고정(빈 공간), postMessage(같은 출처라 불필요).
- 시안에서 뺀 것: 흐름 지도, 결정 메모, 예시 진도/처음 상태 버튼, 오른쪽 위 `… ×` 캡슐(호스트 앱 자리라 단독 웹앱에서는 누를 수 없는 가짜 버튼), 제작 중 화면(시뮬레이션 30개가 다 있다).
- vercel.json 없음: 파일 이름에 해시가 없어서 버셀 기본 캐시(매번 재검증)가 맞다. rewrite 도 필요 없다.
- 홈 화면에 추가: manifest + `icons/`(앱 색 남색 바탕에 쌓인 카드 세 장, 직접 그림). 서비스 워커는 없다(오프라인은 범위 밖).

## 배포
- `app/` 안에서 배포하거나 버셀 프로젝트 Root Directory 를 `app` 으로 둔다. 루트 `../.vercelignore` 는 루트에서 잘못 배포해도 `app/` 만 올라가게 하는 안전망.
- 배포 전 확인: 390/360 가로 넘침, 콘솔 오류, 전체 흐름, em/en dash 0, 원본 문장 겹침 검사.

## 절대 넣지 않는다 (저작권, 루트 CLAUDE.md)
- `../_reference/`(책 원문 md, 책 그림, 원본 PDF, 옛 시안), `../design/`, `../docs/`.
- 책 문장, 책 예시 값, 원 출판사 이름과 브랜딩.
