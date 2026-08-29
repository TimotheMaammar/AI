# Installation of the ryuumonbuchi MCP server (Ghidra)

https://github.com/elliottophellia/Ryuumonbuchi

## MCP Server

```
claude mcp add-json ryuumonbuchi --scope user "{\"type\":\"stdio\",\"command\":\"wsl.exe\",\"args\":[\"-e\",\"uvx\",\"ryuumonbuchi\",\"--ghidra-install-dir\",\"/usr/share/ghidra\"],\"env\":{\"RYUUMONBUCHI_MAX_CPU\":\"4\",\"RYUUMONBUCHI_MAX_HEAP_MB\":\"2048\"}}"
```

Use CMD because PowerShell's argument parsing mangles the JSON and throws an error.

## Ghidra in WSL

```
# 1. Java 21 (required by both Ghidra and ryuumonbuchi)
sudo apt update
sudo apt install -y openjdk-21-jdk unzip curl jq

# 2. Fetch the latest Ghidra release URL automatically (avoids hardcoding a version that goes stale)
GHIDRA_URL=$(curl -s https://api.github.com/repos/NationalSecurityAgency/ghidra/releases/latest \
  | jq -r '.assets[] | select(.name | endswith(".zip")) | .browser_download_url')
echo "$GHIDRA_URL"

# 3. Download and extract to /usr/share (the path used in the ryuumonbuchi config)
curl -L -o /tmp/ghidra.zip "$GHIDRA_URL"
sudo unzip /tmp/ghidra.zip -d /usr/share/

# 4. Rename cleanly (the zip extracts to something like ghidra_12.1.3_PUBLIC)
sudo mv /usr/share/ghidra_*_PUBLIC /usr/share/ghidra

# 5. Make scripts executable (GitHub zip archives sometimes lose the +x flag in transit)
sudo chmod +x /usr/share/ghidra/ghidraRun /usr/share/ghidra/support/*.sh /usr/share/ghidra/support/analyzeHeadless

# 6. Install uv / uvx
curl -LsSf https://astral.sh/uv/install.sh | sh
~/.local/bin/uvx --version

# 7. Symlink uv/uvx into /usr/local/bin
# Required because `wsl.exe -e <cmd>` (the launcher the MCP config uses) runs a non-login shell,
# and that shell's PATH does not include ~/.local/bin, only /usr/local/bin and other system directories.
# Without this the MCP server fails to connect with:
#   "execvpe(uvx) failed: No such file or directory"
sudo ln -sf ~/.local/bin/uvx /usr/local/bin/uvx
sudo ln -sf ~/.local/bin/uv /usr/local/bin/uv
```

## Quick verification

```
java -version                                  # should print 21.x
ls /usr/share/ghidra/support/analyzeHeadless   # must exist, this is what ryuumonbuchi checks on startup
/usr/share/ghidra/support/analyzeHeadless -help | head -5

# run from CMD/PowerShell (not inside WSL): confirms the non-login-shell PATH fix worked
wsl.exe -e uvx --version
```

After this, reboot Claude Code and the terminal session after completing all the steps above, then ask Claude to test the new MCP tools against any binary.
