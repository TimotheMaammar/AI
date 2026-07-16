# DOM Clobbering

**TL;DR**: HTML-only attack. Inject elements with `id`/`name` attributes that overwrite ("clobber") global variables or object properties the JS relies on. Turns HTML injection (no `<script>` needed) into logic bypass or XSS. Survives sanitizers that allow tags/attributes but strip JS.

## Where to look
- HTML injection allowed but JS blocked (sanitizer allows most tags/attrs, e.g. DOMPurify default allows `id`/`name`).
- JS that reads `window.X` / `document.X` / a config property that may be undefined and is then used in a sink (`el.src`, `location`, `innerHTML`, script `src`, allowlist config).

## Techniques
- Clobber a global: `<a id=x href="javascript:...">` makes `window.x` an element; `x` used as a string often becomes the `href`/`id`.
- Nested property `config.url`: `<form id=config><input name=url value="//evil"></form>` -> `config.url.value` (or via `toString`).
- Deeper nesting: `<form id=a><input name=b></form>` for `a.b`; two elements sharing an id yield an `HTMLCollection`.
- String coercion: `<a id=x name=x href="https://evil">` then `String(window.x)` -> the URL (via `HTMLAnchorElement.toString`).
- Clobber `document.getElementById`-style lookups, `window.onload`, feature flags, sanitizer config objects.

## Impact / escalation
- Turn HTML injection into **XSS** by clobbering the source feeding a sink (e.g. a script loader that reads `window.config.cdn`).
- Bypass client-side allowlists / auth booleans read from clobberable globals.
- Chain with script gadgets in common libs (jQuery, AngularJS, Google Analytics) to reach execution.

## Detection
- Grep bundle (`00_JS_RECON.md`) for `window.<name>`, `document.<name>`, `x.y` reads of undefined-by-default config; test by injecting `<a id=name>` and checking behavior in Chrome console.

## Caido
- Mostly client-side; use Caido to deliver the HTML injection, confirm execution in Chrome.

## References
- PortSwigger - DOM clobbering - https://portswigger.net/web-security/dom-based/dom-clobbering
- PayloadsAllTheThings - DOM Clobbering - https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/DOM%20Clobbering
- HackTricks - DOM Clobbering - https://book.hacktricks.wiki/en/pentesting-web/xss-cross-site-scripting/dom-clobbering.html
