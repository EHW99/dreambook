"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/lib/auth-context";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { PageTransition } from "@/components/page-transition";

export default function SignupPage() {
  const router = useRouter();
  const { signup } = useAuth();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [passwordConfirm, setPasswordConfirm] = useState("");
  const [errors, setErrors] = useState<{
    email?: string;
    password?: string;
    passwordConfirm?: string;
    general?: string;
  }>({});
  const [isLoading, setIsLoading] = useState(false);
  const [success, setSuccess] = useState(false);

  const validateForm = (): boolean => {
    const newErrors: typeof errors = {};

    // 이메일 검증
    if (!email) {
      newErrors.email = "이메일을 입력해주세요";
    } else if (!/^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/.test(email)) {
      newErrors.email = "유효하지 않은 이메일 형식입니다";
    }

    // 비밀번호 검증
    if (!password) {
      newErrors.password = "비밀번호를 입력해주세요";
    } else if (password.length < 8) {
      newErrors.password = "비밀번호는 8자 이상이어야 합니다";
    }

    // 비밀번호 확인
    if (password !== passwordConfirm) {
      newErrors.passwordConfirm = "비밀번호가 일치하지 않습니다";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validateForm()) return;

    setIsLoading(true);
    setErrors({});

    const result = await signup(email, password);

    if (result.error) {
      setErrors({ general: result.error });
      setIsLoading(false);
      return;
    }

    setSuccess(true);
    setTimeout(() => {
      router.push("/login");
    }, 1500);
  };

  if (success) {
    return (
      <PageTransition>
      <div className="min-h-screen flex items-center justify-center bg-background px-4">
        <div className="w-full max-w-md bg-white rounded-3xl shadow-card p-8 text-center">
          <div className="text-4xl mb-4">&#127881;</div>
          <h2 className="text-xl font-bold text-text mb-2">
            회원가입 완료!
          </h2>
          <p className="text-text-light">
            로그인 페이지로 이동합니다...
          </p>
        </div>
      </div>
      </PageTransition>
    );
  }

  return (
    <PageTransition>
    <div className="min-h-screen flex items-center justify-center bg-background px-4">
      <div className="w-full max-w-md">
        {/* 로고/타이틀 */}
        <div className="text-center mb-8">
          <Link href="/">
            <h1 className="text-3xl font-bold text-primary font-display cursor-pointer">
              꿈꾸는 나
            </h1>
          </Link>
          <p className="mt-2 text-text-light">
            아이의 꿈을 동화책으로 만들어보세요
          </p>
        </div>

        {/* 폼 카드 */}
        <div className="bg-white rounded-3xl shadow-card p-8">
          <h2 className="text-xl font-bold text-text mb-6 text-center">
            회원가입
          </h2>

          {errors.general && (
            <div className="mb-4 p-3 bg-error/10 border border-error/30 rounded-2xl text-sm text-error-dark">
              {errors.general}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label
                htmlFor="email"
                className="block text-sm font-medium text-text mb-1.5"
              >
                이메일
              </label>
              <Input
                id="email"
                type="email"
                placeholder="example@email.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                error={errors.email}
                disabled={isLoading}
              />
            </div>

            <div>
              <label
                htmlFor="password"
                className="block text-sm font-medium text-text mb-1.5"
              >
                비밀번호
              </label>
              <Input
                id="password"
                type="password"
                placeholder="8자 이상 입력해주세요"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                error={errors.password}
                disabled={isLoading}
              />
            </div>

            <div>
              <label
                htmlFor="passwordConfirm"
                className="block text-sm font-medium text-text mb-1.5"
              >
                비밀번호 확인
              </label>
              <Input
                id="passwordConfirm"
                type="password"
                placeholder="비밀번호를 다시 입력해주세요"
                value={passwordConfirm}
                onChange={(e) => setPasswordConfirm(e.target.value)}
                error={errors.passwordConfirm}
                disabled={isLoading}
              />
            </div>

            <Button
              type="submit"
              className="w-full mt-2"
              size="lg"
              disabled={isLoading}
            >
              {isLoading ? "가입 중..." : "회원가입"}
            </Button>
          </form>

          <div className="mt-6 text-center text-sm text-text-light">
            이미 계정이 있으신가요?{" "}
            <Link
              href="/login"
              className="text-primary font-medium hover:underline"
            >
              로그인
            </Link>
          </div>
        </div>
      </div>
    </div>
    </PageTransition>
  );
}
