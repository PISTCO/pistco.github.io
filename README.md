# PISTCO Research Portfolio

A Korean/English personal research portfolio, managed locally with Codex and published using GitHub Pages.

## Project state

- Authoritative workspace: this repository (initial Windows location: `C:\Users\razer\Desktop\project\github_pages`).
- Repository: https://github.com/PISTCO/pistco.github.io
- Public site: https://pistco.github.io/
- Publication source: `main` branch, `/docs` directory, with `.nojekyll`.
- Initial content: an explicitly labeled editing template. No real research results, affiliations, email, photograph, or CV are supplied.
- The only profile link is the verified public GitHub profile https://github.com/PISTCO.
- Published and verified on 2026-09-18 at 14:09 KST. GitHub Pages uses `main:/docs` and enforces HTTPS.

## Files and editing

- `docs/ko/index.html`: Korean copy and project cards.
- `docs/en/index.html`: matching English copy and project cards.
- `docs/assets/styles.css`: shared responsive design, typography, and focus states.
- `docs/index.html`: redirects the root URL to Korean; includes ordinary language links as a fallback.
- `docs/404.html`: bilingual recovery links for missing pages.

No build system, package installation, JavaScript application, backend, CMS, or database is required. Google Fonts supplies Noto Sans KR through CSS; local system fonts remain available if the font request fails. No analytics or tracking scripts are included.

To add actual content, provide the public name, introduction, research topics, and each project's title, description, images with captions/alternative text, and public links. Update both language pages. Replace only confirmed examples, and remove the preparation labels only when the associated content is real. Do not create clickable project controls without real destinations.

## Local preview

From the repository root, run `node scripts/preview.mjs`, then open the loopback URL printed by the server. The server exposes only `docs/`. Stop it with Ctrl+C. It uses port 4173 by default; set `PORT` to choose another port if necessary. This helper uses only Node.js built-in modules; Node.js is not required by the deployed site.

## Publishing

1. Inspect the local diff and verify both languages and local links.
2. Commit the intended changes to `main` and push to `origin`.
3. In repository Settings > Pages, keep Deploy from a branch with `main` and `/docs`.
4. Confirm successful Pages deployment and fetch `/`, `/ko/`, `/en/`, and `/assets/styles.css` from the public site.

The public deployment contains only `docs/`; other repository files are still visible in the public source repository. Pages settings can be managed through an authenticated GitHub browser when the GitHub connector does not expose Pages configuration.

## Validation record

- Implementation date: 2026-09-18 (Asia/Seoul).
- Local tooling observed: Git 2.53.0.windows.1 and Node.js 24.13.1.
- Passed: all four HTML files parsed with balanced elements; local links, section anchors, unique IDs, UTF-8 encoding, language metadata, and explicit editing-example labels checked.
- Passed: shared CSS parsed with tinycss2 (70 top-level rules, including responsive and reduced-motion rules); Node.js preview script syntax and `git diff --check` passed.
- Passed: local HTTP responses for `/`, `/ko/`, `/en/`, and `/assets/styles.css`, plus the custom 404 response.
- Passed: the same four public HTTPS routes returned HTTP 200 and content matching the local files exactly; an unknown public route returned the matching custom bilingual 404 page.
- Initial publication succeeded: https://github.com/PISTCO/pistco.github.io/actions/runs/35309598128 (site-content commit `e7707d7e41a9e156fd8d136a09c933fb7400d9dd`).
- Local preview was opened successfully. Screenshot-based visual QA, mobile viewport checks, 200% zoom, and interactive keyboard testing were not performed.
- HTTPS validation used PowerShell's normal certificate validation. Inkscape's bundled Python could not validate the local issuer chain; no certificate validation was disabled and no machine trust settings were changed.

## Future work

Replace the editing examples with approved profile/research/project content. Blog posts, publications, forms, analytics, authentication, and a custom domain are outside the first version.
