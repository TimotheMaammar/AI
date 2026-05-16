
# Setup to grant Claude limited access to WSL

## WSL

```
sudo apt update
# sudo apt install -y nmap masscan tcpdump arp-scan dnsutils netcat-openbsd curl

node --version 2>/dev/null || sudo apt install -y nodejs npm
sudo useradd -m -s /bin/bash -c "Claude MCP user" claude
sudo passwd -l claude

sudo -u claude mkdir -p /home/claude/recon
sudo -u claude chmod 700 /home/claude/recon

sudo visudo -f /etc/sudoers.d/claude-recon
	# claude ALL=(root) !ALL
	# claude ALL=(root) NOPASSWD: /usr/bin/nmap, /usr/bin/masscan, /usr/sbin/tcpdump, /usr/sbin/arp-scan 
	

```

## Windows

Configuration file : 

"%AppData%\Local\Packages\Claude_XYZ\LocalCache\Roaming\Claude\claude_desktop_config.json"

```
{
  "preferences": {
    "coworkScheduledTasksEnabled": true,
    "ccdScheduledTasksEnabled": true,
    "sidebarMode": "task",
    "coworkWebSearchEnabled": true,
    "epitaxyPrefs": {
      "starred-local-code-sessions": [],
      "starred-cowork-spaces": [],
      "starred-session-groups": [],
      "dframe-local-slice": {
        "pinnedOrder": [],
        "customGroupAssignments": {},
        "customGroupOrder": {}
      }
    },
    "remoteToolsDeviceName": "appledore"
  },
  "mcpServers": {
    "desktop-commander-wsl": {
      "command": "wsl",
      "args": ["-u", "claude", "bash", "-ic", "npx -y @wonderwhy-er/desktop-commander"]
    }
  }
}
```

Restart Claude after editing the file.

## MCP configuration and restriction

Path (WSL) : /home/claude/.claude-server-commander/config.json

```
{
  "blockedCommands": [
    "mkfs", "mkfs.ext4", "mkfs.ext3", "mkfs.xfs",
    "format", "fdisk", "parted", "diskpart",
    "dd",
    "shred",
    "rm -rf /", "rm -rf /*", "rm -rf ~", "rm -rf $HOME",
    "chown -R /", "chmod -R 777 /", "chmod -R 000 /",
    "curl * | sh", "curl * | bash",
    "wget * | sh", "wget * | bash",
    ":(){ :|:& };:",
    "shutdown", "reboot", "halt", "poweroff", "init 0", "init 6",
    "netsh", "sfc", "bcdedit", "reg",
    "userdel"
  ],
  "defaultShell": "/bin/bash",
  "allowedDirectories": ["/home/claude/recon"],
  "telemetryEnabled": false,
  "fileWriteLineLimit": 500,
  "fileReadLineLimit": 10000,
  "pendingWelcomeOnboarding": false,
  "version": "0.2.41",
  "clientId": "XXX",
  "abTest_OnboardingPreTool": "showOnboardingPage"
}

```
