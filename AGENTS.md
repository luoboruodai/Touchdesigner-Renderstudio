# RenderStudio agent guide

## Start here

1. Read `PROJECT_CONTEXT.md` for the current product contract and architecture.
2. Read `docs/DEVELOPMENT.md` before editing or building, and `docs/TROUBLESHOOTING.md` before changing a previously fixed path.
3. Use `TEST_REPORT.md` and `TEST_SUMMARY.json` for evidence boundaries. Do not repeat old validation merely to recreate a green result.
4. If a separate private `PROJECT.md` exists in a maintainer's workspace, read it for local paths and private exclusions. It is intentionally not part of this public repository.

## Current contract

- Current product: RenderStudio 1.5.0, an independent TouchDesigner COMP export plugin.
- The current release contains a TOX and checksums, not a code-rain TOE. Historical projects are not inputs for a normal plugin change.
- Original plugin source and the independent TOX use MIT. Historical artwork, third-party references and separately downloaded FFmpeg remain under their own terms.
- `source/` contains the seven canonical Python modules. Their bytes are embedded in DATs inside the TOX; normal users do not need the source directory on disk.
- `source/help.txt` is the canonical help DAT text. `scripts/apply_source.py` applies modules, version labels and help to an expanded current TOX without test hooks.

## Change discipline

- Preserve the user's source network, parameter values and existing output files. Work on an isolated copy for destructive or packaging experiments.
- Do not modify global TouchDesigner settings, replace a system FFmpeg, disable TLS verification, or require administrator privileges.
- Do not add credentials, API keys, private URLs, personal/company information, chat transcripts, session logs, local absolute paths, private media or third-party design references.
- Do not copy private host drivers or test hooks into the public tree. Public build tooling must use arguments or repository-relative paths.
- Keep `PROJECT_CONTEXT.md`, `docs/TROUBLESHOOTING.md`, both READMEs and `CHANGELOG.md` synchronized when behavior, architecture or validation scope changes.

## Verification

- Run `python3 source/test_rules.py` for logic changes. The current baseline is 38 checks.
- Run the affected TouchDesigner host tests and decode real short outputs when changing rendering, audio, source ownership, UI behavior or packaging.
- Re-import the final TOX under a different parent and name for packaging changes. Check relative references and confirm there are no Legacy nodes or test hooks.
- Use the real Windows/macOS bootstrap workflow for managed FFmpeg changes. It downloads large pinned packages; do not substitute mocks or skip a failing assertion to obtain a pass.
- Separate pure rules, native executable execution, TouchDesigner execution, decoded media and physical UI evidence. Windows CI is not a native Windows TouchDesigner UI test.

## Publication

- Publishing, tags and Releases require explicit user authorization. Never move an existing public tag or replace an old Release asset silently.
- Use an explicit public whitelist and scan candidates, Git history and the final archive. `docs/PUBLIC_HANDOFF.md` records the public/private boundary.
- Do not upload a maintainer's private project root. Publish only the sanitized active-line files and reviewed documentation.
- A documentation commit does not require a new product version when the TOX and runtime inputs are unchanged. Never claim CI ran on a later commit when it actually ran on an earlier product commit.
