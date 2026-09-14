import { defineConfig } from "vitest/config";
import path from "path";

const templateRoot = path.resolve(import.meta.dirname);

export default defineConfig({
  root: templateRoot,
  esbuild: {
    jsx: "automatic",
  },
  resolve: {
    alias: {
      "@": path.resolve(templateRoot, "client", "src"),
      "@shared": path.resolve(templateRoot, "shared"),
      "@assets": path.resolve(templateRoot, "attached_assets"),
    },
  },
  test: {
    environment: "node",
    environmentMatchGlobs: [["client/**/*.test.tsx", "jsdom"]],
    include: ["server/**/*.test.ts", "server/**/*.spec.ts", "client/**/*.test.tsx"],
    env: {
      LOCAL_DEMO_MODE: "",
      FAKE_NEWS_INTEGRATION_MODE: "",
    },
  },
});
