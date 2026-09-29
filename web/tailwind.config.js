/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        canvas: '#0E1014',
        surface: {
          1: '#15181E',
          2: '#1C2028',
          3: '#12151B',
        },
        kairosBorder: {
          DEFAULT: '#1E2330',
          subtle: '#282D3A',
        },
        kairosText: {
          primary: '#ECE9E2',
          secondary: '#A3A9B5',
          tertiary: '#7D8594',
        },
        intent: {
          1: '#8FB3FF',
          2: '#62D6B4',
          3: '#B98CFF',
          4: '#F0B455',
        },
        kairosStatus: {
          verified: '#6FD39A',
          gap: '#F0B455',
          error: '#EF4444',
          updated: '#8FB3FF',
        },
        accent: {
          blue: '#5B8DEF',
          green: '#4ADE80',
        },
      },
      fontFamily: {
        sans: ['Geist', 'Inter', 'system-ui', '-apple-system', 'sans-serif'],
        serif: ['Newsreader', 'Georgia', 'serif'],
        mono: ['Geist Mono', 'JetBrains Mono', 'monospace'],
      },
    },
  },
  plugins: [],
}
