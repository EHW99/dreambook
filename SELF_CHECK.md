# 셀프체크 -- 태스크 11: 내 책장 + 주문 내역 + 주문 관리 (R2)

## 테스트 결과
- 전체 테스트 수: 209개
- 통과: 209개
- 실패: 0개
- 태스크 11 신규 테스트: 8개 (R1: 6개 + R2: 2개 추가)
- 프론트엔드 빌드: 성공

## R2 피드백 반영 내역

### 1. [필수] 삭제 조건 불일치 수정 — DONE
- **파일**: `backend/app/api/books.py` 157행
- **변경**: `book.status != "draft"` → `book.status not in ("draft", "character_confirmed")`
- **테스트**: `test_delete_character_confirmed_book` 추가 (character_confirmed 상태 삭제 성공 확인)
- **테스트**: `test_delete_generating_book_fails` 추가 (generating 상태 삭제 거부 확인)

### 2. [필수] orderedBookIds 초기화 시점 개선 — DONE
- **파일**: `frontend/src/app/mypage/page.tsx`
- **변경**: MypageContent 마운트 시 `useEffect`로 `apiClient.getOrders()`를 호출하여 orderedBookIds를 미리 로드
- 기존 `handleOrdersLoaded` 콜백도 유지 (주문 탭에서 갱신 시 동기화)

### 3. [권장] generating 상태 카드 UI 보완 — DONE
- **파일**: `frontend/src/components/mypage/bookshelf-tab.tsx`
- **변경**: generating 상태일 때 스피너 + "동화책을 생성하고 있어요..." 텍스트 표시
- isDraft/isEditing/isCompleted 외에 isGenerating 조건 추가

## SPEC 기능 체크

### 1. 내 책장 (프론트엔드)
- [x] 동화책 목록 카드 (썸네일, 제목, 상태 배지: 작성중/완성/주문됨)
- [x] 작성중인 책: [이어서 만들기] 버튼 -> 마지막 저장 단계로 이동
- [x] 완성된 책: [보기] -> 책 뷰어, [주문하기] -> 주문 페이지
- [x] 작성중인 책 삭제 (draft + character_confirmed 모두 삭제 가능, 완성/주문된 책은 삭제 불가)
- [x] generating 상태 카드: 스피너 + "동화책을 생성하고 있어요..." 표시
- [x] "+ 새 동화책 만들기" 카드 (대시 보더 + 호버 효과)
- [x] 빈 상태: "아직 만든 동화책이 없어요" + 일러스트 아이콘
- [x] orderedBookIds 마운트 시 초기화 (탭 전환 없이도 정확한 상태 표시)

### 2. 주문 내역 (프론트엔드)
- [x] 주문 목록 (날짜, 책 제목, 상태, 가격)
- [x] 주문 상세: 배송 정보, 주문 상태, 운송장 번호
- [x] 주문 취소 버튼 (PAID/PDF_READY 상태만 표시) + 확인 다이얼로그
- [x] 배송지 변경 버튼 (PAID~CONFIRMED 상태만 표시) + 인라인 편집 폼

### 3. 백엔드 API
- [x] GET /api/books -- 내 동화책 목록 (art_style, updated_at 필드 추가)
- [x] GET /api/books/:id -- 동화책 상세
- [x] DELETE /api/books/:id -- 작성중(draft + character_confirmed) 동화책 삭제
- [x] GET /api/orders -- 내 주문 목록 (book_title 필드 추가)
- [x] GET /api/orders/:id -- 주문 상세
- [x] POST /api/orders/:id/cancel -- 주문 취소
- [x] PATCH /api/orders/:id/shipping -- 배송지 변경

### 4. 디자인/반응형
- [x] 파스텔 톤 색상 팔레트 일관 적용
- [x] 둥근 모서리, 부드러운 그림자
- [x] 모바일/태블릿/데스크톱 반응형 (grid-cols-1/2/3)
- [x] 로딩/에러/빈 상태 UI 구현
- [x] 삭제/취소 확인 다이얼로그
- [x] 상태별 색상 배지 (작성중=노랑, 생성중=민트, 완성=초록, 주문됨=핑크)

## 신규/수정 파일 (R2)

### 백엔드
- `backend/app/api/books.py` -- 삭제 조건에 character_confirmed 추가
- `backend/tests/test_orders.py` -- character_confirmed 삭제 테스트 + generating 삭제 거부 테스트 추가

### 프론트엔드
- `frontend/src/app/mypage/page.tsx` -- useEffect로 orderedBookIds 마운트 시 로드
- `frontend/src/components/mypage/bookshelf-tab.tsx` -- generating 상태 카드 UI (스피너 + 텍스트)

## 특이사항
- 기존 207개 테스트 + 신규 2개 = 총 209개 모두 통과 (회귀 없음)
- 프론트엔드 빌드 성공
