# REA 레퍼런스 분석 (Brilliant, Toss, Duolingo, Linear)

결론: 네 사이트에서 숫자로 가져올 것은 (1) 눌림 3종(4px 립 이동, scale .97, 팝 오버슈트), (2) 등장 모션의 곡선과 시간(expo-out 계열 400~1000ms), (3) 한글 제목 자간 -0.02em과 행간 단계, (4) 카드 테두리 2px + 아래 4px 립, (5) 회색 불투명도 토큰 기반 그림자다. 룩, 에셋, 문구는 가져오지 않는다. 측정 2026-11-14, 공개 페이지만, 로그인 없음.

## 0. 측정 방법과 Evidence ID

| 구분 | 방법 | 비고 |
|---|---|---|
| REA | `capture-web-screenshot` (데스크톱 1440), `analyze-web-bundle` (정적 번들), `list-browser-targets` | CDP 엔드포인트가 필요해서 크롬을 별도 포트로 띄워 연결 |
| Playwright (REA로 불가한 부분) | 390x844 모바일 스크린샷, 스크롤 시나리오, CSS/JS 응답 본문 정규식, computed style, `getAnimations()`, `Element.animate` 후킹 | 이유는 6장 |

| ID | 내용 | 위치 (scratchpad/rea/) |
|---|---|---|
| R-BR-shot / R-BR-bundle | Brilliant REA 스크린샷 ev_a11a07829ed1, 번들 ev_9a08dee6eb86 | brilliant/desktop_home_rea.png, bundle_evidence.json |
| R-TO-shot / R-TO-bundle | Toss ev_650f72ca1745, 번들 ev_ac56521aabb4 | toss/ |
| R-DU-shot / R-DU-bundle | Duolingo ev_9872d7a1f901, 번들 ev_c2f6fb055af6 (관측 스크립트 6개뿐) | duolingo/ |
| R-LI-shot / R-LI-bundle | Linear ev_9526a96c857c, 번들 ev_9bea099463cc | linear/ |
| P-xx-css | 사이트별 CSS/JS 정규식 집계 (xx = BR, TO, DU, LI) | 사이트폴더/analysis.json |
| P-xx-motion | 스크롤 시나리오, WAAPI 후킹, 데스크톱 호버 탐침 | 사이트폴더/collect.json |
| P-press | 버튼 눌림 실측 (base, hover, active) | press.json |
| P-card | 카드 기하 실측 | card.json |

스크린샷 16장: `design/references-rea/` (모바일 390 폭 3장 + 데스크톱 960 폭 1장, 사이트별).

## 1. 사이트별 핵심 3가지

### Brilliant (따뜻한 오프화이트 + 두툼한 립 + 느리고 긴 등장)
| # | 발견 | 숫자 | Evidence |
|---|---|---|---|
| 1 | 버튼과 카드가 아래 립으로 눌림. 카드: 테두리 2px #E5E5E5 + `0 4px 0 #E5E5E5`, 반경 16, 패딩 14/18, 높이 104. 눌리면 translateY(4px) + 그림자 none | transition transform,box-shadow .1s ease-out (카드), .2s ease (버튼) | P-card, P-BR-motion |
| 2 | 섹션 등장: opacity 0→1 700ms ease-out, translateY 24px→0 1000ms. 곡선 cubic-bezier(.22,1,.36,1) | CSS 곡선 빈도 1위가 (.22,1,.36,1) 18회, 이어서 (.4,0,.2,1) 9회, (.16,1,.3,1) 8회 | P-BR-css |
| 3 | 배경이 순백이 아님. 면적 비율 #F5F3F1 60.8%, 흰색 29.4%, #FAF9F8 6.8%. 글자는 검정 알파 .6이 55%, 검정 18.6% | 반경 토큰 2/4/6/8/12/16/20/32/full, 간격 4px 단위 | P-BR-css (m_bg_ratio, m_fg_ratio) |

### Toss (여백, 꽉 조인 한글 제목, 불투명도 회색 토큰)
| # | 발견 | 숫자 | Evidence |
|---|---|---|---|
| 1 | 모바일 제목 36/46(1.28), 28/39(1.4), 본문 16/25.6와 14/22.4(1.6). 자간 -0.02em 일관 (36px는 -0.72px, 14px는 -0.28px). 폰트 Toss Product Sans | 폰트 토큰 56/48/36/32/24/20/17/15/13/11, 행간 base 1.6 | P-TO-css |
| 2 | 색을 알파 회색으로 만든다. greyOpacity 100~900 (rgba(0,27,55,.1) 등). 그림자 s `0 0 4px op100, 0 4px 16px op100`, m `0 8px 16px op200, 0 4px 8px op100`. 반경 4/8/16/20/24, 목업 카드는 32 | 면적 비율 흰색 87.9%, 포인트 #3182F6 | P-TO-css |
| 3 | 모션: 히어로 translateY 40→0 800ms (.16,1,.3,1), blur 16→0 + translateY 24→0 1000ms (.37,.31,0,1), clip-path 확장 800ms (.33,1,.68,1), 모바일 translateY 80→0 700ms 스프링(linear() 곡선). 팝오버 opacity + translateY(-8px) + scale(.96) 250ms (.4,0,.2,1). 체크 팝 scale .5→1 200ms (.34,1.56,.64,1) | CSS 시간 빈도 .2s 252회, .1s 151회, .15s 46회 | P-TO-motion, P-TO-css |

### Duolingo (립 버튼, 색 면 전환, 짧고 비대칭인 UI 모션)
| # | 발견 | 숫자 | Evidence |
|---|---|---|---|
| 1 | 버튼 높이 50, 반경 12, 15px/700, 대문자 자간 .8px. 립 4px(`--web-ui_button-lip-width`, 컴팩트 2px). 누르면 translateY(4px) + 그림자 none | 실측 active matrix(1,0,0,1,0,4) | P-press, P-DU-css |
| 2 | 카드(코스 그리드 2열): 테두리 2px #E5E5E5, 아래 4px, 반경 16, 패딩 12/12/24, 열 간격 12 | 카드 159x217 | P-card |
| 3 | UI 모션은 짧고 3곡선만 거의 씀. 시간 .1s 312회, .2s 263회, .25s 196회. 곡선 (0,0,.2,1) 307회(들어옴), (.4,0,1,1) 290회(나감), (.05,0,0,1) 177회(눌림 .1s). 면적 비율은 연하늘 #DDF4FF 52% / 남색 #100F3E 48% 전면 색 면 교차 | 키프레임 140개, Lottie 마커 177, Rive 마커 28, .json 자산 37 | P-DU-css |

### Linear (가변 굵기, 자간 단계, 1px 테두리, 눌림 .97)
| # | 발견 | 숫자 | Evidence |
|---|---|---|---|
| 1 | 굵기가 400/510/590/680 (가변 폰트 Inter Variable). 자간이 크기별 단계: text-tiny -.015em, small -.013em, regular -.011em, mini -.01em. 본문 15/24, 제목 24/31.9, 38px는 -.022em | 토큰 `--font-weight-medium:510`, `--text-regular-size:.9375rem` | P-LI-css |
| 2 | 눌림: scale(.97) + brightness(98%), 160ms cubic-bezier(.25,.46,.45,.94). 시트/드로어 곡선 (.32,.72,0,1) | 실측 active matrix(.97) | P-press, P-LI-css |
| 3 | 깊이는 그림자 대신 1px 테두리. `0 0 0 1px #0003`, `inset 0 0 0 1px`, 다층 그림자 5겹. 히어로 줄 등장: delay 400ms, 1000ms, (.25,.1,.25,1), opacity + blur 10→0 + translateY 20%→0 | 면적 비율 #08090A 97.4%, 포인트 색 1.5% | P-LI-css, P-LI-motion |

## 2. 공통 수치 (4개 사이트 CSS 빈도와 실측)

| 항목 | Brilliant | Toss | Duolingo | Linear |
|---|---|---|---|---|
| 자주 쓰는 시간 | .2s .15s .1s | .2s .1s .15s | .1s .2s .25s | .16s .2s .12s |
| 대표 곡선 | (.22,1,.36,1) | (.4,0,.2,1) | (0,0,.2,1) / (.4,0,1,1) | (.32,.72,0,1) / (.25,.46,.45,.94) |
| 눌림 | translateY 4px, 그림자 제거 | 마케팅 페이지에는 없음 (미관측) | translateY 4px | scale .97 |
| 스크롤 연동 CSS (animation-timeline) | 1건 | 0 | 0 | 0 |
| IntersectionObserver 사용 수 | 8 | 44 | 18 | 10 |
| prefers-reduced-motion 규칙 | 3 | 60 | 12 | 53 |
| 주요 반경 | 16 카드, full 버튼 | 8, 16, 24, 32 | 12 버튼, 16 카드 | 8, 12, full |
| 간격 상위 (px) | 10 5 20 15 16 | 8 4 24 16 12 | 16 8 12 24 10 | 8 12 4 16 6 24 |
| 모바일 좌우 여백 | 약 18 | 20 | 30 | 24 |
| 일러스트 | 플랫 벡터, 파랑 3~4단계 + 노랑 1, 외곽선 없음, Rive 마스코트 | 사진 + 실제 같은 UI 목업, 3D 없음 | 플랫 벡터 캐릭터, 외곽선 없음, 팔레트 일정, Lottie/Rive | 선 와이어프레임 + UI 목업, 일러스트 없음 |

공통점: 시간은 3~4단계(100, 160~200, 250~300, 700~1000)만 쓰고, 곡선도 이름 붙은 2~3개만 반복한다. 들어올 때는 느리고(expo-out) 나갈 때는 빠르다. 면적의 약 90%가 무채색이고 포인트 색은 5% 이하다. 네 사이트 모두 reduced-motion 규칙이 있다.

## 3. 사이트가 만든 것 같지 않게 느껴지는 이유 (AI 티가 안 나는 이유)

| 사이트 | 손으로 다듬은 흔적 |
|---|---|
| Brilliant | 순백 대신 #F5F3F1, 립 달린 버튼과 카드가 같은 4px 규칙, 헤드라인 안에 세리프 이탤릭 한 단어, 일러스트가 한 팔레트 |
| Toss | 제목 자간을 -2%로 고정, 알파 회색 토큰, 큰 여백, 실제 같은 숫자가 든 목업 카드, 스프링과 블러를 섞은 등장 |
| Duolingo | 전용 폰트(feather, duolingo-sans), 눌림이 4px로 물리적, 전면 색 면 전환, 일러스트 팔레트 통일 |
| Linear | 510/590 같은 중간 굵기, 크기별 자간, 그림자 대신 1px 테두리, 눌림 .97 하나로 통일 |

AI 시안이 흔히 하는 것(모든 곳 0.3s ease, 똑같은 8px 그림자, 이모지 아이콘, 카드 3개 균등 나열, 임의 그라데이션)을 이 네 곳은 거의 쓰지 않는다. 쓰는 것은 이름 있는 곡선, 3~4단계 시간, 헤어라인 테두리, 조정된 자간이다.

## 4. 우리 앱에 적용할 토큰 (관측값 근거, 우리 값은 제안)

### 모션
| 토큰 | 값 | 근거 |
|---|---|---|
| dur-press | 100ms | Duolingo .1s 312회, Brilliant 카드 .1s |
| dur-fast | 160ms | Linear .16s 49회 |
| dur-base | 240ms | Toss .2s/.25s, Duolingo .25s |
| dur-enter | 420ms (관측 700~1000ms는 마케팅용이라 앱은 줄임) | Brilliant, Toss |
| dur-hero | 800ms (스플래시 한 번만) | Toss 800ms |
| ease-out | cubic-bezier(.22,1,.36,1) | Brilliant 18회, Toss JS |
| ease-std | cubic-bezier(.4,0,.2,1) | Toss 48회, Duolingo 82회 |
| ease-exit | cubic-bezier(.4,0,1,1) | Duolingo 290회 |
| ease-sheet | cubic-bezier(.32,.72,0,1) | Linear 드로어 |
| ease-pop | cubic-bezier(.34,1.56,.64,1) | Toss 체크 팝 |
| 눌림 (행, 타일) | scale(.97), 160ms (.25,.46,.45,.94) | Linear 실측 |
| 눌림 (주 CTA) | translateY(4px) + 립 그림자 제거, 100ms | Duolingo, Brilliant 실측 |
| reduced-motion | 이동과 블러 제거, opacity만 120ms | 4개 사이트 공통 |

### 글자 (Pretendard, 모바일)
| 역할 | 크기/행간 | 굵기 | 자간 | 근거 |
|---|---|---|---|---|
| 큰 제목 (스플래시, 온보딩) | 28/39 | 700 | -0.02em | Toss 28/39.2 |
| 화면 제목 | 22/30 | 700 | -0.02em | Linear 24/31.9 비율 |
| 소제목, 목록 제목 | 17/25 | 600 | -0.01em | Toss 17/25.16 |
| 읽기 본문 (질문 상세) | 16/26 | 400 | -0.01em | Toss 16/25.6 |
| 보조 본문 | 14/22 | 400 | -0.02em | Toss 14/22.4 |
| 캡션, 꼬리표 | 12/19 | 500 | 0 | Toss 12/19.2, Brilliant 12/18 |

### 간격, 반경, 그림자
| 항목 | 값 | 근거 |
|---|---|---|
| 간격 | 4 8 12 16 24 32 48 (4 단위) | Toss, Linear 상위 값 |
| 좌우 여백 | 20 | Toss |
| 반경 | 8 칩, 12 버튼과 입력, 16 카드와 타일, 24 히어로 카드와 시트, full 꼬리표 | Toss 토큰 4/8/16/20/24, Duolingo 12/16 |
| 테두리 | 2px #E5E8EB (TDS grey200, Toss와 동일 값) + 아래 4px | Duolingo, Brilliant 카드 |
| 헤어라인 | inset 0 0 0 1px rgba(0,27,55,.1) | Toss greyOpacity200 |
| 그림자 s | 0 0 4px rgba(2,32,71,.05), 0 4px 16px rgba(2,32,71,.05) | Toss --shadow-s |
| 그림자 m | 0 8px 16px rgba(0,27,55,.1), 0 4px 8px rgba(2,32,71,.05) | Toss --shadow-m |
| 색 비율 | 흰색/회색 약 90%, 파랑 5% 이하, 남색은 주 CTA만 | 네 사이트 면적 비율 |

Toss 회색 토큰은 우리가 쓰는 TDS 회색과 같다: 50 #F9FAFB, 100 #F2F4F6, 200 #E5E8EB, 300 #D1D6DB, 400 #B0B8C1, 500 #8B95A1, 600 #6B7684, 700 #4E5968, 800 #333D4B, 900 #191F28 (P-TO-css).

## 5. 도입 아이디어 10개 (이 앱의 이 부분을 보고, 우리는 이렇게, 어느 화면)

| # | 사이트와 부분 | 우리는 이렇게 도입 | 화면 | Evidence |
|---|---|---|---|---|
| 1 | Duolingo 주 버튼의 4px 립 | 남색 #03257B 버튼 아래에 4px 더 진한 남색 립. 눌리면 translateY(4px), 그림자 제거, 100ms. 높이 50, 반경 12. 주 CTA에만 쓰고 나머지는 평평하게 둔다 | 온보딩 3장 다음 버튼, 시뮬레이션 다음/제출 | P-press, P-DU-css |
| 2 | Duolingo 코스 카드와 Brilliant 코스 목록 카드의 테두리 + 립 | 과목 타일을 테두리 2px #E5E8EB + 아래 4px, 반경 16, 패딩 12/12/24로. 2열 간격 12. 선택 중인 과목만 테두리를 #6194F8로 | 홈 과목 타일, 목차 챕터 행 | P-card |
| 3 | Linear 버튼의 scale .97 눌림 | 목록 행, 랜덤 질문 카드, 시뮬레이션 카드를 눌렀을 때 scale(.97) + 160ms. 서로 다른 눌림을 섞지 않고 행/타일은 이것 하나로 통일 | 홈, 목차, 시뮬레이션 목록 | P-press, P-LI-css |
| 4 | Brilliant 섹션 등장 (opacity + 24px 상승, expo-out) | 홈 처음 진입 때만 이어 읽기 hero부터 위에서 아래로 opacity 0→1 + translateY 16→0, 420ms, (.22,1,.36,1), 50ms 간격(간격은 제안값). 스크롤 때마다 다시 나오게 하지 않는다 | 홈 | P-BR-motion |
| 5 | Toss 제목 자간 -0.02em과 행간 1.28~1.6 | 4장의 글자 표 그대로. 특히 질문 상세 읽기 본문 16/26, 보조 14/22 | 질문 상세, 온보딩, 목차 | P-TO-css |
| 6 | Toss 알파 회색 그림자 토큰 | 이어 읽기 hero와 시뮬레이션 카드에 shadow-s, 올라온 시트에 shadow-m. 테두리는 회색 hex 대신 rgba(0,27,55,.1) 헤어라인 | 홈 이어 읽기, 시뮬레이션 | P-TO-css |
| 7 | Linear 시트 곡선 (.32,.72,0,1) | 아래에서 올라오는 시트(랜덤 질문 결과, 시뮬레이션 해설)를 이 곡선 + 360ms로. 닫을 때는 (.4,0,1,1) 200ms | 홈 랜덤 질문, 시뮬레이션 | P-LI-css |
| 8 | Toss 체크 팝 (scale .5→1, 200ms, 오버슈트 곡선) | ⭐ 빈출 꼬리표 토글과 읽음 체크에만 0.5→1 팝. 다른 곳에 오버슈트는 쓰지 않는다 | 질문 상세, 목차 | P-TO-css (cj5pkvi 규칙) |
| 9 | Linear 가변 굵기 400/510/590 | Pretendard Variable로 500과 700 사이를 쓴다. 본문 400, 레이블 510, 제목 590. 굵기 점프가 줄어들어 덜 둔탁하다 | 전체 | P-LI-css |
| 10 | Brilliant 일러스트 팔레트 규율 (파랑 3~4단계 + 포인트 1색, 외곽선 없음) | 과목 아이콘과 일러스트를 #6194F8, #0E5CF4, #03257B, 연파랑 + 포인트 1색으로 제한. 외곽선 없이 플랫. 기존 A안(정돈된 도식)과 같은 방향이라 규율만 추가 | 홈 과목 타일, 목차 | R-BR-shot, brilliant-m-page2.png |
| 11 | Brilliant 과목 탭 (아이콘 칩 + 밑줄, 선택 칩 테두리 파랑) | 목차 상단에 과목 칩 가로 스크롤. 선택 칩은 테두리 #6194F8 + 아래 2px 밑줄 | 목차 | brilliant-m-page2.png |
| 12 | Toss 채용 목록 (카드 없이 17/25 제목 + 13~14px 회색 부제, 여백으로만 구분) | 목차의 질문 목록을 카드 대신 이 구조로. 이미 P(토스 목록형)와 같은 방향이라 확정 근거로만 사용 | 목차 | toss-m-page2.png |

넣지 않은 것: 스플래시와 온보딩의 CS 개념 모션(시뮬레이션과 겹쳐 식상함, 지시), Lottie/Rive 마스코트(자산 규모 큼), 다크 테마(Linear), 사진 히어로(Toss), 전면 색 면 교차(Duolingo, 우리는 흰 바탕 확정), 블러 등장(Toss, Linear: 반복 노출 UI에는 과함. 스플래시 한 번 정도는 가능하나 필요가 분명하지 않아 보류).

## 6. REA 명령 결과

| 명령 | 결과 |
|---|---|
| `--help`, `<command> --help`, `--schema`, `guidance` | 성공. capture-browser-scenario 입력은 `--help`에 없고 빈 입력 검증 오류와 guidance 읽기로 알아냄 |
| `list-browser-targets` | 성공 |
| `capture-web-screenshot` | 성공(데스크톱). 단 REA 연결에는 내 에뮬레이션이 적용되지 않고 헤드리스 최소 창 폭 500 때문에 390 모바일은 못 찍음. 1440 창에서 데스크톱만 사용 |
| `analyze-web-bundle` | `--detail summary --evidence_output --view '{"kind":"web-bundle","collection":"summary"}'` 필수(없으면 invalid_input), view에 limit/offset 넣으면 오류. Brilliant 38초, 스크립트 73개 분석, 1개는 힙 1GiB 초과로 unknown. 결과는 벤더 지문(Next.js)과 엔드포인트 후보 위주라 CSS, 모션 정보는 없음. Duolingo는 3초 관측에 스크립트 6개만 잡힘. evidence_output은 덮어쓰지 않아서 재실행 시 파일 삭제 필요 |
| `capture-browser-scenario` | 사용 불가. viewport 옵션 없음(unknown_argument), 액션이 goto/click/fill/press/select_option/check/uncheck/wait_for/request/wait_for_timeout뿐이라 스크롤 불가. 실행은 하지 않고 입력 검증만 시도 |
| `inspect-analysis-view`, `export-web-scripts` | 필요 없어서 쓰지 않음 |

Playwright 대체 범위: 390x844 모바일(DPR 2) 스크린샷과 스크롤 5지점(early/1초 후), CSS/JS 응답 본문 정규식 집계, computed style 표본, `document.getAnimations()`, `Element.prototype.animate` 후킹(WAAPI 시간과 곡선 포착), 눌림/호버 탐침.

## 7. 한계

- 마케팅 사이트 측정이라 앱 안 화면(Duolingo 레슨, Toss 앱)의 모션은 직접 본 것이 아니다. Toss 눌림은 관측하지 못했고(미관측), 위 눌림 값은 Duolingo, Brilliant, Linear 실측이다.
- Brilliant 쿠키 배너는 누르지 않아 스크린샷 하단에 보인다. Brilliant 3번째 페이지(CS 기초 코스)는 /courses/로 리다이렉트되어 2페이지만 확보했다.
- JS 마커 개수(lottie, rive, gsap, three 등)는 번들 문자열 정규식 매치 수라 거짓 양성이 있다(Toss three 620은 신뢰하지 않음). 자산 확장자 개수(.riv 2, .json 42 등)는 네트워크 응답 기준.
- Linear 시트 곡선 (.32,.72,0,1)과 700ms 전환은 같은 요소에 묶여 있다고 확인하지 못했다. 곡선은 CSS 키프레임, 토큰 근거이고 시간은 우리 제안값이다.
- 우리 적용값(dur-enter 420ms, 50ms 간격, 글자 표)은 관측값에서 앱용으로 줄이거나 반올림한 제안이다.
