/**
 * 500 에러 페이지 테스트
 */
import { render, screen, fireEvent } from "@testing-library/react";

// framer-motion mock
jest.mock("framer-motion", () => ({
  motion: {
    div: ({ children, ...props }: any) => <div {...props}>{children}</div>,
  },
}));

import ErrorPage from "../error";

describe("에러 페이지 (500)", () => {
  const mockError = new Error("테스트 에러");
  const mockReset = jest.fn();

  it("'잠시 후 다시 시도해주세요' 메시지를 표시한다", () => {
    render(<ErrorPage error={mockError} reset={mockReset} />);
    expect(screen.getByText(/잠시 후 다시 시도해주세요/)).toBeInTheDocument();
  });

  it("다시 시도 버튼이 있다", () => {
    render(<ErrorPage error={mockError} reset={mockReset} />);
    const button = screen.getByRole("button", { name: /다시 시도/ });
    expect(button).toBeInTheDocument();
  });

  it("다시 시도 버튼 클릭 시 reset이 호출된다", () => {
    render(<ErrorPage error={mockError} reset={mockReset} />);
    const button = screen.getByRole("button", { name: /다시 시도/ });
    fireEvent.click(button);
    expect(mockReset).toHaveBeenCalledTimes(1);
  });

  it("홈으로 돌아가기 링크가 있다", () => {
    render(<ErrorPage error={mockError} reset={mockReset} />);
    const link = screen.getByRole("link", { name: /홈으로 돌아가기/ });
    expect(link).toBeInTheDocument();
    expect(link).toHaveAttribute("href", "/");
  });
});
