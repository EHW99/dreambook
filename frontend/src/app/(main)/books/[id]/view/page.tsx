"use client";

import { useState, useEffect } from "react";
import { useRouter, useParams } from "next/navigation";
import { ArrowLeft, BookOpen } from "lucide-react";
import { AuthGuard } from "@/components/auth-guard";
import { PageTransition } from "@/components/page-transition";
import { Button } from "@/components/ui/button";
import { apiClient, BookItem, PageItem } from "@/lib/api";
import BookViewer from "@/components/book-viewer";
import BookPreview from "@/components/book-preview";

function BookViewContent() {
  const router = useRouter();
  const params = useParams();
  const bookId = params?.id ? Number(params.id) : null;

  const [book, setBook] = useState<BookItem | null>(null);
  const [pages, setPages] = useState<PageItem[]>([]);
  const [thumbnails, setThumbnails] = useState<{ cover: string | null; pages: string[] } | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!bookId) return;
    loadData(bookId);
  }, [bookId]);

  async function loadData(id: number) {
    setLoading(true);
    const [bookRes, pagesRes, thumbRes] = await Promise.all([
      apiClient.getBook(id),
      apiClient.getPages(id),
      apiClient.getThumbnails(id).catch(() => ({ data: null, error: null })),
    ]);
    if (bookRes.data) setBook(bookRes.data);
    else setError("동화책을 찾을 수 없습니다");
    if (pagesRes.data) setPages(pagesRes.data);
    if (thumbRes.data) setThumbnails(thumbRes.data);
    setLoading(false);
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="text-center space-y-4">
          <div className="animate-spin w-10 h-10 border-3 border-primary border-t-transparent rounded-full mx-auto" />
          <p className="text-text-light">동화책을 불러오는 중...</p>
        </div>
      </div>
    );
  }

  if (error || !book) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="text-center space-y-4">
          <BookOpen className="w-12 h-12 text-text-lighter mx-auto" />
          <p className="text-error-dark">{error || "동화책을 찾을 수 없습니다"}</p>
          <Button onClick={() => router.push("/bookshelf")}>내 책장으로</Button>
        </div>
      </div>
    );
  }

  const hasThumbnails = thumbnails && thumbnails.pages.length > 0;

  return (
    <PageTransition>
      <div className="max-w-7xl mx-auto px-2 sm:px-4 py-4 pb-20 md:pb-4">
        {/* 뒤로가기 */}
        <button
          onClick={() => router.back()}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white border border-secondary hover:border-primary hover:text-primary transition-all shadow-sm mb-4"
        >
          <ArrowLeft size={18} />
          <span className="text-sm font-medium">내 책장</span>
        </button>
        {hasThumbnails ? (
          <BookViewer
            cover={thumbnails.cover}
            pages={thumbnails.pages}
            title={book.title || "동화책"}
            author={book.child_name}
          />
        ) : pages.length > 0 ? (
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
    </PageTransition>
  );
}

export default function BookViewPage() {
  return (
    <AuthGuard>
      <BookViewContent />
    </AuthGuard>
  );
}
