"use client";

import { useVoucherGate } from "@/lib/voucher-gate-context";
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
    image: "/images/art-styles/watercolor.png",
  },
  {
    name: "파스텔",
    description: "몽환적이고 부드러운 파스텔 톤",
    bgColor: "bg-purple-50",
    borderColor: "border-purple-200",
    image: "/images/art-styles/pastel.png",
  },
  {
    name: "크레파스",
    description: "어린이 감성 가득한 크레파스 풍",
    bgColor: "bg-yellow-50",
    borderColor: "border-yellow-200",
    image: "/images/art-styles/crayon.png",
  },
  {
    name: "3D",
    description: "입체적이고 생동감 넘치는 3D",
    bgColor: "bg-indigo-50",
    borderColor: "border-indigo-200",
    image: "/images/art-styles/3d.png",
  },
  {
    name: "만화",
    description: "재미있고 역동적인 만화 스타일",
    bgColor: "bg-green-50",
    borderColor: "border-green-200",
    image: "/images/art-styles/cartoon.png",
  },
];

const PRICING = {
  name: "동화책 이용권",
  price: "9,900",
  description: "아이의 꿈이 동화 속 주인공이 됩니다",
  features: [
    "AI 맞춤 동화 스토리 11편",
    "AI 일러스트 생성",
    "5가지 그림체 선택",
    "디지털 동화책 뷰어",
  ],
  note: "실물 책 인쇄 및 배송은 별도 요금이 발생합니다",
};

/* ───────── 메인 페이지 ───────── */

export default function LandingPage() {
  const { startCreate } = useVoucherGate();

  return (
    <>
        {/* ── 히어로 섹션 ── */}
        <section className="relative overflow-hidden py-14 sm:py-24 lg:py-32">
          <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex flex-col lg:flex-row items-center gap-8 lg:gap-4">

              {/* 왼쪽 이미지 */}
              <motion.div
                initial={{ opacity: 0, x: -40 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.8, delay: 0.2 }}
                className="hidden lg:block lg:flex-1 lg:max-w-[340px] xl:max-w-[420px]"
              >
                <img
                  src="/images/hero/hero-left.png"
                  alt="동화책에서 튀어나오는 아이들"
                  className="w-full h-auto"
                />
              </motion.div>

              {/* 중앙 텍스트 */}
              <motion.div
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8, ease: "easeOut" }}
                className="flex-1 text-center max-w-2xl mx-auto lg:mx-0"
              >
                <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 text-primary-dark text-sm font-medium mb-6">
                  <Sparkles className="w-4 h-4" />
                  우리 아이의 미래를 먼저 만나보세요
                </div>

                <h1 className="text-3xl sm:text-5xl lg:text-5xl xl:text-6xl font-bold font-display text-text leading-tight mb-6">
                  아이가 꿈꾸는 내일,
                  <br />
                  <span className="text-primary">동화책</span>에서
                  <br />
                  먼저 만나요
                </h1>

                <p className="text-base sm:text-lg lg:text-xl text-text-light max-w-xl mx-auto mb-10 leading-relaxed">
                  커서 뭐가 되고 싶어?
                  <br className="hidden sm:block" />
                  그 대답이 한 권의 동화책이 됩니다.
                </p>

                <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
                  <button
                    onClick={startCreate}
                    className="inline-flex items-center gap-2 px-6 sm:px-8 py-3 sm:py-4 rounded-2xl bg-primary text-white text-base sm:text-lg font-bold shadow-soft hover:bg-primary-dark hover:shadow-hover transition-all duration-200 hover:scale-105"
                  >
                    <BookOpen className="w-5 h-5" />
                    동화책 만들기
                    <ArrowRight className="w-5 h-5" />
                  </button>
                </div>

                {/* 모바일: 이미지 2장 가로 배치 */}
                <div className="flex gap-4 mt-10 lg:hidden justify-center">
                  <motion.img
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6, delay: 0.3 }}
                    src="/images/hero/hero-left.png"
                    alt="동화책에서 튀어나오는 아이들"
                    className="w-44 sm:w-60 h-auto"
                  />
                  <motion.img
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6, delay: 0.5 }}
                    src="/images/hero/hero-right.png"
                    alt="꿈의 세계들"
                    className="w-44 sm:w-60 h-auto"
                  />
                </div>

                {/* 하단 스크롤 안내 */}
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 1.2, duration: 0.6 }}
                  className="mt-12 flex justify-center"
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
              </motion.div>

              {/* 오른쪽 이미지 */}
              <motion.div
                initial={{ opacity: 0, x: 40 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.8, delay: 0.4 }}
                className="hidden lg:block lg:flex-1 lg:max-w-[340px] xl:max-w-[420px]"
              >
                <img
                  src="/images/hero/hero-right.png"
                  alt="꿈의 세계들"
                  className="w-full h-auto"
                />
              </motion.div>

            </div>
          </div>
        </section>

        {/* ── 샘플 동화책 섹션 ── */}
        <section className="py-14 sm:py-20 bg-white/50">
          <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
            <FadeInSection className="text-center mb-12">
              <h2 className="text-3xl sm:text-4xl font-bold font-display text-text mb-4">
                이미 많은 아이들이 꿈을 펼치고 있어요
              </h2>
              <p className="text-text-light text-lg max-w-2xl mx-auto">
                아이의 이름과 꿈꾸는 직업이 세상에 단 하나뿐인 동화가 됩니다.
              </p>
            </FadeInSection>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 lg:gap-8">
              {SAMPLE_BOOKS.map((book, index) => (
                <FadeInSection key={book.id} delay={index * 0.15}>
                  <div
                    data-testid="sample-book-card"
                    className="group cursor-pointer"
                  >
                    {/* 책 형태 3D 효과 */}
                    <div className="relative mx-auto" style={{ perspective: "800px" }}>
                      {/* 그림자 + 페이지 레이어 */}
                      <div className="absolute inset-0 translate-x-1 translate-y-1 bg-text/5 rounded-2xl" />
                      <div className="absolute inset-0 translate-x-0.5 translate-y-0.5 bg-white border border-gray-100 rounded-2xl" />
                      {/* 메인 카드 */}
                      <div className="relative bg-white rounded-2xl shadow-card overflow-hidden hover:shadow-hover transition-all duration-300 group-hover:-translate-y-1">
                        {/* 표지 영역 — 책 느낌 */}
                        <div className={`relative h-52 sm:h-56 bg-gradient-to-br ${book.coverColor} flex flex-col items-center justify-center overflow-hidden`}>
                          {/* 장식 요소 */}
                          <div className="absolute top-3 left-3 w-8 h-8 rounded-full bg-white/20" />
                          <div className="absolute bottom-4 right-4 w-12 h-12 rounded-full bg-white/15" />
                          <div className="absolute top-1/4 right-1/4 w-5 h-5 rounded-full bg-white/10" />
                          {/* 책등 라인 */}
                          <div className="absolute left-0 top-0 bottom-0 w-1.5 bg-black/10 rounded-l-2xl" />
                          {/* 이모지 + 텍스트 */}
                          <span className="text-7xl mb-3 group-hover:scale-110 transition-transform duration-300 drop-shadow-sm">
                            {book.emoji}
                          </span>
                          <span className="text-base font-bold text-text/70 px-4 text-center leading-tight">
                            {book.title}
                          </span>
                          {/* 하단 태그 */}
                          <span className="mt-2 inline-flex items-center gap-1 px-3 py-1 rounded-full bg-white/40 text-xs font-medium text-text/60">
                            <BookOpen className="w-3 h-3" />
                            AI 동화책
                          </span>
                        </div>
                        {/* 하단 설명 */}
                        <div className="p-5">
                          <h3 className="text-lg font-bold text-text mb-1.5 group-hover:text-primary transition-colors">
                            {book.title}
                          </h3>
                          <p className="text-sm text-text-light leading-relaxed mb-3">
                            {book.description}
                          </p>
                          <span className="inline-flex items-center gap-1 text-xs font-medium text-primary">
                            미리보기
                            <ArrowRight className="w-3 h-3 group-hover:translate-x-0.5 transition-transform" />
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                </FadeInSection>
              ))}
            </div>
          </div>
        </section>

        {/* ── 그림체 샘플 섹션 ── */}
        <section className="py-14 sm:py-20">
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

            <div className="grid grid-cols-2 xs:grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3 sm:gap-4 lg:gap-6">
              {ART_STYLES.map((style, index) => (
                <FadeInSection key={style.name} delay={index * 0.1}>
                  <div
                    className={`group ${style.bgColor} border-2 ${style.borderColor} rounded-2xl p-3 sm:p-4 text-center hover:shadow-card transition-all duration-300 hover:-translate-y-1`}
                  >
                    <div className="w-full aspect-square rounded-xl overflow-hidden mb-3">
                      <img
                        src={style.image}
                        alt={`${style.name} 스타일`}
                        className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                        loading="lazy"
                      />
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
        <section className="py-14 sm:py-20 bg-white/50">
          <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
            <FadeInSection className="text-center mb-12">
              <h2 className="text-3xl sm:text-4xl font-bold font-display text-text mb-4">
                꿈이 동화책이 되기까지
              </h2>
              <p className="text-text-light text-lg">
                아이의 이름과 사진 하나면 충분해요
              </p>
            </FadeInSection>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
              {[
                { icon: <Sparkles className="w-6 h-6" />, step: "1", title: "꿈 알려주기", desc: "아이의 이름, 사진, 되고 싶은 직업을 알려주세요" },
                { icon: <Palette className="w-6 h-6" />, step: "2", title: "그림체 고르기", desc: "수채화, 크레파스, 3D 등 아이가 좋아할 스타일을 골라요" },
                { icon: <BookOpen className="w-6 h-6" />, step: "3", title: "동화 탄생", desc: "AI가 아이의 꿈을 11편의 동화 이야기로 만들어요" },
                { icon: <Printer className="w-6 h-6" />, step: "4", title: "책으로 만나기", desc: "세상에 단 하나뿐인 동화책이 우리 집으로 찾아와요" },
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
        <section className="py-14 sm:py-20">
          <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
            <FadeInSection className="text-center mb-12">
              <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 text-primary-dark text-sm font-medium mb-4">
                <Star className="w-4 h-4" />
                합리적인 가격
              </div>
              <h2 className="text-3xl sm:text-4xl font-bold font-display text-text mb-4">
                꿈에 가격을 매길 순 없지만
              </h2>
              <p className="text-text-light text-lg max-w-2xl mx-auto">
                한 권의 동화책으로, 아이의 눈이 반짝이는 순간을 선물하세요.
              </p>
            </FadeInSection>

            <div className="max-w-md mx-auto">
              <FadeInSection>
                <div className="bg-white border-2 border-primary rounded-3xl p-6 sm:p-8 hover:shadow-hover transition-all duration-300">
                  <h3 className="text-lg font-bold text-text mb-2">{PRICING.name}</h3>
                  <p className="text-sm text-text-light mb-4">{PRICING.description}</p>
                  <div className="mb-6">
                    <span className="text-3xl sm:text-4xl font-bold text-text">{PRICING.price}</span>
                    <span className="text-text-light ml-1">원</span>
                  </div>
                  <ul className="space-y-3 mb-8">
                    {PRICING.features.map((feature) => (
                      <li key={feature} className="flex items-center gap-2 text-sm text-text">
                        <Check className="w-4 h-4 text-success-dark flex-shrink-0" />
                        {feature}
                      </li>
                    ))}
                  </ul>
                  <p className="text-xs text-text-lighter text-center mb-5">
                    {PRICING.note}
                  </p>
                  <button
                    onClick={startCreate}
                    className="block w-full text-center py-3 rounded-2xl font-medium transition-all duration-200 bg-primary text-white hover:bg-primary-dark shadow-soft hover:shadow-hover"
                  >
                    시작하기
                  </button>
                </div>
              </FadeInSection>
            </div>
          </div>
        </section>

        {/* ── 최종 CTA 섹션 ── */}
        <section className="py-14 sm:py-20 pb-24 md:pb-20 bg-gradient-to-br from-primary/5 via-secondary/5 to-accent/5">
          <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
            <FadeInSection>
              <h2 className="text-3xl sm:text-4xl font-bold font-display text-text mb-4">
                우리 아이의 꿈, 동화책으로 만나볼까요?
              </h2>
              <p className="text-text-light text-lg mb-8">
                오늘 아이가 꿈꾸는 미래의 모습을, 동화책에서 먼저 만나보세요.
              </p>
              <button
                onClick={startCreate}
                className="inline-flex items-center gap-2 px-8 py-4 rounded-2xl bg-primary text-white text-lg font-bold shadow-soft hover:bg-primary-dark hover:shadow-hover transition-all duration-200 hover:scale-105"
              >
                <BookOpen className="w-5 h-5" />
                우리 아이 동화책 만들기
                <ArrowRight className="w-5 h-5" />
              </button>
            </FadeInSection>
          </div>
        </section>
    </>
  );
}
