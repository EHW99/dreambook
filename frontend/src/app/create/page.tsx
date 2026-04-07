"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { ArrowLeft, ArrowRight, AlertCircle, Sparkles, ImageIcon, RefreshCw } from "lucide-react";
import { AuthGuard } from "@/components/auth-guard";
import { Button } from "@/components/ui/button";
import { WizardProgress } from "@/components/create/wizard-progress";
import { StepInfoInput, validateInfoInput } from "@/components/create/step-info-input";
import { StepJobSelect, validateJobSelect } from "@/components/create/step-job-select";
import { validateArtStyle } from "@/components/create/step-art-style";
import { StepArtAndCharacter } from "@/components/create/step-art-and-character";
import { StepPlot, validatePlot } from "@/components/create/step-plot";
import { StepGenerating } from "@/components/create/step-generating";
import { apiClient, BookItem, PageItem } from "@/lib/api";

// 위자드 스텝: 1.정보 → 2.직업 → 3.스타일+캐릭터 → 4.줄거리 → 5.스토리생성 → 6.글편집 → 7.그림생성

function CreateWizardContent() {
  const router = useRouter();
  const searchParams = useSearchParams();

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // 현재 동화책 + 위자드 단계
  const [book, setBook] = useState<BookItem | null>(null);
  const [currentStep, setCurrentStep] = useState(1);

  // ── DEV 기본값 ──
  const isDev = process.env.NODE_ENV === "development";
  const DEV_DEFAULTS = {
    childName: "김서준",
    childGender: "male",
    childBirthDate: "2020-03-15",
    jobCategory: "안전/봉사",
    jobName: "소방관",
    artStyle: "watercolor",
    plotInput: "",
  };

  // 정보 입력 상태
  const [childName, setChildName] = useState(isDev ? DEV_DEFAULTS.childName : "");
  const [childGender, setChildGender] = useState(isDev ? DEV_DEFAULTS.childGender : "");
  const [childBirthDate, setChildBirthDate] = useState(isDev ? DEV_DEFAULTS.childBirthDate : "");
  const [photoId, setPhotoId] = useState<number | null>(null);
  const [infoErrors, setInfoErrors] = useState<{ name?: string; gender?: string; birthDate?: string }>({});

  // 직업 선택 상태
  const [jobCategory, setJobCategory] = useState(isDev ? DEV_DEFAULTS.jobCategory : "");
  const [jobName, setJobName] = useState(isDev ? DEV_DEFAULTS.jobName : "");
  const [jobError, setJobError] = useState<string | null>(null);

  // 그림체 상태
  const [artStyle, setArtStyle] = useState(isDev ? DEV_DEFAULTS.artStyle : "");
  const [styleError, setStyleError] = useState<string | null>(null);

  // 캐릭터 미리보기 상태
  const [characterConfirmed, setCharacterConfirmed] = useState(false);

  // 옵션 상태
  const [bookSpecUid, setBookSpecUid] = useState("SQUAREBOOK_HC");

  // 줄거리 상태
  const [plotInput, setPlotInput] = useState("");

  // step 6: 글편집용 페이지 데이터
  const [storyPages, setStoryPages] = useState<PageItem[]>([]);
  const [editingPageId, setEditingPageId] = useState<number | null>(null);
  const [editText, setEditText] = useState("");

  // step 6: 스토리 재생성
  const [regeneratingStory, setRegeneratingStory] = useState(false);

  // step 7: 그림 생성 상태
  const [isGeneratingIllust, setIsGeneratingIllust] = useState(false);

  // Strict Mode 이중 실행 방지
  const initRef = useRef(false);
  const pendingUpdate = useRef<{ child_name?: string; child_gender?: string; child_birth_date?: string }>({});

  // beforeunload
  useEffect(() => {
    function handleBeforeUnload(e: BeforeUnloadEvent) {
      e.preventDefault();
      e.returnValue = "";
    }
    window.addEventListener("beforeunload", handleBeforeUnload);
    return () => window.removeEventListener("beforeunload", handleBeforeUnload);
  }, []);

  // 초기화
  useEffect(() => {
    if (initRef.current) return;
    initRef.current = true;
    initWizard();
  }, []);

  async function initWizard() {
    setLoading(true);

    const bookIdParam = searchParams.get("book_id");
    if (bookIdParam) {
      const result = await apiClient.getBook(Number(bookIdParam));
      if (result.data) {
        loadBookState(result.data);
        setLoading(false);
        return;
      }
      setError("동화책을 불러올 수 없습니다");
      setLoading(false);
      return;
    }

    const voucherIdParam = searchParams.get("voucher_id");
    if (voucherIdParam) {
      const result = await apiClient.createBook(Number(voucherIdParam));
      if (result.data) {
        // URL을 book_id 기반으로 교체 (새로고침 시 이용권 재사용 방지)
        router.replace(`/create?book_id=${result.data.id}`);
        loadBookState(result.data);
        setLoading(false);
        return;
      } else {
        setError(result.error || "동화책 생성에 실패했습니다");
        setLoading(false);
        return;
      }
    }

    router.replace("/");
  }

  function loadBookState(bookData: BookItem) {
    setBook(bookData);
    setCurrentStep(bookData.current_step);
    setChildName(bookData.child_name || (isDev ? DEV_DEFAULTS.childName : ""));
    setChildGender(bookData.child_gender || (isDev ? DEV_DEFAULTS.childGender : ""));
    setChildBirthDate(bookData.child_birth_date || (isDev ? DEV_DEFAULTS.childBirthDate : ""));
    setPhotoId(bookData.photo_id);
    setJobCategory(bookData.job_category || (isDev ? DEV_DEFAULTS.jobCategory : ""));
    setJobName(bookData.job_name || (isDev ? DEV_DEFAULTS.jobName : ""));
    setArtStyle(bookData.art_style || (isDev ? DEV_DEFAULTS.artStyle : ""));
    setBookSpecUid(bookData.book_spec_uid || "SQUAREBOOK_HC");
    setPlotInput(bookData.plot_input || "");
    setCharacterConfirmed(bookData.status === "character_confirmed" || bookData.current_step > 3);

    // story_generated 상태면 step 6으로
    if (bookData.status === "story_generated" && bookData.current_step <= 6) {
      setCurrentStep(6);
      loadStoryPages(bookData.id);
    }
    // editing 상태면 step 7 완료 → edit 페이지로
    if (bookData.status === "editing") {
      router.push(`/create/edit?book_id=${bookData.id}`);
    }
  }

  async function loadStoryPages(bookId: number) {
    const result = await apiClient.getPages(bookId);
    if (result.data) {
      setStoryPages(result.data);
    }
  }

  // 다음 버튼
  async function handleNext() {
    if (!book) return;
    setError(null);

    if (currentStep === 1) {
      const nameToValidate = pendingUpdate.current.child_name ?? childName;
      const genderToValidate = pendingUpdate.current.child_gender ?? childGender;
      const birthToValidate = pendingUpdate.current.child_birth_date ?? childBirthDate;
      const validation = validateInfoInput({ childName: nameToValidate, childGender: genderToValidate, childBirthDate: birthToValidate });
      if (!validation.valid) { setInfoErrors(validation.errors); return; }
      setInfoErrors({});

      setSaving(true);
      const updateData: Record<string, unknown> = {
        child_name: nameToValidate.trim(),
        child_gender: genderToValidate,
        child_birth_date: birthToValidate,
        current_step: 2,
      };

      const result = await apiClient.updateBook(book.id, updateData as Record<string, string | number>);
      setSaving(false);
      if (result.data) { loadBookState(result.data); setCurrentStep(2); }
      else setError(result.error || "저장에 실패했습니다");

    } else if (currentStep === 2) {
      const validation = validateJobSelect({ jobCategory, jobName });
      if (!validation.valid) { setJobError(validation.error || null); return; }
      setJobError(null);

      setSaving(true);
      const result = await apiClient.updateBook(book.id, { job_category: jobCategory, job_name: jobName, current_step: 3 });
      setSaving(false);
      if (result.data) { loadBookState(result.data); setCurrentStep(3); }
      else setError(result.error || "저장에 실패했습니다");

    } else if (currentStep === 3) {
      const validation = validateArtStyle(artStyle);
      if (!validation.valid) { setStyleError(validation.error || null); return; }
      setStyleError(null);
      if (!characterConfirmed) { setError("캐릭터를 확정해주세요"); return; }

      setSaving(true);
      const result = await apiClient.updateBook(book.id, { art_style: artStyle, current_step: 4, status: "character_confirmed" });
      setSaving(false);
      if (result.data) { loadBookState(result.data); setCurrentStep(4); }
      else setError(result.error || "저장에 실패했습니다");

    } else if (currentStep === 4) {
      const validation = validatePlot(plotInput);
      if (!validation.valid) { setError(validation.error); return; }

      setSaving(true);
      const result = await apiClient.updateBook(book.id, {
        plot_input: plotInput.trim(),
        page_count: 24,
        book_spec_uid: bookSpecUid,
        current_step: 5,
      });
      setSaving(false);
      if (result.data) { loadBookState(result.data); setCurrentStep(5); }
      else setError(result.error || "저장에 실패했습니다");

    } else if (currentStep === 6) {
      // 글편집 완료 → 그림 생성 안내 (step 7)
      setCurrentStep(7);
    }
  }

  // 뒤로가기
  function handleBack() {
    if (currentStep === 5) return; // 스토리 생성 단계에서는 뒤로가기 차단
    if (currentStep === 7 && isGeneratingIllust) return;
    setError(null);
    if (currentStep === 1) {
      router.push("/mypage");
    } else if (currentStep === 6) {
      // 글편집에서 뒤로가면 줄거리로 (스토리 재생성 의미)
      setCurrentStep(4);
    } else {
      setCurrentStep(currentStep - 1);
    }
  }

  const handleInfoUpdate = useCallback(
    (data: { child_name?: string; child_gender?: string; child_birth_date?: string }) => {
      pendingUpdate.current = data;
      if (data.child_name !== undefined) setChildName(data.child_name);
      if (data.child_gender !== undefined) setChildGender(data.child_gender);
      if (data.child_birth_date !== undefined) setChildBirthDate(data.child_birth_date);
    }, []
  );

  const handleJobSelect = useCallback((category: string, job: string) => {
    setJobCategory(category);
    setJobName(job);
    setJobError(null);
  }, []);

  // 글편집: 텍스트 저장
  async function handleRegenerateStory() {
    if (!book || regeneratingStory) return;
    if (book.story_regen_count >= 3) return;
    if (!confirm("스토리를 재생성하면 현재 텍스트가 모두 초기화됩니다.\n\n계속하시겠습니까?")) return;
    setRegeneratingStory(true);
    const res = await apiClient.regenerateStory(book.id);
    if (res.data) {
      setBook({ ...book, story_regen_count: (book.story_regen_count || 0) + 1, status: res.data.status });
      setStoryPages(res.data.pages || []);
    } else {
      setError(res.error || "스토리 재생성에 실패했습니다");
    }
    setRegeneratingStory(false);
  }

  async function handleStartIllustration() {
    if (!book) return;
    setIsGeneratingIllust(true);
    const result = await apiClient.generateIllustrations(book.id);
    setIsGeneratingIllust(false);
    if (result.data) {
      router.push(`/create/edit?book_id=${book.id}`);
    } else {
      setError(result.error || "그림 생성에 실패했습니다");
      setCurrentStep(6);
    }
  }

  async function handleSaveStoryText(pageId: number) {
    if (!book) return;
    const result = await apiClient.updatePageText(book.id, pageId, editText);
    if (result.data) {
      setStoryPages((prev) => prev.map((p) => (p.id === pageId ? { ...p, text_content: editText } : p)));
      setEditingPageId(null);
      setEditText("");
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="text-center space-y-4">
          <div className="animate-spin w-10 h-10 border-3 border-primary border-t-transparent rounded-full mx-auto" />
          <p className="text-text-light">준비 중...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background flex flex-col">
      {/* 헤더 + 진행 바 */}
      <div className="sticky top-0 z-10 bg-background/90 backdrop-blur-sm border-b border-secondary/30">
        <div className="max-w-3xl mx-auto px-4 py-3">
          <div className="flex items-center justify-between mb-3">
            <h1 className="text-lg font-bold text-text">동화책 만들기</h1>
            <button onClick={() => router.push("/mypage")} className="text-sm text-text-light hover:text-text transition-colors">
              나중에 하기
            </button>
          </div>
          <WizardProgress currentStep={currentStep} variant="B" />
        </div>
      </div>

      {/* 본문 */}
      <div className="flex-1 max-w-2xl mx-auto w-full px-3 sm:px-4 py-6 sm:py-8">
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-6 p-4 bg-error/10 border border-error/30 rounded-2xl flex items-center gap-3"
          >
            <AlertCircle className="w-5 h-5 text-error-dark flex-shrink-0" />
            <span className="text-sm text-error-dark">{error}</span>
          </motion.div>
        )}

        <AnimatePresence mode="wait">
          {currentStep === 1 && (
            <StepInfoInput
              key="step-1"
              childName={childName} childGender={childGender} childBirthDate={childBirthDate}
              onUpdate={handleInfoUpdate}
              onValidate={() => { const v = validateInfoInput({ childName, childGender, childBirthDate }); setInfoErrors(v.errors); return v.valid; }}
            />
          )}
          {currentStep === 2 && (
            <StepJobSelect key="step-2" selectedCategory={jobCategory} selectedJob={jobName} onSelect={handleJobSelect} />
          )}
          {currentStep === 3 && book && (
            <StepArtAndCharacter
              key="step-3"
              bookId={book.id} artStyle={artStyle} photoId={photoId} characterRegenCount={book.character_regen_count}
              onArtStyleChange={(style) => { setArtStyle(style); setStyleError(null); }}
              onArtStyleSaved={async () => { const r = await apiClient.getBook(book.id); if (r.data) loadBookState(r.data); }}
              onPhotoChange={(id) => setPhotoId(id)}
              onConfirm={async () => {
                const chars = await apiClient.getCharacters(book.id);
                const hasSelected = chars.data?.some((c) => c.is_selected) ?? false;
                setCharacterConfirmed(hasSelected);
              }}
              onRegenCountUpdate={(count) => { if (book) setBook({ ...book, character_regen_count: count }); }}
            />
          )}
          {currentStep === 4 && (
            <StepPlot key="step-4" bookId={book!.id} plotInput={plotInput} jobName={book?.job_name || null} onPlotChange={setPlotInput} />
          )}

          {/* step 5: 스토리 생성 */}
          {currentStep === 5 && book && (
            <StepGenerating
              key="step-5"
              bookId={book.id}
              onComplete={async () => {
                await loadStoryPages(book.id);
                setCurrentStep(6);
              }}
              onError={(msg) => { setError(msg); setCurrentStep(4); }}
            />
          )}

          {/* step 6: 글 편집 */}
          {currentStep === 6 && (
            <motion.div key="step-6" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }}>
              <div className="text-center mb-4">
                <h2 className="text-xl font-bold text-text mb-2">이야기를 확인하고 편집하세요</h2>
                <p className="text-sm text-text-light">
                  AI가 만든 스토리를 확인하고, 원하는 대로 수정할 수 있어요.<br />
                  편집이 끝나면 이 텍스트를 기반으로 그림을 그려요.
                </p>
              </div>

              {/* 스토리 재생성 */}
              <div className="flex items-center justify-between mb-4 px-1">
                <p className="text-xs text-text-lighter">
                  스토리 재생성은 이 단계에서만 가능합니다 ({book?.story_regen_count || 0}/3회 사용)
                </p>
                <button
                  onClick={handleRegenerateStory}
                  disabled={regeneratingStory || (book?.story_regen_count ?? 0) >= 3}
                  className="text-xs px-3 py-1.5 rounded-lg border border-secondary hover:border-primary hover:text-primary disabled:opacity-40 disabled:cursor-not-allowed transition-colors flex items-center gap-1"
                >
                  <RefreshCw className={`w-3 h-3 ${regeneratingStory ? "animate-spin" : ""}`} />
                  {regeneratingStory ? "재생성 중..." : "스토리 재생성"}
                </button>
              </div>

              <div className="space-y-3 max-h-[60vh] overflow-y-auto pr-1">
                {storyPages
                  .filter((p) => p.page_type === "story")
                  .map((page) => (
                    <div key={page.id} className="bg-white rounded-2xl border border-secondary/30 p-4 shadow-sm">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-xs font-bold text-primary bg-primary/10 px-2 py-0.5 rounded-full">
                          {page.page_number}p
                        </span>
                        {editingPageId !== page.id && (
                          <button
                            onClick={() => { setEditingPageId(page.id); setEditText(page.text_content || ""); }}
                            className="text-xs text-text-light hover:text-primary transition-colors"
                          >
                            편집
                          </button>
                        )}
                      </div>

                      {editingPageId === page.id ? (
                        <div>
                          <textarea
                            value={editText}
                            onChange={(e) => setEditText(e.target.value)}
                            className="w-full min-h-[100px] p-3 border border-secondary rounded-xl text-sm leading-relaxed font-display focus:outline-none focus:ring-2 focus:ring-primary/40 resize-none"
                            autoFocus
                          />
                          <div className="flex gap-2 mt-2 justify-end">
                            <button
                              onClick={() => { setEditingPageId(null); setEditText(""); }}
                              className="text-xs text-text-light hover:text-text px-3 py-1.5 rounded-lg"
                            >
                              취소
                            </button>
                            <button
                              onClick={() => handleSaveStoryText(page.id)}
                              className="text-xs text-white bg-primary hover:bg-primary/90 px-3 py-1.5 rounded-lg font-medium"
                            >
                              저장
                            </button>
                          </div>
                        </div>
                      ) : (
                        <p className="text-sm leading-relaxed text-text font-display whitespace-pre-wrap">
                          {page.text_content || "(텍스트 없음)"}
                        </p>
                      )}
                    </div>
                  ))}
              </div>
            </motion.div>
          )}

          {/* step 7: 그림 생성 */}
          {currentStep === 7 && !isGeneratingIllust && (
            <motion.div key="step-7-ready" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }}
              className="flex flex-col items-center justify-center min-h-[400px] space-y-8"
            >
              <div className="w-20 h-20 bg-primary/10 rounded-full flex items-center justify-center">
                <ImageIcon className="w-10 h-10 text-primary" />
              </div>
              <div className="text-center space-y-3 max-w-sm">
                <h2 className="text-xl font-bold text-text">그림을 그릴 준비가 되었어요</h2>
                <p className="text-sm text-text-light leading-relaxed">
                  편집한 이야기를 바탕으로 AI가 11장의 일러스트와 표지를 그려요.
                </p>
              </div>
              <Button onClick={handleStartIllustration} size="lg" className="gap-2">
                <Sparkles className="w-5 h-5" />
                그림 생성하기
              </Button>
              <p className="text-xs text-text-lighter">생성에 약 2~5분이 소요됩니다</p>
            </motion.div>
          )}
          {currentStep === 7 && isGeneratingIllust && (
            <motion.div key="step-7-gen" initial={{ opacity: 0 }} animate={{ opacity: 1 }}
              className="flex flex-col items-center justify-center min-h-[400px] space-y-8"
            >
              <div className="relative">
                <div className="w-32 h-32 rounded-full border-4 border-secondary flex items-center justify-center">
                  <motion.div animate={{ rotate: 360 }} transition={{ duration: 3, repeat: Infinity, ease: "linear" }}>
                    <ImageIcon className="w-10 h-10 text-primary" />
                  </motion.div>
                </div>
              </div>
              <div className="text-center space-y-2">
                <p className="text-lg font-bold text-text">그림을 그리고 있어요...</p>
                <p className="text-sm text-text-light">편집한 이야기를 바탕으로 일러스트를 생성하고 있어요</p>
              </div>
              <div className="bg-warning/10 border border-warning/30 rounded-2xl px-4 py-3 max-w-sm">
                <p className="text-xs text-text-light text-center">이 화면을 닫지 마세요.</p>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* 유효성 에러 */}
        {currentStep === 1 && (infoErrors.name || infoErrors.birthDate) && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="mt-4 p-3 bg-error/10 border border-error/20 rounded-xl">
            {infoErrors.name && <p className="text-sm text-error-dark flex items-center gap-1"><AlertCircle className="w-3.5 h-3.5" /> {infoErrors.name}</p>}
            {infoErrors.birthDate && <p className="text-sm text-error-dark flex items-center gap-1 mt-1"><AlertCircle className="w-3.5 h-3.5" /> {infoErrors.birthDate}</p>}
          </motion.div>
        )}
        {currentStep === 2 && jobError && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="mt-4 p-3 bg-error/10 border border-error/20 rounded-xl">
            <p className="text-sm text-error-dark flex items-center gap-1"><AlertCircle className="w-3.5 h-3.5" /> {jobError}</p>
          </motion.div>
        )}
      </div>

      {/* 하단 네비게이션 — 생성 중에는 숨김 */}
      {currentStep !== 5 && !(currentStep === 7 && isGeneratingIllust) && (
        <div className="sticky bottom-0 bg-background/90 backdrop-blur-sm border-t border-secondary/30">
          <div className="max-w-2xl mx-auto px-4 py-4 flex items-center justify-between">
            <Button variant="ghost" onClick={handleBack} className="gap-2">
              <ArrowLeft className="w-4 h-4" />
              {currentStep === 1 ? "취소" : "이전"}
            </Button>

            <Button
              onClick={handleNext}
              disabled={saving || (currentStep === 3 && !characterConfirmed)}
              className="gap-2"
            >
              {saving ? (
                <>
                  <div className="animate-spin w-4 h-4 border-2 border-white border-t-transparent rounded-full" />
                  저장 중...
                </>
              ) : currentStep === 4 ? (
                <>
                  <Sparkles className="w-4 h-4" />
                  스토리 생성하기
                </>
              ) : currentStep === 6 ? (
                <>
                  <ImageIcon className="w-4 h-4" />
                  그림 생성하기
                </>
              ) : (
                <>
                  다음
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}

export default function CreatePage() {
  return (
    <AuthGuard>
      <CreateWizardContent />
    </AuthGuard>
  );
}
