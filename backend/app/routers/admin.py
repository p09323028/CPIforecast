from __future__ import annotations

import logging
import threading
from datetime import datetime, timezone

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException

from forecast import storage
from forecast.categories import english_names
from forecast.runner import run_full

from ..config import settings
from ..deps import verify_admin_token
from ..jobs import job_manager

log = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/admin", tags=["admin"], dependencies=[Depends(verify_admin_token)]
)


def _execute(run_id: str) -> None:
    total = len(english_names())

    def cb(idx: int, total_: int, cat: str) -> None:
        job_manager.update_progress(run_id, idx, total_, cat)

    try:
        run_full(
            settings.DATA_DIR,
            run_id,
            dgbas_url=settings.DGBAS_URL,
            progress_cb=cb,
            keep_runs=settings.KEEP_RUNS,
        )
        job_manager.finish(run_id, ok=True)
    except Exception as exc:
        log.exception("run %s failed", run_id)
        job_manager.finish(run_id, ok=False, error=str(exc))


@router.post("/trigger")
def trigger(background: BackgroundTasks) -> dict:
    run_id = storage.new_run_id()
    total = len(english_names())
    if not job_manager.try_start(run_id, total):
        raise HTTPException(
            409,
            {
                "detail": "another forecast run is already active",
                "active_run_id": job_manager.active_run_id(),
            },
        )
    started_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    threading.Thread(target=_execute, args=(run_id,), daemon=True).start()
    return {"run_id": run_id, "started_at": started_at}


@router.get("/status/{run_id}")
def status(run_id: str) -> dict:
    state = job_manager.get(run_id)
    if not state:
        try:
            manifest = storage.read_manifest(settings.DATA_DIR, run_id)
            return {
                "run_id": run_id,
                "state": "done"
                if manifest.get("finished_at")
                else "unknown",
                "started_at": manifest.get("started_at"),
                "finished_at": manifest.get("finished_at"),
                "current_index": manifest.get("n_ok", 0),
                "total": len(english_names()),
                "current_category": None,
                "error": None,
            }
        except FileNotFoundError:
            raise HTTPException(404, f"run {run_id} not tracked")
    return state
