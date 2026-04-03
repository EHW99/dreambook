"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { Ticket, Sparkles, BookOpen, Printer, Check, ArrowLeft } from "lucide-react";
import { AuthGuard } from "@/components/auth-guard";
import { Button } from "@/components/ui/button";
import { apiClient, VoucherItem } from "@/lib/api";

const VOUCHER_TYPES = [
  {
    type: "story_only",
    name: "AI 스토리북",
    price: 9900,
    priceLabel: "9,900원",
    description: "AI가 만든 나만의 동화책을 디지털로 감상하세요",
    features: ["AI 맞춤 동화 스토리", "AI 일러스트 생성", "디지털 동화책 뷰어", "오디오북 기능"],
    icon: BookOpen,
    color: "from-accent/30 to-accent/10",
    borderColor: "border-accent",
    buttonColor: "bg-accent hover:bg-accent-dark",
  },
  {
    type: "story_and_print",
    name: "AI 스토리북 + 실물 책",
    price: 29900,
    priceLabel: "29,900원",
    description: "세상에 하나뿐인 동화책을 실물로 받아보세요",
    features: [
      "AI 스토리북의 모든 기능",
      "하드커버 실물 책 인쇄",
      "택배 배송",
      "고품질 인쇄",
    ],
    icon: Printer,
    color: "from-primary/30 to-primary/10",
    borderColor: "border-primary",
    buttonColor: "bg-primary hover:bg-primary-dark",
    popular: true,
  },
];

function VouchersContent() {
  const router = useRouter();
  const [purchasing, setPurchasing] = useState<string | null>(null);
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

  async function handlePurchase(voucherType: string) {
    setPurchasing(voucherType);
    const result = await apiClient.purchaseVoucher(voucherType);
    if (result.data) {
      // 구매 성공 — 동화책 만들기로 이동
      router.push(`/create?voucher_id=${result.data.id}`);
    }
    setPurchasing(null);
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

      <div className="max-w-4xl mx-auto px-4 py-8">
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

        {/* 타이틀 */}
        <div className="text-center mb-10">
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
            <Sparkles className="w-10 h-10 text-primary mx-auto mb-3" />
            <h2 className="text-2xl font-bold text-text mb-2">이용권을 선택해주세요</h2>
            <p className="text-text-light">아이의 꿈을 동화책으로 만들어보세요</p>
          </motion.div>
        </div>

        {/* 이용권 카드 */}
        <div className="grid md:grid-cols-2 gap-6 max-w-3xl mx-auto">
          {VOUCHER_TYPES.map((voucher, index) => {
            const Icon = voucher.icon;
            return (
              <motion.div
                key={voucher.type}
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.15 }}
                className={`relative bg-gradient-to-br ${voucher.color} border-2 ${voucher.borderColor} rounded-3xl p-6 flex flex-col`}
              >
                {voucher.popular && (
                  <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-primary text-white text-xs font-bold px-4 py-1 rounded-full">
                    인기
                  </div>
                )}
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-12 h-12 rounded-2xl bg-white/60 flex items-center justify-center">
                    <Icon className="w-6 h-6 text-text" />
                  </div>
                  <div>
                    <h3 className="font-bold text-text">{voucher.name}</h3>
                    <p className="text-sm text-text-light">{voucher.description}</p>
                  </div>
                </div>

                <div className="mb-4">
                  <span className="text-3xl font-bold text-text">{voucher.priceLabel}</span>
                </div>

                <ul className="space-y-2 mb-6 flex-1">
                  {voucher.features.map((feature) => (
                    <li key={feature} className="flex items-center gap-2 text-sm text-text">
                      <Check className="w-4 h-4 text-success-dark flex-shrink-0" />
                      {feature}
                    </li>
                  ))}
                </ul>

                <Button
                  className={`w-full text-white ${voucher.buttonColor}`}
                  onClick={() => handlePurchase(voucher.type)}
                  disabled={purchasing !== null}
                >
                  {purchasing === voucher.type ? "구매 중..." : "구매하기"}
                </Button>
              </motion.div>
            );
          })}
        </div>
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
