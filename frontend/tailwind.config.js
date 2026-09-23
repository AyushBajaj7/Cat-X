/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        cat: {
          yellow: '#FFCD11',
          black: '#111111',
          dark: '#1C1C1C',
          gray: '#2D2D2D',
          light: '#E5E5E5',
          accent: '#E0A800',
        },
      },
    },
  },
  plugins: [],
}
