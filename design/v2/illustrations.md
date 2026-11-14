# v2 일러스트 자리 (3회차)

## 0. 3회차 지적 → 반영

| 지적 (리뷰 · 항목) | 반영 |
|---|---|
| 다 읽음 그림이 반쯤 빈 탑으로 보임, 배지가 가려짐, 홈 탑과 모양이 다름, 띠 안에서 좁음 (리드 1·필수4, 시각 1-1·필수1, UX 1·권장5) | 4.1 `hero-done` 을 모든 칸이 파란 2열 탑 + 탑 위 배지로 다시 그림. 다 읽음 그림 띠 높이 160(세로로 긴 탑이 띠 높이의 약 75%) |
| 헷갈림 0개 그림이 데이터베이스 기호와 같은 실루엣 (리드 1·필수4, 시각 1-1·필수2, UX 1·권장6) | 4.3 `ill-empty-conf` 를 쌓인 카드 + 체크로 다시 그림(원통 아님). 프롬프트에 `Not a cylinder` 를 넣음 |
| 불러오지 못함 그림이 내려받기 구름 (리드 1·필수4, 시각 1-1·필수3, UX 1·권장6) | 4.3: 못 불러옴은 온라인이면 `ill-notfound`(문서 + 돋보기). 구름 `ill-offline` 은 오프라인일 때 loadFail 만. 쓰는 곳 열을 고침 |
| 자료구조 장면·기호 무게가 다른 과목의 절반 (시각 1-5·필수5) | 4.1 `hero-ds`, 4.2 `sym-ds` 를 다시 그려 네 과목 무게를 맞춤 |
| PNG 파랑이 토큰보다 어둡고 카드에 그림자가 들어감 (시각 1-5·권장) | 12장에 공통 색·그림자 보정을 함(카드 그림자 제거 포함, 공통 프롬프트 `no shadows` 와 맞춤). 5절 |
| 12장 다시 그리기 (리드 1·필수4) | 코덱스가 PNG 12장 전부를 다시 그림. 파일 이름·크기 그대로라 `ready.js` 와 앱 자리는 그대로 |

## 0-1. 2회차 지적 → 반영 (지난 회차)

| 지적 (리뷰 · 항목) | 반영 |
|---|---|
| 장면 오른쪽 끝 앱 마크(막대 3단)가 로고 도장으로 읽힘 (리드 1-1·3-7, 시각 1-1·3-4) | 장면 프롬프트에서 막대 3단 문장을 지우고 공통 문장에 No logo 를 넣음 |
| 장면 왼쪽 40% 가 빈 면 (시각 1-1·3-4) | 구도 문장: 사물은 가로 가운데 70% 안 |
| 다 읽음 그림이 마지막 과목 장면 (리드 2·3-7, 시각 1-2·3-9, UX 1) | 새 자리 hero-done: 블록이 꽉 찬 탑 |
| 대체 그림 결이 선·면으로 섞임 (시각 1-1·3-6) | 5절 대체 그림 한 벌 규칙 |
| 과목 표지 차이 규칙 없음 (시각 빠진 것) | 4.1 과목마다 주인공 실루엣과 따뜻한 색 자리 고정 |
| PNG 가 아직 없음 (리드 2·3-8, 시각 1-6, UX 1) | 2026-11-14 코덱스가 12장 생성, ready.js 등록, 34장면 이상 다시 찍음 |

## 0-2. 1회차 지적 → 반영 (지난 회차)

| 지적 (리뷰 · 항목) | 반영 |
|---|---|
| 파랑 단색 평면 벡터 = undraw·생성 모델 기본값 결, 홈 전체가 파랑 한 톤 (시각 1-1·1, 리드 1) | 기존 팔레트 안의 따뜻한 색 #FFE0B0(빈출 꼬리표, A안 도식에 이미 있음)을 그림 면적 5% 이하로 허용. 구도·시점·모서리를 고정하는 문장 추가(2절) |
| 과목 그림 한 벌을 168px 히어로와 36px 아이콘에 같이 씀, 사물 2~4개라 작게 줄이면 뭉갬 (시각 3-1) | 두 벌로 나눔: 장면(히어로 띠, 가로 35:12)과 기호(사물 하나, 정사각) |
| 히어로 구도 모순(가운데 그림을 밀기만 함) (시각 3-1) | 장면 그림 프롬프트에 구도를 박음: 사물은 오른쪽 60% 안, 왼쪽 40% 는 바탕만 |
| 가장 흔한 CS 소재(DB 원통, 칩, 노트북·서버, 책과 돋보기) (리드 1) | 기호는 실루엣 구분이 먼저라 원통·칩을 유지하되 결을 고정(정면, 3도형 이하, 모서리 비율). 장면은 사물을 앱의 블록(차곡 막대)과 함께 놓아 이 앱만의 장면으로 |
| 첫 장을 기준 이미지로 나머지를 생성 (시각 3-1) | 3절 생성 순서 |

## 1. 넣는 법과 자리 수

- 파일: `design/v2/illustrations/<id>.png`. 넣은 뒤 `design/v2/illustrations/ready.js` 의 `ILL_READY` 목록에 id 를 더한다. 시안은 목록에 있는 자리만 `<img onerror>` 로 그 그림을 쓰고, 없으면 자리 안 인라인 SVG 대체 그림(00 5.15, 오픽 final 과 같은 방식).
- 자리 12개: 장면 5(과목 4 + 다 읽음) + 기호 4 + 상태 3. 2026-11-14 12장 모두 PNG(ready.js 등록). 3회차에 12장 모두 코덱스가 다시 그렸다(파일 이름·크기 그대로).
- 대상이 아닌 것: UI 아이콘(Tabler), 본문 도식(`illustrations/a/*.svg`, A안 확정), 시뮬레이션 포스터(도식 첫 묶음을 줄여 씀, 04 4절).

## 2. 공통 스타일 프롬프트 (그대로 복사)

```
Flat vector illustration in a calm editorial style. Palette strictly limited to: blue #6194F8, white #FFFFFF, very light blue #EAF1FE, navy #03257B for small details under 10% of the area, and one warm accent #FFE0B0 under 5% of the area. Front view, no perspective, no isometric, no 3D, no shadows, no gradients, no texture, no outlines. Shapes are simple rounded rectangles and circles with corner radius about 18% of each shape's short side. No text, letters, numbers, code symbols, faces, hands or emoji. No logo, no app mark, no signature. Transparent background PNG.
```

자리별 프롬프트 앞에 위 문장을 붙인다. 장면은 `Composition:` 문장을 반드시 함께 넣는다.

## 3. 생성 순서 (결 맞추기)

1. `sym-db` 를 먼저 만든다(가장 단순한 원통). 결이 맞을 때까지 다시 뽑는다.
2. 나머지 기호 3장은 `sym-db.png` 를 기준 이미지로 붙여 같은 선 굵기, 모서리, 색 비율로.
3. 장면 4장은 같은 과목의 기호를 기준 이미지로 붙여 그 사물이 장면의 주인공이 되게.
4. 상태 3장은 `sym-db.png` 를 기준 이미지로.

## 4. 자리 목록

### 4.1 장면 (히어로 그림 띠, 홈 이어 읽기와 첫 실행)

크기: 표시 350 x 120(360 폭에서 320 x 120, 가운데 맞춤이라 양옆 15 씩 잘림. 사물은 가운데 70% 안이라 잘리지 않음), 파일 1050 x 360. 바탕은 투명, 띠 바탕 `--stage` #EAF1FE 위에 놓인다.
공통 구도 문장: `Composition: wide banner 35:12. All objects sit inside the middle 70% of the frame, horizontally centered, vertically centered with about 12% margin top and bottom. No logo or signature mark. Objects rest on an invisible baseline, no floor line.`

| id | 쓰는 곳 | 자리별 프롬프트 | 대체 그림 (시안의 인라인 SVG) |
|---|---|---|---|
| hero-ds | 히어로(자료구조) | Subject: a horizontal row of five rounded square cells, the fourth cell lifted slightly upward and filled with the warm accent; beside it a short chain of three round beads linked by short bars. | 칸 5개(흰 채움 + #6194F8 테두리 2), 넷째 칸 #FFE0B0 로 6px 위, 오른쪽 구슬 3개 사슬(#6194F8), 면만, 가운데 70% |
| hero-os | 히어로(운영체제) | Subject: a square processor chip with short pins on all four sides; two small rounded task cards stacked beside it, the top card with a thin warm accent stripe. | 칩(#6194F8, 안쪽 흰 사각, 핀), 카드 2장(흰, 위 카드에 #FFE0B0 줄), 면만, 가운데 70% |
| hero-db | 히어로(데이터베이스) | Subject: a database cylinder of three stacked rounded discs; a small table card with simple rows leaning against it, one row highlighted with the warm accent. | 원통 3단(#6194F8 옆, 흰 윗면), 표 카드(머리 줄 #6194F8, 한 줄 #FFE0B0), 면만, 가운데 70% |
| hero-net | 히어로(네트워크) | Subject: two rounded boxes, a small client box and a taller server box, joined by a gentle curved line; one small envelope shape with the warm accent sits on the line. | 상자 2개(#6194F8, #03257B 띠), 곡선 #6194F8 2px, 봉투 #FFE0B0, 면만, 가운데 70% |
| hero-done | 히어로(40문항 다 읽음, 띠 높이 160) | Subject: a completed tower of flat rounded blocks stacked neatly in two columns, every block filled blue, with one small round badge holding a check mark on top in the warm accent. | 데이터대로 과목 탑 4개가 꽉 참(블록 46 x 6, 사이 2, 헷갈림은 #F04452 1.5 테두리) |

- 3회차 다시 그림: `hero-done` 은 모든 칸이 파란 2열 탑 + 탑 위 배지(흰 줄 없음)다. 세로로 긴 탑이라 다 읽음 띠만 높이 160 이고 탑이 띠 높이의 약 75% 를 채운다(01 5절). `hero-ds` 는 다른 장면과 무게가 맞게 다시 그렸다.
- 과목 표지 차이(고정): 자료구조는 가로 칸 줄(따뜻한 색은 넷째 칸), 운영체제는 정사각 칩(따뜻한 색은 카드 줄), 데이터베이스는 세로 원통(따뜻한 색은 표 한 줄), 네트워크는 두 상자와 곡선(따뜻한 색은 봉투). 띠 바탕은 모두 --stage.

### 4.2 기호 (작은 판: 홈 탑 32, 목차·시뮬레이션 목록 장 머리 48, 포스터 대체 48)

크기: 정사각, 파일 384 x 384. 바탕 투명(흰 바탕과 `--stage` 바탕 둘 다 위에 놓임).
공통 구도 문장: `Composition: square 1:1, one single object filling about 70% of the frame, centered, readable as a silhouette at 32 pixels.`

| id | 자리별 프롬프트 | 대체 그림 |
|---|---|---|
| sym-ds | Subject: a row of three rounded square cells, the middle cell filled blue and lifted slightly. | 칸 3개(#6194F8 둘, 가운데 #03257B 4px 위) |
| sym-os | Subject: a square processor chip with three short pins on each side. | 둥근 사각 칩 #6194F8, 안쪽 흰 사각, 핀 |
| sym-db | Subject: a database cylinder of three stacked rounded discs. | 원통 #6194F8 + 흰 칸 선 + 윗면 #03257B |
| sym-net | Subject: a globe made of a circle with one horizontal and two curved vertical lines. | 원 #6194F8 + 흰 경선·위선 |

- 3회차 다시 그림: `sym-ds` 를 다른 기호와 무게가 맞게 다시 그렸다.
- 32px 에서 네 실루엣이 서로 달라야 한다: 가로 줄, 사각, 세로 원통, 원. #FFE0B0 는 기호에 쓰지 않는다(작은 크기에서 얼룩으로 보임).

### 4.3 상태 (빈 상태, 오류)

크기: 160 x 120, 파일 480 x 360, 바탕 투명(흰 바탕 위).
공통 구도 문장: `Composition: 4:3, objects centered with about 15% margin.`

| id | 쓰는 곳 | 자리별 프롬프트 | 대체 그림 |
|---|---|---|---|
| ill-empty-conf | 목차 헷갈림만 0개(confEmpty, confCleared) | Subject: a neat stack of flat rounded cards, all aligned, with a small round badge holding a check mark above. Not a cylinder, no ellipse tops. | 막대 4단(#6194F8, 맨 위 #03257B), 위 원 배지(#FFE0B0) + 체크 #03257B |
| ill-notfound | 없는 질문·시뮬레이션 주소, 온라인일 때 본문을 못 불러옴(loadFail, qFail) | Subject: a flat rounded document sheet with a few simple lines and a round magnifying glass over it. | 펼친 책(#EAF1FE 면, #6194F8 책등) + 위 #6194F8 판 안 흰 칸 |
| ill-offline | 오프라인일 때 본문을 못 불러옴(loadFail 만) | Subject: a small rounded cloud with a short downward arrow, next to a stack of three flat rounded bars. | 구름 #6194F8 + 흰 아래 화살표 + 옆 #EAF1FE 문서 |

- 구름 `ill-offline` 은 구름 + 아래 화살표라 내려받기 아이콘으로 읽힌다. 그래서 오프라인일 때 loadFail 한 곳에만 쓴다. 나머지 못 불러옴(온라인 loadFail, qFail)은 `ill-notfound`(06 3.2).

## 5. 쓰는 규칙

- 같은 과목은 어느 화면에서나 같은 장면·기호를 쓴다(크기만 다름).
- 대체 SVG 는 같은 viewBox(장면 0 0 350 120, 기호 0 0 48 48, 상태 0 0 160 120)로 그려 PNG 로 바뀌어도 자리가 흔들리지 않는다.
- #FFE0B0 는 장면과 상태에만, 그림 하나에 한 곳.
- 그림은 움직이지 않는다(00 9.2-4).
- 3회차 보정: 12장 모두에 공통 색·그림자 보정을 했다(카드 그림자 제거 포함). 파일 이름과 크기는 그대로.
- 대체 그림 한 벌: 면만 쓴다(테두리 선 없음). 선이 필요한 곳(흰 칸 선, 곡선, 체크)은 2px 하나. 색은 #6194F8 주색, #03257B 작은 부분, 흰색·#EAF1FE 밝은 면, #FFE0B0 한 곳. PNG 와 같은 결이라 파일이 빠져도 한 벌로 보인다.
