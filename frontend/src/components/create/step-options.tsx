"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { BookOpen, Ruler, Sparkles, Check } from "lucide-react";
import { apiClient, BookSpecItem } from "@/lib/api";

interface StepOptionsProps {
  pageCount: number;
  bookSpecUid: string;
  onPageCountChange: (count: number) => void;
  onBookSpecChange: (uid: string) => void;
}

// 제외할 판형 (최소 페이지가 24p 초과인 판형)
const EXCLUDED_SPECS = new Set(["PHOTOBOOK_A5_SC"]);

// 24페이지 고정 구성 안내
const BOOK_STRUCTURE = [
  { label: "표지", pages: "표지" },
  { label: "제목 페이지", pages: "1p" },
  { label: "그림 + 이야기 × 11", pages: "2~23p" },
  { label: "판권", pages: "24p" },
];

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
        const filtered = result.data.filter((s) => !EXCLUDED_SPECS.has(s.uid));
        setSpecs(filtered);

        // 현재 선택된 판형이 필터링된 목록에 없으면 첫 번째로 변경
        if (filtered.length > 0 && !filtered.find((s) => s.uid === bookSpecUid)) {
          onBookSpecChange(filtered[0].uid);
        }
      }
      setLoading(false);
    }
    load();
  }, []);

  // 24페이지 고정
  if (pageCount !== 24) onPageCountChange(24);

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
        <h2 className="text-xl font-bold text-text mb-2">책 구성 선택</h2>
        <p className="text-sm text-text-light">
          24페이지 동화책의 판형을 선택해주세요
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
            return (
              <motion.button
                key={spec.uid}
                whileHover={{ scale: 1.01 }}
                whileTap={{ scale: 0.99 }}
                onClick={() => onBookSpecChange(spec.uid)}
                className={`w-full p-4 rounded-2xl border-2 text-left transition-all ${
                  isSelected
                    ? "border-primary bg-primary/5 shadow-md"
                    : "border-secondary/40 bg-white hover:border-primary/40"
                }`}
              >
                <div className="flex items-center justify-between">
                  <div>
                    <p className={`font-bold text-sm ${isSelected ? "text-primary" : "text-text"}`}>
                      {spec.name}
                    </p>
                    <p className="text-xs text-text-light mt-1">
                      {spec.width_mm}×{spec.height_mm}mm · {spec.cover_type || "커버"} · 24페이지
                    </p>
                  </div>
                  <div className={`w-5 h-5 rounded-full border-2 flex items-center justify-center ${
                    isSelected ? "border-primary bg-primary" : "border-text-lighter"
                  }`}>
                    {isSelected && <Check className="w-3 h-3 text-white" />}
                  </div>
                </div>
              </motion.button>
            );
          })}
        </div>
      </div>

      {/* 페이지 구성 */}
      <div className="space-y-3">
        <div className="flex items-center gap-2 text-sm font-medium text-text">
          <BookOpen className="w-4 h-4 text-primary" />
          페이지 구성
        </div>
        <div className="bg-white rounded-2xl border border-secondary/40 overflow-hidden">
          {BOOK_STRUCTURE.map((item, idx) => (
            <div
              key={idx}
              className={`flex items-center justify-between px-5 py-3 ${
                idx < BOOK_STRUCTURE.length - 1 ? "border-b border-secondary/20" : ""
              }`}
            >
              <span className="text-sm text-text">{item.label}</span>
              <span className="text-xs text-text-lighter font-mono">{item.pages}</span>
            </div>
          ))}
        </div>
        <p className="text-xs text-text-lighter text-center">
          11개의 이야기마다 AI가 그림을 그려줘요
        </p>
      </div>

      {/* AI 생성 안내 */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-gradient-to-r from-accent/10 to-primary/10 rounded-2xl p-5 border border-accent/20"
      >
        <div className="flex items-center gap-2 mb-2">
          <Sparkles className="w-4 h-4 text-accent" />
          <span className="text-sm font-medium text-text">AI가 만드는 것</span>
        </div>
        <ul className="text-sm text-text-light space-y-1">
          <li>· 동화 스토리 11편 (기승전결 구조)</li>
          <li>· 각 이야기에 맞는 일러스트 11장</li>
          <li>· 제목 페이지 일러스트 1장</li>
        </ul>
      </motion.div>
    </motion.div>
  );
}

export function validateOptions(pageCount: number, bookSpecUid: string) {
  if (!bookSpecUid) {
    return { valid: false, error: "판형을 선택해주세요" };
  }
  return { valid: true, error: null };
}
