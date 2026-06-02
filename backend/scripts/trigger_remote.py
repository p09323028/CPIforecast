"""POST to /api/admin/trigger from a Render Cron Job.

Required env vars: WEB_URL, ADMIN_TOKEN
"""
from __future__ import annotations

import os
import sys

import requests


def main() -> int:
    url = os.environ["WEB_URL"].rstrip("/")
    token = os.environ["ADMIN_TOKEN"]
    resp = requests.post(
        f"{url}/api/admin/trigger",
        headers={"Authorization": f"Bearer {token}"},
        timeout=30,
    )
    print(resp.status_code, resp.text)
    return 0 if resp.ok else 1


if __name__ == "__main__":
    sys.exit(main())
