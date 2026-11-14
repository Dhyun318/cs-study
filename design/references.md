# 홈 화면 레퍼런스 보드

CS 공부 자료 앱 홈 화면용 레퍼런스 18건. 목표 결은 토스 같은 담백한 UI(흰 바탕, 회색 단계, 파랑 한 가지, Pretendard)다.

## 이어 읽기 (3)

홈 최상단에 지금 보던 자리를 한 장으로 보여주는 패턴

### [Apple Books](https://screensdesign.com/apps/apple-books/)
- 출처: 실제 앱 (화면 모음)
- 화면과 패턴: 홈의 Continue reading 카드, 리더 하단 진행 표시(222 / 291쪽), 다 읽은 책을 따로 보여주는 섹션.
- 빌려올 점: 홈 맨 위에 이어 읽기 카드 한 장만 두고, 다 읽은 문항은 아래 섹션으로 분리한다.
- 토스 결: 흑백 위주의 UI에 표지 외 장식이 없다. 결이 가장 가깝다.
- 썸네일: https://media.screensdesign.com/app-previews/22699bf72bed40dabeee9d24d602d0b4.webp

### [Reader App by Mykola G.](https://dribbble.com/Ketdji/collections/6415566-Reader-App)
- 출처: 디자인 갤러리 (Dribbble 컬렉션)
- 화면과 패턴: 흰 배경 홈. 이어 읽기 카드(제목 + 원형 70%)와 장르 알약 칩(Adventure, Sci-Fi, Thriller).
- 빌려올 점: 카드 하나에 위치와 퍼센트만 담는다. 칩은 선택됐을 때만 짙은 채움으로 바꾼다.
- 토스 결: 흰 바탕, 검정 버튼, 큰 모서리로 토스 결에 근접하다. 카드의 노란 틴트는 회색 단계로 바꾼다.
- 썸네일: https://cdn.dribbble.com/userupload/4972639/file/original-94e175c2e83497c875344f0c5c3d6ba3.png?resize=800x600

### [Brilliant](https://screensdesign.com/apps/brilliant-learn-by-doing/)
- 출처: 실제 앱 (화면 모음)
- 화면과 패턴: 홈 상단 이어하기 카드와 Continue 버튼, 그 아래 카테고리 칩.
- 빌려올 점: 화면에서 강조 버튼은 이어 읽기 하나로 제한한다.
- 토스 결: 흰 바탕에 검정 버튼 구조는 맞다. 일러스트와 스트릭 장식은 가져오지 않는다.
- 썸네일: https://media.screensdesign.com/app-previews/93286823e9784ecda41ce6f96fc6763e.webp

## 목차 / 진도 (5)

챕터 > 토픽 > 문항 트리와 챕터별 진도 표시

### [챕터 내비게이션 UX 글 (ScreensDesign)](https://screensdesign.com/articles/mobile-reader-chapter-navigation-ux/)
- 출처: UX 분석 글
- 화면과 패턴: Apple Books의 쪽수 + 강조된 목차 행, Bookey의 Chapter 2 of 5, AlphaNovel의 챕터 진도값 등 10개 앱의 목차 비교.
- 빌려올 점: 현재 위치 행을 강조하고, 진도 수치는 책 전체인지 챕터인지 범위를 적는다.
- 토스 결: 화면이 아니라 원칙 글이다. 토스 결과 무관하게 구조 판단 근거로 쓴다.
- 썸네일: https://media.screensdesign.com/avs-pp-png/13aaa760d6154fb5a281b23b99f73249.png

### [Online Course Mobile App User Interface](https://dribbble.com/shots/15443728-Online-Course-Mobile-App-User-Interface)
- 출처: 디자인 갤러리 (Dribbble 샷)
- 화면과 패턴: My Course 리스트. 강의 행마다 가는 진행바와 % complete 한 줄.
- 빌려올 점: 챕터 행마다 가는 진행바와 완료율 한 줄을 붙인다.
- 토스 결: 구조만 차용한다. 청록색과 그림자 카드는 빼고 회색 트랙 + 파랑 한 가지로 바꾼다.
- 썸네일: https://cdn.dribbble.com/userupload/31295052/file/original-ca118882622515f22554e6b7cfe893f9.png?resize=800x600

### [eLearning App for High School Students UI/UX Design](https://dribbble.com/shots/15509620-eLearning-App-for-High-School-Students-UI-UX-Design)
- 출처: 디자인 갤러리 (Dribbble 샷)
- 화면과 패턴: 책 카드의 37% 진행바, 챕터 묶음별 Quiz 행(Chapter 1-5), 문제 화면의 7 of 12 카운터와 번호 칩 격자.
- 빌려올 점: 토픽 안 40문항을 번호 칩 격자로 점프하게 하고, 상단에 N of M 카운터를 둔다.
- 토스 결: 색과 그림이 과하다. 번호 칩 격자와 카운터 구조만 쓴다.
- 썸네일: https://cdn.dribbble.com/userupload/31427372/file/original-324d51e57fa4d52e042952dd65ab582b.png?resize=800x600

### [토스 TDS ListRow 문서](https://tossmini-docs.toss.im/tds-mobile/components/ListRow/list-row-components/)
- 출처: 토스 공식 문서
- 화면과 패턴: 왼쪽 에셋(Icon, Image, Text), 가운데 Texts 1~3줄, 오른쪽 Badge, 아이콘 버튼, withArrow 화살표.
- 빌려올 점: 챕터 > 토픽 행을 ListRow로 구성한다. 왼쪽 번호, 가운데 2줄 제목, 오른쪽 진도 Badge와 화살표.
- 토스 결: 토스 본체의 목록 문법이다.

### [토스 TDS ProgressBar 문서 (React Native)](https://tossmini-docs.toss.im/tds-react-native/components/progress-bar/)
- 출처: 토스 공식 문서
- 화면과 패턴: size는 light, normal, bold, progress는 0~100, withAnimation으로 애니메이션.
- 빌려올 점: 챕터 진도는 light 두께 한 줄로 표시한다.
- 토스 결: 토스 본체다. 단 React Native 문서라 웹용 TDS와 API가 다를 수 있다.

## 복습 카드 (4)

헷갈린 문항을 다시 꺼내 보는 흐름

### [AnkiMobile 덱 목록](https://docs.ankiweb.net/ankimobile/deck-list)
- 출처: 공식 문서
- 화면과 패턴: 덱마다 숫자 두 개(오늘 복습 초록, 새 카드 파랑). 덱을 탭하면 바로 학습, 왼쪽 스와이프로 관리 메뉴.
- 빌려올 점: 복습 진입 줄에 남은 개수 숫자를 크게 보여주고, 탭하면 바로 복습을 시작한다.
- 토스 결: 숫자 중심 구조가 좋다. 색은 파랑 단일 액센트로 통일한다. 이 링크는 문서 설명이며 실제 화면 캡처가 아니다.
- 썸네일: https://anki.mintlify.site/_mintlify/api/og/v2?division=AnkiMobile+Manual&title=The+Deck+List&theme=2650dd725c5bcd88e4c7344c&signature=9a61a4ea7c913acb6f73d08b6c80a714436591f2d50b44bd282e97d2a06f52b0

### [Anki Mobile Flashcard Interface (컨셉)](https://contra.com/p/M7WsUWsM-anki-app-mobile-flashcard-interface)
- 출처: 디자인 포트폴리오 (Contra)
- 화면과 패턴: 뒤집은 카드 아래에 10 min / 1 day / 8 days 간격 버튼 세 개.
- 빌려올 점: 헷갈림 처리를 버튼 두 개(다시 보기, 알겠음)로 줄이고, 다음에 다시 나오는 시점만 작게 적는다.
- 토스 결: 어두운 컨셉이라 색은 쓰지 않는다. 카드 아래 버튼 배치만 참고한다.
- 썸네일: https://contra.com/api/@internal/open-graph-card/project/WyJQb3J0Zm9saW9Qcm9qZWN0Iiw0NTQzODUyNF0=

### [Quizlet](https://screensdesign.com/apps/quizlet-study-with-flashcards/)
- 출처: 실제 앱 (화면 모음)
- 화면과 패턴: 세트 상세에 학습 모드 목록(Flashcards, Learn, Test, Match), 카드 1 of 34 카운터, 오른쪽 스와이프로 알고 있음 처리.
- 빌려올 점: 복습 카드 상단에 N of M을 두고, 스와이프 대신 하단 고정 버튼으로 처리한다.
- 토스 결: 흰 바탕의 담백한 구성이다. 모드가 여러 개인 점은 우리 범위가 아니라 가져오지 않는다.
- 썸네일: https://media.screensdesign.com/app-previews/a067ffb808b543bfa3aa03a54fd58473.webp

### [말해보카](https://apps.apple.com/kr/app/1460766549)
- 출처: 한국 앱 (App Store 설명문 기준)
- 화면과 패턴: 망각 곡선에 따른 자동 복습, 외우고 싶은 단어를 먼저 공부하는 학습 추가 기능.
- 빌려올 점: 홈에서 오늘 복습 N개 한 줄로 진입시키는 방식과 문구 톤을 참고한다.
- 토스 결: 화면은 직접 확인하지 못했다. 설명문에 적힌 기능만 근거다.

## 태그 / 필터 (3)

별 빈도, 읽음 상태, 주제별로 좁혀 보기

### [Pocket](https://screensdesign.com/apps/pocket-stay-informed/)
- 출처: 실제 앱 (화면 모음)
- 화면과 패턴: 저장 목록 상단 필터 탭 All / Listen / Tagged / Favorites, 태그 선택 바텀시트, 읽기 화면 글꼴 설정.
- 빌려올 점: 별 개수 필터는 상단 탭 또는 칩으로, 태그 편집은 바텀시트로 처리한다.
- 토스 결: 단순한 탭 구조다. 서비스는 종료된 것으로 알고 있으나 이번에 재확인하지 못했고, 화면 기록용으로만 본다.
- 썸네일: https://media.screensdesign.com/app-previews/d6bc53725c27450895c2372fb7475538.webp

### [밀리의서재](https://apps.apple.com/KR/app/id1213788923)
- 출처: 한국 앱 (App Store 업데이트 노트 기준)
- 화면과 패턴: 내 서재에서 상태별 필터, 여러 권의 독서 상태 일괄 변경, 독서 기록 바로가기, 하이라이트 목록 이동.
- 빌려올 점: 안 읽음 / 읽는 중 / 헷갈림 / 완료 상태 필터와 일괄 변경 아이디어를 참고한다.
- 토스 결: 화면은 직접 확인하지 못했다. 노트에 적힌 기능만 근거다.

### [Bookmory](https://screensdesign.com/apps/bookmory-reading-tracker/)
- 출처: 실제 앱 (화면 모음)
- 화면과 패턴: 알약 선택 칩(Page / Percentage), 태그 관리 칩, Status: All 필터 버튼과 정렬 드롭다운, 홈의 현재 진도.
- 빌려올 점: 필터 칩 높이와 간격, Status 버튼 + 정렬 드롭다운 조합을 쓴다.
- 토스 결: 베이지 톤은 쓰지 않는다. 칩 구조만 참고한다.
- 썸네일: https://media.screensdesign.com/app-previews/40da64b77c984fcfad319292ac4ef767.webp

## 타이포 / 전체 톤 (3)

읽기 자료다운 글자와 토스 같은 담백한 화면

### [Reader by Alex Void](https://dribbble.com/pxlhead/collections/7134916-Reader)
- 출처: 디자인 갤러리 (Dribbble 컬렉션)
- 화면과 패턴: 흰 바탕에 Inter 계열 산세리프. 읽기 설정 시트(배경색 칩 3개, 글자 크기 슬라이더), 상세의 3칸 요약(평점, 쪽수, 리뷰)과 태그 칩.
- 빌려올 점: 읽기 설정에 글자 크기 슬라이더를 넣고, 상세 상단에 3칸 요약(문항 수, 별 빈도, 진도)을 둔다.
- 토스 결: 흰 바탕, 회색 단계, 단일 청록 액센트로 토스 결에 가깝다. 이 모음 중 톤이 가장 맞다.
- 썸네일: https://cdn.dribbble.com/userupload/38450139/file/original-5caeb41f7f137521a8ee94ddcbdbc0c8.jpg?resize=800x600

### [토스 프로덕트 산스 제작기 (토스피드)](https://toss.im/tossfeed/article/beginning-of-tps)
- 출처: 토스 공식 글
- 화면과 패턴: 토스가 금융 맥락과 디지털 환경을 고려해 전용 서체를 만든 과정.
- 빌려올 점: 숫자와 한글이 섞인 줄의 가독성을 어떻게 다루는지 참고한다.
- 토스 결: 토스 서체는 비공개라 우리는 Pretendard를 쓴다. 이 글에서 토스가 Pretendard를 쓴다는 근거는 확인하지 못했다.

### [토스 TDS 컴포넌트 개요 (앱인토스 개발자센터)](https://developers-apps-in-toss.toss.im/design/components)
- 출처: 토스 공식 문서
- 화면과 패턴: 핵심 컴포넌트 11종 목록: Badge, Border, BottomCTA, Button, Asset, ListRow, ListHeader, Navigation, Paragraph, Tab, Top.
- 빌려올 점: 홈을 Top + Tab + ListHeader + ListRow + BottomCTA 조합으로 짜면 토스 문법이 된다.
- 토스 결: 토스 본체다. 목록만 있고 설명은 각 링크 안에 있다.
- 썸네일: https://developers-apps-in-toss.toss.im/~gitbook/image?url=https%3A%2F%2Fstatic.toss.im%2Fillusts%2Fog-apps-in-toss.png&width=1200&height=630&sign=3838f56dd16dd1c7b3cdd252799db14a&sv=3

## 확인 메모

- 썸네일은 대부분 원본 사이트의 대표 이미지다. ScreensDesign 썸네일은 앱 소개 이미지이고, 해당 패턴 화면은 링크 안의 화면 목록에서 확인한다.
- Dribbble 샷 2건과 컬렉션 2건, Contra 1건은 썸네일을 직접 열어 확인했다. 같은 검색에서 나온 다른 Dribbble 샷 다수는 내용이 맞지 않아 뺐다(범용 3D 일러스트, 목업 소스 등).
- 확인하지 못한 것: Readwise Reader(홈과 진도 화면 설명 없음), Behance(차단), Mobbin 개별 화면(검색에 안 나옴), 밀리의서재와 말해보카의 실제 화면(앱 설명문만 확인).
