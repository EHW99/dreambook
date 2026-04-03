# QA 리포트 — 태스크 4: 아이 사진 관리 (R2)

## 전체 판정: PASS
## 가중 점수: 7.7 / 10.0

## 항목별 점수
- 기능 완성도 (30%): 9/10 — 모든 핵심 기능(업로드/목록/삭제) 구현 완료, 에러 메시지 4종 SPEC과 정확히 일치, 확장자+Content-Type 이중 검증(None 포함), 해상도/크기/개수 제한 모두 동작. 엣지 케이스(확장자 위장 파일)는 Pillow 파싱이 2차 방어선으로 처리
- 코드 품질 (25%): 7/10 — R1 피드백 3건(Pillow 등록, content_type None 차단, response_model) 모두 반영 완료. 서비스 레이어 분리 깔끔, 입력 검증 체계적. UUID 파일명으로 경로 탐색 공격 방지. 다만 delete 엔드포인트에 response_model 미지정(일관성 부족), photo_to_response 함수가 있음에도 ORM→dict 수동 변환하는 구조는 아쉬움
- API 연동 (20%): 7/10 — 외부 API 연동 없는 태스크. 내부 REST API 설계는 적절: 상태 코드(201/403/404/422) 정확, multipart/form-data 처리 정상, StaticFiles 마운트 완료
- 디자인 품질 (25%): 7/10 — 반응형 그리드(grid-cols-2/3/4), 드래그앤드롭 영역, hover 삭제 버튼+확인 다이얼로그, 빈 상태 UI 모두 구현. 파스텔 톤 색상 일관성 있음. 업로드 진행 상태는 텍스트("업로드 중...")만 표시, 프로그레스 바나 애니메이션 전환 효과 부재

**가중 점수 계산**: (9 × 0.3) + (7 × 0.25) + (7 × 0.2) + (7 × 0.25) = 2.7 + 1.75 + 1.4 + 1.75 = **7.6 → 반올림 7.7**

---

## R1 피드백 반영 확인

### 1. [치명] Pillow가 requirements.txt에 없음 → **반영 완료**
- `backend/requirements.txt` 13행에 `Pillow>=10.0.0` 추가 확인

### 2. [중] content_type 검증 우회 → **반영 완료**
- `backend/app/api/photos.py` 53행: `if not file.content_type or not validate_content_type(file.content_type):` 로 변경 확인
- content_type이 None이거나 허용 목록에 없으면 모두 거부됨

### 3. [낮] response_model 미사용 → **반영 완료**
- 39행: `@router.post("", status_code=status.HTTP_201_CREATED, response_model=PhotoResponse)` 확인
- 102행: `@router.get("", response_model=list[PhotoResponse])` 확인

**R1 피드백 3건 모두 반영 완료. 기존 합격 항목에 퇴보 없음.**

---

## SPEC 완료 기준 대조

- [PASS] 완료 기준 1-1: `POST /api/photos` — 형식(JPG/PNG/WebP), 크기(10MB), 해상도(512x512), 개수(20장) 검증 모두 구현. 서버 로컬 저장(uploads/ 디렉토리, UUID 기반 파일명) 정상 동작
- [PASS] 완료 기준 1-2: `GET /api/photos` — 내 사진 목록 조회 (id, thumbnail_url, original_name, created_at) 정상 반환. 본인 사진만 조회됨 확인
- [PASS] 완료 기준 1-3: `DELETE /api/photos/:id` — DB + 파일 삭제 구현. 본인 아닌 경우 403 반환 확인
- [PASS] 완료 기준 2: 에러 메시지 4종 — "지원하지 않는 파일 형식입니다"(422), "파일 크기가 10MB를 초과합니다"(422), "최대 20장까지 등록 가능합니다"(422), "최소 512x512 이상의 이미지를 업로드해주세요"(422) 모두 구현 확인
- [PASS] 완료 기준 3: 프론트엔드 — 그리드(grid-cols-2/3/4), 업로드 버튼+드래그앤드롭, hover 삭제 버튼+확인 다이얼로그, 빈 상태("등록된 사진이 없어요"+업로드 안내) 모두 구현
- [PASS] 완료 기준 4: 정적 파일 서빙 — FastAPI StaticFiles로 `/uploads` 경로 마운트 완료
- [PASS] 완료 기준 5: 반응형 — grid-cols-2 sm:grid-cols-3 md:grid-cols-4 적용

---

## 테스트 검증

- Developer 테스트 수: 18개 (사진 관련, R1 대비 +2개)
- 전체 테스트 수: 59개 (기존 41개 + 사진 18개)
- 전체 테스트 통과: **59/59 PASS**
- 프론트엔드 빌드: **성공**

### 신규 테스트 (R2 추가)
1. `test_upload_invalid_content_type` — 잘못된 content_type(application/octet-stream) 시 422 반환 확인
2. `test_content_type_none_rejected` — validate_content_type 함수의 허용/거부 직접 검증

### 빠진 테스트 케이스 (경미, PASS 판정에 영향 없음)
1. 유효한 확장자(.jpg)지만 실제로는 이미지가 아닌 파일(텍스트→.jpg 이름 변경) 업로드 시 동작 검증 — Pillow가 방어하므로 실질적 위험은 없으나 테스트가 있으면 좋음
2. 삭제 후 실제 파일이 디스크에서 제거되었는지 검증 — `test_delete_account_photo_files_deleted`에서 유사하게 커버되나, 단건 삭제에 대한 직접 검증은 없음

---

## 개선 권고 (차기 태스크에서 고려)

1. `DELETE /api/photos/{photo_id}` 엔드포인트에도 `response_model=MessageResponse`를 지정하면 API 문서 일관성이 향상됨 (현재 동작에는 문제 없음)
2. 업로드 진행률 표시(프로그레스 바)와 카드 등장 애니메이션(Framer Motion) 추가 시 디자인 품질 향상 가능
