"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import { Home, Sparkles, BookOpen, Image, User } from "lucide-react";

const TABS = [
  { href: "/", label: "홈", icon: Home },
  { href: "/create", label: "만들기", icon: Sparkles, auth: true },
  { href: "/bookshelf", label: "내 책장", icon: BookOpen, auth: true },
  { href: "/gallery", label: "갤러리", icon: Image },
  { href: "/mypage", label: "MY", icon: User, auth: true },
];

export function BottomTabBar() {
  const pathname = usePathname();
  const router = useRouter();
  const { user } = useAuth();
  const [loginAlert, setLoginAlert] = useState(false);

  if (pathname === "/login" || pathname === "/signup") return null;

  return (
    <>
      <nav className="md:hidden fixed bottom-0 left-0 right-0 z-50 bg-white/95 backdrop-blur-md border-t border-secondary/50 safe-area-bottom">
        <div className="flex items-center justify-around h-14 px-1">
          {TABS.map((tab) => {
            const isActive = pathname === tab.href || (tab.href !== "/" && pathname.startsWith(tab.href));
            const Icon = tab.icon;

            const handleClick = (e: React.MouseEvent) => {
              if (tab.auth && !user) {
                e.preventDefault();
                setLoginAlert(true);
              }
            };

            return (
              <Link
                key={tab.href}
                href={tab.href}
                onClick={handleClick}
                className={`flex flex-col items-center justify-center gap-0.5 flex-1 py-1.5 rounded-lg transition-colors ${
                  isActive
                    ? "text-primary"
                    : "text-text/40 active:text-text/60"
                }`}
              >
                <Icon className={`w-5 h-5 ${isActive ? "stroke-[2.5]" : ""}`} />
                <span className="text-[10px] font-medium leading-tight">{tab.label}</span>
              </Link>
            );
          })}
        </div>
      </nav>

      {/* 로그인 필요 알림 모달 */}
      {loginAlert && (
        <div
          className="fixed inset-0 z-[100] flex items-center justify-center bg-black/40"
          onClick={() => setLoginAlert(false)}
        >
          <div
            className="bg-white rounded-2xl shadow-hover p-6 max-w-sm w-full mx-4 text-center"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="text-4xl mb-3">🔒</div>
            <h3 className="text-lg font-bold text-text mb-2">
              로그인이 필요해요
            </h3>
            <p className="text-sm text-text-light mb-6">
              이 기능을 이용하려면 로그인이 필요합니다.
            </p>
            <div className="flex gap-3">
              <button
                onClick={() => setLoginAlert(false)}
                className="flex-1 py-2.5 rounded-xl border border-gray-200 text-sm font-medium text-gray-600 hover:bg-gray-50 transition-colors"
              >
                닫기
              </button>
              <Link
                href="/login"
                onClick={() => setLoginAlert(false)}
                className="flex-1 py-2.5 rounded-xl bg-primary text-white text-sm font-medium hover:bg-primary-dark transition-colors text-center"
              >
                로그인하기
              </Link>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
