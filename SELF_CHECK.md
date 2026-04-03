# 셀프체크 — 태스크 6: 동화책 만들기 위자드 — 정보 입력 + 직업 선택

## 테스트 결과
- 전체 테스트 수: 83개 (기존 59개 + 신규 24개)
- 통과: 83개
- 실패: 0개
- 프론트엔드 빌드: 성공

## 신규 테스트 내역 (24개)
### test_vouchers.py (7개)
- 이용권 구매 (story_only): 201, 가격 9900 확인
- 이용권 구매 (story_and_print): 201, 가격 29900 확인
- 잘못된 이용권 타입: 422
- 인증 없이 구매: 401/403
- 빈 이용권 목록: 200, []
- 구매 후 목록: 200, 2건
- 인증 없이 목록: 401/403

### test_books.py (17개)
- 동화책 생성 (이용권 연결): 201, draft 상태
- 이용권 사용 처리 확인: used 상태 전환
- 이미 사용된 이용권: 400
- 존재하지 않는 이용권: 404
- 다른 사용자 이용권: 403
- 인증 없이 생성: 401/403
- 정보 입력 업데이트 (이름+생년월일): 200
- 직업 선택 업데이트: 200
- 이름 21자 초과: 422
- 이름 공백만: 422
- 존재하지 않는 책: 404
- 다른 사용자 책 수정: 403
- 동화책 상세 조회: 200
- 존재하지 않는 책 조회: 404
- 빈 목록: 200, []
- 생성 후 목록: 200, 1건
- draft 삭제: 200 + 삭제 확인

## SPEC 기능 체크
- [x] 이용권 확인: "새 동화책 만들기" 시 이용권 보유 확인 → 없으면 /vouchers로 이동
- [x] 이용권 구매 UI (목업): 2종(9,900원/29,900원) 선택 → 즉시 구매 완료
- [x] 위자드 레이아웃: 9단계 진행 표시 바, 뒤로가기/다음 버튼
- [x] 정보 입력 단계: 이름(필수, 최대 20자), 생년월일(필수), 사진 선택/업로드, 입력 검증+에러
- [x] 직업 선택 단계: 5개 카테고리 아코디언, 직업 카드(아이콘+직업명), "어떤 직업이 좋을지 모르겠어요" → "준비 중" 배지
- [x] 백엔드 POST /api/books: draft 생성, 이용권 연결
- [x] 백엔드 PATCH /api/books/:id: 정보 입력/직업 선택 저장
- [x] 백엔드 POST /api/vouchers/purchase: 목업 구매
- [x] 백엔드 GET /api/vouchers: 이용권 목록
- [x] 저장 정책: "다음" 버튼 시 서버 저장
- [x] beforeunload 이벤트 등록 (이탈 방지)
- [x] 디자인: 파스텔 톤, 둥근 모서리, Framer Motion 애니메이션
- [x] 반응형: 모바일/태블릿/데스크톱 대응

## 구현 파일 목록

### 백엔드
- `backend/app/schemas/voucher.py` — 이용권 스키마
- `backend/app/schemas/book.py` — 동화책 스키마
- `backend/app/services/voucher.py` — 이용권 서비스
- `backend/app/services/book.py` — 동화책 서비스
- `backend/app/api/vouchers.py` — 이용권 API 라우터
- `backend/app/api/books.py` — 동화책 API 라우터
- `backend/app/main.py` — 라우터 등록 추가
- `backend/tests/test_vouchers.py` — 이용권 테스트 (7개)
- `backend/tests/test_books.py` — 동화책 테스트 (17개)

### 프론트엔드
- `frontend/src/lib/api.ts` — API 클라이언트 확장 (vouchers, books)
- `frontend/src/lib/jobs-data.ts` — 직업 카테고리/목록 데이터
- `frontend/src/app/vouchers/page.tsx` — 이용권 구매 페이지
- `frontend/src/app/create/page.tsx` — 위자드 메인 페이지
- `frontend/src/components/create/wizard-progress.tsx` — 진행 표시 바
- `frontend/src/components/create/step-info-input.tsx` — 정보 입력 단계
- `frontend/src/components/create/step-job-select.tsx` — 직업 선택 단계

## 특이사항
- Book 모델의 child_name은 DB에서 NOT NULL이므로 생성 시 빈 문자열("")로 초기화
- 위자드 3단계 이후(동화 스타일, 그림체 등)는 태스크 7의 영역이므로 "준비 중" 메시지 표시
- 기존 테스트 59개 모두 통과 유지 (깨뜨린 것 없음)
