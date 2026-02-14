#!/usr/bin/env python3
"""
FK94 OpenClaw Runner
Executes autonomous pipeline decisions using backend events API.

Usage:
  python3 openclaw_runner.py --once
  python3 openclaw_runner.py --daemon
"""

from __future__ import annotations

import argparse
import logging
import os
import time
from pathlib import Path

import httpx
import yaml
from dotenv import load_dotenv


ROOT = Path(__file__).parent
TOPOLOGY_PATH = ROOT / "agent_topology.yaml"
LOG_PATH = ROOT / "openclaw_runner.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler(LOG_PATH), logging.StreamHandler()],
)
log = logging.getLogger("fk94-openclaw")


class Runner:
    def __init__(self) -> None:
        load_dotenv(ROOT / ".env", override=False)
        self.api_base = os.environ.get("FK94_API_BASE_URL", "").rstrip("/")
        if not self.api_base:
            self.api_base = "http://localhost:8000/api/v1"
        self.enabled = os.environ.get("ENABLE_AUTONOMY", "false").lower() == "true"
        self.mode = os.environ.get("AUTONOMY_MODE", "guarded").lower()
        self.growth_stage = os.environ.get("GROWTH_STAGE", "pre_pmf").lower()
        self.min_paid_for_post_pmf = int(os.environ.get("MIN_PAID_CUSTOMERS_FOR_POST_PMF", "5"))
        self.daily_spend_cap = float(os.environ.get("DAILY_SPEND_CAP_USD", "300"))
        self.topology = self._load_topology()

    def _load_topology(self) -> dict:
        if not TOPOLOGY_PATH.exists():
            raise FileNotFoundError(f"Missing topology file: {TOPOLOGY_PATH}")
        with TOPOLOGY_PATH.open("r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def _get_stats(self) -> dict:
        url = f"{self.api_base}/events/stats"
        try:
            with httpx.Client(timeout=20.0) as client:
                res = client.get(url)
                res.raise_for_status()
                return res.json()
        except Exception as exc:
            log.warning(f"Could not fetch stats from {url}: {exc}")
            return {"total_events": 0, "scan_completed": 0, "checkout_started": 0, "checkout_success": 0}

    def _track(self, event_type: str, payload: dict) -> None:
        url = f"{self.api_base}/events/track"
        body = {
            "event_type": event_type,
            "payload": payload,
            "source": "openclaw_runner",
        }
        try:
            with httpx.Client(timeout=20.0) as client:
                client.post(url, json=body)
        except Exception as exc:
            log.warning(f"Could not track event {event_type}: {exc}")

    def _execute_pipeline_once(self, pipeline_id: str, stats: dict) -> None:
        """
        Minimal deterministic rules until full event-by-event orchestration is connected.
        """
        checkout_started = int(stats.get("checkout_started", 0))
        checkout_success = int(stats.get("checkout_success", 0))
        scans = int(stats.get("scan_completed", 0))
        total_events = int(stats.get("total_events", 0))

        if pipeline_id == "traffic_engine":
            log.info("[traffic_engine] Running acquisition/content heartbeat")
            self._track("openclaw_acquisition_tick", {"stage": self.growth_stage, "total_events": total_events})
            return

        if pipeline_id == "lead_capture":
            log.info("[lead_capture] Running lead capture heartbeat")
            self._track("openclaw_lead_capture_tick", {"stage": self.growth_stage, "scan_completed": scans})
            return

        if pipeline_id == "free_to_paid":
            if checkout_started > checkout_success:
                pending = checkout_started - checkout_success
                log.info(f"[free_to_paid] Found {pending} pending checkouts; triggering recovery flow")
                self._track("openclaw_checkout_recovery_triggered", {"pending_checkouts": pending})
            else:
                self._track("openclaw_upgrade_nurture_tick", {"stage": self.growth_stage, "scan_completed": scans})
            return

        if pipeline_id == "paid_to_consulting":
            if scans > 0:
                log.info("[paid_to_consulting] Scans detected; enabling consulting qualification checks")
                self._track("openclaw_consulting_qualification_tick", {"scan_completed_count": scans})
            return

        if pipeline_id == "churn_recovery":
            log.info("[churn_recovery] Running churn recovery heartbeat")
            self._track("openclaw_churn_recovery_tick", {"mode": self.mode})

    def run_once(self) -> None:
        if not self.enabled:
            log.warning("Autonomy disabled (ENABLE_AUTONOMY=false). Exiting.")
            return

        stats = self._get_stats()
        paid_customers = int(stats.get("checkout_success", 0))
        effective_stage = self.growth_stage
        if self.growth_stage == "pre_pmf" and paid_customers >= self.min_paid_for_post_pmf:
            effective_stage = "post_pmf"
        self.growth_stage = effective_stage

        log.info(f"Fetched stats: {stats}")
        self._track(
            "openclaw_tick",
            {
                "mode": self.mode,
                "growth_stage": self.growth_stage,
                "daily_spend_cap": self.daily_spend_cap,
                "paid_customers_estimate": paid_customers,
            },
        )

        for pipeline in self.topology.get("pipelines", []):
            pipeline_id = pipeline.get("id", "")
            if not pipeline_id:
                continue
            stages = pipeline.get("stages", [])
            if stages and self.growth_stage not in stages:
                log.info(f"[{pipeline_id}] Skipped for stage={self.growth_stage}")
                continue
            self._execute_pipeline_once(pipeline_id, stats)

    def run_daemon(self, interval_sec: int = 300) -> None:
        log.info(f"Starting daemon loop every {interval_sec}s")
        while True:
            try:
                self.run_once()
            except Exception as exc:
                log.error(f"Runner loop error: {exc}")
            time.sleep(interval_sec)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true", help="Run one iteration")
    parser.add_argument("--daemon", action="store_true", help="Run forever")
    parser.add_argument("--interval", type=int, default=300, help="Daemon interval in seconds")
    args = parser.parse_args()

    runner = Runner()
    if args.once:
        runner.run_once()
        return
    if args.daemon:
        runner.run_daemon(args.interval)
        return
    parser.print_help()


if __name__ == "__main__":
    main()
