# Race Conditions / TOCTOU

**TL;DR**: send requests in parallel to exploit a window where state is not yet updated (check-then-act). Classic: spend a balance/coupon twice, bypass a "one-time" limit.

## Where to look
- "One-time" / limited actions: coupon, promo code, invitation, vote, like, bonus claim, gift-card redeem, free trial.
- Values that must stay consistent: balance, points, stock, quota, withdrawal/transfer limit.
- Multi-step with check-then-act (TOCTOU): withdraw, transfer, apply-then-charge.
- MFA/OTP: brute-force via race to bypass a rate-limit.

## Exploitable patterns
- **Limit overrun**: apply N times what should apply once (coupon x50 in parallel).
- **Double spend**: use/debit the same credit twice.
- **State collision**: two workflows stepping on each other (2 signups same username, 2 bookings of the same slot).
- **Multi-endpoint TOCTOU**: validate on one endpoint, act on another during the window.

## Technique (max concurrency)
- **Single-packet attack** (HTTP/2): send ~20-30 requests in one TCP packet to null out network latency → tightest window. Reference tool: **Turbo Intruder** (`race-single-packet-attack.py`) or Burp Repeater "send group in parallel". (Caido has no native single-packet; prepare in Caido, fire the burst via Turbo Intruder/script.)
- HTTP/1.1: "last-byte sync" (send all but the last byte, then release together).
- Reduce jitter: same connection, warm-up, close server.

## Method
1. Isolate the single "limited action" request.
2. Establish the before-state (balance/counter).
3. Send 20-50 copies in parallel (single-packet).
4. Check the after-state (overrun = vuln).
5. Prove with symbolic amounts, do not drain a real system.

## Chaining / concrete cases
- OTP/2FA brute-force bypassing the rate-limit (`AUTH_SESSION.md`).
- Coupon stacking (`BUSINESS_LOGIC.md`).
- IDOR + race for concurrent states.

## Impact
- Financial loss, security-limit bypass (MFA rate-limit), fraud = often High.

## Caido
- Caido: prepare/validate the request, measure state. For true concurrency: **Turbo Intruder** (Burp) or a Python asyncio/h2 script. Check the Caido plugin store for a race plugin.

## References
- PortSwigger - Race conditions - https://portswigger.net/web-security/race-conditions
- PortSwigger research - Smashing the state machine (single-packet) - https://portswigger.net/research/smashing-the-state-machine
- Turbo Intruder - https://github.com/PortSwigger/turbo-intruder
- PayloadsAllTheThings - Race Condition - https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Race%20Condition
- HackTricks - Race Condition - https://book.hacktricks.wiki/en/pentesting-web/race-condition.html
- YesWeHack guide - Race conditions - https://www.yeswehack.com/learn-bug-bounty/ultimate-guide-race-condition-vulnerabilities
