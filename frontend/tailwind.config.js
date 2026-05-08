/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: '#f5f5f7', // Apple 风格浅灰背景
        surface: 'rgba(255, 255, 255, 0.7)', // 毛玻璃基础色
      }
    },
  },
  plugins: [],
}