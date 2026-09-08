# AgToosa Registry — Community Template Packs

Browse, search, and install community-created workflow packs (domain-specific templates, platform configs, etc.).

---

## Quick Start

**List available packs:**
```bash
bash agtoosa.sh --registry list
```

**Search for packs:**
```bash
bash agtoosa.sh --registry search ml-pipeline
```

**Show pack details:**
```bash
bash agtoosa.sh --registry info ml-pipeline
```

**Install a pack:**
```bash
bash agtoosa.sh --registry install ml-pipeline
```

**Install a specific version:**
```bash
bash agtoosa.sh --registry install ml-pipeline@1.2.0
```

**Install a local pack (offline mode):**
```bash
bash agtoosa.sh --registry install ./my-local-pack
```

---

## What Are Packs?

Packs are bundles of markdown workflow files and configuration stubs that extend AgToosa for specific use cases:

- **Domain-specific workflows:** ML pipelines, mobile apps, embedded systems, data engineering, etc.
- **Platform configs:** Custom IDE rules, slash commands, and AI prompt templates.
- **Organizational standards:** Company-specific quality gates, review checklists, deployment procedures.

Packs are **markdown-only** for safety — no executable code is automatically run when you install them.

---

## Installation Flow

1. **Browse or search** the registry to find a pack.
2. **Check verified status** — unverified packs are rejected unless you pass `--allow-unverified` (or set `AGTOOSA_ALLOW_UNVERIFIED=1`).
3. **Download** the pack tarball from GitHub.
4. **Verify SHA-256** against the registry index (abort on mismatch).
5. **Pre-scan the archive** — member paths with absolute segments or `..` are rejected **before** extraction (tar-slip protection).
6. **Stage in isolation** — the pack extracts to a temp directory, never directly into your project.
7. **Preview and confirm** — AgToosa prints the full file tree, flags AI-instruction surfaces, and marks denylisted paths that will be skipped at merge. Confirm to proceed (or pass `--yes` for non-interactive installs).
8. **Queue** validated files under `.agtoosa/pack-queue/<pack-name>/` (durable staging outside ephemeral `ship/`).
9. **Merge** — run `bash agtoosa.sh` in your project to integrate queued packs alongside core AgToosa workflows.

**Verified packs only by default.** Registry entries include a `verified` flag. Packs with `verified: false` require explicit opt-in:

```bash
bash agtoosa.sh --registry install my-pack --allow-unverified
# or: AGTOOSA_ALLOW_UNVERIFIED=1 bash agtoosa.sh --registry install my-pack
```

---

## Creating Your Own Pack

Before opening a registry PR, complete the canonical readiness checklist in the AgToosa maintainer handbook:
[registry-pack-authoring.md](https://github.com/sky2464/AgToosa/blob/main/docs/registry-pack-authoring.md)
(scoped spec, tests, threat notes, compatibility, provenance, worked example, and named owner).
That handbook owns the full checklist — this section is discovery only.

Publication summary:

1. Create a GitHub repo: `your-org/agtoosa-my-pack`
2. Write your workflow markdown files.
3. Tag a release: `git tag v1.0.0 && git push --tags`
4. Download the release tarball and compute its SHA-256:
   ```bash
   sha256sum agtoosa-my-pack-v1.0.0.tar.gz
   ```
5. Open a PR against `sky2464/agtoosa-registry`:
   - Add an entry to `registry.json` with name, description, author, version, URL, and SHA-256.
   - Add a `packs/my-pack.json` manifest with full metadata and link to your repo docs.

A maintainer will review and merge your contribution (`verified: true` is manual approval).

---

## Registry Index

The registry is maintained at **[sky2464/agtoosa-registry](https://github.com/sky2464/agtoosa-registry)**.

Each pack entry includes:
- **name** — Pack identifier (used in `--registry install <name>`)
- **description** — Short summary of what the pack provides
- **author** — GitHub username of the pack maintainer
- **version** — Semantic version (e.g., 1.2.0)
- **url** — Direct link to the release tarball on GitHub
- **sha256** — SHA-256 hash of the tarball (verified during install)
- **verified** — Whether the pack has been reviewed and approved
- **signature** *(optional)* — Signed provenance object (DEV-054 / ADR-011):

```json
"signature": {
  "alg": "minisign",
  "url": "https://example.com/pack.tar.gz.minisig",
  "pubkey_id": "agtoosa-release"
}
```

Primary algorithm: **minisign**. Cosign/Sigstore is a documented future alternate (not implemented).
A sidecar file next to a `file://` tarball (`pack.tar.gz.minisig`) is also recognized.

---

## Offline cache and trust

> **Canonical CLI matrix:** See [`Docs/AgToosa_Network_Matrix.md`](AgToosa_Network_Matrix.md) for offline / network-optional / network-required classes across install, update, verify, doctor, registry, catalog, and launch-readiness. This section covers registry cache locations only — not a competing dependency table.

AgToosa caches `registry.json` locally so list/search/info work when the network is slow or unavailable (default TTL: 1 hour).

| Surface | Cache location |
|---------|----------------|
| Bash | `$AGTOOSA_REGISTRY_CACHE_DIR/registry.json` if set, else `~/.cache/agtoosa/registry.json` |
| PowerShell | `%USERPROFILE%\.cache\agtoosa\registry.json` |

**HTTPS trust model:** The registry index is downloaded over HTTPS from GitHub only. There is no fail-closed signed manifest for `registry.json` in v1 — treat the index as trusted to the same degree as the HTTPS origin. If you need a fresh index, delete the cache file (or wait for TTL expiry) and run `--registry list` again when online.

**Optional minisign soft-warn (DEV-054):** When a signature sidecar or `signature.url` is present, AgToosa attempts `minisign -Vm` using `AGTOOSA_MINISIGN_PUBKEY` or `Docs/security/agtoosa.minisign.pub`. On failure (invalid sig, missing tool, missing pubkey) it **warns and continues** if SHA-256 and the verified-flag gate still pass. Unsigned packs are unchanged. Fail-closed require-signatures remains **roadmap**. Private-key generation remains **manual** (`DEV-054 M-1`).

**High-assurance installs:** Pack tarballs are always SHA-256 checked against the hash in the index during install. For stricter environments, pre-seed `AGTOOSA_REGISTRY_CACHE_DIR` with a vetted `registry.json` and independently verify each pack's SHA-256 (e.g. `sha256sum`) against a trusted source before `bash agtoosa.sh --registry install <name>`. Optionally attach `.minisig` sidecars and set `AGTOOSA_MINISIGN_PUBKEY`.

**Publishing packs:** Use Bash — `bash agtoosa.sh --registry publish` (the PowerShell port prints a redirect; it does not run the publish wizard).

---

## Security

**How your safety is protected:**

- ✅ **SHA-256 verification** — Ensures the tarball wasn't tampered with during download.
- ✅ **Tar-slip pre-scan** — Archive member lists are checked for absolute paths and `..` segments **before** extraction; hostile tarballs are rejected without writing to disk.
- ✅ **Isolated staging** — Packs extract to a temp directory first; only user-confirmed content reaches `.agtoosa/pack-queue/`.
- ✅ **Informed-consent preview** — Before queueing, AgToosa prints the full file tree and flags AI-instruction surfaces (`.cursor/*`, `CLAUDE.md`, etc.) so you know what your assistant will follow.
- ✅ **Verified-pack gate** — Registry entries with `"verified": false` are rejected unless you pass `--allow-unverified` (or set `AGTOOSA_ALLOW_UNVERIFIED=1`).
- ✅ **Sensitive-path denylist** — Packs cannot write to `.claude/settings.json`, `.claude/hooks/`, `.github/workflows/`, or `Docs/Master-Plan.md` (project-owned PM state; also blocks the lowercase `docs/Master-Plan.md` form used by AgToosa's own maintainer source repository; blocked at preview and merge).
- ✅ **File-type allowlist** — Only `.md`, `.json`, `.toml`, and `.mdc` files are accepted; no scripts or binaries.
- ✅ **Registry review** — New packs require PR approval from maintainers before publication (`verified: true`).
- ✅ **Pinned versions** — Each published version's hash is recorded; existing installs are unaffected if a pack author goes rogue.
- ✅ **HTTPS from GitHub** — Registry and pack tarballs are fetched over HTTPS from trusted GitHub CDN.
- ⚠️ **Optional minisign soft-warn** — When a `.minisig` / `signature.url` is present, verification is attempted; failures warn and do **not** block install (SHA-256 + verified remain authoritative). Not a mandatory signed-install mode.

> **Trust boundary:** Packs are third-party markdown that instructs your AI assistant. AgToosa screens and contains them as above, but you should still read the preview before confirming any install.

---

## Troubleshooting

**"Pack not verified"**
- The pack exists in the registry but `verified` is `false`.
- Re-run with `--allow-unverified` only after reviewing the content preview and trusting the author.

**"Pack not found"**
- Check the pack name: `bash agtoosa.sh --registry list`
- Make sure you spelled it correctly (names are case-sensitive).

**"SHA-256 mismatch"**
- The downloaded file doesn't match the registry record.
- This usually means a network glitch; try again.
- If it persists, report it to the pack maintainer.

**"Network error"**
- The registry fetch failed (GitHub may be down or you lack internet).
- The registry is cached for 1 hour; try again later.
- For offline installation, use `--registry install ./local-pack`.

**"Pack version not found"**
- The `@version` you requested is not listed in `registry.json` for that pack name.
- Run `--registry info <name>` to see the version currently in the index.
- To install the index version, omit `@version`: `--registry install <name>`.
- Pinned installs fail closed; AgToosa will not install a different version silently.

**"Pack not verified"**
- The pack exists in the index but has `"verified": false` (not yet reviewed by registry maintainers).
- Prefer waiting for maintainer approval, or install with explicit opt-in: `bash agtoosa.sh --allow-unverified --registry install <name>`.
- Unverified packs still run the full preview and denylist checks — verification status is about maintainer review, not tarball integrity.

**"Archive contains path traversal" or "absolute path member"**
- The tarball failed the pre-extraction tar-slip scan (a member path escapes the archive root).
- Do not install the pack; report it to the pack maintainer and registry maintainers.
- For local packs, rebuild the tarball with relative paths only.

**Version pinning**
- `--registry install <name>` installs the pack row for that name in the registry index.
- `--registry install <name>@1.2.0` installs only when the index lists exactly `1.2.0` for that name.

---

## Trust surface

Registry packs are labeled so readers can tell **who reviewed** a pack before queueing install instructions. Labels are a documentation and metadata contract — they do **not** replace install safety controls.

### Pack classes

| Class | Meaning | Typical signals |
|-------|---------|-----------------|
| **Verified** | Maintainer-reviewed for registry publication (`verified: true` in the index after manual approval) | Registry index `verified: true`; catalog trust may show `registry_verified_snapshot: true` when the index check is recorded |
| **Community** | Submitted by a third party; **not** maintainer-verified until review completes | Registry index `verified: false` (requires `--allow-unverified`); catalog `review_status` not a maintainer-accepted verified state |
| **Official pilot** | Maintained local candidate under the official pilot inventory (see [Official Pack Pilot](#official-pack-pilot)) | Manifest `trust.curation_tier: official-pilot`, `review_status: local-candidate` until external acceptance |

### Allowed and forbidden claims

| Class | Allowed claims | Forbidden claims |
|-------|----------------|------------------|
| **Verified** | “Maintainer-reviewed”; “approved for the registry index (`verified: true`)”; “passed registry review” | “Security certified”; “deterministic security enforcement”; “guaranteed safe”; “bypasses preview/consent” |
| **Community** | “Community submission”; “not maintainer-verified”; “install only with `--allow-unverified` after preview” | “Official”; “maintainer-approved”; “maintainer verified”; “verified pack” |
| **Official pilot** | “Official pilot”; “local candidate”; “not externally published” (until confirmation) | “Available in the registry” / “published” without independent confirmation; “marketplace listing” |

### Manifest field mapping (DEV-053)

Labels map to **existing** catalog/manifest keys only — do not invent schema fields:

| Label concern | Manifest / metadata field | Notes |
|---------------|---------------------------|-------|
| Curation class | `trust.curation_tier` | e.g. `official-pilot` for maintained pilots |
| Registry verified snapshot | `trust.registry_verified_snapshot` | Catalog display of a checked index snapshot — not a new verification pipeline |
| Review / publication honesty | `trust.review_status` | e.g. `local-candidate` until external acceptance |
| Ownership | `maintainers[]` | Named maintainer records (DEV-053 ownership block) |
| Index gate (install) | Registry JSON `verified` | Enforced by `--registry install` / `--allow-unverified` |

Unknown keys such as `verified_by_agtoosa_cloud` are **not** part of the contract.

### Publication state machine (DEV-080)

Official pilots and other inventory rows use the same honesty rules:

| State | Meaning | Allowed claim |
|-------|---------|---------------|
| **local candidate** | Authored and proven in the AgToosa distribution only | “local candidate” / “not externally published” |
| **submitted** | PR or submission opened against `agtoosa-registry` | “submitted” — **not** published, **not** “available in the registry” |
| **published** | Accepted external registry record **independently confirmed** | “externally published” / “available” in registry |

Do not report a pack as published or available until that independent confirmation exists. Canonical external submit/confirm procedure: see the AgToosa distribution’s `docs/registry-external-publication-runbook.md` (maintainer dogfood path; not installed into host `Docs/` by default).

### Install safety reminder

**Labeling does not bypass** preview, consent, integrity (SHA-256), tar-slip pre-scan, file allowlist, or sensitive-path denylist. Verified and community packs both run the same generator-enforced install gates; `--allow-unverified` only opts into installing `verified: false` index rows after those gates still apply.

### Pack behavioral scenario binding (DEV-121)

Official and verified packs may document **required behavioral scenario ids** from `Docs/AgToosa_Behavioral_Conformance.md` (for example `lifecycle-compass-proof`). This extends — but does not replace — DEV-096 SHA/manifest validation and DEV-101 trust labels.

| Layer | What it proves |
|-------|----------------|
| DEV-096 pack validation CI | Manifest + tarball integrity |
| DEV-101 trust label | Maintainer review state |
| BCL scenario id + `scenario-run.json` | Fixed proof task artifacts for a platform (maintainer-run; not default CI) |

Pack README or metadata may list `behavioral_scenarios: ["lifecycle-compass-proof"]`. Passing static corpus bats does **not** claim live assistant execution or hosted certification.

---

## Official Pack Pilot

AgToosa maintains exactly five **local candidate** official pilot packs (Rev4 five-pack maximum; not a marketplace; **not externally published** until an accepted external registry record is confirmed). Catalog contract: DEV-053 `schema_version` 1.0. `official-web` is stack-agnostic SPA; `official-react` is React/Next/Vite-specific.

| Pack | Primary domain | Status |
|------|----------------|--------|
| `official-web` | primary domain: web | local candidate — not externally published |
| `official-api` | primary domain: api | local candidate — not externally published |
| `official-infra` | primary domain: infrastructure | local candidate — not externally published |
| `official-react` | primary domain: react | local candidate — not externally published |
| `official-security` | primary domain: security | local candidate — not externally published |

**Support boundary:** “Official” means curated under documented maintenance policy for the pilot — not a fit guarantee. Install via local pack path when provided by your AgToosa distribution; registry safety controls (preview, consent, allowlist, denylist) remain authoritative.

External submission/approval is **manual**. A local artifact or open PR is not proof of publication. Maintainer procedure: `docs/registry-external-publication-runbook.md` (AgToosa source tree).

## Extension and Preset Catalog

For curated discovery by use case (extensions and team presets), use the **Catalog** workflow — it lists, searches, and plans installs but always delegates to `--registry install` for the actual merge. See `Docs/AgToosa_Catalog.md` for compatibility, trust boundaries, and planning commands. Install safety rules remain in this Registry document only.

---

## Next Steps

1. **Discover packs** — `bash agtoosa.sh --registry list`
2. **Share your own** — Create a pack and submit a PR to the registry repo.
3. **Give feedback** — Open an issue on [sky2464/agtoosa-registry](https://github.com/sky2464/agtoosa-registry) with suggestions.
