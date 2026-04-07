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
  HeadphonesIcon,
  AlertTriangleIcon,
} from "@/components/icons";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const STATUS_MAP: Record<string, { label: string; bg: string; text: string }> = {
  draft: { label: "작성중", bg: "bg-warning/80", text: "text-yellow-900" },
  character_confirmed: { label: "작성중", bg: "bg-warning/80", text: "text-yellow-900" },
  story_generated: { label: "편집중", bg: "bg-accent/80", text: "text-teal-900" },
  generating: { label: "생성중", bg: "bg-accent/80", text: "text-teal-900" },
  editing: { label: "편집중", bg: "bg-accent/80", text: "text-teal-900" },
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
          const isCompleted = book.status === "completed";
          const isOrdered = orderedBookIds.has(book.id);
          const canDelete = isDraft && !isOrdered;
          const cover = coverUrl(book.cover_image_path);

          return (
            <motion.div
              key={book.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.05, duration: 0.3 }}
              className="bg-white border border-secondary/60 rounded-2xl overflow-hidden shadow-soft hover:shadow-hover transition-all duration-200 group"
            >
              {/* 표지 (정사각형) */}
              <div
                className="relative aspect-square overflow-hidden cursor-pointer"
                onClick={() => handleContinue(book)}
              >
                {cover ? (
                  <img
                    src={cover}
                    alt={book.title || "표지"}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                    crossOrigin="anonymous"
                  />
                ) : (
                  <div className="w-full h-full bg-gradient-to-br from-secondary/40 to-primary/10 flex flex-col items-center justify-center gap-3">
                    <BookOpenIcon className="w-14 h-14 text-primary/30" />
                    <span className="text-xs text-primary/40 font-medium">표지 미생성</span>
                  </div>
                )}

                {/* 상태 배지 */}
                <div className={`absolute top-3 right-3 text-[11px] font-bold px-2.5 py-0.5 rounded-full backdrop-blur-sm ${
                  isOrdered ? "bg-primary/80 text-white" : `${status.bg} ${status.text}`
                }`}>
                  {isOrdered ? "주문완료" : status.label}
                </div>
              </div>

              {/* 정보 */}
              <div className="p-4">
                <h3 className="font-bold text-text text-sm truncate mb-1">
                  {book.title || `${book.child_name}의 동화책`}
                </h3>
                <div className="flex items-center gap-2 text-xs text-text-light mb-3">
                  {book.job_name && <span>{book.job_name}</span>}
                  {book.job_name && book.art_style && <span className="text-text-lighter">·</span>}
                  {book.art_style && <span>{ART_LABELS[book.art_style] || book.art_style}</span>}
                </div>
                <p className="text-xs text-text-lighter mb-4">
                  {formatDate(book.updated_at || book.created_at)}
                </p>

                {/* 액션 버튼 */}
                <div className="flex gap-2">
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

                  {isCompleted && !isOrdered && (
                    <>
                      <Button size="sm" variant="outline" className="flex-1" onClick={() => router.push(`/books/${book.id}/view`)}>
                        <EyeIcon className="w-3.5 h-3.5 mr-1" />보기
                      </Button>
                      <Button size="sm" variant="outline" className="flex-1" onClick={() => router.push(`/books/${book.id}/listen`)}>
                        <HeadphonesIcon className="w-3.5 h-3.5 mr-1" />듣기
                      </Button>
                      <Button size="sm" className="flex-1" onClick={() => router.push(`/create/order?bookId=${book.id}`)}>
                        <ShoppingCartIcon className="w-3.5 h-3.5 mr-1" />주문
                      </Button>
                    </>
                  )}

                  {isCompleted && isOrdered && (
                    <>
                      <Button size="sm" variant="outline" className="flex-1" onClick={() => router.push(`/books/${book.id}/view`)}>
                        <EyeIcon className="w-3.5 h-3.5 mr-1" />보기
                      </Button>
                      <Button size="sm" variant="outline" className="flex-1" onClick={() => router.push(`/books/${book.id}/listen`)}>
                        <HeadphonesIcon className="w-3.5 h-3.5 mr-1" />듣기
                      </Button>
                    </>
                  )}

                  {canDelete && (
                    <Button size="sm" variant="ghost" className="text-text-lighter hover:text-error-dark" onClick={() => setDeleteTarget(book)}>
                      <TrashIcon className="w-3.5 h-3.5" />
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
        {deleteTarget && (
          <motion.div
            initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm"
            onClick={(e) => { if (e.target === e.currentTarget) setDeleteTarget(null); }}
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
              <p className="text-sm text-text-light mb-6">삭제하면 복구할 수 없습니다.</p>
              <div className="flex gap-3">
                <Button variant="ghost" className="flex-1" onClick={() => setDeleteTarget(null)} disabled={isDeleting}>취소</Button>
                <Button variant="destructive" className="flex-1" onClick={handleDelete} disabled={isDeleting}>
                  {isDeleting ? "삭제 중..." : "삭제하기"}
                </Button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
