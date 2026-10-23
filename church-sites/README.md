# Church project landing pages

Minimal, buildless public landing pages for libre.faith (Heritage Bible),
libre.show (SyncShow), and libre.church (LibreChurch Stack and Heritage Community).
The existing app deployments stay in place; these pages link to them and to
public source/release information. No community member data or sign-in is hosted here.

Run `python3 build.py` to regenerate only the approved LibreChurch and LibreShow
landing `dist/` directories from the shared template and product copy. Use
`--site libre-church` or `--site libre-show` for one site. LibreFaith is paused: its
tracked artifacts/config stay unchanged, and the builder refuses that target. LibreShow must use the combined package below; its Worker
configuration points at `./package`, preventing a landing-only build from
publishing a broken Prepare link. LibreChurch remains a static landing; LibreFaith is excluded from this release.
Each Worker uses static assets, automatic trailing slashes, and the supplied 404 page.

The adaptive SVG favicons use dark green in light browser themes and cream in dark
themes. The portfolio uses separate white variants. No JavaScript or third-party
fonts, trackers, or assets are required by these landing pages.

## Package the LibreShow preview

Build the editor in its separate SyncShow checkout, then package it locally:

```sh
cd /path/to/SyncShow
npm run build:web-prepare
cd /path/to/edydex.github.io
python3 church-sites/build.py
python3 church-sites/package_libre_show.py --prepare-dir /path/to/SyncShow/web-prepare/dist
```

This creates ignored `church-sites/libre-show/package/` with the landing at `/`
and editor at `/prepare/`. The packager copies an explicit static-file allowlist,
rejects symlinks/unknown source files, refuses unrecognized output, and records
hashes in `build-receipt.json`. It never deploys or changes DNS. Cloudflare reads
the single root `_headers`; the package uses the editor's local-only policy so
Blob images work without conflicting nested rules.

Download points to the existing public SyncShow release feed. Prepare is labelled
as a focused preview; advanced authoring/live presentation remain on desktop.
The editor defaults to `.syncshow-service` for current public desktop releases;
`.libreshow` remains an additive choice for desktop builds supporting it. Files
and recovery stay in the browser. No deployed LibreShow page is claimed here.

The user approved publication of LibreShow and LibreChurch on 2026-10-23.
LibreFaith remains paused. See `RELEASE.md` for exact existing hosting, source
refs, package verification, access requirements and rollback; approval does not
authorize new credentials, GitHub App grants or hosting/DNS changes.

Migration preparation keeps these sites separate from church deployments.
`wotbc.heritage.faith` is protected: do not change its hostname, routing,
configuration, callbacks, data or behavior. These static Worker artifacts have
no API, sign-in, database, tunnel, redirect or wildcard route. The Bible landing
page continues to open `heritage.faith` while browser-data continuity and the
church's dependencies are verified. Publishing a landing page is not a reader
migration. Keep existing app names and application IDs for update continuity.

Run `python3 -m unittest discover -s church-sites -p 'test_*.py'` from the
repository root. This checks artifact boundaries and link continuity; inspect
Cloudflare's actual custom domains, routes and rules before any live cutover.
