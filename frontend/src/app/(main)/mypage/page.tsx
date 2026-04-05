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
        <h2 className="text-2xl font-bold text-text mb-2">마이페이지</h2>
        <p className="text-sm text-text-light mb-6">{user?.email}</p>

        {/* 바로가기 메뉴 */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mb-6">
          {MYPAGE_LINKS.map((link) => {
            const Icon = link.icon;
            return (
              <Link
                key={link.href}
                href={link.href}
                className="flex items-center gap-3 bg-white rounded-2xl shadow-soft p-4 hover:shadow-card transition-shadow"
              >
                <div className="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center flex-shrink-0">
                  <Icon className="w-5 h-5 text-primary" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="font-medium text-text text-sm">{link.label}</p>
                  <p className="text-xs text-text-lighter">{link.desc}</p>
                </div>
                <ChevronRight className="w-4 h-4 text-text-lighter flex-shrink-0" />
              </Link>
            );
          })}
        </div>

        {/* 회원정보 */}
        <div className="bg-white rounded-3xl shadow-card overflow-hidden p-6 sm:p-8">
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
