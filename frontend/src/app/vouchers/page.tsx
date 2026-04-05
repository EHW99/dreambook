"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { Ticket, BookOpen, Check, ArrowLeft } from "lucide-react";
import { AuthGuard } from "@/components/auth-guard";
import { Button } from "@/components/ui/button";
import { apiClient, VoucherItem } from "@/lib/api";

function VouchersContent() {
  const router = useRouter();
  const [purchasing, setPurchasing] = useState(false);
  const [vouchers, setVouchers] = useState<VoucherItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadVouchers();
  }, []);

  async function loadVouchers() {
    const result = await apiClient.getVouchers();
    if (result.data) {
      setVouchers(result.data);
    }
    setLoading(false);
  }

  async function handlePurchase() {
    setPurchasing(true);
    const result = await apiClient.purchaseVoucher();
    if (result.data) {
      router.push(`/create?voucher_id=${result.data.id}`);
    }
    setPurchasing(false);
  }

  const availableCount = vouchers.filter((v) => v.status === "purchased").length;

  return (
    <div className="min-h-screen bg-background">
      {/* 헤더 */}
      <div className="sticky top-0 z-10 bg-background/80 backdrop-blur-sm border-b border-secondary/30">
        <div className="max-w-4xl mx-auto px-4 py-4 flex items-center gap-3">
          <button onClick={() => router.back()} className="p-2 hover:bg-secondary/50 rounded-xl transition-colors">
            <ArrowLeft className="w-5 h-5 text-text" />
          </button>
          <h1 className="text-xl font-bold text-text">이용권 구매</h1>
        </div>
      </div>

      <div className="max-w-lg mx-auto px-4 py-8">
        {/* 보유 이용권 안내 */}
        {availableCount > 0 && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-8 p-4 bg-success/20 border border-success rounded-2xl flex items-center gap-3"
          >
            <Ticket className="w-5 h-5 text-success-dark" />
            <span className="text-sm text-text">
              사용 가능한 이용권이 <strong>{availableCount}장</strong> 있어요!
            </span>
            <Button
              size="sm"
              variant="accent"
              className="ml-auto"
              onClick={() => router.push("/create")}
            >
              동화책 만들기
            </Button>
          </motion.div>
        )}

        {/* 이용권 카드 */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white border-2 border-primary rounded-3xl p-8"
        >
          <div className="text-center mb-6">
            <div className="w-14 h-14 rounded-2xl bg-primary/10 flex items-center justify-center mx-auto mb-4">
              <BookOpen className="w-7 h-7 text-primary" />
            </div>
            <h2 className="text-xl font-bold text-text mb-1">동화책 이용권</h2>
            <p className="text-sm text-text-light">AI 동화책 생성 + 실물 하드커버 책 배송</p>
          </div>

          <div className="text-center mb-6">
            <span className="text-4xl font-bold text-text">29,900</span>
            <span className="text-text-light ml-1">원</span>
          </div>

          <ul className="space-y-3 mb-8">
            {[
              "AI 맞춤 동화 스토리 11편",
              "AI 일러스트 생성",
              "5가지 그림체 선택",
              "디지털 동화책 뷰어 + 오디오북",
              "하드커버 실물 책 인쇄 (243×248mm, 24p)",
              "무료 배송",
            ].map((feature) => (
              <li key={feature} className="flex items-center gap-2.5 text-sm text-text">
                <Check className="w-4 h-4 text-green-500 flex-shrink-0" />
                {feature}
              </li>
            ))}
          </ul>

          <Button
            className="w-full bg-primary hover:bg-primary-dark text-white"
            size="lg"
            onClick={handlePurchase}
            disabled={purchasing}
          >
            {purchasing ? "구매 중..." : "구매하기"}
          </Button>
        </motion.div>
      </div>
    </div>
  );
}

export default function VouchersPage() {
  return (
    <AuthGuard>
      <VouchersContent />
    </AuthGuard>
  );
}
