# QA 리포트 — 태스크 16: AI 캐릭터 시트 생성 (GPT Image) (R2)

## 전체 판정: PASS
## 가중 점수: 8.1 / 10.0

## 항목별 점수
- 기능 완성도 (30%): 9/10 — R1 피드백 2건(이미지 렌더링, 콘텐츠 정책 에러 전달) 모두 반영 완료. 캐릭터 AI 생성, 더미 폴백, 재생성 횟수 제한, 콘텐츠 정책 에러 전달, 프론트엔드 이미지 렌더링 모두 동작.
- 코드 품질 (25%): 8/10 — CharacterGenerationError 예외 체인이 깔끔하게 분리됨(re-raise vs 더미 폴백). output_format="png" 명시. docstring 업데이트 완료. 이미지 경로가 URL 형태로 통일됨.
- API 연동 (20%): 7/10 — GPT Image images.edit 호출 구조 정확. model/size/quality/output_format 파라미터 모두 적절. 태스크 특성상 Book Print API 연동은 해당 없음.
- 디자인 품질 (25%): 8/10 — 갤러리 UI에서 실제 AI 이미지를 렌더링하며, onError 폴백으로 로딩 실패 시 placeholder 표시. 선택/확정 애니메이션 양호. 반응형 grid 적용.

**가중 점수**: (9 x 0.3) + (8 x 0.25) + (7 x 0.2) + (8 x 0.25) = 2.7 + 2.0 + 1.4 + 2.0 = **8.1**

## R1 피드백 반영 확인

### 피드백 1: [MUST] 프론트엔드 캐릭터 이미지 실제 렌더링 — 반영 완료
- `step-character-preview.tsx`에서 `char.image_path`가 존재하고 "dummy_"를 포함하지 않으면 `<img src={API_BASE + image_path}>` 태그로 실제 이미지 표시
- `onError` 핸들러로 이미지 로딩 실패 시 img 요소를 숨기고 User 아이콘 placeholder 폴백 표시
- AI 생성 이미지 경로가 `/uploads/characters/filename.png` URL 형태로 저장되어 프론트엔드에서 정상 접근 가능

### 피드백 2: [MUST] 콘텐츠 정책 위반 에러 전달 — 반영 완료
- `character.py`의 `_generate_ai_character()`에서 `CharacterGenerationError`를 `except`로 별도 catch 후 `raise`로 상위 전파 (84~85행)
- `except Exception`에서만 더미 폴백 (86~88행)
- `api/characters.py`에서 `CharacterGenerationError`를 catch하여 HTTP 400으로 사용자 메시지 전달 (52~56행)
- 테스트 `test_content_policy_error_returns_400`에서 400 응답 + "콘텐츠 정책" 메시지 검증 통과

### 피드백 3: [SHOULD] output_format="png" 명시 — 반영 완료
- `ai_character.py` images.edit 호출에 `output_format="png"` 파라미터 추가 (128행)
- 테스트 `test_output_format_png_specified`에서 파라미터 전달 검증 통과

### 피드백 4: [SHOULD] 라우터 docstring 업데이트 — 반영 완료
- `api/characters.py` docstring이 "AI 생성, API 키 없으면 더미 폴백"으로 변경됨 (47행)

## SPEC 완료 기준 대조
- [PASS] 완료 기준 1: `POST /api/books/:id/character`가 GPT Image `images.edit`으로 교체됨 (ai_character.py)
- [PASS] 완료 기준 2: 입력으로 아이 사진(photo_path) + 그림체(art_style) + 직업(job_name) + 동화 스타일(story_style) 전달
- [PASS] 완료 기준 3: size="1024x1024", output_format="png" 설정으로 1024x1024 PNG 출력
- [PASS] 완료 기준 4: `ART_STYLE_KEYWORDS`에 5종 그림체 키워드, `JOB_DESCRIPTIONS`에 15개 직업 복장 묘사. 프롬프트에 반영 확인.
- [PASS] 완료 기준 5: 이미지를 `uploads/characters/`에 파일 저장, `character_sheets` 테이블에 DB 레코드 생성. 경로는 URL 형태(`/uploads/characters/filename.png`)로 통일.
- [PASS] 완료 기준 6: `MAX_CHARACTER_GENERATIONS = 5` (최초 1회 + 재생성 4회)로 제한. 갤러리 방식 유지.
- [PASS] 완료 기준 7: 콘텐츠 정책 위반 시 `CharacterGenerationError` → HTTP 400으로 사용자에게 에러 메시지 전달. 기타 오류는 더미 폴백.

## 테스트 검증
- Developer 테스트 수: 49개 (test_ai_character.py 21개 + test_characters.py 28개)
- 전체 통과: 49/49
- R2에서 추가된 테스트: 3개 (content_policy_400, url_format, output_format)
- 빠진 테스트 케이스: 특이사항 없음

## 구체적 개선 지시
없음. R1 피드백 항목(MUST 2건, SHOULD 2건)이 모두 적절히 반영되었고, 기존 합격 항목에 퇴보 없음.
