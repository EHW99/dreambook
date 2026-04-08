"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { apiClient, BookListItem } from "@/lib/api";
import { Button } from "@/components/ui/button";
import {
  BookOpenIcon,
  PlusIcon,
  EyeIcon,
  ShoppingCartIcon,
  TrashIcon,
  EditIcon,
  AlertTriangleIcon,
} from "@/components/icons";
import { MoreHorizontal } from "lucide-react";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const STATUS_MAP: Record<string, { label: string; bg: string; text: string }> = {
  draft: { label: "작성중", bg: "bg-warning/80", text: "text-yellow-900" },
  character_confirmed: { label: "작성중", bg: "bg-warning/80", text: "text-yellow-900" },
  story_generated: { label: "편집중", bg: "bg-accent/80", text: "text-teal-900" },
  editing: { label: "편집중", bg: "bg-accent/80", text: "text-teal-900" },
  confirmed: { label: "주문 대기", bg: "bg-primary/80", text: "text-white" },
  completed: { label: "완성", bg: "bg-success/80", text: "text-green-900" },
};

const ART_LABELS: Record<string, string> = {
  watercolor: "수채화", pastel: "파스텔", crayon: "크레파스", "3d": "3D", cartoon: "만화",
};

function coverUrl(path: string | null): string {
  if (!path) return "";
  const filename = path.split(/[/\\]/).pop();
  return `${API_BASE}/uploads/${filename}`;
}

function formatDate(s: string) {
  const d = new Date(s);
  return `${d.getFullYear()}.${String(d.getMonth() + 1).padStart(2, "0")}.${String(d.getDate()).padStart(2, "0")}`;
}

interface BookshelfTabProps {
  orderedBookIds?: Set<number>;
}

export function BookshelfTab({ orderedBookIds = new Set() }: BookshelfTabProps) {
  const router = useRouter();
  const [books, setBooks] = useState<BookListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [deleteTarget, setDeleteTarget] = useState<BookListItem | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);
  const [deleteConfirmText, setDeleteConfirmText] = useState("");
  const [menuOpenId, setMenuOpenId] = useState<number | null>(null);

  const fetchBooks = async () => {
    setLoading(true);
    const result = await apiClient.getBooks();
    if (result.data) setBooks(result.data);
    else setError(result.error || "동화책 목록을 불러오지 못했습니다");
    setLoading(false);
  };

  useEffect(() => { fetchBooks(); }, []);

  const handleDelete = async () => {
    if (!deleteTarget) return;
    setIsDeleting(true);
    const result = await apiClient.deleteBook(deleteTarget.id);
    if (result.error) setError(result.error);
    else setBooks((prev) => prev.filter((b) => b.id !== deleteTarget.id));
    setDeleteTarget(null);
    setDeleteConfirmText("");
    setIsDeleting(false);
  };

  const handleContinue = (book: BookListItem) => {
    if (book.status === "editing" || book.status === "completed") {
      router.push(`/create/edit?book_id=${book.id}`);
    } else {
      router.push(`/create?book_id=${book.id}`);
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-16">
        <div className="w-10 h-10 border-3 border-primary border-t-transparent rounded-full animate-spin" />
        <p className="mt-4 text-sm text-text-light">동화책을 불러오는 중...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center py-16">
        <AlertTriangleIcon className="w-10 h-10 text-error-dark mb-3" />
        <p className="text-sm text-error-dark">{error}</p>
        <Button variant="ghost" className="mt-4" onClick={fetchBooks}>다시 시도</Button>
      </div>
    );
  }

  if (books.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-20">
        <div className="w-20 h-20 rounded-full bg-secondary/50 flex items-center justify-center mb-6">
          <BookOpenIcon className="w-10 h-10 text-primary" />
        </div>
        <p className="text-lg font-medium text-text mb-2">아직 만든 동화책이 없어요</p>
        <p className="text-sm text-text-light mb-6">아이만의 특별한 동화책을 만들어보세요</p>
        <Button onClick={() => router.push("/create")}>
          <PlusIcon className="w-4 h-4 mr-2" />새 동화책 만들기
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
        {books.map((book, i) => {
          const status = STATUS_MAP[book.status] || { label: book.status, bg: "bg-gray-200", text: "text-gray-700" };
          const isDraft = book.status === "draft" || book.status === "character_confirmed";
          const isEditing = book.status === "editing" || book.status === "story_generated";
          const isConfirmed = book.status === "confirmed";
          const isCompleted = book.status === "completed";
          const isOrdered = orderedBookIds.has(book.id);
          const canDelete = true;
          const cover = coverUrl(book.cover_image_path);

          return (
            <motion.div
              key={book.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.05, duration: 0.3 }}
              className="bg-white border border-secondary/60 rounded-2xl overflow-hidden shadow-soft hover:shadow-hover transition-all duration-200 group flex flex-col"
            >
              {/* 표지 (정사각형) */}
              <div className="relative aspect-square overflow-hidden">
                {cover ? (
                  <img
                    src={cover}
                    alt={book.title || "표지"}
                    className="w-full h-full object-cover"
                    crossOrigin="anonymous"
                  />
                ) : (
                  <div className="w-full h-full bg-gradient-to-br from-secondary/40 to-primary/10 flex flex-col items-center justify-center gap-3">
                    <BookOpenIcon className="w-14 h-14 text-primary/30" />
                    <span className="text-xs text-primary/40 font-medium">표지 미생성</span>
                  </div>
                )}

                {/* 상태 배지 — 왼쪽 위 */}
                <div className={`absolute top-3 left-3 text-[11px] font-bold px-2.5 py-0.5 rounded-full backdrop-blur-sm ${
                  isOrdered ? "bg-primary/80 text-white" : `${status.bg} ${status.text}`
                }`}>
                  {isOrdered ? "주문완료" : status.label}
                </div>

                {/* ⋯ 메뉴 — 오른쪽 위 */}
                <div className="absolute top-2 right-2">
                  <button
                    onClick={(e) => { e.stopPropagation(); setMenuOpenId(menuOpenId === book.id ? null : book.id); }}
                    className="w-5 h-5 rounded-full flex items-center justify-center bg-black/25 hover:bg-black/50 text-white backdrop-blur-sm transition-colors"
                  >
                    <MoreHorizontal size={10} />
                  </button>
                  {menuOpenId === book.id && (
                    <>
                      <div className="fixed inset-0 z-40" onClick={() => setMenuOpenId(null)} />
                      <div className="absolute right-0 top-full mt-1 z-50 bg-white border border-secondary/60 rounded-xl shadow-hover py-1 min-w-[120px]">
                        <button
                          onClick={() => { setMenuOpenId(null); setDeleteTarget(book); }}
                          className="w-full flex items-center gap-2 px-3 py-2 text-xs text-error-dark hover:bg-error/10 transition-colors"
                        >
                          <TrashIcon className="w-3.5 h-3.5" />
                          삭제
                        </button>
                      </div>
                    </>
                  )}
                </div>
              </div>

              {/* 정보 */}
              <div className="p-4 flex flex-col flex-1">
                <h3 className="font-bold text-text text-sm truncate mb-1">
                  {book.title || `${book.child_name}의 동화책`}
                </h3>
                <div className="flex items-center gap-2 text-xs text-text-light">
                  {book.job_name && <span>{book.job_name}</span>}
                  {book.job_name && book.art_style && <span className="text-text-lighter">·</span>}
                  {book.art_style && <span>{ART_LABELS[book.art_style] || book.art_style}</span>}
                </div>
                <p className="text-xs text-text-lighter mt-1">
                  {formatDate(book.updated_at || book.created_at)}
                </p>

                {/* 액션 버튼 — 하단 고정 */}
                <div className="flex gap-2 mt-auto pt-3">
                  {isDraft && (
                    <Button size="sm" className="flex-1" onClick={() => handleContinue(book)}>
                      <EditIcon className="w-3.5 h-3.5 mr-1" />이어서 만들기
                    </Button>
                  )}

                  {isEditing && (
                    <Button size="sm" className="flex-1" onClick={() => handleContinue(book)}>
                      <EditIcon className="w-3.5 h-3.5 mr-1" />편집하기
                    </Button>
                  )}

                  {(isConfirmed || isCompleted) && (
                    <Button size="sm" variant="outline" className="flex-1" onClick={() => router.push(`/books/${book.id}/view`)}>
                      <EyeIcon className="w-3.5 h-3.5 mr-1" />보기
                    </Button>
                  )}

                </div>
              </div>
            </motion.div>
          );
        })}

        {/* 새 동화책 만들기 카드 */}
        <motion.button
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: books.length * 0.05, duration: 0.3 }}
          onClick={() => router.push("/create")}
          className="border-2 border-dashed border-secondary hover:border-primary rounded-2xl min-h-[300px] flex flex-col items-center justify-center gap-3 text-text-light hover:text-primary transition-all duration-200 group"
        >
          <div className="w-14 h-14 rounded-full bg-secondary/50 group-hover:bg-primary/10 flex items-center justify-center transition-colors">
            <PlusIcon className="w-7 h-7" />
          </div>
          <span className="text-sm font-medium">새 동화책 만들기</span>
        </motion.button>
      </div>

      {/* 삭제 확인 */}
      <AnimatePresence>
        {deleteTarget && (() => {
          const targetOrdered = orderedBookIds.has(deleteTarget.id);
          return (
            <motion.div
              initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
              className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm"
              onClick={(e) => { if (e.target === e.currentTarget) { setDeleteTarget(null); setDeleteConfirmText(""); } }}
            >
              <motion.div
                initial={{ scale: 0.95, y: 10 }} animate={{ scale: 1, y: 0 }} exit={{ scale: 0.95, y: 10 }}
                className="bg-white rounded-3xl shadow-hover p-7 max-w-sm w-full mx-4"
              >
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-10 h-10 rounded-full bg-error/20 flex items-center justify-center">
                    <TrashIcon className="w-5 h-5 text-error-dark" />
                  </div>
                  <h4 className="text-lg font-bold text-text">동화책 삭제</h4>
                </div>
                <p className="text-sm text-text-light mb-1">
                  <strong>&quot;{deleteTarget.title || `${deleteTarget.child_name}의 동화책`}&quot;</strong>
                </p>
                {targetOrdered ? (
                  <>
                    <div className="bg-error/10 border border-error/20 rounded-xl p-3 my-3">
                      <p className="text-xs text-error-dark font-semibold mb-1">이미 주문된 책입니다</p>
                      <p className="text-xs text-error-dark/80">삭제하면 주문도 함께 취소됩니다. 이 작업은 되돌릴 수 없습니다.</p>
                    </div>
                    <p className="text-xs text-text-light mb-2">확인을 위해 <strong className="text-error-dark">"주문 취소 후 삭제"</strong>를 입력하세요.</p>
                    <input
                      type="text"
                      value={deleteConfirmText}
                      onChange={(e) => setDeleteConfirmText(e.target.value)}
                      placeholder="주문 취소 후 삭제"
                      className="w-full border-2 border-secondary rounded-xl px-3 py-2 text-sm text-center outline-none transition-colors focus:border-error mb-4"
                    />
                  </>
                ) : (
                  <p className="text-sm text-text-light mb-6">삭제하면 복구할 수 없습니다.</p>
                )}
                <div className="flex gap-3">
                  <Button variant="ghost" className="flex-1" onClick={() => { setDeleteTarget(null); setDeleteConfirmText(""); }} disabled={isDeleting}>취소</Button>
                  <Button
                    variant="destructive"
                    className="flex-1"
                    onClick={handleDelete}
                    disabled={isDeleting || (targetOrdered && deleteConfirmText !== "주문 취소 후 삭제")}
                  >
                    {isDeleting ? "삭제 중..." : targetOrdered ? "주문 취소 및 삭제" : "삭제하기"}
                  </Button>
                </div>
              </motion.div>
            </motion.div>
          );
        })()}
      </AnimatePresence>
    </div>
  );
}
