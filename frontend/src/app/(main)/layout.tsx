"use client";

import { Header } from "@/components/layout/header";
import { Footer } from "@/components/layout/footer";
import { BottomTabBar } from "@/components/layout/bottom-tab-bar";

export default function MainLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <>
      <Header />
      <main className="flex-1">{children}</main>
      <Footer />
      <BottomTabBar />
    </>
  );
}
