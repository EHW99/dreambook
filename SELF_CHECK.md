# 셀프체크 — 태스크 18: AI 생성 통합 테스트 + 성향 테스트 UI

## 테스트 결과
- 전체 테스트 수: 28개 (test_integration_e2e.py)
- 통과: 28개
- 실패: 0개
- 기존 테스트: 영향 없음 (기존 실패는 OpenAI API 쿼터 초과로 인한 pre-existing 이슈)

## SPEC 기능 체크
- [x] **E2E 테스트**: 정보 입력 → 직업 → 스타일 → 그림체 → 캐릭터 생성 → 확정 → 줄거리 → AI 생성 → 편집 전체 흐름 동작 (TestE2EWizardFlow)
- [x] **스토리 테마 선택 연결**: 테마 카드 클릭 시 해당 테마를 줄거리로 전달 → AI 스토리 생성에 반영 (step-plot.tsx에서 THEME_PLOTS 매핑 + TestThemePlotIntegration)
- [x] **성향 테스트 UI**: "어떤 직업이 좋을지 모르겠어요" → 간단한 성향 질문 (5개) → 직업 추천 (규칙 기반) (aptitude-test.tsx + aptitude_test.py + aptitude.py API)
- [x] **재생성 전체 흐름 테스트**: 캐릭터 4회 (TestRegeneration.test_character_regeneration_max_4), 스토리 3회 (test_story_regeneration_max_3), 이미지 페이지당 4회 (test_image_regeneration_max_4_per_page)
- [x] **비용 모니터링 로그**: API 호출 횟수, 토큰 사용량 로깅 (cost_monitor.py + ai_story/ai_character/ai_illustration에 로깅 추가)

## 구현 내용

### 백엔드
1. **cost_monitor.py** — AI API 비용 모니터링 싱글톤 (호출 횟수, 토큰 수, 에러 추적)
2. **ai_story.py** — GPT-4o 호출 성공/실패 시 cost_monitor에 로깅 추가
3. **ai_character.py** — GPT Image 호출 성공/실패 시 cost_monitor에 로깅 추가
4. **ai_illustration.py** — GPT Image 호출 성공/실패 시 cost_monitor에 로깅 추가
5. **aptitude_test.py** — 규칙 기반 성향 테스트 서비스 (5개 질문, 5개 카테고리, 점수 계산)
6. **aptitude.py API** — GET /api/aptitude/questions, POST /api/aptitude/result (비로그인 접근 가능)
7. **test_integration_e2e.py** — 28개 테스트 (E2E, 테마 연결, 재생성, 성향 테스트, 비용 모니터링)

### 프론트엔드
1. **step-plot.tsx** — 3개 테마 카드("모험", "도움", "배움") 활성화, 클릭 시 줄거리 자동 생성
2. **aptitude-test.tsx** — 성향 테스트 컴포넌트 (질문 UI, 결과 화면, 직업 추천)
3. **step-job-select.tsx** — "어떤 직업이 좋을지 모르겠어요" 버튼을 성향 테스트 모달로 연결

## 특이사항
- 모든 테스트에서 실제 OpenAI API 호출 없음 (전부 mock 또는 더미 폴백 사용)
- 비용 모니터링은 로깅만 구현 (실제 과금 집계는 하지 않음)
- 성향 테스트는 AI 호출 없이 규칙 기반으로 동작
- 기존 test_generate.py의 일부 테스트가 실패하나, 이는 OpenAI API 쿼터 초과로 인한 pre-existing 이슈로 본 태스크와 무관
