/**
 * FK94 Security - Hardening Script Generator Config
 */

export type OS = 'macos' | 'windows' | 'linux';
export type RiskLevel = 'basic' | 'medium' | 'maximum';

export interface Question {
  id: string;
  question: string;
  options: { value: string; label: string }[];
}

export interface HardeningRule {
  id: string;
  name: string;
  description: string;
  os: OS[];
  riskLevel: RiskLevel[];
  conditions?: { questionId: string; values: string[] }[];
  macCommand?: string;
  windowsCommand?: string;
  linuxCommand?: string;
}

export const questions: Question[] = [
  {
    id: 'os',
    question: 'What operating system do you use?',
    options: [
      { value: 'macos', label: 'macOS' },
      { value: 'windows', label: 'Windows' },
      { value: 'linux', label: 'Linux' },
    ],
  },
  {
    id: 'risk_level',
    question: 'What level of security do you need?',
    options: [
      { value: 'basic', label: 'Basic - Just the essentials' },
      { value: 'medium', label: 'Medium - I handle sensitive data' },
      { value: 'maximum', label: 'Maximum - High risk profile (crypto, journalist, activist)' },
    ],
  },
  {
    id: 'has_crypto',
    question: 'Do you hold cryptocurrency?',
    options: [
      { value: 'yes', label: 'Yes' },
      { value: 'no', label: 'No' },
    ],
  },
  {
    id: 'uses_vpn',
    question: 'Do you currently use a VPN?',
    options: [
      { value: 'yes', label: 'Yes, always' },
      { value: 'sometimes', label: 'Sometimes' },
      { value: 'no', label: 'No' },
    ],
  },
  {
    id: 'public_figure',
    question: 'Are you a public figure or handle sensitive information?',
    options: [
      { value: 'yes', label: 'Yes' },
      { value: 'no', label: 'No' },
    ],
  },
  {
    id: 'work_type',
    question: 'What best describes your work?',
    options: [
      { value: 'general', label: 'General / Office work' },
      { value: 'tech', label: 'Tech / Developer' },
      { value: 'finance', label: 'Finance / Trading' },
      { value: 'journalism', label: 'Journalism / Activism' },
    ],
  },
];

export const hardeningRules: HardeningRule[] = [
  // ============================================
  // FIREWALL
  // ============================================
  {
    id: 'firewall',
    name: 'Enable Firewall',
    description: 'Block unauthorized incoming connections',
    os: ['macos', 'windows', 'linux'],
    riskLevel: ['basic', 'medium', 'maximum'],
    macCommand: `# Enable firewall
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setglobalstate on
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setblockall on
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setstealthmode on
echo "✓ Firewall enabled with stealth mode"`,
    windowsCommand: `# Enable Windows Firewall
Set-NetFirewallProfile -Profile Domain,Public,Private -Enabled True
Write-Host "✓ Firewall enabled"`,
    linuxCommand: `# Enable UFW firewall
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw enable
echo "✓ UFW firewall enabled"`,
  },

  // ============================================
  // DISK ENCRYPTION
  // ============================================
  {
    id: 'disk_encryption',
    name: 'Enable Full Disk Encryption',
    description: 'Encrypt your entire disk to protect data at rest',
    os: ['macos', 'windows'],
    riskLevel: ['basic', 'medium', 'maximum'],
    macCommand: `# Check FileVault status and enable if needed
if ! fdesetup status | grep -q "On"; then
    echo "FileVault is OFF. To enable, run:"
    echo "sudo fdesetup enable"
    echo "⚠️  You will need to restart and save the recovery key!"
else
    echo "✓ FileVault is already enabled"
fi`,
    windowsCommand: `# Check BitLocker status
$status = Get-BitLockerVolume -MountPoint "C:"
if ($status.ProtectionStatus -eq "Off") {
    Write-Host "BitLocker is OFF. To enable, run:"
    Write-Host "Enable-BitLocker -MountPoint 'C:' -EncryptionMethod Aes256"
    Write-Host "⚠️  Save your recovery key!"
} else {
    Write-Host "✓ BitLocker is already enabled"
}`,
  },

  // ============================================
  // DNS ENCRYPTION
  // ============================================
  {
    id: 'dns_encryption',
    name: 'Configure Encrypted DNS',
    description: 'Use DNS over HTTPS to prevent DNS snooping',
    os: ['macos', 'windows', 'linux'],
    riskLevel: ['basic', 'medium', 'maximum'],
    macCommand: `# Set DNS to Cloudflare (1.1.1.1) with DoH
networksetup -setdnsservers Wi-Fi 1.1.1.1 1.0.0.1
echo "✓ DNS set to Cloudflare (1.1.1.1)"
echo "For full DoH, configure in System Settings > Network > DNS"`,
    windowsCommand: `# Set DNS to Cloudflare
Set-DnsClientServerAddress -InterfaceAlias "Wi-Fi" -ServerAddresses ("1.1.1.1","1.0.0.1")
Set-DnsClientServerAddress -InterfaceAlias "Ethernet" -ServerAddresses ("1.1.1.1","1.0.0.1")
Write-Host "✓ DNS set to Cloudflare (1.1.1.1)"`,
    linuxCommand: `# Set DNS to Cloudflare
echo "nameserver 1.1.1.1" | sudo tee /etc/resolv.conf
echo "nameserver 1.0.0.1" | sudo tee -a /etc/resolv.conf
echo "✓ DNS set to Cloudflare (1.1.1.1)"`,
  },

  // ============================================
  // DISABLE REMOTE ACCESS
  // ============================================
  {
    id: 'disable_remote',
    name: 'Disable Remote Access',
    description: 'Turn off remote login and screen sharing',
    os: ['macos', 'windows'],
    riskLevel: ['basic', 'medium', 'maximum'],
    macCommand: `# Disable remote login
sudo systemsetup -setremotelogin off 2>/dev/null || true
# Disable remote management
sudo /System/Library/CoreServices/RemoteManagement/ARDAgent.app/Contents/Resources/kickstart -deactivate -stop 2>/dev/null || true
echo "✓ Remote access disabled"`,
    windowsCommand: `# Disable Remote Desktop
Set-ItemProperty -Path 'HKLM:\\System\\CurrentControlSet\\Control\\Terminal Server' -Name "fDenyTSConnections" -Value 1
Write-Host "✓ Remote Desktop disabled"`,
  },

  // ============================================
  // SCREEN LOCK
  // ============================================
  {
    id: 'screen_lock',
    name: 'Configure Auto Screen Lock',
    description: 'Lock screen automatically after inactivity',
    os: ['macos', 'windows'],
    riskLevel: ['basic', 'medium', 'maximum'],
    macCommand: `# Require password immediately after sleep
defaults write com.apple.screensaver askForPassword -int 1
defaults write com.apple.screensaver askForPasswordDelay -int 0
# Set screen saver to 5 minutes
defaults -currentHost write com.apple.screensaver idleTime -int 300
echo "✓ Screen lock configured (5 min timeout)"`,
    windowsCommand: `# Set screen lock timeout to 5 minutes
powercfg -change -monitor-timeout-ac 5
powercfg -change -monitor-timeout-dc 5
Write-Host "✓ Screen lock timeout set to 5 minutes"`,
  },

  // ============================================
  // DISABLE BLUETOOTH (Medium+)
  // ============================================
  {
    id: 'bluetooth',
    name: 'Disable Bluetooth When Not In Use',
    description: 'Bluetooth can be used for tracking and attacks',
    os: ['macos'],
    riskLevel: ['medium', 'maximum'],
    macCommand: `# Note: This disables Bluetooth. Re-enable in System Settings if needed.
sudo defaults write /Library/Preferences/com.apple.Bluetooth ControllerPowerState -int 0
sudo killall -HUP blued
echo "✓ Bluetooth disabled (re-enable in System Settings when needed)"`,
  },

  // ============================================
  // DISABLE TELEMETRY
  // ============================================
  {
    id: 'telemetry',
    name: 'Disable Analytics & Telemetry',
    description: 'Stop sending usage data to Apple/Microsoft',
    os: ['macos', 'windows'],
    riskLevel: ['basic', 'medium', 'maximum'],
    macCommand: `# Disable Apple analytics
defaults write com.apple.assistant.support "Siri Data Sharing Opt-In Status" -int 2
defaults write com.apple.CrashReporter DialogType none
defaults write com.apple.SoftwareUpdate ScheduleFrequency -int 1
# Disable personalized ads
defaults write com.apple.AdLib allowApplePersonalizedAdvertising -bool false
echo "✓ Apple telemetry and personalized ads disabled"`,
    windowsCommand: `# Disable Windows telemetry
Set-ItemProperty -Path "HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\DataCollection" -Name "AllowTelemetry" -Value 0
Set-Service -Name "DiagTrack" -StartupType Disabled
Stop-Service -Name "DiagTrack" -Force
Write-Host "✓ Windows telemetry disabled"`,
  },

  // ============================================
  // GATEKEEPER (macOS)
  // ============================================
  {
    id: 'gatekeeper',
    name: 'Enable Gatekeeper',
    description: 'Only allow apps from identified developers',
    os: ['macos'],
    riskLevel: ['basic', 'medium', 'maximum'],
    macCommand: `# Enable Gatekeeper
sudo spctl --master-enable
echo "✓ Gatekeeper enabled"`,
  },

  // ============================================
  // DISABLE GUEST ACCOUNT
  // ============================================
  {
    id: 'guest_account',
    name: 'Disable Guest Account',
    description: 'Remove guest login option',
    os: ['macos', 'windows'],
    riskLevel: ['basic', 'medium', 'maximum'],
    macCommand: `# Disable guest account
sudo defaults write /Library/Preferences/com.apple.loginwindow GuestEnabled -bool false
echo "✓ Guest account disabled"`,
    windowsCommand: `# Disable Guest account
net user Guest /active:no
Write-Host "✓ Guest account disabled"`,
  },

  // ============================================
  // SECURE HOSTNAME (Medium+)
  // ============================================
  {
    id: 'hostname',
    name: 'Randomize Device Hostname',
    description: 'Use a generic hostname to avoid identification',
    os: ['macos'],
    riskLevel: ['medium', 'maximum'],
    macCommand: `# Set generic hostname
HOSTNAME="MacBook-$(openssl rand -hex 3)"
sudo scutil --set ComputerName "$HOSTNAME"
sudo scutil --set HostName "$HOSTNAME"
sudo scutil --set LocalHostName "$HOSTNAME"
echo "✓ Hostname changed to: $HOSTNAME"`,
  },

  // ============================================
  // DISABLE LOCATION SERVICES (Maximum)
  // ============================================
  {
    id: 'location',
    name: 'Disable Location Services',
    description: 'Prevent apps from accessing your location',
    os: ['macos'],
    riskLevel: ['maximum'],
    macCommand: `# Disable location services (requires restart)
sudo defaults write /var/db/locationd/Library/Preferences/ByHost/com.apple.locationd LocationServicesEnabled -int 0
echo "✓ Location services disabled (restart required)"`,
  },

  // ============================================
  // CRYPTO-SPECIFIC: SECURE CLIPBOARD
  // ============================================
  {
    id: 'clipboard_crypto',
    name: 'Clear Clipboard Regularly',
    description: 'Prevent clipboard malware from stealing wallet addresses',
    os: ['macos', 'windows'],
    riskLevel: ['medium', 'maximum'],
    conditions: [{ questionId: 'has_crypto', values: ['yes'] }],
    macCommand: `# Clear clipboard now
pbcopy < /dev/null
echo "✓ Clipboard cleared"
echo "TIP: Consider using a clipboard manager that auto-clears (like Maccy)"`,
    windowsCommand: `# Clear clipboard
Set-Clipboard -Value $null
Write-Host "✓ Clipboard cleared"`,
  },

  // ============================================
  // DISABLE AIRDROP (Medium+)
  // ============================================
  {
    id: 'airdrop',
    name: 'Disable AirDrop',
    description: 'Prevent unauthorized file sharing',
    os: ['macos'],
    riskLevel: ['medium', 'maximum'],
    macCommand: `# Disable AirDrop
defaults write com.apple.NetworkBrowser DisableAirDrop -bool true
echo "✓ AirDrop disabled"`,
  },

  // ============================================
  // SECURE SSH (Tech users)
  // ============================================
  {
    id: 'ssh_security',
    name: 'Secure SSH Configuration',
    description: 'Harden SSH if you use it',
    os: ['macos', 'linux'],
    riskLevel: ['medium', 'maximum'],
    conditions: [{ questionId: 'work_type', values: ['tech'] }],
    macCommand: `# Secure SSH (if enabled)
if [ -f /etc/ssh/sshd_config ]; then
    echo "SSH detected. Recommended settings:"
    echo "  PermitRootLogin no"
    echo "  PasswordAuthentication no"
    echo "  PubkeyAuthentication yes"
    echo "Apply manually in /etc/ssh/sshd_config"
else
    echo "✓ SSH not enabled"
fi`,
    linuxCommand: `# Secure SSH
sudo sed -i 's/#PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
sudo sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
sudo systemctl restart sshd
echo "✓ SSH hardened"`,
  },

  // ============================================
  // BROWSER PRIVACY REMINDER
  // ============================================
  {
    id: 'browser_reminder',
    name: 'Browser Security Reminder',
    description: 'Important browser settings',
    os: ['macos', 'windows', 'linux'],
    riskLevel: ['basic', 'medium', 'maximum'],
    macCommand: `echo ""
echo "═══════════════════════════════════════════"
echo "BROWSER SECURITY CHECKLIST"
echo "═══════════════════════════════════════════"
echo "1. Install uBlock Origin extension"
echo "2. Use DuckDuckGo or Brave Search"
echo "3. Disable third-party cookies"
echo "4. Enable Enhanced Tracking Protection"
echo "5. Consider using Firefox or Brave"
echo "═══════════════════════════════════════════"`,
    windowsCommand: `Write-Host ""
Write-Host "═══════════════════════════════════════════"
Write-Host "BROWSER SECURITY CHECKLIST"
Write-Host "═══════════════════════════════════════════"
Write-Host "1. Install uBlock Origin extension"
Write-Host "2. Use DuckDuckGo or Brave Search"
Write-Host "3. Disable third-party cookies"
Write-Host "4. Enable Enhanced Tracking Protection"
Write-Host "5. Consider using Firefox or Brave"
Write-Host "═══════════════════════════════════════════"`,
    linuxCommand: `echo ""
echo "═══════════════════════════════════════════"
echo "BROWSER SECURITY CHECKLIST"
echo "═══════════════════════════════════════════"
echo "1. Install uBlock Origin extension"
echo "2. Use DuckDuckGo or Brave Search"
echo "3. Disable third-party cookies"
echo "4. Enable Enhanced Tracking Protection"
echo "5. Consider using Firefox or Brave"
echo "═══════════════════════════════════════════"`,
  },
];

// Generate script based on answers
export function generateScript(answers: Record<string, string>): string {
  const os = answers.os as OS;
  const riskLevel = answers.risk_level as RiskLevel;

  const applicableRules = hardeningRules.filter((rule) => {
    // Check OS compatibility
    if (!rule.os.includes(os)) return false;

    // Check risk level
    if (!rule.riskLevel.includes(riskLevel)) return false;

    // Check conditions
    if (rule.conditions) {
      for (const condition of rule.conditions) {
        const answer = answers[condition.questionId];
        if (!condition.values.includes(answer)) return false;
      }
    }

    return true;
  });

  const commandKey = os === 'macos' ? 'macCommand' : os === 'windows' ? 'windowsCommand' : 'linuxCommand';

  let script = '';

  if (os === 'macos' || os === 'linux') {
    script = `#!/bin/bash
#
# FK94 Security - Hardening Script
# Generated: ${new Date().toISOString()}
# OS: ${os}
# Risk Level: ${riskLevel}
#
# Run with: chmod +x fk94-harden.sh && ./fk94-harden.sh
#

set -e

echo "═══════════════════════════════════════════"
echo "  FK94 Security - System Hardening Script"
echo "  Risk Level: ${riskLevel.toUpperCase()}"
echo "═══════════════════════════════════════════"
echo ""

`;
  } else {
    script = `#
# FK94 Security - Hardening Script
# Generated: ${new Date().toISOString()}
# OS: Windows
# Risk Level: ${riskLevel}
#
# Run as Administrator in PowerShell
#

Write-Host "═══════════════════════════════════════════"
Write-Host "  FK94 Security - System Hardening Script"
Write-Host "  Risk Level: ${riskLevel.toUpperCase()}"
Write-Host "═══════════════════════════════════════════"
Write-Host ""

`;
  }

  for (const rule of applicableRules) {
    const command = rule[commandKey];
    if (command) {
      if (os === 'windows') {
        script += `
# ${rule.name}
# ${rule.description}
${command}
Write-Host ""

`;
      } else {
        script += `
# ${rule.name}
# ${rule.description}
${command}
echo ""

`;
      }
    }
  }

  if (os === 'macos' || os === 'linux') {
    script += `
echo "═══════════════════════════════════════════"
echo "  HARDENING COMPLETE"
echo "  Some changes may require a restart."
echo ""
echo "  For more security tools, visit:"
echo "  https://fk94security.com"
echo "═══════════════════════════════════════════"
`;
  } else {
    script += `
Write-Host "═══════════════════════════════════════════"
Write-Host "  HARDENING COMPLETE"
Write-Host "  Some changes may require a restart."
Write-Host ""
Write-Host "  For more security tools, visit:"
Write-Host "  https://fk94security.com"
Write-Host "═══════════════════════════════════════════"
`;
  }

  return script;
}

export function getScriptFilename(os: OS): string {
  if (os === 'windows') return 'fk94-harden.ps1';
  return 'fk94-harden.sh';
}

export function getScriptInstructions(os: OS): string[] {
  if (os === 'windows') {
    return [
      'Open PowerShell as Administrator',
      'Navigate to download folder: cd Downloads',
      'Allow script execution: Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass',
      'Run the script: .\\fk94-harden.ps1',
    ];
  }
  return [
    'Open Terminal',
    'Navigate to download folder: cd ~/Downloads',
    'Make executable: chmod +x fk94-harden.sh',
    'Run the script: ./fk94-harden.sh',
  ];
}
