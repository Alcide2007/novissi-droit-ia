import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";

// Exécution locale : le proxy Vite relaie /api vers le backend FastAPI.
const target = (globalThis as { process?: { env?: Record<string, string | undefined> } }).process?.env?.VITE_API_TARGET
  ?? "http://localhost:8000";

export default defineConfig({
  plugins: [react()],
  test: { environment: "jsdom", setupFiles: ["./src/setupTests.ts"], css: false },
  server: { proxy: { "/api": { target, changeOrigin: true, rewrite: (p) => p.replace(/^\/api/, "") } } },
});
