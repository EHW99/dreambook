# 셀프체크 — 태스크 17: AI 페이지 일러스트 생성 (GPT Image)

## 테스트 결과
- 전체 테스트 수: 19개 (test_ai_illustration.py)
- 통과: 19개
- 실패: 0개

## SPEC 기능 체크
- [x] 1. `POST /api/books/:id/generate`의 이미지 생성 로직을 GPT Image images.edit으로 교체
- [x] 2. **입력**: 캐릭터 시트 (참조 이미지) + scene_description + 그림체 키워드
- [x] 3. **출력**: 1024x1024 PNG 일러스트 (quality: medium)
- [x] 4. 페이지별 일러스트 순차 생성 (전체 페이지 수만큼)
- [x] 5. 이미지 재생성 (`POST /api/books/:id/pages/:pageId/regenerate-image`) 실제 AI 호출
- [x] 6. 재생성 횟수 체크 (페이지당 최대 4회, 갤러리 방식)
- [x] 7. **스토리 재생성 연쇄 처리**: 스토리 재생성 시 기존 페이지 삭제 → 새 일러스트 자동 생성 → image_regen_count 리셋
- [x] 8. 생성 진행률 표시: 페이지별 로깅 (프론트엔드 진행률 바와 연동 가능)
- [x] 9. 에러 처리: 콘텐츠 정책 위반/API 오류/키 미설정 → 더미 폴백

## 구현 파일
- `backend/app/services/ai_illustration.py` — **신규**: GPT Image 일러스트 생성 서비스
- `backend/app/services/generate.py` — **수정**: AI 일러스트 연동, `_generate_page_illustration` 헬퍼
- `backend/app/api/books.py` — **수정**: `regenerate_image`에 AI 호출 추가
- `backend/tests/test_ai_illustration.py` — **신규**: 19개 테스트 (전부 mock, 실제 API 호출 없음)

## 특이사항
- OPENAI_API_KEY가 환경에 설정되어 있으면 실제 GPT Image API 호출, 없으면 placeholder 이미지 폴백
- AI 호출 실패 시에도 서비스 중단 없이 placeholder로 폴백
- quality: medium 사용하여 비용 절약
- 기존 test_generate.py의 일부 테스트 실패는 이번 태스크와 무관 — 환경에 OPENAI_API_KEY가 있어 GPT-4o API 429(quota exceeded) 발생
