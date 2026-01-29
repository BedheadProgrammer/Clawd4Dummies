/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Primary backgrounds
        'space-black': '#0D1117',
        'elevated': '#161B22',
        // Text
        'text-primary': '#E6EDF3',
        'text-secondary': '#7D8590',
        // Accent
        'action-blue': '#58A6FF',
        // Severity colors (Dev View - bold)
        'critical': '#F85149',
        'high': '#DB6D28',
        'medium': '#D29922',
        'low': '#3FB950',
        'info': '#8B949E',
        // User-friendly colors (softer)
        'friendly': {
          'urgent': '#FEE2E2',
          'urgent-text': '#DC2626',
          'important': '#FFEDD5',
          'important-text': '#C2410C',
          'recommended': '#FEF3C7',
          'recommended-text': '#B45309',
          'optional': '#D1FAE5',
          'optional-text': '#059669',
          'info': '#F1F5F9',
          'info-text': '#475569',
        },
      },
      fontFamily: {
        'display': ['JetBrains Mono', 'monospace'],
        'body': ['IBM Plex Sans', 'sans-serif'],
        'mono': ['Fira Code', 'monospace'],
      },
    },
  },
  plugins: [],
}
