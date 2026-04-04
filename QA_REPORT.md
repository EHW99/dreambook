# QA 리포트 — 태스크 17: AI 페이지 일러스트 생성 (GPT Image) (R1)

## 전체 판정: PASS
## 가중 점수: 7.5 / 10.0

## 항목별 점수
- 기능 완성도 (30%): 8/10 — 9개 완료 기준 모두 구현됨. 진행률은 프론트엔드 시뮬레이션 방식(실시간 서버 연동이 아님)이지만 기능적으로 충분
- 코드 품질 (25%): 7/10 — 에러 처리 및 폴백 잘 구현됨. ART_STYLE_KEYWORDS/JOB_DESCRIPTIONS가 3개 서비스 파일에 중복 정의. character_sheet_path 빈 문자열 전달 시 비효율적 에러 경로 존재
- API 연동 (20%): 8/10 — images.edit 호출 파라미터(model=gpt-image-1, size=1024x1024, quality=medium, output_format=png)가 gpt-image-api.md 권장값과 일치. b64_json 응답 처리 정확. 타임아웃 120초 적절
- 디자인 품질 (25%): 7/10 — 원형 진행률 바 + 단계별 상태 텍스트 + 파스텔 컬러 + 이탈 방지 경고 포함. 프론트엔드 신규 변경은 이번 태스크 범위 밖이므로 기존 UI 유지 상태로 평가

**가중 점수 계산**: (8 x 0.3) + (7 x 0.25) + (8 x 0.2) + (7 x 0.25) = 2.4 + 1.75 + 1.6 + 1.75 = **7.5**

## SPEC 완료 기준 대조
- [PASS] 완료 기준 1: `POST /api/books/:id/generate`에서 `generate_story()` → `_generate_page_illustration()` → `generate_illustration_or_dummy()` 순으로 GPT Image images.edit을 호출한다
- [PASS] 완료 기준 2: 입력으로 캐릭터 시트(참조 이미지) + scene_description + art_style 키워드를 사용한다. `_build_illustration_prompt()`에서 ai-guide.md 규칙(그림체 키워드 동일, 캐릭터 외형 묘사 포함, 텍스트 영역 확보)을 준수한다
- [PASS] 완료 기준 3: size="1024x1024", quality="medium", output_format="png" 설정 확인. b64_json 디코딩 후 PNG 바이트 반환
- [PASS] 완료 기준 4: `generate_story()`에서 `story_data["pages"]`를 순회하며 페이지별 `_generate_page_illustration()`을 호출. `logger.info(f"페이지 {page_number}/{total_pages} 일러스트 생성 완료")`로 진행 로깅
- [PASS] 완료 기준 5: `regenerate_image` 엔드포인트(books.py 314행)에서 `generate_illustration_or_dummy()`를 직접 호출하여 AI 재생성 수행
- [PASS] 완료 기준 6: `page.image_regen_count >= 4` 검증 후 422 에러 반환. 갤러리 방식으로 기존 이미지 is_selected=False 후 새 이미지 추가. 테스트에서 4회 재생성 후 5회째 422 확인됨
- [PASS] 완료 기준 7: `regenerate_story` → `generate_story()` → `db.query(Page).filter(...).delete()` → 새 페이지 생성(image_regen_count=0 기본값). 테스트 `test_story_regen_resets_image_regen_count`에서 검증됨
- [PASS] 완료 기준 8: 프론트엔드 `step-generating.tsx`에서 원형 진행률 바 + 단계별 상태 텍스트 표시. 백엔드에서 페이지별 로깅. 실시간 SSE/WebSocket은 아니지만 SPEC 요구사항 충족
- [PASS] 완료 기준 9: 에러 처리 3단계 — (1) BadRequestError에서 content_policy 검출, (2) 일반 Exception catch + IllustrationGenerationError, (3) `generate_illustration_or_dummy`에서 모든 실패를 None으로 변환하여 placeholder 폴백

## 테스트 검증
- Developer 테스트 수: 19개 (test_ai_illustration.py)
- 전체 통과: 19/19
- 테스트 범주: 프롬프트 구성(4), API 호출 mock(3), 폴백 로직(3), 생성 연동(3), 재생성(3), 스토리 연쇄(2), 진행률(1)
- 빠진 테스트 케이스:
  - character_sheet_path가 빈 문자열("")일 때의 동작 테스트 (현재는 open("") → 예외 → catch → None 폴백으로 암묵 처리됨)
  - JOB_DESCRIPTIONS에 없는 직업명에 대한 `_get_job_description` 폴백 테스트 (로직은 단순하지만 커버리지 누락)
  - 동시 generate 요청 시 race condition 테스트 (동일 book_id로 중복 호출 가능성)

## ai-guide.md 프롬프트 규칙 준수 확인
- [PASS] 매 페이지에 그림체 키워드 동일 포함: `ART_STYLE_KEYWORDS`에서 조회 → 프롬프트 첫 문장에 삽입
- [PASS] 캐릭터 시트를 매번 참조 이미지로 전달: `image=photo_file` (캐릭터 시트 파일)
- [PASS] 캐릭터 외형 묘사 매번 포함: `JOB_DESCRIPTIONS`에서 직업 복장 묘사를 프롬프트에 포함
- [PASS] "No text or letters in the image" — 이미지에 텍스트 미포함 지시
- [PASS] 텍스트 배치 영역 확보 지시 ("Leave space at the bottom or top for text overlay")
- [PASS] Anti-Slop: 배경 묘사 포함 ("Detailed background matching the scene")
- [PASS] quality: medium 사용 (비용 절약)
- [PASS] size: 1024x1024 (정방형 판형에 맞음)

## 구체적 개선 지시

### 비차단 개선 사항 (PASS 유지, 향후 개선 권장)

1. **ART_STYLE_KEYWORDS / JOB_DESCRIPTIONS 중복 제거**: `ai_illustration.py`, `ai_character.py`, `ai_story.py` 3개 파일에 동일한 딕셔너리가 중복 정의되어 있다. 공통 모듈(예: `app/services/ai_constants.py`)로 추출하여 단일 소스로 관리할 것.

2. **character_sheet_path 빈 문자열 처리 개선**: `books.py` 357행과 `generate.py` 88행에서 `char_path or ""`로 빈 문자열을 전달하면 `generate_illustration_image()`에서 `open("")` 호출 → 예외 발생 → catch → None 반환의 비효율적 경로를 탄다. `generate_illustration_or_dummy()` 함수 시작 부분에서 `character_sheet_path`가 비어있거나 파일이 존재하지 않으면 API 호출 전에 early return None하는 가드를 추가하는 것이 좋다.

3. **파일 핸들 관리**: `ai_illustration.py` 122행에서 `photo_file = open(...)` + `try/finally/close()` 대신 `with` 구문을 사용하는 것이 더 Pythonic하다. 현재도 동작에 문제는 없다.
