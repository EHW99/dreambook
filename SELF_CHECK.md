# 셀프체크 — 태스크 14: 에러/빈 상태 페이지 + 디자인 통합 마무리

## 테스트 결과
- 전체 테스트 수: 28개 (기존 16개 + 신규 12개)
- 통과: 28개
- 실패: 0개

### 신규 테스트 파일
- `src/app/__tests__/not-found.test.tsx` (4개) — 404 페이지 렌더링, 메시지, 홈 링크, 아이콘
- `src/app/__tests__/error-page.test.tsx` (4개) — 500 에러 메시지, 다시 시도 버튼, reset 호출, 홈 링크
- `src/app/__tests__/empty-states.test.tsx` (4개) — 책장/사진/주문 빈 상태 메시지 확인

## SPEC 기능 체크

### 에러 페이지
- [x] 404 페이지: 따뜻한 일러스트 (BookOpen 아이콘 + 떠다니는 도형 애니메이션) + "길을 잃었나봐요" + 홈으로 돌아가기 버튼
- [x] 500 에러 페이지: AlertTriangle 일러스트 + "잠시 후 다시 시도해주세요" + 다시 시도 버튼 + 홈 버튼

### 빈 상태 UI
- [x] 내 책장: "아직 만든 동화책이 없어요" + BookOpen 아이콘 + 새 동화책 만들기 버튼 (기존 구현 확인)
- [x] 사진 목록: "등록된 사진이 없어요" + 드래그앤드롭 영역 + 업로드 안내 (기존 구현 확인)
- [x] 주문 내역: "아직 주문 내역이 없어요" + ShoppingBag 아이콘 (메시지 수정: "주문 내역이 없어요" → "아직 주문 내역이 없어요")

### 디자인 통합 점검
- [x] 색상 팔레트 일관 적용 확인: 모든 페이지가 tailwind.config.ts의 커스텀 색상(primary, secondary, accent, background, text 등) 사용
- [x] 타이포그래피 통일: Noto Sans KR (본문) + Gowun Batang (디스플레이) — layout.tsx에서 전역 설정
- [x] 모서리 둥글기 일관: rounded-2xl(16px) / rounded-3xl(20px) / rounded-full 일관 사용
- [x] Framer Motion 페이지 전환: login/signup/mypage는 PageTransition 래퍼 사용, 나머지 페이지는 framer-motion의 motion 컴포넌트 직접 사용하여 동일한 fade+slide 효과 적용
- [x] 로딩 상태 UI 통일: 스피너를 `w-10 h-10 border-3 border-primary border-t-transparent rounded-full animate-spin`으로 통일 (photos-tab의 w-8을 w-10으로 수정)
- [x] 반응형: 모든 페이지에 grid 및 flex 기반 반응형 레이아웃 적용 (sm/md/lg breakpoint 사용)

## 변경 파일 목록
1. **신규** `frontend/src/app/not-found.tsx` — 404 페이지
2. **신규** `frontend/src/app/error.tsx` — 500 에러 페이지
3. **수정** `frontend/src/components/mypage/orders-tab.tsx` — 빈 상태 메시지 "아직" 추가
4. **수정** `frontend/src/components/mypage/photos-tab.tsx` — 로딩 스피너 사이즈 통일 (w-8 → w-10)
5. **신규** `frontend/src/app/__tests__/not-found.test.tsx` — 404 테스트
6. **신규** `frontend/src/app/__tests__/error-page.test.tsx` — 에러 페이지 테스트
7. **신규** `frontend/src/app/__tests__/empty-states.test.tsx` — 빈 상태 테스트

## 특이사항
- PageTransition 래퍼가 login/signup/mypage에만 적용되어 있으나, 다른 페이지(create, vouchers, books 등)는 framer-motion의 motion 컴포넌트를 직접 사용하여 동일한 효과를 내고 있으므로 기능적으로 문제 없음. 기존 코드를 깨뜨리지 않기 위해 일괄 변경하지 않음.
- 에러/빈 상태 페이지 모두 프로젝트 디자인 시스템(파스텔 톤, 둥근 모서리, 부드러운 애니메이션)과 일관되게 구현
