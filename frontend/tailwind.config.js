/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: {
          50: "#f4f7f7",
          100: "#e3ecec",
          200: "#c5d6d6",
          300: "#9bb8b8",
          400: "#6d9494",
          500: "#517878",
          600: "#3f6060",
          700: "#354e4e",
          800: "#2e4141",
          900: "#293737",
          950: "#142020",
        },
        accent: {
          DEFAULT: "#0f766e",
          soft: "#14b8a6",
          muted: "#ccfbf1",
        },
        sand: {
          DEFAULT: "#f3efe6",
          deep: "#e7dfd0",
        },
      },
      fontFamily: {
        display: ['"Syne"', "system-ui", "sans-serif"],
        sans: ['"Figtree"', "system-ui", "sans-serif"],
      },
      boxShadow: {
        panel: "0 18px 50px rgba(20, 32, 32, 0.08)",
      },
      backgroundImage: {
        mesh: "radial-gradient(ellipse at 20% 0%, rgba(20,184,166,0.18), transparent 45%), radial-gradient(ellipse at 90% 10%, rgba(15,118,110,0.12), transparent 40%), linear-gradient(180deg, #f7f4ee 0%, #eef2f1 55%, #e8eeed 100%)",
      },
    },
  },
  plugins: [],
};
