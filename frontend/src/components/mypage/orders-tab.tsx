"use client";

import { useState, useEffect, useCallback } from "react";
import {
  apiClient,
  OrderListItem,
  OrderDetailResult,
  ShippingData,
} from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  ShoppingBagIcon,
  PackageIcon,
  TruckIcon,
  MapPinIcon,
  ChevronRightIcon,
  ChevronLeftIcon,
  XIcon,
  AlertTriangleIcon,
  CheckCircleIcon,
  EditIcon,
} from "@/components/icons";

// 주문 상태 정보
const ORDER_STATUS: Record<
  string,
  { label: string; color: string; icon: typeof PackageIcon }
> = {
  PAID: { label: "결제 완료", color: "bg-accent text-teal-800", icon: PackageIcon },
  PDF_READY: { label: "PDF 준비", color: "bg-accent text-teal-800", icon: PackageIcon },
  CONFIRMED: { label: "주문 확정", color: "bg-success text-green-800", icon: CheckCircleIcon },
  IN_PRODUCTION: { label: "제작 중", color: "bg-warning text-yellow-800", icon: PackageIcon },
  SHIPPED: { label: "배송 중", color: "bg-primary/20 text-primary-dark", icon: TruckIcon },
  DELIVERED: { label: "배송 완료", color: "bg-success text-green-800", icon: CheckCircleIcon },
  CANCELLED: { label: "취소됨", color: "bg-gray-200 text-gray-600", icon: XIcon },
  CANCELLED_REFUND: { label: "취소/환불", color: "bg-gray-200 text-gray-600", icon: XIcon },
};

function getOrderStatusInfo(status: string) {
  return (
    ORDER_STATUS[status] || {
      label: status,
      color: "bg-gray-200 text-gray-700",
      icon: PackageIcon,
    }
  );
}

function formatDate(dateStr: string) {
  const d = new Date(dateStr);
  return `${d.getFullYear()}.${String(d.getMonth() + 1).padStart(2, "0")}.${String(d.getDate()).padStart(2, "0")}`;
}

function formatPrice(amount: number) {
  return amount.toLocaleString("ko-KR") + "원";
}

// 취소 가능 상태 (PAID, PDF_READY)
function canCancel(statusCode: number) {
  return statusCode === 20 || statusCode === 25;
}

// 배송지 변경 가능 상태 (PAID ~ CONFIRMED)
function canChangeShipping(statusCode: number) {
  return statusCode === 20 || statusCode === 25 || statusCode === 30;
}

interface OrdersTabProps {
  onOrdersLoaded?: (bookIds: Set<number>) => void;
}

export function OrdersTab({ onOrdersLoaded }: OrdersTabProps) {
  const [orders, setOrders] = useState<OrderListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // 상세 보기
  const [selectedOrderId, setSelectedOrderId] = useState<number | null>(null);
  const [orderDetail, setOrderDetail] = useState<OrderDetailResult | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);

  // 취소
  const [cancelTarget, setCancelTarget] = useState<number | null>(null);
  const [isCancelling, setIsCancelling] = useState(false);

  // 배송지 변경
  const [shippingEditMode, setShippingEditMode] = useState(false);
  const [shippingForm, setShippingForm] = useState<Partial<ShippingData>>({});
  const [isUpdatingShipping, setIsUpdatingShipping] = useState(false);
  const [shippingSuccess, setShippingSuccess] = useState("");

  const fetchOrders = useCallback(async () => {
    setLoading(true);
    const result = await apiClient.getOrders();
    if (result.data) {
      setOrders(result.data);
      if (onOrdersLoaded) {
        onOrdersLoaded(new Set(result.data.map((o) => o.book_id)));
      }
    } else {
      setError(result.error || "주문 내역을 불러오지 못했습니다");
    }
    setLoading(false);
  }, [onOrdersLoaded]);

  useEffect(() => {
    fetchOrders();
  }, [fetchOrders]);

  const fetchOrderDetail = async (orderId: number) => {
    setDetailLoading(true);
    setShippingEditMode(false);
    setShippingSuccess("");
    const result = await apiClient.getOrder(orderId);
    if (result.data) {
      setOrderDetail(result.data);
    }
    setDetailLoading(false);
  };

  const handleSelectOrder = (orderId: number) => {
    setSelectedOrderId(orderId);
    fetchOrderDetail(orderId);
  };

  const handleBack = () => {
    setSelectedOrderId(null);
    setOrderDetail(null);
    setShippingEditMode(false);
    setShippingSuccess("");
  };

  const handleCancel = async () => {
    if (cancelTarget === null) return;
    setIsCancelling(true);
    const result = await apiClient.cancelOrder(cancelTarget);
    if (result.error) {
      setError(result.error);
    } else {
      // 목록 새로고침
      await fetchOrders();
      if (selectedOrderId === cancelTarget) {
        fetchOrderDetail(cancelTarget);
      }
    }
    setCancelTarget(null);
    setIsCancelling(false);
  };

  const handleShippingEdit = () => {
    if (!orderDetail) return;
    setShippingForm({
      recipient_name: orderDetail.recipient_name,
      recipient_phone: orderDetail.recipient_phone,
      postal_code: orderDetail.postal_code,
      address1: orderDetail.address1,
      address2: orderDetail.address2 || "",
      shipping_memo: orderDetail.shipping_memo || "",
    });
    setShippingEditMode(true);
    setShippingSuccess("");
  };

  const handleShippingUpdate = async () => {
    if (!orderDetail) return;
    setIsUpdatingShipping(true);

    const result = await apiClient.updateShipping(orderDetail.id, shippingForm);
    if (result.error) {
      setError(result.error);
    } else if (result.data) {
      setOrderDetail(result.data);
      setShippingEditMode(false);
      setShippingSuccess("배송지가 변경되었습니다");
    }
    setIsUpdatingShipping(false);
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-16">
        <div className="w-10 h-10 border-3 border-primary border-t-transparent rounded-full animate-spin" />
        <p className="mt-4 text-sm text-text-light">주문 내역을 불러오는 중...</p>
      </div>
    );
  }

  if (error && !orders.length) {
    return (
      <div className="flex flex-col items-center justify-center py-16">
        <AlertTriangleIcon className="w-10 h-10 text-error-dark mb-3" />
        <p className="text-sm text-error-dark">{error}</p>
        <Button variant="ghost" className="mt-4" onClick={fetchOrders}>
          다시 시도
        </Button>
      </div>
    );
  }

  // 빈 상태
  if (orders.length === 0 && !selectedOrderId) {
    return (
      <div className="flex flex-col items-center justify-center py-20">
        <div className="w-20 h-20 rounded-full bg-secondary/50 flex items-center justify-center mb-6">
          <ShoppingBagIcon className="w-10 h-10 text-primary" />
        </div>
        <p className="text-lg font-medium text-text mb-2">주문 내역이 없어요</p>
        <p className="text-sm text-text-light">
          동화책을 완성하면 실물 책으로 주문할 수 있어요
        </p>
      </div>
    );
  }

  // 주문 상세 뷰
  if (selectedOrderId && orderDetail) {
    const statusInfo = getOrderStatusInfo(orderDetail.status);

    return (
      <div className="space-y-6">
        {/* 뒤로가기 */}
        <button
          onClick={handleBack}
          className="flex items-center gap-1 text-sm text-text-light hover:text-primary transition-colors"
        >
          <ChevronLeftIcon className="w-4 h-4" />
          주문 목록으로
        </button>

        {/* 주문 상태 */}
        <div className="bg-gradient-to-r from-secondary/30 to-primary/10 rounded-2xl p-6">
          <div className="flex items-center gap-3 mb-3">
            <span className={`text-xs font-semibold px-3 py-1 rounded-full ${statusInfo.color}`}>
              {statusInfo.label}
            </span>
            <span className="text-xs text-text-lighter">
              주문번호 #{orderDetail.id}
            </span>
          </div>
          <p className="text-sm text-text-light">
            주문일: {formatDate(orderDetail.ordered_at)}
          </p>
          <p className="text-lg font-bold text-text mt-1">
            {formatPrice(orderDetail.total_amount)}
          </p>
        </div>

        {/* 성공 메시지 */}
        {shippingSuccess && (
          <div className="p-3 bg-success/20 border border-success rounded-2xl text-sm text-success-dark flex items-center gap-2">
            <CheckCircleIcon className="w-4 h-4" />
            {shippingSuccess}
          </div>
        )}

        {/* 배송 정보 */}
        <div className="bg-white border border-secondary/60 rounded-2xl p-6">
          <div className="flex items-center justify-between mb-4">
            <h4 className="font-bold text-text flex items-center gap-2">
              <MapPinIcon className="w-4 h-4 text-primary" />
              배송 정보
            </h4>
            {canChangeShipping(orderDetail.status_code) && !shippingEditMode && (
              <Button size="sm" variant="ghost" onClick={handleShippingEdit}>
                <EditIcon className="w-3.5 h-3.5 mr-1" />
                변경
              </Button>
            )}
          </div>

          {!shippingEditMode ? (
            <div className="space-y-2 text-sm">
              <div className="flex">
                <span className="text-text-light w-20 shrink-0">수령인</span>
                <span className="text-text">{orderDetail.recipient_name}</span>
              </div>
              <div className="flex">
                <span className="text-text-light w-20 shrink-0">연락처</span>
                <span className="text-text">{orderDetail.recipient_phone}</span>
              </div>
              <div className="flex">
                <span className="text-text-light w-20 shrink-0">주소</span>
                <span className="text-text">
                  ({orderDetail.postal_code}) {orderDetail.address1}
                  {orderDetail.address2 && ` ${orderDetail.address2}`}
                </span>
              </div>
              {orderDetail.shipping_memo && (
                <div className="flex">
                  <span className="text-text-light w-20 shrink-0">메모</span>
                  <span className="text-text">{orderDetail.shipping_memo}</span>
                </div>
              )}
            </div>
          ) : (
            <div className="space-y-3">
              <div>
                <label className="block text-xs font-medium text-text-light mb-1">수령인</label>
                <Input
                  value={shippingForm.recipient_name || ""}
                  onChange={(e) =>
                    setShippingForm((p) => ({ ...p, recipient_name: e.target.value }))
                  }
                  disabled={isUpdatingShipping}
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-text-light mb-1">연락처</label>
                <Input
                  value={shippingForm.recipient_phone || ""}
                  onChange={(e) =>
                    setShippingForm((p) => ({ ...p, recipient_phone: e.target.value }))
                  }
                  disabled={isUpdatingShipping}
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-text-light mb-1">우편번호</label>
                <Input
                  value={shippingForm.postal_code || ""}
                  onChange={(e) =>
                    setShippingForm((p) => ({ ...p, postal_code: e.target.value }))
                  }
                  disabled={isUpdatingShipping}
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-text-light mb-1">주소</label>
                <Input
                  value={shippingForm.address1 || ""}
                  onChange={(e) =>
                    setShippingForm((p) => ({ ...p, address1: e.target.value }))
                  }
                  disabled={isUpdatingShipping}
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-text-light mb-1">상세주소</label>
                <Input
                  value={shippingForm.address2 || ""}
                  onChange={(e) =>
                    setShippingForm((p) => ({ ...p, address2: e.target.value }))
                  }
                  disabled={isUpdatingShipping}
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-text-light mb-1">배송 메모</label>
                <Input
                  value={shippingForm.shipping_memo || ""}
                  onChange={(e) =>
                    setShippingForm((p) => ({ ...p, shipping_memo: e.target.value }))
                  }
                  disabled={isUpdatingShipping}
                />
              </div>
              <div className="flex gap-2 pt-2">
                <Button
                  variant="ghost"
                  size="sm"
                  className="flex-1"
                  onClick={() => setShippingEditMode(false)}
                  disabled={isUpdatingShipping}
                >
                  취소
                </Button>
                <Button
                  size="sm"
                  className="flex-1"
                  onClick={handleShippingUpdate}
                  disabled={isUpdatingShipping}
                >
                  {isUpdatingShipping ? "변경 중..." : "배송지 변경"}
                </Button>
              </div>
            </div>
          )}
        </div>

        {/* 운송장 정보 */}
        {orderDetail.tracking_number && (
          <div className="bg-white border border-secondary/60 rounded-2xl p-6">
            <h4 className="font-bold text-text flex items-center gap-2 mb-4">
              <TruckIcon className="w-4 h-4 text-primary" />
              배송 추적
            </h4>
            <div className="space-y-2 text-sm">
              <div className="flex">
                <span className="text-text-light w-20 shrink-0">택배사</span>
                <span className="text-text">{orderDetail.tracking_carrier || "-"}</span>
              </div>
              <div className="flex">
                <span className="text-text-light w-20 shrink-0">운송장</span>
                <span className="text-text font-mono">{orderDetail.tracking_number}</span>
              </div>
            </div>
          </div>
        )}

        {/* 액션 버튼 */}
        {canCancel(orderDetail.status_code) && (
          <div className="pt-2">
            <Button
              variant="destructive"
              className="w-full"
              onClick={() => setCancelTarget(orderDetail.id)}
            >
              주문 취소
            </Button>
          </div>
        )}

        {/* 취소 확인 다이얼로그 */}
        {cancelTarget !== null && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
            <div className="bg-white rounded-3xl shadow-hover p-8 max-w-sm w-full mx-4">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-full bg-error/20 flex items-center justify-center">
                  <AlertTriangleIcon className="w-5 h-5 text-error-dark" />
                </div>
                <h4 className="text-lg font-bold text-text">주문 취소</h4>
              </div>
              <p className="text-sm text-text-light mb-6">
                정말 이 주문을 취소하시겠습니까?
              </p>
              <div className="flex gap-3">
                <Button
                  variant="ghost"
                  className="flex-1"
                  onClick={() => setCancelTarget(null)}
                  disabled={isCancelling}
                >
                  돌아가기
                </Button>
                <Button
                  variant="destructive"
                  className="flex-1"
                  onClick={handleCancel}
                  disabled={isCancelling}
                >
                  {isCancelling ? "취소 중..." : "주문 취소"}
                </Button>
              </div>
            </div>
          </div>
        )}
      </div>
    );
  }

  // 상세 로딩 중
  if (selectedOrderId && detailLoading) {
    return (
      <div className="flex flex-col items-center justify-center py-16">
        <div className="w-10 h-10 border-3 border-primary border-t-transparent rounded-full animate-spin" />
        <p className="mt-4 text-sm text-text-light">주문 상세 정보를 불러오는 중...</p>
      </div>
    );
  }

  // 주문 목록
  return (
    <div className="space-y-3">
      {orders.map((order) => {
        const statusInfo = getOrderStatusInfo(order.status);
        const StatusIcon = statusInfo.icon;

        return (
          <button
            key={order.id}
            onClick={() => handleSelectOrder(order.id)}
            className="w-full bg-white border border-secondary/60 rounded-2xl p-4 hover:shadow-hover transition-all duration-200 text-left flex items-center gap-4"
          >
            <div className="w-10 h-10 rounded-full bg-secondary/40 flex items-center justify-center shrink-0">
              <StatusIcon className="w-5 h-5 text-primary" />
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-1">
                <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${statusInfo.color}`}>
                  {statusInfo.label}
                </span>
                <span className="text-xs text-text-lighter">
                  {formatDate(order.ordered_at)}
                </span>
              </div>
              <p className="text-sm font-medium text-text truncate">
                {order.book_title || `동화책 #${order.book_id}`}
              </p>
              <p className="text-sm font-bold text-primary mt-0.5">
                {formatPrice(order.total_amount)}
              </p>
            </div>
            <ChevronRightIcon className="w-5 h-5 text-text-lighter shrink-0" />
          </button>
        );
      })}
    </div>
  );
}
