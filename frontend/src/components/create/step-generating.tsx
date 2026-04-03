"use client";

import { useState, useEffect, useRef } from "react";
import { motion } from "framer-motion";
import { Sparkles } from "lucide-react";

interface StepGeneratingProps {
  bookId: number;
  onComplete: () => void;
  onError: (message: string) => void;
}

export function StepGenerating({
  bookId,
  onComplete,
  onError,
}: StepGeneratingProps) {
  const [progress, setProgress] = useState(0);
  const [statusText, setStatusText] = useState("스토리를 만들고 있어요...");
  const hasStarted = useRef(false);

  useEffect(() => {
    if (hasStarted.current) return;
    hasStarted.current = true;

    // 뒤로가기 차단
    const handlePopState = (e: PopStateEvent) => {
      e.preventDefault();
      window.history.pushState(null, "", window.location.href);
    };
    window.history.pushState(null, "", window.location.href);
    window.addEventListener("popstate", handlePopState);

    // 진행률 시뮬레이션 + 실제 생성 호출
    startGeneration();

    return () => {
      window.removeEventListener("popstate", handlePopState);
    };
  }, []);

  async function startGeneration() {
    // 진행률 애니메이션 (0 → 90% 빠르게, 90 → 100은 완료 후)
    const stages = [
      { target: 20, text: "스토리를 만들고 있어요...", delay: 300 },
      { target: 45, text: "장면을 구성하고 있어요...", delay: 500 },
      { target: 70, text: "일러스트를 그리고 있어요...", delay: 400 },
      { target: 90, text: "마무리하고 있어요...", delay: 300 },
    ];

    // 진행률 애니메이션 시작
    let currentStage = 0;
    const progressInterval = setInterval(() => {
      if (currentStage < stages.length) {
        setProgress(stages[currentStage].target);
        setStatusText(stages[currentStage].text);
        currentStage++;
      } else {
        clearInterval(progressInterval);
      }
    }, 400);

    try {
      // API에서 import하기
      const { apiClient } = await import("@/lib/api");
      const result = await apiClient.generateBook(bookId);

      clearInterval(progressInterval);

      if (result.data) {
        setProgress(100);
        setStatusText("완성되었어요!");
        // 약간의 딜레이 후 완료 콜백
        setTimeout(() => {
          onComplete();
        }, 800);
      } else {
        onError(result.error || "생성에 실패했습니다");
      }
    } catch {
      clearInterval(progressInterval);
      onError("생성 중 오류가 발생했습니다");
    }
  }

  // 원형 진행률 SVG
  const radius = 60;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (progress / 100) * circumference;

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="flex flex-col items-center justify-center min-h-[400px] space-y-8"
    >
      {/* 원형 진행률 */}
      <div className="relative">
        <svg width="160" height="160" className="transform -rotate-90">
          {/* 배경 원 */}
          <circle
            cx="80"
            cy="80"
            r={radius}
            fill="none"
            stroke="#FDE8E3"
            strokeWidth="8"
          />
          {/* 진행률 원 */}
          <motion.circle
            cx="80"
            cy="80"
            r={radius}
            fill="none"
            stroke="#FFB5A7"
            strokeWidth="8"
            strokeLinecap="round"
            strokeDasharray={circumference}
            animate={{ strokeDashoffset }}
            transition={{ duration: 0.5, ease: "easeInOut" }}
          />
        </svg>
        {/* 중앙 아이콘 + 퍼센트 */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 3, repeat: Infinity, ease: "linear" }}
          >
            <Sparkles className="w-6 h-6 text-primary mb-1" />
          </motion.div>
          <span className="text-2xl font-bold text-text">{progress}%</span>
        </div>
      </div>

      {/* 상태 텍스트 */}
      <motion.div
        key={statusText}
        initial={{ opacity: 0, y: 5 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center space-y-2"
      >
        <p className="text-lg font-bold text-text">{statusText}</p>
        <p className="text-sm text-text-light">
          잠시만 기다려 주세요, 동화책이 만들어지고 있어요
        </p>
      </motion.div>

      {/* 주의 문구 */}
      <div className="bg-warning/10 border border-warning/30 rounded-2xl px-4 py-3 max-w-sm">
        <p className="text-xs text-text-light text-center">
          이 화면을 닫지 마세요. 생성이 완료되면 자동으로 편집 화면으로 이동합니다.
        </p>
      </div>
    </motion.div>
  );
}
