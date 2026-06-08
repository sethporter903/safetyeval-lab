/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        ink: '#17202a',
        panel: '#f8fafc',
        safety: '#0f766e',
        warning: '#b45309',
        danger: '#b91c1c',
      },
    },
  },
  plugins: [],
};
