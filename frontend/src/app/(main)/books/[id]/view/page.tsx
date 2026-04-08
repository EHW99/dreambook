"use client";

import { useState, useEffect, useCallback } from "react";
import { useRouter, useParams } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import {
  ArrowLeft, BookOpen, ShoppingCart, X, Loader2,
  Package, MapPin, Phone, User, FileText,
  CheckCircle, AlertCircle, PartyPopper, Truck,
} from "lucide-react";
import { AuthGuard } from "@/components/auth-guard";
import { PageTransition } from "@/components/page-transition";
import { Button } from "@/components/ui/button";
import {
  apiClient, BookItem, PageItem, BookSpecItem,
  EstimateResult, OrderResult, ShippingData,
} from "@/lib/api";
import BookViewer from "@/components/book-viewer";

function ThumbnailLoading({ bookId, onLoaded }: { bookId: number; onLoaded: (t: { cover: string | null; pages: string[] }) => void }) {
  const [dots, setDots] = useState("");

  useEffect(() => {
    const dotInterval = setInterval(() => setDots(d => d.length >= 3 ? "" : d + "."), 500);

    const poll = setInterval(async () => {
      const res = await apiClient.getThumbnails(bookId).catch(() => ({ data: null, error: null }));
      if (res.data && res.data.pages.length > 0) {
        clearInterval(poll);
        clearInterval(dotInterval);
        onLoaded(res.data);
      }
    }, 5000);

    return () => { clearInterval(poll); clearInterval(dotInterval); };
  }, [bookId, onLoaded]);

  return (
    <div className="flex items-center justify-center py-20">
      <div className="text-center space-y-3">
        <div className="animate-spin w-8 h-8 border-3 border-primary border-t-transparent rounded-full mx-auto" />
        <p className="text-text-light text-sm">렌더링 준비 중{dots}</p>
        <p className="text-text-lighter text-xs">약 2~3분 정도 소요됩니다</p>
      </div>
    </div>
  );
}

function BookViewContent() {
  const router = useRouter();
  const params = useParams();
  const bookId = params?.id ? Number(params.id) : null;

  const [book, setBook] = useState<BookItem | null>(null);
  const [pages, setPages] = useState<PageItem[]>([]);
  const [thumbnails, setThumbnails] = useState<{ cover: string | null; pages: string[] } | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // 주문 모달
  const [showOrderModal, setShowOrderModal] = useState(false);
  const [ordering, setOrdering] = useState(false);
  const [orderStep, setOrderStep] = useState("");
  const [orderError, setOrderError] = useState<string | null>(null);
  const [orderComplete, setOrderComplete] = useState(false);
  const [orderResult, setOrderResult] = useState<OrderResult | null>(null);
  const [estimate, setEstimate] = useState<EstimateResult | null>(null);
  const [estimateLoading, setEstimateLoading] = useState(false);
  const [specs, setSpecs] = useState<BookSpecItem[]>([]);
  const [formErrors, setFormErrors] = useState<Record<string, string>>({});

  // 배송지 폼
  const [recipientName, setRecipientName] = useState("");
  const [recipientPhone, setRecipientPhone] = useState("");
  const [postalCode, setPostalCode] = useState("");
  const [address1, setAddress1] = useState("");
  const [address2, setAddress2] = useState("");
  const [shippingMemo, setShippingMemo] = useState("");

  useEffect(() => {
    if (!bookId) return;
    loadData(bookId);
  }, [bookId]);

  async function loadData(id: number) {
    setLoading(true);
    const [bookRes, pagesRes, thumbRes] = await Promise.all([
      apiClient.getBook(id),
      apiClient.getPages(id),
      apiClient.getThumbnails(id).catch(() => ({ data: null, error: null })),
    ]);
    if (bookRes.data) setBook(bookRes.data);
    else setError("동화책을 찾을 수 없습니다");
    if (pagesRes.data) setPages(pagesRes.data);
    if (thumbRes.data) setThumbnails(thumbRes.data);
    setLoading(false);
  }

  // 주문 모달 열 때 견적 + 회원정보 로드
  const openOrderModal = async () => {
    setShowOrderModal(true);
    if (!bookId) return;

    // 견적
    setEstimateLoading(true);
    const [estRes, specsRes, meRes] = await Promise.all([
      apiClient.getEstimate(bookId),
      apiClient.getBookSpecs(),
      apiClient.getMe(),
    ]);
    if (estRes.data) setEstimate(estRes.data);
    if (specsRes.data) setSpecs(specsRes.data);
    if (meRes.data) {
      if (!recipientName && meRes.data.name) setRecipientName(meRes.data.name);
      if (!recipientPhone && meRes.data.phone) setRecipientPhone(meRes.data.phone);
    }
    setEstimateLoading(false);
  };

  // 유효성 검사
  const validateForm = useCallback((): boolean => {
    const errors: Record<string, string> = {};
    if (!recipientName.trim()) errors.recipientName = "수령인 이름을 입력해주세요";
    else if (recipientName.trim().length > 100) errors.recipientName = "최대 100자";
    if (!recipientPhone.trim()) errors.recipientPhone = "전화번호를 입력해주세요";
    else {
      const cleaned = recipientPhone.replace(/[\s-]/g, "");
      if (!/^0\d{9,10}$/.test(cleaned)) errors.recipientPhone = "올바른 전화번호 형식이 아닙니다";
    }
    if (!postalCode.trim()) errors.postalCode = "우편번호를 입력해주세요";
    else if (!/^\d{5}$/.test(postalCode.trim())) errors.postalCode = "5자리 숫자를 입력해주세요";
    if (!address1.trim()) errors.address1 = "주소를 입력해주세요";
    else if (address1.trim().length > 200) errors.address1 = "최대 200자";
    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  }, [recipientName, recipientPhone, postalCode, address1]);

  // 주문 실행
  const handleOrder = useCallback(async () => {
    if (!validateForm() || !bookId) return;
    setOrdering(true);
    setOrderError(null);

    const steps = [
      "충전금 확인 중...", "동화책 생성 중...", "일러스트 업로드 중...",
      "표지 생성 중...", "내지 구성 중...", "최종 검수 중...",
      "견적 확인 중...", "주문 처리 중...",
    ];
    let stepIdx = 0;
    const interval = setInterval(() => {
      if (stepIdx < steps.length) { setOrderStep(steps[stepIdx]); stepIdx++; }
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

      const res = await apiClient.createOrder(bookId, shipping);
      clearInterval(interval);

      if (res.error) {
        setOrderError(res.error);
        setOrdering(false);
        return;
      }
      setOrderResult(res.data!);
      setOrderComplete(true);
      setBook((prev) => prev ? { ...prev, status: "completed" } : prev);
    } catch {
      clearInterval(interval);
      setOrderError("주문 처리 중 오류가 발생했습니다.");
    } finally {
      setOrdering(false);
    }
  }, [bookId, recipientName, recipientPhone, postalCode, address1, address2, shippingMemo, validateForm]);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="text-center space-y-4">
          <div className="animate-spin w-10 h-10 border-3 border-primary border-t-transparent rounded-full mx-auto" />
          <p className="text-text-light">동화책을 불러오는 중...</p>
        </div>
      </div>
    );
  }

  if (error || !book) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="text-center space-y-4">
          <BookOpen className="w-12 h-12 text-text-lighter mx-auto" />
          <p className="text-error-dark">{error || "동화책을 찾을 수 없습니다"}</p>
          <Button onClick={() => router.push("/bookshelf")}>내 책장으로</Button>
        </div>
      </div>
    );
  }

  const hasThumbnails = thumbnails && thumbnails.pages.length > 0;
  const canOrder = book.status === "confirmed" && hasThumbnails;

  // 입력 필드 공통 스타일
  const inputClass = (field: string) =>
    `w-full px-4 py-2.5 rounded-xl border text-sm transition-colors focus:outline-none focus:ring-2 focus:ring-primary/40 ${
      formErrors[field] ? "border-error bg-error/5" : "border-secondary hover:border-primary/40"
    }`;

  return (
    <PageTransition>
      <div className="max-w-7xl mx-auto px-2 sm:px-4 py-4 pb-20 md:pb-4">
        {/* 상단 */}
        <div className="flex items-center justify-between mb-4">
          <button onClick={() => router.push("/bookshelf")}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white border border-secondary hover:border-primary hover:text-primary transition-all shadow-sm"
          >
            <ArrowLeft size={18} />
            <span className="text-sm font-medium">내 책장</span>
          </button>
          {book.status === "confirmed" && !hasThumbnails ? (
            <div className="flex items-center gap-2 px-4 py-2 rounded-full bg-secondary/50 text-text-light text-sm">
              <div className="animate-spin w-4 h-4 border-2 border-primary border-t-transparent rounded-full" />
              책을 준비하고 있어요
            </div>
          ) : canOrder ? (
            <Button onClick={openOrderModal}
              className="gap-2 bg-primary hover:bg-primary/90 text-white rounded-full px-6"
            >
              <ShoppingCart size={16} />주문하기
            </Button>
          ) : null}
        </div>

        {/* 뷰어 */}
        {hasThumbnails ? (
          <BookViewer cover={thumbnails.cover} pages={thumbnails.pages}
            title={book.title || "동화책"} author={book.child_name} />
        ) : (
          <ThumbnailLoading bookId={bookId!} onLoaded={(t) => setThumbnails(t)} />
        )}
      </div>

      {/* ========== 주문 모달 ========== */}
      <AnimatePresence>
        {showOrderModal && (
          <motion.div
            initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm p-4"
            onClick={(e) => { if (e.target === e.currentTarget && !ordering) setShowOrderModal(false); }}
          >
            <motion.div
              initial={{ scale: 0.95, y: 10 }} animate={{ scale: 1, y: 0 }} exit={{ scale: 0.95, y: 10 }}
              className="bg-white rounded-3xl shadow-hover max-w-lg w-full max-h-[90vh] overflow-y-auto"
            >
              {/* ── 주문 진행 중 ── */}
              {ordering ? (
                <div className="p-8 text-center">
                  <div className="relative w-20 h-20 mx-auto mb-6">
                    <div className="absolute inset-0 border-4 border-primary/20 rounded-full" />
                    <motion.div
                      className="absolute inset-0 border-4 border-transparent border-t-primary rounded-full"
                      animate={{ rotate: 360 }}
                      transition={{ repeat: Infinity, duration: 1, ease: "linear" }}
                    />
                    <div className="absolute inset-0 flex items-center justify-center">
                      <Package className="w-8 h-8 text-primary" />
                    </div>
                  </div>
                  <h3 className="text-lg font-bold text-text mb-2">동화책을 만들고 있어요</h3>
                  <motion.p key={orderStep} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
                    className="text-sm text-text-light">{orderStep}</motion.p>
                  <p className="text-xs text-text-lighter mt-4">잠시만 기다려주세요. 30초~1분 정도 소요됩니다.</p>
                </div>

              /* ── 주문 완료 ── */
              ) : orderComplete && orderResult ? (
                <div className="p-8 text-center">
                  <motion.div initial={{ scale: 0 }} animate={{ scale: 1 }}
                    transition={{ delay: 0.2, type: "spring", stiffness: 200 }}
                    className="w-20 h-20 mx-auto mb-6 bg-success/20 rounded-full flex items-center justify-center"
                  >
                    <PartyPopper className="w-10 h-10 text-success" />
                  </motion.div>
                  <h3 className="text-2xl font-bold text-text mb-2">주문이 완료되었습니다!</h3>
                  <p className="text-text-light mb-6">{book.child_name}의 동화책이 곧 만들어져요</p>

                  <div className="bg-background rounded-2xl p-4 mb-6 text-left space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-text-light">주문 번호</span>
                      <span className="font-medium text-text">{orderResult.bookprint_order_uid || `#${orderResult.id}`}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-text-light">상태</span>
                      <span className="font-medium text-primary">결제 완료</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-text-light">결제 금액</span>
                      <span className="font-medium text-text">{orderResult.total_amount.toLocaleString()}원</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-text-light">수령인</span>
                      <span className="font-medium text-text">{orderResult.recipient_name}</span>
                    </div>
                  </div>

                  <p className="text-xs text-text-lighter mb-6">
                    Sandbox 환경에서는 결제 완료(PAID) 상태에서 정지됩니다.
                  </p>

                  <div className="flex flex-col gap-3">
                    <Button onClick={() => { setShowOrderModal(false); router.push("/mypage/orders"); }} className="w-full">
                      주문내역 보기
                    </Button>
                    <Button variant="outline" onClick={() => setShowOrderModal(false)} className="w-full">
                      계속 보기
                    </Button>
                  </div>
                </div>

              /* ── 주문 입력 폼 ── */
              ) : (
                <div className="p-6 sm:p-7 space-y-5">
                  {/* 헤더 */}
                  <div className="flex items-center justify-between">
                    <h4 className="text-lg font-bold text-text">주문하기</h4>
                    <button onClick={() => setShowOrderModal(false)}
                      className="w-8 h-8 rounded-full flex items-center justify-center hover:bg-secondary/50 transition-colors"
                    ><X size={18} className="text-text-light" /></button>
                  </div>

                  {/* 동화책 정보 */}
                  <div className="bg-background rounded-2xl p-4">
                    <h5 className="text-sm font-bold text-text mb-3 flex items-center gap-2">
                      <Package className="w-4 h-4 text-primary" />주문 동화책
                    </h5>
                    <div className="space-y-1.5 text-sm">
                      <div className="flex justify-between">
                        <span className="text-text-light">제목</span>
                        <span className="text-text font-medium">{book.title || `${book.child_name}의 동화책`}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-text-light">아이 이름</span>
                        <span className="text-text">{book.child_name}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-text-light">판형</span>
                        <span className="text-text">{specs.find(s => s.uid === book.book_spec_uid)?.name || book.book_spec_uid}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-text-light">페이지 수</span>
                        <span className="text-text">{book.page_count}페이지</span>
                      </div>
                    </div>
                  </div>

                  {/* 견적 정보 */}
                  <div className="bg-background rounded-2xl p-4">
                    <h5 className="text-sm font-bold text-text mb-3 flex items-center gap-2">
                      <FileText className="w-4 h-4 text-primary" />예상 가격
                    </h5>
                    {estimateLoading ? (
                      <div className="flex items-center justify-center py-3">
                        <Loader2 className="w-4 h-4 animate-spin text-primary" />
                        <span className="ml-2 text-sm text-text-light">견적 계산 중...</span>
                      </div>
                    ) : estimate ? (
                      <div className="space-y-1.5 text-sm">
                        <div className="flex justify-between">
                          <span className="text-text-light">제작비</span>
                          <span className="text-text">{estimate.product_amount.toLocaleString()}원</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-text-light">배송비</span>
                          <span className="text-text">{estimate.shipping_fee.toLocaleString()}원</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-text-light">포장비</span>
                          <span className="text-text">{estimate.packaging_fee.toLocaleString()}원</span>
                        </div>
                        <div className="border-t border-secondary/30 pt-2 mt-2 flex justify-between">
                          <span className="text-text font-bold">총 금액</span>
                          <span className="text-primary font-bold text-lg">{estimate.total_amount.toLocaleString()}원</span>
                        </div>
                      </div>
                    ) : (
                      <p className="text-sm text-text-light">견적을 불러올 수 없습니다.</p>
                    )}
                  </div>

                  {/* 배송 정보 */}
                  <div>
                    <h5 className="text-sm font-bold text-text mb-3 flex items-center gap-2">
                      <Truck className="w-4 h-4 text-primary" />배송 정보
                    </h5>
                    <div className="space-y-3">
                      <div>
                        <label className="flex items-center gap-1.5 text-xs font-medium text-text mb-1">
                          <User className="w-3 h-3 text-text-light" />수령인 <span className="text-error">*</span>
                        </label>
                        <input type="text" value={recipientName}
                          onChange={(e) => { setRecipientName(e.target.value); setFormErrors(p => ({ ...p, recipientName: "" })); }}
                          placeholder="수령인 이름" className={inputClass("recipientName")} />
                        {formErrors.recipientName && <p className="text-xs text-error mt-1">{formErrors.recipientName}</p>}
                      </div>
                      <div>
                        <label className="flex items-center gap-1.5 text-xs font-medium text-text mb-1">
                          <Phone className="w-3 h-3 text-text-light" />전화번호 <span className="text-error">*</span>
                        </label>
                        <input type="tel" value={recipientPhone}
                          onChange={(e) => { setRecipientPhone(e.target.value); setFormErrors(p => ({ ...p, recipientPhone: "" })); }}
                          placeholder="010-1234-5678" className={inputClass("recipientPhone")} />
                        {formErrors.recipientPhone && <p className="text-xs text-error mt-1">{formErrors.recipientPhone}</p>}
                      </div>
                      <div>
                        <label className="flex items-center gap-1.5 text-xs font-medium text-text mb-1">
                          <MapPin className="w-3 h-3 text-text-light" />우편번호 <span className="text-error">*</span>
                        </label>
                        <input type="text" value={postalCode} maxLength={5}
                          onChange={(e) => { setPostalCode(e.target.value); setFormErrors(p => ({ ...p, postalCode: "" })); }}
                          placeholder="12345" className={inputClass("postalCode")} />
                        {formErrors.postalCode && <p className="text-xs text-error mt-1">{formErrors.postalCode}</p>}
                      </div>
                      <div>
                        <label className="flex items-center gap-1.5 text-xs font-medium text-text mb-1">
                          <MapPin className="w-3 h-3 text-text-light" />주소 <span className="text-error">*</span>
                        </label>
                        <input type="text" value={address1}
                          onChange={(e) => { setAddress1(e.target.value); setFormErrors(p => ({ ...p, address1: "" })); }}
                          placeholder="도로명 주소 또는 지번 주소" className={inputClass("address1")} />
                        {formErrors.address1 && <p className="text-xs text-error mt-1">{formErrors.address1}</p>}
                      </div>
                      <div>
                        <label className="text-xs font-medium text-text mb-1 block">상세주소</label>
                        <input type="text" value={address2} onChange={(e) => setAddress2(e.target.value)}
                          placeholder="아파트/동/호수"
                          className="w-full px-4 py-2.5 rounded-xl border border-secondary text-sm transition-colors focus:outline-none focus:ring-2 focus:ring-primary/40 hover:border-primary/40" />
                      </div>
                      <div>
                        <label className="text-xs font-medium text-text mb-1 block">배송 메모</label>
                        <input type="text" value={shippingMemo} onChange={(e) => setShippingMemo(e.target.value)}
                          placeholder="부재시 경비실에 맡겨주세요"
                          className="w-full px-4 py-2.5 rounded-xl border border-secondary text-sm transition-colors focus:outline-none focus:ring-2 focus:ring-primary/40 hover:border-primary/40" />
                      </div>
                    </div>
                  </div>

                  {/* Sandbox 안내 */}
                  <div className="bg-accent/10 rounded-xl p-3 text-xs text-text-light flex items-start gap-2">
                    <AlertCircle className="w-3.5 h-3.5 text-accent flex-shrink-0 mt-0.5" />
                    <div>
                      <p className="font-medium text-text">Sandbox 환경 안내</p>
                      <p className="mt-0.5">테스트 환경입니다. 결제 완료(PAID) 상태에서 정지되며, 실제 인쇄/배송은 진행되지 않습니다.</p>
                    </div>
                  </div>

                  {/* 에러 */}
                  {orderError && (
                    <div className="p-3 bg-error/10 border border-error/30 rounded-xl flex items-start gap-2">
                      <AlertCircle className="w-4 h-4 text-error flex-shrink-0 mt-0.5" />
                      <p className="text-sm text-error">{orderError}</p>
                    </div>
                  )}

                  {/* 주문 버튼 */}
                  <div className="flex gap-3 pt-1">
                    <Button variant="ghost" className="flex-1" onClick={() => setShowOrderModal(false)}>취소</Button>
                    <Button className="flex-1 bg-primary hover:bg-primary/90 text-white gap-2 h-12 text-base" onClick={handleOrder}>
                      <CheckCircle className="w-5 h-5" />
                      {estimate ? `${estimate.total_amount.toLocaleString()}원 주문하기` : "주문하기"}
                    </Button>
                  </div>
                </div>
              )}
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </PageTransition>
  );
}

export default function BookViewPage() {
  return (
    <AuthGuard>
      <BookViewContent />
    </AuthGuard>
  );
}
