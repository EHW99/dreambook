"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { useRouter, useParams } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import {
  Play, Pause, SkipBack, SkipForward,
  ArrowLeft, ImageIcon, Volume2, VolumeX,
} from "lucide-react";
import { AuthGuard } from "@/components/auth-guard";
import { Button } from "@/components/ui/button";
import { apiClient, AudioBookData, AudioPageData } from "@/lib/api";

function AudiobookContent() {
  const router = useRouter();
  const params = useParams();
  const bookId = params?.id ? Number(params.id) : null;

  const [audioData, setAudioData] = useState<AudioBookData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [currentPage, setCurrentPage] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);

  const utteranceRef = useRef<SpeechSynthesisUtterance | null>(null);
  const synthRef = useRef<SpeechSynthesis | null>(null);

  // SpeechSynthesis 초기화
  useEffect(() => {
    if (typeof window !== "undefined") {
      synthRef.current = window.speechSynthesis;
    }
    return () => {
      // 클린업: 진행 중인 음성 중지
      if (synthRef.current) {
        synthRef.current.cancel();
      }
    };
  }, []);

  // 데이터 로드
  useEffect(() => {
    if (!bookId) return;
    loadAudioData(bookId);
  }, [bookId]);

  async function loadAudioData(id: number) {
    setLoading(true);
    const res = await apiClient.getAudioData(id);
    if (res.data) {
      setAudioData(res.data);
    } else {
      setError(res.error || "오디오 데이터를 불러올 수 없습니다");
    }
    setLoading(false);
  }

  const pages = audioData?.pages || [];
  const totalPages = pages.length;
  const currentPageData: AudioPageData | null = pages[currentPage] || null;

  // TTS로 현재 페이지 읽기
  const speakCurrentPage = useCallback(() => {
    if (!synthRef.current || !currentPageData?.text_content) return;

    // 이전 음성 중지
    synthRef.current.cancel();

    const utterance = new SpeechSynthesisUtterance(currentPageData.text_content);
    utterance.lang = "ko-KR";
    utterance.rate = 0.9; // 약간 느리게 (아동용)
    utterance.pitch = 1.1; // 약간 높게 (밝은 느낌)

    // 한국어 음성 찾기
    const voices = synthRef.current.getVoices();
    const koreanVoice = voices.find((v) => v.lang.startsWith("ko"));
    if (koreanVoice) {
      utterance.voice = koreanVoice;
    }

    utterance.onstart = () => {
      setIsSpeaking(true);
    };

    utterance.onend = () => {
      setIsSpeaking(false);
      // 자동 페이지 넘김
      if (currentPage < totalPages - 1) {
        setCurrentPage((prev) => prev + 1);
      } else {
        // 마지막 페이지 완료
        setIsPlaying(false);
      }
    };

    utterance.onerror = () => {
      setIsSpeaking(false);
    };

    utteranceRef.current = utterance;
    synthRef.current.speak(utterance);
  }, [currentPageData, currentPage, totalPages]);

  // isPlaying 변경 시 TTS 제어
  useEffect(() => {
    if (isPlaying && currentPageData?.text_content) {
      speakCurrentPage();
    } else if (!isPlaying && synthRef.current) {
      synthRef.current.cancel();
      setIsSpeaking(false);
    }
  }, [isPlaying, currentPage]);

  const handlePlayPause = () => {
    setIsPlaying((prev) => !prev);
  };

  const handlePrevPage = () => {
    if (currentPage > 0) {
      if (synthRef.current) synthRef.current.cancel();
      setCurrentPage((prev) => prev - 1);
    }
  };

  const handleNextPage = () => {
    if (currentPage < totalPages - 1) {
      if (synthRef.current) synthRef.current.cancel();
      setCurrentPage((prev) => prev + 1);
    }
  };

  const handleGoBack = () => {
    if (synthRef.current) synthRef.current.cancel();
    setIsPlaying(false);
    router.back();
  };

  // 진행률 계산
  const progress = totalPages > 0 ? ((currentPage + 1) / totalPages) * 100 : 0;

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#2a2420]">
        <div className="text-center space-y-4">
          <div className="animate-spin w-10 h-10 border-3 border-primary border-t-transparent rounded-full mx-auto" />
          <p className="text-white/60">오디오북을 준비하는 중...</p>
        </div>
      </div>
    );
  }

  if (error || !audioData) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="text-center space-y-4">
          <VolumeX className="w-12 h-12 text-text-lighter mx-auto" />
          <p className="text-error-dark">{error || "오디오 데이터를 찾을 수 없습니다"}</p>
          <Button onClick={() => router.push("/mypage")}>마이페이지로</Button>
        </div>
      </div>
    );
  }

  if (totalPages === 0) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="text-center space-y-4">
          <Volume2 className="w-12 h-12 text-text-lighter mx-auto" />
          <p className="text-text-light">아직 동화책 페이지가 없어요</p>
          <Button onClick={() => router.push("/mypage")}>마이페이지로</Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-[#2a2420] to-[#1a1510] flex flex-col">
      {/* 상단 헤더 */}
      <div className="flex items-center justify-between px-4 py-3 bg-black/20">
        <button
          onClick={handleGoBack}
          className="text-white/70 hover:text-white transition-colors flex items-center gap-2"
        >
          <ArrowLeft className="w-5 h-5" />
          <span className="text-sm hidden sm:inline">돌아가기</span>
        </button>
        <h3 className="text-white/80 text-sm font-medium truncate mx-4">
          {audioData.book_title || `${audioData.child_name}의 동화책`}
        </h3>
        <span className="text-white/50 text-xs">
          {currentPage + 1} / {totalPages}
        </span>
      </div>

      {/* 진행률 바 */}
      <div className="h-1 bg-white/10">
        <motion.div
          className="h-full bg-primary rounded-r-full"
          initial={{ width: 0 }}
          animate={{ width: `${progress}%` }}
          transition={{ duration: 0.3, ease: "easeOut" }}
        />
      </div>

      {/* 메인 컨텐츠 — 큰 일러스트 + 텍스트 */}
      <div className="flex-1 flex flex-col items-center justify-center px-4 py-6 overflow-hidden">
        <AnimatePresence mode="wait">
          <motion.div
            key={currentPage}
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -50 }}
            transition={{ duration: 0.3 }}
            className="w-full max-w-lg flex flex-col items-center gap-6"
          >
            {/* 일러스트 영역 */}
            <div className="w-full aspect-square max-w-[400px] rounded-3xl overflow-hidden bg-[#fef9f1] shadow-2xl">
              {currentPageData?.image_url ? (
                <img
                  src={currentPageData.image_url}
                  alt={`페이지 ${currentPage + 1} 일러스트`}
                  className="w-full h-full object-cover"
                />
              ) : (
                <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-secondary/30 to-primary/20">
                  <div className="text-center">
                    <ImageIcon className="w-16 h-16 text-primary/30 mx-auto mb-2" />
                    <p className="text-sm text-text-lighter">
                      일러스트 #{currentPageData?.page_number}
                    </p>
                  </div>
                </div>
              )}
            </div>

            {/* 텍스트 영역 */}
            <div className="w-full px-2">
              <p
                className={`text-center text-base sm:text-lg leading-relaxed font-medium break-words transition-colors duration-300 ${
                  isSpeaking ? "text-white" : "text-white/80"
                }`}
                style={{ fontFamily: "'Pretendard', sans-serif" }}
              >
                {currentPageData?.text_content || "..."}
              </p>
            </div>
          </motion.div>
        </AnimatePresence>
      </div>

      {/* 하단 컨트롤 바 */}
      <div className="bg-black/30 backdrop-blur-sm border-t border-white/5 px-4 py-4 sm:py-5">
        {/* 페이지 인디케이터 (작은 점들) */}
        <div className="flex items-center justify-center gap-1 mb-4">
          {pages.map((_, idx) => (
            <button
              key={idx}
              onClick={() => {
                if (synthRef.current) synthRef.current.cancel();
                setCurrentPage(idx);
              }}
              className={`rounded-full transition-all duration-200 ${
                idx === currentPage
                  ? "w-6 h-2 bg-primary"
                  : "w-2 h-2 bg-white/30 hover:bg-white/50"
              }`}
            />
          ))}
        </div>

        {/* 재생 컨트롤 */}
        <div className="flex items-center justify-center gap-6">
          {/* 이전 페이지 */}
          <button
            onClick={handlePrevPage}
            disabled={currentPage === 0}
            className="w-12 h-12 rounded-full bg-white/10 hover:bg-white/20 disabled:opacity-30 disabled:hover:bg-white/10 flex items-center justify-center transition-all"
          >
            <SkipBack className="w-5 h-5 text-white" />
          </button>

          {/* 재생/일시정지 */}
          <button
            onClick={handlePlayPause}
            className={`w-14 h-14 sm:w-16 sm:h-16 rounded-full flex items-center justify-center transition-all shadow-lg ${
              isPlaying
                ? "bg-primary hover:bg-primary/80"
                : "bg-primary hover:bg-primary/80"
            }`}
          >
            {isPlaying ? (
              <Pause className="w-7 h-7 text-white" />
            ) : (
              <Play className="w-7 h-7 text-white ml-1" />
            )}
          </button>

          {/* 다음 페이지 */}
          <button
            onClick={handleNextPage}
            disabled={currentPage === totalPages - 1}
            className="w-12 h-12 rounded-full bg-white/10 hover:bg-white/20 disabled:opacity-30 disabled:hover:bg-white/10 flex items-center justify-center transition-all"
          >
            <SkipForward className="w-5 h-5 text-white" />
          </button>
        </div>

        {/* 재생 상태 텍스트 */}
        <p className="text-center text-white/40 text-xs mt-3">
          {isPlaying
            ? isSpeaking
              ? "읽는 중..."
              : "다음 페이지 준비 중..."
            : "재생 버튼을 눌러주세요"}
        </p>
      </div>
    </div>
  );
}

export default function AudiobookPage() {
  return (
    <AuthGuard>
      <AudiobookContent />
    </AuthGuard>
  );
}
