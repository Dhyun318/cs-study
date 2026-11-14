# A 스타일 전체 세트 검증 결과

31개 SVG, 합계 122,141 bytes, 최대 6,244 bytes. 모든 SVG는 내장 글꼴 없이 390px 폭이며 30KB 미만이다.

## 파일별 크기

| 파일 | bytes | notes 기준 |
|---|---:|---|
| a/bplus-tree.svg | 3793 | 03-database.md · sim:bplus-tree |
| a/bst-search.svg | 4133 | 01-data-structure.md · sim:bst-search |
| a/bst-structure.svg | 4696 | 01-data-structure.md · sim:bst-structure |
| a/context-switch.svg | 3979 | 02-os.md · sim:context-switch |
| a/cookie-session.svg | 4205 | 04-network.md · sim:cookie-session |
| a/db-keys.svg | 3201 | 03-database.md · sim:db-keys |
| a/deadlock.svg | 3195 | 02-os.md · sim:deadlock |
| a/dynamic-array.svg | 4123 | 01-data-structure.md · sim:dynamic-array |
| a/encapsulation.svg | 4990 | 04-network.md · sim:encapsulation |
| a/er-relationship.svg | 3920 | 03-database.md · sim:er-relationship |
| a/google-request.svg | 4799 | 04-network.md · sim:google-request |
| a/hash-collision.svg | 3527 | 01-data-structure.md · sim:hash-collision |
| a/hash-storage.svg | 4433 | 01-data-structure.md · sim:hash-storage |
| a/heap.svg | 5485 | 01-data-structure.md · sim:heap |
| a/http-message.svg | 3091 | 04-network.md · sim:http-message |
| a/index-search.svg | 3167 | 03-database.md · sim:index-search |
| a/ipc.svg | 3545 | 02-os.md · sim:ipc |
| a/join-types.svg | 4767 | 03-database.md · sim:join-types |
| a/linked-list.svg | 3222 | 01-data-structure.md · sim:linked-list |
| a/mutex.svg | 2825 | 02-os.md · sim:mutex |
| a/paging.svg | 3336 | 02-os.md · sim:paging |
| a/process-memory.svg | 3824 | 02-os.md · sim:process-memory |
| a/queue-stack.svg | 4058 | 01-data-structure.md · sim:queue-stack |
| a/race-condition.svg | 4266 | 02-os.md · sim:race-condition |
| a/segmentation.svg | 2846 | 02-os.md · sim:segmentation |
| a/semaphore.svg | 2970 | 02-os.md · sim:semaphore |
| a/tcp-handshake.svg | 6244 | 04-network.md · sim:tcp-handshake |
| a/tcp-udp-header.svg | 4472 | 04-network.md · sim:tcp-udp-header |
| a/tcp-udp-order.svg | 3473 | 04-network.md · sim:tcp-udp-order |
| a/transaction-lock.svg | 3967 | 03-database.md · sim:transaction-lock |
| a/virtual-memory.svg | 3589 | 02-os.md · sim:virtual-memory |

## 갤러리

- compare.html: 134,969 bytes.
- gallery.png: 1,268,871 bytes, 1600×10151px.
- 자료구조 8개, 운영체제 10개, 데이터베이스 6개, 네트워크 7개.
- 각 과목 안에서 왼쪽에서 오른쪽으로, 행 끝에서 다음 행으로 이어지는 연결선 27개.

## 검증

- docs/simulations.md의 31개 고유 id와 a/의 31개 파일이 일치한다.
- 각 id의 notes 시뮬레이션 마커를 대조했다. 31개 XML 정상, 독립 headless Chrome 렌더링 정상.
- 31개 파일 모두 내장 글꼴, 외부 이미지, 스크립트, em dash 없음.
- 독립 SVG와 공유 Pretendard 갤러리에서 모든 text의 실제 경계가 캔버스 안에 있음.
- 1600px와 390px viewport에서 실제 프레임 390px 폭 유지. 4개 그룹 및 31개 프레임, 인라인 ID 중복 없음.
- 페이지·콘솔 오류 0건. 네 과목 전체 캡처를 육안 검토함.

## 예시와 정지 그림 범위

- 해시: notes의 1032/1039, mod 7, 버킷 3으로 기존 A 파일을 조정했다.
- 배열: 용량 4→8, 힙: [5,12,9,20,15]에 3 추가. BST: 40/20/60/10/30/50/70에서 30 검색.
- 경쟁 상태: likes 10에서 두 증가가 겹쳐 기대 12 대신 11. 세마포어: DB 연결 3개와 네 번째 요청 대기.
- 페이징: page size 1024, 논리 주소 2500 → page 2 / offset 452 → frame 9 → 9668.
- 세그먼트: base 8000, limit 600, (1,200) → 8200, (1,700)은 trap.
- DB: 재고 10→9/8, 이름 이도현, employee의 emp_no/email, order_item 복합키, author/book 및 membership 연결.
- B+ 트리: notes의 age ≥ 30 조건. 트리 값 18/24/30/36/42/51은 규칙을 만족하는 새 예시다.
- 연결 리스트: notes에 구체 값이 없어 A/B 사이 X를 삽입하는 새 예시다.
- 네트워크: notes의 /books?id=7, shop.example.com, sid=A1B2와 user 42를 사용한다. A1B2는 설명용이며 실제 세션 ID 생성 규칙이 아니다.
- TCP 종료는 일반적인 순차 종료이며 FIN/ACK 결합, 동시 종료, 재전송은 생략했다. 헤더 그림은 필드 역할 비교이며 비트 폭에 비례하지 않는다.
- 각 SVG는 개념을 설명하는 정지 단면이다. 삽입·삭제의 모든 중간 상태, 메모리의 모든 주소, 전체 시뮬레이션 조작을 모두 나열하지 않는다.
- 실제 모바일 기기 확인과 배포는 수행하지 않았다. 원본 도서 이미지는 열거나 복제하지 않았다.

## 모바일 가독성 보강 검증

- A 31개 모두 최소 font-size 14px. 기존 14~15px 주요 라벨은 16px, 제목은 기존 크기를 유지했다.
- 16px 이하에서 가는 400/500 굵기를 600으로 올렸다. 값, 문구, 도형 배치와 파일명은 유지했다.
- 31개 XML 유효, 모두 30KB 미만이며 글꼴 데이터는 내장하지 않는다.
- 독립 SVG의 340px 및 390px 표시, 공유 Pretendard 갤러리의 글자 경계 검사 통과.
- 갤러리의 text 간 교차 검사에서 겹침 0건. 브라우저 페이지·콘솔 오류 0건. 과목별 전체 캡처 육안 확인.
- 실행: `python3 illustrations/check-legibility.py --render`. 스크립트가 파일별 최소 font-size를 출력한다.
- gallery.png와 compare.html의 인라인 SVG도 갱신했다. 실제 휴대전화 검증과 배포는 하지 않았다.
