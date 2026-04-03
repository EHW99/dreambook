"use client";

import { motion } from "framer-motion";
import { Droplets, PenTool, Palette, Box, Zap } from "lucide-react";

const ART_STYLES = [
  {
    id: "watercolor",
    title: "수채화",
    description: "부드럽고 따뜻한 수채화 느낌",
    icon: Droplets,
    color: "#A8DADC",
    bgGradient: "from-[#A8DADC]/20 to-[#B5EAD7]/20",
    sampleColors: ["#A8DADC", "#B5EAD7", "#FCD5CE"],
  },
  {
    id: "pencil",
    title: "연필화",
    description: "섬세하고 정교한 연필 스케치",
    icon: PenTool,
    color: "#9B9B9B",
    bgGradient: "from-gray-100 to-gray-50",
    sampleColors: ["#666666", "#999999", "#CCCCCC"],
  },
  {
    id: "crayon",
    title: "크레파스",
    description: "아이가 직접 그린 듯한 크레파스 느낌",
    icon: Palette,
    color: "#FFB5A7",
    bgGradient: "from-[#FFB5A7]/20 to-[#FFE0AC]/20",
    sampleColors: ["#FFB5A7", "#FFE0AC", "#B5EAD7"],
  },
  {
    id: "3d",
    title: "3D",
    description: "생동감 넘치는 3D 애니메이션 스타일",
    icon: Box,
    color: "#7C9EF7",
    bgGradient: "from-[#7C9EF7]/20 to-[#A8DADC]/20",
    sampleColors: ["#7C9EF7", "#A8DADC", "#FFB5A7"],
  },
  {
    id: "cartoon",
    title: "만화",
    description: "밝고 유쾌한 만화 스타일",
    icon: Zap,
    color: "#FFE0AC",
    bgGradient: "from-[#FFE0AC]/20 to-[#FFB5A7]/20",
    sampleColors: ["#FFE0AC", "#FFB5A7", "#B5EAD7"],
  },
];

interface StepArtStyleProps {
  selected: string;
  onSelect: (styleId: string) => void;
}

export function StepArtStyle({ selected, onSelect }: StepArtStyleProps) {
  return (
    <motion.div
      initial={{ opacity: 0, x: 30 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -30 }}
      transition={{ duration: 0.3 }}
      className="space-y-6"
    >
      <div className="text-center space-y-2">
        <h2 className="text-2xl font-bold text-text">그림체를 선택해주세요</h2>
        <p className="text-text-light text-sm">동화책의 일러스트 스타일을 골라주세요</p>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 mt-8">
        {ART_STYLES.map((style) => {
          const isSelected = selected === style.id;
          const Icon = style.icon;

          return (
            <motion.button
              key={style.id}
              whileHover={{ scale: 1.03 }}
              whileTap={{ scale: 0.97 }}
              onClick={() => onSelect(style.id)}
              className={`relative p-4 rounded-2xl border-2 text-center transition-all duration-200 ${
                isSelected
                  ? "border-primary bg-primary/5 shadow-lg ring-2 ring-primary/30 ring-offset-2"
                  : "border-secondary/50 bg-white hover:border-secondary hover:shadow-md"
              }`}
            >
              {/* 선택 표시 */}
              {isSelected && (
                <motion.div
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  className="absolute top-2 right-2 w-5 h-5 rounded-full bg-primary flex items-center justify-center"
                >
                  <svg className="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                  </svg>
                </motion.div>
              )}

              {/* 샘플 미리보기 영역 */}
              <div className={`w-full aspect-square rounded-xl bg-gradient-to-br ${style.bgGradient} mb-3 flex items-center justify-center relative overflow-hidden`}>
                <Icon className="w-10 h-10" style={{ color: style.color }} />
                {/* 장식용 색상 점들 */}
                <div className="absolute bottom-2 left-0 right-0 flex justify-center gap-1.5">
                  {style.sampleColors.map((c, i) => (
                    <div
                      key={i}
                      className="w-3 h-3 rounded-full"
                      style={{ backgroundColor: c }}
                    />
                  ))}
                </div>
              </div>

              <h3 className="text-sm font-bold text-text">{style.title}</h3>
              <p className="text-xs text-text-light mt-1 leading-relaxed">{style.description}</p>
            </motion.button>
          );
        })}
      </div>
    </motion.div>
  );
}

export function validateArtStyle(artStyle: string): { valid: boolean; error?: string } {
  if (!artStyle) {
    return { valid: false, error: "그림체를 선택해주세요" };
  }
  return { valid: true };
}
