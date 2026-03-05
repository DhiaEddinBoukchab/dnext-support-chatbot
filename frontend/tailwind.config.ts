import type { Config } from 'tailwindcss'
import defaultTheme from 'tailwindcss/defaultTheme'

const config: Config = {
  darkMode: ['class'],
  content: [
    './app/**/*.{js,ts,jsx,tsx}',
    './components/**/*.{js,ts,jsx,tsx}',
    './lib/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        // Light mode
        background: {
          light: '#ffffff',
          'light-secondary': '#f8f9fa',
          'light-tertiary': '#f1f3f5',
          DEFAULT: 'hsl(var(--background))',
        },
        foreground: {
          light: '#1a1a1a',
          'light-secondary': '#6b7280',
          DEFAULT: 'hsl(var(--foreground))',
        },
        border: {
          light: '#e5e7eb',
          DEFAULT: 'hsl(var(--border))',
        },
        // Dark mode
        'dark-bg': {
          primary: '#0f172a',
          secondary: '#1e293b',
          tertiary: '#334155',
        },
        'dark-text': {
          primary: '#f1f5f9',
          secondary: '#cbd5e1',
        },
        'dark-border': '#475569',
        // Accent colors
        accent: {
          primary: '#1e40af',
          secondary: '#06b6d4',
          success: '#10b981',
        },
      },
      fontFamily: {
        sans: ['Inter', ...defaultTheme.fontFamily.sans],
      },
      fontSize: {
        xs: ['12px', { lineHeight: '16px' }],
        sm: ['14px', { lineHeight: '20px' }],
        base: ['16px', { lineHeight: '24px' }],
        lg: ['18px', { lineHeight: '28px' }],
        xl: ['20px', { lineHeight: '28px' }],
        '2xl': ['24px', { lineHeight: '32px' }],
        '3xl': ['30px', { lineHeight: '36px' }],
      },
      borderRadius: {
        'none': '0',
        'sm': '4px',
        'base': '6px',
        'md': '8px',
        'lg': '10px',
        'xl': '12px',
        '2xl': '14px',
        'full': '9999px',
      },
      spacing: {
        'xs': '4px',
        'sm': '8px',
        'md': '12px',
        'lg': '16px',
        'xl': '24px',
        '2xl': '32px',
        '3xl': '48px',
        '4xl': '64px',
      },
      boxShadow: {
        'sm': '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
        'base': '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
        'md': '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
        'lg': '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
        'xl': '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
        'dark-sm': '0 1px 2px 0 rgba(0, 0, 0, 0.3)',
        'dark-base': '0 1px 3px 0 rgba(0, 0, 0, 0.3), 0 1px 2px 0 rgba(0, 0, 0, 0.2)',
        'dark-md': '0 4px 6px -1px rgba(0, 0, 0, 0.3), 0 2px 4px -1px rgba(0, 0, 0, 0.2)',
      },
      animation: {
        'fade-in': 'fadeIn 0.3s ease-in-out',
        'fade-in-slow': 'fadeIn 0.5s ease-in-out',
        'slide-in-from-right': 'slideInFromRight 0.3s ease-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideInFromRight: {
          '0%': { transform: 'translateX(16px)', opacity: '0' },
          '100%': { transform: 'translateX(0)', opacity: '1' },
        },
      },
    },
  },
  plugins: [
    require('tailwindcss/plugin')(function ({ addBase, e, theme }) {
      addBase({
        ':root': {
          '--background': '0 0% 100%',
          '--foreground': '0 0% 10%',
          '--border': '0 0% 90%',
        },
        '@media (prefers-color-scheme: dark)': {
          ':root': {
            '--background': '210 40% 6%',
            '--foreground': '210 40% 97%',
            '--border': '210 20% 30%',
          },
        },
      })
    }),
  ],
}

export default config
