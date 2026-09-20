import path from "node:path";
import { defineConfig } from "vitest/config";

const templateRoot = path.resolve(import.meta.dirname);

export default defineConfig({
  root: templateRoot,
  esbuild: {
    jsx: "automatic",
  },
  resolve: {
    alias: {
      "@": path.resolve(templateRoot, "src"),
      "@client": path.resolve(templateRoot, "client/src"),
      "@shared": path.resolve(templateRoot, "shared"),
      "@assets": path.resolve(templateRoot, "src/assets"),
    },
  },
  test: {
    environment: "node",
    setupFiles: [path.resolve(templateRoot, "src/test/setup.ts")],
    environmentMatchGlobs: [
      ["client/**/*.test.tsx", "jsdom"],
      ["src/**/*.test.tsx", "jsdom"],
      ["src/**/*.test.ts", "jsdom"],
    ],
    include: [
      "server/**/*.test.ts",
      "server/**/*.spec.ts",
      "client/**/*.test.tsx",
      "src/**/*.test.{ts,tsx}",
    ],
    env: {
      LOCAL_DEMO_MODE: "",
      FAKE_NEWS_INTEGRATION_MODE: "",
    },
  },
});
