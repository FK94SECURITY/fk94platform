#!/usr/bin/env python3
"""
FK94 OpenClaw Preflight
Validates required env vars and endpoint availability before deploy.
"""
from __future__ import annotations

import os
import sys
from typing import Iterable

import httpx
from dotenv import load_dotenv


REQUIRED = [
    "FK94_API_BASE_URL",
    "SUPABASE_URL",
    "SUPABASE_SERVICE_ROLE_KEY",
    "STRIPE_SECRET_KEY",
    "STRIPE_WEBHOOK_SECRET",
    "OPENCLAW_API_URL",
    "OPENCLAW_API_KEY",
    "OPENCLAW_PROJECT_ID",
]


def is_set(name: str) -> bool:
    return bool(os.environ.get(name, "").strip())


def check_required(required: Iterable[str]) -> tuple[bool, list[str]]:
    missing = [name for name in required if not is_set(name)]
    return len(missing) == 0, missing


def check_api_health(api_base: str) -> bool:
    url = f"{api_base.rstrip('/')}/health"
    try:
        with httpx.Client(timeout=8.0) as client:
            res = client.get(url)
            return res.status_code == 200
    except Exception:
        return False


def main() -> int:
    load_dotenv(".env", override=False)
    load_dotenv(".env.production", override=False)

    ok, missing = check_required(REQUIRED)
    if not ok:
        print("PRECHECK: FAIL")
        print("Missing required vars:")
        for name in missing:
            print(f"- {name}")
        return 1

    api_base = os.environ["FK94_API_BASE_URL"]
    health_ok = check_api_health(api_base)
    if not health_ok:
        print("PRECHECK: FAIL")
        print(f"- API health check failed at {api_base}/health")
        return 1

    print("PRECHECK: OK")
    print("- Required environment variables: present")
    print(f"- API health check: OK ({api_base}/health)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
