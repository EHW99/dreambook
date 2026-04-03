# GPT Image API 레퍼런스

## 모델 정보

| 항목 | 내용 |
|------|------|
| 모델명 | gpt-image-1 |
| 제공사 | OpenAI |
| 특징 | 네이티브 멀티모달 (텍스트+이미지 입력 → 이미지 출력) |
| style 파라미터 | 없음 (DALL-E 3에서 제거됨, 프롬프트로 스타일 지정) |
| 파인튜닝 | 미지원 |
| 스트리밍 | 미지원 (gpt-image-1.5만 지원) |

---

## 1. images.generate (이미지 생성)

**엔드포인트**: `POST /v1/images/generations`

| 파라미터 | 타입 | 필수 | 허용 값 | 기본값 | 설명 |
|---|---|---|---|---|---|
| `model` | string | O | `gpt-image-1` | — | 사용할 모델 |
| `prompt` | string | O | 최대 32,000자 | — | 생성할 이미지 설명 |
| `n` | integer | X | 1~10 | 1 | 생성할 이미지 수 |
| `size` | string | X | `1024x1024`, `1024x1536`, `1536x1024`, `auto` | `auto` | 이미지 크기 |
| `quality` | string | X | `low`, `medium`, `high` | `medium` | 품질 수준 |
| `output_format` | string | X | `png`, `jpeg`, `webp` | `png` | 출력 포맷 |
| `output_compression` | integer | X | 0~100 | 100 | 압축률 (jpeg/webp만 적용) |
| `background` | string | X | `transparent`, `opaque`, `auto` | `auto` | 배경 투명 여부 (png/webp만 지원) |
| `moderation` | string | X | `auto`, `low` | `auto` | 콘텐츠 필터링 강도 |
| `response_format` | string | X | `b64_json`, `url` | `b64_json` | 응답 형식 |
| `user` | string | X | 임의 문자열 | — | 최종 사용자 식별용 |

**참고**: gpt-image-1은 항상 base64 인코딩 이미지를 반환한다 (url 방식 미지원 보고 있음).

---

## 2. images.edit (이미지 편집 / 참조 이미지 입력)

**엔드포인트**: `POST /v1/images/edits`

| 파라미터 | 타입 | 필수 | 허용 값 | 기본값 | 설명 |
|---|---|---|---|---|---|
| `model` | string | O | `gpt-image-1` | — | 사용할 모델 |
| `prompt` | string | O | 최대 32,000자 | — | 편집 지시사항 |
| `image` | file | O | PNG, WebP, JPG (최대 16장, 각 50MB) | — | 참조/편집할 이미지 |
| `mask` | file | X | PNG (4MB, 원본과 동일 해상도) | — | 편집 영역 마스크 (투명=편집 대상) |
| `n` | integer | X | 1~10 | 1 | 생성할 이미지 수 |
| `size` | string | X | `1024x1024`, `1024x1536`, `1536x1024` | `1024x1024` | 출력 크기 |
| `quality` | string | X | `low`, `medium`, `high` | `medium` | 품질 수준 |
| `output_format` | string | X | `png`, `jpeg`, `webp` | `png` | 출력 포맷 |
| `output_compression` | integer | X | 0~100 | 100 | 압축률 |
| `background` | string | X | `transparent`, `opaque`, `auto` | `auto` | 배경 투명 여부 |
| `response_format` | string | X | `b64_json`, `url` | — | 응답 형식 |
| `user` | string | X | 임의 문자열 | — | 사용자 식별 |

**주의**: images.edit은 로컬 파일 경로만 허용. URL이나 base64 입력은 지원하지 않음.

---

## 3. 참조 이미지 활용 (캐릭터 일관성)

images.edit의 `image` 파라미터로 **최대 16장**의 참조 이미지를 입력할 수 있다.

### 캐릭터 시트 방식

```
Step 1: 캐릭터 시트 생성 (1회)
  입력: 아이 원본 사진
  API: images.edit
  프롬프트: "이 아이를 동화 일러스트 스타일로 변환.
            정면/측면/전신 포즈. 수채화 톤."
  출력: 일러스트화된 캐릭터 시트 → 저장

Step 2: 페이지별 장면 생성 (페이지마다)
  입력: 캐릭터 시트 (참조 이미지)
  API: images.edit
  프롬프트: "이 캐릭터가 소방차 앞에서 호스를 들고 있는 장면.
            동화 일러스트 스타일. 수채화 톤."
  출력: 해당 페이지 일러스트
```

### 일관성 강화 팁
- 캐릭터 시트를 여러 앵글로 생성 → 참조 이미지로 여러 장 입력
- 매 페이지 프롬프트에 스타일 키워드 통일 (예: "수채화", "파스텔 톤")
- 캐릭터 외형 묘사를 프롬프트에 매번 포함 ("갈색 머리, 빨간 소방관 모자")

---

## 4. 가격

### 토큰 기반 가격 (1M 토큰당)
| 유형 | 가격 |
|------|------|
| 텍스트 입력 | $5.00 |
| 텍스트 입력 (캐시) | $1.25 |
| 이미지 입력 | $10.00 |
| 이미지 출력 | $40.00 |

### 이미지당 예상 가격
| 품질 | 1024x1024 | 1024x1536 |
|------|-----------|-----------|
| low | ~$0.011 | ~$0.016 |
| medium | ~$0.042 | ~$0.063 |
| high | ~$0.167 | ~$0.250 |

### 우리 프로젝트 비용 추정 (24p 책 1권)
- 캐릭터 시트 1장 (medium): ~$0.042
- 내용 11장면 (medium): ~$0.042 × 11 = ~$0.462
- 재생성 포함 최악 (페이지당 4회): ~$0.042 × 11 × 4 = ~$1.848
- **1권당 예상 비용: $0.5 ~ $1.9 (약 700~2,700원)**

---

## 5. 제한사항

| 항목 | 제한 |
|------|------|
| 지원 크기 | 1024x1024, 1024x1536, 1536x1024 (3종만) |
| 요청당 최대 생성 수 (n) | 10장 |
| 프롬프트 최대 길이 | 32,000자 |
| 입력 이미지 최대 크기 | 50MB |
| 입력 이미지 최대 개수 (edit) | 16장 |
| 마스크 최대 크기 | 4MB (PNG만) |
| Rate limit | 티어별 분당 5~250장 |
| 지원 포맷 | PNG, WebP, JPG |

---

## 6. 우리 프로젝트 적용 설정 권장값

| 파라미터 | 권장값 | 이유 |
|---|---|---|
| `model` | `gpt-image-1` | 기본 모델 |
| `size` | `1024x1024` | 정방형 판형 (SQUAREBOOK_HC)에 맞음 |
| `quality` | `medium` | 비용/품질 균형 |
| `output_format` | `png` | Book Print API 업로드 호환 |
| `background` | `opaque` | 동화 일러스트는 배경 필요 |
