"use client";

import { Heart } from "lucide-react";
import Image from "next/image";
import Link from "next/link";

export function Footer() {
  return (
    <footer className="bg-secondary/30 border-t border-secondary/50 mt-auto pb-16 md:pb-0">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {/* 서비스 정보 */}
          <div>
            <Link href="/" className="inline-block mb-4">
              <Image src="/logo.png" alt="Dreambook" width={140} height={26} className="h-6 w-auto" />
            </Link>
            <p className="text-sm text-text-light leading-relaxed">
              아이의 꿈을 세상에서 단 하나뿐인
              <br />
              동화책으로 만들어주는 AI 서비스
            </p>
          </div>

          {/* 바로가기 */}
          <div>
            <h3 className="text-sm font-bold text-text mb-4">바로가기</h3>
            <ul className="space-y-2">
              <li>
                <Link href="/create" className="text-sm text-text-light hover:text-primary transition-colors">
                  동화 만들기
                </Link>
              </li>
              <li>
                <Link href="/gallery" className="text-sm text-text-light hover:text-primary transition-colors">
                  공개 갤러리
                </Link>
              </li>
              <li>
                <Link href="/bookshelf" className="text-sm text-text-light hover:text-primary transition-colors">
                  내 책장
                </Link>
              </li>
            </ul>
          </div>

          {/* 회사 정보 */}
          <div>
            <h3 className="text-sm font-bold text-text mb-4">회사 정보</h3>
            <ul className="space-y-2 text-sm text-text-light">
              <li>(주)스위트북</li>
              <li>서비스명: Dreambook</li>
            </ul>
          </div>
        </div>

        {/* 하단 카피라이트 */}
        <div className="mt-8 pt-8 border-t border-secondary/50 flex flex-col sm:flex-row items-center justify-between gap-4">
          <p className="text-xs text-text-lighter">
            &copy; {new Date().getFullYear()} (주)스위트북. All rights reserved.
          </p>
          <p className="text-xs text-text-lighter flex items-center gap-1">
            Made with <Heart className="w-3 h-3 text-primary fill-primary" /> for children&apos;s dreams
          </p>
        </div>
      </div>
    </footer>
  );
}
