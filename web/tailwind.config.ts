import type { Config } from 'tailwindcss';

const config: Config = {
  darkMode: ['class'],
  content: ['./app/**/*.{js,ts,jsx,tsx}', './components/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        'on-surface-variant': '#c4c6cc',
        'on-secondary': '#263046',
        secondary: '#bbc6e2',
        outline: '#8e9196',
        'secondary-fixed-dim': '#bbc6e2',
        'on-primary-fixed': '#001f27',
        'on-primary-container': '#008fac',
        'surface-container-highest': '#353439',
        'on-primary-fixed-variant': '#004e5f',
        'on-tertiary-fixed': '#2d0050',
        background: '#131317',
        'surface-tint': '#4cd6fb',
        'primary-container': '#001d25',
        'surface-bright': '#39393d',
        'inverse-on-surface': '#303034',
        'on-primary': '#003642',
        'surface-container-high': '#2a2a2e',
        'surface-container-low': '#1b1b1f',
        'secondary-container': '#3e4960',
        'surface-container-lowest': '#0e0e12',
        'tertiary-fixed': '#f1dbff',
        'tertiary-container': '#2b004d',
        'primary-fixed-dim': '#4cd6fb',
        surface: '#131317',
        'primary-fixed': '#b3ebff',
        'surface-variant': '#353439',
        'inverse-primary': '#00677d',
        tertiary: '#deb7ff',
        'on-secondary-fixed': '#101b30',
        'tertiary-fixed-dim': '#deb7ff',
        'on-surface': '#e4e1e7',
        'on-error-container': '#ffdad6',
        'outline-variant': '#44474c',
        'secondary-fixed': '#d7e2ff',
        'on-secondary-fixed-variant': '#3c475d',
        'surface-container': '#1f1f23',
        'on-error': '#690005',
        'on-tertiary': '#4a007f',
        error: '#ffb4ab',
        'on-secondary-container': '#adb8d3',
        'on-tertiary-container': '#a95eee',
        'error-container': '#93000a',
        'on-background': '#e4e1e7',
        primary: '#4cd6fb',
        'inverse-surface': '#e4e1e7',
        'surface-dim': '#131317',
        'on-tertiary-fixed-variant': '#680eac'
      },
      borderRadius: {
        DEFAULT: '0.125rem',
        lg: '0.25rem',
        xl: '0.5rem',
        full: '0.75rem'
      },
      fontFamily: {
        headline: ['Space Grotesk', 'sans-serif'],
        body: ['Inter', 'sans-serif'],
        label: ['Inter', 'sans-serif']
      }
    }
  },
  plugins: []
};

export default config;
