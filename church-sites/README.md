# Church project landing pages

Minimal, buildless public landing pages for libre.faith (Heritage Bible),
libre.show (SyncShow), and libre.church (Heritage Community).
The existing app deployments stay in place; these pages link to them and to
public source/release information. No community member data or sign-in is hosted here.

Run `python3 build.py` to regenerate each `dist/` from the shared template and product
copy. Upload each `dist/` to the correspondingly named Cloudflare static Worker,
or run `wrangler deploy` from that product directory after authenticating.
Each Worker uses static assets, automatic trailing slashes, and the supplied 404 page.

The adaptive SVG favicons use dark green in light browser themes and cream in dark
themes. The portfolio uses separate white variants. No JavaScript or third-party
fonts, trackers, or assets are required by these landing pages.
