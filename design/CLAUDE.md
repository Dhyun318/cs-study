# design/ 시안 규칙

## 무엇을 디자인하나
- 기능과 화면은 `../docs/features.md`를 기준으로 한다. 화면 목록(홈, 목차, 질문 상세, 시뮬레이션, 복습)과 1차/나중 구분을 따른다. 1차 기능만 화면에 넣고, 나중 기능은 넣지 않는다.
- 느낌: 공부 자료(교재, 정리노트, 리더). 면접 연습 느낌은 빼고, ⭐는 기출 빈도 표시로만 쓴다.
- 내용은 `../notes/`(우리 말로 새로 쓴 해설)와 `../illustrations/a/`(새 일러스트)를 쓴다. `../_reference/content/`(책 원문)와 책 그림은 쓰지 않는다(저작권, 루트 CLAUDE.md). 진도 같은 사용자 수치만 예시 값으로 둔다.

## 스타일 (사용자 취향, 확정)
- 색과 글꼴: 사용자의 오픽 앱(`~/2useclaude/프로젝트/Opic practice/src/index.css`, 읽기 전용) 토큰. 흰 바탕, 회색 단계, 파랑 #6194F8 / 글자 파랑 #0E5CF4, 남색 버튼 #03257B, Pretendard. 이 토큰을 그대로 옮긴 옛 시안이 `../_reference/design-old/j/landing.html`.
- 라이트 테마만. 노랑·주황 글자를 흰 바탕에 쓰지 않는다(대비 부족). 별은 주황 바탕 꼬리표 + 진한 글자.
- 레퍼런스: `references.html` / `references.md`. 추천 5개(Reader App, Reader by Alex Void, 토스 TDS ListRow, Apple Books, AnkiMobile)를 우선 참고한다.

## 만드는 방식
- 시안 하나 = 폴더 하나(`design/<글자>/landing.html` + `landing.png` + `landing-full.png`). 다른 시안 폴더는 건드리지 않는다.
- 390px 모바일 폭. 한 파일 안에 CSS 포함.
- 완료 전 `~/.claude/rules/ui-check.md` 체크리스트(design-taste-frontend 14장)를 돌리고, em dash 0개를 확인한다.
- 옛 시안 A~P와 비교 화면(index.html, colors.html)은 책 문장이 들어 있어 `../_reference/design-old/`로 옮겼다(git 제외). 지금 기준 시안은 `p-flow/` 하나.

## 지금까지 결정
- 1차 시안 A~J: 면접 느낌이라 탈락. 색은 오픽 색으로 정함.
- 2차 시안 K(교재 목차), L(정리노트), M(읽기+복습): 공부 자료 방향.
- 3차 시안 N(리더 앱형), O(토스 목록형): 추천 레퍼런스 기반. O를 바탕으로 N의 이어 읽기 카드를 합치기로 함 → P.
- 시뮬레이션은 책 그림 전부를 만든다(`../docs/simulations.md`, 2026-11-14). 홈에는 일부만 보이고 전체 보기로 연결. 공부 알림은 뺐으므로 홈에 알림 입구를 두지 않는다.
- 2026-11-14 최종 선택: **P**(O 바탕 + N 이어 읽기 카드). 이후 모든 화면은 P 스타일을 따른다. 화면 흐름 프로토타입은 `p-flow/`.
- 2026-11-14 디자인 결과물 형식: 오픽 앱의 `~/2useclaude/프로젝트/Opic practice/spike/design/final/index.html`과 같은 형식으로 만든다. 제목 + 결정 메모 목록, 흐름 묶음별 썸네일 줄(화살표로 연결, 줄 바꿈), 썸네일을 누르면 왼쪽 큰 폰이 그 화면으로 이동. 결과물은 `p-flow/index.html`.
- 2026-11-14 일러스트는 A안(정돈된 도식) 채택. 피그마식 별도 캔버스(flow.html)는 버리고 오픽 형식 하나로 감. 폰만 보기는 `p-flow/index.html?only=1`.
