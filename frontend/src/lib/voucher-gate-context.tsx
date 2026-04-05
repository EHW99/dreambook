"use client";

import { createContext, useContext, useState, useCallback, useRef } from "react";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { useAuth } from "@/lib/auth-context";
import { VoucherModal } from "@/components/voucher-modal";
import { apiClient, VoucherItem } from "@/lib/api";
import { Ticket, X } from "lucide-react";
import { Button } from "@/components/ui/button";

interface VoucherGateContextType {
  startCreate: () => void;
}

const VoucherGateContext = createContext<VoucherGateContextType>({
  startCreate: () => {},
});

export function useVoucherGate() {
  return useContext(VoucherGateContext);
}

export function VoucherGateProvider({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const { user } = useAuth();
  const busyRef = useRef(false);
  const [showPurchaseModal, setShowPurchaseModal] = useState(false);

  // 이용권 사용 확인 모달
  const [showConfirm, setShowConfirm] = useState(false);
  const [confirmVoucherId, setConfirmVoucherId] = useState<number | null>(null);
  const [availableCount, setAvailableCount] = useState(0);

  const startCreate = useCallback(async () => {
    if (!user) {
      router.push("/login");
      return;
    }
    if (busyRef.current) return;
    busyRef.current = true;

    try {
      const result = await apiClient.getVouchers();
      if (result.data) {
        const available = result.data.filter(
          (v: VoucherItem) => v.status === "purchased"
        );
        if (available.length > 0) {
          setConfirmVoucherId(available[0].id);
          setAvailableCount(available.length);
          setShowConfirm(true);
          return;
        }
      }
      setShowPurchaseModal(true);
    } finally {
      busyRef.current = false;
    }
  }, [user, router]);

  function handleConfirm() {
    if (confirmVoucherId) {
      setShowConfirm(false);
      router.push(`/create?voucher_id=${confirmVoucherId}`);
    }
  }

  function handleCancel() {
    setShowConfirm(false);
    setConfirmVoucherId(null);
  }

  return (
    <VoucherGateContext.Provider value={{ startCreate }}>
      {children}

      {/* 이용권 사용 확인 모달 */}
      <AnimatePresence>
        {showConfirm && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="fixed inset-0 z-50 flex items-center justify-center px-4"
            onClick={handleCancel}
          >
            <div className="absolute inset-0 bg-black/40" />
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 10 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 10 }}
              transition={{ duration: 0.2 }}
              className="relative bg-white rounded-3xl shadow-xl p-6 sm:p-8 max-w-sm w-full"
              onClick={(e) => e.stopPropagation()}
            >
              <button
                onClick={handleCancel}
                className="absolute top-4 right-4 w-8 h-8 rounded-full hover:bg-gray-100 flex items-center justify-center transition-colors"
              >
                <X className="w-4 h-4 text-text-lighter" />
              </button>

              <div className="text-center mb-5">
                <div className="w-14 h-14 rounded-2xl bg-primary/10 flex items-center justify-center mx-auto mb-4">
                  <Ticket className="w-7 h-7 text-primary" />
                </div>
                <h2 className="text-lg font-bold text-text mb-1">이용권을 사용합니다</h2>
                <p className="text-sm text-text-light">
                  보유 이용권 <span className="font-bold text-text">{availableCount}장</span> 중
                  1장을 사용하여 동화책을 만듭니다.
                </p>
              </div>

              <div className="flex gap-3">
                <button
                  onClick={handleCancel}
                  className="flex-1 py-2.5 rounded-xl border border-gray-200 text-sm font-medium text-gray-600 hover:bg-gray-50 transition-colors"
                >
                  취소
                </button>
                <Button
                  onClick={handleConfirm}
                  className="flex-1 bg-primary hover:bg-primary-dark text-white"
                >
                  만들기 시작
                </Button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* 이용권 구매 모달 (이용권 없을 때) */}
      <VoucherModal
        open={showPurchaseModal}
        onClose={() => setShowPurchaseModal(false)}
        onPurchased={(voucherId) => {
          setShowPurchaseModal(false);
          router.push(`/create?voucher_id=${voucherId}`);
        }}
      />
    </VoucherGateContext.Provider>
  );
}
