"use client";

import Link from "next/link";
import { useAuth } from "@/lib/auth-context";
import { BookOpen, User, LogIn, UserPlus, Menu, X, LogOut } from "lucide-react";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";

export function Header() {
  const { user, loading, logout } = useAuth();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const router = useRouter();

  const handleLogout = async () => {
    await logout();
    setMobileMenuOpen(false);
    router.push("/");
  };

  return (
    <header className="sticky top-0 z-50 bg-background/80 backdrop-blur-md border-b border-secondary/50">
      <nav className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* 로고 */}
          <Link href="/" className="flex items-center gap-2 group">
            <BookOpen className="w-7 h-7 text-primary group-hover:text-primary-dark transition-colors" />
            <span className="text-xl font-bold font-display text-text group-hover:text-primary-dark transition-colors">
              꿈꾸는 나
            </span>
          </Link>

          {/* 데스크톱 네비게이션 */}
          <div className="hidden md:flex items-center gap-3">
            {!loading && (
              <>
                {user ? (
                  <>
                    <Link
                      href="/mypage"
                      className="inline-flex items-center gap-2 px-5 py-2.5 rounded-2xl bg-primary text-white font-medium shadow-soft hover:bg-primary-dark hover:shadow-hover transition-all duration-200"
                    >
                      <User className="w-4 h-4" />
                      마이페이지
                    </Link>
                    <button
                      onClick={handleLogout}
                      className="inline-flex items-center gap-2 px-4 py-2.5 rounded-2xl border-2 border-secondary text-text/70 font-medium hover:bg-secondary/50 transition-all duration-200"
                    >
                      <LogOut className="w-4 h-4" />
                      로그아웃
                    </button>
                  </>
                ) : (
                  <>
                    <Link
                      href="/login"
                      className="inline-flex items-center gap-2 px-5 py-2.5 rounded-2xl border-2 border-primary text-primary font-medium hover:bg-primary hover:text-white transition-all duration-200"
                    >
                      <LogIn className="w-4 h-4" />
                      로그인
                    </Link>
                    <Link
                      href="/signup"
                      className="inline-flex items-center gap-2 px-5 py-2.5 rounded-2xl bg-primary text-white font-medium shadow-soft hover:bg-primary-dark hover:shadow-hover transition-all duration-200"
                    >
                      <UserPlus className="w-4 h-4" />
                      회원가입
                    </Link>
                  </>
                )}
              </>
            )}
          </div>

          {/* 모바일 햄버거 */}
          <button
            className="md:hidden p-2 rounded-xl text-text hover:bg-secondary/50 transition-colors"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            aria-label="메뉴 열기"
          >
            {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>

        {/* 모바일 메뉴 */}
        <AnimatePresence>
          {mobileMenuOpen && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              exit={{ opacity: 0, height: 0 }}
              className="md:hidden overflow-hidden"
            >
              <div className="py-4 space-y-3 border-t border-secondary/50">
                {!loading && (
                  <>
                    {user ? (
                      <>
                        <Link
                          href="/mypage"
                          className="flex items-center gap-2 px-4 py-3 rounded-2xl bg-primary text-white font-medium"
                          onClick={() => setMobileMenuOpen(false)}
                        >
                          <User className="w-4 h-4" />
                          마이페이지
                        </Link>
                        <button
                          onClick={handleLogout}
                          className="flex items-center gap-2 px-4 py-3 rounded-2xl border-2 border-secondary text-text/70 font-medium w-full"
                        >
                          <LogOut className="w-4 h-4" />
                          로그아웃
                        </button>
                      </>
                    ) : (
                      <>
                        <Link
                          href="/login"
                          className="flex items-center gap-2 px-4 py-3 rounded-2xl border-2 border-primary text-primary font-medium"
                          onClick={() => setMobileMenuOpen(false)}
                        >
                          <LogIn className="w-4 h-4" />
                          로그인
                        </Link>
                        <Link
                          href="/signup"
                          className="flex items-center gap-2 px-4 py-3 rounded-2xl bg-primary text-white font-medium"
                          onClick={() => setMobileMenuOpen(false)}
                        >
                          <UserPlus className="w-4 h-4" />
                          회원가입
                        </Link>
                      </>
                    )}
                  </>
                )}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </nav>
    </header>
  );
}
