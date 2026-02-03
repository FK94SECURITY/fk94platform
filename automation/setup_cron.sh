#!/bin/bash
# FK94 Social Media - Cron Setup
# Posts every 2 days at 10:00 AM (Argentina time)

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Install Python dependencies
pip3 install -r "$SCRIPT_DIR/requirements.txt"

# Add cron job: every 2 days at 10:00 AM
CRON_CMD="0 13 */2 * * cd $SCRIPT_DIR && /usr/bin/python3 poster.py es >> poster.log 2>&1"

# Check if already installed
if crontab -l 2>/dev/null | grep -q "poster.py"; then
    echo "Cron job already installed. Skipping."
else
    (crontab -l 2>/dev/null; echo "$CRON_CMD") | crontab -
fi

echo "Cron job installed. Posts will publish every 2 days at 10:00 AM (UTC-3)."
echo "To check: crontab -l"
echo "To see logs: tail -f $SCRIPT_DIR/poster.log"
