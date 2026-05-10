/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: "class",
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        // Stitch AI Design System Colors
        'primary-fixed': '#ffdad8',
        'tertiary': '#5d5c5b',
        'surface-tint': '#bb162c',
        'error': '#ba1a1a',
        'on-primary': '#ffffff',
        'surface-container-low': '#f3f3f3',
        'outline-variant': '#e4bebc',
        'inverse-on-surface': '#f1f1f1',
        'on-error': '#ffffff',
        'inverse-primary': '#ffb3b1',
        'on-surface': '#1a1c1c',
        'error-container': '#ffdad6',
        'on-tertiary-fixed': '#1b1b1b',
        'secondary-fixed-dim': '#f4bd6a',
        'on-error-container': '#93000a',
        'tertiary-fixed': '#e5e2e1',
        'on-secondary-fixed': '#291800',
        'on-secondary-container': '#785000',
        'on-tertiary-fixed-variant': '#474746',
        'tertiary-fixed-dim': '#c8c6c5',
        'inverse-surface': '#2f3131',
        'outline': '#8f6f6e',
        'primary-container': '#db313f',
        'on-secondary': '#ffffff',
        'on-primary-fixed-variant': '#92001c',
        'surface-dim': '#dadada',
        'surface-container-highest': '#e2e2e2',
        'surface-container-lowest': '#ffffff',
        'primary': '#b7122a',
        'on-background': '#1a1c1c',
        'secondary-container': '#fdc571',
        'surface': '#f9f9f9',
        'secondary-fixed': '#ffddb1',
        'primary-fixed-dim': '#ffb3b1',
        'on-surface-variant': '#5b403f',
        'surface-variant': '#e2e2e2',
        'surface-bright': '#f9f9f9',
        'on-tertiary': '#ffffff',
        'surface-container': '#eeeeee',
        'on-primary-fixed': '#410007',
        'on-secondary-fixed-variant': '#614000',
        'background': '#f9f9f9',
        'secondary': '#7f5608',
        'on-primary-container': '#fffbff',
        'surface-container-high': '#e8e8e8',
        'tertiary-container': '#757474',
        'on-tertiary-container': '#fffcfb'
      },
      borderRadius: {
        'DEFAULT': '0.25rem',
        'lg': '0.5rem',
        'xl': '0.75rem',
        'full': '9999px'
      },
      spacing: {
        'margin-mobile': '16px',
        'margin-desktop': '24px',
        'container-max': '1200px',
        'gutter': '16px'
      },
      fontFamily: {
        'body-lg': ['Lexend', 'sans-serif'],
        'body-sm': ['Lexend', 'sans-serif'],
        'title-md': ['Lexend', 'sans-serif'],
        'headline-lg': ['Lexend', 'sans-serif'],
        'ai-recommendation': ['Lexend', 'sans-serif'],
        'headline-lg-mobile': ['Lexend', 'sans-serif'],
        'headline-xl': ['Lexend', 'sans-serif'],
        'label-caps': ['Lexend', 'sans-serif'],
        'sans': ['Lexend', 'sans-serif']
      },
      fontSize: {
        'body-lg': ['16px', { lineHeight: '24px', fontWeight: '400' }],
        'body-sm': ['14px', { lineHeight: '20px', fontWeight: '400' }],
        'title-md': ['20px', { lineHeight: '28px', fontWeight: '600' }],
        'headline-lg': ['32px', { lineHeight: '40px', letterSpacing: '-0.01em', fontWeight: '600' }],
        'ai-recommendation': ['14px', { lineHeight: '20px', fontWeight: '500' }],
        'headline-lg-mobile': ['24px', { lineHeight: '30px', fontWeight: '600' }],
        'headline-xl': ['40px', { lineHeight: '48px', letterSpacing: '-0.02em', fontWeight: '700' }],
        'label-caps': ['12px', { lineHeight: '16px', letterSpacing: '0.05em', fontWeight: '600' }]
      },
      animation: {
        'shimmer': 'shimmer 2s linear infinite',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
      keyframes: {
        shimmer: {
          '0%': { backgroundPosition: '200% 0' },
          '100%': { backgroundPosition: '-200% 0' }
        }
      }
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/container-queries'),
  ],
}
