import { defineConfig } from '@playwright/test'

export default defineConfig({
  testDir: './e2e',
  use: {
    baseURL: 'http://127.0.0.1:5173',
  },
  webServer: {
    command: 'bun run dev --host 127.0.0.1',
    reuseExistingServer: true,
    url: 'http://127.0.0.1:5173',
  },
})
