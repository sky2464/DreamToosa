# AgToosa Offline and Network-Dependency Matrix

> **Canonical source** for CLI offline / network behavior. Agent and Registry docs **link here** — do not maintain competing command×class tables elsewhere.
>
> Generated projects receive this file as `Docs/AgToosa_Network_Matrix.md`. The AgToosa maintainer mirror is `docs/AgToosa_Network_Matrix.md`.

## Dependency classes

| Class | Meaning |
|-------|---------|
| `offline` | Succeeds with no network egress once the local generator/install is present |
| `network-required` | Needs network to complete successfully |
| `network-optional` | Prefers network; a documented offline fallback (cache, local path, or private mode) exists |

Exactly one class applies per command/mode row.

## Matrix

| Command / mode | Bash | PowerShell | Class | Offline fallback / notes |
|----------------|------|------------|-------|--------------------------|
| install (project wizard) | `bash agtoosa.sh` / `--path` / `--platforms` | `.\agtoosa.ps1` / `-Path` / `-Platforms` | offline | Copies from the local generator `template/`; no registry fetch. Bootstrap/`curl` first-time download of AgToosa itself is separate and network-required. |
| update | `bash agtoosa.sh --update [path]` | `.\agtoosa.ps1 -Update -UpdatePath <path>` | offline | Applies the local generator baseline to a project install. |
| verify | `bash agtoosa.sh --verify [path]` | `.\agtoosa.ps1 -Verify -UpdatePath <path>` | offline | Runs the local lifecycle verifier (`Docs/agtoosa-verify.sh`). |
| doctor | `bash agtoosa.sh --doctor [path]` | `.\agtoosa.ps1 -Doctor -UpdatePath <path>` | offline | Local install diagnosis only (version skew, wiring, context). |
| registry list | `bash agtoosa.sh --registry list` | `.\agtoosa.ps1 -Registry -RegistryCommand list` | network-optional | Uses cached `registry.json` when fresh (`AGTOOSA_REGISTRY_CACHE_DIR` or `~/.cache/agtoosa`); pre-seed the cache for air-gapped list. |
| registry info | `bash agtoosa.sh --registry info <name>` | `.\agtoosa.ps1 -Registry -RegistryCommand info -RegistryArg <name>` | network-optional | Same registry cache / pre-seed path as list. |
| registry install | `bash agtoosa.sh --registry install <name-or-./path>` | `.\agtoosa.ps1 -Registry -RegistryCommand install -RegistryArg <name-or-.\path>` | network-optional | Offline: `--registry install ./local-pack` (or absolute path). Remote name installs need network or a pre-seeded cache plus a reachable/local tarball URL. |
| registry publish | `bash agtoosa.sh --registry publish [pack-dir]` | Prints Bash/WSL/Git Bash redirect (no native wizard) | network-optional | Local wizard validates the pack and prints a `registry.json` entry; opening the PR on GitHub requires network. |
| catalog validate | `bash agtoosa.sh --catalog validate <path>` | `.\agtoosa.ps1 -Catalog -CatalogCommand validate -CatalogArg <path>` | offline | Validates a local catalog JSON file; no network. |
| launch-readiness (private) | `bash scripts/check-launch-readiness.sh --mode private` | Use Bash/WSL/Git Bash (script is bash) | offline | Local Docs/language checks only; skips anonymous public URL checks. |
| launch-readiness (public) | `bash scripts/check-launch-readiness.sh --mode public` | Use Bash/WSL/Git Bash (script is bash) | network-required | Performs anonymous public URL checks (`curl`) against advertised surfaces. |

## Mitigations cheat sheet

| Mitigation | How |
|------------|-----|
| Local pack install | `bash agtoosa.sh --registry install ./my-pack` |
| Registry cache dir | `export AGTOOSA_REGISTRY_CACHE_DIR=/path/to/vetted-cache` (pre-seed `registry.json`) |
| Private launch mode | `bash scripts/check-launch-readiness.sh --mode private` |
| High-assurance offline | Pre-seed cache + verify pack SHA-256 before install; optional minisign soft-warn via `AGTOOSA_MINISIGN_PUBKEY` |

## Related

- Agent command overview: `Docs/AgToosa_Agent.md`
- Registry cache and trust detail: `Docs/AgToosa_Registry.md` (operational notes only — not a second matrix)

<!-- AGTOOSA PRODUCT TRUTH START: claims.surface.template-network -->
<!-- Static conformance and freshness only; not behavioral or provenance proof. -->
| Claim ID | Target | Status | Evidence class | Expires |
| --- | --- | --- | --- | --- |
| `claim.adapter.cursor` | `cursor.project-commands` | verified | static-conformance | 2026-10-12 |
| `claim.adapter.windsurf` | `windsurf.workflows` | verified | static-conformance | 2026-10-12 |
| `claim.adapter.claude` | `anthropic.claude-code` | verified | static-conformance | 2026-10-12 |
| `claim.adapter.gemini` | `google.gemini-cli` | verified | static-conformance | 2026-10-12 |
| `claim.adapter.copilot-vscode` | `github.copilot-vscode` | verified | static-conformance | 2026-10-12 |
| `claim.adapter.codex` | `openai.codex-cli` | verified | static-conformance | 2026-10-12 |
| `claim.windows.bootstrap-ref` | `windows-native` | verified | static-conformance | 2026-10-12 |
| `claim.product-truth.local` | `maintainer` | verified | static-conformance | 2026-10-12 |

### Backend classification

| Operation ID | Backend | Commands | Network | Missing behavior |
| --- | --- | --- | --- | --- |
| `operation.bootstrap-powershell` | `bash-delegated` | `powershell`, `git`, `bash`, `curl`, `tar` | yes | abort before work-directory mutation |
| `operation.install-bash` | `native` | `bash`, `python3` | no | abort before project mutation |
| `operation.install-powershell` | `native` | `powershell` | no | abort before project mutation |
| `operation.update-powershell` | `bash-delegated` | `powershell`, `bash` | no | abort before project mutation |
| `operation.maintain-powershell` | `bash-delegated` | `powershell`, `bash` | no | abort before target mutation |
| `operation.registry-publish-powershell` | `redirect-only` | `powershell`, `bash` | no | print Bash/WSL/Git Bash redirect without mutation |
| `operation.registry-json-bash` | `native` | `bash`, `jq` | yes | use validated cache only where documented or abort |
| `operation.product-truth` | `native` | `python3` | no | abort without reading governed artifacts or writing |
| `operation.markdownlint-ci` | `optional/degraded` | `node`, `npm` | yes | skip only when explicitly classified degraded |
<!-- AGTOOSA PRODUCT TRUTH END: claims.surface.template-network -->
