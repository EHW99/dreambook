/**
 * 404 Not Found 페이지 테스트
 */
import { render, screen } from "@testing-library/react";

// framer-motion mock
jest.mock("framer-motion", () => ({
  motion: {
    div: ({ children, ...props }: any) => <div {...props}>{children}</div>,
  },
}));

// next/link mock
jest.mock("next/link", () => {
  return ({ children, href, ...props }: any) => (
    <a href={href} {...props}>
      {children}
    </a>
  );
});

import NotFound from "../not-found";

describe("404 Not Found 페이지", () => {
  it("'길을 잃었나봐요' 메시지를 표시한다", () => {
    render(<NotFound />);
    expect(screen.getByText(/길을 잃었나봐요/)).toBeInTheDocument();
  });

  it("404 상태 코드 텍스트를 표시한다", () => {
    render(<NotFound />);
    expect(screen.getByText("404")).toBeInTheDocument();
  });

  it("홈으로 돌아가기 버튼이 있다", () => {
    render(<NotFound />);
    const link = screen.getByRole("link", { name: /홈으로 돌아가기/ });
    expect(link).toBeInTheDocument();
    expect(link).toHaveAttribute("href", "/");
  });

  it("따뜻한 일러스트 (아이콘)가 표시된다", () => {
    render(<NotFound />);
    // SVG 아이콘이 존재하는지 확인
    const svg = document.querySelector("svg");
    expect(svg).toBeInTheDocument();
  });
});
