from __future__ import annotations

import logging
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from forecast import storage

from .config import settings
from .routers import admin, categories, downloads, forecast, health, prices, runs

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
    stream=sys.stdout,
)
log = logging.getLogger("cpi-api")


def _check_security_config() -> None:
    if not settings.ADMIN_TOKEN:
        log.error("ADMIN_TOKEN env var is not set — admin endpoints will refuse.")
    elif len(settings.ADMIN_TOKEN) < 32:
        log.warning(
            "ADMIN_TOKEN is shorter than 32 chars; use a longer secret in production."
        )


app = FastAPI(
    title="CPI Forecast API",
    description="Taiwan CPI 14-category SARIMA + Monte Carlo forecasts.",
    version="0.1.0",
)

origins = [o.strip() for o in settings.FRONTEND_ORIGIN.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins or ["http://localhost:5173"],
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(health.router)
app.include_router(categories.router)
app.include_router(runs.router)
app.include_router(forecast.router)
app.include_router(prices.router)
app.include_router(downloads.router)
app.include_router(admin.router)


def _cleanup_stale_runs() -> None:
    """Mark any run missing a manifest finished_at as stale and skip latest promotion.

    A run dir without manifest.json (process died before any category completed)
    is removed outright; a run with manifest but no finished_at gets a `stale:
    true` flag.
    """
    import json
    import os
    import shutil

    base = settings.DATA_DIR
    runs_root = os.path.join(base, "runs")
    if not os.path.isdir(runs_root):
        return
    for rid in os.listdir(runs_root):
        rd = os.path.join(runs_root, rid)
        manifest_path = os.path.join(rd, "manifest.json")
        if not os.path.exists(manifest_path):
            log.warning("removing incomplete run dir (no manifest): %s", rid)
            shutil.rmtree(rd, ignore_errors=True)
            continue
        try:
            with open(manifest_path, encoding="utf-8") as f:
                m = json.load(f)
        except Exception:
            continue
        if not m.get("finished_at") and not m.get("stale"):
            log.warning("marking stale run: %s", rid)
            m["stale"] = True
            storage.write_manifest(base, rid, m)

    # Repair latest pointer if it references a missing/incomplete run
    current_latest = storage.get_latest_run_id(base)
    if current_latest:
        latest_manifest = os.path.join(runs_root, current_latest, "manifest.json")
        if not os.path.exists(latest_manifest):
            log.warning(
                "latest.txt points to missing run %s — searching for replacement",
                current_latest,
            )
            for rid in sorted(os.listdir(runs_root), reverse=True):
                mp = os.path.join(runs_root, rid, "manifest.json")
                if not os.path.exists(mp):
                    continue
                try:
                    with open(mp, encoding="utf-8") as f:
                        m = json.load(f)
                except Exception:
                    continue
                if m.get("finished_at") and m.get("n_ok", 0) > 0:
                    storage.set_latest(base, rid)
                    log.info("repaired latest → %s", rid)
                    return


@app.on_event("startup")
def _startup() -> None:
    _check_security_config()
    _cleanup_stale_runs()
    log.info("CPI Forecast API started. DATA_DIR=%s", settings.DATA_DIR)
