/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          primary: '#4f46e5',    // indigo-600
          secondary: '#9333ea',  // purple-600
          dark: '#3730a3',       // indigo-700
          light: '#e0e7ff',      // indigo-100
        },
        medical: {
          primary: '#0369a1',
          success: '#16a34a',
          warning: '#ea580c',
          danger: '#dc2626',
          info: '#0ea5e9',
        },
        status: {
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
