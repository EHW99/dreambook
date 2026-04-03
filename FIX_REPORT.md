# 통합 수정 리포트 - 라운드 2

## 수정 일시
2026-04-04 (금)

## 수정 내역

### 치명 문제 수정

#### 문제 1: `parameters.definitions` 미언래핑 — 템플릿 파라미터 매핑 전면 실패

- **원인**: Book Print API `GET /templates/{uid}` 응답의 파라미터 정의가 `data.parameters.definitions` 안에 중첩되어 있는데, `get_template_detail()` 메서드가 `data` 만 반환하여 사용처(4곳)에서 `detail.get("parameters", {})` → `{"definitions": {...}}` 를 파라미터 dict로 착각.
- **수정 파일**: `backend/app/services/bookprint.py:257-267` (`get_template_detail()`)
- **수정 내용**: `get_template_detail()` 메서드에서 `parameters.definitions` 를 `parameters`로 끌어올림 (언래핑). `definitions` 키가 존재하면 교체, 없으면 기존 동작 유지 (하위 호환).
  ```python
  params = data.get("parameters", {})
  if isinstance(params, dict) and "definitions" in params:
      data["parameters"] = params["definitions"]
  ```
- **영향 범위**: 이 한 곳 수정으로 4개 사용처(`_select_best_template`, `_select_best_content_template`, `_build_cover_parameters`, `_build_content_parameters`) 모두 자동 해결.
- **추가 테스트**: `tests/test_bookprint_fixes.py::TestParametersDefinitionsUnwrap` (5개 케이스)
  - `test_unwraps_definitions_layer`: definitions 중첩 해제 확인
  - `test_unwrap_preserves_empty_definitions`: 빈 definitions 처리
  - `test_unwrap_handles_no_definitions_key`: definitions 키 없는 경우 하위 호환
  - `test_select_best_template_after_unwrap`: 언래핑 후 올바른 param_count 계산
  - `test_build_cover_params_after_unwrap`: 언래핑 후 frontPhoto/dateRange/spineTitle 매핑 확인
- **검증**: pytest 통과

### 중요 문제 수정

#### 문제 2: `regenerate-image` 엔드포인트에서 가상 경로 사용

- **원인**: `books.py`의 `regenerate_image()` 엔드포인트가 `/placeholder/illustration_{page_number}_v{index}.png` 가상 경로를 사용. 이미지 재생성 후 주문 시 해당 파일이 존재하지 않아 Book Print API 업로드 실패 가능.
- **수정 파일**: `backend/app/api/books.py:324-332`
- **수정 내용**: 가상 경로 대신 `generate.py`의 `_create_placeholder_image()` 를 호출하여 실제 PNG 파일을 생성.
  ```python
  from app.services.generate import _create_placeholder_image
  image_path = _create_placeholder_image(page.page_number, f"Regen v{new_index}", book.id)
  ```
- **추가 테스트**: 기존 `TestPlaceholderImageGeneration` 테스트가 커버 (2개 케이스)
- **검증**: pytest 통과

### 경미 문제 수정

#### 문제 3: 랜딩 페이지 하단 콘텐츠 영역 시각적으로 빈 느낌

- **원인**: 샘플 동화책 카드와 그림체 카드의 placeholder 영역이 너무 커서 빈 공간이 많은 면적을 차지.
- **수정 파일**: `frontend/src/app/page.tsx`
- **수정 내용**:
  - 샘플 동화책 카드 높이: `h-48 sm:h-56` → `h-40 sm:h-44` (20% 축소)
  - 그림체 카드 비율: `aspect-square` → `aspect-[4/3]` (정사각형 → 4:3 비율로 높이 축소)
- **검증**: 프론트엔드 시각적 확인 필요

#### 문제 4: 인증 보호 페이지 "로딩 중..." 텍스트만 표시

- **원인**: `auth-guard.tsx`의 로딩 상태에서 텍스트만 표시, 스피너/스켈레톤 UI 없음.
- **수정 파일**: `frontend/src/components/auth-guard.tsx:17-23`
- **수정 내용**: "로딩 중..." 텍스트를 CSS 스피너 + 안내 텍스트 조합으로 교체.
  - `border-4 border-primary/30 border-t-primary rounded-full animate-spin` 스피너
  - "잠시만 기다려주세요..." 부드러운 안내 텍스트
- **검증**: 프론트엔드 시각적 확인 필요

## 테스트 결과

- 기존 테스트: 257개 통과 / 7개 실패 (기존 실패 — audiobook 테스트 인프라 + auth 테스트 인프라 문제, 이번 수정과 무관)
- 신규 테스트: 5개 추가 (`TestParametersDefinitionsUnwrap`)
- bookprint 수정 관련 테스트: **25개 전체 통과**
- 총: 264개 중 257개 통과 (기존 7개 실패 유지)

## Tester에게 전달

위 수정 사항을 반영한 후 Integration Tester의 재검증을 요청합니다.

재검증 범위:
1. **`parameters.definitions` 언래핑 확인**: `bookprint.py`의 `get_template_detail()` 수정 확인
2. **전체 주문 워크플로우 재실행**: 충전금 → 책 생성 → 사진 업로드 → 템플릿 선택(파라미터 올바르게 파싱 확인) → 표지(frontPhoto/dateRange/spineTitle 전달 확인) → 내지 24p → 최종화 → 견적 → 주문
3. **이미지 재생성 확인**: `POST /api/books/:id/pages/:id/regenerate-image` 호출 후 실제 파일 존재 여부
4. **UI 확인**: 랜딩 페이지 카드 높이 변경, auth guard 스피너 확인
5. **테스트 실행**: 기존 + 신규 테스트 전체 통과 확인
