# 셀프체크 — 태스크 9: 편집 / 미리보기 + 책 뷰어

## 테스트 결과
- 전체 테스트 수: 157개 (기존 139 + 신규 18)
- 통과: 157개
- 실패: 0개
- 프론트엔드 빌드: 성공

## SPEC 기능 체크

### 편집 화면
- [x] 페이지 목록 (썸네일 사이드바 — 데스크톱 좌측, 모바일 상단 수평 스크롤)
- [x] 선택된 페이지: 일러스트 + 텍스트 좌우 배치 (md: flex-row)
- [x] 텍스트 인라인 편집 (편집 버튼 → textarea → 저장/취소)
- [x] 스토리 재생성 버튼 (남은 횟수 표시, 최대 3회)
  - [x] Phase 2: 재생성 시 동일 더미 반환, 횟수만 카운트
  - [x] 재생성 시 연쇄 처리: 기존 페이지/이미지 삭제 + 새로 생성 + image_regen_count 리셋
- [x] 페이지별 이미지 재생성 버튼 (남은 횟수 표시, 최대 4회, 갤러리 방식)
- [x] "재생성 횟수를 모두 사용했습니다" 비활성화 + 경고 메시지

### 전체 미리보기 (책 뷰어)
- [x] 페이지 플립 애니메이션 (rotateY 기반 책 넘기기 효과)
- [x] 좌우 페이지 표시 (표지: 단독, 내용: 2장씩 스프레드)
- [x] 전체화면 모드 (Fullscreen API)
- [x] 페이지 네비게이션 (이전/다음 버튼 + 키보드 화살표/스페이스)
- [x] 페이지 인디케이터 (하단 도트)
- [x] 독립 책 뷰어 페이지 (/books/[id]/view)

### 백엔드 API
- [x] `GET /api/books/:id/pages` — 전체 페이지 조회 (기존)
- [x] `PATCH /api/books/:id/pages/:pageId` — 텍스트 수정
- [x] `POST /api/books/:id/regenerate-story` — 스토리 재생성 (더미, 횟수 체크)
- [x] `POST /api/books/:id/pages/:pageId/regenerate-image` — 이미지 재생성 (더미, 횟수)
- [x] `GET /api/books/:id/pages/:pageId/images` — 이미지 갤러리
- [x] `PATCH /api/books/:id/pages/:pageId/images/:imgId/select` — 이미지 선택

### 디자인, 반응형
- [x] 파스텔 톤 색상 팔레트 일관 적용
- [x] 반응형 레이아웃 (모바일/태블릿/데스크톱)
- [x] Framer Motion 애니메이션 (페이지 전환, 모달, 토스트)
- [x] 둥근 모서리 (rounded-2xl, rounded-3xl)
- [x] 따뜻한 동화책 느낌 (ivory 배경, soft 그림자)

## 신규 테스트 목록 (18개)
1. TestPatchPageText::test_update_page_text
2. TestPatchPageText::test_update_page_text_persists
3. TestPatchPageText::test_update_page_text_other_user_forbidden
4. TestPatchPageText::test_update_nonexistent_page
5. TestPatchPageText::test_update_page_empty_text_allowed
6. TestRegenerateStory::test_regenerate_story_success
7. TestRegenerateStory::test_regenerate_story_increments_count
8. TestRegenerateStory::test_regenerate_story_max_3_times
9. TestRegenerateStory::test_regenerate_story_resets_image_regen_counts
10. TestRegenerateStory::test_regenerate_story_other_user_forbidden
11. TestRegenerateImage::test_regenerate_image_success
12. TestRegenerateImage::test_regenerate_image_increments_count
13. TestRegenerateImage::test_regenerate_image_max_4_times
14. TestRegenerateImage::test_regenerate_image_new_selected
15. TestImageGallery::test_get_images
16. TestImageGallery::test_get_images_after_regenerate
17. TestImageSelect::test_select_image
18. TestImageSelect::test_select_nonexistent_image

## 특이사항
- Phase 2이므로 이미지는 placeholder 경로만 저장 (실제 이미지 파일 없음). Phase 3에서 AI 생성으로 교체 예정.
- 스토리 재생성 시 generate_dummy_story를 재사용하여 기존 페이지를 삭제 후 새로 생성. story_regen_count는 API 레이어에서 관리.
- 이미지 갤러리 모달 및 이미지 선택 기능은 Phase 3의 AI 이미지 재생성과 호환되도록 설계.
