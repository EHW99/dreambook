# 셀프체크 — 태스크 15: AI 스토리 생성 (GPT-4o) — R2

## 테스트 결과
- 전체 테스트 수: 21개 (test_ai_story.py)
- 통과: 21개
- 실패: 0개

### 기존 테스트 (test_generate.py)
- 전체: 28개
- 통과: 26개
- 실패: 2개 (기존 SQLite teardown 순서 이슈 — 본 태스크와 무관)

## R1 → R2 피드백 반영 내역

### 1. [필수] requirements.txt에 openai 패키지 추가 ✅
- `backend/requirements.txt`에 `openai>=1.0.0` 추가
- 새 환경에서 `pip install -r requirements.txt`만으로 openai 설치 가능

### 2. [권장] 프롬프트 검증 테스트 강화 ✅
- `test_generate_story_dreaming_today_style`: `"꿈이 이루어진 세계"` 키워드 검증 추가
- `test_generate_story_future_me_style`: `"성장 과정"` 또는 `"일대기"` 키워드 검증 추가
- `test_generate_story_art_style_in_prompt` (신규): art_style="watercolor" 전달 시 시스템 프롬프트에 "watercolor" 포함 검증

### 3. [권장] 응답 검증 엣지 케이스 테스트 추가 ✅
- `test_response_missing_pages_key_raises` (신규): pages 키 없는 JSON → StoryGenerationError 발생
- `test_response_missing_title_uses_fallback` (신규): title 없는 응답 → 첫 페이지 텍스트로 대체
- `test_page_count_mismatch_logs_warning` (신규): 페이지 수 불일치 시 warning 로그 확인

## SPEC 기능 체크
- [x] `POST /api/books/:id/generate`의 스토리 생성 로직을 GPT-4o 호출로 교체
- [x] **입력**: 아이 이름, 직업, 동화 스타일(꿈꾸는 오늘/미래의 나), 줄거리, 페이지 수
- [x] **출력**: 페이지별 text_content + scene_description (이미지 생성 프롬프트)
- [x] **프롬프트**: ai-guide.md 규칙에 따라 설계 (5~7세 어휘, 금지사항, 동화 스타일별 분기)
- [x] 스토리 재생성 (`POST /api/books/:id/regenerate-story`) GPT-4o 호출로 교체
- [x] 재생성 횟수 체크 (최대 3회)
- [x] 에러 처리: API 실패 시 사용자 안내 (500 + "스토리 생성에 실패했습니다"), 타임아웃 처리
- [x] OPENAI_API_KEY 없으면 더미 스토리 폴백 (개발 편의)

## 구현 파일
1. `backend/app/services/ai_story.py` — AI 스토리 생성 서비스 (변경 없음)
2. `backend/app/services/generate.py` — 더미 → AI 호출 분기 (변경 없음)
3. `backend/app/api/books.py` — 에러 핸들링 (변경 없음)
4. `backend/requirements.txt` — openai>=1.0.0 추가 (R2)
5. `backend/tests/test_ai_story.py` — 17개 → 21개 테스트 (R2: +4개)

## 특이사항
- 모든 테스트에서 OpenAI API는 mock 사용 (실제 호출 없음)
- 기존 test_generate.py의 2개 실패는 SQLite teardown 순서 문제로 본 태스크 이전부터 존재하는 이슈
- `response_format: {"type": "json_object"}`를 사용하여 GPT-4o가 반드시 JSON으로 응답하도록 강제
- 재생성 실패 시 story_regen_count를 롤백하여 사용자가 재시도할 수 있도록 처리
