# Dependency Confusion (Supply Chain)

**TL;DR**: publish a malicious package with the same name as a target's **private/internal** package to a public registry with a higher version. Their build resolves the public one, pulls your code, and runs it in CI/dev -> RCE. High severity, but strict rules: authorization required, benign PoC only, and it can hit third parties.

## Where to look (find internal package names)
- JS bundles / source maps (`00_JS_RECON.md`), leaked `package.json`, `.npmrc`, `requirements.txt`, `pom.xml`, `Gemfile`, `composer.json`, `nuget.config`.
- Error messages / stack traces, public GitHub repos and org dorks, Wayback, internal docs.
- Scoped npm packages (`@company/pkg`) where the scope is not reserved on the public registry.

## Method (responsible PoC)
1. Collect candidate internal names (per ecosystem: npm, PyPI, RubyGems, Maven, NuGet, Go).
2. Check the name is **unclaimed** on the public registry (a 404 = claimable).
3. Publish a PoC package with a **higher semver** than the internal one, containing only a benign callback in the install hook (npm `preinstall`/`postinstall`, PyPI `setup.py`) that does a DNS/HTTP beacon to your collaborator with a unique marker + hostname/whoami. No destructive payload.
4. If the beacon fires from the target's build infra = confirmed.

## Notes / caution
- Beacon only; never real code execution beyond proving resolution. Include your handle in the package description.
- Some resolvers are protected (scoped registries, `.npmrc` with explicit registry, PyPI `--index-url`); note this in the report.
- Programs vary widely on whether this is in scope; confirm before publishing anything public.

## Related
- Repo-jacking (unclaimed GitHub org/user in a dependency URL), typosquatting, unclaimed S3/CDN in a build (`SUBDOMAIN_TAKEOVER.md`).

## References
- Alex Birsan - Dependency Confusion (original research) - https://medium.com/@alex.birsan/dependency-confusion-4a5d60fec610
- PayloadsAllTheThings - Dependency Confusion - https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Dependency%20Confusion
- confused (detection tool) - https://github.com/visma-prodsec/confused
