"use client";

import { AuthGuard } from "@/components/auth-guard";
import { PageTransition } from "@/components/page-transition";
import { PhotosTab } from "@/components/mypage/photos-tab";

function PhotosContent() {
  return (
    <PageTransition>
      <div className="max-w-5xl mx-auto px-4 py-8 pb-20 md:pb-8">
        <h2 className="text-2xl font-bold text-text mb-6">아이 사진</h2>
        <div className="bg-white rounded-3xl shadow-card overflow-hidden p-6 sm:p-8">
          <PhotosTab />
        </div>
      </div>
    </PageTransition>
  );
}

export default function PhotosPage() {
  return (
    <AuthGuard>
      <PhotosContent />
    </AuthGuard>
  );
}
