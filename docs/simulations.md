# 시뮬레이션 목록

책(원본 PDF)에 실린 CS 개념 그림마다 하나씩 만든 시뮬레이션 목록이다. 2026-11-14 결정으로 전부 만들었다(31행, `hash-storage`와 `hash-collision`은 `sims/hash-table` 하나로 합침).

- id는 폴더 이름(`sims/<id>/`), 그림 이름(`illustrations/a/<id>.svg`), 본문 표시(`notes/`의 `[[sim:<id>]]`)에 그대로 쓴다.
- 시뮬레이션의 예시 값과 설명은 모두 새로 만든 것이다. 책 그림 분류와 단계 메모(책 예시 값 포함)는 저작권 때문에 공개 레포에 두지 않고 `_reference/simulations-full.md`(git 제외)에 있다.

| id | 과목 | 시뮬레이션 | 연결 질문(⭐) |
|---|---|---|---|
| dynamic-array | 자료구조 | Dynamic Array 크기 늘리기 | Dynamic Array (별 없음) |
| linked-list | 자료구조 | Linked List 노드 끼우기/빼기 | Linked List (별 없음) |
| queue-stack | 자료구조 | Queue와 Stack 넣고 빼기 | Queue (별 없음), Stack (별 없음) |
| bst-search | 자료구조 | BST 키 검색 | ⭐⭐ BST |
| hash-storage | 자료구조 | Hash table 저장: h(k)=k mod 9 | ⭐⭐ Hash table |
| hash-collision | 자료구조 | Hash 충돌과 separate chaining | ⭐⭐⭐⭐ Hash table collision |
| context-switch | 운영체제 | Context switch (PCB 저장/복구) | ⭐⭐⭐⭐ Multi process |
| race-condition | 운영체제 | 동기화 문제 (race condition) | ⭐ Multi process/thread 동기화 |
| mutex | 운영체제 | Mutex lock/unlock | ⭐ Multi process/thread 동기화 |
| semaphore | 운영체제 | Semaphore wait/signal | ⭐ Multi process/thread 동기화 (mutex와 semaphore 비교) |
| deadlock | 운영체제, 데이터베이스 | Deadlock (서로 상대 자원 기다림) | 교착상태 (OS, 별 없음), ⭐ DeadLock (DB) |
| virtual-memory | 운영체제 | 가상 메모리와 page fault | ⭐ 가상 메모리 |
| paging | 운영체제 | Paging 주소 매핑 | paging (별 없음) |
| segmentation | 운영체제 | Segmentation 주소 변환 | segmentation (별 없음) |
| transaction-lock | 데이터베이스 | Transaction 동시 접근과 Lock | ⭐⭐ Transaction |
| index-search | 데이터베이스 | Index 검색 경로 | Index가 왜 필요한가 (별 없음) |
| bplus-tree | 데이터베이스 | B+tree 탐색과 범위 검색 | ⭐ index는 왜 hash table이 아니라 B+tree |
| encapsulation | 네트워크 | 캡슐화와 역캡슐화 | OSI 7계층과 TCP/IP 4계층 (별 없음), ⭐ TCP vs UDP (p111-1) |
| tcp-udp-order | 네트워크 | TCP와 UDP의 패킷 순서 | ⭐ TCP vs UDP |
| tcp-handshake | 네트워크 | TCP 3-way, 4-way handshake | 3-way handshake (별 없음) |
| google-request | 네트워크 | 주소창에 google.com 입력 후 과정 | ⭐⭐ www.google.com을 주소창에 쳤을 때 |
| cookie-session | 네트워크 | 쿠키와 세션 로그인 흐름 | ⭐ 쿠키와 세션, 쿠키와 세션 로그인 (별 없음) |
| heap | 자료구조 | Heap 삽입/삭제와 배열 대응 | ⭐ Queue vs priority queue |
| bst-structure | 자료구조 | BST 만들기, 서브트리, 순회 순서 | ⭐⭐ BST |
| process-memory | 운영체제, 자료구조 | 프로세스 메모리 영역과 thread 공유 | process 간단히 설명 (별 없음), ⭐⭐ Multi thread, ⭐ Array vs Linked list |
| ipc | 운영체제 | Process 간 통신: shared memory와 message passing | ⭐⭐ multi process에서 process 간 데이터 주고받기 |
| db-keys | 데이터베이스 | table 용어와 key 종류 | Primary key (별 없음), Primary key 꼬꼬무(composite key) |
| er-relationship | 데이터베이스 | 1:N, N:M 관계와 PK/FK 연결 | N:M 관계 (별 없음) |
| join-types | 데이터베이스 | inner join과 left join 결과 | left outer join, inner join 차이 (별 없음) |
| tcp-udp-header | 네트워크 | TCP 헤더와 UDP 헤더 비교 | ⭐ TCP vs UDP |
| http-message | 네트워크 | HTTP 요청/응답 메시지와 GET/POST | HTTP가 뭔지 (별 없음), ⭐⭐ GET vs POST |
