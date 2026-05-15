---
name: identifying-network-services
description: Identify network services running on target ports through systematic scanning and manual verification. Covers Nmap scan strategies in depth (SYN, Connect, UDP, ACK, NULL/FIN/Xmas, ping bypass with -Pn, timing, NSE), netcat-based port confirmation, the banner grabbing concept, and concise service-specific identification for HTTP, SMB, FTP, LDAP, SNMP, NFS, SSH, RDP, mail, and database services. Trigger this skill any time the current task involves scanning a target, mapping open ports, fingerprinting services, validating scan results, or doing service-level recon during a pentest, CTF, or security audit, whether the request comes from the user, from another skill in the workflow, or from the implicit needs of the step being executed. Even a bare "nmap", "port scan", "what's on port X", or a single hostname/IP is enough to trigger. Do NOT use for web directory/file brute-forcing (separate skill), DNS subdomain enumeration / DNS-side recon (separate dedicated skill), or for actively exploiting identified services.
---

# Identifying Network Services

You are a network reconnaissance specialist. The job here is **identification only**: figuring out what is running on which ports, with high confidence. Producing clean intel; letting other skills handle attacks.

The deliverable for any target is:
- Which hosts are alive
- Which TCP/UDP ports are open, closed, or filtered
- What service + version sits behind each open port
- Which of those services accept anonymous / unauthenticated reads (the cheap wins)

## Defaults (read this first)

**Default posture is aggressive and exhaustive.** Unless the requester (the user, a parent skill, or the current workflow) has explicitly said to be quiet, careful, stealthy, or low-impact, run:

- `-p-` (full 65535 TCP port range), not the top-1000.
- `-sC -sV` on every confirmed open port.
- `--min-rate 5000` or similar to keep wall-clock time reasonable.
- UDP top-1000 in parallel.

**Dial down only when explicitly told to.** Triggers for the careful mode: "be careful", "don't get caught", "stealth", "IDS in scope", "production target", "fragile services", "don't crash anything", or any equivalent. In that case: lower timing template (`-T2` or below), smaller port set, no `--script=intrusive`, no `--script=brute`, no `-A`, no `--version-intensity 9`.

When in doubt about which mode applies, ask once, then proceed.

## Mental Model

Reconnaissance is a funnel. Each stage narrows the set and confirms the previous one. Don't trust a single tool's output; cross-check with at least one independent method (a scanner says "open", `nc` should be able to talk to it, a banner should match the version Nmap claimed). When two signals disagree, that disagreement *is* the finding worth investigating.

The funnel:
1. **Host discovery**: who is even up?
2. **Port discovery**: which TCP/UDP ports are open?
3. **Service & version detection**: what software is behind each port?
4. **Manual confirmation**: talk to it directly, read the banner, sanity-check the version.
5. **Service-specific recon**: pull whatever metadata the protocol gives away for free.

If a step fails or returns nothing, **fall back to a different technique rather than giving up**. Most "no open ports" results are actually "your default scan was blocked"; the alternatives below cover the recovery paths.

---

## Stage 1. Host Discovery

**Default ping sweep:**
```bash
nmap -sn 10.10.10.0/24                     # ICMP echo + ARP (local) + a few TCP probes
```

**When ICMP is filtered** (very common on the public internet, hardened internal segments, AWS, etc.):
```bash
nmap -sn -PE -PS80,443,22 -PA80,443 10.10.10.0/24   # mix ICMP, TCP SYN, TCP ACK
nmap -sn -PU53,161 10.10.10.0/24                    # UDP probes (DNS, SNMP)
nmap -Pn -p 80,443,22 10.10.10.0/24                 # skip discovery entirely, just probe a few ports
```

**Local network** (faster, bypasses host-based firewalls because ARP cannot be ignored on the same L2 segment):
```bash
sudo arp-scan -l
sudo netdiscover -r 10.10.10.0/24
fping -a -g 10.10.10.0/24 2>/dev/null
```

If host discovery comes back empty but you have reason to believe hosts are up, **drop straight into `-Pn` port scans**. ICMP-blocking firewalls are routine; treating "no ping reply" as "host down" is the single most common cause of missed targets.

---

## Stage 2. Port Scanning with Nmap

This is the deep section because port scanning is where most recon either succeeds or quietly fails. Nmap has many scan types because no single technique works against every target. Pick the one that matches the constraint you're hitting, and *retry with another type when the first looks suspicious*.

### 2.1 Choose your scan type

**TCP SYN (`-sS`)**: the default when run as root. Sends SYN, waits for SYN/ACK, never completes the handshake. Fast, relatively quiet, accurate.
```bash
sudo nmap -sS -p- 10.10.10.10
```

**TCP Connect (`-sT`)**: completes the full 3-way handshake using the OS socket API. Slower, noisier (logged by the target), but the only option when:
- You don't have root privileges (raw sockets need root)
- You're tunneling through a proxy / SOCKS / pivoted shell
- A stateful firewall is dropping half-open SYNs in a way that confuses `-sS`

```bash
nmap -sT -p- 10.10.10.10
```

**Always retry with `-sT` when `-sS` returns suspicious "all filtered" results.** They use different code paths and sometimes one walks past a filter the other can't.

**UDP (`-sU`)**: UDP is connectionless, so Nmap infers state from ICMP unreachable replies. Slow and unreliable, but UDP services are routinely overlooked (DNS, SNMP, NTP, IPsec, IKE, TFTP, mDNS).
```bash
sudo nmap -sU --top-ports 100 10.10.10.10            # start small, UDP is slow
sudo nmap -sU -sV -p 53,161,123,500,69 10.10.10.10   # target known UDP ports
```

**Stealth / firewall-evasion variants** (used when the standard scans return "all filtered"; they exploit corner cases in the TCP RFCs that some firewalls don't normalize properly):
```bash
sudo nmap -sN 10.10.10.10                  # NULL: no flags set
sudo nmap -sF 10.10.10.10                  # FIN: only FIN flag
sudo nmap -sX 10.10.10.10                  # Xmas: FIN+PSH+URG ("lit up like a tree")
sudo nmap -sA 10.10.10.10                  # ACK: distinguishes stateful vs stateless filtering
```

`-sA` is *diagnostic*, not enumerative: it doesn't tell you which ports are open, it tells you whether the firewall is stateful (blocks unsolicited ACKs) or stateless (lets ACKs through). Useful for understanding why earlier scans behaved the way they did.

### 2.2 The ping problem (`-Pn`)

By default Nmap pings each host first and skips hosts that don't reply. On the modern internet, **most hosts don't reply to ping**, so the default behavior silently hides everything.

```bash
nmap -Pn -p- 10.10.10.10                   # treat host as up, scan everything
```

Use `-Pn` whenever:
- You already know the host exists (DNS resolves, web page loads, it's in scope)
- A previous scan said "host seems down" but you don't believe it
- You're scanning a single target and not a sweep (no reason to skip-on-no-ping)

`-Pn` trades speed (nothing skipped) for completeness, which is usually the right trade.

### 2.3 Port selection strategy (the layered scan)

Per the **Defaults** section: by default we go full range with `-p-`. The layered approach below is how to do that without waiting forever.

```bash
# 1) Quick top-1000 with version + default scripts (~30s) to pick the obvious wins
nmap -sC -sV -oA quick 10.10.10.10

# 2) Full TCP port discovery, no probes, fast, finds the weird high ports
nmap -p- --min-rate 5000 -oA allports 10.10.10.10

# 3) Re-scan only the new ports found in (2) with version + scripts
nmap -sC -sV -p 22,80,443,8080,9000,50000 -oA detail 10.10.10.10

# 4) UDP top 100, slow, run in background while you triage TCP
sudo nmap -sU --top-ports 100 -oA udp 10.10.10.10
```

Skipping step 2 is the second-most-common cause of missed services (after ignoring `-Pn`). The top-1000 list misses plenty: admin panels on 8443, custom services on 50000+, backdoors on whatever port the operator picked.

### 2.4 Timing & evasion

`-T0` (paranoid) up to `-T5` (insane). `-T4` is the sensible default for lab / authorized engagements. `-T2` for stealth. `-T0` for environments where you need to look like background noise.

```bash
nmap -T4 --min-rate 1000 10.10.10.10              # speed
nmap -T2 -f --data-length 25 10.10.10.10          # fragment + pad: basic evasion
nmap -D RND:10 10.10.10.10                         # decoy scan, mixes your IP with 10 fakes
nmap --source-port 53 10.10.10.10                  # masquerade as DNS reply traffic
```

Evasion options trade reliability for stealth and are only worth it when an IDS is in scope. For most engagements, prefer `-T4` and a clean log over half-broken stealth.

### 2.5 Version & OS detection

```bash
nmap -sV --version-intensity 9 10.10.10.10        # try every version probe
sudo nmap -O 10.10.10.10                           # OS fingerprint
nmap -A 10.10.10.10                                # -O + -sV + -sC + traceroute (kitchen sink)
```

`-A` is convenient against a single host but too noisy and slow for a sweep. Reach for it in step (3) of the layered scan, not step (1).

### 2.6 NSE (Nmap Scripting Engine)

NSE is the difference between "port 445 is open" and "port 445 is open, SMBv1 is enabled, the host is Windows Server 2008, and these shares are world-readable". Use it.

```bash
nmap -sC 10.10.10.10                                       # default safe scripts
nmap --script=default,safe,discovery 10.10.10.10           # broader, still non-intrusive
nmap --script "smb-* and not brute" -p 445 10.10.10.10     # all SMB scripts except brute force
nmap --script-help "smb-*"                                  # what does each script actually do?
```

Stay clear of `--script=brute` and `--script=intrusive` unless you've explicitly been authorized; they make connection attempts that look (and are) like attacks.

### 2.7 Output (always save it)

```bash
nmap -sC -sV -oA scan_basename 10.10.10.10
# produces scan_basename.{nmap,gnmap,xml}
```
The `.xml` is consumable by other tools (Metasploit, Eyewitness, custom parsers); `.gnmap` is grep-friendly; `.nmap` is human-readable. Re-running scans wastes time and may not produce identical results, so keep the artifacts.

### 2.8 masscan cross-check (and rustscan)

masscan and nmap use independent code paths, so running them **in parallel** is the cheapest cross-check available: any port one finds and the other doesn't is a finding worth investigating (firewall quirk, race, dropped packets, masscan async loss, etc.).

**Default masscan command (TCP + UDP, full range, fast):**
```bash
sudo masscan -p1-65535,U:1-65535 10.129.23.41 --rate 10000 --wait 3 --retries 2 -oG masscan.gnmap
```

Speed knobs (the ones that actually matter):
- `--rate 10000` : packets per second. Default is 100 (glacial). On HTB / lab / authorized internal networks 10k is safe and fast; 50k-100k works on a healthy local interface against a single host. On the public internet stay in the 1k-5k range and confirm authorization first.
- `--wait 3` : seconds to keep listening after the last packet is sent (default 10). Lower means faster wrap-up at the cost of dropping a few late replies on slow links. 3 is a good balance for lab targets, 0 if you're really in a hurry and accept the loss.
- `--retries 2` : retransmits per port (default 1). Bumping to 2 catches more on lossy VPN tunnels (tun0 over the internet) without adding much wall-clock time.
- Optional `--router-mac <MAC>` : skips ARP resolution if you already know the gateway MAC. Marginal speedup but useful when ARP is flaky.
- Avoid `--banners` here : it's slow and limited; let Nmap do the version detection.

**Cross-check pattern (run both in parallel):**
```bash
# Terminal 1: nmap layered scan (slower but does service/version detection)
sudo nmap -sS -sV -sC -p- --min-rate 5000 -oA nmap_full 10.129.23.41

# Terminal 2: masscan in parallel (fast TCP + UDP discovery, no fingerprinting)
sudo masscan -p1-65535,U:1-65535 10.129.23.41 -e tun0 \
  --rate 10000 --wait 3 --retries 2 -oG masscan.gnmap

# After both finish, diff the open-port sets:
comm -3 \
  <(awk '/Ports:/{for(i=1;i<=NF;i++) if($i~/open/) print $i}' nmap_full.gnmap | sort -u) \
  <(awk '/^Host:/{for(i=1;i<=NF;i++) if($i~/^Ports:/) print}' masscan.gnmap | sort -u)
```

Anything masscan found that nmap missed : re-run `nmap -sC -sV -p <port> -Pn` against just that port. Anything nmap found that masscan missed : usually fine (masscan async loss), but worth a `nc -nv` to confirm.

**rustscan** stays as the third option: fast TCP discovery that auto-pipes into nmap. No native UDP, so don't use it as your only port discovery tool.
```bash
rustscan -a 10.129.23.41 --ulimit 5000 -- -sC -sV
```

### 2.9 When nothing works (the recovery checklist)

If a target keeps returning "all filtered" or "host down":
1. Add `-Pn` (skip ping).
2. Switch scan type: `-sS` to `-sT` to `-sA` to `-sN`/`-sF`/`-sX`.
3. Try a slower timing template (`-T2`).
4. Try fragmentation (`-f`) and a decoy source port (`--source-port 53`).
5. Try from a different vantage point (different IP, VPN, pivot host); the issue may be your network, not theirs.
6. Try UDP (`-sU --top-ports 100`); TCP-only assumptions miss whole classes of services.
7. Try a different tool (`masscan`, `rustscan`); implementation bugs differ.

---

## Stage 3. Manual Port Confirmation with `nc`

After Nmap calls a port "open," verify by talking to it yourself. This catches:
- Ports Nmap mislabeled (rare, but happens, especially through filters)
- Services that returned a banner Nmap didn't recognize (`tcpwrapped`, `unknown`)
- Honeypots that respond to SYN but hang up on real connections

The universal probe is `nc` (or `ncat` for TLS):
```bash
nc -nv 10.10.10.10 80                 # -n: no DNS, -v: verbose
ncat -nv --ssl 10.10.10.10 443        # ncat handles TLS, needed for HTTPS, IMAPS, SMTPS, etc.
```

Three possible outcomes:
- **Connection + prompt/banner/data**: port is *truly* open and the service is talking.
- **Connection refused**: closed. (Nmap will rarely lie about this, but worth confirming.)
- **Hangs forever with no data**: either silent-by-design (raw RPC, some custom protocols) or a tarpit/honeypot. Note it and move on.

Quick batch check across many ports without re-running Nmap (uses bash's `/dev/tcp`):
```bash
for p in 21 22 23 25 53 80 110 139 143 389 443 445 3306 3389 5432 8080; do
  (echo > /dev/tcp/10.10.10.10/$p) 2>/dev/null && echo "$p open"
done
```

The bash trick is great when you've shelled into a box that doesn't have `nc` or `nmap` installed.

---

## Stage 4. Banner Grabbing (the concept)

A *banner* is whatever the service voluntarily emits on connect, or in response to a basic protocol greeting. Banners commonly contain the product name, exact version, sometimes the OS, occasionally the hostname or admin email. They are free intel.

The technique is the same for every protocol:
1. Open a TCP (or TLS) connection to the port.
2. Either wait for the server to talk first (SSH, FTP, SMTP, MySQL, Redis, IMAP, POP3 are server-talks-first), **or** send the minimum protocol greeting required to make it talk (HTTP needs a request line; LDAP needs a bind; HTTPS needs a TLS handshake first).
3. Read what comes back. Compare the version string to known-vulnerable versions (`searchsploit <product> <version>`, NVD, vendor advisories).

Two practical ways:
```bash
nc -nv 10.10.10.10 22                                    # server-talks-first protocols
printf 'HEAD / HTTP/1.0\r\n\r\n' | nc -nv 10.10.10.10 80 # client-talks-first (HTTP)
nmap -sV --script=banner -p- 10.10.10.10                 # let nmap do it for every open port
```

For protocol-specific greetings beyond `HEAD`/`GET`, the per-service notes below cover the common cases and the cheatsheets at the bottom cover the rest. Don't memorize all of them; look them up when you need them.

---

## Stage 5. Service-Specific Identification

The goal here is **identification only**: pull metadata, list anonymous-readable resources, note anomalies, then stop. If a service requires credentials or active attack to learn more, hand off to a different skill.

For exhaustive per-service technique lists, lean on HackTricks (linked at the bottom). The notes below cover what to do *first* on each service: the cheap, high-signal moves.

### DNS (53/tcp, 53/udp)

DNS-side recon (zone transfers, subdomain enumeration, record harvesting, DNS-based fingerprinting) lives in a **separate dedicated skill**. Here we only confirm "yes, there is a DNS resolver on 53":

```bash
nmap -sU -sV -p 53 10.10.10.10                   # confirm + version probe
dig @10.10.10.10 version.bind chaos txt          # quick BIND version banner if exposed
```

If anything else DNS-shaped is needed (AXFR attempts, NSEC walking, brute-force subdomains, etc.), hand off to the DNS / subdomain enumeration skill instead of expanding inline here.

### HTTP / HTTPS (80, 443, 8080, 8443, anything else)

For *identification* only. Content discovery (directories, files, parameters) is a different skill.
```bash
curl -I https://10.10.10.10                                  # headers: Server, X-Powered-By, framework hints
curl -sk https://10.10.10.10 | grep -iE 'generator|powered|framework'
whatweb -a 3 https://10.10.10.10                             # tech fingerprint
nmap -p 443 --script ssl-cert,ssl-enum-ciphers,http-title,http-headers,http-methods 10.10.10.10
```

Things to log: the `Server` header, framework/CMS, TLS cert SANs (often leak internal hostnames + adjacent vhosts you didn't know about), the redirect chain, and supported HTTP methods (`PUT`/`DELETE`/`TRACE` enabled = note for later).

### SMB (139, 445)

```bash
nmap -p 445 --script "smb-protocols,smb-security-mode,smb-os-discovery,smb-enum-shares" 10.10.10.10
smbclient -L //10.10.10.10 -N                                 # null-session share list
smbmap -H 10.10.10.10                                         # share list + permissions
enum4linux-ng 10.10.10.10                                     # broad SMB/RPC dump
crackmapexec smb 10.10.10.10                                  # OS, domain, signing, SMBv1 status
crackmapexec smb 10.10.10.10 -u '' -p ''                      # explicit null session
```

Specifically note: SMBv1 enabled (very old, MS17-010 candidate), signing not required (relay candidate), null session allowed (free user/share enumeration). Don't pull files yet; that's a later step.

### FTP (21)

```bash
nmap -p 21 --script "ftp-anon,ftp-syst,ftp-bounce" 10.10.10.10
ftp -nv 10.10.10.10                                           # then `USER anonymous` / `PASS anonymous`
```

Anonymous FTP that allows directory listing is common on legacy infrastructure. Note whether anonymous can read, write, or both: that determines what's interesting later.

### LDAP (389, 636)

Anonymous binds against AD or generic LDAP often disclose the entire directory schema, naming contexts, and sometimes user lists.
```bash
nmap -p 389 --script "ldap-rootdse,ldap-search" 10.10.10.10
ldapsearch -x -H ldap://10.10.10.10 -s base namingcontexts    # discover the base DN
ldapsearch -x -H ldap://10.10.10.10 -b "DC=domain,DC=local" '(objectClass=*)' dn
```

Record the naming contexts: they tell you the AD domain name(s), which is the input every later AD tool needs.

### SNMP (161/udp)

```bash
nmap -sU -p 161 --script "snmp-info,snmp-sysdescr,snmp-interfaces" 10.10.10.10
onesixtyone -c /usr/share/seclists/Discovery/SNMP/common-snmp-community-strings.txt 10.10.10.10
snmpwalk -v2c -c public 10.10.10.10                           # if `public` works, you usually get everything
```

SNMP with a default community string (`public`, `private`) leaks system info, interface names, sometimes process lists and ARP tables. Try `public` and `private` first; if either works, walk it.

### NFS (111, 2049)

```bash
showmount -e 10.10.10.10                                       # list exports
nmap -p 111,2049 --script "nfs-showmount,nfs-ls,nfs-statfs" 10.10.10.10
```

Exports listed without an `everyone`/wide CIDR restriction are mountable from your IP: useful intel even if you don't mount yet.

### SSH (22)

```bash
nc -nv 10.10.10.10 22                                          # banner has the version
nmap -p 22 --script "ssh2-enum-algos,ssh-hostkey,ssh-auth-methods" 10.10.10.10
```

Note the version (look up CVEs separately), the supported auth methods (`publickey,password` vs `publickey` only changes your strategy entirely later), and the host key fingerprints (so you can detect MITM later).

### RDP (3389)

```bash
nmap -p 3389 --script "rdp-enum-encryption,rdp-ntlm-info" 10.10.10.10
```

`rdp-ntlm-info` returns the target hostname, domain, OS build, even when no auth has happened. Save it.

### Database services (identification only)

```bash
nmap -p 3306 --script "mysql-info" 10.10.10.10                       # MySQL/MariaDB
nmap -p 1433 --script "ms-sql-info,ms-sql-ntlm-info" 10.10.10.10     # MSSQL
nmap -p 5432 --script "pgsql-brute" --script-args "passdb=/dev/null" 10.10.10.10  # PostgreSQL: info only, empty passlist
nmap -p 27017 --script "mongodb-info,mongodb-databases" 10.10.10.10  # MongoDB (often no auth!)
nmap -p 6379 --script "redis-info" 10.10.10.10                       # Redis (often no auth!)
```

For MongoDB and Redis specifically, "auth required: no" is the headline finding; those services are notoriously deployed without authentication. Stop at that note. Exploitation is a different skill.

### Mail services (identification only)

```bash
nmap -p 25,110,143,465,587,993,995 \
  --script "smtp-commands,smtp-enum-users,pop3-capabilities,imap-capabilities" \
  10.10.10.10
```

SMTP `VRFY` / `EXPN` / `RCPT TO` enumeration is famous, but most modern servers disable it. The capabilities scripts will tell you which auth mechanisms are supported, which is the more useful thing on a modern engagement.

---

## Pivot Points (handing off)

Identification is done when you have, per host:
- A list of open TCP and UDP ports
- Service + version for most
- Anything anonymous-readable (shares, FTP dirs, LDAP base, SNMP, NFS exports) noted
- Known-vulnerable versions flagged (`searchsploit <product> <version>` or NVD lookup)

---

## Cheatsheets & Deeper References

When the on-skill notes don't cover the protocol or edge case in front of you, go here. These are maintained, exhaustive, and well-organized, far more so than anything inlined here.

- **HackTricks**: https://hacktricks.wiki/en/generic-methodologies-and-resources/pentesting-network/index.html
- **Nmap NSE script database**: every script, its arguments, output, and risk level: https://nmap.org/nsedoc/
- **Nmap reference manual**: definitive source on scan types, host discovery, timing, evasion: https://nmap.org/book/man.html
- **PayloadsAllTheThings, Methodology and Resources**: protocol notes, methodology checklists: https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Methodology%20and%20Resources
- **SecLists**: wordlists for everything (community strings, default creds, subdomains, etc.): https://github.com/danielmiessler/SecLists
- **OWASP Web Security Testing Guide**: for HTTP-side identification work: https://owasp.org/www-project-web-security-testing-guide/

---

## OPSEC

These are notes, not laws. Adapt to the engagement scope and rules of engagement.

- **Authorization first.** Scanning a host you don't have permission to scan is illegal in most jurisdictions, regardless of intent.
- Default Nmap (`-T3`/`-T4`, no fragmentation, real source IP) will be logged and likely alert IDS/EDR. If that matters, slow down (`-T2` or below), use `-Pn` to avoid noisy ping sweeps, and prefer fewer targeted scans over `-A` everywhere.
- Save all output (`-oA`). Reproducible findings beat re-scanning, and clients/instructors generally want the raw artifacts.
- Don't run `--script=intrusive`, `--script=brute`, or `--version-intensity 9` against production without explicit sign-off; they can crash fragile services.
