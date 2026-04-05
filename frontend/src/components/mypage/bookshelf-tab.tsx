"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { apiClient, BookListItem } from "@/lib/api";
import { Button } from "@/components/ui/button";
import {
  BookOpenIcon,
  PlusIcon,
  EyeIcon,
  ShoppingCartIcon,
  TrashIcon,
  PlayIcon,
  AlertTriangleIcon,
  EditIcon,
  HeadphonesIcon,
} from "@/components/icons";

const STATUS_LABELS: Record<string, { label: string; color: string }> = {
  draft: { label: "작성중", color: "bg-warning text-yellow-800" },
  character_confirmed: { label: "작성중", color: "bg-warning text-yellow-800" },
  generating: { label: "생성중", color: "bg-accent text-teal-800" },
  editing: { label: "편집중", color: "bg-accent text-teal-800" },
  completed: { label: "완성", color: "bg-success text-green-800" },
};

const ART_STYLE_LABELS: Record<string, string> = {
  watercolor: "수채화",
  pencil: "연필화",
  crayon: "크레파스",
  "3d": "3D",
  cartoon: "만화",
};

function getStatusInfo(status: string) {
  return STATUS_LABELS[status] || { label: status, color: "bg-gray-200 text-gray-700" };
}

function isOrdered(book: BookListItem): boolean {
  // completed 상태면서 주문이 된 경우 — 실제로는 orders 목록과 비교해야 하지만,
  // 간단히 status로 판단. 주문이 된 책은 별도로 표시하기 위해 부모에서 orderedBookIds를 전달.
  return false;
}

function formatDate(dateStr: string) {
  const d = new Date(dateStr);
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
    if (result.data) {
      setBooks(result.data);
    } else {
      setError(result.error || "동화책 목록을 불러오지 못했습니다");
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchBooks();
  }, []);

  const handleDelete = async () => {
    if (!deleteTarget) return;
    setIsDeleting(true);
    const result = await apiClient.deleteBook(deleteTarget.id);
    if (result.error) {
      setError(result.error);
    } else {
      setBooks((prev) => prev.filter((b) => b.id !== deleteTarget.id));
    }
    setDeleteTarget(null);
    setIsDeleting(false);
  };

  const handleContinue = (book: BookListItem) => {
    if (book.status === "editing" || book.status === "completed") {
      // 편집/완성 상태면 편집 페이지로 이동
      router.push(`/create/edit?book_id=${book.id}`);
    } else {
      // draft/character_confirmed 등은 위자드로 이동
      router.push(`/create?book_id=${book.id}`);
    }
  };

  const handleView = (book: BookListItem) => {
    router.push(`/books/${book.id}/view`);
  };

  const handleOrder = (book: BookListItem) => {
    router.push(`/create/order?bookId=${book.id}`);
  };

  const handleListen = (book: BookListItem) => {
    router.push(`/books/${book.id}/listen`);
  };

  const handleCreateNew = () => {
    router.push("/create");
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
        <Button variant="ghost" className="mt-4" onClick={fetchBooks}>
          다시 시도
        </Button>
      </div>
    );
  }

  // 빈 상태
  if (books.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-20">
        <div className="w-20 h-20 rounded-full bg-secondary/50 flex items-center justify-center mb-6">
          <BookOpenIcon className="w-10 h-10 text-primary" />
        </div>
        <p className="text-lg font-medium text-text mb-2">아직 만든 동화책이 없어요</p>
        <p className="text-sm text-text-light mb-6">
          아이만의 특별한 동화책을 만들어보세요
        </p>
        <Button onClick={handleCreateNew}>
          <PlusIcon className="w-4 h-4 mr-2" />
          새 동화책 만들기
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* 책 카드 그리드 */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {books.map((book) => {
          const statusInfo = getStatusInfo(book.status);
          const isDraft = book.status === "draft" || book.status === "character_confirmed";
          const isGenerating = book.status === "generating";
          const isEditing = book.status === "editing";
          const isCompleted = book.status === "completed";
          const isBookOrdered = orderedBookIds.has(book.id);
          const canDelete = isDraft && !isBookOrdered;

          return (
            <div
              key={book.id}
              className="bg-white border border-secondary/60 rounded-2xl overflow-hidden shadow-soft hover:shadow-hover transition-all duration-200 group"
            >
              {/* 썸네일 영역 */}
              <div className="relative h-40 bg-gradient-to-br from-secondary/30 to-primary/10 flex items-center justify-center">
                <BookOpenIcon className="w-16 h-16 text-primary/30" />
                {/* 상태 배지 */}
                <span
                  className={`absolute top-3 right-3 text-xs font-semibold px-2.5 py-1 rounded-full ${
                    isBookOrdered
                      ? "bg-primary/20 text-primary-dark"
                      : statusInfo.color
                  }`}
                >
                  {isBookOrdered ? "주문됨" : statusInfo.label}
                </span>
              </div>

              {/* 정보 */}
              <div className="p-4">
                <h3 className="font-bold text-text text-sm truncate mb-1">
                  {book.title || `${book.child_name}의 동화책`}
                </h3>
                <div className="flex items-center gap-2 text-xs text-text-light mb-3">
                  {book.job_name && <span>{book.job_name}</span>}
                  {book.art_style && (
                    <>
                      <span>·</span>
                      <span>{ART_STYLE_LABELS[book.art_style] || book.art_style}</span>
                    </>
                  )}
                </div>
                <p className="text-xs text-text-lighter mb-4">
                  {formatDate(book.updated_at || book.created_at)}
                </p>

                {/* 액션 버튼 */}
                <div className="flex gap-2">
                  {isDraft && (
                    <Button
                      size="sm"
                      className="flex-1"
                      onClick={() => handleContinue(book)}
                    >
                      <EditIcon className="w-3.5 h-3.5 mr-1" />
                      이어서 만들기
                    </Button>
                  )}

                  {isGenerating && (
                    <div className="flex-1 flex items-center justify-center gap-2 py-2 text-sm text-accent-dark">
                      <div className="w-4 h-4 border-2 border-accent border-t-transparent rounded-full animate-spin" />
                      <span>동화책을 생성하고 있어요...</span>
                    </div>
                  )}

                  {isEditing && (
                    <Button
                      size="sm"
                      className="flex-1"
                      onClick={() => handleContinue(book)}
                    >
                      <EditIcon className="w-3.5 h-3.5 mr-1" />
                      편집하기
                    </Button>
                  )}

                  {isCompleted && !isBookOrdered && (
                    <>
                      <Button
                        size="sm"
                        variant="outline"
                        className="flex-1"
                        onClick={() => handleView(book)}
                      >
                        <EyeIcon className="w-3.5 h-3.5 mr-1" />
                        보기
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        className="flex-1"
                        onClick={() => handleListen(book)}
                      >
                        <HeadphonesIcon className="w-3.5 h-3.5 mr-1" />
                        듣기
                      </Button>
                      <Button
                        size="sm"
                        className="flex-1"
                        onClick={() => handleOrder(book)}
                      >
                        <ShoppingCartIcon className="w-3.5 h-3.5 mr-1" />
                        주문하기
                      </Button>
                    </>
                  )}

                  {isCompleted && isBookOrdered && (
                    <>
                      <Button
                        size="sm"
                        variant="outline"
                        className="flex-1"
                        onClick={() => handleView(book)}
                      >
                        <EyeIcon className="w-3.5 h-3.5 mr-1" />
                        보기
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        className="flex-1"
                        onClick={() => handleListen(book)}
                      >
                        <HeadphonesIcon className="w-3.5 h-3.5 mr-1" />
                        듣기
                      </Button>
                    </>
                  )}

                  {canDelete && (
                    <Button
                      size="sm"
                      variant="ghost"
                      className="text-text-lighter hover:text-error-dark"
                      onClick={() => setDeleteTarget(book)}
                    >
                      <TrashIcon className="w-3.5 h-3.5" />
                    </Button>
                  )}
                </div>
              </div>
            </div>
          );
        })}

        {/* 새 동화책 만들기 카드 */}
        <button
          onClick={handleCreateNew}
          className="border-2 border-dashed border-secondary hover:border-primary rounded-2xl h-full min-h-[240px] flex flex-col items-center justify-center gap-3 text-text-light hover:text-primary transition-all duration-200 group"
        >
          <div className="w-14 h-14 rounded-full bg-secondary/50 group-hover:bg-primary/10 flex items-center justify-center transition-colors">
            <PlusIcon className="w-7 h-7" />
          </div>
          <span className="text-sm font-medium">새 동화책 만들기</span>
        </button>
      </div>

      {/* 삭제 확인 다이얼로그 */}
      {deleteTarget && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
          <div className="bg-white rounded-3xl shadow-hover p-8 max-w-sm w-full mx-4">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 rounded-full bg-error/20 flex items-center justify-center">
                <TrashIcon className="w-5 h-5 text-error-dark" />
              </div>
              <h4 className="text-lg font-bold text-text">동화책 삭제</h4>
            </div>
            <p className="text-sm text-text-light mb-2">
              <strong>&quot;{deleteTarget.title || `${deleteTarget.child_name}의 동화책`}&quot;</strong>
            </p>
            <p className="text-sm text-text-light mb-6">
              이 동화책을 삭제하시겠습니까? 삭제된 동화책은 복구할 수 없습니다.
            </p>
            <div className="flex gap-3">
              <Button
                variant="ghost"
                className="flex-1"
                onClick={() => setDeleteTarget(null)}
                disabled={isDeleting}
              >
                취소
              </Button>
              <Button
                variant="destructive"
                className="flex-1"
                onClick={handleDelete}
                disabled={isDeleting}
              >
                {isDeleting ? "삭제 중..." : "삭제하기"}
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
