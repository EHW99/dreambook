# 셀프체크 — 태스크 13: 오디오북 프로토타입

## 테스트 결과
- 전체 테스트 수: 239개 (기존 232 + 신규 7)
- 통과: 239개
- 실패: 0개

## SPEC 기능 체크
- [x] **오디오북 뷰어 UI**: 일러스트를 화면에 크게 표시 (aspect-square, max-w-[400px], 둥근 모서리 3xl)
- [x] **TTS 읽기**: SpeechSynthesis API로 한국어 텍스트 읽기 (rate 0.9, pitch 1.1 — 아동 친화적)
- [x] **자동 페이지 넘김**: TTS onend 이벤트에서 다음 페이지로 자동 전환
- [x] **재생/일시정지 버튼**: Play/Pause 토글 버튼 (중앙 큰 원형 버튼)
- [x] **이전/다음 페이지 버튼**: SkipBack/SkipForward 버튼 (첫/마지막 페이지 disabled)
- [x] **진행률 표시**: 상단 진행률 바 (animated) + 하단 페이지 인디케이터 점
- [x] **TTS 구현 (Phase 2)**: 브라우저 SpeechSynthesis API 사용, 한국어 음성 자동 선택
- [x] **백엔드 API**: `GET /api/books/:id/audio-data` — 페이지별 텍스트 + 선택된 이미지 URL 반환
- [x] **내 책장 [듣기] 버튼**: 완성/주문된 책에 HeadphonesIcon + "듣기" 버튼 추가
- [x] **디자인**: 큰 일러스트 + 하단 컨트롤 바, 어둡고 따뜻한 배경 (#2a2420), 아동 친화적 UI
- [x] **인증/권한 처리**: AuthGuard 적용, 본인 책만 접근 가능 (403), 미인증 시 거부

## 구현 파일
- `backend/app/api/books.py` — audio-data 엔드포인트 추가
- `backend/app/schemas/audiobook.py` — AudioBookData, AudioPageData 스키마
- `backend/tests/test_audiobook.py` — 7개 테스트 케이스
- `frontend/src/app/books/[id]/listen/page.tsx` — 오디오북 뷰어 페이지
- `frontend/src/lib/api.ts` — getAudioData 메서드 + AudioBookData 인터페이스
- `frontend/src/components/mypage/bookshelf-tab.tsx` — [듣기] 버튼 추가
- `frontend/src/components/icons.tsx` — HeadphonesIcon 추가

## 특이사항
- SpeechSynthesis API는 브라우저마다 지원 음성이 다름. 한국어 음성이 없는 환경에서는 기본 음성으로 fallback
- 마지막 페이지 읽기 완료 시 자동으로 재생 정지 (isPlaying = false)
- 페이지 인디케이터를 클릭해 직접 페이지 이동 가능
- 뒤로가기 시 TTS를 중지하고 이전 페이지로 이동
