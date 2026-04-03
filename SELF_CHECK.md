# 셀프체크 — 태스크 10: Book Print API 연동 + 주문 (R2)

## 테스트 결과
- 전체 테스트 수: 201개
- 통과: 201개
- 실패: 0개
- 태스크 10 테스트: 44개 (기존 28 + 신규 16)

## QA 피드백 반영 (5건)

### 1. 배송지 변경 스키마 분리
- [x] `ShippingUpdateRequest` 스키마 신규 생성 (모든 필드 Optional)
- [x] `PATCH /orders/:id/shipping` 엔드포인트가 `ShippingUpdateRequest`를 사용하도록 변경
- [x] `model_dump(exclude_unset=True)`로 전달된 필드만 추출 → 부분 업데이트 구현
- [x] Book Print API에도 변경된 필드만 전달 (snake_case → camelCase 매핑)

### 2. 배송지 변경 테스트 추가
- [x] `test_update_shipping_success` — 정상 배송지 변경 (전체 필드)
- [x] `test_update_shipping_partial` — 부분 변경 (이름만), 기존 값 유지 확인
- [x] `test_update_shipping_wrong_status` — IN_PRODUCTION(40) 상태 → 400
- [x] `test_update_shipping_other_user` — 타인 주문 변경 → 403
- [x] `test_update_shipping_no_auth` — 인증 없음 → 401/403
- [x] `ShippingUpdateRequest` 스키마 단위 테스트 5건 (부분 업데이트, 검증)

### 3. 페이지 수 사전 검증
- [x] `execute_order_workflow`에서 최종화 전 판형별 `page_min`~`page_max` 범위 체크
- [x] 범위 밖이면 `BookPrintAPIError` 발생, 최종화 호출 방지
- [x] `test_page_count_out_of_range` 테스트 추가

### 4. Rate Limit(429) 재시도
- [x] `_request` 메서드에 429 응답 시 `Retry-After` 헤더 기반 재시도 로직 (최대 2회)
- [x] 안전 상한 30초, asyncio.sleep 사용
- [x] `test_429_retries_with_retry_after` — 재시도 후 성공 확인
- [x] `test_429_max_retries_exceeded` — 최대 재시도 초과 시 에러

### 5. 워크플로우 중간 실패 시 중단
- [x] 내지 삽입 실패 시 즉시 `BookPrintAPIError` 발생 → 워크플로우 중단
- [x] 불완전한 책의 최종화 방지
- [x] `test_content_insert_failure_aborts_workflow` — finalize_book 미호출 확인

### 추가 테스트
- [x] `test_cancel_in_production_fails` — IN_PRODUCTION 상태 취소 → 400
- [x] `test_cancel_other_user_order_fails` — 타인 주문 취소 → 403

## SPEC 기능 체크 (R1에서 이미 완료)

### 1. 백엔드 — Book Print API 연동 서비스
- [x] Sandbox 충전금 확인 + 부족 시 자동 충전
- [x] 책 생성, 사진 업로드, 템플릿 조회, 표지 생성, 내지 삽입, 최종화, 견적 조회, 주문 생성

### 2. 주문 페이지 (프론트엔드)
- [x] 배송지 입력 폼 + 검증 + 견적 표시 + 워크플로우 실행 + 로딩 + 완료 화면

### 3. 에러 처리
- [x] 충전금 부족 → 자동 충전, API 오류 → 사용자 안내, 타임아웃 처리

### 4. 백엔드 API
- [x] estimate, order, orders 목록/상세, cancel, shipping 변경

### 5. Sandbox PAID 상태 정지 인지
- [x] Sandbox 안내 메시지 표시

## 수정 파일
- `backend/app/schemas/order.py` — `ShippingUpdateRequest` 스키마 추가
- `backend/app/api/orders.py` — 배송지 변경 엔드포인트 `ShippingUpdateRequest` 적용 + 부분 업데이트
- `backend/app/services/bookprint.py` — Rate Limit 재시도, 페이지 수 검증, 내지 삽입 실패 중단
- `backend/tests/test_orders.py` — 테스트 16건 추가

## 특이사항
- 기존 28개 테스트 모두 통과 유지 (회귀 없음)
- 전체 프로젝트 201개 테스트 모두 통과
