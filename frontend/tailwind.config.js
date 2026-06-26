/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        workspace: {
          DEFAULT: '#F9FAFB', // Off-white canvas
          accent: '#F3F4F6'
        },
        slate: {
          850: '#1e293b', // Deep slate gray
          900: '#0f172a',
        },
        status: {
          resolved: {
            bg: '#ecfdf5', // Soft green
            text: '#065f46' // Dark green
          },
          pending: {
            bg: '#fffbeb', // Muted amber
            text: '#92400e' // Dark amber
          },
          critical: {
            bg: '#fef2f2', // Soft red
            text: '#991b1b' // Dark red
          }
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        'micro': '0 2px 4px rgba(0, 0, 0, 0.02), 0 1px 2px rgba(0, 0, 0, 0.04)',
        'elevated': '0 10px 15px -3px rgba(0, 0, 0, 0.05), 0 4px 6px -2px rgba(0, 0, 0, 0.025)',
      }
    },
  },
  plugins: [],
}
