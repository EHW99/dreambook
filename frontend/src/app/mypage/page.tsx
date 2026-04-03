"use client";

import { useState, useCallback, useEffect } from "react";
import Link from "next/link";
import { AuthGuard } from "@/components/auth-guard";
import { PageTransition } from "@/components/page-transition";
import { useAuth } from "@/lib/auth-context";
import { ProfileTab } from "@/components/mypage/profile-tab";
import { PhotosTab } from "@/components/mypage/photos-tab";
import { BookshelfTab } from "@/components/mypage/bookshelf-tab";
import { OrdersTab } from "@/components/mypage/orders-tab";
import {
  UserIcon,
  CameraIcon,
  BookOpenIcon,
  ShoppingBagIcon,
} from "@/components/icons";
import { apiClient } from "@/lib/api";

const TABS = [
  { id: "profile", label: "회원 정보", icon: UserIcon },
  { id: "photos", label: "아이 사진", icon: CameraIcon },
  { id: "bookshelf", label: "내 책장", icon: BookOpenIcon },
  { id: "orders", label: "주문 내역", icon: ShoppingBagIcon },
] as const;

type TabId = (typeof TABS)[number]["id"];

function MypageContent() {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState<TabId>("profile");
  const [orderedBookIds, setOrderedBookIds] = useState<Set<number>>(new Set());

  const handleOrdersLoaded = useCallback((bookIds: Set<number>) => {
    setOrderedBookIds(bookIds);
  }, []);

  // 마운트 시 주문 목록을 미리 로드하여 orderedBookIds 초기화
  useEffect(() => {
    async function loadOrderedBookIds() {
      const result = await apiClient.getOrders();
      if (result.data) {
        setOrderedBookIds(new Set(result.data.map((o) => o.book_id)));
      }
    }
    loadOrderedBookIds();
  }, []);

  return (
    <PageTransition>
      <div className="min-h-screen bg-background">
        {/* 헤더 */}
        <header className="bg-white shadow-soft">
          <div className="max-w-5xl mx-auto px-4 py-4 flex items-center justify-between">
            <Link href="/">
              <h1 className="text-2xl font-bold text-primary font-display cursor-pointer">
                꿈꾸는 나
              </h1>
            </Link>
            <span className="text-sm text-text-light">{user?.email}</span>
          </div>
        </header>

        <main className="max-w-5xl mx-auto px-4 py-8">
          <h2 className="text-2xl font-bold text-text mb-6">마이페이지</h2>

          {/* 탭 네비게이션 */}
          <div className="bg-white rounded-3xl shadow-card overflow-hidden">
            {/* 탭 바 */}
            <div className="flex border-b border-secondary">
              {TABS.map((tab) => {
                const Icon = tab.icon;
                const isActive = activeTab === tab.id;
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`
                      flex-1 flex items-center justify-center gap-2 py-4 px-3 text-sm font-medium transition-colors
                      ${
                        isActive
                          ? "text-primary border-b-2 border-primary bg-primary/5"
                          : "text-text-light hover:text-text hover:bg-secondary/30"
                      }
                    `}
                  >
                    <Icon className="w-4 h-4" />
                    <span className="hidden sm:inline">{tab.label}</span>
                  </button>
                );
              })}
            </div>

            {/* 탭 콘텐츠 */}
            <div className="p-6 sm:p-8">
              {activeTab === "profile" && <ProfileTab />}
              {activeTab === "photos" && <PhotosTab />}
              {activeTab === "bookshelf" && (
                <BookshelfTab orderedBookIds={orderedBookIds} />
              )}
              {activeTab === "orders" && (
                <OrdersTab onOrdersLoaded={handleOrdersLoaded} />
              )}
            </div>
          </div>
        </main>
      </div>
    </PageTransition>
  );
}

export default function MypagePage() {
  return (
    <AuthGuard>
      <MypageContent />
    </AuthGuard>
  );
}
