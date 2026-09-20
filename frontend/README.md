# VERITAS AI — Neural Verification & Dual-Model Fake News Detection Platform

> **Production-Grade Web Application & Architectural Overhaul**  
> Comparing Stacked Bi-LSTM vs. Fine-Tuned BERT Transformer with Token-Level Attention Saliency Visualization and Empirical Machine Learning Benchmarks.

---

## 1. Architectural Doctrine & Overview

VERITAS AI transforms the fake news detection machine learning pipeline from a collection of scripts into a premier, interactive, production-grade intelligence platform. Built upon the **Bulletproof React** modular architecture and styled with an **OLED True-Black Glassmorphic** aesthetic, the platform empowers researchers, journalists, and compliance auditors to inspect real-time neural inferences with complete explainability.

### Key Highlights
- **Dual-Model Parallel Inference**: Compare lightweight recurrent networks (**GloVe + Stacked Bi-LSTM**, ~4.2M params) against deep transformer representations (**Fine-Tuned BERT**, ~109.5M params) side-by-side.
- **Attention Token Saliency Heatmap**: Token-by-token visual attribution highlighting word-level log-odds impact toward Credible (Emerald) or Deceptive (Crimson) veracity with an interactive saliency threshold filter slider.
- **Empirical Benchmarks Hub**: Interactive 2x2 confusion matrices, SVG Receiver Operating Characteristic (ROC) curves, and comprehensive hyperparameter pipeline specifications derived directly from reproducible training reports.
- **Persistent Local Audit Trail**: Browser-persisted verification history with instant export to formatted JSON and structured Markdown audit reports.
- **Deterministic Simulation Fallback**: Zero-crash resilience. If the Python FastAPI backend is offline, the application seamlessly activates an intelligent local tokenizer and attribution simulation engine.

---

## 2. Technology Stack & Tooling Constraints

| Layer | Technology | Specification & Role |
| :--- | :--- | :--- |
| **Package Manager** | `pnpm` (v10) | Strict dependency management, disk-efficient symlinked lockfiles. |
| **Framework & Runtime** | Vite 7 + React 19 (TypeScript 5.9) | ESM bundling, modern hook primitives, and strict type safety. |
| **Quality & Linter** | Biome (`@biomejs/biome`) | High-speed Rust-based linter and formatter configured with tab width 2 and strict unused variable rules. |
| **Git Quality Gate** | Lefthook (`evilmartians/lefthook`) | Polyglot pre-commit and pre-push hooks running Biome, typecheck, and Vitest test gates. |
| **Application Structure** | Bulletproof React | Domain-driven slices (`src/features/*`), agnostic UI (`src/components/*`), shared utilities (`src/lib/*`), global hooks (`src/hooks/*`). |
| **Styling Engine** | Tailwind CSS v4 | Utility-first CSS, CSS variables for theming, zero runtime CSS-in-JS overhead. |
| **UI Primitives** | `shadcn/ui` (Radix UI) | Accessible, unstyled primitives (`Dialog`, `Slider`, `Tabs`, `Tooltip`, `Badge`, `Progress`). |
| **Motion & Micro-interactions** | Motion (`framer-motion`) | Physics-based spring animations, layout transitions, and cursor magnetism. |
| **Server State & Data Fetching** | TanStack Query v5 (`@tanstack/react-query`) | Server caching, optimistic state synchronization, request deduplication, and retry logic. |
| **Forms & Validation** | `react-hook-form` + `zod` | Uncontrolled high-performance inputs backed by schema-validated runtime guarantees. |
| **Testing Matrix** | Vitest + React Testing Library + Axe-Core | Unit tests, component integration tests, and automated accessibility auditing. |

---

## 3. Directory & File Organization

The application strictly implements the Bulletproof React modular hierarchy:

```text
frontend/
├── .lefthook.yml                 # Pre-commit & pre-push git quality hooks
├── biome.json                    # Biome linting, formatting, and organize-imports rules
├── index.html                    # Root HTML shell with OLED background and Google Fonts
├── package.json                  # Pnpm configuration and scripts
├── tailwind.config.ts            # Tailwind CSS v4 design tokens and custom animations
├── tsconfig.json                 # TypeScript strict compiler configuration and path aliases
├── vite.config.ts                # Vite dev server, root configuration, and backend API proxy
├── vitest.config.ts              # Vitest test runner configuration and environment matchers
└── src/
    ├── app/                      # App-wide routing, providers, and layout wrapper
    │   ├── App.tsx               # Main dashboard layout, navigation tabs, and toast feedback
    │   ├── App.test.tsx          # Component integration tests
    │   ├── main.tsx              # Application entrypoint with axe-core a11y auditing
    │   └── providers.tsx         # TanStack QueryClientProvider & TooltipProvider
    ├── assets/                   # Static icons and vector graphics
    ├── components/               # Cross-feature, domain-agnostic UI elements
    │   ├── ui/                   # Source-owned accessible shadcn/Radix UI primitives
    │   └── react-bits/           # Bespoke interactive animated components
    │       ├── AnimatedCounter.tsx   # Smooth number-roll interpolation for latency and confidence
    │       ├── AuroraBackground.tsx  # Ambient organic mesh background glow
    │       ├── MagnetButton.tsx      # Physics-based magnetic attraction cursor button
    │       ├── SpotlightCard.tsx     # Dynamic pointer-tracking radial spotlight card
    │       └── TextScramble.tsx      # Decoded glyph transition animation for classification badges
    ├── features/                 # Modular domain slices
    │   ├── inference/            # Article submission, preset loader, real-time prediction
    │   │   ├── api/              # TanStack Query mutations (useInferenceMutation), API client & deterministic fallback
    │   │   ├── components/       # InputArea, PredictButton, ModelOutputCard
    │   │   ├── data/             # Curated article presets with known ground truth
    │   │   └── types/            # Prediction schema, API payloads
    │   ├── comparison/           # Dual-model side-by-side analysis (LSTM vs. BERT)
    │   │   ├── components/       # ComparisonGrid, DualModelCard, DifferentialConfidenceGauge
    │   │   └── utils/            # Metric variance and telemetry calculations
    │   ├── explainability/       # NLP Token attention heatmap and attribution
    │   │   ├── components/       # TokenHighlighter, SaliencyPopover, TokenHeatmap, WeightScale
    │   │   └── types/            # TokenAttention interfaces
    │   ├── benchmarks/           # Visual evaluation dashboards
    │   │   ├── components/       # BenchmarksHub, MetricsRadar, LossGraph, ConfusionMatrix, ROCChart, ArchitectureSpecs
    │   │   └── data/             # Static precomputed empirical data from training runs
    │   └── history/              # Local inference history, CSV/JSON report export
    │       ├── components/       # HistoryTable, ExportModal (Markdown, JSON, CSV)
    │       └── store/            # LocalStorage persistence and synchronization store
    ├── hooks/                    # Global utilities (useMediaQuery, useClipboard, useMobile)
    ├── lib/                      # Axios apiClient, classnames merging (cn)
    └── types/                    # Universal TypeScript declarations (inference, benchmarks)
```

---

## 4. Visual Design & Animated Primitives

### Dark Mode Aesthetic (OLED Glassmorphism)
- **True Black Canvas**: `#030712` base accented by subtle, non-intrusive animated radial mesh gradient (`AuroraBackground`).
- **Glass Surfaces**: Translucent dark surfaces (`bg-zinc-950/70`, `backdrop-blur-xl`, `border border-white/10`).
- **Semantic Glow Tokens**:
  - **Verified Credible**: Emerald glow (`text-emerald-400`, `bg-emerald-500/10`, `border-emerald-500/20`).
  - **Flagged as Deceptive**: Crimson glow (`text-rose-400`, `bg-rose-500/10`, `border-rose-500/20`).
  - **Uncertain / Ambiguous**: Amber glow (`text-amber-400`, `bg-amber-500/10`, `border-amber-500/20`).
  - **Interactive Accent**: Electric Indigo (`text-indigo-400`, `bg-indigo-600`).
- **Typography**: Modern sans font (**Inter**) paired with monospace font (**JetBrains Mono**) for token matrices, classification probabilities, and execution latencies.

### React Bits Primitives (`src/components/react-bits/`)
- `SpotlightCard`: Tracks pointer coordinates via mouse-move listeners and renders a localized radial gradient spotlight behind the translucent card surface.
- `TextScramble`: Decodes classification verdicts by cycling through cryptographic glyphs before resolving to text (e.g. `VERIFIED CREDIBLE` or `FLAGGED AS DECEPTIVE`).
- `MagnetButton`: Attracts toward the cursor within threshold radius using spring damping (`framer-motion`), providing tangible tactile feedback.
- `AnimatedCounter`: Interpolates numeric percentages and latencies continuously across state changes.
- `AuroraBackground`: Organic, multi-layered background light mesh moving smoothly across ambient space.

---

## 5. API Integration & Simulation Fallback Contract

### Target Endpoints
The frontend is configured to communicate with the FastAPI backend at `http://localhost:8000`:
- `POST /api/predict/lstm` — Bi-LSTM inference pass
- `POST /api/predict/bert` — BERT Transformer inference pass
- `POST /api/predict/both` — Dual-model parallel inference pass

### Deterministic Mock Engine
When the backend service is offline, the client does not crash. It automatically activates an intelligent local tokenizer:
1. **Sensationalist Keyword Scoring**: Flags emotional clickbait triggers (e.g., `"shocking"`, `"miracle cure"`, `"banned"`, `"secret plot"`, `"whistleblower"`) with negative log-odds attribution pulling toward `FAKE`.
2. **Credible Marker Attribution**: Identifies verified journalistic institutions and economic terms (e.g., `"announced"`, `"liquidity facility"`, `"central bank"`, `"interbank"`, `"according to"`) with positive attribution pulling toward `REAL`.
3. **Telemetry Emulation**: Generates realistic execution latencies (Bi-LSTM: 14–25ms vs. BERT: 120–165ms) and token counts.
4. **Simulation Badge**: Displays a non-intrusive banner indicating `"Running in Local Demo/Simulation Mode"`.

---

## 6. Available Scripts & Quality Gates

Run all commands from the `frontend/` directory using `pnpm`:

```bash
# Start Vite development server with HMR on port 5173
pnpm dev

# Typecheck codebase using strict TypeScript compiler
pnpm check

# Run Biome linter, formatter, and organize-imports checks
pnpm lint

# Automatically apply Biome formatting and fixes
pnpm lint:fix

# Format entire codebase with Biome
pnpm format

# Run comprehensive Vitest unit and integration test suite
pnpm test

# Build production bundle to dist/public
pnpm build
```

---

## 7. Verification & Compliance Record

- **TypeScript Compilation**: `pnpm check` passes with zero errors (`tsc --noEmit`).
- **Biome Quality Gate**: `pnpm lint` validates all 83 files in 49ms with zero errors and zero warnings.
- **Vitest Test Suite**: 15 test files passed, 40 total tests passed:
  - Form submission and end-to-end inference execution verified.
  - TanStack Query mutation lifecycle and query cache synchronization verified.
  - Token saliency attribution calculations and unique key generation verified.
  - SaliencyPopover and TokenHighlighter directional rendering verified.
  - MetricsRadar multi-dimensional pentagonal chart verified.
  - LossGraph training & validation loss curves across epochs verified.
  - ExportModal Markdown, JSON, and CSV report export formats verified.
  - Global responsive hooks (useMediaQuery, useClipboard) verified.
  - ModelOutputCard individual model metrics telemetry verified.
  - Model variance and comparative telemetry metrics verified.
  - Persistent localStorage history store verified.
  - Existing repository contract tests and FastAPI proxy integration verified.
- **Accessibility**: High-contrast ratios, visible focus outlines, keyboard tab navigation, and automated `@axe-core/react` development-time DOM auditing.
