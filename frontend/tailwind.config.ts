import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: "#FFB5A7",
          light: "#FFDDD6",
          dark: "#E89585",
        },
        secondary: {
          DEFAULT: "#FCD5CE",
          light: "#FDE8E3",
          dark: "#E8B5AC",
        },
        accent: {
          DEFAULT: "#A8DADC",
          light: "#C5E8EA",
          dark: "#7BBFC2",
        },
        background: {
          DEFAULT: "#FFF8F0",
          card: "#FFFFFF",
        },
        text: {
          DEFAULT: "#2D3436",
          light: "#636E72",
          lighter: "#B2BEC3",
        },
        success: {
          DEFAULT: "#B5EAD7",
          dark: "#7DC8AC",
        },
        warning: {
          DEFAULT: "#FFE0AC",
          dark: "#E8C48A",
        },
        error: {
          DEFAULT: "#FFB5B5",
          dark: "#E89595",
        },
      },
      fontFamily: {
        sans: ["var(--font-noto-sans-kr)", '"Noto Sans KR"', "sans-serif"],
        display: ["var(--font-gowun-batang)", '"Gowun Batang"', "serif"],
      },
      borderRadius: {
        xl: "12px",
        "2xl": "16px",
        "3xl": "20px",
      },
      boxShadow: {
        soft: "0 2px 15px rgba(0, 0, 0, 0.05)",
        card: "0 4px 20px rgba(0, 0, 0, 0.08)",
        hover: "0 8px 30px rgba(0, 0, 0, 0.12)",
      },
    },
  },
  plugins: [],
};

export default config;
