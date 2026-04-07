"use client";

import { useState, useEffect, useCallback } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import {
  BookOpen, ArrowLeft, RefreshCw, Eye, Sparkles,
  AlertCircle, ImageIcon, ShoppingCart,
} from "lucide-react";
import { AuthGuard } from "@/components/auth-guard";
import { Button } from "@/components/ui/button";
import { apiClient, BookItem, PageItem } from "@/lib/api";
import BookPreview from "@/components/book-preview";

/* ------------------------------------------------------------------ */
/*  편집 화면 — 실제 인쇄 규격 미리보기 + 인라인 편집                       */
/* ------------------------------------------------------------------ */
function EditContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const bookId = searchParams.get("book_id");

  const [book, setBook] = useState<BookItem | null>(null);
  const [pages, setPages] = useState<PageItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // 재생성 로딩
  const [regeneratingStory, setRegeneratingStory] = useState(false);
  const [regeneratingIllust, setRegeneratingIllust] = useState(false);

  // 토스트
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

  /* 텍스트 저장 */
  const handleTextSave = useCallback(async (pageId: number, text: string) => {
    if (!book) return;
    const res = await apiClient.updatePageText(book.id, pageId, text);
    if (res.data) {
      setPages((prev) =>
        prev.map((p) => (p.id === pageId ? { ...p, text_content: text } : p))
      );
      showToast("저장되었습니다");
    } else {
      showToast(res.error || "저장에 실패했습니다");
    }
  }, [book, showToast]);

  /* 스토리 재생성 */
  const handleRegenerateStory = async () => {
    if (!book) return;
    if (book.story_regen_count >= 3) {
      showToast("스토리 재생성 횟수를 모두 사용했습니다");
      return;
    }
    const confirmed = window.confirm(
      "스토리를 재생성하면 현재 텍스트와 그림이 모두 초기화됩니다.\n재생성 후 일러스트를 다시 생성해야 합니다.\n\n계속하시겠습니까?"
    );
    if (!confirmed) return;
    setRegeneratingStory(true);
    const res = await apiClient.regenerateStory(book.id);
    if (res.data) {
      setPages(res.data.pages);
      setBook((prev) =>
        prev ? { ...prev, story_regen_count: res.data!.story_regen_count } : prev
      );
      showToast("스토리가 재생성되었습니다");
    } else {
      showToast(res.error || "재생성에 실패했습니다");
    }
    setRegeneratingStory(false);
  };

  /* 일러스트 재생성 */
  const handleRegenerateIllust = async () => {
    if (!book) return;
    setRegeneratingIllust(true);
    const res = await apiClient.generateIllustrations(book.id);
    if (res.data) {
      setPages(res.data.pages);
      // book 데이터도 갱신 (cover_image_path 등)
      const bookRes = await apiClient.getBook(book.id);
      if (bookRes.data) setBook(bookRes.data);
      showToast("일러스트가 재생성되었습니다");
    } else {
      showToast(res.error || "일러스트 생성에 실패했습니다");
    }
    setRegeneratingIllust(false);
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

  if (error || !book) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="text-center space-y-4">
          <AlertCircle className="w-12 h-12 text-error mx-auto" />
          <p className="text-error-dark">{error || "오류가 발생했습니다"}</p>
          <Button onClick={() => router.push("/mypage")}>마이페이지로</Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#faf8f5]">
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
      <div className="sticky top-0 z-20 bg-white/90 backdrop-blur-sm border-b border-secondary/30">
        <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <button
              onClick={() => router.push("/mypage")}
              className="text-text-light hover:text-text transition-colors p-1"
            >
              <ArrowLeft className="w-5 h-5" />
            </button>
            <div>
              <h1 className="text-lg font-bold text-text truncate max-w-[55vw] sm:max-w-none">
                {book.title || "동화책 편집"}
              </h1>
              <p className="text-xs text-text-lighter">
                {book.child_name} &middot; {book.job_name}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            {/* 스토리 재생성 */}
            <Button
              variant="outline"
              size="sm"
              onClick={handleRegenerateStory}
              disabled={regeneratingStory || book.story_regen_count >= 3}
              className="gap-1.5 text-xs hidden sm:flex"
            >
              <Sparkles className="w-3.5 h-3.5" />
              스토리 재생성
              <span className="text-text-lighter">
                ({3 - book.story_regen_count}회)
              </span>
            </Button>
            {/* 일러스트 재생성 */}
            <Button
              variant="outline"
              size="sm"
              onClick={handleRegenerateIllust}
              disabled={regeneratingIllust}
              className="gap-1.5 text-xs hidden sm:flex"
            >
              <ImageIcon className="w-3.5 h-3.5" />
              {regeneratingIllust ? "생성 중..." : "그림 재생성"}
            </Button>
            {/* 주문하기 */}
            <Button
              size="sm"
              onClick={() => router.push(`/create/order?book_id=${bookId}`)}
              className="gap-1.5 bg-primary hover:bg-primary/90 text-white"
            >
              <ShoppingCart className="w-3.5 h-3.5" />
              <span>주문하기</span>
            </Button>
          </div>
        </div>
      </div>

      {/* 메인: 책 미리보기 */}
      <div className="max-w-6xl mx-auto px-4 py-6">
        {/* 안내 */}
        <div className="text-center mb-4">
          <p className="text-sm text-text-light">
            실제 인쇄될 모습과 동일한 미리보기입니다. 이야기 텍스트를 클릭하여 편집할 수 있습니다.
          </p>
          <p className="text-xs text-text-lighter mt-1">
            키보드 좌우 화살표 또는 스페이스바로 페이지를 넘길 수 있습니다
          </p>
        </div>

        {/* BookPreview 컴포넌트 */}
        {pages.length > 0 ? (
          <BookPreview
            pages={pages}
            title={book.title || "동화책"}
            childName={book.child_name}
            coverImageUrl={book.cover_image_path || undefined}
            onTextSave={handleTextSave}
          />
        ) : (
          <div className="flex items-center justify-center py-20">
            <div className="text-center">
              <BookOpen className="w-12 h-12 mx-auto text-text-lighter mb-4" />
              <p className="text-text-light">아직 생성된 페이지가 없습니다</p>
            </div>
          </div>
        )}

        {/* 모바일용 하단 버튼 */}
        <div className="flex gap-2 mt-4 sm:hidden">
          <Button
            variant="outline"
            size="sm"
            onClick={handleRegenerateStory}
            disabled={regeneratingStory || book.story_regen_count >= 3}
            className="flex-1 gap-1 text-xs"
          >
            <Sparkles className="w-3.5 h-3.5" />
            스토리 ({3 - book.story_regen_count}회)
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={handleRegenerateIllust}
            disabled={regeneratingIllust}
            className="flex-1 gap-1 text-xs"
          >
            <ImageIcon className="w-3.5 h-3.5" />
            {regeneratingIllust ? "생성중..." : "그림"}
          </Button>
        </div>

        {/* 재생성 횟수 경고 */}
        {book.story_regen_count >= 3 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="mt-3 flex items-center gap-2 text-xs text-warning-dark bg-warning/20 px-4 py-2 rounded-xl justify-center"
          >
            <AlertCircle className="w-3.5 h-3.5" />
            스토리 재생성 횟수를 모두 사용했습니다
          </motion.div>
        )}
      </div>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  Export                                                              */
/* ------------------------------------------------------------------ */
export default function EditPage() {
  return (
    <AuthGuard>
      <EditContent />
    </AuthGuard>
  );
}
