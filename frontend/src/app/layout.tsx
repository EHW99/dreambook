import type { Metadata } from "next";
import { Noto_Sans_KR, Gowun_Batang } from "next/font/google";
import "./globals.css";
import { Providers } from "./providers";

const notoSansKR = Noto_Sans_KR({
  subsets: ["latin"],
  weight: ["400", "500", "700"],
  display: "swap",
  variable: "--font-noto-sans-kr",
});

const gowunBatang = Gowun_Batang({
  subsets: ["latin"],
  weight: ["400", "700"],
  display: "swap",
  variable: "--font-gowun-batang",
});

export const metadata: Metadata = {
  title: "꿈꾸는 나 — AI 직업 동화책",
  description: "아이의 꿈을 동화책으로 만들어주는 AI 서비스",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ko" className={`h-full antialiased ${notoSansKR.variable} ${gowunBatang.variable}`}>
      <body className="min-h-full flex flex-col bg-background text-text font-sans">
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
