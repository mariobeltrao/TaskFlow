/// <reference types="vitest/config" />
import {defineConfig} from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig(({mode})=>({
  define: mode==='test'?{'import.meta.env.VITE_ENABLE_GOOGLE_INTEGRATION': JSON.stringify('true')}:undefined,
  plugins: [react()],
  server: {proxy: {'/api': 'http://127.0.0.1:8000'}},
  test: {
    environment: 'jsdom',
    fileParallelism: false,
    setupFiles: ['./src/test/setup.ts'],
    exclude: ['e2e/**', 'node_modules/**', 'dist/**'],
    css: false,
    coverage: {
      provider: 'v8',
      reporter: ['text', 'html', 'lcov'],
      include: ['src/**/*.{ts,tsx}'],
      exclude: [
        'src/main.tsx',
        'src/vite-env.d.ts',
        'src/types/**',
        'src/pages/GoogleCalendarIntegration.tsx',
      ],
      thresholds: {lines: 85, statements: 85, functions: 85, branches: 75},
    },
  },
}));
