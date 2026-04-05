"use client";

import { createContext, useContext, useState, useCallback, useRef } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import { VoucherModal } from "@/components/voucher-modal";
import { apiClient, VoucherItem } from "@/lib/api";

interface VoucherGateContextType {
  /** 이용권 확인 후 동화책 만들기 페이지로 이동 */
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
  const [showModal, setShowModal] = useState(false);

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
          router.push(`/create?voucher_id=${available[0].id}`);
          return;
        }
      }
      setShowModal(true);
    } finally {
      busyRef.current = false;
    }
  }, [user, router]);

  return (
    <VoucherGateContext.Provider value={{ startCreate }}>
      {children}
      <VoucherModal
        open={showModal}
        onClose={() => setShowModal(false)}
        onPurchased={(voucherId) => {
          setShowModal(false);
          router.push(`/create?voucher_id=${voucherId}`);
        }}
      />
    </VoucherGateContext.Provider>
  );
}
