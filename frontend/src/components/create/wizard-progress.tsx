"use client";

import { Check } from "lucide-react";
import { motion } from "framer-motion";

const STEPS = [
  { number: 1, label: "정보" },
  { number: 2, label: "직업" },
  { number: 3, label: "스타일" },
  { number: 4, label: "줄거리" },
  { number: 5, label: "스토리" },
  { number: 6, label: "그림" },
];

const TOTAL = STEPS.length;

// ── 3단계 그룹 매핑 ──
const GROUPS = [
  { label: "정보 입력", steps: [1, 2, 3] },
  { label: "동화 생성", steps: [4, 5] },
  { label: "편집/완성", steps: [6] },
];

interface WizardProgressProps {
  currentStep: number;
  variant?: "A" | "B" | "C";
}

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// A) 심플 바 — 숫자/라벨 없이 얇은 진행 바만
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
function VariantA({ currentStep }: { currentStep: number }) {
  const progress = ((currentStep - 1) / (TOTAL - 1)) * 100;

  return (
    <div className="flex items-center gap-3">
      <div className="flex-1 h-1.5 bg-secondary/50 rounded-full overflow-hidden">
        <motion.div
          className="h-full bg-primary rounded-full"
          initial={false}
          animate={{ width: `${progress}%` }}
          transition={{ duration: 0.4, ease: "easeOut" }}
        />
      </div>
      <span className="text-xs text-text-lighter shrink-0">
        {currentStep}/{TOTAL}
      </span>
    </div>
  );
}

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// B) 현재 스텝만 표시 — 나머지 숨김
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
function VariantB({ currentStep }: { currentStep: number }) {
  const current = STEPS.find((s) => s.number === currentStep);
  const progress = ((currentStep - 1) / (TOTAL - 1)) * 100;

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <p className="text-sm text-text">
          <span className="font-bold text-primary">Step {currentStep}</span>
          <span className="text-text-lighter mx-1.5">·</span>
          <span className="font-medium">{current?.label}</span>
        </p>
        <span className="text-xs text-text-lighter">{currentStep}/{TOTAL}</span>
      </div>
      <div className="h-1 bg-secondary/50 rounded-full overflow-hidden">
        <motion.div
          className="h-full bg-primary rounded-full"
          initial={false}
          animate={{ width: `${progress}%` }}
          transition={{ duration: 0.4, ease: "easeOut" }}
        />
      </div>
    </div>
  );
}

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// C) 3단계 그룹 — 정보입력 / 동화생성 / 편집완성
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
function VariantC({ currentStep }: { currentStep: number }) {
  return (
    <div className="flex items-center gap-2">
      {GROUPS.map((group, gi) => {
        const isCompleted = currentStep > Math.max(...group.steps);
        const isCurrent = group.steps.includes(currentStep);

        return (
          <div key={group.label} className="flex items-center flex-1 gap-2">
            <div className="flex-1">
              <div
                className={`text-center py-2 rounded-xl text-xs font-medium transition-all ${
                  isCompleted
                    ? "bg-success/20 text-success-dark"
                    : isCurrent
                    ? "bg-primary/15 text-primary-dark font-bold"
                    : "bg-secondary/30 text-text-lighter"
                }`}
              >
                {isCompleted ? (
                  <span className="flex items-center justify-center gap-1">
                    <Check className="w-3 h-3" />
                    {group.label}
                  </span>
                ) : (
                  group.label
                )}
              </div>
            </div>
            {gi < GROUPS.length - 1 && (
              <div className={`w-4 h-0.5 shrink-0 ${isCompleted ? "bg-success" : "bg-secondary/40"}`} />
            )}
          </div>
        );
      })}
    </div>
  );
}

// ── 메인 컴포넌트 ──
export function WizardProgress({ currentStep, variant = "A" }: WizardProgressProps) {
  switch (variant) {
    case "A": return <VariantA currentStep={currentStep} />;
    case "B": return <VariantB currentStep={currentStep} />;
    case "C": return <VariantC currentStep={currentStep} />;
    default: return <VariantA currentStep={currentStep} />;
  }
}
