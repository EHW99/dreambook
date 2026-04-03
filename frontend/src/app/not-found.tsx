"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { BookOpenIcon } from "@/components/icons";

/**
 * 404 Not Found 페이지
 * 따뜻한 일러스트 + "길을 잃었나봐요" + 홈으로 돌아가기 버튼
 */
export default function NotFound() {
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
          {/* 배경 원 */}
          <div className="w-40 h-40 mx-auto rounded-full bg-gradient-to-br from-secondary/60 to-primary/20 flex items-center justify-center">
            <div className="w-28 h-28 rounded-full bg-white/60 flex items-center justify-center">
              <BookOpenIcon className="w-14 h-14 text-primary" />
            </div>
          </div>
          {/* 떠다니는 별들 */}
          <motion.div
            animate={{ y: [-3, 3, -3] }}
            transition={{ repeat: Infinity, duration: 3, ease: "easeInOut" }}
            className="absolute top-2 right-8 w-4 h-4 rounded-full bg-warning"
          />
          <motion.div
            animate={{ y: [3, -3, 3] }}
            transition={{ repeat: Infinity, duration: 2.5, ease: "easeInOut" }}
            className="absolute bottom-4 left-10 w-3 h-3 rounded-full bg-accent"
          />
          <motion.div
            animate={{ y: [-2, 4, -2] }}
            transition={{ repeat: Infinity, duration: 3.5, ease: "easeInOut" }}
            className="absolute top-10 left-4 w-2 h-2 rounded-full bg-success"
          />
        </div>

        {/* 404 */}
        <p className="text-6xl font-bold text-primary/60 mb-4 font-display">404</p>

        {/* 메시지 */}
        <h1 className="text-2xl font-bold text-text mb-3">
          길을 잃었나봐요
        </h1>
        <p className="text-sm text-text-light mb-8 leading-relaxed">
          찾으시는 페이지가 존재하지 않거나
          <br />
          주소가 변경되었을 수 있어요
        </p>

        {/* 홈으로 돌아가기 버튼 */}
        <Link
          href="/"
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
            <path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
            <polyline points="9 22 9 12 15 12 15 22" />
          </svg>
          홈으로 돌아가기
        </Link>
      </motion.div>
    </div>
  );
}
