"use client";

import { useState, useEffect, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Package,
  Truck,
  MapPin,
  ChevronRight,
  X,
  AlertTriangle,
  CheckCircle2,
  Pencil,
  ShoppingBag,
  Clock,
  Ban,
  Loader2,
  BookOpen,
} from "lucide-react";
import {
  apiClient,
  OrderListItem,
  OrderDetailResult,
  ShippingData,
} from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

// ── 상태 매핑 ──
const ORDER_STATUS: Record<
  string,
  { label: string; color: string; bg: string; stripe: string; icon: typeof Package }
> = {
  PAID:             { label: "결제 완료",  color: "text-accent-dark",  bg: "bg-accent/10",  stripe: "bg-accent-dark",  icon: CheckCircle2 },
  PDF_READY:        { label: "PDF 준비",   color: "text-accent-dark",  bg: "bg-accent/10",  stripe: "bg-accent-dark",  icon: Package },
  CONFIRMED:        { label: "주문 확정",  color: "text-success-dark", bg: "bg-success/10", stripe: "bg-success-dark", icon: CheckCircle2 },
  IN_PRODUCTION:    { label: "제작 중",    color: "text-warning-dark", bg: "bg-warning/10", stripe: "bg-warning-dark", icon: Clock },
  SHIPPED:          { label: "배송 중",    color: "text-primary-dark", bg: "bg-primary/10", stripe: "bg-primary-dark", icon: Truck },
  DELIVERED:        { label: "배송 완료",  color: "text-success-dark", bg: "bg-success/10", stripe: "bg-success-dark", icon: CheckCircle2 },
  CANCELLED:        { label: "취소됨",     color: "text-text-lighter", bg: "bg-gray-100",   stripe: "bg-gray-300",     icon: Ban },
  CANCELLED_REFUND: { label: "취소/환불",  color: "text-text-lighter", bg: "bg-gray-100",   stripe: "bg-gray-300",     icon: Ban },
};

function getStatusInfo(status: string) {
  return ORDER_STATUS[status] || {
    label: status, color: "text-text-lighter", bg: "bg-gray-100", stripe: "bg-gray-300", icon: Package,
  };
}

function formatDate(dateStr: string) {
  const d = new Date(dateStr);
  return `${d.getFullYear()}.${String(d.getMonth() + 1).padStart(2, "0")}.${String(d.getDate()).padStart(2, "0")}`;
}

function formatPrice(amount: number) {
  return amount.toLocaleString("ko-KR") + "원";
}

function canCancel(sc: number) { return sc === 20 || sc === 25; }
function canChangeShipping(sc: number) { return sc === 20 || sc === 25 || sc === 30; }

// ── 컴포넌트 ──
interface OrdersTabProps {
  onOrdersLoaded?: (bookIds: Set<number>) => void;
}

export function OrdersTab({ onOrdersLoaded }: OrdersTabProps) {
  const [orders, setOrders] = useState<OrderListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // 모달
  const [modalOrderId, setModalOrderId] = useState<number | null>(null);
  const [detail, setDetail] = useState<OrderDetailResult | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);

  // 취소
  const [cancelConfirm, setCancelConfirm] = useState(false);
  const [isCancelling, setIsCancelling] = useState(false);

  // 배송지
  const [shippingEdit, setShippingEdit] = useState(false);
  const [shippingForm, setShippingForm] = useState<Partial<ShippingData>>({});
  const [isUpdatingShipping, setIsUpdatingShipping] = useState(false);
  const [shippingSuccess, setShippingSuccess] = useState("");

  const fetchOrders = useCallback(async () => {
    setLoading(true);
    const result = await apiClient.getOrders();
    if (result.data) {
      setOrders(result.data);
      onOrdersLoaded?.(new Set(result.data.map((o) => o.book_id)));
    } else {
      setError(result.error || "주문 내역을 불러오지 못했습니다");
    }
    setLoading(false);
  }, [onOrdersLoaded]);

  useEffect(() => { fetchOrders(); }, [fetchOrders]);

  // 모달 열기
  const openModal = async (orderId: number) => {
    setModalOrderId(orderId);
    setDetailLoading(true);
    setShippingEdit(false);
    setShippingSuccess("");
    setCancelConfirm(false);
    const res = await apiClient.getOrder(orderId);
    if (res.data) setDetail(res.data);
    setDetailLoading(false);
  };

  const closeModal = () => {
    setModalOrderId(null);
    setDetail(null);
    setShippingEdit(false);
    setShippingSuccess("");
    setCancelConfirm(false);
  };

  // 취소
  const handleCancel = async () => {
    if (!detail) return;
    setIsCancelling(true);
    const result = await apiClient.cancelOrder(detail.id);
    if (result.error) {
      setError(result.error);
    } else {
      await fetchOrders();
      const res = await apiClient.getOrder(detail.id);
      if (res.data) setDetail(res.data);
    }
    setCancelConfirm(false);
    setIsCancelling(false);
  };

  // 배송지
  const startShippingEdit = () => {
    if (!detail) return;
    setShippingForm({
      recipient_name: detail.recipient_name,
      recipient_phone: detail.recipient_phone,
      postal_code: detail.postal_code,
      address1: detail.address1,
      address2: detail.address2 || "",
      shipping_memo: detail.shipping_memo || "",
    });
    setShippingEdit(true);
    setShippingSuccess("");
  };

  const handleShippingUpdate = async () => {
    if (!detail) return;
    setIsUpdatingShipping(true);
    const result = await apiClient.updateShipping(detail.id, shippingForm);
    if (result.error) {
      setError(result.error);
    } else if (result.data) {
      setDetail(result.data);
      setShippingEdit(false);
      setShippingSuccess("배송지가 변경되었습니다");
    }
    setIsUpdatingShipping(false);
  };

  // ── 로딩 ──
  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-16">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
        <p className="mt-3 text-sm text-text-light">주문 내역을 불러오는 중...</p>
      </div>
    );
  }

  // ── 에러 ──
  if (error && !orders.length) {
    return (
      <div className="flex flex-col items-center justify-center py-16">
        <AlertTriangle className="w-10 h-10 text-error-dark mb-3" />
        <p className="text-sm text-error-dark">{error}</p>
        <Button variant="ghost" className="mt-4" onClick={fetchOrders}>다시 시도</Button>
      </div>
    );
  }

  // ── 빈 상태 ──
  if (orders.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-20">
        <div className="w-20 h-20 rounded-full bg-gradient-to-br from-primary/10 to-accent/10 flex items-center justify-center mb-5">
          <BookOpen className="w-9 h-9 text-primary" />
        </div>
        <p className="text-lg font-bold text-text mb-1">아직 주문이 없어요</p>
        <p className="text-sm text-text-light text-center max-w-xs">
          동화책을 완성하면 세상에 단 하나뿐인 실물 책으로 주문할 수 있어요
        </p>
      </div>
    );
  }

  // ── 목록 + 모달 ──
  return (
    <>
      {/* 목록 */}
      <div className="divide-y divide-text/10">
        {orders.map((order, i) => {
          const info = getStatusInfo(order.status);
          return (
            <motion.button
              key={order.id}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: i * 0.03 }}
              onClick={() => openModal(order.id)}
              className="w-full py-5 text-left hover:bg-gray-50/50 transition-colors group"
            >
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1 min-w-0">
                  <p className="text-base font-medium text-text truncate">
                    {order.book_title || `동화책 #${order.book_id}`}
                  </p>
                  <div className="flex items-center gap-1.5 mt-1.5">
                    <span className={`text-xs font-semibold ${info.color}`}>
                      {info.label}
                    </span>
                    <span className="text-text-lighter text-xs">·</span>
                    <span className="text-xs text-text-lighter">
                      {formatDate(order.ordered_at)}
                    </span>
                    <span className="text-text-lighter text-xs">·</span>
                    <span className="text-xs text-text-lighter">
                      주문번호 #{order.id}
                    </span>
                  </div>
                </div>
                <div className="text-right shrink-0">
                  <p className="text-base font-bold text-text">
                    {formatPrice(order.total_amount)}
                  </p>
                  <p className="text-[11px] text-text-lighter mt-1 group-hover:text-primary transition-colors">
                    상세보기 →
                  </p>
                </div>
              </div>
            </motion.button>
          );
        })}
      </div>

      {/* ── 상세 모달 ── */}
      <AnimatePresence>
        {modalOrderId !== null && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="fixed inset-0 z-50 flex items-center justify-center px-4"
            onClick={closeModal}
          >
            <div className="absolute inset-0 bg-black/40" />

            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 10 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 10 }}
              transition={{ duration: 0.2 }}
              className="relative bg-white rounded-3xl shadow-xl w-full max-w-md max-h-[85vh] overflow-y-auto"
              onClick={(e) => e.stopPropagation()}
            >
              {detailLoading || !detail ? (
                <div className="flex flex-col items-center justify-center py-20">
                  <Loader2 className="w-8 h-8 animate-spin text-primary" />
                  <p className="mt-3 text-sm text-text-light">불러오는 중...</p>
                </div>
              ) : (
                <div className="p-6 sm:p-7 space-y-5">
                  {/* 닫기 */}
                  <button
                    onClick={closeModal}
                    className="absolute top-4 right-4 w-8 h-8 rounded-full hover:bg-gray-100 flex items-center justify-center transition-colors"
                  >
                    <X className="w-4 h-4 text-text-lighter" />
                  </button>

                  {/* 상태 + 금액 */}
                  {(() => {
                    const info = getStatusInfo(detail.status);
                    return (
                      <div>
                        <div className="flex items-center gap-2 mb-3">
                          <span className={`text-xs font-bold px-2.5 py-1 rounded-full ${info.bg} ${info.color}`}>
                            {info.label}
                          </span>
                          <span className="text-xs text-text-lighter">
                            #{detail.id}
                          </span>
                        </div>
                        <p className="text-xs text-text-lighter">
                          {formatDate(detail.ordered_at)} 주문
                        </p>
                        <p className="text-2xl font-bold text-text mt-1">
                          {formatPrice(detail.total_amount)}
                        </p>
                      </div>
                    );
                  })()}

                  <div className="border-t border-secondary/30" />

                  {/* 성공 메시지 */}
                  <AnimatePresence>
                    {shippingSuccess && (
                      <motion.div
                        initial={{ opacity: 0, y: -8 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -8 }}
                        className="p-3 bg-success/15 border border-success/30 rounded-xl text-sm text-success-dark flex items-center gap-2"
                      >
                        <CheckCircle2 className="w-4 h-4" />
                        {shippingSuccess}
                      </motion.div>
                    )}
                  </AnimatePresence>

                  {/* 배송 정보 */}
                  <div>
                    <div className="flex items-center justify-between mb-3">
                      <h4 className="text-sm font-bold text-text flex items-center gap-1.5">
                        <MapPin className="w-3.5 h-3.5 text-primary" />
                        배송 정보
                      </h4>
                      {canChangeShipping(detail.status_code) && !shippingEdit && (
                        <button
                          onClick={startShippingEdit}
                          className="text-xs text-text-lighter hover:text-primary flex items-center gap-1 transition-colors"
                        >
                          <Pencil className="w-3 h-3" />
                          변경
                        </button>
                      )}
                    </div>

                    {!shippingEdit ? (
                      <div className="space-y-2 text-sm bg-gray-50 rounded-xl p-4">
                        {[
                          ["수령인", detail.recipient_name],
                          ["연락처", detail.recipient_phone],
                          ["주소", `(${detail.postal_code}) ${detail.address1}${detail.address2 ? ` ${detail.address2}` : ""}`],
                          ...(detail.shipping_memo ? [["메모", detail.shipping_memo]] : []),
                        ].map(([label, value]) => (
                          <div key={label} className="flex">
                            <span className="text-text-lighter w-14 shrink-0 text-xs">{label}</span>
                            <span className="text-text text-xs">{value}</span>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="space-y-2.5 bg-gray-50 rounded-xl p-4">
                        {[
                          { label: "수령인", key: "recipient_name" },
                          { label: "연락처", key: "recipient_phone" },
                          { label: "우편번호", key: "postal_code" },
                          { label: "주소", key: "address1" },
                          { label: "상세주소", key: "address2" },
                          { label: "배송 메모", key: "shipping_memo" },
                        ].map(({ label, key }) => (
                          <div key={key}>
                            <label className="block text-[11px] font-medium text-text-lighter mb-1">{label}</label>
                            <Input
                              value={(shippingForm as any)[key] || ""}
                              onChange={(e) => setShippingForm((p) => ({ ...p, [key]: e.target.value }))}
                              disabled={isUpdatingShipping}
                              className="h-9 text-sm"
                            />
                          </div>
                        ))}
                        <div className="flex gap-2 pt-1">
                          <Button variant="ghost" size="sm" className="flex-1" onClick={() => setShippingEdit(false)} disabled={isUpdatingShipping}>
                            취소
                          </Button>
                          <Button size="sm" className="flex-1" onClick={handleShippingUpdate} disabled={isUpdatingShipping}>
                            {isUpdatingShipping ? "변경 중..." : "배송지 변경"}
                          </Button>
                        </div>
                      </div>
                    )}
                  </div>

                  {/* 운송장 */}
                  {detail.tracking_number && (
                    <div>
                      <h4 className="text-sm font-bold text-text flex items-center gap-1.5 mb-3">
                        <Truck className="w-3.5 h-3.5 text-primary" />
                        배송 추적
                      </h4>
                      <div className="space-y-2 text-sm bg-gray-50 rounded-xl p-4">
                        <div className="flex">
                          <span className="text-text-lighter w-14 shrink-0 text-xs">택배사</span>
                          <span className="text-text text-xs">{detail.tracking_carrier || "-"}</span>
                        </div>
                        <div className="flex">
                          <span className="text-text-lighter w-14 shrink-0 text-xs">운송장</span>
                          <span className="text-text font-mono text-xs">{detail.tracking_number}</span>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* 취소 버튼 */}
                  {canCancel(detail.status_code) && !cancelConfirm && (
                    <button
                      onClick={() => setCancelConfirm(true)}
                      className="w-full text-center text-sm text-text-lighter hover:text-error-dark transition-colors py-2"
                    >
                      주문 취소
                    </button>
                  )}

                  {/* 취소 확인 */}
                  <AnimatePresence>
                    {cancelConfirm && (
                      <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: "auto" }}
                        exit={{ opacity: 0, height: 0 }}
                        className="overflow-hidden"
                      >
                        <div className="bg-error/5 border border-error/20 rounded-xl p-4">
                          <div className="flex items-center gap-2 mb-3">
                            <AlertTriangle className="w-4 h-4 text-error-dark" />
                            <p className="text-sm font-medium text-error-dark">정말 취소하시겠습니까?</p>
                          </div>
                          <div className="flex gap-2">
                            <Button variant="ghost" size="sm" className="flex-1" onClick={() => setCancelConfirm(false)} disabled={isCancelling}>
                              돌아가기
                            </Button>
                            <Button variant="destructive" size="sm" className="flex-1" onClick={handleCancel} disabled={isCancelling}>
                              {isCancelling ? "취소 중..." : "주문 취소"}
                            </Button>
                          </div>
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>
              )}
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
