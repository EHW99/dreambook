"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { ArrowLeft, ArrowRight, AlertCircle, Sparkles } from "lucide-react";
import { AuthGuard } from "@/components/auth-guard";
import { Button } from "@/components/ui/button";
import { WizardProgress } from "@/components/create/wizard-progress";
import { StepInfoInput, validateInfoInput } from "@/components/create/step-info-input";
import { StepJobSelect, validateJobSelect } from "@/components/create/step-job-select";
import { StepStoryStyle, validateStoryStyle } from "@/components/create/step-story-style";
import { StepArtStyle, validateArtStyle } from "@/components/create/step-art-style";
import { StepCharacterPreview } from "@/components/create/step-character-preview";
import { StepOptions, validateOptions } from "@/components/create/step-options";
import { StepPlot, validatePlot } from "@/components/create/step-plot";
import { StepGenerating } from "@/components/create/step-generating";
import { apiClient, BookItem, VoucherItem } from "@/lib/api";

function CreateWizardContent() {
  const router = useRouter();
  const searchParams = useSearchParams();

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // 현재 동화책 + 위자드 단계
  const [book, setBook] = useState<BookItem | null>(null);
  const [currentStep, setCurrentStep] = useState(1);

  // ── DEV 기본값 (개발 편의용, 프로덕션에서는 빈 값) ──
  const isDev = process.env.NODE_ENV === "development";
  const DEV_DEFAULTS = {
    childName: "김서준",
    childBirthDate: "2020-03-15",
    jobCategory: "안전/봉사",
    jobName: "소방관",
    storyStyle: "dreaming_today",
    artStyle: "watercolor",
    plotInput: "",
  };

  // 정보 입력 상태
  const [childName, setChildName] = useState(isDev ? DEV_DEFAULTS.childName : "");
  const [childBirthDate, setChildBirthDate] = useState(isDev ? DEV_DEFAULTS.childBirthDate : "");
  const [photoId, setPhotoId] = useState<number | null>(null);
  const [infoErrors, setInfoErrors] = useState<{ name?: string; birthDate?: string }>({});

  // 직업 선택 상태
  const [jobCategory, setJobCategory] = useState(isDev ? DEV_DEFAULTS.jobCategory : "");
  const [jobName, setJobName] = useState(isDev ? DEV_DEFAULTS.jobName : "");
  const [jobError, setJobError] = useState<string | null>(null);

  // 동화 스타일 + 그림체 상태
  const [storyStyle, setStoryStyle] = useState(isDev ? DEV_DEFAULTS.storyStyle : "");
  const [artStyle, setArtStyle] = useState(isDev ? DEV_DEFAULTS.artStyle : "");
  const [styleError, setStyleError] = useState<string | null>(null);

  // 캐릭터 미리보기 상태
  const [characterConfirmed, setCharacterConfirmed] = useState(false);

  // 옵션 상태
  const [pageCount, setPageCount] = useState(24);
  const [bookSpecUid, setBookSpecUid] = useState("SQUAREBOOK_HC");

  // 줄거리 상태
  const [plotInput, setPlotInput] = useState("");

  // 생성 상태
  const [isGenerating, setIsGenerating] = useState(false);

  // 임시 데이터 ref (StepInfoInput에서 업데이트)
  const pendingUpdate = useRef<{ child_name?: string; child_birth_date?: string; photo_id?: number }>({});

  // beforeunload 이탈 방지
  useEffect(() => {
    function handleBeforeUnload(e: BeforeUnloadEvent) {
      e.preventDefault();
      e.returnValue = "";
    }
    window.addEventListener("beforeunload", handleBeforeUnload);
    return () => window.removeEventListener("beforeunload", handleBeforeUnload);
  }, []);

  // 초기화: 이용권 확인 → 동화책 생성 또는 기존 동화책 불러오기
  useEffect(() => {
    initWizard();
  }, []);

  async function initWizard() {
    setLoading(true);

    // URL 파라미터에 book_id가 있으면 기존 동화책 불러오기
    const bookIdParam = searchParams.get("book_id");
    if (bookIdParam) {
      const result = await apiClient.getBook(Number(bookIdParam));
      if (result.data) {
        loadBookState(result.data);
        setLoading(false);
        return;
      }
    }

    // URL 파라미터에 voucher_id가 있으면 새 동화책 생성
    const voucherIdParam = searchParams.get("voucher_id");
    if (voucherIdParam) {
      const result = await apiClient.createBook(Number(voucherIdParam));
      if (result.data) {
        loadBookState(result.data);
        setLoading(false);
        return;
      } else {
        setError(result.error || "동화책 생성에 실패했습니다");
        setLoading(false);
        return;
      }
    }

    // 아무 파라미터도 없으면 이용권 확인
    const voucherResult = await apiClient.getVouchers();
    if (voucherResult.data) {
      const available = voucherResult.data.filter(
        (v: VoucherItem) => v.status === "purchased"
      );
      if (available.length === 0) {
        // 이용권 없음 → 구매 페이지로
        router.replace("/vouchers");
        return;
      }
      // 이용권 있으면 첫 번째 것으로 동화책 생성
      const createResult = await apiClient.createBook(available[0].id);
      if (createResult.data) {
        loadBookState(createResult.data);
      } else {
        setError(createResult.error || "동화책 생성에 실패했습니다");
      }
    }
    setLoading(false);
  }

  function loadBookState(bookData: BookItem) {
    setBook(bookData);
    setCurrentStep(bookData.current_step);
    setChildName(bookData.child_name || (isDev ? DEV_DEFAULTS.childName : ""));
    setChildBirthDate(bookData.child_birth_date || (isDev ? DEV_DEFAULTS.childBirthDate : ""));
    setPhotoId(bookData.photo_id);
    setJobCategory(bookData.job_category || (isDev ? DEV_DEFAULTS.jobCategory : ""));
    setJobName(bookData.job_name || (isDev ? DEV_DEFAULTS.jobName : ""));
    setStoryStyle(bookData.story_style || (isDev ? DEV_DEFAULTS.storyStyle : ""));
    setArtStyle(bookData.art_style || (isDev ? DEV_DEFAULTS.artStyle : ""));
    setPageCount(bookData.page_count || 24);
    setBookSpecUid(bookData.book_spec_uid || "SQUAREBOOK_HC");
    setPlotInput(bookData.plot_input || "");
    // 캐릭터 확정 상태는 status로 판단
    setCharacterConfirmed(bookData.status === "character_confirmed" || bookData.current_step > 5);
    // 생성 중 상태 복원
    setIsGenerating(bookData.status === "generating");
  }

  // 다음 버튼 핸들러
  async function handleNext() {
    if (!book) return;
    setError(null);

    if (currentStep === 1) {
      // 정보 입력 유효성 검사
      const nameToValidate = pendingUpdate.current.child_name ?? childName;
      const birthToValidate = pendingUpdate.current.child_birth_date ?? childBirthDate;

      const validation = validateInfoInput({
        childName: nameToValidate,
        childBirthDate: birthToValidate,
      });
      if (!validation.valid) {
        setInfoErrors(validation.errors);
        return;
      }
      setInfoErrors({});

      // 서버 저장
      setSaving(true);
      const updateData: Record<string, unknown> = {
        child_name: nameToValidate.trim(),
        child_birth_date: birthToValidate,
        current_step: 2,
      };
      if (pendingUpdate.current.photo_id) {
        updateData.photo_id = pendingUpdate.current.photo_id;
      } else if (photoId) {
        updateData.photo_id = photoId;
      }

      const result = await apiClient.updateBook(book.id, updateData as Record<string, string | number>);
      setSaving(false);

      if (result.data) {
        loadBookState(result.data);
        setCurrentStep(2);
      } else {
        setError(result.error || "저장에 실패했습니다");
      }
    } else if (currentStep === 2) {
      // 직업 선택 유효성 검사
      const validation = validateJobSelect({ jobCategory, jobName });
      if (!validation.valid) {
        setJobError(validation.error || null);
        return;
      }
      setJobError(null);

      // 서버 저장
      setSaving(true);
      const result = await apiClient.updateBook(book.id, {
        job_category: jobCategory,
        job_name: jobName,
        current_step: 3,
      });
      setSaving(false);

      if (result.data) {
        loadBookState(result.data);
        setCurrentStep(3);
      } else {
        setError(result.error || "저장에 실패했습니다");
      }
    } else if (currentStep === 3) {
      // 동화 스타일 유효성 검사
      const validation = validateStoryStyle(storyStyle);
      if (!validation.valid) {
        setStyleError(validation.error || null);
        return;
      }
      setStyleError(null);

      // 서버 저장
      setSaving(true);
      const result = await apiClient.updateBook(book.id, {
        story_style: storyStyle,
        current_step: 4,
      });
      setSaving(false);

      if (result.data) {
        loadBookState(result.data);
        setCurrentStep(4);
      } else {
        setError(result.error || "저장에 실패했습니다");
      }
    } else if (currentStep === 4) {
      // 그림체 유효성 검사
      const validation = validateArtStyle(artStyle);
      if (!validation.valid) {
        setStyleError(validation.error || null);
        return;
      }
      setStyleError(null);

      // 서버 저장
      setSaving(true);
      const result = await apiClient.updateBook(book.id, {
        art_style: artStyle,
        current_step: 5,
      });
      setSaving(false);

      if (result.data) {
        loadBookState(result.data);
        setCurrentStep(5);
      } else {
        setError(result.error || "저장에 실패했습니다");
      }
    } else if (currentStep === 5) {
      // 캐릭터 미리보기 — 확정 필요
      if (!characterConfirmed) {
        setError("캐릭터를 확정해주세요");
        return;
      }

      // 서버 저장 (status도 character_confirmed로 보장)
      setSaving(true);
      const result = await apiClient.updateBook(book.id, {
        current_step: 6,
        status: "character_confirmed",
      });
      setSaving(false);

      if (result.data) {
        loadBookState(result.data);
        setCurrentStep(6);
      } else {
        setError(result.error || "저장에 실패했습니다");
      }
    } else if (currentStep === 6) {
      // 옵션 선택 유효성 검사
      const validation = validateOptions(pageCount, bookSpecUid);
      if (!validation.valid) {
        setError(validation.error);
        return;
      }

      // 서버 저장
      setSaving(true);
      const result = await apiClient.updateBook(book.id, {
        page_count: pageCount,
        book_spec_uid: bookSpecUid,
        current_step: 7,
      });
      setSaving(false);

      if (result.data) {
        loadBookState(result.data);
        setCurrentStep(7);
      } else {
        setError(result.error || "저장에 실패했습니다");
      }
    } else if (currentStep === 7) {
      // 줄거리 유효성 검사
      const validation = validatePlot(plotInput);
      if (!validation.valid) {
        setError(validation.error);
        return;
      }

      // 줄거리 저장
      setSaving(true);
      const result = await apiClient.updateBook(book.id, {
        plot_input: plotInput.trim(),
        current_step: 8,
      });
      setSaving(false);

      if (result.data) {
        loadBookState(result.data);
        setCurrentStep(8);
        setIsGenerating(true);
      } else {
        setError(result.error || "저장에 실패했습니다");
      }
    }
  }

  // 뒤로가기
  function handleBack() {
    if (currentStep === 8 && isGenerating) {
      // 생성 중에는 뒤로가기 차단
      return;
    }
    setError(null);
    if (currentStep === 1) {
      router.push("/mypage");
    } else {
      setCurrentStep(currentStep - 1);
    }
  }

  // StepInfoInput에서 데이터 업데이트 수신
  const handleInfoUpdate = useCallback(
    (data: { child_name?: string; child_birth_date?: string; photo_id?: number }) => {
      pendingUpdate.current = data;
      if (data.child_name !== undefined) setChildName(data.child_name);
      if (data.child_birth_date !== undefined) setChildBirthDate(data.child_birth_date);
      if (data.photo_id !== undefined) setPhotoId(data.photo_id);
    },
    []
  );

  // 직업 선택
  const handleJobSelect = useCallback((category: string, job: string) => {
    setJobCategory(category);
    setJobName(job);
    setJobError(null);
  }, []);

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
            <button
              onClick={() => router.push("/mypage")}
              className="text-sm text-text-light hover:text-text transition-colors"
            >
              나중에 하기
            </button>
          </div>
          <WizardProgress currentStep={currentStep} />
        </div>
      </div>

      {/* 본문 */}
      <div className="flex-1 max-w-2xl mx-auto w-full px-4 py-8">
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
              childName={childName}
              childBirthDate={childBirthDate}
              photoId={photoId}
              onUpdate={handleInfoUpdate}
              onValidate={() => {
                const v = validateInfoInput({ childName, childBirthDate });
                setInfoErrors(v.errors);
                return v.valid;
              }}
            />
          )}
          {currentStep === 2 && (
            <StepJobSelect
              key="step-2"
              selectedCategory={jobCategory}
              selectedJob={jobName}
              onSelect={handleJobSelect}
            />
          )}
          {currentStep === 3 && (
            <StepStoryStyle
              key="step-3"
              selected={storyStyle}
              onSelect={(style) => {
                setStoryStyle(style);
                setStyleError(null);
              }}
            />
          )}
          {currentStep === 4 && (
            <StepArtStyle
              key="step-4"
              selected={artStyle}
              onSelect={(style) => {
                setArtStyle(style);
                setStyleError(null);
              }}
            />
          )}
          {currentStep === 5 && book && (
            <StepCharacterPreview
              key="step-5"
              bookId={book.id}
              characterRegenCount={book.character_regen_count}
              onConfirm={async () => {
                // 서버에서 최신 book 상태 로드 (캐릭터 선택 시 status가 character_confirmed로 변경됨)
                const result = await apiClient.getBook(book.id);
                if (result.data) {
                  loadBookState(result.data);
                }
                setCharacterConfirmed(true);
              }}
              onRegenCountUpdate={(count) => {
                if (book) {
                  setBook({ ...book, character_regen_count: count });
                }
              }}
            />
          )}
          {currentStep === 6 && (
            <StepOptions
              key="step-6"
              pageCount={pageCount}
              bookSpecUid={bookSpecUid}
              onPageCountChange={setPageCount}
              onBookSpecChange={setBookSpecUid}
            />
          )}
          {currentStep === 7 && (
            <StepPlot
              key="step-7"
              plotInput={plotInput}
              jobName={book?.job_name || null}
              onPlotChange={setPlotInput}
            />
          )}
          {currentStep === 8 && book && isGenerating && (
            <StepGenerating
              key="step-8"
              bookId={book.id}
              onComplete={async () => {
                setIsGenerating(false);
                // 편집 화면으로 이동
                router.push(`/create/edit?book_id=${book.id}`);
              }}
              onError={(msg) => {
                setIsGenerating(false);
                setError(msg);
                setCurrentStep(7); // 줄거리로 복귀
              }}
            />
          )}
        </AnimatePresence>

        {/* 유효성 검사 에러 표시 */}
        {currentStep === 1 && (infoErrors.name || infoErrors.birthDate) && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="mt-4 p-3 bg-error/10 border border-error/20 rounded-xl"
          >
            {infoErrors.name && (
              <p className="text-sm text-error-dark flex items-center gap-1">
                <AlertCircle className="w-3.5 h-3.5" /> {infoErrors.name}
              </p>
            )}
            {infoErrors.birthDate && (
              <p className="text-sm text-error-dark flex items-center gap-1 mt-1">
                <AlertCircle className="w-3.5 h-3.5" /> {infoErrors.birthDate}
              </p>
            )}
          </motion.div>
        )}

        {currentStep === 2 && jobError && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="mt-4 p-3 bg-error/10 border border-error/20 rounded-xl"
          >
            <p className="text-sm text-error-dark flex items-center gap-1">
              <AlertCircle className="w-3.5 h-3.5" /> {jobError}
            </p>
          </motion.div>
        )}

        {(currentStep === 3 || currentStep === 4) && styleError && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="mt-4 p-3 bg-error/10 border border-error/20 rounded-xl"
          >
            <p className="text-sm text-error-dark flex items-center gap-1">
              <AlertCircle className="w-3.5 h-3.5" /> {styleError}
            </p>
          </motion.div>
        )}
      </div>

      {/* 하단 네비게이션 — 생성 중에는 숨김 */}
      {!(currentStep === 8 && isGenerating) && (
        <div className="sticky bottom-0 bg-background/90 backdrop-blur-sm border-t border-secondary/30">
          <div className="max-w-2xl mx-auto px-4 py-4 flex items-center justify-between">
            <Button variant="ghost" onClick={handleBack} className="gap-2">
              <ArrowLeft className="w-4 h-4" />
              {currentStep === 1 ? "취소" : "이전"}
            </Button>

            <Button
              onClick={handleNext}
              disabled={saving || (currentStep === 5 && !characterConfirmed)}
              className="gap-2"
            >
              {saving ? (
                <>
                  <div className="animate-spin w-4 h-4 border-2 border-white border-t-transparent rounded-full" />
                  저장 중...
                </>
              ) : currentStep === 7 ? (
                <>
                  <Sparkles className="w-4 h-4" />
                  동화책 생성하기
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
