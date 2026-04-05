"use client";

import { AuthProvider } from "@/lib/auth-context";
import { VoucherGateProvider } from "@/lib/voucher-gate-context";

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <AuthProvider>
      <VoucherGateProvider>{children}</VoucherGateProvider>
    </AuthProvider>
  );
}
