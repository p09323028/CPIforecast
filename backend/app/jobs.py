"""In-process job manager — a single active forecasting run at a time."""
from __future__ import annotations

import logging
import threading
from datetime import datetime, timezone
from typing import Optional, TypedDict

log = logging.getLogger(__name__)


class JobState(TypedDict, total=False):
    run_id: str
    state: str  # "running" | "done" | "failed"
    started_at: str
    finished_at: Optional[str]
    current_index: int
    total: int
    current_category: Optional[str]
    error: Optional[str]


class JobManager:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._jobs: dict[str, JobState] = {}
        self._active: Optional[str] = None

    def try_start(self, run_id: str, total: int) -> bool:
        with self._lock:
            if self._active is not None:
                return False
            self._active = run_id
            self._jobs[run_id] = {
                "run_id": run_id,
                "state": "running",
                "started_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "finished_at": None,
                "current_index": 0,
                "total": total,
                "current_category": None,
                "error": None,
            }
            return True

    def update_progress(self, run_id: str, index: int, total: int, category: str) -> None:
        with self._lock:
            job = self._jobs.get(run_id)
            if not job:
                return
            job["current_index"] = index
            job["total"] = total
            job["current_category"] = category

    def finish(self, run_id: str, *, ok: bool, error: Optional[str] = None) -> None:
        with self._lock:
            job = self._jobs.get(run_id)
            if not job:
                return
            job["state"] = "done" if ok else "failed"
            job["finished_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
            if error:
                job["error"] = error
            if self._active == run_id:
                self._active = None

    def get(self, run_id: str) -> Optional[JobState]:
        with self._lock:
            job = self._jobs.get(run_id)
            return dict(job) if job else None

    def active_run_id(self) -> Optional[str]:
        with self._lock:
            return self._active


job_manager = JobManager()
