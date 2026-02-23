/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['DM Sans', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      colors: {
        surface: {
          50: '#f8f9fa',
          100: '#eef0f3',
          200: '#dde1e7',
          800: '#2d3239',
          900: '#1a1d21',
        },
        accent: { green: '#22c55e', amber: '#f59e0b', slate: '#64748b' },
      },
    },
  },
  plugins: [],
}
