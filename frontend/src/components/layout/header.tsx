"use client";

import { useState } from "react";
import Link from "next/link";
import Image from "next/image";
import { useAuth } from "@/lib/auth-context";
import { useVoucherGate } from "@/lib/voucher-gate-context";
import { useRouter, usePathname } from "next/navigation";

const NAV_LINKS = [
  { href: "/create", label: "동화 만들기", auth: true },
  { href: "/bookshelf", label: "내 책장", auth: true },
  { href: "/gallery", label: "공개 갤러리" },
  { href: "/mypage/photos", label: "아이 사진", auth: true },
  { href: "/mypage/orders", label: "주문 내역", auth: true },
];

export function Header() {
  const { user, loading, logout } = useAuth();
  const { startCreate } = useVoucherGate();
  const router = useRouter();
  const pathname = usePathname();
  const [loginAlert, setLoginAlert] = useState(false);

  const handleLogout = async () => {
    await logout();
    router.push("/");
  };

  const handleNavClick = (e: React.MouseEvent, link: typeof NAV_LINKS[0]) => {
    if (link.auth && !user) {
      e.preventDefault();
      setLoginAlert(true);
    }
  };

  return (
    <>
      <header className="sticky top-0 z-50">
        {/* 1단: 유틸리티 바 */}
        <div className="hidden md:block bg-[#f5f5f5] border-b border-gray-200/80">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-end h-9 gap-1">
              {!loading && (
                <>
                  {user ? (
                    <>
                      {user.name && (
                        <span className="px-2 py-1 text-xs text-text font-medium">
                          {user.name}님
                        </span>
                      )}
                      <Link
                        href="/mypage"
                        className="px-3 py-1 text-xs text-gray-500 hover:text-gray-800 transition-colors"
                      >
                        회원정보
                      </Link>
                      <span className="text-gray-300 text-xs">|</span>
                      <button
                        onClick={handleLogout}
                        className="px-3 py-1 text-xs text-gray-500 hover:text-gray-800 transition-colors"
                      >
                        로그아웃
                      </button>
                    </>
                  ) : (
                    <>
                      <Link
                        href="/login"
                        className="px-3 py-1 text-xs text-gray-500 hover:text-gray-800 transition-colors"
                      >
                        로그인
                      </Link>
                      <span className="text-gray-300 text-xs">|</span>
                      <Link
                        href="/signup"
                        className="px-3 py-1 text-xs text-gray-500 hover:text-gray-800 transition-colors"
                      >
                        회원가입
                      </Link>
                    </>
                  )}
                </>
              )}
            </div>
          </div>
        </div>

        {/* 2단: 메인 네비게이션 */}
        <div className="bg-white border-b border-gray-200/60">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between h-16">
              {/* 로고 */}
              <Link href="/" className="flex-shrink-0">
                <Image
                  src="/logo.png"
                  alt="Dreambook"
                  width={180}
                  height={32}
                  className="h-8 w-auto"
                  priority
                />
              </Link>

              {/* 데스크톱 메뉴 */}
              <nav className="hidden md:flex items-center gap-8 lg:gap-10">
                {NAV_LINKS.map((link) => {
                  const isActive =
                    pathname === link.href ||
                    (link.href !== "/" && pathname.startsWith(link.href));

                  // "동화 만들기"는 이용권 게이트를 거치는 버튼으로 렌더링
                  if (link.href === "/create") {
                    return (
                      <button
                        key={link.href}
                        onClick={() => {
                          if (!user) {
                            setLoginAlert(true);
                          } else {
                            startCreate();
                          }
                        }}
                        className={`text-sm font-medium transition-colors py-1 border-b-2 ${
                          isActive
                            ? "text-primary border-primary"
                            : "text-gray-600 border-transparent hover:text-gray-900"
                        }`}
                      >
                        {link.label}
                      </button>
                    );
                  }

                  return (
                    <Link
                      key={link.href}
                      href={link.href}
                      onClick={(e) => handleNavClick(e, link)}
                      className={`text-sm font-medium transition-colors py-1 border-b-2 ${
                        isActive
                          ? "text-primary border-primary"
                          : "text-gray-600 border-transparent hover:text-gray-900"
                      }`}
                    >
                      {link.label}
                    </Link>
                  );
                })}
              </nav>

              {/* 모바일: 로그인/회원가입 */}
              <div className="flex md:hidden items-center gap-1">
                {!loading && !user && (
                  <>
                    <Link
                      href="/login"
                      className="px-3 py-2 text-sm font-medium text-gray-600 hover:text-gray-900 transition-colors"
                    >
                      로그인
                    </Link>
                    <Link
                      href="/signup"
                      className="px-4 py-2 rounded-xl bg-primary text-white text-sm font-medium hover:bg-primary-dark transition-colors"
                    >
                      회원가입
                    </Link>
                  </>
                )}
                {!loading && user && (
                  <button
                    onClick={handleLogout}
                    className="px-3 py-2 text-sm font-medium text-gray-500 hover:text-gray-800 transition-colors"
                  >
                    로그아웃
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>
      </header>

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
