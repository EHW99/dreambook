"use client";

import { useState, useEffect, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { X, ChevronLeft, ChevronRight } from "lucide-react";

interface PhotoLightboxProps {
  images: { src: string; alt?: string }[];
  initialIndex: number;
  onClose: () => void;
}

export function PhotoLightbox({ images, initialIndex, onClose }: PhotoLightboxProps) {
  const [currentIndex, setCurrentIndex] = useState(initialIndex);

  const hasMultiple = images.length > 1;

  const goNext = useCallback(() => {
    if (!hasMultiple) return;
    setCurrentIndex((prev) => (prev + 1) % images.length);
  }, [hasMultiple, images.length]);

  const goPrev = useCallback(() => {
    if (!hasMultiple) return;
    setCurrentIndex((prev) => (prev - 1 + images.length) % images.length);
  }, [hasMultiple, images.length]);

  // 키보드 이벤트
  useEffect(() => {
    function handleKeyDown(e: KeyboardEvent) {
      if (e.key === "Escape") onClose();
      else if (e.key === "ArrowRight") goNext();
      else if (e.key === "ArrowLeft") goPrev();
    }
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [onClose, goNext, goPrev]);

  // body 스크롤 방지
  useEffect(() => {
    const prev = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => {
      document.body.style.overflow = prev;
    };
  }, []);

  const current = images[currentIndex];
  if (!current) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        transition={{ duration: 0.2 }}
        className="fixed inset-0 z-[100] flex items-center justify-center"
        onClick={onClose}
      >
        {/* 배경 오버레이 */}
        <div className="absolute inset-0 bg-black/85 backdrop-blur-sm" />

        {/* 상단 컨트롤 바 */}
        <div className="absolute top-0 left-0 right-0 z-10 flex items-center justify-between px-4 py-3 sm:px-6 sm:py-4">
          {/* 카운터 */}
          {hasMultiple && (
            <span className="text-white/70 text-sm font-medium tracking-wide">
              {currentIndex + 1} / {images.length}
            </span>
          )}
          {!hasMultiple && <span />}

          {/* 닫기 버튼 */}
          <button
            onClick={(e) => {
              e.stopPropagation();
              onClose();
            }}
            className="w-10 h-10 rounded-full bg-white/10 hover:bg-white/20 flex items-center justify-center text-white transition-colors"
            title="닫기 (ESC)"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* 좌측 화살표 */}
        {hasMultiple && (
          <button
            onClick={(e) => {
              e.stopPropagation();
              goPrev();
            }}
            className="absolute left-2 sm:left-4 top-1/2 -translate-y-1/2 z-10 w-11 h-11 rounded-full bg-white/10 hover:bg-white/25 flex items-center justify-center text-white transition-colors"
          >
            <ChevronLeft className="w-6 h-6" />
          </button>
        )}

        {/* 우측 화살표 */}
        {hasMultiple && (
          <button
            onClick={(e) => {
              e.stopPropagation();
              goNext();
            }}
            className="absolute right-2 sm:right-4 top-1/2 -translate-y-1/2 z-10 w-11 h-11 rounded-full bg-white/10 hover:bg-white/25 flex items-center justify-center text-white transition-colors"
          >
            <ChevronRight className="w-6 h-6" />
          </button>
        )}

        {/* 이미지 */}
        <motion.div
          key={currentIndex}
          initial={{ opacity: 0, scale: 0.92 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.92 }}
          transition={{ duration: 0.2, ease: "easeOut" }}
          className="relative z-[1] flex items-center justify-center px-12 sm:px-20"
          style={{ maxWidth: "100vw", maxHeight: "100vh" }}
          onClick={(e) => e.stopPropagation()}
        >
          <img
            src={current.src}
            alt={current.alt || "사진"}
            draggable={false}
            className="select-none rounded-lg shadow-2xl max-w-[85vw] max-h-[80vh] object-contain"
          />
        </motion.div>

        {/* 하단 썸네일 스트립 (5장 이상이면 표시) */}
        {hasMultiple && images.length >= 3 && (
          <div className="absolute bottom-0 left-0 right-0 z-10 pb-4 pt-8 bg-gradient-to-t from-black/50 to-transparent">
            <div className="flex items-center justify-center gap-2 px-4 overflow-x-auto no-scrollbar">
              {images.map((img, idx) => (
                <button
                  key={idx}
                  onClick={(e) => {
                    e.stopPropagation();
                    setCurrentIndex(idx);
                  }}
                  className={`
                    flex-shrink-0 w-12 h-12 sm:w-14 sm:h-14 rounded-lg overflow-hidden border-2 transition-all
                    ${idx === currentIndex
                      ? "border-white ring-1 ring-white/30 opacity-100 scale-105"
                      : "border-transparent opacity-50 hover:opacity-80"
                    }
                  `}
                >
                  <img
                    src={img.src}
                    alt=""
                    className="w-full h-full object-cover"
                    draggable={false}
                  />
                </button>
              ))}
            </div>
          </div>
        )}
      </motion.div>
    </AnimatePresence>
  );
}
