# QA 리포트 — 태스크 6: 동화책 만들기 위자드 — 정보 입력 + 직업 선택 (R1)

## 전체 판정: PASS
## 가중 점수: 7.6 / 10.0

## 항목별 점수
- 기능 완성도 (30%): 8/10 — 9개 완료 기준 모두 구현됨. 생년월일 서버 유효성 검사 누락(미래 날짜 허용), photo_id 클리어 불가 등 엣지 케이스 미비
- 코드 품질 (25%): 8/10 — 깔끔한 서비스 레이어 분리, 적절한 에러 처리, 보안 이슈 없음. 테스트에 일부 빠진 케이스 존재
- API 연동 (20%): 6/10 — 이 태스크는 Book Print API 연동 범위가 아님. 내부 API 4개 정상 구현. API 연동 항목 해당 사항 적음
- 디자인 품질 (25%): 8/10 — 파스텔 톤 일관성, Framer Motion 전환 애니메이션, 반응형 그리드, 진행 바 UI 양호. 아코디언 직업 선택 UI 잘 구성됨

**가중 계산**: (8×0.3) + (8×0.25) + (6×0.2) + (8×0.25) = 2.4 + 2.0 + 1.2 + 2.0 = **7.6**

## SPEC 완료 기준 대조
- [PASS] 완료 기준 1 (이용권 확인): `/create` 페이지 진입 시 `apiClient.getVouchers()` 호출 → 사용 가능 이용권 없으면 `/vouchers`로 리다이렉트. `create/page.tsx` 85~93행
- [PASS] 완료 기준 2 (이용권 구매 목업): `/vouchers` 페이지에서 2종(9,900원/29,900원) 카드 UI, 구매 버튼 클릭 시 `POST /api/vouchers/purchase` 호출 → 즉시 `purchased` 상태. 구매 후 `/create?voucher_id=` 이동
- [PASS] 완료 기준 3 (위자드 레이아웃): `wizard-progress.tsx`에 9단계 진행 바 구현 (완료/현재/미래 시각 구분, 애니메이션). 뒤로가기/다음 버튼 하단 고정 배치
- [PASS] 완료 기준 4 (정보 입력 단계): 이름 입력(필수, maxLength 20), 생년월일 date input(max=today), 사진 그리드(기존 선택/새 업로드), 유효성 에러 표시
- [PASS] 완료 기준 5 (직업 선택 단계): 5개 카테고리 아코디언 UI, 카테고리별 직업 카드(이모지 아이콘+이름), "어떤 직업이 좋을지 모르겠어요" disabled + "준비 중" 배지(Lock 아이콘)
- [PASS] 완료 기준 6 (백엔드 API 4개): `POST /api/books`(draft 생성+이용권 연결), `PATCH /api/books/:id`(정보/직업 저장), `POST /api/vouchers/purchase`(목업), `GET /api/vouchers`(목록) — 모두 인증/소유권 검증 포함
- [PASS] 완료 기준 7 (저장 정책): "다음" 버튼 클릭 시 `apiClient.updateBook()` 호출로 서버 저장 + `current_step` 증가. `create/page.tsx` 117~184행
- [PASS] 완료 기준 8 (beforeunload): `create/page.tsx` 41~48행에서 `beforeunload` 이벤트 등록 + cleanup
- [PASS] 완료 기준 9 (디자인+반응형): 파스텔 톤 색상, 둥근 모서리(rounded-2xl/3xl), Framer Motion 애니메이션, 반응형 그리드(grid-cols-2 sm:grid-cols-3 등)

## 테스트 검증
- Developer 테스트 수: 24개 (voucher 7개 + books 17개)
- 전체 테스트: 83개 통과, 0개 실패
- 빠진 테스트 케이스:
  1. `DELETE /api/books/:id` — 비draft 상태(예: completed) 삭제 거부 테스트 없음
  2. `DELETE /api/books/:id` — 다른 사용자의 책 삭제 시도 403 테스트 없음
  3. `GET /api/books` — 인증 없이 접근 시 401/403 테스트 없음
  4. `PATCH /api/books/:id` — 존재하지 않는 photo_id 전달 시 404 테스트 없음
  5. 이용권 목록 격리 — 사용자A 이용권이 사용자B에게 보이지 않는지 테스트 없음
  6. `child_birth_date` — 미래 날짜 서버 검증 테스트 없음 (서버 검증 자체가 누락)

## 구체적 개선 지시 (다음 태스크에서 참고)
1. **`backend/app/schemas/book.py` `BookUpdateRequest`**: `child_birth_date`에 대한 서버 사이드 유효성 검사 추가 필요 — 미래 날짜를 거부하는 `field_validator` 추가. 현재 프론트엔드 `max` 속성에만 의존하고 있어 API 직접 호출 시 미래 날짜 저장 가능.
2. **`backend/tests/test_books.py`**: 위 "빠진 테스트 케이스" 6개 항목 추가 권장. 특히 비draft 삭제 거부, 다른 사용자 삭제 403, 인증 없는 목록 조회는 보안 관련이므로 중요.
3. **`backend/app/services/book.py` `update_book` 함수 36~39행**: `if value is not None` 조건 때문에 명시적으로 `photo_id=null`을 보내도 사진 선택 해제가 불가능. `exclude_unset=True`와 `None` 체크를 분리하여, unset된 필드만 제외하고 `None`은 허용하도록 수정 필요. (현 태스크 범위에선 문제없으나 향후 편집 기능에서 문제될 수 있음)

## 비고
- 태스크 6은 Book Print API 연동 범위가 아니므로 API 연동 항목은 내부 REST API 구현 품질 기준으로 채점
- 기존 59개 테스트 전부 통과 — 기존 기능 퇴보 없음
- 프론트엔드 빌드 성공 확인 (10개 라우트 생성)
