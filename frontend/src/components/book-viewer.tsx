"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronLeft, ChevronRight, Maximize, Minimize } from "lucide-react";

/* ================================================================
 *  BookViewer — 완성 책 뷰어
 *
 *  레퍼런스: 스위트북 미리보기 뷰어
 *  - 밝은 배경, 하단 썸네일 스트립
 *  - 제목/저자 표시, 프로그레스 바
 *  - 미묘한 종이 그림자/질감
 *
 *  cover.jpg: 뒷표지+책등+앞표지 전체 (가로형)
 *  0.jpg~23.jpg: 내지 24페이지
 * ================================================================ */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface BookViewerProps {
  cover: string | null;
  pages: string[];
  title?: string;
  author?: string;
}

interface Spread {
  type: "cover" | "spread" | "backcover";
  left: string | null;
  right: string | null;
  label: string;
}

function buildSpreads(cover: string | null, pages: string[]): Spread[] {
  const spreads: Spread[] = [];

  // 표지 (단독)
  spreads.push({ type: "cover", left: null, right: cover, label: "커버" });

  // [빈, 간지(0.jpg)]
  spreads.push({ type: "spread", left: null, right: pages[0] || null, label: "1" });

  // [그림, 스토리] 쌍: 1+2, 3+4, ..., 21+22
  for (let i = 1; i < pages.length - 1; i += 2) {
    const left = pages[i] || null;
    const right = pages[i + 1] || null;
    const startPage = i + 1;
    const endPage = i + 2;
    spreads.push({ type: "spread", left, right, label: `${startPage}-${endPage}` });
  }

  // [발행면(23.jpg), 빈]
  if (pages.length >= 24) {
    spreads.push({ type: "spread", left: pages[23] || null, right: null, label: "24" });
  }

  // 뒷표지 (단독)
  spreads.push({ type: "backcover", left: cover, right: null, label: "뒷표지" });

  return spreads;
}

function imgSrc(path: string | null): string {
  if (!path) return "";
  if (path.startsWith("http")) return path;
  return `${API_BASE}${path}`;
}

export default function BookViewer({ cover, pages, title, author }: BookViewerProps) {
  const [si, setSi] = useState(0);
  const [direction, setDirection] = useState(0);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);
  const thumbStripRef = useRef<HTMLDivElement>(null);
  const touchStartX = useRef(0);

  const spreads = buildSpreads(cover, pages);
  const cur = spreads[si];
  const isFirst = si === 0;
  const isLast = si === spreads.length - 1;
  const isSingle = cur.type === "cover" || cur.type === "backcover";
  const progress = spreads.length > 1 ? si / (spreads.length - 1) : 0;

  const goto = useCallback((idx: number) => {
    setDirection(idx > si ? 1 : -1);
    setSi(idx);
  }, [si]);

  const next = useCallback(() => {
    if (si < spreads.length - 1) goto(si + 1);
  }, [si, spreads.length, goto]);

  const prev = useCallback(() => {
    if (si > 0) goto(si - 1);
  }, [si, goto]);

  // Scroll active thumbnail into view
  useEffect(() => {
    const strip = thumbStripRef.current;
    if (!strip) return;
    const active = strip.children[si] as HTMLElement;
    if (active) {
      active.scrollIntoView({ behavior: "smooth", block: "nearest", inline: "center" });
    }
  }, [si]);

  // Keyboard
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === "ArrowRight" || e.key === " ") { e.preventDefault(); next(); }
      else if (e.key === "ArrowLeft") { e.preventDefault(); prev(); }
      else if (e.key === "Escape" && isFullscreen) setIsFullscreen(false);
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [next, prev, isFullscreen]);

  // Touch swipe
  const onTouchStart = (e: React.TouchEvent) => { touchStartX.current = e.touches[0].clientX; };
  const onTouchEnd = (e: React.TouchEvent) => {
    const diff = touchStartX.current - e.changedTouches[0].clientX;
    if (Math.abs(diff) > 50) { diff > 0 ? next() : prev(); }
  };

  // Fullscreen
  const toggleFullscreen = () => {
    if (!isFullscreen) containerRef.current?.requestFullscreen?.();
    else document.exitFullscreen?.();
  };
  useEffect(() => {
    const handler = () => setIsFullscreen(!!document.fullscreenElement);
    document.addEventListener("fullscreenchange", handler);
    return () => document.removeEventListener("fullscreenchange", handler);
  }, []);

  // Cover image cropping helper
  const CoverImage = ({ side, alt }: { side: "front" | "back"; alt: string }) => {
    const src = imgSrc(cover);
    if (!src) return <div className="w-full h-full bg-[#FFF8F0]" />;
    return (
      <div className="w-full h-full overflow-hidden">
        <img
          src={src} alt={alt} draggable={false} crossOrigin="anonymous"
          className="h-full object-cover"
          style={{
            width: "200%", maxWidth: "none",
            objectPosition: side === "front" ? "right center" : "left center",
            transform: side === "front" ? "translateX(-50%)" : undefined,
          }}
        />
      </div>
    );
  };

  // Page component with paper effect
  const Page = ({ src, position }: { src: string | null; position: "left" | "right" | "single" }) => {
    const roundedClass = position === "left" ? "rounded-l-[3px]"
      : position === "right" ? "rounded-r-[3px]"
      : "rounded-[3px]";

    return (
      <div className={`relative bg-white ${roundedClass} overflow-hidden`}
        style={{
          width: isSingle ? "min(42vw, 400px)" : "min(36vw, 340px)",
          aspectRatio: isSingle ? "978/1000.8" : "978/1000.8",
        }}
      >
        {src ? (
          <img src={imgSrc(src)} alt="" className="w-full h-full object-contain"
            crossOrigin="anonymous" draggable={false} />
        ) : (
          <div className="w-full h-full bg-white" />
        )}
        {/* Inner spine shadow */}
        {position === "left" && (
          <div className="absolute top-0 right-0 bottom-0 w-8 pointer-events-none"
            style={{ background: "linear-gradient(to left, rgba(0,0,0,0.06), transparent)" }} />
        )}
        {position === "right" && (
          <div className="absolute top-0 left-0 bottom-0 w-8 pointer-events-none"
            style={{ background: "linear-gradient(to right, rgba(0,0,0,0.06), transparent)" }} />
        )}
      </div>
    );
  };

  return (
    <div ref={containerRef}
      className="relative w-full flex flex-col select-none"
      style={{
        background: isFullscreen ? "#f5f3f0" : "transparent",
        borderRadius: isFullscreen ? 0 : 16,
        height: isFullscreen ? "100vh" : "auto",
      }}
      onTouchStart={onTouchStart} onTouchEnd={onTouchEnd}
    >
      {/* Main viewer area */}
      <div className="relative flex items-center justify-center"
        style={{
          background: "#f5f3f0",
          borderRadius: 16,
          minHeight: "min(70vh, 560px)",
          padding: "40px 60px",
        }}
      >
        {/* Fullscreen button */}
        <button onClick={toggleFullscreen}
          className="absolute top-3 right-3 z-10 w-8 h-8 rounded-full flex items-center justify-center border-none cursor-pointer transition-all hover:bg-black/10"
          style={{ background: "rgba(0,0,0,0.04)", color: "#999" }}
        >
          {isFullscreen ? <Minimize size={15} /> : <Maximize size={15} />}
        </button>

        {/* Prev button */}
        <button onClick={prev} disabled={isFirst}
          className="absolute left-4 top-1/2 -translate-y-1/2 z-10 w-11 h-11 rounded-full flex items-center justify-center border transition-all"
          style={{
            background: "white",
            borderColor: isFirst ? "transparent" : "#e0dcd8",
            color: isFirst ? "#ddd" : "#888",
            cursor: isFirst ? "default" : "pointer",
            boxShadow: isFirst ? "none" : "0 2px 8px rgba(0,0,0,0.06)",
          }}
        >
          <ChevronLeft size={20} />
        </button>

        {/* Next button */}
        <button onClick={next} disabled={isLast}
          className="absolute right-4 top-1/2 -translate-y-1/2 z-10 w-11 h-11 rounded-full flex items-center justify-center border transition-all"
          style={{
            background: "white",
            borderColor: isLast ? "transparent" : "#e0dcd8",
            color: isLast ? "#ddd" : "#888",
            cursor: isLast ? "default" : "pointer",
            boxShadow: isLast ? "none" : "0 2px 8px rgba(0,0,0,0.06)",
          }}
        >
          <ChevronRight size={20} />
        </button>

        {/* Book display */}
        <AnimatePresence mode="wait" custom={direction}>
          <motion.div
            key={si}
            custom={direction}
            initial={{ opacity: 0, x: direction > 0 ? 40 : -40 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: direction > 0 ? -40 : 40 }}
            transition={{ duration: 0.35, ease: [0.4, 0, 0.2, 1] }}
            className="flex"
            style={{
              filter: "drop-shadow(0 4px 20px rgba(0,0,0,0.1)) drop-shadow(0 12px 40px rgba(0,0,0,0.06))",
            }}
          >
            {isSingle ? (
              /* Single page: Cover or Back Cover */
              <div className="relative rounded-[3px] overflow-hidden bg-white"
                style={{
                  width: "min(42vw, 400px)",
                  aspectRatio: "978/1000.8",
                }}
              >
                {cur.type === "cover" ? (
                  <CoverImage side="front" alt="앞표지" />
                ) : (
                  <CoverImage side="back" alt="뒷표지" />
                )}
              </div>
            ) : (
              /* Spread: Two pages */
              <div className="flex">
                <Page src={cur.left} position="left" />
                {/* Spine */}
                <div className="w-[1px] self-stretch" style={{ background: "rgba(0,0,0,0.08)" }} />
                <Page src={cur.right} position="right" />
              </div>
            )}
          </motion.div>
        </AnimatePresence>
      </div>

      {/* Title + Author */}
      <div className="flex items-center justify-center gap-3 py-4">
        {title && (
          <span className="text-sm font-semibold" style={{ color: "#E8836B" }}>
            {title}
          </span>
        )}
        {author && (
          <span className="text-sm" style={{ color: "#999" }}>
            by {author} 작가님
          </span>
        )}
      </div>

      {/* Thumbnail strip */}
      <div className="relative">
        <div ref={thumbStripRef}
          className="flex gap-2 overflow-x-auto px-4 pb-2 justify-center"
          style={{ scrollbarWidth: "none" }}
        >
          <style>{`
            .__bv-thumbs::-webkit-scrollbar { display: none; }
          `}</style>
          {spreads.map((sp, i) => {
            const active = i === si;
            const isSingleThumb = sp.type === "cover" || sp.type === "backcover";

            return (
              <button key={i} onClick={() => goto(i)}
                className="flex-shrink-0 flex flex-col items-center gap-1 bg-transparent border-none cursor-pointer p-0"
              >
                {/* Thumbnail image */}
                <div className="flex gap-[1px] rounded overflow-hidden transition-all"
                  style={{
                    width: isSingleThumb ? 60 : 110,
                    height: 56,
                    border: active ? "2px solid #7B61FF" : "2px solid transparent",
                    borderRadius: 4,
                    opacity: active ? 1 : 0.7,
                  }}
                >
                  {isSingleThumb ? (
                    /* Single thumbnail */
                    <div className="w-full h-full bg-[#f0ede8] overflow-hidden">
                      {sp.right && sp.type === "cover" ? (
                        <img src={imgSrc(sp.right)} alt="" className="h-full object-cover"
                          style={{ width: "200%", maxWidth: "none", objectPosition: "right center", transform: "translateX(-50%)" }}
                          crossOrigin="anonymous" draggable={false} />
                      ) : sp.left && sp.type === "backcover" ? (
                        <img src={imgSrc(sp.left)} alt="" className="h-full object-cover"
                          style={{ width: "200%", maxWidth: "none", objectPosition: "left center" }}
                          crossOrigin="anonymous" draggable={false} />
                      ) : (
                        <div className="w-full h-full bg-[#f0ede8]" />
                      )}
                    </div>
                  ) : (
                    /* Spread thumbnail */
                    <>
                      <div className="flex-1 h-full bg-[#f0ede8] overflow-hidden">
                        {sp.left ? (
                          <img src={imgSrc(sp.left)} alt="" className="w-full h-full object-cover"
                            crossOrigin="anonymous" draggable={false} />
                        ) : <div className="w-full h-full bg-white" />}
                      </div>
                      <div className="flex-1 h-full bg-[#f0ede8] overflow-hidden">
                        {sp.right ? (
                          <img src={imgSrc(sp.right)} alt="" className="w-full h-full object-cover"
                            crossOrigin="anonymous" draggable={false} />
                        ) : <div className="w-full h-full bg-white" />}
                      </div>
                    </>
                  )}
                </div>
                {/* Label */}
                <span className="text-[10px] transition-colors"
                  style={{ color: active ? "#7B61FF" : "#aaa" }}
                >
                  {sp.label}
                </span>
              </button>
            );
          })}
        </div>

        {/* Progress bar */}
        <div className="h-[3px] mx-4 mt-1 mb-1 rounded-full overflow-hidden" style={{ background: "#e8e5e0" }}>
          <motion.div
            className="h-full rounded-full"
            style={{ background: "#7B61FF" }}
            animate={{ width: `${progress * 100}%` }}
            transition={{ duration: 0.3, ease: "easeOut" }}
          />
        </div>
      </div>
    </div>
  );
}
