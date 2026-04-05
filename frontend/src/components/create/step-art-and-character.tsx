"use client";

import { useState, useEffect, useCallback } from "react";
import Image from "next/image";
import { motion, AnimatePresence } from "framer-motion";
import {
  Droplets, PenTool, Palette, Box, Zap,
  RefreshCw, Check, User, ImageIcon,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { apiClient, CharacterSheetItem } from "@/lib/api";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const MAX_GENERATIONS = 5;

const ART_STYLES = [
  {
    id: "watercolor",
    title: "수채화",
    description: "부드럽고 따뜻한 느낌",
    icon: Droplets,
    color: "#A8DADC",
    bg: "from-[#A8DADC]/20 to-[#B5EAD7]/20",
    image: "/images/art-styles/watercolor.png",
  },
  {
    id: "pencil",
    title: "연필화",
    description: "섬세한 연필 스케치",
    icon: PenTool,
    color: "#9B9B9B",
    bg: "from-gray-100 to-gray-50",
    image: "/images/art-styles/pencil.png",
  },
  {
    id: "crayon",
    title: "크레파스",
    description: "아이가 그린 듯한 느낌",
    icon: Palette,
    color: "#FFB5A7",
    bg: "from-[#FFB5A7]/20 to-[#FFE0AC]/20",
    image: "/images/art-styles/crayon.png",
  },
  {
    id: "3d",
    title: "3D",
    description: "생동감 넘치는 3D",
    icon: Box,
    color: "#7C9EF7",
    bg: "from-[#7C9EF7]/20 to-[#A8DADC]/20",
    image: "/images/art-styles/3d.png",
  },
  {
    id: "cartoon",
    title: "만화",
    description: "밝고 유쾌한 만화풍",
    icon: Zap,
    color: "#FFE0AC",
    bg: "from-[#FFE0AC]/20 to-[#FFB5A7]/20",
    image: "/images/art-styles/cartoon.png",
  },
];

interface StepArtAndCharacterProps {
  bookId: number;
  artStyle: string;
  characterRegenCount: number;
  onArtStyleChange: (style: string) => void;
  onArtStyleSaved: () => void;
  onConfirm: () => void | Promise<void>;
  onRegenCountUpdate: (count: number) => void;
}

export function StepArtAndCharacter({
  bookId,
  artStyle,
  characterRegenCount,
  onArtStyleChange,
  onArtStyleSaved,
  onConfirm,
  onRegenCountUpdate,
}: StepArtAndCharacterProps) {
  const [characters, setCharacters] = useState<CharacterSheetItem[]>([]);
  const [loadingChars, setLoadingChars] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [selecting, setSelecting] = useState(false);
  const [savingStyle, setSavingStyle] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [imgErrors, setImgErrors] = useState<Record<string, boolean>>({});

  const selectedChar = characters.find((c) => c.is_selected);
  const remainingRegens = MAX_GENERATIONS - characters.length;
  const canRegenerate = remainingRegens > 0;
  const hasCharacters = characters.length > 0;

  const loadCharacters = useCallback(async () => {
    const result = await apiClient.getCharacters(bookId);
    if (result.data) setCharacters(result.data);
    setLoadingChars(false);
  }, [bookId]);

  useEffect(() => {
    loadCharacters();
  }, [loadCharacters]);

  async function handleStyleChange(styleId: string) {
    if (styleId === artStyle || savingStyle) return;
    onArtStyleChange(styleId);
    setSavingStyle(true);
    const result = await apiClient.updateBook(bookId, { art_style: styleId });
    setSavingStyle(false);
    if (result.data) onArtStyleSaved();
  }

  async function handleGenerate() {
    if (!artStyle) {
      setError("그림체를 먼저 선택해주세요");
      return;
    }
    setGenerating(true);
    setError(null);
    const result = await apiClient.createCharacter(bookId);
    if (result.data) {
      setCharacters((prev) => [...prev, result.data!]);
      if (characters.length > 0) onRegenCountUpdate(characters.length);
    } else {
      setError(result.error || "캐릭터 생성에 실패했습니다");
    }
    setGenerating(false);
  }

  async function handleSelect(charId: number) {
    setSelecting(true);
    setError(null);
    const result = await apiClient.selectCharacter(bookId, charId);
    if (result.data) {
      setCharacters((prev) => prev.map((c) => ({ ...c, is_selected: c.id === charId })));
    } else {
      setError(result.error || "캐릭터 선택에 실패했습니다");
    }
    setSelecting(false);
  }

  return (
    <motion.div
      initial={{ opacity: 0, x: 30 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -30 }}
      transition={{ duration: 0.3 }}
      className="space-y-8"
    >
      {/* ── 그림체 선택 ── */}
      <section>
        <div className="text-center space-y-2 mb-6">
          <h2 className="text-2xl font-bold text-text">그림체 & 캐릭터</h2>
          <p className="text-text-light text-sm">그림체를 선택하고 캐릭터를 만들어주세요</p>
        </div>

        <p className="text-sm font-medium text-text mb-3">그림체 선택</p>
        <div className="grid grid-cols-3 sm:grid-cols-5 gap-2 sm:gap-3">
          {ART_STYLES.map((style) => {
            const isSelected = artStyle === style.id;
            const Icon = style.icon;
            const hasImage = !imgErrors[style.id];

            return (
              <motion.button
                key={style.id}
                whileTap={{ scale: 0.96 }}
                onClick={() => handleStyleChange(style.id)}
                disabled={savingStyle}
                className={`relative rounded-2xl border-2 overflow-hidden transition-all ${
                  isSelected
                    ? "border-primary shadow-md ring-2 ring-primary/20 ring-offset-1"
                    : "border-secondary/40 hover:border-secondary hover:shadow-sm"
                }`}
              >
                {/* 선택 체크 */}
                {isSelected && (
                  <motion.div
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    className="absolute top-1.5 right-1.5 z-10 w-5 h-5 rounded-full bg-primary flex items-center justify-center shadow"
                  >
                    <Check className="w-3 h-3 text-white" />
                  </motion.div>
                )}

                {/* 예시 이미지 영역 */}
                <div className={`aspect-[4/3] bg-gradient-to-br ${style.bg} flex items-center justify-center overflow-hidden`}>
                  {hasImage ? (
                    <Image
                      src={style.image}
                      alt={`${style.title} 예시`}
                      width={200}
                      height={150}
                      className="w-full h-full object-cover"
                      onError={() => setImgErrors((prev) => ({ ...prev, [style.id]: true }))}
                    />
                  ) : (
                    <Icon className="w-8 h-8 sm:w-10 sm:h-10 opacity-60" style={{ color: style.color }} />
                  )}
                </div>

                {/* 타이틀 */}
                <div className="px-1.5 py-2 text-center">
                  <p className={`text-xs sm:text-sm font-medium ${isSelected ? "text-primary-dark" : "text-text"}`}>
                    {style.title}
                  </p>
                  <p className="text-[10px] text-text-lighter hidden sm:block mt-0.5">{style.description}</p>
                </div>
              </motion.button>
            );
          })}
        </div>
      </section>

      {/* ── 구분선 ── */}
      <div className="border-t border-secondary/30" />

      {/* ── 캐릭터 미리보기 ── */}
      <section>
        <p className="text-sm font-medium text-text mb-4">캐릭터 미리보기</p>

        {error && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-4 p-3 bg-error/10 border border-error/30 rounded-xl text-center"
          >
            <span className="text-sm text-error-dark">{error}</span>
          </motion.div>
        )}

        {loadingChars ? (
          <div className="flex items-center justify-center py-16">
            <div className="animate-spin w-8 h-8 border-3 border-primary border-t-transparent rounded-full" />
          </div>
        ) : !hasCharacters ? (
          <div className="text-center py-10 space-y-5">
            <div className="w-20 h-20 mx-auto bg-secondary/30 rounded-full flex items-center justify-center">
              <User className="w-10 h-10 text-text-lighter" />
            </div>
            <div className="space-y-1">
              <p className="text-text-light">아직 생성된 캐릭터가 없어요</p>
              <p className="text-text-lighter text-sm">
                {artStyle ? "버튼을 눌러 캐릭터를 생성해보세요" : "그림체를 먼저 선택해주세요"}
              </p>
            </div>
            <Button
              onClick={handleGenerate}
              disabled={generating || !artStyle}
              size="lg"
              className="gap-2"
            >
              {generating ? (
                <>
                  <div className="animate-spin w-4 h-4 border-2 border-white border-t-transparent rounded-full" />
                  생성 중...
                </>
              ) : (
                <>
                  <ImageIcon className="w-5 h-5" />
                  캐릭터 생성하기
                </>
              )}
            </Button>
          </div>
        ) : (
          <>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 sm:gap-4">
              <AnimatePresence>
                {characters.map((char) => (
                  <motion.button
                    key={char.id}
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.9 }}
                    whileHover={{ scale: 1.03 }}
                    whileTap={{ scale: 0.97 }}
                    onClick={() => handleSelect(char.id)}
                    disabled={selecting}
                    className={`relative rounded-2xl border-2 overflow-hidden transition-all duration-200 ${
                      char.is_selected
                        ? "border-primary shadow-lg ring-2 ring-primary/30 ring-offset-2"
                        : "border-secondary/50 hover:border-secondary hover:shadow-md"
                    }`}
                  >
                    {char.is_selected && (
                      <motion.div
                        initial={{ scale: 0 }}
                        animate={{ scale: 1 }}
                        className="absolute top-2 right-2 z-10 w-6 h-6 rounded-full bg-primary flex items-center justify-center shadow-md"
                      >
                        <Check className="w-3.5 h-3.5 text-white" />
                      </motion.div>
                    )}
                    <div className="aspect-square bg-gradient-to-br from-secondary/30 to-accent/20 flex items-center justify-center overflow-hidden">
                      {char.image_path && !char.image_path.includes("dummy_") ? (
                        <img
                          src={`${API_BASE}${char.image_path}`}
                          alt={`캐릭터 #${char.generation_index + 1}`}
                          className="w-full h-full object-cover"
                          onError={(e) => {
                            const target = e.currentTarget;
                            target.style.display = "none";
                            const fallback = target.nextElementSibling as HTMLElement;
                            if (fallback) fallback.style.display = "flex";
                          }}
                        />
                      ) : null}
                      <div
                        className="text-center space-y-2 flex flex-col items-center justify-center w-full h-full"
                        style={{ display: char.image_path && !char.image_path.includes("dummy_") ? "none" : "flex" }}
                      >
                        <User className="w-12 h-12 text-text-lighter" />
                        <span className="text-xs text-text-lighter block">캐릭터 #{char.generation_index + 1}</span>
                      </div>
                    </div>
                  </motion.button>
                ))}
              </AnimatePresence>
            </div>

            <div className="flex items-center justify-center gap-4 mt-5">
              <Button
                onClick={handleGenerate}
                disabled={generating || !canRegenerate}
                variant="outline"
                className="gap-2"
              >
                {generating ? (
                  <>
                    <div className="animate-spin w-4 h-4 border-2 border-primary border-t-transparent rounded-full" />
                    생성 중...
                  </>
                ) : (
                  <>
                    <RefreshCw className="w-4 h-4" />
                    다른 캐릭터 생성
                  </>
                )}
              </Button>
              <span className="text-sm text-text-light">
                남은 횟수: <span className={`font-bold ${remainingRegens === 0 ? "text-error-dark" : "text-primary"}`}>{remainingRegens}회</span>
              </span>
            </div>

            <div className="text-center pt-4">
              <Button
                onClick={onConfirm}
                disabled={!selectedChar || selecting}
                size="lg"
                className="gap-2 px-8"
              >
                <Check className="w-5 h-5" />
                캐릭터 확정하기
              </Button>
              {!selectedChar && (
                <p className="text-xs text-text-lighter mt-2">캐릭터를 선택하면 확정할 수 있어요</p>
              )}
            </div>
          </>
        )}
      </section>
    </motion.div>
  );
}
