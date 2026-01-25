import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: true, // Expose the server to external connections (e.g., Codespaces)
    port: 3000, // Default port for the Vite server
    strictPort: true, // Ensure the server uses the specified port
    watch: {
      usePolling: true, // Fix for file system issues in some environments
    },
    hmr: {
      clientPort: 443, // Ensure HMR works in Codespaces
    },
  },
  build: {
    outDir: 'dist', // Output directory for the build
  },
});