# GPT Image 실전 가이드 — dreambook 서비스 특화

## 모델 정보

| 항목 | gpt-image-1 | gpt-image-1.5 (최신) |
|------|------------|---------------------|
| 1024x1024 Low | $0.011 | $0.009 |
| 1024x1024 Medium | $0.042 | $0.034 |
| 1024x1024 High | $0.167 | $0.133 |
| 특징 | 안정적, 저렴 | 더 정밀, 일관성 개선 |

**우리 서비스 권장**: `gpt-image-1` + `quality: medium` (장당 $0.042)
- 24페이지 책 1권 = 약 $1.05 (캐릭터 시트 포함)
- 테스트/반복 시 `quality: low` 사용 ($0.011)

---

## 캐릭터 시트 생성 (images.edit)

### 핵심 전략: Character Anchor

1. **베이스 캐릭터 먼저 생성** — 아이 사진을 참조 이미지로, 정면 전신 캐릭터 생성
2. **이 캐릭터를 모든 페이지의 참조 이미지로 재사용**
3. **매 프롬프트마다 외형 묘사를 반복** — "same face, same hair, same proportions"

### 프롬프트 템플릿

```
Transform this child into a [ART_STYLE] storybook character.
Full body, front-facing pose, plain white background.
Preserve the child's facial features: [구체적 특징 - eye shape, hair color, face shape].
Wearing [JOB] uniform/outfit: [복장 상세 묘사].
Age-appropriate proportions for a [나이]yo child.
Style: [그림체 키워드]
```

### 그림체별 최적 키워드

| 스타일 | 프롬프트 키워드 (검증됨) |
|--------|----------------------|
| 수채화 | `watercolor illustration, soft warm tones, gentle brushstrokes, children's picture book style, muted pastel palette` |
| 연필화 | `pencil sketch illustration, fine line art, hand-drawn, cross-hatching, soft graphite shading` |
| 크레파스 | `crayon drawing, childlike texture, bold saturated colors, thick waxy strokes, kindergarten art style` |
| 3D | `3D render, Pixar-style character, soft ambient lighting, rounded smooth shapes, subsurface scattering on skin` |
| 만화 | `cartoon style, cel-shaded, vibrant flat colors, clean black outlines, anime-influenced children's illustration` |

---

## 페이지별 일러스트 일관성

### 반드시 지켜야 할 규칙

1. **참조 이미지 매번 전달** — 확정된 캐릭터 시트를 images.edit의 image로 매번 전달
2. **외형 묘사 매번 반복** — 프롬프트에 캐릭터 특징을 매번 명시
3. **그림체 키워드 동일하게** — 모든 페이지에서 같은 스타일 키워드 사용
4. **구도만 변경** — 캐릭터는 고정, 배경/포즈/상황만 변경

### 일러스트 프롬프트 템플릿

```
[ART_STYLE] children's storybook illustration.
Scene: [scene_description]
Character: [캐릭터 묘사 — 캐릭터 시트 기반. 항상 동일하게]
- Same face, same hair, same proportions as the reference image
- Wearing [직업 복장]
Composition: Leave space for text at [top/bottom].
Background: [장면에 맞는 구체적 배경 묘사]
Mood: warm, inviting, age-appropriate for 5-7 year olds
```

### Anti-Slop 체크리스트

피해야 할 것:
- ❌ "beautiful", "stunning", "amazing" 같은 모호한 형용사
- ❌ 배경 없이 캐릭터만 둥둥 뜬 이미지
- ❌ 페이지마다 완전히 다른 그림체
- ❌ 성인 체형 (꿈꾸는 오늘 스타일)
- ❌ 비현실적으로 큰 눈

해야 할 것:
- ✅ 구체적인 시각 묘사 ("medium shot from waist up")
- ✅ 배경 디테일 명시
- ✅ 조명/분위기 명시 ("warm golden hour lighting")
- ✅ 매 페이지 캐릭터 특징 반복 명시

---

## 아이 사진 → 캐릭터 변환 주의사항

### 콘텐츠 필터링

- GPT-4o/gpt-image-1은 **아이 사진에 대해 더 엄격한 필터** 적용
- 실사 아이 이미지의 편집을 거부할 수 있음
- **대응 방법**:
  - 프롬프트에 "children's storybook illustration", "cartoon character" 명시
  - "Transform into illustrated character" 방식으로 요청
  - 거부 시 사용자에게 "다른 사진을 시도해주세요" 안내
  - `moderation: "auto"` 유지 (기본값)

### 얼굴 특징 유지 팁

- 일반적 묘사 대신 **구체적 특징** 사용
  - ❌ "cute face"
  - ✅ "round face with small nose, dark brown straight hair with bangs, slightly upturned eyes"
- 캐릭터 시트 생성 시 **정면 포즈** 필수 (측면은 일관성 떨어짐)

---

## 비용 최적화 전략

### 1. 프롬프트를 한 번에 잘 쓰기
- 모호한 프롬프트 → 재생성 필요 → 비용 2배
- 구체적 프롬프트 → 1회로 충분 → 비용 절약

### 2. Quality 선택 기준
| 상황 | 추천 quality |
|------|------------|
| 개발/테스트 | low ($0.011) |
| 사용자 미리보기 | medium ($0.042) |
| 최종 인쇄용 | high ($0.167) |

### 3. 재생성 비용 예측 (24페이지 책 기준, medium)
- 캐릭터 시트 1회: $0.042
- 페이지 일러스트 24회: $1.008
- **기본 1권 = ~$1.05**
- 캐릭터 재생성 4회 추가: +$0.168
- 스토리 재생성 시 일러스트 전부 재생성: +$1.008
- **최악의 경우 = ~$3.3**

### 4. 서버 테스트 시 반드시 API 키 제거
- `.env`에서 `OPENAI_API_KEY` 주석 처리
- 더미 폴백이 동작하여 비용 발생 없음

---

## 에러 처리

| 에러 | 원인 | 대응 |
|------|------|------|
| 400 content_policy | 아이 사진 필터링 | "다른 사진을 사용해주세요" 안내 |
| 400 invalid_image | 이미지 형식/크기 문제 | 이미지 리사이즈 후 재시도 |
| 429 rate_limit | 초당 요청 초과 | Retry-After 기반 대기 후 재시도 |
| 500 server_error | OpenAI 서버 문제 | 3회 재시도 후 placeholder 폴백 |
| timeout | 생성 시간 초과 | 120초 타임아웃, placeholder 폴백 |

---

## gpt-image-1.5 업그레이드 고려사항

현재 gpt-image-1을 사용 중이나, gpt-image-1.5가 더 나은 점:
- 캐릭터 일관성 개선
- 가격 약 20% 저렴
- 더 정밀한 프롬프트 준수

모델명만 변경하면 마이그레이션 가능 (`model="gpt-image-1"` → `"gpt-image-1.5"`).
서비스 안정화 후 전환 고려.
