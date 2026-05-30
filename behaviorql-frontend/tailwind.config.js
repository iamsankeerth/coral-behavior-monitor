/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        darkBg: "#070908",
        surface: "#0E1110",
        surfaceAlt: "#151A18",
        customBorder: "#25302B",
        customText: "#F4F7F2",
        customMuted: "#9EA9A2",
        accent: "#FF6B5A",
        accentSoft: "rgba(255, 107, 90, 0.14)",
        customGreen: "#7BE495",
        customYellow: "#F6D365"
      },
      fontFamily: {
        outfit: ["Outfit", "sans-serif"],
        mono: ["JetBrains Mono", "Fira Code", "monospace"]
      }
    },
  },
  plugins: [],
}
