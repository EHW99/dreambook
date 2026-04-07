"use client";

import { useState, useEffect, useCallback } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import {
  BookOpen, ArrowLeft, AlertCircle,
  ImageIcon, CheckCircle, Pencil, X, Check,
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
  const [regeneratingIllust, setRegeneratingIllust] = useState(false);
  const [showConfirmModal, setShowConfirmModal] = useState(false);
  const [confirming, setConfirming] = useState(false);

  // 제목 편집
  const [editingTitle, setEditingTitle] = useState(false);
  const [titleDraft, setTitleDraft] = useState("");

  // 토스트
  const [toast, setToast] = useState<string | null>(null);
  const showToast = useCallback((msg: string) => {
    setToast(msg);
    setTimeout(() => setToast(null), 3000);
  }, []);

  useEffect(() => {
    if (!bookId) {
      router.replace("/bookshelf");
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

    if (bookResult.data) {
      // 확정/완료된 책은 편집 불가 → 뷰어로 이동
      if (bookResult.data.status === "confirmed" || bookResult.data.status === "completed") {
        router.replace(`/books/${id}/view`);
        return;
      }
      setBook(bookResult.data);
    } else {
      setError("동화책을 불러올 수 없습니다");
    }

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

  /* 확정하기 */
  const handleConfirm = async () => {
    if (!book) return;
    setConfirming(true);
    const res = await apiClient.confirmBook(book.id);
    if (res.data) {
      router.replace(`/books/${book.id}/view`);
    } else {
      showToast(res.error || "확정에 실패했습니다");
      setConfirming(false);
      setShowConfirmModal(false);
    }
  };

  /* 제목 저장 */
  const handleTitleSave = async () => {
    if (!book || !titleDraft.trim()) return;
    const res = await apiClient.updateBook(book.id, { title: titleDraft.trim() });
    if (res.data) {
      setBook({ ...book, title: titleDraft.trim() });
      // 간지 page의 text_content도 업데이트
      const titlePage = pages.find(p => p.page_type === "title");
      if (titlePage) {
        await apiClient.updatePageText(book.id, titlePage.id, titleDraft.trim());
        setPages(prev => prev.map(p => p.id === titlePage.id ? { ...p, text_content: titleDraft.trim() } : p));
      }
      setEditingTitle(false);
      showToast("제목이 수정되었습니다");
    } else {
      showToast(res.error || "제목 수정에 실패했습니다");
    }
  };

  /* 일러스트 재생성 */
  const [showRegenModal, setShowRegenModal] = useState(false);

  const handleRegenerateIllust = async () => {
    if (!book) return;
    setShowRegenModal(false);
    setRegeneratingIllust(true);
    const res = await apiClient.generateIllustrations(book.id);
    if (res.data) {
      setPages(res.data.pages);
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
          <Button onClick={() => router.push("/bookshelf")}>내 책장으로</Button>
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
              onClick={() => router.push("/bookshelf")}
              className="text-text-light hover:text-text transition-colors p-1"
            >
              <ArrowLeft className="w-5 h-5" />
            </button>
            <div className="min-w-0">
              {editingTitle ? (
                <div className="flex items-center gap-1.5">
                  <input
                    type="text"
                    value={titleDraft}
                    onChange={(e) => setTitleDraft(e.target.value)}
                    onKeyDown={(e) => { if (e.key === "Enter") handleTitleSave(); if (e.key === "Escape") setEditingTitle(false); }}
                    autoFocus
                    className="text-lg font-bold text-text border-b-2 border-primary outline-none bg-transparent max-w-[50vw] sm:max-w-[300px]"
                  />
                  <button onClick={handleTitleSave} className="p-1 text-primary hover:bg-primary/10 rounded">
                    <Check size={16} />
                  </button>
                  <button onClick={() => setEditingTitle(false)} className="p-1 text-text-lighter hover:bg-secondary/50 rounded">
                    <X size={16} />
                  </button>
                </div>
              ) : (
                <button
                  onClick={() => { setTitleDraft(book.title || ""); setEditingTitle(true); }}
                  className="flex items-center gap-1.5 group text-left"
                >
                  <h1 className="text-lg font-bold text-text truncate max-w-[50vw] sm:max-w-none">
                    {book.title || "동화책 편집"}
                  </h1>
                  <Pencil size={13} className="text-text-lighter opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0" />
                </button>
              )}
              <p className="text-xs text-text-lighter">
                {book.child_name} &middot; {book.job_name}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            {/* 일러스트 재생성 */}
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowRegenModal(true)}
              disabled={regeneratingIllust || (book.illust_regen_count ?? 0) >= 2}
              className="gap-1.5 text-xs hidden sm:flex"
            >
              <ImageIcon className="w-3.5 h-3.5" />
              {regeneratingIllust ? "생성 중..." : `그림 재생성 (${2 - (book.illust_regen_count ?? 0)}회)`}
            </Button>
          </div>
        </div>
      </div>

      {/* 메인: 책 미리보기 */}
      <div className="max-w-6xl mx-auto px-4 py-6">
        {/* 안내 */}
        <div className="text-center mb-4">
          <p className="text-sm text-text-light">
            미리보기입니다. 실제 인쇄 결과와 다소 차이가 있을 수 있습니다. 이야기 텍스트를 클릭하여 편집할 수 있습니다.
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

      </div>

      {/* 하단 고정 CTA — 확정하기 */}
      <div className="sticky bottom-0 z-20 bg-white/95 backdrop-blur-sm border-t border-secondary/30">
        <div className="max-w-6xl mx-auto px-4 py-3 flex items-center gap-3">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowRegenModal(true)}
            disabled={regeneratingIllust || (book.illust_regen_count ?? 0) >= 2}
            className="gap-1.5 text-xs sm:hidden"
          >
            <ImageIcon className="w-3.5 h-3.5" />
            {regeneratingIllust ? "생성중..." : `그림 재생성 (${2 - (book.illust_regen_count ?? 0)}회)`}
          </Button>
          <div className="flex-1" />
          <p className="text-xs text-text-lighter hidden sm:block">편집이 완료되면 확정해주세요</p>
          <Button
            onClick={() => setShowConfirmModal(true)}
            className="gap-2 text-white px-6 h-10 transition-colors"
            style={{ background: "#de7460" }}
            onMouseEnter={(e) => e.currentTarget.style.background = "#c9614e"}
            onMouseLeave={(e) => e.currentTarget.style.background = "#de7460"}
          >
            <CheckCircle className="w-4 h-4" />
            편집 완료 · 확정하기
          </Button>
        </div>
      </div>

      {/* 그림 재생성 확인 모달 */}
      <AnimatePresence>
        {showRegenModal && (
          <motion.div
            initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm"
            onClick={(e) => { if (e.target === e.currentTarget) setShowRegenModal(false); }}
          >
            <motion.div
              initial={{ scale: 0.95, y: 10 }} animate={{ scale: 1, y: 0 }} exit={{ scale: 0.95, y: 10 }}
              className="bg-white rounded-3xl shadow-hover p-7 max-w-sm w-full mx-4"
            >
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-full bg-warning/20 flex items-center justify-center">
                  <ImageIcon className="w-5 h-5 text-warning-dark" />
                </div>
                <h4 className="text-lg font-bold text-text">그림 재생성</h4>
              </div>
              <p className="text-sm text-text-light mb-1">
                전체 일러스트 <strong>11장 + 표지</strong>를 다시 생성합니다.
                캐릭터에 사용된 그림체로 생성됩니다.
              </p>
              <p className="text-sm text-text-light mb-1">
                약 <strong>2~5분</strong>이 소요되며, 기존 그림은 사라집니다.
              </p>
              <p className="text-xs text-text-lighter mt-3 mb-5">
                남은 재생성 횟수: {2 - (book.illust_regen_count ?? 0)}회 / 2회
              </p>
              <div className="flex gap-3">
                <Button variant="ghost" className="flex-1" onClick={() => setShowRegenModal(false)}>취소</Button>
                <Button variant="outline" className="flex-1 gap-1.5" onClick={handleRegenerateIllust}>
                  <ImageIcon className="w-3.5 h-3.5" />
                  재생성하기
                </Button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* 확정 확인 모달 */}
      <AnimatePresence>
        {showConfirmModal && (
          <motion.div
            initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm"
            onClick={(e) => { if (e.target === e.currentTarget && !confirming) setShowConfirmModal(false); }}
          >
            <motion.div
              initial={{ scale: 0.95, y: 10 }} animate={{ scale: 1, y: 0 }} exit={{ scale: 0.95, y: 10 }}
              className="bg-white rounded-3xl shadow-hover p-7 max-w-sm w-full mx-4"
            >
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-full bg-primary/20 flex items-center justify-center">
                  <CheckCircle className="w-5 h-5 text-primary" />
                </div>
                <h4 className="text-lg font-bold text-text">동화책 확정</h4>
              </div>
              <p className="text-sm text-text-light mb-1">
                확정하면 <strong>더 이상 수정할 수 없습니다.</strong>
              </p>
              <p className="text-sm text-text-light mb-6">
                확정 후 뷰어에서 주문할 수 있습니다.
              </p>
              <div className="flex gap-3">
                <Button variant="ghost" className="flex-1" onClick={() => setShowConfirmModal(false)} disabled={confirming}>
                  취소
                </Button>
                <Button className="flex-1 bg-primary hover:bg-primary/90 text-white" onClick={handleConfirm} disabled={confirming}>
                  {confirming ? "확정 중..." : "확정하기"}
                </Button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
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
