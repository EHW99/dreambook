"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { useRouter, useParams } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import {
  ChevronLeft, ChevronRight, X, Maximize2, Minimize2,
  ImageIcon, ArrowLeft, BookOpen,
} from "lucide-react";
import { AuthGuard } from "@/components/auth-guard";
import { Button } from "@/components/ui/button";
import { apiClient, BookItem, PageItem } from "@/lib/api";

function BookViewContent() {
  const router = useRouter();
  const params = useParams();
  const bookId = params?.id ? Number(params.id) : null;

  const [book, setBook] = useState<BookItem | null>(null);
  const [pages, setPages] = useState<PageItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [currentSpread, setCurrentSpread] = useState(0);
  const [fullscreen, setFullscreen] = useState(false);
  const [direction, setDirection] = useState(0);
  const containerRef = useRef<HTMLDivElement>(null);

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

  // 양면 펼침
  const spreads: PageItem[][] = [];
  if (pages.length > 0) spreads.push([pages[0]]);
  for (let i = 1; i < pages.length; i += 2) {
    if (i + 1 < pages.length) spreads.push([pages[i], pages[i + 1]]);
    else spreads.push([pages[i]]);
  }
  const totalSpreads = spreads.length;

  const goNext = useCallback(() => {
    if (currentSpread < totalSpreads - 1) {
      setDirection(1);
      setCurrentSpread((p) => p + 1);
    }
  }, [currentSpread, totalSpreads]);

  const goPrev = useCallback(() => {
    if (currentSpread > 0) {
      setDirection(-1);
      setCurrentSpread((p) => p - 1);
    }
  }, [currentSpread]);

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
    const h = () => setFullscreen(!!document.fullscreenElement);
    document.addEventListener("fullscreenchange", h);
    return () => document.removeEventListener("fullscreenchange", h);
  }, []);

  useEffect(() => {
    const h = (e: KeyboardEvent) => {
      if (e.key === "ArrowRight" || e.key === " ") goNext();
      if (e.key === "ArrowLeft") goPrev();
      if (e.key === "Escape" && fullscreen) {
        document.exitFullscreen?.();
      }
    };
    window.addEventListener("keydown", h);
    return () => window.removeEventListener("keydown", h);
  }, [goNext, goPrev, fullscreen]);

  const flipVariants = {
    enter: (dir: number) => ({ rotateY: dir > 0 ? 90 : -90, opacity: 0 }),
    center: { rotateY: 0, opacity: 1 },
    exit: (dir: number) => ({ rotateY: dir > 0 ? -90 : 90, opacity: 0 }),
  };

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

  const currentPages = spreads[currentSpread] || [];

  return (
    <div
      ref={containerRef}
      className="min-h-screen bg-[#2a2420] flex flex-col"
    >
      {/* 헤더 */}
      <div className="flex items-center justify-between px-4 py-3 bg-black/20">
        <button
          onClick={() => router.back()}
          className="text-white/70 hover:text-white transition-colors flex items-center gap-2"
        >
          <ArrowLeft className="w-5 h-5" />
          <span className="text-sm hidden sm:inline">돌아가기</span>
        </button>
        <h3 className="text-white/80 text-sm font-medium truncate mx-4">
          {book.title || "동화책"}
        </h3>
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
        <button
          onClick={goPrev}
          disabled={currentSpread === 0}
          className="absolute left-2 sm:left-6 z-10 text-white/40 hover:text-white disabled:opacity-20 transition-all p-2"
        >
          <ChevronLeft className="w-8 h-8" />
        </button>

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
              className={`flex ${currentPages.length === 1 ? "justify-center" : ""} gap-1 mx-auto`}
              style={{ transformStyle: "preserve-3d" }}
            >
              {currentPages.map((page) => (
                <div
                  key={page.id}
                  className={`bg-[#fef9f1] rounded-lg shadow-2xl overflow-hidden ${
                    currentPages.length === 1 ? "w-full max-w-sm" : "w-1/2"
                  }`}
                >
                  <div className="aspect-square bg-gradient-to-br from-secondary/20 to-primary/10 flex items-center justify-center">
                    <div className="text-center p-4">
                      <ImageIcon className="w-12 h-12 text-primary/20 mx-auto mb-2" />
                      <p className="text-xs text-text-lighter">
                        일러스트 #{page.page_number}
                      </p>
                    </div>
                  </div>
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

        <button
          onClick={goNext}
          disabled={currentSpread === totalSpreads - 1}
          className="absolute right-2 sm:right-6 z-10 text-white/40 hover:text-white disabled:opacity-20 transition-all p-2"
        >
          <ChevronRight className="w-8 h-8" />
        </button>
      </div>

      {/* 페이지 인디케이터 */}
      <div className="flex items-center justify-center gap-1.5 pb-4">
        {spreads.map((_, idx) => (
          <button
            key={idx}
            onClick={() => {
              setDirection(idx > currentSpread ? 1 : -1);
              setCurrentSpread(idx);
            }}
            className={`w-2 h-2 rounded-full transition-all ${
              idx === currentSpread ? "bg-primary w-6" : "bg-white/30 hover:bg-white/50"
            }`}
          />
        ))}
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
