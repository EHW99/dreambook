"use client";

import { motion } from "framer-motion";
import { BookOpen, Ruler, DollarSign } from "lucide-react";

const BOOK_SPECS = [
  {
    uid: "SQUAREBOOK_HC",
    label: "정사각 하드커버",
    desc: "243×248mm · 하드커버 · 24~130p",
    priceBase: 15000,
    pricePerPage: 200,
    minPages: 24,
    maxPages: 130,
  },
  {
    uid: "PHOTOBOOK_A4_SC",
    label: "A4 소프트커버",
    desc: "210×297mm · 소프트커버 · 24~130p",
    priceBase: 12000,
    pricePerPage: 150,
    minPages: 24,
    maxPages: 130,
  },
  {
    uid: "PHOTOBOOK_A5_SC",
    label: "A5 소프트커버",
    desc: "148×210mm · 소프트커버 · 50~200p",
    priceBase: 9000,
    pricePerPage: 100,
    minPages: 50,
    maxPages: 200,
  },
];

interface StepOptionsProps {
  pageCount: number;
  bookSpecUid: string;
  onPageCountChange: (count: number) => void;
  onBookSpecChange: (uid: string) => void;
}

function getEstimatedPrice(bookSpecUid: string, pageCount: number): number {
  const spec = BOOK_SPECS.find((s) => s.uid === bookSpecUid);
  if (!spec) return 0;
  const extraPages = Math.max(0, pageCount - spec.minPages);
  return spec.priceBase + extraPages * spec.pricePerPage;
}

function getSpecRange(bookSpecUid: string) {
  const spec = BOOK_SPECS.find((s) => s.uid === bookSpecUid);
  return { minPages: spec?.minPages ?? 24, maxPages: spec?.maxPages ?? 130 };
}

export function StepOptions({
  pageCount,
  bookSpecUid,
  onPageCountChange,
  onBookSpecChange,
}: StepOptionsProps) {
  const price = getEstimatedPrice(bookSpecUid, pageCount);
  const { minPages, maxPages } = getSpecRange(bookSpecUid);

  const handleBookSpecChange = (uid: string) => {
    onBookSpecChange(uid);
    const range = getSpecRange(uid);
    // 판형 변경 시 현재 페이지 수가 새 범위 밖이면 보정
    if (pageCount < range.minPages) {
      onPageCountChange(range.minPages);
    } else if (pageCount > range.maxPages) {
      onPageCountChange(range.maxPages);
    }
  };

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
          {BOOK_SPECS.map((spec) => {
            const isSelected = bookSpecUid === spec.uid;
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
                      {spec.label}
                    </p>
                    <p className="text-xs text-text-light mt-1">{spec.desc}</p>
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
  const validUids = new Set(BOOK_SPECS.map((s) => s.uid));
  if (!validUids.has(bookSpecUid)) {
    return { valid: false, error: "판형을 선택해주세요" };
  }
  if (pageCount % 2 !== 0) {
    return { valid: false, error: "페이지 수는 2의 배수여야 합니다" };
  }
  const spec = BOOK_SPECS.find((s) => s.uid === bookSpecUid)!;
  if (pageCount < spec.minPages || pageCount > spec.maxPages) {
    return {
      valid: false,
      error: `${spec.label}의 페이지 수는 ${spec.minPages}~${spec.maxPages}p 범위여야 합니다`,
    };
  }
  return { valid: true, error: null };
}
