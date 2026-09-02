
1. **Prioritize source code review early and reference code in findings**

Begin reviewing the application's source code as early as possible in the testing process. Use code analysis to identify vulnerable patterns, sinks, and data flows before crafting attack payloads. This accelerates vulnerability discovery and reduces guesswork. All findings must include references to the responsible source code when possible - include the file path, function or method name, and line numbers. This helps developers locate and remediate vulnerabilities faster and improves report quality.

2. **Prioritize by probability and criticality, then explore exotic vectors**

Focus first on vulnerability classes that are either statistically prevalent in the target's technology stack or pose the highest business impact (authentication flaws, injection vulnerabilities, sensitive data exposure, broken access control). Align your testing methodology with known weaknesses in the specific framework, language, and architecture. Exhaustively validate these high-probability and high-impact vectors before exploring exotic or edge-case attack paths.

3. **Fuzz with special characters and edge-case inputs after traditional testing**

Once conventional testing vectors are exhausted, test application boundaries with unconventional input patterns - special characters, Unicode variations (Zalgo text, combining characters), null bytes, control characters, extreme values, and encoding anomalies. These inputs often bypass validation and trigger unhandled exceptions.

4. **Apply discovered vulnerabilities patterns across the entire application**

After discovering a vulnerability, systematically test the same attack vector across all similar application components. Developers tend to implement equivalent functionality multiple times, replicating the same security issues in different locations.

5. **Reference external resources to validate and enhance testing**

Leverage established external resources to inform your testing approach, discover payloads, and validate findings. Consult repositories and guides such as:
* https://github.com/swisskyrepo/PayloadsAllTheThings
* https://github.com/OWASP/wstg/blob/master/document/README.md
* https://hacktricks.wiki/en/index.html
