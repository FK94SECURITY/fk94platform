#!/bin/bash
# =============================================================
# FK94 Rasperito - Raspberry Pi Hardening Script
# Run as root: sudo bash harden_raspi.sh
# =============================================================

set -e

echo "=== FK94 Rasperito Hardening ==="
echo ""

# --- 1. Check running as root ---
if [ "$EUID" -ne 0 ]; then
    echo "ERROR: Run as root (sudo bash harden_raspi.sh)"
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
RASPI_USER="${1:-pi}"

echo "[1/8] Updating system packages..."
apt-get update -qq && apt-get upgrade -y -qq

# --- 2. SSH Hardening ---
echo "[2/8] Hardening SSH..."
SSHD_CONFIG="/etc/ssh/sshd_config"

# Backup original
cp "$SSHD_CONFIG" "$SSHD_CONFIG.bak.$(date +%s)" 2>/dev/null || true

# Disable root login
sed -i 's/^#*PermitRootLogin.*/PermitRootLogin no/' "$SSHD_CONFIG"

# Disable password auth (use keys only)
sed -i 's/^#*PasswordAuthentication.*/PasswordAuthentication no/' "$SSHD_CONFIG"

# Disable empty passwords
sed -i 's/^#*PermitEmptyPasswords.*/PermitEmptyPasswords no/' "$SSHD_CONFIG"

# Limit login attempts
sed -i 's/^#*MaxAuthTries.*/MaxAuthTries 3/' "$SSHD_CONFIG"

# Timeout idle sessions (5 min)
sed -i 's/^#*ClientAliveInterval.*/ClientAliveInterval 300/' "$SSHD_CONFIG"
sed -i 's/^#*ClientAliveCountMax.*/ClientAliveCountMax 2/' "$SSHD_CONFIG"

# Change SSH port (optional but recommended)
# sed -i 's/^#*Port.*/Port 2222/' "$SSHD_CONFIG"

systemctl restart sshd 2>/dev/null || systemctl restart ssh 2>/dev/null || true
echo "  SSH: root login disabled, password auth disabled, max 3 attempts"

# --- 3. Firewall (UFW) ---
echo "[3/8] Configuring firewall..."
apt-get install -y -qq ufw

ufw default deny incoming
ufw default allow outgoing
ufw allow ssh  # or 2222 if you changed the port
ufw --force enable
echo "  Firewall: only SSH allowed inbound"

# --- 4. Fail2Ban ---
echo "[4/8] Installing fail2ban..."
apt-get install -y -qq fail2ban

cat > /etc/fail2ban/jail.local << 'JAIL'
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 3

[sshd]
enabled = true
port = ssh
filter = sshd
logpath = /var/log/auth.log
maxretry = 3
bantime = 7200
JAIL

systemctl enable fail2ban
systemctl restart fail2ban
echo "  Fail2Ban: 3 failed SSH attempts = 2 hour ban"

# --- 5. Secure automation files ---
echo "[5/8] Securing automation files..."

# Set ownership
chown -R "$RASPI_USER":"$RASPI_USER" "$SCRIPT_DIR"

# Restrict .env file (owner read only)
if [ -f "$SCRIPT_DIR/.env" ]; then
    chmod 600 "$SCRIPT_DIR/.env"
    echo "  .env: chmod 600 (owner read only)"
fi

# Restrict browser sessions directory
if [ -d "$SCRIPT_DIR/browser_sessions" ]; then
    chmod 700 "$SCRIPT_DIR/browser_sessions"
    chmod 600 "$SCRIPT_DIR/browser_sessions/"*.json 2>/dev/null || true
    echo "  browser_sessions/: chmod 700 (owner only)"
fi

# Restrict state file
if [ -f "$SCRIPT_DIR/poster_state.json" ]; then
    chmod 600 "$SCRIPT_DIR/poster_state.json"
fi

# Scripts executable only by owner
chmod 700 "$SCRIPT_DIR/"*.py 2>/dev/null || true
chmod 700 "$SCRIPT_DIR/"*.sh 2>/dev/null || true

# Calendar readable by owner only
chmod 600 "$SCRIPT_DIR/content_calendar.json"

echo "  All automation files restricted to owner"

# --- 6. Automatic security updates ---
echo "[6/8] Enabling automatic security updates..."
apt-get install -y -qq unattended-upgrades
dpkg-reconfigure -plow unattended-upgrades 2>/dev/null || true
echo "  Unattended-upgrades: enabled"

# --- 7. Disable unnecessary services ---
echo "[7/8] Disabling unnecessary services..."
systemctl disable bluetooth 2>/dev/null || true
systemctl stop bluetooth 2>/dev/null || true
systemctl disable avahi-daemon 2>/dev/null || true
systemctl stop avahi-daemon 2>/dev/null || true
echo "  Disabled: bluetooth, avahi-daemon"

# --- 8. Log monitoring ---
echo "[8/8] Setting up log rotation for automation..."
cat > /etc/logrotate.d/fk94-automation << LOGROTATE
$SCRIPT_DIR/*.log {
    weekly
    rotate 4
    compress
    missingok
    notifempty
    create 640 $RASPI_USER $RASPI_USER
}
LOGROTATE
echo "  Log rotation: weekly, keep 4 weeks"

echo ""
echo "=== Hardening Complete ==="
echo ""
echo "Summary:"
echo "  - SSH: root disabled, key-only auth, max 3 attempts"
echo "  - Firewall: UFW active, only SSH allowed"
echo "  - Fail2Ban: 3 failed logins = 2h ban"
echo "  - File permissions: .env, sessions, scripts restricted"
echo "  - Auto-updates: security patches enabled"
echo "  - Services: bluetooth and avahi disabled"
echo "  - Logs: rotation configured"
echo ""
echo "IMPORTANT: Make sure you have SSH key access before"
echo "disconnecting, since password auth is now disabled!"
echo ""
echo "To add your SSH key (from your Mac):"
echo "  ssh-copy-id $RASPI_USER@<raspi-ip>"
