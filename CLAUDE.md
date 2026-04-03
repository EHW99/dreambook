# 꿈꾸는 나 (dreambook) — AI 직업 동화책 서비스

- **GitHub 저장소**: `dreambook`

## 프로젝트 개요

- **서비스**: 아이의 이름/특징 + 직업 선택 → AI 동화 스토리 + 일러스트 생성 → 실물 동화책 인쇄/배송
- **회사**: (주)스위트북 — 포토북 인쇄/배송
- **마감**: 2026-04-08 (화) 23:59
- **제출**: GitHub Public 저장소 + 구글폼 서술형 4문항

## 기술 스택

| 영역 | 기술 |
|------|------|
| 프론트엔드 | Next.js (App Router) |
| 백엔드 | FastAPI (Python) |
| DB | SQLite (SQLAlchemy) |
| 스토리 생성 | GPT-4o (OpenAI API) |
| 이미지 생성 | GPT Image (OpenAI API) |
| 책 제작 | Book Print API (Sandbox) |

## 환경변수

```
BOOKPRINT_API_KEY=...        # 스위트북 API (필수)
BOOKPRINT_BASE_URL=https://api-sandbox.sweetbook.com/v1
OPENAI_API_KEY=...           # OpenAI (필수)
OPENROUTER_API_KEY=...       # OpenRouter (선택)
```

## Book Print API 핵심

- Sandbox URL: `https://api-sandbox.sweetbook.com/v1`
- 인증: `Authorization: Bearer {API_KEY}`
- **GET /book-specs 403** — 판형 UID 하드코딩:
  - SQUAREBOOK_HC (243×248mm, 하드커버, 24~130p)
  - PHOTOBOOK_A4_SC (210×297mm, 소프트커버, 24~130p)
  - PHOTOBOOK_A5_SC (148×210mm, 소프트커버, 50~200p)
- 워크플로우: 책 생성 → 사진 업로드 → 표지 → 내지(반복) → 최종화 → 견적 → 주문
- Sandbox 주문은 PAID 상태에서 정지 (실제 인쇄 없음)

---

# 오케스트레이터

이 프로젝트는 **3-Agent 하네스 구조**로 동작합니다.
Planner → Developer → Reviewer 파이프라인을 따릅니다.

## 전체 파이프라인

```
Phase 1: 전체 설계 (1회)
┌─────────────────────────────────────────┐
│  Planner 서브에이전트                     │
│  → .claude/docs/SPEC.md 생성             │
│  → .claude/docs/TASKS.md 생성            │
└─────────────────────────────────────────┘
                    ↓
Phase 2: 태스크 순차 실행 (반복)
┌─────────────────────────────────────────┐
│  각 태스크마다:                           │
│  Developer 서브에이전트 → 코드 구현        │
│  Reviewer 서브에이전트 → 검수              │
│    ├── PASS → 다음 태스크                 │
│    └── FAIL → Developer 재작업 (최대 3회)  │
└─────────────────────────────────────────┘
                    ↓
Phase 3: AI 기능 통합
┌─────────────────────────────────────────┐
│  ai-guide.md 규칙에 따라 AI 연동          │
│  기존 스텁을 실제 API 호출로 교체          │
│  Developer → Reviewer 루프 동일 적용      │
└─────────────────────────────────────────┘
                    ↓
Phase 4: 최종 검증 + 제출 마무리
```

---

## 서브에이전트 호출 방법

각 단계에서 **Agent 도구**를 사용하여 서브에이전트를 호출합니다.
**핵심: Developer와 Reviewer는 반드시 다른 서브에이전트로 호출한다.** (만드는 놈 ≠ 평가하는 놈)

---

## 단계별 실행 지시

### 단계 1: Planner 호출 (프로젝트 시작 시 1회)

```
.claude/agents/planner.md 파일을 읽고, 그 지시를 따라라.
.claude/agents/evaluation_criteria.md 파일도 읽고 참고하라.
.claude/docs/service-plan.md 파일을 읽어라. 이것이 확정된 서비스 기획서다.

결과를 .claude/docs/SPEC.md와 .claude/docs/TASKS.md로 저장하라.
```

Planner가 SPEC.md + TASKS.md를 생성하면, 사용자에게 리뷰를 요청한다.
사용자 승인 후 Phase 2로 진행.

설계 변경이 필요한 경우에만 Planner를 재호출한다.

### 단계 2: Developer 호출 (태스크별)

최초 실행:
```
.claude/agents/developer.md 파일을 읽고, 그 지시를 따라라.
.claude/agents/evaluation_criteria.md 파일도 읽고 참고하라.
.claude/docs/SPEC.md 파일을 읽어라. 이것이 전체 설계서다.
.claude/docs/TASKS.md 파일을 읽어라.

현재 태스크: 태스크 [번호] — [이름]
완료 기준: [TASKS.md에서 해당 태스크의 완료 기준]

TDD로 구현하라. 완료 후 SELF_CHECK.md를 작성하라.
```

피드백 반영 시 (R2, R3):
```
.claude/agents/developer.md 파일을 읽고, 그 지시를 따라라.
.claude/agents/evaluation_criteria.md 파일도 읽고 참고하라.
.claude/docs/SPEC.md 파일을 읽어라.
QA_REPORT.md 파일을 읽어라. 이것이 Reviewer의 피드백이다.

피드백의 "구체적 개선 지시"를 모두 반영하라.
완료 후 SELF_CHECK.md를 업데이트하라.
```

### 단계 3: Reviewer 호출 (태스크별)

```
.claude/agents/reviewer.md 파일을 읽고, 그 지시를 따라라.
.claude/agents/evaluation_criteria.md 파일을 읽어라. 이것이 채점 기준이다.
.claude/docs/SPEC.md 파일을 읽어라. 이것이 설계서다.
.claude/docs/TASKS.md 파일을 읽어라.
SELF_CHECK.md 파일을 읽어라. 이것은 Developer의 자체 점검이다 (신뢰하지 말 것).

현재 태스크: 태스크 [번호] — [이름]

검수 절차:
1. Developer가 작성한 테스트를 실행하라
2. 빠진 테스트 케이스를 찾아라
3. TASKS.md의 완료 기준을 하나하나 대조하라
4. evaluation_criteria.md에 따라 4개 항목을 채점하라
5. 최종 판정(PASS/CONDITIONAL/FAIL)을 내려라

결과를 QA_REPORT.md 파일로 저장하라.
```

### 단계 4: 판정 확인

QA_REPORT.md를 읽고 판정을 확인한다.

- **PASS** → 사용자에게 완료 보고 → 다음 태스크
- **CONDITIONAL / FAIL** → Developer에게 피드백 전달 → 단계 2로
- **3회째도 FAIL** → 자동 재시도 안 함. 사용자에게 보고하고 판단 위임

---

## 완료 보고 형식

태스크 완료 시:
```
## 태스크 [번호] 완료

**태스크**: [이름]
**QA 라운드**: X회
**최종 점수**: 기능 X/10, 코드 X/10, API X/10, UI X/10 (가중 X.X/10)

**실행 흐름**:
1. Developer R1: [구현 내용 한 줄]
2. Reviewer R1: [판정 + 핵심 피드백]
3. Developer R2: [수정 내용] (있는 경우)
4. Reviewer R2: [판정] (있는 경우)
```

---

## 프로젝트 구조

```
sweetbook/
├── CLAUDE.md                          ← 이 파일 (오케스트레이터)
├── .claude/
│   ├── agents/
│   │   ├── planner.md                 ← 전체 설계 + 태스크 분할
│   │   ├── developer.md               ← TDD 코드 구현
│   │   ├── reviewer.md                ← 엄격한 검수 (최대 3회)
│   │   ├── evaluation_criteria.md     ← 공용 평가 기준표
│   │   └── ai-guide.md               ← AI 프롬프트 가이드라인
│   └── docs/
│       ├── bookprint-api.md           ← Book Print API 레퍼런스
│       ├── orders-api.md              ← Orders API 분석
│       ├── project-history.md         ← 이전 세션 작업 기록
│       ├── SPEC.md                    ← (Planner가 생성)
│       └── TASKS.md                   ← (Planner가 생성)
├── frontend/                          ← Next.js (App Router)
├── backend/                           ← FastAPI
├── test/
│   └── bookprintapi-python-sdk/       ← Python SDK (수정 금지)
├── AI_이미지생성엔진_비교분석.md
├── AI_스토리생성모델_비교분석.md
├── 동화책_시장조사.md
├── 하네스_엔지니어링_분석.md
├── 스위트북_개발과제_안내문.pdf
├── SELF_CHECK.md                      ← (Developer가 생성)
└── QA_REPORT.md                       ← (Reviewer가 생성)
```

---

## 커밋 규칙

- 커밋 전에 반드시 사용자에게 먼저 확인 ("커밋할까요?" 등)
- 작업 단위로 커밋 (기능 하나, 버그 수정 하나 등)
- 커밋 메시지는 한국어
- .env, API Key 등 민감 정보는 절대 커밋하지 않음

---

## 절대 규칙

- API Key 절대 커밋하지 않음
- `test/bookprintapi-python-sdk/` 수정 금지
- Developer와 Reviewer는 반드시 별도 서브에이전트로 호출 (역할 분리)
- 서브에이전트 호출 시 필요한 파일을 반드시 읽도록 지시
- 서브에이전트는 검토/보고만 — 수정은 사용자 승인 후 반영
- 한국어 사용
