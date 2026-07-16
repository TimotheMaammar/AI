# Client-Side Path Traversal (CSPT)

**TL;DR**: user-controlled input flows into a path the **front-end** uses to build an API request URL (`fetch('/api/'+x+'/...')`). By injecting `../`, you make the victim's browser send its own authenticated request to a different endpoint. Main payoff: **CSPT2CSRF** (turn a benign GET into a state-changing call) and reflected-data leaks.

## Where to look
- Read the JS bundle (see `00_JS_RECON.md`): find where user input (path segment, `id`, `next`, slug) is concatenated into a request path before `fetch`/`axios`/`XMLHttpRequest`.
- URL fragments/params that the SPA maps into an API path. Endpoints like `/api/v1/users/{input}/avatar`.

## Technique
- Inject traversal in the controlled segment: `id=..%2f..%2fadmin%2fpromote` so the client calls `/api/admin/promote` instead of `/api/users/<id>/avatar`.
- **CSPT2CSRF**: if the front sends the request with the victim's cookies/CSRF token and you can steer it to a state-changing endpoint, you get CSRF even when classic CSRF is blocked (the request carries the app's own headers/token). Doyensec's CSPT2CSRF research covers the GET->action pivot.
- Encoding: `..%2f`, `..%252f`, `%2e%2e%2f`, mix. The traversal happens client-side, so browser URL normalization matters.
- Reflected read: steer the fetch to an endpoint whose JSON the page then renders into the DOM = leak other data into the victim's view (or into an XSS sink).

## Detection
- Static: grep the bundle for request paths built from a variable (template literals or `'/api/'+input`) feeding `fetch`/`axios`.
- Dynamic: put `../` in the candidate input, watch (Caido/DevTools) which backend URL the browser actually requests.

## Escalation
- CSPT2CSRF -> account actions (change email, add key), especially where there is no classic CSRF because the SPA adds a token automatically.
- Chain with open redirect / XSS sink for full impact.

## Caido
- Observe the outbound request the SPA builds after injecting traversal (HTTP History), confirm it hits a different endpoint. Exploit PoC is built client-side (Chrome).

## References
- PayloadsAllTheThings - Client Side Path Traversal - https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Client%20Side%20Path%20Traversal
- Doyensec - CSPT2CSRF research - https://blog.doyensec.com/2024/07/02/cspt2csrf.html
- HackTricks - Client Side Path Traversal - https://book.hacktricks.wiki/en/pentesting-web/client-side-path-traversal.html
