import typography from "@tailwindcss/typography";

/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      fontFamily: {
        sans: [
          "Noto Sans TC",
          "PingFang TC",
          "Microsoft JhengHei",
          "system-ui",
          "sans-serif",
        ],
        serif: [
          "Noto Serif TC",
          "Source Han Serif TC",
          "PingFang TC",
          "serif",
        ],
      },
    },
  },
  plugins: [typography],
};
