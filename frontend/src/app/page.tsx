"use client";

import Link from "next/link";
import { useAuth } from "@/lib/auth-context";
import { motion, useInView } from "framer-motion";
import { useRef } from "react";
import {
  Sparkles,
  BookOpen,
  Palette,
  Printer,
  Star,
  Check,
  ArrowRight,
} from "lucide-react";
import { Header } from "@/components/layout/header";
import { Footer } from "@/components/layout/footer";

/* ───────── 애니메이션 헬퍼 ───────── */
function FadeInSection({ children, className = "", delay = 0 }: {
  children: React.ReactNode;
  className?: string;
  delay?: number;
}) {
  const ref = useRef<HTMLDivElement>(null);
  const isInView = useInView(ref, { once: true, margin: "-80px" });

  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 40 }}
      animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 40 }}
      transition={{ duration: 0.6, ease: "easeOut", delay }}
      className={className}
    >
      {children}
    </motion.div>
  );
}

/* ───────── 데이터 ───────── */

const SAMPLE_BOOKS = [
  {
    id: "sample-1",
    title: "소방관이 된 지민이",
    description: "용감한 지민이가 소방관이 되어 마을을 지키는 이야기",
    coverColor: "from-red-200 to-orange-200",
    emoji: "🚒",
  },
  {
    id: "sample-2",
    title: "우주비행사 하은이",
    description: "호기심 가득한 하은이가 우주를 탐험하는 이야기",
    coverColor: "from-indigo-200 to-purple-200",
    emoji: "🚀",
  },
  {
    id: "sample-3",
    title: "요리사 서준이",
    description: "맛있는 요리를 만드는 서준이의 특별한 하루",
    coverColor: "from-yellow-200 to-amber-200",
    emoji: "👨‍🍳",
  },
];

const ART_STYLES = [
  {
    name: "수채화",
    description: "부드럽고 따뜻한 수채화 느낌",
    bgColor: "bg-blue-50",
    borderColor: "border-blue-200",
    placeholderColor: "from-blue-100 to-sky-100",
  },
  {
    name: "연필화",
    description: "섬세한 연필 터치의 감성",
    bgColor: "bg-gray-50",
    borderColor: "border-gray-200",
    placeholderColor: "from-gray-100 to-slate-100",
  },
  {
    name: "크레파스",
    description: "어린이 감성 가득한 크레파스 풍",
    bgColor: "bg-yellow-50",
    borderColor: "border-yellow-200",
    placeholderColor: "from-yellow-100 to-orange-100",
  },
  {
    name: "3D",
    description: "입체적이고 생동감 넘치는 3D",
    bgColor: "bg-purple-50",
    borderColor: "border-purple-200",
    placeholderColor: "from-purple-100 to-pink-100",
  },
  {
    name: "만화",
    description: "재미있고 역동적인 만화 스타일",
    bgColor: "bg-green-50",
    borderColor: "border-green-200",
    placeholderColor: "from-green-100 to-emerald-100",
  },
];

const PRICING = [
  {
    name: "AI 스토리북",
    price: "9,900",
    description: "AI가 만드는 나만의 동화책",
    features: [
      "AI 스토리 생성",
      "5가지 그림체 선택",
      "캐릭터 커스터마이징",
      "온라인 뷰어로 읽기",
      "오디오북 기능",
    ],
    popular: false,
    bgColor: "bg-white",
    borderColor: "border-secondary",
  },
  {
    name: "AI 스토리북 + 실물 책",
    price: "29,900",
    description: "세상에 단 하나뿐인 실물 동화책",
    features: [
      "AI 스토리북 모든 기능",
      "하드커버 실물 책 제작",
      "고품질 인쇄 (243x248mm)",
      "무료 배송",
      "소중한 선물로 딱!",
    ],
    popular: true,
    bgColor: "bg-gradient-to-br from-primary/5 to-accent/5",
    borderColor: "border-primary",
  },
];

/* ───────── 메인 페이지 ───────── */

export default function LandingPage() {
  const { user, loading } = useAuth();
  const ctaHref = user ? "/create" : "/login";

  return (
    <>
      <Header />

      <main className="flex-1">
        {/* ── 히어로 섹션 ── */}
        <section className="relative overflow-hidden py-20 sm:py-28 lg:py-36">
          {/* 배경 장식 */}
          <div className="absolute inset-0 pointer-events-none">
            <div className="absolute top-10 left-10 w-72 h-72 bg-primary/10 rounded-full blur-3xl" />
            <div className="absolute bottom-10 right-10 w-96 h-96 bg-accent/10 rounded-full blur-3xl" />
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-secondary/10 rounded-full blur-3xl" />
          </div>

          <div className="relative max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, ease: "easeOut" }}
            >
              <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 text-primary-dark text-sm font-medium mb-6">
                <Sparkles className="w-4 h-4" />
                AI가 만드는 세상에 단 하나뿐인 동화책
              </div>

              <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold font-display text-text leading-tight mb-6">
                아이의 꿈을
                <br />
                <span className="text-primary">동화책</span>으로
                <br />
                만들어주세요
              </h1>

              <p className="text-lg sm:text-xl text-text-light max-w-2xl mx-auto mb-10 leading-relaxed">
                아이의 이름과 꿈꾸는 직업을 알려주세요.
                <br className="hidden sm:block" />
                AI가 아이만의 특별한 동화 이야기와 그림을 만들어 드려요.
              </p>

              <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
                <Link
                  href={ctaHref}
                  className="inline-flex items-center gap-2 px-8 py-4 rounded-2xl bg-primary text-white text-lg font-bold shadow-soft hover:bg-primary-dark hover:shadow-hover transition-all duration-200 hover:scale-105"
                >
                  <BookOpen className="w-5 h-5" />
                  동화책 만들기
                  <ArrowRight className="w-5 h-5" />
                </Link>
              </div>
            </motion.div>

            {/* 하단 스크롤 안내 */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 1.2, duration: 0.6 }}
              className="mt-16 flex justify-center"
            >
              <motion.div
                animate={{ y: [0, 10, 0] }}
                transition={{ repeat: Infinity, duration: 2, ease: "easeInOut" }}
                className="text-text-lighter text-sm flex flex-col items-center gap-2"
              >
                <span>아래로 스크롤</span>
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M12 5v14M19 12l-7 7-7-7" />
                </svg>
              </motion.div>
            </motion.div>
          </div>
        </section>

        {/* ── 샘플 동화책 섹션 ── */}
        <section className="py-20 bg-white/50">
          <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
            <FadeInSection className="text-center mb-12">
              <h2 className="text-3xl sm:text-4xl font-bold font-display text-text mb-4">
                샘플 동화책 미리보기
              </h2>
              <p className="text-text-light text-lg max-w-2xl mx-auto">
                이런 동화책이 만들어져요! 아이의 이름과 직업으로 특별한 이야기가 탄생합니다.
              </p>
            </FadeInSection>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 lg:gap-8">
              {SAMPLE_BOOKS.map((book, index) => (
                <FadeInSection key={book.id} delay={index * 0.15}>
                  <div
                    data-testid="sample-book-card"
                    className="group bg-white rounded-3xl shadow-card overflow-hidden hover:shadow-hover transition-all duration-300 hover:-translate-y-1 cursor-pointer"
                  >
                    {/* 더미 표지 */}
                    <div className={`h-40 sm:h-44 bg-gradient-to-br ${book.coverColor} flex flex-col items-center justify-center gap-2`}>
                      <span className="text-6xl group-hover:scale-110 transition-transform duration-300">
                        {book.emoji}
                      </span>
                      <span className="text-sm font-bold text-text/60 mt-2">
                        {book.title}
                      </span>
                      <span className="text-xs text-text/40 px-4 text-center">
                        AI가 만든 샘플 미리보기
                      </span>
                    </div>
                    <div className="p-5">
                      <h3 className="text-lg font-bold text-text mb-2 group-hover:text-primary transition-colors">
                        {book.title}
                      </h3>
                      <p className="text-sm text-text-light leading-relaxed">
                        {book.description}
                      </p>
                    </div>
                  </div>
                </FadeInSection>
              ))}
            </div>
          </div>
        </section>

        {/* ── 그림체 샘플 섹션 ── */}
        <section className="py-20">
          <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
            <FadeInSection className="text-center mb-12">
              <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-accent/10 text-accent-dark text-sm font-medium mb-4">
                <Palette className="w-4 h-4" />
                다양한 스타일
              </div>
              <h2 className="text-3xl sm:text-4xl font-bold font-display text-text mb-4">
                5가지 그림체로 만나는 동화
              </h2>
              <p className="text-text-light text-lg max-w-2xl mx-auto">
                아이가 좋아하는 그림체를 선택하세요. 같은 이야기도 그림체에 따라 전혀 다른 느낌이에요.
              </p>
            </FadeInSection>

            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4 lg:gap-6">
              {ART_STYLES.map((style, index) => (
                <FadeInSection key={style.name} delay={index * 0.1}>
                  <div
                    className={`group ${style.bgColor} border-2 ${style.borderColor} rounded-2xl p-4 text-center hover:shadow-card transition-all duration-300 hover:-translate-y-1`}
                  >
                    {/* placeholder 이미지 영역 */}
                    <div className={`w-full aspect-[4/3] rounded-xl bg-gradient-to-br ${style.placeholderColor} mb-3 flex flex-col items-center justify-center gap-1`}>
                      <Palette className="w-8 h-8 text-text-lighter group-hover:text-text-light transition-colors" />
                      <span className="text-xs text-text-lighter/70 font-medium">{style.name} 스타일</span>
                    </div>
                    <h3 className="font-bold text-text text-sm sm:text-base mb-1">{style.name}</h3>
                    <p className="text-xs text-text-light hidden sm:block">{style.description}</p>
                  </div>
                </FadeInSection>
              ))}
            </div>
          </div>
        </section>

        {/* ── 만드는 과정 섹션 ── */}
        <section className="py-20 bg-white/50">
          <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
            <FadeInSection className="text-center mb-12">
              <h2 className="text-3xl sm:text-4xl font-bold font-display text-text mb-4">
                이렇게 만들어져요
              </h2>
              <p className="text-text-light text-lg">
                간단한 4단계로 세상에 단 하나뿐인 동화책 완성!
              </p>
            </FadeInSection>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
              {[
                { icon: <Sparkles className="w-6 h-6" />, step: "1", title: "정보 입력", desc: "아이 이름과 사진, 꿈꾸는 직업을 알려주세요" },
                { icon: <Palette className="w-6 h-6" />, step: "2", title: "스타일 선택", desc: "원하는 그림체와 동화 스타일을 선택해요" },
                { icon: <BookOpen className="w-6 h-6" />, step: "3", title: "AI 동화 생성", desc: "AI가 아이만의 특별한 동화를 만들어요" },
                { icon: <Printer className="w-6 h-6" />, step: "4", title: "실물 책 배송", desc: "하드커버 동화책으로 인쇄하여 배송해요" },
              ].map((item, index) => (
                <FadeInSection key={item.step} delay={index * 0.15}>
                  <div className="bg-white rounded-3xl shadow-soft p-6 text-center hover:shadow-card transition-all duration-300">
                    <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-primary/10 text-primary mb-4">
                      {item.icon}
                    </div>
                    <div className="text-xs font-bold text-primary mb-2">STEP {item.step}</div>
                    <h3 className="text-lg font-bold text-text mb-2">{item.title}</h3>
                    <p className="text-sm text-text-light leading-relaxed">{item.desc}</p>
                  </div>
                </FadeInSection>
              ))}
            </div>
          </div>
        </section>

        {/* ── 가격/이용권 섹션 ── */}
        <section className="py-20">
          <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
            <FadeInSection className="text-center mb-12">
              <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 text-primary-dark text-sm font-medium mb-4">
                <Star className="w-4 h-4" />
                합리적인 가격
              </div>
              <h2 className="text-3xl sm:text-4xl font-bold font-display text-text mb-4">
                이용권 안내
              </h2>
              <p className="text-text-light text-lg max-w-2xl mx-auto">
                아이의 꿈을 담은 동화책, 부담 없는 가격으로 만나보세요.
              </p>
            </FadeInSection>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 lg:gap-8">
              {PRICING.map((plan, index) => (
                <FadeInSection key={plan.name} delay={index * 0.15}>
                  <div
                    className={`relative ${plan.bgColor} border-2 ${plan.borderColor} rounded-3xl p-6 sm:p-8 hover:shadow-hover transition-all duration-300 ${
                      plan.popular ? "ring-2 ring-primary/30" : ""
                    }`}
                  >
                    {plan.popular && (
                      <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-4 py-1 rounded-full bg-primary text-white text-xs font-bold">
                        추천
                      </div>
                    )}
                    <h3 className="text-lg font-bold text-text mb-2">{plan.name}</h3>
                    <p className="text-sm text-text-light mb-4">{plan.description}</p>
                    <div className="mb-6">
                      <span className="text-4xl font-bold text-text">{plan.price}</span>
                      <span className="text-text-light ml-1">원</span>
                    </div>
                    <ul className="space-y-3 mb-8">
                      {plan.features.map((feature) => (
                        <li key={feature} className="flex items-center gap-2 text-sm text-text">
                          <Check className="w-4 h-4 text-success-dark flex-shrink-0" />
                          {feature}
                        </li>
                      ))}
                    </ul>
                    <Link
                      href={ctaHref}
                      className={`block w-full text-center py-3 rounded-2xl font-medium transition-all duration-200 ${
                        plan.popular
                          ? "bg-primary text-white hover:bg-primary-dark shadow-soft hover:shadow-hover"
                          : "border-2 border-primary text-primary hover:bg-primary hover:text-white"
                      }`}
                    >
                      시작하기
                    </Link>
                  </div>
                </FadeInSection>
              ))}
            </div>
          </div>
        </section>

        {/* ── 최종 CTA 섹션 ── */}
        <section className="py-20 bg-gradient-to-br from-primary/5 via-secondary/5 to-accent/5">
          <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
            <FadeInSection>
              <h2 className="text-3xl sm:text-4xl font-bold font-display text-text mb-4">
                지금 바로 시작하세요
              </h2>
              <p className="text-text-light text-lg mb-8">
                아이의 꿈이 동화책이 되는 마법같은 경험을 선물해 주세요.
              </p>
              <Link
                href={ctaHref}
                className="inline-flex items-center gap-2 px-8 py-4 rounded-2xl bg-primary text-white text-lg font-bold shadow-soft hover:bg-primary-dark hover:shadow-hover transition-all duration-200 hover:scale-105"
              >
                <BookOpen className="w-5 h-5" />
                동화책 만들기
                <ArrowRight className="w-5 h-5" />
              </Link>
            </FadeInSection>
          </div>
        </section>
      </main>

      <Footer />
    </>
  );
}
