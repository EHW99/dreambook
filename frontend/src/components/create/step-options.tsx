"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { BookOpen, Ruler, DollarSign } from "lucide-react";
import { apiClient, BookSpecItem } from "@/lib/api";

interface StepOptionsProps {
  pageCount: number;
  bookSpecUid: string;
  onPageCountChange: (count: number) => void;
  onBookSpecChange: (uid: string) => void;
}

function getEstimatedPrice(spec: BookSpecItem, pageCount: number): number {
  // 간이 가격 계산 (판형별 기본가 + 페이지당 추가)
  const priceMap: Record<string, { base: number; perPage: number }> = {
    SQUAREBOOK_HC: { base: 15000, perPage: 200 },
    PHOTOBOOK_A4_SC: { base: 12000, perPage: 150 },
    PHOTOBOOK_A5_SC: { base: 9000, perPage: 100 },
  };
  const pricing = priceMap[spec.uid] || { base: 10000, perPage: 150 };
  const extraPages = Math.max(0, pageCount - spec.page_min);
  return pricing.base + extraPages * pricing.perPage;
}

export function StepOptions({
  pageCount,
  bookSpecUid,
  onPageCountChange,
  onBookSpecChange,
}: StepOptionsProps) {
  const [specs, setSpecs] = useState<BookSpecItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      const result = await apiClient.getBookSpecs();
      if (result.data && result.data.length > 0) {
        setSpecs(result.data);
      }
      setLoading(false);
    }
    load();
  }, []);

  const currentSpec = specs.find((s) => s.uid === bookSpecUid);
  const minPages = currentSpec?.page_min ?? 24;
  const maxPages = currentSpec?.page_max ?? 130;
  const price = currentSpec ? getEstimatedPrice(currentSpec, pageCount) : 0;

  const handleBookSpecChange = (uid: string) => {
    onBookSpecChange(uid);
    const spec = specs.find((s) => s.uid === uid);
    if (spec) {
      if (pageCount < spec.page_min) onPageCountChange(spec.page_min);
      else if (pageCount > spec.page_max) onPageCountChange(spec.page_max);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-16">
        <div className="w-8 h-8 border-3 border-primary border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, x: 30 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -30 }}
      transition={{ duration: 0.3 }}
      className="space-y-8"
    >
      <div className="text-center mb-6">
        <h2 className="text-xl font-bold text-text mb-2">책 옵션 선택</h2>
        <p className="text-sm text-text-light">
          동화책의 크기와 페이지 수를 선택해 주세요
        </p>
      </div>

      {/* 판형 선택 */}
      <div className="space-y-3">
        <div className="flex items-center gap-2 text-sm font-medium text-text">
          <Ruler className="w-4 h-4 text-primary" />
          판형 선택
        </div>
        <div className="grid gap-3">
          {specs.map((spec) => {
            const isSelected = bookSpecUid === spec.uid;
            const desc = `${spec.width_mm}×${spec.height_mm}mm · ${spec.cover_type || "커버"} · ${spec.page_min}~${spec.page_max}p`;
            return (
              <motion.button
                key={spec.uid}
                whileHover={{ scale: 1.01 }}
                whileTap={{ scale: 0.99 }}
                onClick={() => handleBookSpecChange(spec.uid)}
                className={`w-full p-4 rounded-2xl border-2 text-left transition-all ${
                  isSelected
                    ? "border-primary bg-primary/5 shadow-md"
                    : "border-secondary/40 bg-white hover:border-primary/40"
                }`}
              >
                <div className="flex items-center justify-between">
                  <div>
                    <p
                      className={`font-bold text-sm ${
                        isSelected ? "text-primary" : "text-text"
                      }`}
                    >
                      {spec.name}
                    </p>
                    <p className="text-xs text-text-light mt-1">{desc}</p>
                  </div>
                  <div
                    className={`w-5 h-5 rounded-full border-2 flex items-center justify-center ${
                      isSelected
                        ? "border-primary bg-primary"
                        : "border-text-lighter"
                    }`}
                  >
                    {isSelected && (
                      <div className="w-2 h-2 rounded-full bg-white" />
                    )}
                  </div>
                </div>
              </motion.button>
            );
          })}
        </div>
      </div>

      {/* 페이지 수 선택 */}
      <div className="space-y-3">
        <div className="flex items-center gap-2 text-sm font-medium text-text">
          <BookOpen className="w-4 h-4 text-primary" />
          페이지 수
        </div>
        <div className="bg-white rounded-2xl border border-secondary/40 p-4">
          <div className="flex items-center justify-between mb-3">
            <span className="text-2xl font-bold text-primary">{pageCount}p</span>
            <div className="flex items-center gap-2">
              <button
                onClick={() => onPageCountChange(Math.max(minPages, pageCount - 2))}
                disabled={pageCount <= minPages}
                className="w-8 h-8 rounded-full bg-secondary/50 text-text font-bold flex items-center justify-center hover:bg-secondary disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
              >
                -
              </button>
              <button
                onClick={() => onPageCountChange(Math.min(maxPages, pageCount + 2))}
                disabled={pageCount >= maxPages}
                className="w-8 h-8 rounded-full bg-primary/20 text-primary font-bold flex items-center justify-center hover:bg-primary/30 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
              >
                +
              </button>
            </div>
          </div>
          <input
            type="range"
            min={minPages}
            max={maxPages}
            step={2}
            value={pageCount}
            onChange={(e) => onPageCountChange(Number(e.target.value))}
            className="w-full accent-primary h-2 rounded-full appearance-none bg-secondary/30 cursor-pointer"
          />
          <div className="flex justify-between text-xs text-text-lighter mt-1">
            <span>{minPages}p</span>
            <span>{maxPages}p</span>
          </div>
        </div>
      </div>

      {/* 예상 가격 */}
      <motion.div
        key={`${bookSpecUid}-${pageCount}`}
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-gradient-to-r from-accent/10 to-primary/10 rounded-2xl p-5 border border-accent/20"
      >
        <div className="flex items-center gap-2 mb-2">
          <DollarSign className="w-4 h-4 text-accent" />
          <span className="text-sm font-medium text-text">예상 가격</span>
        </div>
        <p className="text-2xl font-bold text-text">
          {price.toLocaleString()}
          <span className="text-sm font-normal text-text-light ml-1">원</span>
        </p>
        <p className="text-xs text-text-lighter mt-1">
          * 최종 가격은 인쇄 시 달라질 수 있습니다
        </p>
      </motion.div>
    </motion.div>
  );
}

export function validateOptions(pageCount: number, bookSpecUid: string) {
  if (!bookSpecUid) {
    return { valid: false, error: "판형을 선택해주세요" };
  }
  if (pageCount % 2 !== 0) {
    return { valid: false, error: "페이지 수는 2의 배수여야 합니다" };
  }
  return { valid: true, error: null };
}
