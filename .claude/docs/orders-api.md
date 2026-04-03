# Orders API 분석 보고서

> 작성일: 2026-04-02
> 목적: Book Print API의 Orders API 완전 분석 — 필수 사용 API

---

## 1. 개요

Orders API는 FINALIZED 상태의 책을 대상으로 **주문 생성, 조회, 취소, 배송지 변경**을 처리한다.
주문 생성 시 **충전금이 즉시 차감**되는 선불 결제 방식이다.

---

## 2. 엔드포인트 전체 목록

| 메서드 | URL | 설명 |
|--------|-----|------|
| POST | `/v1/orders/estimate` | 견적 조회 (차감 없음) |
| POST | `/v1/orders` | 주문 생성 (충전금 즉시 차감) |
| GET | `/v1/orders` | 주문 목록 조회 |
| GET | `/v1/orders/{orderUid}` | 주문 상세 조회 |
| POST | `/v1/orders/{orderUid}/cancel` | 주문 취소 (환불) |
| PATCH | `/v1/orders/{orderUid}/shipping` | 배송지 변경 |

---

## 3. 주문 전체 흐름

```
[1] GET /credits              → 충전금 잔액 확인
[2] POST /orders/estimate     → 견적 조회 (비용 미리 확인)
[3] POST /orders              → 주문 생성 (충전금 차감)
[4] GET /orders/{orderUid}    → 주문 상태 확인
[5] (선택) 취소 또는 배송지 변경
```

---

## 4. 견적 조회 (POST /orders/estimate)

주문 전 비용을 미리 확인한다. 충전금은 차감되지 않는다.

### 요청

```json
{
  "items": [
    { "bookUid": "bk_abc123", "quantity": 1 },
    { "bookUid": "bk_def456", "quantity": 2 }
  ]
}
```

| 필드 | 타입 | 필수 | 설명 |
|------|------|:---:|------|
| items | array | O | 주문 항목 목록 |
| items[].bookUid | string | O | FINALIZED 상태의 책 UID |
| items[].quantity | int | O | 수량 (1~100) |

### 응답

```json
{
  "success": true,
  "data": {
    "items": [
      {
        "bookUid": "bk_abc123",
        "pageCount": 24,
        "quantity": 1,
        "unitPrice": 20300,
        "itemAmount": 20300
      }
    ],
    "productAmount": 20300,
    "shippingFee": 3500,
    "packagingFee": 500,
    "totalAmount": 24300,
    "paidCreditAmount": 25630,
    "creditBalance": 401000,
    "creditSufficient": true
  }
}
```

| 응답 필드 | 설명 |
|----------|------|
| productAmount | 상품 금액 합계 |
| shippingFee | 배송비 (3,500원 고정) |
| packagingFee | 포장비 (500원 × 수량) |
| totalAmount | 세전 합계 |
| paidCreditAmount | **실제 차감액 (VAT 10% 포함)** |
| creditBalance | 현재 충전금 잔액 |
| creditSufficient | 잔액 충분 여부 (true/false) |

### 비용 구조

```
상품금액 (productAmount)
  + 배송비 (shippingFee: 3,500원)
  + 포장비 (packagingFee: 500원 × 수량)
  = 세전 합계 (totalAmount)
  × 1.1 (VAT 10%)
  = 최종 차감액 (paidCreditAmount)
```

### SDK 사용법

```python
result = client.orders.estimate([
    {"bookUid": "bk_abc123", "quantity": 1}
])
data = result["data"]
print(f"결제금액: {data['paidCreditAmount']}원")
print(f"잔액 충분: {data['creditSufficient']}")
```

---

## 5. 주문 생성 (POST /orders)

FINALIZED 상태의 책을 주문한다. **충전금이 즉시 차감된다.**

### 요청

```json
{
  "items": [
    { "bookUid": "bk_abc123", "quantity": 1 }
  ],
  "shipping": {
    "recipientName": "홍길동",
    "recipientPhone": "010-1234-5678",
    "postalCode": "06101",
    "address1": "서울시 강남구 테헤란로 123",
    "address2": "4층 401호",
    "memo": "부재시 경비실"
  },
  "externalRef": "MY-ORDER-001"
}
```

| 필드 | 타입 | 필수 | 설명 |
|------|------|:---:|------|
| items | array | O | 주문 항목 |
| items[].bookUid | string | O | FINALIZED 책 UID |
| items[].quantity | int | O | 수량 (1~100) |
| shipping.recipientName | string | O | 수령인 (최대 100자) |
| shipping.recipientPhone | string | O | 연락처 (최대 20자) |
| shipping.postalCode | string | O | 우편번호 (최대 10자) |
| shipping.address1 | string | O | 주소 (최대 200자) |
| shipping.address2 | string | — | 상세주소 (최대 200자) |
| shipping.memo | string | — | 배송 메모 (최대 200자) |
| externalRef | string | — | 외부 참조 ID (최대 100자) |

### 응답 (201 Created)

```json
{
  "success": true,
  "message": "주문이 생성되었습니다",
  "data": {
    "orderUid": "or_3eAx1IQiGByu",
    "orderType": "NORMAL",
    "orderStatus": 20,
    "orderStatusDisplay": "결제완료",
    "isTest": true,
    "totalProductAmount": 60400.00,
    "totalShippingFee": 3500.00,
    "totalPackagingFee": 500.00,
    "totalAmount": 64400.00,
    "paidCreditAmount": 64400.00,
    "creditBalanceAfter": 935600.00,
    "recipientName": "홍길동",
    "recipientPhone": "010-1234-5678",
    "postalCode": "06101",
    "address1": "서울시 강남구 테헤란로 123",
    "address2": "4층 401호",
    "shippingMemo": "부재시 경비실",
    "orderedAt": "2026-02-19T01:10:47Z",
    "paidAt": "2026-02-19T01:10:47Z",
    "items": [
      {
        "itemUid": "oi_aB3cD4eF5gH6",
        "bookUid": "bk_abc123",
        "bookTitle": "우리 아이 성장앨범",
        "bookSpecUid": "bs_spec001",
        "bookSpecName": "포토북 A4",
        "quantity": 1,
        "pageCount": 24,
        "unitPrice": 60400.00,
        "itemAmount": 60400.00,
        "itemStatus": 20,
        "itemStatusDisplay": "결제완료"
      }
    ]
  }
}
```

### 처리 로직

1. 각 bookUid 유효성 검증 (존재 여부, 파트너 소유, FINALIZED 상태)
2. bookSpecUid 기반 가격 계산
3. 배송비(3,500원) + 포장비(500원 × 수량) + 상품금액 합산
4. VAT 10% 적용
5. 충전금 잔액 확인 → 차감
6. 주문/항목 레코드 생성

### 에러 응답

**402 Payment Required (충전금 부족)**
```json
{
  "success": false,
  "message": "Insufficient Credit",
  "data": {
    "required": 64400.00,
    "balance": 10000.00,
    "currency": "KRW"
  },
  "errors": ["잔액이 부족합니다. 필요: 64400.00, 잔액: 10000.00"]
}
```

**400 Bad Request (유효성 실패)**
```json
{
  "success": false,
  "message": "Validation Error",
  "errors": ["Book을 찾을 수 없습니다: bk_invalid"]
}
```

### SDK 사용법

```python
order = client.orders.create(
    items=[{"bookUid": "bk_abc123", "quantity": 1}],
    shipping={
        "recipientName": "홍길동",
        "recipientPhone": "010-1234-5678",
        "postalCode": "06101",
        "address1": "서울시 강남구 테헤란로 123",
        "address2": "4층 401호",
        "memo": "부재시 경비실"
    },
    external_ref="MY-ORDER-001"
)
order_uid = order["data"]["orderUid"]
```

---

## 6. 주문 목록 조회 (GET /orders)

### 쿼리 파라미터

| 파라미터 | 타입 | 기본값 | 설명 |
|---------|------|-------|------|
| limit | int | 20 | 조회 수 (최대 100) |
| offset | int | 0 | 건너뛸 수 |
| status | int | — | 상태 필터 (20, 25, 30...) |
| from | string | — | 시작 일시 (ISO 8601) |
| to | string | — | 종료 일시 (ISO 8601) |

### SDK 사용법

```python
# 전체 조회
result = client.orders.list(limit=30)

# PAID 상태만
result = client.orders.list(status=20)

# 기간 필터
result = client.orders.list(
    from_date="2026-01-01T00:00:00Z",
    to_date="2026-03-31T23:59:59Z"
)
```

---

## 7. 주문 상세 조회 (GET /orders/{orderUid})

주문 생성 응답과 동일한 구조의 상세 정보 반환.
추가로 배송 추적 정보(trackingCarrier, trackingNumber)가 포함될 수 있음.

### SDK 사용법

```python
detail = client.orders.get("or_3eAx1IQiGByu")
data = detail["data"]
print(f"상태: {data['orderStatusDisplay']} ({data['orderStatus']})")
```

---

## 8. 주문 취소 (POST /orders/{orderUid}/cancel)

### 취소 조건

- **PAID(20)** 상태에서만 파트너가 취소 가능
- CONFIRMED(30) 이후에는 **관리자만** 취소 가능
- 취소 시 충전금 **전액 즉시 환불**

### 요청

```json
{
  "cancelReason": "고객 변심"
}
```

### SDK 사용법

```python
client.orders.cancel("or_3eAx1IQiGByu", "테스트 주문 취소")
```

---

## 9. 배송지 변경 (PATCH /orders/{orderUid}/shipping)

### 변경 조건

- PAID(20), PDF_READY(25), CONFIRMED(30) 상태에서만 가능
- SHIPPED(60) 이후에는 변경 불가
- 변경할 필드만 전달하면 됨

### 요청

```json
{
  "recipientName": "김영희",
  "address1": "서울시 서초구 반포대로 100"
}
```

### SDK 사용법

```python
client.orders.update_shipping(
    "or_3eAx1IQiGByu",
    recipient_name="김영희",
    address1="서울시 서초구 반포대로 100"
)
```

---

## 10. 주문 상태 흐름

### 정상 흐름

```
PAID (20)
  ↓ 자동 (PDF 생성)
PDF_READY (25)
  ↓ 관리자 (제작 확정)
CONFIRMED (30)
  ↓ 관리자 (제작 시작)
IN_PRODUCTION (40)
  ↓ 관리자 (제작 완료)
PRODUCTION_COMPLETE (50)
  ↓ 관리자 (발송)
SHIPPED (60)
  ↓ 관리자 (배송 완료)
DELIVERED (70)
```

### 취소 흐름

```
PAID (20) ──→ CANCELLED_REFUND (81)  [파트너 취소, 즉시 환불]
PDF_READY (25) ──→ CANCELLED_REFUND (81)  [파트너 취소, 즉시 환불]
```

### 상태별 가능 액션

| 상태 | 코드 | 파트너 취소 | 배송지 변경 | 설명 |
|------|:---:|:--------:|:--------:|------|
| PAID | 20 | O | O | 결제 완료 |
| PDF_READY | 25 | O | O | PDF 생성 완료 |
| CONFIRMED | 30 | X | O | 제작 확정 |
| IN_PRODUCTION | 40 | X | X | 인쇄 중 |
| PRODUCTION_COMPLETE | 50 | X | X | 제작 완료 |
| SHIPPED | 60 | X | X | 발송됨 |
| DELIVERED | 70 | X | X | 배송 완료 |
| CANCELLED | 80 | — | — | 취소 |
| CANCELLED_REFUND | 81 | — | — | 취소+환불 완료 |

---

## 11. Sandbox 환경 특이사항

- 주문이 **PAID(20) 상태에서 멈춤** — 이후 상태 전이는 발생하지 않음
- 테스트 가격 적용 (100원 이하)
- 실제 인쇄/배송 없음
- 충전금 무료 충전 가능 (파트너 포털 또는 `POST /credits/sandbox/charge`)
- 웹훅 테스트는 `POST /webhooks/test`로 이벤트 시뮬레이션 가능

---

## 12. 웹훅 이벤트 연동

주문 상태 변경 시 등록된 웹훅 URL로 이벤트가 전송됨.

| 이벤트 | 발생 시점 |
|--------|---------|
| `order.paid` | 주문 생성 및 결제 완료 |
| `order.confirmed` | 제작 확정 |
| `order.status_changed` | 상태 변경 (범용) |
| `order.shipped` | 발송 완료 |
| `order.cancelled` | 주문 취소 |

---

## 13. 에러 코드 정리

| HTTP 코드 | 원인 | 대응 |
|----------|------|------|
| 201 | 주문 생성 성공 | — |
| 200 | 조회/수정 성공 | — |
| 400 | 유효성 실패 (책 미존재, 미FINALIZED 등) | 요청 파라미터 확인 |
| 401 | 인증 실패 | API Key 확인 |
| 402 | 충전금 부족 | 충전 필요, 견적 조회로 사전 확인 |
| 404 | 주문 미존재 | orderUid 확인 |
| 500 | 서버 오류 | 재시도 |

---

## 14. 실제 테스트 결과 (2026-04-02)

SDK를 사용한 Sandbox 환경 테스트:

```bash
$ python simple_orders.py list
주문이 없습니다.
```

- API 인증 정상 동작 확인
- 현재 주문 0건 (책 미생성 상태)
- 전체 테스트(책 생성→최종화→주문→취소)는 충전금 충전 후 가능

### 충전금 상태

```bash
$ python simple_credits.py balance
충전금 잔액: 0원 (KRW)
환경: test
```

**주문 테스트를 위해서는 먼저 Sandbox 충전금을 충전해야 함.**

---

## 15. 참고 자료

- [Orders API 공식 문서](https://api.sweetbook.com/docs/api/orders/)
- [주문 상태 흐름](https://api.sweetbook.com/docs/operations/order-status/)
- [주문/결제 가이드](https://api.sweetbook.com/docs/guides/orders/)
- [충전금 관리](https://api.sweetbook.com/docs/operations/credits/)
- [웹훅 이벤트](https://api.sweetbook.com/docs/api/webhook-events/)
- [에러 코드](https://api.sweetbook.com/docs/api/errors/)
- [Python SDK orders.py](https://github.com/sweet-book/bookprintapi-python-sdk/blob/main/bookprintapi/orders.py)
- [SDK 주문 예제](https://github.com/sweet-book/bookprintapi-python-sdk/blob/main/examples/simple_orders.py)
