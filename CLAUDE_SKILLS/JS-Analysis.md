# JavaScript analysis - Beautify, annotation and secrets

You are analyzing JavaScript files for a penetration test.
Your goals are to make the code readable, find hardcoded secrets or credentials, and identify potential vulnerabilities or leaks.

All commands below run on Windows (CMD or PowerShell). Node.js and ripgrep are the primary dependencies. 

---
## Prerequisites

```
# Check that Node.js is available
node --version

# Check that ripgrep is available
rg --version
```

No global installs needed for most tools, npx handles it on the fly.

---
## Getting the JavaScript files

Work in a dedicated folder:       

```powershell
mkdir C:\Tools\js-analysis\TARGET
cd C:\Tools\js-analysis\TARGET
```

Before analysis, collect the target JavaScript files.      
Main options:      
1) Download a single file : `curl -o target.js https://TARGET/static/app.js`
2) Download all JavaScript referenced on a page with DevTools => Sources
3) Use the files that are already analyzed to find new filenames

### Working with HTML files containing inline JavaScript

If the target is an HTML file (e.g. `app.html`, `index.html`) rather than a standalone `.js` file, the beautify and deobfuscation tools in phase 1 won't work on it directly. They expect pure JavaScript as input. However, the ripgrep patterns in phase 2 work fine on HTML files as-is, since `rg` searches raw text regardless of format.

For the beautify/deobfuscate/annotate steps, extract the inline script blocks first using this Node.js one-liner for example:

```powershell
node -e "
const fs = require('fs');
const html = fs.readFileSync('target.html', 'utf8');
const matches = [...html.matchAll(/<script[^>]*>([\s\S]*?)<\/script>/gi)];
fs.writeFileSync('extracted.js', matches.map(m => m[1]).join('\n\n'));
console.log(matches.length + ' script block(s) extracted');
"
```

This concatenates all `<script>` blocks into a single `extracted.js` file, which you can then feed into the normal Phase 1 workflow. If the page has external script tags (`<script src="...">`) those point to separate `.js` files — download them individually as described above.

---
## Phase 1 - Beautify, deobfuscate and annotate

First, assess readability. Open the file and skim it. If it's already readable (well-named variables, clear structure, no hexadecimal encoding), skip steps 1a and 1b entirely and go straight to 1c or phase 2.

Only minified or obfuscated code needs the tools below, don't over-engineer.

### Step 1a: Beautify (minified JavaScript)

```powershell
# Prettify a single file
npx js-beautify target.js -o target_clean.js

# With prettier
npx prettier --parser babel target.js > target_clean.js
```

### Step 1b: Deobfuscate

```powershell
# webcrack — Broader coverage
# Also unpacks webpack bundles
npx webcrack target.js -o ./unpacked/
```

If both fail or produce garbage, it's likely a custom obfuscation. Move to
manual analysis. 

Pay special attention to the keywords listed in the JavaScript.txt file.

### Step 1c: Annotation and variable renaming (AI-assisted, with Claude Code)

Whether the code was already readable or just deobfuscated, a good annotation pass makes phase 2 much faster. Pass the file to Claude Code with this prompt and adapt it based on what you actually need : 

**Full annotation (recommended for complex or unknown files):**

> "Read this JS file. Do three things:
> 1. Add a JSDoc-style comment above each function describing what it does,
>    its parameters, and any security-relevant behaviour (auth checks, data
>    handling, network calls).
> 2. Rename any cryptically-named variables (like `_0x3f1a`, `a`, `b`) to
>    meaningful names based on how they're used in context.
> 3. Add inline comments on lines that look security-sensitive (eval, innerHTML,
>    fetch calls, credential handling, etc.).
> Rewrite the full file with these changes."

**Quick orientation pass (for large files, before deciding where to focus):**
> "Read this JS file and give me:
> - A one-paragraph summary of what this script does overall
> - A list of the main functions with a one-line description of each
> - Any lines or sections that immediately look security-relevant"

Use the quick pass first on large webpack bundles to decide which modules
or functions deserve a full annotation. Claude Code can handle large files
and will track context across the whole file, which is much better than doing this
manually or with a simple regex.

---
## Phase 2 - Secret Hunting

Use ripgrep (`rg`) for fast pattern matching. Run these against the beautified file, not the original if it was minified or obfuscated.           

The following sections are classical examples of interesting things.       
### API keys, tokens, passwords

```powershell
# Generic credential patterns
rg -i "api[_-]?key|api[_-]?secret|access[_-]?key|secret[_-]?key|client[_-]?secret|private[_-]?key" target_clean.js

# Password and authentication patterns
rg -i "password|passwd|pwd|passphrase|auth[_-]?token|bearer|authorization" target_clean.js

# Common third-party key formats
rg "AIza[0-9A-Za-z\-_]{35}" target_clean.js           # Google API key
rg "sk-[a-zA-Z0-9]{48}" target_clean.js               # OpenAI key
rg "AKIA[0-9A-Z]{16}" target_clean.js                 # AWS access key
rg "gh[pousr]_[A-Za-z0-9_]{36}" target_clean.js       # GitHub token
rg "xox[baprs]-[0-9a-zA-Z]{10,48}" target_clean.js    # Slack token
rg "EAA[a-zA-Z0-9]+" target_clean.js                  # Facebook token
[...]
```

### JWT and Base64 secrets

```powershell
# JWT tokens (starts with "eyJ")
rg "eyJ[A-Za-z0-9+/=_-]{20,}" target_clean.js

# Long Base64 strings (potential secrets or encoded stuff)
rg "['\"][A-Za-z0-9+/]{40,}={0,2}['\"]" target_clean.js
```

### Internal endpoints and infrastructure

```powershell
# Hardcoded URLs (API endpoints, internal hosts, etc.)
rg "https?://[a-zA-Z0-9._/-]+" target_clean.js

# IP addresses
rg "\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b" target_clean.js

# Interesting path patterns
rg -i "/(api|admin|internal|dev|debug|test|staging|v[0-9])/" target_clean.js
```

### Environment variables leaked into frontend bundles

```powershell
# Webpack often embeds process.env values at build time
rg "process\.env\." target_clean.js
rg "import\.meta\.env\." target_clean.js
```

**Triage tip:** ripgrep output can be noisy. Pipe to a file and review:

```powershell
rg -i "api[_-]?key|token|secret|password" target_clean.js > secrets_candidates.txt
```

---
## Recommended Workflow

```
1. COLLECT
   → Download JS files from the target
   → Work in C:\Tools\js-analysis\TARGET\

2. ASSESS READABILITY
   → Skim the file: is it already clear? → skip to step 1c
   → Minified only? → npx js-beautify
   → Obfuscated? → npx webcrack

3. ANNOTATE (Claude Code)
   → Quick orientation pass on large/unknown files first
   → Full annotation + variable renaming on security-critical sections

4. SECRET HUNTING
   → rg patterns for keys, tokens, passwords, endpoints
   → Flag candidates in secrets_candidates.txt

6. REPORT
   → Document findings with file name, line number, and impact assessment
```

---
## Final Report Format

Save as `js_analysis_[TARGET]_[DATE].md`.

```markdown
# JavaScript analysis report — [TARGET] — [DATE]

## Files analyzed
| File | Size | Obfuscated? | Notes |
|------|------|-------------|-------|

## Secrets and credentials found
| Pattern | Value | Line | Severity |
|---------|-------|------|----------|

## Potential vulnerabilities 
| Source | File | Line | Sanitization present? |
|--------|------|------|-----------------------|

## Endpoints discovered
(Internal URLs, API routes, staging hosts found in JS)

## Notes
(Obfuscation technique used, tools that worked/failed, recommended next steps)
```

---
## Context notes

- Always beautify before hunting, since minified code produces false negatives.
- Large webpack bundles can contain dozens of embedded modules but webcrack
  splits them into individual files, making analysis much more tractable.
- This skill is designed for authorized environments: bug bounty within defined
  scope, CTF, personal lab, etc.
