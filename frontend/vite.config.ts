import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Dev: the React app runs on :5173 and proxies /api to the FastAPI backend on :8000.
// Production: `npm run build` writes dist/, which FastAPI serves at http://localhost:8000/.
// Set AVF_API_PORT if the backend runs on another port (e.g. 8001 when 8000 is taken).
const apiPort = process.env.AVF_API_PORT ?? "8000";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: { "/api": { target: `http://127.0.0.1:${apiPort}`, changeOrigin: false } },
  },
  build: { outDir: "dist", sourcemap: false },
});
