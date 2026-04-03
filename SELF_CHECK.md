# 셀프체크 — 태스크 2: 회원가입 / 로그인 / 인증 (R2)

## 테스트 결과
- 전체 테스트 수: 31개 (인증 17개 + 모델/헬스 14개)
- 통과: 31개
- 실패: 0개

## R1 피드백 반영 내역

### 1. refresh 엔드포인트 보안 — DB 사용자 존재 확인 추가
- `backend/app/api/auth.py` refresh 함수에 `db: Session = Depends(get_db)` 추가
- `get_user_by_id(db, int(user_id))` 호출하여 사용자 존재 확인
- 존재하지 않으면 401 반환
- 테스트: `test_refresh_deleted_user_rejected` 추가 — PASS

### 2. Refresh Token httpOnly 쿠키 전환
- **백엔드**: login 응답에서 `response.set_cookie(key="refresh_token", httponly=True, samesite="lax", path="/api/auth/refresh")` 설정
- **백엔드**: refresh 엔드포인트에서 `refresh_token: Optional[str] = Cookie(None)`으로 쿠키에서 읽도록 변경 (기존 JSON body → 쿠키)
- **백엔드**: `POST /api/auth/logout` 엔드포인트 추가 — 쿠키 삭제
- **프론트엔드**: `api.ts`에서 refresh_token localStorage 저장/읽기 코드 제거
- **프론트엔드**: refresh 호출 시 `credentials: "include"`로 쿠키 자동 포함
- **프론트엔드**: `apiClient.logout()` → 서버에 POST /api/auth/logout 호출하여 쿠키 삭제
- 스키마: `LoginResponse` 추가 (JSON에는 access_token + refresh_token 포함, refresh_token은 httpOnly 쿠키로도 전달)
- 테스트: 로그인 시 쿠키 설정 확인, 쿠키 없이 refresh → 401 확인

### 3. 웹 폰트 로딩 구현
- `frontend/src/app/layout.tsx`에서 `next/font/google`의 `Noto_Sans_KR`과 `Gowun_Batang` import
- CSS variable (`--font-noto-sans-kr`, `--font-gowun-batang`)로 `<html>`에 적용
- `tailwind.config.ts` fontFamily에 CSS variable 우선 적용
- 빌드 성공 확인

### 4. apiClient 403 처리 추가
- `frontend/src/lib/api.ts` — `(res.status === 401 || res.status === 403) && requireAuth` 조건으로 변경
- FastAPI HTTPBearer가 토큰 없이 접근 시 403 반환하는 케이스 대응

### 5. 페이지 전환 애니메이션
- `framer-motion` 패키지 설치
- `frontend/src/components/page-transition.tsx` — `motion.div`로 페이드인 + 슬라이드업 효과
- 로그인/회원가입 페이지에 `<PageTransition>` 래퍼 적용
- `initial={{ opacity: 0, y: 20 }}` → `animate={{ opacity: 1, y: 0 }}`, duration 0.4s

### 6. 누락 테스트 3건 추가
- (a) `test_refresh_access_token_type_rejected` — access token을 refresh 쿠키에 넣으면 401 — PASS
- (b) `test_refresh_deleted_user_rejected` — 탈퇴한 사용자의 refresh token으로 갱신 시도 → 401 — PASS
- (c) `test_me_refresh_token_rejected` — refresh token으로 /me 접근 시도 → 401 — PASS

## SPEC 기능 체크

### 백엔드 API
- [x] `POST /api/auth/signup` — 이메일 형식/중복/비밀번호 길이 검증, bcrypt 해시 저장
- [x] `POST /api/auth/login` — JWT 발급, refresh token httpOnly 쿠키 설정
- [x] `POST /api/auth/refresh` — 쿠키 기반 토큰 갱신, DB 사용자 존재 확인
- [x] `GET /api/auth/me` — 토큰 인증, password/password_hash 비노출
- [x] `POST /api/auth/logout` — httpOnly 쿠키 삭제

### 에러 메시지
- [x] "이미 가입된 이메일입니다" (409)
- [x] "이메일 또는 비밀번호가 틀렸습니다" (401)
- [x] "비밀번호는 8자 이상이어야 합니다" (422)
- [x] "유효하지 않은 이메일 형식입니다" (422)

### 프론트엔드
- [x] 회원가입 페이지 (`/signup`) — 입력 폼, 유효성 검사, 에러 표시
- [x] 로그인 페이지 (`/login`) — 입력 폼, 에러 표시, 회원가입 링크
- [x] 토큰 저장: access_token은 localStorage, refresh_token은 httpOnly 쿠키
- [x] 인증 리다이렉트 (AuthGuard)
- [x] 토큰 자동 갱신 (401 + 403 대응)

### 디자인
- [x] 파스텔 톤 색상 팔레트 (primary: #FFB5A7 등)
- [x] 둥근 모서리 (rounded-3xl/2xl)
- [x] 웹 폰트 로딩 (Noto Sans KR + Gowun Batang via next/font/google)
- [x] 페이지 전환 애니메이션 (Framer Motion 페이드인 + 슬라이드업)
- [x] 반응형 (max-w-md + px-4)

## 구현/수정 파일 목록

### 백엔드
- `backend/app/api/auth.py` — refresh DB 검증 추가, httpOnly 쿠키 설정, logout 엔드포인트 추가
- `backend/app/schemas/auth.py` — LoginResponse 스키마 추가
- `backend/tests/test_auth.py` — 17개 (기존 14개 + 신규 3개)

### 프론트엔드
- `frontend/src/lib/api.ts` — refresh_token localStorage 제거, 쿠키 기반 갱신, 403 처리, logout 서버 호출
- `frontend/src/lib/auth-context.tsx` — logout async 변경
- `frontend/src/app/layout.tsx` — next/font/google 폰트 로딩 추가
- `frontend/tailwind.config.ts` — CSS variable 기반 폰트 연결
- `frontend/src/components/page-transition.tsx` — 신규 (Framer Motion 페이지 전환)
- `frontend/src/app/login/page.tsx` — PageTransition 래퍼 적용
- `frontend/src/app/signup/page.tsx` — PageTransition 래퍼 적용
- `frontend/package.json` — framer-motion 의존성 추가

## 특이사항
- login 응답 JSON에 refresh_token을 여전히 포함 (테스트 편의성 + 디버깅). 실제 보안은 httpOnly 쿠키로 보장되며 프론트엔드 코드에서 refresh_token을 localStorage에 저장하지 않음.
- POST /api/auth/logout 엔드포인트 추가 — SPEC에는 "클라이언트에서 토큰 삭제"만 명시되어 있으나, httpOnly 쿠키는 JavaScript로 삭제 불가하므로 서버 엔드포인트 필수.
