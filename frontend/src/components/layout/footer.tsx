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
              아이의 이름으로 만드는
              <br />
              세상에 하나뿐인 동화책
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
                <Link href="/bookshelf" className="text-sm text-text-light hover:text-primary transition-colors">
                  내 책장
                </Link>
              </li>
              <li>
                <Link href="/gallery" className="text-sm text-text-light hover:text-primary transition-colors">
                  공개 갤러리
                </Link>
              </li>
              <li>
                <Link href="/mypage/photos" className="text-sm text-text-light hover:text-primary transition-colors">
                  아이 사진
                </Link>
              </li>
              <li>
                <Link href="/mypage/orders" className="text-sm text-text-light hover:text-primary transition-colors">
                  주문 내역
                </Link>
              </li>
            </ul>
          </div>

          {/* 서비스 정보 */}
          <div>
            <h3 className="text-sm font-bold text-text mb-4">서비스</h3>
            <ul className="space-y-2 text-sm text-text-light">
              <li>서비스명: Dreambook</li>
              <li>AI 동화책 제작 서비스</li>
            </ul>
          </div>
        </div>

        {/* 하단 카피라이트 */}
        <div className="mt-8 pt-8 border-t border-secondary/50 flex flex-col sm:flex-row items-center justify-between gap-4">
          <p className="text-xs text-text-lighter">
            &copy; {new Date().getFullYear()} Dreambook. All rights reserved.
          </p>
          <p className="text-xs text-text-lighter flex items-center gap-1">
            Made with <Heart className="w-3 h-3 text-primary fill-primary" /> for children&apos;s dreams
          </p>
        </div>
      </div>
    </footer>
  );
}
