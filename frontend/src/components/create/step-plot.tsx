"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Sparkles, PenLine, Lock } from "lucide-react";

interface ThemeCard {
  id: string;
  label: string;
  desc: string;
  icon: React.ReactNode;
  available: boolean;
}

const THEME_CARDS: ThemeCard[] = [
  {
    id: "adventure",
    label: "모험 이야기",
    desc: "직업 세계를 탐험하는 흥미진진한 모험",
    icon: <Sparkles className="w-5 h-5" />,
    available: false,
  },
  {
    id: "helping",
    label: "도움 이야기",
    desc: "사람들을 돕는 따뜻한 하루",
    icon: <Sparkles className="w-5 h-5" />,
    available: false,
  },
  {
    id: "learning",
    label: "배움 이야기",
    desc: "직업에 대해 배우고 성장하는 이야기",
    icon: <Sparkles className="w-5 h-5" />,
    available: false,
  },
  {
    id: "custom",
    label: "직접 쓸래요",
    desc: "나만의 줄거리를 직접 작성해요",
    icon: <PenLine className="w-5 h-5" />,
    available: true,
  },
];

interface StepPlotProps {
  plotInput: string;
  jobName: string | null;
  onPlotChange: (plot: string) => void;
}

export function StepPlot({ plotInput, jobName, onPlotChange }: StepPlotProps) {
  const [selectedTheme, setSelectedTheme] = useState<string>(
    plotInput ? "custom" : ""
  );
  const [toast, setToast] = useState<string | null>(null);

  function handleThemeClick(theme: ThemeCard) {
    if (!theme.available) {
      setToast("곧 제공될 예정입니다");
      setTimeout(() => setToast(null), 2000);
      return;
    }
    setSelectedTheme(theme.id);
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
        <h2 className="text-xl font-bold text-text mb-2">줄거리 작성</h2>
        <p className="text-sm text-text-light">
          {jobName
            ? `${jobName} 동화의 줄거리를 선택하거나 직접 써 보세요`
            : "동화의 줄거리를 선택하거나 직접 써 보세요"}
        </p>
      </div>

      {/* 테마 카드들 */}
      <div className="grid grid-cols-2 gap-3">
        {THEME_CARDS.map((theme) => {
          const isSelected = selectedTheme === theme.id;
          return (
            <motion.button
              key={theme.id}
              whileHover={{ scale: theme.available ? 1.02 : 1 }}
              whileTap={{ scale: theme.available ? 0.98 : 1 }}
              onClick={() => handleThemeClick(theme)}
              className={`relative p-4 rounded-2xl border-2 text-left transition-all ${
                isSelected
                  ? "border-primary bg-primary/5 shadow-md"
                  : theme.available
                  ? "border-secondary/40 bg-white hover:border-primary/30"
                  : "border-secondary/20 bg-gray-50/50 cursor-not-allowed opacity-60"
              }`}
            >
              {/* 준비 중 배지 */}
              {!theme.available && (
                <div className="absolute top-2 right-2 flex items-center gap-1 bg-warning/80 text-text text-[10px] font-bold px-2 py-0.5 rounded-full">
                  <Lock className="w-2.5 h-2.5" />
                  준비 중
                </div>
              )}
              <div
                className={`mb-2 ${
                  isSelected ? "text-primary" : "text-text-light"
                }`}
              >
                {theme.icon}
              </div>
              <p
                className={`font-bold text-sm ${
                  isSelected ? "text-primary" : "text-text"
                }`}
              >
                {theme.label}
              </p>
              <p className="text-xs text-text-lighter mt-1">{theme.desc}</p>
            </motion.button>
          );
        })}
      </div>

      {/* 토스트 메시지 */}
      {toast && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0 }}
          className="text-center py-2 px-4 bg-warning/20 rounded-xl text-sm text-text"
        >
          {toast}
        </motion.div>
      )}

      {/* 직접 쓸래요 선택 시 textarea */}
      {selectedTheme === "custom" && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: "auto" }}
          transition={{ duration: 0.3 }}
          className="space-y-2"
        >
          <label className="text-sm font-medium text-text">
            줄거리를 작성해 주세요
          </label>
          <textarea
            value={plotInput}
            onChange={(e) => onPlotChange(e.target.value)}
            placeholder="예: 소방관이 되어 마을의 화재를 진압하고, 사람들에게 감사를 받는 이야기"
            rows={5}
            maxLength={1000}
            className="w-full px-4 py-3 rounded-2xl border border-secondary/40 bg-white text-text placeholder:text-text-lighter text-sm resize-none focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition-all"
          />
          <div className="text-right text-xs text-text-lighter">
            {plotInput.length} / 1,000
          </div>
        </motion.div>
      )}
    </motion.div>
  );
}

export function validatePlot(plotInput: string) {
  if (!plotInput || plotInput.trim().length === 0) {
    return { valid: false, error: "줄거리를 입력해주세요" };
  }
  if (plotInput.trim().length < 5) {
    return { valid: false, error: "줄거리를 5자 이상 입력해주세요" };
  }
  return { valid: true, error: null };
}
