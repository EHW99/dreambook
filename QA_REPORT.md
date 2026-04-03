# QA 리포트 — 태스크 2: 회원가입 / 로그인 / 인증 (R2)

## 전체 판정: PASS
## 가중 점수: 8.1 / 10.0

## 항목별 점수
- 기능 완성도 (30%): 9/10 — SPEC의 모든 인증 API 및 프론트엔드 기능 구현 완료, R1 피드백 6건 모두 정확히 반영됨
- 코드 품질 (25%): 8/10 — 보안 우수(httpOnly 쿠키, bcrypt, 토큰 타입 검증), 에러 처리 적절, 구조 명확. login 응답 JSON에 refresh_token이 여전히 포함되는 점은 디버깅 편의상 허용 가능하나 프로덕션에서는 제거 권장
- API 연동 (20%): 7/10 — 현 태스크는 Book Print API 연동 범위 아님. 자체 인증 API 설계 및 구현은 정확함
- 디자인 품질 (25%): 8/10 — 파스텔 색상 팔레트, 둥근 모서리, 웹 폰트(Noto Sans KR + Gowun Batang), Framer Motion 페이지 전환 적용. 반응형 대응(max-w-md + px-4)

**가중 계산**: (9 x 0.3) + (8 x 0.25) + (7 x 0.2) + (8 x 0.25) = 2.7 + 2.0 + 1.4 + 2.0 = **8.1**

## SPEC 완료 기준 대조

### 1. 백엔드 API
- [PASS] `POST /api/auth/signup` — 이메일 형식(정규식), 중복(409), 비밀번호 8자(422) 검증, bcrypt 해시 저장 확인
- [PASS] `POST /api/auth/login` — Access Token(1시간) + Refresh Token(7일) 발급, httpOnly 쿠키 설정 확인
- [PASS] `POST /api/auth/refresh` — 쿠키 기반 Refresh Token 읽기, DB 사용자 존재 확인, 토큰 타입 검증 확인
- [PASS] `GET /api/auth/me` — 토큰 인증, password/password_hash 비노출 확인
- [PASS] `POST /api/auth/logout` — httpOnly 쿠키 삭제 (SPEC에는 "클라이언트에서 토큰 삭제"이나 httpOnly 특성상 서버 엔드포인트 필수 — 적절한 판단)

### 2. 에러 메시지 4종
- [PASS] "이미 가입된 이메일입니다" (409)
- [PASS] "이메일 또는 비밀번호가 틀렸습니다" (401)
- [PASS] "비밀번호는 8자 이상이어야 합니다" (422)
- [PASS] "유효하지 않은 이메일 형식입니다" (422)

### 3. 프론트엔드
- [PASS] 회원가입 페이지 (`/signup`) — 이메일/비밀번호/비밀번호 확인 폼, 프론트엔드 유효성 검사, 서버 에러 표시, 성공 시 로그인 페이지 리다이렉트
- [PASS] 로그인 페이지 (`/login`) — 이메일/비밀번호 폼, 에러 표시, 회원가입 링크
- [PASS] 로그인 성공 시 access_token localStorage 저장 + 홈 리다이렉트
- [PASS] Refresh Token httpOnly 쿠키 저장 — localStorage에서 제거됨, XSS 방지
- [PASS] 인증 필요 페이지 접근 시 리다이렉트 (AuthGuard 컨텍스트)
- [PASS] 토큰 자동 갱신 — 401 및 403 모두 대응

### 4. 디자인
- [PASS] 파스텔 톤 색상 팔레트 적용 (#FFB5A7, #FCD5CE, #A8DADC, #FFF8F0 등 SPEC 일치)
- [PASS] 둥근 모서리 (rounded-3xl 카드, rounded-2xl)
- [PASS] 웹 폰트 로딩 (Noto Sans KR + Gowun Batang via next/font/google, CSS variable)
- [PASS] 페이지 전환 애니메이션 (Framer Motion 페이드인 + 슬라이드업)
- [PASS] 반응형 (max-w-md + px-4)

## R1 피드백 6건 반영 확인

### 1. refresh 엔드포인트 보안 — DB 사용자 존재 확인
- [PASS] `auth.py` refresh 함수에서 `get_user_by_id(db, int(user_id))` 호출, None이면 401 반환
- 테스트 `test_refresh_deleted_user_rejected`에서 DB에서 사용자 삭제 후 refresh → 401 확인

### 2. Refresh Token httpOnly 쿠키 전환
- [PASS] 백엔드: `response.set_cookie(key="refresh_token", httponly=True, samesite="lax", path="/api/auth/refresh", max_age=...)` 설정
- [PASS] 백엔드: refresh 엔드포인트에서 `Cookie(None)` 파라미터로 쿠키 읽기
- [PASS] 백엔드: `POST /api/auth/logout` 엔드포인트로 쿠키 삭제
- [PASS] 프론트엔드: `api.ts`에서 refresh_token localStorage 코드 완전 제거
- [PASS] 프론트엔드: refresh 호출 시 `credentials: "include"` 설정
- [PASS] 프론트엔드: logout 시 서버 POST /api/auth/logout 호출

### 3. 웹 폰트 로딩
- [PASS] `layout.tsx`에서 `next/font/google`의 `Noto_Sans_KR`과 `Gowun_Batang` import
- [PASS] CSS variable (`--font-noto-sans-kr`, `--font-gowun-batang`)을 `<html>`에 적용
- [PASS] `tailwind.config.ts`에서 CSS variable 기반 fontFamily 설정

### 4. apiClient 403 처리
- [PASS] `api.ts`에서 `res.status === 401 || res.status === 403` 조건으로 토큰 갱신 시도

### 5. 페이지 전환 애니메이션
- [PASS] `framer-motion` 패키지 설치
- [PASS] `page-transition.tsx` 컴포넌트 (opacity: 0, y: 20 → opacity: 1, y: 0, duration 0.4s)
- [PASS] 로그인/회원가입 페이지에 `<PageTransition>` 래퍼 적용

### 6. 누락 테스트 3건
- [PASS] (a) `test_refresh_access_token_type_rejected` — access token을 refresh 쿠키에 넣으면 401
- [PASS] (b) `test_refresh_deleted_user_rejected` — 탈퇴한 사용자의 refresh token → 401
- [PASS] (c) `test_me_refresh_token_rejected` — refresh token으로 /me 접근 → 401

## 테스트 검증
- Developer 테스트 수: 17개 (인증) + 14개 (모델/헬스) = 31개 전체 통과
- 프론트엔드 빌드: Next.js 빌드 성공 (/ , /login, /signup 정상 빌드)
- 빠진 테스트 케이스: 없음

## 보안 점검
- [PASS] API Key 하드코딩 없음 — 환경변수에서 로드
- [PASS] bcrypt 해시 저장 ($2 prefix)
- [PASS] 토큰 타입 분리 (access/refresh) — 교차 사용 차단
- [PASS] httpOnly 쿠키로 Refresh Token 저장 — XSS 방지
- [PASS] password/password_hash 응답 비노출

## 구체적 개선 지시
없음 — R1 피드백 6건 모두 정확히 반영됨. 기존 합격 항목의 퇴보 없음.

## 비고 (프로덕션 배포 전 권장 사항)
- `LoginResponse`에 refresh_token이 JSON 응답에도 포함됨. 프론트엔드에서 이를 localStorage에 저장하지 않으므로 현재 보안 문제는 없으나, 프로덕션 배포 전 JSON 응답에서 제거 권장.
- `config.py`의 `SECRET_KEY` 기본값이 `"dev-secret-key-change-in-production"`. `.env` 오버라이드 구조이므로 개발 중 문제 없으나, 프로덕션 반드시 변경 필요.
- 쿠키에 `secure=False` 설정 — 로컬 개발용. 프로덕션에서는 `secure=True` 필수.
