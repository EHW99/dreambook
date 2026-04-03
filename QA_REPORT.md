# QA 리포트 — 태스크 12: 웹훅 + 주문 상태 추적 (R2)

## 전체 판정: PASS
## 가중 점수: 7.6 / 10.0

## 항목별 점수
- 기능 완성도 (30%): 8/10 — R1 피드백 3건(상태 역행 방지, FIFO 캐시, 빠진 테스트) 모두 반영 완료. 5개 이벤트 처리, HMAC-SHA256 서명 검증(sha256= 접두사 호환), 웹훅 자동 등록, 중복 이벤트 멱등성, 상태 역행 방지 가드 전 핸들러 적용.
- 코드 품질 (25%): 8/10 — OrderedDict FIFO 캐시로 결정론적 eviction 보장. 상태 역행 방지 로직이 각 핸들러에 일관되게 적용됨. CANCELLED(80+) 예외 처리 정확. API Key 하드코딩 없음. 에러 시에도 200 반환(모범 사례).
- API 연동 (20%): 7/10 — BookPrintService 웹훅 메서드 5개(register, get, delete, test, deliveries) 모두 구현. lifespan에서 자동 등록 + secretKey 동적 반영. Sandbox PAID 상태 정지 인지.
- 디자인 품질 (25%): 6/10 — 백엔드 전용 태스크. 프론트엔드에 주문 상태 실시간 반영 UI가 없으나, 이는 태스크 12 범위 밖(주문 목록 UI는 태스크 11 영역). 웹훅 수신 후 DB 업데이트까지의 백엔드 흐름은 완성됨.

## R1 피드백 반영 확인

### 피드백 1: 상태 역행 방지 로직 — PASS
- `_handle_order_confirmed()`: `if order.status_code >= 30: return` 가드 추가 확인 (webhooks.py 128행)
- `_handle_order_shipped()`: `if order.status_code >= 50: return` 가드 추가 확인 (webhooks.py 182행)
- `_handle_order_status_changed()`: `if status_code < 80 and order.status_code >= status_code: return` 가드 추가 확인 (webhooks.py 156행)
- `_handle_order_cancelled()`: 가드 없음 — 어떤 상태에서든 취소 가능 (설계 의도 부합)
- `_handle_order_paid()`: 기존 `if order.status_code <= 20` 가드 유지

### 피드백 2: 중복 방지 캐시 FIFO — PASS
- `set` → `collections.OrderedDict`로 변경 확인 (webhooks.py 10행, 29행)
- eviction: `while len >= _MAX_DELIVERY_CACHE: popitem(last=False)` — 가장 오래된 항목부터 FIFO 제거 확인 (webhooks.py 291-292행)
- 삽입: `_processed_deliveries[delivery_id] = True` 확인 (webhooks.py 293행)

### 피드백 3: 빠진 테스트 — PASS
- `sha256=` 접두사 포함 서명 테스트: `TestWebhookSignatureSha256Prefix` 클래스 1개 테스트 추가 확인
- 상태 역행 방지 테스트: `TestWebhookStateRegressionPrevention` 클래스 5개 테스트 추가 확인
  - SHIPPED → order.confirmed 무시
  - SHIPPED → order.status_changed(IN_PRODUCTION) 무시
  - CANCELLED은 어떤 상태에서든 전이 가능
  - DELIVERED → order.shipped 무시
  - SHIPPED → order.status_changed(CANCELLED) 가능
- `delete_webhook()` mock 테스트 추가 확인
- `get_webhook_deliveries()` mock 테스트 추가 확인

### 기존 합격 항목 퇴보 여부 — 없음
- R1에서 통과한 15개 테스트 전부 유지, 추가 8개 포함 총 23개 전수 통과 확인

## SPEC 완료 기준 대조
- [PASS] 완료 기준 1: `POST /api/webhooks/sweetbook` 엔드포인트 구현. HMAC-SHA256 서명 검증 (sha256= 접두사 호환, 타임스탬프 만료 300초). 5개 이벤트(order.paid, order.confirmed, order.status_changed, order.shipped, order.cancelled) 모두 처리. orders 테이블 상태/tracking 업데이트. 상태 역행 방지 가드 전 핸들러 적용.
- [PASS] 완료 기준 2: lifespan에서 `PUT /webhooks/config` 호출하여 웹훅 자동 등록. WEBHOOK_URL 미설정 시 건너뜀. secretKey 동적 반영.
- [PASS] 완료 기준 3: `BookPrintService.send_test_webhook()`, `get_webhook_deliveries()` 포함 5개 메서드 구현 + mock 테스트 완비.
- [PASS] 완료 기준 4: Sandbox PAID 이후 상태 전이 없음 인지. isTest 필드 로깅.

## 테스트 검증
- Developer 테스트 수: 23개 (R1: 15개 → R2: +8개)
- 통과: 23개 / 23개
- 실행 시간: 5.10초
- 빠진 테스트 케이스: 없음 (R1 지적 사항 모두 반영됨)

## 구체적 개선 지시
없음 — R1 피드백 3건 모두 정확히 반영되었고, 기존 기능 퇴보 없음.
