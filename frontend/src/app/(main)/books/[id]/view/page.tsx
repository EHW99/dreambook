"use client";

import { useState, useEffect } from "react";
import { useRouter, useParams } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { ArrowLeft, BookOpen, ShoppingCart, X, Loader2 } from "lucide-react";
import { AuthGuard } from "@/components/auth-guard";
import { PageTransition } from "@/components/page-transition";
import { Button } from "@/components/ui/button";
import { apiClient, BookItem, PageItem } from "@/lib/api";
import BookViewer from "@/components/book-viewer";
import BookPreview from "@/components/book-preview";

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
  const [orderError, setOrderError] = useState<string | null>(null);
  const [orderSuccess, setOrderSuccess] = useState(false);
  const [shipping, setShipping] = useState({
    recipient_name: "",
    recipient_phone: "",
    postal_code: "",
    address1: "",
    address2: "",
    shipping_memo: "",
  });

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

  const handleOrder = async () => {
    if (!bookId) return;
    if (!shipping.recipient_name || !shipping.recipient_phone || !shipping.postal_code || !shipping.address1) {
      setOrderError("필수 항목을 모두 입력해주세요");
      return;
    }
    setOrdering(true);
    setOrderError(null);
    const res = await apiClient.createOrder(bookId, shipping);
    if (res.data) {
      setOrderSuccess(true);
      setBook((prev) => prev ? { ...prev, status: "completed" } : prev);
    } else {
      setOrderError(res.error || "주문에 실패했습니다");
    }
    setOrdering(false);
  };

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
  const canOrder = book.status === "confirmed";

  return (
    <PageTransition>
      <div className="max-w-7xl mx-auto px-2 sm:px-4 py-4 pb-20 md:pb-4">
        {/* 상단: 뒤로가기 + 주문 버튼 */}
        <div className="flex items-center justify-between mb-4">
          <button
            onClick={() => router.back()}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white border border-secondary hover:border-primary hover:text-primary transition-all shadow-sm"
          >
            <ArrowLeft size={18} />
            <span className="text-sm font-medium">내 책장</span>
          </button>

          {canOrder && (
            <Button
              onClick={() => setShowOrderModal(true)}
              className="gap-2 bg-primary hover:bg-primary/90 text-white rounded-full px-6"
            >
              <ShoppingCart size={16} />
              주문하기
            </Button>
          )}
        </div>

        {/* 뷰어 */}
        {hasThumbnails ? (
          <BookViewer
            cover={thumbnails.cover}
            pages={thumbnails.pages}
            title={book.title || "동화책"}
            author={book.child_name}
          />
        ) : pages.length > 0 ? (
          <BookPreview
            pages={pages}
            title={book.title || "동화책"}
            childName={book.child_name}
            coverImageUrl={book.cover_image_path || undefined}
          />
        ) : (
          <div className="flex items-center justify-center py-20">
            <div className="text-center">
              <BookOpen className="w-12 h-12 mx-auto text-text-lighter mb-4" />
              <p className="text-text-light">페이지가 없습니다</p>
            </div>
          </div>
        )}
      </div>

      {/* 주문 모달 */}
      <AnimatePresence>
        {showOrderModal && (
          <motion.div
            initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm p-4"
            onClick={(e) => { if (e.target === e.currentTarget && !ordering) setShowOrderModal(false); }}
          >
            <motion.div
              initial={{ scale: 0.95, y: 10 }} animate={{ scale: 1, y: 0 }} exit={{ scale: 0.95, y: 10 }}
              className="bg-white rounded-3xl shadow-hover p-6 sm:p-7 max-w-md w-full max-h-[90vh] overflow-y-auto"
            >
              {orderSuccess ? (
                /* 주문 완료 */
                <div className="text-center py-6">
                  <div className="w-16 h-16 rounded-full bg-success/20 flex items-center justify-center mx-auto mb-4">
                    <ShoppingCart className="w-8 h-8 text-success" />
                  </div>
                  <h4 className="text-xl font-bold text-text mb-2">주문 완료!</h4>
                  <p className="text-sm text-text-light mb-6">동화책이 곧 인쇄되어 배송됩니다.</p>
                  <Button onClick={() => { setShowOrderModal(false); router.push("/bookshelf"); }}
                    className="bg-primary hover:bg-primary/90 text-white"
                  >
                    내 책장으로
                  </Button>
                </div>
              ) : (
                /* 배송지 입력 */
                <>
                  <div className="flex items-center justify-between mb-5">
                    <h4 className="text-lg font-bold text-text">주문하기</h4>
                    <button onClick={() => setShowOrderModal(false)} disabled={ordering}
                      className="w-8 h-8 rounded-full flex items-center justify-center hover:bg-secondary/50 transition-colors"
                    >
                      <X size={18} className="text-text-light" />
                    </button>
                  </div>

                  <div className="space-y-3">
                    <div>
                      <label className="text-xs font-medium text-text-light mb-1 block">수령인 *</label>
                      <input type="text" value={shipping.recipient_name}
                        onChange={(e) => setShipping({ ...shipping, recipient_name: e.target.value })}
                        className="w-full border-2 border-secondary rounded-xl px-3 py-2.5 text-sm outline-none focus:border-primary transition-colors"
                        placeholder="홍길동"
                      />
                    </div>
                    <div>
                      <label className="text-xs font-medium text-text-light mb-1 block">연락처 *</label>
                      <input type="tel" value={shipping.recipient_phone}
                        onChange={(e) => setShipping({ ...shipping, recipient_phone: e.target.value })}
                        className="w-full border-2 border-secondary rounded-xl px-3 py-2.5 text-sm outline-none focus:border-primary transition-colors"
                        placeholder="010-1234-5678"
                      />
                    </div>
                    <div>
                      <label className="text-xs font-medium text-text-light mb-1 block">우편번호 *</label>
                      <input type="text" value={shipping.postal_code}
                        onChange={(e) => setShipping({ ...shipping, postal_code: e.target.value })}
                        className="w-full border-2 border-secondary rounded-xl px-3 py-2.5 text-sm outline-none focus:border-primary transition-colors"
                        placeholder="12345"
                      />
                    </div>
                    <div>
                      <label className="text-xs font-medium text-text-light mb-1 block">주소 *</label>
                      <input type="text" value={shipping.address1}
                        onChange={(e) => setShipping({ ...shipping, address1: e.target.value })}
                        className="w-full border-2 border-secondary rounded-xl px-3 py-2.5 text-sm outline-none focus:border-primary transition-colors"
                        placeholder="서울시 강남구 ..."
                      />
                    </div>
                    <div>
                      <label className="text-xs font-medium text-text-light mb-1 block">상세주소</label>
                      <input type="text" value={shipping.address2}
                        onChange={(e) => setShipping({ ...shipping, address2: e.target.value })}
                        className="w-full border-2 border-secondary rounded-xl px-3 py-2.5 text-sm outline-none focus:border-primary transition-colors"
                        placeholder="101동 202호"
                      />
                    </div>
                    <div>
                      <label className="text-xs font-medium text-text-light mb-1 block">배송 메모</label>
                      <input type="text" value={shipping.shipping_memo}
                        onChange={(e) => setShipping({ ...shipping, shipping_memo: e.target.value })}
                        className="w-full border-2 border-secondary rounded-xl px-3 py-2.5 text-sm outline-none focus:border-primary transition-colors"
                        placeholder="부재 시 경비실에 맡겨주세요"
                      />
                    </div>
                  </div>

                  {orderError && (
                    <p className="text-xs text-error-dark mt-3 text-center">{orderError}</p>
                  )}

                  <div className="flex gap-3 mt-5">
                    <Button variant="ghost" className="flex-1" onClick={() => setShowOrderModal(false)} disabled={ordering}>
                      취소
                    </Button>
                    <Button className="flex-1 bg-primary hover:bg-primary/90 text-white gap-2" onClick={handleOrder} disabled={ordering}>
                      {ordering ? <><Loader2 size={14} className="animate-spin" />주문 중...</> : "주문하기"}
                    </Button>
                  </div>
                </>
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
