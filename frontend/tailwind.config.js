/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'space-dark': '#0a0a0f',
        'space-gray': '#1a1a2e',
        'tech-blue': '#00d4ff',
        'quantum-purple': '#8b5cf6',
        'neon-green': '#00ff88',
      },
      fontFamily: {
        'orbitron': ['Orbitron', 'sans-serif'],
        'mono': ['JetBrains Mono', 'monospace'],
      },
    },
  },
  plugins: [],
}
