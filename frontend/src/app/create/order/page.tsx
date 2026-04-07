"use client";

import { useState, useEffect, useCallback } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import {
  ArrowLeft, Package, MapPin, Phone, User, FileText,
  CheckCircle, AlertCircle, Loader2, PartyPopper, Truck,
} from "lucide-react";
import { AuthGuard } from "@/components/auth-guard";
import { Button } from "@/components/ui/button";
import {
  apiClient,
  BookItem,
  BookSpecItem,
  EstimateResult,
  OrderResult,
  ShippingData,
} from "@/lib/api";

/* ------------------------------------------------------------------ */
/*  주문 페이지                                                        */
/* ------------------------------------------------------------------ */
function OrderContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const bookId = searchParams.get("book_id");

  const [book, setBook] = useState<BookItem | null>(null);
  const [estimate, setEstimate] = useState<EstimateResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [estimateLoading, setEstimateLoading] = useState(false);
  const [ordering, setOrdering] = useState(false);
  const [orderComplete, setOrderComplete] = useState(false);
  const [orderResult, setOrderResult] = useState<OrderResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [specs, setSpecs] = useState<BookSpecItem[]>([]);

  // 배송지 폼
  const [recipientName, setRecipientName] = useState("");
  const [recipientPhone, setRecipientPhone] = useState("");
  const [postalCode, setPostalCode] = useState("");
  const [address1, setAddress1] = useState("");
  const [address2, setAddress2] = useState("");
  const [shippingMemo, setShippingMemo] = useState("");

  // 폼 에러
  const [formErrors, setFormErrors] = useState<Record<string, string>>({});

  // 주문 진행 단계 (로딩 표시용)
  const [orderStep, setOrderStep] = useState("");

  // 데이터 로드
  useEffect(() => {
    if (!bookId) {
      setError("동화책 ID가 없습니다");
      setLoading(false);
      return;
    }

    const loadData = async () => {
      try {
        const bookRes = await apiClient.getBook(Number(bookId));
        if (bookRes.error) {
          setError(bookRes.error);
          return;
        }
        setBook(bookRes.data!);

        // 판형 정보 로드
        const specsRes = await apiClient.getBookSpecs();
        if (specsRes.data) setSpecs(specsRes.data);

        // 견적 로드
        setEstimateLoading(true);
        const estRes = await apiClient.getEstimate(Number(bookId));
        if (estRes.data) {
          setEstimate(estRes.data);
        }

        // 회원 정보로 수령인 기본값 채우기
        const meRes = await apiClient.getMe();
        if (meRes.data) {
          if (!recipientName && meRes.data.name) {
            setRecipientName(meRes.data.name);
          }
          if (!recipientPhone && meRes.data.phone) {
            setRecipientPhone(meRes.data.phone);
          }
        }
      } catch {
        setError("데이터를 불러오는데 실패했습니다");
      } finally {
        setLoading(false);
        setEstimateLoading(false);
      }
    };

    loadData();
  }, [bookId]);

  // 입력 검증
  const validateForm = useCallback((): boolean => {
    const errors: Record<string, string> = {};

    if (!recipientName.trim()) {
      errors.recipientName = "수령인 이름을 입력해주세요";
    } else if (recipientName.trim().length > 100) {
      errors.recipientName = "수령인 이름은 최대 100자까지 입력 가능합니다";
    }

    if (!recipientPhone.trim()) {
      errors.recipientPhone = "전화번호를 입력해주세요";
    } else {
      const cleaned = recipientPhone.replace(/[\s-]/g, "");
      if (!/^0\d{9,10}$/.test(cleaned)) {
        errors.recipientPhone = "올바른 전화번호 형식이 아닙니다 (예: 010-1234-5678)";
      }
    }

    if (!postalCode.trim()) {
      errors.postalCode = "우편번호를 입력해주세요";
    } else if (!/^\d{5}$/.test(postalCode.trim())) {
      errors.postalCode = "올바른 우편번호 형식이 아닙니다 (5자리 숫자)";
    }

    if (!address1.trim()) {
      errors.address1 = "주소를 입력해주세요";
    } else if (address1.trim().length > 200) {
      errors.address1 = "주소는 최대 200자까지 입력 가능합니다";
    }

    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  }, [recipientName, recipientPhone, postalCode, address1]);

  // 주문 실행
  const handleOrder = useCallback(async () => {
    if (!validateForm() || !bookId) return;

    setOrdering(true);
    setError(null);

    const steps = [
      "충전금 확인 중...",
      "동화책 생성 중...",
      "일러스트 업로드 중...",
      "표지 생성 중...",
      "내지 구성 중...",
      "최종 검수 중...",
      "견적 확인 중...",
      "주문 처리 중...",
    ];

    let stepIdx = 0;
    const stepInterval = setInterval(() => {
      if (stepIdx < steps.length) {
        setOrderStep(steps[stepIdx]);
        stepIdx++;
      }
    }, 2000);

    setOrderStep(steps[0]);

    try {
      const shipping: ShippingData = {
        recipient_name: recipientName.trim(),
        recipient_phone: recipientPhone.trim(),
        postal_code: postalCode.trim(),
        address1: address1.trim(),
      };
      if (address2.trim()) shipping.address2 = address2.trim();
      if (shippingMemo.trim()) shipping.shipping_memo = shippingMemo.trim();

      const res = await apiClient.createOrder(Number(bookId), shipping);

      clearInterval(stepInterval);

      if (res.error) {
        setError(res.error);
        setOrdering(false);
        return;
      }

      setOrderResult(res.data!);
      setOrderComplete(true);
    } catch {
      clearInterval(stepInterval);
      setError("주문 처리 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.");
    } finally {
      setOrdering(false);
    }
  }, [bookId, recipientName, recipientPhone, postalCode, address1, address2, shippingMemo, validateForm]);

  // 주문 완료 화면
  if (orderComplete && orderResult) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center p-4">
        <motion.div
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ type: "spring", duration: 0.6 }}
          className="max-w-md w-full bg-white rounded-3xl shadow-hover p-8 text-center"
        >
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.2, type: "spring", stiffness: 200 }}
            className="w-20 h-20 mx-auto mb-6 bg-success/20 rounded-full flex items-center justify-center"
          >
            <PartyPopper className="w-10 h-10 text-success" />
          </motion.div>

          <motion.h2
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.3 }}
            className="text-2xl font-bold text-text mb-2"
          >
            주문이 완료되었습니다!
          </motion.h2>

          <motion.p
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.4 }}
            className="text-text-light mb-6"
          >
            {book?.child_name}의 동화책이 곧 만들어져요
          </motion.p>

          <motion.div
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.5 }}
            className="bg-background rounded-2xl p-4 mb-6 text-left space-y-2"
          >
            <div className="flex justify-between text-sm">
              <span className="text-text-light">주문 번호</span>
              <span className="font-medium text-text">
                {orderResult.bookprint_order_uid || `#${orderResult.id}`}
              </span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-text-light">상태</span>
              <span className="font-medium text-primary">결제 완료</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-text-light">결제 금액</span>
              <span className="font-medium text-text">
                {orderResult.total_amount.toLocaleString()}원
              </span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-text-light">수령인</span>
              <span className="font-medium text-text">{orderResult.recipient_name}</span>
            </div>
          </motion.div>

          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.6 }}
            className="text-xs text-text-lighter mb-6"
          >
            Sandbox 환경에서는 결제 완료(PAID) 상태에서 정지됩니다.
            실제 인쇄/배송은 진행되지 않습니다.
          </motion.p>

          <motion.div
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.7 }}
            className="flex flex-col gap-3"
          >
            <Button onClick={() => router.push("/bookshelf")} className="w-full">
              내 책장으로 이동
            </Button>
            <Button
              variant="outline"
              onClick={() => router.push("/")}
              className="w-full"
            >
              홈으로 돌아가기
            </Button>
          </motion.div>
        </motion.div>
      </div>
    );
  }

  // 로딩
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin w-10 h-10 border-3 border-primary border-t-transparent rounded-full mx-auto" />
          <p className="mt-4 text-text-light">로딩 중...</p>
        </div>
      </div>
    );
  }

  // 에러 (데이터 로드 실패)
  if (!book) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4">
        <div className="text-center">
          <AlertCircle className="w-12 h-12 text-error mx-auto mb-4" />
          <p className="text-text mb-4">{error || "동화책을 찾을 수 없습니다"}</p>
          <Button onClick={() => router.back()}>돌아가기</Button>
        </div>
      </div>
    );
  }

  // 주문 진행 중 로딩 오버레이
  if (ordering) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="max-w-sm w-full bg-white rounded-3xl shadow-hover p-8 text-center"
        >
          <div className="relative w-20 h-20 mx-auto mb-6">
            <motion.div
              className="absolute inset-0 border-4 border-primary/20 rounded-full"
            />
            <motion.div
              className="absolute inset-0 border-4 border-transparent border-t-primary rounded-full"
              animate={{ rotate: 360 }}
              transition={{ repeat: Infinity, duration: 1, ease: "linear" }}
            />
            <div className="absolute inset-0 flex items-center justify-center">
              <Package className="w-8 h-8 text-primary" />
            </div>
          </div>

          <h3 className="text-lg font-bold text-text mb-2">
            동화책을 만들고 있어요
          </h3>
          <motion.p
            key={orderStep}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-sm text-text-light"
          >
            {orderStep}
          </motion.p>

          <p className="text-xs text-text-lighter mt-4">
            잠시만 기다려주세요. 이 과정은 1~2분 정도 소요됩니다.
          </p>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      {/* 헤더 */}
      <div className="sticky top-0 z-10 bg-background/90 backdrop-blur-sm border-b border-secondary/30">
        <div className="max-w-2xl mx-auto px-4 py-3 flex items-center gap-3">
          <button
            onClick={() => router.push(`/create/edit?book_id=${bookId}`)}
            className="text-text-light hover:text-text transition-colors p-1"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <h1 className="text-lg font-bold text-text">주문하기</h1>
        </div>
      </div>

      <div className="max-w-2xl mx-auto px-4 py-6 space-y-6">
        {/* 에러 표시 */}
        <AnimatePresence>
          {error && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="p-4 bg-error/10 border border-error/30 rounded-2xl flex items-start gap-3"
            >
              <AlertCircle className="w-5 h-5 text-error flex-shrink-0 mt-0.5" />
              <div>
                <p className="text-sm text-error font-medium">{error}</p>
                <p className="text-xs text-error/70 mt-1">
                  문제가 계속되면 잠시 후 다시 시도해주세요.
                </p>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* 동화책 정보 */}
        <div className="bg-white rounded-2xl shadow-soft p-5">
          <h2 className="text-base font-bold text-text mb-3 flex items-center gap-2">
            <Package className="w-4 h-4 text-primary" />
            주문 동화책
          </h2>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-text-light">제목</span>
              <span className="text-text font-medium">
                {book.title || `${book.child_name}의 동화책`}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-text-light">아이 이름</span>
              <span className="text-text">{book.child_name}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-text-light">판형</span>
              <span className="text-text">
{specs.find((s) => s.uid === book.book_spec_uid)?.name || book.book_spec_uid}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-text-light">페이지 수</span>
              <span className="text-text">{book.page_count}페이지</span>
            </div>
          </div>
        </div>

        {/* 견적 정보 */}
        <div className="bg-white rounded-2xl shadow-soft p-5">
          <h2 className="text-base font-bold text-text mb-3 flex items-center gap-2">
            <FileText className="w-4 h-4 text-primary" />
            예상 가격
          </h2>
          {estimateLoading ? (
            <div className="flex items-center justify-center py-4">
              <Loader2 className="w-5 h-5 animate-spin text-primary" />
              <span className="ml-2 text-sm text-text-light">견적 계산 중...</span>
            </div>
          ) : estimate ? (
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-text-light">제작비</span>
                <span className="text-text">
                  {estimate.product_amount.toLocaleString()}원
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-text-light">배송비</span>
                <span className="text-text">
                  {estimate.shipping_fee.toLocaleString()}원
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-text-light">포장비</span>
                <span className="text-text">
                  {estimate.packaging_fee.toLocaleString()}원
                </span>
              </div>
              <div className="border-t border-secondary/30 pt-2 mt-2 flex justify-between">
                <span className="text-text font-bold">총 금액</span>
                <span className="text-primary font-bold text-lg">
                  {estimate.total_amount.toLocaleString()}원
                </span>
              </div>
              {estimate.paid_credit_amount > 0 && (
                <div className="flex justify-between text-xs text-text-lighter">
                  <span>VAT 포함 결제액</span>
                  <span>{estimate.paid_credit_amount.toLocaleString()}원</span>
                </div>
              )}
            </div>
          ) : (
            <p className="text-sm text-text-light">
              견적을 불러올 수 없습니다.
            </p>
          )}
        </div>

        {/* 배송지 입력 */}
        <div className="bg-white rounded-2xl shadow-soft p-5">
          <h2 className="text-base font-bold text-text mb-4 flex items-center gap-2">
            <Truck className="w-4 h-4 text-primary" />
            배송 정보
          </h2>

          <div className="space-y-4">
            {/* 수령인 */}
            <div>
              <label className="flex items-center gap-1.5 text-sm font-medium text-text mb-1.5">
                <User className="w-3.5 h-3.5 text-text-light" />
                수령인 <span className="text-error">*</span>
              </label>
              <input
                type="text"
                value={recipientName}
                onChange={(e) => {
                  setRecipientName(e.target.value);
                  setFormErrors((prev) => ({ ...prev, recipientName: "" }));
                }}
                placeholder="수령인 이름"
                className={`w-full px-4 py-2.5 rounded-xl border text-sm transition-colors focus:outline-none focus:ring-2 focus:ring-primary/40 ${
                  formErrors.recipientName
                    ? "border-error bg-error/5"
                    : "border-secondary hover:border-primary/40"
                }`}
              />
              {formErrors.recipientName && (
                <p className="text-xs text-error mt-1">{formErrors.recipientName}</p>
              )}
            </div>

            {/* 전화번호 */}
            <div>
              <label className="flex items-center gap-1.5 text-sm font-medium text-text mb-1.5">
                <Phone className="w-3.5 h-3.5 text-text-light" />
                전화번호 <span className="text-error">*</span>
              </label>
              <input
                type="tel"
                value={recipientPhone}
                onChange={(e) => {
                  setRecipientPhone(e.target.value);
                  setFormErrors((prev) => ({ ...prev, recipientPhone: "" }));
                }}
                placeholder="010-1234-5678"
                className={`w-full px-4 py-2.5 rounded-xl border text-sm transition-colors focus:outline-none focus:ring-2 focus:ring-primary/40 ${
                  formErrors.recipientPhone
                    ? "border-error bg-error/5"
                    : "border-secondary hover:border-primary/40"
                }`}
              />
              {formErrors.recipientPhone && (
                <p className="text-xs text-error mt-1">{formErrors.recipientPhone}</p>
              )}
            </div>

            {/* 우편번호 */}
            <div>
              <label className="flex items-center gap-1.5 text-sm font-medium text-text mb-1.5">
                <MapPin className="w-3.5 h-3.5 text-text-light" />
                우편번호 <span className="text-error">*</span>
              </label>
              <input
                type="text"
                value={postalCode}
                onChange={(e) => {
                  setPostalCode(e.target.value);
                  setFormErrors((prev) => ({ ...prev, postalCode: "" }));
                }}
                placeholder="12345"
                maxLength={5}
                className={`w-full px-4 py-2.5 rounded-xl border text-sm transition-colors focus:outline-none focus:ring-2 focus:ring-primary/40 ${
                  formErrors.postalCode
                    ? "border-error bg-error/5"
                    : "border-secondary hover:border-primary/40"
                }`}
              />
              {formErrors.postalCode && (
                <p className="text-xs text-error mt-1">{formErrors.postalCode}</p>
              )}
            </div>

            {/* 주소 */}
            <div>
              <label className="flex items-center gap-1.5 text-sm font-medium text-text mb-1.5">
                <MapPin className="w-3.5 h-3.5 text-text-light" />
                주소 <span className="text-error">*</span>
              </label>
              <input
                type="text"
                value={address1}
                onChange={(e) => {
                  setAddress1(e.target.value);
                  setFormErrors((prev) => ({ ...prev, address1: "" }));
                }}
                placeholder="도로명 주소 또는 지번 주소"
                className={`w-full px-4 py-2.5 rounded-xl border text-sm transition-colors focus:outline-none focus:ring-2 focus:ring-primary/40 ${
                  formErrors.address1
                    ? "border-error bg-error/5"
                    : "border-secondary hover:border-primary/40"
                }`}
              />
              {formErrors.address1 && (
                <p className="text-xs text-error mt-1">{formErrors.address1}</p>
              )}
            </div>

            {/* 상세주소 */}
            <div>
              <label className="text-sm font-medium text-text mb-1.5 block">
                상세주소
              </label>
              <input
                type="text"
                value={address2}
                onChange={(e) => setAddress2(e.target.value)}
                placeholder="아파트/동/호수"
                className="w-full px-4 py-2.5 rounded-xl border border-secondary text-sm transition-colors focus:outline-none focus:ring-2 focus:ring-primary/40 hover:border-primary/40"
              />
            </div>

            {/* 배송 메모 */}
            <div>
              <label className="text-sm font-medium text-text mb-1.5 block">
                배송 메모
              </label>
              <input
                type="text"
                value={shippingMemo}
                onChange={(e) => setShippingMemo(e.target.value)}
                placeholder="부재시 경비실에 맡겨주세요"
                className="w-full px-4 py-2.5 rounded-xl border border-secondary text-sm transition-colors focus:outline-none focus:ring-2 focus:ring-primary/40 hover:border-primary/40"
              />
            </div>
          </div>
        </div>

        {/* Sandbox 안내 */}
        <div className="bg-accent/10 rounded-2xl p-4 text-sm text-text-light flex items-start gap-2">
          <AlertCircle className="w-4 h-4 text-accent flex-shrink-0 mt-0.5" />
          <div>
            <p className="font-medium text-text">Sandbox 환경 안내</p>
            <p className="mt-1 text-xs">
              현재 테스트 환경에서 운영 중입니다. 결제 완료(PAID) 상태에서 정지되며,
              실제 인쇄/배송은 진행되지 않습니다.
            </p>
          </div>
        </div>

        {/* 주문 버튼 spacer (모바일 키보드/sticky 여백) */}
        <div className="h-4 md:h-0" />

        {/* 주문 버튼 */}
        <div className="sticky bottom-0 bg-background/90 backdrop-blur-sm border-t border-secondary/30 -mx-3 sm:-mx-4 px-3 sm:px-4 py-4">
          <Button
            onClick={handleOrder}
            disabled={ordering}
            className="w-full h-12 text-base gap-2"
          >
            {ordering ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                주문 처리 중...
              </>
            ) : (
              <>
                <CheckCircle className="w-5 h-5" />
                {estimate
                  ? `${estimate.total_amount.toLocaleString()}원 주문하기`
                  : "주문하기"}
              </>
            )}
          </Button>
        </div>
      </div>
    </div>
  );
}

export default function OrderPage() {
  return (
    <AuthGuard>
      <OrderContent />
    </AuthGuard>
  );
}
