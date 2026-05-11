import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  build: {
    // Output directly into the Python package so the built assets are
    // bundled into the PyPI distribution by pyproject.toml package-data.
    outDir: path.resolve(__dirname, '../paint_tracker/static'),
    emptyOutDir: true,
  },
})
