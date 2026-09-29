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
        brand: {
          50: '#eff6ff',
          100: '#dbeafe',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
          900: '#1e3a8a',
        },
        slate: {
          850: '#151e2e',
          900: '#0f172a',
          950: '#0b0f19',
        },
        decision: {
          retrieve: '#2563EB',
          wait: '#64748B',
          suppress: '#8B5CF6',
        },
        intent: {
          1: '#3B82F6', // Blue
          2: '#10B981', // Emerald
          3: '#8B5CF6', // Violet
          4: '#F97316', // Orange
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
    },
  },
  plugins: [],
}
