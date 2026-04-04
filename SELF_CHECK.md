# 셀프체크 -- 태스크 16: AI 캐릭터 시트 생성 (GPT Image) — R2

## 테스트 결과
- 전체 테스트 수: 21개 (test_ai_character.py) + 28개 (test_characters.py) = 49개
- 통과: 49개
- 실패: 0개

## R2 피드백 반영 사항

### 1. [MUST] 프론트엔드 캐릭터 이미지 실제 렌더링
- `step-character-preview.tsx`에서 `char.image_path`가 존재하고 더미가 아닌 경우 `<img>` 태그로 실제 이미지 표시
- `API_BASE + image_path` 형태로 백엔드 /uploads/ 정적 파일 접근
- 이미지 로딩 실패 시 기존 User 아이콘 placeholder로 폴백

### 2. [MUST] 콘텐�� 정책 위반 에러 전달
- `character.py`의 `_generate_ai_character()`에서 `CharacterGenerationError`를 별도 catch하여 상위로 전파 (re-raise)
- `except Exception`에서만 더미 폴백 (일반 오류)
- `api/characters.py`에서 `CharacterGenerationError`를 catch하여 HTTP 400으로 사용자에게 에러 메시지 전달
- 테스트 추가: `test_content_policy_error_returns_400` — 콘텐츠 정책 위반 시 400 응답 확���

### 3. [SHOULD] output_format="png" 명시
- `ai_character.py`의 `images.edit` 호출에 `output_format="png"` 파라미터 추가
- 테스트 추가: `test_output_format_png_specified`

### 4. [SHOULD] 라우터 docstring 업데이트
- `api/characters.py` docstring을 "AI 생성, API 키 없으면 더미 폴백"으로 변경

### 5. AI 이미지 경로 형식 수정
- AI 생성 이미지의 `image_path`를 OS 절대 경로 대신 `/uploads/characters/filename.png` URL 형태로 저장
- 테스트 추가: `test_ai_image_path_is_url_format`

## SPEC 기능 체크
- [x] 1. `POST /api/books/:id/character`를 GPT Image images.edit으로 교체
- [x] 2. 입력: 아이 사진 + 그림체 + 직업 + 동화 스타일
- [x] 3. 출력: 1024x1024 PNG 캐릭터 시트
- [x] 4. 프롬프트: 그림체별 키워드 + 직업 복장 묘사
- [x] 5. 생성된 이미지 서버 저장 + DB 저장
- [x] 6. 재생성 횟수 체크 (최대 5회)
- [x] 7. 에러 처리: 콘텐츠 정책 위반 시 400 에러로 사용자 안내, 기타 오류는 더미 폴백

## 수정된 파일
- `backend/app/services/character.py`: CharacterGenerationError re-raise, 이미지 경로 URL 형식
- `backend/app/api/characters.py`: CharacterGenerationError → HTTP 400 처리, docstring 업데이트
- `backend/app/services/ai_character.py`: output_format="png" 추가
- `frontend/src/components/create/step-character-preview.tsx`: 실제 이미지 렌더링
- `backend/tests/test_ai_character.py`: 3개 테스트 추가 (content_policy_400, url_format, output_format)
