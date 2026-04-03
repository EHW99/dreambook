"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronDown, Check, Lock } from "lucide-react";
import { JOB_CATEGORIES, UNDECIDED_CATEGORY, type JobCategory } from "@/lib/jobs-data";

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

  function handleCategoryClick(categoryId: string) {
    if (categoryId === UNDECIDED_CATEGORY.id) {
      // "모르겠어요" — 준비 중
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

      {/* 카테고리별 아코디언 */}
      <div className="space-y-3">
        {JOB_CATEGORIES.map((category) => {
          const isExpanded = expandedCategory === category.id;
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
                      {category.jobs.map((job) => {
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
        <div className="rounded-2xl overflow-hidden border border-secondary/50 bg-white/50 opacity-70">
          <button
            onClick={() => handleCategoryClick(UNDECIDED_CATEGORY.id)}
            className="w-full flex items-center justify-between p-4 cursor-not-allowed"
            disabled
          >
            <div className="flex items-center gap-3">
              <span className="text-2xl">{UNDECIDED_CATEGORY.icon}</span>
              <span className="font-medium text-text-light">{UNDECIDED_CATEGORY.name}</span>
              <span className="text-[10px] bg-warning/50 text-warning-dark px-2 py-0.5 rounded-full font-medium flex items-center gap-1">
                <Lock className="w-3 h-3" />
                준비 중
              </span>
            </div>
          </button>
        </div>
      </div>
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
