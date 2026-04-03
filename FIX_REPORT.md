# 통합 수정 리포트 — 라운드 3

## 수정 일시
2026-04-04 (금)

## 수정 내역

### 치명 문제 수정

#### 문제 1: `generate_dummy_story()`가 판형 최소 페이지 수보다 적은 페이지를 생성
- **원인**: `generate.py:97`에서 `total_pages = page_count // 2`로 계산하여 `page_count=24`일 때 12페이지만 생성. 그러나 Book Print API의 `insert_content()`는 1회 호출 = 1페이지로 카운트하므로, SQUAREBOOK_HC(최소 24페이지)에 12페이지만 삽입되어 `execute_order_workflow()`에서 "페이지 수 부족" 에러 발생.
- **수정 파일**: `backend/app/services/generate.py:95-97`
- **수정 내용**: `total_pages = page_count // 2` → `total_pages = page_count`. 이로써 `page_count=24`일 때 title(1) + content(22) + ending(1) = 24페이지가 생성되어 SQUAREBOOK_HC 최소 요구 사항 충족.
- **테스트 수정**: `backend/tests/test_generate.py`
  - `test_generate_creates_correct_pages`: `assert len(data["pages"]) == 12` → `== 24`
  - `test_get_pages_after_generate`: `assert len(pages) == 12` → `== 24`
- **검증**: pytest tests/test_generate.py — 28개 전체 통과, pytest tests/test_orders.py — 52개 전체 통과

### 경미 문제 수정

#### 문제 2: 랜딩 페이지 하단 "샘플 동화책 미리보기" 영역에 실제 콘텐츠 부재
- **원인**: 카드 높이 축소 후에도 이미지 없이 빈 그래디언트 배경만 표시되어 시각적 밀도 부족
- **수정 파일**: `frontend/src/app/page.tsx:228-257`
- **수정 내용**:
  - 카드에 책 형태 3D 효과 추가 (perspective, 페이지 레이어 그림자)
  - 표지 영역 높이 확대 (h-40→h-52) + 장식 원형 요소 3개 + 책등 라인 추가로 시각적 밀도 향상
  - 이모지 크기 확대 (text-6xl→text-7xl) + drop-shadow
  - 하단에 "AI 동화책" 태그 배지 + "미리보기" 링크 텍스트 추가
  - 전체적으로 빈 느낌을 해소하고 책 오브젝트로서의 완성도 향상
- **검증**: 빌드 에러 없음 (기존 컴포넌트/아이콘만 사용)

## 테스트 결과
- 관련 테스트: test_generate.py 28개 통과 / 0개 실패
- 관련 테스트: test_orders.py 52개 통과 / 0개 실패
- 관련 테스트: test_edit_pages.py 18개 통과 / 0개 실패
- 기존 실패 (수정 전부터 존재, 본 수정과 무관): test_audiobook.py 4개, test_auth.py 3개, test_books.py 1개 — DB 초기화/인증 관련 기존 이슈

## Tester에게 전달
위 수정 사항을 반영한 후 Integration Tester의 재검증을 요청합니다.

재검증 범위:
1. **`POST /api/books/:id/generate`** — 24페이지 생성 확인 (page_count=24 설정 시)
2. **`POST /api/books/:id/order`** — 주문 성공 확인 (502 에러 해소)
3. **전체 주문 워크플로우** — 내부 API 경유로 표지→내지 24p→최종화→견적→주문 성공
4. **랜딩 페이지 스크린샷** — 샘플 동화책 섹션의 시각적 밀도 개선 확인
