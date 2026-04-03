"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import {
  BookOpen, ArrowLeft, RefreshCw, Eye, Edit3, Check, X,
  ChevronLeft, ChevronRight, Maximize2, Minimize2, ImageIcon,
  Sparkles, AlertCircle,
} from "lucide-react";
import { AuthGuard } from "@/components/auth-guard";
import { Button } from "@/components/ui/button";
import { apiClient, BookItem, PageItem, PageImageItem } from "@/lib/api";

/* ------------------------------------------------------------------ */
/*  편집 화면                                                          */
/* ------------------------------------------------------------------ */
function EditContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const bookId = searchParams.get("book_id");

  const [book, setBook] = useState<BookItem | null>(null);
  const [pages, setPages] = useState<PageItem[]>([]);
  const [selectedPageIdx, setSelectedPageIdx] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // 인라인 편집
  const [editingText, setEditingText] = useState(false);
  const [editText, setEditText] = useState("");
  const [savingText, setSavingText] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // 재생성 로딩
  const [regeneratingStory, setRegeneratingStory] = useState(false);
  const [regeneratingImage, setRegeneratingImage] = useState(false);

  // 이미지 갤러리 모달
  const [galleryOpen, setGalleryOpen] = useState(false);
  const [galleryImages, setGalleryImages] = useState<PageImageItem[]>([]);

  // 책 뷰어
  const [viewerOpen, setViewerOpen] = useState(false);

  // 토스트 메시지
  const [toast, setToast] = useState<string | null>(null);

  const showToast = useCallback((msg: string) => {
    setToast(msg);
    setTimeout(() => setToast(null), 3000);
  }, []);

  useEffect(() => {
    if (!bookId) {
      router.replace("/mypage");
      return;
    }
    loadBookData(Number(bookId));
  }, [bookId]);

  async function loadBookData(id: number) {
    setLoading(true);
    const [bookResult, pagesResult] = await Promise.all([
      apiClient.getBook(id),
      apiClient.getPages(id),
    ]);

    if (bookResult.data) setBook(bookResult.data);
    else setError("동화책을 불러올 수 없습니다");

    if (pagesResult.data) setPages(pagesResult.data);
    setLoading(false);
  }

  const selectedPage = pages[selectedPageIdx] || null;

  const getSelectedImage = (page: PageItem): PageImageItem | null => {
    return page.images.find((img) => img.is_selected) || page.images[0] || null;
  };

  /* 텍스트 편집 */
  const startEditing = () => {
    if (!selectedPage) return;
    setEditText(selectedPage.text_content || "");
    setEditingText(true);
    setTimeout(() => textareaRef.current?.focus(), 100);
  };

  const cancelEditing = () => {
    setEditingText(false);
    setEditText("");
  };

  const saveText = async () => {
    if (!selectedPage || !book) return;
    setSavingText(true);
    const res = await apiClient.updatePageText(book.id, selectedPage.id, editText);
    if (res.data) {
      setPages((prev) =>
        prev.map((p) => (p.id === selectedPage.id ? { ...p, text_content: editText } : p))
      );
      showToast("저장되었습니다");
    } else {
      showToast(res.error || "저장에 실패했습니다");
    }
    setSavingText(false);
    setEditingText(false);
  };

  /* 스토리 재생성 */
  const handleRegenerateStory = async () => {
    if (!book) return;
    if (book.story_regen_count >= 3) {
      showToast("스토리 재생성 횟수를 모두 사용했습니다");
      return;
    }
    setRegeneratingStory(true);
    const res = await apiClient.regenerateStory(book.id);
    if (res.data) {
      setPages(res.data.pages);
      setBook((prev) =>
        prev ? { ...prev, story_regen_count: res.data!.story_regen_count } : prev
      );
      setSelectedPageIdx(0);
      showToast("스토리가 재생성되었습니다");
    } else {
      showToast(res.error || "재생성에 실패했습니다");
    }
    setRegeneratingStory(false);
  };

  /* 이미지 재생성 */
  const handleRegenerateImage = async () => {
    if (!book || !selectedPage) return;
    if (selectedPage.image_regen_count >= 4) {
      showToast("이미지 재생성 횟수를 모두 사용했습니다");
      return;
    }
    setRegeneratingImage(true);
    const res = await apiClient.regenerateImage(book.id, selectedPage.id);
    if (res.data) {
      setPages((prev) =>
        prev.map((p) =>
          p.id === selectedPage.id
            ? { ...p, image_regen_count: res.data!.image_regen_count, images: res.data!.images }
            : p
        )
      );
      showToast("이미지가 재생성되었습니다");
    } else {
      showToast(res.error || "이미지 재생성에 실패했습니다");
    }
    setRegeneratingImage(false);
  };

  /* 이미지 갤러리 열기 */
  const openGallery = async () => {
    if (!book || !selectedPage) return;
    const res = await apiClient.getPageImages(book.id, selectedPage.id);
    if (res.data) {
      setGalleryImages(res.data);
      setGalleryOpen(true);
    }
  };

  /* 이미지 선택 */
  const handleSelectImage = async (imgId: number) => {
    if (!book || !selectedPage) return;
    const res = await apiClient.selectPageImage(book.id, selectedPage.id, imgId);
    if (res.data) {
      setGalleryImages((prev) =>
        prev.map((img) => ({ ...img, is_selected: img.id === imgId }))
      );
      setPages((prev) =>
        prev.map((p) =>
          p.id === selectedPage.id
            ? {
                ...p,
                images: p.images.map((img) => ({
                  ...img,
                  is_selected: img.id === imgId,
                })),
              }
            : p
        )
      );
      showToast("이미지가 선택되었습니다");
    }
  };

  /* 로딩 */
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="text-center space-y-4">
          <div className="animate-spin w-10 h-10 border-3 border-primary border-t-transparent rounded-full mx-auto" />
          <p className="text-text-light">동화책을 불러오는 중...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="text-center space-y-4">
          <AlertCircle className="w-12 h-12 text-error mx-auto" />
          <p className="text-error-dark">{error}</p>
          <Button onClick={() => router.push("/mypage")}>마이페이지로</Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      {/* 토스트 */}
      <AnimatePresence>
        {toast && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="fixed top-4 left-1/2 -translate-x-1/2 z-50 bg-text text-white px-6 py-3 rounded-2xl shadow-hover text-sm"
          >
            {toast}
          </motion.div>
        )}
      </AnimatePresence>

      {/* 헤더 */}
      <div className="sticky top-0 z-10 bg-background/90 backdrop-blur-sm border-b border-secondary/30">
        <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <button
              onClick={() => router.push("/mypage")}
              className="text-text-light hover:text-text transition-colors p-1"
            >
              <ArrowLeft className="w-5 h-5" />
            </button>
            <h1 className="text-lg font-bold text-text truncate max-w-[200px] sm:max-w-none">
              {book?.title || "동화책 편집"}
            </h1>
          </div>
          <div className="flex items-center gap-2">
            {/* 스토리 재생성 */}
            <Button
              variant="outline"
              size="sm"
              onClick={handleRegenerateStory}
              disabled={regeneratingStory || (book?.story_regen_count ?? 0) >= 3}
              className="gap-1.5 text-xs"
            >
              <Sparkles className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">스토리 재생성</span>
              <span className="text-text-lighter">
                ({3 - (book?.story_regen_count ?? 0)}회)
              </span>
            </Button>
            {/* 미리보기 */}
            <Button
              variant="secondary"
              size="sm"
              onClick={() => setViewerOpen(true)}
              className="gap-1.5"
            >
              <Eye className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">미리보기</span>
            </Button>
            {/* 주문하기 */}
            <Button
              size="sm"
              onClick={() => router.push(`/create/order?book_id=${bookId}`)}
              className="gap-1.5 bg-primary hover:bg-primary/90 text-white"
            >
              <BookOpen className="w-3.5 h-3.5" />
              <span>주문하기</span>
            </Button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-6 flex flex-col lg:flex-row gap-6">
        {/* 사이드바: 페이지 썸네일 */}
        <div className="lg:w-48 flex-shrink-0">
          <div className="flex lg:flex-col gap-2 overflow-x-auto lg:overflow-x-visible pb-2 lg:pb-0">
            {pages.map((page, idx) => (
              <button
                key={page.id}
                onClick={() => {
                  setSelectedPageIdx(idx);
                  setEditingText(false);
                }}
                className={`flex-shrink-0 w-28 lg:w-full rounded-xl border-2 transition-all duration-200 overflow-hidden ${
                  idx === selectedPageIdx
                    ? "border-primary shadow-card"
                    : "border-transparent hover:border-secondary"
                }`}
              >
                <div className="aspect-square bg-secondary/20 flex items-center justify-center relative">
                  <BookOpen
                    className={`w-6 h-6 ${
                      idx === selectedPageIdx ? "text-primary" : "text-text-lighter"
                    }`}
                  />
                  <span className="absolute bottom-1 right-1 text-[10px] bg-white/80 px-1.5 py-0.5 rounded-full text-text-light">
                    {page.page_type === "title"
                      ? "표지"
                      : page.page_type === "ending"
                      ? "끝"
                      : `${page.page_number}p`}
                  </span>
                </div>
                <div className="p-1.5">
                  <p className="text-[10px] text-text-light truncate">
                    {page.text_content?.substring(0, 20) || "..."}
                  </p>
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* 메인: 선택된 페이지 */}
        {selectedPage && (
          <motion.div
            key={selectedPage.id}
            initial={{ opacity: 0, x: 10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.2 }}
            className="flex-1 min-w-0"
          >
            <div className="bg-white rounded-3xl shadow-card overflow-hidden">
              <div className="flex flex-col md:flex-row">
                {/* 일러스트 영역 */}
                <div className="md:w-1/2 relative group">
                  <div className="aspect-square bg-gradient-to-br from-secondary/30 to-primary/10 flex items-center justify-center relative">
                    {getSelectedImage(selectedPage) ? (
                      <div className="text-center p-8">
                        <ImageIcon className="w-16 h-16 text-primary/30 mx-auto mb-3" />
                        <p className="text-sm text-text-lighter">
                          일러스트 #{selectedPage.page_number}
                        </p>
                        <p className="text-xs text-text-lighter mt-1">
                          {getSelectedImage(selectedPage)?.image_path}
                        </p>
                      </div>
                    ) : (
                      <div className="text-center p-8">
                        <ImageIcon className="w-12 h-12 text-text-lighter mx-auto mb-2" />
                        <p className="text-sm text-text-lighter">이미지 없음</p>
                      </div>
                    )}

                    {/* 이미지 재생성/갤러리 오버레이 */}
                    <div className="absolute bottom-3 left-3 right-3 flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
                      <Button
                        variant="secondary"
                        size="sm"
                        onClick={handleRegenerateImage}
                        disabled={regeneratingImage || selectedPage.image_regen_count >= 4}
                        className="flex-1 gap-1 text-xs bg-white/90 backdrop-blur-sm"
                      >
                        <RefreshCw className={`w-3 h-3 ${regeneratingImage ? "animate-spin" : ""}`} />
                        재생성 ({4 - selectedPage.image_regen_count}회)
                      </Button>
                      {selectedPage.images.length > 1 && (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={openGallery}
                          className="gap-1 text-xs bg-white/90 backdrop-blur-sm"
                        >
                          <ImageIcon className="w-3 h-3" />
                          갤러리 ({selectedPage.images.length})
                        </Button>
                      )}
                    </div>
                  </div>

                  {/* 이미지 재생성 카운트 (모바일) */}
                  <div className="flex gap-2 p-3 md:hidden">
                    <Button
                      variant="secondary"
                      size="sm"
                      onClick={handleRegenerateImage}
                      disabled={regeneratingImage || selectedPage.image_regen_count >= 4}
                      className="flex-1 gap-1 text-xs"
                    >
                      <RefreshCw className={`w-3 h-3 ${regeneratingImage ? "animate-spin" : ""}`} />
                      이미지 재생성 ({4 - selectedPage.image_regen_count}회)
                    </Button>
                    {selectedPage.images.length > 1 && (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={openGallery}
                        className="gap-1 text-xs"
                      >
                        <ImageIcon className="w-3 h-3" />
                        ({selectedPage.images.length})
                      </Button>
                    )}
                  </div>
                </div>

                {/* 텍스트 영역 */}
                <div className="md:w-1/2 p-6 md:p-8 flex flex-col">
                  <div className="flex items-center justify-between mb-4">
                    <span
                      className={`text-xs font-bold px-3 py-1 rounded-full ${
                        selectedPage.page_type === "title"
                          ? "bg-primary/10 text-primary"
                          : selectedPage.page_type === "ending"
                          ? "bg-accent/10 text-accent-dark"
                          : "bg-secondary/40 text-text-light"
                      }`}
                    >
                      {selectedPage.page_type === "title"
                        ? "표지"
                        : selectedPage.page_type === "ending"
                        ? "엔딩"
                        : `${selectedPage.page_number} 페이지`}
                    </span>
                    {!editingText && (
                      <button
                        onClick={startEditing}
                        className="flex items-center gap-1 text-xs text-text-light hover:text-primary transition-colors"
                      >
                        <Edit3 className="w-3.5 h-3.5" />
                        편집
                      </button>
                    )}
                  </div>

                  {editingText ? (
                    <div className="flex-1 flex flex-col">
                      <textarea
                        ref={textareaRef}
                        value={editText}
                        onChange={(e) => setEditText(e.target.value)}
                        className="flex-1 min-h-[200px] w-full resize-none rounded-xl border border-secondary p-4 text-sm leading-relaxed text-text font-display focus:outline-none focus:ring-2 focus:ring-primary/40 focus:border-primary"
                      />
                      <div className="flex gap-2 mt-3 justify-end">
                        <Button variant="ghost" size="sm" onClick={cancelEditing}>
                          <X className="w-4 h-4 mr-1" />
                          취소
                        </Button>
                        <Button size="sm" onClick={saveText} disabled={savingText}>
                          <Check className="w-4 h-4 mr-1" />
                          {savingText ? "저장 중..." : "저장"}
                        </Button>
                      </div>
                    </div>
                  ) : (
                    <div className="flex-1">
                      <p className="text-sm md:text-base leading-relaxed text-text font-display whitespace-pre-wrap">
                        {selectedPage.text_content || "(텍스트 없음)"}
                      </p>
                    </div>
                  )}

                  {/* 페이지 네비게이션 */}
                  <div className="flex items-center justify-between mt-6 pt-4 border-t border-secondary/30">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => {
                        setSelectedPageIdx(Math.max(0, selectedPageIdx - 1));
                        setEditingText(false);
                      }}
                      disabled={selectedPageIdx === 0}
                    >
                      <ChevronLeft className="w-4 h-4 mr-1" />
                      이전
                    </Button>
                    <span className="text-xs text-text-lighter">
                      {selectedPageIdx + 1} / {pages.length}
                    </span>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => {
                        setSelectedPageIdx(Math.min(pages.length - 1, selectedPageIdx + 1));
                        setEditingText(false);
                      }}
                      disabled={selectedPageIdx === pages.length - 1}
                    >
                      다음
                      <ChevronRight className="w-4 h-4 ml-1" />
                    </Button>
                  </div>
                </div>
              </div>
            </div>

            {/* 재생성 횟수 초과 경고 */}
            {selectedPage.image_regen_count >= 4 && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="mt-3 flex items-center gap-2 text-xs text-warning-dark bg-warning/20 px-4 py-2 rounded-xl"
              >
                <AlertCircle className="w-3.5 h-3.5" />
                이 페이지의 이미지 재생성 횟수를 모두 사용했습니다
              </motion.div>
            )}
            {(book?.story_regen_count ?? 0) >= 3 && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="mt-2 flex items-center gap-2 text-xs text-warning-dark bg-warning/20 px-4 py-2 rounded-xl"
              >
                <AlertCircle className="w-3.5 h-3.5" />
                스토리 재생성 횟수를 모두 사용했습니다
              </motion.div>
            )}
          </motion.div>
        )}

        {pages.length === 0 && (
          <div className="flex-1 flex items-center justify-center py-20">
            <div className="text-center">
              <BookOpen className="w-12 h-12 mx-auto text-text-lighter mb-4" />
              <p className="text-text-light">아직 생성된 페이지가 없습니다</p>
            </div>
          </div>
        )}
      </div>

      {/* 이미지 갤러리 모달 */}
      <AnimatePresence>
        {galleryOpen && selectedPage && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-40 bg-black/50 flex items-center justify-center p-4"
            onClick={() => setGalleryOpen(false)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="bg-white rounded-3xl p-6 max-w-lg w-full max-h-[80vh] overflow-y-auto"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-bold text-text">이미지 갤러리</h3>
                <button
                  onClick={() => setGalleryOpen(false)}
                  className="text-text-lighter hover:text-text p-1"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
              <div className="grid grid-cols-2 gap-3">
                {galleryImages.map((img) => (
                  <button
                    key={img.id}
                    onClick={() => handleSelectImage(img.id)}
                    className={`relative aspect-square rounded-xl overflow-hidden border-2 transition-all ${
                      img.is_selected
                        ? "border-primary shadow-card"
                        : "border-transparent hover:border-secondary"
                    }`}
                  >
                    <div className="w-full h-full bg-gradient-to-br from-secondary/30 to-primary/10 flex items-center justify-center">
                      <ImageIcon className="w-8 h-8 text-primary/30" />
                    </div>
                    {img.is_selected && (
                      <div className="absolute top-2 right-2 bg-primary text-white rounded-full p-1">
                        <Check className="w-3 h-3" />
                      </div>
                    )}
                    <div className="absolute bottom-1 left-1 text-[10px] bg-white/80 px-1.5 py-0.5 rounded-full text-text-light">
                      v{img.generation_index + 1}
                    </div>
                  </button>
                ))}
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* 책 뷰어 모달 */}
      <AnimatePresence>
        {viewerOpen && (
          <BookViewer
            pages={pages}
            title={book?.title || "동화책"}
            onClose={() => setViewerOpen(false)}
          />
        )}
      </AnimatePresence>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  책 뷰어 (페이지 플립)                                               */
/* ------------------------------------------------------------------ */
function BookViewer({
  pages,
  title,
  onClose,
}: {
  pages: PageItem[];
  title: string;
  onClose: () => void;
}) {
  const [currentSpread, setCurrentSpread] = useState(0);
  const [fullscreen, setFullscreen] = useState(false);
  const [direction, setDirection] = useState(0); // -1: 이전, 1: 다음
  const containerRef = useRef<HTMLDivElement>(null);

  // 양면 펼침: [0] → 단독 표지, [1,2], [3,4], ... → 마지막 단독 끝
  const spreads: PageItem[][] = [];
  // 첫 페이지 (표지) 단독
  if (pages.length > 0) spreads.push([pages[0]]);
  // 내용 페이지들 2장씩
  for (let i = 1; i < pages.length; i += 2) {
    if (i + 1 < pages.length) {
      spreads.push([pages[i], pages[i + 1]]);
    } else {
      spreads.push([pages[i]]);
    }
  }

  const totalSpreads = spreads.length;

  const goNext = () => {
    if (currentSpread < totalSpreads - 1) {
      setDirection(1);
      setCurrentSpread((prev) => prev + 1);
    }
  };

  const goPrev = () => {
    if (currentSpread > 0) {
      setDirection(-1);
      setCurrentSpread((prev) => prev - 1);
    }
  };

  const toggleFullscreen = () => {
    if (!fullscreen && containerRef.current) {
      containerRef.current.requestFullscreen?.();
      setFullscreen(true);
    } else {
      document.exitFullscreen?.();
      setFullscreen(false);
    }
  };

  useEffect(() => {
    const handleFs = () => setFullscreen(!!document.fullscreenElement);
    document.addEventListener("fullscreenchange", handleFs);
    return () => document.removeEventListener("fullscreenchange", handleFs);
  }, []);

  // 키보드 네비게이션
  useEffect(() => {
    const handleKey = (e: KeyboardEvent) => {
      if (e.key === "ArrowRight" || e.key === " ") goNext();
      if (e.key === "ArrowLeft") goPrev();
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", handleKey);
    return () => window.removeEventListener("keydown", handleKey);
  }, [currentSpread, totalSpreads]);

  const currentPages = spreads[currentSpread] || [];

  const flipVariants = {
    enter: (dir: number) => ({
      rotateY: dir > 0 ? 90 : -90,
      opacity: 0,
    }),
    center: {
      rotateY: 0,
      opacity: 1,
    },
    exit: (dir: number) => ({
      rotateY: dir > 0 ? -90 : 90,
      opacity: 0,
    }),
  };

  return (
    <motion.div
      ref={containerRef}
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 z-50 bg-[#2a2420] flex flex-col"
    >
      {/* 뷰어 헤더 */}
      <div className="flex items-center justify-between px-4 py-3 bg-black/20">
        <button onClick={onClose} className="text-white/70 hover:text-white transition-colors">
          <X className="w-5 h-5" />
        </button>
        <h3 className="text-white/80 text-sm font-medium truncate mx-4">{title}</h3>
        <div className="flex items-center gap-3">
          <span className="text-white/50 text-xs">
            {currentSpread + 1} / {totalSpreads}
          </span>
          <button onClick={toggleFullscreen} className="text-white/70 hover:text-white transition-colors">
            {fullscreen ? <Minimize2 className="w-4 h-4" /> : <Maximize2 className="w-4 h-4" />}
          </button>
        </div>
      </div>

      {/* 책 본문 */}
      <div className="flex-1 flex items-center justify-center px-4 py-8 relative">
        {/* 이전 버튼 */}
        <button
          onClick={goPrev}
          disabled={currentSpread === 0}
          className="absolute left-2 sm:left-6 z-10 text-white/40 hover:text-white disabled:opacity-20 transition-all p-2"
        >
          <ChevronLeft className="w-8 h-8" />
        </button>

        {/* 페이지 스프레드 */}
        <div className="w-full max-w-4xl" style={{ perspective: "1200px" }}>
          <AnimatePresence mode="wait" custom={direction}>
            <motion.div
              key={currentSpread}
              custom={direction}
              variants={flipVariants}
              initial="enter"
              animate="center"
              exit="exit"
              transition={{ duration: 0.4, ease: "easeInOut" }}
              className={`flex ${
                currentPages.length === 1 ? "justify-center" : ""
              } gap-1 mx-auto`}
              style={{ transformStyle: "preserve-3d" }}
            >
              {currentPages.map((page) => (
                <div
                  key={page.id}
                  className={`bg-[#fef9f1] rounded-lg shadow-2xl overflow-hidden ${
                    currentPages.length === 1 ? "w-full max-w-sm" : "w-1/2"
                  }`}
                >
                  {/* 일러스트 */}
                  <div className="aspect-square bg-gradient-to-br from-secondary/20 to-primary/10 flex items-center justify-center">
                    <div className="text-center p-4">
                      <ImageIcon className="w-12 h-12 text-primary/20 mx-auto mb-2" />
                      <p className="text-xs text-text-lighter">
                        일러스트 #{page.page_number}
                      </p>
                    </div>
                  </div>
                  {/* 텍스트 */}
                  <div className="p-4 sm:p-6">
                    <p className="text-xs sm:text-sm leading-relaxed text-text font-display">
                      {page.text_content}
                    </p>
                  </div>
                </div>
              ))}
            </motion.div>
          </AnimatePresence>
        </div>

        {/* 다음 버튼 */}
        <button
          onClick={goNext}
          disabled={currentSpread === totalSpreads - 1}
          className="absolute right-2 sm:right-6 z-10 text-white/40 hover:text-white disabled:opacity-20 transition-all p-2"
        >
          <ChevronRight className="w-8 h-8" />
        </button>
      </div>

      {/* 하단 페이지 인디케이터 */}
      <div className="flex items-center justify-center gap-1.5 pb-4">
        {spreads.map((_, idx) => (
          <button
            key={idx}
            onClick={() => {
              setDirection(idx > currentSpread ? 1 : -1);
              setCurrentSpread(idx);
            }}
            className={`w-2 h-2 rounded-full transition-all ${
              idx === currentSpread
                ? "bg-primary w-6"
                : "bg-white/30 hover:bg-white/50"
            }`}
          />
        ))}
      </div>
    </motion.div>
  );
}

/* ------------------------------------------------------------------ */
/*  페이지 Export                                                      */
/* ------------------------------------------------------------------ */
export default function EditPage() {
  return (
    <AuthGuard>
      <EditContent />
    </AuthGuard>
  );
}
