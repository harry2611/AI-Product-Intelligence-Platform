/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#eef9f4',
          100: '#d8efe4',
          200: '#b5dfcb',
          300: '#84c7a7',
          400: '#4aa679',
          500: '#29885d',
          600: '#1c6d4a',
          700: '#17573c',
          800: '#154531',
          900: '#12392a'
        }
      }
    }
  },
  plugins: []
};
