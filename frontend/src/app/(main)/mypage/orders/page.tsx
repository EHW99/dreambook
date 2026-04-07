"use client";

import { AuthGuard } from "@/components/auth-guard";
import { PageTransition } from "@/components/page-transition";
import { OrdersTab } from "@/components/mypage/orders-tab";

function OrdersContent() {
  return (
    <PageTransition>
      <div className="max-w-5xl mx-auto px-4 py-8 pb-20 md:pb-8">
        <h2 className="text-2xl font-bold text-text mb-2">주문 내역</h2>
        <div className="border-b-2 border-text/15 mb-6" />
        <OrdersTab />
      </div>
    </PageTransition>
  );
}

export default function OrdersPage() {
  return (
    <AuthGuard>
      <OrdersContent />
    </AuthGuard>
  );
}
