"use client";

import { motion } from "framer-motion";
import { Sparkles, Rocket } from "lucide-react";

const STORY_STYLES = [
  {
    id: "dreaming_today",
    title: "꿈꾸는 오늘",
    description: "오늘 하루, 아이가 꿈속에서 그 직업으로 활약하는 판타지 동화예요. 마법같은 하루를 선물해주세요!",
    icon: Sparkles,
    color: "from-[#FFB5A7] to-[#FCD5CE]",
    borderColor: "border-[#FFB5A7]",
    bgColor: "bg-[#FFF0ED]",
  },
  {
    id: "future_me",
    title: "미래의 나",
    description: "아이가 자라서 실제로 그 직업인이 되어 활약하는 이야기예요. 미래의 멋진 모습을 미리 만나보세요!",
    icon: Rocket,
    color: "from-[#A8DADC] to-[#B5EAD7]",
    borderColor: "border-[#A8DADC]",
    bgColor: "bg-[#F0FAFB]",
  },
];

interface StepStoryStyleProps {
  selected: string;
  onSelect: (styleId: string) => void;
}

export function StepStoryStyle({ selected, onSelect }: StepStoryStyleProps) {
  return (
    <motion.div
      initial={{ opacity: 0, x: 30 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -30 }}
      transition={{ duration: 0.3 }}
      className="space-y-6"
    >
      <div className="text-center space-y-2">
        <h2 className="text-2xl font-bold text-text">동화 스타일을 선택해주세요</h2>
        <p className="text-text-light text-sm">아이의 동화책이 어떤 이야기가 될지 골라주세요</p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mt-8">
        {STORY_STYLES.map((style) => {
          const isSelected = selected === style.id;
          const Icon = style.icon;

          return (
            <motion.button
              key={style.id}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => onSelect(style.id)}
              className={`relative p-6 rounded-2xl border-2 text-left transition-all duration-200 ${
                isSelected
                  ? `${style.borderColor} ${style.bgColor} shadow-lg ring-2 ring-offset-2 ${style.borderColor.replace("border", "ring")}`
                  : "border-secondary/50 bg-white hover:border-secondary hover:shadow-md"
              }`}
            >
              {/* 선택 표시 */}
              {isSelected && (
                <motion.div
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  className={`absolute top-3 right-3 w-6 h-6 rounded-full bg-gradient-to-r ${style.color} flex items-center justify-center`}
                >
                  <svg className="w-3.5 h-3.5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                  </svg>
                </motion.div>
              )}

              <div className={`w-14 h-14 rounded-2xl bg-gradient-to-r ${style.color} flex items-center justify-center mb-4`}>
                <Icon className="w-7 h-7 text-white" />
              </div>

              <h3 className="text-lg font-bold text-text mb-2">{style.title}</h3>
              <p className="text-sm text-text-light leading-relaxed">{style.description}</p>
            </motion.button>
          );
        })}
      </div>
    </motion.div>
  );
}

export function validateStoryStyle(storyStyle: string): { valid: boolean; error?: string } {
  if (!storyStyle) {
    return { valid: false, error: "동화 스타일을 선택해주세요" };
  }
  return { valid: true };
}
