"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronDown, Check, HelpCircle, PenLine, Search } from "lucide-react";
import { JOB_CATEGORIES, UNDECIDED_CATEGORY, type JobCategory } from "@/lib/jobs-data";
import { AptitudeTest } from "./aptitude-test";

interface StepJobSelectProps {
  selectedCategory: string;
  selectedJob: string;
  onSelect: (category: string, job: string) => void;
}

export function StepJobSelect({
  selectedCategory,
  selectedJob,
  onSelect,
}: StepJobSelectProps) {
  const [expandedCategory, setExpandedCategory] = useState<string | null>(
    selectedCategory || null
  );
  const [showAptitudeTest, setShowAptitudeTest] = useState(false);
  const [showCustomInput, setShowCustomInput] = useState(false);
  const [customJob, setCustomJob] = useState("");
  const [searchQuery, setSearchQuery] = useState("");

  function handleCategoryClick(categoryId: string) {
    if (categoryId === UNDECIDED_CATEGORY.id) {
      setShowAptitudeTest(true);
      return;
    }
    setExpandedCategory(expandedCategory === categoryId ? null : categoryId);
  }

  function handleJobClick(category: JobCategory, jobName: string) {
    onSelect(category.name, jobName);
  }

  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
      className="space-y-6"
    >
      <div className="text-center mb-6">
        <h2 className="text-2xl font-bold text-text mb-2">어떤 직업을 꿈꾸나요?</h2>
        <p className="text-text-light">동화 속 주인공의 직업을 선택해주세요</p>
      </div>

      {/* 검색 */}
      <div className="relative">
        <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-text-lighter" />
        <input
          type="text"
          placeholder="직업 검색..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full h-11 pl-10 pr-4 rounded-2xl border-2 border-secondary bg-white text-sm outline-none transition-colors focus:border-primary focus:ring-2 focus:ring-primary/30"
        />
      </div>

      {/* 카테고리별 아코디언 */}
      <div className="space-y-3">
        {JOB_CATEGORIES.filter((cat) => {
          if (!searchQuery.trim()) return true;
          const q = searchQuery.trim().toLowerCase();
          return cat.name.toLowerCase().includes(q) ||
            cat.jobs.some((j) => j.name.toLowerCase().includes(q));
        }).map((category) => {
          const isExpanded = searchQuery.trim() ? true : expandedCategory === category.id;
          const hasSelection = selectedCategory === category.name;

          return (
            <div key={category.id} className="rounded-2xl overflow-hidden border border-secondary/50 bg-white">
              {/* 카테고리 헤더 */}
              <button
                onClick={() => handleCategoryClick(category.id)}
                className={`w-full flex items-center justify-between p-4 transition-colors ${
                  hasSelection
                    ? "bg-primary/10"
                    : "hover:bg-secondary/20"
                }`}
              >
                <div className="flex items-center gap-3">
                  <span className="text-2xl">{category.icon}</span>
                  <span className="font-medium text-text">{category.name}</span>
                  {hasSelection && (
                    <span className="text-xs bg-primary/20 text-primary-dark px-2 py-0.5 rounded-full">
                      {selectedJob}
                    </span>
                  )}
                </div>
                <motion.div
                  animate={{ rotate: isExpanded ? 180 : 0 }}
                  transition={{ duration: 0.2 }}
                >
                  <ChevronDown className="w-5 h-5 text-text-light" />
                </motion.div>
              </button>

              {/* 직업 목록 */}
              <AnimatePresence>
                {isExpanded && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: "auto", opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.2 }}
                    className="overflow-hidden"
                  >
                    <div className="p-3 pt-0 grid grid-cols-2 sm:grid-cols-3 gap-2">
                      {category.jobs.filter((job) => {
                        if (!searchQuery.trim()) return true;
                        return job.name.toLowerCase().includes(searchQuery.trim().toLowerCase());
                      }).map((job) => {
                        const isSelected =
                          selectedCategory === category.name && selectedJob === job.name;

                        return (
                          <motion.button
                            key={job.name}
                            whileHover={{ scale: 1.03 }}
                            whileTap={{ scale: 0.97 }}
                            onClick={() => handleJobClick(category, job.name)}
                            className={`relative flex items-center gap-2 p-3 rounded-xl border-2 transition-all ${
                              isSelected
                                ? "border-primary bg-primary/10 shadow-soft"
                                : "border-transparent bg-secondary/10 hover:bg-secondary/20"
                            }`}
                          >
                            <span className="text-xl">{job.icon}</span>
                            <span className="text-sm font-medium text-text">{job.name}</span>
                            {isSelected && (
                              <Check className="w-4 h-4 text-primary ml-auto" />
                            )}
                          </motion.button>
                        );
                      })}
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          );
        })}

        {/* "어떤 직업이 좋을지 모르겠어요" */}
        <div className="rounded-2xl overflow-hidden border border-primary/30 bg-primary/5">
          <button
            onClick={() => handleCategoryClick(UNDECIDED_CATEGORY.id)}
            className="w-full flex items-center justify-between p-4 hover:bg-primary/10 transition-colors"
          >
            <div className="flex items-center gap-3">
              <span className="text-2xl">{UNDECIDED_CATEGORY.icon}</span>
              <span className="font-medium text-text">{UNDECIDED_CATEGORY.name}</span>
              <span className="text-[10px] bg-primary/20 text-primary-dark px-2 py-0.5 rounded-full font-medium flex items-center gap-1">
                <HelpCircle className="w-3 h-3" />
                성향 테스트
              </span>
            </div>
          </button>
        </div>

        {/* 직접 입력 */}
        <div className="rounded-2xl overflow-hidden border border-secondary/50 bg-white">
          <button
            onClick={() => setShowCustomInput(!showCustomInput)}
            className="w-full flex items-center justify-between p-4 hover:bg-secondary/20 transition-colors"
          >
            <div className="flex items-center gap-3">
              <span className="text-2xl">✏️</span>
              <span className="font-medium text-text">직접 입력하기</span>
              {selectedCategory === "직접 입력" && (
                <span className="text-xs bg-primary/20 text-primary-dark px-2 py-0.5 rounded-full">
                  {selectedJob}
                </span>
              )}
            </div>
            <motion.div animate={{ rotate: showCustomInput ? 180 : 0 }} transition={{ duration: 0.2 }}>
              <ChevronDown className="w-5 h-5 text-text-light" />
            </motion.div>
          </button>
          <AnimatePresence>
            {showCustomInput && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: "auto", opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                transition={{ duration: 0.2 }}
                className="overflow-hidden"
              >
                <div className="p-4 pt-0 space-y-3">
                  <p className="text-xs text-text-light">
                    목록에 없는 직업을 직접 입력해주세요
                  </p>
                  <div className="flex gap-2">
                    <input
                      type="text"
                      value={customJob}
                      onChange={(e) => setCustomJob(e.target.value)}
                      placeholder="예: 마술사, 유튜버, 치과의사..."
                      maxLength={20}
                      className="flex-1 h-11 px-4 rounded-2xl border-2 border-secondary bg-white text-sm outline-none transition-colors focus:border-primary focus:ring-2 focus:ring-primary/30"
                      onKeyDown={(e) => {
                        if (e.key === "Enter" && customJob.trim()) {
                          onSelect("직접 입력", customJob.trim());
                        }
                      }}
                    />
                    <button
                      onClick={() => {
                        if (customJob.trim()) {
                          onSelect("직접 입력", customJob.trim());
                        }
                      }}
                      disabled={!customJob.trim()}
                      className="h-11 px-5 rounded-2xl bg-primary text-white text-sm font-medium disabled:opacity-40 transition-all hover:bg-primary-dark"
                    >
                      선택
                    </button>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>

      {/* 성향 테스트 모달 */}
      <AnimatePresence>
        {showAptitudeTest && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 flex items-center justify-center bg-black/30 p-4"
            onClick={(e) => {
              if (e.target === e.currentTarget) setShowAptitudeTest(false);
            }}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="bg-background rounded-3xl shadow-xl p-6 w-full max-w-md max-h-[85vh] overflow-y-auto"
            >
              <h2 className="text-lg font-bold text-text text-center mb-4">
                나에게 맞는 직업 찾기
              </h2>
              <AptitudeTest
                onSelectJob={(categoryName, jobName) => {
                  onSelect(categoryName, jobName);
                  setShowAptitudeTest(false);
                }}
                onClose={() => setShowAptitudeTest(false)}
              />
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

export function validateJobSelect(data: {
  jobCategory: string;
  jobName: string;
}): { valid: boolean; error?: string } {
  if (!data.jobCategory || !data.jobName) {
    return { valid: false, error: "직업을 선택해주세요" };
  }
  return { valid: true };
}
