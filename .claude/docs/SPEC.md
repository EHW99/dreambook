# 꿈꾸는 나 — 서비스 설계서

## 1. 서비스 개요

**꿈꾸는 나(dreambook)**는 아이의 이름/생년월일/사진/직업을 입력하면, AI가 그 직업으로 활약하는 동화책을 만들어 실물 책으로 인쇄/배송하는 서비스이다.

- **타겟**: 유아(5~7세) 자녀를 둔 부모, 유치원/어린이집
- **차별점**: 아이 사진 기반 캐릭터 + 직업 동화 개인화
- **회사**: (주)스위트북 — 포토북 인쇄/배송 인프라 보유
- **기본 판형**: SQUAREBOOK_HC (243x248mm, 하드커버, 24~130p)

---

## 2. 사용자 플로우

```
0. 랜딩 페이지
   서비스 소개, 샘플 동화책 미리보기, 가격/이용권 안내
   [비로그인 접근 가능]
            ↓
1. 회원가입 / 로그인
   이메일 + 비밀번호 기반 인증 (JWT)
            ↓
2. 이용권 구매 (목업)
   이용권 선택 → 결제 (목업: 버튼 누르면 즉시 구매 완료)
   이용권이 있으면 스킵
            ↓
3. 정보 입력
   아이 이름, 생년월일, 사진 업로드
   (기존 등록 사진에서 선택도 가능)
            ↓
4. 직업 선택
   카테고리별 목록에서 선택
            ↓
5. 동화 스타일 선택
   꿈꾸는 오늘 / 미래의 나
            ↓
6. 그림체 선택
   수채화 / 연필화 / 크레파스 / 3D / 만화
   각 스타일별 샘플 이미지 미리보기
            ↓
7. 캐릭터 미리보기
   아이 사진 + 그림체 + 직업 복장 + 동화 스타일 반영
   → 캐릭터 시트 생성 (Phase 3)
   → Phase 2에서는 더미 캐릭터 이미지
   마음에 안 들면 재생성 (최대 4회, 갤러리 방식)
   확정해야 다음 단계 진행
            ↓
8. 옵션 선택
   페이지 수 (24p~), 판형
   예상 가격 실시간 표시
            ↓
9. 줄거리 작성
   스토리 테마 선택 (Phase 2: "직접 쓸래요"만 동작)
   나머지 테마는 "준비 중" 배지 + 토스트 메시지
            ↓
10. 생성 중
    AI 스토리 → AI 이미지 (Phase 3)
    Phase 2: 더미 데이터로 즉시 완료
    원형 진행률 + 예상 소요 시간 안내
            ↓
11. 편집 / 미리보기
    페이지별 일러스트 + 텍스트 확인
    텍스트 직접 수정 가능
    스토리 재생성 (3회) / 이미지 재생성 (페이지당 4회)
    → Phase 2: 재생성 UI만, 실제 AI 호출은 Phase 3
    전체 미리보기 (책 넘기기 뷰)
            ↓
12. 주문
    배송지 입력 (수령인, 주소, 전화번호)
    Book Print API로 책 생성 → 사진 업로드 → 표지/내지 → 최종화 → 견적 → 주문
```

---

## 3. 페이지 구성

### 3.1 랜딩 페이지 (`/`)
- 서비스 소개 히어로 섹션
- 샘플 동화책 미리보기 (책 뷰어로 연결)
- 그림체 스타일별 샘플 이미지 갤러리
- 가격/이용권 안내 섹션
- "동화책 만들기" CTA 버튼 → 비로그인 시 로그인 페이지로 이동
- 접근 권한: 비로그인 O

### 3.2 회원가입 페이지 (`/signup`)
- 이메일, 비밀번호, 비밀번호 확인
- 입력 검증: 이메일 형식, 이메일 중복, 비밀번호 최소 8자
- 에러 메시지: "이미 가입된 이메일입니다", "비밀번호가 일치하지 않습니다" 등
- 가입 성공 → 로그인 페이지로 이동

### 3.3 로그인 페이지 (`/login`)
- 이메일, 비밀번호
- 에러 메시지: "이메일 또는 비밀번호가 틀렸습니다"
- 로그인 성공 → JWT 발급 → 이전 페이지 또는 홈으로 이동
- 회원가입 링크

### 3.4 마이페이지 (`/mypage`)
- 접근 권한: 로그인 필수
- 탭 구성:
  - **회원 정보**: 이메일(변경 불가), 비밀번호 변경, 회원 탈퇴
  - **아이 사진 관리**: 등록된 사진 목록, 추가 업로드, 삭제
  - **내 책장**: 완성된/작성중인 동화책 목록, 새 동화책 만들기 버튼
  - **주문 내역**: 주문 목록 (날짜, 책 제목, 상태, 가격), 주문 상세

### 3.5 동화책 만들기 위자드 (`/create`)
- 스텝 바이 스텝 위자드 UI
- 진행 표시 바 (현재 단계 표시)
- 뒤로가기/다음 버튼
- 단계: 정보 입력 → 직업 선택 → 동화 스타일 → 그림체 → 캐릭터 미리보기 → 옵션 → 줄거리 → 생성 중 → 편집
- beforeunload 이벤트로 이탈 방지
- "다음" 버튼 시 해당 단계 서버 저장

### 3.6 편집/미리보기 페이지 (`/create/edit`)
- 페이지별 일러스트 + 텍스트 좌우 배치
- 텍스트 인라인 편집
- 재생성 버튼 (남은 횟수 표시)
- 전체 미리보기 (책 넘기기 뷰)

### 3.7 책 뷰어 (`/books/:id/view`)
- 접근 권한: 로그인 필수 (본인 책만)
- 페이지 플립 애니메이션 (책 넘기기 효과)
- 전체화면 모드
- 오디오북 재생 버튼

### 3.8 오디오북 뷰어 (`/books/:id/listen`)
- 일러스트를 화면에 띄우면서 TTS가 해당 페이지 텍스트를 읽어줌
- 자동 페이지 넘김
- 재생/일시정지 컨트롤
- Phase 2: UI + 브라우저 기본 TTS (SpeechSynthesis API)

### 3.9 주문 페이지 (`/create/order`)
- 배송지 입력 (수령인, 주소, 전화번호, 우편번호, 상세주소, 메모)
- 견적 표시 (Book Print API estimate)
- 주문 확정 버튼

### 3.10 에러/빈 상태 페이지
- 404 페이지 (없는 페이지) — 따뜻한 일러스트 + "길을 잃었나봐요"
- 500 에러 페이지 — "잠시 후 다시 시도해주세요"
- 빈 상태: "아직 만든 동화책이 없어요", "등록된 사진이 없어요" 등

---

## 4. DB 스키마

### 4.1 users (사용자)
| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | INTEGER PK | 자동 증가 |
| email | VARCHAR(255) UNIQUE | 이메일 |
| password_hash | VARCHAR(255) | bcrypt 해시 |
| created_at | DATETIME | 가입일 |
| updated_at | DATETIME | 수정일 |

### 4.2 photos (아이 사진)
| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | INTEGER PK | 자동 증가 |
| user_id | INTEGER FK → users | 소유자 |
| file_path | VARCHAR(500) | 서버 저장 경로 |
| original_name | VARCHAR(255) | 원본 파일명 |
| file_size | INTEGER | 파일 크기 (바이트) |
| width | INTEGER | 가로 해상도 |
| height | INTEGER | 세로 해상도 |
| created_at | DATETIME | 업로드일 |

제약: 사용자당 최대 20장. 허용 형식: JPG, PNG, WebP. 최대 10MB. 최소 해상도: 512x512.

### 4.3 books (동화책)
| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | INTEGER PK | 자동 증가 |
| user_id | INTEGER FK → users | 소유자 |
| voucher_id | INTEGER FK → vouchers | 사용된 이용권 |
| child_name | VARCHAR(50) | 아이 이름 |
| child_birth_date | DATE | 생년월일 |
| photo_id | INTEGER FK → photos | 선택된 사진 |
| job_category | VARCHAR(50) | 직업 카테고리 |
| job_name | VARCHAR(50) | 선택된 직업 |
| story_style | VARCHAR(20) | "dreaming_today" / "future_me" |
| art_style | VARCHAR(20) | 수채화/연필화/크레파스/3D/만화 |
| page_count | INTEGER | 페이지 수 (24~) |
| book_spec_uid | VARCHAR(50) | 판형 UID |
| plot_input | TEXT | 사용자 입력 줄거리 |
| status | VARCHAR(20) | draft/character_confirmed/generating/editing/completed |
| current_step | INTEGER | 현재 진행 단계 번호 |
| title | VARCHAR(200) | 동화책 제목 (AI 생성 또는 자동 생성) |
| story_regen_count | INTEGER DEFAULT 0 | 스토리 재생성 횟수 (최대 3) |
| character_regen_count | INTEGER DEFAULT 0 | 캐릭터 재생성 횟수 (최대 4) |
| bookprint_book_uid | VARCHAR(50) | Book Print API의 bookUid |
| created_at | DATETIME | 생성일 |
| updated_at | DATETIME | 수정일 |

### 4.4 character_sheets (캐릭터 시트)
| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | INTEGER PK | 자동 증가 |
| book_id | INTEGER FK → books | 소속 동화책 |
| image_path | VARCHAR(500) | 저장 경로 |
| generation_index | INTEGER | 생성 순서 (0~4) |
| is_selected | BOOLEAN | 선택 여부 |
| created_at | DATETIME | 생성일 |

갤러리 방식: 재생성 시 기존 결과 유지. 생성된 모든 시트 중 선택.

### 4.5 pages (동화책 페이지)
| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | INTEGER PK | 자동 증가 |
| book_id | INTEGER FK → books | 소속 동화책 |
| page_number | INTEGER | 페이지 번호 (1~) |
| page_type | VARCHAR(20) | title/content/ending |
| scene_description | TEXT | 장면 설명 (AI 생성용) |
| text_content | TEXT | 페이지 텍스트 (사용자 편집 가능) |
| image_regen_count | INTEGER DEFAULT 0 | 이미지 재생성 횟수 (최대 4) |
| created_at | DATETIME | 생성일 |
| updated_at | DATETIME | 수정일 |

### 4.6 page_images (페이지 이미지)
| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | INTEGER PK | 자동 증가 |
| page_id | INTEGER FK → pages | 소속 페이지 |
| image_path | VARCHAR(500) | 저장 경로 |
| generation_index | INTEGER | 생성 순서 |
| is_selected | BOOLEAN | 선택 여부 |
| created_at | DATETIME | 생성일 |

갤러리 방식: 재생성 시 기존 결과 유지. 생성된 이미지 중 선택.

### 4.7 vouchers (이용권)
| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | INTEGER PK | 자동 증가 |
| user_id | INTEGER FK → users | 소유자 |
| voucher_type | VARCHAR(30) | "story_only" / "story_and_print" |
| price | INTEGER | 가격 (9900 또는 29900) |
| status | VARCHAR(20) | purchased / used / expired |
| book_id | INTEGER FK → books NULL | 사용된 동화책 |
| purchased_at | DATETIME | 구매일 |
| used_at | DATETIME NULL | 사용일 |

### 4.8 orders (주문)
| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | INTEGER PK | 자동 증가 |
| user_id | INTEGER FK → users | 주문자 |
| book_id | INTEGER FK → books | 주문 동화책 |
| bookprint_order_uid | VARCHAR(50) | Book Print API orderUid |
| status | VARCHAR(30) | PAID/PDF_READY/CONFIRMED/IN_PRODUCTION/SHIPPED/DELIVERED/CANCELLED |
| status_code | INTEGER | 상태 코드 (20,25,30,40,50,60,70,80,81) |
| recipient_name | VARCHAR(100) | 수령인 |
| recipient_phone | VARCHAR(20) | 전화번호 |
| postal_code | VARCHAR(10) | 우편번호 |
| address1 | VARCHAR(200) | 주소 |
| address2 | VARCHAR(200) | 상세주소 |
| shipping_memo | VARCHAR(200) | 배송 메모 |
| total_amount | INTEGER | 총 금액 |
| tracking_number | VARCHAR(50) | 운송장 번호 |
| tracking_carrier | VARCHAR(20) | 택배사 코드 |
| ordered_at | DATETIME | 주문일 |
| updated_at | DATETIME | 상태 변경일 |

### 관계도
```
users (1) ──→ (N) photos
users (1) ──→ (N) vouchers
users (1) ──→ (N) books
users (1) ──→ (N) orders
books (1) ──→ (N) character_sheets
books (1) ──→ (N) pages
books (1) ──→ (1) orders
pages (1) ──→ (N) page_images
vouchers (1) ──→ (0..1) books
```

### 삭제 정책
- **회원 탈퇴**: 모든 데이터 즉시 삭제 (CASCADE) — users, photos(파일 포함), books, character_sheets, pages, page_images, vouchers, orders
- **사진 삭제**: DB 레코드 + 서버 파일 즉시 삭제. 이미 생성된 캐릭터 시트/일러스트는 유지
- **동화책 삭제**: 작성중 상태만 삭제 가능. 완성/주문된 책은 삭제 불가

---

## 5. API 엔드포인트 목록

### 5.1 인증 API

| 메서드 | 경로 | 설명 | 인증 |
|--------|------|------|------|
| POST | `/api/auth/signup` | 회원가입 | X |
| POST | `/api/auth/login` | 로그인 (JWT 발급) | X |
| POST | `/api/auth/refresh` | 토큰 갱신 | O |
| GET | `/api/auth/me` | 내 정보 조회 | O |

### 5.2 사용자 API

| 메서드 | 경로 | 설명 | 인증 |
|--------|------|------|------|
| PATCH | `/api/users/password` | 비밀번호 변경 | O |
| DELETE | `/api/users/me` | 회원 탈퇴 | O |

### 5.3 사진 API

| 메서드 | 경로 | 설명 | 인증 |
|--------|------|------|------|
| GET | `/api/photos` | 내 사진 목록 | O |
| POST | `/api/photos` | 사진 업로드 | O |
| DELETE | `/api/photos/:id` | 사진 삭제 | O |

요청 검증: 형식(JPG/PNG/WebP), 크기(10MB), 해상도(512x512), 개수(20장)
에러: "지원하지 않는 파일 형식입니다", "파일 크기가 10MB를 초과합니다", "최대 20장까지 등록 가능합니다", "최소 512x512 이상의 이미지를 업로드해주세요"

### 5.4 이용권 API

| 메서드 | 경로 | 설명 | 인증 |
|--------|------|------|------|
| GET | `/api/vouchers` | 내 이용권 목록 | O |
| POST | `/api/vouchers/purchase` | 이용권 구매 (목업) | O |

### 5.5 동화책 API

| 메서드 | 경로 | 설명 | 인증 |
|--------|------|------|------|
| GET | `/api/books` | 내 동화책 목록 (내 책장) | O |
| POST | `/api/books` | 동화책 생성 (작성 시작) | O |
| GET | `/api/books/:id` | 동화책 상세 조회 | O |
| PATCH | `/api/books/:id` | 동화책 정보 수정 (단계별 저장) | O |
| DELETE | `/api/books/:id` | 동화책 삭제 (작성중만) | O |

### 5.6 캐릭터 API

| 메서드 | 경로 | 설명 | 인증 |
|--------|------|------|------|
| POST | `/api/books/:id/character` | 캐릭터 시트 생성 (Phase 3: AI, Phase 2: 더미) | O |
| GET | `/api/books/:id/characters` | 캐릭터 시트 갤러리 조회 | O |
| PATCH | `/api/books/:id/character/:charId/select` | 캐릭터 선택 (확정) | O |

### 5.7 스토리/페이지 API

| 메서드 | 경로 | 설명 | 인증 |
|--------|------|------|------|
| POST | `/api/books/:id/generate` | 스토리+이미지 생성 (Phase 3: AI, Phase 2: 더미) | O |
| GET | `/api/books/:id/pages` | 전체 페이지 조회 | O |
| PATCH | `/api/books/:id/pages/:pageId` | 페이지 텍스트 수정 | O |
| POST | `/api/books/:id/regenerate-story` | 스토리 재생성 (Phase 3) | O |
| POST | `/api/books/:id/pages/:pageId/regenerate-image` | 페이지 이미지 재생성 (Phase 3) | O |
| GET | `/api/books/:id/pages/:pageId/images` | 페이지 이미지 갤러리 | O |
| PATCH | `/api/books/:id/pages/:pageId/images/:imgId/select` | 이미지 선택 | O |

### 5.8 주문 API

| 메서드 | 경로 | 설명 | 인증 |
|--------|------|------|------|
| POST | `/api/books/:id/estimate` | 견적 조회 (Book Print API 연동) | O |
| POST | `/api/books/:id/order` | 주문 생성 (Book Print API 전체 워크플로우) | O |
| GET | `/api/orders` | 내 주문 목록 | O |
| GET | `/api/orders/:id` | 주문 상세 | O |
| POST | `/api/orders/:id/cancel` | 주문 취소 | O |
| PATCH | `/api/orders/:id/shipping` | 배송지 변경 | O |

### 5.9 웹훅 API

| 메서드 | 경로 | 설명 | 인증 |
|--------|------|------|------|
| POST | `/api/webhooks/sweetbook` | Book Print API 웹훅 수신 | HMAC 서명 검증 |

### 5.10 TTS API (오디오북)

| 메서드 | 경로 | 설명 | 인증 |
|--------|------|------|------|
| GET | `/api/books/:id/audio-data` | 오디오북용 페이지별 텍스트+이미지 | O |

---

## 6. Book Print API 연동 흐름

주문 확정 시점에 Book Print API를 일괄 호출한다. 편집 단계까지는 우리 서버 DB에만 저장.

### 6.1 전체 흐름

```
[사용자: 주문 확정 버튼 클릭]
        ↓
1. Sandbox 충전금 확인
   GET /credits → 잔액 확인
   부족 시 POST /credits/sandbox/charge → 자동 충전
        ↓
2. 책 생성
   POST /books
   body: { title, bookSpecUid: "SQUAREBOOK_HC", creationType: "TEST" }
   → bookUid 획득
        ↓
3. 사진 업로드 (일러스트 이미지들)
   POST /books/{bookUid}/photos
   → 표지 이미지 + 내지 이미지 × 페이지 수
   → 각 fileName 획득
        ↓
4. 템플릿 조회
   GET /templates?bookSpecUid=SQUAREBOOK_HC
   → 사용할 표지/내지 템플릿 UID 확보
        ↓
5. 표지 생성
   POST /books/{bookUid}/cover
   body: templateUid, parameters(제목, 표지이미지)
        ↓
6. 내지 삽입 (반복)
   POST /books/{bookUid}/contents?breakBefore=page
   body: templateUid, parameters(텍스트, 이미지)
   → 페이지 수만큼 반복
        ↓
7. 책 최종화
   POST /books/{bookUid}/finalization
   → FINALIZED 상태 전환
        ↓
8. 견적 조회
   POST /orders/estimate
   body: { items: [{ bookUid, quantity: 1 }] }
   → 예상 가격 확인
        ↓
9. 주문 생성
   POST /orders
   body: { items, shipping(수령인, 주소 등) }
   → orderUid 획득, 충전금 차감
        ↓
10. 웹훅 수신 대기
    POST /api/webhooks/sweetbook
    → order.paid, order.status_changed 등 상태 업데이트
```

### 6.2 제약사항 반영

- **GET /book-specs 403 에러**: 판형 UID 하드코딩으로 우회
  - SQUAREBOOK_HC, PHOTOBOOK_A4_SC, PHOTOBOOK_A5_SC
- **Sandbox 환경**: 주문이 PAID(20) 상태에서 멈춤 (이후 상태 전이 없음)
- **충전금**: Sandbox에서 0원 시작. `POST /credits/sandbox/charge`로 자동 충전 로직 필요
- **테스트 가격**: Sandbox에서는 100원 이하 적용
- **템플릿**: 실제 사용 가능한 템플릿을 API 호출로 조회 후 적합한 것 선택

### 6.3 에러 처리

| 상황 | 처리 |
|------|------|
| 충전금 부족 (402) | 자동 충전 시도 → 재주문 |
| 책 미존재/미FINALIZED (400) | 사용자에게 "책 생성에 실패했습니다" 안내 |
| 인증 실패 (401) | API Key 설정 확인 안내 |
| Rate Limit (429) | 재시도 (Retry-After 헤더 참고) |
| 서버 오류 (500) | 재시도 + 실패 시 사용자 안내 |

---

## 7. 인증 방식

### 7.1 사용자 인증 (프론트엔드 ↔ 백엔드)

- **방식**: JWT (JSON Web Token)
- **로그인**: 이메일 + 비밀번호 → bcrypt 검증 → Access Token + Refresh Token 발급
- **Access Token**: 유효기간 1시간, 매 API 요청 시 `Authorization: Bearer {token}` 헤더
- **Refresh Token**: 유효기간 7일, httpOnly 쿠키 저장, Access Token 만료 시 갱신
- **로그아웃**: 클라이언트에서 토큰 삭제

### 7.2 Book Print API 인증 (백엔드 → 스위트북)

- **방식**: API Key (Bearer Token)
- **저장**: 환경변수 `BOOKPRINT_API_KEY`
- **사용**: 백엔드 서버에서만 사용 (프론트엔드 노출 금지)
- **URL**: 환경변수 `BOOKPRINT_BASE_URL`

### 7.3 OpenAI API 인증 (백엔드 → OpenAI)

- **방식**: API Key (Bearer Token)
- **저장**: 환경변수 `OPENAI_API_KEY`
- **사용**: 백엔드 서버에서만 사용

---

## 8. AI 연동 인터페이스 (Phase 3 대비)

### 8.1 스토리 생성

- **호출 시점**: "생성 중" 단계에서 호출
- **입력**: 아이 이름, 직업, 동화 스타일, 줄거리, 페이지 수
- **출력**: 페이지별 텍스트 + scene_description (이미지 생성 프롬프트)
- **모델**: GPT-4o (OpenAI API)
- **Phase 2 스텁**: 하드코딩된 더미 스토리 반환 (아이 이름, 직업을 변수 치환)

### 8.2 캐릭터 시트 생성

- **호출 시점**: "캐릭터 미리보기" 단계에서 호출
- **입력**: 아이 사진 + 그림체 + 직업 + 동화 스타일
- **출력**: 캐릭터 시트 이미지 (정면/측면/전신)
- **API**: GPT Image `images.edit` (참조 이미지로 아이 사진 입력)
- **Phase 2 스텁**: 더미 캐릭터 이미지 반환

### 8.3 페이지 일러스트 생성

- **호출 시점**: "생성 중" 단계에서 스토리 생성 후 호출
- **입력**: 캐릭터 시트 (참조 이미지) + scene_description + 그림체 키워드
- **출력**: 1024x1024 PNG 이미지
- **API**: GPT Image `images.edit` (캐릭터 시트를 참조 이미지로 입력)
- **Phase 2 스텁**: 더미 일러스트 이미지 반환

### 8.4 스텁 구현 범위 (Phase 2)

| 기능 | Phase 2 (스텁) | Phase 3 (실제) |
|------|---------------|---------------|
| 캐릭터 시트 생성 | 미리 준비된 더미 이미지 반환 | GPT Image images.edit |
| 스토리 생성 | 템플릿 기반 더미 텍스트 (이름/직업 치환) | GPT-4o |
| 페이지 일러스트 | 미리 준비된 더미 이미지 반환 | GPT Image images.edit |
| 재생성 | 횟수 카운트만, 동일 더미 반환 | 실제 새로운 결과 생성 |
| 오디오북 TTS | 브라우저 SpeechSynthesis API | 고급 TTS API |

### 8.5 재생성 규칙

- **캐릭터 시트**: 최대 4회, 갤러리 방식 (기존 유지 + 새로 생성 → 선택)
- **스토리**: 최대 3회, 교체 방식 (이전 스토리 삭제)
  - 스토리 재생성 시 → 기존 페이지 이미지 전부 폐기 → 새 이미지 자동 생성 → 이미지 재생성 횟수 리셋
- **이미지**: 페이지당 최대 4회, 갤러리 방식
- **UI**: 남은 횟수 표시, 초과 시 "재생성 횟수를 모두 사용했습니다" 메시지

---

## 9. 디자인 시스템

### 색상 팔레트
```
Primary:    #FFB5A7 (따뜻한 살몬 핑크)
Secondary:  #FCD5CE (연한 복숭아)
Accent:     #A8DADC (부드러운 민트)
Background: #FFF8F0 (따뜻한 아이보리)
Text:       #2D3436 (부드러운 차콜)
Success:    #B5EAD7 (연한 민트 그린)
Warning:    #FFE0AC (부드러운 옐로우)
```

### UI 라이브러리
- shadcn/ui + Tailwind CSS
- Framer Motion (페이지 전환, 카드 애니메이션)
- LottieFiles (로딩, 축하 애니메이션)
- Lucide Icons (라인 아이콘)

### 디자인 원칙
- 모든 모서리 둥글게 (12~20px)
- 부드러운 그림자 (투명도 낮게)
- 부드러운 페이지 전환
- 따뜻한 로딩 애니메이션
- 빈 상태 일러스트
- 반응형 (데스크톱/태블릿/모바일)
- 아동/가족 서비스에 어울리는 친근한 느낌

---

## 10. 뒤로가기 / 저장 정책

### 저장 정책
- "다음" 버튼 클릭 시 해당 단계 데이터 서버 저장
- 단계 내부 작업 중에는 저장되지 않음
- 자동 저장 없음
- 브라우저 닫기 시: beforeunload 경고창
- 재접속 시: 마지막 "다음" 단계부터 이어서

### 뒤로가기 규칙
| 현재 단계 | 뒤로가기 | 처리 |
|----------|---------|------|
| 정보 입력 ~ 그림체 선택 | O | 자유 이동 |
| 캐릭터 미리보기 (확정 전) | O | 자유 이동 |
| 캐릭터 확정 후 → 이전 단계 | O | 캐릭터 재선택 가능, 재생성 횟수 유지, 이후 단계 리셋 |
| 줄거리 작성 | O | 이전 자유 이동, 입력 내용 유지 |
| 생성 중 | X | 뒤로가기 차단 |
| 편집/미리보기 | O | 이전 단계 이동 시 콘텐츠 유지 |
| 주문 (배송지 입력) | O | 편집으로 돌아가기 가능 |
| 주문 (결제 완료 후) | X | 돌아갈 수 없음 |
