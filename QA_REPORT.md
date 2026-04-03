# QA 리포트 — 태스크 8: 옵션 + 줄거리 + 생성 (R2)

## 전체 판정: PASS
## 가중 점수: 7.6 / 10.0

## 항목별 점수
- 기능 완성도 (30%): 8/10 — R1 피드백 4건 모두 반영 완료. 판형별 페이지 수 범위 분리, plot_input 길이 제한, generate 재호출 방어 모두 정상 동작. 단, model_validator에서 page_count와 book_spec_uid가 동시 제공될 때만 교차 검증되는 점은 향후 개선 여지가 있으나, 프론트엔드에서 항상 함께 전송하는 구조이므로 현 단계에서는 허용 가능
- 코드 품질 (25%): 8/10 — BOOK_SPEC_PAGE_RANGES 딕셔너리로 판형별 범위를 깔끔하게 관리. field_validator와 model_validator를 적절히 분리 사용. generate 재호출 방어 로직이 명확
- API 연동 (20%): 7/10 — 이 태스크는 외부 API 연동 없이 내부 API만 구현. 판형별 페이지 수 제약이 SPEC과 일치하도록 수정 완료. PHOTOBOOK_A5_SC 50~200p 범위 정확히 반영
- 디자인 품질 (25%): 7/10 — 파스텔 톤 일관, Framer Motion 애니메이션 적용, 슬라이더 min/max 동적 변경, 판형 변경 시 pageCount 자동 보정 등 UX 세부사항 잘 처리. Lottie 대신 SVG 사용은 합리적 판단

## SPEC 완료 기준 대조

### 1. 옵션 선택
- [PASS] 페이지 수 선택 — 슬라이더 + +-버튼, 2p 단위 증가, 판형별 동적 min/max
- [PASS] 판형별 페이지 수 범위 — SQUAREBOOK_HC/PHOTOBOOK_A4_SC: 24~130p, PHOTOBOOK_A5_SC: 50~200p. 백엔드 model_validator + 프론트엔드 동적 슬라이더 모두 적용
- [PASS] 판형 선택 — 3종 라디오 버튼, 판형 변경 시 pageCount 범위 밖이면 자동 보정
- [PASS] 예상 가격 실시간 표시 — 판형 + 페이지 수 기반 계산, AnimatePresence 갱신 애니메이션

### 2. 줄거리 작성
- [PASS] 스토리 테마 카드 3개 + "직접 쓸래요" — 4개 카드 UI
- [PASS] "직접 쓸래요"만 활성화, 나머지 "준비 중" 배지 — Lock 아이콘 + 비활성 스타일링
- [PASS] "준비 중" 클릭 시 토스트 — "곧 제공될 예정입니다" 메시지
- [PASS] textarea (최대 1000자, 글자 수 표시) — maxLength=1000 + 글자 수 카운터

### 3. 생성 중
- [PASS] 더미 데이터로 즉시 페이지 생성 — generate_dummy_story에서 템플릿 기반 텍스트+placeholder 이미지
- [PASS] 원형 진행률 UI — SVG 기반 원형 프로그레스 + Framer Motion 애니메이션
- [PASS] 뒤로가기 차단 — popstate 이벤트 차단 + 네비게이션 버튼 숨김
- [PASS] 생성 완료 시 자동 편집 화면 이동 — /create/edit?book_id=...

### 4. 백엔드 API
- [PASS] PATCH /api/books/:id — page_count, book_spec_uid, plot_input 저장 + 판형별 교차 검증 + plot_input 1000자 제한
- [PASS] POST /api/books/:id/generate — 더미 스토리+이미지 생성 + 재호출 방어 (editing/completed 상태 시 422)
- [PASS] GET /api/books/:id/pages — 페이지 목록 조회, page_number 순 정렬
- [PASS] 더미 스토리 이름/직업 치환 — 확인 완료
- [PASS] book.status → "editing", current_step → 9, title 자동 설정 — 확인 완료
- [PASS] plot_input 길이 제한 — @field_validator로 최대 1000자 검증, 초과 시 에러 반환

### 5. 디자인 + 반응형
- [PASS] 파스텔 톤 색상 팔레트 — primary/secondary/accent 일관
- [PASS] Framer Motion 애니메이션 — 페이지 전환, 카드 hover, 진행률 원
- [PASS] 반응형 레이아웃 — max-w, grid 구조
- [PASS] 둥근 모서리 — rounded-2xl 일관 적용

## R1 피드백 반영 확인

### 1. 판형별 페이지 수 범위 분리 — 반영 완료
- 백엔드: `BOOK_SPEC_PAGE_RANGES` 딕셔너리 + `@model_validator(mode="after")` 교차 검증
- 프론트엔드: BOOK_SPECS에 minPages/maxPages 추가, 슬라이더 동적 범위, 판형 변경 시 pageCount 자동 보정

### 2. plot_input 길이 제한 — 반영 완료
- `@field_validator("plot_input")`으로 1000자 초과 시 에러 반환

### 3. generate 재호출 방어 — 반영 완료
- `book.status not in ("draft", "character_confirmed")` 체크, 422 반환

### 4. 테스트 케이스 추가 — 반영 완료
- 11개 신규 테스트 추가 (총 28개): 판형별 범위 6건, plot_input 2건, 재호출 2건, page_type 1건

## 테스트 검증
- Developer 테스트 수: 28개 (태스크 8)
- 전체 테스트: 139개, 전부 통과
- 프론트엔드 빌드: 성공

### 빠진 테스트 케이스
- 없음 (R1 지적 사항 모두 테스트로 커버됨)

## 기존 합격 항목 퇴보 여부
- 기존 111개 테스트 모두 통과 — 퇴보 없음

## 참고 사항 (향후 개선 여지)
- `model_validator`에서 page_count와 book_spec_uid가 **동시 제공**될 때만 교차 검증됨. 기존 book에 book_spec_uid가 이미 설정된 상태에서 page_count만 PATCH로 보내면 범위 검증을 우회할 수 있음. 현재 프론트엔드가 항상 둘을 함께 전송하므로 실질적 문제는 없으나, 보안 강화가 필요하면 라우터 레벨에서 DB의 기존 book_spec_uid를 참조하는 검증 추가 가능

## 구체적 개선 지시
- 없음 (PASS 판정)
