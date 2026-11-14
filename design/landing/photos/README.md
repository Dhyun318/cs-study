# CS 차곡 랜딩 온보딩 사진

네 장 모두 내장 image_gen으로 생성한 AI 사진이다. 실제 인물이나 촬영 사진이 아니며 특정 실존 인물을 참고하지 않았다. 오픽 앱의 photo-onboarding-1~4.png와 ob1-strip.png를 직접 열어 밝은 자연광, 흰색·연한 하늘색·베이지, 깔끔한 한국 일상 공간의 분위기를 참고했다.

| 파일 | 장면과 선택 이유 | 크기 | 용량 |
| --- | --- | --- | --- |
| photo-1.webp | 답 가리고 떠올리기. 창가 책상에서 휴대폰을 보며 잠시 생각하는 여성의 뒷모습과 노트·펜이 함께 보여 회상 학습에 어울린다. | 1170×1500 | 171390 bytes |
| photo-2.webp | 시뮬레이션으로 이해. 노트북의 흐릿한 연결 도식과 노트의 손그림 트리가 CS 개념 학습을 드러내며, 사람 없는 장면으로 사진 묶음에 변화를 준다. | 1170×1500 | 102628 bytes |
| photo-3.webp | 매일 조금씩 쌓기. 아침 햇살이 들어오는 버스 창가에서 휴대폰을 보는 여성의 뒷모습이 이동 중 짧은 공부를 자연스럽게 보여준다. | 1170×1500 | 197482 bytes |
| photo-4.webp | 헷갈린 것만 다시. 카페 테이블의 휴대폰·빈 포스트잇·손을 가까이 담아 골라서 다시 살펴보는 분위기에 어울린다. | 1170×1500 | 204494 bytes |

## 생성 프롬프트 요약

공통: photorealistic-natural, portrait 1170:1500, bright Korean everyday study space, natural morning light, white/pale blue/beige, believable photographic texture, no readable writing or logos or brands, no frontal face, no purple/neon, no beauty filter, no UI overlay.

1. Korean woman in her twenties with long dark hair and pale blue cardigan, strictly rear view at a white window desk, looking thoughtfully at an unbranded phone, open blank notebook and pen beside her.
2. No person, unbranded silver laptop at a white window desk, softly blurred blue node network without text on screen, open notebook with hand drawn empty circular tree diagram and pale blue pen.
3. Korean woman in her twenties with long dark hair, pale blue shirt and cream trousers, rear shoulder view on a clean commuter bus, studying on phone beside a sunlit window, softly blurred trees outside.
4. Close diagonal view of a cafe table by a window, unbranded phone with blurred pale blue rectangles, four blank pale blue/cream sticky notes, pen, white coffee cup, one naturally relaxed hand touching phone.

## 후보와 검증

- candidates/photo-1-a.png ~ photo-4-a.png: 각 장의 생성 원본 후보. 각 장 한 후보를 생성했고 전부 자연스러워 채택했다. 추가 후보 생성·수정은 하지 않았다.
- 원본은 1108×1420, 마지막 장은 1108×1419이다. 1170×1500으로 비율을 맞추며 약 6% 확대하고 WebP 품질 88, method 6으로 저장했다. 확대는 새 세부 묘사를 만드는 작업이 아니다.
- 네 파일 모두 실제 디코딩, WebP 형식, 1170×1500 크기, 250000 bytes 이하를 assert로 확인했다.
- contact.png: 최종 WebP 네 장을 1~4 순서로 나란히 배치한 1560×540 확인용 이미지. 직접 열어 통일감, 피사체 구도, 손, 글자·로고가 눈에 띄지 않는지 육안 확인했다. OCR 검증은 하지 않았다.
- 원본 후보도 각각 직접 열어 확인했다. 사람이 나온 장면은 정면 얼굴이 없고, 화면과 종이에 읽을 수 있는 문구가 보이지 않는다.
- 사진 자산만 제작했다. design/landing/index.html 수정, 브라우저 배치 검증, git commit은 하지 않았다.
