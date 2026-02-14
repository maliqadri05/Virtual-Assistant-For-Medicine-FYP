/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        medical: {
          primary: '#0369a1',
          success: '#16a34a',
          warning: '#ea580c',
          danger: '#dc2626',
          info: '#0ea5e9',
        },
      },
    },
  },
  plugins: [],
};
