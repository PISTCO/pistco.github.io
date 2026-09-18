# PISTCO Research Portfolio

Bilingual static portfolio at https://pistco.github.io/, published from main:/docs. Browser code uses no server, database, or framework.

## Management and authoritative inputs

- Management entrance: https://pistco.github.io/admin/
- Private drafts: https://github.com/PISTCO/pistco-site-content (PISTCO only).
- Content source: content/profile.json, content/projects.json, and referenced media/ files in the private repository.
- Layout source: templates/ko.html, templates/en.html, docs/assets/styles.css, and docs/admin/index.html here.
- Generated pages: docs/ko/index.html, docs/en/index.html, and docs/assets/media/.
- Public entrypoints: docs/index.html, docs/404.html, and docs/.nojekyll.

The public management page contains navigation links only. GitHub enforces access to actual editing, uploads, previews, and manual publishing. Do not enter passwords or tokens into the website.

## Local workspace

Initial location: C:\Users\razer\Desktop\project\github_pages. Private source belongs under .private/site-content/, excluded from public Git tracking. The isolated build environment is .private/build-venv/. No system packages are changed.

Use that environment's Python interpreter with scripts/build.py, passing --content .private/site-content --out .private/preview-NEW-NAME. The output directory must not exist. Open generated ko/index.html or en/index.html locally. The existing node scripts/preview.mjs command serves the public docs/ directory on loopback port 4173 only.

Build requirements: Python 3.12+ and requirements-build.txt (Pillow 12.3.0). Run scripts/test_security.py for regression checks. Edit private content or public templates, never generated page content. Pull the public repository after workflow publication before further local changes. Preserve unrelated edits.

## Owner workflow

1. Open the management page and sign in to GitHub as PISTCO.
2. Edit both translations in the private JSON files. Upload images to media/ and reference a path such as media/project.jpg.
3. Run Preview private draft on main. Download its private preview artifact and open ko/index.html or en/index.html locally. Artifacts expire after 3 days.
4. Run Publish approved draft on main with its confirmation checked. This publishes the whole current draft snapshot.
5. Review the summary: private source commit, engine commit, public commit, and public HTTP verification.

Saving drafts never publishes. Unreferenced images stay private. Removing references removes files from the next live snapshot, but previously published material can remain in public Git history, caches, and visitor copies.

## Validation and security boundary

- Validate strict schema, both languages, unique IDs/order, HTTPS links, and file references before output.
- Escape all content as text; reject non-HTTPS links, embedded credentials, whitespace and backslashes in URLs.
- Allow JPEG/PNG/WebP up to 10 MiB and 25 megapixels; reject animation, mismatched formats, corrupt files, symlinks and path traversal.
- Decode/re-encode to WebP, at most 2400 pixels per side, without original EXIF/XMP metadata. Public filenames are content hashes.
- Export fixed entrypoints and explicitly referenced normalized images only. Never copy the private source tree or Git history.
- Preserve non-site public files. Publish through one non-force ref update; concurrent writes fail rather than overwrite newer work.
- Private workflow jobs require owner ID 220297881, triggering actor PISTCO, workflow_dispatch, and main. Publishing additionally requires a checked confirmation. No external PR trigger is configured.

## Publishing App

Create a dedicated GitHub App installed only on PISTCO/pistco.github.io with Contents read/write and required Metadata read. Disable webhooks; grant no other repository, organization, account, or Actions-write permissions.

Set APP_CLIENT_ID as a variable and APP_PRIVATE_KEY as an Actions Secret in the private repository. Never commit the key or paste it into the public site. The workflow requests a short-lived token for only the public repository and contents:write, then revokes it on completion. Until configured, publishing fails closed; preview works without it.

All Actions and the public engine are pinned to reviewed commit SHAs in both private workflows. Update engine pins deliberately when changing rendering/security code.

## Recovery and limits

Restore an earlier private content version, preview, then publish again. Do not force-push or represent rollback as erasing public history. If Pages verification times out after a public commit was created, inspect that deployment before retrying.

Private Actions use account-included usage. This project does not enable paid usage. Quota/permission failure leaves the existing site available.

## Verification record

Initial portfolio was deployed and verified on 2026-09-18 KST. Public collaborator listing confirmed only PISTCO before this change. New security regression tests and local generation passed; live App connection and final remote results are recorded in the private README and completion message. Tests do not guarantee absolute security, and giving another user access changes the trust boundary.
