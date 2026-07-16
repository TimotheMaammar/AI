# Clickjacking

**TL;DR**: frame the target in an invisible/opaque iframe and trick a logged-in user into clicking a sensitive action. Exploitable only if the page is framable (no `X-Frame-Options` / no CSP `frame-ancestors`) AND the action is state-changing with cookie auth (SameSite not blocking). Low-ish alone, High when it lands a 1-click ATO.

## Where to look
- State-changing actions reachable in one click: change email, change password, delete account, add member/admin, transfer funds, enable an integration, OAuth "Authorize" consent.
- Pages missing framing protection (check headers). Actions that accept prefilled values via URL params (make the click do the whole thing).

## Detection
- Read response headers: `X-Frame-Options` (`DENY`/`SAMEORIGIN`) and CSP `frame-ancestors`. Both absent = framable.
- Quick PoC: load the target in an `<iframe src=...>`; if it renders (not blank), it frames.
- `frame-ancestors` in CSP overrides XFO and is the real control; XFO-only can sometimes be dodged.

## Tricks
- Classic overlay: full-page iframe `opacity:0.0001`, positioned so the sensitive button sits under a decoy ("Click to win"). Align with `position:absolute` + `z-index`.
- Prefill via URL: `target/settings?email=attacker@evil.com` so a single click submits attacker data.
- Multi-step: chain iframes / reposition to get several clicks (drag sequence).
- Variants: likejacking, cursorjacking, drag-and-drop data theft, `sandbox` iframe to neutralize JS frame-busters (`sandbox="allow-forms allow-scripts"` without `allow-top-navigation` kills `top.location` busters).
- SameSite check: if the action is a cross-site POST and the cookie is `Lax/Strict`, clickjacking usually fails (browser drops the cookie). GET-based actions or `SameSite=None` are the sweet spot.

## PoC skeleton
```html
<style>iframe{width:1200px;height:800px;opacity:.0001;position:absolute;top:-120px;left:-40px;z-index:2}
#decoy{position:absolute;top:300px;left:220px;z-index:1}</style>
<div id="decoy">CLICK HERE TO CLAIM</div>
<iframe src="https://target/settings/email?email=attacker@evil.com"></iframe>
```

## Escalation
- 1-click ATO: clickjack "change email" then trigger password reset. Or clickjack OAuth consent to link the attacker app.
- Fund transfer, role change, feature toggle. Severity = the forced action.

## Caido
- Inspect responses for `X-Frame-Options` / `frame-ancestors` (HTTPQL filter on headers). Otherwise this is a client-side PoC built by hand / in Chrome.

## References
- PortSwigger - Clickjacking - https://portswigger.net/web-security/clickjacking
- PayloadsAllTheThings - Clickjacking - https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Clickjacking
- OWASP - Clickjacking Defense Cheat Sheet - https://cheatsheetseries.owasp.org/cheatsheets/Clickjacking_Defense_Cheat_Sheet.html
- HackTricks - Clickjacking - https://book.hacktricks.wiki/en/pentesting-web/clickjacking.html
