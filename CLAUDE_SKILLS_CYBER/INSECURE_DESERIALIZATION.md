# Insecure Deserialization

**TL;DR**: the app deserializes user-controlled data → object manipulation, often **RCE** via gadget chains. Spot the serialized blob and the language, then apply the known gadgets (ysoserial & co.).

## Recognize the format
- **Java**: base64 starting with `rO0` (or bytes `AC ED 00 05`), `Content-Type: application/x-java-serialized-object`, viewstate-like cookies, RMI/JMX, JNDI.
- **PHP**: `O:8:"stdClass":...`, `a:2:{...}`, serialized cookies, `unserialize()`.
- **Python**: pickle (base64, often starts `gAS`/bytes `80 04`), `__reduce__`.
- **.NET**: `__VIEWSTATE`, `BinaryFormatter`, `ObjectStateFormatter`, `LosFormatter`, `Json.NET` with `TypeNameHandling`, big base64 blobs.
- **Ruby**: Marshal (`\x04\x08`), YAML (`!ruby/object`).
- **Node**: `node-serialize` (`_$$ND_FUNC$$_`), `funcster`.
- **YAML**: `!!python/object`, `!ruby/object`, SnakeYAML `!!javax...`.

## Detection
- Slightly modify the blob → deserialization error (stacktrace = confirms + leaks classes/libs).
- Find endpoints that take these blobs (cookies, params, view state, message queues, caches).

## Exploitation (gadget chains)
- **Java**: `ysoserial` (CommonsCollections1-7, Spring, Groovy, etc.). Pick the chain per present libs (fingerprint via errors/deps). URLDNS gadget = **non-RCE detection** (triggers a DNS lookup → collaborator) without executing code: ideal for a responsible PoC.
- **PHP**: POP chains (magic methods `__wakeup`, `__destruct`, `__toString`). `phpggc` generates payloads per framework (Laravel, Symfony, WordPress, Monolog...). Also **phar://** deserialization (LFI → deser) → `PATH_TRAVERSAL_LFI.md`.
- **Python**: pickle `__reduce__` → trivial RCE (but destructive: stick to a controlled PoC, e.g. DNS/sleep).
- **.NET**: `ysoserial.net` (TypeConfuseDelegate, ObjectDataProvider). ViewState without MAC / with leaked machineKey → RCE.
- **Ruby**: universal gadget (Marshal/YAML) → RCE.
- **Node**: `node-serialize` IIFE `_$$ND_FUNC$$_` → RCE.

## Responsible PoC
- Prefer a **non-destructive** gadget: URLDNS (Java) → DNS callback, or `sleep`/`nslookup` to collaborator. Prove execution without breaking the system.

## Bypass / tips
- Class blocklist → alternate chains, less-known packages.
- Blob compression/encoding (gzip+base64): reproduce the pipeline.
- Signature/MAC (ViewState `__VIEWSTATEGENERATOR`, JSF): look for the leaked machineKey/secret.

## Impact
- RCE = Critical. Even without RCE: object injection → auth bypass, LFI, DoS.

## Caido
- Spot/tamper the blob in Replay; generate payloads offline (ysoserial/phpggc/ysoserial.net) and inject; listen for OOB (URLDNS).

## References
- PortSwigger - Insecure deserialization - https://portswigger.net/web-security/deserialization
- PayloadsAllTheThings - Insecure Deserialization - https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Insecure%20Deserialization
- OWASP - Deserialization Cheat Sheet - https://cheatsheetseries.owasp.org/cheatsheets/Deserialization_Cheat_Sheet.html
- ysoserial - https://github.com/frohoff/ysoserial · ysoserial.net - https://github.com/pwntester/ysoserial.net · phpggc - https://github.com/ambionics/phpggc
- HackTricks - Deserialization - https://book.hacktricks.wiki/en/pentesting-web/deserialization/
