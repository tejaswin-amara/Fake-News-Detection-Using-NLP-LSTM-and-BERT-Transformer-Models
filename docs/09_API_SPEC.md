# VERITAS API Specification

## 1. Overview & Architecture Boundary

The VERITAS serving tier is an enterprise FastAPI application serving verified Machine Learning artifacts for fake news detection, calibration, drift monitoring, and capstone evaluation evidence.

- **Base URL (Local)**: `http://localhost:8000`
- **Serving Modes**: `native` (scikit-learn joblib pipeline) and `onnx` (ONNX Runtime session)
- **Protocol**: HTTP/1.1 REST with JSON payloads (`application/json`)
- **Metrics**: Prometheus exposition on `/metrics`
- **Concurrency & Admission Control**: Bounded inference semaphore with non-blocking rejection (HTTP 429)

---

## 2. Global Security & Transport Headers

Every response from the VERITAS API is hardened with the following strict security and telemetry headers:

| Header Name | Value / Format | Purpose |
| :--- | :--- | :--- |
| `X-Request-ID` | String (UUID or sanitized caller trace ID, max 128 chars) | Distributed tracing and audit logging |
| `X-Process-Time-Ms` | Float (e.g. `1.245`) | Server-side execution duration in milliseconds |
| `Cache-Control` | `no-store` | Prevents browser or intermediary caching of prediction results |
| `Content-Security-Policy`| `frame-ancestors 'none'` | Clickjacking mitigation |
| `Referrer-Policy` | `no-referrer` | Privacy leak prevention |
| `X-Content-Type-Options` | `nosniff` | MIME sniffing mitigation |
| `X-Frame-Options` | `DENY` | Disallows framing in external sites |

---

## 3. Endpoints

### 3.1. `GET /health`
Liveness and diagnostic probe for container orchestration.

- **Request**: No parameters or body
- **Response (200 OK)**:
```json
{
  "status": "ready",
  "model_ready": true,
  "model_name": "logistic_l2",
  "artifact_version": "20260910T052501Z",
  "serving_mode": "native",
  "calibration_status": "platt_calibrated",
  "warmup_complete": true,
  "warmup_error": null
}
```

### 3.2. `GET /ready`
Readiness probe verifying that the model artifact is loaded, verified by SHA-256 against `package_manifest.json`, and warmed up.

- **Request**: No parameters or body
- **Response (200 OK)**:
```json
{
  "status": "ready",
  "warmup_complete": true,
  "model_ready": true,
  "model_name": "logistic_l2",
  "artifact_version": "20260910T052501Z",
  "serving_mode": "native",
  "calibration_status": "platt_calibrated"
}
```
- **Error (503 Service Unavailable)**: Returned if the model is not loaded, artifact verification fails, or warmup is incomplete.

### 3.3. `POST /predict`
Single-article inference endpoint. Requires strictly formatted JSON. Unknown fields and control characters are rejected.

- **Headers**: `Content-Type: application/json`
- **Request Body**:
```json
{
  "title": "Federal Reserve Holds Benchmark Interest Rate Steady",
  "text": "The Federal Reserve announced today that it will maintain the federal funds rate at its current target range following a two-day meeting..."
}
```
- **Constraints**:
  - `title`: optional string, max 20,000 chars.
  - `text`: required string, min 1 char, max 50,000 chars.
  - Extra fields are forbidden (`extra="forbid"`).
- **Response (200 OK)**:
```json
{
  "label": 0,
  "label_name": "real",
  "probability_real": 0.8967,
  "probability_fake": 0.1033,
  "model_name": "logistic_l2",
  "artifact_version": "20260910T052501Z",
  "raw_probability_fake": 0.1033,
  "calibrated_probability_fake": 0.1033,
  "confidence_interval_low": null,
  "confidence_interval_high": null,
  "calibration_status": "platt_calibrated",
  "serving_mode": "native",
  "low_signal": false
}
```

### 3.4. `POST /predict/batch`
Bounded batch inference for high-throughput evaluation.

- **Headers**: `Content-Type: application/json`
- **Request Body**:
```json
{
  "requests": [
    {
      "title": "Article 1",
      "text": "The Environmental Protection Agency finalized national standards..."
    },
    {
      "title": "Article 2",
      "text": "Secret whistleblower leaks evidence of alien pyramids under Antarctica..."
    }
  ]
}
```
- **Constraints**:
  - `requests`: array of 1 to 64 `PredictionRequest` items.
- **Response (200 OK)**:
```json
{
  "predictions": [
    {
      "label": 0,
      "label_name": "real",
      "probability_real": 0.8967,
      "probability_fake": 0.1033,
      "model_name": "logistic_l2",
      "artifact_version": "20260910T052501Z",
      "raw_probability_fake": 0.1033,
      "calibrated_probability_fake": 0.1033,
      "confidence_interval_low": null,
      "confidence_interval_high": null,
      "calibration_status": "platt_calibrated",
      "serving_mode": "native",
      "low_signal": false
    },
    {
      "label": 1,
      "label_name": "fake",
      "probability_real": 0.0674,
      "probability_fake": 0.9326,
      "model_name": "logistic_l2",
      "artifact_version": "20260910T052501Z",
      "raw_probability_fake": 0.9326,
      "calibrated_probability_fake": 0.9326,
      "confidence_interval_low": null,
      "confidence_interval_high": null,
      "calibration_status": "platt_calibrated",
      "serving_mode": "native",
      "low_signal": false
    }
  ],
  "count": 2,
  "model_name": "logistic_l2",
  "artifact_version": "20260910T052501Z"
}
```

### 3.5. `POST /monitoring/drift`
Submits an asynchronous data drift job to the bounded drift queue.

- **Headers**: `Content-Type: application/json`
- **Request Body**:
```json
{
  "baseline_revision": "reference-v1",
  "window_id": "window-2026-09-10",
  "reference_probabilities": [0.1, 0.2, 0.3, 0.4, 0.5],
  "current_probabilities": [0.12, 0.18, 0.32, 0.38, 0.52],
  "ks_alpha": 0.05,
  "psi_threshold": 0.20
}
```
- **Response (202 Accepted)**:
```json
{
  "job_id": "db13d0fdd83d4e79b554f5b6e7166182",
  "status": "queued"
}
```
- **Error (429 Too Many Requests)**: Returned if the drift job queue (maxsize 128) is saturated. Header includes `Retry-After: 5`.

### 3.6. `GET /monitoring/drift/{job_id}`
Retrieves the execution status and computed statistical results for a submitted drift job.

- **Response (200 OK)**:
```json
{
  "job_id": "db13d0fdd83d4e79b554f5b6e7166182",
  "status": "completed",
  "result": {
    "baseline_revision": "reference-v1",
    "window_id": "window-2026-09-10",
    "probability": {
      "psi": 0.0807,
      "psi_threshold": 0.20,
      "psi_drift_detected": false,
      "ks": {
        "statistic": 0.125,
        "p_value": 0.1123,
        "drift_detected": false,
        "reference_n": 200,
        "current_n": 200,
        "alpha": 0.05
      },
      "drift_detected": false
    },
    "drifted_features": [],
    "drift_detected": false,
    "retraining_signal": {
      "triggered": false,
      "suggested_action": "continue_monitoring",
      "requires_human_approval": true,
      "cooldown_hours": 24
    }
  },
  "error": null
}
```

### 3.7. `GET /reports/{report_name}`
Exposes authoritative, generated Capstone evidence files for dashboard consumption and academic audit.

- **Allowlisted Report Names**:
  - `data_summary`
  - `linear_models_comparison`
  - `tree_models_comparison`
  - `unsupervised_analysis`
  - `evaluation_report`
  - `calibration_report`
  - `model_comparison`
  - `champion_model`
  - `drift_report`
  - `final_evidence_manifest`
- **Response (200 OK)**: Parsed JSON report structure.
- **Error (404 Not Found)**: Unknown or ungenerated report identifier.

### 3.8. `GET /metrics`
Prometheus exposition format providing operational telemetry:
- `fake_news_http_requests_total{method, route, status}`
- `fake_news_http_request_latency_seconds{method, route, status}`
- `fake_news_inference_latency_seconds{endpoint, serving_mode}`
- `fake_news_inference_queue_depth`
- `fake_news_drift_queue_depth`
- `fake_news_rate_limiter_rejections_total{reason}`

---

## 4. Error Handling Matrix

| HTTP Code | Error Condition | Detail Schema |
| :--- | :--- | :--- |
| `413 Payload Too Large` | Request body exceeds `MAX_REQUEST_BYTES` (1,000,000 bytes) | `{"detail": "Request body exceeds the configured limit", "request_id": "..."}` |
| `415 Unsupported Media Type` | POST endpoint requested with non-`application/json` Content-Type | `{"detail": "This endpoint requires application/json", "request_id": "..."}` |
| `422 Unprocessable Entity` | Pydantic validation failure (missing text, disallowed extra keys, control chars) | `{"detail": "Request validation failed", "request_id": "..."}` |
| `429 Too Many Requests` | Concurrency limit reached or client rate exceeded | `{"detail": "Inference concurrency budget exhausted", "request_id": "..."}` |
| `503 Service Unavailable` | Model artifact missing, corrupt, un-warmed, or queue offline | `{"detail": "Prediction service unavailable", "request_id": "..."}` |

