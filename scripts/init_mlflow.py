"""Initialize a local MLflow experiment without a hosted tracking server."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.tracking import initialize_tracking


def main() -> None:
    parser = argparse.ArgumentParser(description="Initialize a local MLflow experiment")
    parser.add_argument("--tracking-uri", default="mlruns")
    parser.add_argument("--artifact-location", default=None)
    parser.add_argument("--experiment-name", default="fake-news-detection")
    args = parser.parse_args()
    result = initialize_tracking(
        tracking_uri=args.tracking_uri,
        artifact_location=args.artifact_location,
        experiment_name=args.experiment_name,
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
