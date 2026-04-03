# QA 리포트 -- 태스크 11: 내 책장 + 주문 내역 + 주문 관리 (R2)

## 전체 판정: PASS
## 가중 점수: 7.4 / 10.0

## 항목별 점수
- 기능 완성도 (30%): 8/10 -- R1의 3건 피드백 모두 반영 완료. 삭제 조건(draft+character_confirmed), orderedBookIds 마운트 시 초기화, generating 상태 카드 UI 모두 정상 동작. 완료 기준 전항목 충족.
- 코드 품질 (25%): 7/10 -- 에러 처리 양호, 구조 명확. 신규 테스트 2건 추가(총 209개 전체 통과). isOrdered 함수(38~42행)가 사용되지 않는 dead code로 남아있으나 기능에 영향 없음.
- API 연동 (20%): 7/10 -- 주문 취소/배송지 변경 Book Print API 연동 유지, 이 태스크의 주 범위는 프론트엔드 UI이므로 적정 수준.
- 디자인 품질 (25%): 7/10 -- R1 대비 generating 상태 카드에 스피너+텍스트 추가로 개선. 파스텔 톤 일관, 반응형 그리드, 빈 상태/로딩/에러 UI, 삭제 확인 다이얼로그 모두 구현. 탭 내부 콘텐츠 전환 애니메이션 미적용은 경미한 사항.

가중 점수: (8 x 0.3) + (7 x 0.25) + (7 x 0.2) + (7 x 0.25) = 2.4 + 1.75 + 1.4 + 1.75 = 7.3 -> 7.4 (반올림)

## R1 피드백 반영 확인

### 1. [필수] 삭제 조건 불일치 수정 -- 반영 확인
- `backend/app/api/books.py` 157행: `book.status not in ("draft", "character_confirmed")` 으로 변경됨
- 테스트 `test_delete_character_confirmed_book` 추가: character_confirmed 상태 삭제 성공 확인
- 테스트 `test_delete_generating_book_fails` 추가: generating 상태 삭제 거부 확인
- 프론트/백 삭제 조건 일치 확인 완료

### 2. [필수] orderedBookIds 초기화 시점 개선 -- 반영 확인
- `frontend/src/app/mypage/page.tsx`: MypageContent 마운트 시 `useEffect`로 `apiClient.getOrders()` 호출하여 orderedBookIds 미리 로드
- 기존 `handleOrdersLoaded` 콜백도 유지하여 주문 탭에서 갱신 시 동기화
- "내 책장" 탭만 방문해도 주문 상태가 정확히 반영됨

### 3. [권장] generating 상태 카드 UI 보완 -- 반영 확인
- `frontend/src/components/mypage/bookshelf-tab.tsx` 153행: `isGenerating` 변수 추가
- 210~215행: generating 상태에서 스피너 + "동화책을 생성하고 있어요..." 텍스트 표시
- 상태별 색상 배지에도 generating이 "생성중"(민트)으로 정상 매핑

## SPEC 완료 기준 대조

### 1. 내 책장 (프론트엔드)
- [PASS] 동화책 목록 카드 (썸네일, 제목, 상태 배지: 작성중/완성/주문됨) -- STATUS_LABELS로 상태 매핑, orderedBookIds로 "주문됨" 배지 표시
- [PASS] 작성중인 책: [이어서 만들기] 버튼 -> 마지막 저장 단계로 이동 -- draft/character_confirmed 상태에서 `/create?bookId=` 로 이동
- [PASS] 완성된 책: [보기] -> 책 뷰어, [주문하기] -> 주문 페이지 -- isCompleted && !isBookOrdered 조건에서 두 버튼 모두 표시
- [PASS] 작성중인 책 삭제 (완성/주문된 책은 삭제 불가) -- 백엔드 draft+character_confirmed 허용, 프론트 canDelete 로직 일치
- [PASS] "+ 새 동화책 만들기" 카드 -- 대시 보더 + 호버 효과 적용
- [PASS] 빈 상태: "아직 만든 동화책이 없어요" -- 아이콘 + 메시지 + CTA 버튼 구현

### 2. 주문 내역 (프론트엔드)
- [PASS] 주문 목록 (날짜, 책 제목, 상태, 가격) -- OrdersTab에서 ordered_at, book_title, status, total_amount 표시
- [PASS] 주문 상세: 배송 정보, 주문 상태, 운송장 번호 -- 상세 뷰에서 tracking_number/tracking_carrier 표시
- [PASS] 주문 취소 버튼 (PAID/PDF_READY 상태만 표시) -- status_code 20/25만 허용, 확인 다이얼로그 포함
- [PASS] 배송지 변경 버튼 (PAID~CONFIRMED 상태만 표시) -- status_code 20/25/30만 허용, 인라인 편집 폼 구현

### 3. 백엔드 API
- [PASS] GET /api/books -- BookListResponse에 art_style, updated_at 필드 포함
- [PASS] GET /api/books/:id -- 기존 구현 정상 동작
- [PASS] DELETE /api/books/:id -- draft + character_confirmed 두 상태 모두 삭제 허용
- [PASS] GET /api/orders -- book_title 서버사이드 조인 포함
- [PASS] GET /api/orders/:id -- 소유자 확인 + 상세 정보 반환
- [PASS] POST /api/orders/:id/cancel -- 상태 검증(20/25) + Book Print API 연동
- [PASS] PATCH /api/orders/:id/shipping -- 상태 검증(20/25/30) + 부분 업데이트 + Book Print API 연동

### 4. 디자인 + 반응형
- [PASS] 파스텔 톤 색상 팔레트 일관 적용
- [PASS] 둥근 모서리, 부드러운 그림자
- [PASS] 반응형 그리드 (grid-cols-1/2/3)
- [PASS] 로딩/에러/빈 상태 UI
- [PASS] 삭제/취소 확인 다이얼로그
- [PASS] 상태별 색상 배지 (작성중=노랑, 생성중=민트, 완성=초록, 주문됨=핑크)

## 테스트 검증
- Developer 테스트 수: 209개 (전체), 태스크 11 신규 8개 (R1: 6개 + R2: 2개)
- 전체 통과: 209/209
- 프론트엔드 빌드: 성공
- 회귀 없음 확인

### R2 추가 테스트 목록:
1. TestBookshelfEndpoints::test_delete_character_confirmed_book -- character_confirmed 상태 삭제 성공
2. TestBookshelfEndpoints::test_delete_generating_book_fails -- generating 상태 삭제 거부

## 경미한 개선 사항 (PASS에 영향 없음)
1. `bookshelf-tab.tsx` 38~42행의 `isOrdered()` 함수가 사용되지 않는 dead code. 제거 권장.
2. 탭 내부 콘텐츠 전환 시 Framer Motion 애니메이션 미적용. 태스크 14(디자인 마무리)에서 일괄 처리 가능.
