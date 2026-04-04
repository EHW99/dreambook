"use client";

import { useState, useEffect, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { RefreshCw, Check, User, ImageIcon } from "lucide-react";
import { Button } from "@/components/ui/button";
import { apiClient, CharacterSheetItem } from "@/lib/api";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const MAX_GENERATIONS = 5; // 최초 1회 + 재생성 4회

interface StepCharacterPreviewProps {
  bookId: number;
  characterRegenCount: number;
  onConfirm: () => void | Promise<void>;
  onRegenCountUpdate: (count: number) => void;
}

export function StepCharacterPreview({
  bookId,
  characterRegenCount,
  onConfirm,
  onRegenCountUpdate,
}: StepCharacterPreviewProps) {
  const [characters, setCharacters] = useState<CharacterSheetItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [selecting, setSelecting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const selectedChar = characters.find((c) => c.is_selected);
  const totalGenerated = characters.length;
  const remainingRegens = MAX_GENERATIONS - totalGenerated;
  const canRegenerate = remainingRegens > 0;
  const hasCharacters = characters.length > 0;

  // 갤러리 로딩
  const loadCharacters = useCallback(async () => {
    const result = await apiClient.getCharacters(bookId);
    if (result.data) {
      setCharacters(result.data);
    }
    setLoading(false);
  }, [bookId]);

  useEffect(() => {
    loadCharacters();
  }, [loadCharacters]);

  // 캐릭터 생성
  async function handleGenerate() {
    setGenerating(true);
    setError(null);

    const result = await apiClient.createCharacter(bookId);
    if (result.data) {
      setCharacters((prev) => [...prev, result.data!]);
      // 첫 생성이 아니면 regen count 업데이트
      if (characters.length > 0) {
        onRegenCountUpdate(characters.length);
      }
    } else {
      setError(result.error || "캐릭터 생성에 실패했습니다");
    }
    setGenerating(false);
  }

  // 캐릭터 선택
  async function handleSelect(charId: number) {
    setSelecting(true);
    setError(null);

    const result = await apiClient.selectCharacter(bookId, charId);
    if (result.data) {
      setCharacters((prev) =>
        prev.map((c) => ({
          ...c,
          is_selected: c.id === charId,
        }))
      );
    } else {
      setError(result.error || "캐릭터 선택에 실패했습니다");
    }
    setSelecting(false);
  }

  if (loading) {
    return (
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="flex items-center justify-center py-20"
      >
        <div className="animate-spin w-8 h-8 border-3 border-primary border-t-transparent rounded-full" />
      </motion.div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, x: 30 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -30 }}
      transition={{ duration: 0.3 }}
      className="space-y-6"
    >
      <div className="text-center space-y-2">
        <h2 className="text-2xl font-bold text-text">캐릭터 미리보기</h2>
        <p className="text-text-light text-sm">
          아이의 캐릭터를 생성하고 마음에 드는 것을 선택해주세요
        </p>
      </div>

      {/* 에러 메시지 */}
      {error && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="p-3 bg-error/10 border border-error/30 rounded-xl text-center"
        >
          <span className="text-sm text-error-dark">{error}</span>
        </motion.div>
      )}

      {/* 캐릭터가 없을 때 */}
      {!hasCharacters && (
        <div className="text-center py-12 space-y-6">
          <div className="w-24 h-24 mx-auto bg-secondary/30 rounded-full flex items-center justify-center">
            <User className="w-12 h-12 text-text-lighter" />
          </div>
          <div className="space-y-2">
            <p className="text-text-light">아직 생성된 캐릭터가 없어요</p>
            <p className="text-text-lighter text-sm">아래 버튼을 눌러 캐릭터를 생성해보세요</p>
          </div>
          <Button
            onClick={handleGenerate}
            disabled={generating}
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
      )}

      {/* 캐릭터 갤러리 */}
      {hasCharacters && (
        <>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
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
                  {/* 선택 표시 */}
                  {char.is_selected && (
                    <motion.div
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      className="absolute top-2 right-2 z-10 w-6 h-6 rounded-full bg-primary flex items-center justify-center shadow-md"
                    >
                      <Check className="w-3.5 h-3.5 text-white" />
                    </motion.div>
                  )}

                  {/* 캐릭터 이미지 */}
                  <div className="aspect-square bg-gradient-to-br from-secondary/30 to-accent/20 flex items-center justify-center overflow-hidden">
                    {char.image_path && !char.image_path.includes("dummy_") ? (
                      <img
                        src={`${API_BASE}${char.image_path}`}
                        alt={`캐릭터 #${char.generation_index + 1}`}
                        className="w-full h-full object-cover"
                        onError={(e) => {
                          // 이미지 로딩 실패 시 placeholder로 폴백
                          const target = e.currentTarget;
                          target.style.display = "none";
                          const fallback = target.nextElementSibling as HTMLElement;
                          if (fallback) fallback.style.display = "flex";
                        }}
                      />
                    ) : null}
                    <div
                      className="text-center space-y-2 flex flex-col items-center justify-center w-full h-full"
                      style={{
                        display: char.image_path && !char.image_path.includes("dummy_") ? "none" : "flex",
                      }}
                    >
                      <User className="w-12 h-12 text-text-lighter" />
                      <span className="text-xs text-text-lighter block">
                        캐릭터 #{char.generation_index + 1}
                      </span>
                    </div>
                  </div>
                </motion.button>
              ))}
            </AnimatePresence>
          </div>

          {/* 재생성 버튼 + 남은 횟수 */}
          <div className="flex items-center justify-center gap-4">
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
                  재생성
                </>
              )}
            </Button>
            <span className="text-sm text-text-light">
              남은 횟수: <span className={`font-bold ${remainingRegens === 0 ? "text-error-dark" : "text-primary"}`}>{remainingRegens}회</span>
            </span>
          </div>

          {/* 확정 버튼 */}
          <div className="text-center pt-4">
            <Button
              onClick={onConfirm}
              disabled={!selectedChar || selecting}
              size="lg"
              className="gap-2 px-8"
            >
              <Check className="w-5 h-5" />
              확정하기
            </Button>
            {!selectedChar && hasCharacters && (
              <p className="text-xs text-text-lighter mt-2">
                캐릭터를 선택하면 확정할 수 있어요
              </p>
            )}
          </div>
        </>
      )}
    </motion.div>
  );
}
