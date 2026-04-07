"use client";

import Link from "next/link";
import { AuthGuard } from "@/components/auth-guard";
import { PageTransition } from "@/components/page-transition";
import { useAuth } from "@/lib/auth-context";
import { ProfileTab } from "@/components/mypage/profile-tab";
import { Ticket, ShoppingBag, Camera, ChevronRight } from "lucide-react";

const MYPAGE_LINKS = [
  { href: "/mypage/photos", label: "아이 사진", desc: "사진 관리", icon: Camera },
  { href: "/mypage/vouchers", label: "이용권 관리", desc: "구매, 조회, 환불", icon: Ticket },
  { href: "/mypage/orders", label: "주문 내역", desc: "실물 책 주문 현황", icon: ShoppingBag },
];

function MypageContent() {
  const { user } = useAuth();

  return (
    <PageTransition>
      <div className="max-w-5xl mx-auto px-4 py-8 pb-20 md:pb-8">
        <h2 className="text-2xl font-bold text-text mb-6">마이페이지</h2>

        {/* 회원정보 */}
        <div className="bg-white rounded-2xl sm:rounded-3xl shadow-card overflow-hidden p-4 sm:p-6 md:p-8">
          <h3 className="text-lg font-bold text-text mb-4">회원정보</h3>
          <ProfileTab />
        </div>
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
