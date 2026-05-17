---
name: analyzing-binaries
description: >
  Static reverse-engineering of a compiled binary (ELF, PE, Mach-O, or raw blob) for understanding what it does and flagging vulnerable patterns, WITHOUT executing it. 
  The primary deliverable is a prose summary of the program's behavior (what it reads, what it computes, what it produces, how it is structured).
  This can be complemented by a list of dangerous library calls, interesting strings, security defenses in place (NX, PIE, RELRO, canary, ASLR, Fortify), heuristic vuln-symptom flags (stack/heap overflows, format strings, integer overflows, command injection sinks, logic bugs, hidden/backdoor functions), and when worthwhile a structural sketch of the program. 
  Tools used: file, checksec, strings, nm, readelf, objdump, radare2, ghidra (GUI or headless). For reading and explaining individual functions encountered during this workflow, delegate to the asm-analysis skill's methodology (calling convention identification, pattern collapsing, pseudocode, intent paragraph). 
  Trigger this skill any time the current task involves understanding a compiled binary without running it, whether the request comes from the user, from another skill in the workflow, or from the implicit needs of the step being executed. 
  Do NOT use for: anything that requires executing the binary.
---

# Analyzing Binaries (Static Only)

You are a reverse engineer. The job here is **understanding the program**, statically and safely: no execution, no debugger run, no `./binary`. Everything is read from the bytes, the disassembly, the strings, and the metadata. Producing clean intel and a clear behavioral summary; letting other skills handle anything that needs the program to actually run.

The deliverable for any binary, in priority order:

1. **Prose summary of behavior** (the priority): a short, accurate description of what the program does, what its inputs and outputs are, and roughly how it is organized. Two to five paragraphs is the sweet spot.
2. **Dangerous library calls** with their callsites and whether attacker input is plausibly reachable.
3. **Interesting strings** classified into useful buckets (URLs, paths, format strings, credentials, error messages that leak logic, embedded scripts, version strings).
4. **Security defenses** enumerated (NX, PIE, RELRO, canary, Fortify, RPATH/RUNPATH), with one-liner implications for each.
5. **Heuristic vuln-symptom flags** with the function/address and a one-liner reason for each suspicion. False positives are fine; missing the obvious is not.
6. **Structural sketch** when the binary is non-trivial (more than roughly 30 user-defined functions) and the audience will not open ghidra themselves.

The prose summary in (1) is the synthesis the other items feed into. Always produce it, even when short.

## Defaults

**Always run all static stages exhaustively.** Static analysis is risk-free: looking at bytes, headers, symbols, and disassembly cannot harm anything. There is no "careful mode" for static analysis. The triage, disassembly, string hunt, imports, defenses, and vuln-symptom hunting are all run by default on every binary.

**Never execute the binary.** Not with `./binary`, not under gdb, not under ltrace, not under strace. Even seemingly innocent execution is out of scope for this skill. If the analysis hits a wall that only dynamic data could resolve, name that in the report ("X is determined at runtime from Y, static analysis cannot resolve without execution") and stop. Hand off to a dynamic-analysis or sandbox skill if running is needed.

If asked to run the binary in this skill: refuse politely and point at the appropriate handoff skill.

## Mental Model

Static binary analysis is a funnel from cheap-and-broad to expensive-and-specific:

1. **Triage**: file type, architecture, packing, stripping, defenses. Five minutes, decides everything else.
2. **Static enumeration**: symbols, strings, imports, exports, sections. Cheap to gather, high signal.
3. **Per-function reading**: pick the interesting functions and read them in a disassembler/decompiler. This is where the asm-snippet-analysis skill's methodology applies.
4. **Defenses**: enumerate mitigations and their implications.
5. **Vuln-symptom hunting**: pattern-match on disassembly / decompiled output for known-bad code patterns.
6. **Synthesis**: stitch the findings into the prose behavior summary that is the priority deliverable.
7. **Structural sketch**: only when the binary is non-trivial and a diagram beats prose for the audience.

If a step gives nothing, fall back to a different angle rather than going deeper into the same dead end. Don't spend an hour in ghidra on a binary that turned out to be packed (strip packer first, in triage).

---

## Stage 1. Triage

Goal: know what you're looking at before you commit to any deeper tool.

```bash
cd ~/recon                                          # or wherever the binary lives
B=./mybinary                                        # adjust path

file "$B"                                           # type, arch, dynamic/static, stripped, endian
sha256sum "$B"                                      # save the hash for the report
stat "$B"                                           # size, permissions, mtime

checksec --file="$B"                                # NX, PIE, RELRO, canary, Fortify, RPATH, RUNPATH
                                                    # (if no checksec: see Stage 3 for manual readelf flags)

strings -a -n 6 "$B" | wc -l                        # rough scale of string surface
strings -a -n 6 "$B" | head -50                     # quick eyeball

readelf -h "$B" | head -20                          # ELF header: entrypoint, machine, ABI
readelf -d "$B" | head -30                          # dynamic section: needed libs, soname, runpath
readelf -S "$B" | head -40                          # sections (.text, .data, .rodata, .bss, custom)
```

Things to log right now:
- **Type and arch**: `ELF 64-bit LSB executable, x86-64, dynamically linked, not stripped` is very different from `ELF 32-bit LSB, ARM, statically linked, stripped`. The path forward changes.
- **Stripped or not**: if `not stripped`, you have function names (huge time saver). If stripped, ghidra/radare2 will name everything `FUN_xxxx`/`sym.xxxx` and you reverse from scratch.
- **Packing indicators**: `file` will sometimes say "UPX compressed" or similar. If `strings | head -50` shows only `UPX!` signatures and 5 readable strings total, the binary is packed. Unpack first (`upx -d "$B"` or, for non-UPX packers, look for `Section names suggesting packing: .upx0/.upx1`, `.UPX0/.UPX1`, `.aspack`, `.themida`, etc.) before going further.
- **PIE or not**: changes whether addresses you see in disassembly are absolute or relative. Affects everything downstream.
- **Statically linked**: no imports in the usual sense; library calls are inlined. The xref-based vuln-hunting in Stage 4 needs to fall back to pattern recognition (canonical `gets` / `strcpy` machine-code signatures).

If the binary is packed, malformed, or unrecognized: stop, fix that first, then resume from Stage 1.

For PE binaries (Windows `.exe` / `.dll`): swap `readelf` for `objdump -p` and `radare2 -A "$B"` to get section and import info. ghidra reads PE natively. For Mach-O (macOS): `otool` is the canonical tool but is rare in Linux WSL; `objdump` (with mach-o support compiled in) and ghidra both work.

---

## Stage 2. Static Enumeration and Per-Function Reading

### 2.1 Choose your disassembler

Three tiers, pick by depth needed. **In practice, plan to escalate from Tier 1 to Tier 3 across one binary**: Tier 1 for the initial broad pass, Tier 3 for the functions that matter.

**Tier 1 (binutils, every Linux box has it, no install needed):**
```bash
objdump -d -M intel "$B" | less                      # full disassembly, Intel syntax
objdump -d -M intel -j .text "$B" | head -200        # main code section
objdump -d -M intel --disassemble=main "$B"          # one function
nm "$B" | head -40                                   # symbol table (if not stripped)
nm -D "$B"                                           # dynamic symbols (imports)
nm -C "$B" | head -40                                # demangle C++ symbols
readelf -s "$B" | head -40                           # alternate symbol view, includes sizes
```

Good for: quick peek, scripting, grepping disassembly, confirming a single function, sanity checks. Bad for: reading whole programs (no decompiler, no graph view, no cross-references on demand).

**Tier 2 (radare2 / rizin, CLI, scriptable):**
```bash
r2 -A "$B"                                           # -A runs all default analyses
# Inside r2:
> afl                                                # list functions
> iz                                                 # strings in data sections
> izz                                                # strings in the whole file
> ii                                                 # imports
> iS                                                 # sections
> ie                                                 # entrypoints
> pdf @ sym.main                                     # print disassembly of main
> pdg @ sym.main                                     # ghidra-style decompile (requires r2ghidra plugin)
> agf @ sym.main                                     # ASCII control-flow graph
> axt @ sym.imp.system                               # all xrefs TO system()
> /R                                                 # ROP gadget search
> q                                                  # quit
```

Good for: serious static work without leaving the terminal, scripting via `r2pipe`, CTF, and when you want decompilation without ghidra's GUI overhead (install `r2ghidra` for the decompiler).

**Tier 3 (ghidra, GUI, the heavyweight free option):**
- Best for: actually reading the program. Decompiles to C-like pseudocode, navigates cross-references visually, lets you rename functions/variables as you understand them.
- Workflow: open ghidra, create new project, import `$B`, accept default analysis options.
- The Decompiler window (Window > Decompiler) is the killer feature. It turns even unfamiliar arch assembly into readable C.
- Symbol Tree (Window > Symbol Tree) and Function Graph (Window > Function Graph) for navigation.
- Add comments / rename liberally as you reverse. The names persist across sessions.

**Ghidra headless mode** (for automation from this skill, useful when you want a programmatic export of decompiled C):

```bash
# Assumes GHIDRA_HOME=/opt/ghidra and the JRE is installed
$GHIDRA_HOME/support/analyzeHeadless /tmp/ghidra_proj MyProj \
  -import "$B" \
  -postScript DecompileToFile.java
# DecompileToFile.java loops over functions and writes their decompiled C to disk.
```

Useful for batch jobs, but for a single binary the GUI is usually faster.

### 2.2 Entrypoint and function inventory

The first concrete question to answer: **where does execution start, and what is the function call graph from there?**

```bash
# Entrypoint
readelf -h "$B" | grep Entry                         # address of _start
# Most ELFs go _start -> __libc_start_main -> main, so main is the real start.

# Function list (if not stripped)
nm "$B" | grep ' T ' | head -40                      # T = text section, defined symbols
nm "$B" | grep ' U '                                 # U = undefined (imports)
nm -S "$B" | sort -k 2 | head -40                    # sort by address (alternate)

# In r2: afl | head -40
# In ghidra: Symbol Tree > Functions
```

If the binary is **stripped**, you don't get function names. Two recovery options:
1. ghidra and radare2 both auto-name unnamed functions and detect `main` heuristically (it's the function whose address is passed to `__libc_start_main`).
2. Use signature-based recognition (ghidra "Apply data archives" with libc signatures; r2 `aaa` and `zign`). Pull in libc Sigs that match the target version to recognize statically-linked libc functions.

Identify roles early. Even before reading, function names (when present) hint at what each does. Look for: `main`, `parse_*`, `handle_*`, `process_*`, `read_*`, `write_*`, `init_*`, `cleanup_*`, `do_*`, `check_*`, `auth_*`, `verify_*`, `debug_*`, `test_*`.

### 2.3 String hunt

Strings are the highest signal-per-byte intel in any binary. Always run, always read.

```bash
strings -a -n 6 "$B" > strings.txt                   # all strings >= 6 chars
wc -l strings.txt

# Buckets worth grepping (case-insensitive, broad first):
grep -iE 'http[s]?://|ftp://|ssh://|ws[s]?://' strings.txt   # URLs, callbacks
grep -iE 'password|passwd|secret|token|api[_ ]?key|bearer|jwt' strings.txt
grep -iE '\.so($|\.)|\.dll|\.dylib' strings.txt              # loaded libraries (also visible via readelf -d)
grep -E '^/[a-zA-Z]' strings.txt                             # absolute paths (configs, sockets, devices)
grep -E '%[0-9.\-]*[sdxnpu]' strings.txt                     # format strings (potential printf sinks)
grep -iE 'error|fail|invalid|denied|forbidden|unauthorized' strings.txt | head -30
grep -iE 'debug|verbose|trace|test|tmp|todo|fixme|backdoor|easter' strings.txt
grep -iE 'usage:|--help|-h\b|\boption\b' strings.txt         # CLI surface
grep -iE 'select |insert |update |delete |create table' strings.txt   # embedded SQL
grep -iE '\$[a-z_]+|export ' strings.txt                     # env vars in use
grep -E '[A-Za-z0-9+/]{40,}={0,2}' strings.txt               # long base64-like blobs
grep -E '[0-9a-f]{32,}' strings.txt                          # long hex blobs (hashes, keys)
```

Pay special attention to:
- **Hard-coded credentials, tokens, IPs, ports**: findings on their own.
- **Format strings** with `%n`, `%s`, `%x`: if they reach attacker-controlled `printf`, that is the bug.
- **Error messages that reveal logic**: "user authenticated", "bypass token accepted", "admin mode enabled" each describes a code branch worth finding in disassembly.
- **Embedded scripts or commands**: SQL, shell, Lua, Python embedded in `.rodata` is often the program's core logic encoded.
- **Version strings**: the program's own version (`--version` output) is often embedded; same with library versions when statically linked.

For UTF-16 strings (Windows PE often has them): `strings -el "$B"` for 16-bit little-endian.

After the broad grep, drop into the disassembler and **xref each interesting string back to its callsite**:
```
# In r2:
> izz                                  # find string offset
> axt @ <string_offset>                # xref to its uses
> pdf @ <caller_addr>                  # disassemble the user
```
In ghidra: double-click a string in the Defined Strings window, then right-click > References > Show References to.

### 2.4 Imports and exports

What the binary calls into = where it touches the outside world.

```bash
# Imports (dynamic symbols needed from libs):
nm -D --undefined-only "$B" | head -40
readelf --dyn-syms "$B" | awk '$5=="GLOBAL" && $7=="UND" {print $NF}' | head -40
objdump -T "$B" | grep '\*UND\*' | head -40

# For PE binaries:
# (mingw binutils) x86_64-w64-mingw32-objdump -p "$B" | grep -A100 'Import Table'
# Or: r2 -qc 'ii' "$B"
```

What to look for, fast:
- **Network**: `socket`, `connect`, `bind`, `listen`, `accept`, `recv`, `send`, `getaddrinfo`, `curl_*`, `SSL_*` (network capability, sometimes covert)
- **Process / exec**: `system`, `popen`, `execve`, `execl*`, `fork`, `posix_spawn` (command injection sinks)
- **File I/O**: `fopen`, `open`, `read`, `write`, `mmap`, `unlink`, `chmod`, `chown` (filesystem capability)
- **Memory**: `malloc`, `free`, `realloc`, `calloc`, `mmap` (heap usage = heap bug surface)
- **Crypto**: `EVP_*`, `RSA_*`, `AES_*`, `SHA*`, `MD5_*`, `crypt_*` (crypto in use, hash for fingerprint, sometimes home-rolled is the finding)
- **Bad-API canon (see Stage 4)**: `strcpy`, `strcat`, `sprintf`, `gets`, `scanf("%s")`, `memcpy` with attacker-controlled length

### 2.5 Per-function reading (delegate to asm-snippet-analysis)

Once you have the list of functions worth understanding (main, parsers, anything reached from a dangerous import, anything with a suggestive name, anything triggered by an interesting string), read each in the disassembler/decompiler.

**Methodology for reading any single function**: apply the asm-snippet-analysis skill. Its six steps fit exactly here:

1. **Identify what kind of code this is** (arch, source, context).
2. **Identify the calling convention** (System V x86-64, Windows x64, ARM64 AAPCS64, etc.). Decompilers infer this but verify on hand-written or unusual code.
3. **Rename registers / locals** with semantic names as you understand their role. In ghidra, the rename persists; in radare2, use `afvn` and `afvr`.
4. **Collapse instruction groups** into higher-level operations (zero check, loop, memcpy, frame setup, etc.). The asm-snippet skill ships a pattern table for this.
5. **Write clean pseudocode** for the function. If the function is decompiled by ghidra, the pseudocode is mostly there; just rename and annotate.
6. **Explain the intent in one short paragraph**: what does this function do, what data does it produce or consume, what is its role in the program.

For each function you read, record the intent-paragraph in your notes. These paragraphs feed directly into the Stage 6 synthesis (the priority deliverable).

When reading: don't try to read every function. Pick by xref count, by being on the path from `main`, by being called near dangerous imports, or by name. A typical binary needs five to twenty functions read to produce a solid summary; the rest is plumbing.

### 2.6 Cross-references (xrefs) as the navigation primitive

Throughout Stage 2, the single most valuable navigation operation is: **given a function, string, or import, who references it?**

```
# In r2:
> axt @ sym.imp.system                 # who calls system()
> axt @ str.username                   # who references the string "username"
> axt @ 0x401234                       # who jumps to or calls 0x401234

# In ghidra:
# Right-click any symbol or address > References > Show References to (Ctrl+Shift+F).
```

Walking xrefs is how you turn imports into vuln findings (Stage 4) and how you find the code reachable from `main`.

---

## Stage 3. Defenses

Run `checksec` (from Stage 1) and read each row carefully. Without `checksec`, the same info is in `readelf -W -l "$B"` (NX from program headers) and `readelf -W -d "$B"` (BIND_NOW for RELRO).

| Defense | Output | Meaning if OFF | Meaning if ON |
|---|---|---|---|
| **NX** | `NX enabled` | Stack/heap executable, classic shellcode injection possible | Need ROP / ret2libc / data-only attacks |
| **PIE** | `PIE enabled` | Code at fixed addresses, no ASLR for the binary itself | Code base randomized per run, need a leak to defeat |
| **RELRO** | `Full RELRO` / `Partial RELRO` / `No RELRO` | GOT writable, GOT overwrite attacks possible | (Full) GOT read-only after init, GOT overwrite blocked |
| **Canary** | `Canary found` | Stack canary present, classic stack BO detected and aborts | Stack overflows trip the canary, need to leak or bypass |
| **Fortify** | `FORTIFY` | `_chk` variants of dangerous functions in use (some runtime BO detection) | Worth listing which funcs are fortified |
| **RPATH / RUNPATH** | `readelf -d \| grep PATH` | If set to a writable dir = library hijack possible | Note for the report |

Note the **combination**, not just individual flags. The worst-case for a defender is "No NX + No canary + No PIE + No RELRO + statically linked" (classic CTF baby pwn). Modern compiled-with-defaults binaries usually have NX + PIE + Full RELRO + canary + Fortify, which is solid baseline. Anything missing on a recent Linux distribution is suspicious (the developer disabled it on purpose, ask why).

---

## Stage 4. Vuln-symptom hunting

Heuristic. The goal is to flag suspicious patterns with a function name / address and a one-liner reason. NOT to write a working exploit (that's a different skill). False positives are fine; missing the obvious is not.

### 4.1 Stack-based buffer overflow indicators

```bash
objdump -d "$B" | grep -E 'call.*(strcpy|strcat|gets|sprintf|vsprintf|scanf|fscanf|gets_s)@plt' | head
```

Flag:
- `gets` is unconditionally dangerous (no bound at all). Always a finding.
- `strcpy(dst, src)` where `src` is attacker-controlled and `dst` is a fixed-size stack buffer.
- `sprintf(buf, fmt, ...)` with format strings that include `%s` and user data.
- `scanf("%s", buf)` (no width specifier).
- `memcpy(dst, src, n)` / `strncpy(dst, src, n)` where `n` is computed from attacker input (integer overflow in `n` is a sub-category, see 4.4).
- Variadic functions whose format string is not constant.

For each: xref to caller, read the caller (asm-snippet methodology), assess whether the source / length is attacker-controlled.

### 4.2 Heap indicators

Look at:
- `malloc(size)` / `realloc(p, size)` where `size` is attacker-controlled and not bounds-checked.
- `free(p)` paths that can be reached twice on the same `p` (double-free).
- `free(p); use(p);` paths (use-after-free).
- Custom allocators that wrap malloc/free (worth a name lookup and a quick read).
- `malloc(0)` paths (returns a valid pointer to a zero-size chunk; later writes are OOB).

Easier to spot in ghidra's decompiler than in raw objdump. The asm-snippet methodology applies to the suspect functions.

### 4.3 Format string indicators

```bash
objdump -d "$B" | grep -E 'call.*(printf|fprintf|sprintf|snprintf|syslog|err|warn|asprintf)@plt' | head -20
```

For each call, check (in ghidra/r2 decompiler) whether the **first argument** (the format string) is a constant pointer to `.rodata` or an attacker-controlled value. If attacker-controlled, format string vulnerability = full read/write primitive. The presence of `%s`/`%n` inside attacker data is the giveaway.

### 4.4 Integer issues

Patterns:
- `malloc(n * sizeof(*p))` where `n` is attacker-controlled and the multiplication can overflow (giving you a tiny allocation followed by a larger write).
- `signed int` used in length comparisons that should have been `size_t` (negative length passes the bound check, becomes enormous after cast).
- `int` (32-bit) holding sizes / offsets that can wrap on 64-bit data.
- Off-by-one in `for (i = 0; i <= n; i++)` patterns (especially when followed by `buf[i] = ...`).

Usually need decompiler eyes (ghidra). Search for `malloc(` and `* size_var` in the decompiled output.

### 4.5 Command injection / unsafe exec

Already partially covered in 2.4. Specifically:
```bash
objdump -d "$B" | grep -E 'call.*(system|popen|execv?p?|execle?|posix_spawn)@plt'
```
For each, check what string is being constructed as the command. If it concatenates attacker input without escaping, that is the finding. `system("cmd ")` with a constant string is fine; `system(user_input)` or `snprintf(buf, n, "cmd %s", user); system(buf)` is not.

### 4.6 Logic bugs (auth bypass, missing checks, TOCTOU, races)

Harder, requires reading. The hooks:
- Functions whose name contains `auth`, `login`, `check`, `verify`, `admin`, `debug`, `test`, `backdoor`. Read them all (asm-snippet methodology).
- Comparison constants that look like passwords / tokens / magic numbers (hex strings that look human-meaningful, suspicious decimals like `0x1337`, `0xdeadbeef`).
- Branches that depend on environment variables (`getenv`) or on file presence (`access`, `stat`). These are common backdoor triggers.
- TOCTOU: `access(path, ...)` then later `open(path, ...)`.
- Race-prone designs: `mkstemp` vs `tmpnam`, `pthread_*` without sync.

### 4.7 Hidden / backdoor functions

For each non-stripped function not reached from `main`'s call graph, ask: who calls it? If the answer is "nothing" or "only a string-triggered branch in input parsing", that's interesting and might be a debug backdoor or a hidden activation path.

```
# In r2:
> afl                                  # list functions
> axt @ sym.suspicious_func            # callers
# A function with no callers but present in the binary is a tell.
```

In ghidra, the Function Graph and the Symbol Tree highlight unused functions.

---

## Stage 5. Synthesis (the priority deliverable)

This is where the value is. After Stages 1 to 4, you have raw intel: strings, imports, defenses, function intent-paragraphs, vuln flags. The synthesis stitches them into a coherent behavior description.

**Structure of the synthesis** (two to five paragraphs, prose, no bullet points unless the audience requested them):

1. **Paragraph 1**: What kind of program is this and what does it do at the top level? One or two sentences. Examples:
   - "A CLI utility that periodically fetches a URL, parses JSON, and writes selected fields to a local log."
   - "An ELF setuid binary that takes a username argument, checks it against a hash list, and on match drops a privileged shell."
   - "A network daemon listening on TCP/8080, accepting an HTTP-like protocol with a custom command set, dispatching to handlers per command verb."

2. **Paragraph 2**: How is it structured? Identify the main function's role (dispatcher, parser, main loop, init-and-exit), the helper functions it calls, and the general flow. If there are clear architectural layers (parser, business logic, IO), name them. This is where the per-function intent-paragraphs collected in 2.5 are most useful.

3. **Paragraph 3**: What inputs does it consume and what outputs does it produce? Argv, stdin, env, files read, network reads on one side; stdout, files written, network writes, process spawns on the other. Cite addresses or function names for the non-obvious ones.

4. **Paragraph 4** (when present): Notable implementation choices that affect security or behavior. Hard-coded credentials. Custom crypto. Old library versions inlined statically. Suspicious branches gated by env vars. Disabled defenses.

5. **Paragraph 5** (when present): What the static analysis could not resolve and why. Common cases: behavior determined at runtime by a config file, decryption of an embedded blob with a runtime-derived key, behavior gated by network-fetched data. Name what is unknown precisely; do not paper over it.

The synthesis is the deliverable the audience reads first. Spend real time on it. The bullet lists of defenses and vuln flags are appendices to this paragraph.

---

## Stage 6. Structural sketch (when worth it)

For non-trivial binaries (more than roughly 30 user-defined functions) and an audience that will not open ghidra themselves, a sketch is faster to consume than re-reading the synthesis paragraphs.

Format: a text-based block diagram in markdown (or mermaid if the consumer renders it). Group functions into roles, draw the data-flow arrows, mark the dangerous-call sites with a star.

Example skeleton (replace with actual function names):
```
                +----------------+
                |    main()      |
                +-------+--------+
                        |
              +---------+---------+
              v                   v
        +-----------+       +-----------+
        | parse_cli |       | init_env  |
        +-----------+       +-----------+
              |                   |
              v                   v
        +-----------+       +-----------+
        |  dispatch | ----> | handler_X |  *system() reached if -x flag is set
        +-----------+       +-----------+
              |
              v
        +-----------+
        | handler_Y |       *strcpy() with argv[2]
        +-----------+
```

Skip Stage 6 for small binaries (under 10 functions). The synthesis paragraphs are sufficient.

---

## Pivot Points (handing off)

Identification is done when you have, per binary:
- Triage row filled (type, arch, packing, stripped, hash, size, defenses)
- Imports / exports listed with the dangerous ones flagged and xref'd
- Strings classified into useful buckets with the non-obvious ones xref'd
- For each function you read: intent-paragraph captured
- Defenses fully enumerated with implications
- Vuln-symptom flags listed with addresses and one-liner reasons
- **Synthesis paragraphs produced** (the priority deliverable)
- (Optional) structural sketch

What comes next belongs in other skills:
- **Dynamic analysis** (actually running, tracing syscalls, debugging): separate skill, not invoked from here.
- **Malware sandboxing** (running suspected malware in an isolated VM with traffic capture): separate skill.
- **PoC / exploit writing** (turning a vuln flag into a working RCE / info leak): pwn-exploitation skill.
- **Fuzzing** (finding bugs the heuristics missed): fuzzing skill (AFL++, libfuzzer, honggfuzz).
- **Patch / mitigation suggestion** (telling the developer what to fix): code review skill, possibly with source if available.

For reading any single function's assembly: **asm-snippet-analysis** skill (referenced throughout Stage 2.5).

---

## Cheatsheets & Deeper References

- **ctf101 binary exploitation primer**: https://ctf101.org/binary-exploitation/overview/
- **Ghidra Class materials (NSA, official)**: https://github.com/NationalSecurityAgency/ghidra/tree/master/GhidraDocs/GhidraClass
- **radare2 book**: https://book.rada.re/
- **how2heap** (heap exploitation reference, useful for recognizing patterns in disassembly): https://github.com/shellphish/how2heap
- **The Shellcoder's Handbook** (book): canonical bug-class taxonomy.
- **Practical Binary Analysis** (book, Dennis Andriesse): rigorous coverage of static methods.
- **awesome-reverse-engineering** (curated tools): https://github.com/wtsxDev/reverse-engineering
- **GTFOBins** (when the binary turns out to be a known LOLBin you can abuse): https://gtfobins.github.io/
- **Felix Cloutier x86 ref** (instruction-by-instruction): https://www.felixcloutier.com/x86/

---

## Prerequisites (one-time install in WSL)

Static-only toolset, no debugger / tracer needed:

```bash
sudo apt update
sudo apt install -y \
  binutils file \
  radare2 \
  default-jre \
  python3-pip python3-dev \
  upx-ucl \
  checksec

# Ghidra (download from https://ghidra-sre.org/, extract to /opt/ghidra):
# sudo mkdir -p /opt/ghidra && cd /opt/ghidra && unzip ~/Downloads/ghidra_*.zip
# echo 'export GHIDRA_HOME=/opt/ghidra/ghidra_*' >> ~/.bashrc

# Optional for advanced static work:
pip3 install --user angr ROPgadget          # symbolic execution + ROP gadget hunt (static)
sudo apt install -y binwalk                 # firmware / blob carving
sudo apt install -y r2ghidra                # ghidra decompiler as a radare2 plugin (when packaged)
```

None of these require root at run time. No additional sudoers entries needed for analysis (no execution happens in this skill).

---

## OPSEC and safety

- Static analysis is read-only. Reading bytes, headers, symbols, strings, and disassembly cannot harm anything. Do all of Stages 1 to 5 freely on any binary, including known malware samples.
- **Do not execute the binary in this skill**, period. Not casually, not "just to see", not "with a quick `./bin --help`". Even `--help` triggers initialization code that can do anything. Execution is for the dynamic-analysis or sandbox skill.
- Document the SHA-256 hash of every binary you touch in the report. If a sample turns out to be malware later, you want a reference.
- Don't paste raw binary content (bytes, base64) into chat unless asked. Strings, function lists, decompiler output, and pseudocode are fine and useful in the report.
- When the binary contains credentials, tokens, keys, or other secrets in strings, treat them as findings, but don't reproduce them verbatim in shared reports without confirming with the requester (the secret might still be live).
