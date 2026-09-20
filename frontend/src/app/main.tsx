import React, { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { App } from "./App";
import { Providers } from "./providers";
import "../index.css";

// Automated accessibility audits in development
if (process.env.NODE_ENV !== "production" && typeof window !== "undefined") {
  import("@axe-core/react")
    .then((axe) => {
      axe.default(React, createRoot, 1000);
    })
    .catch(() => {
      // Axe-core optional fallback in dev
    });
}

const container = document.getElementById("root");
if (!container) {
  throw new Error("Root container element '#root' not found");
}

const root = createRoot(container);
root.render(
  <StrictMode>
    <Providers>
      <App />
    </Providers>
  </StrictMode>
);
