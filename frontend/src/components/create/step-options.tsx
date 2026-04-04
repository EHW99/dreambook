"use client";

import { motion } from "framer-motion";
import { BookOpen, Ruler, Sparkles } from "lucide-react";

interface StepOptionsProps {
  pageCount: number;
  bookSpecUid: string;
  onPageCountChange: (count: number) => void;
  onBookSpecChange: (uid: string) => void;
}

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
  // 고정값 적용 (혹시 다른 값이 들어와도 강제)
  if (pageCount !== 24) onPageCountChange(24);
  if (bookSpecUid !== "SQUAREBOOK_HC") onBookSpecChange("SQUAREBOOK_HC");

  return (
    <motion.div
      initial={{ opacity: 0, x: 30 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -30 }}
      transition={{ duration: 0.3 }}
      className="space-y-8"
    >
      <div className="text-center mb-6">
        <h2 className="text-xl font-bold text-text mb-2">책 구성 확인</h2>
        <p className="text-sm text-text-light">
          24페이지 정사각형 하드커버 동화책이 만들어져요
        </p>
      </div>

      {/* 판형 정보 */}
      <div className="bg-white rounded-2xl border border-secondary/40 p-5 space-y-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center">
            <Ruler className="w-5 h-5 text-primary" />
          </div>
          <div>
            <p className="font-bold text-text">정사각형 하드커버</p>
            <p className="text-xs text-text-light">243 × 248mm · 하드커버 · 24페이지</p>
          </div>
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
  // 고정값이므로 항상 통과
  return { valid: true, error: null };
}
