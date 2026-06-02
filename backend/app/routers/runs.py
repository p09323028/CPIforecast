from __future__ import annotations

from fastapi import APIRouter, HTTPException

from forecast import storage

from ..config import settings

router = APIRouter(prefix="/api/runs", tags=["runs"])


@router.get("")
def list_runs() -> list[dict]:
    out: list[dict] = []
    for rid in storage.list_run_ids(settings.DATA_DIR):
        try:
            manifest = storage.read_manifest(settings.DATA_DIR, rid)
            out.append(
                {
                    "run_id": rid,
                    "started_at": manifest.get("started_at"),
                    "finished_at": manifest.get("finished_at"),
                    "data_end_date": manifest.get("data_end_date"),
                    "n_ok": manifest.get("n_ok"),
                    "n_failed": manifest.get("n_failed"),
                }
            )
        except FileNotFoundError:
            out.append({"run_id": rid, "status": "no-manifest"})
    return out


@router.get("/latest")
def latest_run() -> dict:
    rid = storage.get_latest_run_id(settings.DATA_DIR)
    if not rid:
        raise HTTPException(404, "no forecast available yet")
    return {"run_id": rid}


@router.get("/{run_id}")
def get_run(run_id: str) -> dict:
    try:
        return storage.read_manifest(settings.DATA_DIR, run_id)
    except FileNotFoundError:
        raise HTTPException(404, f"run {run_id} not found")
