"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ArrowLeft, ArrowRight, Sparkles, RotateCcw } from "lucide-react";
import { Button } from "@/components/ui/button";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface QuestionOption {
  id: string;
  text: string;
}

interface Question {
  id: number;
  text: string;
  options: QuestionOption[];
}

interface JobRecommendation {
  name: string;
  icon: string;
  desc: string;
}

interface AptitudeResult {
  category_id: string;
  category_name: string;
  recommended_jobs: JobRecommendation[];
  scores: Record<string, number>;
}

interface AptitudeTestProps {
  onSelectJob: (categoryName: string, jobName: string) => void;
  onClose: () => void;
}

export function AptitudeTest({ onSelectJob, onClose }: AptitudeTestProps) {
  const [questions, setQuestions] = useState<Question[]>([]);
  const [currentQ, setCurrentQ] = useState(0);
  const [answers, setAnswers] = useState<Record<number, string>>({});
  const [result, setResult] = useState<AptitudeResult | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchQuestions();
  }, []);

  async function fetchQuestions() {
    try {
      const res = await fetch(`${API_BASE}/api/aptitude/questions`);
      const data = await res.json();
      setQuestions(data);
    } catch {
      // 네트워크 실패 시 기본 질문 사용
      setQuestions([]);
    }
    setLoading(false);
  }

  function handleAnswer(questionId: number, optionId: string) {
    setAnswers((prev) => ({ ...prev, [questionId]: optionId }));
  }

  async function handleSubmit() {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/aptitude/result`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ answers }),
      });
      const data = await res.json();
      setResult(data);
    } catch {
      // 실패 시 에러 무시
    }
    setLoading(false);
  }

  function handleReset() {
    setAnswers({});
    setCurrentQ(0);
    setResult(null);
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin w-8 h-8 border-3 border-primary border-t-transparent rounded-full" />
      </div>
    );
  }

  // 결과 화면
  if (result) {
    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="space-y-6"
      >
        <div className="text-center">
          <div className="text-4xl mb-3">
            <Sparkles className="w-10 h-10 text-primary mx-auto" />
          </div>
          <h3 className="text-xl font-bold text-text mb-2">
            추천 직업 분야
          </h3>
          <p className="text-primary font-bold text-lg">
            {result.category_name}
          </p>
        </div>

        <div className="space-y-3">
          {result.recommended_jobs.map((job) => (
            <motion.button
              key={job.name}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => onSelectJob(result.category_name, job.name)}
              className="w-full flex items-center gap-4 p-4 rounded-2xl border-2 border-secondary/40 bg-white hover:border-primary/40 transition-all text-left"
            >
              <span className="text-3xl">{job.icon}</span>
              <div>
                <p className="font-bold text-text">{job.name}</p>
                <p className="text-sm text-text-light">{job.desc}</p>
              </div>
            </motion.button>
          ))}
        </div>

        <div className="flex gap-3">
          <Button
            variant="ghost"
            onClick={handleReset}
            className="flex-1 gap-2"
          >
            <RotateCcw className="w-4 h-4" />
            다시 하기
          </Button>
          <Button variant="ghost" onClick={onClose} className="flex-1">
            닫기
          </Button>
        </div>
      </motion.div>
    );
  }

  // 질문이 없으면 닫기
  if (questions.length === 0) {
    return (
      <div className="text-center py-8">
        <p className="text-text-light mb-4">성향 테스트를 불러올 수 없습니다</p>
        <Button variant="ghost" onClick={onClose}>
          닫기
        </Button>
      </div>
    );
  }

  const question = questions[currentQ];
  const isLastQuestion = currentQ === questions.length - 1;
  const currentAnswer = answers[question.id];

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="space-y-6"
    >
      {/* 진행 상태 */}
      <div className="text-center">
        <p className="text-xs text-text-lighter mb-2">
          {currentQ + 1} / {questions.length}
        </p>
        <div className="h-1.5 bg-secondary/30 rounded-full overflow-hidden">
          <motion.div
            className="h-full bg-primary rounded-full"
            initial={{ width: 0 }}
            animate={{
              width: `${((currentQ + 1) / questions.length) * 100}%`,
            }}
            transition={{ duration: 0.3 }}
          />
        </div>
      </div>

      {/* 질문 */}
      <AnimatePresence mode="wait">
        <motion.div
          key={question.id}
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -20 }}
          className="space-y-4"
        >
          <h3 className="text-lg font-bold text-text text-center">
            {question.text}
          </h3>

          <div className="space-y-2">
            {question.options.map((option) => {
              const isSelected = currentAnswer === option.id;
              return (
                <motion.button
                  key={option.id}
                  whileHover={{ scale: 1.01 }}
                  whileTap={{ scale: 0.99 }}
                  onClick={() => handleAnswer(question.id, option.id)}
                  className={`w-full p-4 rounded-2xl border-2 text-left transition-all ${
                    isSelected
                      ? "border-primary bg-primary/10 shadow-sm"
                      : "border-secondary/30 bg-white hover:border-primary/20"
                  }`}
                >
                  <span className="text-sm font-medium text-text">
                    {option.text}
                  </span>
                </motion.button>
              );
            })}
          </div>
        </motion.div>
      </AnimatePresence>

      {/* 네비게이션 */}
      <div className="flex gap-3">
        {currentQ > 0 ? (
          <Button
            variant="ghost"
            onClick={() => setCurrentQ(currentQ - 1)}
            className="flex-1 gap-2"
          >
            <ArrowLeft className="w-4 h-4" />
            이전
          </Button>
        ) : (
          <Button variant="ghost" onClick={onClose} className="flex-1">
            닫기
          </Button>
        )}

        {isLastQuestion ? (
          <Button
            onClick={handleSubmit}
            disabled={!currentAnswer}
            className="flex-1 gap-2"
          >
            <Sparkles className="w-4 h-4" />
            결과 보기
          </Button>
        ) : (
          <Button
            onClick={() => setCurrentQ(currentQ + 1)}
            disabled={!currentAnswer}
            className="flex-1 gap-2"
          >
            다음
            <ArrowRight className="w-4 h-4" />
          </Button>
        )}
      </div>
    </motion.div>
  );
}
