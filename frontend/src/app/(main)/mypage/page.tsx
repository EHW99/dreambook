"use client";

import { AuthGuard } from "@/components/auth-guard";
import { PageTransition } from "@/components/page-transition";
import { useAuth } from "@/lib/auth-context";
import { ProfileTab } from "@/components/mypage/profile-tab";

function MypageContent() {
  const { user } = useAuth();

  return (
    <PageTransition>
      <div className="max-w-5xl mx-auto px-4 py-8 pb-20 md:pb-8">
        <h2 className="text-2xl font-bold text-text mb-2">회원정보</h2>
        <p className="text-sm text-text-light mb-6">{user?.email}</p>

        <div className="bg-white rounded-3xl shadow-card overflow-hidden p-6 sm:p-8">
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
