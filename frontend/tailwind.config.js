/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: {
          50: "#f4f2ff",
          100: "#e8e4f8",
          200: "#c9c2e4",
          300: "#9b92c0",
          400: "#6e6794",
          500: "#524d73",
          600: "#3d3858",
          700: "#2c2743",
          800: "#1c1830",
          900: "#12101f",
          950: "#070b14",
        },
        accent: {
          DEFAULT: "#4f46e5",
          soft: "#818cf8",
          muted: "#e0e7ff",
        },
        sand: {
          DEFAULT: "#f7f5ff",
          deep: "#ece8ff",
        },
      },
      fontFamily: {
        display: ['"Sora"', "system-ui", "sans-serif"],
        sans: ['"Outfit"', "system-ui", "sans-serif"],
      },
      boxShadow: {
        panel: "0 24px 80px rgba(7, 11, 20, 0.18)",
        glow: "0 0 0 1px rgba(129, 140, 248, 0.35), 0 20px 50px rgba(79, 70, 229, 0.18)",
      },
      backgroundImage: {
        mesh: "radial-gradient(ellipse at 10% -10%, rgba(99,102,241,0.35), transparent 42%), radial-gradient(ellipse at 90% 0%, rgba(244,63,94,0.18), transparent 40%), linear-gradient(165deg, #070b14 0%, #12101f 55%, #1c1830 100%)",
        stage:
          "radial-gradient(ellipse at 0% 0%, rgba(99,102,241,0.12), transparent 40%), radial-gradient(ellipse at 100% 0%, rgba(14,165,233,0.08), transparent 36%), linear-gradient(180deg, #fbfaff 0%, #f3f0ff 100%)",
      },
      borderRadius: {
        stage: "1.75rem",
      },
    },
  },
  plugins: [],
};
