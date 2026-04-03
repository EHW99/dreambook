# 셀프체크 -- 태스크 12: 웹훅 + 주문 상태 추적 (R2)

## 테스트 결과
- 전체 테스트 수: 23개 (R1: 15개 → R2: 23개, +8개 신규)
- 통과: 23개
- 실패: 0개

## R2 피드백 반영 내역

### 1. 상태 역행 방지 로직 추가
- [x] `_handle_order_confirmed()` — `if order.status_code >= 30: return` 가드 추가
- [x] `_handle_order_shipped()` — `if order.status_code >= 50: return` 가드 추가
- [x] `_handle_order_status_changed()` — `if status_code < 80 and order.status_code >= status_code: return` 가드 추가
- [x] CANCELLED(80+)은 예외: 어떤 상태에서든 전이 가능 (가드 없음)
- [x] `_handle_order_paid()` — 기존 가드 유지 (`if order.status_code <= 20`)
- [x] `_handle_order_cancelled()` — 가드 없음 (어떤 상태에서든 취소 가능)

### 2. 중복 방지 캐시 FIFO 개선
- [x] `set` → `collections.OrderedDict`로 변경
- [x] eviction: `while len >= MAX: popitem(last=False)` — 가장 오래된 항목부터 FIFO 제거
- [x] 삽입: `_processed_deliveries[delivery_id] = True`

### 3. 빠진 테스트 추가
- [x] `sha256=` 접두사 포함 서명 테스트 — `TestWebhookSignatureSha256Prefix`
- [x] 상태 역행 방지 테스트 5개 — `TestWebhookStateRegressionPrevention`
  - SHIPPED → order.confirmed 무시
  - SHIPPED → order.status_changed(IN_PRODUCTION) 무시
  - CANCELLED은 어떤 상태에서든 전이 가능 (order.cancelled)
  - DELIVERED → order.shipped 무시
  - SHIPPED → order.status_changed(CANCELLED) 가능
- [x] `delete_webhook()` 메서드 mock 테스트
- [x] `get_webhook_deliveries()` 메서드 mock 테스트

## SPEC 기능 체크

### 1. 웹훅 수신 엔드포인트
- [x] `POST /api/webhooks/sweetbook` -- 웹훅 수신: 구현 완료
- [x] HMAC-SHA256 서명 검증: `verify_webhook_signature()` 구현 (sha256= 접두사 자동 제거, tolerance 300초)
- [x] 이벤트 처리: order.paid -- 주문 확인 (PAID 상태 유지, 역행 방지)
- [x] 이벤트 처리: order.confirmed -- 상태 CONFIRMED(30)으로 업데이트 (역행 방지)
- [x] 이벤트 처리: order.status_changed -- 범용 상태 전이 (역행 방지, CANCELLED 예외)
- [x] 이벤트 처리: order.shipped -- SHIPPED(50) + tracking 정보 (역행 방지)
- [x] 이벤트 처리: order.cancelled -- CANCELLED(80) 상태로 업데이트 (항상 가능)

### 2. 웹훅 등록
- [x] 서버 시작 시 웹훅 URL 자동 등록: lifespan에서 PUT /webhooks/config 호출
- [x] BookPrintService 메서드 5개 구현 + 테스트

### 3. Sandbox 환경
- [x] Sandbox에서 PAID 이후 상태 전이 없음 인지

### 추가 구현 사항
- [x] 중복 이벤트 방지: OrderedDict FIFO 기반 멱등성 보장 (최대 10,000개)
- [x] 타임스탬프 만료 검증: 5분(300초) 허용 오차
- [x] 모범 사례 준수: 항상 200 응답 반환, 30초 내 응답

## 수정 파일 (R2)
- `backend/app/api/webhooks.py` -- 상태 역행 방지 가드 추가, OrderedDict FIFO 캐시로 변경
- `backend/tests/test_webhooks.py` -- 테스트 8개 추가 (sha256 접두사, 상태 역행 5개, delete_webhook, get_webhook_deliveries)
- `SELF_CHECK.md` -- R2 반영 업데이트
