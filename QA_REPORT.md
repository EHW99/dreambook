# QA 리포트 — 태스크 10: Book Print API 연동 + 주문 (R2)

## 전체 판정: PASS
## 가중 점수: 7.4 / 10.0

## 항목별 점수
- 기능 완성도 (30%): 8/10 — R1 피드백 5건 전부 반영 완료. 배송지 변경 부분 업데이트, 페이지 수 사전 검증, Rate Limit 재시도, 내지 삽입 실패 시 워크플로우 중단 모두 동작 확인. 엣지 케이스 테스트까지 추가됨.
- 코드 품질 (25%): 8/10 — ShippingUpdateRequest 스키마 분리 적절. model_dump(exclude_unset=True)로 부분 업데이트 정확히 구현. snake_case→camelCase 매핑 명확. 429 재시도 로직 안전 상한(30초) 포함. import json이 함수 내부에 2곳 있어 약간 아쉬우나 기능에는 영향 없음.
- API 연동 (20%): 7/10 — 전체 10단계 워크플로우 구현. 템플릿 API 활용, 충전금 자동충전, Rate Limit 재시도, 페이지 수 검증 모두 구현. 멱등성 키(Idempotency-Key) 미사용은 여전하나, Sandbox 환경에서는 실질적 위험이 낮고 태스크 범위를 넘는 수준.
- 디자인 품질 (25%): 6/10 — 주문 페이지 파스텔 톤 적용, 단계별 로딩 메시지, 완료 화면 구현. 다만 Lottie 애니메이션 미사용(PartyPopper 아이콘으로 대체), 모바일 하단 마진 우려는 R1과 동일.

## SPEC 완료 기준 대조

### 1. 백엔드 — Book Print API 연동 서비스
- [PASS] 충전금 확인 + 부족 시 자동 충전
- [PASS] 책 생성 (POST /books)
- [PASS] 사진 업로드 (POST /books/{bookUid}/photos) — 파일/바이트 모두 지원
- [PASS] 템플릿 조회 (GET /templates) — cover/content 분리
- [PASS] 표지 생성 (POST /books/{bookUid}/cover)
- [PASS] 내지 삽입 반복 (POST /books/{bookUid}/contents?breakBefore=page)
- [PASS] 책 최종화 (POST /books/{bookUid}/finalization)
- [PASS] 견적 조회 (POST /orders/estimate) + 로컬 폴백
- [PASS] 주문 생성 (POST /orders)

### 2. 주문 페이지 (프론트엔드)
- [PASS] 배송지 입력 폼 6개 필드
- [PASS] 입력 검증 (필수 필드, 전화번호, 우편번호)
- [PASS] 견적 표시
- [PASS] 주문하기 → 워크플로우 실행
- [PASS] 주문 진행 중 로딩 (8단계 메시지)
- [PASS] 주문 완료 화면

### 3. 에러 처리
- [PASS] 충전금 부족 → 자동 충전 + 402 재시도
- [PASS] API 오류 → 502 + 사용자 메시지
- [PASS] 타임아웃 → 408
- [PASS] Rate Limit(429) → Retry-After 기반 재시도 (최대 2회, 상한 30초) **(R2 신규)**

### 4. 백엔드 API
- [PASS] POST /api/books/:id/estimate
- [PASS] POST /api/books/:id/order
- [PASS] GET /api/orders
- [PASS] GET /api/orders/:id
- [PASS] POST /api/orders/:id/cancel
- [PASS] PATCH /api/orders/:id/shipping — ShippingUpdateRequest로 부분 업데이트 구현 **(R1 피드백 반영 완료)**

### 5. Sandbox PAID 상태 정지 인지
- [PASS] 주문 완료 화면 + 주문 페이지에 Sandbox 안내

## R1 피드백 반영 확인

### 1. 배송지 변경 스키마 분리 — 반영됨
- `ShippingUpdateRequest` 스키마 신규 생성. 모든 필드 `Optional`. validator 포함.
- `update_order_shipping` 엔드포인트에서 `ShippingUpdateRequest` 사용.
- `model_dump(exclude_unset=True)`로 전달된 필드만 추출 → DB에서 해당 필드만 setattr.

### 2. 배송지 변경 테스트 추가 — 반영됨
- `test_update_shipping_success` — 전체 필드 변경 → 200, 모든 값 확인
- `test_update_shipping_partial` — 이름만 변경, 기존 postal_code/address1 유지 확인
- `test_update_shipping_wrong_status` — IN_PRODUCTION(40) → 400
- `test_update_shipping_other_user` — 타인 주문 → 403
- `test_update_shipping_no_auth` — 미인증 → 401/403
- ShippingUpdateRequest 스키마 단위 테스트 5건 추가

### 3. 페이지 수 사전 검증 — 반영됨
- `execute_order_workflow`에서 내지 삽입 후, 최종화 전에 `BOOK_SPEC_UIDS` 기반 page_min~page_max 검증.
- 범위 밖이면 `BookPrintAPIError` raise → 최종화 미호출.
- `test_page_count_out_of_range` 테스트 확인: 10페이지(최소 24) → 에러.

### 4. Rate Limit(429) 재시도 — 반영됨
- `_request` 메서드에 `_retry_count` 파라미터 + 재귀 재시도 (최대 2회).
- `Retry-After` 헤더 파싱, 상한 30초.
- `test_429_retries_with_retry_after` — 재시도 후 성공, sleep(1) 호출 확인.
- `test_429_max_retries_exceeded` — 3회 연속 429 → BookPrintAPIError(429).

### 5. 워크플로우 중간 실패 시 중단 — 반영됨
- 내지 삽입 실패 시 즉시 `BookPrintAPIError` raise (기존: logger.warning 후 계속 진행).
- `test_content_insert_failure_aborts_workflow` — finalize_book.assert_not_called() 확인.

## 테스트 검증
- Developer 테스트 수: 44개 (기존 28 + R2 신규 16)
- 전체 테스트: 201개 통과, 0개 실패
- 회귀: 없음 (기존 28개 모두 통과 유지)
- 빠진 테스트 케이스:
  - 빈 update_fields 전달 시 400 반환 테스트 — `ShippingUpdateRequest()`로 모든 필드 None일 때 `exclude_unset=True`가 빈 dict를 반환하는 케이스. 코드에서 처리하고 있으나 엔드포인트 레벨 테스트가 없다. 단, 스키마 단위 테스트에서 빈 생성은 확인됨.
  - 크리티컬한 누락은 아님.

## 구체적 개선 지시

없음 — R1 피드백 5건 모두 적절히 반영됨. PASS 판정.
