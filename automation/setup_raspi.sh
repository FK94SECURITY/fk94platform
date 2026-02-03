#!/bin/bash
# FK94 Security - Raspberry Pi Setup Script
# Run once to configure the Raspi for social media automation.
#
# Usage:
#   chmod +x setup_raspi.sh
#   ./setup_raspi.sh

set -e

echo "=== FK94 Security - Raspi Setup ==="
echo ""

# Update system
echo "[1/6] Updating system packages..."
sudo apt-get update -y
sudo apt-get upgrade -y

# Install Python 3 and dependencies
echo "[2/6] Installing Python and system dependencies..."
sudo apt-get install -y python3 python3-pip python3-venv git curl chromium-browser

# Create project directory
echo "[3/6] Setting up project directory..."
PROJECT_DIR="$HOME/fk94/automation"
mkdir -p "$PROJECT_DIR"
cd "$PROJECT_DIR"

# Copy files if not already there (assumes git clone or manual copy)
if [ ! -f "browser_poster.py" ]; then
    echo "WARNING: Automation scripts not found in $PROJECT_DIR"
    echo "Copy the automation/ directory here first, or clone the repo:"
    echo "  git clone <your-repo> $HOME/fk94"
fi

# Create virtual environment
echo "[4/6] Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Install Playwright + Chromium
echo "[5/6] Installing Playwright and Chromium..."
pip install playwright
playwright install chromium
playwright install-deps

# Create directories
mkdir -p browser_sessions
mkdir -p logs

# Create .env from example if not exists
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "Created .env from .env.example - edit it with your keys"
    else
        cat > .env << 'ENVEOF'
# FK94 Automation Environment
PLATFORM_URL=https://fk94platform.vercel.app

# Kimi K2.5 API (free: platform.moonshot.cn)
KIMI_API_KEY=
KIMI_BASE_URL=https://api.moonshot.ai/v1
AI_MODEL=kimi-k2.5

# Alert notifications (Telegram)
ALERT_TELEGRAM_BOT_TOKEN=
ALERT_TELEGRAM_CHAT_ID=

# Health check URLs
FK94_HEALTH_URL=https://fk94platform.onrender.com/api/v1/health
FK94_FRONTEND_URL=https://fk94platform.vercel.app
ENVEOF
        echo "Created .env - edit it with your API keys"
    fi
fi

# Setup crontab
echo "[6/6] Setting up cron jobs..."
CRON_FILE="/tmp/fk94_crontab"
VENV_PYTHON="$PROJECT_DIR/venv/bin/python3"

cat > "$CRON_FILE" << CRONEOF
# FK94 Security - Automated Social Media & Monitoring
# Installed by setup_raspi.sh on $(date)

# Load environment
SHELL=/bin/bash
PATH=/usr/local/bin:/usr/bin:/bin

# --- Social Media Posting ---
# Twitter: every 2 days at 10am
0 10 */2 * * cd $PROJECT_DIR && $VENV_PYTHON browser_poster.py post twitter >> logs/poster.log 2>&1

# LinkedIn: Monday and Thursday at 10am
0 10 * * 1,4 cd $PROJECT_DIR && $VENV_PYTHON browser_poster.py post linkedin >> logs/poster.log 2>&1

# Reddit: Wednesday at 2pm
0 14 * * 3 cd $PROJECT_DIR && $VENV_PYTHON browser_poster.py post reddit >> logs/poster.log 2>&1

# --- Engagement ---
# X engagement: weekdays at 10am and 5pm
0 10,17 * * 1-5 cd $PROJECT_DIR && $VENV_PYTHON x_engagement.py >> logs/x_engagement.log 2>&1

# Reddit engagement: weekdays at 3pm
0 15 * * 1-5 cd $PROJECT_DIR && $VENV_PYTHON reddit_bot.py >> logs/reddit.log 2>&1

# --- Content Generation ---
# Generate new posts: Sunday 8am
0 8 * * 0 cd $PROJECT_DIR && $VENV_PYTHON content_generator.py --count 10 >> logs/generator.log 2>&1

# --- Monitoring ---
# Health check: every 5 minutes during business hours
*/5 8-22 * * * cd $PROJECT_DIR && $VENV_PYTHON alert.py >> logs/alert.log 2>&1

# --- Cleanup ---
# Rotate logs monthly
0 0 1 * * find $PROJECT_DIR/logs -name "*.log" -size +10M -exec truncate -s 0 {} \;
CRONEOF

# Install crontab (preserving existing entries)
crontab -l 2>/dev/null | grep -v "fk94" > /tmp/existing_cron 2>/dev/null || true
cat /tmp/existing_cron "$CRON_FILE" | crontab -
rm -f /tmp/existing_cron "$CRON_FILE"

echo ""
echo "=== Setup Complete ==="
echo ""
echo "Next steps:"
echo "  1. Edit .env with your API keys (especially KIMI_API_KEY for content generation)"
echo "  2. Login to social platforms (needs a display/VNC for initial login):"
echo "     cd $PROJECT_DIR && source venv/bin/activate"
echo "     python3 browser_poster.py login twitter"
echo "     python3 browser_poster.py login linkedin"
echo "     python3 browser_poster.py login reddit"
echo "  3. Test a dry run:"
echo "     python3 x_engagement.py --dry-run"
echo "     python3 reddit_bot.py --dry-run"
echo "  4. Test alerts:"
echo "     python3 alert.py --test"
echo "  5. Verify cron is running:"
echo "     crontab -l"
echo ""
echo "Logs will be in: $PROJECT_DIR/logs/"
