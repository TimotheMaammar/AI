# Business Logic Errors

**TL;DR**: abuse the business rules rather than a technical flaw. Invisible to scanners → few duplicates, often well paid. Ask: "what happens if I do this in the wrong order / with the wrong value / too many times / in parallel?"

## Mindset
- Understand the intended workflow, then violate every implicit assumption the dev made.
- Look for client-side-only controls, trusted values (price, quantity, status), skippable steps, inconsistencies between endpoints.

## Categories & tricks

**Price / payment / e-commerce**
- [ ] Modify the **price**/amount in the request (`price`, `amount`, `total`) - often recomputed, but test.
- [ ] **Negative** quantity → refund/credit; quantity `0` or decimal.
- [ ] Manipulable **currency** (pay in a weak currency).
- [ ] **Coupon/discount**: stacking, reuse, multiple application, expired coupon, apply after calculation.
- [ ] Exploitable **rounding** (0.001 * n).
- [ ] Add items **after** the payment step; modify the cart between validation and capture.
- [ ] Change the **order status** directly (`status=paid`).
- [ ] Payment webhook integrity (forge a "payment success").

**Workflow / steps**
- [ ] **Skip steps**: jump straight to the final endpoint (checkout without payment, KYC skip, onboarding skip).
- [ ] Replay a step, go back, play out of order.
- [ ] Reuse a step token/nonce.

**Quotas / limits**
- [ ] Bypass a limit (free trials, invitations, votes, likes) via counter reset, multi-accounts, race (`RACE_CONDITIONS.md`).
- [ ] Client-side-only limits.
- [ ] Trial abuse / infinite renewal.

**Trusted values / hidden params**
- [ ] Fields that should not be modifiable (`isPremium`, `verified`, `balance`, `role`, `discount`) → also `API_MASS_ASSIGNMENT.md`.
- [ ] Forced statuses/states (`account_type=business`).
- [ ] Manipulable dates (backdate, extend a subscription).

**Object reference / relations**
- [ ] Associate an object with another user/tenant (mixing IDs → also `IDOR`).
- [ ] Transfer money/points to yourself, negative amount = credit.

**Feature abuse**
- [ ] Replayable "refund/cancel" function.
- [ ] Referral: self-refer, bonus loops.
- [ ] Export/notification feature for spam/amplification.
- [ ] Resource/ID exhaustion: spam a create endpoint (checkout, order, signup) to burn sequential IDs, pollute the DB, or DoS limited stock.

## How to prove it cleanly
- Reproduce with your **own** accounts, symbolic amounts. Document the gap between expected and observed behavior and the quantified **business/financial impact**.

## Impact
- Direct financial loss, fraud, control bypass = often High. Depends on the business lever.

## Caido
- Replay to replay/alter steps and values; Automate/parallelism for limits (mind the rate-limit); compare states across endpoints.

## References
- PortSwigger - Business logic vulnerabilities - https://portswigger.net/web-security/logic-flaws
- PortSwigger - examples - https://portswigger.net/web-security/logic-flaws/examples
- OWASP WSTG - Business Logic Testing - https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/10-Business_Logic_Testing/
- HackTricks - Web pentesting - https://book.hacktricks.wiki/en/pentesting-web/
- YesWeHack guide - SSTI / cache poisoning / logic - https://www.yeswehack.com/learn-bug-bounty/ssti-cache-poisoning-logic-vulnerabilities
