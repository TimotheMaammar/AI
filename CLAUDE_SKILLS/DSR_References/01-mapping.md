# Phase 1: High-level mapping

The goal is to write a product brief that every later phase will reference. Skip this and the rest of the skill becomes guesswork.

## 1.1 Questions to answer (in writing, in this order)

### What does the product actually do?

One paragraph, technical, no marketing. Bad: "TeamCollab is a powerful productivity suite for modern teams." Good: "TeamCollab is a Java-based on-premise server exposing an HTTPS web interface on 8443 and a REST API on 8080, backed by PostgreSQL, providing wiki pages, file storage, real-time chat, and a plugin system written in Groovy. It is typically deployed as a single JVM behind a reverse proxy and authenticates users via LDAP, SAML, or local accounts."

What to include:
- Language / runtime (Java JVM, Python interpreter, Go binary, Node.js, native C++, Electron, .NET, mobile native, etc.)
- Deployment model (self-hosted appliance, SaaS, on-prem server, desktop app, mobile app, browser plugin, library, CLI tool)
- Major components (server processes, client processes, databases, message brokers, caches)
- External interfaces (HTTP on which ports, native sockets, IPC channels, USB, Bluetooth, whatever applies)
- Authentication model (local, LDAP, SAML, OIDC, API keys, certificate-based, none)

### What runs as what user?

- Server processes: what UID/account do they run as? (Vendor's recommendation is the floor, real deployments often grant more.)
- Sub-processes: does the main process spawn workers, helpers, plugin runners? Do they inherit privileges or drop them?
- On desktop: does any component run elevated (admin/root)? Auto-start as system service? Driver components?
- On mobile: what permissions does it request? Any of them dangerous (accessibility service, device admin, MDM)?

Privilege boundaries are where impact multiplies. A bug in a low-priv worker is far less interesting than the same bug in a root daemon.

### Where is the trust boundary?

Draw the line(s) between trusted and untrusted. Examples:

- Unauthenticated internet → web frontend → authenticated session → admin endpoints (three boundaries to cross).
- User → desktop GUI → privileged helper service (one boundary, often via IPC).
- Mobile app → backend API → internal microservices (network boundaries).
- Plugin code ↔ host application (sandbox boundary, often porous).

Every boundary is a place where a vulnerability has impact. Phase 4 hypotheses are mostly "X feature lets attacker cross boundary Y".

### What receives untrusted input?

Inventory the input vectors:
- External users (web requests, API calls, form submissions)
- Uploaded files
- Imported configuration / settings / data
- Plugins and extensions installed by users
- Documents/files opened by the desktop app
- Network peers (federation, sync, replication)
- Embedded scripts / macros / templates with user content
- IPC messages from other (potentially less-privileged) processes
- URL schemes / deep links
- Update servers (vendor or third-party)
- Browser content (for any app with an embedded browser/webview)

For each: who can send the input, and which component first parses/handles it?

### What executes code, evaluates expressions, or transforms data?

This is the highest-signal question. Code execution surfaces are where RCEs live.

- Interpreters (JS, Python, Lua, Groovy, custom DSL)
- Template engines (Jinja, Twig, Handlebars, Freemarker, Velocity, ERB, Razor)
- Deserialization (pickle, Java serialization, .NET BinaryFormatter, YAML, XML, custom binary)
- Parsers (XML, JSON, CSV, archive formats, image formats, document formats, font files, custom protocols)
- Native code loaders (DLL, .so, plugin .jar/.py, kernel modules)
- Command execution (shell-out, subprocess, exec)
- Browser engines (Chromium embedded, WebView, WKWebView)
- Sandbox systems (their existence is good; their design and history of breakouts is what matters)

For each: how does input reach this surface, and is the input ever attacker-controlled?

### Authentication and authorization model

- How do users authenticate? Multiple methods?
- Are there service accounts, API keys, machine-to-machine tokens?
- Is there an admin role distinction? Multiple privilege tiers?
- Is there impersonation or delegation? ("Login as user", "act on behalf of")
- Are there unauthenticated endpoints by design? (Health checks, public APIs, embed widgets, all worth listing.)
- How are sessions handled? Tokens, cookies, expiration, revocation?
- Is MFA supported? Is it bypassable for any flows? (Account recovery, OAuth, API key auth often bypass MFA.)

### Deployment context

- Internet-facing or internal-only by default?
- What ports/services does the install procedure expose?
- Reverse proxy assumed or direct exposure?
- Container / Kubernetes / bare metal / serverless?
- Multi-tenant or single-tenant?
- Backup, log, and config storage locations?

A product designed for internal-only deployment but commonly exposed to the internet has a much larger effective attack surface than the docs imply.

## 1.2 Component / data-flow sketch

Draw a small diagram (ASCII or mermaid if the consumer renders it) showing the major components and the data flows between them. This makes the rest of the skill faster: "endpoint X on the API gateway hits the worker, which spawns the plugin runner" is much faster to reason about with a picture than with prose.

Skeleton (replace with real components):

```
                     internet
                        |
                +-------+--------+
                | reverse proxy  |
                +-------+--------+
                        |
            +-----------+-----------+
            | web frontend (auth)   |
            +-----+-----------+-----+
                  |           |
       +----------+---+   +---+--------------+
       | REST API     |   | static asset CDN |
       +----+---------+   +------------------+
            |
   +--------+--------+
   | worker pool     |  *runs plugins as forked subprocesses
   | (groovy plugins)|
   +--------+--------+
            |
       +----+----+
       | postgres |
       +----------+
```

Mark anything that crosses a trust boundary, runs as a different user, or evaluates code. These marks become the priority targets.

## 1.3 Output of phase 1

A document with:
- The product brief paragraph
- The trust boundary statement
- A list of input vectors
- A list of code-execution surfaces
- The auth/authz overview
- The deployment context
- The component/data-flow sketch

Two pages, maximum. This goes at the top of the "annex" part of the deliverable, before chapter-by-chapter notes.
