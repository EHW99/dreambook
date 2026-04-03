# 셀프체크 -- 태스크 4: 아이 사진 관리 (R2)

## QA 피드백 반영 내역

### 1. [치명] Pillow가 requirements.txt에 없음 → 반영 완료
- `backend/requirements.txt`에 `Pillow>=10.0.0` 추가

### 2. [중] content_type 검증 우회 → 반영 완료
- `backend/app/api/photos.py` 53행: `if file.content_type and not ...` → `if not file.content_type or not ...` 로 변경
- content_type이 None이거나 허용 목록에 없으면 모두 거부

### 3. [낮] response_model 미사용 → 반영 완료
- `@router.post("", status_code=201, response_model=PhotoResponse)` 추가
- `@router.get("", response_model=list[PhotoResponse])` 추가

## 테스트 결과
- 전체 테스트 수: 59개 (기존 57개 + 신규 2개)
- 통과: 59개
- 실패: 0개

### 신규 테스트
1. `test_upload_invalid_content_type` — 잘못된 content_type(application/octet-stream)이면 422 반환 확인
2. `test_content_type_none_rejected` — validate_content_type 함수의 허용/거부 동작 직접 검증

## SPEC 기능 체크

### 백엔드 API
- [x] `POST /api/photos` -- 파일 업로드 (multipart/form-data): 구현 완료
- [x] 형식 검증: JPG, PNG, WebP만 허용 (확장자 + Content-Type 이중 검증, None 차단)
- [x] 크기 검증: 10MB 이하
- [x] 해상도 검증: 512x512 이상 (Pillow로 실제 이미지 파싱)
- [x] 개수 검증: 사용자당 최대 20장
- [x] 서버 로컬 저장 (uploads/ 디렉토리, UUID 파일명)
- [x] `GET /api/photos` -- 내 사진 목록 (id, thumbnail_url, original_name, created_at)
- [x] `DELETE /api/photos/:id` -- 사진 삭제 (DB + 파일 즉시 삭제)
- [x] 본인 사진만 삭제 가능 (403)
- [x] response_model 지정 (PhotoResponse, list[PhotoResponse])

### 에러 메시지
- [x] "지원하지 않는 파일 형식입니다" (422)
- [x] "파일 크기가 10MB를 초과합니다" (422)
- [x] "최대 20장까지 등록 가능합니다" (422)
- [x] "최소 512x512 이상의 이미지를 업로드해주세요" (422)

### 프론트엔드
- [x] 사진 목록 그리드 (썸네일 + 파일명 + 날짜)
- [x] 업로드 버튼 + 드래그앤드롭 지원
- [x] 삭제 버튼 (hover 시 표시) + 확인 다이얼로그
- [x] 빈 상태: "등록된 사진이 없어요" + 업로드 안내

### 기타
- [x] 정적 파일 서빙 (FastAPI StaticFiles로 /uploads 경로 마운트)
- [x] 반응형 (grid-cols-2 sm:grid-cols-3 md:grid-cols-4)
- [x] Pillow가 requirements.txt에 등록됨
- [x] 기존 테스트 전부 통과 (59/59)

## 특이사항
- TestClient에서 `content_type=None` 전달 시 httpx가 확장자 기반으로 자동 추론하므로 API 레벨에서 None 테스트가 불가. 대신 서비스 함수 직접 테스트 + 잘못된 content_type 전달 테스트로 커버
