# LibreShow and LibreChurch release

The owner approved publication of these two sites on 2026-10-23. LibreFaith,
heritage.faith and WOTBC remain unchanged. This file describes the approved
candidate and source relationship; it is not proof of a completed deployment.

## Source and hosting

- Landing template, product copy, icons and packager live in this repository's
  `church-sites/`. The release branch is
  `codex/libre-sites-release-2026-10-23`, based on the existing `codex/mayos-dev`
  source at `ca412b874c1b978e7a03c5043d4f6ef092a21b6d`.
- Browser editor source and maintained core/portable-format helpers live in
  [edydex/SyncShow](https://github.com/edydex/SyncShow), commit
  **`54a7552f42ed174bb662ebe65f1735ead95bd4c4`**, branch
  `codex/libreshow-preview-release-2026-10-23`. Its additive desktop filename
  support is source preparation, not a new installer or release. The public
  download remains v2.1.0; browser exports default to `.syncshow-service`.
- Production hosting stays on the existing Cloudflare static Workers
  **libre-show** and **libre-church**, in account
  `ae36ed0ca979f0ca51d27a26c8f6c6a2`, retaining exact apex bindings.
- GitHub source hosting and Cloudflare production hosting are separate. This
  repository's current default `main` serves the unrelated legacy GitHub Pages
  site at `www.mayo.onl`; no default branch, CNAME or Pages setting is changed.
  Pushing these dedicated source branches does not establish a Cloudflare
  GitHub integration or prove a production release.

## Reproduce the reviewed assets

Use the pinned SyncShow commit above, with Node 24 and Python 3 already installed.
The browser build uses Node built-ins; it does not need an npm install or secrets.
From that checkout:

```sh
node scripts/build-web-prepare.mjs
```

From this repository's release checkout:

```sh
python3 church-sites/build.py
python3 church-sites/package_libre_show.py --prepare-dir /path/to/pinned/SyncShow/web-prepare/dist
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s church-sites -p 'test_*.py'
```

The builder only accepts `libre-church` and `libre-show`; default builds both.
`--site libre-church` builds the home alone. LibreFaith's tracked files and
configuration are preserved byte-for-byte and its build target is refused.

The output directories are independent:

| Existing Worker | Only serve this directory | Candidate inventory |
| --- | --- | --- |
| libre-show | `church-sites/libre-show/package/` | 21 files; root landing plus `/prepare/`; verify `build-receipt.json`. |
| libre-church | `church-sites/libre-church/dist/` | 9 static files; public stack/community information, no member login/backend. |

The reviewed LibreShow transport ZIP is 163060 bytes, SHA-256
`e1ed09bbba1e47ea800e9de03a5c49c0c20a22be8c7422899b7dc8990c1bf2ce`.
The LibreChurch transport ZIP is 4607 bytes, SHA-256
`63964fb408459bcd93898d3d49d67e1592da16ffd9b872259973bed16a8e9652`.
Do not publish raw LibreShow `dist/`, which has a Prepare link but no editor.
The archives are transport artifacts; serve their contained directories using
the supported existing Worker deployment path.

For local LibreChurch browser acceptance, use an existing Playwright install and
sandbox-capable Chrome; `LIBRE_SITE_PLAYWRIGHT_MODULE` can identify the module and
`LIBRE_SITE_BROWSER_EXECUTABLE` the browser. Run
`node church-sites/verify_church_preview.cjs`. It uses only a loopback server,
blocks external page requests and saves desktop/mobile/dark screenshots. The
test does not authenticate or publish anywhere.

## Publish without changing hosting

Before an approved upload, read both active Worker versions using an existing
authorized session. The parent's prior read-only baselines were:

- libre-show: `3e8af731-be89-45f9-b21f-97d7131fc9bc`, existing manual landing.
- libre-church: `1b1044c2-a239-4067-94db-dfb0d529e32e`.

If either has changed, inspect the newer deployment before proceeding. Upload
only the matching static directory to that existing Worker, preserving its
bindings, runtime settings and all other resources. Local configs are not a
complete export of live settings. Record actual new version IDs and verify
HTTPS pages, assets, served headers/404s and synthetic file flows after release.
Upload success alone is insufficient. Never deploy the other Worker folder as
a convenience; do not touch libre-faith, DNS, mail, tunnels, auth or security.

If acceptance fails, restore only the affected Worker's captured version, confirm
its serving state and preserve user local recovery/downloads. Do not clear
browser storage or restore church databases. Rollback of LibreShow removes
`/prepare/` again, leaving local recovery inaccessible until the editor returns.

## GitHub-linked deployment remains unconfigured

No new deploy token, OAuth grant, GitHub App permission or Actions secret is
authorized. No existing Cloudflare CLI session/credential or callable browser
control was available on Whitebox during preparation; both repositories had
zero repository Actions secrets. That does not prove whether an account-side
Cloudflare GitHub App integration exists. Its project/repository authorization,
branch and build settings must be inspected in an existing authenticated
Cloudflare session before proposing changes.

The smallest publication unblock is access to that existing authorized Worker
deployment surface. Automatic builds are optional. If later using an already
authorized GitHub integration, select this release source, use the pinned
SyncShow input, and keep the two build roots/assets directories above separate.
Inspect the provider's supported build command/runtime and existing permissions
before enabling it. Ask per action if any new persistent authorization is needed;
do not substitute a token workflow or a GitHub Pages/DNS migration.

## Preview limitations

Browser preparation supports focused basic authoring; advanced supported content
and image bytes are retained, while unknown fields/unsupported archives are
rejected whole. Full planner/advanced authoring and live presentation remain
desktop features. Chrome 156 was exercised; Safari/Firefox, installed public
desktop UI, physical mobile downloads, broader assistive technology and actual
crash recovery remain unverified. Browser archives are capped at 32 MiB, fonts
and layout preview are approximate, and local recovery can be evicted or lose
edits in its 350 ms debounce window. Download is the durable copy.
