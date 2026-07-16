# 00 - JS Bundle / Source Map Recon (SPA)

**TL;DR**: on a SPA (React/Vue/Angular), all client-side business logic (routes, endpoints, sinks, feature flags) is compiled into one or more JS bundles anyone can download. Before blind fuzzing, **read the bundle** - often faster and more exhaustive than content brute-force. Do this early, right after `00_METHODOLOGY.md` steps 1-2.

## Why it's a priority
- The bundle holds the **complete** list of API calls the front can make (even routes never clicked in the observed UI).
- It reveals the exact field names each endpoint expects (form-data, JSON body).
- It exposes dangerous sinks (`dangerouslySetInnerHTML`, `innerHTML`, `v-html`) and lets you know *before* testing whether a reflected field can actually XSS.
- Often left in the clear while the server itself is well protected - an exploitable asymmetry.

## Step 1 - Grab the whole bundle
- The prod bundle is minified (one giant line, 1-2 letter variables). A simple GET is enough; beware tools that truncate large responses (e.g. Caido `send_request` has a small default body limit - verify the exact value for your version) - use `get_request` with a high `bodyLimit`, or save to disk then grep/jq over it rather than holding it all in memory.
- Find every chunk: `asset-manifest.json` (CRA), `_next/static/chunks/*` (Next.js), `<script src=...>` in the initial HTML.

## Step 2 - Targeted grep (the bundle is unreadable line by line, you need patterns)
- API routes: `/api/[a-zA-Z0-9_/-]+` or equivalent per the observed prefix.
- HTTP method tied to the route: `\.(get|post|put|patch|delete)\(` (the HTTP lib name - axios/fetch wrapper - is minified to 1-2 letters, identify it from the context of the first match, e.g. `Xn.post("/api/...")`).
- Form fields: `\.append\(\s*["'][a-zA-Z0-9_]+["']` (FormData - never renamed by the bundler since it's a native browser API; note the real call is `.append("field", value)`, so do not anchor on a closing paren right after the field name).
- XSS sinks: `dangerouslySetInnerHTML` (React), `v-html` (Vue), `\[innerHTML\]`/`bypassSecurityTrust` (Angular) - search the literal string, never minified either (these are API/prop names, not internal identifiers).
- Auth/token storage: `localStorage`, `sessionStorage`, `Authorization`, `Bearer`, `Basic \$\{btoa\(` - determines whether CSRF/browser cache applies (see `CSRF.md`).
- Client routes (React Router / Vue Router): `path:\s*["'][a-zA-Z0-9/_-]*["']` - gives the page list, including pages not linked in the visible nav.
- To pull **readable context** around a match in a giant line: capture N chars before/after (`.{100}keyword.{300}`) rather than lines - otherwise everything collapses to a single "line 1".

## Step 3 - Source maps (jackpot if exposed)
- Test `<bundle>.js.map` (often listed in `asset-manifest.json` or on the bundle's last line: `//# sourceMappingURL=...`).
- If 200 + valid JSON with `sourcesContent` populated: **verbatim** reconstruction of the original source (real variable/function names, developer comments included) - extract each `sources[]`/`sourcesContent[]` entry into a separate file (filter out `node_modules`).
- Specifically search the reconstructed code for: `// TODO`, `// FIXME`, `// for demo`, `// in production` comments, authorization logic commented out or simplified "for the demo".
- If there is no `sourcesContent` but only `mappings`: the map still lets you recover original variable/function names (useful to de-obfuscate a stack trace or a sink name), but not to rebuild the full file.

## Secret hunting (ripgrep, after beautify)
- Generic: `rg -i "api[_-]?key|secret|access[_-]?key|client[_-]?secret|private[_-]?key|password|bearer|authorization" app.js`
- Key formats: `AIza[0-9A-Za-z\-_]{35}` (Google), `sk-[a-zA-Z0-9]{48}` (OpenAI), `AKIA[0-9A-Z]{16}` (AWS), `gh[pousr]_[A-Za-z0-9_]{36}` (GitHub), `xox[baprs]-[0-9a-zA-Z]{10,48}` (Slack), `eyJ[A-Za-z0-9+/=_-]{20,}` (JWT).
- Build-time env leaked into the bundle: `rg "process\.env\.|import\.meta\.env\." app.js`.
- Deobfuscate first: `npx js-beautify`, `npx webcrack app.js -o ./unpacked/` (unpacks webpack). Deep dive: internal skill `js-analysis`.

## Signals to note during recon
- A `dangerouslySetInnerHTML`/`v-html` found on a field = certain XSS candidate **if** that field is reachable with controlled content (cross-reference `XSS.md`).
- A route discovered in the bundle but never seen in captured traffic = test it directly (often not in HTTP history because you never clicked the right button).
- A client route guard (`ProtectedRoute`/`AdminRoute` equivalent) that only checks a "logged in" boolean and not a role = note as a minor finding (missing defense-in-depth), but **separately verify** whether the real check happens server-side before concluding a bypass (often yes, in which case the finding stays Low/Info, not Critical).

## Impact
- Rarely a vulnerability itself (except hardcoded secrets/keys found) - it's a **recon multiplier**: drastically cuts the time to find the real flaw (IDOR, XSS, business logic) by giving the full map of the playground.

## Caido
- `caido_get_request` (or equivalent) with a high `bodyLimit` to beat default truncation; if the file is too big for direct display, write it to disk and grep over it.
- Once routes are extracted, replay each one in Replay to confirm they really exist server-side (the bundle may be stale/misleading).

## References
- OWASP WSTG - Testing for Client-Side JS - https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/11-Client-side_Testing/
- Source map exposure (generic write-ups) - https://github.com/swisskyrepo/PayloadsAllTheThings (search "source map")
- HackTricks - JS recon / Source maps - https://book.hacktricks.wiki/en/network-services-pentesting/pentesting-web/
- Internal skill `js-analysis` (deobfuscation, secrets in JS)
