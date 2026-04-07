# 계획: 책 미리보기/뷰어 리팩토링

> **작성일**: 2026-04-07
> **목적**: 편집용 미리보기와 완성 책 뷰어를 분리하고, 각각의 정확도와 UX를 개선한다.

---

## 배경

### 현재 상태
- `BookPreview` 컴포넌트 1개로 편집(`/create/edit`)과 보기(`/books/[id]/view`) 모두 처리
- 템플릿 좌표를 하드코딩하여 직접 렌더링 (정확도 부족, 템플릿 변경 시 수동 업데이트 필요)
- 완성 책 보기에 실제 인쇄 모습과 다를 수 있음

### 목표 구조

| | 편집 미리보기 | 완성 책 뷰어 |
|--|-------------|-------------|
| **경로** | `/create/edit` | `/books/[id]/view` |
| **컴포넌트** | `BookPreview` (기존, 개선) | `BookViewer` (신규) |
| **데이터 소스** | 우리 DB (Page, PageImage) | Book Print API 렌더링 썸네일 (다운로드 저장) |
| **편집** | O (텍스트 클릭 수정) | X (읽기 전용) |
| **정확도** | 템플릿 좌표 기반 (근사치) | 실제 인쇄 모습 100% |
| **전제 조건** | 없음 | 주문 완료 (API에 책 존재) |
| **표지** | 우리 cover_image_path + 템플릿 좌표 렌더링 | API 썸네일 (cover.jpg) |
| **로고** | `/logo.png` 직접 배치 | API가 자동 포함 |

---

## Phase 1: 완성 책 뷰어 (BookViewer)

### 1-1. 렌더링 썸네일 다운로드 서비스 (백엔드)

**파일**: `backend/app/services/bookprint.py`에 메서드 추가

```python
async def download_thumbnails(self, book_uid: str, out_dir: str) -> dict:
    """Book Print API에서 렌더링 썸네일을 다운로드하여 파일로 저장한다.
    
    Returns:
        {"cover": "path/to/cover.jpg", "pages": ["path/to/0.jpg", ...]}
    """
```

**동작**:
1. 24페이지 렌더 요청 (POST /render/page-thumbnail × 24)
2. 5초 대기
3. cover.jpg + 0.jpg~23.jpg 다운로드
4. `uploads/thumbnails/{book_uid}/` 디렉토리에 저장
5. 실패한 페이지는 재시도 1회

### 1-2. 주문 완료 시 자동 다운로드

**파일**: `backend/app/api/orders.py`의 `create_order()` 수정

`execute_order_workflow()` 성공 후, `download_thumbnails()` 호출:
```python
# 주문 성공 후
result = await service.execute_order_workflow(...)

# 렌더링 썸네일 다운로드 (비동기, 실패해도 주문은 유지)
try:
    thumbnails = await service.download_thumbnails(result["book_uid"], thumbnail_dir)
    book.thumbnail_dir = thumbnail_dir  # DB에 경로 저장
except Exception:
    logger.warning("썸네일 다운로드 실패 — 나중에 재시도 가능")
```

### 1-3. 썸네일 조회 API (백엔드)

**새 엔드포인트**: `GET /api/books/{book_id}/thumbnails`

```python
@router.get("/{book_id}/thumbnails")
def get_thumbnails(book_id: int, ...):
    """완성된 책의 렌더링 썸네일 목록 반환
    
    Returns:
        {
            "cover": "/uploads/thumbnails/bk_xxx/cover.jpg",
            "pages": [
                "/uploads/thumbnails/bk_xxx/0.jpg",
                "/uploads/thumbnails/bk_xxx/1.jpg",
                ...
            ]
        }
    """
```

### 1-4. BookViewer 컴포넌트 (프론트엔드)

**파일**: `frontend/src/components/book-viewer.tsx` (신규)

실물 책을 보는 듯한 몰입감 있는 뷰어.

#### 핵심 UX
- **3D 페이지 플립 애니메이션**: 페이지를 넘길 때 종이가 접히며 넘어가는 CSS 3D transform 효과. `perspective` + `rotateY` 기반. 왼쪽→오른쪽(다음), 오른쪽→왼쪽(이전) 방향 구분.
- **책 그림자/두께감**: 펼친 책 중앙에 세로 그림자(책등 느낌), 페이지 가장자리에 미묘한 그라데이션 그림자로 종이 두께감 표현. `box-shadow` + `inset shadow` 레이어링.
- 키보드 좌우/스페이스 네비게이션
- 터치 스와이프 지원 (모바일)
- 풀스크린 지원
- 편집 기능 없음 (읽기 전용)

#### 스프레드 구성
```
[표지 앞면 (cover.jpg 오른쪽 절반)] — 단독
[0.jpg + 1.jpg] — 스프레드 (간지 + 그림1)
[2.jpg + 3.jpg] — 스프레드 (스토리1 + 그림2)
...
[뒷표지 (cover.jpg 왼쪽 절반)] — 단독
```

#### 비주얼 디테일
- 배경: 어두운 우드 톤 또는 따뜻한 다크 (#2a2420)
- 펼친 책 양쪽에 미묘한 페이지 컬 효과 (CSS `::after` pseudo element)
- 책등 중앙 라인: 얇은 세로 그림자로 양쪽 페이지 구분
- 페이지 넘길 때 그림자가 자연스럽게 이동
- 현재 페이지 인디케이터 (하단 dot 또는 "3 / 13")

**주의**: cover.jpg는 뒷표지+책등+앞표지 전체가 하나의 가로 이미지.
앞표지만 보여주려면 이미지의 오른쪽 ~48%를 잘라서 표시.

#### 기술 구현
- `framer-motion`의 `AnimatePresence` + `variants`로 플립 애니메이션
- `transform-style: preserve-3d`, `backface-visibility: hidden`
- 페이지 앞/뒤를 별도 div로 구성하여 넘어갈 때 뒷면이 보이는 효과
- 모바일: `onTouchStart`/`onTouchEnd`로 스와이프 감지

### 1-5. 보기 페이지 수정

**파일**: `frontend/src/app/books/[id]/view/page.tsx`

- `BookPreview` 대신 `BookViewer` 사용
- 썸네일이 없으면 "렌더링 중..." 또는 기존 `BookPreview` 폴백

---

## Phase 2: 편집 미리보기 개선 (BookPreview)

### 2-1. 템플릿 좌표 업데이트

현재 `book-preview.tsx`의 하드코딩 좌표를 **최신 템플릿 조회 결과**에 맞춰 업데이트.

**변경된 좌표 (2026-04-07 조회)**:

#### 표지 (CoverPage)
```
기존: front-subtitle (1327, 820), author (1478, 876)
변경: front-subtitle (1327, 850), author (1478, 926)

앞표지 상대좌표 (x-1060 기준):
  사진: (189, 156) 636×636 — 변경 없음
  제목: (267, 850) 479×52 — y: 820→850
  저자: (418, 926) 179×40 — y: 876→926
```

#### 그림 페이지 (IllustPage)
```
photo: (14, 12.4) 900×900 — 변경 없음
pageMargin: spine=25, head=30 — 변경 없음
```

#### 스토리 페이지 (StoryPage)
```
storyText: (114, 62.4) 700×800 — 변경 없음
font: NanumMyeongjo 24px Bold — 변경 없음
```

#### 발행면 (ColophonPage)
```
photo: (50, 277) 293×293 — 변경 없음
title: (50, 600) 652×50 — 변경 없음
info: (50, 650) 350×100 — 변경 없음
logo: (53, 833) 268×47 — 변경 없음
```

### 2-2. 로고 이미지 추가

표지 뒷면과 발행면에 Dreambook 로고 (`/logo.png`) 표시:
- 표지: (372-1060, 950) ≈ 뒷표지 하단 — **미리보기에서는 앞표지만 보이므로 생략 가능**
- 발행면: (53, 833) 268×47

### 2-3. 폰트 매핑

템플릿에서 사용하는 폰트 → 웹 폰트 매핑:

| 템플릿 폰트 | 웹 폰트 | 용도 |
|------------|---------|------|
| tvN 즐거운이야기 Bold | Jua (대체) | 표지 제목, 간지 제목 |
| 나눔바른펜 주아 | Jua | 간지 저자 |
| NanumMyeongjo | Nanum Myeongjo | 스토리 텍스트 |
| NotoSansKR | Noto Sans KR | 표지 저자 |
| 나눔고딕 | Nanum Gothic | 페이지 번호, 발행면 |

**참고**: `tvN 즐거운이야기 Bold`는 웹 폰트로 제공 안 됨 → `Jua`로 대체 중.
실제 인쇄물과 약간 다를 수 있음 (이건 완성 뷰어에서 API 썸네일로 해결).

### 2-4. 스프레드 구성 (현재 구현 확인)

```
[표지] → 단독 1:1
[빈, 간지] → 스프레드
[그림1, 스토리1] ~ [그림11, 스토리11] → 스프레드
[발행면, 빈] → 스프레드
[뒷표지] → 단독 1:1
```

이 구조는 현재 코드에 반영돼있음. 변경 불필요.

---

## Phase 3: DB/모델 변경

### 3-1. Book 모델에 thumbnail 경로 필드 추가

```python
# models/book.py
thumbnail_dir: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
```

또는 별도 테이블:
```python
class BookThumbnail(Base):
    __tablename__ = "book_thumbnails"
    id: ...
    book_id: ForeignKey("books.id")
    page_type: str  # "cover", "page"
    page_num: int   # -1 for cover, 0~23 for pages
    file_path: str
```

**권장**: 단순하게 `book.thumbnail_dir` 필드 하나로 관리.
디렉토리 안에 `cover.jpg`, `0.jpg`~`23.jpg`가 있으면 됨.

---

## 작업 순서

| 순서 | 작업 | 예상 난이도 |
|------|------|-----------|
| 1 | Phase 2-1: BookPreview 좌표 업데이트 | 쉬움 |
| 2 | Phase 2-2: 로고 이미지 추가 | 쉬움 |
| 3 | Phase 1-1: download_thumbnails 서비스 | 보통 |
| 4 | Phase 1-2: 주문 시 자동 다운로드 | 쉬움 |
| 5 | Phase 1-3: 썸네일 조회 API | 쉬움 |
| 6 | Phase 1-4: BookViewer 컴포넌트 | 보통 |
| 7 | Phase 1-5: 보기 페이지 연결 | 쉬움 |
| 8 | Phase 3: DB 변경 | 쉬움 |

---

## 참고 자료

- **템플릿 상세**: `.claude/docs/book-assembly-guide.md` 섹션 6
- **렌더링 API**: `.claude/docs/book-assembly-guide.md` 섹션 12
- **현재 BookPreview 코드**: `frontend/src/components/book-preview.tsx`
- **현재 보기 페이지**: `frontend/src/app/books/[id]/view/page.tsx`
- **템플릿 원본 JSON**: `backend/template_details.json`
