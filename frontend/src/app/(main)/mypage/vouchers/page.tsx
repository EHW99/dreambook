"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { motion, AnimatePresence } from "framer-motion";
import { AuthGuard } from "@/components/auth-guard";
import { PageTransition } from "@/components/page-transition";
import {
  Ticket,
  CreditCard,
  Receipt,
  ChevronDown,
  Minus,
  Plus,
  BookOpen,
  RefreshCw,
  AlertCircle,
  CheckCircle2,
  XCircle,
  ArrowLeft,
  Sparkles,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { apiClient, VoucherItem, VoucherSummary, PaymentItem } from "@/lib/api";

const VOUCHER_PRICE = 9900;

const PAYMENT_METHODS = [
  { id: "card", label: "신용/체크카드", icon: CreditCard },
  { id: "kakao_pay", label: "카카오페이", icon: Sparkles },
];

const FAQ_ITEMS = [
  {
    q: "이용권 1장으로 무엇을 할 수 있나요?",
    a: "이용권 1장으로 AI 동화책 1권을 만들 수 있습니다. 스토리 11편, 일러스트, 디지털 뷰어가 포함됩니다.",
  },
  {
    q: "실물 책 인쇄 비용은 별도인가요?",
    a: "네, 실물 책 인쇄 및 배송은 별도 요금이 발생합니다. 동화책 완성 후 주문 시 견적을 확인할 수 있습니다.",
  },
  {
    q: "이용권 환불이 가능한가요?",
    a: "미사용 이용권에 한해 환불이 가능합니다. 동화책 생성에 사용된 이용권은 환불이 불가합니다.",
  },
  {
    q: "이용권 유효기간이 있나요?",
    a: "이용권은 구매일로부터 1년간 사용 가능합니다.",
  },
];

function VouchersContent() {
  const [summary, setSummary] = useState<VoucherSummary | null>(null);
  const [vouchers, setVouchers] = useState<VoucherItem[]>([]);
  const [payments, setPayments] = useState<PaymentItem[]>([]);
  const [loading, setLoading] = useState(true);

  const [quantity, setQuantity] = useState(1);
  const [paymentMethod, setPaymentMethod] = useState("card");
  const [purchasing, setPurchasing] = useState(false);
  const [purchaseSuccess, setPurchaseSuccess] = useState(false);
  const [purchaseError, setPurchaseError] = useState("");

  const [refundingId, setRefundingId] = useState<number | null>(null);
  const [activeTab, setActiveTab] = useState<"issued" | "used">("issued");
  const [openFaq, setOpenFaq] = useState<number | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  async function loadData() {
    setLoading(true);
    const [summaryRes, vouchersRes, paymentsRes] = await Promise.all([
      apiClient.getVoucherSummary(),
      apiClient.getVouchers(),
      apiClient.getPayments(),
    ]);
    if (summaryRes.data) setSummary(summaryRes.data);
    if (vouchersRes.data) setVouchers(vouchersRes.data);
    if (paymentsRes.data) setPayments(paymentsRes.data);
    setLoading(false);
  }

  async function handlePurchase() {
    setPurchasing(true);
    setPurchaseError("");
    setPurchaseSuccess(false);
    await new Promise((r) => setTimeout(r, 1500));
    const result = await apiClient.purchaseVoucher(quantity, paymentMethod);
    if (result.data) {
      setPurchaseSuccess(true);
      setQuantity(1);
      await loadData();
      setTimeout(() => setPurchaseSuccess(false), 3000);
    } else {
      setPurchaseError(result.error || "결제에 실패했습니다");
    }
    setPurchasing(false);
  }

  async function handleRefund(voucherId: number) {
    setRefundingId(voucherId);
    const result = await apiClient.refundVoucher(voucherId);
    if (result.data) await loadData();
    setRefundingId(null);
  }

  const totalPrice = VOUCHER_PRICE * quantity;
  const issuedVouchers = vouchers.filter((v) => v.status === "purchased");
  const usedVouchers = vouchers.filter((v) => v.status !== "purchased");

  if (loading) {
    return (
      <div className="min-h-[400px] flex items-center justify-center">
        <div className="text-center space-y-3">
          <div className="animate-spin w-8 h-8 border-3 border-primary border-t-transparent rounded-full mx-auto" />
          <p className="text-sm text-text-light">불러오는 중...</p>
        </div>
      </div>
    );
  }

  return (
    <PageTransition>
      <div className="max-w-6xl mx-auto px-4 py-6 pb-24 md:py-10 md:pb-10">
        {/* 헤더 */}
        <div className="flex items-center gap-3 mb-6 md:mb-10">
          <Link
            href="/mypage"
            className="w-9 h-9 rounded-xl bg-white shadow-soft flex items-center justify-center hover:shadow-card transition-shadow"
          >
            <ArrowLeft className="w-4 h-4 text-text-light" />
          </Link>
          <h2 className="text-xl md:text-2xl font-bold text-text">이용권 관리</h2>
        </div>

        {/* 2컬럼 레이아웃 (데스크톱) / 1컬럼 (모바일) */}
        <div className="flex flex-col lg:flex-row gap-6 lg:gap-8 lg:items-start">

          {/* ━━━ 왼쪽: 구매 + FAQ ━━━ */}
          <div className="flex-1 min-w-0 space-y-6">

            {/* 구매 카드 */}
            <section className="bg-white rounded-3xl shadow-card overflow-hidden">
              {/* 상단 배너 */}
              <div className="bg-gradient-to-r from-primary/20 via-secondary-light/40 to-accent/20 px-5 py-5 sm:px-7 sm:py-6">
                <div className="flex items-center gap-3 mb-1">
                  <div className="w-10 h-10 rounded-2xl bg-white/80 backdrop-blur flex items-center justify-center shadow-sm">
                    <Ticket className="w-5 h-5 text-primary-dark" />
                  </div>
                  <div>
                    <h3 className="text-lg font-bold text-text">동화책 이용권</h3>
                    <p className="text-xs text-text-light">AI 스토리 + 일러스트 + 디지털 뷰어</p>
                  </div>
                </div>
                <p className="text-3xl font-bold text-text mt-3">
                  {VOUCHER_PRICE.toLocaleString()}
                  <span className="text-sm font-medium text-text-light ml-1">원 / 1권</span>
                </p>
              </div>

              <div className="px-5 py-5 sm:px-7 sm:py-6 space-y-5">
                {/* 수량 */}
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-text">수량</span>
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => setQuantity(Math.max(1, quantity - 1))}
                      disabled={quantity <= 1}
                      className="w-9 h-9 rounded-xl border border-gray-200 flex items-center justify-center hover:bg-gray-50 disabled:opacity-30 transition-colors"
                    >
                      <Minus className="w-4 h-4" />
                    </button>
                    <span className="w-10 text-center text-lg font-bold text-text">{quantity}</span>
                    <button
                      onClick={() => setQuantity(Math.min(10, quantity + 1))}
                      disabled={quantity >= 10}
                      className="w-9 h-9 rounded-xl border border-gray-200 flex items-center justify-center hover:bg-gray-50 disabled:opacity-30 transition-colors"
                    >
                      <Plus className="w-4 h-4" />
                    </button>
                  </div>
                </div>

                {/* 결제 수단 */}
                <div>
                  <span className="text-sm font-medium text-text block mb-2">결제 수단</span>
                  <div className="flex gap-2">
                    {PAYMENT_METHODS.map((m) => {
                      const Icon = m.icon;
                      const selected = paymentMethod === m.id;
                      return (
                        <button
                          key={m.id}
                          onClick={() => setPaymentMethod(m.id)}
                          className={`flex-1 flex items-center justify-center gap-2 py-2.5 rounded-xl border-2 text-sm font-medium transition-all ${
                            selected
                              ? "border-primary bg-primary/5 text-primary-dark"
                              : "border-gray-200 text-text-light hover:border-gray-300"
                          }`}
                        >
                          <Icon className="w-4 h-4" />
                          {m.label}
                        </button>
                      );
                    })}
                  </div>
                </div>

                {/* 구분선 + 합계 */}
                <div className="border-t border-secondary/40 pt-4 flex items-center justify-between">
                  <span className="text-text-light text-sm">총 결제 금액</span>
                  <span className="text-2xl font-bold text-text">
                    {totalPrice.toLocaleString()}
                    <span className="text-sm font-normal text-text-light ml-1">원</span>
                  </span>
                </div>

                {/* 알림 */}
                <AnimatePresence>
                  {purchaseError && (
                    <motion.div
                      initial={{ opacity: 0, y: -8 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -8 }}
                      className="p-3 bg-error/10 border border-error/30 rounded-xl flex items-center gap-2 text-sm text-error-dark"
                    >
                      <AlertCircle className="w-4 h-4 flex-shrink-0" />
                      {purchaseError}
                    </motion.div>
                  )}
                  {purchaseSuccess && (
                    <motion.div
                      initial={{ opacity: 0, y: -8 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -8 }}
                      className="p-3 bg-success/30 border border-success-dark/30 rounded-xl flex items-center gap-2 text-sm text-success-dark"
                    >
                      <CheckCircle2 className="w-4 h-4 flex-shrink-0" />
                      이용권이 발급되었습니다!
                    </motion.div>
                  )}
                </AnimatePresence>

                {/* 결제 버튼 */}
                <Button
                  className="w-full"
                  size="lg"
                  onClick={handlePurchase}
                  disabled={purchasing}
                >
                  {purchasing ? (
                    <span className="flex items-center gap-2">
                      <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                      결제 처리 중...
                    </span>
                  ) : (
                    `${totalPrice.toLocaleString()}원 결제하기`
                  )}
                </Button>
              </div>
            </section>

            {/* FAQ */}
            <section className="bg-white rounded-3xl shadow-card p-5 sm:p-7">
              <h3 className="text-base font-bold text-text mb-4">자주 묻는 질문</h3>
              <div className="space-y-1.5">
                {FAQ_ITEMS.map((item, i) => (
                  <div key={i} className="rounded-xl overflow-hidden">
                    <button
                      onClick={() => setOpenFaq(openFaq === i ? null : i)}
                      className="w-full flex items-center justify-between p-3.5 text-left hover:bg-gray-50 rounded-xl transition-colors"
                    >
                      <span className="text-sm text-text pr-4">{item.q}</span>
                      <ChevronDown
                        className={`w-4 h-4 text-text-lighter flex-shrink-0 transition-transform duration-200 ${
                          openFaq === i ? "rotate-180" : ""
                        }`}
                      />
                    </button>
                    <AnimatePresence>
                      {openFaq === i && (
                        <motion.div
                          initial={{ height: 0, opacity: 0 }}
                          animate={{ height: "auto", opacity: 1 }}
                          exit={{ height: 0, opacity: 0 }}
                          transition={{ duration: 0.2 }}
                          className="overflow-hidden"
                        >
                          <p className="text-sm text-text-light leading-relaxed px-3.5 pb-3.5">
                            {item.a}
                          </p>
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </div>
                ))}
              </div>
            </section>
          </div>

          {/* ━━━ 오른쪽: 보유현황 + 내역 (데스크톱 sticky) ━━━ */}
          <div className="lg:w-[380px] lg:flex-shrink-0 space-y-6">

            {/* 보유 이용권 카드 */}
            {summary && (
              <section className="bg-gradient-to-br from-primary/10 via-white to-accent/10 rounded-3xl shadow-card p-5 sm:p-6">
                <p className="text-sm text-text-light mb-3">내 이용권</p>
                <div className="flex items-end gap-6">
                  <div>
                    <p className="text-5xl font-bold text-text leading-none">
                      {summary.available}
                      <span className="text-lg font-medium text-text-light ml-1">장</span>
                    </p>
                    <p className="text-xs text-text-lighter mt-1.5">사용 가능</p>
                  </div>
                  <div className="pb-1">
                    <p className="text-lg font-bold text-text-lighter leading-none">
                      {summary.used}
                      <span className="text-sm font-normal ml-0.5">장</span>
                    </p>
                    <p className="text-xs text-text-lighter mt-1">사용 완료</p>
                  </div>
                </div>
                {summary.available > 0 && (
                  <Link
                    href="/create"
                    className="mt-4 block w-full text-center py-2.5 rounded-xl bg-white/80 border border-primary/30 text-sm font-medium text-primary-dark hover:bg-white transition-colors"
                  >
                    동화책 만들러 가기
                  </Link>
                )}
              </section>
            )}

            {/* 이용권 내역 */}
            <section className="bg-white rounded-3xl shadow-card p-5 sm:p-6">
              <div className="flex items-center gap-2 mb-4">
                <Receipt className="w-4 h-4 text-text-lighter" />
                <h3 className="text-base font-bold text-text">이용권 내역</h3>
              </div>

              {/* 탭 */}
              <div className="flex gap-1 p-1 bg-gray-100 rounded-xl mb-4">
                <button
                  onClick={() => setActiveTab("issued")}
                  className={`flex-1 py-2 rounded-lg text-xs font-medium transition-all ${
                    activeTab === "issued"
                      ? "bg-white text-text shadow-sm"
                      : "text-text-light hover:text-text"
                  }`}
                >
                  보유 ({issuedVouchers.length})
                </button>
                <button
                  onClick={() => setActiveTab("used")}
                  className={`flex-1 py-2 rounded-lg text-xs font-medium transition-all ${
                    activeTab === "used"
                      ? "bg-white text-text shadow-sm"
                      : "text-text-light hover:text-text"
                  }`}
                >
                  사용/환불 ({usedVouchers.length})
                </button>
              </div>

              {/* 보유 목록 */}
              {activeTab === "issued" && (
                <div className="space-y-2 max-h-[360px] overflow-y-auto">
                  {issuedVouchers.length === 0 ? (
                    <div className="text-center py-8 text-text-lighter">
                      <Ticket className="w-8 h-8 mx-auto mb-2 opacity-30" />
                      <p className="text-xs">보유 중인 이용권이 없습니다</p>
                    </div>
                  ) : (
                    issuedVouchers.map((v) => (
                      <div
                        key={v.id}
                        className="flex items-center justify-between p-3 bg-gray-50 rounded-xl"
                      >
                        <div className="flex items-center gap-2.5">
                          <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center">
                            <Ticket className="w-4 h-4 text-primary" />
                          </div>
                          <div>
                            <p className="text-sm font-medium text-text">동화책 이용권</p>
                            <p className="text-[11px] text-text-lighter">
                              {new Date(v.purchased_at).toLocaleDateString("ko-KR")}
                            </p>
                          </div>
                        </div>
                        <button
                          onClick={() => handleRefund(v.id)}
                          disabled={refundingId === v.id}
                          className="text-[11px] text-text-lighter hover:text-error-dark transition-colors disabled:opacity-50 px-2 py-1 rounded-lg hover:bg-error/5"
                        >
                          {refundingId === v.id ? (
                            <RefreshCw className="w-3 h-3 animate-spin" />
                          ) : (
                            "환불"
                          )}
                        </button>
                      </div>
                    ))
                  )}
                </div>
              )}

              {/* 사용/환불 목록 */}
              {activeTab === "used" && (
                <div className="space-y-2 max-h-[360px] overflow-y-auto">
                  {usedVouchers.length === 0 ? (
                    <div className="text-center py-8 text-text-lighter">
                      <BookOpen className="w-8 h-8 mx-auto mb-2 opacity-30" />
                      <p className="text-xs">사용 내역이 없습니다</p>
                    </div>
                  ) : (
                    usedVouchers.map((v) => (
                      <div
                        key={v.id}
                        className="flex items-center justify-between p-3 bg-gray-50 rounded-xl"
                      >
                        <div className="flex items-center gap-2.5">
                          <div
                            className={`w-8 h-8 rounded-lg flex items-center justify-center ${
                              v.status === "used" ? "bg-accent/10" : "bg-gray-200"
                            }`}
                          >
                            {v.status === "used" ? (
                              <BookOpen className="w-4 h-4 text-accent-dark" />
                            ) : (
                              <XCircle className="w-4 h-4 text-text-lighter" />
                            )}
                          </div>
                          <div>
                            <p className="text-sm font-medium text-text">
                              {v.status === "used"
                                ? v.book_title || "동화책 생성"
                                : "환불 완료"}
                            </p>
                            <p className="text-[11px] text-text-lighter">
                              {v.used_at
                                ? new Date(v.used_at).toLocaleDateString("ko-KR")
                                : new Date(v.purchased_at).toLocaleDateString("ko-KR")}
                            </p>
                          </div>
                        </div>
                        <span
                          className={`text-[11px] font-medium px-2 py-0.5 rounded-lg ${
                            v.status === "used"
                              ? "bg-accent/10 text-accent-dark"
                              : "bg-gray-100 text-text-lighter"
                          }`}
                        >
                          {v.status === "used" ? "사용" : "환불"}
                        </span>
                      </div>
                    ))
                  )}
                </div>
              )}
            </section>
          </div>
        </div>
      </div>
    </PageTransition>
  );
}

export default function VouchersPage() {
  return (
    <AuthGuard>
      <VouchersContent />
    </AuthGuard>
  );
}
