import pandas as pd

from forecast import storage


def test_round_trip(tmp_path):
    rid = storage.new_run_id()
    storage.run_dir(tmp_path, rid)
    storage.write_manifest(tmp_path, rid, {"run_id": rid, "n_ok": 14})
    storage.set_latest(tmp_path, rid)
    assert storage.get_latest_run_id(tmp_path) == rid
    assert storage.read_manifest(tmp_path, rid)["n_ok"] == 14
    assert rid in storage.list_run_ids(tmp_path)


def test_prune_keeps_latest(tmp_path):
    for i in range(5):
        rid = f"2026-01-{i:02d}T00-00-00Z"
        storage.run_dir(tmp_path, rid)
        storage.write_manifest(tmp_path, rid, {"run_id": rid})
    storage.set_latest(tmp_path, "2026-01-00T00-00-00Z")  # oldest is "latest"
    storage.prune_old_runs(tmp_path, keep=2)
    runs = storage.list_run_ids(tmp_path)
    # latest is always kept
    assert "2026-01-00T00-00-00Z" in runs
