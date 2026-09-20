# System Context Architecture (C4 Level 1)

This diagram illustrates the high-level system context of the **VERITAS AI** platform, depicting external users, core system boundaries, and interacting enterprise systems.

```mermaid
C4Context
    title System Context Diagram for VERITAS AI Fake News Detection Platform

    Person(auditor, "Compliance Auditor / Journalist", "Submits news claims, inspects veracity scores, and reviews token-level attention attributions.")
    Person(mlops, "MLOps / DevSecOps Engineer", "Monitors inference latency, tracks model drift, audits security scans, and manages releases.")

    Enterprise_Boundary(b0, "VERITAS AI Trust Boundary") {
        System(veritas_platform, "VERITAS AI Full-Stack System", "Unified web interface, edge reverse proxy, and dual-model neural inference platform (Bi-LSTM & BERT).")
    }

    System_Ext(wire_services, "External Wire Feeds", "Source content for claim validation (Reuters, AP, Bloomberg, OpenWire).")
    System_Ext(ci_cd, "GitHub Actions CI/CD", "Automated quality gates, security SAST, container scanning, and artifact delivery.")
    System_Ext(docker_registry, "OCI Container Registry", "Versioned multi-stage images for edge proxy and ML backend.")

    Rel(auditor, veritas_platform, "Submits articles, queries predictions, audits attributions", "HTTPS / REST")
    Rel(mlops, veritas_platform, "Monitors health metrics (/healthz), reviews benchmarks", "HTTPS / Prometheus")
    Rel(ci_cd, docker_registry, "Publishes verified, scanned OCI images", "Docker Push")
    Rel(ci_cd, veritas_platform, "Deploys container recipes via Docker Compose", "SSH / Compose")
    Rel(veritas_platform, wire_services, "Cross-references wire citation metadata", "HTTPS")
```

## System Responsibilities

1. **User Interaction**: Modern React 19 single-page application with responsive OLED glassmorphic interface, interactive token heatmap, and audit trail export.
2. **Edge Security & Routing**: Caddy 2 HTTPS-first reverse proxy enforcing gzip/zstd compression, CSP headers, and routing `/api/*` to FastAPI.
3. **ML Inference Engine**: Python 3.11 FastAPI service executing Stacked Bi-LSTM and Fine-Tuned BERT sequence classification with attention-head token attribution.
