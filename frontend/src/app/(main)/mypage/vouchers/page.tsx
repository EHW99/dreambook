"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { AuthGuard } from "@/components/auth-guard";
import { PageTransition } from "@/components/page-transition";
import {
  Ticket,
  CreditCard,
  Receipt,
  ChevronDown,
  ChevronUp,
  Minus,
  Plus,
  BookOpen,
  RefreshCw,
  AlertCircle,
  CheckCircle2,
  XCircle,
  ArrowLeft,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { apiClient, VoucherItem, VoucherSummary, PaymentItem } from "@/lib/api";

const VOUCHER_PRICE = 9900;

const PAYMENT_METHODS = [
  { id: "card", label: "신용/체크카드", icon: "💳" },
  { id: "bank_transfer", label: "계좌이체", icon: "🏦" },
  { id: "kakao_pay", label: "카카오페이", icon: "💛" },
];

const FAQ_ITEMS = [
  {
    q: "이용권 1장으로 무엇을 할 수 있나요?",
    a: "이용권 1장으로 AI 동화책 1권을 만들 수 있습니다. 스토리 11편, 일러스트, 디지털 뷰어, 오디오북이 포함됩니다.",
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

  // 구매 상태
  const [quantity, setQuantity] = useState(1);
  const [paymentMethod, setPaymentMethod] = useState("card");
  const [purchasing, setPurchasing] = useState(false);
  const [purchaseSuccess, setPurchaseSuccess] = useState(false);
  const [purchaseError, setPurchaseError] = useState("");

  // 환불 상태
  const [refundingId, setRefundingId] = useState<number | null>(null);

  // 탭 상태
  const [activeTab, setActiveTab] = useState<"issued" | "used">("issued");

  // FAQ 열림 상태
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

    // 가상 결제 처리 딜레이 (실제 PG 응답 시뮬레이션)
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
    if (result.data) {
      await loadData();
    }
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
      <div className="max-w-3xl mx-auto px-4 py-8 pb-24 md:pb-8">
        {/* 헤더 */}
        <div className="flex items-center gap-3 mb-8">
          <Link
            href="/mypage"
            className="w-9 h-9 rounded-xl bg-white shadow-soft flex items-center justify-center hover:shadow-card transition-shadow"
          >
            <ArrowLeft className="w-4 h-4 text-text-light" />
          </Link>
          <div>
            <h2 className="text-2xl font-bold text-text">이용권 관리</h2>
            <p className="text-sm text-text-light">이용권 구매, 조회, 환불을 관리합니다</p>
          </div>
        </div>

        {/* 요약 카드 */}
        {summary && (
          <div className="grid grid-cols-2 gap-3 sm:gap-4 mb-8">
            <div className="bg-white rounded-2xl shadow-soft p-4 sm:p-5">
              <div className="flex items-center gap-2 mb-2">
                <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center">
                  <Ticket className="w-4 h-4 text-primary" />
                </div>
                <span className="text-xs text-text-light">보유 이용권</span>
              </div>
              <p className="text-2xl sm:text-3xl font-bold text-text">
                {summary.available}<span className="text-base font-normal text-text-light ml-1">장</span>
              </p>
            </div>
            <div className="bg-white rounded-2xl shadow-soft p-4 sm:p-5">
              <div className="flex items-center gap-2 mb-2">
                <div className="w-8 h-8 rounded-lg bg-accent/10 flex items-center justify-center">
                  <BookOpen className="w-4 h-4 text-accent-dark" />
                </div>
                <span className="text-xs text-text-light">사용 완료</span>
              </div>
              <p className="text-2xl sm:text-3xl font-bold text-text">
                {summary.used}<span className="text-base font-normal text-text-light ml-1">장</span>
              </p>
            </div>
          </div>
        )}

        {/* 이용권 구매 섹션 */}
        <section className="bg-white rounded-3xl shadow-card p-5 sm:p-7 mb-8">
          <h3 className="text-lg font-bold text-text mb-5 flex items-center gap-2">
            <CreditCard className="w-5 h-5 text-primary" />
            이용권 구매
          </h3>

          {/* 상품 정보 */}
          <div className="border border-secondary/50 rounded-2xl p-4 mb-5">
            <div className="flex items-center justify-between mb-3">
              <div>
                <p className="font-bold text-text">동화책 이용권</p>
                <p className="text-sm text-text-light">AI 동화 스토리 + 일러스트 + 뷰어</p>
              </div>
              <p className="text-lg font-bold text-text">
                {VOUCHER_PRICE.toLocaleString()}<span className="text-sm font-normal text-text-light">원</span>
              </p>
            </div>

            {/* 수량 선택 */}
            <div className="flex items-center justify-between pt-3 border-t border-secondary/30">
              <span className="text-sm text-text-light">수량</span>
              <div className="flex items-center gap-3">
                <button
                  onClick={() => setQuantity(Math.max(1, quantity - 1))}
                  disabled={quantity <= 1}
                  className="w-8 h-8 rounded-lg border border-gray-200 flex items-center justify-center hover:bg-gray-50 disabled:opacity-30 transition-colors"
                >
                  <Minus className="w-3.5 h-3.5" />
                </button>
                <span className="w-8 text-center font-bold text-text">{quantity}</span>
                <button
                  onClick={() => setQuantity(Math.min(10, quantity + 1))}
                  disabled={quantity >= 10}
                  className="w-8 h-8 rounded-lg border border-gray-200 flex items-center justify-center hover:bg-gray-50 disabled:opacity-30 transition-colors"
                >
                  <Plus className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          </div>

          {/* 결제 수단 */}
          <div className="mb-5">
            <p className="text-sm font-medium text-text mb-3">결제 수단</p>
            <div className="grid grid-cols-3 gap-2">
              {PAYMENT_METHODS.map((m) => (
                <button
                  key={m.id}
                  onClick={() => setPaymentMethod(m.id)}
                  className={`py-3 px-2 rounded-xl border-2 text-center transition-all ${
                    paymentMethod === m.id
                      ? "border-primary bg-primary/5"
                      : "border-gray-200 hover:border-gray-300"
                  }`}
                >
                  <span className="text-lg block mb-0.5">{m.icon}</span>
                  <span className="text-xs text-text">{m.label}</span>
                </button>
              ))}
            </div>
          </div>

          {/* 합계 + 결제 버튼 */}
          <div className="flex items-center justify-between py-4 border-t border-secondary/30 mb-4">
            <span className="text-text-light">결제 금액</span>
            <span className="text-2xl font-bold text-text">
              {totalPrice.toLocaleString()}<span className="text-sm font-normal text-text-light ml-1">원</span>
            </span>
          </div>

          {purchaseError && (
            <div className="mb-4 p-3 bg-error/10 border border-error/30 rounded-xl flex items-center gap-2 text-sm text-error-dark">
              <AlertCircle className="w-4 h-4 flex-shrink-0" />
              {purchaseError}
            </div>
          )}

          {purchaseSuccess && (
            <div className="mb-4 p-3 bg-green-50 border border-green-200 rounded-xl flex items-center gap-2 text-sm text-green-700">
              <CheckCircle2 className="w-4 h-4 flex-shrink-0" />
              이용권 {quantity}장이 발급되었습니다!
            </div>
          )}

          <Button
            className="w-full bg-primary hover:bg-primary-dark text-white"
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
        </section>

        {/* 이용권 내역 섹션 */}
        <section className="bg-white rounded-3xl shadow-card p-5 sm:p-7 mb-8">
          <h3 className="text-lg font-bold text-text mb-5 flex items-center gap-2">
            <Receipt className="w-5 h-5 text-primary" />
            이용권 내역
          </h3>

          {/* 탭 */}
          <div className="flex gap-1 p-1 bg-gray-100 rounded-xl mb-5">
            <button
              onClick={() => setActiveTab("issued")}
              className={`flex-1 py-2 px-3 rounded-lg text-sm font-medium transition-all ${
                activeTab === "issued"
                  ? "bg-white text-text shadow-sm"
                  : "text-text-light hover:text-text"
              }`}
            >
              보유 이용권 ({issuedVouchers.length})
            </button>
            <button
              onClick={() => setActiveTab("used")}
              className={`flex-1 py-2 px-3 rounded-lg text-sm font-medium transition-all ${
                activeTab === "used"
                  ? "bg-white text-text shadow-sm"
                  : "text-text-light hover:text-text"
              }`}
            >
              사용/환불 내역 ({usedVouchers.length})
            </button>
          </div>

          {/* 보유 이용권 목록 */}
          {activeTab === "issued" && (
            <div className="space-y-3">
              {issuedVouchers.length === 0 ? (
                <div className="text-center py-10 text-text-light">
                  <Ticket className="w-10 h-10 mx-auto mb-3 opacity-30" />
                  <p className="text-sm">보유 중인 이용권이 없습니다</p>
                </div>
              ) : (
                issuedVouchers.map((v) => (
                  <div
                    key={v.id}
                    className="flex items-center justify-between p-4 border border-secondary/50 rounded-xl"
                  >
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center">
                        <Ticket className="w-5 h-5 text-primary" />
                      </div>
                      <div>
                        <p className="font-medium text-text text-sm">동화책 이용권</p>
                        <p className="text-xs text-text-lighter">
                          {new Date(v.purchased_at).toLocaleDateString("ko-KR")} 구매
                        </p>
                      </div>
                    </div>
                    <button
                      onClick={() => handleRefund(v.id)}
                      disabled={refundingId === v.id}
                      className="text-xs text-text-lighter hover:text-error-dark transition-colors disabled:opacity-50"
                    >
                      {refundingId === v.id ? (
                        <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                      ) : (
                        "환불"
                      )}
                    </button>
                  </div>
                ))
              )}
            </div>
          )}

          {/* 사용/환불 내역 */}
          {activeTab === "used" && (
            <div className="space-y-3">
              {usedVouchers.length === 0 ? (
                <div className="text-center py-10 text-text-light">
                  <BookOpen className="w-10 h-10 mx-auto mb-3 opacity-30" />
                  <p className="text-sm">사용 내역이 없습니다</p>
                </div>
              ) : (
                usedVouchers.map((v) => (
                  <div
                    key={v.id}
                    className="flex items-center justify-between p-4 border border-secondary/50 rounded-xl"
                  >
                    <div className="flex items-center gap-3">
                      <div
                        className={`w-10 h-10 rounded-xl flex items-center justify-center ${
                          v.status === "used"
                            ? "bg-accent/10"
                            : "bg-gray-100"
                        }`}
                      >
                        {v.status === "used" ? (
                          <BookOpen className="w-5 h-5 text-accent-dark" />
                        ) : (
                          <XCircle className="w-5 h-5 text-text-lighter" />
                        )}
                      </div>
                      <div>
                        <p className="font-medium text-text text-sm">
                          {v.status === "used"
                            ? v.book_title || "동화책 생성에 사용"
                            : "환불 완료"}
                        </p>
                        <p className="text-xs text-text-lighter">
                          {v.used_at
                            ? new Date(v.used_at).toLocaleDateString("ko-KR")
                            : new Date(v.purchased_at).toLocaleDateString("ko-KR")}
                        </p>
                      </div>
                    </div>
                    <span
                      className={`text-xs font-medium px-2 py-1 rounded-lg ${
                        v.status === "used"
                          ? "bg-accent/10 text-accent-dark"
                          : "bg-gray-100 text-text-lighter"
                      }`}
                    >
                      {v.status === "used" ? "사용완료" : "환불"}
                    </span>
                  </div>
                ))
              )}
            </div>
          )}
        </section>

        {/* 구매 안내 (FAQ) */}
        <section className="bg-white rounded-3xl shadow-card p-5 sm:p-7">
          <h3 className="text-lg font-bold text-text mb-5">구매 안내</h3>
          <div className="space-y-2">
            {FAQ_ITEMS.map((item, i) => (
              <div key={i} className="border border-secondary/40 rounded-xl overflow-hidden">
                <button
                  onClick={() => setOpenFaq(openFaq === i ? null : i)}
                  className="w-full flex items-center justify-between p-4 text-left"
                >
                  <span className="text-sm font-medium text-text pr-4">{item.q}</span>
                  {openFaq === i ? (
                    <ChevronUp className="w-4 h-4 text-text-lighter flex-shrink-0" />
                  ) : (
                    <ChevronDown className="w-4 h-4 text-text-lighter flex-shrink-0" />
                  )}
                </button>
                {openFaq === i && (
                  <div className="px-4 pb-4">
                    <p className="text-sm text-text-light leading-relaxed">{item.a}</p>
                  </div>
                )}
              </div>
            ))}
          </div>
        </section>
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
