#!/usr/bin/env python3
"""
FK94 Security - Uptime Monitor & Alert System
Checks backend health and sends alerts via Telegram or email.

Usage:
    python3 alert.py                    # Check health, alert if down
    python3 alert.py --test             # Send test alert
    python3 alert.py --status           # Show current status
"""

import json
import os
import sys
import logging
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(Path(__file__).parent / "alert.log"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger("fk94-alert")

STATE_PATH = Path(__file__).parent / "alert_state.json"

HEALTH_URL = os.environ.get("FK94_HEALTH_URL", "https://fk94platform.onrender.com/api/v1/health")
FRONTEND_URL = os.environ.get("FK94_FRONTEND_URL", "https://fk94platform.vercel.app")

# Telegram alert config
TELEGRAM_BOT_TOKEN = os.environ.get("ALERT_TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("ALERT_TELEGRAM_CHAT_ID", "")

# Don't spam alerts
ALERT_COOLDOWN_MINUTES = 30


def load_state():
    if STATE_PATH.exists():
        with open(STATE_PATH) as f:
            return json.load(f)
    return {"last_alert": "", "consecutive_failures": 0, "last_check": "", "status": "unknown"}


def save_state(state):
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)


def check_health(url, timeout=15):
    """Check if URL responds with 200."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "FK94-Monitor/1.0"})
        response = urllib.request.urlopen(req, timeout=timeout)
        return response.status == 200
    except Exception as e:
        log.error(f"Health check failed for {url}: {e}")
        return False


def send_telegram_alert(message):
    """Send alert via Telegram bot."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        log.warning("Telegram not configured. Set ALERT_TELEGRAM_BOT_TOKEN and ALERT_TELEGRAM_CHAT_ID")
        return False

    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = json.dumps({
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "HTML",
        }).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=10)
        log.info("Telegram alert sent")
        return True
    except Exception as e:
        log.error(f"Telegram alert failed: {e}")
        return False


def should_alert(state):
    """Check if enough time has passed since last alert."""
    last_alert = state.get("last_alert", "")
    if not last_alert:
        return True
    try:
        last = datetime.fromisoformat(last_alert)
        diff = (datetime.now() - last).total_seconds() / 60
        return diff >= ALERT_COOLDOWN_MINUTES
    except Exception:
        return True


def run_check():
    state = load_state()

    backend_ok = check_health(HEALTH_URL)
    frontend_ok = check_health(FRONTEND_URL)

    state["last_check"] = datetime.now().isoformat()

    if backend_ok and frontend_ok:
        if state.get("consecutive_failures", 0) > 0:
            # Service recovered
            msg = (
                f"<b>FK94 RECOVERED</b>\n\n"
                f"Backend: OK\n"
                f"Frontend: OK\n"
                f"After {state['consecutive_failures']} failed checks.\n"
                f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            )
            send_telegram_alert(msg)

        state["consecutive_failures"] = 0
        state["status"] = "healthy"
        log.info("All services healthy")

    else:
        state["consecutive_failures"] = state.get("consecutive_failures", 0) + 1

        issues = []
        if not backend_ok:
            issues.append("Backend DOWN")
        if not frontend_ok:
            issues.append("Frontend DOWN")

        state["status"] = "degraded" if (backend_ok or frontend_ok) else "down"

        if should_alert(state):
            msg = (
                f"<b>FK94 ALERT</b>\n\n"
                f"Issues: {', '.join(issues)}\n"
                f"Backend: {'OK' if backend_ok else 'DOWN'}\n"
                f"Frontend: {'OK' if frontend_ok else 'DOWN'}\n"
                f"Consecutive failures: {state['consecutive_failures']}\n"
                f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
                f"Check: {HEALTH_URL}"
            )
            send_telegram_alert(msg)
            state["last_alert"] = datetime.now().isoformat()

        log.warning(f"Issues detected: {issues} (failures: {state['consecutive_failures']})")

    save_state(state)


def show_status():
    state = load_state()
    print(f"Status: {state.get('status', 'unknown')}")
    print(f"Last check: {state.get('last_check', 'never')}")
    print(f"Consecutive failures: {state.get('consecutive_failures', 0)}")
    print(f"Last alert: {state.get('last_alert', 'never')}")


def main():
    if "--test" in sys.argv:
        msg = f"FK94 Monitor test alert\nTime: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        if send_telegram_alert(msg):
            print("Test alert sent successfully")
        else:
            print("Failed to send test alert. Check ALERT_TELEGRAM_BOT_TOKEN and ALERT_TELEGRAM_CHAT_ID")
    elif "--status" in sys.argv:
        show_status()
    else:
        run_check()


if __name__ == "__main__":
    main()
