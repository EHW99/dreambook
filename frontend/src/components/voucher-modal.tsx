"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { BookOpen, Check, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { apiClient } from "@/lib/api";

interface VoucherModalProps {
  open: boolean;
  onClose: () => void;
  onPurchased: (voucherId: number) => void;
}

export function VoucherModal({ open, onClose, onPurchased }: VoucherModalProps) {
  const [purchasing, setPurchasing] = useState(false);
  const [error, setError] = useState("");

  async function handlePurchase() {
    setPurchasing(true);
    setError("");
    const result = await apiClient.purchaseVoucher();
    if (result.data) {
      onPurchased(result.data.id);
    } else {
      setError(result.error || "구매에 실패했습니다");
    }
    setPurchasing(false);
  }

  return (
    <AnimatePresence>
      {open && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.2 }}
          className="fixed inset-0 z-50 flex items-center justify-center px-4"
          onClick={onClose}
        >
          {/* 백드롭 */}
          <div className="absolute inset-0 bg-black/40 backdrop-blur-sm" />

          {/* 모달 */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 10 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 10 }}
            transition={{ duration: 0.2 }}
            className="relative bg-white rounded-3xl shadow-xl p-6 sm:p-8 max-w-sm w-full"
            onClick={(e) => e.stopPropagation()}
          >
            {/* 닫기 버튼 */}
            <button
              onClick={onClose}
              className="absolute top-4 right-4 w-8 h-8 rounded-full hover:bg-gray-100 flex items-center justify-center transition-colors"
            >
              <X className="w-4 h-4 text-text-lighter" />
            </button>

            {/* 내용 */}
            <div className="text-center mb-6">
              <div className="w-14 h-14 rounded-2xl bg-primary/10 flex items-center justify-center mx-auto mb-4">
                <BookOpen className="w-7 h-7 text-primary" />
              </div>
              <h2 className="text-xl font-bold text-text mb-1">동화책 이용권</h2>
              <p className="text-sm text-text-light">이용권을 구매하면 동화책을 만들 수 있어요</p>
            </div>

            <div className="text-center mb-5">
              <span className="text-3xl font-bold text-text">9,900</span>
              <span className="text-text-light ml-1">원</span>
            </div>

            <ul className="space-y-2.5 mb-6">
              {[
                "AI 맞춤 동화 스토리 11편",
                "AI 일러스트 생성",
                "5가지 그림체 선택",
                "디지털 동화책 뷰어",
                "오디오북 기능",
              ].map((feature) => (
                <li key={feature} className="flex items-center gap-2 text-sm text-text">
                  <Check className="w-4 h-4 text-green-500 flex-shrink-0" />
                  {feature}
                </li>
              ))}
            </ul>

            <p className="text-xs text-text-lighter text-center mb-5">
              실물 책 인쇄 및 배송은 별도 요금이 발생합니다
            </p>

            {error && (
              <div className="mb-4 p-3 bg-error/10 border border-error/30 rounded-xl text-sm text-error-dark text-center">
                {error}
              </div>
            )}

            <Button
              className="w-full bg-primary hover:bg-primary-dark text-white"
              size="lg"
              onClick={handlePurchase}
              disabled={purchasing}
            >
              {purchasing ? "구매 중..." : "구매하기"}
            </Button>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
