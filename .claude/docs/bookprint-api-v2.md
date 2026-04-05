# Book Print API 공식 문서 (전체)

> 크롤링 일시: 2026-04-05
> 소스: https://api.sweetbook.com/docs/
> 총 37개 페이지

---

## 목차

### 시작하기
- [개요](https://api.sweetbook.com/docs/)
- [회원가입](https://api.sweetbook.com/docs/registration/)
- [환경](https://api.sweetbook.com/docs/environments/)
- [인증](https://api.sweetbook.com/docs/authentication/)
- [퀵스타트](https://api.sweetbook.com/docs/quickstart/)

### 통합 가이드
- [워크플로우](https://api.sweetbook.com/docs/guides/workflow/)
- [판형](https://api.sweetbook.com/docs/guides/book-specs/)
- [템플릿](https://api.sweetbook.com/docs/guides/templates/)
- [책](https://api.sweetbook.com/docs/guides/books/)
- [이미지](https://api.sweetbook.com/docs/guides/images/)
- [주문](https://api.sweetbook.com/docs/guides/orders/)
- [웹훅](https://api.sweetbook.com/docs/guides/webhooks/)
- [Go Live](https://api.sweetbook.com/docs/guides/go-live/)

### API 레퍼런스
- [공통](https://api.sweetbook.com/docs/api/common/)
- [Books](https://api.sweetbook.com/docs/api/books/)
- [Orders](https://api.sweetbook.com/docs/api/orders/)
- [Templates](https://api.sweetbook.com/docs/api/templates/)
- [BookSpecs](https://api.sweetbook.com/docs/api/book-specs/)
- [Credits](https://api.sweetbook.com/docs/api/credits/)
- [Webhooks](https://api.sweetbook.com/docs/api/webhooks/)
- [Webhook Events](https://api.sweetbook.com/docs/api/webhook-events/)
- [Errors](https://api.sweetbook.com/docs/api/errors/)

### 운영 가이드
- [충전금](https://api.sweetbook.com/docs/operations/credits/)
- [주문 상태](https://api.sweetbook.com/docs/operations/order-status/)
- [트러블슈팅](https://api.sweetbook.com/docs/operations/troubleshooting/)

### 개념
- [동적 레이아웃](https://api.sweetbook.com/docs/concepts/dynamic-layout/)
- [템플릿 엔진](https://api.sweetbook.com/docs/concepts/template-engine/)
- [요소 그루핑](https://api.sweetbook.com/docs/concepts/element-grouping/)
- [갤러리](https://api.sweetbook.com/docs/concepts/gallery/)
- [컬럼](https://api.sweetbook.com/docs/concepts/column/)
- [베이스 레이어](https://api.sweetbook.com/docs/concepts/base-layer/)
- [텍스트 처리](https://api.sweetbook.com/docs/concepts/text-processing/)
- [특수 페이지 규칙](https://api.sweetbook.com/docs/concepts/special-page-rules/)
- [멱등성](https://api.sweetbook.com/docs/concepts/idempotency/)

### SDKs & Tools
- [SDK](https://api.sweetbook.com/docs/sdk/)
- [데모 앱](https://api.sweetbook.com/docs/demo-apps/)
- [변경 로그](https://api.sweetbook.com/docs/changelog/)

---


================================================================================
# 시작하기
================================================================================


------------------------------------------------------------
## 시작하기 > 개요
**URL**: https://api.sweetbook.com/docs/
------------------------------------------------------------

# SweetBook API 개요

SweetBook API를 사용하면 포토북 생성부터 주문, 배송까지 전 과정을 자동화할 수 있습니다.

파트너 여정:가입→Sandbox 테스트→사업 협의→가격 결정→Live 운영
## 기본 정보

| Base URL (Live) | https://api.sweetbook.com/v1 |
| --- | --- |
| Base URL (Sandbox) | https://api-sandbox.sweetbook.com/v1 |
| API 버전 | v1 |
| 응답 형식 | JSON |
| 인증 | API Key (Bearer Token) |

**모든 API 요청에는 API Key가 필요합니다.** 파트너 포털에서 API Key를 발급받아 요청 헤더에 포함하세요. 자세한 내용은 [인증 가이드](/docs/authentication/)를 참조하세요.RequestSandboxLiveCopy```
curl -X GET 'https://api-sandbox.sweetbook.com/v1/books' \
  -H "Authorization: Bearer {YOUR_API_KEY}"
```


## 표준 응답 형식

모든 API는 다음과 같은 표준 응답 형식을 사용합니다.


### 성공 응답

성공 응답에서는 `errors` 필드가 JSON에 포함되지 않습니다.ResponseCopy```
{
  "success": true,
  "message": "Success",
  "data": { ... }
}
```


### 실패 응답

요청이 실패하면 success가 false이며, errors 배열에 상세 오류 메시지가 포함됩니다.

Error responseCopy```
{
  "success": false,
  "message": "Error message",
  "data": null,
  "errors": ["세부 에러 메시지들"]
}
```


## 주요 엔드포인트


### Books (책 관리)

| 메서드 | 엔드포인트 | 설명 |
| --- | --- | --- |
| POST | /books | 책 생성 |
| GET | /books | 책 목록 조회 |
| POST | /books/{bookUid}/cover | 표지 추가 |
| POST | /books/{bookUid}/contents | 콘텐츠 추가 |
| POST | /books/{bookUid}/finalization | 책 최종화 |


### Orders (주문 관리)

| 메서드 | 엔드포인트 | 설명 |
| --- | --- | --- |
| POST | /orders | 주문 생성 |
| POST | /orders/estimate | 가격 조회 |
| GET | /orders | 주문 목록 조회 |
| GET | /orders/{orderUid} | 주문 상세 조회 |
| POST | /orders/{orderUid}/cancel | 주문 취소 |


### Templates (템플릿)

| 메서드 | 엔드포인트 | 설명 |
| --- | --- | --- |
| GET | /templates | 템플릿 목록 조회 |
| GET | /templates/{templateUid} | 템플릿 상세 조회 |
| GET | /template-categories | 템플릿 카테고리 목록 조회 |


### BookSpecs (판형)

| 메서드 | 엔드포인트 | 설명 |
| --- | --- | --- |
| GET | /book-specs | 판형 목록 조회 |
| GET | /book-specs/{bookSpecUid} | 판형 상세 조회 |


### Webhooks (웹훅)

| 메서드 | 엔드포인트 | 설명 |
| --- | --- | --- |
| PUT | /webhooks/config | 웹훅 등록/수정 |
| POST | /webhooks/test | 테스트 이벤트 전송 |


## 시작하기

[파트너 등록가입하고 Sandbox API Key를 발급받으세요.자세히 보기 →](/docs/registration/)[환경 이해하기Sandbox와 Live 환경의 차이를 알아보세요.자세히 보기 →](/docs/environments/)[빠른 시작 가이드Sandbox에서 첫 포토북을 만들어 보세요.자세히 보기 →](/docs/quickstart/)[인증 (API Key)API Key 인증 방식을 자세히 알아보세요.자세히 보기 →](/docs/authentication/)[Books API책 생성, 표지/내지 추가, 최종화 API를 확인하세요.자세히 보기 →](/docs/api/books/)[Orders API주문 생성, 가격 조회, 상태 관리 API를 확인하세요.자세히 보기 →](/docs/api/orders/)[Templates 활용 가이드템플릿 종류와 책에 적용하는 방법을 알아보세요.자세히 보기 →](/docs/api/templates/)[BookSpecs 가이드판형 종류와 선택 기준을 확인하세요.자세히 보기 →](/docs/api/book-specs/)[Webhooks 연동 가이드웹훅 설정과 이벤트 수신 서버 구현 방법을 알아보세요.자세히 보기 →](/docs/api/webhooks/)


------------------------------------------------------------
## 시작하기 > 회원가입
**URL**: https://api.sweetbook.com/docs/registration/
------------------------------------------------------------

# 파트너 등록 가이드

가입부터 Sandbox API Key 발급까지의 절차를 안내합니다. 5분이면 완료할 수 있습니다.


## 전체 흐름

1. 가입→2. 이메일 인증→3. 로그인→4. API Key 발급→5. 첫 API 호출
## Step 1. 회원가입

- 파트너 포털 가입 페이지에 접속합니다
- 이메일 주소를 입력하고 인증번호 발송을 클릭합니다
- 이메일로 수신된 인증번호를 입력합니다
- 비밀번호를 설정하고 가입을 완료합니다

가입 즉시 **Personal 계정**이 생성되며, Sandbox 환경을 사용할 수 있습니다. Live 환경은 스위트북과 사업 협의 후 사용 가능합니다.
## Step 2. 파트너 포털 로그인

- 파트너 포털 로그인 페이지에서 가입한 이메일과 비밀번호로 로그인합니다
- 로그인 후 파트너 대시보드가 표시됩니다


## Step 3. Sandbox API Key 발급

- 좌측 메뉴에서 API Key 관리를 클릭합니다
- 새 API Key 발급 버튼을 클릭합니다
- 환경에서 Sandbox를 선택합니다
- 메모(선택)를 입력하고 발급합니다
- 발급된 API Key를 복사하여 안전한 곳에 저장합니다

**API Key는 발급 시에만 전체 값을 확인할 수 있습니다.** 이후에는 접두사(prefix)만 표시됩니다. 발급 즉시 안전한 곳에 저장하세요.- 모든 API Key는 SB 접두사로 시작합니다
- 접두사와 시크릿은 .으로 구분됩니다
- 발급 개수 제한이 없으며, 필요 시 폐기 후 재발급 가능합니다
- 만료 기간 없이 폐기하지 않는 한 계속 유효합니다

API Key formatCopy```
SB{12자리 prefix}.{시크릿}
예시: SB9A1X36H2YZ.a1b2c3d4e5f6g7h8i9j0...
```


## Step 4. 첫 API 호출 테스트

발급받은 Sandbox API Key로 상품 목록을 조회해보세요.

응답이 정상적으로 돌아왔다면 연동 준비가 완료된 것입니다.
### 인증 실패 시

| 에러 | 원인 | 해결 |
| --- | --- | --- |
| 401 Unauthorized | API Key가 잘못되었거나, Sandbox Key로 Live URL에 요청 | API Key 확인, Base URL이 api-sandbox인지 확인 |
| 403 Forbidden | 폐기된 API Key 사용, 또는 IP 제한에 걸림 | 파트너 포털에서 API Key 상태 확인 |

RequestSandboxLiveCopy```
curl -X GET 'https://api-sandbox.sweetbook.com/v1/book-specs' \
  -H "Authorization: Bearer {발급받은_SANDBOX_API_KEY}"
```

ResponseCopy```
{
  "success": true,
  "message": "Success",
  "data": [
    {
      "bookSpecUid": "PHOTOBOOK_A4_SC",
      "name": "A4 소프트커버 포토북",
      "pageMin": 24,
      "pageMax": 130,
      ...
    }
  ]
}
```


## Sandbox 충전금

- 파트너 포털의 충전금 관리 메뉴에서 원하는 금액을 충전할 수 있습니다
- Sandbox 주문 시 테스트 가격(100원 이하)이 적용됩니다
- Sandbox 충전금과 Live 충전금은 완전히 분리되어 있습니다


## 다음 단계

[환경 이해하기Sandbox와 Live 환경의 차이를 알아보세요.자세히 보기 →](/docs/environments/)[빠른 시작 가이드Sandbox에서 첫 포토북을 만들어 보세요.자세히 보기 →](/docs/quickstart/)[인증 가이드API Key 인증 방식을 자세히 알아보세요.자세히 보기 →](/docs/authentication/)


------------------------------------------------------------
## 시작하기 > 환경
**URL**: https://api.sweetbook.com/docs/environments/
------------------------------------------------------------

# 환경 이해하기

SweetBook API는 Sandbox와 Live 두 가지 환경을 제공합니다. 각 환경은 완전히 분리되어 있으며, API Key와 Base URL이 다릅니다.


## API Base URL

**Sandbox와 Live의 Base URL이 다릅니다.** Sandbox API Key로 Live URL에 요청하면 인증 오류(401)가 발생합니다.| 환경 | Base URL |
| --- | --- |
| Sandbox | https://api-sandbox.sweetbook.com/v1 |
| Live | https://api.sweetbook.com/v1 |

서버는 요청 도메인을 기반으로 환경을 자동 판별합니다. 별도의 환경 파라미터가 필요하지 않습니다.

RequestCopy```
# Sandbox 환경
curl -X GET 'https://api-sandbox.sweetbook.com/v1/book-specs' \
  -H "Authorization: Bearer {SANDBOX_API_KEY}"

# Live 환경
curl -X GET 'https://api.sweetbook.com/v1/book-specs' \
  -H "Authorization: Bearer {LIVE_API_KEY}"
```


## 환경별 차이

| 항목 | Sandbox | Live |
| --- | --- | --- |
| Base URL | api-sandbox.sweetbook.com | api.sweetbook.com |
| API Key | Sandbox 전용 키 | Live 전용 키 |
| 충전금 | Sandbox 충전금 (파트너 포털에서 충전) | 실제 충전금 (결제로 충전) |
| 가격 | 테스트 가격 (100원 이하) | 협의된 실제 가격 |
| 실제 인쇄 | 하지 않음 | 실제 인쇄 진행 |
| 실제 배송 | 하지 않음 | 한진택배 배송 (3~4영업일 출고) |
| 웹훅 | 발생함 | 발생함 |
| 주문 상태 | 결제완료(PAID)에서 멈춤 | 전체 흐름 진행 |
| 데이터 | Sandbox 전용 (Live와 완전 분리) | Live 전용 |


## 계정 타입별 환경 접근

가입 시 Personal 계정이 생성되며, 사업 협의 완료 후 Business 계정으로 전환됩니다.

| 계정 타입 | Sandbox | Live | 전환 조건 |
| --- | --- | --- | --- |
| Personal | 사용 가능 | 사용 불가 | 가입 즉시 |
| Business | 사용 가능 | 사용 가능 | 스위트북과 사업 협의 완료 후 |


## Sandbox 환경 상세


### Sandbox 충전금

- 파트너 포털의 충전금 관리 메뉴에서 Sandbox 충전금을 충전할 수 있습니다
- Sandbox 충전금을 원하는 금액만큼 충전할 수 있습니다
- Sandbox 충전금과 Live 충전금은 완전히 분리되어 있습니다


### 테스트 주문

- 주문 생성 시 Sandbox 충전금이 차감됩니다
- 테스트 가격이 적용됩니다 (100원 이하)
- 주문 상태가 결제완료(PAID)에서 멈춥니다 (실제 제작/배송이 진행되지 않음)
- 웹훅 이벤트는 정상적으로 발생합니다
- 주문 취소 테스트도 가능합니다

Sandbox 환경에서 생성한 책, 주문, 웹훅 설정 등의 데이터는 Live 환경으로 이관되지 않습니다.
## Live 환경으로 전환하기

- 사업 협의 — 스위트북과 개별 협의를 진행합니다 (가격, 상품, 운영 조건 등)
- Business 계정 전환 — 협의 완료 후 계정이 Business로 전환됩니다
- Live API Key 발급 — 파트너 포털에서 Live 환경 API Key를 발급합니다
- 실제 충전금 충전 — 파트너 포털에서 결제를 통해 충전금을 충전합니다
- 코드 변경 — Base URL과 API Key만 변경하면 됩니다. API 인터페이스는 동일합니다

ConfigurationCopy```
# 변경 전 (Sandbox)
- BASE_URL=https://api-sandbox.sweetbook.com/v1
- API_KEY=SBxxxx.sandbox_key

# 변경 후 (Live)
+ BASE_URL=https://api.sweetbook.com/v1
+ API_KEY=SBxxxx.live_key
```


## 다음 단계

[파트너 등록가입하고 API Key를 발급받으세요.자세히 보기 →](/docs/registration/)[빠른 시작 가이드Sandbox에서 첫 포토북을 만들어 보세요.자세히 보기 →](/docs/quickstart/)


------------------------------------------------------------
## 시작하기 > 인증
**URL**: https://api.sweetbook.com/docs/authentication/
------------------------------------------------------------

# 인증 (API Key)

API Key를 사용하여 SweetBook API에 인증하는 방법을 설명합니다.


## 개요

SweetBook API는 API Key 기반 Bearer Token 인증을 사용합니다. 모든 API 요청에 Authorization 헤더를 포함해야 합니다.


### API Key 특징

- SB 접두사: 모든 API Key는 SB로 시작하며 .을 포함합니다
- 환경 구분: Sandbox 키와 Live 키가 분리되어 있습니다
- IP 제한: 선택적으로 허용 IP를 설정하여 보안을 강화할 수 있습니다
- 만료 없음: API Key는 폐기하지 않는 한 계속 유효합니다

Authenticated requestCopy```
Authorization: Bearer {YOUR_API_KEY}
```


## API Key 발급

API Key는 파트너 포털에서 발급받을 수 있습니다.

- 파트너 포털에 로그인합니다
- 설정 > API Key 메뉴로 이동합니다
- 새 API Key 발급 버튼을 클릭합니다
- 환경(Sandbox/Live)을 선택합니다
- 발급된 API Key를 안전하게 저장합니다

**API Key는 발급 시에만 전체 값을 확인할 수 있습니다.** 발급 후에는 접두사(prefix)만 표시되므로, 발급 즉시 안전한 곳에 저장하세요.
### 환경별 API Key

| 환경 | 용도 | 과금 |
| --- | --- | --- |
| sandbox | 개발 및 테스트 환경 | Sandbox 충전금 사용 |
| live | 프로덕션 환경 (사업 협의 후 사용 가능) | 실제 충전금 차감 |


## Sandbox 환경

환경에 따라 API Base URL이 다르며, 서버는 요청 도메인을 기반으로 자동으로 환경을 판별합니다.


### 도메인 기반 환경 분기

- Sandbox: 도메인에 sandbox가 포함되거나, localhost, 127.0.0.1인 경우
- Live: 위 조건에 해당하지 않는 모든 도메인

**Sandbox API Key는 반드시 sandbox 도메인으로 호출해야 합니다.** Live 도메인으로 호출하면 환경 불일치 에러가 발생합니다.RequestSandboxLiveCopy```
curl -X GET 'https://api-sandbox.sweetbook.com/v1/books' \
  -H "Authorization: Bearer SBxxxxxxxx.xxxxxxxxxxxxxxxx"
```


## JavaScript (fetch)

Sandbox 테스트 시에는 Base URL을 https://api-sandbox.sweetbook.com/v1로 변경하세요.

JavaScript (fetch)Copy```
const API_KEY = 'SBxxxxxxxx.xxxxxxxxxxxxxxxx';
// Sandbox: 'https://api-sandbox.sweetbook.com/v1'
const BASE_URL = 'https://api.sweetbook.com/v1';

const response = await fetch(`${BASE_URL}/books`, {
  headers: {
    'Authorization': `Bearer ${API_KEY}`
  }
});

const data = await response.json();
// { "success": true, "data": [...], "message": "Success" }
```


## JavaScript (axios)

JavaScript (axios)Copy```
import axios from 'axios';

const api = axios.create({
  baseURL: 'https://api.sweetbook.com/v1',
  headers: {
    'Authorization': 'Bearer SBxxxxxxxx.xxxxxxxxxxxxxxxx'
  }
});

const { data } = await api.get('/books');
console.log(data);
```


## Python (requests)

PythonCopy```
import requests

API_KEY = 'SBxxxxxxxx.xxxxxxxxxxxxxxxx'
BASE_URL = 'https://api.sweetbook.com/v1'

headers = {
    'Authorization': f'Bearer {API_KEY}'
}

response = requests.get(f'{BASE_URL}/books', headers=headers)
data = response.json()
print(data)
```


## 인증 에러

| 상태 코드 | 의미 | 원인 |
| --- | --- | --- |
| 401 Unauthorized | 인증 실패 | API Key가 없거나 잘못된 형식 |
| 403 Forbidden | 접근 거부 | API Key가 폐기되었거나, IP 제한에 의해 차단됨 |
| 429 Too Many Requests | 요청 제한 초과 | 단시간에 너무 많은 요청을 전송함 |

Error responseCopy```
{
  "success": false,
  "message": "Unauthorized",
  "data": null,
  "errors": ["유효하지 않은 API Key입니다."]
}
```

Error handlingCopy```
const response = await fetch('https://api.sweetbook.com/v1/books', {
  headers: { 'Authorization': `Bearer ${API_KEY}` }
});

if (!response.ok) {
  const error = await response.json();
  switch (response.status) {
    case 401: console.error('API Key가 유효하지 않습니다.'); break;
    case 403: console.error('접근이 거부되었습니다:', error.message); break;
    case 429: console.error('요청 제한을 초과했습니다.'); break;
    default:  console.error('API 에러:', error.message);
  }
}
```


## API Key 스코프

API Key 생성 시 scopes 파라미터로 해당 키의 권한 범위를 지정할 수 있습니다. 스코프를 제한하면 키가 노출되더라도 피해 범위를 최소화할 수 있습니다.


### 키 생성 시 Request Body

| 필드 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| note | string | Y | API Key 메모 |
| env | string | Y | 환경 (sandbox 또는 live) |
| allowIps | string[] | N | 허용 IP 목록 (미설정 시 모든 IP 허용) |
| scopes | string[] | N | 권한 범위 (기본값: ["*"] — 전체 권한) |


### 스코프 종류

| 스코프 | 설명 |
| --- | --- |
| * | 전체 권한 (기본값) |
| book:read | 책 목록 및 상세 조회 |
| book:write | 책 생성, 표지/내지 추가, 최종화 |
| order:read | 주문 목록 및 상세 조회 |
| order:write | 주문 생성 및 취소 |
| catalog:read | 판형(BookSpec) 및 템플릿 조회 |
| billing:read | 충전금 잔액 및 거래 내역 조회 |
| billing:write | Sandbox 충전금 충전/차감 |

요청한 작업에 필요한 스코프가 API Key에 없으면 **403 Forbidden**이 반환됩니다. 최소 권한 원칙에 따라 필요한 스코프만 부여하는 것을 권장합니다.POST /keys — 스코프를 제한한 키 생성SandboxLiveCopy```
curl -X POST 'https://api-sandbox.sweetbook.com/v1/keys' \
  -H 'Authorization: Bearer YOUR_API_KEY' \
  -H 'Content-Type: application/json' \
  -d '{
  "note": "읽기 전용 키",
  "env": "live",
  "scopes": ["book:read", "order:read"]
}'
```

스코프 부족 시 에러 응답Copy```
{
  "success": false,
  "message": "Forbidden",
  "data": null,
  "errors": ["이 작업을 수행할 권한이 없습니다."]
}
```


## API Key 보안

API Key는 SB{10자}.[{32자}] 형식입니다.

- Secret은 발급 시 1회만 표시: 생성 즉시 안전한 곳에 저장하세요.
- SHA-256 해싱: 서버에 원본 Secret을 저장하지 않습니다.
- IP 화이트리스트: allow_ips 설정으로 특정 IP만 허용 가능합니다.
- 환경 변수 사용: API Key를 코드에 직접 포함하지 마세요.
- 클라이언트 측 노출 금지: 반드시 서버 사이드에서만 호출하세요.

Rate Limiting에 대한 자세한 내용은 [Rate Limiting 가이드](/docs/guides/rate-limiting/)를 참고하세요..envCopy```
# .env
SWEETBOOK_API_KEY=SBxxxxxxxx.xxxxxxxxxxxxxxxx
```

Node.jsCopy```
// Node.js에서 환경 변수 사용
const API_KEY = process.env.SWEETBOOK_API_KEY;

const response = await fetch('https://api.sweetbook.com/v1/books', {
  headers: {
    'Authorization': `Bearer ${API_KEY}`
  }
});
```


## FAQ

QSandbox 키와 Live 키의 차이는 무엇인가요?ASandbox 키로 생성한 책과 주문은 실제 인쇄되지 않으며 과금되지 않습니다.QAPI Key가 노출되면 어떻게 하나요?A즉시 파트너 포털에서 해당 API Key를 폐기하고 새로운 키를 발급받으세요.QPostman에서 테스트하려면 어떻게 하나요?AAuthorization 탭에서 Type을 Bearer Token으로 선택하고 API Key를 입력하세요.


------------------------------------------------------------
## 시작하기 > 퀵스타트
**URL**: https://api.sweetbook.com/docs/quickstart/
------------------------------------------------------------

# 빠른 시작 가이드

Sandbox 환경에서 첫 포토북 생성부터 주문까지 완료하기


## 사전 준비

- Sandbox API Key: 파트너 등록을 완료하고 Sandbox API Key를 발급받으세요
- Sandbox 충전금: 파트너 포털의 충전금 관리에서 Sandbox 충전금을 충전하세요
- 이미지 파일: 표지용 2장(front.jpg, back.jpg), 내지용 15장 이상
- API 테스트 도구: curl, Postman 등

모든 API 호출은 Sandbox URL `https://api-sandbox.sweetbook.com/v1`을 사용합니다. 테스트 가격(100원 이하)이 적용되며, 실제 인쇄/배송은 진행되지 않습니다.아래 예시에서 YOUR_API_KEY를 발급받은 Sandbox API Key로 교체하세요. 소요 시간: 약 10분


## Step 1. 판형(BookSpec) 조회

먼저 사용 가능한 판형 목록을 조회합니다.

이 가이드에서는 `SQUAREBOOK_HC`를 사용합니다. 응답에서 원하는 `specUid`를 선택하세요.RequestSandboxLiveCopy```
curl -X GET 'https://api-sandbox.sweetbook.com/v1/book-specs' \
  -H 'Authorization: Bearer YOUR_API_KEY'
```


## Step 2. 템플릿 조회

표지와 내지에 사용할 템플릿을 조회합니다.

응답에서 표지용(templateKind: cover)과 내지용(templateKind: content) 템플릿의 templateUid를 메모하세요.

RequestSandboxLiveCopy```
curl -X GET 'https://api-sandbox.sweetbook.com/v1/templates?bookSpecUid=SQUAREBOOK_HC' \
  -H 'Authorization: Bearer YOUR_API_KEY'
```


## Step 3. 책 생성

제목과 판형을 지정하여 책 객체를 생성합니다.

응답의 `bookUid`를 복사해두세요. 이후 모든 단계에서 사용됩니다.RequestSandboxLiveCopy```
curl -X POST 'https://api-sandbox.sweetbook.com/v1/books' \
  -H 'Authorization: Bearer YOUR_API_KEY' \
  -H 'Content-Type: application/json' \
  -d '{
  "title": "나의 첫 포토북",
  "bookSpecUid": "SQUAREBOOK_HC"
}'
```


## Step 4. 표지 추가

앞표지(frontPhoto)와 뒷표지(backPhoto) 이미지와 템플릿을 지정합니다.

`{bookUid}`와 `COVER_TEMPLATE_UID`를 실제 값으로 교체하세요.RequestSandboxLiveCopy```
curl -X POST \
  'https://api-sandbox.sweetbook.com/v1/books/{bookUid}/cover' \
  -H 'Authorization: Bearer YOUR_API_KEY' \
  -H 'Content-Type: multipart/form-data' \
  -F 'frontPhoto=@front.jpg;type=image/jpeg' \
  -F 'backPhoto=@back.jpg;type=image/jpeg' \
  -F 'templateUid=COVER_TEMPLATE_UID' \
  -F 'parameters={"title":"나의 첫 포토북","author":"홍길동"}'
```


## Step 5. 내지 추가 (반복)

최소 페이지 수(SQUAREBOOK_HC: 24페이지)를 충족할 때까지 반복하세요.

지원 이미지: JPG, PNG, GIF, BMP, WebP, HEIC (SVG 미지원)

RequestSandboxLiveCopy```
# 여러 페이지를 빠르게 추가
for i in {1..15}; do
  curl -X POST \
    'https://api-sandbox.sweetbook.com/v1/books/{bookUid}/contents?breakBefore=page' \
    -H 'Authorization: Bearer YOUR_API_KEY' \
    -H 'Content-Type: multipart/form-data' \
    -F "files=@photo${i}.jpg;type=image/jpeg" \
    -F 'templateUid=CONTENT_TEMPLATE_UID'
done
```


## Step 6. 책 최종화

모든 콘텐츠 추가가 완료되면 책을 최종화합니다. 이후에는 내용을 변경할 수 없습니다.

RequestSandboxLiveCopy```
curl -X POST \
  'https://api-sandbox.sweetbook.com/v1/books/{bookUid}/finalization' \
  -H 'Authorization: Bearer YOUR_API_KEY'
```


## Step 7. 견적 조회

Sandbox에서는 테스트 가격(100원 이하)이 적용됩니다.

`creditSufficient`가 `false`이면 파트너 포털에서 Sandbox 충전금을 충전하세요.RequestSandboxLiveCopy```
curl -X POST 'https://api-sandbox.sweetbook.com/v1/orders/estimate' \
  -H 'Authorization: Bearer YOUR_API_KEY' \
  -H 'Content-Type: application/json' \
  -d '{
  "items": [
    { "bookUid": "{bookUid}", "quantity": 1 }
  ]
}'
```


## Step 8. 주문 생성

주문 즉시 Sandbox 충전금이 차감되며, order.paid 웹훅 이벤트가 발생합니다.

Sandbox에서는 주문 상태가 **PAID(결제완료)**에서 멈춥니다. 실제 인쇄/배송은 진행되지 않습니다.RequestSandboxLiveCopy```
curl -X POST 'https://api-sandbox.sweetbook.com/v1/orders' \
  -H 'Authorization: Bearer YOUR_API_KEY' \
  -H 'Content-Type: application/json' \
  -d '{
  "items": [
    { "bookUid": "{bookUid}", "quantity": 1 }
  ],
  "shipping": {
    "recipientName": "홍길동",
    "recipientPhone": "010-1234-5678",
    "postalCode": "06236",
    "address1": "서울특별시 강남구 테헤란로 123",
    "address2": "4층"
  }
}'
```


## 완료!

전체 흐름을 완료했습니다. Live 환경으로 전환할 때는 Base URL과 API Key만 변경하면 됩니다.

[웹훅 연동주문 상태 변경을 실시간 수신자세히 보기 →](/docs/api/webhooks/)[Orders API주문 조회, 취소, 배송지 변경자세히 보기 →](/docs/api/orders/)[Live 전환운영 환경으로 전환하기자세히 보기 →](/docs/environments/)
## 문제 해결

| 에러 | 원인 | 해결 |
| --- | --- | --- |
| 401 Unauthorized | API Key 오류 또는 Sandbox Key로 Live URL 호출 | API Key 확인, URL이 api-sandbox인지 확인 |
| 402 Payment Required | Sandbox 충전금 부족 | 파트너 포털에서 Sandbox 충전금 충전 |
| 최소 페이지 수 부족 | 판형의 최소 페이지 미충족 | Step 5에서 더 많은 내지 추가 |
| Template not found | 잘못된 템플릿 UID | Step 2에서 조회한 정확한 templateUid 사용 |
| 이미지 업로드 실패 | 미지원 형식(SVG 등) | JPG, PNG, WebP, HEIC 등 지원 형식 사용 |


================================================================================
# 통합 가이드
================================================================================


------------------------------------------------------------
## 통합 가이드 > 워크플로우
**URL**: https://api.sweetbook.com/docs/guides/workflow/
------------------------------------------------------------

# 전체 워크플로우

SweetBook API를 사용하여 포토북을 제작하고 주문하는 전체 과정을 안내합니다. 각 단계별 API 엔드포인트와 연동 시나리오를 설명합니다.


## 전체 흐름

포토북 제작부터 주문 완료까지 다음 단계를 순서대로 진행합니다.

1판형 선택→2템플릿 선택→3책 생성→4사진 업로드→5표지 추가→6내지 추가 (반복)→7최종화→8견적 조회→9주문 생성→10웹훅 수신
## 단계별 API 엔드포인트

각 단계에서 호출하는 API 엔드포인트와 역할입니다.

| 단계 | API 엔드포인트 | 설명 |
| --- | --- | --- |
| 1. 판형 선택 | GET /book-specs | 사용 가능한 판형 목록 조회 |
| 2. 템플릿 선택 | GET /templates | 판형에 맞는 표지/내지 템플릿 조회 |
| 3. 책 생성 | POST /books | 초안(draft) 상태의 책 생성 |
| 4. 사진 업로드 | POST /books/{bookUid}/photos | 갤러리 템플릿에 사용할 사진 업로드 |
| 5. 표지 추가 | POST /books/{bookUid}/cover | 표지 템플릿 적용 및 파라미터 전달 |
| 6. 내지 추가 | POST /books/{bookUid}/contents | 내지 템플릿 적용 (반복 호출 가능) |
| 7. 최종화 | POST /books/{bookUid}/finalization | 책 완성 처리 (페이지 수 검증) |
| 8. 견적 조회 | POST /orders/estimate | 주문 전 예상 비용 확인 |
| 9. 주문 생성 | POST /orders | 주문 생성 및 충전금 차감 |
| 10. 웹훅 수신 | Webhook | 주문 상태 변경 알림 수신 |


## 시나리오 A: 사용자 선택형 (앨범 앱)

사용자가 직접 템플릿을 선택하고 사진을 업로드하여 포토북을 만드는 시나리오입니다. 앨범 앱, 사진 편집 앱 등에 적합합니다.

판형 목록과 템플릿 목록은 자주 변경되지 않으므로 캐시하여 사용하는 것을 권장합니다.SweetBook API파트너 서버사용자 앱 UI#mermaid-4whvsr6{font-family:'Pretendard',-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;font-size:13px;fill:#1E293B;}@keyframes edge-animation-frame{from{stroke-dashoffset:0;}}@keyframes dash{to{stroke-dashoffset:0;}}#mermaid-4whvsr6 .edge-animation-slow{stroke-dasharray:9,5!important;stroke-dashoffset:900;animation:dash 50s linear infinite;stroke-linecap:round;}#mermaid-4whvsr6 .edge-animation-fast{stroke-dasharray:9,5!important;stroke-dashoffset:900;animation:dash 20s linear infinite;stroke-linecap:round;}#mermaid-4whvsr6 .error-icon{fill:hsl(30, 100%, 100%);}#mermaid-4whvsr6 .error-text{fill:#000000;stroke:#000000;}#mermaid-4whvsr6 .edge-thickness-normal{stroke-width:1px;}#mermaid-4whvsr6 .edge-thickness-thick{stroke-width:3.5px;}#mermaid-4whvsr6 .edge-pattern-solid{stroke-dasharray:0;}#mermaid-4whvsr6 .edge-thickness-invisible{stroke-width:0;fill:none;}#mermaid-4whvsr6 .edge-pattern-dashed{stroke-dasharray:3;}#mermaid-4whvsr6 .edge-pattern-dotted{stroke-dasharray:2;}#mermaid-4whvsr6 .marker{fill:#94A3B8;stroke:#94A3B8;}#mermaid-4whvsr6 .marker.cross{stroke:#94A3B8;}#mermaid-4whvsr6 svg{font-family:'Pretendard',-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;font-size:13px;}#mermaid-4whvsr6 p{margin:0;}#mermaid-4whvsr6 .actor{stroke:#CBD5E1;fill:#F8FAFC;}#mermaid-4whvsr6 text.actor>tspan{fill:#1E293B;stroke:none;}#mermaid-4whvsr6 .actor-line{stroke:#CBD5E1;}#mermaid-4whvsr6 .innerArc{stroke-width:1.5;stroke-dasharray:none;}#mermaid-4whvsr6 .messageLine0{stroke-width:1.5;stroke-dasharray:none;stroke:#94A3B8;}#mermaid-4whvsr6 .messageLine1{stroke-width:1.5;stroke-dasharray:2,2;stroke:#94A3B8;}#mermaid-4whvsr6 #arrowhead path{fill:#94A3B8;stroke:#94A3B8;}#mermaid-4whvsr6 .sequenceNumber{fill:#FFFFFF;}#mermaid-4whvsr6 #sequencenumber{fill:#94A3B8;}#mermaid-4whvsr6 #crosshead path{fill:#94A3B8;stroke:#94A3B8;}#mermaid-4whvsr6 .messageText{fill:#1E293B;stroke:none;}#mermaid-4whvsr6 .labelBox{stroke:#CBD5E1;fill:#F8FAFC;}#mermaid-4whvsr6 .labelText,#mermaid-4whvsr6 .labelText>tspan{fill:#1E293B;stroke:none;}#mermaid-4whvsr6 .loopText,#mermaid-4whvsr6 .loopText>tspan{fill:#1E293B;stroke:none;}#mermaid-4whvsr6 .loopLine{stroke-width:2px;stroke-dasharray:2,2;stroke:#CBD5E1;fill:#CBD5E1;}#mermaid-4whvsr6 .note{stroke:#86EFAC;fill:#F0FDF4;}#mermaid-4whvsr6 .noteText,#mermaid-4whvsr6 .noteText>tspan{fill:#166534;stroke:none;}#mermaid-4whvsr6 .activation0{fill:hsl(90, 100%, 96.0784313725%);stroke:hsl(90, 100%, 86.0784313725%);}#mermaid-4whvsr6 .activation1{fill:hsl(90, 100%, 96.0784313725%);stroke:hsl(90, 100%, 86.0784313725%);}#mermaid-4whvsr6 .activation2{fill:hsl(90, 100%, 96.0784313725%);stroke:hsl(90, 100%, 86.0784313725%);}#mermaid-4whvsr6 .actorPopupMenu{position:absolute;}#mermaid-4whvsr6 .actorPopupMenuPanel{position:absolute;fill:#F8FAFC;box-shadow:0px 8px 16px 0px rgba(0,0,0,0.2);filter:drop-shadow(3px 5px 2px rgb(0 0 0 / 0.4));}#mermaid-4whvsr6 .actor-man line{stroke:#CBD5E1;fill:#F8FAFC;}#mermaid-4whvsr6 .actor-man circle,#mermaid-4whvsr6 line{stroke:#CBD5E1;fill:#F8FAFC;stroke-width:2px;}#mermaid-4whvsr6 :root{--mermaid-font-family:"trebuchet ms",verdana,arial,sans-serif;}판형 목록 요청1GET /book-specs2판형 목록 응답3판형 목록 표시4템플릿 선택5GET /templates?bookSpecUid=..6템플릿 목록 응답7템플릿 목록 표시8사진 선택 + 주문 요청9POST /books10POST /books/{id}/photos11POST /books/{id}/cover12POST /books/{id}/contents (반복)13POST /books/{id}/finalization14POST /orders15주문 응답16주문 완료17- 사용자 앱 → 파트너 서버: 판형 목록 요청
- 파트너 서버 → API: GET /book-specs
- API → 파트너 서버: 판형 목록 응답
- 파트너 서버 → 사용자 앱: 판형 목록 표시
- 사용자 앱 → 파트너 서버: 템플릿 선택
- 파트너 서버 → API: GET /templates?bookSpecUid=..
- API → 파트너 서버: 템플릿 목록 응답
- 파트너 서버 → 사용자 앱: 템플릿 목록 표시
- 사용자 앱 → 파트너 서버: 사진 선택 + 주문 요청
- 파트너 서버 → API: POST /books
- 파트너 서버 → API: POST /books/{id}/photos
- 파트너 서버 → API: POST /books/{id}/cover
- 파트너 서버 → API: POST /books/{id}/contents (반복)
- 파트너 서버 → API: POST /books/{id}/finalization
- 파트너 서버 → API: POST /orders
- API → 파트너 서버: 주문 응답
- 파트너 서버 → 사용자 앱: 주문 완료


## 시나리오 B: 서버 자동 생성형 (일기장/알림장 앱)

서버가 데이터(일기, 알림장 등)를 기반으로 자동으로 포토북을 생성하는 시나리오입니다. 사용자는 기간만 선택하면 서버가 나머지를 처리합니다.

서버 자동 생성 시나리오에서는 템플릿 `templateUid`와 파라미터 매핑을 서버에 미리 설정해 두는 것이 일반적입니다.SweetBook API파트너 서버사용자 앱 UI#mermaid-7mlvbmp{font-family:'Pretendard',-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;font-size:13px;fill:#1E293B;}@keyframes edge-animation-frame{from{stroke-dashoffset:0;}}@keyframes dash{to{stroke-dashoffset:0;}}#mermaid-7mlvbmp .edge-animation-slow{stroke-dasharray:9,5!important;stroke-dashoffset:900;animation:dash 50s linear infinite;stroke-linecap:round;}#mermaid-7mlvbmp .edge-animation-fast{stroke-dasharray:9,5!important;stroke-dashoffset:900;animation:dash 20s linear infinite;stroke-linecap:round;}#mermaid-7mlvbmp .error-icon{fill:hsl(30, 100%, 100%);}#mermaid-7mlvbmp .error-text{fill:#000000;stroke:#000000;}#mermaid-7mlvbmp .edge-thickness-normal{stroke-width:1px;}#mermaid-7mlvbmp .edge-thickness-thick{stroke-width:3.5px;}#mermaid-7mlvbmp .edge-pattern-solid{stroke-dasharray:0;}#mermaid-7mlvbmp .edge-thickness-invisible{stroke-width:0;fill:none;}#mermaid-7mlvbmp .edge-pattern-dashed{stroke-dasharray:3;}#mermaid-7mlvbmp .edge-pattern-dotted{stroke-dasharray:2;}#mermaid-7mlvbmp .marker{fill:#94A3B8;stroke:#94A3B8;}#mermaid-7mlvbmp .marker.cross{stroke:#94A3B8;}#mermaid-7mlvbmp svg{font-family:'Pretendard',-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;font-size:13px;}#mermaid-7mlvbmp p{margin:0;}#mermaid-7mlvbmp .actor{stroke:#CBD5E1;fill:#F8FAFC;}#mermaid-7mlvbmp text.actor>tspan{fill:#1E293B;stroke:none;}#mermaid-7mlvbmp .actor-line{stroke:#CBD5E1;}#mermaid-7mlvbmp .innerArc{stroke-width:1.5;stroke-dasharray:none;}#mermaid-7mlvbmp .messageLine0{stroke-width:1.5;stroke-dasharray:none;stroke:#94A3B8;}#mermaid-7mlvbmp .messageLine1{stroke-width:1.5;stroke-dasharray:2,2;stroke:#94A3B8;}#mermaid-7mlvbmp #arrowhead path{fill:#94A3B8;stroke:#94A3B8;}#mermaid-7mlvbmp .sequenceNumber{fill:#FFFFFF;}#mermaid-7mlvbmp #sequencenumber{fill:#94A3B8;}#mermaid-7mlvbmp #crosshead path{fill:#94A3B8;stroke:#94A3B8;}#mermaid-7mlvbmp .messageText{fill:#1E293B;stroke:none;}#mermaid-7mlvbmp .labelBox{stroke:#CBD5E1;fill:#F8FAFC;}#mermaid-7mlvbmp .labelText,#mermaid-7mlvbmp .labelText>tspan{fill:#1E293B;stroke:none;}#mermaid-7mlvbmp .loopText,#mermaid-7mlvbmp .loopText>tspan{fill:#1E293B;stroke:none;}#mermaid-7mlvbmp .loopLine{stroke-width:2px;stroke-dasharray:2,2;stroke:#CBD5E1;fill:#CBD5E1;}#mermaid-7mlvbmp .note{stroke:#86EFAC;fill:#F0FDF4;}#mermaid-7mlvbmp .noteText,#mermaid-7mlvbmp .noteText>tspan{fill:#166534;stroke:none;}#mermaid-7mlvbmp .activation0{fill:hsl(90, 100%, 96.0784313725%);stroke:hsl(90, 100%, 86.0784313725%);}#mermaid-7mlvbmp .activation1{fill:hsl(90, 100%, 96.0784313725%);stroke:hsl(90, 100%, 86.0784313725%);}#mermaid-7mlvbmp .activation2{fill:hsl(90, 100%, 96.0784313725%);stroke:hsl(90, 100%, 86.0784313725%);}#mermaid-7mlvbmp .actorPopupMenu{position:absolute;}#mermaid-7mlvbmp .actorPopupMenuPanel{position:absolute;fill:#F8FAFC;box-shadow:0px 8px 16px 0px rgba(0,0,0,0.2);filter:drop-shadow(3px 5px 2px rgb(0 0 0 / 0.4));}#mermaid-7mlvbmp .actor-man line{stroke:#CBD5E1;fill:#F8FAFC;}#mermaid-7mlvbmp .actor-man circle,#mermaid-7mlvbmp line{stroke:#CBD5E1;fill:#F8FAFC;stroke-width:2px;}#mermaid-7mlvbmp :root{--mermaid-font-family:"trebuchet ms",verdana,arial,sans-serif;}loop[일기 데이터마다 반복]"3월 일기장 만들기" 요청1DB에서 3월 일기 데이터 조회2POST /books3POST /books/{id}/photos4POST /books/{id}/cover5POST /books/{id}/contents6POST /books/{id}/finalization7POST /orders/estimate8견적 응답9견적 표시 + 결제 확인10결제 확인11POST /orders12주문 응답13주문 완료14- 사용자 앱 → 파트너 서버: "3월 일기장 만들기" 요청
- 파트너 서버: DB에서 3월 일기 데이터 조회
- 파트너 서버 → API: POST /books
- 파트너 서버 → API: POST /books/{id}/photos
- 파트너 서버 → API: POST /books/{id}/cover
- 파트너 서버 → API: POST /books/{id}/contents (일기 데이터마다 반복)
- 파트너 서버 → API: POST /books/{id}/finalization
- 파트너 서버 → API: POST /orders/estimate
- API → 파트너 서버: 견적 응답
- 파트너 서버 → 사용자 앱: 견적 표시 + 결제 확인
- 사용자 앱 → 파트너 서버: 결제 확인
- 파트너 서버 → API: POST /orders
- API → 파트너 서버: 주문 응답
- 파트너 서버 → 사용자 앱: 주문 완료


## 단계별 상세 가이드

각 단계의 자세한 사용법은 아래 가이드를 참고하세요.

- Step 1: 판형(BookSpec) 선택 — 판형 조회 및 선택
- Step 2: 템플릿 선택 및 이해 — 템플릿 조회 및 파라미터 바인딩
- Step 3: 책 생성 — Books API로 책 생성
- Step 4: 이미지 업로드 — 지원 포맷 및 업로드 가이드
- Step 5~7: 표지/내지 추가 및 최종화 — Books API 상세
- Step 8~9: 견적 조회 및 주문 — Orders API
- Step 10: 웹훅 수신 — Webhook 설정 및 이벤트


## 관련 문서

- 인증 — API Key 발급 및 인증 방법
- 환경 — Sandbox / Live 환경 안내
- 충전금 시스템 — 충전금 관리 및 비용 계산
- 빠른 시작 — 5분만에 첫 포토북 만들기


------------------------------------------------------------
## 통합 가이드 > 판형
**URL**: https://api.sweetbook.com/docs/guides/book-specs/
------------------------------------------------------------

# 판형 선택 가이드

포토북 제작의 첫 단계는 판형을 선택하는 것입니다. 판형에 따라 사용 가능한 템플릿, 페이지 범위, 제본 방식이 결정됩니다.


## 개요

BookSpec은 포토북의 물리적 사양을 정의합니다. 판형 크기, 제본 방식, 표지 유형, 페이지 범위 등의 정보를 포함하며, 책을 생성할 때 반드시 하나의 BookSpec을 지정해야 합니다.

BookSpec을 선택하면 이후 단계에서 해당 스펙에 호환되는 템플릿만 사용할 수 있습니다.
## 판형 목록 조회

GET /book-specs로 사용 가능한 전체 판형 목록을 조회합니다.

RequestSandboxLiveCopy```
curl 'https://api-sandbox.sweetbook.com/v1/book-specs' \
  -H 'Authorization: Bearer YOUR_API_KEY'
```

ResponseCopy```
{
  "success": true,
  "message": "Success",
  "data": {
    "items": [
      {
        "bookSpecUid": "PHOTOBOOK_A4_SC",
        "name": "A4 소프트커버 포토북",
        "innerTrimWidthMm": 210,
        "innerTrimHeightMm": 297,
        "coverType": "Softcover",
        "bindingType": "PUR",
        "pageMin": 24,
        "pageMax": 130,
        "pageIncrement": 2
      },
      {
        "bookSpecUid": "PHOTOBOOK_A5_SC",
        "name": "A5 소프트커버 포토북",
        "innerTrimWidthMm": 148,
        "innerTrimHeightMm": 210,
        "coverType": "Softcover",
        "bindingType": "PUR",
        "pageMin": 50,
        "pageMax": 200,
        "pageIncrement": 2
      },
      {
        "bookSpecUid": "SQUAREBOOK_HC",
        "name": "고화질 스퀘어북 (하드커버)",
        "innerTrimWidthMm": 243,
        "innerTrimHeightMm": 248,
        "coverType": "Hardcover",
        "bindingType": "PUR",
        "pageMin": 24,
        "pageMax": 130,
        "pageIncrement": 2
      }
    ]
  }
}
```


## 상세 조회

GET /book-specs/{specUid}로 특정 판형의 상세 정보를 조회합니다. 가격 정보와 레이아웃 크기 등 추가 정보가 포함됩니다.

RequestSandboxLiveCopy```
curl 'https://api-sandbox.sweetbook.com/v1/book-specs/SQUAREBOOK_HC' \
  -H 'Authorization: Bearer YOUR_API_KEY'
```


## 주요 필드 설명

| 필드 | 타입 | 설명 |
| --- | --- | --- |
| bookSpecUid | string | 판형 고유 식별자. 책 생성 시 이 값을 사용합니다. |
| name | string | 판형명 (예: A4 소프트커버 포토북, 고화질 스퀘어북) |
| innerTrimWidthMm / innerTrimHeightMm | number | 내지 크기 (mm 단위) |
| pageMin / pageMax | number | 허용 페이지 범위. 최종화 시 이 범위 내여야 합니다. |
| pageIncrement | number | 페이지 증가 단위 (예: 2페이지씩 증가) |
| coverType | string | 표지 유형 (Softcover, Hardcover) |
| bindingType | string | 제본 방식 (PUR) |
| priceBase | number | 기본 가격 (최소 페이지 기준) |
| pricePerIncrement | number | 페이지 증가당 추가 가격 |
| layoutSize | object | 레이아웃 작업 영역 크기 (표지/내지 width, height) |


## 가격 안내

**Sandbox 환경:** 테스트용 가격(100원 미만)이 적용됩니다. 실제 서비스 가격과 다릅니다.**Live 환경:** 실제 가격은 SweetBook과의 개별 협의를 통해 결정됩니다. 영업팀에 문의해 주세요.
## 용도별 선택 가이드

서비스 특성에 맞는 판형을 선택하세요.

| 용도 | 추천 판형 | 이유 |
| --- | --- | --- |
| 일기장 / 알림장 | SQUAREBOOK_HC | 최대 130페이지로 한 달치 일기를 충분히 담을 수 있음 |
| 문서 / 포트폴리오 | PHOTOBOOK_A4_SC | A4 규격으로 문서, 작품집 등에 적합 |
| 대량 사진 앨범 | PHOTOBOOK_A5_SC | 최대 200페이지로 많은 사진을 담을 수 있음 |
| 고급 포토북 / 선물용 | SQUAREBOOK_HC | 하드커버로 고급스러운 마감 |
| 졸업앨범 / 범용 | SQUAREBOOK_HC | 정사각 판형으로 다양한 레이아웃 활용 가능 |


## 다음 단계

- Step 2: 템플릿 선택 및 이해 — 선택한 판형에 맞는 템플릿 조회
- 전체 워크플로우 — 전체 연동 흐름 보기
- BookSpecs API 레퍼런스 — 판형 상세 API 문서


------------------------------------------------------------
## 통합 가이드 > 템플릿
**URL**: https://api.sweetbook.com/docs/guides/templates/
------------------------------------------------------------

# 템플릿 선택 가이드

선택한 판형(BookSpec)에 맞는 템플릿을 조회하고, 파라미터 바인딩 방식을 이해하는 단계입니다. 템플릿의 종류, 파라미터 구조, 갤러리/컬럼 템플릿 사용법을 안내합니다.


## 템플릿 목록 조회

GET /templates로 사용 가능한 템플릿을 조회합니다. 반드시 bookSpecUid를 지정하여 해당 판형에 호환되는 템플릿만 필터링하세요.

| Query Parameter | 필수 | 설명 |
| --- | --- | --- |
| bookSpecUid | 권장 | 판형 UID로 필터링 (예: SQUAREBOOK_HC) |
| templateKind | 권장 | cover (표지) 또는 content (내지) |
| category | 선택 | 카테고리 필터 (예: diary, album, wedding) |
| limit, offset | 선택 | 페이지네이션 (기본 limit: 50) |

RequestSandboxLiveCopy```
# SQUAREBOOK_HC용 표지 템플릿 조회
curl 'https://api-sandbox.sweetbook.com/v1/templates?bookSpecUid=SQUAREBOOK_HC&templateKind=cover' \
  -H 'Authorization: Bearer YOUR_API_KEY'
```

RequestSandboxLiveCopy```
# SQUAREBOOK_HC용 내지 템플릿 조회
curl 'https://api-sandbox.sweetbook.com/v1/templates?bookSpecUid=SQUAREBOOK_HC&templateKind=content' \
  -H 'Authorization: Bearer YOUR_API_KEY'
```


## 템플릿 종류: cover vs content

템플릿은 templateKind로 구분됩니다.

| 종류 | 값 | 용도 | 적용 API |
| --- | --- | --- | --- |
| 표지 템플릿 | cover | 책 표지 디자인. 책당 하나만 적용됩니다. | POST /books/{bookUid}/cover |
| 내지 템플릿 | content | 내지 페이지 디자인. 여러 번 적용 가능합니다. | POST /books/{bookUid}/contents |

표지에 내지 템플릿을 사용하거나, 내지에 표지 템플릿을 사용할 수 없습니다. 반드시 종류를 일치시키세요.
## 템플릿 상세 조회

GET /templates/{templateUid}로 특정 템플릿의 상세 정보를 확인합니다. 파라미터 정의, 레이아웃, 베이스 레이어 등이 포함됩니다.

| 응답 필드 | 설명 |
| --- | --- |
| parameters | 파라미터 정의 목록 (텍스트, 이미지, 갤러리 바인딩 정보) |
| layout | 레이아웃 정의 (요소 배치, 크기) |
| layoutRules | 레이아웃 규칙 (여백, 흐름, 컬럼 등) |
| baseLayer | 베이스 레이어 (홀수/짝수 페이지 배경) |
| thumbnails | 썸네일 URL (레이아웃, 베이스 레이어) |

RequestSandboxLiveCopy```
curl 'https://api-sandbox.sweetbook.com/v1/templates/8hKvbcNJdSgj' \
  -H 'Authorization: Bearer YOUR_API_KEY'
```


## 파라미터 바인딩

템플릿의 parameters에 정의된 바인딩 유형에 따라 값을 전달합니다. 파라미터 이름은 $$이름$$ 형식으로 템플릿 내에서 참조됩니다.


### 텍스트 바인딩

템플릿 내 $$title$$, $$date$$ 등의 텍스트 플레이스홀더에 문자열 값을 전달합니다.

Request bodyCopy```
{
  "templateUid": "COVER_TEMPLATE_UID",
  "parameters": {
    "bookTitle": "우리 가족 앨범",
    "year": "2026"
  }
}
```


### 사진(file) 바인딩

$$photo1$$ 등의 이미지 플레이스홀더에 업로드된 사진의 fileName이나 URL을 전달합니다.

Request bodyCopy```
{
  "templateUid": "CONTENT_TEMPLATE_UID",
  "parameters": {
    "photo1": "uploaded_photo_abc123.jpg"
  }
}
```


### 갤러리(rowGallery) 바인딩

$$galleryPhotos$$ 등의 갤러리 플레이스홀더에 사진 파일명 배열을 전달합니다. 갤러리 템플릿은 전달된 사진 수에 따라 레이아웃이 동적으로 배치됩니다.

갤러리 바인딩에 사용할 사진은 먼저 `POST /books/{bookUid}/photos`로 업로드한 후, 반환된 `fileName`을 사용합니다.Request bodyCopy```
{
  "templateUid": "GALLERY_TEMPLATE_UID",
  "parameters": {
    "galleryPhotos": ["photo1.jpg", "photo2.jpg", "photo3.jpg", "photo4.jpg"]
  }
}
```


## 템플릿 선택 기준

템플릿을 선택할 때 다음 사항을 확인하세요.

- bookSpecUid 일치: 템플릿의 bookSpecUid가 생성한 책의 bookSpecUid와 일치해야 합니다.
- templateKind 확인: 표지에는 cover, 내지에는 content 템플릿을 사용하세요.
- 파라미터 확인: 상세 조회로 parameters를 확인하여 어떤 값을 전달해야 하는지 파악하세요.
- 카테고리 활용: 서비스 용도에 맞는 카테고리로 필터링하면 적합한 템플릿을 빠르게 찾을 수 있습니다.


## 갤러리 템플릿 사용법

갤러리 템플릿은 전달된 사진 수에 따라 레이아웃이 자동으로 배치됩니다. 사진이 많으면 여러 페이지에 걸쳐 자동 분배되므로, 한 번의 API 호출로 다수의 사진을 효율적으로 배치할 수 있습니다.

갤러리 템플릿의 동작 원리와 레이아웃 배치 규칙은 [Gallery Templates](/docs/concepts/gallery/) 문서를 참고하세요.RequestSandboxLiveCopy```
curl -X POST 'https://api-sandbox.sweetbook.com/v1/books/{bookUid}/contents' \
  -H 'Authorization: Bearer YOUR_API_KEY' \
  -H 'Content-Type: application/json' \
  -d '{
  "templateUid": "GALLERY_TEMPLATE_UID",
  "parameters": {
    "galleryPhotos": [
      "photo1.jpg", "photo2.jpg", "photo3.jpg",
      "photo4.jpg", "photo5.jpg", "photo6.jpg"
    ]
  }
}'
```


## 컬럼 템플릿 사용법

컬럼 템플릿은 텍스트와 사진을 세로 방향으로 쌓아 배치합니다. 일기장, 알림장처럼 텍스트 분량이 가변적인 콘텐츠에 적합합니다. 텍스트 길이에 따라 레이아웃이 자동으로 조정됩니다.

컬럼 레이아웃의 상세 동작은 [Column Layout](/docs/concepts/column/) 문서를 참고하세요.
## 다음 단계

- Step 3: 책 생성 — Books API로 책 생성하기
- Step 4: 이미지 업로드 — 지원 포맷 및 업로드 가이드
- Step 1: 판형 선택 — 이전 단계로 돌아가기
- 전체 워크플로우 — 전체 연동 흐름 보기
- Templates API 레퍼런스 — 상세 API 문서


------------------------------------------------------------
## 통합 가이드 > 책
**URL**: https://api.sweetbook.com/docs/guides/books/
------------------------------------------------------------

# 책 생성 가이드

책을 생성하고, 표지와 내지를 추가한 후 최종화하는 전체 과정을 안내합니다.


## 책 생성

POST /books로 새 책을 생성합니다. title과 bookSpecUid는 필수이며, 선택적으로 bookAuthor, specProfileUid, externalRef를 지정할 수 있습니다.

| 파라미터 | 필수 | 설명 |
| --- | --- | --- |
| title | O | 책 제목 |
| bookSpecUid | O | 판형 UID (GET /book-specs에서 조회) |
| bookAuthor |  | 저자명 |
| specProfileUid |  | 사양 프로필 UID |
| externalRef |  | 파트너 시스템의 내부 ID (매핑용) |

**Sandbox 환경:** Sandbox에서는 `creationType`이 자동으로 `TEST`로 설정됩니다. 별도로 지정할 필요가 없습니다.RequestSandboxLiveCopy```
curl -X POST 'https://api-sandbox.sweetbook.com/v1/books' \
  -H 'Authorization: Bearer YOUR_API_KEY' \
  -H 'Content-Type: application/json' \
  -d '{
  "title": "나의 첫 포토북",
  "bookSpecUid": "SQUAREBOOK_HC",
  "bookAuthor": "홍길동",
  "externalRef": "partner-book-001"
}'
```

ResponseCopy```
{
  "success": true,
  "message": "책 생성 완료",
  "data": {
    "bookUid": "bk_3dJTg8WOpR2e"
  }
}
```


## externalRef 활용 패턴

externalRef는 파트너 시스템의 내부 ID를 SweetBook의 책과 매핑하기 위한 필드입니다. 파트너 측 DB의 주문번호, 상품번호 등을 저장하면 양쪽 시스템 간의 데이터 추적이 용이합니다.

이후 GET /books 응답에서 externalRef 값을 확인하여 파트너 시스템과 연동할 수 있습니다.

Request bodyCopy```
{
  "title": "졸업앨범 2025",
  "bookSpecUid": "SQUAREBOOK_HC",
  "externalRef": "my-system-order-12345"
}
```


## 표지 추가

POST /books/{bookUid}/cover로 표지를 추가합니다. 템플릿 UID와 함께 앞표지/뒷표지 이미지를 업로드합니다.

템플릿마다 요구하는 파라미터가 다릅니다. `GET /templates/{templateUid}`로 필수 파라미터를 확인하세요.RequestSandboxLiveCopy```
curl -X POST \
  'https://api-sandbox.sweetbook.com/v1/books/{bookUid}/cover' \
  -H 'Authorization: Bearer YOUR_API_KEY' \
  -H 'Content-Type: multipart/form-data' \
  -F 'frontPhoto=@front.jpg;type=image/jpeg' \
  -F 'backPhoto=@back.jpg;type=image/jpeg' \
  -F 'templateUid=COVER_TEMPLATE_UID' \
  -F 'parameters={"title":"나의 첫 포토북","author":"홍길동"}'
```


## 내지 추가 (반복)

POST /books/{bookUid}/contents로 내지 페이지를 추가합니다. 판형의 최소 페이지 수를 충족할 때까지 이 API를 반복 호출합니다.

| 파라미터 | 위치 | 설명 |
| --- | --- | --- |
| breakBefore | Query | 페이지 나눔 방식 (예: page). 새 페이지에서 시작할지 제어 |
| templateUid | Body | 내지 템플릿 UID |
| files | Body | 이미지 파일 (multipart) |
| parameters | Body | 템플릿 파라미터 (JSON) |

여러 페이지를 빠르게 추가하려면 bash 반복문을 사용하세요. 지원 이미지 형식: JPG, PNG, GIF, BMP, WebP, HEIC (SVG 미지원)RequestSandboxLiveCopy```
curl -X POST \
  'https://api-sandbox.sweetbook.com/v1/books/{bookUid}/contents?breakBefore=page' \
  -H 'Authorization: Bearer YOUR_API_KEY' \
  -H 'Content-Type: multipart/form-data' \
  -F 'files=@photo1.jpg;type=image/jpeg' \
  -F 'templateUid=CONTENT_TEMPLATE_UID' \
  -F 'parameters={"date":"2025-10-20","contents":"즐거운 여행의 시작"}'
```


## 내지 초기화

DELETE /books/{bookUid}/contents로 추가된 모든 내지 페이지를 삭제하고 처음부터 다시 시작할 수 있습니다. 표지는 유지됩니다.

RequestSandboxLiveCopy```
curl -X DELETE \
  'https://api-sandbox.sweetbook.com/v1/books/{bookUid}/contents' \
  -H 'Authorization: Bearer YOUR_API_KEY'
```


## 페이지 수 관리

GET /books/{bookUid}로 현재 책의 상태와 페이지 수를 확인할 수 있습니다. 최종화 전에 판형의 최소 페이지 수를 충족하는지 반드시 확인하세요.

판형별 최소/최대 페이지 수는 `GET /book-specs`의 `pageMin`, `pageMax`에서 확인할 수 있습니다. 최소 페이지 수를 충족하지 않으면 최종화가 실패합니다.RequestSandboxLiveCopy```
curl -X GET 'https://api-sandbox.sweetbook.com/v1/books/{bookUid}' \
  -H 'Authorization: Bearer YOUR_API_KEY'
```

ResponseCopy```
{
  "success": true,
  "data": {
    "bookUid": "bk_3dJTg8WOpR2e",
    "title": "나의 첫 포토북",
    "bookSpecUid": "SQUAREBOOK_HC",
    "externalRef": "partner-book-001",
    "pageCount": 28,
    "status": "EDITING",
    "creationType": "TEST",
    "createdAt": "2025-10-20T10:00:00Z"
  }
}
```


## 책 최종화

POST /books/{bookUid}/finalization으로 편집을 완료합니다. 최종화가 완료된 책만 주문에 사용할 수 있습니다. 최소 페이지 수를 충족해야 합니다.

RequestSandboxLiveCopy```
curl -X POST \
  'https://api-sandbox.sweetbook.com/v1/books/{bookUid}/finalization' \
  -H 'Authorization: Bearer YOUR_API_KEY'
```

ResponseCopy```
{
  "success": true,
  "message": "책 최종화 완료",
  "data": {
    "result": "페이지를 추가하지 않고 완료",
    "pageCount": 32,
    "finalizedAt": "2025-10-21T02:28:45.505Z"
  }
}
```


## 다음 단계

- Templates API — 템플릿 조회 및 이미지 업로드
- Step 5: 주문 및 결제 — 견적 조회, 주문 생성, 충전금 결제
- Books API 레퍼런스 — 전체 Books API 상세 문서


------------------------------------------------------------
## 통합 가이드 > 이미지
**URL**: https://api.sweetbook.com/docs/guides/images/
------------------------------------------------------------

# 이미지 업로드 가이드

포토북에 사용할 이미지의 지원 포맷, 크기 제한, 자동 처리 방식, 배치 모드를 안내합니다.


## 지원 이미지 포맷

다음 이미지 포맷을 지원합니다.

| 포맷 | 확장자 | 비고 |
| --- | --- | --- |
| JPEG | .jpg, .jpeg | 가장 일반적인 사진 포맷 |
| PNG | .png | 투명 배경 지원 |
| GIF | .gif | 첫 번째 프레임만 사용 |
| BMP | .bmp | 비압축 비트맵 |
| WebP | .webp | 구글 포맷, 자동 변환 처리 |
| HEIC / HEIF | .heic, .heif | iPhone 기본 포맷, 자동으로 JPEG 변환 |

**SVG는 지원하지 않습니다.** 벡터 이미지(SVG)는 업로드할 수 없습니다. SVG 이미지를 사용해야 하는 경우, 먼저 PNG 또는 JPEG로 변환(래스터라이즈)한 후 업로드하세요.
## 자동 처리

업로드된 이미지는 서버에서 자동으로 다음 처리를 수행합니다.

| 처리 | 설명 |
| --- | --- |
| HEIC/HEIF 변환 | HEIC/HEIF 포맷은 자동으로 JPEG로 변환됩니다. 별도의 사전 변환이 필요 없습니다. |
| EXIF 회전 보정 | EXIF 메타데이터의 방향(orientation) 정보를 읽어 이미지를 올바른 방향으로 자동 회전합니다. |
| 썸네일 생성 | 업로드된 이미지의 썸네일을 자동 생성합니다. 최대 800px 크기로 리사이즈됩니다. |

원본 이미지는 그대로 보존됩니다. 자동 처리는 인쇄 렌더링과 썸네일 표시에만 적용됩니다.
## 이미지 배치 모드

이미지가 템플릿의 이미지 영역에 배치될 때 두 가지 모드가 적용될 수 있습니다.

| 모드 | 동작 | 잘림 여부 | 사용 예 |
| --- | --- | --- | --- |
| cover (채우기) | 영역을 완전히 채우도록 이미지를 확대/축소합니다. 비율이 다르면 일부가 잘립니다. | 잘릴 수 있음 | 전면 사진, 배경 이미지 |
| contain (맞추기) | 이미지 전체가 영역 안에 보이도록 축소합니다. 비율이 다르면 여백이 생깁니다. | 잘리지 않음 | 로고, 일러스트 |

배치 모드는 템플릿의 이미지 요소에 미리 설정되어 있습니다. API 호출 시 별도로 지정할 필요는 없습니다.
## 파일 크기 제한

| 항목 | 제한 | 비고 |
| --- | --- | --- |
| 요청당 최대 크기 | 200MB | 하나의 업로드 요청에 포함된 전체 파일 크기 합계 |
| 개별 파일 크기 | 제한 없음 | 요청당 최대 크기 이내라면 개별 파일 크기 제한 없음 |


## 해상도 권장사항

이미지 해상도에 대한 명시적 제한은 없지만, 인쇄 품질을 위해 고해상도 이미지를 권장합니다.

- 인쇄 품질 기준으로 300 DPI 이상을 권장합니다.
- 저해상도 이미지는 인쇄 시 흐릿하게 출력될 수 있습니다.
- 스마트폰 기본 카메라로 촬영한 사진은 대부분 충분한 해상도를 가지고 있습니다.

SNS에서 다운로드한 이미지, 스크린샷, 메신저로 전송받은 이미지는 압축되어 해상도가 낮을 수 있습니다. 원본 이미지 사용을 권장합니다.
## 썸네일 자동 생성

업로드된 이미지에 대해 썸네일이 자동 생성됩니다. 썸네일은 긴 변 기준 최대 800px로 리사이즈되며, 앱에서 미리보기 용도로 활용할 수 있습니다.

ResponseCopy```
{
  "fileName": "abc123_photo.jpg",
  "originalUrl": "https://storage.sweetbook.com/originals/abc123_photo.jpg",
  "thumbnailUrl": "https://storage.sweetbook.com/thumbnails/abc123_photo_thumb.jpg",
  "width": 4032,
  "height": 3024
}
```


## 업로드 예시

HEIC 파일(`photo3.heic`)이 자동으로 JPEG로 변환되어 `.jpg` 확장자로 반환된 것을 확인하세요.RequestSandboxLiveCopy```
curl -X POST 'https://api-sandbox.sweetbook.com/v1/books/{bookUid}/photos' \
  -H 'Authorization: Bearer YOUR_API_KEY' \
  -F 'files=@photo1.jpg' \
  -F 'files=@photo2.jpg' \
  -F 'files=@photo3.heic'
```

ResponseCopy```
{
  "success": true,
  "message": "Success",
  "data": {
    "photos": [
      {
        "fileName": "abc123_photo1.jpg",
        "thumbnailUrl": "https://storage.sweetbook.com/thumbnails/abc123_photo1_thumb.jpg",
        "width": 4032,
        "height": 3024
      },
      {
        "fileName": "def456_photo2.jpg",
        "thumbnailUrl": "https://storage.sweetbook.com/thumbnails/def456_photo2_thumb.jpg",
        "width": 3000,
        "height": 4000
      },
      {
        "fileName": "ghi789_photo3.jpg",
        "thumbnailUrl": "https://storage.sweetbook.com/thumbnails/ghi789_photo3_thumb.jpg",
        "width": 4032,
        "height": 3024
      }
    ]
  }
}
```


## 다음 단계

- Step 5~7: 표지/내지 추가 및 최종화 — 업로드한 사진을 템플릿에 적용
- Step 2: 템플릿 선택 — 이전 단계로 돌아가기
- 전체 워크플로우 — 전체 연동 흐름 보기


------------------------------------------------------------
## 통합 가이드 > 주문
**URL**: https://api.sweetbook.com/docs/guides/orders/
------------------------------------------------------------

# 주문 및 결제 가이드

견적 조회, 주문 생성, 취소, 배송지 변경 등 주문 관련 전체 프로세스를 안내합니다.


## 견적 조회

POST /orders/estimate로 주문 전에 가격을 확인합니다. 응답에는 productAmount(제작비) + shippingFee(배송비) + packagingFee(포장비) = totalAmount(합계)가 포함되며,paidCreditAmount는 부가세(10%)가 포함된 실제 차감 금액입니다.

Sandbox에서는 테스트 가격(100원 이하)이 적용됩니다. Live 환경의 실제 가격은 개별 협의에 따라 결정됩니다.RequestSandboxLiveCopy```
curl -X POST 'https://api-sandbox.sweetbook.com/v1/orders/estimate' \
  -H 'Authorization: Bearer YOUR_API_KEY' \
  -H 'Content-Type: application/json' \
  -d '{
  "items": [
    { "bookUid": "bk_3dJTg8WOpR2e", "quantity": 1 }
  ]
}'
```

ResponseCopy```
{
  "success": true,
  "data": {
    "items": [
      {
        "bookUid": "bk_3dJTg8WOpR2e",
        "bookSpecUid": "SQUAREBOOK_HC",
        "pageCount": 32,
        "quantity": 1,
        "unitPrice": 100,
        "itemAmount": 100,
        "packagingFee": 0
      }
    ],
    "productAmount": 100,
    "shippingFee": 0,
    "packagingFee": 0,
    "totalAmount": 100,
    "paidCreditAmount": 110,
    "creditBalance": 100000,
    "creditSufficient": true,
    "currency": "KRW"
  }
}
```


## 충전금 잔액 확인

GET /credits로 현재 충전금 잔액을 확인합니다. 주문 생성 전에 잔액이 충분한지 반드시 확인하세요.

**Sandbox 충전금:** 파트너 포털의 충전금 관리에서 Sandbox 충전금을 충전할 수 있습니다. Live 환경과 완전히 분리되어 있습니다.RequestSandboxLiveCopy```
curl -X GET 'https://api-sandbox.sweetbook.com/v1/credits' \
  -H 'Authorization: Bearer YOUR_API_KEY'
```


## 주문 생성

POST /orders로 주문을 생성합니다. 주문 생성 즉시 충전금이 차감되며, 배송 정보가 필수입니다. 충전금 이중 차감을 방지하려면 Idempotency-Key 헤더를 반드시 포함하세요.

RequestSandboxLiveCopy```
curl -X POST 'https://api-sandbox.sweetbook.com/v1/orders' \
  -H 'Authorization: Bearer YOUR_API_KEY' \
  -H 'Content-Type: application/json' \
  -H 'Idempotency-Key: unique-request-id-12345' \
  -d '{
  "items": [
    { "bookUid": "bk_3dJTg8WOpR2e", "quantity": 1 }
  ],
  "shipping": {
    "recipientName": "홍길동",
    "recipientPhone": "010-1234-5678",
    "postalCode": "06236",
    "address1": "서울특별시 강남구 테헤란로 123",
    "address2": "4층"
  },
  "externalRef": "PARTNER-ORDER-001"
}'
```

ResponseCopy```
{
  "success": true,
  "data": {
    "orderUid": "ord_a1b2c3d4e5f6",
    "orderStatus": "PAID",
    "totalAmount": 100,
    "paidCreditAmount": 110,
    "items": [
      {
        "itemUid": "itm_x1y2z3w4",
        "bookUid": "bk_3dJTg8WOpR2e",
        "quantity": 1,
        "unitPrice": 100,
        "itemAmount": 100
      }
    ]
  }
}
```


## 충전금 부족 (402 에러)

충전금 잔액이 부족한 상태에서 주문을 생성하면 402 Payment Required 응답이 반환됩니다.

주문 생성 전에 `POST /orders/estimate`의 `creditSufficient` 필드로 잔액 충분 여부를 미리 확인하세요. Live 환경에서는 파트너 포털에서 충전금을 결제하여 충전합니다.Error responseCopy```
{
  "success": false,
  "message": "Insufficient credits. Required: 12500, Available: 5000",
  "data": null
}
```


## 주문 취소

PAID 또는 PDF_READY 상태의 주문만 취소할 수 있습니다. 취소 즉시 충전금이 환불됩니다.


### Request 필드 설명

| 필드 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| cancelReason | string | O | 취소 사유 (최대 500자) |

**취소 불가 상태:** CONFIRMED 이후의 주문은 이미 제작이 시작되어 취소할 수 없습니다.
에러 메시지: `"주문을 찾을 수 없습니다."` 또는 `"PAID 또는 PDF_READY 상태의 주문만 취소할 수 있습니다."`RequestSandboxLiveCopy```
curl -X POST 'https://api-sandbox.sweetbook.com/v1/orders/{orderUid}/cancel' \
  -H 'Authorization: Bearer YOUR_API_KEY' \
  -H 'Content-Type: application/json' \
  -d '{
  "cancelReason": "고객 변심"
}'
```


## 배송지 변경

PATCH /orders/{orderUid}/shipping으로 배송지 정보를 변경할 수 있습니다.

RequestSandboxLiveCopy```
curl -X PATCH 'https://api-sandbox.sweetbook.com/v1/orders/{orderUid}/shipping' \
  -H 'Authorization: Bearer YOUR_API_KEY' \
  -H 'Content-Type: application/json' \
  -d '{
  "recipientName": "김철수",
  "recipientPhone": "010-9876-5432",
  "postalCode": "04523",
  "address1": "서울특별시 중구 세종대로 110",
  "address2": "2층"
}'
```


## 주문 조회

GET /orders로 주문 목록을, GET /orders/{orderUid}로 개별 주문 상세를 조회합니다.

RequestSandboxLiveCopy```
# 주문 목록 조회
curl -X GET 'https://api-sandbox.sweetbook.com/v1/orders?limit=20&offset=0' \
  -H 'Authorization: Bearer YOUR_API_KEY'

# 개별 주문 조회
curl -X GET 'https://api-sandbox.sweetbook.com/v1/orders/{orderUid}' \
  -H 'Authorization: Bearer YOUR_API_KEY'
```


## 주문 상태 코드

주문은 다음 상태를 순서대로 거칩니다.

| Code | 상태 | 설명 |
| --- | --- | --- |
| 20 | PAID | 결제 완료 (충전금 차감됨) |
| 25 | PDF_READY | 인쇄용 PDF 생성 완료 |
| 30 | CONFIRMED | 제작 확정 |
| 40 | IN_PRODUCTION | 제작 진행 중 |
| 45 | COMPLETED | 개별 항목 제작 완료 |
| 50 | PRODUCTION_COMPLETE | 제작 완료 |
| 60 | SHIPPED | 배송 출발 |
| 70 | DELIVERED | 배송 완료 |
| 80 | CANCELLED | 주문 취소 |
| 81 | CANCELLED_REFUND | 취소 및 환불 완료 |
| 90 | ERROR | 오류 |

취소는 `PAID`(20) 또는 `PDF_READY`(25) 상태에서만 가능합니다.`CONFIRMED`(30) 이후에는 이미 제작이 시작되어 API를 통한 취소가 불가능합니다.
## 다음 단계

- Step 6: 웹훅으로 상태 추적 — 주문 상태 변경을 실시간으로 수신
- 충전금 시스템 — 충전금 잔액 관리 및 거래 내역
- Orders API 레퍼런스 — 전체 Orders API 상세 문서


------------------------------------------------------------
## 통합 가이드 > 웹훅
**URL**: https://api.sweetbook.com/docs/guides/webhooks/
------------------------------------------------------------

# 웹훅 연동 가이드

웹훅을 등록하고, 주문 상태 변경 이벤트를 실시간으로 수신하는 방법을 안내합니다.


## 웹훅 설정

PUT /webhooks/config로 웹훅 URL과 수신할 이벤트를 등록합니다.

RequestSandboxLiveCopy```
curl -X PUT 'https://api-sandbox.sweetbook.com/v1/webhooks/config' \
  -H 'Authorization: Bearer YOUR_API_KEY' \
  -H 'Content-Type: application/json' \
  -d '{
  "url": "https://your-server.com/webhooks/sweetbook",
  "events": [
    "order.paid",
    "order.confirmed",
    "order.status_changed",
    "order.shipped",
    "order.cancelled"
  ]
}'
```


### 설정 조회

GET /webhooks/config로 현재 등록된 웹훅 설정을 조회합니다.

RequestSandboxLiveCopy```
curl -X GET 'https://api-sandbox.sweetbook.com/v1/webhooks/config' \
  -H 'Authorization: Bearer YOUR_API_KEY'
```


### 테스트 이벤트 전송

POST /webhooks/test로 등록된 URL에 테스트 이벤트를 보내 정상 수신 여부를 확인할 수 있습니다.

RequestSandboxLiveCopy```
curl -X POST 'https://api-sandbox.sweetbook.com/v1/webhooks/test' \
  -H 'Authorization: Bearer YOUR_API_KEY'
```


## 서명 검증 (HMAC-SHA256)

웹훅 요청의 진위를 확인하기 위해 HMAC-SHA256 서명을 검증해야 합니다. 요청 헤더에 다음 정보가 포함됩니다.

| 헤더 | 설명 |
| --- | --- |
| X-Webhook-Event | 이벤트 타입 (예: order.paid) |
| X-Webhook-Delivery | 고유 전송 ID |
| X-Webhook-Timestamp | Unix 타임스탬프 |
| X-Webhook-Signature | 서명 값 (sha256=... 형식) |

서명 검증 방식: {timestamp}.{payload} 문자열을 시크릿 키로 HMAC-SHA256 해싱하여 비교합니다.


### JavaScript 예시

Node.jsCopy```
const crypto = require('crypto');

function verifyWebhookSignature(payload, headers, secret) {
  const timestamp = headers['x-webhook-timestamp'];
  const signature = headers['x-webhook-signature'];

  const expectedSig = 'sha256=' + crypto
    .createHmac('sha256', secret)
    .update(`${timestamp}.${payload}`)
    .digest('hex');

  return crypto.timingSafeEqual(
    Buffer.from(signature),
    Buffer.from(expectedSig)
  );
}

// Express.js 예시
app.post('/webhooks/sweetbook', express.raw({ type: 'application/json' }), (req, res) => {
  const payload = req.body.toString();
  const isValid = verifyWebhookSignature(payload, req.headers, WEBHOOK_SECRET);

  if (!isValid) {
    return res.status(401).send('Invalid signature');
  }

  const event = JSON.parse(payload);
  console.log('Event:', event.event_type, event.data);

  res.status(200).send('OK');
});
```


### Python 예시

PythonCopy```
import hmac
import hashlib

def verify_webhook_signature(payload: bytes, headers: dict, secret: str) -> bool:
    timestamp = headers.get('X-Webhook-Timestamp', '')
    signature = headers.get('X-Webhook-Signature', '')

    message = f"{timestamp}.{payload.decode('utf-8')}"
    expected_sig = 'sha256=' + hmac.new(
        secret.encode('utf-8'),
        message.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(signature, expected_sig)

# Flask 예시
@app.route('/webhooks/sweetbook', methods=['POST'])
def handle_webhook():
    payload = request.get_data()
    if not verify_webhook_signature(payload, request.headers, WEBHOOK_SECRET):
        return 'Invalid signature', 401

    event = request.get_json()
    print(f"Event: {event['event_type']}", event['data'])

    return 'OK', 200
```


## 공통 페이로드 구조

모든 웹훅 이벤트는 다음과 같은 공통 구조로 전달됩니다.

| 필드 | 설명 |
| --- | --- |
| event_uid | 이벤트 고유 ID |
| event_type | 이벤트 타입 |
| created_at | 이벤트 생성 시각 (ISO 8601) |
| data | 이벤트별 상세 데이터 |

ResponseCopy```
{
  "event_uid": "evt_abc123def456",
  "event_type": "order.paid",
  "created_at": "2025-10-21T03:00:00Z",
  "data": {
    ...
  }
}
```


## 웹훅 이벤트 목록


### 1. order.paid — 주문 생성 (충전금 차감 완료)

주문이 생성되고 충전금이 차감된 시점에 발생합니다. 주문 UID, 결제 금액, 항목 수가 페이로드에 포함됩니다.

order.paidCopy```
{
  "event_uid": "evt_abc123def456",
  "event_type": "order.paid",
  "created_at": "2025-10-21T03:00:00Z",
  "data": {
    "order_uid": "ord_a1b2c3d4e5f6",
    "order_status": "PAID",
    "total_amount": 15500,
    "item_count": 1,
    "ordered_at": "2025-10-21T03:00:00Z"
  }
}
```


### 2. order.confirmed — 제작 확정

관리자가 주문을 확인하고 출력일(printDay)을 배정한 시점에 발생합니다.

order.confirmedCopy```
{
  "event_uid": "evt_def456ghi789",
  "event_type": "order.confirmed",
  "created_at": "2025-10-22T09:00:00Z",
  "data": {
    "order_uid": "ord_a1b2c3d4e5f6",
    "order_status": "CONFIRMED",
    "print_day": "2025-10-23",
    "confirmed_at": "2025-10-22T09:00:00Z"
  }
}
```


### 3. order.status_changed — 주문 상태 변경

주문 상태가 변경될 때마다 발생합니다. 제작 시작(IN_PRODUCTION), 제작 완료(PRODUCTION_COMPLETE) 등 모든 상태 전이를 포함합니다.

order.status_changedCopy```
{
  "event_uid": "evt_ghi789jkl012",
  "event_type": "order.status_changed",
  "created_at": "2025-10-23T08:00:00Z",
  "data": {
    "order_uid": "ord_a1b2c3d4e5f6",
    "previous_status": "CONFIRMED",
    "new_status": "IN_PRODUCTION",
    "changed_at": "2025-10-23T08:00:00Z"
  }
}
```


### 4. order.shipped — 발송 완료

발송이 완료되어 운송장 번호(trackingNumber)와 택배사 정보가 등록된 시점에 발생합니다.

order.shippedCopy```
{
  "event_uid": "evt_mno345pqr678",
  "event_type": "order.shipped",
  "created_at": "2025-10-26T10:00:00Z",
  "data": {
    "order_uid": "ord_a1b2c3d4e5f6",
    "item_uid": "itm_x1y2z3w4",
    "tracking_number": "1234567890",
    "tracking_carrier": "한진택배",
    "shipped_at": "2025-10-26T10:00:00Z"
  }
}
```


### 5. order.cancelled — 주문 취소

주문이 취소되고 결제 금액이 충전금으로 환불된 시점에 발생합니다. 취소 사유와 환불 금액이 포함됩니다.

order.cancelledCopy```
{
  "event_uid": "evt_pqr678stu901",
  "event_type": "order.cancelled",
  "created_at": "2025-10-21T04:00:00Z",
  "data": {
    "order_uid": "ord_a1b2c3d4e5f6",
    "order_status": "CANCELLED_REFUND",
    "cancel_reason": "고객 요청에 의한 취소",
    "refund_amount": 15500,
    "cancelled_at": "2025-10-21T04:00:00Z"
  }
}
```


## 주문 상태 ↔ 웹훅 이벤트 매핑

| 주문 상태 | 웹훅 이벤트 | 설명 |
| --- | --- | --- |
| PAID | order.paid | 주문 생성 (충전금 차감 완료) |
| CONFIRMED | order.confirmed | 제작 확정 |
| IN_PRODUCTION / PRODUCTION_COMPLETE | order.status_changed | 주문 상태 변경 (제작 시작, 제작 완료 등) |
| SHIPPED | order.shipped | 발송 완료 (송장번호 포함) |
| CANCELLED_REFUND | order.cancelled | 주문 취소 및 환불 |


## 재시도 정책

웹훅 전송이 실패하면 (비-2xx 응답 또는 타임아웃) 최대 3회까지 자동으로 재시도합니다.

| 시도 | 대기 시간 | 설명 |
| --- | --- | --- |
| 1차 재시도 | 1분 후 | 첫 번째 실패 후 |
| 2차 재시도 | 5분 후 | 두 번째 실패 후 |
| 3차 재시도 | 30분 후 | 세 번째 실패 후 (최종) |

3회 재시도 후에도 전송에 실패하면 해당 이벤트는 더 이상 전송되지 않습니다. 파트너 포털의 웹훅 로그에서 실패 내역을 확인할 수 있습니다.
## 폴링 대안

웹훅 구현이 어려운 경우 GET /orders/{orderUid}로 주문 상태를 주기적으로 조회하는 폴링 방식을 사용할 수 있습니다.

폴링 시 Rate Limit을 고려하여 적절한 간격(예: 5~10분)을 두고 조회하세요. 실시간성이 중요한 경우 웹훅 사용을 권장합니다.RequestSandboxLiveCopy```
curl -X GET 'https://api-sandbox.sweetbook.com/v1/orders/{orderUid}' \
  -H 'Authorization: Bearer YOUR_API_KEY'
```


## 다음 단계

- Step 7: 운영 환경 전환 체크리스트 — Sandbox에서 Live로 전환하기
- Webhooks API 레퍼런스 — 전체 Webhooks API 상세 문서
- Webhook Events 레퍼런스 — 이벤트 타입별 상세 스키마


------------------------------------------------------------
## 통합 가이드 > Go Live
**URL**: https://api.sweetbook.com/docs/guides/go-live/
------------------------------------------------------------

# 운영 전환 가이드

Sandbox에서 Live 환경으로 전환하기 위한 사전 조건과 체크리스트를 안내합니다.


## 사전 조건

Live 환경으로 전환하려면 다음 조건이 충족되어야 합니다.

- 사업 협의 완료: 스위트북 담당자와 사업 협의(가격, 물량, 납기 등)가 완료되어야 합니다.
- Business 계정: 파트너 포털에서 Business 계정으로 전환이 완료되어야 합니다.

Live 환경에서의 주문은 **실제로 인쇄 및 배송**됩니다. 테스트 목적이라면 반드시 Sandbox 환경을 사용하세요.
## 전환 체크리스트

아래 항목을 순서대로 확인하세요.

사업 협의 완료스위트북 담당자 확인Business 계정 전환 완료Live API Key 발급Base URL 변경api-sandbox.sweetbook.com → api.sweetbook.com실제 충전금 충전파트너 포털에서 결제웹훅 URL을 운영 환경 주소로 변경IP 화이트리스트 설정권장에러 핸들링 및 재시도 로직 확인충전금 잔액 모니터링 설정첫 Live 주문 테스트실제 인쇄됨!
## 코드 변경 사항

Sandbox에서 Live로 전환할 때 변경해야 하는 항목은 Base URL과 API Key 두 가지뿐입니다.

API 인터페이스는 Sandbox와 Live가 완전히 동일합니다. URL과 Key 외에 코드를 변경할 필요가 없습니다. 환경변수로 관리하면 배포 환경에 따라 자동 전환할 수 있습니다.ConfigurationCopy```
- const BASE_URL = 'https://api-sandbox.sweetbook.com/v1';
- const API_KEY = 'sandbox_sk_...';
+ const BASE_URL = 'https://api.sweetbook.com/v1';
+ const API_KEY = 'live_sk_...';
```


## 제작 및 배송 SLA

Live 환경에서 주문 이후 제작 및 배송에 소요되는 시간은 다음과 같습니다.

| 단계 | 소요 기간 | 비고 |
| --- | --- | --- |
| 제작 | 영업일 기준 3~4일 | 주문 확정(CONFIRMED) 이후 |
| 배송 | 1~2일 | 한진택배를 통한 배송 |

공휴일, 연휴 기간에는 제작 일정이 지연될 수 있습니다.`order.shipped` 웹훅 이벤트에 송장번호(`tracking_number`)와 택배사(`tracking_carrier`) 정보가 포함됩니다.
## 불량 처리

인쇄 불량이 발생한 경우 파트너 포털을 통해 불량 접수를 진행합니다.

- 접수 방법: 파트너 포털에서 해당 주문의 불량 접수 + 불량 사진 첨부
- 재제작 소요: 영업일 기준 3~4일 (불량 확인 후)
- 비용: 인쇄 불량으로 확인된 경우 추가 비용 없이 재제작

불량 접수 시 **불량 부분이 확인 가능한 사진**을 반드시 첨부해 주세요. 원본 이미지 해상도 부족으로 인한 품질 저하는 불량 대상에 포함되지 않습니다.
## 관련 문서

- 환경 분리 (Sandbox / Live) — 환경별 차이점 안내
- 인증 가이드 — API Key 발급 및 인증
- Step 6: 웹훅으로 상태 추적 — 웹훅 설정 및 이벤트
- 충전금 시스템 — 충전금 관리 및 비용 계산
- 빠른 시작 가이드 — Sandbox에서 전체 흐름 테스트


================================================================================
# API 레퍼런스
================================================================================


------------------------------------------------------------
## API 레퍼런스 > 공통
**URL**: https://api.sweetbook.com/docs/api/common/
------------------------------------------------------------

# API 공통 사항

SweetBook API의 인증, 요청/응답 형식, 페이지네이션, Rate Limiting 등 공통 규칙을 안내합니다.


## 인증

모든 API 요청에는 Bearer Token 인증이 필요합니다. 파트너 포털에서 발급받은 API Key를 Authorization 헤더에 포함하세요.

API Key는 SB 접두사로 시작하며, .으로 구분된 prefix와 secret으로 구성됩니다. Sandbox 키와 Live 키가 분리되어 있으므로 환경에 맞는 키를 사용하세요.

**보안 주의:** API Key는 서버 측에서만 사용하세요. 클라이언트(브라우저, 앱)에 노출하지 마세요.Authorization headerCopy```
Authorization: Bearer SB{prefix}.{secret}
```


## Base URL

| 환경 | Base URL | 용도 |
| --- | --- | --- |
| Sandbox | https://api-sandbox.sweetbook.com/v1 | 개발 및 테스트 |
| Live | https://api.sweetbook.com/v1 | 실제 운영 |

Sandbox 환경에서는 실제 인쇄/배송이 이루어지지 않으며, Sandbox 충전금이 사용됩니다.
## 요청 / 응답 형식

대부분의 API 요청은 JSON 형식을 사용합니다. 파일 업로드가 필요한 엔드포인트는 multipart/form-data를 사용합니다.

| Content-Type | 대상 엔드포인트 |
| --- | --- |
| application/json | 일반 API (Orders, Webhooks 등) |
| multipart/form-data | 파일 업로드 (Cover, Contents, Photos) |


### 응답 필드

| 필드 | 타입 | 항상 포함 | 설명 |
| --- | --- | --- | --- |
| success | boolean | O | 요청 성공 여부 |
| message | string | O | 결과 메시지 |
| data | object | null | O | 응답 데이터 (에러 시 null) |
| errors | string[] | - | 에러 메시지 목록 (에러 시) |
| fieldErrors | object[] | - | 필드별 검증 에러 (400 에러 시) |


### 성공 응답

요청이 성공하면 success: true와 함께 data 필드에 결과가 포함됩니다.

ResponseCopy```
// 성공 응답
{
  "success": true,
  "message": "Success",
  "data": { ... }
}
```


### 에러 응답

요청이 실패하면 success: false와 함께 errors 또는 fieldErrors 필드에 상세 에러 정보가 포함됩니다.

Error responseCopy```
// 에러 응답
{
  "success": false,
  "message": "Validation failed",
  "data": null,
  "errors": ["잔액이 부족합니다."],
  "fieldErrors": [
    {
      "field": "email",
      "message": "Invalid email format"
    }
  ]
}
```


## 페이지네이션

목록 조회 API는 limit/offset 기반 페이지네이션을 사용합니다.

| 파라미터 | 기본값 | 최대값 | 설명 |
| --- | --- | --- | --- |
| limit | 20 | 100 | 한 페이지에 반환할 항목 수 |
| offset | 0 | - | 건너뛸 항목 수 |

| 필드 | 타입 | 설명 |
| --- | --- | --- |
| total | number | 전체 항목 수 |
| hasNext | boolean | 다음 페이지 존재 여부 |
| items | array | 현재 페이지의 항목 목록 |

ResponseCopy```
{
  "success": true,
  "message": "Success",
  "data": {
    "total": 85,
    "limit": 20,
    "offset": 0,
    "hasNext": true,
    "items": [ ... ]
  }
}
```


## Rate Limiting

| 정책 | 대상 | 제한 | 기준 |
| --- | --- | --- | --- |
| auth | 인증 엔드포인트 | 10 req/min | IP 기반 |
| general | 일반 API | 300 req/min | API Key 기반 |
| upload | 파일 업로드 / Contents | 200 req/min | API Key 기반 |

Rate Limit을 초과하면 429 Too Many Requests 응답이 반환됩니다. 응답의 Retry-After 헤더(60초)를 확인한 뒤 재시도하세요.

Error responseCopy```
{
  "success": false,
  "message": "Rate limit exceeded. Please retry after 60 seconds.",
  "data": null
}
```


## 멱등성 (Idempotency)

네트워크 오류로 동일한 요청이 중복 실행되는 것을 방지하기 위해 Idempotency-Key 헤더를 지원합니다.Books/Credits/Orders 주요 POST 엔드포인트(POST /books, POST /orders, POST /credits/sandbox/charge 등)에서 사용을 강력히 권장합니다.

동일한 Idempotency-Key로 동일한 요청을 보내면 이전 응답이 반환됩니다. 동일한 키로 다른 내용의 요청을 보내면 409 Conflict 에러가 발생합니다.

| 엔드포인트 | 설명 |
| --- | --- |
| POST /books | 책 중복 생성 방지 |
| POST /orders | 충전금 이중 차감 방지 |
| POST /credits/sandbox/charge | Sandbox 충전금 이중 충전 방지 |

**중요:** 특히 주문 생성(POST /orders)에는 반드시 Idempotency-Key를 포함하세요. 충전금 이중 차감을 방지합니다.RequestSandboxLiveCopy```
curl -X POST 'https://api-sandbox.sweetbook.com/v1/orders' \
  -H 'Authorization: Bearer YOUR_API_KEY' \
  -H 'Content-Type: application/json' \
  -H 'Idempotency-Key: unique-request-id-12345' \
  -d '{ ... }'
```


## 주요 HTTP 에러 코드

API 응답에서 자주 발생하는 HTTP 상태 코드와 원인입니다.

| 상태 코드 | 원인 | 해결 방법 |
| --- | --- | --- |
| 400 Bad Request | 요청 파라미터 또는 바디 유효성 검증 실패 | fieldErrors 필드를 확인하여 오류 필드 수정 |
| 401 Unauthorized | API Key 누락 또는 유효하지 않음 | Authorization 헤더에 올바른 API Key 포함 |
| 403 Forbidden | API Key 스코프 권한 부족 | 해당 엔드포인트에 접근 가능한 스코프가 부여된 API Key를 사용하거나 파트너 포털에서 키 재발급 |
| 404 Not Found | 요청한 리소스가 존재하지 않거나 접근 권한 없음 | UID 및 파트너 소유권 확인 |
| 402 Payment Required | 충전금 잔액 부족 | 파트너 포털에서 충전금 충전 후 재시도 |
| 409 Conflict | 동일 Idempotency-Key로 다른 요청 본문 전송 | 새로운 고유한 Idempotency-Key 사용 |
| 429 Too Many Requests | Rate Limit 초과 | Retry-After 헤더 값(초) 대기 후 재시도 |
| 500 Internal Server Error | 서버 내부 오류 | 잠시 후 재시도, 지속 시 support@sweetbook.com 문의 |


## 날짜 형식

모든 날짜/시간 필드는 ISO 8601 형식(UTC)을 사용합니다: 2026-03-17T09:30:00Z


## 관련 문서

- 인증 (API Key) — API Key 발급 및 인증 상세
- 환경 (Sandbox / Live) — 환경별 Base URL 및 전환 안내
- Rate Limiting — 요청 빈도 제한 상세 안내
- 페이지네이션 — 목록 조회 페이징 상세
- 멱등성 (Idempotency) — 멱등성 키 상세 동작 원리
- 에러 코드 레퍼런스 — HTTP 상태 코드 및 에러 응답


------------------------------------------------------------
## API 레퍼런스 > Books
**URL**: https://api.sweetbook.com/docs/api/books/
------------------------------------------------------------

# Books API

책 생성, 조회, 표지/내지 추가, 최종화 API 문서입니다.

모든 Books API는 인증이 필요합니다. API Key를 `Authorization: Bearer <API_KEY>` 헤더로 제공하세요.
## 책 목록 조회

GET`/v1/books`파트너가 생성한 책 목록을 조회합니다. 다양한 필터를 사용하여 검색할 수 있습니다.


### Query Parameters

| 파라미터 | 타입 | 기본값 | 설명 |
| --- | --- | --- | --- |
| limit | int | 20 | 조회할 항목 수 (최대 100) |
| offset | int | 0 | 건너뛸 항목 수 |
| pdfStatusIn | string | - | PDF 상태 필터 (1: 대기, 2: 완료, 9: 에러, 쉼표 구분) |
| createdFrom | string | - | 생성일 시작 범위 (ISO 8601, 예: 2026-01-01) |
| createdTo | string | - | 생성일 종료 범위 (ISO 8601, 예: 2026-03-31) |


### 응답 필드

| 필드 | 타입 | 설명 |
| --- | --- | --- |
| bookUid | string | 책 고유 UID |
| title | string | 책 제목 |
| bookSpecUid | string | 판형 UID |
| status | int | 책 상태 (0: draft, 2: finalized, 9: deleted) |
| pdfStatus | int | PDF 상태 |
| pdfRequestedAt | datetime | PDF 요청 일시 |
| createdAt | datetime | 생성 일시 |
| externalRef | string | 파트너 외부 참조 식별자 |

RequestSandboxLiveCopy```
curl -X GET 'https://api-sandbox.sweetbook.com/v1/books?pdfStatusIn=1,2&createdFrom=2026-01-01&createdTo=2026-03-31&limit=10' \
  -H 'Authorization: Bearer YOUR_API_KEY'
```

ResponseCopy```
{
  "success": true,
  "data": {
    "books": [
      {
        "bookUid": "bk_3dJTg8WOpR2e",
        "title": "테스트책",
        "bookSpecUid": "SQUAREBOOK_HC",
        "status": 2,
        "pdfStatus": 2,
        "pdfRequestedAt": "2026-01-15T10:30:00Z",
        "createdAt": "2026-01-15T09:00:00Z",
        "externalRef": "PARTNER-ORDER-001"
      }
    ],
    "total": 1,
    "limit": 10,
    "offset": 0
  }
}
```


## 책 생성

POST`/v1/books`새로운 책을 생성합니다. 초안(draft) 상태로 생성되며, 이후 표지와 콘텐츠를 추가할 수 있습니다.


### Request Body

| 필드 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| title | string | Y | 책 제목 (1-255자) |
| bookSpecUid | string | Y | 판형 UID (예: SQUAREBOOK_HC) |
| specProfileUid | string | N | SpecProfile UID - 제공 시 해당 프로필과 연결. 유효하지 않으면 에러 반환 |
| externalRef | string | N | 파트너 외부 참조 식별자 (최대 100자). 파트너 시스템의 고유 ID를 저장하는 용도 |

이 단계에서는 표지와 내지가 없는 빈 책만 생성됩니다. 이후 `/books/{bookUid}/cover` 및 `/books/{bookUid}/contents` API로 콘텐츠를 추가해야 합니다.**Idempotency-Key 지원:** `POST /books` 요청 시 `Idempotency-Key` 헤더를 제공하면 동일한 키로 재요청해도 책이 중복 생성되지 않습니다. 네트워크 오류 등으로 인한 재시도 시 활용하세요.
### HTTP 상태 코드

| 상태 코드 | 설명 |
| --- | --- |
| 201 Created | 책 생성 성공 |
| 400 Bad Request | 잘못된 요청 (필드 누락, 잘못된 형식 등) |
| 401 Unauthorized | 인증 실패 |
| 500 Internal Server Error | 서버 오류 |

Request bodyCopy```
{
  "title": "테스트책",
  "bookSpecUid": "SQUAREBOOK_HC",
  "specProfileUid": "sp_abc123xyz",
  "externalRef": "PARTNER-ORDER-001"
}
```

RequestSandboxLiveCopy```
curl -X 'POST' \
  'https://api-sandbox.sweetbook.com/v1/books' \
  -H 'Authorization: Bearer YOUR_API_KEY' \
  -H 'Idempotency-Key: unique-request-id-001' \
  -H 'Content-Type: application/json' \
  -d '{
  "title": "테스트책",
  "bookSpecUid": "SQUAREBOOK_HC"
}'
```

ResponseCopy```
{
  "success": true,
  "message": "책 생성 완료",
  "data": {
    "bookUid": "bk_3dJTg8WOpR2e"
  }
}
```


## 파일 업로드 제한

사진 및 이미지 업로드 시 다음 제한 사항이 적용됩니다.

| 항목 | 제한 |
| --- | --- |
| 파일당 최대 크기 | 50MB |
| 책당 최대 사진 수 | 200장 |
| 지원 포맷 | JPEG, PNG, GIF, BMP, TIFF, WebP |
| 업로드 Rate Limit | 200 req/min (일반 API 300 req/min과 별도) |


### 파일 검증

- Magic byte 검증: 파일 확장자뿐만 아니라 파일의 매직 바이트(파일 시그니처)를 확인하여 실제 이미지 파일인지 검증합니다.
- 자동 포맷 변환: JPEG이 아닌 포맷은 서버에서 JPEG으로 자동 변환됩니다.
- 이미지 URL 지원: HTTP/HTTPS URL을 통한 이미지 제공이 가능하며, 다운로드 제한은 50MB / 10초 타임아웃입니다.
- preserveExif: 사진 업로드 시 preserveExif 파라미터를 사용하여 EXIF 데이터 보존 여부를 제어할 수 있습니다.


## 책 표지 추가

POST`/v1/books/{bookUid}/cover`책의 표지를 생성합니다. 템플릿과 이미지를 사용하여 표지를 만들며, multipart/form-data 형식으로 요청합니다. 이미지 필드명은 템플릿 레이아웃의 변수명과 정확히 일치해야 합니다.


### 이미지 제공 방식 (혼용 가능)

| 방식 | 설명 |
| --- | --- |
| 파일 업로드 | multipart/form-data로 이미지 파일 직접 업로드 |
| URL 방식 | parameters JSON 내에 이미지 URL을 문자열로 제공 (http/https/www 지원) |
| 서버 파일명 | Photo Upload API로 미리 업로드한 파일명 사용 (예: photo250105143052123.JPG) |

혼합 방식 사용 시 `$upload` 플레이스홀더로 업로드 파일의 위치를 지정할 수 있습니다. 예: `"frontPhoto": "$upload"` → 이 위치에 업로드된 frontPhoto 파일 배치
### Request (multipart/form-data)

| 필드 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| templateUid | string | Y | 표지 템플릿 UID. 테스트용 권장: tpl_F8d15af9fd |
| parameters | string | N | 템플릿 파라미터 JSON 문자열. 동적 파라미터는 반드시 이 필드로만 전달해야 합니다. |
| 동적 이미지 필드 | file | 조건부 | 템플릿에서 정의한 변수명으로 이미지 제공. 필드명과 템플릿 변수명이 정확히 일치해야 바인딩됩니다. |

EXIF 정보는 항상 보존됩니다. 개별 form 필드로 텍스트 파라미터를 전달하는 방식은 더 이상 지원되지 않습니다. 최종화(status=2) 또는 삭제(status=9)된 책은 표지를 추가할 수 없습니다.
### HTTP 상태 코드

| 상태 코드 | 설명 |
| --- | --- |
| 201 Created | 새로운 표지 생성 성공 |
| 200 OK | 기존 표지 업데이트 성공 |
| 400 Bad Request | 잘못된 요청 |
| 401 Unauthorized | 인증 실패 |
| 500 Internal Server Error | 서버 오류 |

RequestSandboxLiveCopy```
curl -X 'POST' \
  'https://api-sandbox.sweetbook.com/v1/books/bk_3dJTg8WOpR2e/cover' \
  -H 'Authorization: Bearer YOUR_API_KEY' \
  -H 'Content-Type: multipart/form-data' \
  -F 'templateUid=tpl_F8d15af9fd' \
  -F 'frontPhoto=@front.jpg;type=image/jpeg' \
  -F 'backPhoto=@back.jpg;type=image/jpeg' \
  -F 'parameters={"title":"Test Book","author":"Test Author"}'
```

RequestSandboxLiveCopy```
curl -X 'POST' \
  'https://api-sandbox.sweetbook.com/v1/books/bk_3dJTg8WOpR2e/cover' \
  -H 'Authorization: Bearer YOUR_API_KEY' \
  -H 'Content-Type: multipart/form-data' \
  -F 'templateUid=tpl_F8d15af9fd' \
  -F 'parameters={"title":"Test Book","author":"Test Author","frontPhoto":"https://example.com/front.jpg","backPhoto":"https://example.com/back.jpg"}'
```

RequestSandboxLiveCopy```
curl -X 'POST' \
  'https://api-sandbox.sweetbook.com/v1/books/bk_3dJTg8WOpR2e/cover' \
  -H 'Authorization: Bearer YOUR_API_KEY' \
  -H 'Content-Type: multipart/form-data' \
  -F 'templateUid=tpl_F8d15af9fd' \
  -F 'frontPhoto=@front.jpg;type=image/jpeg' \
  -F 'parameters={"title":"Test Book","author":"Test Author","frontPhoto":"$upload","backPhoto":"photo250105143052456.JPG"}'
```

ResponseCopy```
{ "success": true, "message": "Cover created successfully", "data": { "result": "inserted" } }
```

ResponseCopy```
{ "success": true, "message": "Cover updated successfully", "data": { "result": "updated" } }
```


## 사진 업로드

POST`/v1/books/{bookUid}/photos`책에 사용할 사진을 업로드합니다. 업로드된 사진의 fileName을 contents API에서 사용합니다. 지원 형식: jpg, jpeg, png, gif, bmp, webp, heic, heif (최대 50MB)


### Request (multipart/form-data)

| 필드 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| file | file | Y | 이미지 파일 |


### 지원 이미지 포맷

| 포맷 | 확장자 | 서버 처리 |
| --- | --- | --- |
| JPEG | .jpg, .jpeg | 그대로 사용 |
| PNG | .png | 그대로 사용 |
| GIF | .gif | PNG로 자동 변환 |
| WebP | .webp | PNG로 자동 변환 |
| BMP | .bmp | JPG로 자동 변환 |
| HEIC/HEIF | .heic, .heif | JPG로 자동 변환 |

SVG, TIFF, PDF, AI, PSD 등은 지원하지 않습니다. 업로드 시 에러가 발생합니다.파일당 최대 50MB


### 이미지 처리

| 처리 | 내용 |
| --- | --- |
| 리사이즈 | 긴 축 기준 4000px (원본), 800px (썸네일) |
| 형식 변환 | HEIC/HEIF → JPG, GIF/WebP → PNG, BMP → JPG |
| EXIF 처리 | Orientation 적용 후 EXIF 제거 |
| 중복 체크 | MD5 해시로 중복 검사. 중복 시 isDuplicate: true와 함께 기존 파일 정보 반환 |

ResponseCopy```
{
  "success": true,
  "data": {
    "fileName": "photo250105143052123.JPG",
    "originalName": "IMG_1234.jpg",
    "size": 1234567,
    "mimeType": "image/jpeg",
    "uploadedAt": "2026-01-05T14:30:52Z",
    "isDuplicate": false,
    "hash": "d41d8cd98f00b204e9800998ecf8427e"
  }
}
```


## 사진 목록 조회

GET`/v1/books/{bookUid}/photos`책에 업로드된 사진 목록을 조회합니다.

ResponseCopy```
{
  "success": true,
  "data": {
    "photos": [
      {
        "fileName": "photo250105143052123.JPG",
        "originalName": "IMG_1234.jpg",
        "size": 1234567,
        "mimeType": "image/jpeg",
        "uploadedAt": "2026-01-05T14:30:52Z",
        "hash": "d41d8cd98f00b204e9800998ecf8427e"
      }
    ],
    "totalCount": 1
  }
}
```


## 사진 삭제

DELETE`/v1/books/{bookUid}/photos/{fileName}`업로드된 사진을 삭제합니다. 최종화된 책(status=2)의 사진은 삭제할 수 없습니다. 삭제된 사진의 fileName을 contents API에서 사용하면 에러가 발생합니다.

성공 시 (204 No Content) — 응답 본문 없음


## 책 콘텐츠 추가

POST`/v1/books/{bookUid}/contents`책의 내지(콘텐츠 페이지)를 추가합니다. 템플릿과 이미지를 사용하여 페이지를 생성하며, breakBefore 파라미터로 페이지 배치를 제어할 수 있습니다.


### 지원 기능

동적 텍스트 높이 계산 (isDynamic: true), 지능형 요소 배치, Gallery 레이아웃, 컬럼 레이아웃, 필드명 기반 이미지 매칭을 지원합니다.


### Query Parameters

| 파라미터 | 기본값 | 설명 |
| --- | --- | --- |
| breakBefore | content→none, divider/publish→page | page: 항상 새로운 페이지에서 시작 | column: 컬럼 기준 배치 (여유 컬럼에 배치, 없으면 다음 페이지) | none: 이전 콘텐츠 바로 다음에 연속 배치 |


### Request (multipart/form-data)

| 필드 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| templateUid | string | Y | 콘텐츠 템플릿 UID |
| parameters | string | N | 템플릿 파라미터 JSON 문자열. 동적 파라미터는 반드시 이 필드로만 전달해야 합니다. |
| 동적 이미지 필드 | file(s) | 조건부 | 템플릿 변수명과 일치하는 필드명으로 이미지 제공. Gallery는 같은 필드명으로 여러 파일 전송. |


### 필수/선택 파라미터 검증

| required 값 | 동작 |
| --- | --- |
| true | 필수 파라미터 — 누락 시 400 에러 반환 |
| false 또는 미정의 | 선택 파라미터 — 누락 시 해당 요소가 페이지에서 제거됨 |


### 주의사항

최종화(status=2) 또는 삭제(status=9)된 책은 콘텐츠를 추가할 수 없습니다. 템플릿의 변수명과 업로드 필드명이 정확히 일치해야 합니다. URL 방식 사용 시 이미지 다운로드 제한: 최대 50MB, 10초 타임아웃. 판형별 페이지 배치: SQUAREBOOK_HC는 첫 내지 페이지(first)가 오른쪽부터 시작합니다.


### HTTP 상태 코드

| 상태 코드 | 설명 |
| --- | --- |
| 201 Created | 새로운 콘텐츠 생성 성공 |
| 200 OK | 기존 콘텐츠 업데이트 성공 |
| 400 Bad Request | 잘못된 요청 (이미지 누락, breakBefore 값 오류 등) |
| 401 Unauthorized | 인증 실패 |
| 500 Internal Server Error | 서버 오류 |

Request bodyCopy```
{
  "rowPhotos": [
    "$upload",                          // 첫 번째 업로드 파일 위치
    "photo260109120000001.JPG",         // 서버 파일명
    "$upload",                          // 두 번째 업로드 파일 위치
    "https://example.com/img.jpg",      // URL
    "photo260109120000002.JPG"          // 서버 파일명
  ]
}
```

RequestSandboxLiveCopy```
curl -X 'POST' \
  'https://api-sandbox.sweetbook.com/v1/books/bk_3dJTg8WOpR2e/contents?breakBefore=page' \
  -H 'Authorization: Bearer YOUR_API_KEY' \
  -H 'Content-Type: multipart/form-data' \
  -F 'templateUid=5iwCNE0Xa8Gb' \
  -F 'imageMain=@image1.jpg;type=image/jpeg' \
  -F 'parameters={"dateStr":"2025-11-10","contents":"Hello World!"}'
```

RequestSandboxLiveCopy```
curl -X 'POST' \
  'https://api-sandbox.sweetbook.com/v1/books/bk_3dJTg8WOpR2e/contents?breakBefore=page' \
  -H 'Authorization: Bearer YOUR_API_KEY' \
  -H 'Content-Type: multipart/form-data' \
  -F 'templateUid=4HxVDGZxwLbB' \
  -F 'parameters={"date":"2025-10-17","galleryPhotos":["https://example.com/1.jpg","https://example.com/2.jpg","https://example.com/3.jpg"]}'
```

RequestSandboxLiveCopy```
# Step 1: Photo Upload API로 사진 업로드
curl -X 'POST' \
  'https://api-sandbox.sweetbook.com/v1/books/bk_3dJTg8WOpR2e/photos' \
  -H 'Authorization: Bearer YOUR_API_KEY' \
  -F 'file=@photo1.jpg'
# Response: {"data":{"fileName":"photo260107065637669.JPG"}}

# Step 2: 서버 파일명으로 contents 추가
curl -X 'POST' \
  'https://api-sandbox.sweetbook.com/v1/books/bk_3dJTg8WOpR2e/contents?breakBefore=page' \
  -H 'Authorization: Bearer YOUR_API_KEY' \
  -H 'Content-Type: multipart/form-data' \
  -F 'templateUid=4HxVDGZxwLbB' \
  -F 'parameters={"date":"2025-01-07","galleryPhotos":["photo260107065637669.JPG","photo260107065638193.JPG"]}'
```

ResponseCopy```
{
  "success": true,
  "message": "Content created successfully",
  "data": {
    "result": "inserted",
    "breakBefore": "page",
    "pageCount": 4
  }
}
```


## 책 내지 초기화

DELETE`/v1/books/{bookUid}/contents`책의 모든 내지 페이지를 삭제하고 표지만 남깁니다. 개발 및 테스트 용도로 사용됩니다.

개발 테스트용 API입니다. 삭제된 내지 페이지와 이미지는 복구할 수 없습니다. 표지(cover) 페이지는 삭제되지 않고 유지됩니다.
### HTTP 상태 코드

| 상태 코드 | 설명 |
| --- | --- |
| 200 OK | 내지 초기화 성공 |
| 400 Bad Request | 잘못된 요청 |
| 401 Unauthorized | 인증 실패 |
| 404 Not Found | 책을 찾을 수 없음 |
| 500 Internal Server Error | 서버 오류 |

ResponseCopy```
{
  "success": true,
  "message": "책 내지 초기화 완료",
  "data": {
    "deletedPages": 15,
    "message": "15개의 내지 페이지가 삭제되었습니다"
  }
}
```


## 책 삭제

DELETE`/v1/books/{bookUid}`책을 소프트 삭제(soft delete)합니다. 삭제된 책은 상태가 9 (deleted)로 변경되며 조회 목록에서 제외됩니다.


### 제약사항

| 항목 | 내용 |
| --- | --- |
| 소프트 딜리트 | 본인 소유의 책을 삭제합니다 (소프트 딜리트) |
| 권한 | 본인 소유 확인 (소유자만 삭제 가능) |


### HTTP 상태 코드

| 상태 코드 | 설명 |
| --- | --- |
| 200 OK | 삭제 완료 |
| 401 Unauthorized | 인증 실패 |
| 403 Forbidden | 권한 없음 (소유자가 아님) |
| 404 Not Found | 책을 찾을 수 없음 |

RequestSandboxLiveCopy```
curl -X DELETE 'https://api-sandbox.sweetbook.com/v1/books/bk_3dJTg8WOpR2e' \
  -H 'Authorization: Bearer YOUR_API_KEY'
```

ResponseCopy```
{
  "success": true,
  "message": "책이 삭제되었습니다",
  "data": {
    "bookUid": "bk_3dJTg8WOpR2e",
    "status": 9
  }
}
```


## 책 최종화

POST`/v1/books/{bookUid}/finalization`책 편집을 완료하고 최종본(finalized) 상태로 전환합니다. 이후에는 페이지 추가/수정이 불가능합니다. 멱등 처리를 지원하므로 재호출 시 에러 없이 기존 정보를 반환합니다.


### 제약사항

| 항목 | 내용 |
| --- | --- |
| 상태 조건 | DRAFT 상태의 책만 최종화 가능 |
| 권한 | 책 소유자만 최종화 가능 |
| 페이지 수 | 판형의 규칙 만족 필요 (최소/최대/증분) |


### 표지 책등 자동 조정

최종 페이지 수에 따라 cover.json의 책등 크기가 자동으로 조정됩니다. 하드커버의 경우 페이지 수 임계값에 따라 책등 너비가 증가하며, 소프트커버는 페이지 수에 따라 동적으로 계산됩니다. 왼쪽면 요소는 변화 없음, 오른쪽면 요소는 증가분만큼 이동, 책등 내 세로 텍스트는 증가분의 절반만큼 이동합니다.


### HTTP 상태 코드

| 상태 코드 | 설명 |
| --- | --- |
| 201 Created | 최종화 완료 |
| 200 OK | 이미 최종화된 책 (멱등 처리) |
| 400 Bad Request | 페이지 수 규칙 위반 등 |
| 401 Unauthorized | 인증 실패 |
| 403 Forbidden | 권한 없음 (소유자가 아님) |
| 404 Not Found | 책을 찾을 수 없음 |
| 500 Internal Server Error | 서버 오류 |

ResponseCopy```
{
  "success": true,
  "message": "책 최종화 완료",
  "data": {
    "result": "페이지를 추가하지 않고 완료",
    "pageCount": 24,
    "finalizedAt": "2025-10-01T02:28:45.505Z"
  }
}
```

ResponseCopy```
{
  "success": true,
  "message": "이미 최종화된 책입니다",
  "data": {
    "result": "updated",
    "pageCount": 24,
    "finalizedAt": "2025-10-01T02:28:45.505Z"
  }
}
```

Error responseCopy```
{
  "success": false,
  "message": "Validation Error",
  "data": null,
  "errors": ["페이지 수는 최소 20페이지 이상이어야 합니다"]
}
```


------------------------------------------------------------
## API 레퍼런스 > Orders
**URL**: https://api.sweetbook.com/docs/api/orders/
------------------------------------------------------------

# Orders API

주문 생성 및 주문 관리 API 문서입니다.

모든 Orders API는 인증이 필요합니다. API Key를 `Authorization: Bearer <API_KEY>` 헤더로 제공하세요.
## 주문 상태 코드

| 코드 | 키 | 설명 |
| --- | --- | --- |
| 20 | PAID | 결제 완료 (충전금 차감) |
| 25 | PDF_READY | PDF 생성 완료 |
| 30 | CONFIRMED | 제작 확정 (출력일 배정) |
| 40 | IN_PRODUCTION | 제작 진행 중 |
| 45 | COMPLETED | 항목 제작 완료 (개별) |
| 50 | PRODUCTION_COMPLETE | 전체 제작 완료 |
| 60 | SHIPPED | 발송 완료 |
| 70 | DELIVERED | 배송 완료 |
| 80 | CANCELLED | 취소 |
| 81 | CANCELLED_REFUND | 환불 완료 |
| 90 | ERROR | 오류 |


### 상태 전이 (State Transitions)

주문 상태는 다음과 같은 흐름으로 전이됩니다. 파트너 관점에서의 전이 주체를 함께 표기합니다.

| From | To | 주체 | 비고 |
| --- | --- | --- | --- |
| PAID | PDF_READY | 자동 | PDF 생성 완료 시 |
| PDF_READY | CONFIRMED | 관리자 | 제작 확정 |
| CONFIRMED | IN_PRODUCTION | 관리자 | 제작 시작 |
| IN_PRODUCTION | COMPLETED | 관리자 | 개별 항목 제작 완료 |
| COMPLETED | PRODUCTION_COMPLETE | 관리자 | 전체 제작 완료 |
| PRODUCTION_COMPLETE | SHIPPED | 관리자 | 운송장 번호 포함 |
| SHIPPED | DELIVERED | 관리자 | 배송 완료 확인 |
| PAID | CANCELLED_REFUND | 파트너 | 파트너 취소, 자동 환불 |
| PDF_READY | CANCELLED_REFUND | 파트너 | 파트너 취소, 자동 환불 |


### 파트너 가능 액션

| 액션 | 가능 상태 | 설명 |
| --- | --- | --- |
| 주문 취소 | PAID, PDF_READY | PAID 또는 PDF_READY 상태에서 취소 가능, 자동 환불 처리 |
| 배송지 변경 | PAID, PDF_READY, CONFIRMED | 발송 전까지만 배송지 변경 가능 |


## 주문 목록 조회

GET`/v1/orders`파트너의 주문 목록을 조회합니다. 기간 및 상태 필터를 조합하여 사용할 수 있습니다.


### Query 파라미터

| 파라미터 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| limit | int | - | 반환할 항목 수 (기본 20, 최대 100) |
| offset | int | - | 건너뛸 항목 수 (기본 0) |
| status | int | - | 주문 상태 코드로 필터링 (예: 20) |
| from | string | - | 조회 시작일 (ISO 8601, 예: 2026-01-01T00:00:00Z) |
| to | string | - | 조회 종료일 (ISO 8601, 예: 2026-12-31T23:59:59Z) |


### HTTP 상태 코드

| 상태 코드 | 설명 |
| --- | --- |
| 200 OK | 조회 성공 |
| 401 Unauthorized | 인증 실패 |

RequestSandboxLiveCopy```
curl -X GET 'https://api-sandbox.sweetbook.com/v1/orders?limit=20&offset=0&status=20&from=2026-01-01T00:00:00Z&to=2026-12-31T23:59:59Z' \
  -H 'Authorization: Bearer YOUR_API_KEY'
```

ResponseCopy```
{
  "success": true,
  "message": "Success",
  "data": {
    "total": 42,
    "limit": 20,
    "offset": 0,
    "hasNext": true,
    "items": [
      {
        "orderUid": "or_3eAx1IQiGByu",
        "orderStatus": 20,
        "orderStatusDisplay": "결제완료",
        "totalAmount": 64400.00,
        "orderedAt": "2026-02-19T01:10:47Z"
      }
    ]
  }
}
```


## 주문 상세 조회

GET`/v1/orders/{orderUid}`특정 주문의 상세 정보를 조회합니다. 주문 항목, 배송 정보, 현재 상태가 모두 포함됩니다.


### 주요 응답 필드

| 필드 | 타입 | 설명 |
| --- | --- | --- |
| paymentMethod | string | 결제 수단 (항상 "CREDIT") |
| externalUserId | string | null | 파트너 측 유저 식별자 (엔드유저 연동 시 설정) |
| batchUid | string | null | 배치 주문 UID (해당하는 경우) |
| endUserAmount | number | null | 엔드유저 결제 금액 (엔드유저 결제 연동 시 사용) |
| endUserShippingFee | number | null | 엔드유저 배송비 (엔드유저 결제 연동 시 사용) |
| endUserDiscount | number | null | 엔드유저 할인 금액 (엔드유저 결제 연동 시 사용) |
| endUserPaidAmount | number | null | 엔드유저 실결제 금액 (엔드유저 결제 연동 시 사용) |


### HTTP 상태 코드

| 상태 코드 | 설명 |
| --- | --- |
| 200 OK | 조회 성공 |
| 401 Unauthorized | 인증 실패 |
| 404 Not Found | 주문을 찾을 수 없음 |

RequestSandboxLiveCopy```
curl -X GET 'https://api-sandbox.sweetbook.com/v1/orders/or_3eAx1IQiGByu' \
  -H 'Authorization: Bearer YOUR_API_KEY'
```

ResponseCopy```
{
  "success": true,
  "message": "Success",
  "data": {
    "orderUid": "or_3eAx1IQiGByu",
    "orderType": "NORMAL",
    "orderStatus": 20,
    "orderStatusDisplay": "결제완료",
    "externalRef": "PARTNER-ORDER-001",
    "totalProductAmount": 60400.00,
    "totalShippingFee": 3000.00,
    "totalPackagingFee": 0,
    "totalAmount": 63400.00,
    "paidCreditAmount": 63400.00,
    "recipientName": "홍길동",
    "recipientPhone": "010-1234-5678",
    "postalCode": "06101",
    "address1": "서울시 강남구 테헤란로 123",
    "address2": "4층 401호",
    "orderedAt": "2026-02-19T01:10:47Z",
    "items": [
      {
        "itemUid": "oi_aB3cD4eF5gH6",
        "bookUid": "bk_abc123",
        "bookTitle": "우리 아이 성장앨범",
        "quantity": 1,
        "unitPrice": 60400.00,
        "itemAmount": 60400.00,
        "itemStatus": 20,
        "itemStatusDisplay": "결제완료"
      }
    ]
  }
}
```


## 주문 생성

POST`/v1/orders`FINALIZED 상태의 책을 대상으로 주문을 생성합니다. 충전금이 즉시 차감됩니다.

충전금 이중 차감 방지를 위해 `Idempotency-Key` 헤더를 반드시 포함하세요. 동일한 키로 재시도하면 이전 응답이 그대로 반환됩니다. 자세한 내용은 [API 공통 사항 > 멱등성](/docs/api/common/)을 참고하세요.
### Request 필드 설명

| 필드 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| items | array | O | 주문 항목 목록 (최소 1개) |
| items[].bookUid | string | O | 책 UID (FINALIZED 상태여야 함) |
| items[].quantity | int | O | 수량 (1~100) |
| shipping | object | O | 배송지 정보 |
| shipping.recipientName | string | O | 수령인 (최대 100자) |
| shipping.recipientPhone | string | O | 연락처 (최대 20자) |
| shipping.postalCode | string | O | 우편번호 (최대 10자) |
| shipping.address1 | string | O | 주소 (최대 200자) |
| shipping.address2 | string | - | 상세주소 (최대 200자) |
| shipping.memo | string | - | 배송 메모 (최대 200자) |
| externalRef | string | - | 파트너 외부 참조 식별자 (최대 100자) |
| externalUserId | string | - | 파트너 측 유저 식별자 (최대 100자). 엔드유저 연동 시 사용 |


### 처리 로직

- 각 bookUid 유효성 검증 (존재, 파트너 소유, FINALIZED 상태)
- 각 책의 bookSpecUid로 가격 계산
- 배송비(3,000원/주문) + 상품금액 합산
- 충전금 잔액 확인 후 차감
- 주문 생성


### HTTP 상태 코드

| 상태 코드 | 설명 |
| --- | --- |
| 201 Created | 주문 생성 성공 |
| 400 Bad Request | 유효성 검증 실패 (Book 미존재, 미FINALIZED 등) |
| 401 Unauthorized | 인증 실패 |
| 402 Payment Required | 충전금 잔액 부족 |
| 500 Internal Server Error | 서버 오류 |

Request headersCopy```
Authorization: Bearer YOUR_API_KEY
Content-Type: application/json
Idempotency-Key: unique-request-id-12345
```

Request bodyCopy```
{
  "items": [
    { "bookUid": "bk_abc123", "quantity": 1 },
    { "bookUid": "bk_def456", "quantity": 2 }
  ],
  "shipping": {
    "recipientName": "홍길동",
    "recipientPhone": "010-1234-5678",
    "postalCode": "06101",
    "address1": "서울시 강남구 테헤란로 123",
    "address2": "4층 401호",
    "memo": "부재시 경비실"
  },
  "externalRef": "PARTNER-ORDER-001"
}
```

ResponseCopy```
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
    "totalShippingFee": 3000.00,
    "totalPackagingFee": 0,
    "totalAmount": 63400.00,
    "paidCreditAmount": 63400.00,
    "creditBalanceAfter": 936600.00,
    "recipientName": "홍길동",
    "recipientPhone": "010-1234-5678",
    "postalCode": "06101",
    "address1": "서울시 강남구 테헤란로 123",
    "address2": "4층 401호",
    "shippingMemo": "부재시 경비실",
    "paymentMethod": "CREDIT",
    "externalUserId": null,
    "batchUid": null,
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

Error responseCopy```
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


## 주문 취소

POST`/v1/orders/{orderUid}/cancel`PAID 또는 PDF_READY 상태의 주문을 취소합니다. 결제된 충전금은 전액 환불됩니다.


### 취소 조건

- PAID 또는 PDF_READY 상태이고 NORMAL 유형의 주문만 취소 가능합니다
- 제작이 시작된 주문(CONFIRMED 이후)은 취소할 수 없습니다
- 취소 시 결제 금액이 충전금으로 전액 환불됩니다


### Request Body

| 필드 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| cancelReason | string | O | 취소 사유 (최대 500자) |

Response (200 OK): 변경된 주문 상세 정보가 반환됩니다.

Request bodyCopy```
{
  "cancelReason": "고객 변심"
}
```


## 배송지 변경

PATCH`/v1/orders/{orderUid}/shipping`PAID ~ CONFIRMED 상태에서 배송지를 변경할 수 있습니다. 발송(SHIPPED) 이후에는 변경이 불가합니다. 변경할 필드만 전달합니다.

지원 필드: recipientName, recipientPhone, postalCode, address1, address2, shippingMemo

Request bodyCopy```
{
  "recipientName": "김영희",
  "address1": "서울시 서초구 반포대로 100"
}
```


------------------------------------------------------------
## API 레퍼런스 > Templates
**URL**: https://api.sweetbook.com/docs/api/templates/
------------------------------------------------------------

# Templates API

템플릿을 조회하고 책에 적용하는 방법을 안내합니다.


## 템플릿이란?

템플릿은 포토북 페이지의 레이아웃을 정의하는 디자인 틀입니다. 텍스트, 사진, 그래픽 요소의 배치와 스타일이 미리 설정되어 있어, 파라미터만 전달하면 완성된 페이지를 만들 수 있습니다.


## 템플릿 종류

템플릿은 templateKind로 구분되며, 두 가지 종류가 있습니다.

| 종류 | 값 | 용도 | 적용 API |
| --- | --- | --- | --- |
| 표지 템플릿 | cover | 책 표지 디자인. 책당 하나만 적용됩니다. | POST /books/{bookUid}/cover |
| 내지 템플릿 | content | 내지 페이지 디자인. 여러 번 적용하여 페이지를 추가합니다. | POST /books/{bookUid}/contents |

표지 템플릿과 내지 템플릿은 서로 다른 API로 적용합니다. 표지에 내지 템플릿을 사용하거나, 내지에 표지 템플릿을 사용할 수 없습니다.
## 카테고리

템플릿은 용도별 카테고리로 분류됩니다. GET /template-categories로 전체 목록을 조회할 수 있습니다.

| 코드 | key | 한국어 | English |
| --- | --- | --- | --- |
| 1 | diary | 일기장 | Diary |
| 2 | notice | 알림장 | Notice |
| 3 | album | 앨범 | Album |
| 4 | yearbook | 졸업앨범 | Yearbook |
| 5 | wedding | 웨딩 | Wedding |
| 6 | baby | 육아 | Baby |
| 7 | travel | 여행 | Travel |
| 8 | etc | 기타 | Etc |


## 템플릿 조회하기


### 목록 조회

GET /templates로 사용 가능한 템플릿을 조회합니다. 공용(public) 템플릿과 본인이 생성한 템플릿이 함께 조회됩니다.

| Query Parameter | 설명 |
| --- | --- |
| bookSpecUid | 판형 UID로 필터링 (예: SQUAREBOOK_HC) |
| category | 카테고리로 필터링 (예: album, diary) |
| templateKind | 종류로 필터링 (cover 또는 content) |
| templateName | 템플릿 이름 검색 — 띄어쓰기로 구분된 다중 키워드 AND 매칭 (예: 알림장 내지) |
| specProfileUid | SpecProfile UID로 필터링 |
| theme | 테마로 필터링 (예: spring, minimal) |
| sort | 정렬 기준 — name_asc, name_desc, created_asc, updated_desc, updated_asc (기본: created_desc) |
| limit, offset | 페이지네이션 (기본 limit: 50) |

RequestSandboxLiveCopy```
# SQUAREBOOK_HC용 내지 템플릿 조회
curl 'https://api-sandbox.sweetbook.com/v1/templates?bookSpecUid=SQUAREBOOK_HC&templateKind=content' \
  -H 'Authorization: Bearer YOUR_API_KEY'
```

ResponseCopy```
{
  "success": true,
  "message": "Success",
  "data": {
    "templates": [
      {
        "templateUid": "8hKvbcNJdSgj",
        "templateName": "알림장A_내지",
        "templateKind": "content",
        "category": "diary",
        "theme": "minimal",
        "bookSpecUid": "SQUAREBOOK_HC",
        "isPublic": true,
        "status": "active",
        "thumbnails": { "layout": "https://..." },
        "createdAt": "2026-01-15T09:00:00Z",
        "updatedAt": "2026-01-20T14:30:00Z"
      }
    ],
    "pagination": { "total": 45, "limit": 50, "offset": 0, "hasNext": false }
  }
}
```


### 상세 조회

GET /templates/{templateUid}로 특정 템플릿의 상세 정보를 확인할 수 있습니다. 상세 응답에는 파라미터 정의, 레이아웃, 레이아웃 규칙, 베이스 레이어 등이 포함됩니다.

| 상세 응답 필드 | 설명 |
| --- | --- |
| parameters | 파라미터 정의 (텍스트/이미지/갤러리 바인딩 정보) |
| layout | 레이아웃 정의 (요소 배치, 크기) |
| layoutRules | 레이아웃 규칙 (여백, 흐름, 컬럼 등) |
| baseLayer | 베이스 레이어 (홀수/짝수 페이지 배경 요소) |
| thumbnails | 썸네일 URL (layout, baseLayerOdd, baseLayerEven) |

RequestSandboxLiveCopy```
curl 'https://api-sandbox.sweetbook.com/v1/templates/8hKvbcNJdSgj' \
  -H 'Authorization: Bearer YOUR_API_KEY'
```


## 템플릿 선택 기준

템플릿을 선택할 때 다음 사항을 확인하세요.


#### 1. bookSpecUid 일치

템플릿의 bookSpecUid가 생성한 책의 bookSpecUid와 일치해야 합니다. 레이아웃 크기가 다르면 적용할 수 없습니다.


#### 2. templateKind 확인

표지에는 cover 템플릿, 내지에는 content 템플릿을 사용해야 합니다.


#### 3. 파라미터 확인

상세 조회로 parameters를 확인하여 어떤 값(텍스트, 사진 등)을 전달해야 하는지 파악하세요.


## 파라미터 구조

템플릿 상세 응답의 parameters는 definitions 래퍼로 감싸진 구조입니다. 각 파라미터 키는 parameters.definitions.{key} 경로에 위치합니다.

| 필드 | 설명 |
| --- | --- |
| parameters.definitions | 파라미터 정의 목록 객체 |
| parameters.definitions.{key}.binding | 바인딩 타입 — text, file, gallery |
| parameters.definitions.{key}.label | 사람이 읽을 수 있는 파라미터 이름 |

파라미터 필드를 식별할 때 `type` 대신 `binding` 필드를 사용합니다. 플레이스홀더 문법은 `$$variableName$$` (달러 기호 두 개)입니다. 예: `$$bookTitle$$`parameters 구조 예시Copy```
{
  "parameters": {
    "definitions": {
      "bookTitle": {
        "binding": "text",
        "label": "책 제목"
      },
      "frontPhoto": {
        "binding": "file",
        "label": "표지 사진"
      },
      "photos": {
        "binding": "gallery",
        "label": "내지 사진 목록"
      }
    }
  }
}
```


## 파라미터 바인딩

템플릿의 parameters.definitions에 정의된 바인딩 유형에 따라 값을 전달합니다.

| 바인딩 유형 | 전달 값 | 예시 |
| --- | --- | --- |
| text | 텍스트 문자열 | "bookTitle": "우리 가족 앨범" |
| file | 이미지 URL 또는 업로드 파일 | "lineBg": "https://..." |
| rowGallery | 사진 파일명 배열 | "photos": ["photo1.jpg", "photo2.jpg"] |

갤러리 바인딩에 사용할 사진은 먼저 `POST /books/{bookUid}/photos`로 업로드한 후, 반환된 `fileName`을 사용합니다.
## 책에 템플릿 적용하기

책 생성부터 최종화까지의 전체 흐름에서 템플릿이 사용되는 과정입니다.

- POST /books — 책 생성 (bookSpecUid 지정)
- POST /books/{bookUid}/photos — 사진 업로드 (필요 시)
- POST /books/{bookUid}/cover — 표지 적용 (cover 템플릿 + 파라미터)
- POST /books/{bookUid}/contents — 내지 추가 (content 템플릿 + 파라미터) ← 반복
- POST /books/{bookUid}/finalization — 최종화


### 표지 적용 예시

표지 템플릿을 적용할 때는 templateUid, 파라미터(제목, 저자 등), 이미지 파일을 함께 전달합니다.

RequestSandboxLiveCopy```
curl -X POST 'https://api-sandbox.sweetbook.com/v1/books/{bookUid}/cover' \
  -H 'Authorization: Bearer YOUR_API_KEY' \
  -H 'Content-Type: application/json' \
  -d '{
  "templateUid": "COVER_TEMPLATE_UID",
  "parameters": {
    "bookTitle": "우리 가족 앨범",
    "year": "2026"
  }
}'
```


### 내지 추가 예시

내지는 `POST /books/{bookUid}/contents`를 여러 번 호출하여 페이지를 계속 추가할 수 있습니다. 각 호출마다 다른 템플릿을 사용할 수도 있습니다.RequestSandboxLiveCopy```
curl -X POST 'https://api-sandbox.sweetbook.com/v1/books/{bookUid}/contents' \
  -H 'Authorization: Bearer YOUR_API_KEY' \
  -H 'Content-Type: application/json' \
  -d '{
  "templateUid": "8hKvbcNJdSgj",
  "parameters": {
    "date": "2026-03-01",
    "dayOfWeek": "월요일",
    "teacherComment": "오늘 하루도 잘 보냈습니다.",
    "photos": ["photo1.jpg", "photo2.jpg"]
  }
}'
```


## 관련 문서

- Books API — 책 생성, 표지/내지 추가, 최종화
- BookSpecs 가이드 — 판형 선택
- Template Engine — 템플릿 엔진 내부 동작
- Dynamic Layout — 동적 레이아웃 배치
- Gallery Templates — 갤러리 레이아웃


------------------------------------------------------------
## API 레퍼런스 > BookSpecs
**URL**: https://api.sweetbook.com/docs/api/book-specs/
------------------------------------------------------------

# BookSpecs API

포토북 판형의 종류와 특징을 안내하고, 목적에 맞는 판형을 선택하는 방법을 설명합니다.


## 판형(BookSpec)이란?

판형은 포토북의 물리적 제작 사양을 정의합니다. 판형 크기, 제본 방식, 표지 유형, 페이지 범위, 가격 등의 정보를 포함합니다. 책을 생성할 때 bookSpecUid를 지정하며, 이후 사용할 수 있는 템플릿과 페이지 규칙이 이 스펙에 의해 결정됩니다.


## 판형 종류

현재 제공되는 주요 판형입니다. GET /book-specs로 전체 목록을 조회할 수 있습니다.


### A4 소프트커버 포토북

PHOTOBOOK_A4_SC| 내지 크기 | 210 x 297 mm |
| --- | --- |
| 표지 | Softcover (소프트커버) |
| 제본 | PUR |
| 페이지 | 24 ~ 130 페이지 (2페이지씩 증가) |

A4 크기의 소프트커버 포토북입니다. 글과 사진을 넉넉하게 배치할 수 있어 일기장, 알림장 등에 적합합니다.


### A5 소프트커버 포토북

PHOTOBOOK_A5_SC| 내지 크기 | 148 x 210 mm |
| --- | --- |
| 표지 | Softcover (소프트커버) |
| 제본 | PUR |
| 페이지 | 50 ~ 200 페이지 (2페이지씩 증가) |

A5 크기의 소프트커버 포토북입니다. 최대 200페이지까지 지원하여 많은 사진을 담을 수 있습니다.


### 고화질 스퀘어북 (하드커버)

SQUAREBOOK_HC| 내지 크기 | 243 x 248 mm |
| --- | --- |
| 표지 | Hardcover (하드커버) |
| 제본 | PUR |
| 페이지 | 24 ~ 130 페이지 (2페이지씩 증가) |

하드커버의 정사각 판형입니다. 고급스러운 마감으로 선물용, 졸업앨범 등에 적합합니다.


## 판형 조회하기


### 목록 조회

사용 가능한 모든 판형 목록을 조회합니다. 각 상품의 UID, 이름, 바인딩 타입, 페이지 규칙 등이 반환됩니다.

**accountUid 자동 적용:** `accountUid` 파라미터를 전달하지 않으면 인증된 본인의 UID가 자동으로 적용됩니다. 이를 통해 해당 계정에 설정된 커스텀 가격이 자동 반영됩니다. 타인의 `accountUid`를 전달하면 **403 Forbidden**이 반환됩니다.RequestSandboxLiveCopy```
curl 'https://api-sandbox.sweetbook.com/v1/book-specs' \
  -H 'Authorization: Bearer YOUR_API_KEY'
```


### 상세 조회

bookSpecUid로 특정 판형의 상세 정보를 조회합니다. 가격 정보, 페이지 제한(최소/최대/단위), 크기 정보가 포함됩니다.

**accountUid 자동 적용:** `accountUid` 파라미터를 전달하지 않으면 인증된 본인의 UID가 자동으로 적용됩니다. 이를 통해 해당 계정에 설정된 커스텀 가격이 자동 반영됩니다. 타인의 `accountUid`를 전달하면 **403 Forbidden**이 반환됩니다.RequestSandboxLiveCopy```
curl 'https://api-sandbox.sweetbook.com/v1/book-specs/SQUAREBOOK_HC' \
  -H 'Authorization: Bearer YOUR_API_KEY'
```


### 주요 응답 필드

| 필드 | 설명 |
| --- | --- |
| bookSpecUid | 판형 고유 식별자 (책 생성 시 사용) |
| name | 판형명 |
| innerTrimWidthMm / innerTrimHeightMm | 내지 크기 (mm) |
| pageMin / pageMax | 페이지 범위 |
| pageIncrement | 페이지 증가 단위 |
| coverType | 표지 유형 (Softcover, Hardcover) |
| bindingType | 제본 유형 (PUR) |
| priceBase | 기본 가격 |
| pricePerIncrement | 페이지 증가당 추가 가격 |
| layoutSize | 레이아웃 작업 영역 크기 (표지/내지 width, height) |
| visibility | 공개 범위 (PUBLIC / PARTNER_ONLY / HIDDEN, 기본 PUBLIC) |
| ownerAccountUid | 소유 파트너 UID. null이면 공용 판형 |


## 가격 계산

제작 가격은 기본 가격에 추가 페이지 비용을 더해 산출됩니다.

실제 주문 가격은 `POST /orders/estimate`로 확인하세요. 수량, 포장비, 배송비 등 추가 요소가 반영될 수 있습니다.Price formulaCopy```
총 가격 = priceBase + ((pageCount - pageMin) ÷ pageIncrement) × pricePerIncrement

예시: SQUAREBOOK_HC, 40페이지
  기본 가격: 19,800원 (24페이지 포함)
  추가 페이지: (40 - 24) = 16페이지
  추가 비용: (16 ÷ 2) × 500 = 4,000원
  총 가격: 19,800 + 4,000 = 23,800원
```


## 페이지 규칙

책을 최종화(POST /books/{bookUid}/finalization)할 때 페이지 수가 스펙의 규칙을 충족해야 합니다.

- 페이지 수는 pageMin 이상, pageMax 이하여야 합니다.
- 페이지 수는 pageIncrement 단위로 증가해야 합니다 (예: 24, 26, 28, ...).
- 규칙에 맞지 않으면 최종화가 거부됩니다.


## 판형 선택 가이드

| 용도 | 추천 판형 | 이유 |
| --- | --- | --- |
| 일기장 / 알림장 | SQUAREBOOK_HC | 최대 130페이지로 한 달치 일기를 충분히 담을 수 있음 |
| 문서 / 포트폴리오 | PHOTOBOOK_A4_SC | A4 규격으로 문서, 작품집 등에 적합 |
| 대량 사진 앨범 | PHOTOBOOK_A5_SC | 최대 200페이지로 많은 사진을 담을 수 있음 |
| 고급 포토북 / 선물용 | SQUAREBOOK_HC | 하드커버로 고급스러운 마감 |
| 졸업앨범 / 범용 | SQUAREBOOK_HC | 정사각 판형으로 다양한 레이아웃 활용 가능 |


## 관련 문서

- Books API — 책 생성 시 bookSpecUid 사용
- Templates 가이드 — 판형에 맞는 템플릿 선택
- Orders API — 가격 견적 및 주문


------------------------------------------------------------
## API 레퍼런스 > Credits
**URL**: https://api.sweetbook.com/docs/api/credits/
------------------------------------------------------------

# Credits API

충전금 잔액 조회 API와 충전금 시스템의 동작 방식을 안내합니다.

모든 Credits API는 인증이 필요합니다. API Key를 `Authorization: Bearer <API_KEY>` 헤더로 제공하세요.
## 충전금 잔액 조회

GET`/v1/credits`현재 파트너 계정의 충전금 잔액을 조회합니다. API Key의 환경(Sandbox/Live)에 따라 해당 환경의 잔액이 반환됩니다.


### 응답 필드

| 필드 | 타입 | 설명 |
| --- | --- | --- |
| accountUid | string | 계정 고유 UID |
| balance | number | 현재 충전금 잔액 (원) |
| currency | string | 통화 코드 (항상 "KRW") |
| env | string | 환경 ("test" 또는 "live") |
| createdAt | datetime | 계정 생성 일시 |
| updatedAt | datetime | 잔액 마지막 변경 일시 |

**환경 분리:** Sandbox와 Live 환경의 충전금은 완전히 분리되어 있습니다. 사용하는 API Key에 따라 해당 환경의 잔액만 반환됩니다.RequestSandboxLiveCopy```
curl 'https://api-sandbox.sweetbook.com/v1/credits' \
  -H 'Authorization: Bearer YOUR_API_KEY'
```

Response (200 OK)Copy```
{
  "success": true,
  "message": "Success",
  "data": {
    "accountUid": "acc_abc123xyz",
    "balance": 100000,
    "currency": "KRW",
    "env": "test",
    "createdAt": "2026-01-01T00:00:00Z",
    "updatedAt": "2026-03-01T10:00:00Z"
  }
}
```


## 크레딧 거래 내역 조회

GET`/v1/credits/transactions`본인 계정의 크레딧 거래 내역(충전, 차감, 환불 등)을 조회합니다. API Key의 환경(Sandbox/Live)에 따라 해당 환경의 내역이 반환됩니다.


### Query Parameters

| 파라미터 | 타입 | 기본값 | 설명 |
| --- | --- | --- | --- |
| limit | int | 20 | 조회할 항목 수 (최대 100) |
| offset | int | 0 | 건너뛸 항목 수 |
| createdFrom | string | - | 조회 시작일 (ISO 8601) |
| createdTo | string | - | 조회 종료일 (ISO 8601) |


### 응답 필드

| 필드 | 타입 | 설명 |
| --- | --- | --- |
| transactionId | string | 거래 고유 ID |
| accountUid | string | 계정 고유 UID |
| reasonCode | number | 거래 사유 코드 (아래 표 참고) |
| reasonDisplay | string | 거래 사유 설명 (사람이 읽을 수 있는 형식) |
| direction | string | 거래 방향 (credit 충전, debit 차감) |
| amount | number | 거래 금액 (원, 절댓값) |
| balanceAfter | number | 거래 후 잔액 (원) |
| memo | string | 거래 메모 |
| isTest | boolean | 테스트 환경 거래 여부 |
| createdAt | datetime | 거래 일시 |


### reasonCode 목록

| 코드 | 설명 |
| --- | --- |
| 1 | CREDIT_RECHARGE — 결제 충전 |
| 2 | CREDIT_GRANT — 자동 보상 (가입 보너스 등) |
| 3 | ORDER_PAYMENT — 주문 결제 차감 |
| 4 | ORDER_REFUND — 주문 환불 |
| 7 | ORDER_CANCEL_REFUND — 주문 취소 환불 |
| 9 | SANDBOX_CHARGE — Sandbox 테스트 충전 |
| 10 | SANDBOX_DEDUCT — Sandbox 테스트 차감 |
| 11 | ORDER_RESTORE_DEDUCT — 주문 복원 시 재차감 |

거래 내역에 위 목록 외의 코드가 표시될 수 있습니다. 이는 시스템에서 자동 처리된 항목입니다.

RequestSandboxLiveCopy```
curl 'https://api-sandbox.sweetbook.com/v1/credits/transactions?limit=10' \
  -H 'Authorization: Bearer YOUR_API_KEY'
```

ResponseCopy```
{
  "success": true,
  "message": "Success",
  "data": {
    "transactions": [
      {
        "transactionId": "tx_abc123xyz",
        "accountUid": "acc_abc123xyz",
        "reasonCode": 2,
        "reasonDisplay": "주문 결제",
        "direction": "debit",
        "amount": 23800,
        "balanceAfter": 76200,
        "memo": "주문 결제 (or_xyz789)",
        "isTest": false,
        "createdAt": "2026-03-01T10:00:00Z"
      },
      {
        "transactionId": "tx_def456uvw",
        "accountUid": "acc_abc123xyz",
        "reasonCode": 9,
        "reasonDisplay": "Sandbox 충전",
        "direction": "credit",
        "amount": 100000,
        "balanceAfter": 100000,
        "memo": "테스트 충전",
        "isTest": true,
        "createdAt": "2026-02-28T09:00:00Z"
      }
    ],
    "total": 2,
    "limit": 10,
    "offset": 0
  }
}
```


## Sandbox 크레딧 충전 (테스트용)

POST`/v1/credits/sandbox/charge`테스트 목적으로 크레딧을 충전합니다. 항상 test 크레딧에 적용됩니다 (API Key 환경과 무관).


### Request Body

| 필드 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| amount | number | Y | 충전할 금액 (원, 양수) |
| memo | string | N | 충전 메모 (최대 200자) |

**Idempotency-Key 지원:** `Idempotency-Key` 헤더를 사용하면 동일한 충전 요청이 중복 처리되지 않습니다. 재시도가 필요한 경우 반드시 활용하세요.RequestCopy```
curl -X POST 'https://api-sandbox.sweetbook.com/v1/credits/sandbox/charge' \
  -H 'Authorization: Bearer YOUR_SANDBOX_API_KEY' \
  -H 'Idempotency-Key: charge-test-001' \
  -H 'Content-Type: application/json' \
  -d '{
  "amount": 100000,
  "memo": "테스트 충전"
}'
```

ResponseCopy```
{
  "success": true,
  "message": "충전 완료",
  "data": {
    "transactionUid": "tx_sandbox_abc123",
    "amount": 100000,
    "balanceAfter": 200000,
    "currency": "KRW"
  }
}
```


## Sandbox 크레딧 차감 (테스트용)

POST`/v1/credits/sandbox/deduct`테스트 목적으로 크레딧을 차감합니다. 잔액 부족 시나리오 등을 테스트할 때 사용합니다.항상 test 크레딧에 적용됩니다 (API Key 환경과 무관).


### Request Body

| 필드 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| amount | number | Y | 차감할 금액 (원, 양수) |
| memo | string | N | 차감 메모 (최대 200자) |

**Idempotency-Key 지원:** `Idempotency-Key` 헤더를 사용하면 동일한 차감 요청이 중복 처리되지 않습니다.RequestCopy```
curl -X POST 'https://api-sandbox.sweetbook.com/v1/credits/sandbox/deduct' \
  -H 'Authorization: Bearer YOUR_SANDBOX_API_KEY' \
  -H 'Idempotency-Key: deduct-test-001' \
  -H 'Content-Type: application/json' \
  -d '{
  "amount": 50000,
  "memo": "잔액 부족 시나리오 테스트"
}'
```

ResponseCopy```
{
  "success": true,
  "message": "차감 완료",
  "data": {
    "transactionUid": "tx_sandbox_def456",
    "amount": -50000,
    "balanceAfter": 150000,
    "currency": "KRW"
  }
}
```


## 충전금 시스템 개요

SweetBook은 선불 충전금 방식으로 도서 제작 비용을 결제합니다. Sandbox 충전금과 Live 충전금은 별도로 관리됩니다.

| 구분 | 설명 | 충전 방법 |
| --- | --- | --- |
| Sandbox 충전금 | 파트너 포털에서 직접 원하는 금액을 입력하여 충전 가능 | 파트너 포털 |
| Live 충전금 | 파트너 포털에서 PG 결제를 통해 충전 | 파트너 포털 (PG 결제) |

**Live 충전금** 충전은 **파트너 포털에서만** 가능합니다. Sandbox 환경에서는 API(`POST /credits/sandbox/charge`)를 통해 테스트 충전을 할 수 있습니다.
## 충전금 사용

충전금은 주문 생성 시 자동으로 차감되며, 주문 취소 시 즉시 환불됩니다.

- 차감: 주문 생성(POST /orders) 시 총 금액(상품금액 + 배송비 + 포장비, 10% VAT 포함)이 즉시 차감됩니다.
- 환불: 주문 취소(POST /orders/{orderUid}/cancel) 시 결제 금액이 즉시 충전금으로 환불됩니다.
- 사전 확인: 주문 생성 전에 GET /credits로 잔액을 확인하는 것을 권장합니다.


## 잔액 부족 (402 Payment Required)

충전금 잔액이 부족한 상태에서 주문을 생성하면 402 Payment Required 에러가 반환됩니다.

이 에러가 발생하면 파트너 포털에서 충전금을 충전한 후 다시 시도하세요.

Error responseCopy```
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


## 관련 문서

- 충전금 시스템 — 비용 계산, 거래 유형 상세
- Orders API — 주문 생성 및 관리
- 에러 코드 레퍼런스 — HTTP 상태 코드 및 에러 응답


------------------------------------------------------------
## API 레퍼런스 > Webhooks
**URL**: https://api.sweetbook.com/docs/api/webhooks/
------------------------------------------------------------

# Webhooks API

웹훅을 설정하여 주문 상태 변경 등의 이벤트를 실시간으로 수신하는 방법을 안내합니다.


## 웹훅이란?

웹훅은 특정 이벤트 발생 시 등록된 URL로 HTTP POST 요청을 보내는 방식입니다. 주문 상태를 주기적으로 폴링하지 않아도 실시간으로 변경 사항을 수신할 수 있습니다.

- 이벤트 발생 (주문 결제 완료)
- SweetBook 서버가 등록된 URL로 HTTP POST 전송
- 수신 서버가 200 OK 응답
- 전송 완료 (SUCCESS)

**Sandbox 환경:** 웹훅 이벤트는 Live와 Sandbox 환경 모두에서 발생합니다. 페이로드의 `isTest` 필드로 Sandbox 이벤트 여부를 구분할 수 있습니다.
## 이벤트 종류

| 이벤트 | 발생 시점 | 활용 예시 |
| --- | --- | --- |
| order.created | 주문 생성 (충전금 차감 완료) | 주문 접수 알림, 내부 시스템 동기화 |
| order.cancelled | 주문 취소 | 환불 처리, 재고 복원 |
| order.restored | 주문 복원 (취소 철회) | 복원된 주문 재처리 |
| production.confirmed | 제작 확정 | 제작 시작 안내 |
| production.started | 제작 시작 | 제작 진행 상태 업데이트 |
| production.completed | 제작 완료 | 배송 준비 안내 |
| shipping.departed | 발송 완료 | 배송 추적 시작, 고객 알림 |
| shipping.delivered | 배송 완료 | 배송 완료 안내, 리뷰 요청 |

각 이벤트의 페이로드 구조와 JSON 예시는 [Webhook Events 레퍼런스](/docs/api/webhook-events/)를 참고하세요.
## 웹훅 설정하기


### 1. 웹훅 등록

PUT /webhooks/config로 수신 URL을 등록합니다. 최초 등록 시 secretKey가 자동 생성됩니다.

| 필드 | 필수 | 설명 |
| --- | --- | --- |
| webhookUrl | Y | 수신 URL (HTTPS만 허용, 최대 500자) |
| events | N | 구독할 이벤트 목록. null이면 전체 이벤트 구독 |
| description | N | 설명 (최대 200자) |

**secretKey는 최초 등록 시에만 전체 값이 반환됩니다.** 이후 조회 시에는 앞 8자만 노출됩니다 (예: `whsk_a1b...`). 발급 즉시 안전한 곳에 저장하세요.RequestSandboxLiveCopy```
curl -X PUT 'https://api-sandbox.sweetbook.com/v1/webhooks/config' \
  -H 'Authorization: Bearer YOUR_API_KEY' \
  -H 'Content-Type: application/json' \
  -d '{
  "webhookUrl": "https://example.com/webhooks/sweetbook",
  "events": ["order.created", "shipping.departed"],
  "description": "주문 알림 수신"
}'
```


### 2. 설정 조회/수정

GET /webhooks/config로 현재 설정을 확인할 수 있습니다. 설정을 변경하려면 PUT /webhooks/config를 다시 호출하면 됩니다. 기존 secretKey는 유지되며, 수정 응답에는 전체 secretKey가 포함됩니다.


### 3. 웹훅 해제

DELETE /webhooks/config로 웹훅을 비활성화합니다. 기존 전송 이력은 유지됩니다.


## 전송 헤더

웹훅 요청에는 다음 4개의 헤더가 포함됩니다.

| 헤더 | 설명 | 예시 |
| --- | --- | --- |
| X-Webhook-Signature | HMAC-SHA256 서명값 (sha256= 접두사 포함) | sha256=a1b2c3d4... |
| X-Webhook-Timestamp | 서명 생성 시점 (Unix timestamp, 초) | 1709280000 |
| X-Webhook-Event | 이벤트 타입 | order.created |
| X-Webhook-Delivery | 전송 고유 ID | wh_abc123xyz |


## 서명 검증 (HMAC-SHA256)

수신한 웹훅 요청이 SweetBook에서 보낸 것인지 확인하려면 서명을 검증해야 합니다. 서명은 {timestamp}.{payload} 형식의 문자열을 secretKey로 HMAC-SHA256 해시한 값입니다.

Signature FormulaCopy```
서명 페이로드 = "{timestamp}.{JSON body}"
기대값 = "sha256=" + HMAC-SHA256(secretKey, 서명 페이로드)
검증 = 기대값 == X-Webhook-Signature 헤더값 (sha256={hex} 형식)
```


### JavaScript (Express.js)

Node.jsCopy```
const crypto = require('crypto');

function verifySignature(payload, signature, timestamp, secretKey) {
  const signPayload = `${timestamp}.${payload}`;
  const expectedHex = crypto
    .createHmac('sha256', secretKey)
    .update(signPayload)
    .digest('hex');
  const expected = `sha256=${expectedHex}`;
  return crypto.timingSafeEqual(
    Buffer.from(signature),
    Buffer.from(expected)
  );
}

app.post('/webhooks/sweetbook', express.json(), (req, res) => {
  const signature = req.headers['x-webhook-signature'];
  const timestamp = req.headers['x-webhook-timestamp'];
  const event = req.headers['x-webhook-event'];
  const payload = JSON.stringify(req.body);

  if (!verifySignature(payload, signature, timestamp, SECRET_KEY)) {
    return res.status(401).json({ error: 'Invalid signature' });
  }

  // 이벤트 처리
  switch (event) {
    case 'order.created':
      console.log('주문 생성 완료:', req.body);
      break;
    case 'shipping.departed':
      console.log('발송 완료:', req.body);
      break;
  }

  res.status(200).json({ received: true });
});
```


### Python (Flask)

서명 비교 시 반드시 타이밍 공격을 방지하는 함수를 사용하세요. JavaScript: `crypto.timingSafeEqual()`, Python: `hmac.compare_digest()`PythonCopy```
import hmac
import hashlib
from flask import Flask, request, jsonify

app = Flask(__name__)
SECRET_KEY = "whsk_your_secret_key"

def verify_signature(payload, signature, timestamp, secret_key):
    sign_payload = f"{timestamp}.{payload}"
    expected_hex = hmac.new(
        secret_key.encode(),
        sign_payload.encode(),
        hashlib.sha256
    ).hexdigest()
    expected = f"sha256={expected_hex}"
    return hmac.compare_digest(signature, expected)

@app.route('/webhooks/sweetbook', methods=['POST'])
def handle_webhook():
    signature = request.headers.get('X-Webhook-Signature')
    timestamp = request.headers.get('X-Webhook-Timestamp')
    event = request.headers.get('X-Webhook-Event')
    payload = request.get_data(as_text=True)

    if not verify_signature(payload, signature, timestamp, SECRET_KEY):
        return jsonify({"error": "Invalid signature"}), 401

    # 이벤트 처리
    data = request.get_json()
    if event == 'order.created':
        print(f"주문 생성 완료: {data}")
    elif event == 'shipping.departed':
        print(f"발송 완료: {data}")

    return jsonify({"received": True}), 200
```


## 테스트하기

POST /webhooks/test로 테스트 이벤트를 전송하여 수신 서버가 정상 동작하는지 확인할 수 있습니다. 샘플 데이터가 전송되며, 실제 주문 데이터는 포함되지 않습니다.

테스트 전송은 재시도되지 않습니다. 실패 시 응답에서 `responseStatus`와 `responseBody`를 확인하여 문제를 진단하세요.RequestSandboxLiveCopy```
curl -X POST 'https://api-sandbox.sweetbook.com/v1/webhooks/test' \
  -H 'Authorization: Bearer YOUR_API_KEY' \
  -H 'Content-Type: application/json' \
  -d '{"eventType": "order.created"}'
```

ResponseCopy```
{
  "success": true,
  "message": "Success",
  "data": {
    "deliveryUid": "wh_abc123xyz",
    "eventType": "order.created",
    "status": "SUCCESS",
    "responseStatus": 200,
    "responseBody": "{\"received\": true}"
  }
}
```


## 재시도 정책

전송 실패(2xx 외 응답 또는 타임아웃) 시 자동으로 최대 3회 재시도합니다.FAILED 상태인 건만 재시도 대상이며, PENDING 상태는 재시도되지 않습니다. HTTP 타임아웃은 30초입니다. 테스트 전송(isTest: true)은 재시도 없이 1회만 전송됩니다.

| 시도 | 대기 시간 |
| --- | --- |
| 1차 재시도 | 1분 후 |
| 2차 재시도 | 5분 후 |
| 3차 재시도 | 30분 후 |

3회 모두 실패하면 상태가 EXHAUSTED로 변경됩니다.

**EXHAUSTED 알림:** 모든 재시도가 소진되면 `webhook.exhausted` 이벤트가 트리거됩니다. 동일 알림은 **1시간 쿨다운**이 적용되어 과도한 알림이 발생하지 않습니다.
### 전송 상태

| 상태 | 설명 |
| --- | --- |
| PENDING | 전송 대기 또는 진행 중 |
| SUCCESS | 전송 성공 (2xx 응답) |
| FAILED | 전송 실패 (재시도 대기 중) |
| EXHAUSTED | 최대 재시도(3회) 초과 |


## 전송 이력 확인

GET /webhooks/deliveries로 전송 이력을 조회할 수 있습니다. eventType과 status로 필터링할 수 있습니다.

RequestSandboxLiveCopy```
# 실패한 전송 이력만 조회
curl 'https://api-sandbox.sweetbook.com/v1/webhooks/deliveries?status=FAILED&limit=10' \
  -H 'Authorization: Bearer YOUR_API_KEY'
```


## 수신 서버 구현 시 유의사항

- 수신 서버는 200~299 상태 코드로 응답해야 합니다. 그 외 응답은 실패로 처리됩니다.
- 30초 이내에 응답해야 합니다. 시간이 오래 걸리는 작업은 비동기로 처리하세요.
- X-Webhook-Signature를 반드시 검증하여 위변조 요청을 차단하세요.
- 같은 이벤트가 중복 전송될 수 있습니다. X-Webhook-Delivery 헤더로 중복 여부를 확인하세요.
- 수신 URL은 HTTPS만 허용됩니다.


## 관련 문서

- Orders API — 주문 생성 및 관리
- 인증 가이드 — API Key 발급


------------------------------------------------------------
## API 레퍼런스 > Webhook Events
**URL**: https://api.sweetbook.com/docs/api/webhook-events/
------------------------------------------------------------

# Webhook Events 레퍼런스

SweetBook API에서 발생하는 8가지 웹훅 이벤트의 페이로드 구조와 예시를 안내합니다.


## 공통 페이로드 구조

모든 웹훅 이벤트는 아래의 공통 필드를 포함합니다.

| 필드 | 타입 | 설명 |
| --- | --- | --- |
| event | string | 이벤트 타입 (예: order.created) |
| orderUid | string | 주문 고유 ID (예: or_a1b2c3d4) |
| status | string | 현재 주문 상태 |
| timestamp | string | 이벤트 발생 시각 (ISO 8601) |
| isTest | boolean | Sandbox 환경 여부 |


## 전송 헤더

모든 웹훅 요청에는 다음 헤더가 포함됩니다. 서명 검증 시 반드시 확인하세요.

| 헤더 | 설명 | 예시 |
| --- | --- | --- |
| X-Webhook-Signature | HMAC-SHA256 서명값 (sha256= 접두사 포함) | sha256=e3b0c44298fc1c14... |
| X-Webhook-Timestamp | 서명 생성 시점 (Unix timestamp, 초) | 1709280000 |
| X-Webhook-Event | 이벤트 타입 | order.created |
| X-Webhook-Delivery | 전송 고유 ID (중복 수신 확인용) | wh_d7e8f9a0b1c2 |


## 전송 상태 (Delivery Status)

| 상태 | 설명 |
| --- | --- |
| PENDING | 전송 대기 또는 진행 중 |
| SUCCESS | 전송 성공 (수신 서버가 2xx 응답) |
| FAILED | 전송 실패 (재시도 대기 중, 최대 3회) |
| EXHAUSTED | 최대 재시도 횟수(3회) 초과 — 수동 확인 필요 |


## order.created — 주문 생성 (충전금 차감 완료)

주문이 생성되고 충전금 차감이 완료되면 발생합니다. 내부 시스템에 주문 접수를 동기화하거나, 고객에게 주문 접수 알림을 보낼 때 활용합니다.


### 주요 필드

| 필드 | 설명 |
| --- | --- |
| bookUid | 제작 대상 도서 ID |
| quantity | 주문 수량 |
| totalCredits | 차감된 충전금 합계 |
| shippingAddress | 배송지 정보 |

order.createdCopy```
{
  "event": "order.created",
  "orderUid": "or_8f3a2b1c",
  "bookUid": "bk_e4d5c6b7",
  "status": "PAID",
  "quantity": 2,
  "totalCredits": 35000,
  "shippingAddress": {
    "recipientName": "홍길동",
    "phone": "010-1234-5678",
    "zipCode": "06234",
    "address1": "서울특별시 강남구 테헤란로 123",
    "address2": "4층 401호"
  },
  "isTest": false,
  "timestamp": "2025-03-15T10:30:00Z"
}
```


## order.cancelled — 주문 취소

주문이 취소되면 발생합니다. 취소 사유와 충전금 환불 정보가 포함됩니다. 환불 처리나 내부 재고 복원 로직에 활용합니다.


### 주요 필드

| 필드 | 설명 |
| --- | --- |
| cancelledAt | 취소 시각 |
| cancelReason | 취소 사유 |
| refundedCredits | 환불된 충전금 금액 |

order.cancelledCopy```
{
  "event": "order.cancelled",
  "orderUid": "or_8f3a2b1c",
  "bookUid": "bk_e4d5c6b7",
  "status": "CANCELLED",
  "cancelledAt": "2025-03-16T11:20:00Z",
  "cancelReason": "고객 요청에 의한 취소",
  "refundedCredits": 35000,
  "isTest": false,
  "timestamp": "2025-03-16T11:20:00Z"
}
```


## order.restored — 주문 복원

취소된 주문이 복원(취소 철회)되면 발생합니다. 복원 시 충전금이 다시 차감됩니다.


### 주요 필드

| 필드 | 설명 |
| --- | --- |
| restoredAt | 복원 시각 |
| deductedCredits | 복원 시 재차감된 충전금 |

order.restoredCopy```
{
  "event": "order.restored",
  "orderUid": "or_8f3a2b1c",
  "bookUid": "bk_e4d5c6b7",
  "status": "PAID",
  "restoredAt": "2025-03-16T13:00:00Z",
  "deductedCredits": 35000,
  "isTest": false,
  "timestamp": "2025-03-16T13:00:00Z"
}
```


## production.confirmed — 제작 확정

주문이 검수를 통과하여 제작이 확정되면 발생합니다. 고객에게 제작 시작 안내를 보내거나, 예상 완료일을 표시할 때 활용합니다.


### 주요 필드

| 필드 | 설명 |
| --- | --- |
| confirmedAt | 제작 확정 시각 |
| estimatedShipDate | 예상 발송일 |

production.confirmedCopy```
{
  "event": "production.confirmed",
  "orderUid": "or_8f3a2b1c",
  "bookUid": "bk_e4d5c6b7",
  "status": "CONFIRMED",
  "confirmedAt": "2025-03-15T14:00:00Z",
  "estimatedShipDate": "2025-03-20",
  "isTest": false,
  "timestamp": "2025-03-15T14:00:00Z"
}
```


## production.started — 제작 시작

인쇄 제작이 시작되면 발생합니다. 제작 진행 중임을 고객에게 안내할 때 활용합니다.


### 주요 필드

| 필드 | 설명 |
| --- | --- |
| startedAt | 제작 시작 시각 |

production.startedCopy```
{
  "event": "production.started",
  "orderUid": "or_8f3a2b1c",
  "bookUid": "bk_e4d5c6b7",
  "status": "IN_PRODUCTION",
  "startedAt": "2025-03-17T09:00:00Z",
  "isTest": false,
  "timestamp": "2025-03-17T09:00:00Z"
}
```


## production.completed — 제작 완료

모든 제작이 완료되어 배송 준비 단계에 진입하면 발생합니다.


### 주요 필드

| 필드 | 설명 |
| --- | --- |
| completedAt | 제작 완료 시각 |

production.completedCopy```
{
  "event": "production.completed",
  "orderUid": "or_8f3a2b1c",
  "bookUid": "bk_e4d5c6b7",
  "status": "PRODUCTION_COMPLETE",
  "completedAt": "2025-03-19T17:30:00Z",
  "isTest": false,
  "timestamp": "2025-03-19T17:30:00Z"
}
```


## shipping.departed — 발송 완료

제작이 완료되어 택배사에 인계되면 발생합니다. 운송장 번호(trackingNumber)와 택배사 정보(trackingCarrier)가 포함되어 배송 추적을 시작하거나 고객에게 발송 알림을 보낼 때 활용합니다.


### 주요 필드

| 필드 | 설명 |
| --- | --- |
| trackingNumber | 운송장 번호 |
| trackingCarrier | 택배사 코드 (예: CJ, HANJIN, LOTTE) |
| shippedAt | 발송 시각 |

shipping.departedCopy```
{
  "event": "shipping.departed",
  "orderUid": "or_8f3a2b1c",
  "bookUid": "bk_e4d5c6b7",
  "status": "SHIPPED",
  "trackingNumber": "1234567890123",
  "trackingCarrier": "CJ",
  "shippedAt": "2025-03-20T16:45:00Z",
  "isTest": false,
  "timestamp": "2025-03-20T16:45:00Z"
}
```


## shipping.delivered — 배송 완료

배송이 완료되면 발생합니다. 배송 완료 안내 또는 리뷰 요청에 활용합니다.


### 주요 필드

| 필드 | 설명 |
| --- | --- |
| deliveredAt | 배송 완료 시각 |

shipping.deliveredCopy```
{
  "event": "shipping.delivered",
  "orderUid": "or_8f3a2b1c",
  "bookUid": "bk_e4d5c6b7",
  "status": "DELIVERED",
  "deliveredAt": "2025-03-22T14:00:00Z",
  "isTest": false,
  "timestamp": "2025-03-22T14:00:00Z"
}
```


## 관련 문서

- Webhooks 연동 가이드 — 웹훅 설정, 서명 검증, 재시도 정책
- Orders API — 주문 생성 및 관리


------------------------------------------------------------
## API 레퍼런스 > Errors
**URL**: https://api.sweetbook.com/docs/api/errors/
------------------------------------------------------------

# 에러 코드 레퍼런스

SweetBook API에서 반환하는 HTTP 상태 코드와 에러 응답 형식을 안내합니다.


## HTTP 상태 코드

SweetBook API는 다음 HTTP 상태 코드를 사용합니다.

| 코드 | 설명 | 비고 |
| --- | --- | --- |
| 200 | 성공 | 요청이 정상적으로 처리됨 |
| 201 | 리소스 생성 성공 | 새 리소스가 생성됨 (예: 주문, 도서) |
| 400 | 잘못된 요청 | 필드 검증 실패, 잘못된 파라미터 등 |
| 401 | 인증 실패 | API Key가 없거나 유효하지 않음 |
| 402 | 충전금 부족 | 잔액이 부족하여 주문 결제 불가 |
| 403 | 권한 없음 | 해당 리소스에 대한 접근 권한 없음 |
| 404 | 리소스 없음 | 요청한 리소스를 찾을 수 없음 |
| 409 | 충돌 | 중복 요청, 멱등성 키(Idempotency Key) 충돌 |
| 429 | Rate Limit 초과 | 요청 빈도 제한 초과 |
| 500 | 서버 에러 | 서버 내부 오류 (재시도 권장) |


## 에러 응답 형식

모든 에러 응답은 동일한 JSON 구조를 따릅니다. success 필드가 false이고,message에 에러 원인이 포함됩니다.


### 기본 에러 응답

Error responseCopy```
{
  "success": false,
  "message": "Unauthorized. Invalid API key.",
  "data": null
}
```


### 필드 검증 에러 (400)

요청 본문의 필드 검증에 실패한 경우, fieldErrors 배열에 각 필드별 에러 정보가 포함됩니다.

400 Validation ErrorCopy```
{
  "success": false,
  "message": "Validation failed",
  "fieldErrors": [
    {
      "field": "email",
      "message": "Invalid email format"
    },
    {
      "field": "recipientName",
      "message": "recipientName is required"
    }
  ]
}
```


## 주요 에러 시나리오


### 인증 실패 (401)

API Key가 누락되었거나 유효하지 않은 경우 반환됩니다.

401 UnauthorizedCopy```
{
  "success": false,
  "message": "Unauthorized. Invalid API key.",
  "data": null
}
```


### 충전금 부족 (402)

주문 결제 시 충전금 잔액이 부족한 경우 반환됩니다.

402 Insufficient CreditsCopy```
{
  "success": false,
  "message": "Insufficient credits. Required: 12500, Available: 5000",
  "data": null
}
```


### 리소스 없음 (404)

요청한 리소스(도서, 주문 등)가 존재하지 않거나 접근할 수 없는 경우 반환됩니다.

404 Not FoundCopy```
{
  "success": false,
  "message": "Book not found",
  "data": null
}
```


### 멱등성 키 충돌 (409)

동일한 Idempotency-Key 헤더로 다른 내용의 요청을 보낸 경우 반환됩니다.

409 ConflictCopy```
{
  "success": false,
  "message": "Idempotency key conflict. A different request was already processed with this key.",
  "data": null
}
```


### Rate Limit 초과 (429)

요청 빈도 제한을 초과한 경우 반환됩니다. Retry-After 헤더를 확인하세요.

429 Too Many RequestsCopy```
{
  "success": false,
  "message": "Rate limit exceeded. Please retry after 60 seconds.",
  "data": null
}
```


### 서버 에러 (500)

서버 내부 오류가 발생한 경우 반환됩니다. 잠시 후 재시도하거나 지속될 경우 지원팀에 문의하세요.

500 Internal Server ErrorCopy```
{
  "success": false,
  "message": "Internal server error",
  "data": null
}
```


## 에러 처리 권장사항

- 4xx 에러: 요청 내용을 수정한 후 재시도하세요. 동일한 요청을 반복해도 같은 에러가 발생합니다.
- 429 에러: Retry-After 헤더 값만큼 대기 후 재시도하세요. Exponential Backoff를 적용하는 것을 권장합니다.
- 500 에러: 서버 측 문제이므로 잠시 후 재시도하세요. 지속될 경우 지원팀에 문의하세요.
- 필드 에러: fieldErrors 배열을 파싱하여 사용자에게 구체적인 수정 안내를 제공하세요.


## 관련 문서

- Rate Limiting — 요청 빈도 제한 안내
- 충전금 시스템 — 충전금 관리 및 잔액 조회
- 인증 가이드 — API Key 발급 및 인증


================================================================================
# 운영 가이드
================================================================================


------------------------------------------------------------
## 운영 가이드 > 충전금
**URL**: https://api.sweetbook.com/docs/operations/credits/
------------------------------------------------------------

# 충전금 관리

환경별 충전금 운영 방법, 잔액 확인, 차감/환불 규칙, 모니터링 권장사항을 안내합니다.


## Sandbox 충전금

Sandbox 환경에서는 파트너 포털의 충전금 관리 메뉴에서 Sandbox 충전금을 충전할 수 있습니다. Sandbox 충전금은 실제 돈이 아니며, 원하는 금액만큼 충전할 수 있습니다.

Sandbox 충전금이 소진되어도 파트너 포털에서 충전할 수 있습니다. Sandbox 환경의 충전금은 Live 환경과 완전히 분리되어 있습니다.
## Real 충전금 (Live)

Live 환경에서는 파트너 포털에서 PG 결제를 통해 실제 충전금을 충전합니다. 충전된 금액은 주문 생성 시 자동으로 차감됩니다.

**환경 분리:** Sandbox와 Live 환경의 충전금은 완전히 분리되어 있습니다. Sandbox에서 사용한 충전금은 Live에 영향을 주지 않습니다.
## 잔액 조회

GET /credits API로 현재 충전금 잔액을 조회할 수 있습니다.

RequestSandboxLiveCopy```
curl 'https://api-sandbox.sweetbook.com/v1/credits/balance' \
  -H 'Authorization: Bearer YOUR_SANDBOX_API_KEY'
```

ResponseCopy```
{
  "success": true,
  "message": "Success",
  "data": {
    "paidCreditAmount": 150000,
    "freeCreditAmount": 10000,
    "totalCreditAmount": 160000
  }
}
```


## 충전금 차감

주문 생성 시 충전금이 자동으로 차감됩니다. 차감 금액은 주문 금액에 10% VAT가 포함된 금액입니다.

충전금은 주문 생성(`POST /orders`) 시점에 즉시 차감됩니다. 잔액이 부족하면 `402 Payment Required` 에러가 반환됩니다.Deduction formulaCopy```
차감 금액 = 주문 금액 (ProductAmount + ShippingFee + PackagingFee) + 10% VAT
```


## 충전금 환불

주문 취소 시 충전금이 즉시 환불됩니다. 파트너가 직접 취소할 수 있는 상태는PAID(20)와 PDF_READY(25)입니다.

| 취소 시점 | 환불 여부 | 환불 속도 |
| --- | --- | --- |
| PAID (20) | 전액 환불 | 즉시 |
| PDF_READY (25) | 전액 환불 | 즉시 |


## 모니터링 권장사항

- 주문 전 잔액 확인: 주문 생성 전에 GET /credits/balance로 잔액을 확인하세요.
- 잔액 부족 알림 설정: 잔액이 일정 기준 이하로 떨어지면 알림을 보내도록 설정하세요.
- 거래 내역 모니터링: GET /credits/transactions로 정기적으로 거래 내역을 확인하세요.


## 402 에러 처리 패턴

충전금이 부족한 상태에서 주문을 생성하면 402 Payment Required가 반환됩니다. 다음 패턴으로 처리하는 것을 권장합니다.

Node.jsCopy```
async function createOrderWithBalanceCheck(orderData) {
  // 1. 잔액 확인
  const balance = await fetch('/v1/credits/balance', {
    headers: { 'Authorization': 'Bearer YOUR_API_KEY' }
  }).then(res => res.json());

  if (balance.data.totalCreditAmount < estimatedAmount) {
    // 충전 필요 알림
    throw new Error('충전금이 부족합니다. 파트너 포털에서 충전해주세요.');
  }

  // 2. 주문 생성
  const response = await fetch('/v1/orders', {
    method: 'POST',
    headers: { 'Authorization': 'Bearer YOUR_API_KEY' },
    body: JSON.stringify(orderData)
  });

  if (response.status === 402) {
    // 잔액 부족 — 충전 후 재시도
    throw new Error('충전금이 부족합니다. 충전 후 다시 시도해주세요.');
  }

  return response.json();
}
```


## 관련 문서

- 충전금 시스템 — 충전금 거래 유형 및 비용 계산
- Orders API — 주문 생성 및 관리
- 에러 코드 레퍼런스 — HTTP 상태 코드 및 에러 응답
- 주문 상태 흐름 — 상태별 동작 및 취소 규칙


------------------------------------------------------------
## 운영 가이드 > 주문 상태
**URL**: https://api.sweetbook.com/docs/operations/order-status/
------------------------------------------------------------

# 주문 상태 흐름

주문의 전체 상태 흐름, 웹훅 이벤트 매핑, 취소 규칙, Sandbox 동작 차이를 안내합니다.


## 상태 흐름도

주문은 다음과 같은 순서로 상태가 전이됩니다.

PAID (20)→PDF_READY (25)→CONFIRMED (30)→IN_PRODUCTION (40)→PRODUCTION_COMPLETE (50)→SHIPPED (60)→DELIVERED (70)파트너 취소:PAID / PDF_READY→CANCELLED_REFUND (81)관리자 취소:SHIPPED 이전 상태→CANCELLED (80) / CANCELLED_REFUND (81)
## 상태 코드 전체 목록

| 코드 | 상태 | 설명 |
| --- | --- | --- |
| 20 | PAID | 결제 완료 (충전금 차감) |
| 25 | PDF_READY | PDF 생성 완료 |
| 30 | CONFIRMED | 제작 확정 (출력일 배정) |
| 40 | IN_PRODUCTION | 제작 진행 중 |
| 50 | PRODUCTION_COMPLETE | 전체 제작 완료 |
| 60 | SHIPPED | 발송 완료 |
| 70 | DELIVERED | 배송 완료 |
| 80 | CANCELLED | 취소 |
| 81 | CANCELLED_REFUND | 취소 및 환불 완료 |


## 상태 — Webhook 이벤트 매핑

각 주문 상태 전이 시 발송되는 웹훅 이벤트와 주요 필드입니다.

| 상태 | 코드 | Webhook Event | 주요 필드 |
| --- | --- | --- | --- |
| PAID | 20 | order.paid | total_amount, item_count |
| CONFIRMED | 30 | order.confirmed | print_day |
| IN_PRODUCTION | 40 | order.status_changed | previous_status, new_status |
| PRODUCTION_COMPLETE | 50 | order.status_changed | previous_status, new_status |
| SHIPPED | 60 | order.shipped | tracking_number, tracking_carrier |
| CANCELLED / CANCELLED_REFUND | 80 / 81 | order.cancelled | cancel_reason, refund_amount |


## Sandbox 환경 동작

Sandbox 환경에서는 주문이 PAID 상태에서 멈춥니다. 실제 제작이나 배송이 진행되지 않으며, 상태 전이 테스트는 웹훅 테스트 기능을 활용하세요.

Sandbox에서는 `PAID` 이후 자동 상태 전이가 발생하지 않습니다. 웹훅 수신 테스트는 `POST /webhooks/test`를 활용하세요.
## 취소 규칙

파트너가 API로 직접 취소할 수 있는 상태는 PAID(20)와 PDF_READY(25)뿐입니다. 이후 상태에서는 관리자만 취소할 수 있습니다.

| 취소 주체 | 취소 가능 상태 | 결과 상태 | 충전금 환불 |
| --- | --- | --- | --- |
| 파트너 (API) | PAID (20), PDF_READY (25) | CANCELLED_REFUND (81) | 즉시 환불 |
| 관리자 | SHIPPED (60) 이전까지 | CANCELLED (80) / CANCELLED_REFUND (81) | 관리자 판단에 따름 |


## 제작 및 배송 SLA

| 단계 | 소요 기간 | 비고 |
| --- | --- | --- |
| 제작 (CONFIRMED → PRODUCTION_COMPLETE) | 3~4 영업일 | 공휴일 제외 |
| 배송 (SHIPPED → DELIVERED) | 1~2일 | 한진택배 |


## 관련 문서

- Orders API — 주문 생성 및 관리
- Webhook Event Payloads — 이벤트별 페이로드 상세
- 충전금 관리 — 충전금 차감/환불 규칙
- 트러블슈팅 & FAQ — 주문 관련 문제 해결


------------------------------------------------------------
## 운영 가이드 > 트러블슈팅
**URL**: https://api.sweetbook.com/docs/operations/troubleshooting/
------------------------------------------------------------

# 트러블슈팅 & FAQ

API 연동 중 자주 발생하는 에러와 해결 방법, 자주 묻는 질문을 정리했습니다.


## 자주 발생하는 에러

아래 표에서 에러 상황별 원인과 해결 방법을 확인하세요.

| 에러 | 원인 | 해결 방법 |
| --- | --- | --- |
| 401 Unauthorized | API Key가 잘못되었거나, 환경 URL이 맞지 않음 | API Key 확인, api-sandbox vs api URL 확인 |
| 402 Payment Required | 충전금 잔액 부족 | GET /credits/balance로 잔액 확인, 파트너 포털에서 충전 |
| 400 Validation Error | 필수 필드 누락 또는 잘못된 값 | 응답의 fieldErrors 배열에서 구체적인 필드 오류 확인 |
| 404 Not Found | 잘못된 bookUid 또는 orderUid | 생성 응답에서 받은 UID가 맞는지 확인 |
| 429 Too Many Requests | Rate Limit 초과 | Retry-After 헤더 확인 후 대기, 요청 빈도 줄이기 |
| 이미지 업로드 실패 | SVG 미지원, 파일 손상 | JPG / PNG / WebP / HEIC 형식 사용 |
| Finalization 실패 | 최소 페이지 수 미충족 | 콘텐츠 페이지를 추가하여 최소 페이지 요건 충족 |
| Webhook 미수신 | URL 접근 불가, HTTPS 미사용, 방화벽 차단 | POST /webhooks/test로 수신 테스트, HTTPS URL 확인 |
| 주문 취소 실패 | PDF_READY 이후 상태에서 취소 시도 | 파트너는 PAID / PDF_READY 상태에서만 취소 가능 |


## 자주 묻는 질문 (FAQ)

QSandbox Key로 Live URL을 호출하면?A401 Unauthorized 에러가 반환됩니다. Sandbox Key는 api-sandbox.sweetbook.com, Live Key는 api.sweetbook.com에서만 사용할 수 있습니다. URL이 올바른지 확인하세요.Q가격은 어디서 확인하나요?ASandbox 환경에서는 테스트 가격이 적용됩니다. Live 환경의 실제 단가는 협의 후 API(GET /book-specs)로 조회할 수 있습니다.QSandbox 충전금이 소진되면?A파트너 포털에서 Sandbox 충전금을 충전할 수 있습니다. Sandbox 충전금은 실제 돈이 아니므로 개발 및 테스트 기간 동안 부담 없이 사용하세요.QSandbox 데이터가 Live로 이관되나요?A아니요. Sandbox와 Live 환경은 완전히 분리되어 있습니다. 도서, 주문, 충전금, 웹훅 설정 등 모든 데이터가 독립적으로 관리됩니다.QAPI Key가 노출되면?A즉시 파트너 포털에서 해당 API Key를 폐기하고 새로운 Key를 재발급하세요. 노출된 Key로 발생한 피해는 복구가 어려울 수 있으므로 빠른 대응이 중요합니다.Q배송 추적은 어떻게 하나요?A주문이 발송되면 order.shipped 웹훅이 발송됩니다. 페이로드에 포함된 tracking_number와 tracking_carrier를 사용하여 택배사 사이트에서 배송을 추적할 수 있습니다.Q인쇄 불량이 발생하면?A파트너 포털에서 불량 사진을 첨부하여 접수하세요. 접수 후 3~4 영업일 내에 재제작이 진행됩니다.
## 관련 문서

- 에러 코드 레퍼런스 — HTTP 상태 코드 및 에러 응답 형식
- 충전금 관리 — 충전금 운영 및 402 에러 처리
- 주문 상태 흐름 — 상태 전이 및 취소 규칙
- Webhooks API — 웹훅 등록 및 테스트
- 인증 가이드 — API Key 발급 및 관리
- 환경 설정 — Sandbox / Live 환경 안내


================================================================================
# 개념
================================================================================


------------------------------------------------------------
## 개념 > 동적 레이아웃
**URL**: https://api.sweetbook.com/docs/concepts/dynamic-layout/
------------------------------------------------------------

# Dynamic Layout

Contents API의 동적 배치 시스템 가이드입니다. 템플릿 요소들을 페이지에 자동으로 배치하며 컬럼, 페이지, 면(left/right)을 자동으로 관리합니다.


## 개요

동적 배치 시스템은 PhotobookAPI의 핵심 기능으로, page_layout_state 테이블 기반의 상태 추적을 통해 컬럼, 페이지, 면(left/right)을 자동으로 관리하며, 텍스트의 동적 높이 계산 및 분할 기능을 지원합니다.

| 특징 | 설명 |
| --- | --- |
| 자동 배치 | 컬럼, 면, 페이지를 자동으로 선택하여 요소 배치 |
| 컬럼 시스템 | 1~3컬럼 레이아웃 지원, 슬롯 기반 배치 |
| 텍스트 분할 | splittable 속성으로 긴 텍스트 자동 분할 |
| 동적 높이 | isDynamic 속성으로 텍스트 높이 실시간 계산 |
| breakBefore 제어 | 배치 위치를 세밀하게 제어 |
| Lanes | X 범위 기반 독립 Y 흐름 (레인별 독립 배치) |
| shiftUpOnHide | 조건부 요소 숨김 시 레이아웃 자동 재배치 |
| DynamicDelta | isDynamic 요소 높이 변화에 따른 앵커 Y 보정 |


## 페이지 구조


### 양면 인쇄 구조

포토북은 양면 인쇄 구조로 되어 있으며, 각 페이지는 왼쪽(left)과 오른쪽(right) 두 면으로 구성됩니다.


### 페이지 번호 규칙 — PUR 제본 방식 (기본)

| pageNum | pageSide | 설명 | 비고 |
| --- | --- | --- | --- |
| 0 | right | 표지 (Cover) | 앞표지와 뒷표지 |
| 1 | right | 첫 내지 (First) | 오른쪽부터 시작 |
| 2 | left | 두 번째 내지 왼쪽 |  |
| 2 | right | 두 번째 내지 오른쪽 |  |


### 페이지 번호 규칙 — 기타 제본 방식 (슬림앨범, 레이플랫 등)

| pageNum | pageSide | 설명 | 비고 |
| --- | --- | --- | --- |
| 0 | right | 표지 (Cover) | 앞표지와 뒷표지 |
| 1 | left | 첫 내지 | 왼쪽부터 시작 |
| 1 | right | 첫 내지 오른쪽 |  |
| 2 | left | 두 번째 내지 왼쪽 |  |

PUR 제본: 첫 내지(pageNum=1)는 오른쪽(right)부터 시작, page_type은 "first". 기타 제본: 왼쪽(left)부터 시작, page_type은 "photo". 이후 페이지는 왼쪽(left) → 오른쪽(right) 순서로 진행.
### 페이지 JSON 파일명 규칙

| pageNum | 파일명 | 설명 |
| --- | --- | --- |
| 0 | cover.json | 표지 |
| 1 | 000.json | 첫 내지 |
| 2 | 001.json | 두 번째 내지 |
| N | {N-1:D3}.json | N번째 페이지 (3자리 숫자로 포맷) |

Page file namingCopy```
string fileName = pageNum == 0 ? "cover" : (pageNum - 1).ToString("D3");
// 저장 경로: d:\efiles\{bookid}\page\{fileName}.json
```


## 컬럼 시스템

컬럼은 페이지 한 면을 세로로 나눈 영역입니다. 템플릿의 layoutRules.flow.columns 값으로 정의됩니다. 슬롯은 0부터 시작하는 인덱스를 가집니다.


### X 좌표 계산

각 슬롯의 X 좌표는 슬롯 인덱스와 페이지 폭으로 계산됩니다. 오른쪽 면은 pageWidth만큼 오프셋이 추가됩니다.

X coordinate calculationCopy```
double slotWidth = pageWidth / totalColumns;
double xOffset = currentSlotIndex * slotWidth;
if (pageSide == "right") { xOffset += pageWidth; }

// 예시 (2컬럼, pageWidth=978px):
// 왼쪽 면, 슬롯 #0: X = 0
// 왼쪽 면, 슬롯 #1: X = 489
// 오른쪽 면, 슬롯 #0: X = 978
// 오른쪽 면, 슬롯 #1: X = 1467
```


## 페이지 마진과 컬럼 간격


### pageMargin 구조

페이지의 상하좌우 마진을 정의합니다. spine(책등), fore(바깥), head(위), tail(아래) 네 방향으로 설정합니다.

Layout definitionCopy```
{
  "layoutRules": {
    "margin": {
      "pageMargin": {
        "spine": 40,  // 책등 쪽 마진
        "fore": 30,   // 바깥쪽 마진
        "head": 20,   // 위쪽 마진
        "tail": 30    // 아래쪽 마진
      }
    }
  }
}
```


### 컬럼 폭 계산 (pageMargin + columnGap 적용)

pageMargin이 적용되면 콘텐츠 영역이 줄어들고, columnGap만큼 컬럼 사이에 간격이 생깁니다.

Column width calculationCopy```
// 1. 콘텐츠 전체 폭 계산
double contentWidth = pageWidth - (spine + fore);

// 2. 컬럼 폭 계산
double slotWidth = (contentWidth - columnGap * (columns - 1)) / columns;

// 예: 2컬럼, pageWidth=978, spine=40, fore=30, columnGap=20
// contentWidth = 978 - (40 + 30) = 908
// slotWidth = (908 - 20 * 1) / 2 = 444px
```


### 기존 vs 신규 레이아웃 비교

| 항목 | 기존 레이아웃 | 신규 레이아웃 (pageMargin + columnGap) |
| --- | --- | --- |
| 컬럼 폭 | pageWidth / columns | (contentWidth - columnGap*(columns-1)) / columns |
| 왼쪽 면 X | slotIndex * slotWidth | fore + slotIndex * (slotWidth + columnGap) + templateX |
| 오른쪽 면 X | pageWidth + slotIndex * slotWidth | pageWidth + spine + slotIndex * (slotWidth + columnGap) + templateX |
| 세로 높이 | fullPageHeight | fullPageHeight - (head + tail) |
| 첫 요소 Y | originalY | head + originalY |

`pageMargin`이 정의되어 있으면 값이 모두 0이어도 신규 레이아웃이 적용됩니다. 1컬럼 템플릿에서는 `columnGap`이 무시됩니다.
## breakBefore 파라미터

| 값 | 동작 | 사용 시나리오 |
| --- | --- | --- |
| none (기본값) | 이전 콘텐츠 바로 다음에 배치 | 연속된 콘텐츠, 텍스트 플로우 |
| column | 다음 컬럼(슬롯)으로 이동 후 배치 | 컬럼 구분, 섹션 시작 |
| page | 다음 면 또는 페이지로 이동 후 배치 | 챕터 시작, 중요 콘텐츠 |

RequestCopy```
# none: 이어서 배치 (기본값)
POST /books/{bookUid}/contents?breakBefore=none

# column: 다음 컬럼으로 이동
POST /books/{bookUid}/contents?breakBefore=column

# page: 다음 페이지로 이동
POST /books/{bookUid}/contents?breakBefore=page
```


## 텍스트 요소 속성


### isDynamic

isDynamic: true일 때 실제 텍스트 내용에 따라 TextUtil.GetHeight()로 높이 계산합니다. 가변 길이 텍스트(일기, 리뷰, 댓글 등)에 사용합니다.


### splittable

splittable: true일 때 텍스트가 페이지/컬럼 경계를 넘으면 자동 분할합니다. 이진 탐색으로 분할 지점을 찾고, 단어 경계로 조정합니다.

| isDynamic | splittable | 동작 |
| --- | --- | --- |
| false | false | 템플릿 height 사용, 한 덩어리 배치 (기본) |
| true | false | 동적 height 계산, 한 덩어리 배치 |
| false | true | 템플릿 height 사용, 분할 배치 (비권장) |
| true | true | 동적 height 계산, 분할 배치 (권장) |

Element definitionCopy```
{
  "type": "text",
  "text": "$$userContent$$",
  "isDynamic": true,
  "splittable": true,
  "fontSize": 14,
  "width": 400,
  "height": 100
}
```


## Lanes (X-lane 기반 독립 Y 흐름)

일부 템플릿은 페이지 내에서 X 범위가 다른 영역이 독립적인 Y 흐름을 가져야 합니다.layoutRules.lanes로 정의하며, 각 레인은 독립적인 maxY를 유지합니다.

Layout definitionCopy```
{
  "layoutRules": {
    "lanes": [
      { "id": "left",  "xMin": 0,   "xMax": 155  },
      { "id": "right", "xMin": 155, "xMax": 1000 }
    ]
  }
}
```


## shiftUpOnHide (조건부 요소 숨김)

layoutRules.shiftUpOnHide: true와 요소의 visible: "$$param$$" 속성을 조합하면, 파라미터 값이 false일 때 해당 요소가 숨겨지고 아래 요소들이 위로 올라옵니다. lanes가 정의된 경우 숨겨진 요소와 같은 X-lane에 속하는 요소만 상향 이동합니다.


## DynamicDelta (isDynamic 앵커 보정)

같은 템플릿 내 요소들은 TemplateBaseY 앵커로 배치됩니다.isDynamic: true 요소의 높이가 변할 때, 그 변화량을 DynamicDelta로 누적하여 후속 요소의 Y를 보정합니다.

새 템플릿(isFirstOfTemplate)이 시작될 때마다 DynamicDelta는 0으로 리셋됩니다.

FormulaCopy```
최종 Y = max(anchoredY, sequentialY)
anchoredY = TemplateBaseY + OriginalY + DynamicDelta
DynamicDelta = Σ (실제높이 - 템플릿높이)  (각 isDynamic 요소별)
```


## itemSpacing (템플릿 간 간격)

새 템플릿의 첫 요소 배치 시, 이전 콘텐츠의 bottom Y에 itemSpacing.size만큼 간격을 추가합니다. 설정되지 않은 경우 요소의 OriginalY가 간격으로 사용됩니다.

Layout definitionCopy```
{
  "layoutRules": {
    "flow": {
      "itemSpacing": { "size": 15 }
    }
  }
}
```


## 관련 문서

- 컬럼 템플릿
- 텍스트 처리
- 갤러리 템플릿
- 요소 그룹핑
- 템플릿 엔진 스펙


------------------------------------------------------------
## 개념 > 템플릿 엔진
**URL**: https://api.sweetbook.com/docs/concepts/template-engine/
------------------------------------------------------------

# Template Engine

API 플랫폼 신규 템플릿 엔진 구조 개선을 위해 정의된 최신 템플릿 스펙입니다. visible 바인딩, shiftUpOnHide, binding/type 명확화 등을 포함합니다.


## 1. 개요

| 항목 | 내용 |
| --- | --- |
| required 프로퍼티 제거 | parameters에 정의된 모든 항목은 기본적으로 필수(required=true) |
| visible 바인딩 | Layout 요소에 visible 바인딩 처리 도입 |
| shiftUpOnHide | 레이아웃 규칙 추가 |
| binding | text / file 두 종류 |
| type | string / int / boolean / double 명확화 |


## 2. Layout 예시 (visible 제어 적용)

Layout definitionCopy```
{
  "itemIndex": "0",
  "tag": "Print",
  "width": 424,
  "height": 950.8,
  "elements": [
    {
      "element_id": "text-1",
      "type": "text",
      "position": { "x": 0, "y": 20 },
      "width": 424,
      "height": 30,
      "text": "$$dateStr$$",
      "fontFamily": "Malgun Gothic",
      "fontSize": 12,
      "textBold": true,
      "textBrush": "#FF7D90C8",
      "groupName": "group1"
    },
    {
      "element_id": "text-2",
      "type": "text",
      "position": { "x": 0, "y": 87 },
      "width": 424,
      "height": 20,
      "text": "$$contents1$$",
      "fontFamily": "Malgun Gothic",
      "fontSize": 11,
      "textBrush": "#FF000000",
      "isDynamic": true,
      "splittable": true,
      "groupName": "group1"
    },
    {
      "element_id": "graphic-3",
      "type": "graphic",
      "imageSource": "pack://siteoforigin:,,,/ebook/images/puruni/teacher.png",
      "position": { "x": 0, "y": 136 },
      "width": 50,
      "height": 15,
      "groupName": "group2",
      "visible": "$$showTeacherIcon$$"
    },
    {
      "element_id": "text-3",
      "type": "text",
      "position": { "x": 0, "y": 152 },
      "width": 424,
      "height": 150,
      "text": "$$contents2$$",
      "fontFamily": "Malgun Gothic",
      "fontSize": 11,
      "isDynamic": true,
      "splittable": true,
      "groupName": "group2",
      "visible": "$$showContents2$$"
    },
    {
      "element_id": "photo-1",
      "type": "photo",
      "fileName": "$$imageMain$$",
      "position": { "x": 0, "y": 319 },
      "width": 424,
      "height": 424
    }
  ]
}
```


## 3. Parameters 정의

Parameters definitionCopy```
{
  "definitions": {
    "dateStr":          { "binding": "text", "type": "string",  "description": "날짜 텍스트" },
    "contents1":        { "binding": "text", "type": "string",  "description": "본문 텍스트 1" },
    "contents2":        { "binding": "text", "type": "string",  "description": "본문 텍스트 2" },
    "imageMain":        { "binding": "file", "type": "string",  "description": "사진 파일" },
    "showContents2":    { "binding": "text", "type": "boolean", "description": "text-3 표시 여부" },
    "showTeacherIcon":  { "binding": "text", "type": "boolean", "description": "graphic-3 표시 여부" }
  }
}
```


## 4. Layout Rules (shiftUpOnHide 포함)


### layoutRules 속성 정리

| 속성 | 타입 | 설명 |
| --- | --- | --- |
| space | string | 배치 공간 ("page") |
| margin.pageMargin | object | 페이지 마진 (spine, fore, head, tail) |
| margin.mirrorEvenPages | boolean | 짝수 페이지에서 spine/fore 반전 여부 |
| flow.columns | int | 컬럼 수 (1~3) |
| flow.columnGap | number | 컬럼 간격 (px) |
| flow.itemSpacing.size | number | 템플릿 간 간격 (px) |
| shiftUpOnHide | boolean | 숨겨진 요소 아래 재배치 여부 |
| lanes | array | X-lane 정의 (각 레인: id, xMin, xMax) |


### shiftUpOnHide 상세 설명

visible: "$$param$$"에 바인딩된 파라미터 값이 false이면 해당 요소가 숨겨집니다.shiftUpOnHide: true일 때, 숨겨진 요소 아래의 요소를 위로 당겨 배치합니다. lanes가 정의된 경우 숨겨진 요소와 같은 X 범위(레인)에 속하는 요소만 상향 이동합니다. 자세한 내용은 요소 그룹핑 문서를 참조하세요.

Layout rulesCopy```
{
  "space": "page",
  "margin": {
    "pageMargin": { "spine": 50, "fore": 50, "head": 20, "tail": 30 },
    "mirrorEvenPages": false
  },
  "flow": {
    "columns": 2,
    "columnGap": 30,
    "itemAlign": "center",
    "itemSpacing": { "size": 10, "mode": "between" }
  },
  "shiftUpOnHide": true,
  "lanes": [
    { "id": "left",  "xMin": 0,   "xMax": 155  },
    { "id": "right", "xMin": 155, "xMax": 1000 }
  ]
}
```


## 5. binding / type 설명


### binding

API 입력값의 전달 방식을 의미합니다.

| binding | 설명 |
| --- | --- |
| text | 문자열 기반 입력 |
| file | 이미지/파일 ID 또는 URL |


### type

PAGE JSON에 저장할 때의 실제 데이터 타입을 의미합니다.

| type | 설명 |
| --- | --- |
| string | 문자열 |
| int | 정수 |
| double | 실수 |
| boolean | true/false |


### 타입 변환 예시 (fontSize)

Type conversionCopy```
// 템플릿 정의
"fontSize": { "binding": "text", "type": "int" }

// API 입력 (문자열로 전달)
"fontSize": "14"

// PAGE JSON 저장 (정수로 변환)
"fontSize": 14
```


## 6. API 호출 예시


### 둘 다 숨김

visible 파라미터에 false를 전달하여 텍스트와 아이콘 요소를 모두 숨깁니다.

RequestCopy```
{
  "dateStr": "2025-03-01",
  "contents1": "첫 번째 문단",
  "imageMain": "photo_001.jpg",
  "contents2": "",
  "showContents2": "false",
  "showTeacherIcon": "false"
}
```


### 둘 다 표시

visible 파라미터에 true를 전달하여 두 요소를 모두 표시합니다.

RequestCopy```
{
  "dateStr": "2025-03-01",
  "contents1": "첫 번째 문단",
  "imageMain": "photo_001.jpg",
  "contents2": "안녕하세요. 오늘은 봄 소풍을 다녀왔습니다.",
  "showContents2": "true",
  "showTeacherIcon": "true"
}
```


### 텍스트만 숨김, 아이콘 표시

각 요소의 visible을 개별 파라미터로 분리하여 선택적으로 제어합니다.

RequestCopy```
{
  "dateStr": "2025-03-01",
  "contents1": "첫 번째 문단",
  "imageMain": "photo_001.jpg",
  "contents2": "",
  "showContents2": "false",
  "showTeacherIcon": "true"
}
```


## 7. 최종 정리

| 항목 | 설명 |
| --- | --- |
| required 제거 | parameters에 정의된 항목은 모두 필수 |
| visible | 요소의 표시 여부를 결정 |
| shiftUpOnHide | 숨겨진 요소 아래 요소 재정렬 |
| binding | text / file |
| type | PAGE JSON의 저장 타입 |


------------------------------------------------------------
## 개념 > 요소 그루핑
**URL**: https://api.sweetbook.com/docs/concepts/element-grouping/
------------------------------------------------------------

# Element Grouping

템플릿 요소들을 그룹으로 묶어 함께 배치하는 기능입니다. 같은 그룹의 요소들은 항상 같은 컬럼/페이지에 배치됩니다.


## 개요

요소 그룹핑은 템플릿의 여러 요소를 논리적으로 묶어서, 한 컬럼이나 페이지에 함께 배치되도록 하는 기능입니다.

| 특징 | 설명 |
| --- | --- |
| 그룹 단위 배치 | 같은 그룹의 요소들은 항상 같은 컬럼/페이지에 배치 |
| 자동 이동 | 그룹 내 어떤 요소라도 배치 공간이 부족하면 그룹 전체를 다음 컬럼/페이지로 이동 |
| 텍스트 분할 지원 | splittable 텍스트는 분할 허용 (그룹 이동과 무관) |
| 유효성 검증 | 그룹 높이가 페이지 높이를 초과하면 템플릿 오류 반환 |


## 사용 방법


### 템플릿에 groupName 지정

Element definitionCopy```
{
  "elements": [
    {
      "element_id": "text-1",
      "type": "text",
      "position": {"x": 40, "y": 20},
      "width": 409,
      "height": 30,
      "text": "$dateStr$",
      "groupName": "group1"
    },
    {
      "element_id": "graphic-1",
      "type": "graphic",
      "imageSource": "pack://siteoforigin:,,,/ebook/images/bar.png",
      "position": {"x": 40, "y": 60},
      "width": 449,
      "height": 2,
      "groupName": "group1"
    },
    {
      "element_id": "text-2",
      "type": "text",
      "position": {"x": 40, "y": 87},
      "width": 409,
      "height": 150,
      "text": "$contents$",
      "isDynamic": true,
      "splittable": true,
      "groupName": "group1"
    },
    {
      "element_id": "photo-1",
      "type": "photo",
      "fileName": "$imageMain$",
      "position": {"x": 40, "y": 250},
      "width": 409,
      "height": 409,
      "groupName": "group2"
    }
  ]
}
```


## 그룹화 규칙

같은 `groupName`이라도 중간에 다른 그룹 요소가 있으면 별도 그룹으로 처리됩니다. 요소들은 Y 좌표 순으로 정렬되어 처리되므로, Y 좌표 순서를 올바르게 유지해야 합니다.Grouping rulesCopy```
// 올바른 예시: group1 요소들이 연속됨 → 하나의 그룹
[
  {"element_id": "text-1",    "y": 20,  "groupName": "group1"},
  {"element_id": "graphic-1", "y": 60,  "groupName": "group1"},
  {"element_id": "text-2",    "y": 87,  "groupName": "group1"}
]

// 잘못된 예시: group1 사이에 group2가 있음 → 2개의 별도 그룹
[
  {"element_id": "text-1",    "y": 20,  "groupName": "group1"},  // group1-1
  {"element_id": "graphic-1", "y": 60,  "groupName": "group1"},  // group1-1
  {"element_id": "photo-1",   "y": 150, "groupName": "group2"},  // group2
  {"element_id": "text-2",    "y": 300, "groupName": "group1"}   // group1-2 (별도 그룹!)
]
```


## 배치 동작


### 케이스 1: 그룹 전체가 현재 컬럼에 배치 가능

그룹 전체 높이 < 남은 공간 → 모든 요소를 현재 컬럼에 배치합니다.


### 케이스 2: 그룹 전체가 현재 컬럼에 배치 불가능

그룹 전체 높이 > 남은 공간 → 그룹 전체를 다음 컬럼/페이지로 이동합니다.


### 케이스 3: splittable 텍스트 분할

그룹 내 splittable 텍스트가 있고 최소 한 줄은 배치 가능 → 텍스트를 분할하여 현재 컬럼과 다음 컬럼에 나누어 배치합니다. 그룹의 다른 요소는 현재 위치 유지.


### 케이스 4: splittable 텍스트 한 줄도 배치 불가능

그룹 내 splittable 텍스트가 있지만 한 줄도 배치할 공간 없음 → 그룹 전체를 다음 컬럼/페이지로 이동합니다.


## 오류 처리


### 그룹 높이가 페이지 높이 초과

조건: splittable 텍스트가 없는 그룹의 전체 높이가 페이지 높이를 초과할 때.

해결 방법: 그룹 내 요소 개수 줄이기, 요소 높이 줄이기, 텍스트 요소에 splittable: true 추가.

ResponseCopy```
{
  "success": false,
  "message": "Template error: Group 'group1' height (1200.5px) exceeds page height (1000.8px). Cannot place group."
}
```


## 주의사항


### 배치 결과에서 제거되는 속성

groupName은 템플릿 작성 시에만 사용되며, 최종 페이지 JSON에는 포함되지 않습니다.splittable, isDynamic, originalHeight도 배치 결과에서 제거됩니다.


## X-lane 분리 그룹화

layoutRules.lanes가 정의된 경우, 같은 Y 범위에 있더라도 서로 다른 X-lane에 속하는 요소들은 별도 그룹으로 처리됩니다. 각 레인의 요소들은 독립적인 Y 흐름으로 배치됩니다.


## SubGroups (서브그룹)

groupName으로 묶인 그룹 내에 splittable: true 요소가 포함된 경우, non-splittable 요소들은 Y-overlap 기준으로 SubGroup으로 분리됩니다.

SubGroup exampleCopy```
// groupName: "dayEntry" 그룹 내 요소들
[
  { "element_id": "teacher-icon",    "y": 63,  "h": 22 },  // SubGroup A
  { "element_id": "teacher-label",   "y": 63,  "h": 25 },  // SubGroup A (Y 겹침)
  { "element_id": "teacher-comment", "y": 90,  "isDynamic": true, "splittable": true }, // 분리
  { "element_id": "gallery-photos",  "y": 280, "isDynamic": true }  // SubGroup B
]
// SubGroup A: teacher-icon + teacher-label (Y 범위 겹침 → 함께 배치)
// 분리: teacher-comment (splittable → 개별 배치, 텍스트 분할 가능)
// SubGroup B: gallery-photos (독립 배치)
```


## TemplateBaseY 앵커와 그룹 배치

DynamicDelta에 대한 자세한 내용은 동적 레이아웃 시스템 문서를 참조하세요.

FormulaCopy```
최종 Y = max(anchoredY, sequentialY)
anchoredY  = TemplateBaseY + OriginalY + DynamicDelta
sequentialY = CurrentSlotMaxY + spacing
```


## 요약

| 항목 | 설명 |
| --- | --- |
| 목적 | 관련 요소들을 함께 배치 |
| 사용법 | 템플릿 요소에 groupName 속성 추가 |
| 그룹화 규칙 | Y 좌표 순으로 연속된 같은 groupName 요소들 |
| X-lane 분리 | lanes 정의 시 다른 레인의 요소는 별도 그룹 |
| SubGroups | splittable 포함 그룹에서 non-splittable Y-overlap 서브그룹 분리 |
| 배치 원칙 | 그룹 전체가 들어갈 수 없으면 전체 이동 |
| 텍스트 분할 | splittable 텍스트는 분할 허용 (단, 한 줄도 못 들어가면 그룹 전체 이동) |
| 오류 조건 | splittable 없는 그룹의 높이 > 페이지 높이 |
| 배치 결과 | groupName, splittable, isDynamic, originalHeight 제거됨 |


------------------------------------------------------------
## 개념 > 갤러리
**URL**: https://api.sweetbook.com/docs/concepts/gallery/
------------------------------------------------------------

# Gallery Templates

여러 장의 사진을 자동으로 레이아웃하여 배치하는 특수 템플릿 가이드입니다.


## 개요

| 갤러리 타입 | 바인딩 | 사진 제한 | 레이아웃 방식 | 상태 |
| --- | --- | --- | --- | --- |
| collageGallery | collageGallery | 최대 9장 | 콜라주 표현식 | 구현됨 |
| rowGallery | rowGallery | 제한 없음 | 행 기반 배치 | 구현됨 |


## collageGallery (콜라주 갤러리)

PhotoLayoutCore 라이브러리의 콜라주 알고리즘을 사용하여 1~9장의 사진을 예쁘게 배치합니다. 업로드된 사진들의 가로/세로 비율을 분석하여 최적의 배치를 자동 생성합니다.


### 템플릿 정의


### container 속성

| 속성 | 타입 | 기본값 | 설명 |
| --- | --- | --- | --- |
| maxWidth | number | 978 | 콜라주 최대 너비 (px) |
| maxHeight | number | 424 | 콜라주 최대 높이 (px) |
| itemGap | number | 10 | 사진 간 간격 (px) |
| padding | number | 0 | 컨테이너 내부 여백 (px) |
| layout | string | "auto" | 레이아웃 모드 |
| fit | string | "contain" | 피팅 모드: contain |
| align.horizontal | string | "center" | 수평 정렬: left, center, right |
| align.vertical | string | "top" | 수직 정렬: top, center, bottom |

피팅 모드 `contain`은 기본값이자 유일한 옵션으로, 콜라주를 maxWidth x maxHeight 영역 내에 비율을 유지하며 맞춥니다.TemplateCopy```
{
  "parameters": {
    "definitions": {
      "collagePhotos": {
        "binding": "collageGallery",
        "type": "array",
        "itemType": "file",
        "minItems": 1,
        "maxItems": 9,
        "required": true,
        "description": "콜라주 갤러리 사진들"
      }
    }
  },
  "layout": {
    "elements": [
      {
        "element_id": "collageGallery-1",
        "type": "collageGallery",
        "photos": "$$collagePhotos$$",
        "tag": "collageGallery1",
        "fit": "cover",
        "position": { "x": 0, "y": 0 },
        "container": {
          "maxWidth": 424,
          "maxHeight": 424,
          "itemGap": 10,
          "padding": 0,
          "layout": "auto",
          "fit": "contain",
          "align": {
            "horizontal": "center",
            "vertical": "top"
          }
        },
        "isDynamic": true
      }
    ]
  }
}
```


## rowGallery (행 갤러리)

RowPhotoLayoutCore 라이브러리의 O(n) 알고리즘을 사용하여 사진을 행 단위로 자동 배치합니다. 사진 수 제한 없이 사용할 수 있으며, 사진이 많으면 자동으로 여러 그룹으로 분할됩니다.


### 템플릿 정의


### container 속성

| 속성 | 타입 | 기본값 | 설명 |
| --- | --- | --- | --- |
| maxWidth | number | 978 | 컨테이너 최대 너비 (px) |
| maxHeight | number | 0 | 컨테이너 최대 높이 (px), 0=무제한 |
| itemGap | number | 10 | 사진 간 간격 및 행 간 간격 (px) |
| padding | number | 0 | 컨테이너 내부 여백 (px) |
| row.maxHeight | number | 400 | 행 최대 높이 (px), 최소 100px |
| row.fillMiddle | boolean | false | 중간 행 가로 채움 (Justified 모드) |


### heightMode 속성

| 값 | 설명 |
| --- | --- |
| auto (기본값) | 동적 높이 - 사진에 맞게 자동 조절 |
| fixed | 고정 높이 - container.maxHeight 기준 청크 분할 |

TemplateCopy```
{
  "parameters": {
    "definitions": {
      "rowPhotos": {
        "binding": "rowGallery",
        "type": "array",
        "itemType": "file",
        "minItems": 1,
        "required": true,
        "description": "행 갤러리 사진들"
      }
    }
  },
  "layout": {
    "elements": [
      {
        "element_id": "rowGallery-1",
        "type": "rowGallery",
        "photos": "$$rowPhotos$$",
        "tag": "rowGallery1",
        "fit": "cover",
        "position": { "x": 0, "y": 0 },
        "container": {
          "maxWidth": 424,
          "maxHeight": 424,
          "itemGap": 10,
          "padding": 0,
          "row": {
            "maxHeight": 300,
            "fillMiddle": true
          }
        },
        "isDynamic": true
      }
    ]
  }
}
```


## API 호출 예시


### collageGallery 호출

행×열 그리드 구조로 이미지를 배치합니다. 사진 수에 따라 1~9장까지 자동으로 레이아웃이 결정됩니다.

RequestSandboxLiveCopy```
curl -X 'POST' \
  'https://api-sandbox.sweetbook.com/v1/books/{bookUid}/contents' \
  -H 'Content-Type: multipart/form-data' \
  -F 'templateUid=6VgvkpdYZzsI' \
  -F 'parameters={"dateStr":"2025-01-15","contents1":"부모님 말씀","contents2":"교사 코멘트"}' \
  -F 'collagePhotos=@photo1.jpg' \
  -F 'collagePhotos=@photo2.jpg' \
  -F 'collagePhotos=@photo3.jpg'
```


### rowGallery 호출

가로 방향으로 사진을 나열하며, 행 높이를 고정하고 너비는 원본 비율에 맞춰 자동 조정됩니다. 사진 수 제한 없이 다중 페이지를 지원합니다.

RequestSandboxLiveCopy```
curl -X 'POST' \
  'https://api-sandbox.sweetbook.com/v1/books/{bookUid}/contents' \
  -H 'Content-Type: multipart/form-data' \
  -F 'templateUid=3Z5VACFSGpEW' \
  -F 'parameters={"dateStr":"2025-01-15","contents1":"부모님 말씀","contents2":"교사 코멘트"}' \
  -F 'rowPhotos=@photo1.jpg' \
  -F 'rowPhotos=@photo2.jpg' \
  -F 'rowPhotos=@photo3.jpg' \
  -F 'rowPhotos=@photo4.jpg' \
  -F 'rowPhotos=@photo5.jpg'
```


## 자동 분할 기능


### collageGallery 분할 기준

| 콜라주 너비 | ratio | 설명 |
| --- | --- | --- |
| <= 400px | 0.5 | 작은 콜라주는 관대하게 |
| <= 500px | 0.3 | 중간 콜라주 |
| <= 1000px | 0.2 | 큰 콜라주 |
| > 1000px | 0.15 | 매우 큰 콜라주 |

분할 공식: 분할 필요 = minPhotoArea < (collageWidth × ratio)²


### 분할 결과 groupName

collageGallery: collageGallery_tag_part0, collageGallery_tag_part1, ...rowGallery: rowGallery_tag_page0, rowGallery_tag_page1, ...


## collageGallery vs rowGallery 선택 기준

| 기준 | collageGallery | rowGallery |
| --- | --- | --- |
| 사진 수 | 1~9장 | 제한 없음 |
| 레이아웃 | 콜라주 표현식 (미적) | 행 기반 (정돈) |
| 용도 | 소수의 사진을 예쁘게 | 많은 사진을 체계적으로 |
| 알고리즘 | 표현식 기반 | O(n) 행 완성 |


## 주의사항

collageGallery는 1~9장의 사진이 필요합니다. rowGallery는 최소 1장 이상의 사진이 필요합니다. 동일한 필드명으로 여러 파일을 업로드해야 하며, 갤러리 요소는 서버에서 자동으로 개별 photo 요소들로 변환됩니다.
## 관련 문서

- 컬럼 템플릿
- 동적 레이아웃 시스템


------------------------------------------------------------
## 개념 > 컬럼
**URL**: https://api.sweetbook.com/docs/concepts/column/
------------------------------------------------------------

# Column Templates

컬럼 레이아웃 템플릿 사용 가이드입니다. 페이지를 여러 개의 세로 열로 나누어 콘텐츠를 배치합니다.


## 개요

컬럼 템플릿은 page_layout_state 테이블 기반 배치 시스템을 사용하여 같은 페이지 내에서 컬럼별로 콘텐츠를 효율적으로 배치할 수 있습니다.


## 사용 가능한 컬럼 템플릿


### 1. 1컬럼 내지 템플릿

템플릿 UID: cnH0Ud1nl1f9 — 파라미터: date (날짜), contents (본문 내용)  — 페이지 전체를 하나의 열로 사용 (일반적인 전면 레이아웃).


### 2. 2컬럼 내지 템플릿

템플릿 UID: 4G5qpFLebGKd — 파라미터: date (날짜), contents (본문 내용)  — 페이지를 2개의 열로 나누어 콘텐츠 배치 (신문/잡지 스타일).


### 3. 3컬럼 내지 템플릿

템플릿 UID: 2Ec6Dp8duR3z — 파라미터: date (날짜), contents (본문 내용)  — 페이지를 3개의 열로 나누어 콘텐츠 배치 (멀티 컬럼 레이아웃).


## 컬럼 템플릿 특징

| 특징 | 설명 |
| --- | --- |
| 자동 배치 최적화 | page_layout_state 테이블을 활용하여 최적의 위치에 자동 배치 |
| 컬럼 호환성 체크 | 같은 페이지 내에서 동일한 컬럼 수를 가진 템플릿만 배치 가능 |
| 배치 우선순위 | 같은 면 빈 슬롯 → 반대 면 → 다음 페이지 |
| 슬롯 기반 좌표 계산 | 컬럼별로 X 좌표를 자동 계산하여 정렬 |
| 상태 추적 | 각 면의 컬럼 사용 현황을 실시간으로 추적 |


## 사용 방법


### curl 예시 — 2컬럼 템플릿

2컬럼 템플릿을 적용하면 콘텐츠 영역이 좌우 두 슬롯으로 나뉘어 배치됩니다.

RequestSandboxLiveCopy```
curl -X 'POST' \
  'https://api-sandbox.sweetbook.com/v1/books/bk_3dJTg8WOpR2e/contents?breakBefore=page' \
  -H 'Authorization: Bearer YOUR_API_KEY' \
  -H 'Content-Type: multipart/form-data' \
  -F 'files=@image.jpg;type=image/jpeg' \
  -F 'templateUid=4G5qpFLebGKd' \
  -F 'parameters={"date":"2025-08-27","contents":"Hello World!\nThis is a test."}'
```


### curl 예시 — 3컬럼 템플릿

3컬럼 구성에서는 세 개의 슬롯이 생성되며, columnGap만큼 간격을 두고 배치됩니다.

RequestSandboxLiveCopy```
curl -X 'POST' \
  'https://api-sandbox.sweetbook.com/v1/books/bk_3dJTg8WOpR2e/contents?breakBefore=page' \
  -H 'Authorization: Bearer YOUR_API_KEY' \
  -H 'Content-Type: multipart/form-data' \
  -F 'files=@image.jpg;type=image/jpeg' \
  -F 'templateUid=2Ec6Dp8duR3z' \
  -F 'parameters={"date":"2025-10-22","contents":"3컬럼 레이아웃 테스트\n여러 줄의 텍스트"}'
```


### curl 예시 — 1컬럼 템플릿

1컬럼(기본값)에서는 전체 콘텐츠 영역을 하나의 슬롯으로 사용합니다.

RequestSandboxLiveCopy```
curl -X 'POST' \
  'https://api-sandbox.sweetbook.com/v1/books/bk_3dJTg8WOpR2e/contents?breakBefore=page' \
  -H 'Authorization: Bearer YOUR_API_KEY' \
  -H 'Content-Type: multipart/form-data' \
  -F 'files=@image.jpg;type=image/jpeg' \
  -F 'templateUid=cnH0Ud1nl1f9' \
  -F 'parameters={"date":"2025-08-27","contents":"Hello World!\nThis is a test."}'
```


## 컬럼 배치 규칙


### 컬럼 호환성

같은 컬럼 수의 템플릿끼리는 같은 페이지 면에 배치 가능합니다. 다른 컬럼 수의 템플릿은 같은 페이지 면에 배치할 수 없으며, 다음 면 또는 페이지로 이동합니다.


### 컬럼 폭 및 X 좌표 계산 (pageMargin + columnGap)

페이지 단면 너비: pageWidth. 양쪽 마진: spine (책등 쪽), fore (바깥쪽).


### 1컬럼일 때

슬롯 너비가 콘텐츠 영역 전체 너비와 동일합니다.

FormulaCopy```
colWidth = contentWidth = pageWidth - (spine + fore)
// columnGap은 무시됨

X 시작점:
  왼쪽 면(left):  X = fore
  오른쪽 면(right): X = pageWidth + spine
```


### 2컬럼 이상일 때

슬롯 너비 = (contentWidth - columnGap × (columns-1)) / columns 으로 계산됩니다.

FormulaCopy```
colWidth = (contentWidth - columnGap × (columns - 1)) / columns

baseX:
  왼쪽 면(left):  baseX = fore
  오른쪽 면(right): baseX = pageWidth + spine

columnOffset = CurrentSlotIndex × (colWidth + columnGap)

X_final = baseX + columnOffset + templateX
```


### 세로 높이 (head/tail 마진)

슬롯의 사용 가능한 높이는 head와 tail 마진을 제외한 영역입니다.

FormulaCopy```
effectivePageHeight = pageHeight - (head + tail)
// Contents API는 이 값을 기준으로 슬롯 여부를 판단합니다.
```


## 처리 과정

1. 템플릿 조회 및 layout_rules에서 컬럼 수 추출2. page_layout_state 테이블에서 최근 페이지 상태 조회3. 배치 위치 결정: 같은 면 빈 슬롯 → 반대 면 → 다음 페이지4. 슬롯 기반 X 좌표 계산5. JSON 파일 저장 및 데이터베이스 업데이트6. page_layout_state 업데이트 (PageNum, PageSide, TotalColumns, UsedColumns)


## 컬럼 레이아웃 활용 예시 — 신문/잡지 스타일 책 만들기 (2컬럼)

RequestSandboxLiveCopy```
# 1. 책 생성
curl -X 'POST' 'https://api-sandbox.sweetbook.com/v1/books' \
  -H 'Authorization: Bearer YOUR_API_KEY' \
  -H 'Content-Type: application/json' \
  -d '{"title":"2컬럼 잡지 스타일","bookSpecUid":"SQUAREBOOK_HC","creationType":"TEST"}'

# 2. 2컬럼 콘텐츠 연속 추가 (같은 페이지에 2개까지 배치 가능)
curl -X 'POST' 'https://api-sandbox.sweetbook.com/v1/books/bk_xxxxx/contents' \
  -F 'files=@image1.jpg' \
  -F 'templateUid=4G5qpFLebGKd' \
  -F 'parameters={"date":"2025-10-22","contents":"첫 번째 컬럼 내용"}'

curl -X 'POST' 'https://api-sandbox.sweetbook.com/v1/books/bk_xxxxx/contents' \
  -F 'files=@image2.jpg' \
  -F 'templateUid=4G5qpFLebGKd' \
  -F 'parameters={"date":"2025-10-22","contents":"두 번째 컬럼 내용 (같은 페이지 왼쪽에 자동 배치)"}'
```


## 주의사항

같은 면에는 동일한 컬럼 수의 템플릿만 배치됩니다. 컬럼이 호환되지 않으면 자동으로 다음 면/페이지로 이동합니다. 표지(pageNum=0) 다음 첫 내지는 항상 오른쪽 면(pageSide=right)에 배치됩니다. 텍스트 파라미터와 함께 이미지 파일 1장 업로드가 필요합니다.
## 관련 문서

- 갤러리 템플릿
- 동적 레이아웃 시스템


------------------------------------------------------------
## 개념 > 베이스 레이어
**URL**: https://api.sweetbook.com/docs/concepts/base-layer/
------------------------------------------------------------

# Base Layer

템플릿에 페이지별 헤더/푸터를 자동으로 적용하는 기능입니다. 콘텐츠 아래에 깔리는 배경 레이어로, 모든 페이지에 일관된 헤더/푸터/장식 요소를 자동 적용합니다.


## 개요

| 특징 | 설명 |
| --- | --- |
| 페이지별 자동 적용 | 콘텐츠가 여러 페이지에 걸쳐 분할되면 각 페이지에 맞는 baseLayer가 자동 적용 |
| 홀수/짝수 페이지 분리 | 책의 좌우 페이지에 서로 다른 레이아웃 적용 가능 |
| 시스템 변수 지원 | 페이지 번호, 날짜 등 동적 값 자동 치환 |
| 사용자 파라미터 바인딩 | $$변수명$$ 형식으로 사용자 입력 값 바인딩 |


## 구조


### 페이지 규칙

| 페이지 번호 | 물리적 위치 | baseLayer |
| --- | --- | --- |
| 1 | 오른쪽 (첫 페이지) | odd |
| 2 | 왼쪽 | even |
| 3 | 오른쪽 | odd |
| 4 | 왼쪽 | even |

Layout definitionCopy```
{
  "baseLayer": {
    "odd": {
      "elements": [ /* 홀수 페이지(오른쪽)용 요소 */ ]
    },
    "even": {
      "elements": [ /* 짝수 페이지(왼쪽)용 요소 */ ]
    }
  }
}
```


## 요소 정의

각 요소에는 고유한 element_id가 필요합니다. 접두사 규칙: bl-odd-* (홀수 페이지용), bl-even-* (짝수 페이지용).


### 예시: 헤더/푸터

Element definitionCopy```
{
  "baseLayer": {
    "odd": {
      "elements": [
        {
          "element_id": "bl-odd-header",
          "type": "text",
          "position": { "x": 1028, "y": 25 },
          "width": 878,
          "height": 35,
          "text": "$$headerTitle$$ | 페이지 @@pageNum@@",
          "fontFamily": "Malgun Gothic",
          "fontSize": 12.0,
          "textAlignment": "Right",
          "verticalAlignment": "Center"
        },
        {
          "element_id": "bl-odd-footer",
          "type": "text",
          "position": { "x": 1028, "y": 960 },
          "width": 878,
          "height": 25,
          "text": "@@datetime.year@@년 @@datetime.month@@월 | 오른쪽 페이지",
          "textAlignment": "Right"
        }
      ]
    },
    "even": {
      "elements": [
        {
          "element_id": "bl-even-header",
          "type": "text",
          "position": { "x": 50, "y": 25 },
          "width": 878,
          "height": 35,
          "text": "페이지 @@pageNum@@ | $$headerTitle$$",
          "fontFamily": "Malgun Gothic",
          "fontSize": 12.0,
          "textAlignment": "Left",
          "verticalAlignment": "Center"
        },
        {
          "element_id": "bl-even-footer",
          "type": "text",
          "position": { "x": 50, "y": 960 },
          "width": 878,
          "height": 25,
          "text": "왼쪽 페이지 | @@datetime.year@@년 @@datetime.month@@월",
          "textAlignment": "Left"
        }
      ]
    }
  }
}
```


## 변수 바인딩


### 사용자 파라미터 ($$변수명$$)

템플릿의 parameters에 정의된 값으로 치환됩니다. API 호출 시 "headerTitle": "나의 포토북"을 전달하면 $$headerTitle$$이 나의 포토북으로 치환됩니다.


### 시스템 변수 (@@변수명@@)

| 변수 | 설명 | 예시 |
| --- | --- | --- |
| @@pageNum@@ | 실제 페이지 번호 | 1, 2, 3, ... |
| @@datetime.year@@ | 현재 연도 | 2026 |
| @@datetime.month@@ | 현재 월 | 1, 2, ..., 12 |
| @@datetime.date@@ | 현재 일 | 1, 2, ..., 31 |
| @@bookTitle@@ | 책 제목 | 나의 포토북 |


## 좌표 시스템

양페이지(spread) 기준 좌표입니다. 전체 너비: 약 1956px (bookSpec에 따라 다름).

| 페이지 | X 좌표 범위 | 너비 |
| --- | --- | --- |
| 왼쪽 페이지 (even) | 50 ~ 928 | 978px |
| 오른쪽 페이지 (odd) | 1028 ~ 1906 | 978px |


## 지원 요소 타입

baseLayer에서 사용 가능한 요소 타입:

- text: 텍스트 요소 (헤더, 푸터, 페이지 번호 등)
- graphic: 이미지/장식 요소 (라인, 로고 등)


## 완전한 템플릿 예시

TemplateCopy```
{
  "templateName": "헤더/푸터가 있는 본문 템플릿",
  "bookSpecUid": "SQUAREBOOK_HC",
  "templateKind": "content",
  "parameters": {
    "definitions": {
      "headerTitle": {
        "binding": "text",
        "type": "string",
        "required": false,
        "description": "헤더 제목"
      },
      "contents": {
        "binding": "text",
        "type": "string",
        "required": true,
        "description": "본문 내용"
      }
    }
  },
  "baseLayer": {
    "odd": {
      "elements": [
        {
          "element_id": "bl-odd-header",
          "type": "text",
          "position": { "x": 1028, "y": 25 },
          "width": 878,
          "height": 35,
          "text": "$$headerTitle$$ | 페이지 @@pageNum@@",
          "textAlignment": "Right"
        }
      ]
    },
    "even": {
      "elements": [
        {
          "element_id": "bl-even-header",
          "type": "text",
          "position": { "x": 50, "y": 25 },
          "width": 878,
          "height": 35,
          "text": "페이지 @@pageNum@@ | $$headerTitle$$",
          "textAlignment": "Left"
        }
      ]
    }
  },
  "layout": {
    "itemIndex": "0",
    "tag": "Print",
    "width": 424,
    "height": 860,
    "elements": [
      {
        "element_id": "content-text",
        "type": "text",
        "position": { "x": 0, "y": 0 },
        "width": 424,
        "height": 800,
        "text": "$$contents$$",
        "splittable": true,
        "isDynamic": true
      }
    ]
  },
  "layoutRules": {
    "space": "page",
    "margin": {
      "pageMargin": { "spine": 50, "fore": 50, "head": 80, "tail": 60 }
    },
    "flow": {
      "columns": 2,
      "columnGap": 30
    }
  }
}
```


## 주의사항

**element_id 필수**: 모든 baseLayer 요소는 고유한 `element_id`가 필요합니다.
**접두사 규칙**: `bl-odd-*`, `bl-even-*` 접두사를 사용하면 시스템이 중복 적용을 방지합니다.
**좌표 주의**: odd(오른쪽) 요소는 x 좌표를 1028 이상으로, even(왼쪽) 요소는 50 근처로 설정해야 합니다.
**콘텐츠 영역 고려**: 헤더/푸터 영역과 콘텐츠 영역이 겹치지 않도록 `layoutRules.margin`을 적절히 설정하세요.


------------------------------------------------------------
## 개념 > 텍스트 처리
**URL**: https://api.sweetbook.com/docs/concepts/text-processing/
------------------------------------------------------------

# Text Processing

WPF FormattedText 기반의 정확한 텍스트 높이 계산 기능 가이드입니다. 레거시 .NET 4.5 편집기와의 완벽한 호환성을 유지하며 다양한 폰트, 크기, 스타일을 지원합니다.


## 개요

| 특징 | 설명 |
| --- | --- |
| 레거시 호환성 | .NET 4.5 편집기와 동일한 측정 규칙 적용 |
| WPF 기반 | Windows 렌더링 엔진을 사용한 정확한 측정 |
| 다국어 지원 | 한글, 영문 등 모든 폰트 지원 |
| 고성능 | STA 스레드 풀을 통한 동시 처리 (기본 4개 스레드) |
| 안정성 | 타임아웃 및 과부하 방지 메커니즘 |


## 레거시 측정 규칙

| 규칙 | 값 | 설명 |
| --- | --- | --- |
| 폭 인셋 | width - 8 | 텍스트 프레임 폭에서 8px 제외 |
| 라인 높이 | fontSize × 1.6984 | 고정 배수 적용 (px 단위) |
| 정렬 방식 | justify | 양쪽 정렬 강제 |
| 최종 높이 | Max(oneLine, total + 10) | 최소 1줄 높이 보장, 전체 높이에 10px 패딩 |
| 폰트 크기 | fontSize × 1.1 | WPF 내부 처리용 |


## TextUtil API


### GetHeight()

텍스트의 계산된 높이를 반환합니다.

GetHeight()Copy```
double height = TextUtil.GetHeight(
    text: "안녕하세요\n여러 줄의\n텍스트입니다",
    fontSize: 20,
    width: 300,
    fontFamily: "Malgun Gothic",
    lineHeight: "normal",
    textAlign: "justify",
    bold: false,
    italic: false
);
```


### GetLineCount()

텍스트가 차지하는 줄 수를 반환합니다.

GetLineCount()Copy```
int lines = TextUtil.GetLineCount(
    text: "긴 텍스트가 여기에 들어갑니다",
    fontSize: 16,
    width: 250,
    fontFamily: "카페24 당당해"
);
```


### GetOneLineHeight()

한 줄의 높이를 반환합니다 (텍스트 내용과 무관).


### GetDispartText()

주어진 높이 제한 내에서 텍스트를 분할합니다.

GetDispartText()Copy```
List<string> parts = TextUtil.GetDispartText(
    text: "매우 긴 텍스트 내용...",
    fontSize: 14,
    height: 100,
    width: 200,
    fontFamily: "맑은 고딕"
);
// parts[0]: 100px 높이 내에 들어가는 텍스트
// parts[1]: 나머지 텍스트 (있는 경우)
```


### BadTextRemover()

HTML 엔티티 및 특수문자를 제거합니다.

BadTextRemover()Copy```
string cleaned = TextUtil.BadTextRemover("&lt;div&gt;텍스트&nbsp;&amp;&nbsp;내용&lt;/div&gt;");
// 결과: "텍스트 & 내용"
```


## Test API


### POST /books/{bookUid}/text-height

텍스트 높이 계산을 테스트하고 결과를 페이지로 추가하는 API입니다. 개발/디버깅 용도로 사용합니다.

Request / ResponseCopy```
// 요청 본문
{
  "templateUid": "template-blank-page",
  "textJson": [
    {
      "type": "text",
      "position": {"x": 100, "y": 200},
      "width": 300,
      "height": 0,
      "text": "측정할 텍스트\n여러 줄 가능",
      "fontFamily": "Malgun Gothic",
      "fontSize": 20,
      "bold": false,
      "italic": false
    }
  ]
}

// 응답
{
  "success": true,
  "data": {
    "pageNumber": 5,
    "calculatedHeights": [85.5, 62.3]
  },
  "message": "Text height page added"
}
```


## 폰트 처리

텍스트 스타일(굵기, 기울임)은 템플릿 JSON의 textBold와 textItalic 프로퍼티를 통해 적용됩니다.

폰트 파일을 `/fonts/` 디렉토리에 넣는 것만으로는 충분하지 않습니다. 반드시 **시스템에 설치**해야 합니다 (Windows: `C:\Windows\Fonts\`).
## 프로덕션 환경 고려사항


### 스레드 풀 설정

Thread pool configurationCopy```
# Windows
set WPF_TEXT_MEASURER_THREADS=8

# Linux (Docker)
ENV WPF_TEXT_MEASURER_THREADS=8

# 권장 설정:
# 낮은 부하: 2~4 스레드
# 중간 부하: 4~8 스레드
# 높은 부하: 8~16 스레드
```


### 타임아웃 설정

| 항목 | 값 |
| --- | --- |
| 큐 추가 타임아웃 | 2초 |
| 측정 타임아웃 | 10초 |
| 대기열 용량 | 1,000개 |


### 성능 벤치마크

| 작업 | 평균 시간 | 동시 처리 |
| --- | --- | --- |
| 단일 텍스트 측정 (1줄) | 5ms | 4 스레드 |
| 단일 텍스트 측정 (10줄) | 8ms | 4 스레드 |
| 배치 측정 (10개) | 45ms | 4 스레드 |
| 최대 처리량 | ~800 req/s | 8 스레드 |


## 제약사항

**Windows 전용**: WPF 의존으로 Linux에서 동작하지 않습니다. Docker 사용 시 Windows 컨테이너가 필요합니다. 크로스 플랫폼 지원이 필요한 경우 SkiaSharp 또는 SixLabors.Fonts로 전환을 고려하세요.정확도 관련: WPF와 브라우저의 렌더링 엔진이 다르므로 약간의 차이가 발생할 수 있습니다. 정확한 측정을 위해 동일한 폰트가 시스템에 설치되어 있어야 합니다. DPI는 96으로 고정됩니다.


## 텍스트 분할 구현


### 이진 탐색 알고리즘

원본 LinkedBooks의 선형 탐색(O(n)) 대신 이진 탐색(O(log n))을 사용하여 분할 지점을 찾습니다.

| 텍스트 길이 | 이진 탐색 | 선형 탐색 | 성능 향상 |
| --- | --- | --- | --- |
| 100자 | 7번 | 최대 100번 | 14배 |
| 500자 | 9번 | 최대 500번 | 55배 |
| 1000자 | 10번 | 최대 1000번 | 100배 |
| 10000자 | 14번 | 최대 10000번 | 714배 |


### 단어 경계 조정 우선순위

이진 탐색으로 찾은 분할 지점을 자연스러운 위치로 조정합니다.

- 공백 문자 (` `, `\t`) — 단어 중간에서 자르지 않음. 개행(`\n`)은 제외 (문단 간격 보존)
- 문장 부호 (`.`, `!`, `?`, `,`, `。`) — 문장 단위로 자름
- 최소 95% 유지 — 너무 적은 텍스트가 배치되지 않도록
- 원본 지점 — 좋은 지점을 못 찾으면 이진 탐색 결과 사용


### 개행 처리 방식

Newline handlingCopy```
원본: "상상력을 발휘했어요.\n\n두 번째 전시실에는..."

분할 후:
  첫 번째: "상상력을 발휘했어요."      (TrimEnd)
  두 번째: "\n두 번째 전시실에는..."   (앞 개행 1개만 제거, 문단 간격 유지)

// "\n\n두 번째..." → "\n두 번째..." (문단 간격 유지)
// "\n다음 문장"    → "다음 문장"     (바로 시작)
```


## 원본(LinkedBooks)과의 차이점 요약

| 항목 | 원본 (LinkedBooks) | 현재 (PhotobookAPI) |
| --- | --- | --- |
| 분할 알고리즘 | 선형 탐색 O(n) | 이진 탐색 O(log n) |
| 폰트 지원 | 고정 (Malgun Gothic) | 다양한 폰트/스타일 |
| 공백 처리 | 항상 Trim() 제거 | trimWhitespace 옵션으로 제어 |
| 분할 정확도 | 단어 경계만 | 문장 > 단어 > 문자 |
| 500자 처리 시간 | ~2,500-4,000ms | ~50-80ms |


## 관련 문서

- 동적 레이아웃 시스템
- 갤러리 템플릿
- 컬럼 템플릿


------------------------------------------------------------
## 개념 > 특수 페이지 규칙
**URL**: https://api.sweetbook.com/docs/concepts/special-page-rules/
------------------------------------------------------------

# Special Page Rules

template_kind = cover | content | divider | publish 기반으로 special page(간지/발행면) 배치 규칙과 pageSide 동작 상세 규칙을 정의합니다.


## 1. Template Kinds


### template_kind = content

일반 내지 콘텐츠. Flow 엔진으로 이전 콘텐츠 뒤에 자연스럽게 이어 배치됩니다.breakBefore의 column 값 사용 가능.pageSide 사용 불가.


### template_kind = divider

섹션 구분 간지 페이지. Flow에 섞이지 않는 특수 페이지로, 항상 독립 페이지로 취급됩니다.breakBefore는 생략 또는 page만 허용.none / column은 에러.


### template_kind = publish

발행면(콜로폰) 페이지. divider와 동일하게 독립 특수 페이지입니다. 책 앞/뒤 어디든 배치 가능하지만 항상 기존 콘텐츠의 뒤에 위치합니다.


## 2. Query Parameters


### 2.1 breakBefore

| 값 | content에서의 의미 | divider/publish에서의 의미 |
| --- | --- | --- |
| none | Flow 그대로 이어서 배치 (기본값) | 에러 |
| column | 같은 페이지의 다음 컬럼에서 이어쓰기 | 에러 |
| page | 새 페이지에서 시작 | 새 페이지에서 시작 (기본값) |

기본값은 템플릿 종류(`template_kind`)에 따라 자동으로 설정됩니다. 사용자가 명시적으로 값을 지정하면 해당 값이 우선 적용됩니다.
### 2.2 pageSide

값: left | right.divider/publish 전용 옵션입니다. 이 특수 페이지를 어느 면에서 시작할지 지정합니다.content에서 사용 시 에러. 생략 시(auto) 제품/템플릿 기본 규칙 사용.


## 3. Template Kind별 동작


### 3.1 template_kind = content

| breakBefore | pageSide | 결과 |
| --- | --- | --- |
| (생략) | (생략) | Flow 그대로 이어붙기 (기본값 none 자동 적용) |
| none | (생략) | Flow 계속 |
| column | (생략) | 같은 페이지의 다음 컬럼에서 이어쓰기 |
| page | (생략) | 새 페이지에서 시작 |
| (무관) | left/right | 에러 — content는 pageSide 불가 |


### 3.2 template_kind = divider

| breakBefore | pageSide | 처리 |
| --- | --- | --- |
| (생략) | (생략) | 새 페이지 시작 (기본값 page 자동 적용) |
| (생략) | left/right | 새 페이지 시작 + 지정 면 강제 |
| page | (생략) | 새 페이지 시작 |
| page | left/right | 새 페이지 시작 + 지정 면 강제 |
| none | (무관) | 에러 |
| column | (무관) | 에러 |


### 3.3 template_kind = publish (divider와 동일)

| breakBefore | pageSide | 처리 |
| --- | --- | --- |
| (생략) | (생략) | 새 페이지 시작 (기본값 page 자동 적용) |
| (생략) | left/right | 새 페이지 시작 + 지정 면 강제 |
| page | (생략) | 새 페이지 시작 |
| page | left/right | 새 페이지 시작 + 지정 면 강제 |
| none | (무관) | 에러 |
| column | (무관) | 에러 |


## 4. pageSide 상세 동작 규칙 (면 배치 알고리즘)


### 4.1 기본 개념

엔진은 page_layout_state 테이블을 통해 현재 페이지 배치 상태를 관리합니다. 특수 페이지는 항상 독립 페이지로 배치되므로 최근 상태만으로 다음 배치 위치를 판단합니다.

특수 페이지는 현재 커서 기준으로 "뒤쪽"에서만 배치됩니다. 이미 생성된 페이지/면보다 앞으로 되돌아가 배치하지 않습니다.
### 4.2 배치 위치 계산 공식

| 현재 커서 pageside | 요청 pageSide | 결과 pagenum | 결과 pageside | 설명 |
| --- | --- | --- | --- | --- |
| left | left | pagenum + 1 | left | 다음 페이지 left |
| left | right | pagenum | right | 같은 페이지 right |
| right | left | pagenum + 1 | left | 다음 페이지 left |
| right | right | pagenum + 1 | right | 다음 페이지 right |

**특수 케이스 — 스퀘어북 첫 페이지**: 현재 상태 pagenum=0 (cover), pageside=right이고 첫 내지(pagenum=1)는 right부터 시작합니다. `pageSide=left` 요청 시 → `pagenum=2, pageside=left`로 배치됩니다.
### 케이스별 예시

Case 2) 현재 커서가 left + pageSide=left현재: { "pagenum": 3, "pageside": "left" } → 결과: pagenum=4, pageside=left

Case 3) 현재 커서가 left + pageSide=right현재: { "pagenum": 3, "pageside": "left" } → 결과: pagenum=3, pageside=right

Case 4) 현재 커서가 right + pageSide=left현재: { "pagenum": 5, "pageside": "right" } → 결과: pagenum=6, pageside=left

Case 5) 현재 커서가 right + pageSide=right현재: { "pagenum": 5, "pageside": "right" } → 결과: pagenum=6, pageside=right


## 5. Summary

| 구분 | content | divider / publish |
| --- | --- | --- |
| breakBefore | none / column / page (기본: none) | page만 허용 (기본: page), none/column은 에러 |
| pageSide | 사용 불가 (에러) | left / right 선택 가능 (선택 사항) |
| 배치 방식 | Flow 엔진으로 이어 배치 | 항상 독립 특수 페이지, 커서 이후에만 배치 |


## 6. 예시


### 예 1) 스퀘어북 첫 페이지(오른쪽 시작)에서 left 요청

PUR 제본(스퀘어북 등)은 첫 내지가 오른쪽(right)에서 시작합니다. left를 요청하면 다음 페이지의 왼쪽 면에 배치됩니다.

RequestCopy```
POST /books/{id}/contents?pageSide=left
{ "templateUid": "tpl_divider" }

// page_layout_state 현재 상태:
// { "pagenum": 0, "pageside": "right" }

// 계산:
// 스퀘어북 첫 페이지는 right 시작 → pagenum=1은 right
// pageSide=left 요청 → pagenum=2의 left

// 결과: pagenum=2, pageside=left 에 배치
```


### 예 2) 현재 커서가 left일 때 pageSide=right

현재 커서가 왼쪽 면이면 같은 페이지의 오른쪽 면에 바로 배치됩니다.

RequestCopy```
POST /books/{id}/contents?pageSide=right
{ "templateUid": "tpl_publish" }

// page_layout_state 현재 상태:
// { "pagenum": 5, "pageside": "left" }

// 계산: left → right = 같은 페이지의 right

// 결과: pagenum=5, pageside=right 에 배치
```


### 예 3) 현재 커서가 right일 때 pageSide=left

현재 커서가 오른쪽 면이면 다음 페이지의 왼쪽 면에 배치됩니다. 이미 지나간 면으로 되돌아가지 않습니다.

RequestCopy```
POST /books/{id}/contents?pageSide=left
{ "templateUid": "tpl_divider" }

// page_layout_state 현재 상태:
// { "pagenum": 7, "pageside": "right" }

// 계산: right → left = 다음 페이지의 left

// 결과: pagenum=8, pageside=left 에 배치
```


------------------------------------------------------------
## 개념 > 멱등성
**URL**: https://api.sweetbook.com/docs/concepts/idempotency/
------------------------------------------------------------

# 멱등성 (Idempotency)

동일한 API 요청이 여러 번 실행되어도 결과가 동일하게 유지되는 멱등성 개념과 SweetBook API의 중복 요청 방지 메커니즘을 안내합니다.


## 멱등성이란?

멱등성(Idempotency)이란 동일한 요청을 여러 번 보내더라도 서버 상태가 한 번 요청한 것과 동일하게 유지되는 성질입니다. 네트워크 오류, 타임아웃, 클라이언트 재시도 등의 상황에서 주문이 중복 생성되거나 충전금이 이중 차감되는 것을 방지하기 위해 반드시 필요합니다.

- 클라이언트 → POST /orders (요청 #1) → 네트워크 타임아웃
- 클라이언트 → POST /orders (요청 #1 재시도) → 409 Conflict (이미 처리됨)

→ 주문은 1건만 생성되고, 충전금도 1회만 차감됩니다.


## HTTP 메서드별 멱등성

HTTP 메서드에 따라 멱등성이 보장되는 정도가 다릅니다.

| 메서드 | 멱등성 | 설명 |
| --- | --- | --- |
| GET | 멱등 | 데이터를 조회만 하므로 서버 상태를 변경하지 않습니다. 안전하게 재시도할 수 있습니다. |
| PUT | 멱등 | 전체 리소스를 교체하므로 동일 요청을 반복해도 결과가 같습니다. |
| DELETE | 멱등 | 이미 삭제된 리소스에 대해 재요청해도 결과가 동일합니다 (404 또는 200). |
| POST | 비멱등 | 새 리소스를 생성하므로 재시도 시 중복 생성 위험이 있습니다. 별도의 중복 방지 메커니즘이 필요합니다. |

**POST 요청 주의:** 주문 생성(`POST /orders`)과 같은 비멱등 요청은 반드시 아래에서 설명하는 중복 방지 메커니즘을 활용하세요.
## SweetBook의 중복 요청 방지

SweetBook API는 Redis 분산 락(Distributed Lock)을 사용하여 중복 요청을 방지합니다. 동일한 요청이 30초 이내에 다시 수신되면 이전 요청이 아직 처리 중인 것으로 판단하여409 Conflict 응답을 반환합니다.


### 409 Conflict 응답 예시

요청 수신 → Redis Lock 획득 시도 (TTL 30초)├ Lock 획득 성공 → 요청 처리 → 완료 후 Lock 해제└ Lock 획득 실패 → 409 Conflict 즉시 반환

분산 락의 TTL은 **30초**입니다. 정상적인 요청 처리가 완료되면 즉시 락이 해제되므로, 실제로 30초를 기다릴 필요는 거의 없습니다.409 Conflict ResponseCopy```
{
  "success": false,
  "error": {
    "code": "DUPLICATE_REQUEST",
    "message": "이미 동일한 요청이 처리 중입니다. 잠시 후 다시 시도해주세요.",
    "retryAfter": 30
  }
}
```


## Best Practices


### 1. 고유한 Reference ID 사용

주문 생성 시 referenceId 필드에 클라이언트 측에서 생성한 고유 ID를 전달하세요. 동일한 referenceId로 중복 주문을 방지할 수 있습니다.

RequestCopy```
{
  "referenceId": "my-system-order-20250315-001",
  "bookUid": "bk_e4d5c6b7",
  "quantity": 1,
  "shippingAddress": { ... }
}
```


### 2. 409 응답을 정상적으로 처리

409 Conflict 응답을 받으면 에러로 처리하지 말고, 이전 요청이 성공적으로 처리되고 있다는 의미로 해석하세요. 기존 주문을 조회하여 상태를 확인하는 것이 좋습니다.


### 3. Exponential Backoff 재시도

네트워크 오류나 5xx 응답을 받았을 때는 지수 백오프(Exponential Backoff) 전략으로 재시도하세요. 과도한 재시도는 서버 부하를 가중시킬 수 있습니다.

| 재시도 횟수 | 대기 시간 |
| --- | --- |
| 1차 | 1초 |
| 2차 | 2초 |
| 3차 | 4초 |
| 4차 (최대) | 8초 |


## 멱등적 주문 생성 패턴

아래는 referenceId를 활용하여 안전하게 주문을 생성하고, 409 응답과 네트워크 오류를 올바르게 처리하는 예시입니다.

Node.jsCopy```
async function createOrderSafely(bookUid, quantity, shippingAddress) {
  const referenceId = `order-${Date.now()}-${crypto.randomUUID()}`;

  for (let attempt = 0; attempt < 4; attempt++) {
    try {
      const response = await fetch('https://api.sweetbook.com/v1/orders', {
        method: 'POST',
        headers: {
          'Authorization': 'Bearer YOUR_API_KEY',
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          referenceId,
          bookUid,
          quantity,
          shippingAddress,
        }),
      });

      if (response.ok) {
        return await response.json();
      }

      if (response.status === 409) {
        // 이미 처리 중 — 기존 주문 조회
        console.log('중복 요청 감지, 기존 주문을 조회합니다.');
        const existing = await fetch(
          `https://api.sweetbook.com/v1/orders?referenceId=${referenceId}`,
          { headers: { 'Authorization': 'Bearer YOUR_API_KEY' } }
        );
        return await existing.json();
      }

      if (response.status >= 500) {
        // 서버 오류 — 재시도
        const delay = Math.pow(2, attempt) * 1000;
        console.log(`서버 오류 (${response.status}), ${delay}ms 후 재시도...`);
        await new Promise(resolve => setTimeout(resolve, delay));
        continue;
      }

      // 4xx 오류 (409 제외) — 재시도 불필요
      throw new Error(`요청 실패: ${response.status}`);

    } catch (error) {
      if (error.name === 'TypeError') {
        // 네트워크 오류 — 재시도
        const delay = Math.pow(2, attempt) * 1000;
        console.log(`네트워크 오류, ${delay}ms 후 재시도...`);
        await new Promise(resolve => setTimeout(resolve, delay));
        continue;
      }
      throw error;
    }
  }

  throw new Error('최대 재시도 횟수 초과');
}
```

PythonCopy```
import requests
import uuid
import time

def create_order_safely(book_uid, quantity, shipping_address):
    reference_id = f"order-{int(time.time())}-{uuid.uuid4()}"
    url = "https://api.sweetbook.com/v1/orders"
    headers = {
        "Authorization": "Bearer YOUR_API_KEY",
        "Content-Type": "application/json",
    }

    for attempt in range(4):
        try:
            response = requests.post(url, json={
                "referenceId": reference_id,
                "bookUid": book_uid,
                "quantity": quantity,
                "shippingAddress": shipping_address,
            }, headers=headers, timeout=30)

            if response.ok:
                return response.json()

            if response.status_code == 409:
                # 이미 처리 중 — 기존 주문 조회
                print("중복 요청 감지, 기존 주문을 조회합니다.")
                existing = requests.get(
                    f"{url}?referenceId={reference_id}",
                    headers=headers
                )
                return existing.json()

            if response.status_code >= 500:
                delay = (2 ** attempt)
                print(f"서버 오류 ({response.status_code}), {delay}초 후 재시도...")
                time.sleep(delay)
                continue

            response.raise_for_status()

        except requests.exceptions.ConnectionError:
            delay = (2 ** attempt)
            print(f"네트워크 오류, {delay}초 후 재시도...")
            time.sleep(delay)
            continue

    raise Exception("최대 재시도 횟수 초과")
```


## 관련 문서

- Orders API — 주문 생성 및 관리
- Webhooks 연동 가이드 — 웹훅 설정 및 서명 검증
- 인증 가이드 — API Key 발급


================================================================================
# SDKs & Tools
================================================================================


------------------------------------------------------------
## SDKs & Tools > SDK
**URL**: https://api.sweetbook.com/docs/sdk/
------------------------------------------------------------

# SDKs

Book Print API와 연동하기 위한 공식 SDK를 제공합니다.


### Python SDK

포토북 생성부터 주문/배송까지 전체 API를 지원하는 Python SDK입니다. pip install -e .으로 설치하거나 소스를 직접 임포트하여 사용할 수 있습니다.

[View on GitHub](https://github.com/sweet-book/bookprintapi-python-sdk)
### Node.js SDK

Node.js 서버 환경에서 사용할 수 있는 SDK입니다. Express, Fastify 등과 함께 서버 사이드 연동에 적합합니다.

[View on GitHub](https://github.com/sweet-book/bookprintapi-nodejs-sdk)


------------------------------------------------------------
## SDKs & Tools > 데모 앱
**URL**: https://api.sweetbook.com/docs/demo-apps/
------------------------------------------------------------

# Demo Apps

실행 가능한 웹앱 예시입니다. node server.js로 바로 실행할 수 있습니다.


### 일기장 (diaryBook)

일기장 A/B 타입의 포토북을 생성하는 웹앱입니다. JSON 데이터 업로드 또는 직접 입력으로 책을 만들 수 있습니다.

[View on GitHub](https://github.com/sweet-book/diaryBook-demo)
### 알림장 (kidsDailyBook)

어린이집 알림장 A/B/C 타입의 포토북을 생성하는 웹앱입니다. 월별 색상/캐릭터/풍선 디자인이 자동 적용됩니다.

[View on GitHub](https://github.com/sweet-book/kidsDailyBook-demo)
### 구글포토북 (socialBook)

Google Photos 연동으로 포토북을 생성하는 웹앱입니다. Google OAuth 로그인 후 사진을 선택하면 자동으로 책이 만들어집니다.

[View on GitHub](https://github.com/sweet-book/socialBook-demo)
### 주문 (partner-order)

파트너 주문 시스템 웹앱입니다. 충전금 관리, 견적 조회, 주문 생성, 배송지 변경, 주문 취소까지 전체 주문 플로우를 체험할 수 있습니다.

[View on GitHub](https://github.com/sweet-book/partner-order-demo)


------------------------------------------------------------
## SDKs & Tools > 변경 로그
**URL**: https://api.sweetbook.com/docs/changelog/
------------------------------------------------------------

# 변경이력 (Changelog)

Book Print API의 버전별 변경 내역입니다. 이전 버전의 변경 내역을 통해 API의 변화를 추적할 수 있습니다.

전체 버전
## v1.0.2 2026-04-03

API 문서 정확성 개선 및 Sandbox/Live 환경 전환 UI가 추가되었습니다.


### 정정 사항

- 배송비/포장비 정정 — 배송비 3,500원 → 3,000원, 포장비 500원×수량 → 0원 (현재 비활성)
- 웹훅 이벤트 전면 변경 — 5종에서 8종으로 확대. 이벤트명 체계 변경 (order.paid → order.created, order.confirmed → production.confirmed, order.shipped → shipping.departed 등)
- 웹훅 서명 형식 — X-Webhook-Signature 값에 sha256= 접두사 추가
- API Key 스코프 이름 — 복수형에서 단수형으로 변경 (books:read → book:read, orders:write → order:write)
- API Key 생성 필드 — name → note
- 책 삭제 제약 — DRAFT 상태 제한 제거 → 본인 소유 책 상태 무관 삭제 가능 (소프트 딜리트)
- 주문 취소 cancelReason — 필수(최대 500자) 명시
- 크레딧 거래 내역 필드 — transactionUid → transactionId, type → reasonCode+reasonDisplay, description → memo
- Sandbox 크레딧 필드 — description → memo


### 추가 사항

- 주문 응답 필드 — paymentMethod, externalUserId, batchUid, endUserAmount/endUserShippingFee/endUserDiscount/endUserPaidAmount
- 주문 생성 요청 — externalUserId 파라미터 추가
- 크레딧 reason code — 전체 11종 (1~11) 표기, 7 ORDER_CANCEL_REFUND, 8 ADMIN_CANCEL_REFUND 추가
- 크레딧 잔액 응답 — accountUid, createdAt, updatedAt 필드 추가
- Sandbox 크레딧 도메인 규칙 — API Key 환경과 무관하게 항상 test 크레딧에 적용
- BookSpecs 응답 — visibility (PUBLIC/PARTNER_ONLY/HIDDEN), ownerAccountUid 필드 추가
- API Key 스코프 — catalog:read, billing:read, billing:write 추가
- 템플릿 파라미터 구조 — definitions 래퍼, binding 키, $$var$$ 플레이스홀더 구문 설명


### UI 개선

- Sandbox/Live 환경 탭 — 모든 API 요청 코드 예시에 Sandbox/Live URL 전환 탭 추가


## v1.0.1 2026-04-02

API 기능 개선 릴리즈입니다. 책 삭제, 크레딧 거래 내역, Sandbox 크레딧 관리 엔드포인트가 신규 추가되었으며, API Key 스코프 시스템, 멱등성 지원, 템플릿 검색 등 여러 기능이 개선되었습니다.

**Breaking Change 포함:** `책 생성 요청 본문 (POST /books)`에서 `creationType` 필드가 제거되었습니다. 자세한 내용은 아래를 참고하세요.
### Breaking Change


#### 1. 책 생성 요청 본문 (POST /books)에서 creationType 제거

책 생성 요청 본문에서 creationType 필드가 제거되었습니다. 해당 필드를 전송하더라도 무시되며,bookSpecUid만으로 책을 생성할 수 있습니다.

Before — POST /v1/booksCopy```
{
  "bookSpecUid": "spec_abc123",
  "creationType": "TEMPLATE"
}
```

After — POST /v1/booksCopy```
{
  "bookSpecUid": "spec_abc123"
}
```


### 신규 API


#### 2. 책 삭제 — DELETE /v1/books/{bookUid}

DRAFT 상태인 본인 소유의 책을 삭제할 수 있습니다. 삭제는 소프트 딜리트(soft delete)로 처리됩니다. 이미 주문이 연결된 책이나 타인 소유의 책은 삭제할 수 없습니다.

RequestCopy```
curl -X DELETE 'https://api-sandbox.sweetbook.com/v1/books/book_abc123' \
  -H 'Authorization: Bearer YOUR_API_KEY'
```

Response (200 OK)Copy```
{
  "success": true,
  "message": "책이 삭제되었습니다.",
  "data": null
}
```


#### 3. 크레딧 거래 내역 조회 — GET /v1/credits/transactions

본인 계정의 크레딧 충전·차감 거래 내역을 조회합니다. 페이지네이션(limit/offset)을 지원합니다.

RequestCopy```
curl 'https://api-sandbox.sweetbook.com/v1/credits/transactions?limit=20&offset=0' \
  -H 'Authorization: Bearer YOUR_API_KEY'
```

Response (200 OK)Copy```
{
  "success": true,
  "message": "Success",
  "data": {
    "total": 3,
    "transactions": [
      {
        "transactionUid": "txn_xyz789",
        "type": "CHARGE",
        "amount": 50000,
        "balanceAfter": 150000,
        "createdAt": "2026-04-01T09:00:00Z"
      }
    ]
  }
}
```


#### 4. Sandbox 크레딧 충전/차감 — POST /v1/credits/sandbox/charge, POST /v1/credits/sandbox/deduct

Sandbox 환경에서 테스트용 크레딧을 충전하거나 차감할 수 있습니다. Live 환경에서는 동작하지 않습니다.

Sandbox API Key로만 호출 가능합니다. Live API Key로 호출 시 `403 Forbidden`이 반환됩니다.충전 — POST /v1/credits/sandbox/chargeCopy```
curl -X POST 'https://api-sandbox.sweetbook.com/v1/credits/sandbox/charge' \
  -H 'Authorization: Bearer YOUR_SANDBOX_API_KEY' \
  -H 'Content-Type: application/json' \
  -d '{
  "amount": 10000
}'
```

차감 — POST /v1/credits/sandbox/deductCopy```
curl -X POST 'https://api-sandbox.sweetbook.com/v1/credits/sandbox/deduct' \
  -H 'Authorization: Bearer YOUR_SANDBOX_API_KEY' \
  -H 'Content-Type: application/json' \
  -d '{
  "amount": 5000
}'
```


### 기능 개선


#### 5. API Key 스코프 시스템

API Key 생성 시 scopes 파라미터로 접근 가능한 엔드포인트 범위를 제한할 수 있습니다. 스코프가 설정된 키로 허용되지 않은 엔드포인트에 접근하면 403 Forbidden이 반환됩니다.

| 스코프 | 허용 동작 |
| --- | --- |
| books:read | 책 목록/상세 조회 |
| books:write | 책 생성, 수정, 삭제 |
| orders:read | 주문 목록/상세 조회 |
| orders:write | 주문 생성, 취소 |

Before — POST /v1/keys (스코프 없음)Copy```
{
  "env": "live"
}
```

After — POST /v1/keys (스코프 지정)Copy```
{
  "env": "live",
  "scopes": ["books:read", "orders:read"]
}
```

Response — 스코프 부족 시 (403 Forbidden)Copy```
{
  "success": false,
  "message": "이 작업을 수행할 권한이 없습니다.",
  "data": null
}
```


#### 6. 템플릿 목록 정렬/검색 파라미터 추가

GET /v1/templates에 정렬 및 검색 파라미터가 추가되었습니다.

| 파라미터 | 설명 |
| --- | --- |
| sort | name_asc, name_desc, created_asc, updated_desc, updated_asc |
| templateName | 이름 검색 (공백 구분 다중 키워드, AND 조건) |
| specProfileUid | 특정 판형 프로필 UID로 필터 |
| theme | 테마로 필터 (예: minimal) |

Before — GET /v1/templatesCopy```
curl 'https://api.sweetbook.com/v1/templates?limit=20&offset=0' \
  -H 'Authorization: Bearer YOUR_API_KEY'
```

After — 정렬 및 검색 적용Copy```
curl 'https://api.sweetbook.com/v1/templates?sort=updated_desc&templateName=일기장&theme=minimal' \
  -H 'Authorization: Bearer YOUR_API_KEY'
```


#### 7. BookSpecs accountUid 자동 적용

GET /v1/book-specs 조회 시 accountUid를 전달하지 않으면 API Key 소유자의 UID가 자동으로 적용됩니다. 커스텀 가격이 설정된 경우 자동으로 반영됩니다. 타인의 accountUid를 전달하면 403 Forbidden이 반환됩니다.

Before — accountUid 직접 전달 필요Copy```
curl 'https://api.sweetbook.com/v1/book-specs?accountUid=acc_myuid123' \
  -H 'Authorization: Bearer YOUR_API_KEY'
```

After — accountUid 생략 가능 (자동 적용)Copy```
curl 'https://api.sweetbook.com/v1/book-specs' \
  -H 'Authorization: Bearer YOUR_API_KEY'
```


#### 8. 멱등성(Idempotency-Key) 지원 확대

네트워크 재시도 시 중복 처리를 방지하기 위한 Idempotency-Key 헤더 지원이 확대되었습니다. 동일한 키로 재요청하면 최초 응답이 그대로 반환됩니다.

지원 엔드포인트:

- POST /v1/books
- POST /v1/orders
- POST /v1/credits/sandbox/charge

Before — Idempotency-Key 미지원Copy```
curl -X POST 'https://api.sweetbook.com/v1/books' \
  -H 'Authorization: Bearer YOUR_API_KEY' \
  -H 'Content-Type: application/json' \
  -d '{ "bookSpecUid": "spec_abc123" }'
```

After — Idempotency-Key 헤더 추가Copy```
curl -X POST 'https://api.sweetbook.com/v1/books' \
  -H 'Authorization: Bearer YOUR_API_KEY' \
  -H 'Content-Type: application/json' \
  -H 'Idempotency-Key: 550e8400-e29b-41d4-a716-446655440000' \
  -d '{ "bookSpecUid": "spec_abc123" }'
```


#### 9. 콘텐츠 추가 응답에 pageCount 추가

POST /v1/books/{bookUid}/content 응답에 현재까지 추가된 총 페이지 수를 나타내는 pageCount 필드가 포함됩니다.

Before — 콘텐츠 추가 응답Copy```
{
  "success": true,
  "message": "Success",
  "data": {
    "bookUid": "book_xyz123",
    "status": "DRAFT"
  }
}
```

After — pageCount 포함Copy```
{
  "success": true,
  "message": "Success",
  "data": {
    "bookUid": "book_xyz123",
    "status": "DRAFT",
    "pageCount": 4
  }
}
```


#### 10. 템플릿 응답에 theme 필드 추가

GET /v1/templates 목록 및 GET /v1/templates/{templateUid} 상세 응답 객체에 theme 필드가 추가됩니다.

Before — 템플릿 응답 객체Copy```
{
  "templateUid": "tmpl_abc123",
  "name": "미니멀 일기장",
  "bookSpecUid": "spec_xyz"
}
```

After — theme 필드 포함Copy```
{
  "templateUid": "tmpl_abc123",
  "name": "미니멀 일기장",
  "bookSpecUid": "spec_xyz",
  "theme": "minimal"
}
```


## v1.0 2026-03-24

Book Print API 최초 공개 릴리즈입니다. 책 생성부터 주문·배송까지의 전체 워크플로우를 지원하는 7개 리소스 그룹이 포함됩니다.

| 리소스 | 포함 엔드포인트 |
| --- | --- |
| Authentication | API Key 발급 — Bearer token, IP 화이트리스트 |
| Books | 생성, 표지/콘텐츠 추가, 사진 업로드, 최종화, 목록/상세/사진 조회, 내지 초기화 |
| Orders | 견적 조회, 주문 생성, 취소, 배송지 변경, 목록/상세 조회 |
| Templates | 목록/상세 조회 |
| BookSpecs | 목록/상세 조회 |
| Credits | 잔액 조회 |
| Webhooks | 설정 등록/조회/삭제, 테스트 전송, 전송 이력 조회 |


### 1. Authentication (인증)

모든 API 요청은 Authorization: Bearer {API_KEY} 헤더를 통해 인증합니다.


#### Key 형식

API Key는 SB{10자리prefix}.{32자리secret} 형식입니다. prefix(SBXXXXXXXXXX)는 키를 식별하며, secret은 생성 시 1회만 반환됩니다. 서버에는 SHA-256 해시로만 저장되므로 분실 시 재발급이 필요합니다.


#### 주요 특징

- Sandbox / Live 환경별 별도 키 발급 — 환경 간 키 교차 사용 불가
- IP 화이트리스트 최대 10개 등록 가능 (미설정 시 모든 IP 허용)
- 잘못된 키: 401 Unauthorized / 화이트리스트 차단: 403 Forbidden

인증 헤더 예시Copy```
curl 'https://api.sweetbook.com/v1/books' \
  -H 'Authorization: Bearer SBXXXXXXXXXX.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
```

인증 실패 응답 (401 Unauthorized)Copy```
{
  "success": false,
  "message": "유효하지 않은 API Key입니다.",
  "data": null
}
```


### 2. Books API

책의 생성·편집·최종화까지 전체 생명주기를 관리합니다. 책은 DRAFT 상태에서 시작하며,POST /books/{bookUid}/finalization 호출 후 주문 가능한 상태가 됩니다.


#### 엔드포인트 목록

| 메서드 | 경로 | 설명 |
| --- | --- | --- |
| POST | /books | 새 책 생성 (bookSpecUid 필수) |
| GET | /books | 책 목록 조회 — status, limit, offset, isTest 필터 |
| GET | /books/{bookUid} | 책 상세 조회 |
| POST | /books/{bookUid}/cover | 표지 추가 (템플릿 + 이미지 바인딩) |
| POST | /books/{bookUid}/contents | 콘텐츠(내지) 추가 — Gallery 레이아웃 지원 |
| DELETE | /books/{bookUid}/contents | 내지 전체 초기화 |
| POST | /books/{bookUid}/photos | 사진 업로드 (최대 200장, 50MB/파일) |
| GET | /books/{bookUid}/photos | 사진 목록 조회 |
| DELETE | /books/{bookUid}/photos/{photoId} | 사진 삭제 |
| POST | /books/{bookUid}/finalization | 최종화 — 편집 완료, 주문 가능 상태로 전환 |


#### 이미지 업로드 방식

사진 업로드(POST /photos)는 세 가지 방식을 혼합하여 한 번에 전송할 수 있습니다.

- 파일 업로드: multipart/form-data로 직접 전송 ($upload 키 사용)
- URL: 공개 접근 가능한 이미지 URL 지정
- 서버 파일명: 이전에 업로드된 파일의 서버 측 파일명 참조

HEIC / WebP / BMP 포맷은 JPEG으로 자동 변환됩니다. EXIF 방향 정보도 자동으로 보정됩니다. MD5 해시 기반 중복 검사가 적용되어 동일 파일은 재업로드되지 않습니다.


#### Gallery 레이아웃

- Collage: 한 페이지에 최대 9장 배치
- Row: 행 단위 배치, 장 수 제한 없음


#### 외부 시스템 연동

externalRef 파라미터를 통해 파트너 시스템의 고유 ID를 책에 연결할 수 있습니다. 목록 조회 시 해당 값으로 필터링하거나 추적이 가능합니다.

POST /v1/books — 책 생성Copy```
curl -X POST 'https://api.sweetbook.com/v1/books' \
  -H 'Authorization: Bearer YOUR_API_KEY' \
  -H 'Content-Type: application/json' \
  -d '{
  "bookSpecUid": "spec_abc123",
  "externalRef": "my-order-9999"
}'
```

Response (201 Created)Copy```
{
  "success": true,
  "message": "Success",
  "data": {
    "bookUid": "book_xyz789",
    "status": "DRAFT",
    "bookSpecUid": "spec_abc123",
    "externalRef": "my-order-9999",
    "createdAt": "2026-03-24T10:00:00Z"
  }
}
```

POST /v1/books/{bookUid}/photos — 사진 업로드 (혼합)Copy```
curl -X POST 'https://api.sweetbook.com/v1/books/book_xyz789/photos' \
  -H 'Authorization: Bearer YOUR_API_KEY' \
  -F '$upload=@/path/to/photo1.jpg' \
  -F 'url=https://example.com/photo2.jpg'
```

POST /v1/books/{bookUid}/contents — Gallery 레이아웃Copy```
curl -X POST 'https://api.sweetbook.com/v1/books/book_xyz789/contents' \
  -H 'Authorization: Bearer YOUR_API_KEY' \
  -H 'Content-Type: application/json' \
  -d '{
  "layoutType": "COLLAGE",
  "photos": [
    { "photoId": "photo_001" },
    { "photoId": "photo_002" },
    { "photoId": "photo_003" }
  ]
}'
```


### 3. Orders API

견적 조회 후 주문을 생성하면 크레딧이 즉시 차감됩니다. 취소 시 차감된 크레딧은 자동으로 환불됩니다.


#### 엔드포인트 목록

| 메서드 | 경로 | 설명 |
| --- | --- | --- |
| POST | /orders/estimate | 견적 조회 — 주문 전 금액 미리 확인 |
| POST | /orders | 주문 생성 — 크레딧 즉시 차감 |
| GET | /orders | 주문 목록 조회 |
| GET | /orders/{orderUid} | 주문 상세 조회 |
| POST | /orders/{orderUid}/cancel | 주문 취소 — PAID / PDF_READY 상태만 가능, 크레딧 자동 환불 |
| PATCH | /orders/{orderUid}/shipping | 배송지 변경 — PAID / PDF_READY / CONFIRMED 상태 가능 |


#### 금액 계산 공식

| 항목 | 계산식 |
| --- | --- |
| 제품 금액 | 단가 × 수량 |
| 배송비 | 3,500원 / 주문 (수량 무관 고정) |
| 포장비 | 500원 × 수량 |
| 합계 | 제품 금액 + 배송비 + 포장비 |
| 결제 크레딧 (VAT 포함) | floor(합계 × 1.1 / 10) × 10 |


#### 주문 상태 코드 (11종)

| 코드 | 상태명 | 설명 |
| --- | --- | --- |
| 20 | PAID | 결제 완료 — 크레딧 차감됨 |
| 25 | PDF_READY | PDF 생성 완료 — 제작 대기 중 |
| 30 | CONFIRMED | 제작 확정 — 취소 불가 시점 |
| 40 | IN_PRODUCTION | 제작 진행 중 |
| 45 | COMPLETED | 항목 제작 완료 (부분 완료) |
| 50 | PRODUCTION_COMPLETE | 전체 제작 완료 |
| 60 | SHIPPED | 발송 완료 — 운송장 번호 제공 |
| 70 | DELIVERED | 배송 완료 |
| 80 | CANCELLED | 취소 처리됨 |
| 81 | CANCELLED_REFUND | 취소 후 크레딧 환불 완료 |
| 90 | ERROR | 오류 발생 — 고객센터 문의 필요 |

POST /v1/orders/estimate — 견적 조회Copy```
curl -X POST 'https://api.sweetbook.com/v1/orders/estimate' \
  -H 'Authorization: Bearer YOUR_API_KEY' \
  -H 'Content-Type: application/json' \
  -d '{
  "bookUid": "book_xyz789",
  "quantity": 2
}'
```

견적 응답 (200 OK)Copy```
{
  "success": true,
  "message": "Success",
  "data": {
    "unitPrice": 15000,
    "quantity": 2,
    "productAmount": 30000,
    "shippingFee": 3500,
    "packagingFee": 1000,
    "totalAmount": 34500,
    "paidCreditAmount": 37950
  }
}
```

POST /v1/orders — 주문 생성Copy```
curl -X POST 'https://api.sweetbook.com/v1/orders' \
  -H 'Authorization: Bearer YOUR_API_KEY' \
  -H 'Content-Type: application/json' \
  -d '{
  "bookUid": "book_xyz789",
  "quantity": 2,
  "shipping": {
    "recipient": "홍길동",
    "phone": "010-1234-5678",
    "address": "서울시 강남구 테헤란로 123",
    "zipCode": "06234"
  }
}'
```

POST /v1/orders/{orderUid}/cancel — 주문 취소Copy```
curl -X POST 'https://api.sweetbook.com/v1/orders/ord_abc123/cancel' \
  -H 'Authorization: Bearer YOUR_API_KEY'
```


### 4. Templates API

책 표지 및 내지에 적용할 수 있는 디자인 템플릿을 조회합니다. 템플릿에는 $key$ 형식의 파라미터가 포함될 수 있으며, 표지/콘텐츠 추가 시 실제 값으로 치환하여 바인딩합니다.


#### 엔드포인트 목록

| 메서드 | 경로 | 설명 |
| --- | --- | --- |
| GET | /templates | 템플릿 목록 조회 |
| GET | /templates/{templateUid} | 템플릿 상세 조회 |


#### 목록 조회 필터 파라미터

| 파라미터 | 설명 |
| --- | --- |
| scope | 템플릿 접근 범위 (public / private) |
| templateKind | 종류: cover (표지) / content (내지) |
| category | 카테고리 — 일기장, 알림장, 사진앨범 등 |
| bookSpecUid | 특정 판형에 호환되는 템플릿만 필터 |
| limit / offset | 페이지네이션 |


#### 파라미터 바인딩

템플릿 내 $title$, $date$ 등의 플레이스홀더는 표지/콘텐츠 추가 요청 시parameters 객체에 키-값을 전달하여 치환됩니다.

GET /v1/templates — 목록 조회Copy```
curl 'https://api.sweetbook.com/v1/templates?templateKind=cover&category=사진앨범&bookSpecUid=spec_abc123&limit=10' \
  -H 'Authorization: Bearer YOUR_API_KEY'
```

Response (200 OK)Copy```
{
  "success": true,
  "message": "Success",
  "data": {
    "total": 24,
    "templates": [
      {
        "templateUid": "tmpl_001",
        "name": "미니멀 사진앨범 표지",
        "templateKind": "cover",
        "category": "사진앨범",
        "bookSpecUid": "spec_abc123",
        "parameters": ["$title$", "$date$"]
      }
    ]
  }
}
```

POST /v1/books/{bookUid}/cover — 표지 바인딩Copy```
curl -X POST 'https://api.sweetbook.com/v1/books/book_xyz789/cover' \
  -H 'Authorization: Bearer YOUR_API_KEY' \
  -H 'Content-Type: application/json' \
  -d '{
  "templateUid": "tmpl_001",
  "parameters": {
    "$title$": "우리 가족 앨범",
    "$date$": "2026.03"
  },
  "photoId": "photo_cover_001"
}'
```


### 5. BookSpecs API

책 생성에 사용할 수 있는 판형(크기·제본 방식) 목록과 가격 정보를 조회합니다.bookSpecUid는 책 생성 시 필수 파라미터입니다.


#### 엔드포인트 목록

| 메서드 | 경로 | 설명 |
| --- | --- | --- |
| GET | /book-specs | 판형 목록 조회 |
| GET | /book-specs/{bookSpecUid} | 판형 상세 조회 |


#### 제공 판형 종류

| 판형명 | 크기 | 제본 |
| --- | --- | --- |
| A4 소프트커버 | 210 × 297 mm | 소프트커버 무선제본 |
| A5 소프트커버 | 148 × 210 mm | 소프트커버 무선제본 |
| 스퀘어북 하드커버 | 210 × 210 mm | 하드커버 양장 |
| 레이플랫 하드커버 | 210 × 297 mm | 하드커버 레이플랫 |
| 슬림앨범 하드커버 | 148 × 210 mm | 하드커버 양장 |


#### 가격 계산 방식

기본 가격은 pageMin까지의 페이지를 포함합니다. 초과 페이지는 pageIncrement 단위로 추가되며, 초과분당 pricePerExtraPage가 부과됩니다. 전체 페이지 수는 pageMin 이상 pageMax 이하여야 합니다.

- 단가 = 기본가 + (초과 페이지 수 ÷ pageIncrement) × 페이지당 추가금
- 페이지는 반드시 pageIncrement 배수 단위로만 추가 가능

GET /v1/book-specs — 판형 목록Copy```
curl 'https://api.sweetbook.com/v1/book-specs' \
  -H 'Authorization: Bearer YOUR_API_KEY'
```

Response (200 OK)Copy```
{
  "success": true,
  "message": "Success",
  "data": {
    "bookSpecs": [
      {
        "bookSpecUid": "spec_abc123",
        "name": "A4 소프트커버",
        "basePrice": 12000,
        "pricePerExtraPage": 200,
        "pageMin": 24,
        "pageMax": 200,
        "pageIncrement": 4
      }
    ]
  }
}
```


### 6. Credits API

주문 생성 시 사용되는 크레딧 잔액을 조회합니다. Sandbox와 Live 환경은 잔액이 완전히 분리되어 독립적으로 관리됩니다.


#### 엔드포인트

| 메서드 | 경로 | 설명 |
| --- | --- | --- |
| GET | /credits | 현재 크레딧 잔액 조회 |


#### 크레딧 운영 규칙

- 주문 생성(POST /orders) 시 paidCreditAmount만큼 즉시 차감
- 주문 취소 시 차감된 크레딧 전액 자동 환불
- 잔액 부족 시 402 Payment Required 반환
- Sandbox 환경 잔액은 실제 결제와 무관한 테스트 전용 크레딧

GET /v1/credits — 잔액 조회Copy```
curl 'https://api.sweetbook.com/v1/credits' \
  -H 'Authorization: Bearer YOUR_API_KEY'
```

Response (200 OK)Copy```
{
  "success": true,
  "message": "Success",
  "data": {
    "balance": 150000,
    "env": "live",
    "currency": "KRW"
  }
}
```

잔액 부족 응답 (402 Payment Required)Copy```
{
  "success": false,
  "message": "크레딧이 부족합니다.",
  "data": {
    "required": 37950,
    "balance": 10000
  }
}
```


### 7. Webhooks API

주문 상태 변경 등의 이벤트가 발생할 때 지정한 URL로 HTTP POST 요청을 전송합니다. 수신 서버는 HMAC-SHA256 서명을 검증하여 요청의 신뢰성을 확인해야 합니다.


#### 엔드포인트 목록

| 메서드 | 경로 | 설명 |
| --- | --- | --- |
| PUT | /webhooks/config | 웹훅 URL 및 secret 등록/수정 |
| GET | /webhooks/config | 현재 웹훅 설정 조회 |
| DELETE | /webhooks/config | 웹훅 설정 삭제 |
| POST | /webhooks/test | 테스트 이벤트 즉시 전송 |
| GET | /webhooks/deliveries | 전송 이력 조회 (성공/실패 포함) |


#### 지원 이벤트

| 이벤트 | 발생 시점 |
| --- | --- |
| order.paid | 주문 생성 및 크레딧 차감 완료 |
| order.confirmed | 제작 확정 — 이후 취소 불가 |
| order.status_changed | 주문 상태 변경 시 (모든 상태 전환) |
| order.shipped | 발송 완료 — 운송장 번호 포함 |
| order.cancelled | 주문 취소 및 환불 처리 완료 |


#### 전송 헤더

| 헤더 | 설명 |
| --- | --- |
| X-Webhook-Event | 이벤트 종류 (예: order.paid) |
| X-Webhook-Signature | HMAC-SHA256 서명 (sha256=...) |
| X-Webhook-Timestamp | 전송 시각 (Unix timestamp) |
| X-Webhook-Delivery-Id | 전송 이력 고유 ID |


#### 재시도 정책

수신 서버가 2xx 응답을 반환하지 않으면 최대 3회 재시도합니다. 재시도 간격: 1분 후 → 5분 후 → 30분 후. 3회 모두 실패하면 해당 전송은 실패 처리되며 GET /webhooks/deliveries에서 확인할 수 있습니다.

PUT /v1/webhooks/config — 설정 등록Copy```
curl -X PUT 'https://api.sweetbook.com/v1/webhooks/config' \
  -H 'Authorization: Bearer YOUR_API_KEY' \
  -H 'Content-Type: application/json' \
  -d '{
  "url": "https://your-server.com/webhooks/sweetbook",
  "secret": "your-webhook-secret-key"
}'
```

웹훅 페이로드 예시 (order.shipped)Copy```
{
  "event": "order.shipped",
  "timestamp": "2026-03-25T14:30:00Z",
  "data": {
    "orderUid": "ord_abc123",
    "status": "SHIPPED",
    "trackingNumber": "1234567890",
    "carrier": "CJ대한통운"
  }
}
```

서명 검증 예시 (Node.js)Copy```
const crypto = require('crypto');

function verifySignature(payload, signature, secret) {
  const expected = 'sha256=' + crypto
    .createHmac('sha256', secret)
    .update(payload)
    .digest('hex');
  return crypto.timingSafeEqual(
    Buffer.from(expected),
    Buffer.from(signature)
  );
}
```


### 8. 플랫폼 공통 특징

v1.0 전체에 적용되는 공통 동작 및 제약 사항입니다.

| 항목 | 내용 |
| --- | --- |
| 인증 방식 | API Key — Bearer token (Authorization 헤더) |
| 환경 분리 | Sandbox / Live 환경 독립 운영 — 키·크레딧·데이터 모두 분리 |
| 응답 형식 | JSON { success, message, data } 구조 통일 |
| 페이지네이션 | limit / offset 기반 (전체 목록 조회 API 공통) |
| Rate Limiting | 일반 API 300 req/min, 업로드 API 200 req/min |
| 날짜 형식 | ISO 8601 UTC (2026-03-24T00:00:00Z) |
| 이미지 자동 변환 | HEIC / WebP / BMP → JPEG 자동 변환, EXIF 방향 자동 보정 |
| 중복 이미지 검사 | MD5 해시 기반 — 동일 파일 재업로드 방지 |
| Webhook 보안 | HMAC-SHA256 서명 (X-Webhook-Signature) |
| Idempotency-Key | 미지원 (v1.0.1에서 추가됨) |

