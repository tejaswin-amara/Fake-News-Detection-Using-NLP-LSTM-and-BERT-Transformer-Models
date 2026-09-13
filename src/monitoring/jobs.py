"""Bounded asynchronous monitoring job queue."""

from __future__ import annotations

import asyncio
import time
import uuid
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from starlette.concurrency import run_in_threadpool


@dataclass
class _Job:
    status: str
    created_at: float
    result: dict[str, Any] | None = None
    error: str | None = None


class DriftJobManager:
    def __init__(
        self,
        processor: Callable[[dict[str, Any]], dict[str, Any]],
        maxsize: int = 128,
        workers: int = 2,
        ttl_seconds: int = 900,
        on_failure: Callable[[Exception], None] | None = None,
    ) -> None:
        if maxsize < 1 or workers < 1 or ttl_seconds < 1:
            raise ValueError("Drift job manager settings must be positive")
        self.processor = processor
        self.on_failure = on_failure
        self.queue: asyncio.Queue[tuple[str, dict[str, Any]]] = asyncio.Queue(maxsize=maxsize)
        self.workers = workers
        self.ttl_seconds = ttl_seconds
        self.jobs: dict[str, _Job] = {}
        self.tasks: list[asyncio.Task[None]] = []
        self._stopping = False

    async def start(self) -> None:
        self._stopping = False
        self.tasks = [asyncio.create_task(self._worker(), name=f"drift-worker-{index}") for index in range(self.workers)]

    async def stop(self) -> None:
        self._stopping = True
        for task in self.tasks:
            task.cancel()
        if self.tasks:
            await asyncio.gather(*self.tasks, return_exceptions=True)
        self.tasks = []

    async def submit(self, payload: dict[str, Any]) -> str:
        """Atomically reserve a bounded queue slot without blocking."""
        if self._stopping:
            raise RuntimeError("Drift job queue is unavailable")
        if self.queue.full():
            raise OverflowError("Drift job queue is full")
        job_id = uuid.uuid4().hex
        self.jobs[job_id] = _Job(status="queued", created_at=time.time())
        try:
            self.queue.put_nowait((job_id, payload))
        except asyncio.QueueFull as exc:
            self.jobs.pop(job_id, None)
            raise OverflowError("Drift job queue is full") from exc
        return job_id

    def status(self, job_id: str) -> dict[str, Any] | None:
        job = self.jobs.get(job_id)
        if job is None:
            return None
        if time.time() - job.created_at > self.ttl_seconds:
            job.status = "expired"
            job.result = None
            job.error = None
        return {"job_id": job_id, "status": job.status, "result": job.result, "error": job.error}

    async def _worker(self) -> None:
        while True:
            job_id, payload = await self.queue.get()
            job = self.jobs.get(job_id)
            if job is None:
                self.queue.task_done()
                continue
            job.status = "running"
            try:
                job.result = await run_in_threadpool(self.processor, payload)
                job.status = "completed"
            except Exception as exc:
                job.status = "failed"
                job.error = type(exc).__name__
                if self.on_failure is not None:
                    self.on_failure(exc)
            finally:
                self.queue.task_done()
