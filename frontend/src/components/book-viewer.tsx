"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronLeft, ChevronRight, ImageOff } from "lucide-react";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const ACCENT = "#E8836B";
const PAGE_RATIO = 978 / 1000.8;

interface BookViewerProps {
  cover: string | null;
  pages: string[];
  title?: string;
  author?: string;
  compact?: boolean; // 팝업 모드: 버튼 안쪽, 제목 숨김, 높이 축소
}

interface Spread {
  type: "cover" | "spread" | "backcover";
  left: string | null;
  right: string | null;
  label: string;
}

function buildSpreads(cover: string | null, pages: string[]): Spread[] {
  const spreads: Spread[] = [];
  spreads.push({ type: "cover", left: null, right: cover, label: "커버" });
  spreads.push({ type: "spread", left: null, right: pages[0] || null, label: "1" });
  for (let i = 1; i < pages.length - 1; i += 2) {
    spreads.push({
      type: "spread",
      left: pages[i] || null,
      right: pages[i + 1] || null,
      label: `${i + 1}-${i + 2}`,
    });
  }
  if (pages.length >= 24) {
    spreads.push({ type: "spread", left: pages[23] || null, right: null, label: "24" });
  }
  spreads.push({ type: "backcover", left: cover, right: null, label: "뒷표지" });
  return spreads;
}

function imgSrc(path: string | null): string {
  if (!path) return "";
  if (path.startsWith("http")) return path;
  if (path.startsWith("/samples")) return path;
  return `${API_BASE}${path}`;
}

function ImageFallback() {
  return (
    <div className="w-full h-full flex flex-col items-center justify-center gap-2"
      style={{ background: "#f5f2ed" }}>
      <ImageOff size={28} style={{ color: "#ccc" }} />
      <span className="text-xs" style={{ color: "#bbb" }}>이미지 준비 중</span>
    </div>
  );
}

export default function BookViewer({ cover, pages, title, author, compact = false }: BookViewerProps) {
  const [si, setSi] = useState(0);
  const [direction, setDirection] = useState(0);
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

  useEffect(() => {
    const strip = thumbStripRef.current;
    if (!strip) return;
    const active = strip.children[si] as HTMLElement;
    if (active) active.scrollIntoView({ behavior: "smooth", block: "nearest", inline: "center" });
  }, [si]);

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === "ArrowRight" || e.key === " ") { e.preventDefault(); next(); }
      else if (e.key === "ArrowLeft") { e.preventDefault(); prev(); }
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [next, prev]);

  const onTouchStart = (e: React.TouchEvent) => { touchStartX.current = e.touches[0].clientX; };
  const onTouchEnd = (e: React.TouchEvent) => {
    const diff = touchStartX.current - e.changedTouches[0].clientX;
    if (Math.abs(diff) > 50) { diff > 0 ? next() : prev(); }
  };

  const CoverImage = ({ side, alt }: { side: "front" | "back"; alt: string }) => {
    const [hasError, setHasError] = useState(false);
    const src = imgSrc(cover);
    if (!src || hasError) return <ImageFallback />;
    return (
      <div className="w-full h-full overflow-hidden">
        <img src={src} alt={alt} draggable={false} crossOrigin="anonymous"
          className="h-full object-cover" onError={() => setHasError(true)}
          style={{
            width: "200%", maxWidth: "none",
            objectPosition: side === "front" ? "right center" : "left center",
            transform: side === "front" ? "translateX(-50%)" : undefined,
            clipPath: side === "back" ? "inset(0 52% 0 0)" : undefined,
          }}
        />
      </div>
    );
  };

  const PageView = ({ src, position }: { src: string | null; position: "left" | "right" | "single" }) => {
    const [hasError, setHasError] = useState(false);
    const rounded = position === "left" ? "rounded-l-[4px]"
      : position === "right" ? "rounded-r-[4px]" : "rounded-[4px]";
    return (
      <div className={`relative bg-white ${rounded} overflow-hidden`}
        style={{ height: "100%", aspectRatio: `${PAGE_RATIO}` }}
      >
        {src && !hasError ? (
          <img src={imgSrc(src)} alt="" className="w-full h-full object-contain"
            crossOrigin="anonymous" draggable={false} onError={() => setHasError(true)} />
        ) : src && hasError ? (
          <ImageFallback />
        ) : (
          <div className="w-full h-full bg-white" />
        )}
        {position === "left" && (
          <div className="absolute top-0 right-0 bottom-0 w-[15px] pointer-events-none"
            style={{ background: "linear-gradient(to left, rgba(0,0,0,0.12), transparent)" }} />
        )}
        {position === "right" && (
          <div className="absolute top-0 left-0 bottom-0 w-[15px] pointer-events-none"
            style={{ background: "linear-gradient(to right, rgba(0,0,0,0.12), transparent)" }} />
        )}
      </div>
    );
  };

  return (
    <div ref={containerRef}
      className="relative w-full flex flex-col select-none"
      onTouchStart={onTouchStart} onTouchEnd={onTouchEnd}
    >
      <style>{`
        .__bv-thumbs::-webkit-scrollbar { display: none; }
      `}</style>

      {/* Title — 책 바로 위 오른쪽 (compact에서는 숨김) */}
      {!compact && <div className="flex items-center justify-end gap-2 mb-2 px-1">
        {title && (
          <span className="text-xs sm:text-sm font-semibold" style={{ color: ACCENT }}>{title}</span>
        )}
        {author && (
          <span className="text-xs sm:text-sm" style={{ color: "#bbb" }}>by {author} 작가님</span>
        )}
      </div>}

      {/* Book area */}
      <div className="relative flex items-center justify-center">
        {/* Nav — 데스크톱만 */}
        <button onClick={prev} disabled={isFirst}
          className={`hidden md:flex absolute ${compact ? "left-2" : "-left-14"} top-1/2 -translate-y-1/2 z-10 w-11 h-11 rounded-full items-center justify-center border transition-all`}
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
        <button onClick={next} disabled={isLast}
          className={`hidden md:flex absolute ${compact ? "right-2" : "-right-14"} top-1/2 -translate-y-1/2 z-10 w-11 h-11 rounded-full items-center justify-center border transition-all`}
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

        {/* Book */}
        <AnimatePresence mode="wait" custom={direction}>
          <motion.div
            key={si}
            custom={direction}
            initial={{ opacity: 0, x: direction > 0 ? 30 : -30 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: direction > 0 ? -30 : 30 }}
            transition={{ duration: 0.3, ease: [0.4, 0, 0.2, 1] }}
            className="flex items-center justify-center"
            style={{
              /* 높이: 화면 맞춤. 모바일은 vw 기반으로 넘침 방지 */
              height: isSingle
                ? compact ? "min(50vh, 450px)" : "min(65vh, 620px)"
                : compact ? "min(50vh, 450px)" : "min(65vh, 620px)",
              /* 스프레드일 때 width 제한: 2페이지가 화면을 넘지 않게 */
              maxWidth: isSingle ? "min(65vh * 0.977, 606px)" : "100%",
              filter: "drop-shadow(0 4px 24px rgba(0,0,0,0.12)) drop-shadow(0 1px 4px rgba(0,0,0,0.08))",
            }}
          >
            {isSingle ? (
              <div className="h-full rounded-[4px] overflow-hidden bg-white"
                style={{ aspectRatio: `${PAGE_RATIO}` }}
              >
                {cur.type === "cover" ? (
                  <CoverImage side="front" alt="앞표지" />
                ) : (
                  <CoverImage side="back" alt="뒷표지" />
                )}
              </div>
            ) : (
              <div className="flex h-full" style={{ maxWidth: "100%" }}>
                <PageView src={cur.left} position="left" />
                <div className="relative w-[2px] self-stretch flex-shrink-0" style={{ background: "rgba(0,0,0,0.10)" }}>
                  <div className="absolute top-0 bottom-0 -left-[3px] w-[4px] pointer-events-none"
                    style={{ background: "linear-gradient(to right, transparent, rgba(0,0,0,0.04))" }} />
                  <div className="absolute top-0 bottom-0 -right-[3px] w-[4px] pointer-events-none"
                    style={{ background: "linear-gradient(to left, transparent, rgba(0,0,0,0.04))" }} />
                </div>
                <PageView src={cur.right} position="right" />
              </div>
            )}
          </motion.div>
        </AnimatePresence>
      </div>

      {/* Thumbnail strip */}
      <div className={`relative ${compact ? "mt-3" : "mt-6 sm:mt-8"}`}>
        <div className="absolute left-0 top-0 bottom-0 w-8 z-10 pointer-events-none"
          style={{ background: "linear-gradient(to right, white, transparent)" }} />
        <div className="absolute right-0 top-0 bottom-0 w-8 z-10 pointer-events-none"
          style={{ background: "linear-gradient(to left, white, transparent)" }} />

        <div ref={thumbStripRef}
          className="__bv-thumbs flex gap-1.5 overflow-x-auto px-8 pb-1"
          style={{ scrollbarWidth: "none" }}
        >
          {spreads.map((sp, i) => {
            const active = i === si;
            const isSingleThumb = sp.type === "cover" || sp.type === "backcover";
            return (
              <button key={i} onClick={() => goto(i)}
                className="flex-shrink-0 flex flex-col items-center gap-1 bg-transparent border-none cursor-pointer p-0"
              >
                <div className="flex gap-[1px] overflow-hidden transition-all"
                  style={{
                    /* 모바일: 작게, 데스크톱: 크게 — CSS clamp */
                    width: isSingleThumb ? "clamp(48px, 6vw, 72px)" : "clamp(96px, 12vw, 144px)",
                    height: "clamp(46px, 6vw, 70px)",
                    border: active ? `2px solid ${ACCENT}` : "2px solid transparent",
                    borderRadius: 4,
                    opacity: active ? 1 : 0.65,
                  }}
                >
                  {isSingleThumb ? (
                    <div className="w-full h-full bg-[#f0ede8] overflow-hidden">
                      {sp.right && sp.type === "cover" ? (
                        <img src={imgSrc(sp.right)} alt="" className="h-full object-cover"
                          style={{ width: "200%", maxWidth: "none", objectPosition: "right center", transform: "translateX(-50%)" }}
                          crossOrigin="anonymous" draggable={false} />
                      ) : sp.left && sp.type === "backcover" ? (
                        <img src={imgSrc(sp.left)} alt="" className="h-full object-cover"
                          style={{ width: "200%", maxWidth: "none", objectPosition: "left center", clipPath: "inset(0 52% 0 0)" }}
                          crossOrigin="anonymous" draggable={false} />
                      ) : (
                        <div className="w-full h-full bg-[#f0ede8]" />
                      )}
                    </div>
                  ) : (
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
                <span className="text-[10px]" style={{ color: active ? ACCENT : "#aaa" }}>
                  {sp.label}
                </span>
              </button>
            );
          })}
        </div>

        {/* Progress bar */}
        <div className="flex items-center gap-3 mx-4 mt-0.5">
          <div className="flex-1 h-[3px] rounded-full overflow-hidden" style={{ background: "#e8e5e0" }}>
            <motion.div className="h-full rounded-full" style={{ background: ACCENT }}
              animate={{ width: `${progress * 100}%` }}
              transition={{ duration: 0.3, ease: "easeOut" }}
            />
          </div>
          <span className="text-[11px] tabular-nums flex-shrink-0" style={{ color: "#aaa" }}>
            {si + 1} / {spreads.length}
          </span>
        </div>
      </div>
    </div>
  );
}
