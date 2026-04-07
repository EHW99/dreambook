"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Sparkles, BookOpen, ArrowLeft } from "lucide-react";
import { Button } from "@/components/ui/button";

interface StepGeneratingProps {
  bookId: number;
  onComplete: () => void;
  onError: (message: string) => void;
  onBack?: () => void;
}

export function StepGenerating({
  bookId,
  onComplete,
  onError,
  onBack,
}: StepGeneratingProps) {
  const [generating, setGenerating] = useState(false);
  const [statusText, setStatusText] = useState("");

  async function startGeneration() {
    setGenerating(true);
    setStatusText("스토리를 만들고 있어요...");

    // 뒤로가기 차단
    window.history.pushState(null, "", window.location.href);
    const handlePopState = (e: PopStateEvent) => {
      e.preventDefault();
      window.history.pushState(null, "", window.location.href);
    };
    window.addEventListener("popstate", handlePopState);

    try {
      const { apiClient } = await import("@/lib/api");
      const storyResult = await apiClient.generateStoryOnly(bookId);

      if (!storyResult.data) {
        onError(storyResult.error || "스토리 생성에 실패했습니다");
        return;
      }

      setStatusText("스토리가 완성되었어요!");
      setTimeout(() => onComplete(), 800);
    } catch {
      onError("생성 중 오류가 발생했습니다");
    } finally {
      window.removeEventListener("popstate", handlePopState);
    }
  }

  // 아직 시작 안 함 — 안내 + 버튼
  if (!generating) {
    return (
      <motion.div
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        exit={{ opacity: 0, x: -20 }}
        className="flex flex-col items-center justify-center min-h-[400px] space-y-8"
      >
        <div className="w-20 h-20 bg-primary/10 rounded-full flex items-center justify-center">
          <BookOpen className="w-10 h-10 text-primary" />
        </div>
        <div className="text-center space-y-3 max-w-sm">
          <h2 className="text-xl font-bold text-text">스토리를 만들 준비가 되었어요</h2>
          <p className="text-sm text-text-light leading-relaxed">
            선택한 줄거리를 바탕으로 AI가 11편의 이야기를 만들어요.
            각 이야기에는 그림을 위한 장면 묘사도 함께 생성됩니다.
          </p>
        </div>
        <div className="flex items-center gap-3">
          {onBack && (
            <Button onClick={onBack} variant="ghost" size="lg" className="gap-2">
              <ArrowLeft className="w-4 h-4" />
              이전
            </Button>
          )}
          <Button onClick={startGeneration} size="lg" className="gap-2">
            <Sparkles className="w-5 h-5" />
            스토리 생성하기
          </Button>
        </div>
        <p className="text-xs text-text-lighter">생성에 약 10~20초가 소요됩니다</p>
      </motion.div>
    );
  }

  // 생성 중 — 회전 애니메이션
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="flex flex-col items-center justify-center min-h-[400px] space-y-8"
    >
      <div className="relative">
        <div className="w-32 h-32 rounded-full border-4 border-secondary flex items-center justify-center">
          <motion.div animate={{ rotate: 360 }} transition={{ duration: 3, repeat: Infinity, ease: "linear" }}>
            <Sparkles className="w-10 h-10 text-primary" />
          </motion.div>
        </div>
      </div>

      <motion.div key={statusText} initial={{ opacity: 0, y: 5 }} animate={{ opacity: 1, y: 0 }} className="text-center space-y-2">
        <p className="text-lg font-bold text-text">{statusText}</p>
        <p className="text-sm text-text-light">잠시만 기다려 주세요</p>
      </motion.div>

      <div className="bg-warning/10 border border-warning/30 rounded-2xl px-4 py-3 max-w-sm">
        <p className="text-xs text-text-light text-center">이 화면을 닫지 마세요.</p>
      </div>
    </motion.div>
  );
}
