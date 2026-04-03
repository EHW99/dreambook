"use client";

import { useState, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { motion } from "framer-motion";
import { BookOpen, ArrowLeft } from "lucide-react";
import { AuthGuard } from "@/components/auth-guard";
import { Button } from "@/components/ui/button";
import { apiClient, BookItem, PageItem } from "@/lib/api";

function EditContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const bookId = searchParams.get("book_id");

  const [book, setBook] = useState<BookItem | null>(null);
  const [pages, setPages] = useState<PageItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

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

    if (bookResult.data) {
      setBook(bookResult.data);
    } else {
      setError("동화책을 불러올 수 없습니다");
    }

    if (pagesResult.data) {
      setPages(pagesResult.data);
    }
    setLoading(false);
  }

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
          <p className="text-error-dark">{error}</p>
          <Button onClick={() => router.push("/mypage")}>마이페이지로</Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      {/* 헤더 */}
      <div className="sticky top-0 z-10 bg-background/90 backdrop-blur-sm border-b border-secondary/30">
        <div className="max-w-4xl mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <button
              onClick={() => router.push("/mypage")}
              className="text-text-light hover:text-text transition-colors"
            >
              <ArrowLeft className="w-5 h-5" />
            </button>
            <h1 className="text-lg font-bold text-text">
              {book?.title || "동화책 편집"}
            </h1>
          </div>
          <div className="flex items-center gap-2">
            <BookOpen className="w-4 h-4 text-primary" />
            <span className="text-sm text-text-light">{pages.length}페이지</span>
          </div>
        </div>
      </div>

      {/* 페이지 목록 */}
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="grid gap-6">
          {pages.map((page, index) => (
            <motion.div
              key={page.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
              className="bg-white rounded-2xl border border-secondary/30 p-6 shadow-sm"
            >
              <div className="flex items-start gap-6">
                {/* 이미지 영역 */}
                <div className="w-40 h-40 bg-secondary/20 rounded-xl flex items-center justify-center flex-shrink-0">
                  {page.images.length > 0 ? (
                    <div className="text-center text-text-lighter text-xs p-2">
                      <BookOpen className="w-8 h-8 mx-auto mb-1 text-primary/40" />
                      일러스트 #{page.page_number}
                    </div>
                  ) : (
                    <span className="text-xs text-text-lighter">이미지 없음</span>
                  )}
                </div>

                {/* 텍스트 영역 */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-2">
                    <span
                      className={`text-xs font-bold px-2 py-0.5 rounded-full ${
                        page.page_type === "title"
                          ? "bg-primary/10 text-primary"
                          : page.page_type === "ending"
                          ? "bg-accent/10 text-accent"
                          : "bg-secondary/30 text-text-light"
                      }`}
                    >
                      {page.page_type === "title"
                        ? "표지"
                        : page.page_type === "ending"
                        ? "엔딩"
                        : `${page.page_number}p`}
                    </span>
                  </div>
                  <p className="text-sm text-text leading-relaxed whitespace-pre-wrap">
                    {page.text_content || "(텍스트 없음)"}
                  </p>
                </div>
              </div>
            </motion.div>
          ))}
        </div>

        {pages.length === 0 && (
          <div className="text-center py-20">
            <BookOpen className="w-12 h-12 mx-auto text-text-lighter mb-4" />
            <p className="text-text-light">아직 생성된 페이지가 없습니다</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default function EditPage() {
  return (
    <AuthGuard>
      <EditContent />
    </AuthGuard>
  );
}
