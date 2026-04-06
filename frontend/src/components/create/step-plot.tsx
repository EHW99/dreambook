"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Sparkles, PenLine, RefreshCw, Check, BookOpen, Ruler, Layers } from "lucide-react";
import { Button } from "@/components/ui/button";
import { apiClient, BookSpecItem, PlotCandidate } from "@/lib/api";

interface StepPlotProps {
  bookId: number;
  plotInput: string;
  jobName: string | null;
  onPlotChange: (plot: string) => void;
}

export function StepPlot({ bookId, plotInput, jobName, onPlotChange }: StepPlotProps) {
  const [plots, setPlots] = useState<PlotCandidate[]>([]);
  const [selectedIdx, setSelectedIdx] = useState<number | null>(null);
  const [isCustom, setIsCustom] = useState(false);
  const [loading, setLoading] = useState(false);
  const [generated, setGenerated] = useState(false);
  const [regenUsed, setRegenUsed] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [bookSpec, setBookSpec] = useState<BookSpecItem | null>(null);

  // 책 사양 로드
  useEffect(() => {
    async function loadSpec() {
      const result = await apiClient.getBookSpecs();
      if (result.data) {
        const found = result.data.find((s) => s.uid === "SQUAREBOOK_HC");
        if (found) setBookSpec(found);
      }
    }
    loadSpec();
  }, []);

  async function generatePlots() {
    setLoading(true);
    setError(null);
    setSelectedIdx(null);
    setIsCustom(false);
    onPlotChange("");

    const result = await apiClient.generatePlots(bookId);
    if (result.data) {
      setPlots(result.data.plots);
      setGenerated(true);
    } else {
      setError(result.error || "줄거리 생성에 실패했습니다");
    }
    setLoading(false);
  }

  function handleSelectPlot(idx: number) {
    setSelectedIdx(idx);
    setIsCustom(false);
    const plot = plots[idx];
    onPlotChange(`${plot.title}: ${plot.description}`);
  }

  function handleCustom() {
    setSelectedIdx(null);
    setIsCustom(true);
    onPlotChange("");
  }

  async function handleRegen() {
    if (regenUsed) return;
    setRegenUsed(true);
    await generatePlots();
  }

  return (
    <motion.div
      initial={{ opacity: 0, x: 30 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -30 }}
      transition={{ duration: 0.3 }}
      className="space-y-6"
    >
      <div className="text-center mb-6">
        <h2 className="text-xl font-bold text-text mb-2">줄거리를 선택해주세요</h2>
        <p className="text-sm text-text-light">
          {jobName ? `${jobName} 동화의 줄거리를 골라주세요` : "동화의 줄거리를 골라주세요"}
        </p>
      </div>

      {/* 책 정보 */}
      <div className="rounded-2xl border border-secondary/40 bg-white overflow-hidden">
        <div className="px-4 py-3 bg-secondary/10 border-b border-secondary/20">
          <p className="text-xs font-medium text-text-light flex items-center gap-1.5">
            <BookOpen className="w-3.5 h-3.5" />
            이런 동화책이 만들어져요
          </p>
        </div>
        <div className="px-4 py-3 space-y-2.5">
          <div className="flex items-center gap-2.5">
            <Ruler className="w-4 h-4 text-primary flex-shrink-0" />
            <div className="text-sm">
              <span className="font-medium text-text">{bookSpec?.name || "정사각형 하드커버"}</span>
              {bookSpec && (
                <span className="text-text-light"> · {bookSpec.width_mm}×{bookSpec.height_mm}mm</span>
              )}
            </div>
          </div>
          <div className="flex items-center gap-2.5">
            <Layers className="w-4 h-4 text-primary flex-shrink-0" />
            <span className="text-sm text-text">
              <span className="font-medium">24페이지</span>
              <span className="text-text-light"> · 제목 1p + 이야기 11편 + 판권 1p</span>
            </span>
          </div>
        </div>
      </div>

      {/* 초기 안내 — 아직 생성 안 했을 때 */}
      {!generated && !loading && !error && (
        <div className="text-center py-8 space-y-5">
          <div className="w-16 h-16 mx-auto bg-primary/10 rounded-full flex items-center justify-center">
            <Sparkles className="w-8 h-8 text-primary" />
          </div>
          <div className="space-y-2">
            <p className="text-text font-medium">
              AI가 {jobName ? `${jobName}` : "선택한 직업"}에 맞는 줄거리를 만들어드려요
            </p>
            <p className="text-sm text-text-light">
              4가지 줄거리 중 마음에 드는 걸 선택하거나, 직접 작성할 수도 있어요
            </p>
          </div>
          <Button onClick={generatePlots} size="lg" className="gap-2">
            <Sparkles className="w-4 h-4" />
            줄거리 만들기
          </Button>
        </div>
      )}

      {/* 로딩 */}
      {loading && (
        <div className="flex flex-col items-center justify-center py-12 space-y-4">
          <motion.div animate={{ rotate: 360 }} transition={{ duration: 2, repeat: Infinity, ease: "linear" }}>
            <Sparkles className="w-8 h-8 text-primary" />
          </motion.div>
          <p className="text-sm text-text-light">AI가 줄거리를 만들고 있어요...</p>
        </div>
      )}

      {/* 에러 */}
      {error && !loading && (
        <div className="p-4 bg-error/10 border border-error/30 rounded-2xl text-center">
          <p className="text-sm text-error-dark">{error}</p>
          <Button variant="ghost" onClick={generatePlots} className="mt-2 text-xs">
            다시 시도
          </Button>
        </div>
      )}

      {/* 줄거리 카드 */}
      {!loading && plots.length > 0 && (
        <>
          <div className="space-y-3">
            {plots.map((plot, idx) => {
              const isSelected = selectedIdx === idx && !isCustom;
              return (
                <motion.button
                  key={idx}
                  whileHover={{ scale: 1.01 }}
                  whileTap={{ scale: 0.99 }}
                  onClick={() => handleSelectPlot(idx)}
                  className={`w-full text-left p-4 rounded-2xl border-2 transition-all ${
                    isSelected
                      ? "border-primary bg-primary/5 shadow-md"
                      : "border-secondary/40 bg-white hover:border-primary/30"
                  }`}
                >
                  <div className="flex items-start gap-3">
                    <div className={`w-5 h-5 rounded-full border-2 flex-shrink-0 mt-0.5 flex items-center justify-center transition-colors ${
                      isSelected ? "border-primary bg-primary" : "border-secondary"
                    }`}>
                      {isSelected && <Check className="w-3 h-3 text-white" />}
                    </div>
                    <div>
                      <p className={`text-sm font-bold mb-1 ${isSelected ? "text-primary-dark" : "text-text"}`}>
                        {plot.title}
                      </p>
                      <p className="text-sm text-text-light leading-relaxed">
                        {plot.description}
                      </p>
                    </div>
                  </div>
                </motion.button>
              );
            })}

            {/* 직접 쓸래요 */}
            <motion.button
              whileHover={{ scale: 1.01 }}
              whileTap={{ scale: 0.99 }}
              onClick={handleCustom}
              className={`w-full text-left p-4 rounded-2xl border-2 transition-all ${
                isCustom
                  ? "border-primary bg-primary/5 shadow-md"
                  : "border-secondary/40 bg-white hover:border-primary/30"
              }`}
            >
              <div className="flex items-center gap-3">
                <div className={`w-5 h-5 rounded-full border-2 flex-shrink-0 flex items-center justify-center transition-colors ${
                  isCustom ? "border-primary bg-primary" : "border-secondary"
                }`}>
                  {isCustom && <Check className="w-3 h-3 text-white" />}
                </div>
                <div className="flex items-center gap-2">
                  <PenLine className="w-4 h-4 text-text-light" />
                  <span className="text-sm font-bold text-text">직접 쓸래요</span>
                </div>
              </div>
            </motion.button>
          </div>

          {/* 다른 줄거리 보기 */}
          <div className="flex justify-center">
            <Button
              variant="ghost"
              onClick={handleRegen}
              disabled={regenUsed || loading}
              className="gap-2 text-xs"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              {regenUsed ? "재생성 사용 완료" : "다른 줄거리 보기"}
            </Button>
          </div>
        </>
      )}

      {/* 직접 입력 textarea */}
      <AnimatePresence>
        {isCustom && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="space-y-2"
          >
            <label className="text-sm font-medium text-text">줄거리를 작성해 주세요</label>
            <textarea
              value={plotInput}
              onChange={(e) => onPlotChange(e.target.value)}
              placeholder="예: 소방관이 되어 마을의 화재를 진압하고, 사람들에게 감사를 받는 이야기"
              rows={4}
              maxLength={500}
              className="w-full px-4 py-3 rounded-2xl border border-secondary/40 bg-white text-text placeholder:text-text-lighter text-sm resize-none focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition-all"
              autoFocus
            />
            <div className="text-right text-xs text-text-lighter">
              {plotInput.length} / 500
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

export function validatePlot(plotInput: string) {
  if (!plotInput || plotInput.trim().length === 0) {
    return { valid: false, error: "줄거리를 선택하거나 입력해주세요" };
  }
  return { valid: true, error: null };
}
