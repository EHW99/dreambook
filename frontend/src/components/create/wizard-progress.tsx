"use client";

import { Check } from "lucide-react";
import { motion } from "framer-motion";

const STEPS = [
  { number: 1, label: "정보 입력" },
  { number: 2, label: "직업 선택" },
  { number: 3, label: "동화 스타일" },
  { number: 4, label: "그림체" },
  { number: 5, label: "캐릭터" },
  { number: 6, label: "책 구성" },
  { number: 7, label: "줄거리" },
  { number: 8, label: "생성" },
  { number: 9, label: "편집" },
];

interface WizardProgressProps {
  currentStep: number;
}

export function WizardProgress({ currentStep }: WizardProgressProps) {
  return (
    <div className="w-full overflow-x-auto pb-2">
      <div className="flex items-center justify-center min-w-[600px] px-4">
        {STEPS.map((step, index) => {
          const isCompleted = currentStep > step.number;
          const isCurrent = currentStep === step.number;
          const isUpcoming = currentStep < step.number;

          return (
            <div key={step.number} className="flex items-center">
              {/* Step circle */}
              <div className="flex flex-col items-center">
                <motion.div
                  initial={false}
                  animate={{
                    scale: isCurrent ? 1.1 : 1,
                    backgroundColor: isCompleted
                      ? "#B5EAD7"
                      : isCurrent
                      ? "#FFB5A7"
                      : "#FDE8E3",
                  }}
                  className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold transition-colors ${
                    isCompleted
                      ? "text-white"
                      : isCurrent
                      ? "text-white ring-4 ring-primary/20"
                      : "text-text-lighter"
                  }`}
                >
                  {isCompleted ? (
                    <Check className="w-4 h-4" />
                  ) : (
                    step.number
                  )}
                </motion.div>
                <span
                  className={`mt-1 text-[10px] whitespace-nowrap ${
                    isCurrent
                      ? "text-primary font-bold"
                      : isCompleted
                      ? "text-success-dark font-medium"
                      : "text-text-lighter"
                  }`}
                >
                  {step.label}
                </span>
              </div>

              {/* Connector line */}
              {index < STEPS.length - 1 && (
                <div
                  className={`w-6 h-0.5 mx-1 mt-[-14px] ${
                    isCompleted ? "bg-success" : "bg-secondary"
                  }`}
                />
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
