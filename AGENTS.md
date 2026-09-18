# Project Instructions

- This directory is the authoritative local workspace for PISTCO's bilingual research portfolio.
- Read README.md before changes. Preserve the static browser architecture and GitHub Pages deployment from main:/docs. Python and Pillow are build-time tools only.
- Keep Korean and English pages equivalent in scope. Update both when content changes.
- Use only user-provided or explicitly approved factual profile and project content. Clearly label editing examples; never invent research results, affiliations, or credentials.
- Keep public files under docs/. Do not copy unrelated local research files, private data, or credentials into the repository.
- Use UTF-8 without BOM and LF. Maintain responsive layouts, accessible focus states, semantic HTML, and language metadata.
- Publish only when requested or authorized by the current task. Verify remote deployment separately from local file checks.
- Content is authoritative in the private PISTCO/pistco-site-content repository. Its local checkout belongs under .private/site-content and must never be staged in this public repository.
- Edit templates/ko.html and templates/en.html for layout; docs/ko/index.html and docs/en/index.html are generated output. Never copy a private source tree to docs.
- The private workflows pin the public rendering engine to a reviewed commit. Update both workflow pins deliberately after engine changes.
- Keep App keys in GitHub Actions Secrets only. Never put persistent tokens in browser code, local Git remotes, tracked files, artifacts, or logs.
