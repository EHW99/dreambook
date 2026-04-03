# 셀프체크 — 태스크 5: 랜딩 페이지

## 테스트 결과
- 전체 테스트 수: 16개
- 통과: 16개
- 실패: 0개

## SPEC 기능 체크
- [x] 히어로 섹션: 서비스 핵심 메시지("아이의 꿈을 동화책으로 만들어주세요") + CTA 버튼("동화책 만들기") 구현 완료
- [x] 샘플 동화책 섹션: 3개 샘플 동화 카드 (소방관/우주비행사/요리사) 표시, 더미 데이터 사용
- [x] 그림체 샘플 섹션: 5가지 그림체(수채화/연필화/크레파스/3D/만화) 갤러리 구현 완료, placeholder 이미지 사용
- [x] 가격/이용권 섹션: AI 스토리북 9,900원 / AI 스토리북 + 실물 책 29,900원 카드 구현 완료
- [x] 접근 권한: 비로그인/로그인 모두 접근 가능 (useAuth로 조건부 렌더링)
- [x] CTA 버튼: 비로그인 → /login, 로그인 → /create 연결 완료
- [x] 헤더/네비게이션: 로고(꿈꾸는 나), 비로그인 시 로그인/회원가입, 로그인 시 마이페이지 버튼, 모바일 햄버거 메뉴
- [x] 푸터: 서비스명(꿈꾸는 나), 회사 정보((주)스위트북), 바로가기 링크
- [x] 디자인: 파스텔 톤 색상 팔레트 적용, Framer Motion 스크롤 기반 페이드인 애니메이션, 둥근 모서리, 부드러운 그림자
- [x] 반응형: 모바일/태블릿/데스크톱 대응 (grid 반응형, 모바일 메뉴)

## 구현 세부사항

### 파일 구조
- `frontend/src/app/page.tsx` — 랜딩 페이지 (히어로, 샘플 동화책, 그림체 갤러리, 만드는 과정, 가격, 최종 CTA)
- `frontend/src/components/layout/header.tsx` — 공통 헤더 (로고, 네비게이션, 모바일 메뉴)
- `frontend/src/components/layout/footer.tsx` — 공통 푸터 (서비스명, 회사정보, 바로가기)
- `frontend/src/app/__tests__/landing-page.test.tsx` — 테스트 (16개)

### 디자인 구현
- 색상: Primary #FFB5A7, Secondary #FCD5CE, Accent #A8DADC, Background #FFF8F0
- Framer Motion: `FadeInSection` 컴포넌트로 스크롤 기반 페이드인 + 위로 올라오는 애니메이션
- Lucide Icons 사용 (BookOpen, Sparkles, Palette, Printer, Star, Check 등)
- 모서리 둥글게 (rounded-2xl, rounded-3xl)
- 부드러운 그림자 (shadow-soft, shadow-card, shadow-hover)
- 히어로 섹션 배경 장식 (blur 처리된 원형 그라데이션)

### 반응형
- 헤더: 데스크톱(md:) 네비게이션 + 모바일 햄버거 메뉴
- 히어로: 텍스트 크기 반응형 (text-4xl → sm:text-5xl → lg:text-6xl)
- 샘플 동화책: 1열 → 2열 → 3열
- 그림체: 2열 → 3열 → 5열
- 가격: 1열 → 2열

### 테스트 인프라
- Jest + React Testing Library 설정 완료
- jest.config.js, jest.setup.ts, tsconfig.jest.json 추가
- framer-motion, next/link, lucide-react 모킹 설정

## 특이사항
- 샘플 동화책 카드는 Phase 2에서 더미 데이터 사용 (실제 책 뷰어 연결은 해당 태스크에서)
- 그림체 샘플은 placeholder(Palette 아이콘 + 그라데이션 배경)로 대체 (실제 AI 이미지는 Phase 3)
- Header/Footer는 랜딩 페이지에 직접 포함 (다른 페이지에서도 재사용 가능한 독립 컴포넌트로 분리)
- "만드는 과정" 섹션을 추가하여 서비스 이해도 향상 (SPEC에는 명시 안 됨, UX 개선)
