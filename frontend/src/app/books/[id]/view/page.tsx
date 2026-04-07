"use client";

import { useState, useEffect } from "react";
import { useRouter, useParams } from "next/navigation";
import { ArrowLeft, BookOpen } from "lucide-react";
import { AuthGuard } from "@/components/auth-guard";
import { Button } from "@/components/ui/button";
import { apiClient, BookItem, PageItem } from "@/lib/api";
import BookPreview from "@/components/book-preview";

function BookViewContent() {
  const router = useRouter();
  const params = useParams();
  const bookId = params?.id ? Number(params.id) : null;

  const [book, setBook] = useState<BookItem | null>(null);
  const [pages, setPages] = useState<PageItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!bookId) return;
    loadData(bookId);
  }, [bookId]);

  async function loadData(id: number) {
    setLoading(true);
    const [bookRes, pagesRes] = await Promise.all([
      apiClient.getBook(id),
      apiClient.getPages(id),
    ]);
    if (bookRes.data) setBook(bookRes.data);
    else setError("동화책을 찾을 수 없습니다");
    if (pagesRes.data) setPages(pagesRes.data);
    setLoading(false);
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#2a2420]">
        <div className="text-center space-y-4">
          <div className="animate-spin w-10 h-10 border-3 border-primary border-t-transparent rounded-full mx-auto" />
          <p className="text-white/60">동화책을 불러오는 중...</p>
        </div>
      </div>
    );
  }

  if (error || !book) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="text-center space-y-4">
          <BookOpen className="w-12 h-12 text-text-lighter mx-auto" />
          <p className="text-error-dark">{error || "동화책을 찾을 수 없습니다"}</p>
          <Button onClick={() => router.push("/mypage")}>마이페이지로</Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background flex flex-col">
      {/* 헤더 */}
      <div className="flex items-center gap-3 px-4 py-3 border-b border-secondary/30">
        <button
          onClick={() => router.back()}
          className="text-text-light hover:text-text transition-colors flex items-center gap-2"
        >
          <ArrowLeft className="w-5 h-5" />
          <span className="text-sm">돌아가기</span>
        </button>
        <h3 className="text-text text-sm font-bold truncate flex-1 text-center">
          {book.title || "동화책"}
        </h3>
        <div className="w-20" />
      </div>

      {/* BookPreview (편집 기능 없이 읽기 전용) */}
      <div className="flex-1 px-4 py-4">
        {pages.length > 0 ? (
          <BookPreview
            pages={pages}
            title={book.title || "동화책"}
            childName={book.child_name}
            coverImageUrl={book.cover_image_path || undefined}
          />
        ) : (
          <div className="flex items-center justify-center py-20">
            <div className="text-center">
              <BookOpen className="w-12 h-12 mx-auto text-text-lighter mb-4" />
              <p className="text-text-light">페이지가 없습니다</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default function BookViewPage() {
  return (
    <AuthGuard>
      <BookViewContent />
    </AuthGuard>
  );
}
