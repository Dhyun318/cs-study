# 남은 작업 (이어서 하기용)

토큰이 부족해 멈췄거나 세션이 바뀌었으면 이 파일부터 보고 이어서 한다. 끝낸 항목은 [x]로 바꾼다.

## 진행 상태 (2026-11-14 기준)
- [x] 본문 새로 쓰기 `notes/` 5개
- [x] 시뮬레이션 공통 틀 `sims/_kit/` + 첫 시뮬레이션 `sims/hash-table/`
- [x] 일러스트 A 31장 `illustrations/a/` (코덱스)
- [x] P 화면 흐름 `design/p-flow/index.html` (오픽 `spike/design/final/index.html` 형식)
- [x] 시뮬레이션 29개 `sims/<id>/` (과목별 5묶음). 다 되면 `sims/index.html`에 각 묶음 보고의 `<li>` 줄 등록, `python3 sims/_kit/check.py` 전체 PASS 확인
- [x] 앱 만들기 `app/`
- [x] 버셀 배포: https://cs-study-sooty.vercel.app (프로젝트 cs-study, 2026-11-14). 다시 배포: `python3 scripts/build.py` 후 `cd app && npx vercel deploy --prod`

## 상태 확인 방법
- 시뮬레이션: `ls sims/` 폴더 수(목표: _kit, hash-table + 29개)와 `python3 sims/_kit/check.py`
- P 흐름: `design/p-flow/index.html`이 오픽 형식(제목, 결정 메모, 흐름 묶음 썸네일, 왼쪽 폰)인지

## 앱 만들기 계획 (결정)
- 기준: `design/p-flow/index.html` 화면 그대로 구현. 화면 목록은 `docs/features.md`.
- 순수 HTML/CSS/JS, 프레임워크 없음. hash 라우팅(#/home, #/toc, #/q/<id>, #/sims, #/sim/<id>, #/review).
- 본문: `notes/*.md`를 스크립트로 `app/data/notes.json`으로 변환해 둔다(빌드는 로컬, 결과 파일을 배포). `[[sim:<id>]]`는 시뮬레이션 링크와 `illustrations/a/<id>.svg` 그림으로 바꾼다. `hash-storage`, `hash-collision`은 `hash-table`로 연결.
- 상태(읽음, 헷갈림, 마지막 위치)는 localStorage.
- 배포 폴더 `app/`에 앱 + `sims/` + `illustrations/a/` 사본만 넣는다. `_reference/`(책 원본), `design/`, `docs/`는 넣지 않는다(저작권).
- 시뮬레이션 `sims/_kit/kit.js`의 `qUrl`을 앱 질문 화면 주소로 바꾼다.
- 배포 전 확인: 390/360 넘침, 콘솔 오류, 전체 흐름 Playwright, em dash 0, 원본 문장·예시 값 미포함(grep).
