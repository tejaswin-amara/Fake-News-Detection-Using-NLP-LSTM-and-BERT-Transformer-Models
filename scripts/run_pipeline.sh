#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"
export PYTHONPATH="$ROOT_DIR${PYTHONPATH:+:${PYTHONPATH}}"

TRACKING_URI="${MLFLOW_TRACKING_URI:-mlruns}"
EXPERIMENT_NAME="${MLFLOW_EXPERIMENT_NAME:-fake-news-detection}"
MODEL_ARTIFACT="${MODEL_ARTIFACT:-artifacts/models/logistic_l2.joblib}"
TRAINING_DATA="${TRAINING_DATA:-data/processed/train.csv}"
ONNX_PATH="${ONNX_PATH:-artifacts/models/logistic_l2.onnx}"
PACKAGE_MANIFEST="${PACKAGE_MANIFEST:-artifacts/models/package_manifest.json}"
REPORT_DIR="${REPORT_DIR:-reports}"

log() {
  printf '[run_pipeline] %s\n' "$*"
}

require_command() {
  command -v "$1" >/dev/null 2>&1 || { printf 'Missing required command: %s\n' "$1" >&2; exit 1; }
}

log "Validating tools and repository contracts"
require_command python
require_command dvc
python -c 'import yaml; yaml.safe_load(open("configs/default.yaml", encoding="utf-8")); print("configuration: valid")'
python scripts/source_audit.py --root .
dvc stage list >/dev/null
bash -n scripts/run_pipeline.sh

mkdir -p artifacts/models reports/evaluation "$REPORT_DIR" mlruns

log "Initializing local MLflow experiment"
python scripts/init_mlflow.py \
  --tracking-uri "$TRACKING_URI" \
  --experiment-name "$EXPERIMENT_NAME"

log "Running DVC ingestion, training, and held-out evaluation"
dvc repro

log "Running MLflow-backed held-out evaluation"
python -m src.evaluate \
  --test data/processed/test.csv \
  --validation data/processed/validation.csv \
  --artifact "$MODEL_ARTIFACT" \
  --output reports/evaluation/final_metrics.json \
  --report-dir reports/evaluation \
  --config configs/default.yaml \
  --mlflow \
  --tracking-uri "$TRACKING_URI" \
  --experiment-name "$EXPERIMENT_NAME"

log "Exporting ONNX and enforcing parity"
python scripts/export_onnx.py \
  --artifact "$MODEL_ARTIFACT" \
  --training "$TRAINING_DATA" \
  --onnx "$ONNX_PATH" \
  --manifest "$PACKAGE_MANIFEST" \
  --epsilon 0.000009

log "Running complete automated test suite"
python -m pytest -q

log "Generating the finalized MLflow report bundle"
python scripts/generate_reports.py \
  --tracking-uri "$TRACKING_URI" \
  --experiment-name "$EXPERIMENT_NAME" \
  --output-dir "$REPORT_DIR" \
  --primary-metric pr_auc \
  --direction maximize

python - <<'PY'
import json
from pathlib import Path

manifest = Path("artifacts/models/package_manifest.json")
summary = Path("reports/best_model_summary.json")
print(json.dumps({
    "status": "completed",
    "package_manifest": str(manifest),
    "package_status": json.loads(manifest.read_text(encoding="utf-8")).get("status") if manifest.exists() else "unavailable",
    "best_model_summary": str(summary),
    "best_run_id": json.loads(summary.read_text(encoding="utf-8")).get("best_run", {}).get("run_id") if summary.exists() else None,
}, indent=2))
PY
