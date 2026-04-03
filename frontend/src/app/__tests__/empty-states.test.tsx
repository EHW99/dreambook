/**
 * 빈 상태 UI 테스트 — 마이페이지 탭들의 빈 상태 메시지 확인
 */
import { render, screen } from "@testing-library/react";

// next/navigation mock
jest.mock("next/navigation", () => ({
  useRouter: () => ({
    push: jest.fn(),
    replace: jest.fn(),
    back: jest.fn(),
  }),
}));

// apiClient mock
jest.mock("@/lib/api", () => ({
  apiClient: {
    getBooks: jest.fn().mockResolvedValue({ data: [] }),
    getPhotos: jest.fn().mockResolvedValue({ data: [] }),
    getOrders: jest.fn().mockResolvedValue({ data: [] }),
  },
}));

import { BookshelfTab } from "@/components/mypage/bookshelf-tab";
import { PhotosTab } from "@/components/mypage/photos-tab";
import { OrdersTab } from "@/components/mypage/orders-tab";

describe("빈 상태 UI", () => {
  describe("내 책장 빈 상태", () => {
    it("'아직 만든 동화책이 없어요' 메시지를 표시한다", async () => {
      render(<BookshelfTab />);
      expect(await screen.findByText("아직 만든 동화책이 없어요")).toBeInTheDocument();
    });

    it("새 동화책 만들기 버튼이 있다", async () => {
      render(<BookshelfTab />);
      expect(await screen.findByText(/새 동화책 만들기/)).toBeInTheDocument();
    });
  });

  describe("사진 목록 빈 상태", () => {
    it("'등록된 사진이 없어요' 메시지를 표시한다", async () => {
      render(<PhotosTab />);
      expect(await screen.findByText("등록된 사진이 없어요")).toBeInTheDocument();
    });
  });

  describe("주문 내역 빈 상태", () => {
    it("'아직 주문 내역이 없어요' 메시지를 표시한다", async () => {
      render(<OrdersTab />);
      expect(await screen.findByText("아직 주문 내역이 없어요")).toBeInTheDocument();
    });
  });
});
