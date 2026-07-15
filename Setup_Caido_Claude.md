# Setup Caido + Claude

1) Install the MCP server:
```
git clone --branch v1.1.0 https://github.com/c0tton-fluff/caido-mcp-server.git
cd .\caido-mcp-server\
go build -o caido-mcp-server.exe .
```

2) Launch Caido

3) Connect to the Caido instance, then start the server:

```
.\caido-mcp-server.exe login -u http://127.0.0.1:8080
.\caido-mcp-server.exe serve -u http://127.0.0.1:8080
```

4) On the Claude side, add the following content to the `C:\Users\XYZ\.claude.json` file:

```
{
  "mcpServers": {
    "caido": {
      "type": "stdio",
      "command": "C:\\tools\\caido-mcp-server\\caido-mcp-server.exe",
      "args": ["serve"],
      "env": {
        "CAIDO_URL": "http://127.0.0.1:8080"
      }
    }
  }
}
```

5) Restart Claude

6) Verify that the installation was successful using one of the following methods:

- Simply ask Claude whether it can see the tools.     
- Launch Claude from the CLI and run `/mcp`.     

Note: if all Caido traffic is routed through a VPS, Claude will not be affected. It communicates with the local Caido instance, which then forwards the traffic.

```
ssh -D 1080 -N root@vps
# Settings → Network → SOCKS Proxies
```

