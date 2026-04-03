# 셀프체크 — 태스크 3: 마이페이지 — 회원 정보 + 탈퇴

## 테스트 결과
- 전체 테스트 수: 41개 (기존 31개 + 신규 10개)
- 통과: 41개
- 실패: 0개

## SPEC 기능 체크

### 백엔드 API
- [x] `PATCH /api/users/password` — 현재 비밀번호 확인 + 새 비밀번호 검증(8자 이상) + 변경
- [x] `DELETE /api/users/me` — 회원 탈퇴 (CASCADE: 사용자의 모든 데이터 즉시 삭제 — 사진 파일, DB 레코드)

### 에러 메시지
- [x] "현재 비밀번호가 틀렸습니다" (401)
- [x] "새 비밀번호는 8자 이상이어야 합니다" (422)

### 프론트엔드
- [x] 마이페이지 레이아웃 (탭 UI: 회원 정보 / 아이 사진 / 내 책장 / 주문 내역)
- [x] 회원 정보 탭: 이메일(비활성), 비밀번호 변경 폼
- [x] 회원 탈퇴: 확인 다이얼로그 ("정말 탈퇴하시겠습니까? 모든 데이터가 삭제됩니다")
- [x] 탈퇴 성공 → 토큰 삭제 → 랜딩 페이지 이동

### 디자인
- [x] 마이페이지 일관된 레이아웃 (파스텔 톤, 둥근 모서리, shadow-card)
- [x] 반응형 (모바일에서 탭 아이콘만 표시, 데스크톱에서 아이콘+레이블)

## 신규 파일
- `backend/app/api/users.py` — Users API 라우터
- `backend/app/schemas/user.py` — 사용자 관련 Pydantic 스키마
- `backend/app/services/user.py` — 비밀번호 변경, 회원 탈퇴 서비스
- `backend/tests/test_users.py` — 10개 테스트
- `frontend/src/app/mypage/page.tsx` — 마이페이지 (탭 UI)
- `frontend/src/components/mypage/profile-tab.tsx` — 회원 정보 탭
- `frontend/src/components/icons.tsx` — SVG 아이콘 컴포넌트

## 수정 파일
- `backend/app/main.py` — users 라우터 등록
- `frontend/src/lib/api.ts` — changePassword, deleteAccount 메서드 추가

## 특이사항
- 아이 사진 / 내 책장 / 주문 내역 탭은 "준비 중" 플레이스홀더로 구현 (태스크 4 이후에서 구현 예정)
- 비밀번호 변경 폼에 "새 비밀번호 확인" 필드 추가 (프론트엔드 UX 개선)
- 회원 탈퇴 시 사진 파일 삭제는 os.remove()로 처리, 실패해도 DB 삭제는 진행 (데이터 정합성 우선)
