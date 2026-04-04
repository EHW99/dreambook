/**
 * 랜딩 페이지 테스트 — 태스크 5
 */

import React from "react";
import { render, screen } from "@testing-library/react";

// Mock framer-motion
jest.mock("framer-motion", () => ({
  motion: {
    div: React.forwardRef(({ children, ...props }: any, ref: any) => {
      const { initial, animate, transition, whileInView, viewport, ...rest } = props;
      return <div ref={ref} {...rest}>{children}</div>;
    }),
    section: React.forwardRef(({ children, ...props }: any, ref: any) => {
      const { initial, animate, transition, whileInView, viewport, ...rest } = props;
      return <section ref={ref} {...rest}>{children}</section>;
    }),
  },
  useInView: () => true,
  useAnimation: () => ({ start: jest.fn() }),
  AnimatePresence: ({ children }: any) => <>{children}</>,
}));

// Mock useAuth
const mockUseAuth = jest.fn();
jest.mock("@/lib/auth-context", () => ({
  useAuth: () => mockUseAuth(),
}));

// Mock next/link
jest.mock("next/link", () => {
  return ({ children, href, ...props }: any) => (
    <a href={href} {...props}>{children}</a>
  );
});

// Mock lucide-react
jest.mock("lucide-react", () => ({
  BookOpen: ({ className }: any) => <svg data-testid="icon-book-open" className={className} />,
  User: ({ className }: any) => <svg data-testid="icon-user" className={className} />,
  LogIn: ({ className }: any) => <svg data-testid="icon-log-in" className={className} />,
  UserPlus: ({ className }: any) => <svg data-testid="icon-user-plus" className={className} />,
  Menu: ({ className }: any) => <svg data-testid="icon-menu" className={className} />,
  X: ({ className }: any) => <svg data-testid="icon-x" className={className} />,
  Heart: ({ className }: any) => <svg data-testid="icon-heart" className={className} />,
  Sparkles: ({ className }: any) => <svg data-testid="icon-sparkles" className={className} />,
  Palette: ({ className }: any) => <svg data-testid="icon-palette" className={className} />,
  Printer: ({ className }: any) => <svg data-testid="icon-printer" className={className} />,
  Star: ({ className }: any) => <svg data-testid="icon-star" className={className} />,
  Check: ({ className }: any) => <svg data-testid="icon-check" className={className} />,
  ArrowRight: ({ className }: any) => <svg data-testid="icon-arrow-right" className={className} />,
}));

import LandingPage from "../(main)/page";
import { Header } from "@/components/layout/header";
import { Footer } from "@/components/layout/footer";

describe("랜딩 페이지", () => {
  beforeEach(() => {
    mockUseAuth.mockReturnValue({
      user: null,
      loading: false,
      login: jest.fn(),
      signup: jest.fn(),
      logout: jest.fn(),
      refreshUser: jest.fn(),
    });
  });

  // 1. 히어로 섹션
  describe("히어로 섹션", () => {
    it("서비스 핵심 메시지가 표시된다", () => {
      render(<LandingPage />);
      // 히어로 섹션의 h1에 "아이의 꿈을" + "동화책" 포함
      const headings = screen.getAllByText(/아이의 꿈을/);
      expect(headings.length).toBeGreaterThanOrEqual(1);
    });

    it("CTA 버튼 '동화책 만들기'가 존재한다", () => {
      render(<LandingPage />);
      const ctaLinks = screen.getAllByRole("link", { name: /동화책 만들기/ });
      expect(ctaLinks.length).toBeGreaterThanOrEqual(1);
    });

    it("비로그인 시 CTA 버튼이 로그인 페이지로 연결된다", () => {
      mockUseAuth.mockReturnValue({ user: null, loading: false });
      render(<LandingPage />);
      const ctaLinks = screen.getAllByRole("link", { name: /동화책 만들기/ });
      // 모든 CTA가 /login으로 연결되어야 함
      ctaLinks.forEach(link => {
        expect(link).toHaveAttribute("href", "/login");
      });
    });

    it("로그인 시 CTA 버튼이 동화책 만들기 페이지로 연결된다", () => {
      mockUseAuth.mockReturnValue({
        user: { id: 1, email: "test@test.com", created_at: "" },
        loading: false,
      });
      render(<LandingPage />);
      const ctaLinks = screen.getAllByRole("link", { name: /동화책 만들기/ });
      ctaLinks.forEach(link => {
        expect(link).toHaveAttribute("href", "/create");
      });
    });
  });

  // 2. 샘플 동화책 섹션
  describe("샘플 동화책 섹션", () => {
    it("샘플 동화책 섹션 제목이 표시된다", () => {
      render(<LandingPage />);
      expect(screen.getByText(/샘플 동화책/)).toBeInTheDocument();
    });

    it("샘플 카드가 최소 2개 이상 표시된다", () => {
      render(<LandingPage />);
      const sampleCards = screen.getAllByTestId("sample-book-card");
      expect(sampleCards.length).toBeGreaterThanOrEqual(2);
    });
  });

  // 3. 그림체 샘플 섹션
  describe("그림체 샘플 섹션", () => {
    it("5가지 그림체가 모두 표시된다", () => {
      render(<LandingPage />);
      expect(screen.getByText("수채화")).toBeInTheDocument();
      expect(screen.getByText("연필화")).toBeInTheDocument();
      expect(screen.getByText("크레파스")).toBeInTheDocument();
      expect(screen.getByText("3D")).toBeInTheDocument();
      expect(screen.getByText("만화")).toBeInTheDocument();
    });
  });

  // 4. 가격/이용권 섹션
  describe("가격/이용권 섹션", () => {
    it("이용권 2종 가격이 표시된다", () => {
      render(<LandingPage />);
      expect(screen.getByText("9,900")).toBeInTheDocument();
      expect(screen.getByText("29,900")).toBeInTheDocument();
    });

    it("AI 스토리북과 실물 책 이용권이 표시된다", () => {
      render(<LandingPage />);
      expect(screen.getByText("AI 스토리북")).toBeInTheDocument();
      const matches = screen.getAllByText(/실물 책/);
      expect(matches.length).toBeGreaterThanOrEqual(1);
    });
  });

  // 7. 헤더
  describe("헤더", () => {
    it("로고 '꿈꾸는 나'가 표시된다", () => {
      render(<Header />);
      expect(screen.getByText("꿈꾸는 나")).toBeInTheDocument();
    });

    it("비로그인 시 로그인/회원가입 링크가 표시된다", () => {
      mockUseAuth.mockReturnValue({ user: null, loading: false });
      render(<Header />);
      // 데스크톱 + 모바일 두 세트가 있을 수 있으므로 getAllByRole 사용
      const loginLinks = screen.getAllByRole("link", { name: /로그인/ });
      expect(loginLinks.length).toBeGreaterThanOrEqual(1);
      const signupLinks = screen.getAllByRole("link", { name: /회원가입/ });
      expect(signupLinks.length).toBeGreaterThanOrEqual(1);
    });

    it("로그인 시 마이페이지 링크가 표시된다", () => {
      mockUseAuth.mockReturnValue({
        user: { id: 1, email: "test@test.com", created_at: "" },
        loading: false,
      });
      render(<Header />);
      const mypageLinks = screen.getAllByRole("link", { name: /마이페이지/ });
      expect(mypageLinks.length).toBeGreaterThanOrEqual(1);
    });
  });

  // 8. 푸터
  describe("푸터", () => {
    it("서비스명이 표시된다", () => {
      render(<Footer />);
      expect(screen.getByText("꿈꾸는 나")).toBeInTheDocument();
    });

    it("회사 정보가 표시된다", () => {
      render(<Footer />);
      expect(screen.getByText("(주)스위트북")).toBeInTheDocument();
    });
  });

  // 5. 접근 권한 — 비로그인/로그인 모두 접근 가능
  describe("접근 권한", () => {
    it("비로그인 상태에서도 렌더링된다", () => {
      mockUseAuth.mockReturnValue({ user: null, loading: false });
      const { container } = render(<LandingPage />);
      expect(container.querySelector("main")).toBeInTheDocument();
    });

    it("로그인 상태에서도 렌더링된다", () => {
      mockUseAuth.mockReturnValue({
        user: { id: 1, email: "test@test.com", created_at: "" },
        loading: false,
      });
      const { container } = render(<LandingPage />);
      expect(container.querySelector("main")).toBeInTheDocument();
    });
  });
});
