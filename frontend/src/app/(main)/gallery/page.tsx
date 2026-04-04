"use client";

import { PageTransition } from "@/components/page-transition";
import { BookOpen } from "lucide-react";

export default function GalleryPage() {
  return (
    <PageTransition>
      <div className="max-w-5xl mx-auto px-4 py-8 pb-20 md:pb-8">
        <h2 className="text-2xl font-bold text-text mb-6">공개 갤러리</h2>

        <div className="flex flex-col items-center justify-center py-20">
          <div className="w-20 h-20 rounded-full bg-secondary/50 flex items-center justify-center mb-6">
            <BookOpen className="w-10 h-10 text-primary" />
          </div>
          <p className="text-lg font-medium text-text mb-2">
            갤러리 준비 중이에요
          </p>
          <p className="text-sm text-text-light text-center max-w-sm">
            다른 친구들이 만든 멋진 동화책을 구경할 수 있는
            <br />
            공개 갤러리가 곧 열립니다!
          </p>
        </div>
      </div>
    </PageTransition>
  );
}
