/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        navy: '#1B2E56',
        card: '#F8FAFC',
        accent: '#0CAB5C',
      },
      fontFamily: {
        ui: ['system-ui', 'Inter', 'Arial', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
