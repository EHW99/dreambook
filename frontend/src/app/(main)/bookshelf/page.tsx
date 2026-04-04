"use client";

import { useState, useEffect, useCallback } from "react";
import { AuthGuard } from "@/components/auth-guard";
import { PageTransition } from "@/components/page-transition";
import { BookshelfTab } from "@/components/mypage/bookshelf-tab";
import { apiClient } from "@/lib/api";

function BookshelfContent() {
  const [orderedBookIds, setOrderedBookIds] = useState<Set<number>>(new Set());

  useEffect(() => {
    async function loadOrderedBookIds() {
      const result = await apiClient.getOrders();
      if (result.data) {
        setOrderedBookIds(new Set(result.data.map((o) => o.book_id)));
      }
    }
    loadOrderedBookIds();
  }, []);

  const handleOrdersLoaded = useCallback((bookIds: Set<number>) => {
    setOrderedBookIds(bookIds);
  }, []);

  return (
    <PageTransition>
      <div className="max-w-5xl mx-auto px-4 py-8 pb-20 md:pb-8">
        <h2 className="text-2xl font-bold text-text mb-6">내 책장</h2>
        <BookshelfTab orderedBookIds={orderedBookIds} />
      </div>
    </PageTransition>
  );
}

export default function BookshelfPage() {
  return (
    <AuthGuard>
      <BookshelfContent />
    </AuthGuard>
  );
}
