"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/lib/auth-context";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { PageTransition } from "@/components/page-transition";
import { ArrowLeft } from "lucide-react";

export default function LoginPage() {
  const router = useRouter();
  const { login, user, loading } = useAuth();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (!loading && user) {
      router.replace("/");
    }
  }, [user, loading, router]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    if (!email || !password) {
      setError("이메일과 비밀번호를 입력해주세요");
      return;
    }

    setIsLoading(true);

    const result = await login(email, password);

    if (result.error) {
      setError(result.error);
      setIsLoading(false);
      return;
    }

    router.push("/");
  };

  if (loading) {
    return <div className="h-screen bg-background" />;
  }

  return (
    <PageTransition>
      <div className="h-screen overflow-hidden bg-background px-4 flex flex-col">
        {/* 뒤로가기 */}
        <div className="max-w-md mx-auto w-full pt-6 flex-shrink-0">
          <button
            onClick={() => router.back()}
            className="inline-flex items-center gap-1.5 text-sm text-gray-500 hover:text-gray-800 transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            뒤로가기
          </button>
        </div>

        <div className="flex items-center justify-center flex-1">
          <div className="w-full max-w-md -mt-10">
            {/* 로고 */}
            <div className="text-center mb-8">
              <Link href="/" className="inline-block">
                <img src="/logo.png" alt="Dreambook" className="h-10 w-auto mx-auto" />
              </Link>
              <p className="mt-3 text-text-light">
                아이의 꿈을 동화책으로 만들어보세요
              </p>
            </div>

            {/* 폼 카드 */}
            <div className="bg-white rounded-3xl shadow-card p-8">
              <h2 className="text-xl font-bold text-text mb-6 text-center">
                로그인
              </h2>

              {error && (
                <div className="mb-4 p-3 bg-error/10 border border-error/30 rounded-2xl text-sm text-error-dark">
                  {error}
                </div>
              )}

              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label htmlFor="email" className="block text-sm font-medium text-text mb-1.5">
                    이메일
                  </label>
                  <Input
                    id="email"
                    type="email"
                    placeholder="example@email.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    disabled={isLoading}
                  />
                </div>

                <div>
                  <label htmlFor="password" className="block text-sm font-medium text-text mb-1.5">
                    비밀번호
                  </label>
                  <Input
                    id="password"
                    type="password"
                    placeholder="비밀번호를 입력해주세요"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    disabled={isLoading}
                  />
                </div>

                <Button
                  type="submit"
                  className="w-full mt-2"
                  size="lg"
                  disabled={isLoading}
                >
                  {isLoading ? "로그인 중..." : "로그인"}
                </Button>
              </form>

              <div className="mt-6 text-center text-sm text-text-light">
                계정이 없으신가요?{" "}
                <Link href="/signup" className="text-primary font-medium hover:underline">
                  회원가입
                </Link>
              </div>
            </div>
          </div>
        </div>
        <div className="flex-shrink-0 h-6" />
      </div>
    </PageTransition>
  );
}
