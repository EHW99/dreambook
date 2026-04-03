# 셀프체크 — 태스크 7: 동화책 만들기 위자드 — 스타일 선택 + 캐릭터 미리보기 (R2)

## 테스트 결과
- 전체 테스트 수: 111개 (기존 83개 + 태스크 7 신규 28개)
- 통과: 111개
- 실패: 0개

## R2 피드백 반영 내역

### 피드백 1: book.status "character_confirmed" 전이 누락
- [x] `select_character_sheet()`에서 캐릭터 선택 시 `book.status`를 `"character_confirmed"`로 자동 변경
- [x] `BookUpdateRequest`에 `status` 필드(Optional) 추가 + `VALID_STATUSES` 검증
- [x] 프론트엔드 step 5→6 전환 시 `status: "character_confirmed"` 함께 전송
- [x] 테스트 추가: `test_select_character_updates_book_status`, `test_update_status_valid`, `test_update_status_invalid`

### 피드백 2: "확정하기" 서버 동기화 없음
- [x] `onConfirm` 콜백에서 `apiClient.getBook()`으로 서버 최신 상태 로드
- [x] `loadBookState()`로 book 상태 반영 → 새로고침 시에도 `character_confirmed` 상태 유지
- [x] `setCharacterConfirmed`는 `loadBookState` 내부에서 status 기반으로도 판단 (line 128)

### 피드백 3: step 전환 시 서버 검증 없음
- [x] PATCH `/api/books/:id`에서 `current_step >= 6` && `book.current_step <= 5` 전환 시 `is_selected=True`인 캐릭터 존재 여부 서버 측 검증
- [x] 미선택 시 422 에러: "캐릭터를 선택해주세요"
- [x] 테스트 추가: `test_step_5_to_6_without_character_selected`, `test_step_5_to_6_with_character_selected`, `test_step_5_to_6_character_created_but_not_selected`

## SPEC 기능 체크

### 1. 동화 스타일 선택
- [x] "꿈꾸는 오늘" / "미래의 나" 카드 선택 UI
- [x] 각 스타일 설명 텍스트 표시

### 2. 그림체 선택
- [x] 5가지 스타일 카드 (수채화/연필화/크레파스/3D/만화)
- [x] 각 스타일별 아이콘+색상 팔레트 기반 시각적 미리보기

### 3. 캐릭터 미리보기
- [x] "캐릭터 생성하기" 버튼 → 더미 캐릭터 이미지 반환
- [x] 생성된 캐릭터 시트 갤러리 표시
- [x] 재생성 버튼 + 남은 횟수 표시 (최대 4회)
- [x] 갤러리에서 하나 선택 → 선택 시 book.status 자동 전이
- [x] "확정하기" 버튼 → 서버 동기화 + 다음 단계 진행 가능

### 4. 백엔드
- [x] `PATCH /api/books/:id` — 스타일/그림체/status 저장 + 유효성 검증
- [x] `POST /api/books/:id/character` — 캐릭터 시트 생성
- [x] `GET /api/books/:id/characters` — 갤러리 조회
- [x] `PATCH /api/books/:id/character/:charId/select` — 캐릭터 선택 + status 전이
- [x] step 5→6 전환 시 캐릭터 선택 여부 서버 검증 (422)

### 5. 뒤로가기
- [x] 캐릭터 확정 후 이전 단계 돌아갈 시 캐릭터 재선택 가능
- [x] 재생성 횟수 유지 (서버 관리)

### 6. 디자인, 반응형
- [x] 파스텔 톤 디자인 시스템 적용
- [x] Framer Motion 애니메이션
- [x] 반응형: grid-cols-1/2/3 breakpoints

## 특이사항
- Phase 2이므로 캐릭터 이미지는 placeholder 경로만 반환
- 캐릭터 미리보기 UI에서는 아이콘 기반 placeholder 표시
