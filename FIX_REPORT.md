# 통합 수정 리포트

## 수정 일시
2026-04-04 (금)

## 수정 내역

### 치명 문제 수정

#### 문제 1: 내지 템플릿 파라미터 불일치 — 주문 워크플로우 전면 실패
- **원인**: `execute_order_workflow`에서 내지 삽입 시 `{"text": ..., "photo": ...}` 고정 파라미터를 사용했지만, Book Print API의 content 템플릿은 `text`/`photo` 파라미터를 받지 않음. 실제 필수 파라미터는 `year`, `month`, `date`, `diaryText`, `photo1` 등 템플릿별로 다름.
- **수정 파일**: `backend/app/services/bookprint.py`
- **수정 내용**:
  - `_select_best_content_template()` 메서드 추가: 템플릿 상세 조회 후 빈 템플릿(파라미터 없음) > photo+text 단순 템플릿 > 파라미터 최소 템플릿 순으로 우선 선택
  - `_build_content_parameters()` 정적 메서드 추가: 템플릿 파라미터 정의의 binding 유형(text/file/rowGallery)에 따라 동적으로 값을 매핑
  - 기존 `{"text": ..., "photo": ...}` 하드코딩 제거
- **추가 테스트**: `test_bookprint_fixes.py::TestBuildContentParameters` (5개), `TestTemplateSelection::test_select_empty_content_template`
- **검증**: pytest 259개 전체 통과

#### 문제 2: 표지 템플릿 필수 파라미터 누락
- **원인**: 표지 생성 시 `{"title": title}` + `frontPhoto`만 전달했지만, cover 템플릿은 `frontPhoto`(file/필수), `dateRange`(text/필수), `spineTitle`(text/필수) 모두 필요
- **수정 파일**: `backend/app/services/bookprint.py`
- **수정 내용**:
  - `_build_cover_parameters()` 정적 메서드 추가: 템플릿 파라미터 정의를 순회하며 binding 유형별로 적절한 값 매핑
    - file 타입 → 업로드된 이미지 파일명
    - title/booktitle → 책 제목
    - spine → 제목(20자 이내)
    - date/range → 현재 날짜
  - `execute_order_workflow`에서 `_select_best_template()`으로 표지 템플릿 선택 후, `_build_cover_parameters()`로 필수 파라미터 전체 생성
- **추가 테스트**: `test_bookprint_fixes.py::TestBuildCoverParameters` (3개)
- **검증**: pytest 전체 통과

#### 문제 3: 더미 이미지 경로가 실제 파일이 아님 — 사진 업로드 실패
- **원인**: Phase 2 더미 이미지 경로(`/placeholder/illustration_*.png`)는 파일 시스템에 존재하지 않는 가상 경로. `os.path.exists()` 체크에서 False → 업로드 건너뜀 → Book Print API 에러
- **수정 파일**: `backend/app/services/generate.py`, `backend/app/api/orders.py`
- **수정 내용**:
  - `_create_placeholder_image()` 함수 추가: PIL을 사용하여 실제 800x800 PNG 파일을 `uploads/` 디렉토리에 생성. 파스텔 색상 배경 + 페이지 번호/라벨 텍스트 표시
  - `generate_dummy_story()`에서 기존 `DUMMY_IMAGE_PATH.format()` 가상 경로 대신 `_create_placeholder_image()` 호출로 실제 파일 생성
  - `_get_pages_data()` (orders.py): 절대 경로 이미지를 올바르게 인식하도록 `os.path.isabs()` + `os.path.exists()` 검사 추가
- **추가 테스트**: `test_bookprint_fixes.py::TestPlaceholderImageGeneration` (2개)
- **검증**: pytest 전체 통과

### 중요 문제 수정

#### 문제 4: 템플릿 선택 로직 부재 — 첫 번째 템플릿 무조건 사용
- **원인**: `cover_templates[0]`, `content_templates[0]`로 무조건 첫 번째 템플릿 선택. 해당 템플릿이 동화책 서비스에 적합하지 않을 수 있음
- **수정 파일**: `backend/app/services/bookprint.py`
- **수정 내용**:
  - `get_template_detail()` 메서드 추가: `GET /templates/{templateUid}` API 호출로 파라미터 정의 조회
  - `_select_best_template()` 메서드 추가: 최대 5개 템플릿의 상세를 조회하여 파라미터가 가장 적은 것을 선택
  - `_select_best_content_template()` 메서드 추가: 빈 템플릿 > photo+text > 파라미터 최소 순으로 스코어링하여 최적 선택
  - API 조회 실패 시 첫 번째 템플릿으로 폴백
- **추가 테스트**: `test_bookprint_fixes.py::TestTemplateSelection` (3개)
- **검증**: pytest 전체 통과

#### 문제 5: 사진 업로드 MIME type 하드코딩
- **원인**: `upload_photo()`에서 `"image/png"` 하드코딩. JPEG 파일도 PNG로 전송됨
- **수정 파일**: `backend/app/services/bookprint.py`
- **수정 내용**:
  - `detect_mime_type()` 함수 추가: magic bytes 기반 감지 (PNG/JPEG/WebP/GIF/BMP) → 확장자 폴백 → 기본값 `image/png`
  - `upload_photo()`에서 `detect_mime_type(file_path)` 호출로 실제 MIME type 전송
- **추가 테스트**: `test_bookprint_fixes.py::TestDetectMimeType` (6개)
- **검증**: pytest 전체 통과

### 경미 문제 수정

#### 문제 6: 랜딩 페이지 하단 빈 섹션
- **원인**: "샘플 동화책 미리보기" 및 "스타일 갤러리" 섹션의 이미지 placeholder 영역이 아이콘/이모지만 있어 시각적으로 비어 보임
- **수정 파일**: `frontend/src/app/page.tsx`
- **수정 내용**:
  - 샘플 동화책 카드: 이모지 하단에 제목 + "AI가 만든 샘플 미리보기" 텍스트 추가
  - 그림체 카드: Palette 아이콘 하단에 "{스타일명} 스타일" 라벨 추가
  - 빈 공간을 설명 텍스트로 채워 placeholder 의도를 명확히 함
- **추가 테스트**: 프론트엔드 UI — 브라우저 재검증 필요
- **검증**: 빌드 타임 에러 없음

#### 문제 7: 콘솔 에러 1건 — 리소스 404
- **현상**: 브라우저 콘솔에서 `Failed to load resource: 404` 에러 1건
- **조사 결과**: 정확한 리소스 URL이 리포트에 기재되지 않음. favicon.ico는 `src/app/favicon.ico`에 정상 존재. 브라우저 자동 요청(`apple-touch-icon-precomposed.png` 등)으로 추정됨.
- **조치**: 추가 정보 필요. 재검증 시 정확한 404 URL 확인 요청.

#### 문제 8: 페이지 수 사전 검증 위치
- **원인**: 최종화 전 페이지 수 검증이 `len(pages_data)` 기준이지만, 내지 삽입 실패 시 실제 삽입 수와 다를 수 있음
- **수정 파일**: `backend/app/services/bookprint.py`
- **수정 내용**:
  - `total_pages = len(pages_data)` → `inserted_count` (실제 삽입 성공 카운터) 기준으로 변경
  - 내지 삽입 루프에서 `inserted_count` 증가, 검증 시 이 값 사용
- **추가 테스트**: `test_bookprint_fixes.py::TestPageCountValidation` (1개)
- **검증**: pytest 전체 통과

## 테스트 결과
- 기존 테스트: 239개 통과 / 0개 실패
- 신규 테스트: 20개 추가
- 총: **259개 통과 / 0개 실패**

## Tester에게 전달
위 수정 사항을 반영한 후 Integration Tester의 재검증을 요청합니다.

재검증 범위:
- **API 문서 vs 코드 대조**: `bookprint.py`의 `execute_order_workflow` 전면 재검증 (템플릿 선택/파라미터 매핑 로직)
- **주문 워크플로우 E2E**: `POST /api/books/:id/order` API 호출 → Book Print API 전체 워크플로우 재실행
- **사진 업로드**: 다양한 이미지 형식(PNG, JPEG)으로 업로드 MIME type 확인
- **더미 이미지**: `POST /api/books/:id/generate` 후 실제 파일 존재 여부 확인
- **랜딩 페이지 UI**: 브라우저에서 하단 섹션 시각적 확인
- **콘솔 에러**: 404 리소스 URL 특정
