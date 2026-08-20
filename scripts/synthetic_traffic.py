"""Generate bounded or continuous synthetic traffic for local serving tests."""

from __future__ import annotations

import argparse
import json
import logging
import signal
import time
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

LOGGER = logging.getLogger("synthetic_traffic")
_STOP = False


@dataclass(frozen=True)
class TrafficConfig:
    base_url: str
    interval_seconds: float
    drift_every: int
    timeout_seconds: float
    max_requests: int | None


def _stop_handler(_signum: int, _frame: object) -> None:
    global _STOP
    _STOP = True


def _post_json(base_url: str, path: str, payload: dict[str, object], timeout: float) -> int:
    body = json.dumps(payload).encode("utf-8")
    request = Request(
        f"{base_url.rstrip('/')}{path}",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            return int(response.status)
    except HTTPError as exc:
        return int(exc.code)
    except (TimeoutError, URLError, OSError):
        return 0


def send_prediction(config: TrafficConfig, request_number: int) -> int:
    payload = {
        "title": "Synthetic headline",
        "text": f"Synthetic article request {request_number} for serving validation.",
    }
    return _post_json(config.base_url, "/predict", payload, config.timeout_seconds)


def send_drift(config: TrafficConfig, request_number: int) -> int:
    reference = [0.10, 0.20, 0.30, 0.40]
    current = [0.15, 0.25, 0.35, 0.45] if request_number % 2 else [0.75, 0.85, 0.90, 0.95]
    payload = {
        "reference_probabilities": reference,
        "current_probabilities": current,
        "baseline_revision": "synthetic-reference-v1",
        "window_id": f"synthetic-window-{request_number}",
    }
    return _post_json(config.base_url, "/monitoring/drift", payload, config.timeout_seconds)


def run(config: TrafficConfig) -> int:
    global _STOP
    request_number = 0
    while not _STOP and (config.max_requests is None or request_number < config.max_requests):
        request_number += 1
        status = send_prediction(config, request_number)
        LOGGER.info("prediction request=%d status=%d", request_number, status)
        if config.drift_every > 0 and request_number % config.drift_every == 0:
            drift_status = send_drift(config, request_number)
            LOGGER.info("drift request=%d status=%d", request_number, drift_status)
        if config.max_requests is None or request_number < config.max_requests:
            time.sleep(max(config.interval_seconds, 0.0))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate synthetic traffic for the fake-news API")
    parser.add_argument("--base-url", default="http://localhost:8000")
    parser.add_argument("--interval", type=float, default=5.0)
    parser.add_argument("--drift-every", type=int, default=10)
    parser.add_argument("--timeout", type=float, default=5.0)
    parser.add_argument("--max-requests", type=int, default=None)
    parser.add_argument("--log-level", default="INFO")
    args = parser.parse_args()
    logging.basicConfig(level=getattr(logging, args.log_level.upper(), logging.INFO), format="%(message)s")
    if args.max_requests is not None and args.max_requests < 1:
        parser.error("--max-requests must be positive when supplied")
    signal.signal(signal.SIGTERM, _stop_handler)
    signal.signal(signal.SIGINT, _stop_handler)
    return run(TrafficConfig(args.base_url, args.interval, args.drift_every, args.timeout, args.max_requests))


if __name__ == "__main__":
    raise SystemExit(main())
