# mayos.dev

Oles Maiovskyi's personal website and blog. Built with Eleventy 3.1.7.

The design retains mayo.onl's monospace identity, original favicon, monochrome dark palette, and three-part navigation. A site-wide Reach Me footer includes the existing public email and social links. Projects retain the original vertical rules and SVG artwork, with MailReview and three church tools added. Monochrome artwork uses explicit white paint for the dark portfolio. Blog has generated tag pages, RSS, and a small browser-side search script inspired by CampGamesDB's DOM filtering. Everything can be read and navigated without JavaScript; search is an enhancement. Styles, scripts, the favicon, and project artwork use content-hashed URL versions so a new deployment does not keep showing cached assets. No analytics, external fonts, or client framework.

## Edit and build

Requires Node.js 20 or newer.

```sh
npm ci
npm run build
npm run check
npm run dev
```

Development preview: http://localhost:8086. Build output: `_site/`.

- `src/index.njk`: About Me. Contact details live in `src/_includes/base.njk` and `src/_data/site.json`.
- `src/_data/projects.json`: projects.
- `src/blog/`: blog posts. Copy an existing post, set title, description, date, topics and permalink.
- `src/_includes/`: layouts and shared lists.
- `src/assets/site.css`: design.
- `src/assets/search.js`: literal, accent-insensitive full-text search of rendered posts, with no external service.
- `src/evidence/`: the public supporting edition of the first experiment, copied unchanged during builds.

The first post's charts and benchmark evidence are frozen supporting artifacts. The public edition preserves all scored prompts/answers and grading details but omits unrelated internal application records. `publication.json` describes the omissions and the original archive's hash. Updating an article does not rerun models.

`import-benchmark.py` is the one-time import from the original benchmark workspace; normal site builds do not require that workspace. To deliberately reimport revised benchmark artifacts:

```sh
python3 scripts/import-benchmark.py --source-root /path/to/original/workspace
```

## Hosting

The live site uses Cloudflare Worker `mayos-dev` with static assets. An exact `mayos.dev/*` route serves the site through the existing proxied apex records. Other DNS records and subdomains are preserved. Deployments currently use reviewed manual static uploads; GitHub automatic deployment is not connected.

The related product landing pages live in `../church-sites/` and are hosted by separate static Workers at libre.faith, libre.show, and libre.church.

To update this site, Upload the contents of `_site/`, not the source directory or `node_modules`. For a Git-connected Pages deployment, use `npm run build` and output directory `_site`; root directory is the folder containing this package.json. For Workers Static Assets, use the included Wrangler configuration.

The original mayo.onl repository and its main branch are preserved. The new source is kept separately on the `codex/mayos-dev` branch under `mayos-dev/`.

The owner's existing email remains `oles@mayo.onl`. The résumé link points to the existing public résumé; this site does not create a new email mailbox or rewrite the old website.
