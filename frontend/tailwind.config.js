/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['index.html'],
  theme: {
    container: {
      center: true,
      padding: '16px'
    },
    extend: {
      colors: {
        'defaultColor' : '#F9F8F4',
        'white': '#fff',
        'darkBrown' : '#A2816E',
        'navyBlue' : '#263C6B',
        'lightNavy' : '#385CAA',
        'lightBrown' : '#B29E7F',
        'orange' : '#FE6B3D'
      },
      screens: {
        '2xl' : '1320px'
      }
    },
  },
  plugins: [],
}