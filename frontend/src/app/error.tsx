"use client";

import { motion } from "framer-motion";
import { AlertTriangleIcon } from "@/components/icons";

/**
 * 500 에러 페이지 (Error Boundary)
 * Next.js App Router의 error.tsx 규약
 */
export default function ErrorPage({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <div className="min-h-screen bg-background flex items-center justify-center px-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, ease: "easeOut" }}
        className="text-center max-w-md w-full"
      >
        {/* 일러스트 영역 */}
        <div className="relative mx-auto mb-8">
          <div className="w-40 h-40 mx-auto rounded-full bg-gradient-to-br from-warning/40 to-secondary/30 flex items-center justify-center">
            <div className="w-28 h-28 rounded-full bg-white/60 flex items-center justify-center">
              <AlertTriangleIcon className="w-14 h-14 text-warning-dark" />
            </div>
          </div>
          {/* 떠다니는 점 */}
          <motion.div
            animate={{ y: [-3, 3, -3] }}
            transition={{ repeat: Infinity, duration: 3, ease: "easeInOut" }}
            className="absolute top-2 right-8 w-4 h-4 rounded-full bg-primary/40"
          />
          <motion.div
            animate={{ y: [3, -3, 3] }}
            transition={{ repeat: Infinity, duration: 2.5, ease: "easeInOut" }}
            className="absolute bottom-4 left-10 w-3 h-3 rounded-full bg-accent/40"
          />
        </div>

        {/* 메시지 */}
        <h1 className="text-2xl font-bold text-text mb-3">
          이런, 문제가 생겼어요
        </h1>
        <p className="text-sm text-text-light mb-8 leading-relaxed">
          잠시 후 다시 시도해주세요
          <br />
          문제가 계속되면 새로고침해보세요
        </p>

        {/* 버튼들 */}
        <div className="flex flex-col sm:flex-row items-center justify-center gap-3">
          <button
            onClick={reset}
            className="inline-flex items-center gap-2 px-8 py-3 rounded-2xl bg-primary text-white font-medium shadow-soft hover:bg-primary-dark hover:shadow-hover transition-all duration-200"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="18"
              height="18"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <polyline points="23 4 23 10 17 10" />
              <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10" />
            </svg>
            다시 시도
          </button>

          <a
            href="/"
            className="inline-flex items-center gap-2 px-8 py-3 rounded-2xl border-2 border-primary text-primary font-medium hover:bg-primary hover:text-white transition-all duration-200"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="18"
              height="18"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
              <polyline points="9 22 9 12 15 12 15 22" />
            </svg>
            홈으로 돌아가기
          </a>
        </div>
      </motion.div>
    </div>
  );
}
